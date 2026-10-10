"""One original-volume freeze after independently retained host terminal readback.

Preparation source only. This finite API starts no native process and grants no
execution, release or reuse authority. Linux effects require their approved batch.
"""

from array import array
import ctypes
import os
from pathlib import PurePosixPath
import select
import re
import socket
import stat
import time
from typing import Literal, NoReturn

from crewshal.admission import RetainedProc, _fields, _read, _stat_identity
from crewshal.candidate import CANDIDATE_BYTES, FrozenCandidate, _scan_fd
from crewshal.contracts import record_digest
from crewshal.linux_parent import RetainedTrustedTask, _attach, _proc_root
from crewshal.linux_production import (
    EffectiveInstallation,
    _enter_owned_namespace,
    _filesystem_magic,
)
from crewshal.linux_setup import CAPABILITIES, OwnedNamespaceSetup, _role_controls
from crewshal.linux_storage import BoundedStorageJobs


FROZEN_INODES = 64
VALIDATOR_UID = 65531


def _identity(descriptor: int) -> tuple[int, int]:
    info = os.fstat(descriptor)
    return info.st_dev, info.st_ino


def _host_handle(root: int, descriptor: int, pidfd: int, pid: int) -> None:
    """Bind actual proc inode and pidfd to this verified host procfs view."""
    if _fields(_read(root, f"self/fdinfo/{pidfd}")).get("Pid") != str(pid):
        raise ValueError("original host pidfd/proc binding differs")
    actual = os.open(
        str(pid), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
    )
    try:
        if _identity(actual) != _identity(descriptor):
            raise ValueError("original task is not retained in host procfs")
    finally:
        os.close(actual)


def _bind_projection(source: int, path: str, *, remount: bool) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    flags = 4096 | (32 | 1 | 2 | 4 | 8 if remount else 0)
    source_path = None if remount else f"/proc/self/fd/{source}".encode()
    if libc.mount(source_path, path.encode(), None, ctypes.c_ulong(flags), None) != 0:
        raise OSError(ctypes.get_errno(), "original frozen projection refused")


def _verify_original_watchdog(owner: "OriginalVolumeFreeze") -> None:
    """Read the actual original kill FD, parent lifeline and armed timer."""
    task, parent, worker = owner.watchdog, owner.parent, owner.lifetime.worker
    directory = os.open(
        "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=task.descriptor
    )
    try:
        if set(os.listdir(directory)) != {"0", "1", "2", "3", "4", "6"}:
            raise ValueError("original watchdog FD inventory differs")
        kill = os.stat("3", dir_fd=directory)
        expected = os.stat("cgroup.kill", dir_fd=worker.descriptor, follow_symlinks=False)
        lifeline = os.stat("4", dir_fd=directory)
        if (kill.st_dev, kill.st_ino) != (expected.st_dev, expected.st_ino) or not stat.S_ISFIFO(
            lifeline.st_mode
        ):
            raise ValueError("original watchdog control custody differs")
        if os.readlink("6", dir_fd=directory) != "anon_inode:[timerfd]":
            raise ValueError("original watchdog timer FD unavailable")
        for name in ("0", "1", "2"):
            info = os.stat(name, dir_fd=directory)
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(1, 3):
                raise ValueError("original watchdog stdio is not verified null")
    finally:
        os.close(directory)
    for name, mode in (("3", os.O_WRONLY | os.O_NONBLOCK), ("4", os.O_RDONLY)):
        flags = _fields(_read(task.descriptor, "fdinfo/" + name)).get("flags", "")
        if (
            not re.fullmatch("[0-7]+", flags)
            or int(flags, 8) & (os.O_ACCMODE | os.O_NONBLOCK) != mode
        ):
            raise ValueError("original watchdog FD direction differs")
    parent_fds = os.open(
        "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent.descriptor
    )
    try:
        names = os.listdir(parent_fds)
        if len(names) > 128:
            raise ValueError("original parent descriptor bound exceeded")
        writers = []
        for name in names:
            info = os.stat(name, dir_fd=parent_fds)
            if (info.st_dev, info.st_ino) == (lifeline.st_dev, lifeline.st_ino):
                flags = _fields(_read(parent.descriptor, "fdinfo/" + name)).get("flags", "")
                if not re.fullmatch("[0-7]+", flags) or int(flags, 8) & os.O_ACCMODE != os.O_WRONLY:
                    raise ValueError("original parent watchdog lifeline direction differs")
                writers.append(name)
        if len(writers) != 1:
            raise ValueError("original parent must retain exactly its watchdog lifeline")
    finally:
        os.close(parent_fds)
    before = time.monotonic_ns()
    fields = _fields(_read(task.descriptor, "fdinfo/6"))
    after = time.monotonic_ns()
    match = re.fullmatch(r"\(([0-9]+), ([0-9]+)\)", fields.get("it_value", ""))
    flags = fields.get("flags", "")
    if match is None or not re.fullmatch("[0-7]+", flags):
        raise ValueError("original watchdog timer readback malformed")
    seconds, nanos = (int(value) for value in match.groups())
    remaining = seconds * 1_000_000_000 + nanos
    if (
        fields.get("clockid") != "1"
        or fields.get("ticks") != "0"
        or fields.get("settime flags") != "01"
        or fields.get("it_interval") != "(0, 0)"
        or int(flags, 8) & (os.O_ACCMODE | os.O_NONBLOCK | os.O_CLOEXEC)
        != os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC
        or nanos >= 1_000_000_000
        or not 0 < remaining <= 5_000_000_000
        or after < before
    ):
        raise ValueError("original armed five-second watchdog timer differs")
    observed_range = (before + remaining, after + remaining)
    previous = getattr(owner, "watchdog_expiry_range", observed_range)
    retained_range = (max(previous[0], observed_range[0]), min(previous[1], observed_range[1]))
    if retained_range[0] > retained_range[1]:
        raise ValueError("original watchdog timer origin changed")
    owner.watchdog_expiry_range = retained_range


