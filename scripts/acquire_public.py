#!/usr/bin/env python3
"""Acquire and uniformly audit public n=26 circle-packing witnesses.

Every remote payload is checked against ``data/public_sources.json`` before it
is parsed.  Python files and notebooks are treated as syntax/data only: no
third-party code is imported or executed.  Feasibility decisions are delegated
to the repository's exact-rational verifier.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import urllib.request
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from verifier import decimal_string, load_certificate, rational, verify_circles


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/public_sources.json"
DEFAULT_CACHE = ROOT / "work/public_corpus/cache"
DEFAULT_JSON = ROOT / "results/public_corpus_audit.json"
DEFAULT_MARKDOWN = ROOT / "results/public_corpus_audit.md"
CONTRACTS = {
    "0": Fraction(0),
    "1e-10": Fraction(1, 10**10),
    "1e-6": Fraction(1, 10**6),
}
AUTHOR_CERTIFICATES = {
    "0": ("author_exact", "Author exact certificate", ROOT / "data/certificates/exact.csv"),
    "1e-10": (
        "author_1e-10",
        "Author 1e-10 certificate",
        ROOT / "data/certificates/tolerance_1e-10.csv",
    ),
    "1e-6": (
        "author_1e-6",
        "Author 1e-6 certificate",
        ROOT / "data/certificates/tolerance_1e-6.csv",
    ),
}


class AcquisitionError(RuntimeError):
    """Raised when a source cannot be authenticated or parsed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json_numbers(payload: bytes | str) -> Any:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return json.loads(payload, parse_float=str, parse_int=str)


