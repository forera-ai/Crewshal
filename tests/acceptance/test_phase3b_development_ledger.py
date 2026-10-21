"""Local checks for Phase 3B development coverage, with no task execution."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
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

    def test_evidence_inventory_binds_attempt_and_file_bytes(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(
            status="failed",
            reason="Synthetic runtime refusal.",
            attempt_ids=["synthetic-attempt-1"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attempt.json"
            path.write_bytes(b'{"result":"refused"}\n')
            inventory = self._inventory(candidate, [self._attempt(row, path)])
            result = ledger.check_evidence(candidate, inventory, temporary)
            self.assertEqual(result["attempts_indexed"], 1)
            self.assertEqual(result["evidence_files_checked"], 1)
            self.assertIs(result["evidence_inventory_checked"], True)
            self.assertIs(result["evidence_verified"], False)
            path.write_bytes(b'{"result":"forged!"}\n')
            with self.assertRaisesRegex(ERROR, "digest mismatch"):
                ledger.check_evidence(candidate, inventory, temporary)

    def test_evidence_inventory_rejects_missing_attempt_and_false_final_status(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(
            status="verified",
            reason="Synthetic completion.",
            attempt_ids=["synthetic-attempt-1", "synthetic-attempt-2"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attempt.json"
            path.write_bytes(b"synthetic evidence")
            first = self._attempt(row, path)
            first["outcome"] = "failed"
            first["reason"] = "Synthetic failure."
            inventory = self._inventory(candidate, [first])
            with self.assertRaisesRegex(ERROR, "coverage"):
                ledger.check_evidence(candidate, inventory, temporary)
            second = copy.deepcopy(first)
            second["attempt_id"] = "synthetic-attempt-2"
            second["files"][0]["name"] = "second.json"
            (Path(temporary) / "second.json").write_bytes(path.read_bytes())
            inventory["attempts"].append(second)
            with self.assertRaisesRegex(ERROR, "final attempt"):
                ledger.check_evidence(candidate, inventory, temporary)

    def test_evidence_inventory_rejects_symlink_and_path_escape(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(
            status="failed", reason="Synthetic refusal.", attempt_ids=["synthetic-attempt-1"]
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attempt.json"
            path.write_bytes(b"synthetic evidence")
            inventory = self._inventory(candidate, [self._attempt(row, path)])
            inventory["attempts"][0]["files"][0]["name"] = "../attempt.json"
            with self.assertRaisesRegex(ERROR, "name"):
                ledger.check_evidence(candidate, inventory, temporary)
            inventory["attempts"][0]["files"][0]["name"] = "link.json"
            (Path(temporary) / "link.json").symlink_to(path)
            with self.assertRaises(OSError):
                ledger.check_evidence(candidate, inventory, temporary)

    @staticmethod
    def _inventory(candidate, attempts):
        content = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        return {
            "schema_version": 1,
            "record_kind": ledger.EVIDENCE_KIND,
            "package_content_sha256": candidate["package_content_sha256"],
            "ledger_sha256": hashlib.sha256(content).hexdigest(),
            "attempts": attempts,
        }

    @staticmethod
    def _attempt(row, path):
        content = path.read_bytes()
        return {
            "attempt_id": row["attempt_ids"][0],
            "schedule_row_id": row["schedule_row_id"],
            "condition_sha256": row["condition_sha256"],
            "outcome": row["status"],
            "reason": row["reason"],
            "files": [
                {
                    "name": path.name,
                    "kind": "run",
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