class FreezeRefusal(ValueError):
    def __init__(self, reason: str, owner: "OriginalVolumeFreeze"):
        super().__init__(reason)
        self.owner = owner
        self.resources_reusable = False


class _FreezeTransfer:
    """Pin actual created FDs before every later write/permission/mount effect."""

    def __init__(self, owner: "OriginalVolumeFreeze"):
        self.owner = owner
        flags = (
            socket.SOCK_SEQPACKET
            | getattr(socket, "SOCK_CLOEXEC")
            | getattr(socket, "SOCK_NONBLOCK")
        )
        self.parent, self.child = socket.socketpair(socket.AF_UNIX, flags)
        self.stage = 0
        self.entries = 0

    @property
    def descriptor(self) -> int:
        return self.parent.fileno()

    def transfer(self, name: str, descriptor: int) -> None:
        deadline = self.owner.jobs._active_deadline
        if deadline is None:
            raise ValueError("original freeze job deadline unavailable")
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([], [self.child], [], remaining)[1]:
            raise ValueError("original frozen custody deadline exhausted")
        raw = name.encode("ascii")
        if self.child.sendmsg(
            [raw], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", [descriptor]))]
        ) != len(raw):
            raise ValueError("actual frozen FD transfer incomplete")
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([self.child], [], [], remaining)[0]:
            raise ValueError("original frozen custody acknowledgement unavailable")
        if self.child.recv(2) != b"1":
            raise ValueError("original frozen custody acknowledgement differs")

    def pump(self) -> None:
        raw, ancillary, flags, _ = self.parent.recvmsg(
            128, socket.CMSG_SPACE(16 * array("i").itemsize), getattr(socket, "MSG_CMSG_CLOEXEC")
        )
        received: list[int] = []
        malformed = False
        for level, kind, data in ancillary:
            if (level, kind) != (socket.SOL_SOCKET, socket.SCM_RIGHTS):
                malformed = True
                continue
            values = array("i")
            malformed |= bool(len(data) % values.itemsize)
            values.frombytes(data[: len(data) - len(data) % values.itemsize])
            for descriptor in values:
                self.owner.received.append(descriptor)
                received.append(descriptor)
        if malformed or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC) or len(received) != 1:
            raise ValueError("unknown frozen custody packet retained")
        name = raw.decode("ascii")
        if self.stage == 0 and name == "frozen-root":
            self.stage = 1
        elif self.stage == 1 and name == f"entry:{self.entries}" and self.entries < 61:
            self.entries += 1
        elif self.stage == 1 and name == "projection-target":
            self.stage = 2
        elif self.stage == 2 and name == "readonly-projection":
            self.stage = 3
        else:
            raise ValueError("original frozen custody stage differs")
        self.owner.handles[name] = received[0]
        info = os.fstat(received[0])
        source = os.fstat(self.owner.volume)
        if name != "projection-target" and info.st_dev != source.st_dev:
            raise ValueError("frozen FD is outside original volume")
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError("frozen FD is not a regular owned entry")
        self.owner.jobs.verify_creation_child()
        self.owner._verify_terminal_kernel()
        if not select.select([], [self.parent], [], 0)[1] or self.parent.send(b"1") != 1:
            raise ValueError("original freeze acknowledgement refused")


