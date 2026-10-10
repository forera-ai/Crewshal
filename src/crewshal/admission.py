"""Read-only admission of a retained, stopped native child, never a launcher.

Trusted Linux setup must still create and independently qualify the envelope,
deadline, mounts, role policies and credential channel before starting a child.
Admission is a bounded snapshot. It grants no authority and releases no process.
"""

from dataclasses import dataclass
from datetime import datetime
import fcntl
import hashlib
import math
import os
from pathlib import Path, PurePosixPath
import re
import select
import stat
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Annotated, Callable, Literal, Self

from pydantic import Field, model_validator

from crewshal.candidate import FrozenCandidate
from crewshal.contracts import Digest, Identifier, Record, record_digest
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import _Reader
from crewshal.supervisor import (
    CapturedProcess,
    CgroupIdentity,
    OwnedCgroup,
    SupervisionReceipt,
    _counters,
    capture_attached_process,
)

if TYPE_CHECKING:
    from crewshal.dispatch import CodexDispatch, DispatchConfiguration
    from crewshal.durable import CoordinatorStore
    from crewshal.integration import CodexCollection
    from crewshal.linux_setup import OwnedWatchdogLifetime


class NamespaceIdentity(Contract):
    device: Annotated[int, Field(ge=0)]
    inode: Annotated[int, Field(gt=0)]


