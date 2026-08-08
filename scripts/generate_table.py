#!/usr/bin/env python3
"""Generate Markdown tables from the frozen audit snapshot."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def generate() -> Path:
    audit = json.loads((ROOT / "data/audit/strict_leaderboard_audit.json").read_text())
    lines = [
        "# Generated audit tables",
        "",
        f"Frozen audit date: **{audit['audit_date']}**. Candidates: **{audit['candidate_count']}**.",
        "",
        "> A rank here means rank inside the frozen, publicly auditable corpus. It is not a proof of global optimality and excludes claims without a downloadable witness.",
        "",
    ]

    for tolerance in ("0", "1e-10", "1e-6"):
        lines.extend(
            [
                f"## Ranking at tolerance `{tolerance}`",
                "",
                "| Rank | Candidate | Recomputed score | Source |",
                "| ---: | --- | ---: | --- |",
            ]
        )
        for rank, row in enumerate(audit["rankings"][tolerance], 1):
            lines.append(
                f"| {rank} | {row['name']} | `{row['score']}` | {row['source']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## All audited candidates across contracts",
            "",
            "| Candidate | Score | exact | `1e-10` | `1e-6` | Source |",
            "| --- | ---: | :---: | :---: | :---: | --- |",
        ]
    )
    for candidate in audit["candidates"]:
        checks = candidate["checks"]
        score = checks["0"]["score"]
        lines.append(
            "| {name} | `{score}` | {zero} | {ten} | {six} | {source} |".format(
                name=candidate["name"],
                score=score,
                zero=yes_no(checks["0"]["valid"]),
                ten=yes_no(checks["1e-10"]["valid"]),
                six=yes_no(checks["1e-6"]["valid"]),
                source=candidate["source"],
            )
        )
    lines.append("")

    target = ROOT / "results/audit_tables.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


if __name__ == "__main__":
    print(generate().relative_to(ROOT))
