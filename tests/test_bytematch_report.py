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

    def test_initialized_data_report(self):
        report = bytematch.build_report()
        measures = report["measures"]
        self.assertEqual(measures["total_data"], "4036468")
        self.assertEqual(measures["matched_data"], "0")
        self.assertEqual(measures["matched_data_percent"], 0.0)
        self.assertEqual(measures["complete_data"], "0")
        self.assertEqual(sum(int(unit["measures"]["total_data"])
                             for unit in report["units"]), int(measures["total_data"]))
        snapshot = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual([section["name"] for section in snapshot["data_sections"]],
                         [".rodata", ".data"])
        self.assertEqual(sum(section["size"] for section in snapshot["data_sections"]),
                         int(measures["total_data"]))

    def test_bad_data_snapshot_is_rejected(self):
        actual = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        with patch.object(bytematch, "fuzzy_manifest", return_value=bytematch.fuzzy_manifest()):
            with patch.object(bytematch.json, "loads", return_value={**actual, "data_sections": []}):
                with self.assertRaisesRegex(ValueError, "data sections"):
                    bytematch.build_report()

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

    def test_fuzzy_update_is_not_exact(self):
        report = bytematch.build_report()
        snapshot = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        fuzzy = snapshot["fuzzy_functions"]
        self.assertEqual(len(fuzzy), 1)
        self.assertEqual(fuzzy[0]["name"], "sm3d::PlayerMovementCounter::update")
        self.assertEqual(fuzzy[0]["method"], "ppc_opcode_sequence_v1")
        self.assertLess(fuzzy[0]["fuzzy_match_percent"], 100)
        candidate = next(unit for unit in report["units"] if unit["name"] == fuzzy[0]["unit"])
        self.assertEqual(candidate["measures"]["total_code"], "432")
        self.assertEqual(candidate["measures"]["matched_code"], "0")
        self.assertEqual(candidate["measures"]["matched_functions"], 0)
        self.assertEqual(candidate["functions"][0]["fuzzy_match_percent"],
                         fuzzy[0]["fuzzy_match_percent"])
        self.assertGreater(report["measures"]["fuzzy_match_percent"],
                           report["measures"]["matched_code_percent"])
        self.assertEqual(report["measures"]["matched_functions"], 29)
        self.assertEqual(report["measures"]["matched_code"], "308")

    def test_corrupted_fuzzy_measure_is_rejected(self):
        actual = json.loads(bytematch.SNAPSHOT.read_text(encoding="utf-8"))
        corrupted = copy.deepcopy(actual)
        corrupted["fuzzy_functions"][0]["fuzzy_match_percent"] = 100
        with patch.object(bytematch, "fuzzy_manifest", return_value=bytematch.fuzzy_manifest()):
            with patch.object(bytematch.json, "loads", return_value=corrupted):
                with self.assertRaisesRegex(ValueError, "fuzzy similarity"):
                    bytematch.build_report()

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
        with patch.object(bytematch, "fuzzy_manifest", return_value=bytematch.fuzzy_manifest()):
            with patch.object(bytematch.json, "loads", return_value=corrupted):
                with self.assertRaisesRegex(ValueError, "snapshot records"):
                    bytematch.build_report()


if __name__ == "__main__":
    unittest.main()
