"""Finite credential-free validator custody, exec admission and supervision.

Source only; no receipt authorizes startup or release. The qualified namespace
parent must create the direct child in its distinct validator role and view.
Original outer installation/SQLite ownership is never imported into this module.
"""

from datetime import datetime, timezone
import fcntl
import hashlib
import math
import os
from pathlib import PurePosixPath
import re
import select
import signal
import stat
import subprocess
import time
from typing import Annotated, Callable, Literal, NoReturn, Self

from pydantic import Field, model_validator

from crewshal.admission import (
    AdmittedNative,
    NamespaceIdentity,
    _aggregate_readback,
    _current_source,
    _fields,
    _read,
    _stat_identity,
    _verify_file_growth_limit,
)
from crewshal.candidate import FrozenCandidate, _scan_fd
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_bootstrap import (
    ArmedDeadline,
    BootstrapPreparation,
    EXEC_EVENT,
    TraceDriver,
    audit_linux_bootstrap,
)
from crewshal.linux_inventory import RetainedParentInventory
from crewshal.linux_parent import (
    ObservedWatchdog,
    RetainedTrustedTask,
    TrustedTaskSpec,
    _attach,
    _proc_root,
)
from crewshal.linux_production import _filesystem_magic
from crewshal.linux_setup import (
    CAPABILITIES,
    InheritedControls,
    OwnedWatchdogLifetime,
    _role_controls,
    _terminal_task_exited,
)
from crewshal.model import Contract
from crewshal.supervisor import (
    CapturedProcess,
    CgroupIdentity,
    OwnedCgroup,
    capture_attached_process,
)

VALIDATOR_UID = 65531
VALIDATOR_CWD = "/candidate/owned"


def _identity(descriptor: int) -> tuple[int, int]:
    info = os.fstat(descriptor)
    return info.st_dev, info.st_ino


