from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import contact_graph


class ContactGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = contact_graph.load_csv(ROOT / "data/exact/certificate.csv")
        cls.active = contact_graph.detect_active(cls.root)
        cls.metrics = contact_graph.metrics(cls.root, cls.active)

    def test_contact_counts(self):
        self.assertEqual(len(self.active), 78)
        self.assertEqual(self.metrics["active_pair_contacts"], 58)
        self.assertEqual(self.metrics["active_wall_contacts"], 20)

    def test_local_stationarity_diagnostics(self):
        self.assertEqual(self.metrics["jacobian_rank"], 78)
        self.assertGreater(self.metrics["multiplier_min"], 0)
        self.assertLess(self.metrics["stationarity_inf_norm"], 1e-12)
        self.assertAlmostEqual(self.metrics["score"], 2.6359830849176076, places=15)


if __name__ == "__main__":
    unittest.main()
