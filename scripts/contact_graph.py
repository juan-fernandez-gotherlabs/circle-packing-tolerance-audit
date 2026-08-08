#!/usr/bin/env python3
"""Self-contained contact geometry used by refinement and branch tracing.

This replaces the missing historical ``contact_flip.py`` module.  The contact
set is reconstructed from the published certificate, so no hidden sandbox path
or unpublished ``.npz`` seed is required.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
N = 26
LOWER = np.tile([1e-12, 1e-12, 1e-12], N)
UPPER = np.tile([1 - 1e-12, 1 - 1e-12, 0.499999999999], N)

Constraint = tuple[str, int, str] | tuple[str, int, int]
ALL: list[Constraint] = [
    ("W", i, side) for i in range(N) for side in ("L", "R", "B", "T")
] + [("P", i, j) for i in range(N) for j in range(i + 1, N)]


def pack(centers: np.ndarray, radii: np.ndarray) -> np.ndarray:
    value = np.empty(3 * N, dtype=float)
    value[0::3] = centers[:, 0]
    value[1::3] = centers[:, 1]
    value[2::3] = radii
    return value


def unpack(value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    value = np.asarray(value, dtype=float)
    centers = np.column_stack((value[0::3], value[1::3]))
    return centers, value[2::3].copy()


def load_csv(path: Path) -> np.ndarray:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    centers = np.array([[float(row["x"]), float(row["y"])] for row in rows])
    radii = np.array([float(row["radius"]) for row in rows])
    if centers.shape != (N, 2) or radii.shape != (N,):
        raise ValueError(f"{path}: expected {N} circles")
    return pack(centers, radii)


def gap_and_grad(value: np.ndarray, key: Constraint) -> tuple[float, np.ndarray]:
    value = np.asarray(value, dtype=float)
    gradient = np.zeros(3 * N, dtype=float)
    if key[0] == "W":
        _, i, side = key
        x, y, radius = value[3 * i : 3 * i + 3]
        if side == "L":
            gap = x - radius
            gradient[3 * i] = 1
        elif side == "R":
            gap = 1 - x - radius
            gradient[3 * i] = -1
        elif side == "B":
            gap = y - radius
            gradient[3 * i + 1] = 1
        elif side == "T":
            gap = 1 - y - radius
            gradient[3 * i + 1] = -1
        else:
            raise ValueError(key)
        gradient[3 * i + 2] = -1
        return float(gap), gradient

    _, i, j = key
    dx = value[3 * i] - value[3 * j]
    dy = value[3 * i + 1] - value[3 * j + 1]
    distance = float(np.hypot(dx, dy))
    if distance == 0:
        raise ZeroDivisionError(f"coincident centers for {key}")
    gap = distance - value[3 * i + 2] - value[3 * j + 2]
    ux, uy = dx / distance, dy / distance
    gradient[3 * i : 3 * i + 3] = (ux, uy, -1)
    gradient[3 * j : 3 * j + 3] = (-ux, -uy, -1)
    return float(gap), gradient


def values_jacobian(value: np.ndarray, keys: list[Constraint]):
    pairs = [gap_and_grad(value, key) for key in keys]
    return np.array([item[0] for item in pairs]), np.array([item[1] for item in pairs])


def detect_active(value: np.ndarray, threshold: float = 1e-7) -> list[Constraint]:
    active = [key for key in ALL if abs(gap_and_grad(value, key)[0]) < threshold]
    if len(active) != 3 * N:
        gaps = sorted((abs(gap_and_grad(value, key)[0]), key) for key in ALL)
        raise RuntimeError(
            f"expected {3 * N} active constraints, found {len(active)}; "
            f"nearest counts={[item[0] for item in gaps[:3 * N + 2]]}"
        )
    return active


def solve_graph(keys: list[Constraint], seed: np.ndarray, max_nfev: int = 10_000):
    # Lazy import keeps the exact-verification and graph-diagnostic path light;
    # SciPy is needed only when an actual nonlinear solve is requested.
    from scipy.optimize import least_squares

    def fun(value):
        return values_jacobian(value, keys)[0]

    def jac(value):
        return values_jacobian(value, keys)[1]

    return least_squares(
        fun,
        seed,
        jac=jac,
        bounds=(LOWER, UPPER),
        method="trf",
        xtol=3e-13,
        ftol=3e-13,
        gtol=3e-13,
        max_nfev=max_nfev,
        x_scale="jac",
    )


def default_state() -> tuple[np.ndarray, list[Constraint]]:
    seed = load_csv(ROOT / "data/certificates/exact.csv")
    active = detect_active(seed)
    result = solve_graph(active, seed)
    if result.cost > 1e-20:
        raise RuntimeError(f"contact solve did not converge: cost={result.cost}")
    return result.x, active


def metrics(value: np.ndarray, active: list[Constraint] | None = None) -> dict:
    if active is None:
        active = detect_active(value)
    all_gaps = np.array([gap_and_grad(value, key)[0] for key in ALL])
    _, radii = unpack(value)
    _, jacobian = values_jacobian(value, active)
    singular = np.linalg.svd(jacobian, compute_uv=False)
    objective = np.zeros(3 * N)
    objective[2::3] = 1
    # For constraints written as gap >= 0 and a maximization objective,
    # stationarity is grad(objective) + J.T @ lambda = 0.
    multipliers = np.linalg.solve(jacobian.T, -objective)
    return {
        "score": float(radii.sum()),
        "min_gap": float(all_gaps.min()),
        "active_constraints": len(active),
        "active_wall_contacts": sum(key[0] == "W" for key in active),
        "active_pair_contacts": sum(key[0] == "P" for key in active),
        "jacobian_rank": int(np.linalg.matrix_rank(jacobian)),
        "smallest_singular_value": float(singular[-1]),
        "condition_number": float(singular[0] / singular[-1]),
        "multiplier_min": float(multipliers.min()),
        "multiplier_max": float(multipliers.max()),
        "stationarity_inf_norm": float(np.max(np.abs(objective + jacobian.T @ multipliers))),
    }


def key_string(key: Constraint) -> str:
    return ":".join(map(str, key))


def parse_key(value: str) -> Constraint:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError(value)
    if parts[0] == "W":
        return ("W", int(parts[1]), parts[2])
    if parts[0] == "P":
        return ("P", int(parts[1]), int(parts[2]))
    raise ValueError(value)
