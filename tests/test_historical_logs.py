from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_historical_logs


class HistoricalLogTests(unittest.TestCase):
    def test_final_attached_logs_are_complete(self):
        document = json.loads(audit_historical_logs.generate().read_text())
        self.assertEqual(document["cumulative_through_second_layer"], 390)
        self.assertEqual(document["second_layer"]["completed_lines"], 312)
        self.assertTrue(document["second_layer"]["complete"])
        self.assertEqual(document["third_layer"]["completed_lines"], 468)
        self.assertTrue(document["third_layer"]["complete"])


if __name__ == "__main__":
    unittest.main()
