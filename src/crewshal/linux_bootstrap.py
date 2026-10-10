"""Owned exec-stop handoff source for a previously created trusted helper child.

No launcher, authority parser, namespace setup or release entry point is supplied.
The helper and independent watchdog must be created by separately qualified,
authorized trusted setup. Offline drivers never establish Linux capability.
"""

import ctypes
from dataclasses import dataclass
from datetime import datetime
import os
import platform
from pathlib import Path
import re
import select
import signal
import stat
import struct
import subprocess
import sys
import time
from typing import Callable, Literal, Protocol

from crewshal.admission import (
    AdmittedNative,
    NativeAdmissionSpec,
    RetainedProc,
    _aggregate_readback,
    _current_source,
    _fields,
    _read,
    _stat_identity,
    admit_native_process,
)
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_envelope import prepare_linux_envelope
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import _Reader
from crewshal.supervisor import CgroupIdentity, OwnedCgroup

HELPER_PATH = "/bin/crewshal-bootstrap"
TRACEEXEC = 0x10
EXITKILL = 0x100000
EXEC_EVENT = 4


def payload_storage_filter(machine: str) -> bytes:
    """Exact native-ABI kernel program required at the retained exec stop.

    This is control data, not enforcement. Compat/x32 calls cannot select a
    different syscall namespace. Shared mappings (including dev/zero and
    MAP_SHARED|MAP_ANONYMOUS) cannot create unlinked sparse shmem inodes.
    Private mappings, bounded file writes and stdio remain available.
    """
    if machine == "x86_64":
        arch = 0xC000003E
        numbers = (319, 29, 30, 265, 188, 189, 190, 259, 250, 248, 249)
    elif machine == "aarch64":
        arch = 0xC00000B7
        numbers = (279, 194, 196, 37, 5, 6, 7, 33, 219, 217, 218)
    else:
        raise ValueError("qualified native payload filter ABI unavailable")
    instructions = [
        (0x20, 0, 0, 4),
        (0x15, 1, 0, arch),
        (0x06, 0, 0, 0x80000000),
        (0x20, 0, 0, 0),
        (0x35, 0, 1, 0x40000000),
        (0x06, 0, 0, 0x80000000),
    ]
    for number in (*numbers, 447, 425, 463):
        instructions.extend(((0x15, 0, 1, number), (0x06, 0, 0, 0x50001)))
    instructions.extend(
        (
            (0x15, 0, 5, 9 if machine == "x86_64" else 222),
            (0x20, 0, 0, 40),  # seccomp_data.args[3], flags low word
            (0x54, 0, 0, 3),  # MAP_TYPE
            (0x15, 1, 0, 1),  # MAP_SHARED
            (0x15, 0, 1, 3),  # MAP_SHARED_VALIDATE
            (0x06, 0, 0, 0x50001),
        )
    )
    instructions.append((0x06, 0, 0, 0x7FFF0000))
    return b"".join(struct.pack("=HBBI", *row) for row in instructions)


class BootstrapPolicy(Contract):
    schema_version: Literal[1] = 1
    helper_source: Digest
    helper_binary: Digest | None = None
    protocol: Literal["traceme_exec_sigstop_delivery_detach_v1"] = (
        "traceme_exec_sigstop_delivery_detach_v1"
    )
    deadline_seconds: Literal[5] = 5
    recovery_seconds: Literal[1] = 1
    native_release: Literal[False] = False


class BootstrapPreparation(Contract):
    schema_version: Literal[1] = 1
    configuration: Digest
    envelope: Digest
    policy: BootstrapPolicy
    helper_argv: list[str]
    watchdog_argv: list[str]
    watchdog_fds: dict[str, int]
    unresolved: list[str]
    bootstrap_implemented: Literal[False] = False
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False


def bootstrap_policy(helper_binary: str | None = None) -> BootstrapPolicy:
    """Read owned C source as data, never compile or import a historical driver."""
    reader = _Reader(Path(__file__).parent)
    return BootstrapPolicy(
        helper_source=digest(reader.read("bootstrap_helper.c")), helper_binary=helper_binary
    )