class ValidatorAdmissionSpec(Contract):
    """Separate validator identity; the unchanged native role remains 65534."""

    configuration: Digest
    pid: Annotated[int, Field(gt=0)]
    parent_pid: Annotated[int, Field(gt=0)]
    start_ticks: Annotated[int, Field(gt=0)]
    boot_id: str = Field(pattern=r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    validator: CgroupIdentity
    aggregate: CgroupIdentity
    namespaces: dict[str, NamespaceIdentity]
    executable_sha256: Digest
    uid: Literal[65531] = 65531
    gid: Literal[65531] = 65531
    execution_allowed: Literal[False] = False
    profile_qualified: Literal[False] = False

    @model_validator(mode="after")
    def topology(self) -> Self:
        if (
            PurePosixPath(self.validator.relative_path).parent
            != PurePosixPath(self.aggregate.relative_path)
            or PurePosixPath(self.validator.relative_path).name != "validator"
            or self.validator.device != self.aggregate.device
            or self.validator.inode == self.aggregate.inode
            or self.pid == self.parent_pid
            or set(self.namespaces) != {"mnt", "net", "pid", "user"}
        ):
            raise ValueError("validator requires distinct exact retained role identities")
        return self


class ValidatorProcRefusal(ValueError):
    def __init__(self, reason: str, retained: "RetainedValidatorProc"):
        super().__init__(reason)
        self.retained = retained
        self.resources_reusable = False


class RetainedValidatorProc:
    """Actual proc/pidfd custody, with a dedicated validator role contract."""

    def __init__(self, descriptor: int, pidfd: int, spec: ValidatorAdmissionSpec):
        self.spec = ValidatorAdmissionSpec.model_validate_json(spec.model_dump_json())
        self._spec_digest = record_digest(self.spec)
        self.descriptor = self.pidfd = -1
        try:
            self.descriptor = os.dup(descriptor)
            self.pidfd = os.dup(pidfd)
            self.directory = _identity(self.descriptor)
            self.pidfd_identity = _identity(self.pidfd)
        except BaseException as error:
            raise ValidatorProcRefusal(str(error), self) from error

    def close(self) -> None:
        # Only ordinary fixture/caller duplicates; no storage closure inference.
        for name in ("descriptor", "pidfd"):
            descriptor = getattr(self, name)
            if descriptor >= 0:
                os.close(descriptor)
                setattr(self, name, -1)

    def verify_handles(self) -> None:
        if (
            record_digest(self.spec) != self._spec_digest
            or _identity(self.descriptor) != self.directory
            or _identity(self.pidfd) != self.pidfd_identity
        ):
            raise ValueError("retained validator proc/pidfd descriptor changed")

    def verify_exited(self) -> None:
        self.verify_handles()
        if not select.select([self.pidfd], [], [], 0)[0]:
            raise ValueError("retained validator pidfd exit unobserved")
        self.verify_handles()

    def verify_state(self, *, traced: bool) -> None:
        self.verify_handles()
        spec = self.spec
        if select.select([self.pidfd], [], [], 0)[0] or _stat_identity(
            _read(self.descriptor, "stat")
        ) != (spec.pid, "t" if traced else "T", spec.parent_pid, spec.start_ticks):
            raise ValueError("validator PID/start/parent/stopped state differs")
        fields = _fields(_read(self.descriptor, "status"))
        expected = {
            "Pid": str(spec.pid),
            "Tgid": str(spec.pid),
            "PPid": str(spec.parent_pid),
            "TracerPid": str(spec.parent_pid) if traced else "0",
            "Threads": "1",
            "NoNewPrivs": "1",
            "Uid": "65531 65531 65531 65531",
            "Gid": "65531 65531 65531 65531",
        }
        if any(fields.get(key) != value for key, value in expected.items()) or fields.get(
            "Groups"
        ) not in ("", "65531"):
            raise ValueError("validator credential-free role or trace identity differs")
        if any(
            fields.get(name) != "0" * 16
            for name in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")
        ):
            raise ValueError("validator capabilities must be empty")
        _verify_file_growth_limit(self.descriptor)
        self.verify_handles()

    def verify_pipes(self, child: subprocess.Popen[bytes]) -> None:
        if child.stdin is None or child.stdout is None or child.stderr is None:
            raise ValueError("validator requires retained distinct stdio pipes")
        identities = []
        for stream, mode in (
            (child.stdin, os.O_WRONLY),
            (child.stdout, os.O_RDONLY),
            (child.stderr, os.O_RDONLY),
        ):
            descriptor = stream.fileno()
            if (
                not stat.S_ISFIFO(os.fstat(descriptor).st_mode)
                or fcntl.fcntl(descriptor, fcntl.F_GETFL) & os.O_ACCMODE != mode
            ):
                raise ValueError("validator parent pipe type/direction differs")
            identities.append(_identity(descriptor))
        if len(set(identities)) != 3:
            raise ValueError("validator pipes must be distinct")
        directory = os.open(
            "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.descriptor
        )
        try:
            if set(os.listdir(directory)) != {"0", "1", "2"}:
                raise ValueError("validator may inherit only three stdio FDs")
            for number, (_, inode), mode in zip(
                range(3), identities, (os.O_RDONLY, os.O_WRONLY, os.O_WRONLY)
            ):
                flags = _fields(_read(self.descriptor, f"fdinfo/{number}")).get("flags", "")
                if (
                    os.readlink(str(number), dir_fd=directory) != f"pipe:[{inode}]"
                    or not re.fullmatch(r"[0-7]+", flags)
                    or int(flags, 8) & os.O_ACCMODE != mode
                ):
                    raise ValueError("validator stdio custody/direction differs")
        finally:
            os.close(directory)

    def read_configuration(self, configuration: DispatchConfiguration, argv: list[str]) -> None:
        self.verify_handles()
        if record_digest(configuration) != self.spec.configuration:
            raise ValueError("validator configuration identity changed")
        if _read(self.descriptor, "cmdline") != b"\0".join(part.encode() for part in argv) + b"\0":
            raise ValueError("validator argv differs from exact configured check")
        if _read(self.descriptor, "environ") != b"":
            raise ValueError("validator initial environment must be empty")
        if os.readlink("cwd", dir_fd=self.descriptor) != VALIDATOR_CWD:
            raise ValueError("validator cwd must be the frozen candidate")
        if (
            _read(self.descriptor, "cgroup").decode().strip()
            != f"0::/{self.spec.validator.relative_path}"
        ):
            raise ValueError("validator actual cgroup placement differs")
        for name, expected in self.spec.namespaces.items():
            info = os.stat("ns/" + name, dir_fd=self.descriptor)
            if (info.st_dev, info.st_ino) != (expected.device, expected.inode):
                raise ValueError("validator namespace identity differs")
        executable = os.open("exe", os.O_RDONLY | os.O_CLOEXEC, dir_fd=self.descriptor)
        try:
            before = os.fstat(executable)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_uid == VALIDATOR_UID
                or before.st_mode & 0o022
                or before.st_size > 134217728
            ):
                raise ValueError("validator executable authority/size differs")
            sha = hashlib.sha256()
            offset = 0
            while offset < before.st_size:
                chunk = os.pread(executable, min(65536, before.st_size - offset), offset)
                if not chunk:
                    raise ValueError("validator executable truncated")
                sha.update(chunk)
                offset += len(chunk)
            after = os.fstat(executable)
            keys = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_uid",
                "st_gid",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
            if (
                tuple(getattr(before, key) for key in keys)
                != tuple(getattr(after, key) for key in keys)
                or sha.hexdigest() != self.spec.executable_sha256
            ):
                raise ValueError("validator executable actual bytes/identity differ")
        finally:
            os.close(executable)
        self.verify_handles()


class ValidatorRefusal(ValueError):
    def __init__(self, reason: str, attempt: "ValidatorAttempt"):
        super().__init__(reason)
        self.attempt = attempt
        self.resources_reusable = False


