#!/usr/bin/env python3
"""Derive a nearby strict certificate from the published exact witness.

This is a sensitivity/reconstruction diagnostic, not an independent recovery
of ``data/certificates/exact.csv``.  The published witness supplies both the
seed and the detected contact graph, so byte or decimal identity is neither
claimed nor expected.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import mpmath as mp

import contact_graph as cg


def as_mp(value: float) -> mp.mpf:
    return mp.mpf(format(float(value), ".17g"))


def fixed(value: mp.mpf, places: int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    integer = mp.floor(value)
    fraction = mp.nint((value - integer) * mp.mpf(10) ** places)
    if fraction == mp.mpf(10) ** places:
        integer += 1
        fraction = 0
    return f"{sign}{int(integer)}.{int(fraction):0{places}d}"


def derive(output_dir: Path, dps: int = 120, places: int = 90) -> dict:
    mp.mp.dps = dps
    output_dir.mkdir(parents=True, exist_ok=True)
    float_root, keys = cg.default_state()
    z = [as_mp(item) for item in float_root]

    def fj(state):
        values = []
        jacobian = [[mp.mpf("0") for _ in range(3 * cg.N)] for __ in range(3 * cg.N)]
        for row, key in enumerate(keys):
            if key[0] == "W":
                _, i, side = key
                x, y, radius = state[3 * i : 3 * i + 3]
                if side == "L":
                    values.append(x - radius); jacobian[row][3 * i] = 1
                elif side == "R":
                    values.append(1 - x - radius); jacobian[row][3 * i] = -1
                elif side == "B":
                    values.append(y - radius); jacobian[row][3 * i + 1] = 1
                else:
                    values.append(1 - y - radius); jacobian[row][3 * i + 1] = -1
                jacobian[row][3 * i + 2] = -1
            else:
                _, i, j = key
                dx = state[3 * i] - state[3 * j]
                dy = state[3 * i + 1] - state[3 * j + 1]
                distance = mp.sqrt(dx * dx + dy * dy)
                values.append(distance - state[3 * i + 2] - state[3 * j + 2])
                ux, uy = dx / distance, dy / distance
                jacobian[row][3 * i] = ux; jacobian[row][3 * i + 1] = uy; jacobian[row][3 * i + 2] = -1
                jacobian[row][3 * j] = -ux; jacobian[row][3 * j + 1] = -uy; jacobian[row][3 * j + 2] = -1
        return mp.matrix(values), mp.matrix(jacobian)

    def gap(state, key):
        if key[0] == "W":
            _, i, side = key
            x, y, radius = state[3 * i : 3 * i + 3]
            return {"L": x - radius, "R": 1 - x - radius, "B": y - radius, "T": 1 - y - radius}[side]
        _, i, j = key
        dx = state[3 * i] - state[3 * j]
        dy = state[3 * i + 1] - state[3 * j + 1]
        return mp.sqrt(dx * dx + dy * dy) - state[3 * i + 2] - state[3 * j + 2]

    history = []
    for _ in range(12):
        values, jacobian = fj(z)
        residual = max(abs(item) for item in values)
        history.append(mp.nstr(residual, 35))
        if residual < mp.mpf("1e-100"):
            break
        delta = mp.lu_solve(jacobian, -values)
        z = [z[i] + delta[i] for i in range(3 * cg.N)]

    score = sum(z[2::3])
    quantum = mp.mpf(10) ** (-places)
    quantized = [mp.nint(item / quantum) * quantum for item in z]
    minimum_quantized_gap = min(gap(quantized, key) for key in cg.ALL)
    target_margin = mp.mpf("1e-75")
    shrink = max(mp.mpf("0"), target_margin - minimum_quantized_gap)
    strict = quantized[:]
    for i in range(cg.N):
        strict[3 * i + 2] -= shrink
    strict_gaps = [gap(strict, key) for key in cg.ALL]
    strict_score = sum(strict[2::3])

    csv_path = output_dir / "certificate.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["circle", "x", "y", "radius"])
        for i in range(cg.N):
            writer.writerow([i, fixed(strict[3 * i], places), fixed(strict[3 * i + 1], places), fixed(strict[3 * i + 2], places)])

    report = {
        "operation": "derive_nearby_strict_certificate",
        "source_certificate": "data/certificates/exact.csv",
        "independent_reconstruction": False,
        "byte_identical_to_source_claimed": False,
        "mp_dps": dps,
        "newton_history": history,
        "contact_graph_score": mp.nstr(score, 115),
        "strict_score": mp.nstr(strict_score, 115),
        "strict_min_gap": mp.nstr(min(strict_gaps), 85),
        "quantization_places": places,
        "uniform_radius_shrink": mp.nstr(shrink, 85),
        "num_active": len(keys),
        "num_constraints": len(cg.ALL),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Derive another nearby strict witness from the published certificate."
    )
    parser.add_argument("--output-dir", type=Path, default=cg.ROOT / "results/nearby_strict")
    parser.add_argument("--dps", type=int, default=120)
    args = parser.parse_args()
    print(json.dumps(derive(args.output_dir, args.dps), indent=2))
