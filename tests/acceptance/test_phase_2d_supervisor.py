"""Fresh pipes/controller-file fixtures, never Linux/native qualification.

The child poll handle, clock and cgroup.kill effect are explicitly synthetic.
Actual descriptor IO, bounded readback, copying and SQLite transactions are real.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from crewshal.contracts import Approval, Attempt, Binding, Evidence, Run, record_digest
from crewshal.durable import Conflict
from crewshal.dispatch import CodexDispatch, prepare_dispatch_configuration
from crewshal.runtime import CodexRequest
from crewshal.supervisor import (
    CgroupIdentity,
    OwnedCgroup,
    SupervisionReceipt,
    capture_attached_process,
    collect_supervised_codex,
)
from tests.acceptance import test_phase_2d_integration as integration_fixtures
from tests.acceptance import test_phase_2d_dispatch as dispatch_fixtures


NOW = datetime(2026, 10, 8, tzinfo=timezone.utc)


class FixtureProcess:
    pid = 12345

    def __init__(self, poll):
        self.readback = poll

    def poll(self):
        return self.readback()


class FixtureClock:
    def __init__(self, step=0.05):
        self.value = 0
        self.step = step

    def __call__(self):
        self.value += self.step
        return self.value


class Phase2DSupervisor(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.group_path = self.root / "controllers"
        self.group_path.mkdir()
        self.values = {
            "memory.max": "134217728\n",
            "memory.swap.max": "0\n",
            "cpu.max": "100000 100000\n",
            "pids.max": "32\n",
            "cgroup.type": "domain\n",
            "cgroup.events": "populated 0\nfrozen 0\n",
            "cgroup.procs": "",
            "memory.events": "low 0\nhigh 0\nmax 0\noom 0\noom_kill 0\n",
            "pids.events": "max 0\n",
            "cgroup.kill": "",
        }
        for name, value in self.values.items():
            self.write(name, value)
        info = self.group_path.stat()
        self.identity = CgroupIdentity(
            relative_path="owned.slice/worker.service",
            device=info.st_dev,
            inode=info.st_ino,
        )
        descriptor = os.open(self.group_path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            self.group = OwnedCgroup(descriptor, self.identity)
        finally:
            os.close(descriptor)
        self.addCleanup(self.group.close)
        self.stdout, self.out_writer = os.pipe()
        self.stderr, self.err_writer = os.pipe()
        self.descriptors = {self.stdout, self.out_writer, self.stderr, self.err_writer}
        self.addCleanup(self.close_descriptors)
        self.process = FixtureProcess(lambda: 0)
        self.clock = FixtureClock()

    def close_descriptors(self):
        for descriptor in self.descriptors:
            os.close(descriptor)
        self.descriptors.clear()

    def close_writer(self, descriptor):
        os.close(descriptor)
        self.descriptors.remove(descriptor)

    def write(self, name, value):
        (self.group_path / name).write_text(value)

    def eof(self, stdout=b"", stderr=b""):
        os.write(self.out_writer, stdout)
        os.write(self.err_writer, stderr)
        self.close_writer(self.out_writer)
        self.close_writer(self.err_writer)

    def capture(self, **changes):
        arguments = dict(started=NOW, started_monotonic=0.0, cancelled=lambda: False)
        with patch("crewshal.supervisor.time.monotonic", self.clock):
            return capture_attached_process(
                self.process,
                self.group,
                self.stdout,
                self.stderr,
                **{**arguments, **changes},
            )

    def synthetic_stop(self):
        # Real stop write is checked first; synthetic fixture updates controllers.
        self.group.stop_original()
        self.write("cgroup.events", "populated 0\nfrozen 0\n")
        self.write("cgroup.procs", "")
        self.process.readback = lambda: -9

    def patch_stop(self):
        self.group.stop_original = self.group.stop
        return patch.object(self.group, "stop", self.synthetic_stop)

    def test_complete_pipes_and_recursive_empty_readback_produce_capture(self):
        self.eof(b"literal native bytes\n", b"diagnostic")
        result = self.capture()
        self.assertEqual(result.stdout, b"literal native bytes\n")
        self.assertEqual(result.stderr, b"diagnostic")
        self.assertTrue(result.observation.tree_stopped)
        self.assertTrue(result.observation.stdout_complete)
        self.assertTrue(result.observation.stderr_complete)
        self.assertEqual(result.observation.exit_code, 0)
        self.assertIsNone(result.observation.termination)
        self.assertEqual((self.group_path / "cgroup.kill").read_bytes(), b"")
        self.assertTrue(os.get_blocking(self.stdout))

    def test_root_exit_and_empty_direct_pids_do_not_hide_descendant(self):
        self.write("cgroup.events", "populated 1\nfrozen 0\n")
        self.eof(b"worker says stopped\n")
        with self.patch_stop():
            result = self.capture()
        self.assertEqual(result.observation.termination, "interrupted")
        self.assertTrue(result.observation.tree_stopped)
        self.assertTrue(result.initial.populated)
        self.assertEqual((self.group_path / "cgroup.kill").read_bytes(), b"1")

    def test_empty_group_does_not_replace_reaped_native_handle(self):
        self.process = FixtureProcess(lambda: None)
        self.eof(b"native completion\n")
        self.clock = FixtureClock(0.25)
        result = self.capture()
        self.assertEqual(result.observation.termination, "timeout")
        self.assertFalse(result.observation.tree_stopped)

    def test_timeout_includes_time_before_attachment(self):
        self.clock.value = 5
        self.process = FixtureProcess(lambda: None)
        self.write("cgroup.events", "populated 1\nfrozen 0\n")
        self.eof()
        with self.patch_stop():
            result = self.capture()
        self.assertEqual(result.observation.termination, "timeout")
        self.assertTrue(result.observation.tree_stopped)

    def test_cancel_stops_only_owned_subtree_and_preserves_capture(self):
        self.eof(b"partial")
        with self.patch_stop():
            result = self.capture(cancelled=lambda: True)
        self.assertEqual(result.observation.termination, "cancelled")
        self.assertEqual(result.stdout, b"partial")
        self.assertTrue(result.observation.tree_stopped)

    def test_failed_stop_never_claims_tree_stopped(self):
        self.write("cgroup.events", "populated 1\nfrozen 0\n")
        self.eof()
        with patch.object(self.group, "stop", side_effect=PermissionError("synthetic denial")):
            result = self.capture(cancelled=lambda: True)
        self.assertTrue(result.stop_error)
        self.assertFalse(result.observation.tree_stopped)

    def test_open_stream_after_exit_never_becomes_complete(self):
        self.clock = FixtureClock(0.5)
        self.close_writer(self.err_writer)
        result = self.capture()
        self.assertFalse(result.observation.stdout_complete)
        self.assertTrue(result.observation.stderr_complete)
        self.assertTrue(result.observation.tree_stopped)
        self.assertGreaterEqual(result.observation.elapsed_seconds, 10)

    def test_overflow_bounded_during_io_not_after_accumulation(self):
        sent = 0

        def poll():
            nonlocal sent
            if sent <= 65536:
                os.write(self.out_writer, b"x" * 4096)
                sent += 4096
            return 0

        self.process = FixtureProcess(poll)
        self.close_writer(self.err_writer)
        with self.patch_stop():
            result = self.capture()
        self.assertEqual(len(result.stdout), 65536)
        self.assertTrue(result.overflow)
        self.assertFalse(result.observation.stdout_complete)
        self.assertEqual(result.observation.termination, "quota")

    def test_refusal_counters_during_capture_block_success(self):
        def poll():
            self.write("pids.events", "max 1\n")
            return 0

        self.process = FixtureProcess(poll)
        self.eof(b"success\n")
        with self.patch_stop():
            result = self.capture()
        self.assertEqual(result.observation.termination, "quota")

    def test_exact_stream_ceiling_with_eof_is_not_overflow(self):
        sent = 0

        def poll():
            nonlocal sent
            if sent < 65536:
                os.write(self.out_writer, b"x" * 4096)
                sent += 4096
            elif self.out_writer in self.descriptors:
                self.close_writer(self.out_writer)
            return 0

        self.process = FixtureProcess(poll)
        self.close_writer(self.err_writer)
        result = self.capture()
        self.assertEqual(len(result.stdout), 65536)
        self.assertFalse(result.overflow)
        self.assertTrue(result.observation.stdout_complete)
        self.assertIsNone(result.observation.termination)

    def test_poll_failure_best_effort_stops_owned_group_and_restores_pipe_flags(self):
        def fail():
            raise RuntimeError("synthetic handle failure")

        self.process = FixtureProcess(fail)
        with self.assertRaisesRegex(RuntimeError, "synthetic handle failure"):
            self.capture()
        self.assertEqual((self.group_path / "cgroup.kill").read_bytes(), b"1")
        self.assertTrue(os.get_blocking(self.stdout))

    def test_signal_exit_retains_failed_termination(self):
        self.process = FixtureProcess(lambda: -9)
        self.eof(b"worker says success\n")
        result = self.capture()
        self.assertEqual(result.observation.exit_code, -9)
        self.assertEqual(result.observation.termination, "signal")

    def test_nonzero_initial_counters_refuse_reused_group(self):
        self.write("memory.events", "max 0\noom 0\noom_kill 1\n")
        with self.assertRaisesRegex(ValueError, "zero resource-refusal"):
            self.capture()
        self.assertEqual((self.group_path / "cgroup.kill").read_bytes(), b"")

    def test_changed_controls_or_missing_files_during_capture_refuse_stop_proof(self):
        def poll():
            self.write("memory.max", "max\n")
            return 0

        self.process = FixtureProcess(poll)
        self.eof(b"success\n")
        result = self.capture()
        self.assertIsNone(result.final)
        self.assertFalse(result.observation.tree_stopped)
        self.assertEqual(result.observation.termination, "interrupted")

    def test_controller_alias_fifo_oversize_duplicates_and_invalid_state_refuse(self):
        cases = [
            ("cgroup.events", "populated 0\npopulated 1\nfrozen 0\n"),
            ("cgroup.events", "populated 2\nfrozen 0\n"),
            ("cgroup.events", "populated 0\n"),
            ("cgroup.procs", "0\n"),
            ("memory.events", "max -1\noom 0\noom_kill 0\n"),
            ("memory.max", "x" * 4097),
            ("cgroup.type", "threaded\n"),
        ]
        for name, value in cases:
            with self.subTest(name=name, value=value[:32]):
                self.write(name, value)
                with self.assertRaises(ValueError):
                    self.group.sample()
                self.write(name, self.values[name])
        file = self.group_path / "cgroup.events"
        file.unlink()
        file.symlink_to(self.group_path / "pids.events")
        with self.assertRaises(OSError):
            self.group.sample()
        file.unlink()
        os.mkfifo(file)
        with self.assertRaises(ValueError):
            self.group.sample()

    def test_pinned_fd_survives_path_replacement_without_touching_new_group(self):
        self.group_path.rename(self.root / "original-group")
        self.group_path.mkdir()
        (self.group_path / "cgroup.kill").write_bytes(b"unrelated")
        self.group.stop()
        self.assertEqual((self.root / "original-group" / "cgroup.kill").read_bytes(), b"1")
        self.assertEqual((self.group_path / "cgroup.kill").read_bytes(), b"unrelated")

    def test_wrong_inode_and_unsafe_subtree_identity_refuse(self):
        for value in [
            "",
            "/owned/worker",
            "owned",
            "owned/../other",
            "owned//worker",
            "./owned/worker",
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                CgroupIdentity(relative_path=value, device=1, inode=1)
        with self.assertRaises(ValueError):
            OwnedCgroup(
                self.group.descriptor,
                CgroupIdentity(
                    relative_path="owned/worker",
                    device=self.identity.device,
                    inode=self.identity.inode + 1,
                ),
            )

    def test_pipe_alias_regular_file_and_launch_clock_refuse(self):
        duplicate = os.dup(self.stdout)
        self.descriptors.add(duplicate)
        with self.assertRaisesRegex(ValueError, "aliased"):
            capture_attached_process(
                self.process,
                self.group,
                self.stdout,
                duplicate,
                started=NOW,
                started_monotonic=0.0,
                cancelled=lambda: False,
            )
        with self.assertRaises(ValueError):
            self.capture(started_monotonic=float("nan"))
        with self.assertRaises(ValueError):
            self.capture(started_monotonic=1000.0)
        with self.assertRaises(ValueError):
            self.capture(started=NOW.replace(tzinfo=None))
        with patch("crewshal.supervisor.sys.platform", "darwin"), self.assertRaises(ValueError):
            OwnedCgroup.attach(self.identity)

    def integration_fixture(self):
        # Each call constructs its own state, original dirty bytes and snapshots.
        fixture = integration_fixtures.Phase2DIntegration()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        preparation = dispatch_fixtures.Phase2DDispatch()
        preparation.setUp()
        self.addCleanup(preparation.doCleanups)
        # Recreate durable state with the exact prepared task/check/model. The
        # earlier helper's generic task is not promoted to this narrow dispatch.
        fixture.store.close()
        fixture.store = type(fixture.store)(fixture.root / "supervised-state")
        fixture.task = preparation.replace(
            preparation.task,
            checks=[
                preparation.replace(
                    preparation.task.checks[0],
                    environment=integration_fixtures.EMPTY,
                    toolchain=integration_fixtures.EMPTY,
                ),
            ],
        )
        fixture.check = fixture.task.checks[0]
        fixture.binding = Binding.model_validate(
            {
                **fixture.binding.model_dump(),
                "task": record_digest(fixture.task),
            }
        )
        fixture.store.save_project(fixture.model, 0)
        fixture.store.create_task(fixture.task)
        fixture.store.create_run(
            Run(
                id="run",
                task_id=fixture.task.id,
                binding=fixture.binding,
            ),
            fixture.model.project_id,
        )
        fixture.store.acquire("run", "lease")
        fixture.store.owner_approval(
            Approval(
                id="launch-owner",
                run_id="run",
                binding=fixture.binding,
                owner="fixture-owner",
                reason="Offline fixture only; not live authority",
            )
        )
        attempt = Attempt(
            id="worker",
            run_id="run",
            binding=fixture.binding,
            role="implementation",
            state="intent",
            provider=preparation.identity.provider,
            model=preparation.identity.model,
        )
        fixture.store.launch_intent(attempt, "lease")
        fixture.store.record_attempt(
            fixture.replace(
                attempt,
                state="acknowledged",
                handle="owned:worker",
            ),
            1,
            "lease",
        )
        configuration = prepare_dispatch_configuration(
            preparation.selection,
            preparation_digest=record_digest(preparation.expected),
            task=fixture.task,
            binding=fixture.binding,
        )
        identity = preparation.replace(
            preparation.identity,
            configuration=record_digest(configuration),
        )
        request = CodexRequest(
            attempt_id="worker",
            binding=fixture.binding,
            identity=identity,
            requirement=fixture.task.requirement,
        )
        dispatch = CodexDispatch(
            request=request,
            configuration=configuration,
            qualification=preparation.replace(
                preparation.qualified_identity,
                configuration=identity.configuration,
            ),
            qualification_record_digest=record_digest(preparation.qualification),
            task_digest=record_digest(fixture.task),
        )
        return fixture, dispatch

    def collect(self, fixture, dispatch, **changes):
        arguments = dict(
            handle="owned:worker",
            started=NOW,
            started_monotonic=0.0,
            cancelled=lambda: False,
            expected_run_version=1,
            expected_attempt_version=2,
            token="lease",
            initial=fixture.initial,
            candidate=fixture.candidate,
            frozen_target=fixture.frozen,
            allowed_paths=["README.md"],
        )
        with patch("crewshal.supervisor.time.monotonic", self.clock):
            return collect_supervised_codex(
                fixture.store,
                dispatch,
                self.process,
                self.group,
                self.stdout,
                self.stderr,
                **{**arguments, **changes},
            )

    def test_supervised_collection_links_receipt_to_scope_and_persists_private_readback(self):
        fixture, dispatch = self.integration_fixture()
        self.eof(fixture.raw, b"diagnostic")
        collection, receipt = self.collect(fixture, dispatch)
        self.assertEqual(collection.outcome.status, "completed")
        self.assertEqual(receipt.collection, record_digest(collection))
        self.assertFalse(receipt.execution_allowed)
        self.assertFalse(collection.execution_allowed)
        stored, _ = fixture.store.get("supervision", receipt.id, SupervisionReceipt)
        self.assertEqual(stored, receipt)
        scope = fixture.store.records("evidence", Evidence)[0]
        self.assertIn(record_digest(receipt), scope.artifacts)
        fixture.validate(collection)
        fixture.approve_frozen(collection)
        self.assertEqual(fixture.verdict(collection).status, "verified")
        self.assertEqual((fixture.original / "README.md").read_bytes(), b"before\n")

    def test_missing_eof_persists_interruption_without_freeze(self):
        fixture, dispatch = self.integration_fixture()
        os.write(self.out_writer, fixture.raw)
        self.close_writer(self.err_writer)
        self.clock = FixtureClock(0.5)
        collection, receipt = self.collect(fixture, dispatch)
        self.assertEqual(collection.outcome.status, "incomplete_capture")
        self.assertIsNone(collection.frozen)
        self.assertFalse(fixture.frozen.exists())
        self.assertFalse(receipt.observation.stdout_complete)
        self.assertEqual(fixture.store.get("run", "run", Run)[0].state, "interrupted")

    def test_stale_state_handle_source_and_lease_refuse_before_capture(self):
        fixture, dispatch = self.integration_fixture()
        for changes in [
            {"expected_run_version": 0},
            {"expected_attempt_version": 1},
            {"handle": "wrong-worker"},
            {"token": "wrong-lease"},
        ]:
            with (
                self.subTest(changes=changes),
                self.assertRaises(ValueError),
                patch.object(
                    self.group,
                    "sample",
                    side_effect=AssertionError("capture before validation"),
                ),
            ):
                self.collect(fixture, dispatch, **changes)
        with patch("crewshal.dispatch.SOURCE_FILES", ("model.py",)), self.assertRaises(ValueError):
            self.collect(fixture, dispatch)
        self.assertFalse(fixture.frozen.exists())
        self.assertEqual(fixture.store.records("supervision", SupervisionReceipt), [])

    def test_receipt_sql_failure_rolls_back_collection_and_no_replay_on_terminal(self):
        fixture, dispatch = self.integration_fixture()
        self.eof(fixture.raw)
        fixture.store.connection.execute(
            "CREATE TEMP TRIGGER refuse_supervision BEFORE INSERT ON records "
            "WHEN NEW.kind='supervision' BEGIN SELECT RAISE(ABORT, 'receipt failure'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.collect(fixture, dispatch)
        self.assertEqual(fixture.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(fixture.store.records("supervision", SupervisionReceipt), [])
        self.assertTrue(fixture.frozen.exists())
        with self.assertRaises(ValueError):
            self.collect(fixture, dispatch)

    def test_private_receipt_mutation_refuses_final_verdict(self):
        fixture, dispatch = self.integration_fixture()
        self.eof(fixture.raw)
        collection, receipt = self.collect(fixture, dispatch)
        fixture.validate(collection)
        fixture.approve_frozen(collection)
        (fixture.store.directory / "artifacts" / record_digest(receipt)).write_bytes(b"forged")
        with self.assertRaises(ValueError):
            fixture.verdict(collection)
        with self.assertRaises((ValueError, Conflict)):
            self.collect(fixture, dispatch)

    def test_receipt_contradictions_refuse_and_restart_preserves_private_capture(self):
        fixture, dispatch = self.integration_fixture()
        self.eof(fixture.raw)
        collection, receipt = self.collect(fixture, dispatch)
        for changes in [{"final": None}, {"stop_error": True}, {"overflow": True}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                type(receipt).model_validate({**receipt.model_dump(), **changes})
        fixture.store.close()
        fixture.store = type(fixture.store)(fixture.root / "supervised-state")
        self.assertEqual(
            fixture.store.get("supervision", receipt.id, SupervisionReceipt)[0], receipt
        )
        fixture.validate(collection)
        fixture.approve_frozen(collection)
        self.assertEqual(fixture.verdict(collection).status, "verified")


if __name__ == "__main__":
    unittest.main()
