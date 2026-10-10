"""Fresh SQLite/pipe admission linkage; process and kernel effects are synthetic."""

from dataclasses import replace
import sqlite3
import unittest
from unittest.mock import patch

from crewshal.admission import collect_admitted_codex, NativeAdmissionRecord
from crewshal.contracts import Attempt, Evidence, Run, record_digest
from crewshal.durable import CoordinatorStore
from crewshal.integration import CodexCollection
from crewshal.model import digest
from crewshal.supervisor import SupervisionReceipt
from tests.acceptance import test_phase_2d_admission as admission_fixtures
from tests.acceptance import test_phase_2d_supervisor as supervisor_fixtures


class Phase2DAdmissionCollection(unittest.TestCase):
    def setUp(self):
        self.native = admission_fixtures.Phase2DAdmission()
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.supervisor = supervisor_fixtures.Phase2DSupervisor()
        self.supervisor.setUp()
        self.addCleanup(self.supervisor.doCleanups)
        self.fixture, self.dispatch = self.supervisor.integration_fixture()
        self.native.configuration = self.dispatch.configuration
        self.native.proc.spec.configuration = record_digest(self.dispatch.configuration)
        self.native.started = supervisor_fixtures.NOW
        self.admitted = self.native.admit()
        self.store = self.fixture.store

    def terminal(self, exit_code=0):
        self.native.out_writer.write(self.fixture.raw)
        self.native.out_writer.close()
        self.native.err_writer.close()
        self.native.child.result = exit_code
        self.native.pid_writer.close()
        (self.native.worker_path / "cgroup.procs").write_text("")
        (self.native.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")

    def collect(self, **changes):
        arguments = dict(
            handle="owned:worker",
            cancelled=lambda: False,
            expected_run_version=1,
            expected_attempt_version=2,
            token="lease",
            initial=self.fixture.initial,
            candidate=self.fixture.candidate,
            frozen_target=self.fixture.frozen,
            allowed_paths=["README.md"],
        )
        admitted = changes.pop("admitted", self.admitted)
        dispatch = changes.pop("dispatch", self.dispatch)
        with patch("crewshal.supervisor.time.monotonic", self.supervisor.clock):
            return collect_admitted_codex(
                self.store, dispatch, admitted, **{**arguments, **changes}
            )

    def record(self):
        return self.store.records("admission", NativeAdmissionRecord)[0]

    def prepare_verdict(self, collection):
        self.fixture.validate(collection)
        self.fixture.approve_frozen(collection)

    def fresh_case(self):
        case = Phase2DAdmissionCollection()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_receipt_collection_scope_and_restart_readback(self):
        self.terminal()
        collection, supervision = self.collect()
        admission = self.record()
        self.assertEqual(admission.receipt, self.admitted.receipt)
        self.assertEqual(admission.dispatch, record_digest(self.dispatch))
        self.assertEqual(admission.handle, "owned:worker")
        self.assertEqual(supervision.admission, record_digest(admission))
        self.assertEqual(supervision.collection, record_digest(collection))
        scope = self.store.records("evidence", Evidence)[0]
        self.assertTrue(
            {record_digest(admission), record_digest(supervision)} <= set(scope.artifacts)
        )
        self.assertFalse(admission.execution_allowed)
        self.assertFalse(admission.spend_authorized)
        self.assertFalse(admission.profile_qualified)
        artifact = self.store.directory / "artifacts" / record_digest(admission)
        self.assertEqual(artifact.stat().st_mode & 0o777, 0o600)
        self.store.close()
        self.fixture.store = self.store = CoordinatorStore(self.store.directory)
        self.assertEqual(self.record(), admission)
        self.prepare_verdict(collection)
        self.assertEqual(self.fixture.verdict(collection).status, "verified")
        self.assertEqual((self.fixture.original / "README.md").read_bytes(), b"before\n")
        self.assertEqual((self.fixture.original / "dirty.txt").read_bytes(), b"original dirty\n")

    def test_admission_artifact_mutation_blocks_verdict(self):
        self.terminal()
        collection, _ = self.collect()
        self.prepare_verdict(collection)
        artifact = self.store.directory / "artifacts" / record_digest(self.record())
        artifact.write_bytes(b"forged admission")
        with self.assertRaisesRegex(ValueError, "stored capture"):
            self.fixture.verdict(collection)

    def test_missing_admission_record_blocks_verdict(self):
        self.terminal()
        collection, _ = self.collect()
        self.prepare_verdict(collection)
        self.store.connection.execute("DELETE FROM records WHERE kind='admission'")
        with self.assertRaisesRegex(ValueError, "linkage missing"):
            self.fixture.verdict(collection)

    def test_detached_supervision_or_scope_link_blocks_verdict(self):
        for target in ("supervision", "scope"):
            with self.subTest(target=target):
                case = self.fresh_case()
                case.terminal()
                collection, supervision = case.collect()
                case.prepare_verdict(collection)
                if target == "supervision":
                    _, version = case.store.get("supervision", supervision.id, SupervisionReceipt)
                    changed = SupervisionReceipt.model_validate(
                        {**supervision.model_dump(), "admission": None}
                    )
                    case.store._put("supervision", supervision.id, changed, version)
                else:
                    scope = case.store.get(
                        "evidence", f"scope:{digest(case.record().attempt_id.encode())}", Evidence
                    )[0]
                    _, version = case.store.get("evidence", scope.id, Evidence)
                    scope.artifacts.remove(record_digest(case.record()))
                    case.store._put("evidence", scope.id, scope, version)
                with self.assertRaisesRegex(ValueError, "linkage"):
                    case.fixture.verdict(collection)

    def test_admission_or_supervision_sql_failure_rolls_back_all_records(self):
        for kind in ("admission", "supervision"):
            with self.subTest(kind=kind):
                case = self.fresh_case()
                case.terminal()
                before = case.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                case.store.connection.execute(
                    "CREATE TEMP TRIGGER refuse_receipt BEFORE INSERT ON records "
                    f"WHEN NEW.kind='{kind}' BEGIN SELECT RAISE(ABORT,'fixture refusal'); END"
                )
                with self.assertRaises(sqlite3.IntegrityError):
                    case.collect()
                self.assertEqual(
                    case.store.get("attempt", "worker", Attempt)[0].state, "acknowledged"
                )
                self.assertEqual(case.store.get("run", "run", Run)[0].state, "ready")
                for record_kind, contract in (
                    ("admission", NativeAdmissionRecord),
                    ("supervision", SupervisionReceipt),
                    ("collection", CodexCollection),
                    ("evidence", Evidence),
                ):
                    self.assertEqual(case.store.records(record_kind, contract), [])
                self.assertEqual(
                    case.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                    before,
                )
                self.assertEqual(case.fixture.frozen.exists(), kind == "supervision")

    def test_stale_state_wrong_lease_and_handle_refuse_before_capture(self):
        for changes in (
            {"expected_run_version": 0},
            {"expected_attempt_version": 0},
            {"token": "wrong"},
            {"handle": "wrong"},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(ValueError),
                patch.object(
                    type(self.admitted), "capture", side_effect=AssertionError("premature capture")
                ),
            ):
                self.collect(**changes)
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])

    def test_other_dispatch_configuration_refuses_before_capture(self):
        changed = self.dispatch.model_copy(deep=True)
        changed.configuration.native_environment["TOKEN"] = "synthetic"
        with self.assertRaises(ValueError):
            self.collect(dispatch=changed)
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])

    def test_changed_receipt_or_clock_after_admission_refuses(self):
        original = self.admitted.receipt.model_copy(deep=True)
        self.admitted.receipt.spec.start_ticks += 1
        with self.assertRaises(ValueError):
            self.collect()
        self.admitted = replace(self.admitted, receipt=original)
        with self.assertRaisesRegex(ValueError, "launch clock changed"):
            self.collect(admitted=replace(self.admitted, started_monotonic=0.5))
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])

    def test_mutated_proc_identity_cannot_mutate_admission_snapshot(self):
        self.native.proc.spec.start_ticks += 1
        self.assertEqual(self.admitted.receipt.spec.start_ticks, 1234567)
        with self.assertRaisesRegex(ValueError, "retained identities changed"):
            self.collect()
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])

    def test_swapped_pipe_and_relaxed_aggregate_refuse_without_terminal_records(self):
        self.native.child.stdout = self.native.in_reader
        with self.assertRaises(ValueError):
            self.collect()
        self.native.child.stdout = self.native.out_reader
        (self.native.aggregate_path / "memory.max").write_text("max")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])
        self.assertFalse(self.fixture.frozen.exists())

    def test_receipt_mutation_during_capture_rolls_back(self):
        self.terminal()
        original = type(self.admitted).capture

        def mutate(admitted, *, cancelled):
            result = original(admitted, cancelled=cancelled)
            admitted.receipt.argv = digest(b"changed")
            return result

        with (
            patch.object(type(self.admitted), "capture", mutate),
            self.assertRaisesRegex(ValueError, "changed during capture"),
        ):
            self.collect()
        self.assertEqual(self.store.records("admission", NativeAdmissionRecord), [])
        self.assertEqual(self.store.records("collection", CodexCollection), [])

    def test_failed_native_preserves_admission_but_never_freezes(self):
        self.terminal(exit_code=1)
        collection, supervision = self.collect()
        self.assertNotEqual(collection.outcome.status, "completed")
        self.assertIsNone(collection.frozen)
        self.assertEqual(supervision.admission, record_digest(self.record()))
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")

    def test_missing_eof_preserves_incomplete_admitted_capture(self):
        self.native.out_writer.write(self.fixture.raw)
        self.native.err_writer.close()
        self.native.child.result = 0
        self.native.pid_writer.close()
        (self.native.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        (self.native.worker_path / "cgroup.procs").write_text("")
        self.supervisor.clock = supervisor_fixtures.FixtureClock(0.5)
        collection, supervision = self.collect()
        self.assertEqual(collection.outcome.status, "incomplete_capture")
        self.assertIsNone(collection.frozen)
        self.assertEqual(supervision.admission, record_digest(self.record()))

    def test_terminal_replay_refuses_without_duplicate_admission(self):
        self.terminal()
        self.collect()
        before = self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        with self.assertRaises(ValueError):
            self.collect()
        self.assertEqual(len(self.store.records("admission", NativeAdmissionRecord)), 1)
        self.assertEqual(
            self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], before
        )

    def test_worker_repopulation_during_freeze_refuses_records_and_retains_copy(self):
        from crewshal import integration

        self.terminal()
        original = integration.freeze_candidate

        def mutate(*args, **kwargs):
            frozen = original(*args, **kwargs)
            (self.native.worker_path / "cgroup.procs").write_text("777")
            (self.native.worker_path / "cgroup.events").write_text("populated 1\nfrozen 0")
            return frozen

        with patch.object(integration, "freeze_candidate", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "repopulated"):
                self.collect()
        for kind, contract in (
            ("admission", NativeAdmissionRecord),
            ("supervision", SupervisionReceipt),
            ("collection", CodexCollection),
            ("evidence", Evidence),
        ):
            self.assertEqual(self.store.records(kind, contract), [])
        self.assertTrue(self.fixture.frozen.exists())
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "ready")
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")

    def test_closed_receipt_record_rejects_authority_and_unknown_fields(self):
        self.terminal()
        self.collect()
        record = self.record()
        for changes in ({"execution_allowed": True}, {"spend_authorized": True}, {"unknown": "x"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                NativeAdmissionRecord.model_validate({**record.model_dump(), **changes})
