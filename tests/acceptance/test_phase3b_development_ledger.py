"""Local checks for Phase 3B development coverage, with no task execution."""

import copy
import unittest

from scripts import phase3b_development_ledger as ledger


ERROR = ledger.freeze.FreezeError


class Phase3BDevelopmentLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planned = ledger.build()

    def test_planned_rows_match_frozen_schedule_without_authority(self):
        result = ledger.validate(self.planned)
        self.assertEqual(result["development_rows"], 192)
        self.assertEqual(result["sealed_rows_read_only"], 576)
        self.assertEqual(result["status_counts"], {"planned": 192})
        self.assertIs(result["evidence_verified"], False)
        self.assertIs(result["execution_allowed"], False)

    def test_missing_duplicate_or_reordered_rows_refuse(self):
        for mutation in ("missing", "duplicate", "reordered"):
            candidate = copy.deepcopy(self.planned)
            if mutation == "missing":
                candidate["rows"].pop()
            elif mutation == "duplicate":
                candidate["rows"][1] = candidate["rows"][0]
            else:
                candidate["rows"][0], candidate["rows"][1] = (
                    candidate["rows"][1],
                    candidate["rows"][0],
                )
            with self.subTest(mutation=mutation), self.assertRaises(ERROR):
                ledger.validate(candidate)

    def test_sealed_row_and_authority_refuse(self):
        candidate = copy.deepcopy(self.planned)
        candidate["rows"][0]["schedule_row_id"] = 193
        with self.assertRaises(ERROR):
            ledger.validate(candidate)
        candidate = copy.deepcopy(self.planned)
        candidate["execution_allowed"] = True
        with self.assertRaisesRegex(ERROR, "authority"):
            ledger.validate(candidate)

    def test_status_requires_reason_and_attempt_identity(self):
        candidate = copy.deepcopy(self.planned)
        candidate["rows"][0]["status"] = "failed"
        with self.assertRaisesRegex(ERROR, "reason"):
            ledger.validate(candidate)
        candidate["rows"][0]["reason"] = "Synthetic runtime refusal."
        with self.assertRaisesRegex(ERROR, "attempt"):
            ledger.validate(candidate)
        candidate["rows"][0]["attempt_ids"] = ["synthetic-attempt-1"]
        result = ledger.validate(candidate)
        self.assertEqual(result["status_counts"], {"failed": 1, "planned": 191})
        self.assertIs(result["evidence_verified"], False)

    def test_duplicate_attempt_across_rows_and_package_mismatch_refuse(self):
        candidate = copy.deepcopy(self.planned)
        for row in candidate["rows"][:2]:
            row.update(
                status="failed", reason="Synthetic runtime refusal.", attempt_ids=["same-attempt"]
            )
        with self.assertRaisesRegex(ERROR, "reused"):
            ledger.validate(candidate)
        candidate = copy.deepcopy(self.planned)
        candidate["package_content_sha256"] = "0" * 64
        with self.assertRaisesRegex(ERROR, "frozen package"):
            ledger.validate(candidate)


if __name__ == "__main__":
    unittest.main()
