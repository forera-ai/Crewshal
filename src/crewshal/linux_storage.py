"""Retained Linux storage-owner source; never an operational entry point.

All syscalls and fork paths require fresh qualification and the separate live
session gate. Offline tests replace those seams. Bounded proc observations do
not establish a closed world: hidden namespaces, asynchronous kernel references
and concurrent host mutation remain explicit unknowns, never released storage.
"""

import ctypes
import errno
import fcntl
import math
import os
from pathlib import PurePosixPath
import platform
import re
import select
import signal
import stat
import struct
import sys
import time
from typing import Callable, Literal

from crewshal.admission import NamespaceIdentity, _read, _stat_identity
from crewshal.contracts import record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_envelope import prepare_linux_envelope
from crewshal.linux_parent import RetainedTrustedTask, _proc_root
from crewshal.linux_teardown import FileIdentity, LoopIdentity, MountIdentity, PhysicalState
from crewshal.supervisor import OwnedCgroup


LOOP_GET_STATUS64 = 0x4C05
LOOP_CLR_FD = 0x4C01
LOOP_INFO64 = struct.Struct("=QQQQQIIII64s64s32sQQ")


# UAPI dev_t is new_encode_dev(), not the libc dev_t layout in st_dev.
def _loop_device(value: int) -> int:
    return os.makedev((value >> 8) & 0xFFF, (value & 0xFF) | ((value >> 12) & 0xFFFFF00))


def _identity(descriptor: int) -> FileIdentity:
    info = os.fstat(descriptor)
    return FileIdentity(device=info.st_dev, inode=info.st_ino)


def _leaf(name: str) -> None:
    if not name or PurePosixPath(name).name != name or name in (".", "..") or "\x00" in name:
        raise ValueError("single owned backing leaf required")


def _decode_mount(value: str) -> str:
    if re.search(r"\\(?!040|011|012|134)", value):
        raise ValueError("unknown mountinfo escape")
    return re.sub(r"\\(040|011|012|134)", lambda m: chr(int(m[1], 8)), value)


def parse_mountinfo(raw: bytes) -> dict[int, tuple[MountIdentity | None, str, str]]:
    """Parse all rows, including non-owned aliases; never search target substrings."""
    if len(raw) > 1048576:
        raise ValueError("mountinfo exceeds fixed read bound")
    rows: dict[int, tuple[MountIdentity | None, str, str]] = {}
    for line in raw.decode("ascii").splitlines():
        before, separator, after = line.partition(" - ")
        parts, tail = before.split(), after.split()
        if (
            not separator
            or len(parts) < 6
            or len(tail) != 3
            or not re.fullmatch(r"[1-9][0-9]*", parts[0])
            or not re.fullmatch(r"[1-9][0-9]*", parts[1])
            or not re.fullmatch(r"[0-9]+:[0-9]+", parts[2])
        ):
            raise ValueError("malformed mountinfo")
        mid = int(parts[0])
        target = _decode_mount(parts[4])
        root = _decode_mount(parts[3])
        if mid in rows or not target.startswith("/") or not root.startswith("/"):
            raise ValueError("duplicate mount identity or nonabsolute mount path")
        mount = None
        if tail[0] in ("ecryptfs", "ext4"):
            mount = MountIdentity(
                mount_id=mid,
                parent_id=int(parts[1]),
                target=target,
                filesystem="ecryptfs" if tail[0] == "ecryptfs" else "ext4",
                device=parts[2],
            )
        rows[mid] = (mount, parts[2], target)
        if len(rows) > 8192:
            raise ValueError("mount count exceeds bound")
    if not rows:
        raise ValueError("empty mountinfo is unknown")
    return rows


def _keyctl(operation: int, serial: int = 0, buffer: object = None, size: int = 0) -> int:
    if sys.platform != "linux" or platform.machine() not in ("x86_64", "aarch64"):
        raise ValueError("qualified Linux keyctl ABI unavailable")
    libc = ctypes.CDLL(None, use_errno=True)
    call = libc.syscall
    call.restype = ctypes.c_long
    number = 250 if platform.machine() == "x86_64" else 219
    pointer = ctypes.cast(buffer, ctypes.c_void_p) if buffer is not None else ctypes.c_void_p()
    result = int(
        call(
            ctypes.c_long(number),
            ctypes.c_long(operation),
            ctypes.c_long(serial),
            pointer,
            ctypes.c_ulong(size),
            ctypes.c_long(0),
        )
    )
    if result == -1:
        code = ctypes.get_errno()
        raise OSError(code, "retained keyctl operation refused")
    return result