class OriginalVolumeFreeze:
    """Strong one-shot original custody, bound while native and watchdog live."""

    resources_reusable: Literal[False] = False

    def __init__(self) -> None:
        raise ValueError("freeze requires original live installation/task binding")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original frozen custody cannot be copied or exported")

    installation: EffectiveInstallation
    lifetime: OwnedNamespaceSetup
    parent: RetainedTrustedTask
    native: RetainedProc
    watchdog: RetainedTrustedTask
    jobs: BoundedStorageJobs
    received: list[int]
    ancestors: list[tuple[int, int]]
    handles: dict[str, int]
    failed: bool
    source: int
    volume: int
    _owners: tuple[object, ...]
    _specs: tuple[str, str, str]
    _roots: tuple[tuple[int, int], tuple[int, int]]
    transfer: _FreezeTransfer
    manifest: FrozenCandidate
    mount_row: str
    watchdog_expiry_range: tuple[int, int]
    host_proc: int
    _host_proc_identity: tuple[int, int]

    def verify_custody(self) -> None:
        proof, lifetime = self.installation, self.lifetime
        reservation = proof.reservation
        if (
            self.failed
            or getattr(proof, "_freeze", None) is not self
            or getattr(reservation, "_setup_lifetime", None) is not lifetime
            or lifetime.storage_reservation is not reservation
            or self._owners != (proof, lifetime, self.parent, self.native, self.watchdog, self.jobs)
            or self._specs
            != (
                record_digest(self.parent.spec),
                record_digest(self.native.spec),
                record_digest(self.watchdog.spec),
            )
            or self.jobs.observer is not reservation.observer
            or self.jobs.group is not reservation.observer_group
            or self.jobs.aggregate is not reservation.aggregate
            or self.jobs.execution_group is not reservation._batch_timer.setup
            or self.jobs.batch_timer is not reservation._batch_timer
            or self.jobs.deadline != reservation.batch_started + 570
            or self.jobs.failed
            or self.jobs.pending is not None
            or (_identity(self.source), _identity(self.volume)) != self._roots
            or _identity(self.host_proc) != self._host_proc_identity
        ):
            raise ValueError("original frozen custody differs")
        proof.verify_custody()
        reservation.verify()
        if lifetime.wrapper is None or lifetime.wrapper.poll() is not None:
            raise ValueError("original namespace wrapper must remain live")

    def _verify_terminal_kernel(self) -> None:
        self.parent.verify(self.lifetime.supervisor.identity)
        self.native.verify_exited()
        self.watchdog.verify_handles()
        if not select.select([self.watchdog.pidfd], [], [], 0)[0]:
            raise ValueError("original watchdog terminal readback missing")
        self.watchdog.verify_handles()
        # The original pidfds were bound to live tasks in this retained host
        # procfs before execution. Readiness alone also covers an unreaped zombie;
        # -1 additionally requires that the bound pid no longer has a task.
        # Neither observation releases storage or closes retained handles.
        for task in (self.native, self.watchdog):
            if _fields(_read(self.host_proc, f"self/fdinfo/{task.pidfd}")).get("Pid") != "-1":
                raise ValueError("original native/watchdog reap remains unobserved")
        sample = self.lifetime.worker.sample()
        if sample.populated or sample.direct_pids:
            raise ValueError("original native tree remains populated")
        _role_controls(self.lifetime.supervisor)
        if self.lifetime.supervisor._read("cgroup.procs").split() != [str(self.parent.spec.pid)]:
            raise ValueError("freeze requires sole original live namespace parent")
        if (_identity(self.source), _identity(self.volume)) != self._roots:
            raise ValueError("original candidate/validator volume changed")
        self.native.verify_exited()
        self.parent.verify(self.lifetime.supervisor.identity)

    def verify_registered_job(self, jobs: BoundedStorageJobs) -> None:
        if self.failed or jobs is not getattr(self, "jobs", None):
            raise ValueError("frozen work requires its original bounded job")
        self.verify_custody()
        self._verify_terminal_kernel()

    def verify_registered_action(self, jobs: BoundedStorageJobs, action: object) -> None:
        if getattr(action, "__self__", None) is not self:
            raise ValueError("frozen action requires its original retained owner")
        method = getattr(action, "__func__", None)
        copying = (
            method is OriginalVolumeFreeze._freeze_child
            and getattr(self, "_attempted", False)
            and hasattr(self, "transfer")
            and self.transfer.stage == 0
            and not hasattr(self, "manifest")
        )
        reading = (
            method is OriginalVolumeFreeze._verify_readonly_child
            and hasattr(self, "manifest")
            and self.transfer.stage == 3
        )
        if not copying and not reading:
            raise ValueError("frozen action is not its fixed one-shot copy/readback")
        self.verify_registered_job(jobs)

    def freeze(self) -> FrozenCandidate:
        if hasattr(self, "_attempted") or self.failed:
            raise FreezeRefusal("original freeze attempt consumed; no retry", self)
        # Mark attempted before admission; every acquired handle stays pinned.
        self._attempted = True
        try:
            self.transfer = _FreezeTransfer(self)
            self.verify_custody()
            self._verify_terminal_kernel()
            keep = {
                self.source,
                self.volume,
                self.installation.production.handles["namespace"],
                self.installation.production.handles["root-parent"],
                self.transfer.child.fileno(),
                self.parent.descriptor,
                self.parent.pidfd,
                self.native.descriptor,
                self.native.pidfd,
                self.watchdog.descriptor,
                self.watchdog.pidfd,
                self.host_proc,
                self.lifetime.worker.descriptor,
                self.lifetime.supervisor.descriptor,
            }
            raw = self.jobs.run(self._freeze_child, keep, transfer=self.transfer)
            self.verify_custody()
            self._verify_terminal_kernel()
            manifest_raw, separator, mount_raw = raw.partition(b"\n")
            if not separator or self.transfer.stage != 3:
                raise ValueError("original frozen readback incomplete")
            self.manifest = FrozenCandidate.model_validate_json(manifest_raw)
            self.mount_row = mount_raw.decode("ascii")
            self._manifest_digest = record_digest(self.manifest)
            self.verify_projection()
            return self.manifest
        except BaseException as error:
            self.failed = True
            self.installation.reservation._retain_installation_refusal(error)
            raise FreezeRefusal(str(error), self) from error

    def verify_projection(self) -> None:
        try:
            self._verify_projection()
        except BaseException as error:
            self.failed = True
            self.installation.reservation._retain_installation_refusal(error)
            raise FreezeRefusal(str(error), self) from error

    def _verify_projection(self) -> None:
        self.verify_custody()
        self._verify_terminal_kernel()
        if record_digest(self.manifest) != self._manifest_digest:
            raise ValueError("original frozen manifest binding changed")
        raw = self.jobs.run(
            self._verify_readonly_child,
            {
                self.handles["readonly-projection"],
                self.handles["frozen-root"],
                self.source,
                self.volume,
                self.installation.production.handles["namespace"],
                self.parent.descriptor,
                self.parent.pidfd,
                self.native.descriptor,
                self.native.pidfd,
                self.watchdog.descriptor,
                self.watchdog.pidfd,
                self.host_proc,
                self.lifetime.worker.descriptor,
                self.lifetime.supervisor.descriptor,
            },
        )
        self.verify_custody()
        self._verify_terminal_kernel()
        if raw != self._manifest_digest.encode("ascii"):
            raise ValueError("actual original frozen content readback differs")
        projection, frozen = self.handles["readonly-projection"], self.handles["frozen-root"]
        info = os.fstat(projection)
        if (
            _identity(projection) != _identity(frozen)
            or info.st_uid != VALIDATOR_UID
            or info.st_gid != VALIDATOR_UID
            or stat.S_IMODE(info.st_mode) != 0o700
            or not os.fstatvfs(projection).f_flag & os.ST_RDONLY
            or _filesystem_magic(projection) != 0xF15F
        ):
            raise ValueError("actual original frozen readonly projection differs")
        root = _proc_root(self.parent.spec.boot_id)
        try:
            mount = _fields(_read(root, f"self/fdinfo/{projection}")).get("mnt_id")
        finally:
            os.close(root)
        before, separator, after = self.mount_row.partition(" - ")
        fields = before.split()
        expected_path = self.installation.production.root + "/validator-frozen"
        if (
            not separator
            or len(fields) < 6
            or fields[0] != mount
            or fields[2] != f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}"
            or fields[3:5] != ["/frozen", expected_path]
            or not {"ro", "nosuid", "nodev", "noexec"} <= set(fields[5].split(","))
            or after.split()[0] != "ecryptfs"
        ):
            raise ValueError("original frozen mount readback differs")

    def _verify_readonly_child(self) -> bytes:
        self._verify_terminal_kernel()
        _enter_owned_namespace(self.installation.production.handles["namespace"])
        descriptor = self.handles["readonly-projection"]
        if (
            not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY
            or _identity(descriptor) != _identity(self.handles["frozen-root"])
            or _scan_fd(descriptor)[0] != self.manifest
        ):
            raise ValueError("actual readonly frozen contents changed")
        self._verify_terminal_kernel()
        return record_digest(self.manifest).encode("ascii")

    def _freeze_child(self) -> bytes:
        self._verify_terminal_kernel()
        _enter_owned_namespace(self.installation.production.handles["namespace"])
        for descriptor, uid in ((self.source, 65534), (self.volume, 0)):
            info = os.fstat(descriptor)
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != uid
                or info.st_gid != uid
                or stat.S_IMODE(info.st_mode) != 0o700
                or _filesystem_magic(descriptor) != 0xF15F
            ):
                raise ValueError("original candidate/validator encrypted volume differs")
        manifest, contents = _scan_fd(self.source)
        # New root + projection target and filesystem bookkeeping remain within
        # the original 64-inode role ceiling; no larger representation is created.
        if (
            len(manifest.files) > FROZEN_INODES - 3
            or sum(file.size for file in manifest.files) > CANDIDATE_BYTES
        ):
            raise ValueError("original frozen inode/byte bound exceeded")
        if any(
            entry.mode & (0o500 if entry.kind == "directory" else 0o400)
            != (0o500 if entry.kind == "directory" else 0o400)
            for entry in manifest.files
        ):
            raise ValueError("source modes cannot preserve validator readability")
        os.mkdir("frozen", 0o700, dir_fd=self.volume)
        frozen = os.open(
            "frozen",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=self.volume,
        )
        self.transfer.transfer("frozen-root", frozen)
        directories = {".": frozen}
        entries: list[tuple[int, int]] = []
        for index, entry in enumerate(
            sorted(manifest.files, key=lambda file: (file.path.count("/"), file.path))
        ):
            path = PurePosixPath(entry.path)
            parent = directories[str(path.parent)]
            if entry.kind == "directory":
                os.mkdir(path.name, 0o700, dir_fd=parent)
                descriptor = os.open(
                    path.name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=parent,
                )
                directories[entry.path] = descriptor
            else:
                descriptor = os.open(
                    path.name,
                    os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                    0o600,
                    dir_fd=parent,
                )
            self.transfer.transfer(f"entry:{index}", descriptor)
            if entry.kind == "file":
                data, offset = contents[entry.path], 0
                if len(data) > 131072:
                    raise ValueError("frozen file exceeds original inherited growth limit")
                while offset < len(data):
                    written = os.write(descriptor, data[offset:])
                    if written <= 0:
                        raise ValueError("original frozen copy incomplete")
                    offset += written
            entries.append((descriptor, entry.mode))
        # Ownership only changes new frozen entries, never original source or
        # the retained root-owned upper volume. Modes remain the source manifest.
        for descriptor, mode in reversed(entries):
            os.fchown(descriptor, VALIDATOR_UID, VALIDATOR_UID)
            os.fchmod(descriptor, mode)
            os.fsync(descriptor)
        os.fchown(frozen, VALIDATOR_UID, VALIDATOR_UID)
        os.fsync(frozen)
        if _scan_fd(self.source)[0] != manifest or _scan_fd(frozen)[0] != manifest:
            raise ValueError("original candidate changed during freeze")
        parent = self.installation.production.handles["root-parent"]
        os.mkdir("validator-frozen", 0o700, dir_fd=parent)
        target = os.open(
            "validator-frozen",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=parent,
        )
        self.transfer.transfer("projection-target", target)
        projection_path = self.installation.production.root + "/validator-frozen"
        if _identity(target) != (
            os.stat(projection_path, follow_symlinks=False).st_dev,
            os.stat(projection_path, follow_symlinks=False).st_ino,
        ):
            raise ValueError("original projection target changed")
        _bind_projection(frozen, projection_path, remount=False)
        projection = os.open(
            projection_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )
        self.transfer.transfer("readonly-projection", projection)
        _bind_projection(frozen, projection_path, remount=True)
        if not os.fstatvfs(projection).f_flag & os.ST_RDONLY or _identity(projection) != _identity(
            frozen
        ):
            raise ValueError("actual original frozen remount remains unknown")
        if _scan_fd(self.source)[0] != manifest or _scan_fd(projection)[0] != manifest:
            raise ValueError("original frozen contents changed after readonly remount")
        self._verify_terminal_kernel()
        root = _proc_root(self.parent.spec.boot_id)
        try:
            mount = _fields(_read(root, f"self/fdinfo/{projection}")).get("mnt_id")
            rows = [
                row
                for row in _read(root, "self/mountinfo").decode("ascii").splitlines()
                if row.split()[0] == mount
            ]
        finally:
            os.close(root)
        if len(rows) != 1:
            raise ValueError("original readonly frozen mount row unavailable")
        return manifest.model_dump_json().encode() + b"\n" + rows[0].encode("ascii")


