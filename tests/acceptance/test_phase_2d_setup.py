"""Fresh setup/lifetime fixtures; constructors and Linux effects are synthetic."""

from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal import linux_setup as setup
from crewshal.linux_parent import TrustedTaskSpec
from crewshal.supervisor import OwnedCgroup
from tests.acceptance import test_phase_2d_parent as parent_fixtures


class Phase2DSetup(unittest.TestCase):
    def setUp(self):
        fixture = parent_fixtures.Phase2DParent()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.bridge = fixture
        self.f = fixture.f
        self.parent = fixture.parent
        self.supervisor = fixture.supervisor
        self.worker = self.f.worker
        self.aggregate = self.f.aggregate
        self.preparation = fixture.owned.preparation
        self.configuration = self.f.configuration
        path = self.f.aggregate_path / "setup"
        path.mkdir()
        self.setup_group = self.f.group(path, "owned.slice/session.scope/setup", True)
        self.setup_path = path
        self.setup_path.joinpath("cgroup.procs").write_text("")
        self.setup_path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0")
        self.supervisor_path = fixture.supervisor_path
        self.supervisor_path.joinpath("cgroup.procs").write_text(str(os.getpid()))
        self.plan = setup.prepare_namespace_setup(
            self.configuration, self.preparation, self.parent.spec.argv, self.parent.spec.executable
        )
        self.controls = setup.InheritedControls(
            configuration=self.configuration,
            bootstrap=self.preparation,
            setup=self.plan,
            boot_id=self.parent.spec.boot_id,
            outer_namespaces=fixture.outer,
            groups={name: group.identity for name, group in self.groups.items()},
        )
        self.calls = []
        self.pipe_peers = {}

    @property
    def groups(self):
        return {
            "aggregate": self.aggregate,
            "setup": self.setup_group,
            "supervisor": self.supervisor,
            "worker": self.worker,
        }

    def cleanup_watchdog(self, lifetime):
        if lifetime.task is not None:
            lifetime.task.close()
        for name in ("lifeline", "kill"):
            handle = getattr(lifetime, name)
            if handle >= 0:
                os.close(handle)
                setattr(lifetime, name, -1)

    @contextmanager
    def synthetic_popen(self, callback):
        test = self

        class Constructor(type):
            def __call__(cls, argv, **options):
                test.calls.append((argv, options))
                return callback(argv, options)

            def __instancecheck__(cls, value):
                return isinstance(value, subprocess.Popen)

        class Popen(metaclass=Constructor):
            pass

        with patch.object(
            setup, "subprocess", SimpleNamespace(Popen=Popen, DEVNULL=subprocess.DEVNULL)
        ):
            yield

    def pipe2(self, flags):
        reader, writer = os.pipe()
        self.pipe_peers[reader] = writer
        if flags & os.O_NONBLOCK:
            os.set_blocking(reader, False)
            os.set_blocking(writer, False)
        return reader, writer

    def watchdog(self, acknowledgement=None, callback=None):
        bridge = self.bridge
        bridge.watchdog_path = bridge.watchdog_path.rename(bridge.proc_root / "54321")

        def construct(argv, options):
            numbers = [int(x) for x in argv[-3:]]
            self.assertEqual(set(options["pass_fds"]), set(numbers))
            self.assertNotIn("preexec_fn", options)
            self.assertEqual(options["env"], {})
            self.assertTrue(options["close_fds"])
            self.assertEqual(options["stdin"], subprocess.DEVNULL)
            self.assertEqual(argv[:2], ["/bin/setpriv", "--reuid=0"])
            self.assertIn("--bounding-set=-all", argv)
            self.assertEqual(argv[-4], "--watchdog-fds")
            origin = time.monotonic_ns()
            raw = (
                acknowledgement
                if acknowledgement is not None
                else f"READY {origin} {origin + 5_000_000_000}\n".encode()
            )
            os.write(numbers[2], raw)
            info = os.fstat(self.pipe_peers[numbers[1]])
            bridge.watchdog_path.joinpath("fd/4").unlink()
            bridge.watchdog_path.joinpath("fd/4").symlink_to(f"pipe:[{info.st_ino}]")
            self.supervisor_path.joinpath("cgroup.procs").write_text(f"{os.getpid()}\n54321")
            if callback:
                callback()
            return bridge.owned.watchdog

        original_read = parent_fixtures.bridge._read

        def timer_read(descriptor, name, limit=65536):
            if (
                os.fstat(descriptor).st_ino == bridge.watchdog_path.stat().st_ino
                and name == "fdinfo/6"
            ):
                # Read the original creation acknowledgement; independent effective
                # readback still occurs through the real ObservedWatchdog checks.
                raw = acknowledgement if acknowledgement is not None else self.acknowledgement
                expiry = int(raw.split()[2])
                remaining = expiry - time.monotonic_ns()
                return (
                    f"flags: {os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC:o}\nclockid: 1\nticks: 0\nsettime flags: 01\n"
                    f"it_value: ({remaining // 1_000_000_000}, {remaining % 1_000_000_000})\nit_interval: (0, 0)\n"
                ).encode()
            return original_read(descriptor, name, limit)

        # macOS pipe endpoints have distinct inode values; the synthetic Linux
        # proc link uses the retained writer identity, as actual Linux requires.
        original_write = os.write

        def recording_write(fd, raw):
            if raw.startswith(b"READY "):
                self.acknowledgement = raw
            return original_write(fd, raw)

        with (
            bridge.kernel_proc(),
            self.synthetic_popen(construct),
            patch.object(setup.os, "pipe2", side_effect=self.pipe2, create=True),
            patch.object(setup.os, "write", side_effect=recording_write),
            patch.object(parent_fixtures.bridge, "_read", side_effect=timer_read),
        ):
            try:
                lifetime = setup.create_owned_watchdog(
                    self.parent,
                    self.worker,
                    self.supervisor,
                    self.aggregate,
                    self.configuration,
                    self.preparation,
                )
            except setup.WatchdogSetupRefusal as error:
                self.addCleanup(self.cleanup_watchdog, error.lifetime)
                raise
        # Give the synthetic watchdog an independent pidfd event channel;
        # the underlying parent fixture intentionally shares one for readback.
        reader, writer = os.pipe()
        self.addCleanup(os.close, reader)
        self.addCleanup(os.close, writer)
        os.close(lifetime.task.pidfd)
        lifetime.task.pidfd = os.dup(reader)
        self.watch_exit_write = writer
        bridge.watchdog = lifetime.observed
        self.addCleanup(self.cleanup_watchdog, lifetime)
        return lifetime

    def test_passive_namespace_plan_retains_original_limits_and_no_authority(self):
        self.assertFalse(self.plan.execution_allowed)
        self.assertFalse(self.plan.profile_qualified)
        self.assertEqual(
            self.plan.control_fds,
            {"sealed_configuration": 3, "aggregate": 4, "setup": 5, "supervisor": 6, "worker": 7},
        )
        self.assertEqual(self.plan.setup_controls["memory.max"], "805306368")
        self.assertEqual(self.plan.setup_controls["pids.max"], "128")
        self.assertIn("--unshare-net", self.plan.namespace_argv)
        self.assertNotIn("--preserve-fds", self.plan.namespace_argv)
        self.assertIn("CAP_SYS_PTRACE", self.plan.namespace_argv)
        self.assertIn("CAP_SYS_ADMIN", self.plan.namespace_argv)
        command = self.plan.namespace_argv
        self.assertLess(command.index("--dev"), command.index("/dev/shm"))
        self.assertEqual(command[-len(self.parent.spec.argv) :], self.parent.spec.argv)
        self.assertIn("/usr/bin/env", command)
        self.assertIn(
            "mediated_network_policy_in_fresh_namespace_before_worker", self.plan.unresolved
        )

    def test_worker_program_cannot_be_parent_program(self):
        for argv in ([], ["relative"], ["/opt/codex/bin/codex"], ["/bin/crewshal-bootstrap"]):
            with self.subTest(argv=argv), self.assertRaises(ValueError):
                setup.prepare_namespace_setup(self.configuration, self.preparation, argv, "1" * 64)

    def test_watchdog_creation_observes_owned_fds_before_worker(self):
        lifetime = self.watchdog()
        self.assertIsNotNone(lifetime.observed)
        lifetime.observed.check(self.worker, self.configuration)
        self.assertFalse(self.worker.sample().populated)
        self.assertFalse(lifetime.resources_reusable)
        self.assertIs(lifetime.process, self.bridge.owned.watchdog)

    def test_second_watchdog_creation_refused_before_constructor(self):
        self.watchdog()
        with self.assertRaisesRegex(ValueError, "one-shot"):
            setup.create_owned_watchdog(
                self.parent,
                self.worker,
                self.supervisor,
                self.aggregate,
                self.configuration,
                self.preparation,
            )
        self.assertEqual(len(self.calls), 1)

    def test_malformed_readiness_retains_created_handles_and_forbids_retry(self):
        with self.assertRaises(setup.WatchdogSetupRefusal) as caught:
            self.watchdog(b"READY false\n")
        lifetime = caught.exception.lifetime
        self.assertIsNotNone(lifetime.process)
        self.assertIsNotNone(lifetime.task)
        os.fstat(lifetime.kill)
        os.fstat(lifetime.lifeline)
        self.assertTrue(self.parent._watchdog_started)
        self.assertFalse(caught.exception.resources_reusable)

    def test_readiness_overflow_retains_handles(self):
        with self.assertRaisesRegex(setup.WatchdogSetupRefusal, "exceeds"):
            self.watchdog(b"X" * 81)

    def test_effective_timer_required_even_with_valid_readiness(self):
        def change():
            self.bridge.watchdog_path.joinpath("fd/6").unlink()
            self.bridge.watchdog_path.joinpath("fd/6").symlink_to("socket:[1]")

        with self.assertRaisesRegex(setup.WatchdogSetupRefusal, "timer descriptor"):
            self.watchdog(callback=change)

    def test_extra_watchdog_fd_refused(self):
        def change():
            self.bridge.watchdog_path.joinpath("fd/9").symlink_to("/dev/null")

        with self.assertRaisesRegex(setup.WatchdogSetupRefusal, "inventory"):
            self.watchdog(callback=change)

    def test_wrong_watchdog_parent_refused(self):
        def change():
            raw = self.bridge.watchdog_path.joinpath("stat").read_text()
            self.bridge.watchdog_path.joinpath("stat").write_text(
                raw.replace(f" S {os.getpid()} ", " S 999 ")
            )

        with self.assertRaises(setup.WatchdogSetupRefusal):
            self.watchdog(callback=change)

    def test_watchdog_role_change_refused(self):
        def change():
            raw = self.bridge.watchdog_path.joinpath("status").read_text()
            self.bridge.watchdog_path.joinpath("status").write_text(
                raw.replace("Threads: 1", "Threads: 2")
            )

        with self.assertRaises(setup.WatchdogSetupRefusal):
            self.watchdog(callback=change)

    def test_nonempty_worker_refused_before_watchdog_constructor(self):
        self.f.worker_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
        with self.assertRaises(ValueError):
            setup.create_owned_watchdog(
                self.parent,
                self.worker,
                self.supervisor,
                self.aggregate,
                self.configuration,
                self.preparation,
            )
        self.assertEqual(self.calls, [])

    def test_changed_supervisor_ceiling_refused(self):
        self.supervisor_path.joinpath("memory.max").write_text("805306369")
        with self.assertRaises(ValueError):
            setup.create_owned_watchdog(
                self.parent,
                self.worker,
                self.supervisor,
                self.aggregate,
                self.configuration,
                self.preparation,
            )

    def test_terminal_observes_exit_reaping_and_worker_empty(self):
        lifetime = self.watchdog()
        self.bridge.owned.watchdog.result = 0
        os.write(self.watch_exit_write, b"synthetic exit")
        result = lifetime.terminal(recovery_already_attempted=True)
        self.assertTrue(result.worker_empty)
        self.assertTrue(result.watchdog_exited)
        self.assertTrue(result.watchdog_reaped)
        self.assertFalse(result.resources_reusable)
        self.assertEqual(result.errors, ())
        self.assertEqual(lifetime.lifeline, -1)
        os.fstat(lifetime.kill)
        os.fstat(lifetime.task.pidfd)

    def test_surviving_watchdog_blocks_terminal_and_grace_reset(self):
        lifetime = self.watchdog()
        result = lifetime.terminal(recovery_already_attempted=True)
        deadline = lifetime.recovery_deadline
        again = lifetime.terminal()
        self.assertFalse(result.watchdog_exited)
        self.assertFalse(result.watchdog_reaped)
        self.assertFalse(again.resources_reusable)
        self.assertEqual(lifetime.recovery_deadline, deadline)
        self.assertLessEqual(deadline, time.monotonic())

    def test_parent_still_in_worker_prevents_cleanup_kill(self):
        lifetime = self.watchdog()
        self.bridge.parent_path.joinpath("cgroup").write_text(
            f"0::/{self.worker.identity.relative_path}\n"
        )
        with patch.object(self.worker, "stop") as stopped:
            result = lifetime.terminal(recovery_already_attempted=True)
        stopped.assert_not_called()
        self.assertTrue(result.errors)
        self.assertGreaterEqual(lifetime.lifeline, 0)
        self.assertFalse(result.resources_reusable)

    def test_reaping_without_pidfd_exit_is_not_terminal(self):
        lifetime = self.watchdog()
        lifetime.process.result = 0
        result = lifetime.terminal(recovery_already_attempted=True)
        self.assertTrue(result.watchdog_reaped)
        self.assertFalse(result.watchdog_exited)

    def test_namespace_parent_derives_actual_pid_and_migrates_only_self(self):
        bridge = self.bridge
        bridge.parent_path = bridge.parent_path.rename(bridge.proc_root / str(os.getpid()))
        bridge.parent_path.joinpath("cgroup").write_text(
            f"0::/{self.setup_group.identity.relative_path}\n"
        )
        self.supervisor_path.joinpath("cgroup.procs").write_text("")

        def migrate(group):
            self.assertIs(group, self.supervisor)
            bridge.parent_path.joinpath("cgroup").write_text(
                f"0::/{group.identity.relative_path}\n"
            )
            self.supervisor_path.joinpath("cgroup.procs").write_text(str(os.getpid()))

        with bridge.kernel_proc(), patch.object(setup, "_move_self", side_effect=migrate):
            parent = setup.enter_namespace_parent(self.controls, self.groups)
        self.addCleanup(parent.close)
        self.assertEqual(parent.spec.pid, os.getpid())
        self.assertEqual(parent.spec.start_ticks, 123456)
        self.assertEqual(parent.spec.namespaces, bridge.namespaces)
        self.assertEqual(parent.spec.capabilities, setup.CAPABILITIES)
        self.assertFalse(self.worker.sample().populated)

    def test_namespace_alias_is_refused_before_migration(self):
        bridge = self.bridge
        bridge.parent_path = bridge.parent_path.rename(bridge.proc_root / str(os.getpid()))
        controls = self.controls.model_copy(update={"outer_namespaces": bridge.namespaces})
        self.supervisor_path.joinpath("cgroup.procs").write_text("")
        with (
            bridge.kernel_proc(),
            patch.object(setup, "_move_self") as move,
            self.assertRaisesRegex(ValueError, "differ"),
        ):
            setup.enter_namespace_parent(controls, self.groups)
        move.assert_not_called()

    def test_parent_migration_failure_retains_identity_and_groups(self):
        bridge = self.bridge
        bridge.parent_path = bridge.parent_path.rename(bridge.proc_root / str(os.getpid()))
        bridge.parent_path.joinpath("cgroup").write_text(
            f"0::/{self.setup_group.identity.relative_path}\n"
        )
        self.supervisor_path.joinpath("cgroup.procs").write_text("")
        with (
            bridge.kernel_proc(),
            patch.object(setup, "_move_self", side_effect=OSError("synthetic migration refusal")),
            self.assertRaises(setup.NamespaceParentRefusal) as caught,
        ):
            setup.enter_namespace_parent(self.controls, self.groups)
        self.addCleanup(caught.exception.parent.close)
        self.assertIs(caught.exception.groups["worker"], self.worker)
        self.assertFalse(caught.exception.resources_reusable)

    def test_c_helper_source_has_fixed_control_normalization_and_no_native_change(self):
        source = Path("src/crewshal/bootstrap_helper.c").read_text()
        self.assertIn("F_DUPFD_CLOEXEC, 16", source)
        self.assertIn("dup2(retained[i], i + 3)", source)
        self.assertIn('"--watchdog-fds"', source)
        self.assertIn('"--namespace-fds"', source)
        self.assertIn("F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL", source)
        self.assertIn("PTRACE_TRACEME", source)
        self.assertIn("raise(SIGSTOP)", source)
        self.assertIn("execve(argv[2], argv + 2, environ)", source)

    @contextmanager
    def control_transport(self, controls=None, seals=15, wrong_group=False):
        controls = controls or self.controls
        path = self.f.root / "sealed-controls"
        path.write_bytes(controls.model_dump_json().encode())
        descriptors = {3: os.open(path, os.O_RDONLY)}
        for number, name in enumerate(("aggregate", "setup", "supervisor", "worker"), 4):
            descriptors[number] = os.dup(self.groups[name].descriptor)
        if wrong_group:
            os.close(descriptors[7])
            descriptors[7] = os.dup(self.setup_group.descriptor)
        real_os = os

        class DescriptorView:
            def __getattr__(self, key):
                return getattr(real_os, key)

            def fstat(self, number):
                return real_os.fstat(descriptors[number])

            def pread(self, number, count, offset):
                return real_os.pread(descriptors[number], count, offset)

            def close(self, number):
                real_os.close(descriptors.pop(number))

        def attach(identity):
            group = next(group for group in self.groups.values() if group.identity == identity)
            return OwnedCgroup(group.descriptor, identity)

        with (
            patch.object(setup, "os", DescriptorView()),
            patch.object(setup, "_seals", return_value=(10001, 10002, 15)),
            patch.object(setup.fcntl, "fcntl", return_value=seals),
            patch.object(OwnedCgroup, "attach", side_effect=attach),
        ):
            try:
                yield descriptors
            finally:
                for handle in descriptors.values():
                    os.close(handle)

    def test_sealed_transport_reattaches_identity_and_closes_original_controls(self):
        with self.control_transport() as descriptors:
            controls, groups = setup.receive_namespace_controls()
            self.assertEqual(descriptors, {})
        for group in groups.values():
            self.addCleanup(group.close)
        self.assertEqual(controls, self.controls)
        self.assertEqual(
            {name: group.identity for name, group in groups.items()}, self.controls.groups
        )
        self.assertNotEqual(groups["worker"].descriptor, self.worker.descriptor)

    def test_unsealed_control_record_refused_and_originals_closed(self):
        with (
            self.control_transport(seals=7) as descriptors,
            self.assertRaisesRegex(ValueError, "immutable"),
        ):
            setup.receive_namespace_controls()
        self.assertEqual(descriptors, {})

    def test_wrong_inherited_group_object_refused(self):
        with (
            self.control_transport(wrong_group=True),
            self.assertRaisesRegex(ValueError, "descriptor differs"),
        ):
            setup.receive_namespace_controls()

    def test_stale_namespace_command_refused(self):
        controls = self.controls.model_copy(deep=True)
        controls.setup.namespace_argv.append("--as-pid-1")
        with (
            self.control_transport(controls),
            self.assertRaisesRegex(ValueError, "preparation differs"),
        ):
            setup.receive_namespace_controls()

    def test_missing_control_role_refused(self):
        controls = self.controls.model_copy(deep=True)
        controls.groups.pop("setup")
        with self.control_transport(controls), self.assertRaisesRegex(ValueError, "inventory"):
            setup.receive_namespace_controls()

    def test_setup_ceiling_change_refused_after_transport(self):
        self.setup_path.joinpath("pids.max").write_text("129")
        with self.control_transport(), self.assertRaisesRegex(ValueError, "ceiling"):
            setup.receive_namespace_controls()

    def external_observer(self):
        path = self.f.aggregate_path / "observer"
        path.mkdir()
        group = self.f.group(path, "owned.slice/session.scope/observer", True)
        self.observer_group = group
        path.joinpath("cgroup.procs").write_text(str(os.getpid()))
        old = self.parent.spec
        self.parent.spec = TrustedTaskSpec.model_validate(
            {**old.model_dump(), "cgroup": group.identity}
        )
        self.bridge.parent_path.joinpath("cgroup").write_text(
            f"0::/{group.identity.relative_path}\n"
        )
        return group, old

    def namespace(self, fail_constructor=False, fail_return=False):
        self.external_observer()
        self.supervisor_path.joinpath("cgroup.procs").write_text("")
        self.supervisor_path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0")
        self.plan = setup.prepare_namespace_setup(
            self.configuration, self.preparation, self.parent.spec.argv, self.parent.spec.executable
        )
        controls_path = self.f.root / "synthetic-capsule"
        controls_path.write_text("synthetic sealed data")

        def capsule(controls):
            self.captured_controls = controls
            return os.open(controls_path, os.O_RDONLY)

        def migrate(group):
            self.assertIs(group, self.setup_group)
            self.bridge.parent_path.joinpath("cgroup").write_text(
                f"0::/{group.identity.relative_path}\n"
            )
            self.calls.append(("move_setup",))

        def returning(observer, observer_group):
            self.calls.append(("return_observer",))
            if fail_return:
                raise OSError("synthetic observer return failed")
            self.bridge.parent_path.joinpath("cgroup").write_text(
                f"0::/{observer.spec.cgroup.relative_path}\n"
            )
            observer.verify(observer.spec.cgroup)

        def construct(argv, options):
            self.assertEqual(argv[:2], ["/bin/crewshal-bootstrap", "--namespace-fds"])
            self.assertEqual(tuple(int(value) for value in argv[2:7]), options["pass_fds"])
            self.assertEqual(argv[7:9], ["--", "/usr/bin/bwrap"])
            self.assertEqual(options["env"], {})
            self.assertNotIn("preexec_fn", options)
            self.parent.verify(self.setup_group.identity)
            if fail_constructor:
                raise OSError("synthetic Popen failure")
            self.setup_path.joinpath("cgroup.procs").write_text("12345")
            self.setup_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
            return self.f.child

        with (
            patch.object(setup, "_capsule", side_effect=capsule),
            patch.object(setup, "_move_self", side_effect=migrate),
            patch.object(setup, "_move_self_to_observer", side_effect=returning),
            self.synthetic_popen(construct),
        ):
            return setup.create_namespace_setup(
                self.parent,
                self.observer_group,
                self.aggregate,
                self.setup_group,
                self.supervisor,
                self.worker,
                self.configuration,
                self.preparation,
                self.plan,
            )

    def test_outer_wrapper_is_born_in_setup_and_observer_returns(self):
        lifetime = self.namespace()
        self.assertIs(lifetime.wrapper, self.f.child)
        self.assertEqual(self.calls[0], ("move_setup",))
        self.assertEqual(self.calls[-1], ("return_observer",))
        self.assertFalse(self.worker.sample().populated)
        self.assertFalse(lifetime.resources_reusable)
        self.assertTrue(self.parent._setup_started)
        self.assertEqual(lifetime.controls, self.captured_controls)

    def test_wrapper_constructor_failure_returns_observer_and_retains_groups(self):
        with self.assertRaises(setup.NamespaceSetupRefusal) as caught:
            self.namespace(fail_constructor=True)
        self.parent.verify(self.parent.spec.cgroup)
        self.assertIs(caught.exception.lifetime.worker, self.worker)
        self.assertIsNone(caught.exception.lifetime.wrapper)
        self.assertTrue(self.parent._setup_started)
        self.assertFalse(caught.exception.resources_reusable)

    def test_observer_return_failure_retains_created_wrapper_without_worker_stop(self):
        with (
            patch.object(self.worker, "stop") as stop,
            self.assertRaises(setup.NamespaceSetupRefusal) as caught,
        ):
            self.namespace(fail_return=True)
        stop.assert_not_called()
        self.assertIs(caught.exception.lifetime.wrapper, self.f.child)
        self.assertFalse(caught.exception.resources_reusable)

    def external_terminal(self, worker_stops=True, processes_exit=True):
        host_parent = self.parent
        self.external_observer()
        # Keep a separately retained host-view parent handle. Synthetic PID
        # values here are observed fixture data, never migration/signal targets.
        old = host_parent.spec
        parent_spec = TrustedTaskSpec.model_validate(
            {**old.model_dump(), "pid": 44444, "parent_pid": 1, "cgroup": self.supervisor.identity}
        )
        directory = os.open(self.bridge.parent_path, os.O_RDONLY | os.O_DIRECTORY)
        host_parent = parent_fixtures.bridge.RetainedTrustedTask(
            directory, self.f.pid_reader.fileno(), parent_spec
        )
        os.close(directory)
        self.addCleanup(host_parent.close)
        watch = self.bridge.watchdog.task
        watch.spec = TrustedTaskSpec.model_validate(
            {**watch.spec.model_dump(), "parent_pid": 44444}
        )
        wrapper = type(self.f.child)(self.f.in_writer, self.f.out_reader, self.f.err_reader)
        wrapper.pid = 98765
        lifetime = setup.OwnedNamespaceSetup(
            wrapper,
            self.controls,
            self.aggregate,
            self.setup_group,
            self.supervisor,
            self.worker,
            self.observer_group,
        )
        self.setup_path.joinpath("cgroup.procs").write_text("12345")
        self.setup_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
        self.supervisor_path.joinpath("cgroup.procs").write_text("44444\n54321")
        self.supervisor_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
        calls = []

        def role_stop(group, path, name):
            calls.append(name)
            self.assertFalse(self.worker.sample().populated)
            group.stop_original()
            if processes_exit:
                path.joinpath("cgroup.procs").write_text("")
                path.joinpath("cgroup.events").write_text("populated 0\nfrozen 0")

        def ready(handles, writes, errors, timeout):
            # Parent fixture shares pidfd with observer; isolate the synthetic
            # exit observation seam without declaring that observer dead.
            return (list(handles) if processes_exit else [], [], [])

        if processes_exit:
            wrapper.result = 0
        with (
            patch.object(self.supervisor, "stop_original", self.supervisor.stop, create=True),
            patch.object(self.setup_group, "stop_original", self.setup_group.stop, create=True),
            patch.object(
                self.supervisor,
                "stop",
                side_effect=lambda: role_stop(self.supervisor, self.supervisor_path, "supervisor"),
            ),
            patch.object(
                self.setup_group,
                "stop",
                side_effect=lambda: role_stop(self.setup_group, self.setup_path, "setup"),
            ),
            patch.object(
                setup,
                "_terminal_task_exited",
                side_effect=lambda task: bool(ready([task.pidfd], [], [], 0)[0]),
            ),
        ):
            if not worker_stops:
                self.f.worker_path.joinpath("cgroup.events").write_text("populated 1\nfrozen 0")
                with patch.object(
                    self.worker, "stop", side_effect=OSError("synthetic worker stop refusal")
                ):
                    result = setup.terminal_namespace_setup(
                        lifetime, self.parent, host_parent, watch, recovery_already_attempted=True
                    )
            else:
                result = setup.terminal_namespace_setup(
                    lifetime, self.parent, host_parent, watch, recovery_already_attempted=True
                )
        return lifetime, result, calls

    def test_external_terminal_orders_worker_empty_before_wrapper_role_stops(self):
        lifetime, result, calls = self.external_terminal()
        self.assertEqual(calls, ["supervisor", "setup"])
        self.assertTrue(result.groups_empty)
        self.assertTrue(result.parent_exited)
        self.assertTrue(result.watchdog_exited)
        self.assertTrue(result.wrapper_reaped)
        self.assertEqual(result.errors, ())
        self.assertFalse(result.resources_reusable)
        self.assertLessEqual(lifetime.recovery_deadline, time.monotonic())

    def test_failed_worker_stop_keeps_supervisor_watchdog_and_setup_alive(self):
        _, result, calls = self.external_terminal(worker_stops=False)
        self.assertEqual(calls, [])
        self.assertFalse(result.groups_empty)
        self.assertTrue(result.errors)
        self.assertFalse(result.resources_reusable)

    def test_surviving_external_watchdog_and_wrapper_block_terminal(self):
        _, result, _ = self.external_terminal(processes_exit=False)
        self.assertFalse(result.watchdog_exited)
        self.assertFalse(result.wrapper_reaped)
        self.assertFalse(result.groups_empty)
        self.assertFalse(result.resources_reusable)

    def test_resource_refusal_does_not_remove_external_cleanup_ownership(self):
        self.f.aggregate_path.joinpath("memory.events").write_text("max 1\noom 1\noom_kill 1")
        self.supervisor_path.joinpath("pids.events").write_text("max 1")
        _, result, calls = self.external_terminal()
        self.assertEqual(calls, ["supervisor", "setup"])
        self.assertTrue(result.groups_empty)
        self.assertFalse(result.resources_reusable)

    def test_terminal_lifeline_replacement_refused_without_closing_unrelated_file(self):
        lifetime = self.watchdog()
        path = self.f.root / "unrelated-terminal-file"
        path.write_bytes(b"preserved bytes")
        handle = os.open(path, os.O_RDONLY)
        try:
            os.dup2(handle, lifetime.lifeline)
        finally:
            os.close(handle)
        with patch.object(self.worker, "stop") as stop:
            result = lifetime.terminal(recovery_already_attempted=True)
        stop.assert_not_called()
        self.assertTrue(result.errors)
        os.fstat(lifetime.lifeline)
        self.assertEqual(path.read_bytes(), b"preserved bytes")
        self.assertFalse(result.resources_reusable)

    def test_watchdog_setup_preserves_original_stopped_native_admission(self):
        lifetime = self.watchdog()
        admitted = self.bridge.stage()
        self.addCleanup(admitted.proc.close)
        admitted.proc.verify_stopped()
        self.assertIs(admitted.child, self.f.child)
        self.assertEqual(
            admitted.receipt.started_monotonic, lifetime.observed.deadline.started_monotonic
        )
        self.assertEqual(admitted.proc.spec.start_ticks, self.f.spec.start_ticks)
        self.assertFalse(admitted.receipt.execution_allowed)
        self.assertEqual(self.worker.sample().direct_pids, [12345])