class NativeAdmissionSpec(Contract):
    """Trusted setup's retained identities; not input from worker output."""

    schema_version: Literal[1] = 1
    configuration: Digest
    pid: Annotated[int, Field(gt=0)]
    parent_pid: Annotated[int, Field(gt=0)]
    start_ticks: Annotated[int, Field(gt=0)]
    boot_id: str = Field(pattern=r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    worker: CgroupIdentity
    aggregate: CgroupIdentity
    namespaces: dict[str, NamespaceIdentity]
    executable_sha256: Digest
    native_uid: Literal[65534] = 65534
    native_gid: Literal[65534] = 65534
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False

    @model_validator(mode="after")
    def topology(self) -> "NativeAdmissionSpec":
        if str(PurePosixPath(self.worker.relative_path).parent) != self.aggregate.relative_path:
            raise ValueError("worker must be an immediate child of the owned aggregate")
        if self.worker.device != self.aggregate.device or self.worker.inode == self.aggregate.inode:
            raise ValueError("distinct same-filesystem aggregate/worker identities required")
        if set(self.namespaces) != {"mnt", "net", "pid", "user"}:
            raise ValueError("exact mount/network/PID/user namespace identities required")
        if self.pid == self.parent_pid:
            raise ValueError("native process cannot be its own parent")
        return self


def _read(descriptor: int, name: str, limit: int = 65536) -> bytes:
    """Bounded no-follow proc file read; proc magic links have separate readers."""
    child = os.open(
        name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=descriptor
    )
    try:
        if not stat.S_ISREG(os.fstat(child).st_mode):
            raise ValueError("proc readback must be a regular kernel interface")
        result = bytearray()
        while len(result) <= limit:
            part = os.read(child, min(4096, limit + 1 - len(result)))
            if not part:
                return bytes(result)
            result.extend(part)
        raise ValueError("proc readback exceeds bound")
    finally:
        os.close(child)


def _fields(raw: bytes) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in raw.decode("ascii").splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key or key in result:
            raise ValueError("malformed or duplicate proc field")
        result[key] = value.strip()
    return result


def _stat_identity(raw: bytes) -> tuple[int, str, int, int]:
    # comm can itself contain whitespace, ')' and newlines. The final ')' ends it.
    text = raw.decode("ascii")
    left, right = text.find(" ("), text.rfind(") ")
    if left < 1 or right <= left:
        raise ValueError("malformed process stat")
    pid = text[:left]
    fields = text[right + 2 :].split()
    if len(fields) < 20 or not pid.isdigit():
        raise ValueError("incomplete process stat")
    if not fields[1].isdigit() or not fields[19].isdigit():
        raise ValueError("malformed process parent/start identity")
    return int(pid), fields[0], int(fields[1]), int(fields[19])


class RetainedProc:
    """Pinned proc dir plus pidfd; no numeric-PID signalling or process creation."""

    def __init__(self, descriptor: int, pidfd: int, spec: NativeAdmissionSpec):
        # Internal descriptor seam also permits explicit offline file fixtures.
        self.spec = NativeAdmissionSpec.model_validate_json(spec.model_dump_json())
        self.descriptor = os.dup(descriptor)
        try:
            self.pidfd = os.dup(pidfd)
        except BaseException:
            os.close(self.descriptor)
            raise
        self.directory = os.fstat(self.descriptor)
        self.pidfd_identity = os.fstat(self.pidfd)

    @classmethod
    def attach(cls, spec: NativeAdmissionSpec) -> "RetainedProc":
        if sys.platform != "linux" or not hasattr(os, "pidfd_open"):
            raise ValueError("Linux pidfd/proc admission unavailable on this platform")
        spec = NativeAdmissionSpec.model_validate_json(spec.model_dump_json())
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        root = os.open("/proc", flags)
        pidfd = descriptor = -1
        try:
            info = os.fstat(root)
            device = f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}"
            # Refuse an ordinary directory pretending to be the standard procfs.
            found = False
            for line in _read(root, "self/mountinfo").decode("ascii").splitlines():
                before, separator, after = line.partition(" - ")
                fields = before.split()
                if separator and len(fields) >= 6 and after.split()[0] == "proc":
                    found |= fields[2:5] == [device, "/", "/proc"]
            if (
                not found
                or _read(root, "sys/kernel/random/boot_id").decode().strip() != spec.boot_id
            ):
                raise ValueError("proc mount or boot identity differs")
            pidfd = os.pidfd_open(spec.pid, 0)
            identity = _fields(_read(root, f"self/fdinfo/{pidfd}"))
            if identity.get("Pid") != str(spec.pid):
                raise ValueError("pidfd identity differs from retained child")
            descriptor = os.open(str(spec.pid), flags, dir_fd=root)
            retained = cls(descriptor, pidfd, spec)
            try:
                retained.verify_stopped()
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

    def _verify_handles(self) -> None:
        current = os.fstat(self.descriptor)
        if (current.st_dev, current.st_ino) != (self.directory.st_dev, self.directory.st_ino):
            raise ValueError("retained proc descriptor changed")
        current = os.fstat(self.pidfd)
        if (current.st_dev, current.st_ino) != (
            self.pidfd_identity.st_dev,
            self.pidfd_identity.st_ino,
        ):
            raise ValueError("retained pidfd descriptor changed")

    def verify_exited(self) -> None:
        # Production attach supplies an actual pidfd. Ordinary file seams are
        # only offline fixtures; readiness never proves storage reference closure.
        self._verify_handles()
        exited = bool(select.select([self.pidfd], [], [], 0)[0])
        self._verify_handles()
        if not exited:
            raise ValueError("retained pidfd has not observed native exit")

    def verify_stopped(self) -> None:
        self._verify_handles()
        if select.select([self.pidfd], [], [], 0)[0]:
            raise ValueError("retained pidfd reports process exit")
        self._verify_handles()
        if _stat_identity(_read(self.descriptor, "stat")) != (
            self.spec.pid,
            "T",
            self.spec.parent_pid,
            self.spec.start_ticks,
        ):
            raise ValueError("native PID/start/parent or stopped state differs")
        status = _fields(_read(self.descriptor, "status"))
        exact = {
            "Pid": str(self.spec.pid),
            "Tgid": str(self.spec.pid),
            "PPid": str(self.spec.parent_pid),
            "TracerPid": "0",
            "Threads": "1",
            "NoNewPrivs": "1",
        }
        if any(status.get(key) != value for key, value in exact.items()):
            raise ValueError("native role/process status differs")
        for key, number in (("Uid", self.spec.native_uid), ("Gid", self.spec.native_gid)):
            if status.get(key, "").split() != [str(number)] * 4:
                raise ValueError("native real/effective/saved/filesystem role differs")
        if "Groups" not in status or status["Groups"].split() not in (
            [],
            [str(self.spec.native_gid)],
        ):
            raise ValueError("unexpected native supplementary groups")
        for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"):
            value = status.get(key, "")
            if not re.fullmatch(r"[0-9a-fA-F]{16}", value) or int(value, 16) != 0:
                raise ValueError("native capabilities must be empty")

    def read_configuration(self, configuration: "DispatchConfiguration") -> dict[str, Digest]:
        from crewshal.linux_envelope import native_working_directory

        argv = _read(self.descriptor, "cmdline")
        environment = _read(self.descriptor, "environ")
        expected_argv = b"\0".join(part.encode() for part in configuration.native_argv) + b"\0"
        if argv != expected_argv:
            raise ValueError("native argv differs from bound dispatch")
        entries = environment.split(b"\0")
        if not entries or entries[-1] != b"":
            raise ValueError("native initial environment lacks NUL framing")
        values: dict[str, str] = {}
        for entry in entries[:-1]:
            key, separator, value = entry.decode("utf-8").partition("=")
            if not separator or not key or key in values:
                raise ValueError("malformed or duplicate native environment")
            values[key] = value
        if values != configuration.native_environment:
            raise ValueError("native initial environment differs from bound dispatch")
        if os.readlink("cwd", dir_fd=self.descriptor) != native_working_directory(configuration):
            raise ValueError("native cwd differs from dispatch")
        if _read(self.descriptor, "cgroup").decode("ascii").strip() != (
            f"0::/{self.spec.worker.relative_path}"
        ):
            raise ValueError("native process is outside retained worker cgroup")
        namespaces = os.open(
            "ns",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=self.descriptor,
        )
        try:
            for name, identity in self.spec.namespaces.items():
                info = os.stat(name, dir_fd=namespaces)
                if (info.st_dev, info.st_ino) != (identity.device, identity.inode):
                    raise ValueError("native namespace identity differs")
        finally:
            os.close(namespaces)
        # exe is a kernel magic link: intentionally follow only this fixed link.
        executable = os.open("exe", os.O_RDONLY | os.O_CLOEXEC, dir_fd=self.descriptor)
        try:
            info = os.fstat(executable)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid == self.spec.native_uid
                or info.st_mode & 0o022
                or info.st_size > 134217728
            ):
                raise ValueError("native executable authority or size differs")
            sha = hashlib.sha256()
            total = 0
            while chunk := os.read(executable, 65536):
                total += len(chunk)
                if total > 134217728:
                    raise ValueError("native executable exceeds bound")
                sha.update(chunk)
            after = os.fstat(executable)

            # Reading may change atime; it does not change executable identity.
            def file_identity(value: os.stat_result) -> tuple[int, ...]:
                return (
                    value.st_dev,
                    value.st_ino,
                    value.st_size,
                    value.st_mode,
                    value.st_uid,
                    value.st_gid,
                    value.st_mtime_ns,
                    value.st_ctime_ns,
                )

            if (
                file_identity(after) != file_identity(info)
                or sha.hexdigest() != self.spec.executable_sha256
            ):
                raise ValueError("native executable bytes or identity differ")
        finally:
            os.close(executable)
        return {"argv": digest(argv), "initial_environment": digest(environment)}

    def verify_pipes(self, stdin_writer: int, stdout_reader: int, stderr_reader: int) -> None:
        descriptors = (stdin_writer, stdout_reader, stderr_reader)
        identities = []
        for handle, mode in zip(descriptors, (os.O_WRONLY, os.O_RDONLY, os.O_RDONLY)):
            info = os.fstat(handle)
            if (
                not stat.S_ISFIFO(info.st_mode)
                or fcntl.fcntl(handle, fcntl.F_GETFL) & os.O_ACCMODE != mode
            ):
                raise ValueError("retained parent pipe direction/type differs")
            identities.append((info.st_dev, info.st_ino))
        if len(set(identities)) != 3:
            raise ValueError("task/stdout/stderr pipes must be distinct")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        directory = os.open("fd", flags, dir_fd=self.descriptor)
        details = -1
        try:
            details = os.open("fdinfo", flags, dir_fd=self.descriptor)
            # A stopped single-thread bootstrap checkpoint must have only stdio.
            # Additional transport or broker FDs are not silently accepted.
            names: set[str] = set()
            with os.scandir(directory) as entries:
                for entry in entries:
                    names.add(entry.name)
                    if len(names) > 3:
                        raise ValueError("unexpected inherited native file descriptor")
            if names != {"0", "1", "2"}:
                raise ValueError("unexpected inherited native file descriptor")
            for number, (_, inode), mode in zip(
                range(3), identities, (os.O_RDONLY, os.O_WRONLY, os.O_WRONLY)
            ):
                if os.readlink(str(number), dir_fd=directory) != f"pipe:[{inode}]":
                    raise ValueError("native stdio does not match retained pipe")
                value = _fields(_read(details, str(number))).get("flags", "")
                if not re.fullmatch(r"[0-7]+", value) or int(value, 8) & os.O_ACCMODE != mode:
                    raise ValueError("native stdio direction differs")
        finally:
            os.close(directory)
            if details >= 0:
                os.close(details)