def as_fraction(value: str | int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return rational(str(value))


def candidate(
    candidate_id: str,
    name: str,
    source_id: str,
    circles: list[tuple[Any, Any, Any]],
    reported_score: str | None = None,
) -> dict[str, Any]:
    normalized = [tuple(as_fraction(value) for value in circle) for circle in circles]
    if len(normalized) != 26:
        raise AcquisitionError(f"{name}: expected 26 circles, found {len(normalized)}")
    if any(len(circle) != 3 for circle in normalized):
        raise AcquisitionError(f"{name}: every circle must contain x, y, and radius")
    if any(radius <= 0 for _, _, radius in normalized):
        raise AcquisitionError(f"{name}: radii must be positive")
    return {
        "id": candidate_id,
        "name": name,
        "source_id": source_id,
        "circles": normalized,
        "reported_score": reported_score,
    }


def _ast_number(node: ast.AST, source: str) -> Any:
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_ast_number(element, source) for element in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _ast_number(node.operand, source)
        if isinstance(value, list):
            raise AcquisitionError("unexpected unary operator on a sequence")
        return ("-" if isinstance(node.op, ast.USub) else "") + str(value)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        segment = ast.get_source_segment(source, node)
        if segment is None:
            raise AcquisitionError("could not recover a numeric source token")
        return segment.strip()
    if isinstance(node, ast.Call) and node.args:
        # Handles np.array([...]), np.float64(...), float(...), and equivalent
        # wrappers without importing or executing the source file.
        return _ast_number(node.args[0], source)
    raise AcquisitionError(f"unsupported numeric syntax: {ast.dump(node, include_attributes=False)}")


def _assignments(source: str, names: set[str]) -> dict[str, Any]:
    tree = ast.parse(source)
    found: dict[str, Any] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                found[target.id] = _ast_number(node.value, source)
    missing = names - found.keys()
    if missing:
        raise AcquisitionError(f"missing assignments: {', '.join(sorted(missing))}")
    return found


def parse_alphaevolve_notebook(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    notebook = load_json_numbers(payload)
    cell_source = None
    for cell in notebook.get("cells", []):
        text = "".join(cell.get("source", []))
        if "centers_26 =" in text and "radii_26 =" in text:
            cell_source = text
            break
    if cell_source is None:
        raise AcquisitionError("AlphaEvolve notebook has no n=26 data cell")
    values = _assignments(cell_source, {"centers_26", "radii_26"})
    centers, radii = values["centers_26"], values["radii_26"]
    circles = [(center[0], center[1], radius) for center, radius in zip(centers, radii)]
    return [candidate("alphaevolve_v2", "AlphaEvolve v2", source["id"], circles)]


def parse_theta_json(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    entries = load_json_numbers(payload)
    include = set(source["include_names"])
    parsed = []
    for entry in entries:
        name = entry["name"]
        if name not in include:
            continue
        values = entry["list"]
        if name == "8B-w_RL@65-Formal":
            centers, radii = values
            circles = [(center[0], center[1], radius) for center, radius in zip(centers, radii)]
        else:
            circles = values
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        parsed.append(candidate(f"theta_{slug}", f"Theta corpus: {name}", source["id"], circles))
    missing = include - {row["name"].removeprefix("Theta corpus: ") for row in parsed}
    if missing:
        raise AcquisitionError(f"ThetaEvolve payload is missing: {', '.join(sorted(missing))}")
    return parsed


def parse_eurek_jsonl(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    lines = [line for line in payload.decode("utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise AcquisitionError(f"EurekAgent: expected one JSONL record, found {len(lines)}")
    row = load_json_numbers(lines[0])
    solution = row["solution"]
    circles = [
        (center[0], center[1], radius)
        for center, radius in zip(solution["centers"], solution["radii"])
    ]
    return [
        candidate(
            "eurekagent",
            "EurekAgent",
            source["id"],
            circles,
            reported_score=str(row["score"]),
        )
    ]


def parse_hyra_json(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    row = load_json_numbers(payload)
    half = Fraction(1, 2)
    circles = [
        (as_fraction(x) + half, as_fraction(y) + half, as_fraction(radius))
        for x, y, radius in row["pieces"]
    ]
    return [
        candidate(
            "hyra",
            "Hyra",
            source["id"],
            circles,
            reported_score=str(row["sum_s_full"]),
        )
    ]


def parse_station_python(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    text = payload.decode("utf-8")
    circles = _assignments(text, {"CIRCLE_N26"})["CIRCLE_N26"]
    return [candidate("station", "Station", source["id"], circles)]


def parse_packomania_txt(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    text = payload.decode("utf-8")
    circles = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[0].isdigit():
            _, x, y, radius = fields
            circles.append((as_fraction(x) + Fraction(1, 2), as_fraction(y) + Fraction(1, 2), radius))
    score_match = re.search(r"sumradii\s*=\s*([0-9.]+)", text)
    score = score_match.group(1) if score_match else None
    return [candidate("packomania", "Packomania csqv26", source["id"], circles, score)]


def parse_csqv_pck(payload: bytes, source: dict[str, Any]) -> list[dict[str, Any]]:
    lines = [line.strip() for line in payload.decode("utf-8").splitlines() if line.strip()]
    circles = []
    for line in lines[2:]:
        fields = line.split()
        if len(fields) != 3:
            raise AcquisitionError(f"Jason corpus: malformed coordinate line {line!r}")
        x, y, radius = fields
        circles.append((as_fraction(x) + Fraction(1, 2), as_fraction(y) + Fraction(1, 2), radius))
    return [candidate("jason_liang", "Jason Liang csqv26", source["id"], circles)]


PARSERS: dict[str, Callable[[bytes, dict[str, Any]], list[dict[str, Any]]]] = {
    "alphaevolve_notebook": parse_alphaevolve_notebook,
    "theta_json": parse_theta_json,
    "eurek_jsonl": parse_eurek_jsonl,
    "hyra_json": parse_hyra_json,
    "station_python": parse_station_python,
    "packomania_txt": parse_packomania_txt,
    "csqv_pck": parse_csqv_pck,
}


def download_and_authenticate(
    source: dict[str, Any],
    cache_dir: Path,
    offline: bool,
    allow_mutable_drift: bool,
) -> tuple[bytes, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / source["artifact_filename"]
    if offline:
        if not path.is_file():
            raise AcquisitionError(f"offline cache miss: {path}")
        payload = path.read_bytes()
    else:
        request = urllib.request.Request(
            source["url"], headers={"User-Agent": "circle-packing-tolerance-audit/1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
        except Exception as urllib_error:  # macOS framework Python may lack a configured CA bundle
            try:
                completed = subprocess.run(
                    [
                        "curl",
                        "--fail",
                        "--location",
                        "--silent",
                        "--show-error",
                        "--retry",
                        "2",
                        source["url"],
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                payload = completed.stdout
            except (FileNotFoundError, subprocess.CalledProcessError) as curl_error:
                raise AcquisitionError(
                    f"{source['id']}: download failed with urllib ({urllib_error}) "
                    f"and curl ({curl_error})"
                ) from curl_error
        path.write_bytes(payload)

    actual = sha256_bytes(payload)
    matches = actual == source["sha256"]
    if not matches and not (allow_mutable_drift and not source["immutable"]):
        qualifier = "mutable " if not source["immutable"] else ""
        raise AcquisitionError(
            f"{source['id']}: {qualifier}payload SHA-256 changed: {actual}; "
            f"expected {source['sha256']}"
        )
    return payload, {
        "source_id": source["id"],
        "project": source["project"],
        "kind": source["kind"],
        "url": source["url"],
        "commit": source.get("commit"),
        "expected_sha256": source["sha256"],
        "actual_sha256": actual,
        "hash_matches": matches,
        "immutable": source["immutable"],
        "license": source["license"],
        "bytes": len(payload),
        "acquisition": "authenticated_download_or_cache",
    }


def native_binary64_check(row: dict[str, Any], evaluator: str) -> dict[str, Any]:
    try:
        import numpy as np
    except ImportError as error:  # pragma: no cover - reference environment includes NumPy
        raise AcquisitionError("NumPy is required for source-native compatibility checks") from error

    circles = row["circles"]
    centers = np.array([[float(x), float(y)] for x, y, _ in circles], dtype=float)
    radii = np.array([float(radius) for _, _, radius in circles], dtype=float)
    score = float(np.sum(radii))

    if evaluator == "alphaevolve_binary64_zero":
        valid = bool(
            ((radii[:, None] <= centers) & (centers <= 1 - radii[:, None])).all()
            and (radii >= 0).all()
        )
        if valid:
            for i in range(26):
                for j in range(i + 1, 26):
                    distance = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if radii[i] + radii[j] > distance:
                        valid = False
                        break
                if not valid:
                    break
        contract = "independent binary64 reimplementation of the notebook's zero-tolerance check"
    elif evaluator == "eurekagent_binary64_1e-6":
        atol = 1e-6
        reported = float(row["reported_score"] or score)
        valid = bool((radii >= 0).all() and np.isclose(score, reported, atol=atol))
        if valid:
            for i, (x, y) in enumerate(centers):
                radius = radii[i]
                if x - radius < -atol or x + radius > 1 + atol or y - radius < -atol or y + radius > 1 + atol:
                    valid = False
                    break
        if valid:
            for i in range(26):
                for j in range(i + 1, 26):
                    distance = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if distance < radii[i] + radii[j] - atol:
                        valid = False
                        break
                if not valid:
                    break
        contract = "independent binary64 reimplementation of adapted_validate_packing(atol=1e-6)"
    else:
        raise AcquisitionError(f"unsupported source-native evaluator: {evaluator}")

    return {
        "evaluator": evaluator,
        "valid": valid,
        "binary64_score": format(score, ".17g"),
        "interpretation": contract,
        "third_party_code_executed": False,
    }


def public_evaluation(row: dict[str, Any], source: dict[str, Any]) -> tuple[dict[str, Any], Fraction]:
    checks = {label: verify_circles(row["circles"], tolerance) for label, tolerance in CONTRACTS.items()}
    score_fraction = sum((radius for _, _, radius in row["circles"]), Fraction())
    output = {
        "id": row["id"],
        "name": row["name"],
        "source_id": row["source_id"],
        "reported_score": row["reported_score"],
        "recomputed_score": decimal_string(score_fraction),
        "checks": checks,
    }
    if source.get("native_evaluator"):
        output["source_native_compatibility"] = native_binary64_check(row, source["native_evaluator"])
    return output, score_fraction


def _author_row(tolerance_label: str) -> tuple[dict[str, Any], Fraction]:
    candidate_id, name, path = AUTHOR_CERTIFICATES[tolerance_label]
    circles = load_certificate(path)
    score = sum((radius for _, _, radius in circles), Fraction())
    check = verify_circles(circles, CONTRACTS[tolerance_label])
    return {
        "id": candidate_id,
        "name": name,
        "source_id": "this_repository",
        "score": check["score"],
        "valid": check["valid"],
    }, score


def acquire(
    manifest_path: Path = DEFAULT_MANIFEST,
    cache_dir: Path = DEFAULT_CACHE,
    offline: bool = False,
    allow_mutable_drift: bool = False,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise AcquisitionError("unsupported public source manifest schema")

    acquisitions = []
    candidates = []
    raw_candidates: dict[str, dict[str, Any]] = {}
    score_fractions: dict[str, Fraction] = {}

    for source in manifest["sources"]:
        payload, acquisition = download_and_authenticate(
            source, cache_dir, offline, allow_mutable_drift
        )
        acquisitions.append(acquisition)
        if source["kind"] != "witness":
            continue
        parser = PARSERS.get(source.get("parser", ""))
        if parser is None:
            raise AcquisitionError(f"{source['id']}: no parser registered")
        for raw_candidate in parser(payload, source):
            evaluated, score = public_evaluation(raw_candidate, source)
            if evaluated["id"] in score_fractions:
                raise AcquisitionError(f"duplicate candidate id: {evaluated['id']}")
            candidates.append(evaluated)
            raw_candidates[evaluated["id"]] = raw_candidate
            score_fractions[evaluated["id"]] = score

    rankings: dict[str, list[dict[str, Any]]] = {}
    for label in CONTRACTS:
        author, author_score = _author_row(label)
        if not author["valid"]:
            raise AcquisitionError(f"matching author certificate is invalid at tolerance {label}")
        ranking_rows = [(author, author_score)]
        for row in candidates:
            check = row["checks"][label]
            if check["valid"]:
                ranking_rows.append(
                    (
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "source_id": row["source_id"],
                            "score": row["recomputed_score"],
                            "valid": True,
                        },
                        score_fractions[row["id"]],
                    )
                )
        ranking_rows.sort(key=lambda item: item[1], reverse=True)
        rankings[label] = [dict(position=index, **row) for index, (row, _) in enumerate(ranking_rows, 1)]

    source_native_rankings = {}
    for evaluator, author_label in (
        ("alphaevolve_binary64_zero", "0"),
        ("eurekagent_binary64_1e-6", "1e-6"),
    ):
        author_id, author_name, author_path = AUTHOR_CERTIFICATES[author_label]
        author_raw = candidate(
            author_id,
            author_name,
            "this_repository",
            load_certificate(author_path),
        )
        native_rows = []
        for raw_row in [author_raw, *raw_candidates.values()]:
            check = native_binary64_check(raw_row, evaluator)
            if check["valid"]:
                native_rows.append(
                    (
                        {
                            "id": raw_row["id"],
                            "name": raw_row["name"],
                            "source_id": raw_row["source_id"],
                            "binary64_score": check["binary64_score"],
                            "valid": True,
                        },
                        float(check["binary64_score"]),
                    )
                )
        native_rows.sort(key=lambda item: item[1], reverse=True)
        source_native_rankings[evaluator] = [
            dict(position=index, **row) for index, (row, _) in enumerate(native_rows, 1)
        ]

    incomplete = [
        {
            "project": source["project"],
            "source_id": source["id"],
            "url": source["url"],
            "sha256": source["sha256"],
            "reason": source["exclusion_reason"],
        }
        for source in manifest["sources"]
        if source["kind"] == "incomplete_program"
    ]
    incomplete.extend(manifest["claims_without_evaluable_witness"])

    hash_drift = [row["source_id"] for row in acquisitions if not row["hash_matches"]]
    return {
        "schema_version": 1,
        "snapshot_date": manifest["snapshot_date"],
        "problem": manifest["problem"],
        "status": "PASS" if not hash_drift else "PASS_WITH_MUTABLE_SOURCE_DRIFT",
        "uniform_decision_arithmetic": "exact rational",
        "contracts": list(CONTRACTS),
        "third_party_code_executed": False,
        "corpus_scope": "Hash-authenticated complete public witnesses listed in data/public_sources.json; not an exhaustive literature leaderboard.",
        "ranking_scope": "Each ranking contains one matching author certificate and only acquired public witnesses valid under that same rational tolerance.",
        "source_acquisitions": acquisitions,
        "candidates": candidates,
        "rankings": rankings,
        "source_native_rankings": source_native_rankings,
        "excluded_incomplete_or_unavailable": incomplete,
        "mutable_source_drift": hash_drift,
        "source_manifest": str(manifest_path.relative_to(ROOT)) if manifest_path.is_relative_to(ROOT) else str(manifest_path),
    }


def short_score(value: str) -> str:
    return format(Decimal(value), ".18g")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Reproducible public-corpus audit",
        "",
        f"Snapshot date: **{report['snapshot_date']}**. Acquisition status: **{report['status']}**.",
        "",
        "> Scope: this is a reproducible comparison inside the explicitly manifested corpus, not an exhaustive literature leaderboard. Each table uses one common exact-rational tolerance and exactly one matching author certificate.",
        "",
        "> Safety: downloaded Python files and notebooks are parsed as data. No third-party program is imported or executed.",
        "",
        "## Authenticated acquisitions",
        "",
        "| Project | Pin | SHA-256 | License | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["source_acquisitions"]:
        pin = row["commit"][:12] if row["commit"] else "mutable"
        status = "match" if row["hash_matches"] else "DRIFT ACCEPTED"
        lines.append(
            f"| {row['project']} | `{pin}` | `{row['actual_sha256'][:16]}…` | "
            f"`{row['license']}` | {status} |"
        )

    for label in ("0", "1e-10", "1e-6"):
        lines.extend(
            [
                "",
                f"## Corpus position at rational tolerance `{label}`",
                "",
                "| Position | Candidate | Recomputed score | Source |",
                "| ---: | --- | ---: | --- |",
            ]
        )
        for row in report["rankings"][label]:
            lines.append(
                f"| {row['position']} | {row['name']} | `{short_score(row['score'])}` | `{row['source_id']}` |"
            )

    lines.extend(
        [
            "",
            "## Uniform validity matrix",
            "",
            "| Candidate | Score | exact | `1e-10` | `1e-6` |",
            "| --- | ---: | :---: | :---: | :---: |",
        ]
    )
    for row in report["candidates"]:
        check = lambda label: "yes" if row["checks"][label]["valid"] else "no"
        lines.append(
            f"| {row['name']} | `{short_score(row['recomputed_score'])}` | "
            f"{check('0')} | {check('1e-10')} | {check('1e-6')} |"
        )

    native = [row for row in report["candidates"] if "source_native_compatibility" in row]
    if native:
        lines.extend(
            [
                "",
                "## Source-native compatibility",
                "",
                "These checks independently reimplement the published binary64 decision path; they do not execute the upstream evaluator.",
                "",
                "| Candidate | Published contract reimplemented | Valid | Binary64 score |",
                "| --- | --- | :---: | ---: |",
            ]
        )
        for row in native:
            check = row["source_native_compatibility"]
            lines.append(
                f"| {row['name']} | {check['interpretation']} | "
                f"{'yes' if check['valid'] else 'no'} | `{check['binary64_score']}` |"
            )

    for evaluator, title in (
        ("alphaevolve_binary64_zero", "AlphaEvolve notebook binary64 zero-tolerance corpus position"),
        ("eurekagent_binary64_1e-6", "EurekAgent binary64 `atol=1e-6` corpus position"),
    ):
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| Position | Candidate | Binary64 score | Source |",
                "| ---: | --- | ---: | --- |",
            ]
        )
        for row in report["source_native_rankings"][evaluator]:
            lines.append(
                f"| {row['position']} | {row['name']} | `{row['binary64_score']}` | `{row['source_id']}` |"
            )

    lines.extend(
        [
            "",
            "## Excluded from witness rankings",
            "",
            "| Project | Reported score | Reason |",
            "| --- | ---: | --- |",
        ]
    )
    for row in report["excluded_incomplete_or_unavailable"]:
        lines.append(
            f"| [{row['project']}]({row['url']}) | `{row.get('reported_score', 'not serialized')}` | {row['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A position in these tables is mechanically reproducible for this pinned corpus only. It is not a claim that every paper, private run, mutable webpage, or unavailable witness has been covered. Scores from different tolerance tables are not interchangeable.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--offline", action="store_true", help="use previously authenticated cache files")
    parser.add_argument(
        "--allow-mutable-drift",
        action="store_true",
        help="continue only for changed sources explicitly marked mutable",
    )
    args = parser.parse_args()
    report = acquire(args.manifest, args.cache_dir, args.offline, args.allow_mutable_drift)
    write_report(report, args.json_output, args.markdown_output)
    print(
        json.dumps(
            {
                "status": report["status"],
                "authenticated_sources": len(report["source_acquisitions"]),
                "evaluated_public_candidates": len(report["candidates"]),
                "json": str(args.json_output),
                "markdown": str(args.markdown_output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
