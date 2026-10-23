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
        self.assertEqual(measures["matched_code"], "60")
        self.assertEqual(measures["total_code"], "7335668")
        self.assertEqual(measures["matched_functions"], 3)
        self.assertEqual(measures["total_functions"], 30941)

    def test_verified_source_paths(self):
        report = bytematch.build_report()
        matched = [unit for unit in report["units"] if unit["measures"]["matched_code"] != "0"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["metadata"]["source_path"],
                         "src/Game/Player/PlayerInput.cpp")
        self.assertEqual(sum(int(fn["size"]) for fn in matched[0]["functions"]), 60)
        self.assertTrue(all(fn["fuzzy_match_percent"] == 100.0
                            for fn in matched[0]["functions"]))
        self.assertEqual(len(report["units"]), 2)

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
