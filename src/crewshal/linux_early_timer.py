"""Pin the original independent batch timer before either charged build.

These source routines require separate operational approval and Linux evidence.
They cannot authorize compilation, policy loading, authentication, or reuse.
"""

import ctypes
import fcntl
import hashlib
import os
from pathlib import PurePosixPath
import re
import signal
import stat
import struct
import subprocess
import time
from typing import NoReturn
from weakref import WeakKeyDictionary

from pydantic import model_validator

from crewshal.admission import _wait_ready
from crewshal.admission import _aggregate_readback, _fields, _read, _stat_identity
from crewshal.contracts import Digest, record_digest
from crewshal.linux_installed import _mappings
from crewshal.linux_inventory import _metadata
from crewshal.linux_parent import (
    RetainedTrustedTask,
    TrustedTaskSpec,
    _attach,
    _image,
    _namespaces,
    _proc_root,
)
from crewshal.linux_setup import (
    LANE_IDS,
    LANE_ROLES,
    BatchTimerRefusal,
    OwnedBatchTimer,
    OwnedStorageReservation,
    RetainedLaneSetup,
    _observer_placement,
    _role_controls,
    _seals,
)
from crewshal.model import Contract, digest
from crewshal.supervisor import OwnedCgroup, _counters

GROUP_START = 100
LIFELINE_FD = 113
SOURCE_FD = 116
TIMER_FD = 123

# The isolated program loads its reviewed runtime before the initial trace stop.
# Tracer exit releases this SIGTRAP stop. No EXITKILL option is installed.
# The observer retains all thirteen original groups before process creation.
EARLY_TIMER_SOURCE = b"""import ctypes, fcntl, os, select, signal, struct, sys, time
libc = ctypes.CDLL(None, use_errno=True)
class Timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]
class Itimerspec(ctypes.Structure):
    _fields_ = [("interval", Timespec), ("value", Timespec)]
inputs = [int(value) for value in sys.argv[1:]]
if len(inputs) != 17:
    os._exit(125)
parent = inputs.pop()
if parent <= 1:
    os._exit(125)
copies = [fcntl.fcntl(fd, fcntl.F_DUPFD_CLOEXEC, 200) for fd in inputs]
source = os.open(__file__, os.O_RDONLY | os.O_CLOEXEC)
source_copy = fcntl.fcntl(source, fcntl.F_DUPFD_CLOEXEC, 200)
for number, fd in enumerate(copies, 100):
    os.dup2(fd, number, inheritable=False)
os.dup2(source_copy, 116, inheritable=False)
origin_raw = os.pread(115, 9, 0)
if len(origin_raw) != 8:
    os._exit(125)
origin = struct.unpack("=Q", origin_raw)[0]
cutoff, end = origin + 570000000000, origin + 600000000000
if not 0 < origin <= time.monotonic_ns() < cutoff:
    os._exit(125)
timer = libc.timerfd_create(1, os.O_CLOEXEC | os.O_NONBLOCK)
if timer < 0:
    os._exit(125)
os.dup2(timer, 123, inheritable=False)
limit = Itimerspec(Timespec(0, 0), Timespec(cutoff // 1000000000, cutoff % 1000000000))
if libc.timerfd_settime(123, 1, ctypes.byref(limit), None) != 0:
    os._exit(125)
signal.signal(signal.SIGPIPE, signal.SIG_IGN)
signal.signal(signal.SIGTRAP, signal.SIG_IGN)
if os.getppid() == parent and libc.ptrace(0, 0, None, None) != 0:
    os._exit(125)
ready = ("BATCH %d %d %d\\n" % (origin, cutoff, end)).encode()
if os.write(114, ready) != len(ready):
    os._exit(125)
keep = {0, 1, 2, *range(100, 114), 116, 123}
for text in os.listdir("/proc/self/fd"):
    fd = int(text)
    if fd not in keep:
        try:
            os.close(fd)
        except OSError:
            pass
if os.getppid() == parent:
    os.kill(os.getpid(), signal.SIGTRAP)
result = 0
try:
    while True:
        ready, _, _ = select.select([123, 113], [], [])
        if 123 in ready or 113 in ready:
            break
except BaseException:
    result = 125
def empty(number):
    fd = os.open("cgroup.events", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=number)
    try:
        raw = os.read(fd, 4097)
        return len(raw) <= 4096 and b"populated 0\\n" in raw.splitlines(keepends=True)
    finally:
        os.close(fd)
def stop(number):
    global result
    try:
        if empty(number):
            return
        fd = os.open("cgroup.kill", os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=number)
        try:
            if os.write(fd, b"1") != 1:
                result = 125
        finally:
            os.close(fd)
    except BaseException:
        result = 125
for lane in range(3):
    stop(102 + 4 * lane)
for lane in range(3):
    stop(103 + 4 * lane)
stop(112)
try:
    payload_empty = all(empty(102 + 4 * lane) and empty(103 + 4 * lane) for lane in range(3))
except BaseException:
    payload_empty = False
if payload_empty:
    for lane in range(3):
        stop(101 + 4 * lane)
        stop(100 + 4 * lane)
else:
    result = 125
os._exit(result)
"""


