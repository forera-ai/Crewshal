"""From-creation namespace/backing/loop custody source, never an entry point.

This finite producer uses the original retained observer's admitted bounded job.
It never reconstructs ownership from child text or returns operational readiness.
Copied-root, ext4 and private-key/eCryptfs preparation are unqualified source.
Fixed installation, effective total growth and exact Linux/live qualification
remain required before any namespace parent or native execution.
"""

from array import array
import ctypes
import fcntl
import hashlib
import os
from pathlib import PurePosixPath
import platform
import select
import socket
import stat
import sys
import time
from typing import Literal, NoReturn

from crewshal.linux_envelope import prepare_linux_envelope
from crewshal.linux_inventory import (
    RetainedParentInventory,
    TrustedParentInventory,
    audit_parent_inventory,
    helper_library_inventory_digest,
    root_inventory_digest,
    _metadata,
)
from crewshal.contracts import record_digest
from crewshal.linux_setup import OwnedStorageReservation
from crewshal.linux_storage import (
    AnonymousKeyring,
    BoundedStorageJobs,
    LOOP_GET_STATUS64,
    LOOP_INFO64,
    LinuxPhysicalOwner,
    PRIVATE_KEY_PERMISSIONS,
    _key_state,
    _keyctl,
)

CLONE_NEWNS = 0x00020000
MS_REC_PRIVATE = 0x4000 | 0x40000
LOOP_CTL_GET_FREE = 0x4C82
LOOP_SET_FD = 0x4C00
LOOP_SET_STATUS64 = 0x4C04
BACKING_SIZES = {"scratch.img": 33554432, "candidate.img": 16777216}
# Authentication stays inside the original 1 GiB prepared allowance. The other
# two images consume the existing validator-scratch/frozen-candidate allowances.
ADDITIONAL_BACKING_SIZES = {
    "native-auth.img": 67108864,
    "validator-scratch.img": 33554432,
    "validator-candidate.img": 16777216,
}
ALL_BACKING_SIZES = {**BACKING_SIZES, **ADDITIONAL_BACKING_SIZES}
ROOT_COPY_BYTES = 1073741824 - ADDITIONAL_BACKING_SIZES["native-auth.img"]
ROLE_UIDS = {
    "scratch": 65534,
    "candidate": 65534,
    "native-auth": 65534,
    "validator-scratch": 65531,
    "validator-candidate": 0,
}


def _view_path(root: str, role: str, suffix: str) -> str:
    if role not in ROLE_UIDS or suffix not in {"-lower", "-upper"}:
        raise ValueError("fixed owned filesystem view required")
    target = (
        role
        if suffix == "-upper" and role in {"native-auth", "validator-candidate"}
        else role + suffix
    )
    return root + "/" + target


def _add_private_key(kind: str, description: str, payload: object, size: int, ring: int) -> int:
    """One add_key syscall into an already created private ring, never @s/@u."""
    machine = platform.machine()
    if sys.platform != "linux" or machine not in {"x86_64", "aarch64"}:
        raise ValueError("supported Linux add_key ABI unavailable")
    if kind not in {"user", "encrypted"} or ring <= 0 or not 0 < size <= 4096:
        raise ValueError("bounded private key payload required")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    serial = int(
        libc.syscall(
            ctypes.c_long(248 if machine == "x86_64" else 217),
            ctypes.c_char_p(kind.encode("ascii")),
            ctypes.c_char_p(description.encode("ascii")),
            ctypes.cast(payload, ctypes.c_void_p),
            ctypes.c_ulong(size),
            ctypes.c_int(ring),
        )
    )
    if serial <= 0:
        raise OSError(ctypes.get_errno(), "private key creation refused")
    return serial


def _private_key_description(serial: int, kind: str, description: str) -> None:
    buffer = ctypes.create_string_buffer(4096)
    length = _keyctl(6, serial, buffer, len(buffer))
    expected = f"{kind};0;0;003f0000;{description}".encode("ascii") + b"\0"
    if length != len(expected) or buffer.raw[:length] != expected:
        raise ValueError("private key owner/permissions/description readback differs")


