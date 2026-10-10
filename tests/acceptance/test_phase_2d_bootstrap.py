"""Fresh owned-bootstrap source regressions; all child/ptrace/timer effects synthetic."""

from dataclasses import replace
from datetime import datetime, timezone
import ctypes
import os
from pathlib import Path
import signal
import struct
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.admission import NativeAdmissionSpec
from crewshal.contracts import record_digest
from crewshal.dispatch import prepare_dispatch_configuration
from crewshal.linux_bootstrap import (
    ArmedDeadline,
    BootstrapPolicy,
    BootstrapPreparation,
    BootstrapRefusal,
    LinuxTrace,
    audit_linux_bootstrap,
    bootstrap_policy,
    prepare_linux_bootstrap,
    payload_storage_filter,
    stage_retained_bootstrap,
)
from crewshal.linux_envelope import LinuxEnvelopeBindings
from crewshal.model import digest
from tests.acceptance import test_phase_2d_admission as admission_fixtures


STOP = (int(signal.SIGSTOP) << 8) | 0x7F
EXEC = (4 << 16) | (int(signal.SIGTRAP) << 8) | 0x7F


class SyntheticTrace:
    def __init__(self, fixture):
        self.fixture = fixture
        self.events = [STOP, EXEC, STOP]
        self.calls = []
        self.exec_identity = fixture.child.pid
        self.bad_sender = False
        self.detached_state = "T"
        self.extra_fd = False

    def wait(self, pid):
        status = self.events.pop(0)
        self.calls.append(("wait", status))
        if status == EXEC:
            self.fixture.executable.chmod(0o644)
            self.fixture.executable.write_bytes(b"synthetic native bytes")
            self.fixture.executable.chmod(0o555)
            self.fixture.write(
                "cmdline",
                b"\0".join(x.encode() for x in self.fixture.configuration.native_argv) + b"\0",
            )
            if self.extra_fd:
                (self.fixture.proc_path / "fd" / "3").symlink_to("socket:[123]")
        return pid, status

    def options(self, pid):
        self.calls.append(("options", pid))

    def continue_exec(self, pid):
        self.calls.append(("continue", pid))

    def exec_pid(self, pid):
        return self.exec_identity

    def verify_storage_filter(self, pid):
        self.calls.append(("kernel_filter", pid))

    def queue_stop(self, pidfd):
        self.calls.append(("queue_pidfd_stop", pidfd))

    def verify_stop_delivery(self, pid, sender):
        self.calls.append(("delivery", sender))
        if self.bad_sender:
            raise ValueError("synthetic wrong signal sender")

    def detach_stopped(self, pid):
        self.calls.append(("detach", pid))
        self.fixture.status["TracerPid"] = "0"
        self.fixture.write_status()
        self.fixture.write_stat(self.detached_state)


