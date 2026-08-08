from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verifier


class ExactVerifierTests(unittest.TestCase):
    def test_all_three_contracts_pass(self):
        report = verifier.verify_repository(write=False)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(case["valid"] for case in report["cases"].values()))

    def test_relaxed_certificates_fail_at_zero(self):
        report = verifier.verify_repository(write=False)
        self.assertFalse(report["relaxed_certificates_rechecked_at_zero"]["1e-6"]["valid"])
        self.assertFalse(report["relaxed_certificates_rechecked_at_zero"]["1e-10"]["valid"])

    def test_condition_counts_include_radius_positivity(self):
        report = verifier.verify_repository(write=False)
        for case in report["cases"].values():
            self.assertEqual(case["geometric_constraints_checked"], 429)
            self.assertEqual(case["positivity_conditions_checked"], 26)
            self.assertEqual(case["total_conditions_checked"], 455)

    def test_exact_score_is_finite_decimal_rational(self):
        circles = verifier.load_certificate(ROOT / "data/certificates/exact.csv")
        score = sum((radius for _, _, radius in circles), Fraction())
        self.assertEqual(
            Decimal(verifier.decimal_string(score)),
            Decimal("2.6359830849176077831865694854434817303966767982744748577457711298607038493344723396767997365079"),
        )


if __name__ == "__main__":
    unittest.main()
