from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prove_local_optimum


class LocalOptimumIntervalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report_path = ROOT / "results/local_optimum_interval.json"
        cls.committed = json.loads(cls.report_path.read_text())
        cls.recomputed = prove_local_optimum.proof()

    def test_committed_report_is_exactly_recomputed(self):
        self.assertEqual(self.recomputed, self.committed)
        self.assertEqual(self.recomputed["status"], "PASS")

    def test_primal_and_dual_inclusions_are_strict(self):
        self.assertTrue(self.recomputed["primal_krawczyk"]["strict_inclusion"])
        self.assertTrue(self.recomputed["primal_krawczyk"]["unique_root_in_box"])
        self.assertLess(
            Decimal(self.recomputed["primal_krawczyk"]["preconditioned_jacobian_infinity_norm_upper"]),
            1,
        )
        self.assertTrue(self.recomputed["dual_krawczyk"]["strict_inclusion"])
        self.assertGreater(Decimal(self.recomputed["dual_krawczyk"]["minimum_multiplier_lower"]), 0)

    def test_contact_and_feasibility_counts_are_complete(self):
        contacts = self.recomputed["contact_system"]
        self.assertEqual((contacts["active_count"], contacts["wall_contacts"], contacts["pair_contacts"]), (78, 20, 58))
        self.assertTrue(self.recomputed["feasibility"]["all_351_inactive_geometric_constraints_strict"])
        self.assertTrue(self.recomputed["feasibility"]["all_radii_strictly_positive"])

    def test_contact_root_score_exceeds_shrunken_rational_witness(self):
        strict_score = Decimal(
            "2.6359830849176077831865694854434817303966767982744748577457711298607038493344723396767997365079"
        )
        self.assertGreater(Decimal(self.recomputed["score_enclosure"]["lower"]), strict_score)

    def test_certificate_hash_and_dimensions(self):
        certificate_path = ROOT / self.recomputed["certificate"]["path"]
        self.assertEqual(
            hashlib.sha256(certificate_path.read_bytes()).hexdigest(),
            self.recomputed["certificate"]["sha256"],
        )
        certificate = json.loads(certificate_path.read_text())
        self.assertEqual(len(certificate["root_midpoint"]), 78)
        self.assertEqual(len(certificate["preconditioner"]), 78)
        self.assertTrue(all(len(row) == 78 for row in certificate["preconditioner"]))
        self.assertEqual(len(certificate["dual_midpoint"]), 78)

    def test_default_cli_works_without_site_packages(self):
        completed = subprocess.run(
            [sys.executable, "-S", "scripts/prove_local_optimum.py"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        self.assertEqual(json.loads(completed.stdout), self.committed)

    def test_claim_is_local_not_global(self):
        self.assertEqual(
            self.recomputed["theorem"]["conclusion"],
            "strict local maximum; no claim of global optimality",
        )


if __name__ == "__main__":
    unittest.main()