class ValidatorAttempt:
    """Original parent/role/view custody; failed attempts retain every handle."""

    parent: RetainedTrustedTask
    validator: OwnedCgroup
    supervisor: OwnedCgroup
    aggregate: OwnedCgroup
    controls: InheritedControls
    configuration: DispatchConfiguration
    inventory: RetainedParentInventory
    manifest: FrozenCandidate
    _manifest: Digest
    native: AdmittedNative
    native_watchdog: OwnedWatchdogLifetime
    _owners: tuple[
        RetainedTrustedTask,
        OwnedCgroup,
        OwnedCgroup,
        OwnedCgroup,
        RetainedParentInventory,
        InheritedControls,
    ]
    _configuration: Digest
    origin_ns: int
    cutoff_ns: int
    frozen_fd: int
    scratch_fd: int
    frozen_identity: tuple[int, int]
    scratch_identity: tuple[int, int]
    descriptors: list[int]
    failed: bool
    staged: bool
    captured: bool
    resumed: bool
    watchdog_started: bool
    recovery_attempted: bool
    child: subprocess.Popen[bytes] | None
    proc: RetainedValidatorProc | None
    watchdog: OwnedWatchdogLifetime
    _watchdog: OwnedWatchdogLifetime
    admitted: "AdmittedValidator | None"

    def __init__(self) -> None:
        raise ValueError("validator requires its original retained parent preparation")

    def __reduce__(self) -> NoReturn:
        raise TypeError("validator live custody cannot be copied or exported")

    def verify(self, *, watchdog: bool = False) -> None:
        try:
            self._verify(watchdog=watchdog)
        except BaseException:
            self.failed = True
            raise

    def _verify(self, *, watchdog: bool = False) -> None:
        if self.failed or getattr(self.parent, "_validator_attempt", None) is not self:
            raise ValueError("original validator attempt failed or changed")
        if self._owners != (
            self.parent,
            self.validator,
            self.supervisor,
            self.aggregate,
            self.inventory,
            self.controls,
        ):
            raise ValueError("original validator owners changed")
        if (
            record_digest(self.configuration) != self._configuration
            or self.controls.configuration != self.configuration
            or record_digest(self.manifest) != self._manifest
        ):
            raise ValueError("validator sealed configuration changed")
        if (
            getattr(self.controls, "batch_origin_ns", None) != self.origin_ns
            or self.cutoff_ns != self.origin_ns + 570_000_000_000
            or time.monotonic_ns() >= self.cutoff_ns
        ):
            raise ValueError("validator original batch cutoff changed or expired")
        if (
            self.parent.spec.pid != os.getpid()
            or self.parent.spec.configuration != self._configuration
            or self.parent.spec.capabilities != CAPABILITIES
        ):
            raise ValueError("validator requires its original namespace parent")
        self.parent.verify(self.supervisor.identity)
        self.native_watchdog.verify_native_binding(self.native)
        if (
            self.watchdog is not self._watchdog
            or self.watchdog._owners != (self.parent, self.validator, self.supervisor)
            or self.watchdog.parent is not self.parent
            or self.watchdog.worker is not self.validator
            or self.watchdog.supervisor is not self.supervisor
        ):
            raise ValueError("validator original watchdog lifetime changed")
        native_exit = self.native.child.poll()
        if native_exit is None:
            raise ValueError("original native exit remains unknown before validator work")
        self.native.verify_terminal(native_exit)
        if (
            self.native_watchdog.task is None
            or self.native_watchdog.process is None
            or not _terminal_task_exited(self.native_watchdog.task)
            or self.native_watchdog.process.poll() is None
        ):
            raise ValueError("original native watchdog terminal custody differs")
        _current_source(self.configuration)
        for name, group in (
            ("aggregate", self.aggregate),
            ("supervisor", self.supervisor),
            ("validator", self.validator),
        ):
            if self.controls.groups.get(name) != group.identity:
                raise ValueError("validator original sealed cgroup identity differs")
        if (
            len(
                {
                    (group.identity.device, group.identity.inode)
                    for group in (self.validator, self.supervisor, self.aggregate)
                }
            )
            != 3
        ):
            raise ValueError("validator role must be distinct")
        _aggregate_readback(self.aggregate, self.validator)
        _aggregate_readback(self.aggregate, self.supervisor)
        sample = self.validator.sample()
        if any(sample.memory_events.values()) or any(sample.pids_events.values()):
            raise ValueError("validator resource-refusal history is nonzero")
        _role_controls(self.supervisor)
        self.inventory.verify()
        if not os.fstatvfs(self.inventory.descriptor).f_flag & os.ST_RDONLY:
            raise ValueError("validator runtime inventory is not actual readonly storage")
        for descriptor, identity, readonly in (
            (self.frozen_fd, self.frozen_identity, True),
            (self.scratch_fd, self.scratch_identity, False),
        ):
            info = os.fstat(descriptor)
            if (
                _identity(descriptor) != identity
                or not stat.S_ISDIR(info.st_mode)
                or info.st_uid != VALIDATOR_UID
                or info.st_gid != VALIDATOR_UID
                or stat.S_IMODE(info.st_mode) != 0o700
                or _filesystem_magic(descriptor) != 0xF15F
                or bool(os.fstatvfs(descriptor).f_flag & os.ST_RDONLY) != readonly
            ):
                raise ValueError(
                    "actual frozen/scratch validator volume identity or access differs"
                )
        if (
            self.frozen_identity[0] == self.scratch_identity[0]
            or _scan_fd(self.frozen_fd)[0] != self.manifest
        ):
            raise ValueError("validator frozen contents or distinct storage differs")
        for entry in self.manifest.files:
            info = os.stat(entry.path, dir_fd=self.frozen_fd, follow_symlinks=False)
            required = 0o500 if entry.kind == "directory" else 0o400
            if (
                info.st_uid != VALIDATOR_UID
                or info.st_gid != VALIDATOR_UID
                or stat.S_IMODE(info.st_mode) & required != required
            ):
                raise ValueError("frozen candidate is unreadable by the validator")
        if watchdog:
            observed = self.watchdog.observed
            if (
                observed is None
                or observed.task is not self.watchdog.task
                or observed.deadline.watchdog is not self.watchdog.process
                or observed.deadline.expires_ns > self.cutoff_ns
            ):
                raise ValueError("validator watchdog exceeds original batch cutoff")
            observed.check(self.validator, self.configuration)

    def verify_view(self, proc: RetainedValidatorProc) -> None:
        try:
            self._verify_view(proc)
        except BaseException:
            self.failed = True
            raise

    def _verify_view(self, proc: RetainedValidatorProc) -> None:
        self.verify()
        if any(
            proc.spec.namespaces[name] == self.parent.spec.namespaces[name]
            or proc.spec.namespaces[name] == self.controls.outer_namespaces[name]
            for name in ("mnt", "net")
        ):
            raise ValueError("validator mount/network namespace is not distinct")
        if (
            proc.spec.namespaces["pid"] == self.controls.outer_namespaces["pid"]
            or proc.spec.namespaces["user"] != self.parent.spec.namespaces["user"]
        ):
            raise ValueError("validator PID/user namespace identity differs")
        root = os.open("root", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=proc.descriptor)
        try:
            if (
                _identity(root) != self.inventory.identity
                or not os.fstatvfs(root).f_flag & os.ST_RDONLY
            ):
                raise ValueError("validator actual root differs from readonly runtime")
            for path, descriptor, readonly in (
                ("candidate/owned", self.frozen_fd, True),
                ("scratch", self.scratch_fd, False),
            ):
                opened = os.open(
                    path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
                )
                try:
                    if (
                        _identity(opened) != _identity(descriptor)
                        or bool(os.fstatvfs(opened).f_flag & os.ST_RDONLY) != readonly
                    ):
                        raise ValueError("validator actual candidate/scratch mount differs")
                finally:
                    os.close(opened)
            devices = os.open(
                "dev", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
            )
            try:
                authority = os.fstat(devices)
                if (
                    authority.st_uid != 0
                    or authority.st_gid != 0
                    or authority.st_mode & 0o022
                    or set(os.listdir(devices)) != {"null", "shm"}
                ):
                    raise ValueError("validator device inventory or write authority differs")
                null = os.stat("null", dir_fd=devices, follow_symlinks=False)
                if not stat.S_ISCHR(null.st_mode) or null.st_rdev != os.makedev(1, 3):
                    raise ValueError("validator device must be the actual null device")
                shm = os.open(
                    "shm",
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=devices,
                )
                original_shm = -1
                try:
                    original_shm = os.open(
                        "dev/shm",
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                        dir_fd=self.inventory.descriptor,
                    )
                    if (
                        _identity(shm) != _identity(original_shm)
                        or not os.fstatvfs(shm).f_flag & os.ST_RDONLY
                        or os.listdir(shm)
                    ):
                        raise ValueError(
                            "validator shm differs from original empty readonly inventory"
                        )
                finally:
                    if original_shm >= 0:
                        os.close(original_shm)
                    os.close(shm)
            finally:
                os.close(devices)
        finally:
            os.close(root)
        required = {"/": "ro", VALIDATOR_CWD: "ro", "/scratch": "rw", "/dev/shm": "ro"}
        allowed = {
            *required,
            "/proc",
            "/dev",
            "/proc/sys",
            "/proc/sysrq-trigger",
            "/proc/irq",
            "/proc/bus",
            "/proc/kcore",
        }
        found: dict[str, list[str]] = {}
        for row in _read(proc.descriptor, "mountinfo").decode("ascii").splitlines():
            before, separator, after = row.partition(" - ")
            fields = before.split()
            if not separator or len(fields) < 6 or len(after.split()) != 3:
                raise ValueError("validator actual mount inventory malformed")
            path = fields[4]
            if path not in allowed or path in found:
                raise ValueError("validator has an extra/covered mount or authentication view")
            found[path] = fields[5].split(",")
            if path not in {"/proc", "/dev", "/scratch"} and "ro" not in found[path]:
                raise ValueError("validator extra storage is writable")
        if any(mode not in found.get(path, []) for path, mode in required.items()):
            raise ValueError("validator readonly/candidate/scratch/shm mount controls differ")
        network_devices = _read(proc.descriptor, "net/dev").decode("ascii").splitlines()
        interfaces = [line.split(":", 1)[0].strip() for line in network_devices if ":" in line]
        if interfaces != ["lo"] or len(_read(proc.descriptor, "net/route").splitlines()) != 1:
            raise ValueError("validator network has non-loopback interfaces or routes")
        for row in _read(proc.descriptor, "net/if_inet6").decode("ascii").splitlines():
            if len(row.split()) != 6 or row.split()[-1] != "lo":
                raise ValueError("validator IPv6 interface differs")


