"""Local checks for Phase 3B development coverage, with no task execution."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import check_phase_3a_freeze as freeze
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

    def test_measurements_bind_attempts_without_verifying_execution(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(status="failed", reason="Synthetic refusal.", attempt_ids=["attempt-1"])
        measurement = self._measurement(candidate, 0, "attempt-1")
        bundle = self._measurement_bundle(candidate, [measurement])
        result = ledger.check_measurements(candidate, bundle)
        self.assertEqual(result["measurement_attempts_checked"], 1)
        self.assertEqual(result["measurement_outcome_counts"], {"failed": 1})
        self.assertIs(result["evidence_verified"], False)
        self.assertIs(result["execution_allowed"], False)
        with self.assertRaisesRegex(ERROR, "coverage"):
            ledger.check_measurements(candidate, self._measurement_bundle(candidate, []))

    def test_measurements_reject_schedule_and_outcome_changes(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(status="failed", reason="Synthetic refusal.", attempt_ids=["attempt-1"])
        record = self._measurement(candidate, 0, "attempt-1")
        for mutation, message in (
            (lambda item: item["unit"].update(condition="P"), "schedule"),
            (lambda item: item.update(outcome="verified"), "final measurement"),
            (
                lambda item: item["identity"].update(confirmed_model_sha256="a" * 64),
                "baseline claims",
            ),
        ):
            changed = copy.deepcopy(record)
            mutation(changed)
            with self.subTest(message=message), self.assertRaisesRegex(ERROR, message):
                ledger.check_measurements(candidate, self._measurement_bundle(candidate, [changed]))

    def test_measurements_preserve_partial_usage_and_cost_provenance(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(status="failed", reason="Synthetic refusal.", attempt_ids=["attempt-1"])
        record = self._measurement(candidate, 0, "attempt-1")
        record["usage"]["new_input_tokens"] = 7
        ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))
        record["usage"]["unknown_usage"] = False
        with self.assertRaisesRegex(ERROR, "lacks counters"):
            ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))
        record["usage"]["unknown_usage"] = True
        record["usage"]["measured_cost"]["amount"] = 0
        with self.assertRaisesRegex(ERROR, "lacks provenance"):
            ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))
        record["usage"]["measured_cost"].update(
            currency="USD", billing_evidence="synthetic-receipt"
        )
        ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))

    def test_provenance_links_measurements_to_inventory_and_local_bytes(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(status="failed", reason="Synthetic refusal.", attempt_ids=["attempt-1"])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.json"
            path.write_bytes(b'{"synthetic":"refusal"}\n')
            attempt = self._attempt(row, path)
            inventory = self._inventory(candidate, [attempt])
            record = self._measurement(candidate, 0, "attempt-1")
            record["evidence_refs"] = copy.deepcopy(attempt["files"])
            bundle = self._measurement_bundle(candidate, [record], inventory)
            result = ledger.check_provenance(candidate, inventory, bundle, temporary)
            self.assertEqual(result["measurement_evidence_files_linked"], 1)
            self.assertEqual(result["evidence_files_checked"], 1)
            self.assertIs(result["provenance_links_checked"], True)
            self.assertIs(result["evidence_verified"], False)
            self.assertIs(result["execution_allowed"], False)

            changed = copy.deepcopy(bundle)
            changed["records"][0]["evidence_refs"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ERROR, "refs differ"):
                ledger.check_provenance(candidate, inventory, changed, temporary)
            changed = copy.deepcopy(bundle)
            changed["inventory_sha256"] = "0" * 64
            with self.assertRaisesRegex(ERROR, "inventory mismatch"):
                ledger.check_provenance(candidate, inventory, changed, temporary)
            path.write_bytes(b'{"synthetic":"forgery"}\n')
            with self.assertRaisesRegex(ERROR, "digest mismatch"):
                ledger.check_provenance(candidate, inventory, bundle, temporary)

    def test_provenance_rejects_attempt_outcome_disagreement(self):
        candidate = copy.deepcopy(self.planned)
        row = candidate["rows"][0]
        row.update(
            status="failed", reason="Second attempt failed.", attempt_ids=["attempt-1", "attempt-2"]
        )
        with tempfile.TemporaryDirectory() as temporary:
            attempts = []
            records = []
            for number, reason in ((1, "First attempt failed."), (2, row["reason"])):
                path = Path(temporary) / f"run-{number}.json"
                path.write_bytes(f'{{"attempt":{number}}}\n'.encode())
                attempt = self._attempt(row, path)
                attempt["attempt_id"] = f"attempt-{number}"
                attempt["reason"] = reason
                attempts.append(attempt)
                record = self._measurement(candidate, 0, f"attempt-{number}")
                record["reason"] = reason
                record["evidence_refs"] = copy.deepcopy(attempt["files"])
                records.append(record)
            inventory = self._inventory(candidate, attempts)
            bundle = self._measurement_bundle(candidate, records, inventory)
            bundle["records"][0]["reason"] = "Different first outcome."
            with self.assertRaisesRegex(ERROR, "outcome differs"):
                ledger.check_provenance(candidate, inventory, bundle, temporary)

    @staticmethod
    def _measurement(candidate, row_index, attempt_id):
        template = freeze.parse(
            freeze.read(ledger.ROOT, f"{freeze.PACKAGE}/measurement-template.json")
        )
        schedule = freeze.parse(freeze.read(ledger.ROOT, f"{freeze.PACKAGE}/schedule.json"))
        scheduled = [row for row in schedule["rows"] if row["split"] == "development"][row_index]
        record = copy.deepcopy(template)
        record.update(
            record_kind=ledger.MEASUREMENT_KIND,
            status="unverified-development-claim",
            outcome=candidate["rows"][row_index]["status"],
            reason=candidate["rows"][row_index]["reason"],
        )
        record["unit"].update(
            attempt_id=attempt_id,
            schedule_row_id=scheduled["ordinal"],
            condition=scheduled["condition"],
            repetition=scheduled["repetition"],
            repository_id=scheduled["repository_id"],
            role_assignment=scheduled["role_assignment"],
            task_id=scheduled["task_id"],
        )
        record["identity"]["frozen_package_sha256"] = candidate["package_content_sha256"]
        record["evidence_refs"] = [
            {
                "name": f"{attempt_id}.json",
                "kind": "run",
                "bytes": 1,
                "sha256": "0" * 64,
            }
        ]
        return record

    @staticmethod
    def _measurement_bundle(candidate, records, inventory=None):
        canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        inventory_bytes = (
            json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
            if inventory is not None
            else b""
        )
        return {
            "schema_version": 1,
            "record_kind": ledger.MEASUREMENT_KIND,
            "package_content_sha256": candidate["package_content_sha256"],
            "ledger_sha256": hashlib.sha256(canonical).hexdigest(),
            "inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
            "records": records,
        }

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