class PrivateEcryptfsKeys:
    """Finite root-owned master/auth-token creation in original observer's ring.

    The ring atomically holds new keys on add_key success or unknown response.
    Refusal never unlinks, revokes, rejoins or retries. No master bytes leave the
    original task. Source and synthetic tests do not qualify syscall containment
    or mount-time eCryptfs access under the eventual dropped role identities.
    """

    resources_reusable: Literal[False] = False
    operational_ready: Literal[False] = False

    def __init__(self, reservation: OwnedStorageReservation, ring: AnonymousKeyring):
        if hasattr(reservation, "_ecryptfs_keys"):
            raise ValueError("private eCryptfs keys are one-shot; no retry")
        self.reservation, self.ring = reservation, ring
        self._owners = (reservation, ring)
        self.serials: dict[str, int] = {}
        self.failed = False
        self.complete = False
        self.attempted = False
        setattr(reservation, "_ecryptfs_keys", self)
        reservation.verify()
        if (
            type(ring) is not AnonymousKeyring
            or getattr(reservation, "_private_ring", None) is not ring
            or not ring.complete
            or ring.creator != os.getpid()
            or ring.serial <= 0
        ):
            self.failed = True
            raise ValueError("private keys require original live anonymous credential anchor")
        self._ring_identity = (ring.serial, ring.creator, ring.previous)
        self.master_description = "crewshal-" + os.urandom(16).hex()
        self.signature = os.urandom(8).hex()
        self._descriptions = (self.master_description, self.signature)

    def _verify(self) -> None:
        self.reservation.verify()
        if (
            self._owners[0] is not self.reservation
            or self._owners[1] is not self.ring
            or getattr(self.reservation, "_ecryptfs_keys", None) is not self
            or getattr(self.reservation, "_private_ring", None) is not self.ring
            or (self.ring.serial, self.ring.creator, self.ring.previous) != self._ring_identity
            or self._descriptions != (self.master_description, self.signature)
            or not self.ring.complete
            or _key_state(self.ring.serial) != "present"
        ):
            raise ValueError("original private key ownership differs")

    def create(self) -> None:
        if self.attempted or self.failed:
            raise ValueError("private eCryptfs key creation is one-shot; no retry")
        self.attempted = True
        master = ctypes.create_string_buffer(32)
        try:
            self._verify()
            # A temporary immutable os.urandom result stays private to this
            # original task; only the mutable syscall buffer can be scrubbed.
            # Do not claim erasure of every interpreter/kernel representation.
            master.raw = os.urandom(32)
            self.serials["master"] = _add_private_key(
                "user", self.master_description, master, 32, self.ring.serial
            )
            _keyctl(5, self.serials["master"], ctypes.c_void_p(PRIVATE_KEY_PERMISSIONS))
            _private_key_description(self.serials["master"], "user", self.master_description)
            self._verify()
            payload = f"new ecryptfs user:{self.master_description} 64".encode("ascii")
            token = ctypes.create_string_buffer(payload)
            self.serials["auth"] = _add_private_key(
                "encrypted", self.signature, token, len(payload), self.ring.serial
            )
            _keyctl(5, self.serials["auth"], ctypes.c_void_p(PRIVATE_KEY_PERMISSIONS))
            _private_key_description(self.serials["auth"], "encrypted", self.signature)
            self._verify()
            membership = ctypes.create_string_buffer(8)
            if (
                _keyctl(11, self.ring.serial, membership, 8) != 8
                or set(array("i", membership.raw)) != set(self.serials.values())
                or len(set(self.serials.values())) != 2
            ):
                raise ValueError("actual private ring membership differs")
            self.complete = True
        except BaseException:
            self.failed = True
            raise
        finally:
            ctypes.memset(ctypes.addressof(master), 0, len(master))

    def __reduce__(self) -> NoReturn:
        raise TypeError("private key custody cannot be copied or exported")


def _namespace_is_private() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    # Only propagation changes; never unmount or affect an inherited mount.
    if libc.mount(None, b"/", None, ctypes.c_ulong(MS_REC_PRIVATE), None) != 0:
        raise OSError(ctypes.get_errno(), "private namespace propagation refused")


def _unshare_mount_namespace() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.unshare(ctypes.c_int(CLONE_NEWNS)) != 0:
        raise OSError(ctypes.get_errno(), "owned namespace creation refused")


def _enter_owned_namespace(descriptor: int) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.setns(ctypes.c_int(descriptor), ctypes.c_int(CLONE_NEWNS)) != 0:
        raise OSError(ctypes.get_errno(), "owned namespace entry refused")
    actual = os.stat("/proc/self/ns/mnt")
    retained = os.fstat(descriptor)
    if (actual.st_dev, actual.st_ino) != (retained.st_dev, retained.st_ino):
        raise ValueError("entered namespace differs from retained kernel object")


def _readonly_bind(path: str, *, remount: bool) -> None:
    """Only bind/remount the already owned copied root; never unmount."""
    libc = ctypes.CDLL(None, use_errno=True)
    raw = path.encode("ascii")
    flags = 4096 | (32 | 1 | 2 | 4 if remount else 0)  # BIND; REMOUNT/RDONLY/NOSUID/NODEV.
    if libc.mount(None if remount else raw, raw, None, ctypes.c_ulong(flags), None) != 0:
        raise OSError(ctypes.get_errno(), "owned readonly root projection refused")


def _mount_owned(
    source: str, target: str, filesystem: str, options: str | None, *, native_auth: bool = False
) -> None:
    if filesystem not in {"ext4", "ecryptfs"}:
        raise ValueError("only accepted owned filesystem mechanisms allowed")
    libc = ctypes.CDLL(None, use_errno=True)
    # Stock managed helpers execute inside private native authentication storage.
    # This fixed preparation choice grants no tool or validator access authority.
    if (
        libc.mount(
            source.encode("ascii"),
            target.encode("ascii"),
            filesystem.encode("ascii"),
            ctypes.c_ulong(2 | 4 | (0 if native_auth else 8)),
            None if options is None else options.encode("ascii"),
        )
        != 0
    ):
        raise OSError(ctypes.get_errno(), "owned encrypted filesystem mount refused")


def _filesystem_magic(descriptor: int) -> int:
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise ValueError("supported Linux filesystem descriptor readback unavailable")
    libc = ctypes.CDLL(None, use_errno=True)
    result = ctypes.create_string_buffer(256)
    if libc.fstatfs(ctypes.c_int(descriptor), ctypes.byref(result)) != 0:
        raise OSError(ctypes.get_errno(), "owned filesystem descriptor readback refused")
    return ctypes.c_long.from_buffer(result).value


def _encode_device(value: int) -> int:
    return (os.minor(value) & 0xFF) | (os.major(value) << 8) | ((os.minor(value) & ~0xFF) << 12)


