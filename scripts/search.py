#!/usr/bin/env python3
"""Regenerate contact-release seeds and continue the search by layers.

Layer 1 traces all 78 contacts of the exact root.  Later layers select the best
distinct local maxima under an explicit, deterministic policy.  This makes the
new search reproducible without claiming bitwise identity with the historical
run, whose original ``.npz`` seeds were not attached to the ChatGPT response.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

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
    """Release one contact and continue until the first new contact."""
    drop = active[drop_index]
    remaining = [key for i, key in enumerate(active) if i != drop_index]
    inactive = [key for key in cg.ALL if key not in set(active)]
    value = np.asarray(base, dtype=float).copy()
    direction, _ = tangent(value, remaining)
    if np.dot(cg.gap_and_grad(value, drop)[1], direction) < 0:
        direction = -direction

    step, arc = initial_step, 0.0
    inactive_gaps = {key: cg.gap_and_grad(value, key)[0] for key in inactive}
    trace, event = [], None
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
            event = {
                "drop": cg.key_string(drop),
                "add": cg.key_string(add),
                "arc": arc + fraction * distance,
                "steps": iteration + 1,
                "cost": float(solved.cost),
                "distance_from_base": float(np.linalg.norm(candidate - base)),
                "metrics": cg.metrics(candidate, new_active),
                "active": [cg.key_string(key) for key in new_active],
                "z": candidate.tolist(),
            }
            break
        if cg.gap_and_grad(next_value, drop)[0] < -1e-8:
            break
        value, inactive_gaps = next_value, next_inactive
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


def save_npz(path: Path, value: np.ndarray) -> None:
    """Write a byte-reproducible one-array NPZ archive.

    ``numpy.savez`` records the current time in the ZIP member, so otherwise
    identical regenerated seeds have different hashes.  A fixed ZIP timestamp
    makes the published reconstruction reproducible byte for byte.
    """
    buffer = io.BytesIO()
    np.save(buffer, value, allow_pickle=False)
    info = zipfile.ZipInfo("z.npy", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(info, buffer.getvalue())


def signature(value: np.ndarray, active) -> str:
    payload = {
        "contacts": sorted(cg.key_string(key) for key in active),
        "radii": sorted(round(float(radius), 11) for radius in value[2::3]),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def geometry_signature(value: np.ndarray) -> str:
    centers, radii = cg.unpack(value)
    distances = []
    for i in range(cg.N):
        for j in range(i + 1, cg.N):
            distances.append(round(float(np.linalg.norm(centers[i] - centers[j])), 10))
    payload = {
        "radii": sorted(round(float(radius), 10) for radius in radii),
        "distances": sorted(distances),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def run(depth: int, output: Path, max_bases: list[int], max_transitions: int | None = None):
    output.mkdir(parents=True, exist_ok=True)
    root, root_active = cg.default_state()
    save_npz(output / "root.npz", root)
    layers = []
    bases = [(root, root_active, "root")]
    transition_budget = max_transitions

    for layer_index in range(1, depth + 1):
        layer_dir = output / f"layer_{layer_index}"
        layer_dir.mkdir(exist_ok=True)
        events = []
        for base_number, (base, active, base_sig) in enumerate(bases):
            for drop_index in range(len(active)):
                if transition_budget is not None and transition_budget <= 0:
                    break
                record = trace_state(base, active, drop_index)
                record["base_signature"] = base_sig
                record["base_number"] = base_number
                if record["event"] is not None:
                    event = record["event"]
                    value = np.array(event.pop("z"), dtype=float)
                    # Preserve the 78 equations solved at the event. A
                    # degenerate endpoint may have an additional gap within a
                    # discovery threshold, so redetection can incorrectly
                    # report 79 near-contacts.
                    candidate_active = [cg.parse_key(key) for key in event["active"]]
                    sig = signature(value, candidate_active)
                    seed_name = f"base{base_number:02d}_drop{drop_index:02d}_{sig}.npz"
                    save_npz(layer_dir / seed_name, value)
                    event["seed"] = str((layer_dir / seed_name).relative_to(output))
                    event["signature"] = sig
                    event["geometry_signature"] = geometry_signature(value)
                    event["local_max"] = event["metrics"]["multiplier_min"] > 0
                    record["event"] = event
                trace_name = f"base{base_number:02d}_drop{drop_index:02d}.json"
                (layer_dir / trace_name).write_text(json.dumps(record, indent=2) + "\n")
                events.append(record)
                if transition_budget is not None:
                    transition_budget -= 1
            if transition_budget is not None and transition_budget <= 0:
                break

        unique = {}
        for record in events:
            event = record.get("event")
            if event is not None:
                current = unique.get(event["signature"])
                if current is None or event["metrics"]["score"] > current["metrics"]["score"]:
                    unique[event["signature"]] = event
        summary = {
            "layer": layer_index,
            "base_count": len(bases),
            "transitions_attempted": len(events),
            "events_found": sum(record.get("event") is not None for record in events),
            "unique_events": len(unique),
            "local_maxima": sum(event["local_max"] for event in unique.values()),
            "events": sorted(unique.values(), key=lambda event: event["metrics"]["score"], reverse=True),
        }
        (output / f"layer_{layer_index}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        layers.append(summary)
        if layer_index == depth or (transition_budget is not None and transition_budget <= 0):
            break

        candidates = []
        seen_geometries = set()
        root_score = float(root[2::3].sum())
        for event in summary["events"]:
            if not event["local_max"]:
                continue
            # A branch can return to the root through a square symmetry or a
            # circle permutation; do not spend a later-layer base on it.
            if abs(event["metrics"]["score"] - root_score) < 1e-10:
                continue
            if event["geometry_signature"] in seen_geometries:
                continue
            seen_geometries.add(event["geometry_signature"])
            candidates.append(event)
        limit = max_bases[min(layer_index - 1, len(max_bases) - 1)]
        candidates = candidates[:limit]
        bases = []
        for event in candidates:
            array = np.load(output / event["seed"])["z"]
            active = [cg.parse_key(key) for key in event["active"]]
            bases.append((array, active, event["signature"]))
        if not bases:
            break

    report = {
        "policy": "all 78 root releases; later layers use highest-scoring distinct positive-multiplier events",
        "requested_depth": depth,
        "max_bases_after_each_layer": max_bases,
        "layers_completed": len(layers),
        "layers": [{key: value for key, value in layer.items() if key != "events"} for layer in layers],
    }
    (output / "search_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--output", type=Path, default=cg.ROOT / "work/search_reproduction")
    parser.add_argument("--max-bases", default="4,6", help="comma-separated base counts for subsequent layers")
    parser.add_argument("--max-transitions", type=int, help="smoke-test limit")
    args = parser.parse_args()
    limits = [int(value) for value in args.max_bases.split(",") if value]
    print(json.dumps(run(args.depth, args.output, limits, args.max_transitions), indent=2))