def _key_state(serial: int) -> Literal["present", "revoked", "unknown"]:
    buffer = ctypes.create_string_buffer(4096)
    try:
        size = _keyctl(6, serial, buffer, len(buffer))  # KEYCTL_DESCRIBE
    except OSError as error:
        return "revoked" if error.errno == 128 else "unknown"  # Linux EKEYREVOKED only
    if not 0 < size <= len(buffer) or buffer.raw[size - 1] != 0:
        raise ValueError("keyring description exceeds bound or lacks terminator")
    parts = buffer.raw[: size - 1].decode("ascii").split(";")
    if len(parts) != 5 or parts[:3] != ["keyring", "0", "0"] or parts[4] != "_ses":
        raise ValueError("retained anonymous root keyring identity differs")
    if not re.fullmatch(r"[0-9a-f]{8}", parts[3]):
        raise ValueError("invalid private keyring permission readback")
    return "present"


class AnonymousKeyring:
    """Creation provenance retained in memory, not a reconstructed positive ID.

    create() is future qualified trusted setup source, never discovery. It joins
    a new anonymous ring; it never links, clears or revokes an inherited ring.
    This creation call's setup containment still needs effective qualification.
    """

    serial: int
    creator: int
    previous: int
    claimed: bool

    def __init__(self) -> None:
        raise ValueError("private keyring cannot be reconstructed from a serial")

    @classmethod
    def create(cls) -> "AnonymousKeyring":
        # GET_KEYRING_ID with create=0: do not instantiate an ambient ring.
        try:
            previous = _keyctl(0, -3)
        except OSError as error:
            if error.errno != 126:  # ENOKEY
                raise
            previous = 0
        serial = _keyctl(1)  # JOIN_SESSION_KEYRING(NULL)
        ring = object.__new__(cls)
        ring.serial, ring.creator, ring.previous = serial, os.getpid(), previous
        ring.claimed = False
        try:
            observed = _key_state(serial)
        except (OSError, ValueError):
            raise KeyringCreationRefusal(ring) from None
        if serial <= 0 or serial == previous or observed != "present":
            # Unknown newly created state is retained; do not attempt cleanup of
            # a serial whose ownership was not independently established.
            raise KeyringCreationRefusal(ring)
        return ring