def _copy_root_files(
    destination: int, inventory: TrustedParentInventory, sources: dict[str, int]
) -> None:
    """Bounded exclusive copy of explicit input FDs; no import, exec or link walk.

    Caller must already hold actual destination ownership under original job
    containment and retain its FD before this function. This is copying only;
    effective physical growth, readonly mounts and installed identities remain
    separate gates. Never derive runtime authority from matching content hashes.
    """
    inventory = audit_parent_inventory(inventory)
    files = {path for path, entry in inventory.root.items() if entry.kind == "file"}
    if set(sources) != files:
        raise ValueError("exact root file descriptor inventory required")
    sizes: dict[str, int] = {}
    metadata: dict[str, tuple[int, ...]] = {}
    total = 0
    allocated_bound = len(inventory.root) * 4096
    for path in sorted(files):
        info = os.fstat(sources[path])
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != 0
            or info.st_gid != 0
            or info.st_mode & 0o7022
            or info.st_nlink != 1
            or info.st_size < 0
        ):
            raise ValueError("private root input identity/ownership differs")
        total += info.st_size
        allocated_bound += (info.st_size + 4095) // 4096 * 4096
        sizes[path] = info.st_size
        metadata[path] = _metadata(info)
    if max(total, allocated_bound) > ROOT_COPY_BYTES:
        raise ValueError("prepared root exceeds original logical/allocated reservation")
    root = os.fstat(destination)
    if not stat.S_ISDIR(root.st_mode) or root.st_uid != 0 or root.st_gid != 0:
        raise ValueError("private copied root requires actual root-owned directory")
    geometry = os.fstatvfs(destination)
    if geometry.f_frsize != 4096 or geometry.f_bsize != 4096:
        raise ValueError("copied root requires bounded 4096-byte allocation geometry")
    directories = {"/": destination}
    opened: list[int] = []
    try:
        for path, entry in sorted(
            inventory.root.items(), key=lambda item: (item[0].count("/"), item[0])
        ):
            if path == "/":
                continue
            name = PurePosixPath(path).name
            parent = directories[str(PurePosixPath(path).parent)]
            if entry.kind == "directory":
                os.mkdir(name, 0o700, dir_fd=parent)
                descriptor = os.open(
                    name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent
                )
                opened.append(descriptor)
                info = os.fstat(descriptor)
                if info.st_dev != root.st_dev or info.st_uid != 0 or info.st_gid != 0:
                    raise ValueError("copied root directory device/ownership differs")
                directories[path] = descriptor
            elif entry.kind == "symlink":
                assert entry.target is not None
                os.symlink(entry.target, name, dir_fd=parent)
            else:
                source = sources[path]
                before = os.fstat(source)
                if _metadata(before) != metadata[path]:
                    raise ValueError("root input identity changed before copy")
                descriptor = os.open(
                    name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                    0o600,
                    dir_fd=parent,
                )
                try:
                    offset = 0
                    sha = hashlib.sha256()
                    while offset < sizes[path]:
                        chunk = os.pread(source, min(65536, sizes[path] - offset), offset)
                        if not chunk:
                            raise ValueError("root input truncated during copy")
                        sha.update(chunk)
                        position = 0
                        while position < len(chunk):
                            written = os.write(descriptor, chunk[position:])
                            if written <= 0:
                                raise ValueError("root copy incomplete")
                            position += written
                        offset += len(chunk)
                    if (
                        _metadata(before) != _metadata(os.fstat(source))
                        or sha.hexdigest() != entry.sha256
                    ):
                        raise ValueError("root input bytes/identity changed during copy")
                    os.fchmod(descriptor, entry.mode)
                    os.fsync(descriptor)
                    copied = os.fstat(descriptor)
                    if (
                        copied.st_size != sizes[path]
                        or copied.st_blocks * 512 > (sizes[path] + 4095) // 4096 * 4096
                    ):
                        raise ValueError("root file exceeds original copy accounting")
                finally:
                    os.close(descriptor)
        for path, descriptor in sorted(directories.items(), key=lambda item: -item[0].count("/")):
            os.fchmod(descriptor, inventory.root[path].mode)
            os.fsync(descriptor)
    finally:
        # Only private copy-job duplicates close. The retaining observer's root
        # and original input handles survive all failures; no unlink occurs.
        for descriptor in opened:
            os.close(descriptor)


class ProductionRefusal(ValueError):
    def __init__(self, reason: str, production: "OwnedBackingProduction"):
        super().__init__(reason)
        self.production = production
        self.resources_reusable = False


class _CreationChannel:
    """One exact FD per acknowledged fixed stage; every received FD is pinned.

    No textual descriptor number is accepted. Unrecognized/malformed messages
    retain even their unexpected descriptors before refusing. The child awaits
    an acknowledgement before truncate, attach or propagation/mount effects.
    """

    def __init__(self, production: "OwnedBackingProduction"):
        self.production = production
        self.parent: socket.socket | None = None
        self.child: socket.socket | None = None
        self.expected: list[str] = []
        self.position = 0

    @property
    def descriptor(self) -> int:
        if self.parent is None:
            raise ValueError("retained creation transport unavailable")
        return self.parent.fileno()

    def open(self) -> None:
        cloexec = getattr(socket, "SOCK_CLOEXEC", None)
        nonblock = getattr(socket, "SOCK_NONBLOCK", None)
        if not isinstance(cloexec, int) or not isinstance(nonblock, int):
            raise ValueError("Linux atomic creation-channel flags unavailable")
        self.parent, self.child = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_SEQPACKET | cloexec | nonblock
        )

    def transfer(self, name: str, descriptor: int) -> None:
        if self.child is None:
            raise ValueError("retained child transport unavailable")
        deadline = self.production.deadline
        # The following state changes are child's private fork copy only.
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([], [self.child], [], remaining)[1]:
            raise ValueError("original creation deadline exhausted")
        message = name.encode("ascii")
        if self.child.sendmsg(
            [message], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", [descriptor]))]
        ) != len(message):
            raise ValueError("actual FD custody transfer refused")
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([self.child], [], [], remaining)[0]:
            raise ValueError("original custody acknowledgement deadline exhausted")
        if self.child.recv(2) != b"1":
            raise ValueError("actual parent custody acknowledgement refused")

    def pump(self) -> None:
        production = self.production
        if self.parent is None:
            raise ValueError("retained parent transport unavailable")
        cloexec = getattr(socket, "MSG_CMSG_CLOEXEC", None)
        if not isinstance(cloexec, int):
            raise ValueError("Linux atomic received-FD flags unavailable")
        message, ancillary, flags, _ = self.parent.recvmsg(
            128, socket.CMSG_SPACE(16 * array("i").itemsize), cloexec
        )
        received: list[int] = []
        malformed = False
        for level, kind, raw in ancillary:
            if level != socket.SOL_SOCKET or kind != socket.SCM_RIGHTS:
                malformed = True
                continue
            descriptors = array("i")
            if len(raw) % descriptors.itemsize:
                malformed = True
            descriptors.frombytes(raw[: len(raw) - len(raw) % descriptors.itemsize])
            for descriptor in descriptors:
                # Pin BEFORE metadata parsing/verification; no exception path
                # closes an acquired kernel handle or refunds the reservation.
                production.received.append(descriptor)
                received.append(descriptor)
        if (
            malformed
            or flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC)
            or len(received) != 1
            or self.position >= len(self.expected)
            or message != self.expected[self.position].encode("ascii")
        ):
            raise ValueError("actual FD custody stage/message differs")
        name, descriptor = self.expected[self.position], received[0]
        production.handles[name] = descriptor
        production._verify_transferred(name, descriptor)
        production.verify()
        if not select.select([], [self.parent], [], 0)[1] or self.parent.send(b"1") != 1:
            raise ValueError("bounded custody acknowledgement refused")
        self.position += 1


