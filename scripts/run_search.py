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

import contact_graph as cg
from trace_graph import trace_state


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
    parser.add_argument("--output", type=Path, default=cg.ROOT / "results/search_reproduction")
    parser.add_argument("--max-bases", default="4,6", help="comma-separated base counts for subsequent layers")
    parser.add_argument("--max-transitions", type=int, help="smoke-test limit")
    args = parser.parse_args()
    limits = [int(value) for value in args.max_bases.split(",") if value]
    print(json.dumps(run(args.depth, args.output, limits, args.max_transitions), indent=2))
