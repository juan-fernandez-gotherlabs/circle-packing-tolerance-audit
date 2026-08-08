#!/usr/bin/env python3
"""Render the exact certificate and its 78-contact graph as deterministic SVG."""

from __future__ import annotations

import csv
from decimal import Decimal, localcontext
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SIZE = 900
PAD = 60
SCALE = SIZE - 2 * PAD


def load_rows():
    with (ROOT / "data/exact/certificate.csv").open(newline="") as handle:
        return [
            (Decimal(row["x"]), Decimal(row["y"]), Decimal(row["radius"]))
            for row in csv.DictReader(handle)
        ]


def screen(x: Decimal, y: Decimal) -> tuple[float, float]:
    return PAD + float(x) * SCALE, PAD + (1.0 - float(y)) * SCALE


def contacts(rows):
    threshold = Decimal("1e-50")
    pair_contacts = []
    wall_contacts = []
    with localcontext() as ctx:
        ctx.prec = 120
        for i, (x, y, r) in enumerate(rows):
            walls = {
                "L": x - r,
                "R": Decimal(1) - x - r,
                "B": y - r,
                "T": Decimal(1) - y - r,
            }
            wall_contacts.extend((i, side) for side, gap in walls.items() if abs(gap) < threshold)
        for i, (xi, yi, ri) in enumerate(rows):
            for j in range(i + 1, len(rows)):
                xj, yj, rj = rows[j]
                gap = ((xi - xj) ** 2 + (yi - yj) ** 2).sqrt() - ri - rj
                if abs(gap) < threshold:
                    pair_contacts.append((i, j))
    return pair_contacts, wall_contacts


def generate() -> Path:
    rows = load_rows()
    pairs, walls = contacts(rows)
    if (len(pairs), len(walls)) != (58, 20):
        raise AssertionError(f"expected 58 pair and 20 wall contacts, got {len(pairs)} and {len(walls)}")

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE + 80}" viewBox="0 0 {SIZE} {SIZE + 80}" role="img" aria-labelledby="title desc">',
        '<title id="title">Exact n=26 circle packing with contact graph</title>',
        '<desc id="desc">Twenty-six circles in the unit square. Red edges show 58 circle contacts and orange spokes show 20 wall contacts.</desc>',
        '<rect width="100%" height="100%" fill="#fbfcfe"/>',
        f'<rect x="{PAD}" y="{PAD}" width="{SCALE}" height="{SCALE}" fill="#ffffff" stroke="#111827" stroke-width="4"/>',
        '<g id="pair-contacts" stroke="#dc2626" stroke-width="2.3" stroke-opacity="0.72">',
    ]
    for i, j in pairs:
        x1, y1 = screen(rows[i][0], rows[i][1])
        x2, y2 = screen(rows[j][0], rows[j][1])
        parts.append(f'<line x1="{x1:.6f}" y1="{y1:.6f}" x2="{x2:.6f}" y2="{y2:.6f}"/>')
    parts.append("</g>")
    parts.append('<g id="wall-contacts" stroke="#f59e0b" stroke-width="3" stroke-dasharray="7 5">')
    for i, side in walls:
        x, y = screen(rows[i][0], rows[i][1])
        tx = PAD if side == "L" else PAD + SCALE if side == "R" else x
        ty = PAD + SCALE if side == "B" else PAD if side == "T" else y
        parts.append(f'<line x1="{x:.6f}" y1="{y:.6f}" x2="{tx:.6f}" y2="{ty:.6f}"/>')
    parts.append("</g>")
    parts.append('<g id="circles" fill="#60a5fa" fill-opacity="0.35" stroke="#1d4ed8" stroke-width="2">')
    for i, (x, y, r) in enumerate(rows):
        cx, cy = screen(x, y)
        radius = float(r) * SCALE
        parts.append(f'<circle cx="{cx:.6f}" cy="{cy:.6f}" r="{radius:.6f}"/>')
    parts.append("</g>")
    parts.append('<g id="labels" fill="#0f172a" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="13" text-anchor="middle" dominant-baseline="central">')
    for i, (x, y, _) in enumerate(rows):
        cx, cy = screen(x, y)
        parts.append(f'<text x="{cx:.6f}" y="{cy:.6f}">{escape(str(i))}</text>')
    parts.extend(
        [
            "</g>",
            f'<text x="{PAD}" y="{SIZE + 32}" font-family="system-ui, sans-serif" font-size="18" fill="#111827">n=26 exact finite-decimal certificate — 58 pair contacts + 20 wall contacts</text>',
            f'<line x1="{PAD}" y1="{SIZE + 58}" x2="{PAD + 36}" y2="{SIZE + 58}" stroke="#dc2626" stroke-width="3"/><text x="{PAD + 46}" y="{SIZE + 64}" font-family="system-ui, sans-serif" font-size="15">circle contact</text>',
            f'<line x1="{PAD + 220}" y1="{SIZE + 58}" x2="{PAD + 256}" y2="{SIZE + 58}" stroke="#f59e0b" stroke-width="3" stroke-dasharray="7 5"/><text x="{PAD + 266}" y="{SIZE + 64}" font-family="system-ui, sans-serif" font-size="15">wall contact</text>',
            "</svg>",
        ]
    )
    target = ROOT / "figures/exact_packing_contact_graph.svg"
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    print(generate().relative_to(ROOT))