def _aggregate_readback(aggregate: OwnedCgroup, worker: OwnedCgroup) -> dict[str, str]:
    if str(PurePosixPath(worker.identity.relative_path).parent) != aggregate.identity.relative_path:
        raise ValueError("worker is outside retained aggregate")
    # Path strings alone cannot prove ancestry: compare actual retained directory.
    parent = os.stat("..", dir_fd=worker.descriptor)
    if (parent.st_dev, parent.st_ino) != (aggregate.identity.device, aggregate.identity.inode):
        raise ValueError("worker descriptor parent differs from retained aggregate")
    controls = {
        name: aggregate._read(name)
        for name in ("memory.max", "memory.swap.max", "cpu.max", "pids.max", "cgroup.type")
    }
    if controls != {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "128",
        "cgroup.type": "domain",
    }:
        raise ValueError("aggregate controls differ from original ceilings")
    if aggregate._read("cgroup.procs"):
        raise ValueError("owned aggregate must have no direct processes")
    for name, required in (("memory.events", {"max", "oom", "oom_kill"}), ("pids.events", {"max"})):
        events = _counters(aggregate._read(name), required)
        if any(events[key] != 0 for key in required):
            raise ValueError("aggregate has resource-refusal history")
    return controls


class NativeAdmissionReceipt(Contract):
    schema_version: Literal[1] = 1
    spec: NativeAdmissionSpec
    configuration: Digest
    argv: Digest
    initial_environment: Digest
    aggregate_controls: dict[str, str]
    stdout_pipe: NamespaceIdentity
    stderr_pipe: NamespaceIdentity
    stdin_pipe: NamespaceIdentity | None = None
    started: datetime
    started_monotonic: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False

    @model_validator(mode="after")
    def bindings(self) -> Self:
        if self.configuration != self.spec.configuration:
            raise ValueError("admission receipt/spec configuration differs")
        if self.started.tzinfo is None or self.started.utcoffset() is None:
            raise ValueError("admission receipt requires aware launch clock")
        if self.stdout_pipe == self.stderr_pipe:
            raise ValueError("admission receipt requires distinct capture pipes")
        if self.stdin_pipe is not None and self.stdin_pipe in (self.stdout_pipe, self.stderr_pipe):
            raise ValueError("admission receipt requires distinct native stdin")
        return self


