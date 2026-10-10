"""Namespace-resident parent bridge source, invoked only by qualified trusted setup.

No CLI, namespace creator, watchdog launcher or authority parser is provided.
This source must never be invoked on the host using prospective bindings alone.
"""

from dataclasses import dataclass
import fcntl
import hashlib
import os
from pathlib import PurePosixPath
import re
import select
import stat
import subprocess
import sys
import time
from typing import Callable, Literal

from pydantic import Field, model_validator

from crewshal.admission import (
    AdmittedNative,
    NativeAdmissionSpec,
    NamespaceIdentity,
    RetainedProc,
    _aggregate_readback,
    _current_source,
    _fields,
    _read,
    _stat_identity,
)
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_bootstrap import (
    ArmedDeadline,
    BootstrapPreparation,
    BootstrapRefusal,
    TraceDriver,
    _recover,
    _traced,
    audit_linux_bootstrap,
    stage_retained_bootstrap,
)
from crewshal.model import Contract
from crewshal.linux_envelope import native_working_directory
from crewshal.supervisor import CgroupIdentity, OwnedCgroup, _counters


class TrustedTaskSpec(Contract):
    """Exact trusted setup observations, never authority or worker-supplied data."""

    configuration: Digest
    schema_version: Literal[1] = 1
    pid: int = Field(gt=1)
    parent_pid: int = Field(gt=0)
    start_ticks: int = Field(gt=0)
    boot_id: str = Field(pattern=r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    cgroup: CgroupIdentity
    namespaces: dict[str, NamespaceIdentity]
    executable: Digest
    argv: list[str]
    environment: dict[str, str]
    capabilities: str = Field(pattern=r"^[0-9a-f]{16}$")
    # Outer observer paths are not namespace-local native/parent paths. Actual
    # namespace-parent/watchdog/worker admission still requires its exact route.
    cwd: Literal["/", "/scratch/checkout", "/candidate/owned"] = "/scratch/checkout"
    placement: Literal["namespace", "outer_observer"] = "namespace"
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False

    @model_validator(mode="after")
    def exact_trusted_cwd(self) -> "TrustedTaskSpec":
        if (self.placement == "outer_observer") != (self.cwd == "/"):
            raise ValueError("outer observer cwd differs from namespace-local task cwd")
        return self


def _proc_root(boot_id: str) -> int:
    if sys.platform != "linux" or not hasattr(os, "pidfd_open"):
        raise ValueError("Linux namespace-parent proc/pidfd unavailable")
    root = os.open("/proc", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(root)
        device = f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}"
        found = False
        for line in _read(root, "self/mountinfo").decode("ascii").splitlines():
            before, separator, after = line.partition(" - ")
            fields = before.split()
            if separator and len(fields) >= 6 and after.split()[0] == "proc":
                found |= fields[2:5] == [device, "/", "/proc"]
        if not found or _read(root, "sys/kernel/random/boot_id").decode().strip() != boot_id:
            raise ValueError("parent proc mount or boot identity differs")
        return root
    except BaseException:
        os.close(root)
        raise


def _attach(root: int, pid: int) -> tuple[int, int]:
    opener = getattr(os, "pidfd_open", None)
    if opener is None:
        raise ValueError("Linux pidfd attachment unavailable")
    pidfd = opener(pid, 0)
    try:
        if _fields(_read(root, f"self/fdinfo/{pidfd}")).get("Pid") != str(pid):
            raise ValueError("parent bridge pidfd identity differs")
        descriptor = os.open(
            str(pid), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
        )
        return descriptor, pidfd
    except BaseException:
        os.close(pidfd)
        raise


def _namespaces(descriptor: int, expected: dict[str, NamespaceIdentity]) -> None:
    if set(expected) != {"mnt", "net", "pid", "user", "time"}:
        raise ValueError("parent bridge requires exact namespace and monotonic clock identities")
    handle = os.open(
        "ns", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=descriptor
    )
    try:
        for name, identity in expected.items():
            info = os.stat(name, dir_fd=handle)
            if (info.st_dev, info.st_ino) != (identity.device, identity.inode):
                raise ValueError("parent bridge namespace identity differs")
    finally:
        os.close(handle)


def _image(descriptor: int, expected: str) -> None:
    handle = os.open("exe", os.O_RDONLY | os.O_CLOEXEC, dir_fd=descriptor)
    try:
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_mode & 0o022 or before.st_size > 134217728:
            raise ValueError("trusted parent/helper executable authority or size differs")
        sha = hashlib.sha256()
        total = 0
        while chunk := os.read(handle, 65536):
            total += len(chunk)
            if total > 134217728:
                raise ValueError("trusted executable exceeds bound")
            sha.update(chunk)
        after = os.fstat(handle)
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
        if sha.hexdigest() != expected or any(
            getattr(before, k) != getattr(after, k) for k in keys
        ):
            raise ValueError("trusted executable bytes or identity differ")
    finally:
        os.close(handle)


class RetainedTrustedTask:
    """Retained root setup/watchdog identity. Constructor is also an offline seam."""

    def __init__(self, descriptor: int, pidfd: int, spec: TrustedTaskSpec):
        self.spec = TrustedTaskSpec.model_validate_json(spec.model_dump_json())
        self.descriptor = os.dup(descriptor)
        try:
            self.pidfd = os.dup(pidfd)
        except BaseException:
            os.close(self.descriptor)
            raise
        info = os.fstat(self.descriptor)
        self.directory = (info.st_dev, info.st_ino)
        info = os.fstat(self.pidfd)
        self.pidfd_identity = (info.st_dev, info.st_ino)
        self._bridge_claimed = False
        self._setup_started = False
        self._watchdog_started = False

    @classmethod
    def attach(cls, spec: TrustedTaskSpec) -> "RetainedTrustedTask":
        root = _proc_root(spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, spec.pid)
            retained = cls(descriptor, pidfd, spec)
            try:
                retained.verify(spec.cgroup)
                return retained
            except BaseException:
                retained.close()
                raise
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)

    def close(self) -> None:
        for name in ("descriptor", "pidfd"):
            handle = getattr(self, name)
            if handle >= 0:
                os.close(handle)
                setattr(self, name, -1)

    def verify_handles(self) -> None:
        directory = os.fstat(self.descriptor)
        pidfd = os.fstat(self.pidfd)
        if (directory.st_dev, directory.st_ino) != self.directory or (
            pidfd.st_dev,
            pidfd.st_ino,
        ) != self.pidfd_identity:
            raise ValueError("trusted task retained descriptor changed")

    def verify(self, group: CgroupIdentity) -> None:
        self.verify_handles()
        spec = self.spec
        info = os.fstat(self.descriptor)
        pid, state, parent, start = _stat_identity(_read(self.descriptor, "stat"))
        if (
            (info.st_dev, info.st_ino) != self.directory
            or select.select([self.pidfd], [], [], 0)[0]
            or (pid, parent, start) != (spec.pid, spec.parent_pid, spec.start_ticks)
            or spec.pid <= 1
            or spec.start_ticks <= 0
            or state not in ("R", "S")
        ):
            raise ValueError("trusted task PID/start/parent/liveness differs")
        fields = _fields(_read(self.descriptor, "status"))
        expected = {
            "Pid": str(spec.pid),
            "Tgid": str(spec.pid),
            "PPid": str(spec.parent_pid),
            "TracerPid": "0",
            "Threads": "1",
            "NoNewPrivs": "1",
            "Uid": "0 0 0 0",
            "Gid": "0 0 0 0",
            "Groups": "",
            "CapInh": "0000000000000000",
            "CapAmb": "0000000000000000",
            "CapPrm": spec.capabilities,
            "CapEff": spec.capabilities,
            "CapBnd": spec.capabilities,
        }
        if not re.fullmatch(r"[0-9a-f]{16}", spec.capabilities) or any(
            fields.get(k) != v for k, v in expected.items()
        ):
            raise ValueError("trusted task role, capabilities or thread identity differs")
        if _read(self.descriptor, "cgroup").decode().strip() != f"0::/{group.relative_path}":
            raise ValueError("trusted task cgroup placement differs")
        _namespaces(self.descriptor, spec.namespaces)
        if _read(self.descriptor, "cmdline") != b"\0".join(x.encode() for x in spec.argv) + b"\0":
            raise ValueError("trusted task argv differs")
        raw = _read(self.descriptor, "environ")
        entries = raw.split(b"\0") if raw else [b""]
        values: dict[str, str] = {}
        for entry in entries[:-1]:
            key, separator, value = entry.decode().partition("=")
            if not separator or not key or key in values:
                raise ValueError("trusted task environment malformed")
            values[key] = value
        if entries[-1] != b"" or values != spec.environment:
            raise ValueError("trusted task environment differs")
        if os.readlink("cwd", dir_fd=self.descriptor) != spec.cwd:
            raise ValueError("trusted task cwd differs")
        _image(self.descriptor, spec.executable)
        self.verify_handles()