class BoundedStorageJobs:
    """One child at a time, already inside the bounded observer before fork.

    No cgroup migration, exec, Popen, watchdog reset or new resource allowance.
    A blocked syscall may outlive SIGKILL: retain its pidfd, refuse later jobs and
    report unknown. Never wait beyond the original absolute cleanup deadline.
    """

    def __init__(
        self,
        observer: RetainedTrustedTask,
        group: OwnedCgroup,
        aggregate: OwnedCgroup,
        deadline: float,
    ):
        self.observer, self.group, self.aggregate = observer, group, aggregate
        self.deadline = deadline
        self.pending: tuple[int, int] | None = None
        self.failed = False

    def _admit(self) -> None:
        if self.failed or self.pending is not None:
            raise ValueError("storage job failed or remains retained; no retry")
        if not math.isfinite(self.deadline) or time.monotonic() >= self.deadline:
            raise ValueError("original storage cleanup deadline exhausted")
        if sys.platform != "linux" or not hasattr(os, "pidfd_open"):
            raise ValueError("Linux storage job pidfd unavailable")
        if signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
            raise ValueError("storage jobs require exclusive child reaping")
        if self.observer.spec.pid != os.getpid():
            raise ValueError("storage job must fork from retained live observer")
        self.observer.verify(self.group.identity)
        self.group.sample()
        self.aggregate._verify()
        if (
            PurePosixPath(self.group.identity.relative_path).parent
            != PurePosixPath(self.aggregate.identity.relative_path)
            or self.aggregate._read("memory.max") != "805306368"
            or self.aggregate._read("memory.swap.max") != "0"
            or self.aggregate._read("pids.max") != "128"
            or self.aggregate._read("cpu.max") != "100000 100000"
        ):
            raise ValueError("storage observer/aggregate original ceilings differ")

    def run(self, action: Callable[[], bytes], keep: set[int]) -> bytes:
        self._admit()
        read_end, write_end = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        try:
            admit_read, admit_write = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        except BaseException:
            os.close(read_end)
            os.close(write_end)
            self.failed = True
            raise
        parent_pid = os.getpid()
        try:
            pid = os.fork()
        except BaseException:
            os.close(read_end)
            os.close(write_end)
            os.close(admit_read)
            os.close(admit_write)
            self.failed = True
            raise
        if pid == 0:
            # Inherited observer containment precedes every child instruction.
            # Close unrelated inherited FDs, including backing copies, before
            # readback. No daemon, descendant, credential or namespace creator.
            try:
                os.close(admit_write)
                libc = ctypes.CDLL(None, use_errno=True)
                if libc.prctl(1, int(signal.SIGKILL), 0, 0, 0) != 0 or os.getppid() != parent_pid:
                    os._exit(1)
                remaining = self.deadline - time.monotonic()
                if (
                    remaining <= 0
                    or not select.select([admit_read], [], [], remaining)[0]
                    or os.read(admit_read, 2) != b"1"
                ):
                    os._exit(1)
                os.close(admit_read)
                descriptors = os.listdir("/proc/self/fd")
                for text in descriptors:
                    descriptor = int(text)
                    if descriptor not in keep | {write_end}:
                        try:
                            os.close(descriptor)
                        except OSError as error:
                            if error.errno != errno.EBADF:
                                raise
                result = action()
                if len(result) > 65535:
                    raise ValueError("storage response exceeds fixed stream bound")
                payload = b"+" + result
            except BaseException:
                payload = b"-unknown storage syscall/readback failure"
            try:
                offset = 0
                while offset < len(payload):
                    remaining = self.deadline - time.monotonic()
                    if remaining <= 0 or not select.select([], [write_end], [], remaining)[1]:
                        os._exit(1)
                    offset += os.write(write_end, payload[offset:])
                os._exit(0)
            except BaseException:
                os._exit(1)
        os.close(write_end)
        os.close(admit_read)
        pidfd = -1
        reaped = False
        try:
            pidfd = getattr(os, "pidfd_open")(pid, 0)
            self.pending = (pid, pidfd)
            if time.monotonic() >= self.deadline or os.write(admit_write, b"1") != 1:
                raise ValueError("retained storage child admission deadline exhausted")
            os.close(admit_write)
            admit_write = -1
            output = bytearray()
            eof = False
            while not eof:
                remaining = self.deadline - time.monotonic()
                if remaining <= 0 or not select.select([read_end], [], [], remaining)[0]:
                    raise ValueError("original storage cleanup deadline exhausted")
                chunk = os.read(read_end, 65537 - len(output))
                if not chunk:
                    eof = True
                output.extend(chunk)
                if len(output) > 65536:
                    raise ValueError("storage response exceeds fixed stream bound")
            remaining = max(0.0, self.deadline - time.monotonic())
            if not select.select([pidfd], [], [], remaining)[0]:
                raise ValueError("storage child terminal readback unavailable")
            observed, status = os.waitpid(pid, os.WNOHANG)
            if observed != pid:
                raise ValueError("storage child was not independently reaped")
            os.close(pidfd)
            pidfd = -1
            self.pending = None
            reaped = True
            if (
                not os.WIFEXITED(status)
                or os.WEXITSTATUS(status) != 0
                or time.monotonic() >= self.deadline
            ):
                raise ValueError("storage child failed or original deadline exhausted")
            if not output.startswith(b"+"):
                raise ValueError("storage child reported unknown readback")
            # Command exit/status is transport only. Caller independently
            # re-observes kernel state before accepting a physical transition.
            return bytes(output[1:])
        except BaseException:
            self.failed = True
            if pidfd >= 0:
                getattr(signal, "pidfd_send_signal")(pidfd, signal.SIGKILL)
                if select.select([pidfd], [], [], 0)[0] and os.waitpid(pid, os.WNOHANG)[0] == pid:
                    os.close(pidfd)
                    self.pending = None
            elif not reaped:
                # No numeric PID signal. Child has finite pipe output and may
                # remain unreaped; retain the child PID solely for future audit.
                self.pending = (pid, -1)
            raise
        finally:
            if admit_write >= 0:
                os.close(admit_write)
            os.close(read_end)


