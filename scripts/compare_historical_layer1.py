#!/usr/bin/env python3
"""Compare a regenerated first layer with the attached historical summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import contact_graph as cg


def compare(regenerated: Path, output: Path) -> dict:
    historical = json.loads((cg.ROOT / "data/historical_search/layer1_vertices.json").read_text())
    current = json.loads(regenerated.read_text())
    old = {item["drop"]: item for item in historical}
    new = {item["drop"]: item for item in current["events"]}
    common = sorted(old.keys() & new.keys())
    score_differences = [abs(old[key]["score"] - new[key]["metrics"]["score"]) for key in common]
    disagreements = [key for key in common if old[key]["local_max"] != new[key]["local_max"]]
    report = {
        "historical_events": len(old),
        "regenerated_events": len(new),
        "matching_drop_labels": len(common),
        "historical_local_maxima": sum(item["local_max"] for item in old.values()),
        "regenerated_local_maxima": sum(item["local_max"] for item in new.values()),
        "local_max_classification_disagreements": disagreements,
        "maximum_absolute_score_difference": max(score_differences),
        "interpretation": "The clean reimplementation reproduces every released contact and every local-maximum classification. Small endpoint score differences are numerical continuation differences.",
    }
    if len(common) != 78 or disagreements or report["maximum_absolute_score_difference"] >= 1e-9:
        raise AssertionError(report)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("regenerated", type=Path)
    parser.add_argument("--output", type=Path, default=cg.ROOT / "results/search_layer1_validation.json")
    args = parser.parse_args()
    print(json.dumps(compare(args.regenerated, args.output), indent=2))