@dataclass(frozen=True)
class ObservedWatchdog:
    """Kernel readback of a separately created watchdog, never a disarm handle."""

    task: RetainedTrustedTask
    deadline: ArmedDeadline
    kill_descriptor: int

    def claim(self, worker: OwnedCgroup, configuration: DispatchConfiguration) -> None:
        """Consume this retained watchdog once; never retry/reuse its live worker."""
        if self.task._bridge_claimed:
            raise ValueError("retained watchdog/worker already consumed; no resource reuse")
        self.check(worker, configuration)
        self.task._bridge_claimed = True

    def check(self, worker: OwnedCgroup, configuration: DispatchConfiguration) -> None:
        self.deadline.check(worker, configuration)
        worker._verify()
        spec = self.task.spec
        if (
            spec.pid != self.deadline.watchdog.pid
            or spec.parent_pid != os.getpid()
            or spec.configuration != record_digest(configuration)
            or spec.capabilities != "0000000000000000"
            or spec.argv != ["/bin/crewshal-bootstrap", "--watchdog"]
            or spec.environment
        ):
            raise ValueError("watchdog retained identity or role differs")
        self.task.verify(spec.cgroup)
        owned = os.open(
            "cgroup.kill",
            os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=worker.descriptor,
        )
        try:
            identity = os.fstat(owned)
            retained = os.fstat(self.kill_descriptor)
            child = os.stat("fd/3", dir_fd=self.task.descriptor)
            if (
                not stat.S_ISREG(retained.st_mode)
                or (retained.st_dev, retained.st_ino) != (identity.st_dev, identity.st_ino)
                or (child.st_dev, child.st_ino) != (identity.st_dev, identity.st_ino)
                or fcntl.fcntl(self.kill_descriptor, fcntl.F_GETFL) & (os.O_ACCMODE | os.O_NONBLOCK)
                != os.O_WRONLY | os.O_NONBLOCK
            ):
                raise ValueError("watchdog kill interface is not the owned worker")
        finally:
            os.close(owned)
        directory = os.open(
            "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.task.descriptor
        )
        try:
            if set(os.listdir(directory)) != {"0", "1", "2", "3", "4", "6"}:
                raise ValueError("watchdog descriptor inventory differs from armed checkpoint")
            if os.readlink("6", dir_fd=directory) != "anon_inode:[timerfd]":
                raise ValueError("watchdog timer descriptor differs")
            if os.readlink("4", dir_fd=directory) != f"pipe:[{self.deadline.lifeline_identity[1]}]":
                raise ValueError("watchdog lifeline descriptor differs")
            for number in ("0", "1", "2"):
                info = os.stat(number, dir_fd=directory)
                if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(1, 3):
                    raise ValueError("watchdog stdio must be the namespace's verified null device")
        finally:
            os.close(directory)
        for control_number, mode in ((3, os.O_WRONLY | os.O_NONBLOCK), (4, os.O_RDONLY)):
            fields = _fields(_read(self.task.descriptor, f"fdinfo/{control_number}"))
            flags = int(fields["flags"], 8)
            if flags & (os.O_ACCMODE | os.O_NONBLOCK) != mode:
                raise ValueError("watchdog control descriptor direction differs")
        before = time.monotonic_ns()
        timer = _fields(_read(self.task.descriptor, "fdinfo/6"))
        after = time.monotonic_ns()
        match = re.fullmatch(r"\(([0-9]+), ([0-9]+)\)", timer.get("it_value", ""))
        if match is None:
            raise ValueError("watchdog remaining timer malformed")
        seconds, nanos = (int(x) for x in match.groups())
        remaining = seconds * 1_000_000_000 + nanos
        if (
            nanos >= 1_000_000_000
            or remaining <= 0
            or after < before
            or timer.get("clockid") != "1"
            or timer.get("ticks") != "0"
            or timer.get("settime flags") != "01"
            or timer.get("it_interval") != "(0, 0)"
            or int(timer.get("flags", "0"), 8) & (os.O_ACCMODE | os.O_NONBLOCK | os.O_CLOEXEC)
            != os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC
            or not before + remaining <= self.deadline.expires_ns <= after + remaining
        ):
            raise ValueError("watchdog effective monotonic timer differs from original deadline")
        self.deadline.check(worker, configuration)