class FrozenEarlyTimerRuntime(Contract):
    interpreter: str
    interpreter_sha256: Digest
    files: dict[str, Digest]
    source_sha256: Digest = digest(EARLY_TIMER_SOURCE)

    @model_validator(mode="after")
    def exact_runtime(self) -> "FrozenEarlyTimerRuntime":
        if (
            not 1 <= len(self.files) <= 512
            or self.files.get(self.interpreter) != self.interpreter_sha256
            or self.source_sha256 != digest(EARLY_TIMER_SOURCE)
            or any(
                not name.startswith("/")
                or str(PurePosixPath(name)) != name
                or any(part in {".", ".."} for part in name.split("/")[1:])
                for name in self.files
            )
        ):
            raise ValueError("early timer requires its exact reviewed isolated runtime")
        return self


_RUNTIMES: WeakKeyDictionary[OwnedBatchTimer, "RetainedEarlyTimerRuntime"] = WeakKeyDictionary()


class RetainedEarlyTimerRuntime:
    """Retain every runtime FD and actual mapped inode through failure."""

    timer: OwnedBatchTimer
    plan: FrozenEarlyTimerRuntime
    _payload: str
    handles: dict[str, int]
    metadata: dict[str, tuple[int, ...]]
    mapped_handles: dict[str, tuple[int, tuple[int, ...]]]
    _files_snapshot: tuple[tuple[str, int, tuple[int, ...], Digest], ...]

    def __init__(self) -> None:
        raise ValueError("early runtime requires original timer acquisition")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original early runtime cannot be copied or exported")

    def verify(self) -> None:
        timer = self.timer
        if (
            type(timer) is not OwnedBatchTimer
            or _RUNTIMES.get(timer) is not self
            or getattr(timer, "_early_runtime", None) is not self
            or self.plan.model_dump_json() != self._payload
            or tuple(self.handles) != tuple(self.plan.files)
            or self._files_snapshot
            != tuple(
                (name, self.handles[name], self.metadata[name], self.plan.files[name])
                for name in self.plan.files
            )
        ):
            raise ValueError("original isolated timer runtime changed")
        for name, handle in self.handles.items():
            _runtime_protection(handle)
            if _metadata(os.fstat(handle)) != self.metadata[name]:
                raise ValueError("original isolated timer runtime inode changed")
        for handle, metadata in self.mapped_handles.values():
            _runtime_protection(handle)
            if _metadata(os.fstat(handle)) != metadata:
                raise ValueError("original timer mapped inode changed")