def prepare_validator_attempt(
    parent: RetainedTrustedTask,
    validator: OwnedCgroup,
    supervisor: OwnedCgroup,
    aggregate: OwnedCgroup,
    controls: InheritedControls,
    inventory: RetainedParentInventory,
    frozen_fd: int,
    scratch_fd: int,
    manifest: FrozenCandidate,
) -> ValidatorAttempt:
    """Retain received actual views before readback; never import outer owners.

    The original owned transfer must supply these FDs. Manifest/capsule identities
    bind input only; this API cannot reconstruct installation or freeze custody.
    """
    if getattr(parent, "_validator_attempt", None) is not None:
        raise ValueError("original validator preparation consumed; no retry")
    attempt = object.__new__(ValidatorAttempt)
    attempt.parent, attempt.validator, attempt.supervisor, attempt.aggregate = (
        parent,
        validator,
        supervisor,
        aggregate,
    )
    attempt.controls, attempt.configuration, attempt.inventory = (
        controls,
        controls.configuration,
        inventory,
    )
    attempt._owners = (parent, validator, supervisor, aggregate, inventory, controls)
    attempt._configuration = record_digest(attempt.configuration)
    attempt.manifest = FrozenCandidate.model_validate_json(manifest.model_dump_json())
    attempt._manifest = record_digest(attempt.manifest)
    original_origin = getattr(controls, "batch_origin_ns", None)
    attempt.origin_ns = original_origin if type(original_origin) is int else 0
    attempt.cutoff_ns = 0
    attempt.descriptors = []
    attempt.failed = False
    attempt.staged = False
    attempt.captured = False
    attempt.resumed = False
    attempt.watchdog_started = False
    attempt.admitted = None
    attempt.recovery_attempted = False
    attempt.child = None
    attempt.proc = None
    attempt.watchdog = OwnedWatchdogLifetime(parent, validator, supervisor)
    attempt._watchdog = attempt.watchdog
    setattr(parent, "_validator_attempt", attempt)
    try:
        attempt.frozen_fd = os.dup(frozen_fd)
        attempt.descriptors.append(attempt.frozen_fd)
        attempt.scratch_fd = os.dup(scratch_fd)
        attempt.descriptors.append(attempt.scratch_fd)
        attempt.frozen_identity, attempt.scratch_identity = (
            _identity(attempt.frozen_fd),
            _identity(attempt.scratch_fd),
        )
        if type(attempt.origin_ns) is not int or not 0 < attempt.origin_ns <= time.monotonic_ns():
            raise ValueError("validator requires original sealed batch origin")
        attempt.cutoff_ns = attempt.origin_ns + 570_000_000_000
        native_anchor = getattr(parent, "_native_handoff", None)
        native_watchdog = getattr(parent, "_watchdog_lifetime", None)
        if (
            native_anchor is None
            or type(native_anchor[0]) is not AdmittedNative
            or type(native_watchdog) is not OwnedWatchdogLifetime
        ):
            raise ValueError("validator requires original native/watchdog terminal custody")
        native = native_anchor[0]
        attempt.native, attempt.native_watchdog = native, native_watchdog
        result = native.child.poll()
        if result is None:
            raise ValueError("validator cannot precede native terminal capture")
        native_watchdog.verify_native_terminal(native, result)
        attempt.verify()
        sample = validator.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("validator requires a fresh empty original role")
        return attempt
    except BaseException as error:
        attempt.failed = True
        raise ValidatorRefusal(str(error), attempt) from error