class NativeAdmissionRecord(Record):
    """Coordinator linkage; the embedded observation grants no authority."""

    run_id: Identifier
    attempt_id: Identifier
    handle: Identifier
    dispatch: Digest
    receipt: NativeAdmissionReceipt
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False


@dataclass(frozen=True)
class AdmittedNative:
    """Retained resources owned by the caller. No automatic release or retry."""

    child: subprocess.Popen[bytes]
    proc: RetainedProc
    worker: OwnedCgroup
    aggregate: OwnedCgroup
    receipt: NativeAdmissionReceipt
    configuration: "DispatchConfiguration"
    started: datetime
    started_monotonic: float
    receipt_digest: Digest

    def _verify_binding(self) -> None:
        if record_digest(self.receipt) != self.receipt_digest:
            raise ValueError("admitted receipt changed")
        if (
            self.started != self.receipt.started
            or self.started_monotonic != self.receipt.started_monotonic
        ):
            raise ValueError("admitted launch clock changed")
        if record_digest(self.configuration) != self.receipt.configuration:
            raise ValueError("admitted configuration changed")
        if (
            self.worker.identity != self.receipt.spec.worker
            or self.aggregate.identity != self.receipt.spec.aggregate
            or self.proc.spec != self.receipt.spec
        ):
            raise ValueError("admitted retained identities changed")
        _current_source(self.configuration)
        _aggregate_readback(self.aggregate, self.worker)
        if self.child.pid != self.receipt.spec.pid:
            raise ValueError("retained child handle changed")

    def verify_terminal(self, expected_exit: int) -> None:
        """Immediate native/worker readback; no signal, wait, grace or release.

        The watchdog, namespace parent and wrapper retain their separate gates.
        No native-exit observation supplies a storage or namespace closure oracle.
        """
        self._verify_binding()
        self.proc.verify_exited()
        result = self.child.poll()
        if result is None or result != expected_exit:
            raise ValueError("retained native exit/reap differs from capture")
        sample = self.worker.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("retained worker repopulated after native capture")
        self._verify_binding()
        self.proc.verify_exited()

    def capture(self, *, cancelled: Callable[[], bool]) -> CapturedProcess:
        # Trusted launcher must release the stopped child separately, after its
        # exact authority/deadline/envelope gates. Receipt never authorizes that.
        self._verify_binding()
        if self.child.stdout is None or self.child.stderr is None:
            raise ValueError("retained child capture pipes missing")
        exchange = None
        stdin_stream = None
        if self.configuration.native_interface == "app_server_stdio":
            from crewshal.app_server import AppServerExchange

            profile = self.configuration.app_server_profile
            if profile is None or self.receipt.stdin_pipe is None or self.child.stdin is None:
                raise ValueError("admitted app-server profile/stdin missing")
            info = os.fstat(self.child.stdin.fileno())
            if (info.st_dev, info.st_ino) != (
                self.receipt.stdin_pipe.device,
                self.receipt.stdin_pipe.inode,
            ):
                raise ValueError("admitted stdin pipe identity changed")
            exchange = AppServerExchange.from_profile(profile)
            stdin_stream = self.child.stdin
        for stream, expected in (
            (self.child.stdout, self.receipt.stdout_pipe),
            (self.child.stderr, self.receipt.stderr_pipe),
        ):
            info = os.fstat(stream.fileno())
            if (info.st_dev, info.st_ino) != (expected.device, expected.inode):
                raise ValueError("admitted capture pipe identity changed")
        captured = capture_attached_process(
            self.child,
            self.worker,
            self.child.stdout.fileno(),
            self.child.stderr.fileno(),
            started=self.started,
            started_monotonic=self.started_monotonic,
            cancelled=cancelled,
            exchange=exchange,
            stdin_stream=stdin_stream,
        )
        if captured.observation.tree_stopped:
            if captured.observation.exit_code is None:
                raise ValueError("native exit missing from terminal capture")
            self.verify_terminal(captured.observation.exit_code)
        return captured


