from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_provenance
import generate_table
import generate_visualization


class GeneratorTests(unittest.TestCase):
    def test_table_contains_all_contracts(self):
        text = generate_table.generate().read_text()
        self.assertIn("Ranking at tolerance `0`", text)
        self.assertIn("Ranking at tolerance `1e-10`", text)
        self.assertIn("Ranking at tolerance `1e-6`", text)
        self.assertIn("Nuestro certificado exacto", text)

    def test_visualization_has_expected_graph(self):
        text = generate_visualization.generate().read_text()
        self.assertEqual(text.count("<circle "), 26)
        self.assertIn("58 pair contacts + 20 wall contacts", text)

    def test_provenance_covers_every_audited_candidate(self):
        target = generate_provenance.generate()
        import json

        provenance = json.loads(target.read_text())
        audit = json.loads((ROOT / "data/audit/strict_leaderboard_audit.json").read_text())
        names = {entry["candidate"] for entry in provenance["entries"]}
        self.assertTrue({item["name"] for item in audit["candidates"]}.issubset(names))


if __name__ == "__main__":
    unittest.main()