def create_validator_watchdog(
    attempt: ValidatorAttempt, preparation: BootstrapPreparation
) -> OwnedWatchdogLifetime:
    """Own a distinct validator watchdog before the separately qualified child.

    Operational source only. The original native watcher and its flags/lifeline
    are preserved. All partial validator handles remain in the pinned attempt.
    """
    if attempt.watchdog_started:
        raise ValidatorRefusal("validator watchdog creation consumed; no retry", attempt)
    attempt.watchdog_started = True
    lifetime = attempt.watchdog
    reading = ready_read = ready_write = -1
    try:
        attempt.verify()
        preparation = audit_linux_bootstrap(attempt.configuration, preparation)
        binary = preparation.policy.helper_binary
        if binary is None:
            raise ValueError("validator watchdog requires actual installed helper binding")
        if attempt.supervisor._read("cgroup.procs").split() != [str(attempt.parent.spec.pid)]:
            raise ValueError("validator watchdog requires sole original namespace parent")
        sample = attempt.validator.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("validator watchdog requires empty original validator role")
        origin_bound = time.monotonic_ns()
        if origin_bound + 5_000_000_000 > attempt.cutoff_ns:
            raise ValueError("validator watchdog cannot consume original fixed batch reserve")
        started = datetime.now(timezone.utc)
        lifetime.kill = os.open(
            "cgroup.kill",
            os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=attempt.validator.descriptor,
        )
        pipe2 = getattr(os, "pipe2")
        reading, lifetime.lifeline = pipe2(os.O_CLOEXEC)
        lifetime.lifeline_identity = _identity(lifetime.lifeline)
        ready_read, ready_write = pipe2(os.O_CLOEXEC | os.O_NONBLOCK)
        lifetime.process = subprocess.Popen(
            [
                "/bin/setpriv",
                "--reuid=0",
                "--regid=0",
                "--clear-groups",
                "--bounding-set=-all",
                "--inh-caps=-all",
                "--ambient-caps=-all",
                "--no-new-privs",
                "--",
                "/bin/crewshal-bootstrap",
                "--watchdog-fds",
                str(lifetime.kill),
                str(reading),
                str(ready_write),
            ],
            pass_fds=(lifetime.kill, reading, ready_write),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=attempt.parent.spec.cwd,
            env={},
            close_fds=True,
        )
        os.close(reading)
        reading = -1
        os.close(ready_write)
        ready_write = -1
        root = _proc_root(attempt.parent.spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, lifetime.process.pid)
            # Pin actual acquisitions before parsing metadata or constructing a
            # duplicated task. Constructor failure cannot discard the originals.
            attempt.descriptors.extend((descriptor, pidfd))
            pid, _, parent_pid, ticks = _stat_identity(_read(descriptor, "stat"))
            lifetime.task = RetainedTrustedTask(
                descriptor,
                pidfd,
                TrustedTaskSpec(
                    configuration=attempt._configuration,
                    pid=pid,
                    parent_pid=parent_pid,
                    start_ticks=ticks,
                    boot_id=attempt.parent.spec.boot_id,
                    cgroup=attempt.supervisor.identity,
                    namespaces=attempt.parent.spec.namespaces,
                    executable=binary,
                    argv=preparation.watchdog_argv,
                    environment={},
                    capabilities="0" * 16,
                    cwd=attempt.parent.spec.cwd,
                ),
            )
        finally:
            for descriptor in (descriptor, pidfd, root):
                if descriptor >= 0 and descriptor not in attempt.descriptors:
                    os.close(descriptor)
        acknowledgement = bytearray()
        while True:
            if (
                time.monotonic_ns() >= min(origin_bound + 5_000_000_000, attempt.cutoff_ns)
                or lifetime.process.poll() is not None
            ):
                raise ValueError("validator watchdog startup exhausted original attempt bound")
            if not select.select([ready_read], [], [], 0.001)[0]:
                continue
            chunk = os.read(ready_read, 81)
            acknowledgement.extend(chunk)
            if len(acknowledgement) > 80:
                raise ValueError("validator watchdog readiness exceeds bound")
            if not chunk:
                break
        deadline = ArmedDeadline.retain(
            lifetime.process,
            lifetime.lifeline,
            attempt.validator,
            attempt.configuration,
            bytes(acknowledgement),
            started=started,
        )
        if deadline.origin_ns < origin_bound or deadline.expires_ns > attempt.cutoff_ns:
            raise ValueError("validator watcher differs from original attempt/batch bounds")
        lifetime.observed = ObservedWatchdog(lifetime.task, deadline, lifetime.kill)
        lifetime.observed.check(attempt.validator, attempt.configuration)
        if set(attempt.supervisor._read("cgroup.procs").split()) != {
            str(attempt.parent.spec.pid),
            str(lifetime.process.pid),
        }:
            raise ValueError("validator supervisor parent/watchdog population differs")
        return lifetime
    except BaseException as error:
        attempt.failed = True
        raise ValidatorRefusal(str(error), attempt) from error
    finally:
        for descriptor in (reading, ready_read, ready_write):
            if descriptor >= 0:
                os.close(descriptor)


