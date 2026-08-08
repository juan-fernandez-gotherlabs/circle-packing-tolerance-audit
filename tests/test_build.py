from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build


class BuildTests(unittest.TestCase):
    def test_table_contains_all_contracts(self):
        text = build.generate_table().read_text()
        for tolerance in ("0", "1e-10", "1e-6"):
            self.assertIn(f"rational tolerance `{tolerance}`", text)
        self.assertIn("not an end-to-end reproducible leaderboard", text)
        self.assertNotIn("| Nuestro certificado exacto |", text.split("## Snapshot at rational tolerance `1e-10`")[1].split("## Snapshot at rational tolerance `1e-6`")[0])
        self.assertNotIn("| Nuestro candidato 1e-10 |", text.split("## Snapshot at rational tolerance `1e-6`")[1].split("## Stored validity matrix")[0])

    def test_visualization_has_expected_graph(self):
        text = build.generate_visualization().read_text()
        self.assertEqual(text.count("<circle "), 26)
        self.assertEqual(text.count("<line "), 80)
        self.assertIn("58 pair contacts + 20 wall contacts", text)

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