def _current_source(configuration: "DispatchConfiguration") -> None:
    from pathlib import Path
    from crewshal.dispatch import (
        DispatchConfiguration,
        SOURCE_FILES,
        prepare_dispatch_configuration,
    )

    reader = _Reader(Path(__file__).parent)
    if configuration.source_sha256 != {name: digest(reader.read(name)) for name in SOURCE_FILES}:
        raise ValueError("admission dispatch source changed")
    expected = prepare_dispatch_configuration(
        configuration.selection,
        preparation_digest=configuration.preparation_digest,
        linux_envelope=configuration.linux_envelope,
        app_server_profile=configuration.app_server_profile,
    )
    expected = DispatchConfiguration.model_validate(
        {
            **expected.model_dump(),
            "task_digest": configuration.task_digest,
            "launch_binding": configuration.launch_binding,
        }
    )
    if (
        configuration != expected
        or configuration.launch_binding is None
        or configuration.launch_binding.task != configuration.task_digest
    ):
        raise ValueError("admission native configuration differs from pinned dispatch")


def admit_native_process(
    child: subprocess.Popen[bytes],
    proc: RetainedProc,
    worker: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: "DispatchConfiguration",
    *,
    started: datetime,
    started_monotonic: float,
) -> AdmittedNative:
    """Read an already-stopped retained child; no process, signal, writes or authority.

    Production callers must obtain proc/cgroup handles from their Linux attach
    entry points. Internal constructors are trusted coordinator seams and permit
    explicit offline fixtures; their mere construction establishes no capability.
    """
    from crewshal.dispatch import DispatchConfiguration

    configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
    spec = proc.spec
    if (
        not isinstance(child, subprocess.Popen)
        or child.pid != spec.pid
        or child.poll() is not None
        or configuration.launch_binding is None
        or configuration.task_digest is None
        or spec.configuration != record_digest(configuration)
        or worker.identity != spec.worker
        or aggregate.identity != spec.aggregate
        or child.stdin is None
        or child.stdout is None
        or child.stderr is None
    ):
        raise ValueError("native retained child/configuration binding differs")
    elapsed = time.monotonic() - started_monotonic
    if (
        type(started_monotonic) not in (int, float)
        or not math.isfinite(started_monotonic)
        or not 0 <= elapsed < 5
        or started.tzinfo is None
        or started.utcoffset() is None
    ):
        raise ValueError("native launch clock invalid or original deadline expired")
    _current_source(configuration)
    proc.verify_stopped()
    controls = _aggregate_readback(aggregate, worker)
    sample = worker.sample()
    if not sample.populated or sample.direct_pids != [spec.pid]:
        raise ValueError("retained worker population differs from native child")
    if (
        any(sample.memory_events[name] for name in ("max", "oom", "oom_kill"))
        or sample.pids_events["max"]
    ):
        raise ValueError("worker has resource-refusal history")
    values = proc.read_configuration(configuration)
    proc.verify_pipes(child.stdin.fileno(), child.stdout.fileno(), child.stderr.fileno())
    proc.verify_stopped()
    if child.poll() is not None or time.monotonic() - started_monotonic >= 5:
        raise ValueError("native child exited or original deadline expired during admission")
    receipt = NativeAdmissionReceipt(
        spec=NativeAdmissionSpec.model_validate_json(spec.model_dump_json()),
        configuration=record_digest(configuration),
        aggregate_controls=controls,
        argv=values["argv"],
        initial_environment=values["initial_environment"],
        stdin_pipe=NamespaceIdentity(
            device=os.fstat(child.stdin.fileno()).st_dev,
            inode=os.fstat(child.stdin.fileno()).st_ino,
        ),
        stdout_pipe=NamespaceIdentity(
            device=os.fstat(child.stdout.fileno()).st_dev,
            inode=os.fstat(child.stdout.fileno()).st_ino,
        ),
        stderr_pipe=NamespaceIdentity(
            device=os.fstat(child.stderr.fileno()).st_dev,
            inode=os.fstat(child.stderr.fileno()).st_ino,
        ),
        started=started,
        started_monotonic=started_monotonic,
    )
    return AdmittedNative(
        child,
        proc,
        worker,
        aggregate,
        receipt,
        configuration,
        started,
        started_monotonic,
        record_digest(receipt),
    )