def attach_traced_validator(
    child: subprocess.Popen[bytes], spec: ValidatorAdmissionSpec
) -> RetainedValidatorProc:
    if (
        not isinstance(child, subprocess.Popen)
        or child.pid != spec.pid
        or spec.parent_pid != os.getpid()
    ):
        raise ValueError("validator attachment requires original direct Popen child")
    root = _proc_root(spec.boot_id)
    descriptor = pidfd = -1
    try:
        descriptor, pidfd = _attach(root, spec.pid)
        retained = RetainedValidatorProc(descriptor, pidfd, spec)
        try:
            retained.verify_state(traced=True)
            return retained
        except BaseException:
            # Actual acquired copies survive a failed readback. The caller must
            # retain this refusal alongside the original direct child.
            raise ValidatorProcRefusal("validator traced attachment readback failed", retained)
    finally:
        for handle in (descriptor, pidfd, root):
            if handle >= 0:
                os.close(handle)


class AdmittedValidator:
    """Stopped direct validator and original own watchdog; no release method."""

    attempt: ValidatorAttempt
    _owners: tuple[
        ValidatorAttempt, subprocess.Popen[bytes], RetainedValidatorProc, OwnedWatchdogLifetime
    ]
    _pipes: tuple[tuple[int, int], ...]

    def __init__(self) -> None:
        raise ValueError("validator admission requires original successful exec-stop handoff")

    def __reduce__(self) -> NoReturn:
        raise TypeError("admitted validator cannot be copied or exported")

    def resume(self) -> None:
        """Consume the stopped handoff after fresh readback, under its same timer."""
        attempt = self.attempt
        if attempt.resumed or attempt.admitted is not self:
            raise ValidatorRefusal("validator resume consumed or admission changed", attempt)
        attempt.resumed = True
        try:
            attempt.verify(watchdog=True)
            child, proc = attempt.child, attempt.proc
            if (
                child is None
                or proc is None
                or self._owners != (attempt, child, proc, attempt.watchdog)
            ):
                raise ValueError("validator original stopped handoff changed")
            proc.verify_state(traced=False)
            proc.read_configuration(attempt.configuration, attempt.configuration.validator_argv)
            proc.verify_pipes(child)
            self._verify_parent_pipes(child)
            attempt.verify_view(proc)
            attempt.verify(watchdog=True)
            getattr(signal, "pidfd_send_signal")(proc.pidfd, signal.SIGCONT)
        except BaseException as error:
            attempt.failed = True
            raise ValidatorRefusal(str(error), attempt) from error

    def _verify_parent_pipes(self, child: subprocess.Popen[bytes]) -> None:
        if child.stdin is None or child.stdout is None or child.stderr is None:
            raise ValueError("validator retained stdio missing")
        if (
            tuple(
                _identity(stream.fileno()) for stream in (child.stdin, child.stdout, child.stderr)
            )
            != self._pipes
        ):
            raise ValueError("validator retained parent pipe identity changed")

    def verify_terminal(self, expected_exit: int) -> None:
        try:
            self._verify_terminal(expected_exit)
        except BaseException:
            self.attempt.failed = True
            raise

    def _verify_terminal(self, expected_exit: int) -> None:
        attempt = self.attempt
        if attempt.admitted is not self or self._owners != (
            attempt,
            attempt.child,
            attempt.proc,
            attempt.watchdog,
        ):
            raise ValueError("validator admission original custody changed")
        attempt.verify()
        child, proc = attempt.child, attempt.proc
        if child is None or proc is None or child.poll() != expected_exit:
            raise ValueError("validator direct exit/reap differs")
        proc.verify_exited()
        sample = attempt.validator.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("validator role repopulated after capture")
        watchdog = attempt.watchdog
        if (
            watchdog.task is None
            or watchdog.process is None
            or not _terminal_task_exited(watchdog.task)
            or watchdog.process.poll() is None
        ):
            raise ValueError("validator watchdog exit/reap remains unknown")
        if attempt.supervisor._read("cgroup.procs").split() != [str(attempt.parent.spec.pid)]:
            raise ValueError("validator terminal readback requires sole original live parent")
        proc.verify_exited()
        attempt.parent.verify(attempt.supervisor.identity)

    def capture(self, *, cancelled: Callable[[], bool]) -> CapturedProcess:
        attempt = self.attempt
        if attempt.captured or not attempt.resumed or attempt.admitted is not self:
            raise ValidatorRefusal("validator capture consumed or admission changed", attempt)
        attempt.captured = True
        attempt.verify(watchdog=True)
        child = attempt.child
        observed = attempt.watchdog.observed
        if child is None or child.stdout is None or child.stderr is None or observed is None:
            attempt.failed = True
            raise ValueError("validator capture lacks original retained child/watchdog")
        try:
            self._verify_parent_pipes(child)
            captured = capture_attached_process(
                child,
                attempt.validator,
                child.stdout.fileno(),
                child.stderr.fileno(),
                started=observed.deadline.started,
                started_monotonic=observed.deadline.started_monotonic,
                cancelled=cancelled,
            )
        except BaseException:
            attempt.failed = True
            attempt.recovery_attempted = True
            attempt.watchdog.terminal(recovery_already_attempted=True)
            raise
        attempted = captured.observation.termination is not None
        terminal = attempt.watchdog.terminal(recovery_already_attempted=attempted)
        attempt.recovery_attempted = True
        if (
            not captured.observation.tree_stopped
            or captured.observation.exit_code is None
            or not terminal.worker_empty
            or not terminal.watchdog_exited
            or not terminal.watchdog_reaped
        ):
            attempt.failed = True
            raise ValidatorRefusal("validator terminal observation remains unknown", attempt)
        self.verify_terminal(captured.observation.exit_code)
        return captured