def _runtime_protection(handle: int) -> os.stat_result:
    info = os.fstat(handle)
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_uid != 0
        or info.st_gid != 0
        or info.st_mode & 0o7022
        or info.st_nlink != 1
        or not 0 <= info.st_size <= 134217728
        or fcntl.fcntl(handle, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
        or not os.fstatvfs(handle).f_flag & os.ST_RDONLY
    ):
        raise ValueError("early timer runtime requires readonly original protected files")
    return info


def _verify_runtime_file(handle: int, expected: Digest, cutoff_ns: int) -> None:
    info = _runtime_protection(handle)
    if time.monotonic_ns() >= cutoff_ns:
        raise ValueError("original early timer deadline exhausted")
    sha = hashlib.sha256()
    offset = 0
    while offset < info.st_size:
        if time.monotonic_ns() >= cutoff_ns:
            raise ValueError("original early timer deadline exhausted")
        chunk = os.pread(handle, min(65536, info.st_size - offset), offset)
        if not chunk:
            raise ValueError("original early timer runtime read incomplete")
        sha.update(chunk)
        offset += len(chunk)
    if sha.hexdigest() != expected or _metadata(os.fstat(handle)) != _metadata(info):
        raise ValueError("original early timer runtime bytes changed")


def verify_early_timer_roles(timer: OwnedBatchTimer) -> None:
    groups = timer._early_roles
    if (
        type(groups) is not tuple
        or len(groups) != 13
        or groups is not timer._early_role_owners
        or timer._early_inputs is not timer._early_mapping
        or tuple(timer._early_inputs) != LANE_IDS
        or any(tuple(roles) != LANE_ROLES for roles in timer._early_inputs.values())
        or groups[:-1]
        != tuple(timer._early_inputs[lane][role] for lane in LANE_IDS for role in LANE_ROLES)
        or timer._early_handles != tuple(group.descriptor for group in groups)
        or timer._early_configuration != timer.reservation.observer.spec.configuration
        or len({(g.identity.device, g.identity.inode) for g in groups}) != 13
    ):
        raise ValueError("original early timer role pointers changed")
    for number, group in enumerate(groups):
        if type(group) is not OwnedCgroup or group is timer.reservation.observer_group:
            raise ValueError("early timer cannot control an observer or replacement role")
        _aggregate_readback(timer.reservation.aggregate, group)
        if number < 12:
            lane, role = LANE_IDS[number // 4], LANE_ROLES[number % 4]
            if PurePosixPath(group.identity.relative_path).name != role + "--" + lane:
                raise ValueError("early timer original lane role name differs")
            if role in {"setup", "supervisor"}:
                _role_controls(group)
            else:
                sample = group.sample()
                if any(sample.memory_events.values()) or any(sample.pids_events.values()):
                    raise ValueError("early timer original payload role has refusal history")
        else:
            if PurePosixPath(group.identity.relative_path).name != "broker":
                raise ValueError("early timer requires the one original broker")
            if (
                group._read("memory.max") != "67108864"
                or group._read("pids.max") != "16"
                or group._read("memory.swap.max") != "0"
                or group._read("cpu.max") != "100000 100000"
                or group._read("cgroup.type") != "domain"
                or any(_counters(group._read("memory.events"), {"max", "oom", "oom_kill"}).values())
                or any(_counters(group._read("pids.events"), {"max"}).values())
            ):
                raise ValueError("early timer original broker controls differ")
    if timer.lanes is not None:
        if (
            timer.lanes is not timer._lane_owners
            or timer.reservation._lane_contexts is not timer.lanes
        ):
            raise ValueError("early timer original lane contexts changed")
        for context in timer.lanes:
            # Reservation derivation verifies this timer. Check lane custody
            # without calling the same derivation again.
            context._verify_role_handles()


def bind_early_timer_lanes(
    timer: OwnedBatchTimer,
    lanes: tuple[RetainedLaneSetup, ...],
    groups: dict[str, dict[str, OwnedCgroup]],
) -> None:
    if (
        type(timer) is not OwnedBatchTimer
        or _RUNTIMES.get(timer) is not getattr(timer, "_early_runtime", None)
        or getattr(timer, "_early_runtime", None) is None
        or timer.lanes is not None
        or timer._early_inputs is not groups
        or timer._early_roles is None
        or timer.reservation._lane_contexts is not lanes
        or len(lanes) != 3
        or tuple(group for context in lanes for group in context._groups) != timer._early_roles[:-1]
    ):
        raise ValueError("early timer requires one original final lane binding")
    # Final configuration verification includes the registered build derivation.
    from crewshal.linux_charged_build import RetainedBuildDerivation, _DERIVATIONS

    derivation = _DERIVATIONS.get(timer.reservation)
    if (
        type(derivation) is not RetainedBuildDerivation
        or derivation is not getattr(timer.reservation, "_build_derivation", None)
        or derivation.reservation is not timer.reservation
        or derivation.final_configuration is not timer.reservation._configuration
    ):
        raise ValueError("early timer final lanes require the registered original build derivation")
    derivation.verify()
    timer.reservation._verify_identity()
    timer.lanes = timer._lane_owners = lanes
    verify_early_timer_roles(timer)


def _timerfd_deadline(timer: OwnedBatchTimer) -> None:
    assert timer.task is not None
    before = time.monotonic_ns()
    fields = _fields(_read(timer.task.descriptor, f"fdinfo/{TIMER_FD}"))
    after = time.monotonic_ns()
    match = re.fullmatch(r"\(([0-9]+), ([0-9]+)\)", fields.get("it_value", ""))
    if match is None:
        raise ValueError("early timer effective deadline is malformed")
    seconds, nanos = map(int, match.groups())
    remaining = seconds * 1_000_000_000 + nanos
    if (
        nanos >= 1_000_000_000
        or remaining <= 0
        or fields.get("clockid") != "1"
        or fields.get("ticks") != "0"
        or fields.get("settime flags") != "01"
        or fields.get("it_interval") != "(0, 0)"
        or int(fields.get("flags", "0"), 8) & (os.O_ACCMODE | os.O_NONBLOCK | os.O_CLOEXEC)
        != os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC
        or not before + remaining <= timer.cutoff_ns <= after + remaining
    ):
        raise ValueError("early timer kernel deadline differs from the original origin")


def verify_early_timer_readback(timer: OwnedBatchTimer) -> None:
    runtime = _RUNTIMES.get(timer)
    if runtime is None:
        raise ValueError("early timer requires original live runtime custody")
    runtime.verify()
    assert timer.task is not None and timer._early_roles is not None
    directory = os.open(
        "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=timer.task.descriptor
    )
    try:
        expected = {"0", "1", "2", str(LIFELINE_FD), str(SOURCE_FD), str(TIMER_FD)} | {
            str(number) for number in range(GROUP_START, GROUP_START + 13)
        }
        if set(os.listdir(directory)) != expected:
            raise ValueError("early timer actual descriptor inventory differs")
        for number, group in enumerate(timer._early_roles, GROUP_START):
            info = os.stat(str(number), dir_fd=directory)
            flags = int(_fields(_read(timer.task.descriptor, f"fdinfo/{number}"))["flags"], 8)
            if (info.st_dev, info.st_ino) != (
                group.identity.device,
                group.identity.inode,
            ) or flags & os.O_ACCMODE != os.O_RDONLY:
                raise ValueError("early timer actual original group FD differs")
        info = os.fstat(timer.lifeline)
        if (
            os.readlink(str(LIFELINE_FD), dir_fd=directory) != f"pipe:[{info.st_ino}]"
            or int(_fields(_read(timer.task.descriptor, f"fdinfo/{LIFELINE_FD}"))["flags"], 8)
            & (os.O_ACCMODE | os.O_NONBLOCK)
            != os.O_RDONLY
            or os.readlink(str(TIMER_FD), dir_fd=directory) != "anon_inode:[timerfd]"
            or _metadata(os.stat(str(SOURCE_FD), dir_fd=directory))
            != _metadata(os.fstat(timer._early_source))
            or int(_fields(_read(timer.task.descriptor, f"fdinfo/{SOURCE_FD}"))["flags"], 8)
            & (os.O_ACCMODE | os.O_CLOEXEC)
            != os.O_RDONLY | os.O_CLOEXEC
        ):
            raise ValueError("early timer actual source, timer, or lifeline differs")
        for stdio_number in ("0", "1", "2"):
            info = os.stat(stdio_number, dir_fd=directory)
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(1, 3):
                raise ValueError("early timer stdio must use the actual null device")
    finally:
        os.close(directory)
    add, get, seals = _seals()
    del add
    if (
        fcntl.fcntl(timer._early_source, get) != seals
        or fcntl.fcntl(timer._early_source, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
        or os.pread(timer._early_source, len(EARLY_TIMER_SOURCE) + 1, 0) != EARLY_TIMER_SOURCE
    ):
        raise ValueError("early timer source bytes or seals differ")
    rows = _mappings(_read(timer.task.descriptor, "maps", 262144))
    actual_files = set()
    for address, (name, device, inode, _, _) in rows.items():
        handle = runtime.handles.get(name)
        if handle is None or (os.fstat(handle).st_dev, os.fstat(handle).st_ino) != (device, inode):
            raise ValueError("early timer actual mapped image is outside the frozen runtime")
        info = os.stat("map_files/" + address, dir_fd=timer.task.descriptor)
        if _metadata(info) != runtime.metadata[name]:
            raise ValueError("early timer actual mapped inode differs")
        if name not in runtime.mapped_handles:
            mapped = os.open(
                "map_files/" + address, os.O_RDONLY | os.O_CLOEXEC, dir_fd=timer.task.descriptor
            )
            runtime.mapped_handles[name] = (mapped, _metadata(os.fstat(mapped)))
            _verify_runtime_file(mapped, runtime.plan.files[name], timer.cutoff_ns)
        actual_files.add(name)
    if runtime.plan.interpreter not in actual_files:
        raise ValueError("early timer interpreter mapping was not observed")
    _timerfd_deadline(timer)


def _sealed(raw: bytes, name: str, retained: dict[str, int]) -> int:
    add, get, seals = _seals()
    write = getattr(os, "memfd_create")(
        name, getattr(os, "MFD_CLOEXEC") | getattr(os, "MFD_ALLOW_SEALING")
    )
    retained[name + ":writer"] = write
    if os.write(write, raw) != len(raw):
        raise ValueError("early timer sealed input write is incomplete")
    fcntl.fcntl(write, add, seals)
    if fcntl.fcntl(write, get) != seals:
        raise ValueError("early timer sealed input readback differs")
    reading = os.open(f"/proc/self/fd/{write}", os.O_RDONLY | os.O_CLOEXEC)
    retained[name + ":read"] = reading
    # The original sealed inode remains pinned through its readonly FD.
    os.close(write)
    retained[name + ":writer"] = -1
    return reading


def _stopped_task(timer: OwnedBatchTimer) -> None:
    assert timer.task is not None
    task, observer = timer.task, timer.reservation.observer
    task.verify_handles()
    pid, state, parent, ticks = _stat_identity(_read(task.descriptor, "stat"))
    fields = _fields(_read(task.descriptor, "status"))
    expected = {
        "Pid": str(task.spec.pid),
        "Tgid": str(task.spec.pid),
        "PPid": str(observer.spec.pid),
        "TracerPid": str(observer.spec.pid),
        "Threads": "1",
        "NoNewPrivs": "1",
        "Uid": "0 0 0 0",
        "Gid": "0 0 0 0",
        "Groups": "",
        "CapInh": "0000000000000000",
        "CapAmb": "0000000000000000",
        "CapPrm": observer.spec.capabilities,
        "CapEff": observer.spec.capabilities,
        "CapBnd": observer.spec.capabilities,
    }
    if (
        (pid, parent, ticks) != (task.spec.pid, task.spec.parent_pid, task.spec.start_ticks)
        or state != "t"
        or _wait_ready([task.pidfd], [], [], 0)[0]
        or any(fields.get(name) != value for name, value in expected.items())
        or _read(task.descriptor, "environ") != b""
        or _read(task.descriptor, "cmdline")
        != b"\0".join(v.encode() for v in task.spec.argv) + b"\0"
        or _read(task.descriptor, "cgroup").decode().strip()
        != "0::/" + observer.spec.cgroup.relative_path
        or os.readlink("cwd", dir_fd=task.descriptor) != "/"
    ):
        raise ValueError("early timer independent stopped process readback differs")
    _namespaces(task.descriptor, observer.spec.namespaces)
    _image(task.descriptor, task.spec.executable)
    task.verify_handles()


def create_owned_early_batch_timer(
    reservation: OwnedStorageReservation,
    groups: dict[str, dict[str, OwnedCgroup]],
    broker: OwnedCgroup,
    runtime: FrozenEarlyTimerRuntime,
) -> OwnedBatchTimer:
    """Create one timer after the full charge and before compiler effects."""
    if (
        type(reservation) is not OwnedStorageReservation
        or type(runtime) is not FrozenEarlyTimerRuntime
    ):
        raise ValueError("early timer requires original reservation and frozen runtime")
    if hasattr(reservation, "_early_timer_attempted"):
        raise ValueError("original early timer attempt consumed; no retry")
    setattr(reservation, "_early_timer_attempted", True)
    from crewshal.durable import LiveStorageInstallationClaim

    if type(reservation.capacity_claim) is not LiveStorageInstallationClaim:
        raise ValueError("early timer requires the original full installation charge")
    reservation.verify()
    if getattr(reservation.observer, "_setup_started", False) or hasattr(
        reservation, "_compiler_storage"
    ):
        raise ValueError("early timer must precede every compiler effect")
    first = groups[LANE_IDS[0]]
    timer = OwnedBatchTimer(
        reservation,
        first["setup"],
        first["supervisor"],
        first["worker"],
        validator=first["validator"],
        early_groups=groups,
        early_broker=broker,
    )
    retained = object.__new__(RetainedEarlyTimerRuntime)
    retained.timer = timer
    retained.plan = FrozenEarlyTimerRuntime.model_validate_json(runtime.model_dump_json())
    retained._payload = retained.plan.model_dump_json()
    retained.handles = {}
    retained.metadata = {}
    retained.mapped_handles = {}
    retained._files_snapshot = ()
    _RUNTIMES[timer] = retained
    timer._early_runtime = retained
    timer._early_source = timer._early_origin = -1
    timer._early_transport = {}
    deadline = min(
        time.monotonic() + 30, reservation.batch_started + 120, reservation.batch_started + 570
    )
    try:
        verify_early_timer_roles(timer)
        assert timer._early_roles is not None
        _observer_placement(
            reservation.observer,
            reservation.observer_group,
            reservation.aggregate,
            timer._early_roles,
        )
        if any(group._read("cgroup.procs") for group in timer._early_roles):
            raise ValueError("early timer requires empty original operational roles")
        for name, expected in retained.plan.files.items():
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            retained.handles[name] = fd
            _verify_runtime_file(fd, expected, int(deadline * 1_000_000_000))
            retained.metadata[name] = _metadata(os.fstat(fd))
        retained._files_snapshot = tuple(
            (name, retained.handles[name], retained.metadata[name], retained.plan.files[name])
            for name in retained.plan.files
        )
        timer.helper = retained.handles[retained.plan.interpreter]
        info = os.fstat(timer.helper)
        if not info.st_mode & 0o111:
            raise ValueError("early timer interpreter is not executable")
        timer._helper_identity = (timer.helper, info.st_dev, info.st_ino)
        timer._early_source = _sealed(
            EARLY_TIMER_SOURCE, "crewshal-original-early-timer", timer._early_transport
        )
        timer._early_origin = _sealed(
            struct.pack("=Q", timer.origin_ns), "crewshal-original-origin", timer._early_transport
        )
        reading, timer.lifeline = getattr(os, "pipe2")(os.O_CLOEXEC)
        timer._early_transport["lifeline-read"] = reading
        info = os.fstat(timer.lifeline)
        timer.lifeline_identity = (info.st_dev, info.st_ino)
        ready_read, ready_write = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        timer._early_transport.update({"ready-read": ready_read, "ready-write": ready_write})
        inputs = (*timer._early_handles, reading, ready_write, timer._early_origin)
        argv = [
            retained.plan.interpreter,
            "-I",
            "-S",
            "-B",
            f"/proc/self/fd/{timer._early_source}",
            *map(str, inputs),
            str(reservation.observer.spec.pid),
        ]
        timer.process = subprocess.Popen(
            argv,
            executable=f"/proc/self/fd/{timer.helper}",
            pass_fds=(*inputs, timer.helper, timer._early_source),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={},
            cwd="/",
            close_fds=True,
        )
        os.close(ready_write)
        timer._early_transport["ready-write"] = -1
        os.close(reading)
        timer._early_transport["lifeline-read"] = -1
        root = _proc_root(reservation.observer.spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, timer.process.pid)
            pid, _, parent, ticks = _stat_identity(_read(descriptor, "stat"))
            spec = TrustedTaskSpec(
                configuration=reservation.configuration,
                pid=pid,
                parent_pid=parent,
                start_ticks=ticks,
                boot_id=reservation.observer.spec.boot_id,
                cgroup=reservation.observer_group.identity,
                namespaces=reservation.observer.spec.namespaces,
                executable=retained.plan.interpreter_sha256,
                argv=argv,
                environment={},
                capabilities=reservation.observer.spec.capabilities,
                placement="outer_observer",
                cwd="/",
            )
            timer.task = RetainedTrustedTask(descriptor, pidfd, spec)
            timer._birth = (timer.task, timer.process)
            timer._task_digest = record_digest(timer.task.spec)
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)
        raw = bytearray()
        while True:
            if time.monotonic() >= deadline or _wait_ready([timer.task.pidfd], [], [], 0)[0]:
                raise ValueError("original early timer startup deadline exhausted")
            if _wait_ready([ready_read], [], [], min(0.001, deadline - time.monotonic()))[0]:
                chunk = os.read(ready_read, 129)
                raw.extend(chunk)
                if len(raw) > 128:
                    raise ValueError("early timer readiness exceeds its fixed bound")
                if not chunk:
                    break
        if raw != f"BATCH {timer.origin_ns} {timer.cutoff_ns} {timer.end_ns}\n".encode():
            raise ValueError("early timer readiness differs from the original origin")
        assert timer.task is not None
        while _stat_identity(_read(timer.task.descriptor, "stat"))[1] != "t":
            if time.monotonic() >= deadline:
                raise ValueError("early timer initial trace stop was not observed")
        waited, status = os.waitpid(timer.process.pid, os.WNOHANG | os.WUNTRACED)
        if (
            waited != timer.process.pid
            or not os.WIFSTOPPED(status)
            or os.WSTOPSIG(status) != signal.SIGTRAP
        ):
            raise ValueError("early timer original trace stop wait differs")
        _stopped_task(timer)
        verify_early_timer_readback(timer)
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.ptrace(17, timer.process.pid, None, None) != 0:
            raise ValueError("early timer original trace release failed")
        timer.complete = True
        reservation.verify_operational()
        return timer
    except BaseException as error:
        timer.failed = True
        raise BatchTimerRefusal(str(error), timer) from error
