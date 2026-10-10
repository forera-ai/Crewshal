"""Bounded capture of an already admitted Linux worker; no startup or credentials.

Only a future qualified launcher may supply the process, pipe descriptors and
prospectively retained cgroup identity. This module does not create an envelope,
authenticate authority or prove that processes cannot leave their cgroup.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import os
import io
import platform
from pathlib import Path, PurePosixPath
import selectors
import stat
import sys
import time
from typing import TYPE_CHECKING, Annotated, IO, Callable, Literal, Protocol, Self

from pydantic import Field, field_validator, model_validator

from crewshal.candidate import FrozenCandidate
from crewshal.contracts import (
    Attempt,
    Digest,
    Evidence,
    Identifier,
    Record,
    Run,
    record_digest,
)
from crewshal.integration import CodexCollection, _collect_codex_attempt_locked, scope_digest
from crewshal.model import Contract, digest
from crewshal.runtime import ProcessObservation, STREAM_BYTES

if TYPE_CHECKING:
    from crewshal.app_server import AppServerExchange
    from crewshal.admission import AdmittedNative
    from crewshal.linux_setup import OwnedWatchdogLifetime
    from crewshal.durable import CoordinatorStore
    from crewshal.dispatch import CodexDispatch


class CgroupIdentity(Contract):
    """Identity retained by trusted setup, not discovered from worker output."""

    relative_path: str
    device: Annotated[int, Field(ge=0)]
    inode: Annotated[int, Field(gt=0)]

    @field_validator("relative_path")
    @classmethod
    def owned_subtree(cls, value: str) -> str:
        path = PurePosixPath(value)
        if (
            path.is_absolute()
            or len(path.parts) < 2
            or str(path) != value
            or any(part in {".", ".."} for part in path.parts)
            or "\\" in value
            or "\x00" in value
        ):
            raise ValueError("exact non-root owned cgroup subtree required")
        return value


class CgroupSample(Contract):
    identity: CgroupIdentity
    controls: dict[str, str]
    populated: bool
    direct_pids: list[Annotated[int, Field(gt=0)]]
    memory_events: dict[str, Annotated[int, Field(ge=0)]]
    pids_events: dict[str, Annotated[int, Field(ge=0)]]


def _counters(raw: str, required: set[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in raw.splitlines():
        parts = line.split()
        if (
            len(parts) != 2
            or parts[0] in result
            or not parts[1].isascii()
            or not parts[1].isdigit()
        ):
            raise ValueError("malformed or duplicate kernel counter")
        result[parts[0]] = int(parts[1])
    if not required <= result.keys():
        raise ValueError("missing kernel counter")
    return result


def _require_cgroup2(descriptor: int) -> None:
    """Read filesystem type from the actual FD, without exposing host paths.

    The supported 64-bit Linux statfs ABI starts with a native long f_type.
    Exact libc/kernel installation and inherited-FD behavior still require the
    separately approved Linux qualification; this check grants no admission.
    """
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise ValueError("supported Linux cgroup filesystem readback unavailable")
    result = ctypes.create_string_buffer(256)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.fstatfs(ctypes.c_int(descriptor), ctypes.byref(result)) != 0:
        raise OSError(ctypes.get_errno(), "retained cgroup filesystem readback failed")
    if ctypes.c_long.from_buffer(result).value != 0x63677270:
        raise ValueError("retained descriptor is not a cgroup2 filesystem")


class OwnedCgroup:
    """Pinned directory FD; no path-based stop or PID/process-group guessing."""

    def __init__(self, descriptor: int, identity: CgroupIdentity):
        # Construction is coordinator-internal. attach() is the Linux entry point.
        self.descriptor = os.dup(descriptor)
        self.identity = CgroupIdentity.model_validate_json(identity.model_dump_json())
        try:
            self._verify()
        except BaseException:
            self.close()
            raise

    @classmethod
    def attach_inherited(cls, descriptor: int, identity: CgroupIdentity) -> "OwnedCgroup":
        """Duplicate a verified inherited kernel FD inside the copied root.

        The original outer attachment checks recursive accounting mount options.
        This receives that actual object, never recreates it from capsule/path
        text, and never mounts the ambient host cgroup tree for the parent.
        """
        _require_cgroup2(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError("inherited cgroup must exclude worker write authority")
        return cls(descriptor, identity)

    @classmethod
    def attach(cls, identity: CgroupIdentity) -> "OwnedCgroup":
        if sys.platform != "linux":
            raise ValueError("Linux cgroup supervision unavailable on this platform")
        identity = CgroupIdentity.model_validate_json(identity.model_dump_json())
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        descriptor = os.open("/sys/fs/cgroup", flags)
        try:
            root = os.fstat(descriptor)
            if root.st_uid != 0 or root.st_mode & 0o022:
                raise ValueError("cgroup root must exclude worker write authority")
            device = f"{os.major(root.st_dev)}:{os.minor(root.st_dev)}"
            # Require the standard cgroup2 mount, not an ordinary directory with
            # forged controller files. No subprocess/helper or ambient settings.
            mount = False
            with open("/proc/self/mountinfo", "rb") as stream:
                raw = stream.read(65537)
            if len(raw) > 65536:
                raise ValueError("mount inventory exceeds bound")
            for line in raw.decode("ascii").splitlines():
                before, separator, after = line.partition(" - ")
                fields = before.split()
                if separator and len(fields) >= 6 and after.split()[0] == "cgroup2":
                    if fields[2:5] == [device, "/", "/sys/fs/cgroup"]:
                        options = set(fields[5].split(",")) | set(after.split()[-1].split(","))
                        if options & {"memory_localevents", "pids_localevents"}:
                            raise ValueError("recursive resource event accounting required")
                        mount = True
            if not mount:
                raise ValueError("standard cgroup2 mount identity unavailable")
            for part in PurePosixPath(identity.relative_path).parts:
                child = os.open(part, flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
                info = os.fstat(descriptor)
                if info.st_uid != 0 or info.st_mode & 0o022:
                    raise ValueError("cgroup must exclude worker write authority")
            return cls(descriptor, identity)
        finally:
            os.close(descriptor)

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1

    def _verify(self) -> None:
        info = os.fstat(self.descriptor)
        if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != (
            self.identity.device,
            self.identity.inode,
        ):
            raise ValueError("owned cgroup descriptor identity changed")

    def _read(self, name: str) -> str:
        self._verify()
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
            dir_fd=self.descriptor,
        )
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("kernel interface must be a regular control file")
            raw = os.read(descriptor, 4097)
            if len(raw) > 4096:
                raise ValueError("kernel control readback exceeds bound")
            return raw.decode("ascii").strip()
        finally:
            os.close(descriptor)

    def sample(self) -> CgroupSample:
        controls = {
            name: self._read(name)
            for name in ("memory.max", "memory.swap.max", "cpu.max", "pids.max", "cgroup.type")
        }
        if controls != {
            "memory.max": "134217728",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "32",
            "cgroup.type": "domain",
        }:
            raise ValueError("worker cgroup controls differ from original ceilings")
        events = _counters(self._read("cgroup.events"), {"populated", "frozen"})
        if any(events[key] not in {0, 1} for key in ("populated", "frozen")):
            raise ValueError("invalid cgroup population/freezer state")
        pids = self._read("cgroup.procs").splitlines()
        if any(not pid.isascii() or not pid.isdigit() or int(pid) <= 0 for pid in pids):
            raise ValueError("invalid cgroup process inventory")
        return CgroupSample(
            identity=self.identity,
            controls=controls,
            populated=bool(events["populated"]),
            direct_pids=[int(pid) for pid in pids],
            memory_events=_counters(self._read("memory.events"), {"max", "oom", "oom_kill"}),
            pids_events=_counters(self._read("pids.events"), {"max"}),
        )

    def stop(self) -> None:
        """Only kill the pinned owned subtree, including descendants."""
        self._verify()
        descriptor = os.open(
            "cgroup.kill",
            os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
            dir_fd=self.descriptor,
        )
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("invalid cgroup kill interface")
            if os.write(descriptor, b"1") != 1:
                raise ValueError("incomplete owned cgroup stop")
        finally:
            os.close(descriptor)


class ProcessHandle(Protocol):
    """Actual Popen-like child handle retained by the qualified trusted launcher."""

    @property
    def pid(self) -> int: ...

    def poll(self) -> int | None: ...


@dataclass(frozen=True)
class CapturedProcess:
    observation: ProcessObservation
    stdout: bytes
    stderr: bytes
    initial: CgroupSample
    final: CgroupSample | None
    overflow: bool
    stop_error: bool


def _quota(sample: CgroupSample) -> bool:
    return any(sample.memory_events[key] for key in ("max", "oom", "oom_kill")) or bool(
        sample.pids_events["max"]
    )


def capture_attached_process(
    process: ProcessHandle,
    group: OwnedCgroup,
    stdout_descriptor: int,
    stderr_descriptor: int,
    *,
    started: datetime,
    started_monotonic: float,
    cancelled: Callable[[], bool],
    exchange: "AppServerExchange | None" = None,
    stdin_stream: IO[bytes] | None = None,
) -> CapturedProcess:
    """Capture supplied pipes; never start/retry a process or infer child identity.

    Launcher owns child, timestamps and pipe descriptors, with no other pipe
    readers. Five seconds include elapsed time before attachment. Empty recursive
    population, reaped child and both EOFs are separate requirements. Failure to
    observe stop never authorizes freeze. Remaining owned work needs reconciliation.
    """
    # Reuse the closed time contract to reject naive/nonfinite launch data.
    ProcessObservation(
        started=started,
        ended=started,
        elapsed_seconds=started_monotonic,
        exit_code=None,
        stdout_complete=False,
        stderr_complete=False,
        tree_stopped=False,
    )
    attached = time.monotonic()
    if (exchange is None) != (stdin_stream is None):
        raise ValueError("app-server exchange and retained stdin must be supplied together")
    if stdin_stream is not None and (
        type(stdin_stream) is not io.FileIO or not stdin_stream.writable()
    ):
        raise ValueError("app-server stdin must be retained unbuffered FileIO")
    stdin_descriptor = stdin_stream.fileno() if stdin_stream is not None else None
    if started_monotonic > attached or stdout_descriptor == stderr_descriptor:
        raise ValueError("invalid launch clock or aliased capture descriptors")
    for descriptor in (stdout_descriptor, stderr_descriptor):
        if not stat.S_ISFIFO(os.fstat(descriptor).st_mode):
            raise ValueError("capture requires separate native pipe descriptors")
    pipe_info = [os.fstat(d) for d in (stdout_descriptor, stderr_descriptor)]
    if (pipe_info[0].st_dev, pipe_info[0].st_ino) == (pipe_info[1].st_dev, pipe_info[1].st_ino):
        raise ValueError("aliased native pipe descriptions")
    if stdin_descriptor is not None:
        info = os.fstat(stdin_descriptor)
        if not stat.S_ISFIFO(info.st_mode) or (info.st_dev, info.st_ino) in {
            (item.st_dev, item.st_ino) for item in pipe_info
        }:
            raise ValueError("app-server requires a separate retained stdin pipe")
    initial = group.sample()
    if _quota(initial):
        raise ValueError("fresh owned worker requires zero resource-refusal counters")
    buffers = [bytearray(), bytearray()]
    eof = [False, False]
    overflow = False
    stop_error = False
    termination: (
        Literal["timeout", "cancelled", "quota", "signal", "interrupted", "refusal"] | None
    ) = None
    stopped_at: float | None = None
    final: CgroupSample | None = initial
    exit_code: int | None = None
    originals = [os.get_blocking(d) for d in (stdout_descriptor, stderr_descriptor)]
    stdin_blocking = os.get_blocking(stdin_descriptor) if stdin_descriptor is not None else None
    pending = bytearray()
    written = 0
    parsed = 0
    with selectors.DefaultSelector() as selector:
        try:
            for index, descriptor in enumerate((stdout_descriptor, stderr_descriptor)):
                os.set_blocking(descriptor, False)
                selector.register(descriptor, selectors.EVENT_READ, index)
            if exchange is not None and stdin_descriptor is not None:
                os.set_blocking(stdin_descriptor, False)
                pending.extend(exchange.start())
                if len(pending) > STREAM_BYTES:
                    raise ValueError("app-server initial input exceeds capture bound")
                selector.register(stdin_descriptor, selectors.EVENT_WRITE, 2)
            while True:
                now = time.monotonic()
                elapsed = now - started_monotonic
                if elapsed < 0:
                    raise ValueError("monotonic launch clock reversed")
                exit_code = process.poll()
                try:
                    final = group.sample()
                except (OSError, ValueError, UnicodeError):
                    final = None
                    termination = termination or "interrupted"
                if cancelled():
                    termination = termination or "cancelled"
                elif final is not None and _quota(final):
                    termination = termination or "quota"
                elif elapsed >= 5 and not (
                    exit_code is not None
                    and final is not None
                    and not final.populated
                    and not final.direct_pids
                    and all(eof)
                ):
                    termination = termination or "timeout"
                elif exit_code is not None and final is not None and final.populated:
                    termination = termination or "interrupted"
                if exit_code is not None and exit_code < 0:
                    termination = termination or "signal"
                if termination is not None and stopped_at is None:
                    stopped_at = now
                    try:
                        group.stop()
                    except (OSError, ValueError):
                        stop_error = True
                if (
                    stdin_stream is not None
                    and not stdin_stream.closed
                    and (
                        termination is not None
                        or (exchange is not None and exchange.protocol_completed and not pending)
                    )
                ):
                    if stdin_descriptor is not None and stdin_descriptor in selector.get_map():
                        selector.unregister(stdin_descriptor)
                    stdin_stream.close()
                tree_stopped = (
                    exit_code is not None
                    and final is not None
                    and not final.populated
                    and not final.direct_pids
                )
                if tree_stopped and all(eof):
                    break
                if elapsed >= 10 or (stopped_at is not None and now - stopped_at >= 1):
                    break
                for key, _ in selector.select(0.01):
                    index = key.data
                    if index == 2:
                        if termination is not None:
                            continue
                        if cancelled():
                            termination = termination or "cancelled"
                            continue
                        if _quota(group.sample()):
                            termination = termination or "quota"
                            continue
                        if time.monotonic() - started_monotonic >= 5:
                            termination = termination or "timeout"
                            continue
                        if not pending:
                            selector.unregister(key.fd)
                            continue
                        try:
                            count = os.write(key.fd, pending)
                        except BlockingIOError:
                            continue
                        except BrokenPipeError:
                            termination = termination or "interrupted"
                            selector.unregister(key.fd)
                            continue
                        written += count
                        del pending[:count]
                        if written + len(pending) > STREAM_BYTES:
                            termination = termination or "quota"
                        if not pending:
                            selector.unregister(key.fd)
                        continue
                    try:
                        chunk = os.read(key.fd, min(4096, STREAM_BYTES - len(buffers[index]) + 1))
                    except BlockingIOError:
                        continue
                    if not chunk:
                        eof[index] = True
                        selector.unregister(key.fd)
                        continue
                    remaining = STREAM_BYTES - len(buffers[index])
                    buffers[index].extend(chunk[:remaining])
                    if index == 0 and exchange is not None and termination is None:
                        try:
                            while True:
                                end = buffers[0].find(b"\n", parsed)
                                if end < 0:
                                    break
                                messages = exchange.feed(bytes(buffers[0][parsed : end + 1]))
                                parsed = end + 1
                                for message in messages:
                                    if written + len(pending) + len(message) > STREAM_BYTES:
                                        raise ValueError("app-server input exceeds capture bound")
                                    pending.extend(message)
                                if (
                                    pending
                                    and stdin_descriptor is not None
                                    and stdin_descriptor not in selector.get_map()
                                ):
                                    selector.register(stdin_descriptor, selectors.EVENT_WRITE, 2)
                        except (ValueError, UnicodeError):
                            termination = termination or "refusal"
                    if len(chunk) > remaining:
                        overflow = True
                        termination = termination or "quota"
                        # Never pretend the truncated stream is complete.
                        selector.unregister(key.fd)
        except BaseException:
            # A reader/poll/cancellation failure cannot leave an implicit retry.
            # Best-effort owned stop is not a successful stop observation.
            try:
                group.stop()
            except (OSError, ValueError):
                pass
            raise
        finally:
            for descriptor, blocking in zip((stdout_descriptor, stderr_descriptor), originals):
                os.set_blocking(descriptor, blocking)
            if stdin_stream is not None and not stdin_stream.closed and stdin_blocking is not None:
                os.set_blocking(stdin_stream.fileno(), stdin_blocking)
    ended = datetime.now(timezone.utc)
    elapsed = time.monotonic() - started_monotonic
    if ended < started:
        raise ValueError("wall clock reversed during capture; reconciliation required")
    observation = ProcessObservation(
        started=started,
        ended=ended,
        elapsed_seconds=elapsed,
        exit_code=exit_code,
        termination=termination,
        stdout_complete=eof[0],
        stderr_complete=eof[1],
        tree_stopped=(
            exit_code is not None
            and final is not None
            and not final.populated
            and not final.direct_pids
            and not stop_error
        ),
    )
    return CapturedProcess(
        observation,
        bytes(buffers[0]),
        bytes(buffers[1]),
        initial,
        final,
        overflow,
        stop_error,
    )


class SupervisionReceipt(Record):
    run_id: Identifier
    attempt_id: Identifier
    handle: Identifier
    pid: Annotated[int, Field(gt=0)]
    dispatch: Digest
    collection: Digest
    admission: Digest | None = None
    initial: CgroupSample
    final: CgroupSample | None
    observation: ProcessObservation
    stdout: Digest
    stderr: Digest
    overflow: bool
    stop_error: bool
    execution_allowed: Literal[False] = False

    @model_validator(mode="after")
    def stop_consistency(self) -> Self:
        if self.final is not None and self.final.identity != self.initial.identity:
            raise ValueError("supervision cgroup identity changed")
        if self.observation.tree_stopped and (
            self.observation.exit_code is None
            or self.final is None
            or self.final.populated
            or self.final.direct_pids
            or self.stop_error
        ):
            raise ValueError("supervision stop claim contradicts independent readback")
        if self.overflow and self.observation.stdout_complete and self.observation.stderr_complete:
            raise ValueError("overflow cannot claim both streams complete")
        return self


def collect_supervised_codex(
    store: "CoordinatorStore",
    dispatch: "CodexDispatch",
    process: ProcessHandle,
    group: OwnedCgroup,
    stdout_descriptor: int,
    stderr_descriptor: int,
    *,
    handle: str,
    started: datetime,
    started_monotonic: float,
    cancelled: Callable[[], bool],
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: FrozenCandidate,
    candidate: Path,
    frozen_target: Path,
    allowed_paths: list[str],
    admitted: "AdmittedNative | None" = None,
    watchdog: "OwnedWatchdogLifetime | None" = None,
) -> tuple[CodexCollection, SupervisionReceipt]:
    """Bind independent supervision capture to existing collection atomically.

    Inputs are trusted coordinator handles from a future admitted launch, not a
    worker/CLI endpoint. This entry point supplies no launch or spend authority.
    Actual Linux attachment/placement and gate authentication remain unqualified.
    """
    from crewshal.durable import Conflict
    from crewshal.dispatch import CodexDispatch, prepare_dispatch_configuration

    dispatch = CodexDispatch.model_validate_json(dispatch.model_dump_json())
    request = dispatch.request
    configuration = dispatch.configuration
    subscription = configuration.native_interface == "app_server_stdio"
    if subscription and admitted is None:
        raise ValueError("app-server collection requires retained admitted stdin")
    if watchdog is not None and admitted is None:
        raise ValueError("owned watchdog collection requires original admitted native")
    if watchdog is not None or (
        admitted is not None and (subscription or configuration.linux_envelope is not None)
    ):
        from crewshal.linux_setup import OwnedWatchdogLifetime

        if type(watchdog) is not OwnedWatchdogLifetime:
            raise ValueError("admitted collection requires original owned watchdog lifetime")
    if configuration.task_digest is None or configuration.launch_binding is None:
        raise ValueError("unbound dispatch configuration")
    with store.transaction():
        attempt, attempt_version = store.get("attempt", request.attempt_id, Attempt)
        if attempt is None:
            raise ValueError("known acknowledged attempt required")
        store._lease(attempt.run_id, token)
        run, run_version = store.get("run", attempt.run_id, Run)
        if (run_version, attempt_version) != (expected_run_version, expected_attempt_version):
            raise Conflict("supervision state version changed")
        if (
            run is None
            or run.state != "ready"
            or attempt.state != "acknowledged"
            or attempt.handle != handle
            or attempt.binding != request.binding
            or run.binding != request.binding
            or attempt.role != "implementation"
            or attempt.provider != request.identity.provider
            or attempt.model != request.identity.model
            or type(process.pid) is not int
            or process.pid <= 0
        ):
            raise ValueError("supervision process/launch/attempt binding differs")
        from crewshal.contracts import Task

        task, _ = store.get("task", run.task_id, Task)
        if (
            task is None
            or configuration
            != prepare_dispatch_configuration(
                configuration.selection,
                preparation_digest=configuration.preparation_digest,
                task=task,
                binding=request.binding,
                linux_envelope=configuration.linux_envelope,
                app_server_profile=configuration.app_server_profile,
            )
            or request.identity.configuration != record_digest(configuration)
            or dispatch.qualification.configuration != request.identity.configuration
            or dispatch.task_digest != record_digest(task)
            or request.requirement != task.requirement
            or (not subscription and request.requirement + "\n" != configuration.native_stdin)
            or (
                subscription
                and (
                    configuration.app_server_profile is None
                    or request.requirement != configuration.app_server_profile.requirement
                )
            )
            or request.identity.native_interface != configuration.native_interface
            or request.identity.app_server_profile != configuration.app_server_profile
            or configuration.selection.provider != request.identity.provider
            or configuration.selection.model != request.identity.model
            or configuration.selection.destination is None
            or configuration.selection.billing_mode == "unresolved"
            or configuration.selection.credential_treatment
            != ("native_managed_private_home" if subscription else "external_scoped_channel")
            or dispatch.qualification.host_os != "linux"
            or dispatch.qualification.architecture != "aarch64"
            or dispatch.qualification.runtime != "codex-rust-v0.160.1"
            or len(task.checks) != 1
            or task.checks[0].argv != configuration.validator_argv
            or task.checks[0].cwd != "."
            or task.review_required
            or task.independent_provider
        ):
            raise ValueError("supervision source/task/configuration changed")
        if (
            request.binding.candidate != record_digest(initial)
            or request.binding.scope != scope_digest(allowed_paths)
            or allowed_paths != ["README.md"]
            or frozen_target.exists()
            or frozen_target.is_symlink()
        ):
            raise ValueError("supervision snapshot/scope or retained freeze target differs")
        admission_fingerprint = None
        if admitted is not None:
            from crewshal.admission import AdmittedNative, NativeAdmissionRecord

            if (
                not isinstance(admitted, AdmittedNative)
                or admitted.child is not process
                or admitted.worker is not group
                or admitted.configuration != configuration
                or admitted.started != started
                or admitted.started_monotonic != started_monotonic
                or admitted.child.stdout is None
                or admitted.child.stderr is None
                or admitted.child.stdout.fileno() != stdout_descriptor
                or admitted.child.stderr.fileno() != stderr_descriptor
                or record_digest(admitted.receipt) != admitted.receipt_digest
            ):
                raise ValueError("admitted supervision input differs")
            admission = NativeAdmissionRecord(
                id=f"admission:{digest(attempt.id.encode())}",
                run_id=run.id,
                attempt_id=attempt.id,
                handle=handle,
                dispatch=record_digest(dispatch),
                receipt=admitted.receipt,
            )
            # Both immutable private readback and SQLite linkage are retained.
            # Failure rolls records/events back; filesystem artifacts remain.
            admission_fingerprint = record_digest(admission)
            store._artifact(admission_fingerprint, admission.model_dump_json().encode())
            store._put("admission", admission.id, admission, 0)
            if watchdog is not None:
                watchdog.verify_native_binding(admitted)
                if hasattr(watchdog, "_collection_attempted"):
                    raise ValueError("owned native collection is one-shot; no retry")
                setattr(watchdog, "_collection_attempted", True)
            captured = admitted.capture(cancelled=cancelled)
            if watchdog is not None:
                setattr(watchdog, "_native_capture", captured)
            if record_digest(admitted.receipt) != admitted.receipt_digest:
                raise ValueError("admitted receipt changed during capture")
            if watchdog is not None and captured.observation.tree_stopped:
                terminal = watchdog.terminal(
                    recovery_already_attempted=captured.observation.termination is not None
                )
                if (
                    terminal.errors
                    or not terminal.worker_empty
                    or not terminal.watchdog_exited
                    or not terminal.watchdog_reaped
                    or captured.observation.exit_code is None
                ):
                    raise ValueError("original watchdog terminal readback incomplete before freeze")
                watchdog.verify_native_terminal(admitted, captured.observation.exit_code)
        else:
            captured = capture_attached_process(
                process,
                group,
                stdout_descriptor,
                stderr_descriptor,
                started=started,
                started_monotonic=started_monotonic,
                cancelled=cancelled,
            )
        collection = _collect_codex_attempt_locked(
            store,
            attempt_id=attempt.id,
            current=request.binding,
            expected_run_version=expected_run_version,
            expected_attempt_version=expected_attempt_version,
            token=token,
            initial=initial,
            candidate=candidate,
            frozen_target=frozen_target,
            allowed_paths=allowed_paths,
            identity=request.identity,
            expected_configuration=record_digest(configuration),
            observation=captured.observation,
            stdout=captured.stdout,
            stderr=captured.stderr,
        )
        if admitted is not None and collection.frozen is not None:
            if watchdog is not None:
                setattr(watchdog, "_frozen_collection", collection)
            if captured.observation.exit_code is None:
                raise ValueError("native exit missing after freeze")
            if watchdog is not None:
                watchdog.verify_native_terminal(admitted, captured.observation.exit_code)
            else:
                admitted.verify_terminal(captured.observation.exit_code)
        receipt = SupervisionReceipt(
            id=f"supervision:{digest(attempt.id.encode())}",
            run_id=run.id,
            attempt_id=attempt.id,
            handle=handle,
            pid=process.pid,
            dispatch=record_digest(dispatch),
            collection=record_digest(collection),
            admission=admission_fingerprint,
            initial=captured.initial,
            final=captured.final,
            observation=captured.observation,
            stdout=collection.stdout,
            stderr=collection.stderr,
            overflow=captured.overflow,
            stop_error=captured.stop_error,
        )
        fingerprint = record_digest(receipt)
        store._artifact(fingerprint, receipt.model_dump_json().encode())
        store._put("supervision", receipt.id, receipt, 0)
        if collection.frozen is not None:
            evidence, version = store.get(
                "evidence", f"scope:{digest(attempt.id.encode())}", Evidence
            )
            if evidence is None:
                raise ValueError("supervised frozen collection requires scope evidence")
            artifacts = {*evidence.artifacts, fingerprint}
            if admission_fingerprint is not None:
                artifacts.add(admission_fingerprint)
            evidence = Evidence.model_validate(
                {
                    **evidence.model_dump(),
                    "artifacts": sorted(artifacts),
                }
            )
            store._put("evidence", evidence.id, evidence, version)
        return collection, receipt
