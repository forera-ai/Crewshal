"""Fresh coordinator integration fixtures; no native runtime or check is launched."""

from datetime import datetime, timezone
from dataclasses import replace
import json
import os
import sqlite3
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from crewshal.candidate import _scan_fd, freeze_candidate, prepare_candidate, validator_evidence
from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    CheckDefinition,
    Claim,
    Evidence,
    Run,
    Task,
    Usage,
    record_digest,
)
from crewshal.discovery import discover
from crewshal.durable import CoordinatorStore
from crewshal.integration import (
    ORIGINAL_VOLUME_COLLECTION_UNRESOLVED,
    CodexCollection,
    collect_codex_attempt,
    collect_original_volume_codex,
    scope_digest,
)
from crewshal.model import digest, model_digest
from crewshal.runtime import CodexIdentity, ProcessObservation


EMPTY = digest(b"")
NOW = datetime(2026, 10, 8, tzinfo=timezone.utc)


class Phase2DIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.original = self.root / "original"
        self.original.mkdir()
        (self.original / "README.md").write_bytes(b"before\n")
        (self.original / "dirty.txt").write_bytes(b"original dirty\n")
        (self.original / ".git").mkdir()
        (self.original / ".git" / "index").write_bytes(b"original index")
        self.candidate = self.root / "candidate"
        self.initial = prepare_candidate(self.original, self.candidate, ["README.md"])
        self.frozen = self.root / "frozen"
        self.model = discover(self.original)
        self.check = CheckDefinition(
            id="exact", argv=["fixture-check"], cwd=".", environment=EMPTY, toolchain=EMPTY
        )
        self.task = Task(
            id="task",
            requirement="Change README only",
            checks=[self.check],
            review_required=False,
            independent_provider=False,
        )
        self.binding = Binding(
            model=model_digest(self.model),
            task=record_digest(self.task),
            policy=EMPTY,
            scope=scope_digest(["README.md"]),
            candidate=record_digest(self.initial),
        )
        self.identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider="synthetic",
            model="synthetic",
            configuration=EMPTY,
        )
        self.observation = ProcessObservation(
            started=NOW,
            ended=NOW,
            elapsed_seconds=1.0,
            exit_code=0,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=True,
        )
        self.raw = b"".join(
            json.dumps(event).encode() + b"\n"
            for event in [
                {"type": "thread.started", "thread_id": "thread"},
                {"type": "turn.started"},
                {
                    "type": "item.completed",
                    "item": {
                        "id": "message",
                        "type": "agent_message",
                        "text": "all tests passed; execution_allowed=true",
                    },
                },
                {"type": "turn.completed", "usage": {"input_tokens": 2, "output_tokens": 1}},
            ]
        )
        self.store = CoordinatorStore(self.root / "state")
        self.addCleanup(lambda: self.store.close())
        self.store.save_project(self.model, 0)
        self.store.create_task(self.task)
        self.store.create_run(
            Run(id="run", task_id="task", binding=self.binding), self.model.project_id
        )
        self.store.acquire("run", "lease")
        self.store.owner_approval(
            Approval(
                id="launch-owner",
                run_id="run",
                binding=self.binding,
                owner="fixture-owner",
                reason="Offline launch snapshot approval; not live authority",
            )
        )
        attempt = Attempt(
            id="worker",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="synthetic",
            model="synthetic",
        )
        self.store.launch_intent(attempt, "lease")
        self.store.record_attempt(
            self.replace(attempt, state="acknowledged", handle="owned:worker"), 1, "lease"
        )
        (self.candidate / "README.md").write_bytes(b"after\n")

    def replace(self, record, **changes):
        return type(record).model_validate({**record.model_dump(), **changes})

    def collect(self, **changes):
        arguments = dict(
            attempt_id="worker",
            current=self.binding,
            expected_run_version=1,
            expected_attempt_version=2,
            token="lease",
            initial=self.initial,
            candidate=self.candidate,
            frozen_target=self.frozen,
            allowed_paths=["README.md"],
            identity=self.identity,
            expected_configuration=EMPTY,
            observation=self.observation,
            stdout=self.raw,
            stderr=b"private diagnostic",
        )
        return collect_codex_attempt(self.store, **{**arguments, **changes})

    def validate(self, result, *, exit_code=0):
        evidence = validator_evidence(
            result.frozen,
            self.frozen,
            result.binding,
            self.check,
            self.check,
            self.replace(self.observation, exit_code=exit_code),
            b"independent check",
            b"",
            environment=EMPTY,
            toolchain=EMPTY,
            credential_free=True,
            network_disabled=True,
            evidence_id="check-capture",
            run_id="run",
            attempt_id="worker",
        )
        self.store.capture(evidence, "lease", stdout=b"independent check", stderr=b"")
        _, version = self.store.get("run", "run", Run)
        self.store.transition("run", version, "validating", "lease")

    def verdict(self, result):
        return self.store.verdict(
            "run", self.model.project_id, result.binding, "lease", candidate_root=self.frozen
        )

    def approve_frozen(self, result):
        self.store.owner_approval(
            Approval(
                id="candidate-owner",
                run_id="run",
                binding=result.binding,
                owner="fixture-owner",
                reason="Explicit fixture candidate approval",
            )
        )

    def test_changed_candidate_preserves_launch_and_requires_current_approval(self):
        result = self.collect()
        self.assertEqual(result.outcome.status, "completed")
        self.assertEqual(result.launch_binding, self.binding)
        self.assertNotEqual(result.binding.candidate, self.binding.candidate)
        self.assertEqual(result.binding.candidate, record_digest(result.frozen))
        self.assertFalse(result.execution_allowed)
        self.assertFalse(result.outcome.execution_allowed)
        attempt, _ = self.store.get("attempt", "worker", Attempt)
        self.assertEqual(attempt.binding, result.binding)
        self.assertEqual(attempt.handle, "owned:worker")
        self.assertEqual(result.outcome.attempt.binding, self.binding)
        self.assertEqual(len(self.store.records("claim", Claim)), 1)
        self.assertEqual([e.kind for e in self.store.records("evidence", Evidence)], ["scope"])
        self.validate(result)
        blocked = self.verdict(result)
        self.assertEqual(blocked.status, "blocked")
        self.assertEqual(blocked.gates["approval"], "missing")
        self.approve_frozen(result)
        verdict = self.verdict(result)
        self.assertEqual(verdict.status, "verified")
        self.assertFalse(verdict.execution_allowed)
        self.assertEqual((self.original / "README.md").read_bytes(), b"before\n")
        self.assertEqual((self.original / "dirty.txt").read_bytes(), b"original dirty\n")
        self.assertEqual((self.original / ".git" / "index").read_bytes(), b"original index")

    def test_false_completion_cannot_replace_missing_or_failed_check(self):
        result = self.collect()
        self.approve_frozen(result)
        blocked = self.verdict(result)
        self.assertEqual(blocked.gates["check:exact"], "missing")
        self.validate(result, exit_code=1)
        self.assertEqual(self.verdict(result).status, "failed")

    def test_outside_scope_is_captured_and_never_passes(self):
        (self.candidate / "extra").write_bytes(b"unapproved")
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        self.assertEqual(self.verdict(result).gates["scope"], "blocking_findings")

    def test_stale_versions_binding_manifest_scope_and_lease_refuse_before_freeze(self):
        variants = [
            {"expected_run_version": 0},
            {"expected_attempt_version": 1},
            {"token": "wrong"},
            {"current": self.replace(self.binding, policy=digest(b"wrong"))},
            {"initial": self.replace(self.initial, files=[])},
            {"allowed_paths": []},
        ]
        for changes in variants:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.collect(**changes)
            self.assertFalse(self.frozen.exists())
            self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.collect()

    def test_terminal_replay_refuses_without_creating_second_copy(self):
        self.collect()
        with self.assertRaises(ValueError):
            self.collect(frozen_target=self.root / "replay")
        self.assertFalse((self.root / "replay").exists())
        self.assertEqual(len(self.store.records("collection", CodexCollection)), 1)

    def test_native_failure_timeout_and_missing_stop_never_freeze(self):
        result = self.collect(observation=self.replace(self.observation, termination="timeout"))
        self.assertEqual(result.outcome.status, "timeout")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "failed")

    def test_incomplete_stop_and_malformed_events_preserve_refusal(self):
        result = self.collect(observation=self.replace(self.observation, tree_stopped=False))
        self.assertEqual(result.outcome.status, "incomplete_capture")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())

    def test_malformed_output_captures_failure_instead_of_success_claim(self):
        result = self.collect(stdout=b'{"type":"forged-evidence"}\n')
        self.assertEqual(result.outcome.status, "malformed")
        self.assertIsNone(result.frozen)
        self.assertEqual(result.stdout, digest(b'{"type":"forged-evidence"}\n'))

    def test_capture_overflow_refuses_and_leaves_reconciliation_required(self):
        with self.assertRaises(ValueError):
            self.collect(stdout=b"x" * 65537)
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")

    def test_restart_reads_capture_and_private_artifact_tampering_refuses_verdict(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        stored, _ = self.store.get("collection", result.id, CodexCollection)
        self.assertEqual(stored, result)
        (self.root / "state" / "artifacts" / result.stdout).write_bytes(b"forged")
        with self.assertRaises(ValueError):
            self.verdict(result)

    def test_validator_copy_mutation_refuses_after_collection(self):
        result = self.collect()
        (self.frozen / "README.md").write_bytes(b"changed again")
        with self.assertRaises(ValueError):
            self.validate(result)

    def test_mutation_after_successful_validation_refuses_final_verdict(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        (self.frozen / "README.md").write_bytes(b"changed after check")
        with self.assertRaises(ValueError):
            self.verdict(result)

    def test_collection_verdict_requires_fresh_candidate_readback(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        with self.assertRaises(ValueError):
            self.store.verdict("run", self.model.project_id, result.binding, "lease")

    def test_sql_failure_rolls_back_state_and_keeps_owned_copy_for_inspection(self):
        self.store.connection.execute(
            "CREATE TEMP TRIGGER refuse_collection BEFORE INSERT ON records "
            "WHEN NEW.kind='collection' BEGIN "
            "SELECT RAISE(ABORT, 'fixture collection failure'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.collect()
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "ready")
        self.assertEqual(self.store.records("collection", CodexCollection), [])
        self.assertEqual(self.store.records("claim", Claim), [])
        self.assertEqual(self.store.records("evidence", Evidence), [])
        self.assertEqual(self.store.records("usage", Usage), [])
        self.assertEqual((self.frozen / "README.md").read_bytes(), b"after\n")
        self.store.connection.execute("DROP TRIGGER refuse_collection")
        with self.assertRaises(ValueError):
            self.collect()

    def test_failed_freeze_does_not_persist_terminal_or_receipt(self):
        (self.candidate / "link").symlink_to(self.original / "dirty.txt")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(self.store.records("collection", CodexCollection), [])
        self.assertFalse(self.frozen.exists())

    def test_changed_configuration_is_recorded_as_stale_without_freeze(self):
        result = self.collect(expected_configuration=digest(b"different configuration"))
        self.assertEqual(result.outcome.status, "stale")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())

    def test_candidate_paths_cannot_include_private_coordinator_state(self):
        with self.assertRaises(ValueError):
            self.collect(frozen_target=self.store.directory / "worker-readable")
        with self.assertRaises(ValueError):
            self.collect(candidate=self.store.directory)
        self.assertEqual(self.store.records("collection", CodexCollection), [])

    def test_other_attempt_and_failed_copy_leave_no_partial_database_capture(self):
        other = Attempt(
            id="other",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="synthetic",
            model="synthetic",
        )
        self.store.launch_intent(other, "lease")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.records("collection", CodexCollection), [])


class Phase2DOriginalVolumeCollection(unittest.TestCase):
    """Real fresh SQLite/files/retained FDs; Linux custody is an explicit seam."""

    def setUp(self):
        # Use only the fixture helper, never inherit its tests or reuse artifacts.
        from tests.acceptance import test_phase_2d_supervisor as supervisor_fixtures
        from tests.acceptance import test_phase_2d_admission as admission_fixtures
        from crewshal.admission import NativeAdmissionSpec, RetainedProc
        from crewshal.linux_bridge import StoppedNativeBridge
        from crewshal.linux_freeze import OriginalVolumeFreeze
        from crewshal.supervisor import CapturedProcess

        helper = supervisor_fixtures.Phase2DSupervisor()
        self.addCleanup(helper.doCleanups)
        fixture, self.dispatch = helper.integration_fixture()
        self.fixture = fixture
        native_fixture = admission_fixtures.Phase2DAdmission()
        native_fixture.setUp()
        self.addCleanup(native_fixture.doCleanups)
        self.native_fixture = native_fixture
        self.original_dirty = (fixture.original / "dirty.txt").read_bytes()
        fixture.candidate.rename(fixture.root / "candidate-upper")
        fixture.candidate = fixture.root / "candidate-upper"
        fixture.frozen = fixture.root / "validator-frozen"
        manifest = freeze_candidate(fixture.candidate, fixture.frozen, tree_stopped=True)
        descriptor = os.open(fixture.frozen, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        actual = os.fstat(descriptor)
        self.projection = descriptor
        self.projection_identity = actual.st_dev, actual.st_ino
        self.initial_projection = record_digest(manifest)
        installation = SimpleNamespace(
            growth=SimpleNamespace(store=fixture.store),
            production=SimpleNamespace(root=str(fixture.root)),
            reservation=SimpleNamespace(_retain_installation_refusal=Mock()),
        )
        frozen = object.__new__(OriginalVolumeFreeze)
        frozen.installation, frozen.manifest, frozen.failed = installation, manifest, False
        frozen.handles = {"readonly-projection": descriptor, "frozen-root": descriptor}
        frozen.verify_custody = Mock()
        frozen._verify_terminal_kernel = Mock()

        def projection_readback():
            # Read actual original pinned inode/content. Readonly/UID/mount and
            # original host task kernel validation remain explicitly synthetic.
            info = os.fstat(frozen.handles["readonly-projection"])
            if (
                (info.st_dev, info.st_ino) != self.projection_identity
                or _scan_fd(descriptor)[0] != frozen.manifest
                or record_digest(frozen.manifest) != self.initial_projection
            ):
                raise ValueError("synthetic original projection readback changed")

        frozen._verify_projection = Mock(side_effect=projection_readback)
        installation._freeze = frozen
        bridge = self.bridge = object.__new__(StoppedNativeBridge)
        bridge.installation, bridge.freeze, bridge.failed, bridge.stage = (
            installation,
            frozen,
            False,
            3,
        )
        installation._bridge = bridge
        spec = NativeAdmissionSpec.model_validate(
            {
                **native_fixture.spec.model_dump(),
                "configuration": record_digest(self.dispatch.configuration),
            }
        )
        bridge.native = RetainedProc(
            native_fixture.proc.descriptor, native_fixture.pid_reader.fileno(), spec
        )
        self.addCleanup(bridge.native.close)
        bridge.lifetime = SimpleNamespace(
            controls=SimpleNamespace(configuration=self.dispatch.configuration),
            worker=native_fixture.worker,
        )
        initial = native_fixture.worker.sample()
        (native_fixture.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        (native_fixture.worker_path / "cgroup.procs").write_text("")
        final = native_fixture.worker.sample()
        captured = CapturedProcess(
            fixture.observation, fixture.raw, b"diagnostic", initial, final, False, False
        )
        bridge.native_capture = bridge._capture_owner = captured
        bridge._capture_streams = (captured.stdout, captured.stderr)
        bridge.capture_packets = [captured.stdout, captured.stderr, b"synthetic closed header"]
        bridge._capture_records = (
            captured.observation.model_dump_json(),
            captured.initial.model_dump_json(),
            captured.final.model_dump_json(),
            captured.overflow,
            captured.stop_error,
        )
        # The bridge's real immutable capture validation runs. Only Linux
        # observer/task/timer/namespace readback is replaced with this seam.
        bridge._verify_original = Mock()

    def collect(self, **changes):
        fixture = self.fixture
        arguments = dict(
            expected_run_version=1,
            expected_attempt_version=2,
            token="lease",
            initial=fixture.initial,
            allowed_paths=["README.md"],
        )
        store = changes.pop("store", fixture.store)
        dispatch = changes.pop("dispatch", self.dispatch)
        with (
            patch(
                "crewshal.integration.freeze_candidate", side_effect=AssertionError("no path copy")
            ),
            patch("subprocess.Popen.__init__", side_effect=AssertionError("no child startup")),
        ):
            return collect_original_volume_codex(
                store, self.bridge, dispatch, **{**arguments, **changes}
            )

    def assert_uncommitted(self):
        from crewshal.supervisor import SupervisionReceipt

        store = self.fixture.store
        self.assertEqual(store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(store.get("run", "run", Run)[0].state, "ready")
        self.assertEqual(store.records("collection", CodexCollection), [])
        self.assertEqual(store.records("supervision", SupervisionReceipt), [])
        self.assertEqual(store.records("evidence", Evidence), [])
        self.assertEqual((self.fixture.frozen / "README.md").read_bytes(), b"after\n")
        os.fstat(self.projection)

    def test_original_capture_persists_actual_host_supervision_and_scope_link(self):
        from crewshal.supervisor import SupervisionReceipt

        result = self.collect()
        self.assertEqual(result.outcome.status, "completed")
        self.assertEqual(result.frozen, self.bridge.freeze.manifest)
        receipts = self.fixture.store.records("supervision", SupervisionReceipt)
        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt.pid, self.bridge.native.spec.pid)
        self.assertEqual(receipt.dispatch, record_digest(self.dispatch))
        self.assertEqual(receipt.collection, record_digest(result))
        self.assertEqual(receipt.initial, self.bridge.native_capture.initial)
        self.assertEqual(receipt.final, self.bridge.native_capture.final)
        self.assertEqual((receipt.stdout, receipt.stderr), (result.stdout, result.stderr))
        self.assertIsNone(receipt.admission)
        self.assertEqual(
            ORIGINAL_VOLUME_COLLECTION_UNRESOLVED,
            ("original_namespace_admission_receipt_transport",),
        )
        self.assertEqual(
            self.fixture.store.connection.execute(
                "SELECT count(*) FROM records WHERE kind='admission'"
            ).fetchone()[0],
            0,
        )
        evidence = self.fixture.store.records("evidence", Evidence)[0]
        self.assertIn(record_digest(receipt), evidence.artifacts)
        self.assertTrue(
            (self.fixture.store.directory / "artifacts" / record_digest(receipt)).is_file()
        )
        self.assertGreaterEqual(self.bridge._verify_original.call_count, 4)
        self.assertEqual((self.fixture.original / "dirty.txt").read_bytes(), self.original_dirty)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.collect()

    def test_forged_dispatch_requirement_and_task_digest_cannot_pass_current_binding(self):
        dispatch = self.dispatch.model_copy(deep=True)
        dispatch.request.requirement = "silently broaden task"
        dispatch.task_digest = digest(b"forged task")
        with self.assertRaisesRegex(ValueError, "source/task/configuration"):
            self.collect(dispatch=dispatch)
        self.assert_uncommitted()
        self.assertTrue(self.bridge._collection_attempted)
        self.assertTrue(self.bridge.failed)

    def test_source_configuration_forgery_refuses_even_with_matching_bridge_hashes(self):
        dispatch = self.dispatch.model_copy(deep=True)
        dispatch.configuration.source_sha256["integration.py"] = digest(b"stale implementation")
        fingerprint = record_digest(dispatch.configuration)
        dispatch.request.identity.configuration = fingerprint
        dispatch.qualification.configuration = fingerprint
        self.bridge.lifetime.controls.configuration = dispatch.configuration
        self.bridge.native.spec.configuration = fingerprint
        with self.assertRaisesRegex(ValueError, "source/task/configuration"):
            self.collect(dispatch=dispatch)
        self.assert_uncommitted()

    def test_other_original_store_cannot_import_or_reopen_sqlite_and_consumes_bridge(self):
        other = CoordinatorStore(self.fixture.root / "other-state")
        self.addCleanup(other.close)
        with self.assertRaisesRegex(ValueError, "store/bridge custody"):
            self.collect(store=other)
        self.assert_uncommitted()
        self.assertTrue(self.bridge._collection_attempted)
        self.assertTrue(self.bridge.failed)
        self.bridge.installation.reservation._retain_installation_refusal.assert_called_once()

    def test_substituted_capture_refuses_before_any_sqlite_or_artifact_write(self):
        self.bridge.native_capture = replace(self.bridge.native_capture, stdout=b"replacement")
        with self.assertRaisesRegex(ValueError, "capture changed"):
            self.collect()
        self.assert_uncommitted()
        self.assertFalse((self.fixture.store.directory / "artifacts").exists())

    def test_mutated_capture_record_refuses_while_retaining_original_packets(self):
        self.bridge.native_capture.initial.populated = False
        with self.assertRaisesRegex(ValueError, "capture changed"):
            self.collect()
        self.assert_uncommitted()
        self.assertIs(self.bridge.capture_packets[0], self.bridge._capture_streams[0])

    def test_sql_rollback_retains_actual_projection_artifacts_and_consumed_bridge(self):
        store = self.fixture.store
        store.connection.execute(
            "CREATE TEMP TRIGGER refuse_original_supervision "
            "BEFORE INSERT ON records WHEN NEW.kind='supervision' "
            "BEGIN SELECT RAISE(ABORT, 'fixture original SQL failure'); END"
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "original SQL failure"):
            self.collect()
        self.assert_uncommitted()
        self.assertEqual(store.records("usage", Usage), [])
        self.assertEqual(store.records("claim", Claim), [])
        self.assertGreater(len(list((store.directory / "artifacts").iterdir())), 0)
        self.assertTrue(self.bridge._collection_attempted)
        self.assertTrue(self.bridge.failed)
        store.connection.execute("DROP TRIGGER refuse_original_supervision")
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.collect()

    def test_capture_mutation_during_artifact_write_rolls_back_and_retains_artifact(self):
        store = self.fixture.store
        actual_write = store._artifact

        def changed(fingerprint, data):
            actual_write(fingerprint, data)
            self.bridge.native_capture = replace(self.bridge.native_capture, stdout=b"substituted")

        with patch.object(store, "_artifact", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "capture changed"):
                self.collect()
        self.assert_uncommitted()
        self.assertGreater(len(list((store.directory / "artifacts").iterdir())), 0)

    def test_stale_versions_lease_and_scope_refuse_without_store_terminal_state(self):
        # Fresh class instance per invocation; refused attempts cannot retry.
        with self.assertRaisesRegex(ValueError, "state version changed"):
            self.collect(expected_attempt_version=1)
        self.assert_uncommitted()
        self.assertTrue(self.bridge._collection_attempted)

    def test_wrong_lease_cannot_write_collection(self):
        with self.assertRaises(ValueError):
            self.collect(token="wrong")
        self.assert_uncommitted()

    def test_stale_initial_manifest_cannot_rebind_original_frozen_projection(self):
        with self.assertRaisesRegex(ValueError, "snapshot/scope"):
            self.collect(initial=self.fixture.replace(self.fixture.initial, files=[]))
        self.assert_uncommitted()

    def test_other_scope_cannot_broaden_original_approved_candidate(self):
        with self.assertRaisesRegex(ValueError, "snapshot/scope"):
            self.collect(allowed_paths=["README.md", "dirty.txt"])
        self.assert_uncommitted()

    def test_original_projection_inode_replacement_cannot_be_path_copy_fallback(self):
        replacement = self.fixture.root / "replacement"
        replacement.mkdir()
        (replacement / "README.md").write_bytes(b"after\n")
        descriptor = os.open(replacement, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        self.bridge.freeze.handles["readonly-projection"] = descriptor
        with self.assertRaisesRegex(ValueError, "projection readback changed"):
            self.collect()
        self.assert_uncommitted()

    def test_projection_change_after_receipt_write_rolls_back_before_commit(self):
        store = self.fixture.store
        actual_put = store._put

        def altered(kind, key, record, version):
            actual_put(kind, key, record, version)
            if kind == "supervision":
                path = self.fixture.frozen / "README.md"
                path.chmod(0o600)
                path.write_bytes(b"projection changed after receipt")

        with patch.object(store, "_put", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "projection readback changed"):
                self.collect()
        self.assertEqual(store.get("run", "run", Run)[0].state, "ready")
        self.assertEqual(store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(
            store.connection.execute(
                "SELECT count(*) FROM records WHERE kind IN ('collection','supervision','evidence')"
            ).fetchone()[0],
            0,
        )
        self.assertTrue(self.bridge.failed)
        self.assertTrue(self.bridge.freeze.failed)
        self.assertGreater(len(list((store.directory / "artifacts").iterdir())), 0)
        os.fstat(self.projection)

    def test_dispatch_requirement_task_runtime_provider_and_check_each_remain_bound(self):
        modifications = (
            lambda d: setattr(d.request, "requirement", "different task"),
            lambda d: setattr(d, "task_digest", digest(b"different task")),
            lambda d: setattr(d.qualification, "runtime", "different runtime"),
            lambda d: setattr(d.qualification, "architecture", "x86_64"),
            lambda d: setattr(d.request.identity, "provider", "different-provider"),
            lambda d: setattr(d.configuration, "validator_argv", ["/bin/false"]),
        )
        for change in modifications:
            with self.subTest(change=change):
                fresh = Phase2DOriginalVolumeCollection()
                fresh.setUp()
                try:
                    dispatch = fresh.dispatch.model_copy(deep=True)
                    change(dispatch)
                    # These matching data fields cannot replace source/task
                    # preparation. Kernel custody remains the fixture seam.
                    fresh.bridge.lifetime.controls.configuration = dispatch.configuration
                    fresh.bridge.native.spec.configuration = record_digest(dispatch.configuration)
                    with self.assertRaises(ValueError):
                        fresh.collect(dispatch=dispatch)
                    fresh.assert_uncommitted()
                    self.assertTrue(fresh.bridge._collection_attempted)
                finally:
                    fresh.doCleanups()


if __name__ == "__main__":
    unittest.main()