class LinuxPhysicalOwner:
    """Concrete pinned readback/effects with retained unknown closure.

    Every operation is guarded and one-shot. Host proc enumeration cannot prove
    absence of taskless namespaces, io_uring/AIO or other kernel references.
    Until effective reference closure is qualified, zero candidate holders is
    deliberately returned as None. This owner therefore cannot authorize actual
    unlink/teardown from an empty scan. No runtime eligibility or reuse exists.
    """

    def __init__(
        self,
        *,
        configuration: DispatchConfiguration,
        namespace_fd: int,
        directory_fd: int,
        loop_fds: dict[str, int],
        backing_fds: dict[str, int],
        mounts: dict[str, str],
        ring: AnonymousKeyring,
        jobs: BoundedStorageJobs,
        batch_started_monotonic: float,
    ):
        now = time.monotonic()
        if (
            not math.isfinite(batch_started_monotonic)
            or not 0 < batch_started_monotonic <= now
            or not now < jobs.deadline <= min(now + 30, batch_started_monotonic + 600)
        ):
            raise ValueError("original batch origin and bounded cleanup reserve required")
        if (
            ring.claimed
            or ring.creator != os.getpid()
            or ring.serial <= 0
            or ring.serial == ring.previous
        ):
            raise ValueError("unclaimed newly created private anonymous keyring required")
        root = prepare_linux_envelope(configuration).owned_root
        if jobs.observer.spec.configuration != record_digest(configuration):
            raise ValueError("storage observer configuration differs")
        for target in mounts.values():
            path = PurePosixPath(target)
            if (
                not path.is_relative_to(root)
                or str(path) != target
                or str(path) == root
                or ".." in path.parts
                or "\x00" in target
            ):
                raise ValueError("storage mount must stay inside exact owned session root")
        if not mounts or len(mounts) > 16 or not loop_fds or len(loop_fds) > 16:
            raise ValueError("bounded owned mount/loop inventory required")
        if not backing_fds or len(backing_fds) > 16:
            raise ValueError("bounded owned backing inventory required")
        for name in backing_fds:
            _leaf(name)
        ring.claimed = True
        self.ring, self.jobs = ring, jobs
        self._ring_identity = (ring.serial, ring.creator, ring.previous)
        self.configuration = record_digest(configuration)
        self._deadline = jobs.deadline
        self._initial_digest: str | None = None
        self.mount_targets = dict(mounts)
        self._mount_targets = dict(mounts)
        self._owned_root = root
        self.handles: dict[str, int] = {}
        self.attempted: set[str] = set()
        self.effects_failed = False
        self.initial: PhysicalState | None = None
        self.allowed_backing = dict(backing_fds)
        self.pid = os.getpid()
        try:
            for name, descriptor in {
                "namespace": namespace_fd,
                "directory": directory_fd,
                **{"loop:" + n: d for n, d in loop_fds.items()},
            }.items():
                self.handles[name] = os.dup(descriptor)
            self.handles["proc"] = _proc_root(jobs.observer.spec.boot_id)
            self.identities = {name: _identity(fd) for name, fd in self.handles.items()}
            self.backing = {name: _identity(fd) for name, fd in backing_fds.items()}
            if len(set((i.device, i.inode) for i in self.backing.values())) != len(self.backing):
                raise ValueError("distinct owned backing identities required")
            self.initial = self.readback()
            self._initial_digest = record_digest(self.initial)
            if self.initial.keyring_state != "present" or set(self.initial.backing) != set(
                backing_fds
            ):
                raise ValueError("initial private key/backing readback incomplete")
            if set(self.initial.mounts) != set(mounts) or set(self.initial.loops) != set(loop_fds):
                raise ValueError("initial owned kernel mount/loop inventory incomplete")
        except BaseException:
            # A failed retained object is inspectable. Do not close identity
            # handles or clean an unknown partial lifetime in this constructor.
            raise StorageOwnerRefusal(self) from None

    def bind_backing_handles(self, descriptors: dict[str, int]) -> None:
        if set(descriptors) != set(self.backing):
            raise ValueError("complete retained backing descriptor transfer required")
        for name, fd in descriptors.items():
            if _identity(fd) != self.backing[name]:
                raise ValueError("transferred backing descriptor identity differs")
        self.allowed_backing = dict(descriptors)

    @property
    def cleanup_deadline(self) -> float:
        return self.jobs.deadline

    def _verify(self) -> None:
        initial_digest = record_digest(self.initial) if self.initial is not None else None
        if (
            self.jobs.deadline != self._deadline
            or self.mount_targets != self._mount_targets
            or (self._initial_digest is not None and initial_digest != self._initial_digest)
            or self._ring_identity != (self.ring.serial, self.ring.creator, self.ring.previous)
            or not self.ring.claimed
            or self.jobs.observer.spec.configuration != self.configuration
        ):
            raise ValueError("retained private keyring or observer configuration changed")
        if set(self.handles) != set(self.identities):
            raise ValueError("retained storage handle set differs")
        for name, identity in self.identities.items():
            if _identity(self.handles[name]) != identity:
                raise ValueError("retained Linux storage descriptor replaced")
        actual_path = os.readlink(
            f"self/fd/{self.handles['directory']}", dir_fd=self.handles["proc"]
        )
        path = PurePosixPath(actual_path)
        if (
            str(path) != actual_path
            or not path.is_relative_to(self._owned_root)
            or ".." in path.parts
            or " (deleted)" in actual_path
        ):
            raise ValueError("pinned backing directory lies outside owned session root")
        info = os.fstat(self.handles["directory"])
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError("owned backing directory permits untrusted mutation")

    def _enter(self) -> None:
        self._verify()
        if not hasattr(os, "setns"):
            raise ValueError("qualified Linux mount namespace entry unavailable")
        os.setns(self.handles["namespace"], 0x20000)
        info = os.stat("self/ns/mnt", dir_fd=self.handles["proc"])
        if FileIdentity(device=info.st_dev, inode=info.st_ino) != self.identities["namespace"]:
            raise ValueError("entered mount namespace identity differs")

    def _loop(self, name: str) -> LoopIdentity | None:
        fd = self.handles["loop:" + name]
        info = os.fstat(fd)
        if not stat.S_ISBLK(info.st_mode) or os.major(info.st_rdev) != 7:
            raise ValueError("retained owned loop is not a loop block device")
        raw = bytearray(LOOP_INFO64.size)
        try:
            fcntl.ioctl(fd, LOOP_GET_STATUS64, raw, True)
        except OSError as error:
            if error.errno == errno.ENXIO:
                return None
            raise
        values = LOOP_INFO64.unpack(raw)
        backing = FileIdentity(device=_loop_device(values[0]), inode=values[1])
        names = [n for n, identity in self.backing.items() if identity == backing]
        if (
            len(names) != 1
            or values[2] != 0
            or values[3] != 0
            or not 0 < values[4] <= 8589934592
            or values[5] != os.minor(info.st_rdev)
            or values[6] != 0
            or values[7] != 0
            or values[8] & ~1
        ):
            raise ValueError("owned loop backing/offset/size/flags differs")
        result = LoopIdentity(
            device=_identity(fd),
            rdev=info.st_rdev,
            backing=backing,
            backing_name=names[0],
            size_limit=values[4],
        )
        if self.initial is not None and result != self.initial.loops[name]:
            raise ValueError("owned loop reassigned or mutated")
        return result

    def _scan_references(self, devices: set[int]) -> tuple[int | None, int | None]:
        """Positive holder/alias discovery only; bounded scans never grant closure."""
        root = self.handles["proc"]
        aliases = holders = 0
        tasks = sorted(n for n in os.listdir(root) if n.isascii() and n.isdigit())
        if len(tasks) > 4096:
            return None, None
        owned = {(i.device, i.inode) for i in self.backing.values()}
        seen_namespaces: set[tuple[int, int]] = set()
        try:
            for pid in tasks:
                process = os.open(pid, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
                try:
                    before = _stat_identity(_read(process, "stat"))
                    ns = os.stat("ns/mnt", dir_fd=process)
                    namespace = (ns.st_dev, ns.st_ino)
                    if namespace not in seen_namespaces:
                        rows = parse_mountinfo(_read(process, "mountinfo"))
                        for mid, (_, dev, _) in rows.items():
                            major, minor = map(int, dev.split(":"))
                            if os.makedev(major, minor) in devices:
                                own_ns = namespace == (
                                    self.identities["namespace"].device,
                                    self.identities["namespace"].inode,
                                )
                                if (
                                    not own_ns
                                    or self.initial is None
                                    or mid not in {m.mount_id for m in self.initial.mounts.values()}
                                ):
                                    aliases += 1
                        seen_namespaces.add(namespace)
                    directory = os.open(
                        "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=process
                    )
                    try:
                        names = os.listdir(directory)
                        if len(names) > 4096:
                            return None, None
                        for name in names:
                            if not name.isascii() or not name.isdigit():
                                raise ValueError("non-numeric proc descriptor")
                            info = os.stat(name, dir_fd=directory)
                            allowed = pid == str(self.pid) and any(
                                int(name) == fd
                                and (info.st_dev, info.st_ino)
                                == (self.backing[n].device, self.backing[n].inode)
                                for n, fd in self.allowed_backing.items()
                            )
                            if not allowed and (
                                (info.st_dev, info.st_ino) in owned or info.st_dev in devices
                            ):
                                holders += 1
                    finally:
                        os.close(directory)
                    for name in ("cwd", "root"):
                        if os.stat(name, dir_fd=process).st_dev in devices:
                            holders += 1
                    for line in _read(process, "maps").decode("ascii").splitlines():
                        fields = line.split(maxsplit=5)
                        if len(fields) < 5 or not re.fullmatch(r"[0-9a-f]+:[0-9a-f]+", fields[3]):
                            raise ValueError("malformed mapped-file inventory")
                        major, minor = (int(s, 16) for s in fields[3].split(":"))
                        device, inode = os.makedev(major, minor), int(fields[4])
                        if device in devices or (device, inode) in owned:
                            holders += 1
                    after = _stat_identity(_read(process, "stat"))
                    if (after[0], after[2], after[3]) != (before[0], before[2], before[3]):
                        return None, None
                finally:
                    os.close(process)
            if tasks != sorted(n for n in os.listdir(root) if n.isascii() and n.isdigit()):
                return None, None
        except (OSError, ValueError, UnicodeError):
            return None, None
        # A positive reference is decisive. Empty /proc is not proof of absence
        # of orphan mount namespaces, socket-passed FDs, io_uring/AIO, extra loop
        # attachments or concurrent kernel references. Effective closure remains
        # missing and cannot be supplied by a flag or caller receipt.
        return aliases if aliases else None, holders if holders else None

    def _readback(self) -> PhysicalState:
        self._enter()
        rows = parse_mountinfo(_read(self.handles["proc"], "self/mountinfo"))
        mounts: dict[str, MountIdentity] = {}
        if self.initial is not None:
            for pinned_mount in self.initial.mounts.values():
                if pinned_mount.mount_id in rows and rows[pinned_mount.mount_id][0] != pinned_mount:
                    raise ValueError("owned mount moved or changed; not released")
        for name, target in self.mount_targets.items():
            found = [m for m, _, path in rows.values() if path == target]
            if len(found) > 1 or (found and found[0] is None):
                raise ValueError("owned mount target covered or changed filesystem")
            if found:
                mount = found[0]
                assert mount is not None
                if self.initial is not None and mount != self.initial.mounts[name]:
                    raise ValueError("owned mount identity substituted")
                mounts[name] = mount
        loops = {
            name: loop
            for name in (n[5:] for n in self.handles if n.startswith("loop:"))
            if (loop := self._loop(name)) is not None
        }
        loop_devices = {loop.rdev for loop in loops.values()}
        if any(
            os.makedev(*map(int, m.device.split(":"))) not in loop_devices
            for m in mounts.values()
            if m.filesystem == "ext4"
        ):
            raise ValueError("owned ext4 mount is not on an observed owned loop")
        backing: dict[str, FileIdentity] = {}
        for name, expected in self.backing.items():
            try:
                info = os.stat(name, dir_fd=self.handles["directory"], follow_symlinks=False)
            except FileNotFoundError:
                continue
            identity = FileIdentity(device=info.st_dev, inode=info.st_ino)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or identity != expected:
                raise ValueError("owned backing leaf replaced or aliased")
            backing[name] = identity
        if self.initial is None:
            # Seed mount IDs only from this actual kernel observation, so the
            # reference scan can distinguish owned mounts from same-device binds.
            self.initial = PhysicalState(
                namespace=NamespaceIdentity(**self.identities["namespace"].model_dump()),
                mounts=mounts,
                private_keyring=self.ring.serial,
                loops=loops,
                backing=backing,
            )
        devices = {os.makedev(*map(int, m.device.split(":"))) for m in self.initial.mounts.values()}
        aliases, holders = self._scan_references(devices)
        return PhysicalState(
            namespace=NamespaceIdentity(**self.identities["namespace"].model_dump()),
            mounts=mounts,
            private_keyring=self.ring.serial,
            keyring_state=_key_state(self.ring.serial),
            loops=loops,
            backing=backing,
            extra_mount_aliases=aliases,
            extra_open_holders=holders,
        )

    def readback(self) -> PhysicalState:
        self._verify()
        raw = self.jobs.run(
            lambda: self._readback().model_dump_json().encode(), set(self.handles.values())
        )
        return PhysicalState.model_validate_json(raw)

    def _effect(self, key: str, deadline: float, action: Callable[[], None]) -> None:
        if (
            self.effects_failed
            or not math.isfinite(deadline)
            or key in self.attempted
            or deadline != self.jobs.deadline
            or time.monotonic() >= deadline
        ):
            raise ValueError("storage operation already attempted or deadline differs")
        self.attempted.add(key)

        def guarded() -> bytes:
            if time.monotonic() >= deadline:
                raise ValueError("storage operation deadline exhausted")
            state = self._readback()
            if state.extra_mount_aliases != 0 or state.extra_open_holders != 0:
                raise ValueError("actual reference closure unavailable; storage retained")
            action()
            return b""

        try:
            self.jobs.run(guarded, set(self.handles.values()))
        except BaseException:
            self.effects_failed = True
            raise

    def unmount(self, mount: MountIdentity, deadline: float) -> None:
        def release() -> None:
            state = self._readback()
            if mount not in state.mounts.values():
                raise ValueError("exact pinned mount absent or changed")
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.umount2(ctypes.c_char_p(mount.target.encode()), ctypes.c_int(0)) != 0:
                raise OSError(ctypes.get_errno(), "owned unmount refused")

        self._effect("mount:" + str(mount.mount_id), deadline, release)

    def revoke_private_keyring(self, serial: int, deadline: float) -> None:
        def release() -> None:
            state = self._readback()
            if serial != self.ring.serial or state.mounts or state.keyring_state != "present":
                raise ValueError("private key revocation requires absent owned mounts")
            _keyctl(3, serial)  # REVOKE this exact positive private serial only

        self._effect("keyring", deadline, release)

    def detach_loop(self, loop: LoopIdentity, deadline: float) -> None:
        def release() -> None:
            state = self._readback()
            names = [n for n, identity in state.loops.items() if identity == loop]
            if state.mounts or state.keyring_state != "revoked" or len(names) != 1:
                raise ValueError("loop detach requires absent mounts and observed revoked key")
            fcntl.ioctl(self.handles["loop:" + names[0]], LOOP_CLR_FD, 0)

        self._effect("loop:" + str(loop.rdev), deadline, release)

    def remove_backing(self, name: str, identity: FileIdentity, deadline: float) -> None:
        _leaf(name)

        def release() -> None:
            state = self._readback()
            if (
                state.mounts
                or state.loops
                or state.keyring_state != "revoked"
                or state.backing.get(name) != identity
            ):
                raise ValueError("backing unlink requires independently released mount/key/loop")
            info = os.stat(name, dir_fd=self.handles["directory"], follow_symlinks=False)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
                or FileIdentity(device=info.st_dev, inode=info.st_ino) != identity
            ):
                raise ValueError("owned backing changed immediately before unlink")
            os.unlink(name, dir_fd=self.handles["directory"])

        self._effect("backing:" + name, deadline, release)


class StorageOwnerRefusal(ValueError):
    """Retain every acquired handle and the claimed private ring on refusal."""

    def __init__(self, owner: LinuxPhysicalOwner):
        super().__init__("Linux storage-owner readback refused; lifetime remains retained")
        self.owner = owner


class KeyringCreationRefusal(ValueError):
    """Preserve newly observed serial without asserting ownership or cleanup."""

    def __init__(self, ring: AnonymousKeyring):
        super().__init__("new anonymous keyring was not independently observed")
        self.ring = ring