def prepare_linux_bootstrap(
    configuration: DispatchConfiguration, *, helper_binary: str | None = None
) -> BootstrapPreparation:
    configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
    envelope = prepare_linux_envelope(configuration)
    policy = bootstrap_policy(helper_binary)
    unresolved = [
        "qualified_namespace_resident_direct_popen_parent_and_role_placement",
        "compiled_helper_library_and_watchdog_identity_readback",
        "independent_timerfd_origin_and_owned_cgroup_kill_readback",
        "actual_pre_instruction_exec_to_group_stop_qualification",
        *envelope.unresolved,
    ]
    if helper_binary is None:
        unresolved.append("compiled_helper_binary")
    if envelope.bindings.bootstrap_policy_sha256 != record_digest(policy):
        unresolved.append("exact_bootstrap_policy_binding")
    return BootstrapPreparation(
        configuration=record_digest(configuration),
        envelope=record_digest(envelope),
        policy=policy,
        helper_argv=[HELPER_PATH, "--exec", *configuration.native_argv],
        watchdog_argv=[HELPER_PATH, "--watchdog"],
        watchdog_fds={"owned_worker_kill": 3, "parent_lifeline": 4, "armed_readiness": 5},
        unresolved=unresolved,
    )


def audit_linux_bootstrap(
    configuration: DispatchConfiguration, preparation: BootstrapPreparation
) -> BootstrapPreparation:
    snapshot = BootstrapPreparation.model_validate_json(preparation.model_dump_json())
    current = prepare_linux_bootstrap(configuration, helper_binary=snapshot.policy.helper_binary)
    if current != snapshot:
        raise ValueError("bootstrap preparation differs from current source/configuration")
    return current


@dataclass(frozen=True)
class ArmedDeadline:
    """Trusted watchdog acknowledgement, never proof of enforcement or authority.

    Launcher must retain and qualify actual helper/timer/cgroup/FD/role identities.
    The lifeline remains open through terminal capture; closing it kills, never
    cancels, the deadline. No disarm operation is supplied.
    """

    watchdog: subprocess.Popen[bytes]
    lifeline: int
    lifeline_identity: tuple[int, int]
    worker: CgroupIdentity
    configuration: Digest
    origin_ns: int
    expires_ns: int
    started: datetime

    @classmethod
    def retain(
        cls,
        watchdog: subprocess.Popen[bytes],
        lifeline: int,
        worker: OwnedCgroup,
        configuration: DispatchConfiguration,
        acknowledgement: bytes,
        *,
        started: datetime,
    ) -> "ArmedDeadline":
        # Caller retains ownership of the lifeline; no hidden duplicate can keep
        # the watchdog alive after the qualified parent loses its descriptor.
        match = re.fullmatch(rb"READY ([1-9][0-9]{0,18}) ([1-9][0-9]{0,18})\n", acknowledgement)
        if match is None:
            raise ValueError("malformed bounded watchdog acknowledgement")
        origin, expires = (int(value) for value in match.groups())
        if expires - origin != 5_000_000_000:
            raise ValueError("watchdog must retain the original five-second deadline")
        info = os.fstat(lifeline)
        retained = cls(
            watchdog,
            lifeline,
            (info.st_dev, info.st_ino),
            CgroupIdentity.model_validate_json(worker.identity.model_dump_json()),
            record_digest(configuration),
            origin,
            expires,
            started,
        )
        retained.check(worker, configuration)
        return retained

    @property
    def started_monotonic(self) -> float:
        return self.origin_ns / 1_000_000_000

    def check(self, worker: OwnedCgroup, configuration: DispatchConfiguration) -> None:
        import fcntl

        now = time.monotonic_ns()
        info = os.fstat(self.lifeline)
        if (
            not isinstance(self.watchdog, subprocess.Popen)
            or self.watchdog.poll() is not None
            or not stat.S_ISFIFO(info.st_mode)
            or fcntl.fcntl(self.lifeline, fcntl.F_GETFL) & os.O_ACCMODE != os.O_WRONLY
            or (info.st_dev, info.st_ino) != self.lifeline_identity
            or worker.identity != self.worker
            or record_digest(configuration) != self.configuration
            or type(self.origin_ns) is not int
            or type(self.expires_ns) is not int
            or self.expires_ns - self.origin_ns != 5_000_000_000
            or not 0 < self.origin_ns <= now < self.expires_ns
            or self.started.tzinfo is None
            or self.started.utcoffset() is None
        ):
            raise ValueError("watchdog binding, retained lifeline or original deadline differs")