class OwnedBackingProduction:
    """Live partial production pinned before the first creation effect.

    Caller must retain a root-owned private backing directory created by trusted
    setup inside the exact owned root, and a journal-bound full reservation.
    This source does not supply that directory/root producer or qualification.
    Handles, channel and pending job remain strongly owned on every refusal.
    """

    resources_reusable: Literal[False] = False
    operational_ready: Literal[False] = False

    def __init__(
        self,
        reservation: OwnedStorageReservation,
        directory_fd: int,
        jobs: BoundedStorageJobs,
    ):
        if hasattr(reservation, "_production"):
            raise ValueError("owned storage production is one-shot; no reconstruction")
        # Retain original inputs even if duplication or admission fails.
        self.reservation, self.jobs = reservation, jobs
        self._owners = (reservation, jobs)
        self.original_directory = directory_fd
        self.handles: dict[str, int] = {}
        self.received: list[int] = []
        self.attempted = False
        self.failed = False
        self.complete = False
        self.channel = _CreationChannel(self)
        setattr(reservation, "_production", self)
        self.deadline = jobs.deadline
        self._deadline = jobs.deadline
        self.root = prepare_linux_envelope(reservation._configuration).owned_root
        try:
            reservation.verify()
            if getattr(reservation, "capacity_claim", None) is None:
                raise ValueError("production requires its original durable capacity claim")
            if (
                jobs.observer is not reservation.observer
                or jobs.group is not reservation.observer_group
                or jobs.aggregate is not reservation.aggregate
                or jobs.observer.spec.pid != os.getpid()
                or not time.monotonic()
                < jobs.deadline
                <= min(time.monotonic() + 30, reservation.batch_started + 120)
            ):
                raise ValueError("production requires original bounded retained observer/job")
            self.handles["directory"] = os.dup(directory_fd)
            self.directory_identity = self._directory(self.handles["directory"])
            self.channel.open()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def __reduce__(self) -> NoReturn:
        raise TypeError("live production cannot be copied or exported")

    def _directory(self, descriptor: int) -> tuple[int, int]:
        info = os.fstat(descriptor)
        path = os.readlink(f"/proc/self/fd/{descriptor}")
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != 0
            or stat.S_IMODE(info.st_mode) != 0o700
            or path != str(PurePosixPath(self.root) / "backing")
        ):
            raise ValueError("exact root-owned private backing directory required")
        return info.st_dev, info.st_ino

    def verify(self) -> None:
        if self.jobs.pending is None:
            self.reservation.verify()
        else:
            self.reservation.verify_creation_job(self.jobs)
        if (
            self.reservation is not self._owners[0]
            or self.jobs is not self._owners[1]
            or getattr(self.reservation, "_production", None) is not self
            or self.jobs.observer is not self.reservation.observer
            or self.jobs.group is not self.reservation.observer_group
            or self.jobs.aggregate is not self.reservation.aggregate
            or self.jobs.observer.spec.pid != os.getpid()
            or self.deadline != self._deadline
            or self.jobs.deadline != self._deadline
            or not time.monotonic() < self._deadline
            or self._directory(self.handles["directory"]) != self.directory_identity
        ):
            raise ValueError("original retained production identity/deadline differs")

    def _verify_transferred(self, name: str, descriptor: int) -> None:
        info = os.fstat(descriptor)
        if not fcntl.fcntl(descriptor, fcntl.F_GETFD) & fcntl.FD_CLOEXEC:
            raise ValueError("received descriptor must be close-on-exec")
        if name == "namespace":
            path = os.readlink(f"/proc/self/fd/{descriptor}")
            if not stat.S_ISREG(info.st_mode) or not path.startswith("mnt:["):
                raise ValueError("received mount namespace FD differs")
            original = os.stat("/proc/self/ns/mnt")
            if (info.st_dev, info.st_ino) == (original.st_dev, original.st_ino):
                raise ValueError("new namespace must differ from observer namespace")
        elif name == "loop-control":
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(10, 237):
                raise ValueError("received Linux loop-control device differs")
        elif name.startswith("loop:"):
            if not stat.S_ISBLK(info.st_mode) or os.major(info.st_rdev) != 7:
                raise ValueError("received owned loop FD differs")
            # No potentially blocking ioctl in the observer. SET_FD in the
            # bounded child atomically refuses any attached/rundown loop.
            # GET_FREE/ENXIO never proves release or authorizes host cleanup.
        elif name in ALL_BACKING_SIZES:
            parent = self.handles["directory"]
            linked = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != 0
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_nlink != 1
                or info.st_size != 0
                or (info.st_dev, info.st_ino) != (linked.st_dev, linked.st_ino)
                or (info.st_dev, info.st_ino) == self.directory_identity
            ):
                raise ValueError("new backing FD independent readback differs")
        elif name == "readonly-root":
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o700
                or os.readlink(f"/proc/self/fd/{descriptor}") != self.root + "/readonly-root"
                or info.st_dev != os.fstat(self.handles["root-parent"]).st_dev
            ):
                raise ValueError("new copied-root FD independent readback differs")
        elif name == "readonly-projection":
            original = os.fstat(self.handles["readonly-root"])
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o755
                or (info.st_dev, info.st_ino) != (original.st_dev, original.st_ino)
                or os.readlink(f"/proc/self/fd/{descriptor}") != self.root + "/readonly-root"
            ):
                raise ValueError("actual readonly-root projection identity differs")
        elif name in {
            "mounted:" + role + suffix
            for role in (
                "scratch",
                "candidate",
                "native-auth",
                "validator-scratch",
                "validator-candidate",
            )
            for suffix in ("-lower", "-upper")
        }:
            target = name.removeprefix("mounted:")
            lower = target.endswith("-lower")
            role = target.removesuffix("-lower").removesuffix("-upper")
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or _filesystem_magic(descriptor) != (0xEF53 if lower else 0xF15F)
                or os.readlink(f"/proc/self/fd/{descriptor}")
                != _view_path(self.root, role, "-lower" if lower else "-upper")
                or (
                    lower and info.st_dev != os.fstat(self.handles["loop:" + role + ".img"]).st_rdev
                )
            ):
                raise ValueError("actual mounted owned filesystem identity differs")
        else:
            raise ValueError("unexpected transferred creation slot")

    def create(self) -> None:
        """One admitted child creates/pins namespace, backing files and loops.

        Every handle handoff precedes the subsequent modifying stage. Completion
        means these partial objects only; no filesystem/model execution is ready.
        """
        if self.attempted or self.failed:
            raise ValueError("owned production is one-shot; no retry")
        self.attempted = True
        try:
            self.verify()
            if self.channel.child is None:
                raise ValueError("creation child transport unavailable")
            self.channel.expected = ["namespace", "loop-control"]
            for name in BACKING_SIZES:
                self.channel.expected.extend([name, "loop:" + name])
            reply = self.jobs.run(
                self._create_child,
                {self.handles["directory"], self.channel.child.fileno()},
                transfer=self.channel,
            )
            self.verify()
            if reply != b"partial-objects-created" or self.channel.position != len(
                self.channel.expected
            ):
                raise ValueError("complete actual FD custody handoff unavailable")
            expected = bytearray()
            for name, size in BACKING_SIZES.items():
                backing = os.fstat(self.handles[name])
                if backing.st_size != size or backing.st_blocks * 512 > size:
                    raise ValueError("owned backing exceeds fixed logical/allocated size")
                expected.extend(self._expected_loop(name, backing))
            observed = self.jobs.run(self._readback, set(self.handles.values()))
            self.verify()
            if observed != bytes(expected):
                raise ValueError("actual owned loop/backing kernel identity differs")
            self.complete = True
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _create_child(self) -> bytes:
        _unshare_mount_namespace()
        namespace = os.open("/proc/self/ns/mnt", os.O_RDONLY | os.O_CLOEXEC)
        self.channel.transfer("namespace", namespace)
        _namespace_is_private()
        control = os.open("/dev/loop-control", os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
        self.channel.transfer("loop-control", control)
        self._create_images(BACKING_SIZES, self.channel, control)
        return b"partial-objects-created"

    def _create_images(
        self, sizes: dict[str, int], channel: _CreationChannel, control: int
    ) -> None:
        for name, size in sizes.items():
            backing = os.open(
                name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600,
                dir_fd=self.handles["directory"],
            )
            channel.transfer(name, backing)
            os.ftruncate(backing, size)
            number = fcntl.ioctl(control, LOOP_CTL_GET_FREE)
            if not isinstance(number, int) or not 0 <= number < 1048576:
                raise ValueError("bounded Linux free-loop identity unavailable")
            loop = os.open(f"/dev/loop{number}", os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
            info = os.fstat(loop)
            if not stat.S_ISBLK(info.st_mode) or info.st_rdev != os.makedev(7, number):
                # The admitted job retains this unrecognized handle until its
                # termination; no ioctl may modify it before parent handoff.
                raise ValueError("actual selected loop major/minor differs")
            channel.transfer("loop:" + name, loop)
            # SET_FD refuses an already attached loop; no retry/search/cleanup.
            fcntl.ioctl(loop, LOOP_SET_FD, backing)
            backing_info = os.fstat(backing)
            raw = LOOP_INFO64.pack(
                _encode_device(backing_info.st_dev),
                backing_info.st_ino,
                0,
                0,
                size,
                number,
                0,
                0,
                0,
                bytes(64),
                bytes(64),
                bytes(32),
                0,
                0,
            )
            fcntl.ioctl(loop, LOOP_SET_STATUS64, raw)

    def create_auxiliary_backings(self) -> None:
        """One finite set for private auth, fresh validator and frozen candidate.

        All images stay charged to the original reservation and use original
        admitted jobs/namespace/loop-control. No absent leaf grants availability;
        exclusive creation only refuses collisions, never removes or reuses them.
        """
        if (
            hasattr(self, "_auxiliary_channel")
            or hasattr(self, "_format_attempted")
            or self.failed
            or not self.complete
        ):
            raise ValueError("auxiliary creation requires original custody before format; no retry")
        self._auxiliary_channel = _CreationChannel(self)
        try:
            self.verify()
            channel = self._auxiliary_channel
            channel.open()
            channel.expected = [
                slot for name in ADDITIONAL_BACKING_SIZES for slot in (name, "loop:" + name)
            ]
            assert channel.child is not None
            reply = self.jobs.run(
                self._create_auxiliary_child,
                {
                    self.handles["namespace"],
                    self.handles["directory"],
                    self.handles["loop-control"],
                    channel.child.fileno(),
                },
                transfer=channel,
            )
            self.verify()
            if reply != b"auxiliary-backings-created" or channel.position != 6:
                raise ValueError("auxiliary actual FD custody incomplete")
            expected = b"".join(
                self._expected_loop(name, os.fstat(self.handles[name]))
                for name in ALL_BACKING_SIZES
            )
            if self.jobs.run(self._readback, set(self.handles.values())) != expected:
                raise ValueError("auxiliary owned loop/backing kernel identity differs")
            self.verify()
            self._auxiliary_complete = True
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _create_auxiliary_child(self) -> bytes:
        _enter_owned_namespace(self.handles["namespace"])
        self._create_images(
            ADDITIONAL_BACKING_SIZES, self._auxiliary_channel, self.handles["loop-control"]
        )
        return b"auxiliary-backings-created"

    def copy_root(self, inventory: TrustedParentInventory, source_fds: dict[str, int]) -> None:
        """One retained root copy in the existing bounded namespace/job lifetime.

        No installed pool, readonly mount, loader closure or authority is inferred.
        Output custody precedes copying; partial copied bytes remain retained.
        """
        if hasattr(self, "_root_inputs") or self.failed or not self.complete:
            raise ValueError("root copying requires original completed custody; no retry")
        self._root_inputs: dict[str, int] = {}
        self._root_original_inputs = dict(source_fds)
        try:
            self.verify()
            self._root_manifest = audit_parent_inventory(inventory)
            bindings = self.reservation._configuration.linux_envelope
            if (
                bindings is None
                or bindings.parent_inventory_sha256 != record_digest(self._root_manifest)
                or bindings.root_inventory_sha256 != root_inventory_digest(self._root_manifest)
                or bindings.helper_library_inventory_sha256
                != helper_library_inventory_digest(self._root_manifest)
            ):
                raise ValueError("root copy requires current exact inventory bindings")
            files = {
                name for name, entry in self._root_manifest.root.items() if entry.kind == "file"
            }
            if set(source_fds) != files:
                raise ValueError("root copy requires every original file input FD")
            for name, descriptor in source_fds.items():
                self._root_inputs[name] = os.dup(descriptor)
            parent = os.open(
                "..",
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=self.handles["directory"],
            )
            self.handles["root-parent"] = parent
            info = os.fstat(parent)
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o700
                or os.readlink(f"/proc/self/fd/{parent}") != self.root
            ):
                raise ValueError("root copy requires original private owned parent directory")
            self._root_channel = _CreationChannel(self)
            self._root_channel.open()
            self._root_channel.expected = ["readonly-root"]
            assert self._root_channel.child is not None
            reply = self.jobs.run(
                self._copy_root_child,
                {
                    *self._root_inputs.values(),
                    parent,
                    self.handles["namespace"],
                    self._root_channel.child.fileno(),
                },
                transfer=self._root_channel,
            )
            self.verify()
            if reply != b"root-copied" or self._root_channel.position != 1:
                raise ValueError("copied-root transport incomplete")
            self.root_inventory = RetainedParentInventory(
                self.handles["readonly-root"], self._root_manifest
            )
            self.root_inventory.verify()
            self.verify()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _copy_root_child(self) -> bytes:
        _enter_owned_namespace(self.handles["namespace"])
        parent = self.handles["root-parent"]
        os.mkdir("readonly-root", 0o700, dir_fd=parent)
        destination = os.open(
            "readonly-root",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=parent,
        )
        self._root_channel.transfer("readonly-root", destination)
        _copy_root_files(destination, self._root_manifest, self._root_inputs)
        return b"root-copied"

    def project_readonly_root(self) -> None:
        """Retain the new mount FD before remount, then observe that exact FD.

        This does not prove the pool's total accounting or loader closure and
        grants no runtime readiness. Unknown bind/remount results stay retained.
        """
        if (
            hasattr(self, "_root_mount_channel")
            or self.failed
            or not hasattr(self, "root_inventory")
        ):
            raise ValueError("readonly root projection requires original copied root; no retry")
        self._root_mount_channel = _CreationChannel(self)
        try:
            self.verify()
            self.root_inventory.verify()
            self._root_mount_channel.open()
            self._root_mount_channel.expected = ["readonly-projection"]
            assert self._root_mount_channel.child is not None
            reply = self.jobs.run(
                self._readonly_root_child,
                {
                    self.handles["namespace"],
                    self.handles["readonly-root"],
                    self._root_mount_channel.child.fileno(),
                },
                transfer=self._root_mount_channel,
            )
            self.verify()
            if reply != b"root-projected" or self._root_mount_channel.position != 1:
                raise ValueError("readonly root transport incomplete")
            descriptor = self.handles["readonly-projection"]
            if not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY:
                raise ValueError("actual retained root mount remains writable")
            self.projected_inventory = RetainedParentInventory(descriptor, self._root_manifest)
            self.projected_inventory.verify()
            self.verify()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _readonly_root_child(self) -> bytes:
        _enter_owned_namespace(self.handles["namespace"])
        path = self.root + "/readonly-root"
        before = os.stat(path)
        expected = os.fstat(self.handles["readonly-root"])
        if (before.st_dev, before.st_ino) != (expected.st_dev, expected.st_ino):
            raise ValueError("owned root path changed before bind")
        _readonly_bind(path, remount=False)
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        self._root_mount_channel.transfer("readonly-projection", descriptor)
        _readonly_bind(path, remount=True)
        return b"root-projected"

    def format_filesystems(self) -> None:
        """Exec only copied, inventory-bound mkfs.ext4 in original bounded jobs.

        This is trusted setup source, not a generic program launcher. Exact
        installed formatter/loader behavior still needs Linux qualification.
        Exit/output never supplies storage release or a successful mount claim.
        """
        if (
            hasattr(self, "_format_attempted")
            or self.failed
            or not hasattr(self, "projected_inventory")
        ):
            raise ValueError("formatting requires original projected root; no retry")
        self._format_attempted = True
        try:
            self.verify()
            self.projected_inventory.verify()
            entry = self._root_manifest.root.get("/usr/sbin/mkfs.ext4")
            if entry is None or entry.kind != "file" or not entry.mode & 0o111:
                raise ValueError("exact copied ext4 formatter inventory required")
            formatter = os.open(
                "usr/sbin/mkfs.ext4",
                os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=self.projected_inventory.descriptor,
            )
            self.handles["formatter"] = formatter
            before = os.fstat(formatter)
            sha = hashlib.sha256()
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_size > 134217728
                or os.pread(formatter, 4, 0) != b"\x7fELF"
            ):
                raise ValueError("bounded copied ELF ext4 formatter required")
            offset = 0
            while offset < before.st_size:
                chunk = os.pread(formatter, min(65536, before.st_size - offset), offset)
                if not chunk:
                    raise ValueError("copied formatter read incomplete")
                sha.update(chunk)
                offset += len(chunk)
            if sha.hexdigest() != entry.sha256 or _metadata(before) != _metadata(
                os.fstat(formatter)
            ):
                raise ValueError("copied formatter bytes/identity differ")
            self._ext4_metadata: dict[str, bytes] = {}
            sizes = (
                ALL_BACKING_SIZES if getattr(self, "_auxiliary_complete", False) else BACKING_SIZES
            )
            for name in sizes:
                self._format_name = name
                self.jobs.run(
                    self._format_child,
                    {formatter, self.handles["loop:" + name], self.handles[name]},
                    _format_output=True,
                )
                self.verify()
                # Positively read the newly formatted owned backing, not command
                # status. Ext4's magic and declared byte geometry must fit the
                # original image. Full feature/loader/mount qualification follows.
                block = os.pread(self.handles[name], 1024, 1024)
                if len(block) != 1024 or block[56:58] != b"\x53\xef":
                    raise ValueError("actual owned ext4 superblock unavailable")
                blocks = (
                    int.from_bytes(block[4:8], "little")
                    | int.from_bytes(block[336:340], "little") << 32
                )
                shift = int.from_bytes(block[24:28], "little")
                if shift > 2 or blocks * (1024 << shift) != sizes[name]:
                    raise ValueError("owned ext4 declared size differs from original backing")
                self._ext4_metadata[name] = block
            self.verify()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _format_child(self) -> bytes:
        name = self._format_name
        loop = self.handles["loop:" + name]
        raw = bytearray(LOOP_INFO64.size)
        fcntl.ioctl(loop, LOOP_GET_STATUS64, raw, True)
        if bytes(raw) != self._expected_loop(name, os.fstat(self.handles[name])):
            raise ValueError("owned loop identity changed before formatting")
        # Duplicate before normalizing so overlapping source numbers cannot
        # substitute a formatter for its owned loop or leak unrelated handles.
        retained_loop = fcntl.fcntl(loop, fcntl.F_DUPFD_CLOEXEC, 16)
        formatter = fcntl.fcntl(self.handles["formatter"], fcntl.F_DUPFD_CLOEXEC, 16)
        os.dup2(retained_loop, 3)
        for text in os.listdir("/proc/self/fd"):
            descriptor = int(text)
            if descriptor > 3 and descriptor != formatter:
                try:
                    os.close(descriptor)
                except OSError as error:
                    if error.errno != 9:
                        raise
        os.execve(
            formatter,
            ["/usr/sbin/mkfs.ext4", "-q", "-F", "-m", "0", "/proc/self/fd/3"],
            {"MKE2FS_CONFIG": "/dev/null"},
        )
        raise ValueError("fixed formatter exec unexpectedly returned")

    def mount_encrypted_views(self, keys: PrivateEcryptfsKeys) -> None:
        """Mount only original fixed role backings, retaining actual mount FDs.

        The original retained namespace owns even a failed mount before a mount
        FD can be transferred. Unknown effects remain charged and never unmount.
        Auxiliary views require their original preceding custody and formatting.
        Credential/tool separation and aggregate growth remain qualification
        gates; no operational readiness follows from these source operations.
        """
        if (
            hasattr(self, "_mount_channel")
            or self.failed
            or set(getattr(self, "_ext4_metadata", {}))
            != set(
                ALL_BACKING_SIZES if getattr(self, "_auxiliary_complete", False) else BACKING_SIZES
            )
        ):
            raise ValueError("encrypted mounts require original formatted backings; no retry")
        self._mount_channel = _CreationChannel(self)
        self._keys = keys
        roles = tuple(name.removesuffix(".img") for name in self._ext4_metadata)
        self.mounts = {
            role + suffix: _view_path(self.root, role, suffix)
            for role in roles
            for suffix in ("-lower", "-upper")
        }
        try:
            self.verify()
            if (
                type(keys) is not PrivateEcryptfsKeys
                or keys.reservation is not self.reservation
                or not keys.complete
                or keys.failed
            ):
                raise ValueError("mounts require original complete private key custody")
            keys._verify()
            self._mount_channel.open()
            self._mount_channel.expected = ["mounted:" + target for target in self.mounts]
            assert self._mount_channel.child is not None
            reply = self.jobs.run(
                self._mount_views_child,
                {
                    self.handles["namespace"],
                    self.handles["root-parent"],
                    self._mount_channel.child.fileno(),
                    *(self.handles["loop:" + name] for name in self._ext4_metadata),
                    *(self.handles[name] for name in self._ext4_metadata),
                },
                transfer=self._mount_channel,
            )
            self.verify()
            keys._verify()
            if reply != b"encrypted-views-mounted" or self._mount_channel.position != len(
                self.mounts
            ):
                raise ValueError("encrypted view custody transfer incomplete")
            for role in roles:
                lower = self.handles["mounted:" + role + "-lower"]
                upper = self.handles["mounted:" + role + "-upper"]
                if _filesystem_magic(lower) != 0xEF53 or _filesystem_magic(upper) != 0xF15F:
                    raise ValueError("retained encrypted view filesystem changed")
                info = os.fstat(upper)
                if (
                    info.st_uid != ROLE_UIDS[role]
                    or info.st_gid != ROLE_UIDS[role]
                    or stat.S_IMODE(info.st_mode) != 0o700
                ):
                    raise ValueError("actual encrypted role root permissions differ")
            self.verify()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _mount_views_child(self) -> bytes:
        _enter_owned_namespace(self.handles["namespace"])
        parent = self.handles["root-parent"]
        options = f"ecryptfs_sig={self._keys.signature},ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_mount_auth_tok_only"
        for role in (
            name.removesuffix("-lower") for name in self.mounts if name.endswith("-lower")
        ):
            name = role + ".img"
            loop = self.handles["loop:" + name]
            raw = bytearray(LOOP_INFO64.size)
            fcntl.ioctl(loop, LOOP_GET_STATUS64, raw, True)
            if bytes(raw) != self._expected_loop(name, os.fstat(self.handles[name])):
                raise ValueError("owned loop changed before mount")
            for suffix in ("-lower", "-upper"):
                target = PurePosixPath(_view_path(self.root, role, suffix)).name
                os.mkdir(target, 0o700, dir_fd=parent)
            lower_path, upper_path = self.mounts[role + "-lower"], self.mounts[role + "-upper"]
            _mount_owned(f"/proc/self/fd/{loop}", lower_path, "ext4", None)
            lower = os.open(lower_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            self._mount_channel.transfer("mounted:" + role + "-lower", lower)
            if role == "native-auth":
                _mount_owned(lower_path, upper_path, "ecryptfs", options, native_auth=True)
            else:
                _mount_owned(lower_path, upper_path, "ecryptfs", options)
            upper = os.open(upper_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            self._mount_channel.transfer("mounted:" + role + "-upper", upper)
            if role == "scratch":
                os.mkdir("checkout", 0o700, dir_fd=upper)
                os.chown("checkout", 65534, 65534, dir_fd=upper, follow_symlinks=False)
            os.fchown(upper, ROLE_UIDS[role], ROLE_UIDS[role])
            os.fchmod(upper, 0o700)
        return b"encrypted-views-mounted"

    def handoff_storage_owner(self) -> LinuxPhysicalOwner:
        """Original live producer to original concrete owner; no reconstruction."""
        if (
            self.failed
            or not hasattr(self, "_mount_channel")
            or self._mount_channel.position != len(self.mounts)
            or set(self.mounts)
            != {
                role + suffix
                for role in (name.removesuffix(".img") for name in self._ext4_metadata)
                for suffix in ("-lower", "-upper")
            }
        ):
            raise ValueError("storage owner handoff requires actual completed view custody")
        self.verify()
        self._keys._verify()
        # Creation keeps its original startup deadline. The concrete owner gets
        # independent bounded readback jobs on the same original observer with
        # the unchanged absolute batch end. Each job is capped at 30 seconds;
        # this neither restarts origin nor consumes an extra resource allowance.
        readback_jobs = BoundedStorageJobs(
            self.reservation.observer,
            self.reservation.observer_group,
            self.reservation.aggregate,
            self.reservation.batch_started + 600,
        )
        self._readback_jobs = readback_jobs
        owner = LinuxPhysicalOwner(
            configuration=self.reservation._configuration,
            namespace_fd=self.handles["namespace"],
            directory_fd=self.handles["directory"],
            loop_fds={name: self.handles["loop:" + name] for name in self._ext4_metadata},
            backing_fds={name: self.handles[name] for name in self._ext4_metadata},
            mounts=self.mounts,
            ring=self._keys.ring,
            jobs=self.jobs,
            batch_started_monotonic=self.reservation.batch_started,
            reservation=self.reservation,
            retention_readback_jobs=readback_jobs,
        )
        owner.verify_retention(self.reservation)
        return owner

    def _expected_loop(self, name: str, backing: os.stat_result) -> bytes:
        return LOOP_INFO64.pack(
            _encode_device(backing.st_dev),
            backing.st_ino,
            0,
            0,
            ALL_BACKING_SIZES[name],
            os.minor(os.fstat(self.handles["loop:" + name]).st_rdev),
            0,
            0,
            0,
            bytes(64),
            bytes(64),
            bytes(32),
            0,
            0,
        )

    def _readback(self) -> bytes:
        """Potentially blocking kernel observations only in the bounded job."""
        result = bytearray()
        for name, size in ALL_BACKING_SIZES.items():
            if name not in self.handles:
                if name in BACKING_SIZES:
                    raise ValueError("original owned backing custody missing")
                continue
            backing = os.fstat(self.handles[name])
            if backing.st_size != size or backing.st_blocks * 512 > size:
                raise ValueError("owned backing exceeds fixed logical/allocated size")
            loop = self.handles["loop:" + name]
            raw = bytearray(LOOP_INFO64.size)
            fcntl.ioctl(loop, LOOP_GET_STATUS64, raw, True)
            if raw != self._expected_loop(name, backing):
                raise ValueError("actual owned loop/backing kernel identity differs")
            result.extend(raw)
        return bytes(result)
