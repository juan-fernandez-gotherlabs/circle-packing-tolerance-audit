#!/usr/bin/env python3
"""Generate SHA-256 hashes for the citable data artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ("data", "figures", "results")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def generate() -> Path:
    target = ROOT / "SHA256SUMS"
    paths = []
    for dirname in INCLUDE:
        paths.extend(p for p in (ROOT / dirname).rglob("*") if p.is_file())
    paths = sorted(p for p in paths if p != target)
    target.write_text(
        "".join(f"{digest(path)}  {path.relative_to(ROOT)}\n" for path in paths),
        encoding="utf-8",
    )
    return target


if __name__ == "__main__":
    print(generate().relative_to(ROOT))
