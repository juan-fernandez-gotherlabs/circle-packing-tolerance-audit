from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import acquire_public


class PublicAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "data/public_sources.json").read_text())
        cls.report = json.loads((ROOT / "results/public_corpus_audit.json").read_text())

    def test_every_downloaded_payload_is_hash_authenticated(self):
        expected = {source["id"]: source["sha256"] for source in self.manifest["sources"]}
        self.assertEqual(len(self.report["source_acquisitions"]), len(expected))
        for acquisition in self.report["source_acquisitions"]:
            self.assertTrue(acquisition["hash_matches"])
            self.assertEqual(acquisition["actual_sha256"], expected[acquisition["source_id"]])

    def test_all_github_artifacts_are_commit_pinned(self):
        for source in self.manifest["sources"]:
            if "github" in source["url"]:
                self.assertRegex(source.get("commit", ""), r"^[0-9a-f]{40}$")
                self.assertIn(source["commit"], source["url"])

    def test_report_does_not_claim_an_exhaustive_leaderboard(self):
        self.assertIn("not an exhaustive", self.report["corpus_scope"])
        markdown = (ROOT / "results/public_corpus_audit.md").read_text()
        self.assertIn("not an exhaustive literature leaderboard", markdown)
        self.assertIn("Scores from different tolerance tables are not interchangeable", markdown)

    def test_committed_markdown_is_rendered_from_committed_json(self):
        expected = acquire_public.render_markdown(self.report)
        self.assertEqual((ROOT / "results/public_corpus_audit.md").read_text(), expected)

    def test_each_rational_ranking_has_one_matching_author_certificate(self):
        expected = {"0": "author_exact", "1e-10": "author_1e-10", "1e-6": "author_1e-6"}
        all_author_ids = set(expected.values())
        for tolerance, author_id in expected.items():
            present = [row["id"] for row in self.report["rankings"][tolerance] if row["id"] in all_author_ids]
            self.assertEqual(present, [author_id])

    def test_eurek_boundary_is_reported_under_both_contracts(self):
        eurek = next(row for row in self.report["candidates"] if row["id"] == "eurekagent")
        self.assertFalse(eurek["checks"]["1e-6"]["valid"])
        self.assertTrue(eurek["source_native_compatibility"]["valid"])
        native = self.report["source_native_rankings"]["eurekagent_binary64_1e-6"]
        self.assertEqual([row["id"] for row in native[:2]], ["author_1e-6", "eurekagent"])

    def test_incomplete_claims_are_not_ranked(self):
        ranked_ids = {
            row["id"]
            for ranking in self.report["rankings"].values()
            for row in ranking
        }
        self.assertNotIn("alphaz_coral", ranked_ids)
        excluded = {row["project"] for row in self.report["excluded_incomplete_or_unavailable"]}
        self.assertTrue({"AlphaZ-CORAL", "Numaro", "HELIX"} <= excluded)

    def test_python_parser_does_not_execute_source(self):
        rows = ",\n".join("[0.5, 0.5, 0.01]" for _ in range(26))
        payload = f"raise RuntimeError('must not run')\nCIRCLE_N26 = np.array([{rows}])\n".encode()
        parsed = acquire_public.parse_station_python(payload, {"id": "synthetic"})
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]["circles"]), 26)

    def test_hash_mismatch_fails_closed_and_mutable_override_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            payload = b"changed payload\n"
            (cache / "probe.txt").write_bytes(payload)
            source = {
                "id": "probe",
                "project": "probe",
                "kind": "support",
                "artifact_filename": "probe.txt",
                "url": "https://invalid.example/probe.txt",
                "sha256": "0" * 64,
                "immutable": False,
                "license": "NOASSERTION",
            }
            with self.assertRaisesRegex(acquire_public.AcquisitionError, "SHA-256 changed"):
                acquire_public.download_and_authenticate(source, cache, True, False)
            _, acquisition = acquire_public.download_and_authenticate(source, cache, True, True)
            self.assertFalse(acquisition["hash_matches"])

    def test_third_party_code_execution_is_explicitly_false(self):
        self.assertFalse(self.report["third_party_code_executed"])
        for candidate in self.report["candidates"]:
            native = candidate.get("source_native_compatibility")
            if native:
                self.assertFalse(native["third_party_code_executed"])


if __name__ == "__main__":
    unittest.main()