class TraceDriver(Protocol):
    """Trusted kernel seam, not a plugin or worker-supplied observation channel."""

    def wait(self, pid: int) -> tuple[int, int]: ...

    def options(self, pid: int) -> None: ...

    def continue_exec(self, pid: int) -> None: ...

    def exec_pid(self, pid: int) -> int: ...

    def verify_storage_filter(self, pid: int) -> None: ...

    def queue_stop(self, pidfd: int) -> None: ...

    def verify_stop_delivery(self, pid: int, sender: int) -> None: ...

    def detach_stopped(self, pid: int) -> None: ...


class LinuxTrace:
    """64-bit Linux ptrace/pidfd source; constructing it grants no startup gate."""

    def __init__(self) -> None:
        if sys.platform != "linux" or ctypes.sizeof(ctypes.c_void_p) != 8:
            raise ValueError("64-bit Linux bootstrap tracing unavailable")
        self.libc: ctypes.CDLL = ctypes.CDLL(None, use_errno=True)
        self.libc.ptrace.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
        self.libc.ptrace.restype = ctypes.c_long

    def _call(self, request: int, pid: int, data: ctypes.c_void_p) -> None:
        if self.libc.ptrace(request, pid, None, data) == -1:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))

    def wait(self, pid: int) -> tuple[int, int]:
        return os.waitpid(pid, os.WNOHANG | os.WUNTRACED)

    def options(self, pid: int) -> None:
        self._call(0x4200, pid, ctypes.c_void_p(TRACEEXEC | EXITKILL))

    def continue_exec(self, pid: int) -> None:
        self._call(7, pid, ctypes.c_void_p())

    def exec_pid(self, pid: int) -> int:
        value = ctypes.c_ulong()
        self._call(0x4201, pid, ctypes.cast(ctypes.byref(value), ctypes.c_void_p))
        return value.value

    def verify_storage_filter(self, pid: int) -> None:
        # PTRACE_SECCOMP_GET_FILTER is available only to an unfiltered privileged
        # tracer and its actual stopped tracee. Failure is retained refusal; no
        # status/hash-only fallback. Index zero is the helper's newest filter.
        expected = payload_storage_filter(platform.machine())
        size = self.libc.ptrace(0x420C, pid, ctypes.c_void_p(0), None)
        if size == -1:
            raise OSError(ctypes.get_errno(), "actual payload filter readback unavailable")
        if size * 8 != len(expected):
            raise ValueError("actual payload kernel filter length differs")
        buffer = ctypes.create_string_buffer(len(expected))
        count = self.libc.ptrace(
            0x420C, pid, ctypes.c_void_p(0), ctypes.cast(buffer, ctypes.c_void_p)
        )
        if count != size or buffer.raw != expected:
            raise ValueError("actual payload kernel filter instructions differ")

    def queue_stop(self, pidfd: int) -> None:
        sender = getattr(signal, "pidfd_send_signal", None)
        if sender is None:
            raise ValueError("Linux pidfd signal delivery unavailable")
        sender(pidfd, signal.SIGSTOP, None, 0)

    def verify_stop_delivery(self, pid: int, sender: int) -> None:
        # Linux 64-bit siginfo_t: 3 ints, alignment pad, then si_pid/si_uid.
        # GETSIGINFO refuses group-stop (EINVAL); require actual SIGSTOP delivery.
        info = (ctypes.c_long * 16)()
        self._call(0x4202, pid, ctypes.cast(info, ctypes.c_void_p))
        raw = ctypes.string_at(info, 128)
        number = int.from_bytes(raw[0:4], sys.byteorder, signed=True)
        code = int.from_bytes(raw[8:12], sys.byteorder, signed=True)
        origin = int.from_bytes(raw[16:20], sys.byteorder, signed=True)
        if number != signal.SIGSTOP or code not in (0, -6) or origin != sender:
            raise ValueError("unexpected SIGSTOP delivery origin")

    def detach_stopped(self, pid: int) -> None:
        self._call(17, pid, ctypes.c_void_p(signal.SIGSTOP))


