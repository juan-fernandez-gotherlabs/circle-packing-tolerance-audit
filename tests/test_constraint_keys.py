from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import contact_graph
import run_search


class ConstraintKeyTests(unittest.TestCase):
    def test_pair_round_trip(self):
        key = ("P", 8, 19)
        self.assertEqual(contact_graph.parse_key(contact_graph.key_string(key)), key)

    def test_wall_round_trip(self):
        key = ("W", 24, "R")
        self.assertEqual(contact_graph.parse_key(contact_graph.key_string(key)), key)

    def test_seed_archive_is_byte_reproducible(self):
        value = np.array([1.0, 2.0, 3.0])
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.npz"
            second = Path(directory) / "second.npz"
            run_search.save_npz(first, value)
            run_search.save_npz(second, value)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            np.testing.assert_array_equal(np.load(first)["z"], value)


if __name__ == "__main__":
    unittest.main()
