import copy
import json
import unittest
from unittest.mock import patch

from tools import bytematch_report as bytematch


class ByteMatchReportTests(unittest.TestCase):
    def test_objdiff_v2_report(self):
        report = bytematch.build_report()
        self.assertEqual(report["version"], 2)
        self.assertEqual({category["id"] for category in report["categories"]}, {"game"})
        self.assertEqual(report["measures"], report["categories"][0]["measures"])
        measures = report["measures"]
        self.assertEqual(sum(int(unit["measures"]["total_code"])
                             for unit in report["units"]), int(measures["total_code"]))
        self.assertEqual(sum(int(unit["measures"]["matched_code"])
                             for unit in report["units"]), int(measures["matched_code"]))
        self.assertEqual(sum(unit["measures"]["matched_functions"]
                             for unit in report["units"]), measures["matched_functions"])
        self.assertEqual(sum(unit["measures"]["total_functions"]
                             for unit in report["units"]), measures["total_functions"])
        snapshot = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(int(measures["matched_code"]), sum(item["size"] for item in snapshot["matched_functions"]))
        self.assertEqual(measures["total_code"], "7335668")
        self.assertEqual(measures["matched_functions"], len(snapshot["matched_functions"]))
        self.assertEqual(measures["total_functions"], snapshot["estimated_total_functions"])

    def test_verified_source_paths(self):
        report = bytematch.build_report()
        matched = [unit for unit in report["units"] if unit["measures"]["matched_code"] != "0"]
        self.assertTrue(any(unit["metadata"]["source_path"] ==
                            "src/Game/Player/PlayerInput.cpp" for unit in matched))
        self.assertEqual(sum(int(unit["measures"]["matched_code"]) for unit in matched),
                         int(report["measures"]["matched_code"]))
        self.assertTrue(all(unit["metadata"]["source_path"].startswith("src/")
                            for unit in matched))
        self.assertTrue(all(fn["fuzzy_match_percent"] == 100.0
                            for unit in matched for fn in unit["functions"]))
        self.assertTrue(any(unit["name"].startswith("Unmapped .text")
                            for unit in report["units"]))

    def test_stale_source_is_rejected(self):
        hashes = bytematch.input_hashes()
        hashes["src/Game/Player/PlayerInput.cpp"] = "0" * 64
        with patch.object(bytematch, "input_hashes", return_value=hashes):
            with self.assertRaisesRegex(ValueError, "stale"):
                bytematch.build_report()

    def test_tampered_match_is_rejected(self):
        actual = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        corrupted = copy.deepcopy(actual)
        corrupted["matched_functions"][0]["size"] += 4
        with patch.object(bytematch, "SNAPSHOT", bytematch.SNAPSHOT):
            with patch.object(bytematch.json, "loads", return_value=corrupted):
                with self.assertRaisesRegex(ValueError, "snapshot records"):
                    bytematch.build_report()


if __name__ == "__main__":
    unittest.main()
