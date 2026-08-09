#!/usr/bin/env python3
"""Build or check the deterministic publication PDFs.

This is a manual release gate. It deliberately depends on the documented
publication toolchain and does not require a GitHub Actions workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGURE_SOURCES = (
    Path("figures/exact_packing_contact_graph.svg"),
    Path("figures/tolerance_certificates.svg"),
    Path("figures/tolerance_rankings.svg"),
)
PREPRINT_SOURCE = Path("preprint/circle_packing_n26_preprint.tex")
PREPRINT_PDF = PREPRINT_SOURCE.with_suffix(".pdf")
PUBLICATION_PDFS = tuple(path.with_suffix(".pdf") for path in FIGURE_SOURCES) + (
    PREPRINT_PDF,
)
REPRODUCIBLE_ENV = {
    "SOURCE_DATE_EPOCH": "946684800",
    "TZ": "UTC",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"required publication tool is unavailable: {name}")
    return path


def run(command: list[str], *, cwd: Path = ROOT, capture: bool = False) -> str:
    environment = os.environ.copy()
    environment.update(REPRODUCIBLE_ENV)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    return result.stdout if capture else ""


def toolchain() -> dict[str, str]:
    commands = {
        "rsvg-convert": [require_tool("rsvg-convert"), "--version"],
        "latexmk": [require_tool("latexmk"), "-v"],
        "pdflatex": [require_tool("pdflatex"), "--version"],
        "pdfinfo": [require_tool("pdfinfo"), "-v"],
    }
    versions = {}
    for name, command in commands.items():
        versions[name] = run(command, capture=True).splitlines()[0]
    return versions


def build_into(staging: Path) -> dict[Path, Path]:
    generated: dict[Path, Path] = {}
    figures = staging / "figures"
    preprint = staging / "preprint"
    figures.mkdir(parents=True)
    preprint.mkdir(parents=True)

    converter = require_tool("rsvg-convert")
    for relative in FIGURE_SOURCES:
        output = staging / relative.with_suffix(".pdf")
        run([converter, "-f", "pdf", "-o", str(output), str(ROOT / relative)])
        generated[relative.with_suffix(".pdf")] = output

    copied_source = preprint / PREPRINT_SOURCE.name
    shutil.copy2(ROOT / PREPRINT_SOURCE, copied_source)
    run(
        [
            require_tool("latexmk"),
            "-norc",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-synctex=0",
            copied_source.name,
        ],
        cwd=preprint,
    )
    generated[PREPRINT_PDF] = preprint / PREPRINT_PDF.name
    return generated


def validate_pdfs(paths: dict[Path, Path]) -> None:
    inspector = require_tool("pdfinfo")
    for relative, path in paths.items():
        output = run([inspector, str(path)], capture=True)
        if "Pages:" not in output or "PDF version:" not in output:
            raise AssertionError(f"pdfinfo did not validate {relative}")


def compare_pdfs(generated: dict[Path, Path]) -> None:
    mismatches = []
    for relative in PUBLICATION_PDFS:
        expected = ROOT / relative
        actual = generated[relative]
        if not expected.is_file() or expected.read_bytes() != actual.read_bytes():
            expected_hash = digest(expected) if expected.is_file() else "missing"
            mismatches.append(
                f"{relative}: versioned={expected_hash}, rebuilt={digest(actual)}"
            )
    if mismatches:
        raise AssertionError("publication PDF mismatch:\n" + "\n".join(mismatches))


def refresh_manifest() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from build import generate_manifest

    generate_manifest()


def require_clean_worktree() -> None:
    status = run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], capture=True
    )
    if status:
        raise AssertionError("release gate left a non-clean worktree:\n" + status)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="replace versioned PDFs")
    mode.add_argument("--check", action="store_true", help="compare from a clean commit")
    args = parser.parse_args()

    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(
            f"publication gate requires CPython 3.12, found {sys.version.split()[0]}"
        )
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], capture=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("publication gate requires a full Git clone") from error

    versions = toolchain()
    run([str(ROOT / "verify_all.sh")])
    with tempfile.TemporaryDirectory(prefix="circle-packing-publication-") as directory:
        generated = build_into(Path(directory))
        validate_pdfs(generated)
        if args.check:
            compare_pdfs(generated)
        else:
            for relative, source in generated.items():
                shutil.copy2(source, ROOT / relative)
            refresh_manifest()

    if args.check:
        require_clean_worktree()
    print("PUBLICATION PDF GATE: PASS")
    for name, version in versions.items():
        print(f"{name}: {version}")
    for relative in PUBLICATION_PDFS:
        print(f"{digest(ROOT / relative)}  {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
