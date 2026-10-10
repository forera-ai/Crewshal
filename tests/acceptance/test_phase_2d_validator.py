"""Fresh ordinary FD/proc fixtures; every Linux process/trace/view effect is synthetic.

No validator, namespace, helper, compiler, credential or model is executed. These
tests establish source contracts only and cannot qualify the missing view caller.
"""

import os
import signal
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.candidate import FrozenCandidate
from crewshal.admission import NamespaceIdentity
from crewshal.contracts import record_digest
from crewshal.linux_setup import TerminalObservation
from crewshal.linux_validator import (
    AdmittedValidator,
    RetainedValidatorProc,
    ValidatorAdmissionSpec,
    ValidatorAttempt,
    ValidatorProcRefusal,
    ValidatorRefusal,
    attach_traced_validator,
    create_validator_watchdog,
    prepare_validator_attempt,
    stage_retained_validator,
)
from crewshal.model import digest
from crewshal.supervisor import CapturedProcess, ProcessObservation
from tests.acceptance import test_phase_2d_bootstrap as bootstrap_fixtures


class ValidatorTrace:
    def __init__(self, test):
        self.test = test
        self.calls = []
        self.events = [bootstrap_fixtures.STOP, bootstrap_fixtures.EXEC, bootstrap_fixtures.STOP]
        self.exec_identity = test.fixture.child.pid
        self.filter_available = True

    def wait(self, pid):
        event = self.events.pop(0)
        self.calls.append("wait")
        if event == bootstrap_fixtures.EXEC:
            f = self.test.fixture
            f.executable.chmod(0o644)
            f.executable.write_bytes(b"synthetic validator bytes")
            f.executable.chmod(0o555)
            self.test.argv(f.configuration.validator_argv)
        return pid, event

    def options(self, pid):
        self.calls.append("options")

    def continue_exec(self, pid):
        self.calls.append("continue")

    def exec_pid(self, pid):
        return self.exec_identity

    def verify_storage_filter(self, pid):
        self.calls.append("kernel_filter")
        if not self.filter_available:
            raise ValueError("synthetic kernel filter unavailable")

    def queue_stop(self, pidfd):
        self.calls.append("queue_stop")

    def verify_stop_delivery(self, pid, sender):
        self.calls.append(("delivery", sender))

    def detach_stopped(self, pid):
        self.calls.append("detach")
        self.test.fixture.status["TracerPid"] = "0"
        self.test.fixture.write_status()
        self.test.bootstrap.write_stat("T")


