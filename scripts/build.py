#!/usr/bin/env python3
"""Build the human-facing artifacts and optional full-evidence archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from decimal import Decimal, localcontext
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/leaderboard_audit.json"
EXACT = ROOT / "data/certificates/exact.csv"
PRIMARY_CANDIDATES = {
    "0": "Nuestro certificado exacto",
    "1e-10": "Nuestro candidato 1e-10",
    "1e-6": "Nuestro candidato 1e-6",
}
AUTHOR_CANDIDATES = frozenset(PRIMARY_CANDIDATES.values())
EVIDENCE_SOURCE_TAG = "v1.0.0"
EVIDENCE_SOURCE_COMMIT = "2359ee29d5de8747a124a5439779b8d4c553cce0"
EVIDENCE_ARCHIVE_SHA256 = "d55ec1eae5b50c0eb81b89da86fa520c9988d122cbe77465c180af1b30181f87"
EVIDENCE_PATHS = (
    "data/audit/AUDIT_REPORT_ES.md",
    "data/exact/high_precision_report.json",
    "data/exact/original_model_output.md",
    "data/exact/program_strict_reference.py",
    "data/exact/search_report.json",
    "data/exact/strict_high_precision.csv",
    "data/historical_search/",
    "data/tolerance_1e-10/coordinates_internal_1e10.csv",
    "data/tolerance_1e-10/original_model_output.md",
    "data/tolerance_1e-10/program.py",
    "data/tolerance_1e-6/coordinates_public_record.csv",
    "data/tolerance_1e-6/evaluator_compatibility.txt",
    "data/tolerance_1e-6/original_model_output.md",
    "data/tolerance_1e-6/program.py",
    "figures/exact_packing_contact_graph.png",
    "results/search_reproduction/",
)
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_audit() -> dict:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("snapshot_status") != "historical_observational_snapshot":
        raise AssertionError("leaderboard data must be labelled as an observational snapshot")
    if audit.get("end_to_end_reproducible") is not False:
        raise AssertionError("leaderboard snapshot must disclose that it is not end-to-end reproducible")
    for tolerance, expected in PRIMARY_CANDIDATES.items():
        author_rows = [
            row["name"]
            for row in audit["rankings"][tolerance]
            if row["name"] in AUTHOR_CANDIDATES
        ]
        if author_rows != [expected]:
            raise AssertionError(
                f"ranking {tolerance} must contain only {expected!r} from the author; "
                f"found {author_rows!r}"
            )
    return audit


def generate_table() -> Path:
    audit = load_audit()
    lines = [
        "# Historical comparison snapshot",
        "",
        f"Frozen audit date: **{audit['audit_date']}**. Candidates: **{audit['candidate_count']}**.",
        "",
        "> This is an observational snapshot, not an end-to-end reproducible leaderboard. "
        "The acquisition code and all source payloads were not preserved. It must not be cited "
        "as independent proof of rank.",
        "",
        "> Each section contains exactly one author certificate and external candidates checked "
        "under the same rational tolerance. The author's other certificates are excluded.",
        "",
    ]
    for tolerance in ("0", "1e-10", "1e-6"):
        rows = audit["rankings"][tolerance]
        lines.extend(
            [
                f"## Snapshot at rational tolerance `{tolerance}`",
                "",
                "| Snapshot position | Candidate | Stored recomputed score | Source |",
                "| ---: | --- | ---: | --- |",
            ]
        )
        for rank, row in enumerate(rows, 1):
            lines.append(f"| {rank} | {row['name']} | `{row['score']}` | {row['source']} |")
        lines.append("")

    lines.extend(
        [
            "## Stored validity matrix",
            "",
            "> This matrix reports stored checks; it is not a cross-tolerance ranking and its scores "
            "must not be compared across columns.",
            "",
            "| Candidate | Score | exact | `1e-10` | `1e-6` | Source |",
            "| --- | ---: | :---: | :---: | :---: | --- |",
        ]
    )
    for candidate in audit["candidates"]:
        checks = candidate["checks"]
        yes_no = lambda value: "yes" if value else "no"
        lines.append(
            "| {name} | `{score}` | {zero} | {ten} | {six} | {source} |".format(
                name=candidate["name"],
                score=checks["0"]["score"],
                zero=yes_no(checks["0"]["valid"]),
                ten=yes_no(checks["1e-10"]["valid"]),
                six=yes_no(checks["1e-6"]["valid"]),
                source=candidate["source"],
            )
        )
    target = ROOT / "results/audit_tables.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def _certificate_rows():
    with EXACT.open(newline="", encoding="utf-8") as handle:
        return [
            (Decimal(row["x"]), Decimal(row["y"]), Decimal(row["radius"]))
            for row in csv.DictReader(handle)
        ]


def _contacts(rows):
    pairs, walls = [], []
    with localcontext() as ctx:
        ctx.prec = 120
        for i, (x, y, radius) in enumerate(rows):
            gaps = {"L": x - radius, "R": 1 - x - radius, "B": y - radius, "T": 1 - y - radius}
            walls.extend((i, side) for side, gap in gaps.items() if abs(gap) < Decimal("1e-50"))
        for i, (xi, yi, ri) in enumerate(rows):
            for j in range(i + 1, len(rows)):
                xj, yj, rj = rows[j]
                gap = ((xi - xj) ** 2 + (yi - yj) ** 2).sqrt() - ri - rj
                if abs(gap) < Decimal("1e-50"):
                    pairs.append((i, j))
    return pairs, walls


def generate_visualization() -> Path:
    size, pad, scale = 900, 60, 780
    rows = _certificate_rows()
    pairs, walls = _contacts(rows)
    if (len(pairs), len(walls)) != (58, 20):
        raise AssertionError(f"expected 58 pair and 20 wall contacts, got {len(pairs)} and {len(walls)}")

    def screen(x, y):
        return pad + float(x) * scale, pad + (1.0 - float(y)) * scale

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size + 80}" viewBox="0 0 {size} {size + 80}" role="img" aria-labelledby="title desc">',
        '<title id="title">Exact n=26 circle packing with contact graph</title>',
        '<desc id="desc">Twenty-six circles in the unit square. Red edges show 58 circle contacts and orange spokes show 20 wall contacts.</desc>',
        '<rect width="100%" height="100%" fill="#fbfcfe"/>',
        f'<rect x="{pad}" y="{pad}" width="{scale}" height="{scale}" fill="#ffffff" stroke="#111827" stroke-width="4"/>',
        '<g id="pair-contacts" stroke="#dc2626" stroke-width="2.3" stroke-opacity="0.72">',
    ]
    for i, j in pairs:
        x1, y1 = screen(rows[i][0], rows[i][1]); x2, y2 = screen(rows[j][0], rows[j][1])
        parts.append(f'<line x1="{x1:.6f}" y1="{y1:.6f}" x2="{x2:.6f}" y2="{y2:.6f}"/>')
    parts.extend(["</g>", '<g id="wall-contacts" stroke="#f59e0b" stroke-width="3" stroke-dasharray="7 5">'])
    for i, side in walls:
        x, y = screen(rows[i][0], rows[i][1])
        tx = pad if side == "L" else pad + scale if side == "R" else x
        ty = pad + scale if side == "B" else pad if side == "T" else y
        parts.append(f'<line x1="{x:.6f}" y1="{y:.6f}" x2="{tx:.6f}" y2="{ty:.6f}"/>')
    parts.extend(["</g>", '<g id="circles" fill="#60a5fa" fill-opacity="0.35" stroke="#1d4ed8" stroke-width="2">'])
    for x, y, radius in rows:
        cx, cy = screen(x, y)
        parts.append(f'<circle cx="{cx:.6f}" cy="{cy:.6f}" r="{float(radius) * scale:.6f}"/>')
    parts.extend(["</g>", '<g id="labels" fill="#0f172a" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="13" text-anchor="middle" dominant-baseline="central">'])
    for i, (x, y, _) in enumerate(rows):
        cx, cy = screen(x, y)
        parts.append(f'<text x="{cx:.6f}" y="{cy:.6f}">{escape(str(i))}</text>')
    parts.extend(
        [
            "</g>",
            f'<text x="{pad}" y="{size + 32}" font-family="system-ui, sans-serif" font-size="18" fill="#111827">n=26 exact finite-decimal certificate — 58 pair contacts + 20 wall contacts</text>',
            f'<line x1="{pad}" y1="{size + 58}" x2="{pad + 36}" y2="{size + 58}" stroke="#dc2626" stroke-width="3"/><text x="{pad + 46}" y="{size + 64}" font-family="system-ui, sans-serif" font-size="15">circle contact</text>',
            f'<line x1="{pad + 220}" y1="{size + 58}" x2="{pad + 256}" y2="{size + 58}" stroke="#f59e0b" stroke-width="3" stroke-dasharray="7 5"/><text x="{pad + 266}" y="{size + 64}" font-family="system-ui, sans-serif" font-size="15">wall contact</text>',
            "</svg>",
        ]
    )
    target = ROOT / "figures/exact_packing_contact_graph.svg"
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return target


def generate_manifest() -> Path:
    target = ROOT / "SHA256SUMS"
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).split(b"\0")
    unexpected = sorted(path.decode("utf-8") for path in untracked if path)
    if unexpected:
        raise RuntimeError(
            "refusing to generate SHA256SUMS with untracked files: "
            + ", ".join(unexpected)
        )

    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    relative_paths = sorted(
        Path(path.decode("utf-8"))
        for path in tracked
        if path and path.decode("utf-8") != target.name
    )
    missing = [str(path) for path in relative_paths if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(
            "refusing to generate SHA256SUMS with missing tracked files: "
            + ", ".join(missing)
        )
    target.write_text(
        "".join(
            f"{digest_file(ROOT / path)}  {path}\n"
            for path in relative_paths
        ),
        encoding="utf-8",
    )
    return target


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o644 << 16
    return info


def package_evidence(
    output: Path, source_tag: str = EVIDENCE_SOURCE_TAG, source_repo: Path = ROOT
) -> tuple[Path, Path]:
    """Package bulky v1.0 evidence from a pinned and tag-checked commit."""
    resolved_tag = subprocess.check_output(
        ["git", "rev-parse", f"{source_tag}^{{commit}}"], cwd=source_repo, text=True
    ).strip()
    if source_tag != EVIDENCE_SOURCE_TAG or resolved_tag != EVIDENCE_SOURCE_COMMIT:
        raise RuntimeError(
            f"refusing evidence source {source_tag} -> {resolved_tag}; expected "
            f"{EVIDENCE_SOURCE_TAG} -> {EVIDENCE_SOURCE_COMMIT}"
        )
    tar_bytes = subprocess.check_output(
        ["git", "archive", "--format=tar", EVIDENCE_SOURCE_COMMIT, "--", *EVIDENCE_PATHS],
        cwd=source_repo,
    )
    payloads = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as source:
        for member in source.getmembers():
            if member.isfile():
                handle = source.extractfile(member)
                assert handle is not None
                payloads[member.name] = handle.read()
    if len(payloads) != 180:
        raise AssertionError(f"expected 180 evidence files from {source_tag}, found {len(payloads)}")
    entries = []
    for path, value in sorted(payloads.items()):
        entries.append({"path": path, "sha256": digest_bytes(value), "bytes": len(value)})
    manifest = (
        json.dumps(
            {
                "schema_version": 1,
                "source_tag": EVIDENCE_SOURCE_TAG,
                "source_commit": EVIDENCE_SOURCE_COMMIT,
                "file_count": len(entries),
                "files": entries,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = "circle-packing-full-evidence-v1.1.0/"
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr(_zip_info(prefix + "MANIFEST.json"), manifest)
        for path in sorted(payloads):
            archive.writestr(_zip_info(prefix + path), payloads[path])
    archive_digest = digest_file(output)
    if archive_digest != EVIDENCE_ARCHIVE_SHA256:
        raise AssertionError(
            f"evidence archive digest changed: {archive_digest}; "
            f"expected {EVIDENCE_ARCHIVE_SHA256}"
        )
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{archive_digest}  {output.name}\n", encoding="utf-8")
    return output, checksum


def generate_all() -> list[Path]:
    outputs = [generate_table(), generate_visualization()]
    outputs.append(generate_manifest())
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-archive", type=Path)
    parser.add_argument("--source-tag", default="v1.0.0")
    parser.add_argument("--source-repo", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    generated = generate_all()
    if args.evidence_archive:
        generated.extend(package_evidence(args.evidence_archive, args.source_tag, args.source_repo))
    print(json.dumps([str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path) for path in generated], indent=2))