@dataclass(frozen=True)
class BootstrapRecovery:
    worker_empty: bool
    child_reaped: bool
    stop_error: bool


class BootstrapRefusal(ValueError):
    def __init__(self, reason: str, recovery: BootstrapRecovery):
        super().__init__(reason)
        self.recovery = recovery


def _recover(child: subprocess.Popen[bytes] | None, worker: OwnedCgroup) -> BootstrapRecovery:
    stop_error = False
    try:
        worker.stop()
    except (OSError, ValueError):
        stop_error = True
    until = time.monotonic() + 1
    empty = reaped = False
    while time.monotonic() < until:
        try:
            sample = worker.sample()
            empty = not sample.populated and not sample.direct_pids
            reaped = child is None or child.poll() is not None
        except (OSError, ValueError):
            break
        if empty and reaped:
            break
        time.sleep(0.001)
    return BootstrapRecovery(empty, reaped, stop_error)


def _traced(proc: RetainedProc, child: subprocess.Popen[bytes]) -> None:
    spec = proc.spec
    current = os.fstat(proc.descriptor)
    if (current.st_dev, current.st_ino) != (
        proc.directory.st_dev,
        proc.directory.st_ino,
    ) or select.select([proc.pidfd], [], [], 0)[0]:
        raise ValueError("retained bootstrap proc/pidfd changed or exited")
    if child.pid != spec.pid or spec.parent_pid != os.getpid():
        raise ValueError("bootstrap must retain its own direct Popen child")
    if _stat_identity(_read(proc.descriptor, "stat")) != (
        spec.pid,
        "t",
        spec.parent_pid,
        spec.start_ticks,
    ):
        raise ValueError("bootstrap trace PID/start/parent/state differs")
    fields = _fields(_read(proc.descriptor, "status"))
    expected = {
        "Pid": str(spec.pid),
        "Tgid": str(spec.pid),
        "PPid": str(spec.parent_pid),
        "TracerPid": str(spec.parent_pid),
        "Threads": "1",
        "NoNewPrivs": "1",
        "Uid": "65534 65534 65534 65534",
        "Gid": "65534 65534 65534 65534",
    }
    if any(fields.get(key) != value for key, value in expected.items()):
        raise ValueError("bootstrap traced role or parent differs")
    if fields.get("Groups") not in ("", "65534"):
        raise ValueError("bootstrap supplementary groups differ")
    for name in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"):
        if not re.fullmatch(r"0{16}", fields.get(name, "")):
            raise ValueError("bootstrap capabilities differ")


