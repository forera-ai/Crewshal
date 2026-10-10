"""Fresh retained FD/clock/role fixtures; kernel, helper and launch are synthetic."""

from contextlib import contextmanager
import copy
import fcntl
import os
from pathlib import Path
import pickle
import time
from types import SimpleNamespace
import struct
import unittest
from unittest.mock import patch

from crewshal import linux_setup as setup
from crewshal.contracts import record_digest
from crewshal.linux_parent import TrustedTaskSpec
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DBatchTimer(unittest.TestCase):
    def setUp(self, *, installation=False, outer_observer=False, validator=False):
        f = fixtures.Phase2DSetup()
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.f = f
        f.external_observer()
        if outer_observer:
            f.parent.spec = TrustedTaskSpec.model_validate(
                {**f.parent.spec.model_dump(), "placement": "outer_observer", "cwd": "/"}
            )
            f.bridge.parent_path.joinpath("cwd").unlink()
            f.bridge.parent_path.joinpath("cwd").symlink_to("/")
        origin = time.monotonic() - 1
        if installation:
            from crewshal.durable import CoordinatorStore

            store = CoordinatorStore(f.f.root / "installation-journal")
            self.addCleanup(store.close)
            self.reservation = setup.reserve_storage_installation(
                store,
                f.parent,
                f.observer_group,
                f.aggregate,
                f.configuration,
                batch_started_monotonic=origin,
            )
        else:
            capacity = fixtures.synthetic_capacity_claim(
                self, f.f.root, f.parent, f.configuration, origin
            )
            self.reservation = setup.OwnedStorageReservation(
                f.parent,
                f.observer_group,
                f.aggregate,
                f.configuration,
                batch_started_monotonic=origin,
                capacity_claim=capacity,
            )
        self.validator = None
        if validator:
            self.validator_path = f.f.aggregate_path / "validator"
            self.validator_path.mkdir()
            self.validator = f.f.group(
                self.validator_path, "owned.slice/session.scope/validator", False
            )
            self.validator_path.joinpath("cgroup.procs").write_text("")
            self.validator_path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
        self.timer = setup.OwnedBatchTimer(
            self.reservation, f.setup_group, f.supervisor, f.worker, validator=self.validator
        )
        self.path = f.bridge.watchdog_path
        self.task = f.bridge.watchdog.task
        self.task.spec = TrustedTaskSpec.model_validate(
            {
                **self.task.spec.model_dump(),
                "cgroup": f.observer_group.identity,
                "namespaces": f.parent.spec.namespaces,
                "capabilities": f.parent.spec.capabilities,
                "cwd": "/",
                "placement": "outer_observer",
                "argv": [
                    "/bin/crewshal-bootstrap",
                    "--batch-timer-fds",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                ],
            }
        )
        self.path.joinpath("cwd").unlink()
        self.path.joinpath("cwd").symlink_to("/")
        status = self.path.joinpath("status").read_text()
        for name in ("CapPrm", "CapEff", "CapBnd"):
            status = status.replace(f"{name}: {'0' * 16}", f"{name}: {f.parent.spec.capabilities}")
        self.path.joinpath("status").write_text(status)
        self.path.joinpath("cgroup").write_text(f"0::/{f.observer_group.identity.relative_path}\n")
        self.path.joinpath("cmdline").write_bytes(
            b"\0".join(x.encode() for x in self.task.spec.argv) + b"\0"
        )
        self.reader, self.timer.lifeline = os.pipe()
        self.addCleanup(os.close, self.reader)
        self.addCleanup(os.close, self.timer.lifeline)
        info = os.fstat(self.timer.lifeline)
        self.timer.lifeline_identity = (info.st_dev, info.st_ino)
        self.timer.helper = os.open(self.path / "exe", os.O_RDONLY)
        self.addCleanup(os.close, self.timer.helper)
        helper_info = os.fstat(self.timer.helper)
        self.timer._helper_identity = (self.timer.helper, helper_info.st_dev, helper_info.st_ino)
        for entry in self.path.joinpath("fd").iterdir():
            entry.unlink()
        for number in ("0", "1", "2"):
            self.path.joinpath("fd", number).symlink_to("/dev/null")
        for number, group in zip(
            ("3", "4", "5"), (f.f.worker_path, f.supervisor_path, f.setup_path), strict=True
        ):
            self.path.joinpath("fd", number).symlink_to(group)
            self.path.joinpath("fdinfo", number).write_text("flags: 00\n")
        self.path.joinpath("fd", "6").symlink_to(f"pipe:[{info.st_ino}]")
        self.path.joinpath("fdinfo", "6").write_text("flags: 00\n")
        self.path.joinpath("fd", "9").symlink_to("anon_inode:[timerfd]")
        self.timer.task = self.task
        self.timer.process = SimpleNamespace(pid=self.task.spec.pid, poll=lambda: None)
        self.timer._birth = (self.task, self.timer.process)
        self.timer._task_digest = record_digest(self.task.spec)
        self.timer.complete = True
        self.f.f.aggregate_path.joinpath("observer", "cgroup.procs").write_text(
            f"{os.getpid()}\n{self.task.spec.pid}\n"
        )
        self.changed = {}
        self.timer_number = "9"
        if validator:
            self.task.spec = TrustedTaskSpec.model_validate(
                {
                    **self.task.spec.model_dump(),
                    "argv": [
                        "/bin/crewshal-bootstrap",
                        "--batch-timer-validator-fds",
                        "10",
                        "11",
                        "12",
                        "13",
                        "14",
                        "15",
                        "16",
                    ],
                }
            )
            self.path.joinpath("cmdline").write_bytes(
                b"\0".join(x.encode() for x in self.task.spec.argv) + b"\0"
            )
            self.timer._task_digest = record_digest(self.task.spec)
            self.path.joinpath("fd", "6").unlink()
            self.path.joinpath("fd", "6").symlink_to(self.validator_path)
            self.path.joinpath("fd", "7").symlink_to(f"pipe:[{info.st_ino}]")
            self.path.joinpath("fdinfo", "7").write_text("flags: 00\n")
            self.path.joinpath("fd", "9").unlink()
            self.path.joinpath("fd", "10").symlink_to("anon_inode:[timerfd]")
            self.timer_number = "10"

    @contextmanager
    def effective_readback(self):
        original_read = setup._read

        def read(descriptor, name, limit=65536):
            if (
                os.fstat(descriptor).st_ino == self.path.stat().st_ino
                and name == "fdinfo/" + self.timer_number
            ):
                # Kernel timer readback is explicitly synthetic. Real retained
                # files, pipes, proc metadata and group ancestry are read by source.
                remaining = self.timer.cutoff_ns - time.monotonic_ns()
                values = {
                    "flags": f"{os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}",
                    "clockid": "1",
                    "ticks": "0",
                    "settime flags": "01",
                    "it_value": f"({remaining // 1_000_000_000}, {remaining % 1_000_000_000})",
                    "it_interval": "(0, 0)",
                }
                values.update(self.changed)
                return ("\n".join(f"{k}: {v}" for k, v in values.items()) + "\n").encode()
            return original_read(descriptor, name, limit)

        with patch.object(setup, "_read", side_effect=read):
            yield

    def test_original_timer_allows_operational_readback_without_new_allowance(self):
        with self.effective_readback():
            self.reservation.verify_operational()
        self.assertEqual(self.timer.cutoff_ns - self.timer.origin_ns, 570_000_000_000)
        self.assertEqual(self.timer.end_ns - self.timer.origin_ns, 600_000_000_000)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertFalse(self.timer.operational_ready)
        self.assertFalse(self.timer.resources_reusable)
        self.assertEqual(self.f.setup_path.joinpath("cgroup.kill").read_bytes(), b"")
        self.assertEqual(self.f.observer_group._read("pids.max"), "32")

    def test_original_timer_retains_separate_validator_under_original_ceiling(self):
        self.setUp(validator=True)
        with self.effective_readback():
            self.reservation.verify_operational()
        self.assertEqual(len(self.timer.operational_groups), 4)
        self.assertIs(self.timer.operational_groups[-1], self.validator)
        self.assertEqual(self.validator.sample().controls["memory.max"], "134217728")
        self.assertEqual(self.validator.sample().controls["pids.max"], "32")
        self.assertEqual(self.timer.cutoff_ns - self.timer.origin_ns, 570_000_000_000)
        self.assertEqual(self.timer.end_ns - self.timer.origin_ns, 600_000_000_000)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertEqual(self.validator_path.joinpath("cgroup.kill").read_bytes(), b"")

    def test_validator_timer_refuses_aggregate_ceiling_events_and_role_rebinding(self):
        self.setUp(validator=True)
        changes = (
            ("memory.max", "805306368\n"),
            ("pids.max", "128\n"),
            ("memory.events", "max 1\noom 0\noom_kill 0\n"),
            ("pids.events", "max 1\n"),
        )
        for name, value in changes:
            with self.subTest(name=name):
                path = self.validator_path / name
                original = path.read_bytes()
                path.write_text(value)
                with self.effective_readback(), self.assertRaises(ValueError):
                    self.timer.verify()
                path.write_bytes(original)
        self.timer.validator = self.f.worker
        with self.effective_readback(), self.assertRaises(ValueError):
            self.timer.verify()
        self.timer.validator = self.validator
        os.fstat(self.validator.descriptor)

    def test_validator_timer_requires_actual_distinct_validator_and_lifeline_fds(self):
        self.setUp(validator=True)
        link = self.path / "fd/6"
        link.unlink()
        link.symlink_to(self.f.f.worker_path)
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "group handle"):
            self.timer.verify()
        link.unlink()
        link.symlink_to(self.validator_path)
        self.path.joinpath("fdinfo/7").write_text(f"flags: {os.O_WRONLY:o}\n")
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "lifeline"):
            self.timer.verify()
        os.fstat(self.timer.lifeline)

    @contextmanager
    def idle_readback(self):
        root = self.f.f.root / "idle-proc"
        (root / "self/fd").mkdir(parents=True, exist_ok=True)
        (root / "self/fdinfo").mkdir(exist_ok=True)
        link = root / "self/fd" / str(self.task.pidfd)
        if not link.exists() and not link.is_symlink():
            link.symlink_to("anon_inode:[pidfd]")
        (root / "self/fdinfo" / str(self.task.pidfd)).write_text("Pid: -1\n")
        self.timer.process.poll = lambda: 0
        self.f.f.aggregate_path.joinpath("observer/cgroup.procs").write_text(f"{os.getpid()}\n")
        for group in (self.f.setup_path, self.f.supervisor_path, self.f.f.worker_path):
            group.joinpath("cgroup.procs").write_text("")
            group.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
        # Original retained proc/pidfd metadata remains real ordinary files;
        # Linux pidfd termination/reap/clock are explicitly synthetic here.
        original_select = setup.select.select

        def exited(readers, writers, errors, timeout):
            if readers == [self.task.pidfd]:
                return ([self.task.pidfd], [], [])
            return original_select(readers, writers, errors, timeout)

        with (
            patch.object(setup, "_proc_root", side_effect=lambda _: os.open(root, os.O_RDONLY)),
            patch.object(setup.select, "select", side_effect=exited),
            patch.object(setup.time, "monotonic_ns", return_value=self.timer.end_ns + 1),
            patch.object(
                setup.time, "monotonic", return_value=self.reservation.batch_started + 601
            ),
        ):
            yield root

    def test_idle_after_original_batch_retains_full_charge_and_denies_creation(self):
        with self.idle_readback():
            self.reservation.verify_idle_retention()
            with self.assertRaises(ValueError):
                self.reservation.verify()
            with self.assertRaises(ValueError):
                self.reservation.verify_operational()
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertFalse(self.timer.resources_reusable)
        self.assertFalse(self.timer.operational_ready)
        for group in (self.f.setup_path, self.f.supervisor_path, self.f.f.worker_path):
            self.assertEqual(group.joinpath("cgroup.kill").read_bytes(), b"")
        os.fstat(self.timer.lifeline)

    def test_idle_refuses_exit_code_without_original_pidfd_exit_and_reap(self):
        with self.idle_readback() as root:
            path = root / "self/fdinfo" / str(self.task.pidfd)
            path.write_text(f"Pid: {self.task.spec.pid}\n")
            with self.assertRaisesRegex(ValueError, "exit/reap"):
                self.reservation.verify_idle_retention()
            path.write_text("Pid: -1\n")
            self.timer.process.poll = lambda: None
            with self.assertRaisesRegex(ValueError, "exit/reap"):
                self.reservation.verify_idle_retention()
            self.timer.process.poll = lambda: 0
            with patch.object(setup.select, "select", return_value=([], [], [])):
                with self.assertRaisesRegex(ValueError, "exit/reap"):
                    self.reservation.verify_idle_retention()

    def test_idle_refuses_operational_population_unknown_job_or_extra_observer_child(self):
        with self.idle_readback():
            for group in (self.f.setup_path, self.f.supervisor_path, self.f.f.worker_path):
                with self.subTest(group=group.name):
                    group.joinpath("cgroup.events").write_text("populated 1\nfrozen 0\n")
                    with self.assertRaises(ValueError):
                        self.reservation.verify_idle_retention()
                    group.joinpath("cgroup.events").write_text("populated 0\nfrozen 0\n")
            from crewshal.linux_storage import BoundedStorageJobs, LinuxPhysicalOwner

            jobs = BoundedStorageJobs(
                self.reservation.observer,
                self.reservation.observer_group,
                self.reservation.aggregate,
                deadline=self.reservation.batch_started + 600,
                execution_group=self.timer.setup,
                batch_timer=self.timer,
            )
            jobs.pending = (9, self.task.pidfd)
            # Explicit inert constructor seam, no namespace/storage effects.
            owner = object.__new__(LinuxPhysicalOwner)
            owner.reservation = self.reservation
            owner.jobs = owner._jobs = jobs
            owner.retention_readback_jobs = owner._retention_jobs = None
            self.reservation._storage_owner = owner
            with self.assertRaisesRegex(ValueError, "operational job"):
                self.reservation.verify_idle_retention()
            jobs.pending = None
            self.reservation.verify_idle_retention()
            jobs._creation_child = (9, self.task.pidfd, self.task.descriptor, 1, 1, 1)
            with self.assertRaisesRegex(ValueError, "operational job"):
                self.reservation.verify_idle_retention()
            jobs._creation_child = None
            self.f.f.aggregate_path.joinpath("observer/cgroup.procs").write_text(
                f"{os.getpid()}\n9999\n"
            )
            with self.assertRaisesRegex(ValueError, "only the original"):
                self.reservation.verify_idle_retention()

    def test_idle_refuses_rebound_helper_and_changed_original_controls(self):
        with self.idle_readback():
            original = self.timer.process
            self.timer.process = copy.copy(original)
            with self.assertRaises(ValueError):
                self.reservation.verify_idle_retention()
            self.timer.process = original
            self.f.f.aggregate_path.joinpath("memory.max").write_text("max\n")
            with self.assertRaises(ValueError):
                self.reservation.verify_idle_retention()

    def test_idle_retains_handles_when_lifeline_or_helper_fd_custody_changes(self):
        with self.idle_readback():
            original = self.timer.helper
            substitute = os.open(self.f.f.root / "parent-image", os.O_RDONLY)
            try:
                self.timer.helper = substitute
                with self.assertRaisesRegex(ValueError, "descriptor custody"):
                    self.reservation.verify_idle_retention()
            finally:
                self.timer.helper = original
                os.close(substitute)
            self.timer.lifeline_identity = (0, 0)
            with self.assertRaisesRegex(ValueError, "descriptor custody"):
                self.reservation.verify_idle_retention()
            os.fstat(original)
            os.fstat(self.timer.lifeline)

    def test_origin_cutoff_and_reserve_cannot_be_renewed(self):
        for name in ("origin_ns", "cutoff_ns", "end_ns"):
            original = getattr(self.timer, name)
            setattr(self.timer, name, original + 1)
            with self.subTest(name=name), self.effective_readback(), self.assertRaises(ValueError):
                self.timer.verify()
            setattr(self.timer, name, original)

    def test_changed_clock_relative_repeating_or_spent_timer_refuses(self):
        for name, value in (
            ("clockid", "0"),
            ("settime flags", "00"),
            ("ticks", "1"),
            ("it_interval", "(1, 0)"),
            ("it_value", "(600, 0)"),
            ("it_value", "(0, 0)"),
            ("it_value", "(1, 1000000000)"),
        ):
            self.changed = {name: value}
            with (
                self.subTest(name=name, value=value),
                self.effective_readback(),
                self.assertRaises(ValueError),
            ):
                self.reservation.verify_operational()

    def test_operational_cutoff_refuses_new_work_before_cleanup_reserve(self):
        with (
            patch.object(setup.time, "monotonic_ns", return_value=self.timer.cutoff_ns),
            self.assertRaises(ValueError),
        ):
            self.timer.verify()
        self.assertEqual(self.reservation.charges.logical_bytes, 8589934592)

    def test_original_observer_handle_cannot_replace_operational_group(self):
        self.path.joinpath("fd/5").unlink()
        self.path.joinpath("fd/5").symlink_to(self.f.f.aggregate_path / "observer")
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "group handle"):
            self.timer.verify()

    def test_unknown_extra_fd_or_task_never_authorizes_more_creation(self):
        self.path.joinpath("fd/8").symlink_to(self.f.f.root / "parent-image")
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "inventory"):
            self.timer.verify()
        self.path.joinpath("fd/8").unlink()
        self.f.f.aggregate_path.joinpath("observer", "cgroup.procs").write_text(
            f"{os.getpid()}\n{self.task.spec.pid}\n9999\n"
        )
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "sole retained"):
            self.reservation.verify_operational()

    def test_lifeline_and_process_rebinding_refuse_with_handles_retained(self):
        original_process = self.timer.process
        self.timer.process = copy.copy(original_process)
        with self.effective_readback(), self.assertRaises(ValueError):
            self.timer.verify()
        self.timer.process = original_process
        self.path.joinpath("fd/6").unlink()
        self.path.joinpath("fd/6").symlink_to("pipe:[1]")
        with self.effective_readback(), self.assertRaisesRegex(ValueError, "handles"):
            self.timer.verify()
        os.fstat(self.timer.lifeline)

    def test_failed_or_reconstructed_timer_keeps_full_charges_and_blocks_retry(self):
        self.timer.failed = True
        with self.effective_readback(), self.assertRaises(ValueError):
            self.reservation.verify_operational()
        with self.assertRaisesRegex(ValueError, "one-shot"):
            setup.OwnedBatchTimer(
                self.reservation, self.f.setup_group, self.f.supervisor, self.f.worker
            )
        for operation in (copy.copy, copy.deepcopy, pickle.dumps):
            with self.subTest(operation=operation.__name__), self.assertRaises(TypeError):
                operation(self.timer)
        self.assertEqual(self.reservation.charges.allocated_bytes, 8589934592)

    def test_missing_timer_blocks_operational_creation(self):
        del self.reservation._batch_timer
        with self.assertRaisesRegex(ValueError, "independent batch timer"):
            self.reservation.verify_operational()

    def test_observer_as_stopped_role_refuses_before_launch_or_timer_creation(self):
        del self.reservation._batch_timer
        self.f.f.aggregate_path.joinpath("observer", "cgroup.procs").write_text(str(os.getpid()))
        with (
            patch.object(setup.subprocess, "Popen") as launch,
            self.assertRaisesRegex(ValueError, "outside stopped roles"),
        ):
            setup.create_owned_batch_timer(
                self.reservation,
                self.f.setup_group,
                self.f.supervisor,
                self.f.observer_group,
                self.f.preparation,
                -1,
            )
        launch.assert_not_called()
        self.assertFalse(hasattr(self.reservation, "_batch_timer"))

    def create_from_fresh_transport(self, *, malformed=False):
        """Actual files/pipes with explicit syscall/launch/privilege seams only."""
        del self.reservation._batch_timer
        self.f.f.aggregate_path.joinpath("observer", "cgroup.procs").write_text(str(os.getpid()))
        for path in (self.f.setup_path, self.f.supervisor_path, self.f.f.worker_path):
            path.joinpath("cgroup.procs").write_text("")
            path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0")
        helper = os.open(self.path.joinpath("exe"), os.O_RDONLY)
        self.addCleanup(os.close, helper)
        helper_inode = os.fstat(helper).st_ino
        original_fstat, original_fcntl = os.fstat, fcntl.fcntl
        capsule_file = self.f.f.root / "fresh-original-origin"

        def memfd(name, flags):
            # Ordinary file substitutes for Linux sealed memfd; seals below are
            # explicitly synthetic, never an installed capability observation.
            return os.open(capsule_file, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)

        def metadata(fd):
            actual = original_fstat(fd)
            if actual.st_ino == helper_inode:
                values = {k: getattr(actual, k) for k in dir(actual) if k.startswith("st_")}
                return SimpleNamespace(**{**values, "st_uid": 0})
            return actual

        def seals(fd, operation, argument=0):
            if operation == 999991:
                return 0
            if operation == 999992:
                return 15
            return original_fcntl(fd, operation, argument)

        def pipe2(flags):
            reader, writer = os.pipe()
            if flags & os.O_NONBLOCK:
                os.set_blocking(reader, False)
                os.set_blocking(writer, False)
            return reader, writer

        def launch(argv, **options):
            self.assertEqual(argv[:2], ["/bin/crewshal-bootstrap", "--batch-timer-fds"])
            self.assertNotIn("preexec_fn", options)
            self.assertEqual(options["env"], {})
            self.assertEqual(options["cwd"], "/")
            self.assertEqual(options["stdin"], -3)
            self.assertTrue(options["close_fds"])
            inputs = tuple(map(int, argv[2:]))
            self.assertEqual(
                inputs[:3],
                (
                    self.f.worker.descriptor,
                    self.f.supervisor.descriptor,
                    self.f.setup_group.descriptor,
                ),
            )
            self.assertEqual(
                set(options["pass_fds"]), {*inputs, self.reservation._batch_timer.helper}
            )
            origin = struct.unpack("=Q", os.pread(inputs[5], 8, 0))[0]
            self.assertEqual(origin, int(self.reservation.batch_started * 1_000_000_000))
            acknowledgement = f"BATCH {origin + int(malformed)} {origin + 570_000_000_000} {origin + 600_000_000_000}\n".encode()
            os.write(inputs[4], acknowledgement)
            self.path.joinpath("cmdline").write_bytes(b"\0".join(x.encode() for x in argv) + b"\0")
            inode = os.fstat(self.reservation._batch_timer.lifeline).st_ino
            self.path.joinpath("fd/6").unlink()
            self.path.joinpath("fd/6").symlink_to(f"pipe:[{inode}]")
            self.f.f.aggregate_path.joinpath("observer", "cgroup.procs").write_text(
                f"{os.getpid()}\n{self.task.spec.pid}\n"
            )
            return SimpleNamespace(pid=self.task.spec.pid, poll=lambda: None)

        def attach(root, pid):
            self.assertEqual(pid, self.task.spec.pid)
            return os.dup(self.task.descriptor), os.dup(self.task.pidfd)

        with (
            patch.object(setup.os, "fstat", side_effect=metadata),
            patch.object(setup, "_seals", return_value=(999991, 999992, 15)),
            patch.object(setup.os, "memfd_create", side_effect=memfd, create=True),
            patch.object(setup.os, "MFD_CLOEXEC", 1, create=True),
            patch.object(setup.os, "MFD_ALLOW_SEALING", 2, create=True),
            patch.object(setup.fcntl, "fcntl", side_effect=seals),
            patch.object(setup.os, "pipe2", side_effect=pipe2, create=True),
            patch.object(setup.subprocess, "Popen", side_effect=launch),
            patch.object(
                setup, "_proc_root", side_effect=lambda boot: os.dup(self.task.descriptor)
            ),
            patch.object(setup, "_attach", side_effect=attach),
            self.effective_readback(),
        ):
            try:
                return setup.create_owned_batch_timer(
                    self.reservation,
                    self.f.setup_group,
                    self.f.supervisor,
                    self.f.worker,
                    self.f.preparation,
                    helper,
                )
            finally:
                lifetime = getattr(self.reservation, "_batch_timer", None)
                if lifetime is not None:
                    if lifetime.task is not None:
                        self.addCleanup(lifetime.task.close)
                    for descriptor in (lifetime.helper, lifetime.lifeline):
                        if descriptor >= 0:
                            self.addCleanup(os.close, descriptor)

    def test_fresh_capture_binds_original_origin_and_actual_retained_child(self):
        lifetime = self.create_from_fresh_transport()
        self.assertIs(self.reservation._batch_timer, lifetime)
        self.assertIs(lifetime._birth[0], lifetime.task)
        self.assertIs(lifetime._birth[1], lifetime.process)
        self.assertTrue(lifetime.complete)
        self.assertFalse(lifetime.failed)
        self.assertFalse(lifetime.operational_ready)

    def test_bad_readiness_keeps_partial_handles_and_consumes_attempt(self):
        with self.assertRaises(setup.BatchTimerRefusal) as caught:
            self.create_from_fresh_transport(malformed=True)
        lifetime = caught.exception.lifetime
        self.assertIs(self.reservation._batch_timer, lifetime)
        self.assertTrue(lifetime.failed)
        self.assertIsNotNone(lifetime.task)
        os.fstat(lifetime.helper)
        os.fstat(lifetime.lifeline)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            setup.OwnedBatchTimer(
                self.reservation, self.f.setup_group, self.f.supervisor, self.f.worker
            )
        self.assertEqual(self.reservation.charges, setup.StorageCharges())

    def test_helper_source_stops_worker_before_other_roles_and_has_no_owner_stop(self):
        # Structural preparation only; this does not compile/execute the helper.
        source = Path("src/crewshal/bootstrap_helper.c").read_text()
        fragment = source[
            source.index("static int batch_timer(int validator)") : source.index(
                "static int watchdog(void)"
            )
        ]
        stopped = fragment.index("if (!empty_group(3) ||")
        self.assertLess(fragment.index("stop_group(3)"), stopped)
        self.assertLess(fragment.index("stop_group(6)"), stopped)
        self.assertLess(stopped, fragment.index("stop_group(4)"))
        self.assertLess(fragment.index("stop_group(4)"), fragment.index("stop_group(5)"))
        self.assertIn("validator && !empty_group(6) && stop_group(6)", fragment)
        self.assertNotIn("stop_group(7)", fragment)
        self.assertNotIn("now + 1000000000ULL", fragment)
        self.assertIn("origin + 570000000000ULL", fragment)
        self.assertIn("origin + 600000000000ULL", fragment)
        self.assertIn("TFD_TIMER_ABSTIME", fragment)


if __name__ == "__main__":
    unittest.main()
