"""Fresh parent bridge fixtures; every Linux/Popen/migration/timer effect is synthetic."""

from dataclasses import replace
from contextlib import contextmanager
import os
from pathlib import Path
import signal
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal.admission import NamespaceIdentity, RetainedProc
from crewshal.contracts import record_digest
from crewshal import linux_parent as bridge
from crewshal.model import digest
from tests.acceptance import test_phase_2d_bootstrap as bootstrap_fixtures


class Phase2DParent(unittest.TestCase):
    def setUp(self):
        owned = bootstrap_fixtures.Phase2DBootstrap()
        owned.setUp()
        self.addCleanup(owned.doCleanups)
        self.owned = owned
        self.f = owned.fixture
        self.supervisor_path = self.f.aggregate_path / "supervisor"
        self.supervisor_path.mkdir()
        self.supervisor = self.f.group(
            self.supervisor_path, "owned.slice/session.scope/supervisor", True
        )
        self.proc_root = self.f.root / "linux-proc"
        self.proc_root.mkdir()
        self.f.proc_path = self.f.proc_path.rename(self.proc_root / str(self.f.child.pid))
        self.namespaces = dict(self.f.spec.namespaces)
        clock = self.f.root / "namespace-time"
        clock.write_bytes(b"synthetic monotonic namespace")
        info = clock.stat()
        self.namespaces["time"] = NamespaceIdentity(device=info.st_dev, inode=info.st_ino)
        self.parent_path, self.parent = self.task(os.getpid(), parent=True)
        self.watchdog_path, task = self.task(54321, parent=False)
        for number in ("0", "1", "2"):
            (self.watchdog_path / "fd" / number).symlink_to("/dev/null")
        (self.watchdog_path / "fd" / "3").symlink_to(self.f.worker_path / "cgroup.kill")
        (self.watchdog_path / "fd" / "4").symlink_to(
            f"pipe:[{self.owned.deadline.lifeline_identity[1]}]"
        )
        (self.watchdog_path / "fd" / "6").symlink_to("anon_inode:[timerfd]")
        self.write(self.watchdog_path, "fdinfo/3", f"flags: {os.O_WRONLY | os.O_NONBLOCK:o}\n")
        self.write(self.watchdog_path, "fdinfo/4", "flags: 00\n")
        kill = os.open(self.f.worker_path / "cgroup.kill", os.O_WRONLY | os.O_NONBLOCK)
        self.addCleanup(os.close, kill)
        self.watchdog = bridge.ObservedWatchdog(task, self.owned.deadline, kill)
        self.outer = {
            name: NamespaceIdentity(device=identity.device, inode=identity.inode + 1)
            for name, identity in self.namespaces.items()
        }
        self.supervisor_path.joinpath("cgroup.procs").write_text(f"{os.getpid()}\n54321\n")
        self.f.worker_path.joinpath("cgroup.procs").write_text("")
        self.f.worker_path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0")
        for directory in ("self/fdinfo", "sys/kernel/random"):
            self.proc_root.joinpath(directory).mkdir(parents=True)
        root_info = self.proc_root.stat()
        device = f"{os.major(root_info.st_dev)}:{os.minor(root_info.st_dev)}"
        self.proc_root.joinpath("self/mountinfo").write_text(
            f"1 0 {device} / /proc rw - proc proc rw\n"
        )
        self.proc_root.joinpath("sys/kernel/random/boot_id").write_text(self.f.spec.boot_id)
        self.events = []
        self.spawned = False
        original_read = bridge._read

        def kernel_read(descriptor, name, limit=65536):
            if (
                os.fstat(descriptor).st_ino == self.watchdog_path.stat().st_ino
                and name == "fdinfo/6"
            ):
                remaining = self.watchdog.deadline.expires_ns - bridge.time.monotonic_ns()
                return (
                    f"flags: {os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}\nclockid: 1\nticks: 0\nsettime flags: 01\n"
                    f"it_value: ({remaining // 1_000_000_000}, {remaining % 1_000_000_000})\n"
                    "it_interval: (0, 0)\n"
                ).encode()
            return original_read(descriptor, name, limit)

        self.kernel_read = kernel_read
        self.start_patch(patch.object(bridge, "_read", side_effect=kernel_read))
        # Linux null device identity differs from macOS. This substitutes only
        # the synthetic kernel's dev_t comparison, not its character-file check.
        self.start_patch(
            patch.object(bridge.os, "makedev", return_value=Path("/dev/null").stat().st_rdev)
        )

    def start_patch(self, context):
        value = context.start()
        self.addCleanup(context.stop)
        return value

    def write(self, path, name, value):
        path.joinpath(name).write_bytes(value.encode() if isinstance(value, str) else value)

    def test_trusted_task_cwd_is_exact_readback_not_a_fixed_legacy_assumption(self):
        self.parent_path.joinpath("cwd").unlink()
        self.parent_path.joinpath("cwd").symlink_to("/candidate/owned")
        with self.assertRaises(ValueError):
            self.parent.verify(self.supervisor.identity)
        self.parent.spec = bridge.TrustedTaskSpec.model_validate(
            {
                **self.parent.spec.model_dump(),
                "cwd": "/candidate/owned",
            }
        )
        self.parent.verify(self.supervisor.identity)

    def test_trusted_task_cwd_cannot_admit_auth_or_arbitrary_root(self):
        for cwd in ("/native-auth", "/", "/scratch", "/proc"):
            with self.subTest(cwd=cwd), self.assertRaises(ValueError):
                bridge.TrustedTaskSpec.model_validate({**self.parent.spec.model_dump(), "cwd": cwd})

    def task(self, pid, parent):
        path = self.f.root / ("trusted-parent" if parent else "trusted-watchdog")
        path.mkdir()
        for name in ("fd", "fdinfo", "ns"):
            path.joinpath(name).mkdir()
        for name in self.namespaces:
            target = self.f.root / f"namespace-{name}"
            path.joinpath("ns", name).symlink_to(target)
        image = self.f.root / ("parent-image" if parent else "watchdog-image")
        raw = b"synthetic parent program" if parent else b"synthetic owned helper bytes"
        image.write_bytes(raw)
        image.chmod(0o555)
        path.joinpath("exe").symlink_to(image)
        path.joinpath("cwd").symlink_to("/scratch/checkout")
        caps = (
            f"{(1 << 6) | (1 << 7) | (1 << 8) | (1 << 19) | (1 << 21):016x}" if parent else "0" * 16
        )
        spec = bridge.TrustedTaskSpec(
            configuration=record_digest(self.f.configuration),
            pid=pid,
            parent_pid=1 if parent else os.getpid(),
            start_ticks=123456,
            boot_id=self.f.spec.boot_id,
            cgroup=self.supervisor.identity,
            namespaces=self.namespaces,
            executable=digest(raw),
            capabilities=caps,
            argv=["/usr/bin/python3", "trusted-parent"]
            if parent
            else ["/bin/crewshal-bootstrap", "--watchdog"],
            environment={},
        )
        self.write(
            path, "stat", f"{pid} (trusted helper) S {spec.parent_pid} " + "0 " * 17 + "123456\n"
        )
        self.write(
            path,
            "status",
            "\n".join(
                f"{k}: {v}"
                for k, v in {
                    "Pid": str(pid),
                    "Tgid": str(pid),
                    "PPid": str(spec.parent_pid),
                    "TracerPid": "0",
                    "Threads": "1",
                    "NoNewPrivs": "1",
                    "Uid": "0 0 0 0",
                    "Gid": "0 0 0 0",
                    "Groups": "",
                    "CapInh": "0" * 16,
                    "CapAmb": "0" * 16,
                    "CapPrm": caps,
                    "CapEff": caps,
                    "CapBnd": caps,
                }.items()
            )
            + "\n",
        )
        self.write(path, "cgroup", f"0::/{spec.cgroup.relative_path}\n")
        self.write(path, "cmdline", b"\0".join(x.encode() for x in spec.argv) + b"\0")
        self.write(path, "environ", b"")
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            task = bridge.RetainedTrustedTask(descriptor, self.f.pid_reader.fileno(), spec)
        finally:
            os.close(descriptor)
        self.addCleanup(task.close)
        return path, task

    def migrate(self, group):
        bridge._move_self_original(group)
        self.events.append(("migration", group.identity.relative_path))
        self.write(self.parent_path, "cgroup", f"0::/{group.identity.relative_path}\n")
        inside = group is self.f.worker
        pids = ([os.getpid()] if inside else []) + ([self.f.child.pid] if self.spawned else [])
        self.f.worker_path.joinpath("cgroup.procs").write_text("\n".join(str(x) for x in pids))
        self.f.worker_path.joinpath("cgroup.events").write_text(
            f"populated {int(bool(pids))}\nfrozen 0"
        )
        self.supervisor_path.joinpath("cgroup.procs").write_text(
            "54321\n" if inside else f"{os.getpid()}\n54321\n"
        )

    def popen(self, child, argv, **options):
        self.events.append(("Popen", argv))
        self.assertEqual(self.f.worker.sample().direct_pids, [os.getpid()])
        self.parent.verify(self.f.worker.identity)
        self.assertEqual(options["env"], self.f.configuration.native_environment)
        self.assertTrue(options["close_fds"])
        self.assertNotIn("preexec_fn", options)
        self.assertNotIn("pass_fds", options)
        self.assertEqual(options["cwd"], "/scratch/checkout")
        self.assertEqual(argv[0], "/bin/setpriv")
        self.assertNotIn("/usr/bin/bwrap", argv)
        self.assertEqual(argv[argv.index("--") + 1 :], self.owned.preparation.helper_argv)
        self.spawned = True
        self.f.worker_path.joinpath("cgroup.procs").write_text(f"{os.getpid()}\n12345")

    @contextmanager
    def kernel_proc(self, pidfd_identity=None):
        original_open = os.open

        def proc_open(path, *args, **kwargs):
            return original_open(self.proc_root if path == "/proc" else path, *args, **kwargs)

        def pidfd_open(pid, flags):
            handle = os.dup(self.f.pid_reader.fileno())
            self.proc_root.joinpath("self/fdinfo", str(handle)).write_text(
                f"Pid: {pid if pidfd_identity is None else pidfd_identity}\n"
            )
            return handle

        with (
            patch.object(bridge.sys, "platform", "linux"),
            patch.object(bridge.os, "pidfd_open", side_effect=pidfd_open, create=True),
            patch.object(bridge.os, "open", side_effect=proc_open),
        ):
            yield

    def stage(self, **changes):
        arguments = dict(
            parent=self.parent,
            outer_namespaces=self.outer,
            watchdog=self.watchdog,
            worker=self.f.worker,
            supervisor=self.supervisor,
            aggregate=self.f.aggregate,
            configuration=self.f.configuration,
            preparation=self.owned.preparation,
            driver=self.owned.driver,
            native_executable=digest(b"synthetic native bytes"),
            cancelled=lambda: False,
        )
        arguments.update(changes)

        original_check = self.watchdog.check

        def readiness(*args):
            self.events.append(("readiness", None))
            original_check(*args)

        fixture = self

        class PopenType(type):
            def __call__(cls, *args, **kwargs):
                fixture.popen(fixture.f.child, *args, **kwargs)
                return fixture.f.child

            def __instancecheck__(cls, value):
                return isinstance(value, subprocess.Popen)

        class Popen(metaclass=PopenType):
            pass

        with (
            patch.object(bridge, "_move_self_original", bridge._move_self, create=True),
            patch.object(bridge, "_move_self", side_effect=self.migrate),
            self.kernel_proc(),
            patch.object(bridge, "subprocess", SimpleNamespace(Popen=Popen, PIPE=subprocess.PIPE)),
            patch.object(bridge.ObservedWatchdog, "check", side_effect=readiness),
        ):
            return bridge.stage_namespace_parent(**arguments)

    def test_namespace_parent_orders_effective_readiness_migration_and_direct_popen(self):
        admitted = self.stage()
        admitted.proc.verify_stopped()
        self.addCleanup(admitted.proc.close)
        self.assertIs(admitted.child, self.f.child)
        kinds = [kind for kind, _ in self.events]
        self.assertLess(kinds.index("readiness"), kinds.index("migration"))
        self.assertLess(kinds.index("migration"), kinds.index("Popen"))
        self.assertEqual(
            [value for kind, value in self.events if kind == "migration"],
            [self.f.worker.identity.relative_path, self.supervisor.identity.relative_path],
        )
        self.assertEqual(admitted.receipt.started_monotonic, self.owned.deadline.started_monotonic)
        self.assertEqual(admitted.receipt.spec.start_ticks, self.f.spec.start_ticks)
        self.assertFalse(admitted.receipt.execution_allowed)
        self.assertEqual(self.f.worker.sample().direct_pids, [12345])
        self.parent.verify(self.supervisor.identity)

    def test_readiness_text_without_effective_timer_never_migrates_or_starts(self):
        with patch.object(
            bridge,
            "_read",
            side_effect=lambda fd, name, limit=65536: b"clockid: 0\nit_value: (4, 0)\n"
            if name == "fdinfo/6"
            else self.kernel_read(fd, name, limit),
        ):
            with self.assertRaises(ValueError):
                self.stage()
        self.assertFalse(self.spawned)
        self.assertFalse(any(k == "migration" for k, _ in self.events))

    def test_watchdog_clock_ticks_interval_flags_and_reset_expiry_refuse(self):
        mutations = [
            (b"clockid: 1", b"clockid: 0"),
            (b"ticks: 0", b"ticks: 1"),
            (b"it_interval: (0, 0)", b"it_interval: (1, 0)"),
            (b"settime flags: 01", b"settime flags: 00"),
            (f"flags: {os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}".encode(), b"flags: 02"),
        ]
        for old, new in mutations:
            with (
                self.subTest(new=new),
                patch.object(
                    bridge,
                    "_read",
                    side_effect=lambda fd, name, limit=65536: self.kernel_read(
                        fd, name, limit
                    ).replace(old, new),
                ),
                self.assertRaises(ValueError),
            ):
                self.watchdog.check(self.f.worker, self.f.configuration)
        with (
            patch.object(
                bridge,
                "_read",
                side_effect=lambda fd,
                name,
                limit=65536: f"flags: {os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}\nclockid: 1\nticks: 0\nsettime flags: 01\nit_value: (5, 0)\nit_interval: (0, 0)\n".encode()
                if name == "fdinfo/6"
                else self.kernel_read(fd, name, limit),
            ),
            self.assertRaises(ValueError),
        ):
            self.watchdog.check(self.f.worker, self.f.configuration)

    def test_wrong_kill_object_never_starts_and_unrelated_bytes_stay_intact(self):
        foreign = self.f.root / "foreign-kill"
        foreign.write_bytes(b"original unrelated control")
        self.watchdog_path.joinpath("fd/3").unlink()
        self.watchdog_path.joinpath("fd/3").symlink_to(foreign)
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.spawned)
        self.assertEqual(foreign.read_bytes(), b"original unrelated control")

    def test_watchdog_extra_fd_wrong_direction_or_lifeline_refuses(self):
        path = self.watchdog_path / "fd" / "7"
        path.symlink_to("socket:[123]")
        with self.assertRaises(ValueError):
            self.watchdog.check(self.f.worker, self.f.configuration)
        path.unlink()
        self.write(self.watchdog_path, "fdinfo/4", "flags: 01\n")
        with self.assertRaises(ValueError):
            self.watchdog.check(self.f.worker, self.f.configuration)
        self.write(self.watchdog_path, "fdinfo/4", "flags: 00\n")
        self.watchdog_path.joinpath("fd/4").unlink()
        self.watchdog_path.joinpath("fd/4").symlink_to("pipe:[1]")
        with self.assertRaises(ValueError):
            self.watchdog.check(self.f.worker, self.f.configuration)

    def test_host_namespace_wrapper_parent_extra_worker_or_supervisor_pid_refuses(self):
        with self.assertRaises(ValueError):
            self.stage(outer_namespaces=self.namespaces)
        self.f.worker_path.joinpath("cgroup.procs").write_text("12345")
        with self.assertRaises(ValueError):
            self.stage()
        self.f.worker_path.joinpath("cgroup.procs").write_text("")
        self.supervisor_path.joinpath("cgroup.procs").write_text(f"{os.getpid()}\n54321\n98765")
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.spawned)

    def test_trusted_parent_role_threads_tracer_identity_and_image_mutation_refuse(self):
        status = self.parent_path.joinpath("status").read_bytes()
        for old, new in [
            (b"Threads: 1", b"Threads: 2"),
            (b"TracerPid: 0", b"TracerPid: 1"),
            (b"Uid: 0 0 0 0", b"Uid: 65534 65534 65534 65534"),
        ]:
            self.write(self.parent_path, "status", status.replace(old, new))
            with self.subTest(new=new), self.assertRaises(ValueError):
                self.stage()
        self.write(self.parent_path, "status", status)
        image = self.f.root / "parent-image"
        image.chmod(0o644)
        image.write_bytes(b"changed trusted program")
        image.chmod(0o555)
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.spawned)

    def test_cancellation_after_spawn_returns_parent_then_recovers_once_and_retains_watchdog(self):
        with self.assertRaises(bridge.ParentBridgeRefusal) as caught:
            self.stage(cancelled=lambda: self.spawned)
        refusal = caught.exception
        self.assertIs(refusal.child, self.f.child)
        self.assertIs(refusal.watchdog, self.watchdog)
        self.assertFalse(refusal.resources_reusable)
        self.assertTrue(refusal.recovery.worker_empty)
        self.assertTrue(refusal.recovery.child_reaped)
        self.parent.verify(self.supervisor.identity)
        self.assertEqual(self.owned.watchdog.poll(), None)

    def test_handoff_refusal_uses_one_recovery_and_retains_proc(self):
        self.owned.driver.events[1] = (int(signal.SIGTRAP) << 8) | 0x7F
        original = bridge._recover
        with (
            patch("crewshal.linux_bootstrap._recover", wraps=original) as recovery,
            self.assertRaises(bridge.ParentBridgeRefusal) as caught,
        ):
            self.stage()
        self.assertEqual(recovery.call_count, 1)
        self.assertIsNotNone(caught.exception.proc)
        self.addCleanup(caught.exception.proc.close)
        self.assertTrue(caught.exception.recovery.worker_empty)

    def test_handoff_interruption_never_restarts_the_recovery_grace(self):
        with (
            patch.object(self.owned.driver, "options", side_effect=KeyboardInterrupt),
            patch("crewshal.linux_bootstrap._recover", wraps=bridge._recover) as recovery,
            self.assertRaises(bridge.ParentBridgeRefusal) as caught,
        ):
            self.stage()
        self.assertEqual(recovery.call_count, 1)
        self.assertIsNone(caught.exception.recovery)
        self.assertFalse(caught.exception.resources_reusable)
        self.addCleanup(caught.exception.proc.close)

    def test_unchanged_native_attach_still_refuses_initial_traced_helper(self):
        with self.kernel_proc():
            attached = bridge.attach_traced_child(self.f.child, self.f.spec)
            self.addCleanup(attached.close)
            bridge._traced(attached, self.f.child)
            with self.assertRaises(ValueError):
                RetainedProc.attach(self.f.spec)
            with self.assertRaises(ValueError):
                attached.verify_stopped()

    def test_initial_attach_requires_direct_parent_start_state_and_pidfd_identity(self):
        with self.kernel_proc(pidfd_identity=99999), self.assertRaises(ValueError):
            bridge.attach_traced_child(self.f.child, self.f.spec)
        with self.kernel_proc():
            for update in ({"parent_pid": 99999}, {"start_ticks": 99999}):
                wrong = self.f.spec.model_copy(update=update)
                with self.assertRaises(ValueError):
                    bridge.attach_traced_child(self.f.child, wrong)
            self.owned.write_stat("T")
            with self.assertRaises(ValueError):
                bridge.attach_traced_child(self.f.child, self.f.spec)

    def test_initial_attach_rejects_fake_proc_mount_and_changed_boot(self):
        self.proc_root.joinpath("self/mountinfo").write_text(
            "1 0 0:0 / /proc rw - tmpfs tmpfs rw\n"
        )
        with self.kernel_proc(), self.assertRaises(ValueError):
            bridge.attach_traced_child(self.f.child, self.f.spec)
        info = self.proc_root.stat()
        self.proc_root.joinpath("self/mountinfo").write_text(
            f"1 0 {os.major(info.st_dev)}:{os.minor(info.st_dev)} / /proc rw - proc proc rw\n"
        )
        self.proc_root.joinpath("sys/kernel/random/boot_id").write_text("different-boot")
        with self.kernel_proc(), self.assertRaises(ValueError):
            bridge.attach_traced_child(self.f.child, self.f.spec)

    def test_supervisor_control_or_resource_refusal_history_never_starts(self):
        for name, value in (("memory.max", "max"), ("memory.events", "max 1\noom 0\noom_kill 0")):
            path = self.supervisor_path / name
            original = path.read_bytes()
            path.write_text(value)
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.stage()
            path.write_bytes(original)
        self.assertFalse(self.spawned)

    def test_time_namespace_mismatch_and_exited_watchdog_refuse_before_migration(self):
        original = self.watchdog.task.spec.namespaces["time"]
        self.watchdog.task.spec.namespaces["time"] = self.outer["time"]
        with self.assertRaises(ValueError):
            self.stage()
        self.watchdog.task.spec.namespaces["time"] = original
        self.owned.watchdog.result = 125
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.spawned)
        self.assertFalse(any(kind == "migration" for kind, _ in self.events))

    def test_spawn_failure_restores_parent_recovers_with_no_child_and_forbids_retry(self):
        with (
            patch.object(self, "popen", side_effect=OSError("synthetic helper exec refusal")),
            self.assertRaises(bridge.ParentBridgeRefusal) as caught,
        ):
            self.stage()
        self.assertIsNone(caught.exception.child)
        self.assertTrue(caught.exception.recovery.worker_empty)
        self.assertTrue(caught.exception.recovery.child_reaped)
        self.assertIs(caught.exception.worker, self.f.worker)
        self.parent.verify(self.supervisor.identity)
        with self.assertRaisesRegex(ValueError, "already consumed"):
            self.stage()

    def test_failed_return_migration_retains_unknown_recovery_and_does_not_stop_parent(self):
        migrate = self.migrate

        def fail_return(group):
            if group is self.supervisor:
                raise OSError("synthetic return migration denied")
            migrate(group)

        with (
            patch.object(self, "migrate", side_effect=fail_return),
            patch.object(self.f.worker, "stop") as stop,
            self.assertRaises(bridge.ParentBridgeRefusal) as caught,
        ):
            self.stage()
        self.assertIsNone(caught.exception.recovery)
        self.assertFalse(caught.exception.resources_reusable)
        self.assertIs(caught.exception.child, self.f.child)
        stop.assert_not_called()
        self.parent.verify(self.f.worker.identity)
        self.assertTrue(self.watchdog.task._bridge_claimed)

    def test_extra_child_fd_refuses_before_detach_and_does_not_weaken_admission(self):
        self.owned.driver.extra_fd = True
        with self.assertRaises(bridge.ParentBridgeRefusal) as caught:
            self.stage()
        self.addCleanup(caught.exception.proc.close)
        self.assertFalse(any(name == "detach" for name, _ in self.owned.driver.calls))
        self.assertTrue(caught.exception.recovery.worker_empty)

    def test_watchdog_readiness_descriptor_must_be_closed_at_armed_checkpoint(self):
        self.watchdog_path.joinpath("fd/5").symlink_to("pipe:[123]")
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.spawned)

    def test_missing_policy_binding_refuses_before_any_migration(self):
        configuration = self.f.configuration.model_copy(deep=True)
        configuration.linux_envelope.bootstrap_policy_sha256 = "0" * 64
        from crewshal.linux_bootstrap import prepare_linux_bootstrap

        preparation = prepare_linux_bootstrap(configuration, helper_binary=self.owned.binary)
        with self.assertRaisesRegex(ValueError, "exact helper/policy/native"):
            self.stage(configuration=configuration, preparation=preparation)
        self.assertFalse(self.events)

    def test_trusted_task_owns_snapshot_and_unknown_fields_or_bad_digest_refuse(self):
        spec = self.parent.spec.model_copy(deep=True)
        retained = bridge.RetainedTrustedTask(self.parent.descriptor, self.parent.pidfd, spec)
        self.addCleanup(retained.close)
        spec.argv.append("changed")
        retained.verify(self.supervisor.identity)
        with self.assertRaises(ValueError):
            bridge.TrustedTaskSpec.model_validate({**spec.model_dump(), "unknown_authority": True})
        with self.assertRaises(ValueError):
            self.stage(native_executable="not-a-digest")

    def test_move_self_writes_only_zero_to_pinned_group(self):
        bridge._move_self(self.f.worker)
        self.assertEqual(self.f.worker_path.joinpath("cgroup.procs").read_bytes(), b"0")
        self.assertEqual(self.owned.outside.read_bytes(), b"original unrelated bytes")

    def test_false_authority_and_snapshot_isolation(self):
        self.assertFalse(self.parent.spec.execution_allowed)
        self.assertFalse(self.parent.spec.spend_authorized)
        self.assertFalse(self.parent.spec.profile_qualified)
        self.assertFalse(self.owned.preparation.bootstrap_implemented)
        with self.assertRaises(ValueError):
            bridge.TrustedTaskSpec.model_validate(
                {**self.parent.spec.model_dump(), "execution_allowed": True}
            )
        replacement = replace(
            self.watchdog,
            deadline=replace(self.owned.deadline, origin_ns=self.owned.deadline.origin_ns + 1),
        )
        with self.assertRaises(ValueError):
            replacement.check(self.f.worker, self.f.configuration)