class Phase2DBootstrap(unittest.TestCase):
    def setUp(self):
        # This creates its own files/pipes/cgroups/candidate from scratch. No
        # previous test output or historical fixture driver is imported/replayed.
        fixture = admission_fixtures.Phase2DAdmission()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.binary = digest(b"synthetic owned helper bytes")
        old = fixture.configuration
        policy = bootstrap_policy(self.binary)
        bindings = LinuxEnvelopeBindings(
            context=record_digest(old.selection), bootstrap_policy_sha256=record_digest(policy)
        )
        compiled = prepare_dispatch_configuration(
            old.selection, preparation_digest=old.preparation_digest, linux_envelope=bindings
        )
        fixture.configuration = type(old).model_validate(
            {
                **compiled.model_dump(),
                "task_digest": old.task_digest,
                "launch_binding": old.launch_binding,
            }
        )
        fixture.spec = NativeAdmissionSpec.model_validate(
            {
                **fixture.spec.model_dump(),
                "configuration": record_digest(fixture.configuration),
                "parent_pid": os.getpid(),
            }
        )
        fixture.proc.spec = fixture.spec
        fixture.status.update(PPid=str(os.getpid()), TracerPid=str(os.getpid()))
        fixture.write_status()
        fixture.write_stat = self.write_stat
        self.write_stat("t")
        self.preparation = prepare_linux_bootstrap(fixture.configuration, helper_binary=self.binary)
        fixture.executable.chmod(0o644)
        fixture.executable.write_bytes(b"synthetic owned helper bytes")
        fixture.executable.chmod(0o555)
        fixture.write(
            "cmdline", b"\0".join(x.encode() for x in self.preparation.helper_argv) + b"\0"
        )
        reader, writer = os.pipe()
        self.addCleanup(os.close, reader)
        self.addCleanup(os.close, writer)
        self.lifeline = writer
        self.watchdog = admission_fixtures.SyntheticChild(
            fixture.in_writer, fixture.out_reader, fixture.err_reader
        )
        self.watchdog.pid = 54321
        origin = time.monotonic_ns() - 1_000_000
        self.ack = f"READY {origin} {origin + 5_000_000_000}\n".encode()
        self.deadline = self.retain(self.ack)
        self.driver = SyntheticTrace(fixture)
        stop = fixture.worker.stop

        def owned_stop():
            stop()  # A real write to this fixture's pinned control file.
            fixture.write_stat("Z")
            (fixture.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
            (fixture.worker_path / "cgroup.procs").write_text("")
            fixture.child.result = -9

        started = patch.object(fixture.worker, "stop", owned_stop)
        started.start()
        self.addCleanup(started.stop)
        self.outside = fixture.root / "unrelated.control"
        self.outside.write_bytes(b"original unrelated bytes")

    def write_stat(self, state):
        self.fixture.write(
            "stat", f"12345 (owned helper) {state} {os.getpid()} " + "0 " * 17 + "1234567\n"
        )

    def retain(self, ack):
        return ArmedDeadline.retain(
            self.watchdog,
            self.lifeline,
            self.fixture.worker,
            self.fixture.configuration,
            ack,
            started=datetime.now(timezone.utc),
        )

    def stage(self, **changes):
        f = self.fixture
        arguments = dict(
            child=f.child,
            proc=f.proc,
            worker=f.worker,
            aggregate=f.aggregate,
            configuration=f.configuration,
            preparation=self.preparation,
            deadline=self.deadline,
            driver=self.driver,
            cancelled=lambda: False,
        )
        arguments.update(changes)
        return stage_retained_bootstrap(**arguments)

    def test_passive_source_preparation_never_starts_compiles_signals_or_connects(self):
        with (
            patch("subprocess.Popen.__init__", side_effect=AssertionError("no child startup")),
            patch("subprocess.run", side_effect=AssertionError("no compilation")),
            patch("os.kill", side_effect=AssertionError("no signal")),
            patch("socket.socket", side_effect=AssertionError("no network")),
        ):
            plan = prepare_linux_bootstrap(self.fixture.configuration, helper_binary=self.binary)
            audit_linux_bootstrap(self.fixture.configuration, plan)
        self.assertFalse(plan.bootstrap_implemented)
        self.assertFalse(plan.execution_allowed)
        self.assertFalse(plan.spend_authorized)
        self.assertFalse(plan.profile_qualified)
        self.assertIn("actual_pre_instruction_exec_to_group_stop_qualification", plan.unresolved)

    def test_missing_binary_and_complete_hashes_never_supply_readiness(self):
        plan = prepare_linux_bootstrap(self.fixture.configuration)
        self.assertIn("compiled_helper_binary", plan.unresolved)
        self.assertFalse(self.preparation.bootstrap_implemented)
        self.assertIn(
            "independent_timerfd_origin_and_owned_cgroup_kill_readback", self.preparation.unresolved
        )
        self.assertEqual(
            self.preparation.watchdog_fds,
            {"owned_worker_kill": 3, "parent_lifeline": 4, "armed_readiness": 5},
        )

    def test_handshake_queues_real_stop_before_detach_and_retains_exact_admission(self):
        with patch("subprocess.Popen.__init__", side_effect=AssertionError("no process creation")):
            admitted = self.stage()
        admitted.proc.verify_stopped()
        self.assertIs(admitted.child, self.fixture.child)
        self.assertEqual(admitted.receipt.started_monotonic, self.deadline.started_monotonic)
        self.assertFalse(admitted.receipt.execution_allowed)
        self.assertEqual(
            [name for name, _ in self.driver.calls],
            [
                "wait",
                "delivery",
                "options",
                "continue",
                "wait",
                "kernel_filter",
                "queue_pidfd_stop",
                "continue",
                "wait",
                "delivery",
                "detach",
            ],
        )
        self.assertEqual((self.fixture.worker_path / "cgroup.kill").read_bytes(), b"")

    def test_missing_kernel_filter_proof_refuses_before_detach_without_new_grace(self):
        self.driver.verify_storage_filter = Mock(side_effect=OSError(13, "filter unavailable"))
        with self.assertRaisesRegex(BootstrapRefusal, "filter unavailable"):
            self.stage()
        self.assertNotIn("detach", [name for name, _ in self.driver.calls])
        self.assertNotIn("queue_pidfd_stop", [name for name, _ in self.driver.calls])
        self.assertEqual(self.deadline.expires_ns - self.deadline.origin_ns, 5_000_000_000)
        self.assertEqual(self.outside.read_bytes(), b"original unrelated bytes")

    def test_filter_denies_anonymous_storage_and_compat_without_denying_stdio(self):
        # Small independent cBPF evaluator; no kernel loading or C compiler.
        def evaluate(program, arch, number, mmap_flags=0):
            rows = list(struct.iter_unpack("=HBBI", program))
            pc, accumulator = 0, 0
            for _ in range(len(rows)):
                code, yes, no, value = rows[pc]
                if code == 0x20:
                    accumulator = {0: number, 4: arch, 40: mmap_flags}[value]
                elif code == 0x54:
                    accumulator &= value
                elif code in (0x15, 0x35):
                    matches = accumulator == value if code == 0x15 else accumulator >= value
                    pc += yes if matches else no
                elif code == 0x06:
                    return value
                else:
                    raise AssertionError("unexpected filter opcode")
                pc += 1
            raise AssertionError("unterminated filter")

        for machine, arch, anonymous in (
            ("x86_64", 0xC000003E, (319, 29, 30, 447, 425)),
            ("aarch64", 0xC00000B7, (279, 194, 196, 447, 425)),
        ):
            program = payload_storage_filter(machine)
            for number in anonymous:
                self.assertEqual(evaluate(program, arch, number), 0x50001)
            for number in (0x40000000, 0x4000013F, 0xFFFFFFFF):
                self.assertEqual(evaluate(program, arch, number), 0x80000000)
            self.assertEqual(evaluate(program, arch ^ 1, 0), 0x80000000)
            self.assertEqual(evaluate(program, arch, 0), 0x7FFF0000)
            self.assertEqual(evaluate(program, arch, 1), 0x7FFF0000)
            mmap_number = 9 if machine == "x86_64" else 222
            for flags in (1, 3, 0x21, 0x23, 0x4021, 0x80000001):
                self.assertEqual(evaluate(program, arch, mmap_number, flags), 0x50001)
            for flags in (2, 0x22, 0x4022):
                self.assertEqual(evaluate(program, arch, mmap_number, flags), 0x7FFF0000)
        with self.assertRaisesRegex(ValueError, "ABI unavailable"):
            payload_storage_filter("armv7l")

    def test_actual_filter_reader_rejects_missing_short_changed_or_failed_kernel_program(self):
        trace = object.__new__(LinuxTrace)
        expected = payload_storage_filter("aarch64")

        def read(request, pid, index, pointer):
            self.assertEqual((request, pid, index.value), (0x420C, 12345, None))
            if pointer is not None:
                ctypes.memmove(pointer, expected, len(expected))
            return len(expected) // 8

        trace.libc = SimpleNamespace(ptrace=Mock(side_effect=read))
        with patch("crewshal.linux_bootstrap.platform.machine", return_value="aarch64"):
            trace.verify_storage_filter(12345)
            for result in (-1, 0, len(expected) // 8 - 1):
                trace.libc.ptrace = Mock(return_value=result)
                with self.assertRaises((OSError, ValueError)):
                    trace.verify_storage_filter(12345)

            def changed(request, pid, index, pointer):
                if pointer is not None:
                    ctypes.memmove(pointer, bytes(len(expected)), len(expected))
                return len(expected) // 8

            trace.libc.ptrace = Mock(side_effect=changed)
            with self.assertRaisesRegex(ValueError, "instructions differ"):
                trace.verify_storage_filter(12345)

    def test_wrong_exec_event_never_detaches_and_recovers_only_owned_worker(self):
        self.driver.events[1] = (int(signal.SIGTRAP) << 8) | 0x7F
        with self.assertRaises(BootstrapRefusal) as caught:
            self.stage()
        self.assertTrue(caught.exception.recovery.worker_empty)
        self.assertTrue(caught.exception.recovery.child_reaped)
        self.assertNotIn("detach", [name for name, _ in self.driver.calls])
        self.assertEqual(self.outside.read_bytes(), b"original unrelated bytes")

    def test_group_stop_wait_shape_alone_is_not_signal_delivery(self):
        original = self.driver.verify_stop_delivery

        def group_stop(pid, sender):
            if sender == os.getpid():
                raise OSError(22, "synthetic GETSIGINFO group-stop refusal")
            original(pid, sender)

        self.driver.verify_stop_delivery = group_stop
        with self.assertRaises(BootstrapRefusal):
            self.stage()
        self.assertNotIn("detach", [name for name, _ in self.driver.calls])

    def test_fork_wrapper_or_changed_exec_pid_refuses(self):
        self.driver.exec_identity = self.fixture.child.pid + 1
        with self.assertRaisesRegex(BootstrapRefusal, "exec changed"):
            self.stage()

    def test_extra_native_fd_and_wrong_initial_helper_bytes_refuse(self):
        self.fixture.executable.chmod(0o644)
        self.fixture.executable.write_bytes(b"untrusted helper")
        self.fixture.executable.chmod(0o555)
        with self.assertRaisesRegex(BootstrapRefusal, "executable bytes"):
            self.stage()
        self.assertNotIn("continue", [name for name, _ in self.driver.calls])

    def test_extra_fd_after_exec_is_refused_before_pending_stop_handoff(self):
        self.driver.extra_fd = True
        with self.assertRaisesRegex(BootstrapRefusal, "unexpected inherited"):
            self.stage()
        self.assertNotIn("queue_pidfd_stop", [name for name, _ in self.driver.calls])

    def test_wrong_sender_and_bad_initial_tracer_refuse(self):
        self.fixture.status["TracerPid"] = "0"
        self.fixture.write_status()
        with self.assertRaisesRegex(BootstrapRefusal, "traced role"):
            self.stage()

    def test_signal_delivery_sender_refusal_never_detaches(self):
        self.driver.bad_sender = True
        with self.assertRaisesRegex(BootstrapRefusal, "wrong signal sender"):
            self.stage()
        self.assertNotIn("detach", [name for name, _ in self.driver.calls])

    def test_deadline_expiry_during_exec_wait_never_resets_origin(self):
        original = self.driver.wait

        def wait_expired(pid):
            value = original(pid)
            if value[1] == EXEC:
                self.watchdog.result = 0
            return value

        self.driver.wait = wait_expired
        with self.assertRaisesRegex(BootstrapRefusal, "original deadline"):
            self.stage()
        self.assertNotIn("detach", [name for name, _ in self.driver.calls])

    def test_invalid_readiness_clocks_and_reset_intervals_refuse(self):
        for ack in (
            b"READY 1 6000000001\n",
            b"READY nan 5000000000\n",
            b"ready\n",
            b"READY 1 5000000001\nextra",
            b"x" * 1000,
        ):
            with self.subTest(ack=ack[:40]), self.assertRaises(ValueError):
                self.retain(ack)
        with patch(
            "crewshal.linux_bootstrap.time.monotonic_ns", return_value=self.deadline.expires_ns
        ):
            with self.assertRaisesRegex(ValueError, "original deadline"):
                self.retain(self.ack)

    def test_deadline_lifeline_swap_or_configuration_mutation_refuses(self):
        swapped = replace(self.deadline, lifeline=self.fixture.in_writer.fileno())
        with self.assertRaises(ValueError):
            swapped.check(self.fixture.worker, self.fixture.configuration)
        with self.assertRaises(ValueError):
            self.deadline.check(self.fixture.aggregate, self.fixture.configuration)
        changed = self.fixture.configuration.model_copy(deep=True)
        changed.native_environment["TOKEN"] = "synthetic forbidden token"
        with self.assertRaises(ValueError):
            self.deadline.check(self.fixture.worker, changed)

    def test_helper_policy_source_and_configuration_mutation_refuse(self):
        changed = self.preparation.model_copy(deep=True)
        changed.helper_argv[0] = "/bin/sh"
        with self.assertRaisesRegex(ValueError, "current source/configuration"):
            audit_linux_bootstrap(self.fixture.configuration, changed)
        changed = self.preparation.model_copy(deep=True)
        changed.policy.helper_source = digest(b"stale C source")
        with self.assertRaises(ValueError):
            audit_linux_bootstrap(self.fixture.configuration, changed)

    def test_original_five_seconds_and_false_authority_are_closed_contracts(self):
        for change in ({"deadline_seconds": 6}, {"recovery_seconds": 2}, {"native_release": True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                BootstrapPolicy.model_validate({**self.preparation.policy.model_dump(), **change})
        for key in (
            "bootstrap_implemented",
            "execution_allowed",
            "spend_authorized",
            "profile_qualified",
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                BootstrapPreparation.model_validate({**self.preparation.model_dump(), key: True})

    def test_wrong_supplied_owner_never_stops_other_group(self):
        with self.assertRaisesRegex(ValueError, "no recovery authority"):
            self.stage(worker=self.fixture.aggregate)
        self.assertEqual((self.fixture.aggregate_path / "cgroup.kill").read_bytes(), b"")
        self.assertEqual((self.fixture.worker_path / "cgroup.kill").read_bytes(), b"")

    def test_cancellation_and_terminal_helper_exit_preserve_reconciliation(self):
        self.driver.events[0] = 125 << 8
        with self.assertRaises(BootstrapRefusal) as caught:
            self.stage()
        self.assertTrue(caught.exception.recovery.worker_empty)
        self.assertNotIn("options", [name for name, _ in self.driver.calls])

    def test_cancellation_before_handshake_recovers_without_native_continue(self):
        with self.assertRaisesRegex(BootstrapRefusal, "cancelled"):
            self.stage(cancelled=lambda: True)
        self.assertEqual(self.driver.calls, [])

    def test_owned_stop_failure_is_explicit_not_success(self):
        self.fixture.child.result = -9
        (self.fixture.worker_path / "cgroup.events").write_text("populated 0\nfrozen 0")
        (self.fixture.worker_path / "cgroup.procs").write_text("")
        with patch.object(
            self.fixture.worker, "stop", side_effect=OSError("synthetic stop failure")
        ):
            with self.assertRaises(BootstrapRefusal) as caught:
                self.stage(cancelled=lambda: True)
        self.assertTrue(caught.exception.recovery.stop_error)

    def test_native_running_or_nonzero_tracer_cannot_supply_admission(self):
        self.driver.detached_state = "Z"
        with self.assertRaisesRegex(BootstrapRefusal, "detached group-stop"):
            self.stage()

    def test_non_linux_backend_refuses_without_loading_ptrace(self):
        with patch("crewshal.linux_bootstrap.sys.platform", "darwin"):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                LinuxTrace()

    def test_linux_siginfo_reader_requires_stop_delivery_from_exact_sender(self):
        # Exercise the actual decoder with a synthetic syscall buffer, without
        # loading libc/ptrace or turning this into Linux evidence.
        trace = LinuxTrace.__new__(LinuxTrace)

        def fill(request, pid, pointer):
            self.assertEqual(request, 0x4202)
            raw = bytearray(128)
            raw[:4] = int(signal.SIGSTOP).to_bytes(4, sys.byteorder, signed=True)
            raw[16:20] = os.getpid().to_bytes(4, sys.byteorder, signed=True)
            ctypes.memmove(pointer, bytes(raw), len(raw))

        with patch.object(trace, "_call", fill):
            trace.verify_stop_delivery(12345, os.getpid())
            with self.assertRaisesRegex(ValueError, "delivery origin"):
                trace.verify_stop_delivery(12345, os.getpid() + 1)
        with patch.object(trace, "_call", side_effect=OSError(22, "group-stop")):
            with self.assertRaises(OSError):
                trace.verify_stop_delivery(12345, os.getpid())

    def test_linux_driver_queues_stop_only_through_retained_pidfd(self):
        trace = LinuxTrace.__new__(LinuxTrace)
        delivered = []

        def send(descriptor, number, info, flags):
            delivered.append((descriptor, number, info, flags))

        with (
            patch("signal.pidfd_send_signal", send, create=True),
            patch("os.kill", side_effect=AssertionError("no numeric PID signal")),
        ):
            trace.queue_stop(self.fixture.proc.pidfd)
        self.assertEqual(delivered, [(self.fixture.proc.pidfd, signal.SIGSTOP, None, 0)])

    def test_retained_pidfd_exit_refuses_bootstrap(self):
        self.fixture.pid_writer.write(b"synthetic exited child")
        with self.assertRaisesRegex(BootstrapRefusal, "pidfd changed or exited"):
            self.stage()

    def test_bootstrap_source_and_C_bytes_bind_dispatch(self):
        self.assertEqual(len(self.fixture.configuration.source_sha256), 26)
        self.assertEqual(
            self.fixture.configuration.source_sha256["bootstrap_helper.c"],
            digest(
                Path(__file__).parents[2].joinpath("src/crewshal/bootstrap_helper.c").read_bytes()
            ),
        )