def stage_retained_validator(
    attempt: ValidatorAttempt,
    child: subprocess.Popen[bytes],
    proc: RetainedValidatorProc,
    preparation: BootstrapPreparation,
    driver: TraceDriver,
    *,
    cancelled: Callable[[], bool],
) -> AdmittedValidator:
    """One direct-child exec-stop handoff, using its own original five seconds.

    Caller independently creates a fresh validator view before Popen. A bwrap
    wrapper/descendant or arbitrary PID cannot substitute for the direct child.
    The existing native deadline, watchdog and admission API are unchanged.
    """
    if attempt.staged:
        raise ValidatorRefusal("validator handoff consumed; no retry", attempt)
    attempt.staged = True
    if (
        not isinstance(child, subprocess.Popen)
        or child.pid != proc.spec.pid
        or proc.spec.parent_pid != os.getpid()
        or proc.spec.validator != attempt.validator.identity
        or proc.spec.aggregate != attempt.aggregate.identity
    ):
        attempt.failed = True
        raise ValidatorRefusal("validator ownership differs; no recovery authority", attempt)
    attempt.child, attempt.proc = child, proc
    try:
        attempt.verify(watchdog=True)
        preparation = audit_linux_bootstrap(attempt.configuration, preparation)
        helper = preparation.policy.helper_binary
        observed = attempt.watchdog.observed
        if (
            helper is None
            or observed is None
            or observed.deadline.watchdog.pid == child.pid
            or proc.spec.configuration != attempt._configuration
        ):
            raise ValueError("validator exact helper/watchdog binding unavailable")
        deadline = observed.deadline
        observed.claim(attempt.validator, attempt.configuration)

        def check() -> None:
            attempt.verify(watchdog=True)
            if child.poll() is not None or cancelled():
                raise ValueError("validator exited or cancelled during handoff")

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
                    raise ValueError("validator wait PID/event differs")
                check()
                return

        stop = (int(signal.SIGSTOP) << 8) | 0x7F
        executed = (EXEC_EVENT << 16) | (int(signal.SIGTRAP) << 8) | 0x7F
        wait_stop(stop)
        proc.verify_state(traced=True)
        driver.verify_stop_delivery(child.pid, child.pid)
        sample = attempt.validator.sample()
        if not sample.populated or sample.direct_pids != [child.pid]:
            raise ValueError("validator role must contain only original helper")
        helper_spec = ValidatorAdmissionSpec.model_validate(
            {**proc.spec.model_dump(), "executable_sha256": helper}
        )
        helper_proc = RetainedValidatorProc(proc.descriptor, proc.pidfd, helper_spec)
        try:
            helper_proc.read_configuration(
                attempt.configuration,
                ["/bin/crewshal-bootstrap", "--validator", *attempt.configuration.validator_argv],
            )
            helper_proc.verify_pipes(child)
        finally:
            helper_proc.close()
        attempt.verify_view(proc)
        check()
        driver.options(child.pid)
        driver.continue_exec(child.pid)
        wait_stop(executed)
        if driver.exec_pid(child.pid) != child.pid:
            raise ValueError("validator exec changed retained PID/thread")
        proc.verify_state(traced=True)
        driver.verify_storage_filter(child.pid)
        proc.read_configuration(attempt.configuration, attempt.configuration.validator_argv)
        proc.verify_pipes(child)
        attempt.verify_view(proc)
        check()
        driver.queue_stop(proc.pidfd)
        driver.continue_exec(child.pid)
        wait_stop(stop)
        proc.verify_state(traced=True)
        driver.verify_stop_delivery(child.pid, os.getpid())
        driver.detach_stopped(child.pid)
        while True:
            check()
            state = _stat_identity(_read(proc.descriptor, "stat"))[1]
            tracer = _fields(_read(proc.descriptor, "status")).get("TracerPid")
            if state == "T" and tracer == "0":
                break
            if state not in ("t", "R", "S", "T"):
                raise ValueError("validator failed to reach detached group-stop")
            time.sleep(0.001)
        proc.verify_state(traced=False)
        proc.read_configuration(attempt.configuration, attempt.configuration.validator_argv)
        proc.verify_pipes(child)
        attempt.verify_view(proc)
        if (
            not math.isfinite(deadline.started_monotonic)
            or time.monotonic() - deadline.started_monotonic >= 5
        ):
            raise ValueError("validator original five-second admission deadline exhausted")
        admitted = object.__new__(AdmittedValidator)
        admitted.attempt = attempt
        admitted._owners = (attempt, child, proc, attempt.watchdog)
        assert child.stdin is not None and child.stdout is not None and child.stderr is not None
        admitted._pipes = tuple(
            _identity(stream.fileno()) for stream in (child.stdin, child.stdout, child.stderr)
        )
        attempt.admitted = admitted
        return admitted
    except BaseException as error:
        attempt.failed = True
        # No new timer origin and no ordinary retry. Caller must retain the
        # original lifetime and perform its sole bounded terminal recovery.
        raise ValidatorRefusal(str(error), attempt) from error
