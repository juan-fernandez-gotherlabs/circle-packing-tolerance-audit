#!/usr/bin/env python3
"""Count planned and completed transitions in the attached historical logs."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count(path: Path) -> dict:
    lines = path.read_text(errors="replace").splitlines()
    task_lines = [line for line in lines if line.startswith("TASKS ")]
    completed = [line for line in lines if line.startswith(("DONE ", "NONE "))]
    if len(task_lines) != 1:
        raise AssertionError(f"{path}: expected one TASKS line")
    match = re.fullmatch(r"TASKS (\d+)", task_lines[0])
    if match is None:
        raise AssertionError(task_lines[0])
    planned = int(match.group(1))
    return {
        "file": str(path.relative_to(ROOT)),
        "planned": planned,
        "completed_lines": len(completed),
        "complete": len(completed) == planned,
        "last_completion_line": completed[-1] if completed else None,
    }


def generate() -> Path:
    second = count(ROOT / "data/historical_search/multi_trace.log")
    third = count(ROOT / "data/historical_search/layer3_trace.log")
    if (second["planned"], second["completed_lines"]) != (312, 312):
        raise AssertionError(second)
    if (third["planned"], third["completed_lines"]) != (468, 468):
        raise AssertionError(third)
    document = {
        "first_layer_events_from_layer1_vertices_json": 78,
        "second_layer": second,
        "cumulative_through_second_layer": 78 + second["completed_lines"],
        "third_layer": third,
        "correction": "390 is cumulative through layers 1 and 2; the final attached third-layer log is complete.",
    }
    target = ROOT / "results/historical_search_counts.json"
    target.write_text(json.dumps(document, indent=2) + "\n")
    return target


if __name__ == "__main__":
    print(generate().relative_to(ROOT))
