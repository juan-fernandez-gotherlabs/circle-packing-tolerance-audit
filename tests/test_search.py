from __future__ import annotations

import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import contact_graph
import derive_nearby_strict
import search
import verifier


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = contact_graph.load_csv(ROOT / "data/certificates/exact.csv")
        cls.active = contact_graph.detect_active(cls.root)

    def test_contact_graph_diagnostics(self):
        metrics = contact_graph.metrics(self.root, self.active)
        self.assertEqual(metrics["active_constraints"], 78)
        self.assertEqual(metrics["active_pair_contacts"], 58)
        self.assertEqual(metrics["active_wall_contacts"], 20)
        self.assertEqual(metrics["jacobian_rank"], 78)
        self.assertGreater(metrics["multiplier_min"], 0)
        self.assertLess(metrics["stationarity_inf_norm"], 1e-12)

    def test_constraint_keys_round_trip(self):
        for key in (("P", 8, 19), ("W", 24, "R")):
            self.assertEqual(contact_graph.parse_key(contact_graph.key_string(key)), key)

    def test_seed_archive_is_byte_reproducible(self):
        value = np.array([1.0, 2.0, 3.0])
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.npz"
            second = Path(directory) / "second.npz"
            search.save_npz(first, value)
            search.save_npz(second, value)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            np.testing.assert_array_equal(np.load(first)["z"], value)

    def test_published_search_validation_summary(self):
        report = json.loads((ROOT / "results/search_validation.json").read_text())
        historical = report["historical_log_counts"]
        layer1 = report["layer1_reimplementation"]
        self.assertEqual(historical["second_layer"]["completed"], 312)
        self.assertEqual(historical["third_layer"]["completed"], 468)
        self.assertEqual(layer1["matching_drop_labels"], 78)
        self.assertEqual(layer1["local_max_classification_disagreements"], [])

    def test_nearby_derivation_is_honestly_labelled_and_strict(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = derive_nearby_strict.derive(output)
            self.assertEqual(report["source_certificate"], "data/certificates/exact.csv")
            self.assertFalse(report["independent_reconstruction"])
            rebuilt = verifier.verify_certificate(output / "certificate.csv", Fraction(0))
            self.assertTrue(rebuilt["valid"])


if __name__ == "__main__":
    unittest.main()