def collect_admitted_codex(
    store: "CoordinatorStore",
    dispatch: "CodexDispatch",
    admitted: AdmittedNative,
    *,
    handle: str,
    cancelled: Callable[[], bool],
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: FrozenCandidate,
    candidate: Path,
    frozen_target: Path,
    allowed_paths: list[str],
    watchdog: "OwnedWatchdogLifetime | None" = None,
) -> tuple["CodexCollection", SupervisionReceipt]:
    """Persist retained admission and supervised collection in one transaction.

    Linux/subscription collection requires the original watchdog lifetime. The
    earlier envelope-free portable seam remains offline observation data only.
    Capture uses only original owned stop/recovery; release/startup and outer
    terminal readback remain separate qualified launcher obligations. No launch,
    credential access or execution/spend authority is supplied here.
    """
    from crewshal.supervisor import collect_supervised_codex

    if not isinstance(admitted, AdmittedNative):
        raise ValueError("retained native admission required")
    if admitted.child.stdout is None or admitted.child.stderr is None:
        raise ValueError("retained admitted capture pipes missing")
    return collect_supervised_codex(
        store,
        dispatch,
        admitted.child,
        admitted.worker,
        admitted.child.stdout.fileno(),
        admitted.child.stderr.fileno(),
        handle=handle,
        started=admitted.started,
        started_monotonic=admitted.started_monotonic,
        cancelled=cancelled,
        expected_run_version=expected_run_version,
        expected_attempt_version=expected_attempt_version,
        token=token,
        initial=initial,
        candidate=candidate,
        frozen_target=frozen_target,
        allowed_paths=allowed_paths,
        admitted=admitted,
        watchdog=watchdog,
    )