def attach_traced_child(child: subprocess.Popen[bytes], spec: NativeAdmissionSpec) -> RetainedProc:
    """Attach only the parent's initial traced helper; native attach remains strict."""
    if (
        not isinstance(child, subprocess.Popen)
        or child.pid != spec.pid
        or spec.parent_pid != os.getpid()
    ):
        raise ValueError("initial traced attachment requires the direct Popen child")
    root = _proc_root(spec.boot_id)
    descriptor = pidfd = -1
    try:
        descriptor, pidfd = _attach(root, spec.pid)
        return _retain_traced(descriptor, pidfd, child, spec)
    finally:
        for handle in (descriptor, pidfd, root):
            if handle >= 0:
                os.close(handle)


def _retain_traced(
    descriptor: int, pidfd: int, child: subprocess.Popen[bytes], spec: NativeAdmissionSpec
) -> RetainedProc:
    retained = RetainedProc(descriptor, pidfd, spec)
    try:
        _traced(retained, child)
        return retained
    except BaseException:
        retained.close()
        raise


def _move_self(group: OwnedCgroup) -> None:
    group._verify()
    handle = os.open(
        "cgroup.procs",
        os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
        dir_fd=group.descriptor,
    )
    try:
        if os.write(handle, b"0") != 1:
            raise ValueError("owned self-migration incomplete")
    finally:
        os.close(handle)