def stage_retained_bootstrap(
    child: subprocess.Popen[bytes],
    proc: RetainedProc,
    worker: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: DispatchConfiguration,
    preparation: BootstrapPreparation,
    deadline: ArmedDeadline,
    driver: TraceDriver,
    *,
    cancelled: Callable[[], bool],
) -> AdmittedNative:
    """One-shot owned helper-to-native handoff, ending stopped; never a launcher.

    Trusted future setup must establish the actual namespace-resident Popen
    parent, helper placement, watchdog and separate authority gates first.
    Drivers/acknowledgements/digests supplied here do not prove those controls.
    No numeric PID kill, native release, task write, fixture replay or retry.
    """
    # Establish cleanup ownership before entering the recovery region. A wrong
    # supplied group or child must not trigger an unrelated subtree stop.
    if (
        not isinstance(child, subprocess.Popen)
        or child.pid != proc.spec.pid
        or proc.spec.parent_pid != os.getpid()
        or worker.identity != proc.spec.worker
        or aggregate.identity != proc.spec.aggregate
    ):
        raise ValueError("bootstrap retained ownership differs; no recovery authority")
    try:
        configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
        preparation = audit_linux_bootstrap(configuration, preparation)
        policy = preparation.policy
        if (
            policy.helper_binary is None
            or configuration.linux_envelope is None
            or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(policy)
            or proc.spec.configuration != record_digest(configuration)
            or deadline.watchdog.pid == child.pid
        ):
            raise ValueError("exact owned bootstrap helper/policy binding required")
        _current_source(configuration)
        _aggregate_readback(aggregate, worker)

        def check() -> None:
            deadline.check(worker, configuration)
            if cancelled():
                raise ValueError("bootstrap cancelled")

        def wait_stop(expected: int) -> None:
            while True:
                check()
                pid, status = driver.wait(child.pid)
                if pid == 0:
                    time.sleep(0.001)
                    continue
                if pid != child.pid or status != expected:
                    if pid == child.pid and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                        child.returncode = os.waitstatus_to_exitcode(status)
                    raise ValueError("unexpected bootstrap wait PID/event/termination")
                check()
                return

        stop_status = (int(signal.SIGSTOP) << 8) | 0x7F
        exec_status = (EXEC_EVENT << 16) | (int(signal.SIGTRAP) << 8) | 0x7F
        wait_stop(stop_status)
        _traced(proc, child)
        driver.verify_stop_delivery(child.pid, child.pid)
        sample = worker.sample()
        if not sample.populated or sample.direct_pids != [child.pid]:
            raise ValueError("bootstrap worker must contain only retained helper")
        if child.stdin is None or child.stdout is None or child.stderr is None:
            raise ValueError("bootstrap retained stdio required")
        helper_spec = NativeAdmissionSpec.model_validate(
            {**proc.spec.model_dump(), "executable_sha256": policy.helper_binary}
        )
        helper_proc = RetainedProc(proc.descriptor, proc.pidfd, helper_spec)
        try:
            helper_configuration = configuration.model_copy(deep=True)
            helper_configuration.native_argv = preparation.helper_argv.copy()
            helper_proc.read_configuration(helper_configuration)
            helper_proc.verify_pipes(
                child.stdin.fileno(), child.stdout.fileno(), child.stderr.fileno()
            )
        finally:
            helper_proc.close()
        check()
        driver.options(child.pid)
        driver.continue_exec(child.pid)  # Only trusted helper code may run here.
        wait_stop(exec_status)
        if driver.exec_pid(child.pid) != child.pid:
            raise ValueError("bootstrap exec changed retained thread/PID identity")
        _traced(proc, child)
        driver.verify_storage_filter(child.pid)
        proc.read_configuration(configuration)
        proc.verify_pipes(child.stdin.fileno(), child.stdout.fileno(), child.stderr.fileno())
        check()
        # Detach(SIGSTOP) at an exec EVENT is insufficient. Queue a real signal
        # while held, resume to its delivery stop, verify it, then inject/detach.
        driver.queue_stop(proc.pidfd)
        driver.continue_exec(child.pid)
        wait_stop(stop_status)
        _traced(proc, child)
        driver.verify_stop_delivery(child.pid, os.getpid())
        check()
        driver.detach_stopped(child.pid)
        # Scheduling may delay the actual group-stop. Never turn traced state
        # into evidence; wait for exact T/zero-tracer under the original deadline.
        while True:
            check()
            fields = _fields(_read(proc.descriptor, "status"))
            state = _stat_identity(_read(proc.descriptor, "stat"))[1]
            if state == "T" and fields.get("TracerPid") == "0":
                break
            if state not in ("t", "R", "S", "T"):
                raise ValueError("native failed to reach detached group-stop")
            time.sleep(0.001)
        admitted = admit_native_process(
            child,
            proc,
            worker,
            aggregate,
            configuration,
            started=deadline.started,
            started_monotonic=deadline.started_monotonic,
        )
        check()
        return admitted
    except BaseException as error:
        recovery = _recover(child, worker)
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        raise BootstrapRefusal(str(error), recovery) from error
