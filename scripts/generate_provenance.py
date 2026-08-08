#!/usr/bin/env python3
"""Expand the frozen audit candidate list with source and license metadata."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKED = "2026-08-08"


def metadata(name: str, source: str) -> dict:
    common = {
        "candidate": name,
        "audit_source_label": source,
        "license_checked_on": CHECKED,
        "redistribution": "Only derived audit metrics are included; the upstream witness/code is not vendored.",
    }
    if name.startswith("Nuestro "):
        return {
            **common,
            "upstream": "ChatGPT conversation 6a6b0f23-f53c-83eb-8a83-b3d4cdaa383d and recovered local artifacts",
            "license": "MIT for repository code; certificate data released with this repository",
            "redistribution": "Included in data/ as the primary artifact.",
        }
    if name == "EurekAgent público":
        return {
            **common,
            "upstream": "https://github.com/THU-Team-Eureka/EurekAgent/blob/38585790ff56e7993aec322e0179ded8b101d82c/results/circle_packing/result.jsonl",
            "license": "AGPL-3.0 (GitHub repository license detection)",
        }
    if name.startswith("EinsteinArena:"):
        solution_id = source.rsplit(" ", 1)[-1]
        return {
            **common,
            "upstream": "https://einsteinarena.com/problems/circle-packing",
            "upstream_identifier": solution_id,
            "license": "No per-solution redistribution license identified",
        }
    if name.startswith("Packomania"):
        return {
            **common,
            "upstream": "https://www.packomania.com/csqv/txt/csqv26.txt",
            "license": "No explicit redistribution license identified",
        }
    if name.startswith("Tencent Hyra"):
        return {
            **common,
            "upstream": "https://github.com/Tencent-Hunyuan/Hyra-results/blob/main/AI4Science/packing_records/records/cirRsqu_n26.json",
            "license": "Apache-2.0 for Tencent-authored material; upstream LICENSE contains third-party qualifications",
        }
    if name.startswith("ThetaEvolve"):
        return {
            **common,
            "upstream": "https://github.com/ypwang61/ThetaEvolve/blob/main/Results/CirclePacking/data.json",
            "license": "Apache-2.0 (GitHub repository license detection)",
        }
    if name == "Station SOTA":
        return {
            **common,
            "upstream": "https://github.com/dualverse-ai/station/blob/main/example/research_circle_n26/station_sota.py",
            "license": "Apache-2.0 (GitHub repository license detection)",
        }
    if name == "AlphaZ-CORAL best_program":
        return {
            **common,
            "upstream": "https://github.com/Kurorz2004/alphaz-coral/blob/main/task1/result/best_program.py",
            "license": "No repository license detected",
        }
    if name.startswith("Jason Liang"):
        return {
            **common,
            "upstream": "https://github.com/jasonzliang/circle-packing-sota/blob/main/sota/ours/pck/csqv26.pck",
            "license": "No repository license detected",
        }
    return {**common, "upstream": source, "license": "Not determined"}


def generate() -> Path:
    audit = json.loads((ROOT / "data/audit/strict_leaderboard_audit.json").read_text())
    entries = [metadata(item["name"], item["source"]) for item in audit["candidates"]]
    entries.append(
        {
            "candidate": "Numaro reported n=26 claim",
            "audit_source_label": "NUMARO-2026-004",
            "upstream": "https://numaro.tech/research/circle-packing-unit-square-2026/",
            "license": "No witness or explicit data redistribution license identified",
            "license_checked_on": CHECKED,
            "redistribution": "Not included and not ranked because the n=26 witness was unavailable.",
        }
    )
    target = ROOT / "data/provenance.json"
    target.write_text(json.dumps({"generated_on": CHECKED, "entries": entries}, indent=2, ensure_ascii=False) + "\n")
    return target


if __name__ == "__main__":
    print(generate().relative_to(ROOT))