class Phase2DValidator(unittest.TestCase):
    def setUp(self):
        fresh = bootstrap_fixtures.Phase2DBootstrap()
        fresh.setUp()
        self.addCleanup(fresh.doCleanups)
        self.bootstrap = fresh
        f = self.fixture = fresh.fixture
        self.validator_path = f.aggregate_path / "validator"
        self.validator_path.mkdir()
        self.validator = f.group(self.validator_path, "owned.slice/session.scope/validator", False)
        self.spec = ValidatorAdmissionSpec(
            configuration=record_digest(f.configuration),
            pid=f.child.pid,
            parent_pid=os.getpid(),
            start_ticks=f.spec.start_ticks,
            boot_id=f.spec.boot_id,
            validator=self.validator.identity,
            aggregate=f.aggregate.identity,
            namespaces=f.spec.namespaces,
            executable_sha256=digest(b"synthetic validator bytes"),
        )
        self.proc = RetainedValidatorProc(f.proc.descriptor, f.pid_reader.fileno(), self.spec)
        self.addCleanup(self.proc.close)
        f.status.update(Uid="65531 65531 65531 65531", Gid="65531 65531 65531 65531")
        f.write_status()
        f.write("environ", b"")
        f.write("cgroup", "0::/owned.slice/session.scope/validator\n")
        (f.proc_path / "cwd").unlink()
        (f.proc_path / "cwd").symlink_to("/candidate/owned")
        self.argv(["/bin/crewshal-bootstrap", "--validator", *f.configuration.validator_argv])
        attempt = self.attempt = object.__new__(ValidatorAttempt)
        attempt.validator, attempt.aggregate = self.validator, f.aggregate
        attempt.configuration = f.configuration
        attempt._configuration = record_digest(f.configuration)
        attempt.staged = attempt.failed = attempt.resumed = attempt.captured = False
        attempt.child = attempt.proc = attempt.admitted = None
        attempt.parent = SimpleNamespace(spec=SimpleNamespace(pid=os.getpid()), verify=Mock())
        attempt.watchdog = SimpleNamespace(
            observed=SimpleNamespace(deadline=fresh.deadline, claim=Mock()),
            terminal=Mock(return_value=TerminalObservation(True, True, True, ())),
            task=object(),
            process=SimpleNamespace(poll=lambda: 0),
        )
        # Explicit Linux admission/view seams. Actual proc, bytes, FD directions,
        # exec ordering and controller readbacks below remain ordinary fixtures.
        attempt.verify = Mock()
        attempt.verify_view = Mock()
        self.driver = ValidatorTrace(self)

    def argv(self, argv):
        self.fixture.write("cmdline", b"\0".join(x.encode() for x in argv) + b"\0")

    def stage(self, **changes):
        arguments = dict(
            attempt=self.attempt,
            child=self.fixture.child,
            proc=self.proc,
            preparation=self.bootstrap.preparation,
            driver=self.driver,
            cancelled=lambda: False,
        )
        arguments.update(changes)
        with patch("subprocess.Popen.__init__", side_effect=AssertionError("no process startup")):
            return stage_retained_validator(**arguments)

    def resume(self, admitted):
        with patch("crewshal.linux_validator.signal.pidfd_send_signal", create=True) as send:
            admitted.resume()
        send.assert_called_once_with(self.proc.pidfd, signal.SIGCONT)

    def test_dedicated_validator_role_does_not_broaden_native_uid_contract(self):
        with self.assertRaises(ValueError):
            ValidatorAdmissionSpec.model_validate({**self.spec.model_dump(), "uid": 65534})
        with self.assertRaises(ValueError):
            type(self.fixture.spec).model_validate(
                {**self.fixture.spec.model_dump(), "native_uid": 65531}
            )
        with self.assertRaisesRegex(ValueError, "distinct exact"):
            ValidatorAdmissionSpec.model_validate(
                {**self.spec.model_dump(), "validator": self.fixture.worker.identity}
            )

    def test_exec_filter_precedes_queue_detach_and_exact_direct_child_is_retained(self):
        admitted = self.stage()
        self.attempt.watchdog.observed.claim.assert_called_once_with(
            self.validator, self.fixture.configuration
        )
        self.assertIs(admitted.attempt.child, self.fixture.child)
        self.assertIs(admitted.attempt.proc, self.proc)
        self.proc.verify_state(traced=False)
        self.assertLess(
            self.driver.calls.index("kernel_filter"), self.driver.calls.index("queue_stop")
        )
        self.assertLess(self.driver.calls.index("queue_stop"), self.driver.calls.index("detach"))
        self.assertEqual((self.validator_path / "cgroup.kill").read_bytes(), b"")
        self.assertEqual(
            self.bootstrap.deadline.expires_ns - self.bootstrap.deadline.origin_ns, 5_000_000_000
        )

    def test_missing_filter_burns_handoff_retains_handles_and_never_detaches(self):
        self.driver.filter_available = False
        with self.assertRaisesRegex(ValidatorRefusal, "filter unavailable") as error:
            self.stage()
        self.assertIs(error.exception.attempt, self.attempt)
        self.assertFalse(error.exception.resources_reusable)
        self.assertTrue(self.attempt.failed)
        self.assertNotIn("queue_stop", self.driver.calls)
        self.assertNotIn("detach", self.driver.calls)
        with self.assertRaisesRegex(ValidatorRefusal, "consumed"):
            self.stage()
        os.fstat(self.proc.descriptor)
        os.fstat(self.proc.pidfd)

    def test_wrapper_or_arbitrary_pid_cannot_replace_original_direct_child(self):
        with self.assertRaisesRegex(ValidatorRefusal, "ownership differs"):
            self.stage(child=SimpleNamespace(pid=self.spec.pid))
        self.assertEqual(self.driver.calls, [])
        self.attempt.watchdog.terminal.assert_not_called()

    def test_changed_exec_pid_refuses_before_kernel_filter_and_detach(self):
        self.driver.exec_identity += 1
        with self.assertRaisesRegex(ValidatorRefusal, "PID/thread"):
            self.stage()
        self.assertNotIn("kernel_filter", self.driver.calls)
        self.assertNotIn("detach", self.driver.calls)

    def test_extra_inherited_fd_refuses_before_helper_continue(self):
        (self.fixture.proc_path / "fd" / "3").symlink_to("socket:[1]")
        with self.assertRaisesRegex(ValidatorRefusal, "only three"):
            self.stage()
        self.assertNotIn("continue", self.driver.calls)

    def test_actual_uid_capability_privilege_and_hard_limit_readbacks_refuse(self):
        for key, value in (
            ("Uid", "65534 65534 65534 65534"),
            ("Gid", "0 0 0 0"),
            ("CapBnd", "0000000000000001"),
            ("NoNewPrivs", "0"),
            ("Groups", "65531 0"),
            ("Threads", "2"),
        ):
            with self.subTest(key=key):
                old = self.fixture.status[key]
                self.fixture.status[key] = value
                self.fixture.write_status()
                with self.assertRaises(ValueError):
                    self.proc.verify_state(traced=True)
                self.fixture.status[key] = old
                self.fixture.write_status()
        self.fixture.write("limits", "Max file size 131072 unlimited bytes\n")
        with self.assertRaisesRegex(ValueError, "file growth limits"):
            self.proc.verify_state(traced=True)

    def test_nonempty_environment_wrong_argv_cwd_and_group_are_actual_refusals(self):
        argv = [
            "/bin/crewshal-bootstrap",
            "--validator",
            *self.fixture.configuration.validator_argv,
        ]
        for name, value in (
            ("environ", b"TOKEN=secret\0"),
            ("cmdline", b"/bin/python3\0"),
            ("cgroup", b"0::/owned.slice/session.scope/worker\n"),
        ):
            with self.subTest(name=name):
                old = (self.fixture.proc_path / name).read_bytes()
                self.fixture.write(name, value)
                with self.assertRaises(ValueError):
                    self.proc.read_configuration(self.fixture.configuration, argv)
                self.fixture.write(name, old)
        (self.fixture.proc_path / "cwd").unlink()
        (self.fixture.proc_path / "cwd").symlink_to("/scratch/checkout")
        with self.assertRaisesRegex(ValueError, "cwd"):
            self.proc.read_configuration(self.fixture.configuration, argv)

    def test_spec_mutation_cannot_change_retained_actual_proc_authority(self):
        self.proc.spec.start_ticks += 1
        with self.assertRaisesRegex(ValueError, "descriptor changed"):
            self.proc.verify_handles()

    def test_pidfd_exit_is_positive_and_pid_text_alone_is_insufficient(self):
        self.bootstrap.write_stat("Z")
        with self.assertRaisesRegex(ValueError, "exit unobserved"):
            self.proc.verify_exited()
        self.fixture.pid_writer.write(b"synthetic pidfd readiness")
        self.proc.verify_exited()

    def test_stopped_handoff_resume_is_single_use_and_capture_requires_resume(self):
        admitted = self.stage()
        with self.assertRaisesRegex(ValidatorRefusal, "capture consumed"):
            admitted.capture(cancelled=lambda: False)
        self.resume(admitted)
        self.assertTrue(self.attempt.resumed)
        with self.assertRaisesRegex(ValidatorRefusal, "resume consumed"):
            self.resume(admitted)

    def test_resume_rechecks_stopped_role_before_any_signal_and_consumes_failure(self):
        admitted = self.stage()
        self.fixture.status["CapEff"] = "0000000000000001"
        self.fixture.write_status()
        with patch("crewshal.linux_validator.signal.pidfd_send_signal", create=True) as send:
            with self.assertRaisesRegex(ValidatorRefusal, "capabilities"):
                admitted.resume()
        send.assert_not_called()
        self.assertTrue(self.attempt.failed)
        self.assertTrue(self.attempt.resumed)

    def test_resume_does_not_substitute_a_new_parent_pipe(self):
        admitted = self.stage()
        self.fixture.child.stdout = self.fixture.err_reader
        with self.assertRaises(ValidatorRefusal):
            self.resume(admitted)
        self.assertTrue(self.attempt.failed)

    def captured(self, termination=None):
        started = self.bootstrap.deadline.started
        observation = ProcessObservation(
            started=started,
            ended=started,
            elapsed_seconds=0,
            exit_code=0,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=True,
            termination=termination,
        )
        sample = self.validator.sample()
        return CapturedProcess(observation, b"ok\n", b"", sample, sample, False, False)

    def test_capture_forwards_original_timer_and_uses_one_terminal_recovery(self):
        admitted = self.stage()
        self.resume(admitted)
        captured = self.captured("timeout")
        admitted.verify_terminal = Mock()
        with patch(
            "crewshal.linux_validator.capture_attached_process", return_value=captured
        ) as run:
            self.assertIs(admitted.capture(cancelled=lambda: False), captured)
        arguments = run.call_args.kwargs
        self.assertEqual(arguments["started_monotonic"], self.bootstrap.deadline.started_monotonic)
        self.assertEqual(arguments["started"], self.bootstrap.deadline.started)
        self.assertNotIn("stdin_stream", arguments)
        self.assertNotIn("exchange", arguments)
        self.attempt.watchdog.terminal.assert_called_once_with(recovery_already_attempted=True)
        admitted.verify_terminal.assert_called_once_with(0)
        with self.assertRaisesRegex(ValidatorRefusal, "capture consumed"):
            admitted.capture(cancelled=lambda: False)

    def test_capture_unknown_terminal_keeps_original_custody_and_refuses(self):
        admitted = self.stage()
        self.resume(admitted)
        self.attempt.watchdog.terminal.return_value = TerminalObservation(True, False, False, ())
        with patch(
            "crewshal.linux_validator.capture_attached_process", return_value=self.captured()
        ):
            with self.assertRaisesRegex(ValidatorRefusal, "remains unknown"):
                admitted.capture(cancelled=lambda: False)
        self.assertTrue(self.attempt.failed)
        self.assertIs(self.attempt.child, self.fixture.child)
        self.assertIs(self.attempt.proc, self.proc)
        self.attempt.watchdog.terminal.assert_called_once_with(recovery_already_attempted=False)

    def test_capture_exception_cannot_create_another_grace_or_retry(self):
        admitted = self.stage()
        self.resume(admitted)
        with patch(
            "crewshal.linux_validator.capture_attached_process", side_effect=OSError("read")
        ):
            with self.assertRaisesRegex(OSError, "read"):
                admitted.capture(cancelled=lambda: False)
        self.attempt.watchdog.terminal.assert_called_once_with(recovery_already_attempted=True)
        self.assertTrue(self.attempt.failed)

    def test_terminal_pidfd_empty_role_watchdog_and_parent_are_independent(self):
        admitted = self.stage()
        self.fixture.child.result = 0
        self.fixture.pid_writer.write(b"synthetic exit readiness")
        self.attempt.supervisor = SimpleNamespace(
            _read=lambda name: str(os.getpid()), identity=self.fixture.aggregate.identity
        )
        with patch("crewshal.linux_validator._terminal_task_exited", return_value=True):
            with self.assertRaisesRegex(ValueError, "repopulated"):
                admitted.verify_terminal(0)
            (self.validator_path / "cgroup.events").write_text("populated 0\nfrozen 0")
            (self.validator_path / "cgroup.procs").write_text("")
            admitted.verify_terminal(0)
        with patch("crewshal.linux_validator._terminal_task_exited", return_value=False):
            with self.assertRaisesRegex(ValueError, "watchdog"):
                admitted.verify_terminal(0)
        self.attempt.parent.verify.assert_called_once_with(self.attempt.supervisor.identity)

    def test_attachment_rejects_nonchild_before_proc_or_kernel_operations(self):
        with patch("crewshal.linux_validator._proc_root") as root:
            with self.assertRaisesRegex(ValueError, "direct Popen"):
                attach_traced_validator(SimpleNamespace(pid=self.spec.pid), self.spec)
        root.assert_not_called()

    def test_preparation_missing_origin_retains_actual_received_fds_and_burns_retry(self):
        directory = os.open(self.fixture.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, directory)
        parent = SimpleNamespace()
        controls = SimpleNamespace(configuration=self.fixture.configuration, batch_origin_ns=None)
        with patch("subprocess.Popen.__init__", side_effect=AssertionError("no startup")):
            with self.assertRaisesRegex(ValidatorRefusal, "sealed batch origin") as error:
                prepare_validator_attempt(
                    parent,
                    self.validator,
                    self.fixture.aggregate,
                    self.fixture.aggregate,
                    controls,
                    object(),
                    directory,
                    directory,
                    FrozenCandidate(files=[]),
                )
        attempt = error.exception.attempt
        self.assertIs(parent._validator_attempt, attempt)
        self.assertTrue(attempt.failed)
        self.assertEqual(len(attempt.descriptors), 2)
        for descriptor in attempt.descriptors:
            os.fstat(descriptor)
            self.addCleanup(os.close, descriptor)
        with self.assertRaisesRegex(ValueError, "consumed"):
            prepare_validator_attempt(
                parent,
                self.validator,
                self.fixture.aggregate,
                self.fixture.aggregate,
                controls,
                object(),
                directory,
                directory,
                FrozenCandidate(files=[]),
            )

    def test_batch_cutoff_is_original_570_seconds_and_failure_is_latched(self):
        attempt = self.attempt
        del attempt.verify
        attempt.parent._validator_attempt = attempt
        attempt.controls = SimpleNamespace(configuration=attempt.configuration, batch_origin_ns=1)
        attempt.inventory = object()
        attempt._owners = (
            attempt.parent,
            attempt.validator,
            object(),
            attempt.aggregate,
            attempt.inventory,
            attempt.controls,
        )
        attempt.supervisor = attempt._owners[2]
        attempt.manifest = FrozenCandidate(files=[])
        attempt._manifest = record_digest(attempt.manifest)
        attempt.origin_ns = 1
        attempt.cutoff_ns = 570_000_000_001
        with patch("crewshal.linux_validator.time.monotonic_ns", return_value=attempt.cutoff_ns):
            with self.assertRaisesRegex(ValueError, "cutoff"):
                attempt.verify()
        self.assertTrue(attempt.failed)
        with patch("crewshal.linux_validator.time.monotonic_ns", return_value=2):
            with self.assertRaisesRegex(ValueError, "attempt failed"):
                attempt.verify()

    def test_admission_and_attempt_cannot_be_fabricated_or_serialized(self):
        for cls in (AdmittedValidator, ValidatorAttempt):
            with self.assertRaises(ValueError):
                cls()
        admitted = self.stage()
        with self.assertRaises(TypeError):
            admitted.__reduce__()
        with self.assertRaises(TypeError):
            self.attempt.__reduce__()

    def test_elapsed_watchdog_origin_refuses_before_helper_continue_without_renewal(self):
        original = self.bootstrap.deadline

        def checked(*, watchdog=False):
            original.check(self.fixture.worker, self.fixture.configuration)

        self.attempt.verify = checked
        with patch("crewshal.linux_validator.time.monotonic_ns", return_value=original.expires_ns):
            with self.assertRaisesRegex(ValidatorRefusal, "original deadline"):
                self.stage()
        self.assertEqual(self.driver.calls, [])
        self.assertIs(self.attempt.watchdog.observed.deadline, original)
        self.assertTrue(self.attempt.failed)

    def test_last_exec_stop_cannot_extend_original_five_seconds(self):
        original = self.bootstrap.deadline
        with patch(
            "crewshal.linux_validator.time.monotonic", return_value=original.started_monotonic + 5
        ):
            with self.assertRaisesRegex(ValidatorRefusal, "five-second"):
                self.stage()
        self.assertIsNone(self.attempt.admitted)
        self.assertEqual(original.expires_ns - original.origin_ns, 5_000_000_000)

    def test_watchdog_preparation_failure_is_consumed_before_any_operational_startup(self):
        self.attempt.watchdog_started = False
        self.attempt.verify = Mock(side_effect=ValueError("original custody unknown"))
        with patch(
            "subprocess.Popen.__init__", side_effect=AssertionError("no startup")
        ) as startup:
            with self.assertRaisesRegex(ValidatorRefusal, "custody unknown"):
                create_validator_watchdog(self.attempt, self.bootstrap.preparation)
            with self.assertRaisesRegex(ValidatorRefusal, "consumed"):
                create_validator_watchdog(self.attempt, self.bootstrap.preparation)
        startup.assert_not_called()
        self.assertTrue(self.attempt.failed)

    def test_proc_acquisition_failure_retains_actual_fds_before_metadata(self):
        with patch("crewshal.linux_validator._identity", side_effect=OSError("metadata failed")):
            with self.assertRaisesRegex(ValidatorProcRefusal, "metadata failed") as error:
                RetainedValidatorProc(
                    self.fixture.proc.descriptor, self.fixture.pid_reader.fileno(), self.spec
                )
        retained = error.exception.retained
        self.addCleanup(retained.close)
        os.fstat(retained.descriptor)
        os.fstat(retained.pidfd)
        self.assertFalse(error.exception.resources_reusable)

    def test_watchdog_metadata_failure_retains_original_actual_acquisitions(self):
        # Pipe2/Popen/attach are explicit effects seams; only ordinary fixture
        # files and pipes are acquired, never a process or kernel controller.
        attempt = self.attempt
        attempt.watchdog_started = False
        attempt.cutoff_ns = self.bootstrap.deadline.origin_ns + 570_000_000_000
        attempt.descriptors = []
        attempt.supervisor = SimpleNamespace(_read=lambda name: str(os.getpid()))
        attempt.parent.spec.cwd = "/candidate/owned"
        attempt.parent.spec.boot_id = self.spec.boot_id
        attempt.watchdog.kill = attempt.watchdog.lifeline = -1
        (self.validator_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        (self.validator_path / "cgroup.procs").write_text("")
        original_root = os.open(self.fixture.root, os.O_RDONLY | os.O_DIRECTORY)
        proc = os.dup(self.proc.descriptor)
        pidfd = os.dup(self.proc.pidfd)

        def pipe2(flags):
            return os.pipe()

        with (
            patch("crewshal.linux_validator.os.pipe2", create=True, side_effect=pipe2),
            patch(
                "crewshal.linux_validator.subprocess.Popen", return_value=self.bootstrap.watchdog
            ) as startup,
            patch("crewshal.linux_validator._proc_root", return_value=original_root),
            patch("crewshal.linux_validator._attach", return_value=(proc, pidfd)),
            patch("crewshal.linux_validator._stat_identity", side_effect=ValueError("metadata")),
        ):
            with self.assertRaisesRegex(ValidatorRefusal, "metadata") as error:
                create_validator_watchdog(attempt, self.bootstrap.preparation)
        self.assertIs(error.exception.attempt, attempt)
        self.assertIs(attempt.watchdog.process, self.bootstrap.watchdog)
        self.assertEqual(attempt.descriptors, [proc, pidfd])
        self.assertEqual(startup.call_args.kwargs["env"], {})
        self.assertTrue(startup.call_args.kwargs["close_fds"])
        for descriptor in (*attempt.descriptors, attempt.watchdog.kill, attempt.watchdog.lifeline):
            os.fstat(descriptor)
            self.addCleanup(os.close, descriptor)
        self.assertTrue(attempt.failed)

    def view(self):
        """Real linked dirs; readonly, UID and null-device kernel metadata are explicit seams."""
        root = self.fixture.root / "validator-root"
        (root / "candidate" / "owned").mkdir(parents=True)
        (root / "scratch").mkdir()
        (root / "dev" / "shm").mkdir(parents=True)
        (root / "dev" / "null").write_bytes(b"")
        (self.fixture.proc_path / "root").symlink_to(root)
        descriptors = {}
        for key, path in (
            ("root", root),
            ("frozen", root / "candidate" / "owned"),
            ("scratch", root / "scratch"),
            ("devices", root / "dev"),
        ):
            descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            self.addCleanup(os.close, descriptor)
            descriptors[key] = descriptor
        attempt = self.attempt
        del attempt.verify_view
        attempt.inventory = SimpleNamespace(
            descriptor=descriptors["root"], identity=self.identity(descriptors["root"])
        )
        attempt.frozen_fd, attempt.scratch_fd = descriptors["frozen"], descriptors["scratch"]
        unrelated = {
            name: NamespaceIdentity(device=ns.device, inode=ns.inode + 100000)
            for name, ns in self.spec.namespaces.items()
        }
        attempt.parent.spec.namespaces = {**unrelated, "user": self.spec.namespaces["user"]}
        attempt.controls = SimpleNamespace(outer_namespaces=unrelated)
        self.fixture.write(
            "mountinfo",
            "\n".join(
                f"{number} 0 1:1 / {path} {mode} - {'proc' if path == '/proc' else 'tmpfs'} x {mode}"
                for number, (path, mode) in enumerate(
                    (
                        ("/", "ro"),
                        ("/candidate/owned", "ro"),
                        ("/scratch", "rw"),
                        ("/dev/shm", "ro"),
                        ("/dev", "rw"),
                        ("/proc", "rw"),
                    ),
                    1,
                )
            ),
        )
        (self.fixture.proc_path / "net").mkdir()
        self.fixture.write("net/dev", "Inter-| header\n face | header\n lo: 0 0 0\n")
        self.fixture.write("net/route", "Iface Destination Gateway\n")
        self.fixture.write("net/if_inet6", "00000000000000000000000000000001 01 80 10 80 lo\n")
        real_fstat, real_stat = os.fstat, os.stat
        device_identity = self.identity(descriptors["devices"])
        scratch_identity = self.identity(descriptors["scratch"])

        def fstat(descriptor):
            info = real_fstat(descriptor)
            if (info.st_dev, info.st_ino) == device_identity:
                return SimpleNamespace(
                    st_uid=0,
                    st_gid=0,
                    st_mode=stat.S_IFDIR | 0o755,
                    st_dev=info.st_dev,
                    st_ino=info.st_ino,
                )
            return info

        def inspected(path, *args, **kwargs):
            info = real_stat(path, *args, **kwargs)
            if path == "null" and self.identity(kwargs["dir_fd"]) == device_identity:
                return SimpleNamespace(st_mode=stat.S_IFCHR | 0o666, st_rdev=os.makedev(1, 3))
            return info

        def filesystem(descriptor):
            return SimpleNamespace(
                f_flag=0 if self.identity(descriptor) == scratch_identity else os.ST_RDONLY
            )

        for target, side_effect in (
            ("os.fstat", fstat),
            ("os.stat", inspected),
            ("os.fstatvfs", filesystem),
        ):
            started = patch("crewshal.linux_validator." + target, side_effect=side_effect)
            started.start()
            self.addCleanup(started.stop)
        return root

    @staticmethod
    def identity(descriptor):
        info = os.fstat(descriptor)
        return info.st_dev, info.st_ino

    def test_actual_view_readback_binds_retained_readonly_root_candidate_scratch_and_shm(self):
        self.view()
        self.attempt.verify_view(self.proc)
        self.assertFalse(self.attempt.failed)

    def test_view_rejects_extra_auth_mount_and_latches_failure(self):
        self.view()
        path = self.fixture.proc_path / "mountinfo"
        path.write_bytes(path.read_bytes() + b"\n10 0 1:1 / /native-auth rw - tmpfs x rw\n")
        with self.assertRaisesRegex(ValueError, "authentication view"):
            self.attempt.verify_view(self.proc)
        self.assertTrue(self.attempt.failed)

    def test_view_rejects_same_parent_network_namespace(self):
        self.view()
        self.attempt.parent.spec.namespaces["net"] = self.proc.spec.namespaces["net"]
        with self.assertRaisesRegex(ValueError, "not distinct"):
            self.attempt.verify_view(self.proc)

    def test_view_rejects_device_file_and_nonempty_readonly_shm(self):
        root = self.view()
        (root / "dev" / "credential").write_bytes(b"untrusted extra file")
        with self.assertRaisesRegex(ValueError, "device inventory"):
            self.attempt.verify_view(self.proc)
        (root / "dev" / "credential").unlink()
        (root / "dev" / "shm" / "anonymous-storage").write_bytes(b"x")
        with self.assertRaisesRegex(ValueError, "shm differs"):
            self.attempt.verify_view(self.proc)

    def test_view_rejects_nonloopback_interface_and_routes(self):
        self.view()
        self.fixture.write("net/dev", "lo: 0 0\neth0: 0 0\n")
        with self.assertRaisesRegex(ValueError, "network"):
            self.attempt.verify_view(self.proc)

    def test_view_rejects_path_replacement_even_when_original_inode_remains(self):
        root = self.view()
        (root / "candidate" / "owned").rename(root / "candidate" / "retained-old")
        (root / "candidate" / "owned").mkdir()
        with self.assertRaisesRegex(ValueError, "candidate/scratch mount"):
            self.attempt.verify_view(self.proc)
        os.fstat(self.attempt.frozen_fd)


if __name__ == "__main__":
    unittest.main()