class ParentBridgeRefusal(ValueError):
    """Retain all created resources on refusal, including incomplete recovery."""

    def __init__(
        self,
        reason: str,
        parent: RetainedTrustedTask,
        watchdog: ObservedWatchdog,
        child: subprocess.Popen[bytes] | None,
        proc: RetainedProc | None,
        recovery: BootstrapRefusal | None,
        groups: tuple[OwnedCgroup, OwnedCgroup, OwnedCgroup],
    ):
        super().__init__(reason)
        self.parent, self.watchdog = parent, watchdog
        self.child, self.proc = child, proc
        self.recovery = None if recovery is None else recovery.recovery
        self.worker, self.supervisor, self.aggregate = groups
        self.resources_reusable = False


def stage_namespace_parent(
    parent: RetainedTrustedTask,
    outer_namespaces: dict[str, NamespaceIdentity],
    watchdog: ObservedWatchdog,
    worker: OwnedCgroup,
    supervisor: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: DispatchConfiguration,
    preparation: BootstrapPreparation,
    driver: TraceDriver,
    native_executable: Digest,
    *,
    cancelled: Callable[[], bool],
) -> AdmittedNative:
    """Qualified namespace parent's one-shot source route, ending stopped.

    Readiness/effective timer precede migration and Popen. Temporarily placing
    the single-threaded trusted parent in the empty worker ensures the kernel
    assigns its direct child there before any child instruction or exec. The
    independent watchdog covers parent/Popen blockage as well as the child.
    Parent returns to its bounded sibling role before exact worker admission.
    No supplied object, digest or this function itself establishes authority.
    """
    configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
    preparation = audit_linux_bootstrap(configuration, preparation)
    _current_source(configuration)
    if (
        preparation.policy.helper_binary is None
        or configuration.linux_envelope is None
        or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(preparation.policy)
        or not re.fullmatch(r"[0-9a-f]{64}", native_executable)
    ):
        raise ValueError("parent bridge requires exact helper/policy/native bindings before Popen")
    spec = parent.spec
    if (
        spec.pid != os.getpid()
        or spec.configuration != record_digest(configuration)
        or spec.cgroup != supervisor.identity
        or watchdog.task.spec.cgroup != supervisor.identity
        or watchdog.task.spec.executable != preparation.policy.helper_binary
        or watchdog.task.spec.namespaces != spec.namespaces
        or watchdog.task.spec.boot_id != spec.boot_id
        or watchdog.task.spec.pid == spec.pid
        or spec.cwd != native_working_directory(configuration)
        or watchdog.task.spec.cwd != spec.cwd
        or worker.identity == supervisor.identity
        or set(outer_namespaces) != set(spec.namespaces)
        or any(outer_namespaces[k] == spec.namespaces[k] for k in ("mnt", "net", "pid"))
        or PurePosixPath(supervisor.identity.relative_path).parent
        != PurePosixPath(aggregate.identity.relative_path)
    ):
        raise ValueError("namespace parent, watchdog or retained role topology differs")
    required_caps = (1 << 6) | (1 << 7) | (1 << 8) | (1 << 19) | (1 << 21)
    if int(spec.capabilities, 16) != required_caps:
        raise ValueError("namespace parent requires only pinned setup/trace/migration capabilities")
    _aggregate_readback(aggregate, worker)
    _aggregate_readback(aggregate, supervisor)
    parent.verify(supervisor.identity)
    supervisor._verify()
    for name, value in {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "128",
        "cgroup.type": "domain",
    }.items():
        if supervisor._read(name) != value:
            raise ValueError("bounded supervisor controls differ")
    for name, keys in (("memory.events", {"max", "oom", "oom_kill"}), ("pids.events", {"max"})):
        if any(_counters(supervisor._read(name), keys)[k] for k in keys):
            raise ValueError("supervisor has resource-refusal history")
    expected_supervisor = {str(spec.pid), str(watchdog.task.spec.pid)}
    if set(supervisor._read("cgroup.procs").split()) != expected_supervisor:
        raise ValueError("supervisor must retain exactly parent and watchdog")
    sample = worker.sample()
    if sample.populated or sample.direct_pids:
        raise ValueError("namespace bridge requires a fresh empty worker")

    def check() -> None:
        watchdog.check(worker, configuration)
        if cancelled():
            raise ValueError("namespace bridge cancelled")

    check()  # Effective readiness before the first worker migration/startup.
    watchdog.claim(worker, configuration)
    child: subprocess.Popen[bytes] | None = None
    proc: RetainedProc | None = None
    in_handoff = False
    try:
        try:
            _move_self(worker)
            parent.verify(worker.identity)
            if worker.sample().direct_pids != [spec.pid]:
                raise ValueError("worker must contain only the trusted parent before Popen")
            check()
            child = subprocess.Popen(
                [
                    "/bin/setpriv",
                    "--reuid=65534",
                    "--regid=65534",
                    "--clear-groups",
                    "--bounding-set=-all",
                    "--inh-caps=-all",
                    "--ambient-caps=-all",
                    "--no-new-privs",
                    "--",
                    *preparation.helper_argv,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=native_working_directory(configuration),
                env=configuration.native_environment.copy(),
                close_fds=True,
                bufsize=0,
            )
        finally:
            # No worker cleanup/recovery is attempted unless the trusted parent
            # is independently observed outside that subtree. Migration failure
            # leaves the original watchdog armed and resources non-reusable.
            _move_self(supervisor)
            parent.verify(supervisor.identity)
        check()
        # Popen completed the exec-only setpriv/helper errpipe handshake. Poll
        # the helper's initial stop without consuming its wait event; the owned
        # handoff remains responsible for exact SIGSTOP delivery verification.
        root = _proc_root(spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, child.pid)
            while True:
                check()
                pid, state, parent_pid, start = _stat_identity(_read(descriptor, "stat"))
                if (pid, parent_pid) != (child.pid, spec.pid):
                    raise ValueError("new helper PID/parent differs")
                if select.select([pidfd], [], [], 0)[0] or state not in ("R", "S", "t"):
                    raise ValueError("helper exited or failed to reach its initial trace stop")
                if state == "t":
                    break
                time.sleep(0.001)
            native_spec = NativeAdmissionSpec(
                configuration=record_digest(configuration),
                pid=child.pid,
                parent_pid=spec.pid,
                start_ticks=start,
                boot_id=spec.boot_id,
                worker=worker.identity,
                aggregate=aggregate.identity,
                executable_sha256=native_executable,
                namespaces={k: v for k, v in spec.namespaces.items() if k != "time"},
            )
            proc = _retain_traced(descriptor, pidfd, child, native_spec)
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)
        check()

        def monitored_cancellation() -> bool:
            check()
            return False

        in_handoff = True
        admitted = stage_retained_bootstrap(
            child,
            proc,
            worker,
            aggregate,
            configuration,
            preparation,
            watchdog.deadline,
            driver,
            cancelled=monitored_cancellation,
        )
        in_handoff = False
        check()
        # Keep the actual handoff in its original namespace parent. A later
        # freeze may not substitute another child, watchdog or role allocation.
        setattr(parent, "_native_handoff", (admitted, watchdog, worker, supervisor, aggregate))
        return admitted
    except BaseException as error:
        # The same refusal uses one grace only; never recover the handoff twice.
        if in_handoff and isinstance(error, (KeyboardInterrupt, SystemExit)):
            # The handoff already performed its one bounded recovery before
            # reraising the interruption; its result was not returned. Preserve
            # that unknown outcome and resources instead of starting a new grace.
            raise ParentBridgeRefusal(
                str(error),
                parent,
                watchdog,
                child,
                proc,
                None,
                (worker, supervisor, aggregate),
            ) from error
        try:
            parent.verify(supervisor.identity)
        except (OSError, ValueError) as placement_error:
            raise ParentBridgeRefusal(
                f"{error}; parent outside worker unobserved: {placement_error}",
                parent,
                watchdog,
                child,
                proc,
                None,
                (worker, supervisor, aggregate),
            ) from error
        if isinstance(error, BootstrapRefusal):
            refusal = error
        else:
            refusal = BootstrapRefusal(str(error), _recover(child, worker))
        raise ParentBridgeRefusal(
            str(error), parent, watchdog, child, proc, refusal, (worker, supervisor, aggregate)
        ) from error
