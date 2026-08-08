#!/usr/bin/env python3
"""Pseudo-arclength continuation after releasing one active contact."""

from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

import contact_graph as cg


def tangent(value, remaining, previous=None):
    _, jacobian = cg.values_jacobian(value, remaining)
    _, singular, vh = np.linalg.svd(jacobian, full_matrices=True)
    direction = vh[-1]
    direction /= np.linalg.norm(direction)
    if previous is not None and np.dot(direction, previous) < 0:
        direction = -direction
    return direction, float(singular[-1])


def correct(predicted, remaining, plane, max_nfev=80):
    def fun(value):
        gaps, _ = cg.values_jacobian(value, remaining)
        return np.r_[gaps, np.dot(plane, value - predicted)]

    def jac(value):
        _, contact_jacobian = cg.values_jacobian(value, remaining)
        return np.vstack([contact_jacobian, plane])

    return least_squares(
        fun,
        predicted,
        jac=jac,
        bounds=(cg.LOWER, cg.UPPER),
        method="trf",
        xtol=3e-13,
        ftol=3e-13,
        gtol=3e-13,
        max_nfev=max_nfev,
        x_scale="jac",
    )


def trace_state(base, active, drop_index, max_steps=180, max_arc=1.2, initial_step=1.5e-3):
    drop = active[drop_index]
    remaining = [key for i, key in enumerate(active) if i != drop_index]
    inactive = [key for key in cg.ALL if key not in set(active)]
    value = np.asarray(base, dtype=float).copy()
    direction, _ = tangent(value, remaining)
    if np.dot(cg.gap_and_grad(value, drop)[1], direction) < 0:
        direction = -direction

    step = initial_step
    arc = 0.0
    inactive_gaps = {key: cg.gap_and_grad(value, key)[0] for key in inactive}
    trace = []
    event = None
    for iteration in range(max_steps):
        predicted = value + step * direction
        if np.any(predicted <= cg.LOWER) or np.any(predicted >= cg.UPPER):
            step *= 0.5
            continue
        corrected = correct(predicted, remaining, direction)
        if corrected.cost > 1e-16:
            step *= 0.5
            if step < 1e-7:
                break
            continue
        next_value = corrected.x
        distance = float(np.linalg.norm(next_value - value))
        if distance < 1e-10:
            step = min(0.03, step * 1.4)
            continue

        next_inactive = {key: cg.gap_and_grad(next_value, key)[0] for key in inactive}
        crossed = [key for key in inactive if next_inactive[key] <= 0 < inactive_gaps[key]]
        trace.append(
            {
                "iteration": iteration,
                "arc": arc + distance,
                "step": step,
                "score": float(next_value[2::3].sum()),
                "drop_gap": cg.gap_and_grad(next_value, drop)[0],
                "min_inactive": min(next_inactive.values()),
                "cost": float(corrected.cost),
            }
        )
        if crossed:
            add = min(
                crossed,
                key=lambda key: inactive_gaps[key] / max(inactive_gaps[key] - next_inactive[key], 1e-300),
            )
            fraction = inactive_gaps[add] / max(inactive_gaps[add] - next_inactive[add], 1e-300)
            guess = value + fraction * (next_value - value)
            new_active = remaining + [add]
            solved = cg.solve_graph(new_active, guess)
            candidate = solved.x
            candidate_metrics = cg.metrics(candidate, new_active)
            event = {
                "drop": cg.key_string(drop),
                "add": cg.key_string(add),
                "arc": arc + fraction * distance,
                "steps": iteration + 1,
                "cost": float(solved.cost),
                "distance_from_base": float(np.linalg.norm(candidate - base)),
                "metrics": candidate_metrics,
                "active": [cg.key_string(key) for key in new_active],
                "z": candidate.tolist(),
            }
            break

        if cg.gap_and_grad(next_value, drop)[0] < -1e-8:
            break
        value = next_value
        inactive_gaps = next_inactive
        arc += distance
        direction, _ = tangent(value, remaining, direction)
        if corrected.nfev <= 4:
            step = min(0.02, step * 1.25)
        elif corrected.nfev > 10:
            step = max(1e-6, step * 0.6)
        if arc >= max_arc:
            break

    return {
        "drop_index": drop_index,
        "drop": cg.key_string(drop),
        "base_score": float(base[2::3].sum()),
        "event": event,
        "trace": trace,
    }