def bind_original_freeze(
    installation: EffectiveInstallation,
    lifetime: OwnedNamespaceSetup,
    parent: RetainedTrustedTask,
    native: RetainedProc,
    watchdog: RetainedTrustedTask,
    pipes: tuple[int, int, int],
) -> OriginalVolumeFreeze:
    """Bind actual host handles before native exit, never reconstruct from data.

    The approved runtime must supply host-view proc/pidfds via its retained FD
    bridge while native is stopped and its original watchdog is armed. This API
    independently checks them; it supplies no bridge, launch or retry itself.
    """
    if type(installation) is not EffectiveInstallation or hasattr(installation, "_freeze"):
        raise ValueError("original installed freeze binding unavailable or consumed")
    owner = object.__new__(OriginalVolumeFreeze)
    owner.installation, owner.lifetime = installation, lifetime
    owner.parent, owner.native, owner.watchdog = parent, native, watchdog
    owner.failed, owner.received, owner.ancestors, owner.handles = False, [], [], {}
    setattr(installation, "_freeze", owner)
    try:
        reservation = installation.reservation
        installation.verify()
        if (
            type(lifetime) is not OwnedNamespaceSetup
            or type(parent) is not RetainedTrustedTask
            or type(native) is not RetainedProc
            or type(watchdog) is not RetainedTrustedTask
            or getattr(reservation, "_setup_lifetime", None) is not lifetime
            or lifetime.storage_reservation is not reservation
            or lifetime.controls.configuration != reservation._configuration
            or lifetime.aggregate is not reservation.aggregate
            or lifetime.supervisor is not reservation._batch_timer.supervisor
            or lifetime.worker is not reservation._batch_timer.worker
            or lifetime.setup is not reservation._batch_timer.setup
            or lifetime.observer_group is not reservation.observer_group
            or lifetime.wrapper is None
            or lifetime.wrapper.poll() is not None
            or native.spec.parent_pid != parent.spec.pid
            or watchdog.spec.parent_pid != parent.spec.pid
            or parent.spec.configuration != reservation._configuration_digest
            or native.spec.configuration != reservation._configuration_digest
            or watchdog.spec.configuration != reservation._configuration_digest
            or watchdog.spec.executable != lifetime.controls.bootstrap.policy.helper_binary
            or watchdog.spec.argv != lifetime.controls.bootstrap.watchdog_argv
            or watchdog.spec.capabilities != "0" * 16
            or watchdog.spec.namespaces != parent.spec.namespaces
            or native.spec.namespaces
            != {
                name: identity
                for name, identity in parent.spec.namespaces.items()
                if name != "time"
            }
            or native.spec.worker != lifetime.worker.identity
            or native.spec.aggregate != lifetime.aggregate.identity
            or native.spec.executable_sha256
            != installation.production._root_manifest.root["/opt/codex/bin/codex"].sha256
            or parent.spec.argv != lifetime.controls.setup.parent_argv
            or parent.spec.executable != lifetime.controls.setup.parent_executable
            or parent.spec.boot_id != reservation.observer.spec.boot_id
            or native.spec.boot_id != parent.spec.boot_id
            or watchdog.spec.boot_id != parent.spec.boot_id
            or parent.spec.placement != "namespace"
            or parent.spec.capabilities != CAPABILITIES
            or parent.spec.cgroup != lifetime.supervisor.identity
            or watchdog.spec.cgroup != lifetime.supervisor.identity
            or any(
                parent.spec.namespaces[name] == lifetime.controls.outer_namespaces[name]
                for name in ("mnt", "net", "pid")
            )
        ):
            raise ValueError("original parent/native/watchdog host binding differs")
        parent.verify(lifetime.supervisor.identity)
        watchdog.verify(lifetime.supervisor.identity)
        native.verify_stopped()
        native.read_configuration(reservation._configuration)
        native.verify_pipes(*pipes)
        _verify_original_watchdog(owner)
        root = owner.host_proc = _proc_root(parent.spec.boot_id)
        owner._host_proc_identity = _identity(root)
        try:
            for task in (parent, native, watchdog):
                _host_handle(root, task.descriptor, task.pidfd, task.spec.pid)
            ancestor = parent.spec.parent_pid
            for _ in range(8):
                descriptor, pidfd = _attach(root, ancestor)
                owner.ancestors.append((descriptor, pidfd))
                observed, state, ancestor_parent, _ = _stat_identity(_read(descriptor, "stat"))
                if (
                    observed != ancestor
                    or state not in ("R", "S")
                    or select.select([pidfd], [], [], 0)[0]
                ):
                    raise ValueError("original live wrapper ancestry unknown")
                if ancestor == lifetime.wrapper.pid:
                    break
                ancestor = ancestor_parent
            else:
                raise ValueError("namespace parent is outside original wrapper ancestry")
        finally:
            # Retain original verified procfs even on unknown binding/refusal.
            # Fresh per-call descriptors elsewhere do not substitute for it.
            pass
        if set(lifetime.supervisor._read("cgroup.procs").split()) != {
            str(parent.spec.pid),
            str(watchdog.spec.pid),
        }:
            raise ValueError("original supervisor live binding differs")
        sample = lifetime.worker.sample()
        if not sample.populated or sample.direct_pids != [native.spec.pid]:
            raise ValueError("original stopped native must be sole worker")
        owner.source = installation.production.handles["mounted:candidate-upper"]
        owner.volume = installation.production.handles["mounted:validator-candidate-upper"]
        if _identity(owner.source) == _identity(owner.volume):
            raise ValueError("original frozen volume cannot alias native candidate")
        owner._roots = (_identity(owner.source), _identity(owner.volume))
        owner.jobs = BoundedStorageJobs(
            reservation.observer,
            reservation.observer_group,
            reservation.aggregate,
            reservation.batch_started + 570,
            execution_group=reservation._batch_timer.setup,
            batch_timer=reservation._batch_timer,
        )
        owner._owners = (installation, lifetime, parent, native, watchdog, owner.jobs)
        owner._specs = (
            record_digest(parent.spec),
            record_digest(native.spec),
            record_digest(watchdog.spec),
        )
        owner.verify_custody()
        _verify_original_watchdog(owner)
        return owner
    except BaseException as error:
        owner.failed = True
        installation.reservation._retain_installation_refusal(error)
        raise FreezeRefusal(str(error), owner) from error
