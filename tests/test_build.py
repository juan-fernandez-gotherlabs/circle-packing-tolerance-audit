from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build


class BuildTests(unittest.TestCase):
    def test_release_identity_is_synchronized(self):
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        preprint = (
            ROOT / "preprint/circle_packing_n26_preprint.tex"
        ).read_text(encoding="utf-8")
        previous_doi = "10.5281/zenodo.21864592"
        current_doi = "10.5281/zenodo.22060172"
        self.assertIn('version: "1.2.1"', citation)
        self.assertIn("date-released: 2026-08-22", citation)
        self.assertIn(f'doi: "{current_doi}"', citation)
        self.assertIn(current_doi, readme)
        self.assertIn(current_doi, preprint)
        self.assertIn(previous_doi, readme)
        self.assertIn(previous_doi, preprint)

    def test_current_sources_use_provider_neutral_ai_disclosure(self):
        public_sources = [
            ROOT / "README.md",
            ROOT / "data/provenance.json",
            ROOT / "docs/METHODS.md",
            ROOT / "preprint/circle_packing_n26_preprint.tex",
            ROOT / "scripts/search.py",
        ]
        forbidden = ("chat" + "gpt", "co" + "dex")
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in public_sources
        )
        for provider in forbidden:
            self.assertNotIn(provider, combined)
        self.assertIn("göther labs ai-assisted research pipeline", combined)

    def test_machine_readable_rankings_have_one_matching_author_certificate(self):
        audit = json.loads((ROOT / "data/leaderboard_audit.json").read_text())
        for tolerance, expected in build.PRIMARY_CANDIDATES.items():
            author_rows = [
                row["name"]
                for row in audit["rankings"][tolerance]
                if row["name"] in build.AUTHOR_CANDIDATES
            ]
            self.assertEqual(author_rows, [expected])

    def test_table_contains_all_contracts(self):
        text = build.generate_table().read_text()
        for tolerance in ("0", "1e-10", "1e-6"):
            self.assertIn(f"rational tolerance `{tolerance}`", text)
        self.assertIn("not an end-to-end reproducible leaderboard", text)
        self.assertNotIn("| Nuestro certificado exacto |", text.split("## Snapshot at rational tolerance `1e-10`")[1].split("## Snapshot at rational tolerance `1e-6`")[0])
        self.assertNotIn("| Nuestro candidato 1e-10 |", text.split("## Snapshot at rational tolerance `1e-6`")[1].split("## Stored validity matrix")[0])

    def test_certificate_csv_files_share_one_schema(self):
        for path in sorted((ROOT / "data/certificates").glob("*.csv")):
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, ["circle", "x", "y", "radius"])
                self.assertEqual([int(row["circle"]) for row in reader], list(range(26)))

    def test_manifest_exactly_covers_tracked_files(self):
        manifest = build.generate_manifest().read_text().splitlines()
        actual = {line.split("  ", 1)[1] for line in manifest}
        tracked = set(
            subprocess.check_output(
                ["git", "ls-files"], cwd=ROOT, text=True
            ).splitlines()
        )
        self.assertEqual(actual, tracked - {"SHA256SUMS"})
        self.assertIn(".gitignore", actual)

    def test_manifest_rejects_untracked_files(self):
        probe = ROOT / "reviewer-untracked.tmp"
        self.assertFalse(probe.exists())
        try:
            probe.write_text("not part of the Git artifact\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "untracked files"):
                build.generate_manifest()
        finally:
            probe.unlink(missing_ok=True)

    def test_visualization_has_expected_graph(self):
        text = build.generate_visualization().read_text()
        self.assertEqual(text.count("<circle "), 26)
        self.assertEqual(text.count("<line "), 80)
        self.assertIn("58 pair contacts + 20 wall contacts", text)

    def test_tolerance_visualization_keeps_contracts_separate(self):
        text = build.generate_tolerance_visualization().read_text()
        self.assertEqual(text.count("<circle "), 78)
        self.assertIn("exact rational", text)
        self.assertIn("tau = 1e-10", text)
        self.assertIn("tau = 1e-6", text)

    def test_tolerance_rankings_keep_contracts_separate(self):
        text = build.generate_tolerance_rankings().read_text()
        audit = json.loads((ROOT / "results/public_corpus_audit.json").read_text())
        self.assertEqual(text.count('data-contract="'), 3)
        self.assertEqual(text.count('data-rank="'), 15)
        self.assertEqual(text.count('data-source="this_repository"'), 3)
        self.assertIn("(a) τ = 0", text)
        self.assertIn("(b) τ = 1e-10", text)
        self.assertIn("(c) τ = 1e-6", text)
        self.assertIn("compare positions only within the same panel", text)
        for contract in ("0", "1e-10", "1e-6"):
            for row in audit["rankings"][contract][:5]:
                self.assertIn(f'data-score="{row["score"]}"', text)

    def test_provenance_covers_every_audited_candidate(self):
        audit = json.loads((ROOT / "data/leaderboard_audit.json").read_text())
        provenance = json.loads((ROOT / "data/provenance.json").read_text())
        names = {entry["candidate"] for entry in provenance["entries"]}
        self.assertTrue({candidate["name"] for candidate in audit["candidates"]} <= names)

    def test_evidence_archive_is_complete_and_reproducible(self):
        source_repo = Path(os.environ.get("EVIDENCE_SOURCE_REPO", ROOT))
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build.package_evidence(first, source_repo=source_repo)
            build.package_evidence(second, source_repo=source_repo)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                manifest_name = next(name for name in archive.namelist() if name.endswith("MANIFEST.json"))
                manifest = json.loads(archive.read(manifest_name))
                self.assertEqual(manifest["file_count"], 180)
                self.assertEqual(len(manifest["files"]), 180)
                self.assertEqual(manifest["source_commit"], build.EVIDENCE_SOURCE_COMMIT)
            self.assertEqual(build.digest_file(first), build.EVIDENCE_ARCHIVE_SHA256)

    def test_evidence_tag_and_commit_are_pinned(self):
        self.assertEqual(build.EVIDENCE_SOURCE_TAG, "v1.0.0")
        self.assertEqual(
            build.EVIDENCE_SOURCE_COMMIT,
            "2359ee29d5de8747a124a5439779b8d4c553cce0",
        )


if __name__ == "__main__":
    unittest.main()
