"""Fresh original charge and FD fixtures. Kernel and launches remain synthetic."""

import ast
import copy
import fcntl
import os
from pathlib import Path
import pickle
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal import linux_early_timer as early
from crewshal import linux_setup as setup
from crewshal.durable import CoordinatorStore
from crewshal.linux_charged_build import RetainedBuildDerivation, _DERIVATIONS
from crewshal.linux_inventory import _metadata
from crewshal.linux_storage import BoundedStorageJobs
from crewshal import linux_storage as storage
from crewshal.model import digest
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DEarlyTimer(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.Phase2DSetup()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.external_observer()
        self.fixture = fixture
        self.store = CoordinatorStore(fixture.f.root / "early-timer-journal")
        self.addCleanup(self.store.close)
        self.reservation = setup.reserve_storage_installation(
            self.store,
            fixture.parent,
            fixture.observer_group,
            fixture.aggregate,
            fixture.configuration,
            batch_started_monotonic=time.monotonic() - 1,
        )
        self.groups = {}
        for lane in setup.LANE_IDS:
            self.groups[lane] = {}
            for role in setup.LANE_ROLES:
                name = role + "--" + lane
                directory = fixture.f.aggregate_path / name
                directory.mkdir()
                group = fixture.f.group(
                    directory,
                    "owned.slice/session.scope/" + name,
                    role in {"setup", "supervisor"},
                )
                directory.joinpath("cgroup.procs").write_text("")
                directory.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
                self.groups[lane][role] = group
        directory = fixture.f.aggregate_path / "broker"
        directory.mkdir()
        self.broker = fixture.f.group(directory, "owned.slice/session.scope/broker", False)
        directory.joinpath("cgroup.procs").write_text("")
        directory.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
        directory.joinpath("memory.max").write_text("67108864\n")
        directory.joinpath("pids.max").write_text("16\n")
        self.runtime_path = fixture.f.root / "synthetic-python"
        self.runtime_path.write_bytes(b"synthetic runtime bytes")
        self.runtime = early.FrozenEarlyTimerRuntime(
            interpreter=str(self.runtime_path),
            interpreter_sha256=digest(self.runtime_path.read_bytes()),
            files={str(self.runtime_path): digest(self.runtime_path.read_bytes())},
        )

    def timer(self):
        first = self.groups[setup.LANE_IDS[0]]
        timer = setup.OwnedBatchTimer(
            self.reservation,
            first["setup"],
            first["supervisor"],
            first["worker"],
            validator=first["validator"],
            early_groups=self.groups,
            early_broker=self.broker,
        )
        return timer

    def register_runtime(self, timer):
        owner = object.__new__(early.RetainedEarlyTimerRuntime)
        owner.timer, owner.plan = timer, self.runtime
        owner._payload = self.runtime.model_dump_json()
        owner.handles, owner.metadata, owner.mapped_handles = {}, {}, {}
        owner._files_snapshot = ()
        timer._early_runtime = owner
        early._RUNTIMES[timer] = owner
        self.addCleanup(early._RUNTIMES.pop, timer, None)
        return owner

    def test_original_thirteen_roles_include_broker_without_an_extra_charge(self):
        timer = self.timer()
        early.verify_early_timer_roles(timer)
        self.assertEqual(len(timer.operational_groups), 13)
        self.assertIs(timer.operational_groups[-1], self.broker)
        self.assertIs(self.reservation._batch_timer, timer)
        self.assertEqual(timer.cutoff_ns - timer.origin_ns, 570_000_000_000)
        self.assertEqual(timer.end_ns - timer.origin_ns, 600_000_000_000)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertIsNone(timer.lanes)
        self.assertEqual(self.reservation.capacity_claim.record.logical_bytes, 8589934592)

    def test_role_mapping_replacement_and_copied_owner_are_refused(self):
        timer = self.timer()
        original = timer._early_inputs
        timer._early_inputs = {name: dict(roles) for name, roles in original.items()}
        with self.assertRaisesRegex(ValueError, "role pointers"):
            early.verify_early_timer_roles(timer)
        timer._early_inputs = original
        timer._early_roles = tuple(list(timer._early_roles))
        with self.assertRaisesRegex(ValueError, "role pointers"):
            early.verify_early_timer_roles(timer)
        for transform in (copy.copy, copy.deepcopy, pickle.dumps):
            with self.assertRaises(TypeError):
                transform(timer)

    def test_broker_ceiling_change_is_refused(self):
        timer = self.timer()
        Path(self.fixture.f.aggregate_path / "broker/pids.max").write_text("32\n")
        with self.assertRaisesRegex(ValueError, "broker controls"):
            early.verify_early_timer_roles(timer)

    def test_failed_runtime_readback_retains_original_charge_owner_and_partial_fd(self):
        with (
            patch.object(
                early, "_verify_runtime_file", side_effect=ValueError("synthetic refusal")
            ),
            patch.object(
                early.subprocess, "Popen", side_effect=AssertionError("Linux launch is forbidden")
            ) as launch,
        ):
            with self.assertRaises(setup.BatchTimerRefusal) as caught:
                early.create_owned_early_batch_timer(
                    self.reservation, self.groups, self.broker, self.runtime
                )
        timer = caught.exception.lifetime
        self.assertIs(self.reservation._batch_timer, timer)
        self.assertTrue(timer.failed)
        self.assertFalse(timer.complete)
        self.assertIs(timer.reservation, self.reservation)
        owner = early._RUNTIMES[timer]
        retained = owner.handles[str(self.runtime_path)]
        self.addCleanup(os.close, retained)
        self.addCleanup(early._RUNTIMES.pop, timer, None)
        self.assertEqual(os.pread(retained, 100, 0), b"synthetic runtime bytes")
        self.assertEqual(self.reservation.capacity_claim.record.state, "retained")
        self.assertEqual(self.reservation.capacity_claim.record.installation, "unknown")
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        launch.assert_not_called()
        with self.assertRaisesRegex(ValueError, "attempt consumed"):
            early.create_owned_early_batch_timer(
                self.reservation, self.groups, self.broker, self.runtime
            )
        self.assertIs(self.reservation._batch_timer, timer)

    def test_source_digest_and_interpreter_closure_are_exact(self):
        for change in ({"source_sha256": "a" * 64}, {"files": {"/different": "b" * 64}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                early.FrozenEarlyTimerRuntime.model_validate(
                    {**self.runtime.model_dump(), **change}
                )

    def test_no_final_lane_binding_from_an_unregistered_receipt(self):
        timer = self.timer()
        self.register_runtime(timer)
        contexts = tuple(
            SimpleNamespace(_groups=tuple(self.groups[lane].values())) for lane in setup.LANE_IDS
        )
        self.reservation._lane_contexts = contexts
        with self.assertRaisesRegex(ValueError, "registered original build"):
            early.bind_early_timer_lanes(timer, contexts, self.groups)
        self.assertIsNone(timer.lanes)
        self.assertEqual(len(timer.operational_groups), 13)

    def test_final_lane_binding_uses_one_registered_receipt_and_the_same_timer(self):
        timer = self.timer()
        self.register_runtime(timer)
        derivation = object.__new__(RetainedBuildDerivation)
        derivation.reservation = self.reservation
        derivation.final_configuration = self.reservation._configuration
        self.reservation._build_derivation = derivation
        _DERIVATIONS[self.reservation] = derivation
        self.addCleanup(_DERIVATIONS.pop, self.reservation, None)
        timer.task = self.fixture.bridge.watchdog.task
        self.fixture.f.aggregate_path.joinpath("observer/cgroup.procs").write_text(
            f"{self.fixture.parent.spec.pid}\n{timer.task.spec.pid}\n"
        )
        with (
            patch.object(setup.OwnedStorageReservation, "_verify_identity", autospec=True),
            patch.object(setup.OwnedBatchTimer, "verify", autospec=True),
            patch.object(RetainedBuildDerivation, "verify", autospec=True) as readback,
        ):
            contexts = setup.reserve_lane_setups(self.reservation, self.groups)
            self.assertIs(timer.lanes, contexts)
            self.assertIs(contexts[0].timer, timer)
            self.assertEqual(len(timer.operational_groups), 13)
            self.assertEqual(timer._early_configuration, self.fixture.parent.spec.configuration)
            with self.assertRaisesRegex(ValueError, "one original final lane"):
                early.bind_early_timer_lanes(timer, contexts, self.groups)
        readback.assert_called_once_with(derivation)

    def test_effective_kernel_deadline_rejects_changed_clock_reset_and_interval(self):
        timer = self.timer()
        timer.task = SimpleNamespace(descriptor=1)
        before = timer.origin_ns + 1_000_000_000
        remaining = timer.cutoff_ns - before
        fields = {
            "clockid": "1",
            "ticks": "0",
            "settime flags": "01",
            "it_interval": "(0, 0)",
            "flags": f"{os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}",
            "it_value": f"({remaining // 1_000_000_000}, {remaining % 1_000_000_000})",
        }

        def raw(values):
            return ("\n".join(f"{name}: {value}" for name, value in values.items()) + "\n").encode()

        with (
            patch.object(early.time, "monotonic_ns", return_value=before),
            patch.object(early, "_read", return_value=raw(fields)),
        ):
            early._timerfd_deadline(timer)
        for changes in (
            {"clockid": "0"},
            {"settime flags": "00"},
            {"it_interval": "(1, 0)"},
            {"it_value": "(571, 0)"},
            {"ticks": "1"},
        ):
            with (
                self.subTest(changes=changes),
                patch.object(early.time, "monotonic_ns", return_value=before),
                patch.object(early, "_read", return_value=raw({**fields, **changes})),
                self.assertRaises(ValueError),
            ):
                early._timerfd_deadline(timer)

    def bound_lanes_for_readback(self):
        timer = self.timer()
        self.register_runtime(timer)
        derivation = object.__new__(RetainedBuildDerivation)
        derivation.reservation = self.reservation
        derivation.final_configuration = self.reservation._configuration
        self.reservation._build_derivation = derivation
        _DERIVATIONS[self.reservation] = derivation
        self.addCleanup(_DERIVATIONS.pop, self.reservation, None)
        timer.task = self.fixture.bridge.watchdog.task
        self.fixture.f.aggregate_path.joinpath("observer/cgroup.procs").write_text(
            f"{self.fixture.parent.spec.pid}\n{timer.task.spec.pid}\n"
        )
        with (
            patch.object(setup.OwnedStorageReservation, "_verify_identity", autospec=True),
            patch.object(setup.OwnedBatchTimer, "verify", autospec=True),
            patch.object(RetainedBuildDerivation, "verify", autospec=True),
        ):
            contexts = setup.reserve_lane_setups(self.reservation, self.groups)
        return timer, contexts

    def test_bound_timer_roles_do_not_reenter_the_reservation_derivation(self):
        timer, contexts = self.bound_lanes_for_readback()
        with patch.object(
            setup.OwnedStorageReservation,
            "_verify_identity",
            autospec=True,
            side_effect=RecursionError("reservation derivation reenters the timer"),
        ) as verify:
            early.verify_early_timer_roles(timer)
            verify.assert_not_called()
            with self.assertRaisesRegex(RecursionError, "reenters"):
                contexts[0].verify_handles()
            verify.assert_called_once_with(self.reservation)

    def test_bound_timer_roles_still_refuse_registry_and_payload_control_changes(self):
        timer, contexts = self.bound_lanes_for_readback()
        original = self.reservation._lane_contexts
        self.reservation._lane_contexts = tuple(list(original))
        with self.assertRaisesRegex(ValueError, "lane contexts changed"):
            early.verify_early_timer_roles(timer)
        self.reservation._lane_contexts = original
        directory = self.fixture.f.aggregate_path / "worker--live"
        directory.joinpath("memory.events").write_text("max 1\noom 0\noom_kill 0\n")
        with self.assertRaisesRegex(ValueError, "refusal history"):
            early.verify_early_timer_roles(timer)
        for context in contexts:
            for group in context._groups:
                os.fstat(group.descriptor)

    def test_storage_jobs_use_only_original_early_setup_before_final_lane_binding(self):
        timer = self.timer()
        timer.task = self.fixture.bridge.watchdog.task
        self.fixture.f.aggregate_path.joinpath("observer/cgroup.procs").write_text(
            f"{self.fixture.parent.spec.pid}\n{timer.task.spec.pid}\n"
        )
        original_deadline = self.reservation.batch_started + 120
        jobs = BoundedStorageJobs(
            self.reservation.observer,
            self.reservation.observer_group,
            self.reservation.aggregate,
            original_deadline,
            execution_group=timer.setup,
            batch_timer=timer,
        )
        with (
            patch.object(setup.OwnedBatchTimer, "verify", autospec=True),
            patch.object(storage.sys, "platform", "linux"),
            patch.object(storage.os, "pidfd_open", create=True),
        ):
            jobs._admit()
            self.assertEqual(jobs.deadline, original_deadline)
            self.assertIs(jobs.execution_group, timer._early_roles[0])
            self.assertFalse(hasattr(self.reservation, "_lane_contexts"))
            replacement = copy.copy(timer.setup)
            replaced = BoundedStorageJobs(
                self.reservation.observer,
                self.reservation.observer_group,
                self.reservation.aggregate,
                original_deadline,
                execution_group=replacement,
                batch_timer=timer,
            )
            with self.assertRaisesRegex(ValueError, "timer/observer/setup binding"):
                replaced._admit()

    def test_runtime_fd_readback_requires_readonly_mount_and_exact_bytes(self):
        handle = os.open(self.runtime_path, os.O_RDONLY)
        self.addCleanup(os.close, handle)
        original = os.fstat(handle)
        metadata = {
            name: getattr(original, name)
            for name in (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_uid",
                "st_gid",
                "st_nlink",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
        }
        metadata.update(st_uid=0, st_gid=0)
        protected = SimpleNamespace(**metadata)
        cutoff = time.monotonic_ns() + 1_000_000_000
        with (
            patch.object(early.os, "fstat", return_value=protected),
            patch.object(early.os, "fstatvfs", return_value=SimpleNamespace(f_flag=os.ST_RDONLY)),
        ):
            early._verify_runtime_file(handle, self.runtime.interpreter_sha256, cutoff)
            with self.assertRaisesRegex(ValueError, "bytes changed"):
                early._verify_runtime_file(handle, "f" * 64, cutoff)
        with (
            patch.object(early.os, "fstat", return_value=protected),
            patch.object(early.os, "fstatvfs", return_value=SimpleNamespace(f_flag=0)),
            self.assertRaisesRegex(ValueError, "readonly"),
        ):
            early._verify_runtime_file(handle, self.runtime.interpreter_sha256, cutoff)
        self.assertEqual(_metadata(os.fstat(handle)), _metadata(original))

    def test_empty_pinned_module_requires_exact_bytes_mount_and_deadline(self):
        empty = self.fixture.f.root / "empty-module.py"
        empty.write_bytes(b"")
        handle = os.open(empty, os.O_RDONLY)
        self.addCleanup(os.close, handle)
        info = os.fstat(handle)
        protected = SimpleNamespace(
            **{
                name: getattr(info, name)
                for name in (
                    "st_dev",
                    "st_ino",
                    "st_mode",
                    "st_uid",
                    "st_gid",
                    "st_nlink",
                    "st_size",
                    "st_mtime_ns",
                    "st_ctime_ns",
                )
            }
        )
        protected.st_uid = protected.st_gid = 0
        cutoff = time.monotonic_ns() + 1_000_000_000
        with (
            patch.object(early.os, "fstat", return_value=protected),
            patch.object(early.os, "fstatvfs", return_value=SimpleNamespace(f_flag=os.ST_RDONLY)),
        ):
            early._verify_runtime_file(handle, digest(b""), cutoff)
            with self.assertRaisesRegex(ValueError, "bytes changed"):
                early._verify_runtime_file(handle, digest(b"other"), cutoff)
            with self.assertRaisesRegex(ValueError, "deadline exhausted"):
                early._verify_runtime_file(handle, digest(b""), time.monotonic_ns() - 1)
        with (
            patch.object(early.os, "fstat", return_value=protected),
            patch.object(early.os, "fstatvfs", return_value=SimpleNamespace(f_flag=0)),
            self.assertRaisesRegex(ValueError, "readonly"),
        ):
            early._verify_runtime_file(handle, digest(b""), cutoff)

    def test_fixed_source_prepares_deadline_and_trace_before_waiting(self):
        source = early.EARLY_TIMER_SOURCE.decode()
        tree = ast.parse(source)
        self.assertIsInstance(tree, ast.Module)
        self.assertLess(source.index("timerfd_settime(123, 1"), source.index("libc.ptrace(0"))
        self.assertLess(
            source.index("libc.ptrace(0"), source.index("os.kill(os.getpid(), signal.SIGTRAP)")
        )
        self.assertIn("stop(112)", source)
        self.assertEqual(source.count("timerfd_create("), 1)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("exec", source.replace("inheritable=False", "").replace("O_CLOEXEC", ""))

    def test_actual_fd_inventory_and_mapped_inode_refuse_replacements(self):
        timer = self.timer()
        owner = self.register_runtime(timer)
        task_path = self.fixture.bridge.watchdog_path
        timer.task = SimpleNamespace(descriptor=self.fixture.bridge.watchdog.task.descriptor)
        for name in task_path.joinpath("fd").iterdir():
            name.unlink()
        for number in ("0", "1", "2"):
            task_path.joinpath("fd", number).symlink_to("/dev/null")
        for number, group in enumerate(timer._early_roles, early.GROUP_START):
            path = self.fixture.f.aggregate_path / group.identity.relative_path.rsplit("/", 1)[-1]
            task_path.joinpath("fd", str(number)).symlink_to(path)
            task_path.joinpath("fdinfo", str(number)).write_text("flags: 00\n")
        reading, timer.lifeline = os.pipe()
        self.addCleanup(os.close, reading)
        self.addCleanup(os.close, timer.lifeline)
        pipe = os.fstat(timer.lifeline)
        timer.lifeline_identity = (pipe.st_dev, pipe.st_ino)
        task_path.joinpath("fd", str(early.LIFELINE_FD)).symlink_to(f"pipe:[{pipe.st_ino}]")
        task_path.joinpath("fdinfo", str(early.LIFELINE_FD)).write_text("flags: 00\n")
        task_path.joinpath("fd", str(early.TIMER_FD)).symlink_to("anon_inode:[timerfd]")
        source_path = self.fixture.f.root / "fixed-source-fixture"
        source_path.write_bytes(early.EARLY_TIMER_SOURCE)
        timer._early_source = os.open(source_path, os.O_RDONLY)
        self.addCleanup(os.close, timer._early_source)
        task_path.joinpath("fd", str(early.SOURCE_FD)).symlink_to(source_path)
        source_flags = task_path.joinpath("fdinfo", str(early.SOURCE_FD))
        source_flags.write_text(f"flags: {os.O_CLOEXEC:o}\n")
        original_fd = os.open(self.runtime_path, os.O_RDONLY)
        self.addCleanup(os.close, original_fd)
        info = os.fstat(original_fd)
        owner.handles[str(self.runtime_path)] = original_fd
        owner.metadata[str(self.runtime_path)] = _metadata(info)
        map_files = task_path / "map_files"
        map_files.mkdir(exist_ok=True)
        mapping = "1000-2000"
        map_files.joinpath(mapping).symlink_to(self.runtime_path)
        task_path.joinpath("maps").write_text(
            f"{mapping} r-xp 00000000 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino} {self.runtime_path}\n"
        )
        device_pair = (os.major(info.st_dev), os.minor(info.st_dev))
        null_device = Path("/dev/null").stat().st_rdev
        real_fcntl = fcntl.fcntl

        def synthetic_seals(fd, command, *args):
            if command == 444:
                return 15
            return real_fcntl(fd, command, *args)

        with (
            patch.object(
                early.os,
                "makedev",
                side_effect=lambda major, minor: info.st_dev
                if (major, minor) == device_pair
                else null_device,
            ),
            patch.object(early.RetainedEarlyTimerRuntime, "verify", autospec=True),
            patch.object(early, "_seals", return_value=(443, 444, 15)),
            patch.object(early.fcntl, "fcntl", side_effect=synthetic_seals),
            patch.object(early, "_verify_runtime_file", autospec=True),
            patch.object(early, "_timerfd_deadline", autospec=True),
        ):
            early.verify_early_timer_readback(timer)
            retained = owner.mapped_handles[str(self.runtime_path)][0]
            self.addCleanup(os.close, retained)
            self.assertEqual(os.fstat(retained).st_ino, info.st_ino)
            extra = task_path.joinpath("fd/999")
            extra.symlink_to("/dev/null")
            with self.assertRaisesRegex(ValueError, "descriptor inventory"):
                early.verify_early_timer_readback(timer)
            extra.unlink()
            group_link = task_path.joinpath("fd", str(early.GROUP_START))
            original_path = os.readlink(group_link)
            group_link.unlink()
            group_link.symlink_to(self.fixture.f.aggregate_path)
            with self.assertRaisesRegex(ValueError, "original group FD"):
                early.verify_early_timer_readback(timer)
            group_link.unlink()
            group_link.symlink_to(original_path)
            source_flags.write_text(f"flags: {os.O_CLOEXEC | os.O_RDWR:o}\n")
            with self.assertRaisesRegex(ValueError, "source, timer, or lifeline"):
                early.verify_early_timer_readback(timer)
            source_flags.write_text(f"flags: {os.O_CLOEXEC:o}\n")
            task_path.joinpath("maps").write_text(
                f"{mapping} r-xp 00000000 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino + 1} {self.runtime_path}\n"
            )
            with self.assertRaisesRegex(ValueError, "mapped image"):
                early.verify_early_timer_readback(timer)


if __name__ == "__main__":
    unittest.main()
