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
import json
import os
from pathlib import PurePosixPath
import platform
import resource
import select
import socket
import stat
import sys
import time
from typing import TYPE_CHECKING, Literal, NoReturn

from crewshal.linux_envelope import (
    DIRECTORY_GROWTH_KIB,
    EXT4_INODE_LIMITS,
    _verify_ext4_growth,
    prepare_linux_envelope,
)
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
PHYSICAL_DOMAIN_BYTES = 1073741824
ROOT_COPY_BYTES = 1073741824 - 3 * ADDITIONAL_BACKING_SIZES["native-auth.img"]
ROLE_UIDS = {
    "scratch": 65534,
    "candidate": 65534,
    "native-auth": 65534,
    "validator-scratch": 65531,
    "validator-candidate": 0,
}

if TYPE_CHECKING:
    from crewshal.durable import InstallationJournalGrowth


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
        try:
            if type(reservation) is OwnedStorageReservation:
                reservation.verify_operational()
            else:
                reservation.verify()
            if (
                type(ring) is not AnonymousKeyring
                or getattr(reservation, "_private_ring", None) is not ring
                or not ring.complete
                or ring.creator != os.getpid()
                or ring.serial <= 0
            ):
                raise ValueError("private keys require original live anonymous credential anchor")
            self._ring_identity = (ring.serial, ring.creator, ring.previous)
            self.master_description = "crewshal-" + os.urandom(16).hex()
            self.signature = os.urandom(8).hex()
            self._descriptions = (self.master_description, self.signature)
        except BaseException as error:
            self.failed = True
            if type(reservation) is OwnedStorageReservation:
                reservation._retain_installation_refusal(error)
            raise

    def _verify(self) -> None:
        if type(self.reservation) is OwnedStorageReservation:
            self.reservation.verify()
        else:
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
            if type(self.reservation) is OwnedStorageReservation:
                self.reservation.verify_operational()
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
        except BaseException as error:
            self.failed = True
            if type(self.reservation) is OwnedStorageReservation:
                self.reservation._retain_installation_refusal(error)
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
        reservation = getattr(production, "reservation", None)
        if type(reservation) is OwnedStorageReservation:
            reservation._retain_installation_refusal(self)


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

    Caller retains a private existing backing directory or its root-owned
    installation parent. The latter permits one bounded directory-preparation
    child after the original charge/timer; it supplies no physical capacity proof.
    Handles, channel and pending job remain strongly owned on every refusal.
    """

    resources_reusable: Literal[False] = False
    operational_ready: Literal[False] = False

    def __init__(
        self,
        reservation: OwnedStorageReservation,
        directory_fd: int | None,
        jobs: BoundedStorageJobs,
        *,
        installation_parent_fd: int | None = None,
    ):
        if hasattr(reservation, "_production"):
            raise ValueError("owned storage production is one-shot; no reconstruction")
        # Retain original inputs even if duplication or admission fails.
        self.reservation, self.jobs = reservation, jobs
        self._owners = (reservation, jobs)
        self.original_directory = directory_fd
        self.original_installation_parent = installation_parent_fd
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
            reservation.verify_operational()
            if getattr(reservation, "capacity_claim", None) is None:
                raise ValueError("production requires its original durable capacity claim")
            if (
                jobs.observer is not reservation.observer
                or jobs.group is not reservation.observer_group
                or jobs.aggregate is not reservation.aggregate
                or jobs.observer.spec.pid != os.getpid()
                or jobs.execution_group is not reservation._batch_timer.setup
                or jobs.batch_timer is not reservation._batch_timer
                or not time.monotonic()
                < jobs.deadline
                <= min(time.monotonic() + 30, reservation.batch_started + 120)
            ):
                raise ValueError("production requires original bounded retained observer/job")
            if (directory_fd is None) == (installation_parent_fd is None):
                raise ValueError("exactly one existing directory or installation parent required")
            if directory_fd is not None:
                self.handles["directory"] = os.dup(directory_fd)
                self.directory_identity = self._directory(self.handles["directory"])
            else:
                assert installation_parent_fd is not None
                self.handles["installation-parent"] = os.dup(installation_parent_fd)
                self._installation_parent_identity = self._installation_parent(
                    self.handles["installation-parent"]
                )
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

    def _installation_parent(self, descriptor: int) -> tuple[int, int]:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != 0
            or info.st_gid != 0
            or stat.S_IMODE(info.st_mode) != 0o700
            or os.readlink(f"/proc/self/fd/{descriptor}") != str(PurePosixPath(self.root).parent)
        ):
            raise ValueError("original root-owned private installation parent required")
        return info.st_dev, info.st_ino

    def prepare_directory(self) -> None:
        """One charged bounded child creates/pins the root and backing directory.

        Actual FD custody precedes each subsequent effect. This is finite
        directory preparation, not installation capacity/growth proof. A
        preexisting path, failed handoff or unknown child consumes the attempt.
        """
        if (
            "installation-parent" not in self.handles
            or "directory" in self.handles
            or hasattr(self, "_directory_channel")
            or self.failed
            or self.attempted
        ):
            raise ValueError("installation directory creation is one-shot; no retry")
        self._directory_channel = _CreationChannel(self)
        try:
            self.verify()
            self._directory_channel.open()
            self._directory_channel.expected = ["installation-root", "directory"]
            assert self._directory_channel.child is not None
            reply = self.jobs.run(
                self._prepare_directory_child,
                {self.handles["installation-parent"], self._directory_channel.child.fileno()},
                transfer=self._directory_channel,
            )
            self.verify()
            if reply != b"directory-prepared" or self._directory_channel.position != 2:
                raise ValueError("actual installation directory custody incomplete")
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _prepare_directory_child(self) -> bytes:
        parent = self.handles["installation-parent"]
        self._installation_parent(parent)
        leaf = PurePosixPath(self.root).name
        os.mkdir(leaf, 0o700, dir_fd=parent)
        root = os.open(
            leaf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent
        )
        self._directory_channel.transfer("installation-root", root)
        os.mkdir("backing", 0o700, dir_fd=root)
        directory = os.open(
            "backing", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
        )
        self._directory_channel.transfer("directory", directory)
        return b"directory-prepared"

    def install_physical_domain(self, inventory: TrustedParentInventory, formatter_fd: int) -> None:
        """Prepare one fixed ext4 domain through original charged jobs and custody.

        The bootstrap formatter is an explicit retained inventory input. This
        source is not an operational approval or loader qualification. Unknown
        creation, formatting or mount results keep every handle and charge.
        """
        if (
            hasattr(self, "_domain_channel")
            or self.failed
            or self.attempted
            or "installation-root" not in self.handles
            or "namespace" in self.handles
        ):
            raise ValueError("physical domain requires original directory custody; no retry")
        self._domain_channel = _CreationChannel(self)
        try:
            self.verify()
            manifest = audit_parent_inventory(inventory)
            bindings = self.reservation._configuration.linux_envelope
            if bindings is None or bindings.parent_inventory_sha256 != record_digest(manifest):
                raise ValueError("physical domain requires original exact bootstrap inventory")
            entry = manifest.root.get("/usr/sbin/mkfs.ext4")
            if entry is None or entry.kind != "file" or not entry.mode & 0o111:
                raise ValueError("physical domain requires bound formatter input")
            self.handles["domain-formatter"] = os.dup(formatter_fd)
            descriptor = self.handles["domain-formatter"]
            before = os.fstat(descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_uid != 0
                or before.st_gid != 0
                or before.st_mode & 0o7022
                or before.st_size > 134217728
                or fcntl.fcntl(descriptor, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
                or os.pread(descriptor, 4, 0) != b"\x7fELF"
            ):
                raise ValueError("actual retained bootstrap formatter identity differs")
            sha = hashlib.sha256()
            offset = 0
            while offset < before.st_size:
                chunk = os.pread(descriptor, min(65536, before.st_size - offset), offset)
                if not chunk:
                    raise ValueError("bootstrap formatter input truncated")
                sha.update(chunk)
                offset += len(chunk)
            if sha.hexdigest() != entry.sha256 or _metadata(before) != _metadata(
                os.fstat(descriptor)
            ):
                raise ValueError("bootstrap formatter input changed")
            self._domain_formatter_metadata = _metadata(before)
            observer = self.reservation.observer
            if observer.spec.placement != "outer_observer" or observer.spec.pid != os.getpid():
                raise ValueError("physical domain requires original outer retaining observer")
            # Lower the original observer's limits only after the complete
            # charge. Never raise an existing hard limit or renew its lifetime.
            from crewshal.durable import LiveStorageInstallationClaim

            claim = self.reservation.capacity_claim
            if type(claim) is not LiveStorageInstallationClaim:
                raise ValueError("physical domain requires original upfront installation charge")
            _, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            if hard != resource.RLIM_INFINITY and hard < PHYSICAL_DOMAIN_BYTES:
                raise ValueError("original observer hard file limit cannot fit fixed domain")
            resource.setrlimit(
                resource.RLIMIT_FSIZE, (PHYSICAL_DOMAIN_BYTES, PHYSICAL_DOMAIN_BYTES)
            )
            self.journal_growth = claim._store.bind_installation_journal(self.reservation)
            self._domain_channel.open()
            self._domain_channel.expected = [
                "namespace",
                "loop-control",
                "physical-domain.img",
                "loop:physical-domain.img",
            ]
            assert self._domain_channel.child is not None
            reply = self.jobs.run(
                self._domain_objects_child,
                {self.handles["installation-parent"], self._domain_channel.child.fileno()},
                transfer=self._domain_channel,
            )
            if reply != b"domain-objects-created" or self._domain_channel.position != 4:
                raise ValueError("actual physical-domain object custody incomplete")
            self._format_name = "physical-domain.img"
            self.handles["formatter"] = descriptor
            self.jobs.run(
                self._format_child,
                {
                    descriptor,
                    self.handles["physical-domain.img"],
                    self.handles["loop:physical-domain.img"],
                },
                _format_output=True,
            )
            _verify_ext4_growth(
                os.pread(self.handles["physical-domain.img"], 1024, 1024),
                "physical-domain.img",
                PHYSICAL_DOMAIN_BYTES,
            )
            self.jobs.run(
                self._domain_loop_child,
                {self.handles["physical-domain.img"], self.handles["loop:physical-domain.img"]},
            )
            self._domain_mount_channel = _CreationChannel(self)
            self._domain_mount_channel.open()
            self._domain_mount_channel.expected = [
                "physical-domain-root",
                "physical-domain-directory",
            ]
            assert self._domain_mount_channel.child is not None
            reply = self.jobs.run(
                self._domain_mount_child,
                {
                    self.handles["namespace"],
                    self.handles["installation-root"],
                    self.handles["physical-domain.img"],
                    self.handles["loop:physical-domain.img"],
                    self._domain_mount_channel.child.fileno(),
                },
                transfer=self._domain_mount_channel,
            )
            if reply != b"physical-domain-mounted" or self._domain_mount_channel.position != 2:
                raise ValueError("actual physical-domain mount custody incomplete")
            self.handles["unmounted-directory"] = self.handles["directory"]
            self.handles["directory"] = self.handles["physical-domain-directory"]
            self.directory_identity = self._directory(self.handles["directory"])
            self._domain_complete = True
            self._domain_readback = self.jobs.run(
                self._domain_readback_child,
                {
                    self.handles["namespace"],
                    self.handles["physical-domain.img"],
                    self.handles["loop:physical-domain.img"],
                    self.handles["physical-domain-root"],
                },
            )
            self.verify()
        except BaseException as error:
            self.failed = True
            raise ProductionRefusal(str(error), self) from error

    def _domain_objects_child(self) -> bytes:
        _unshare_mount_namespace()
        namespace = os.open("/proc/self/ns/mnt", os.O_RDONLY | os.O_CLOEXEC)
        self._domain_channel.transfer("namespace", namespace)
        _namespace_is_private()
        control = os.open("/dev/loop-control", os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
        self._domain_channel.transfer("loop-control", control)
        name = PurePosixPath(self.root).name + ".capacity.img"
        backing = os.open(
            name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
            dir_fd=self.handles["installation-parent"],
        )
        self._domain_channel.transfer("physical-domain.img", backing)
        os.ftruncate(backing, PHYSICAL_DOMAIN_BYTES)
        self._attach_created_loop(
            "physical-domain.img", PHYSICAL_DOMAIN_BYTES, backing, self._domain_channel, control
        )
        return b"domain-objects-created"

    def _domain_mount_child(self) -> bytes:
        _enter_owned_namespace(self.handles["namespace"])
        self._domain_loop_child()
        before = os.stat(self.root, follow_symlinks=False)
        original = os.fstat(self.handles["installation-root"])
        if (before.st_dev, before.st_ino) != (original.st_dev, original.st_ino):
            raise ValueError("original physical-domain mountpoint identity changed")
        loop = self.handles["loop:physical-domain.img"]
        _mount_owned(
            f"/proc/self/fd/{loop}", self.root, "ext4", "max_dir_size_kb=64", native_auth=True
        )
        root = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        self._domain_mount_channel.transfer("physical-domain-root", root)
        os.fchmod(root, 0o700)
        os.mkdir("backing", 0o700, dir_fd=root)
        directory = os.open(
            "backing", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root
        )
        self._domain_mount_channel.transfer("physical-domain-directory", directory)
        return b"physical-domain-mounted"

    def _domain_loop_child(self) -> bytes:
        backing = os.fstat(self.handles["physical-domain.img"])
        if (
            backing.st_size != PHYSICAL_DOMAIN_BYTES
            or backing.st_blocks * 512 > PHYSICAL_DOMAIN_BYTES
        ):
            raise ValueError("actual original physical-domain backing exceeds fixed bound")
        raw = bytearray(LOOP_INFO64.size)
        fcntl.ioctl(self.handles["loop:physical-domain.img"], LOOP_GET_STATUS64, raw, True)
        if bytes(raw) != self._expected_loop("physical-domain.img", backing):
            raise ValueError("actual original physical-domain loop binding differs")
        return bytes(raw)

    def _domain_readback_child(self) -> bytes:
        """Bounded positive mount/geometry/loop readback; no free-space oracle."""
        _enter_owned_namespace(self.handles["namespace"])
        result = self._domain_loop_child()
        _verify_ext4_growth(
            os.pread(self.handles["physical-domain.img"], 1024, 1024),
            "physical-domain.img",
            PHYSICAL_DOMAIN_BYTES,
        )
        root = self.handles["physical-domain-root"]
        info = os.fstat(root)
        geometry = os.fstatvfs(root)
        if (
            _filesystem_magic(root) != 0xEF53
            or info.st_dev != os.fstat(self.handles["loop:physical-domain.img"]).st_rdev
            or info.st_uid != 0
            or info.st_gid != 0
            or stat.S_IMODE(info.st_mode) != 0o700
            or geometry.f_bsize != 4096
            or geometry.f_frsize != 4096
            or not 0 < geometry.f_blocks * geometry.f_frsize <= PHYSICAL_DOMAIN_BYTES
            or not 11 <= geometry.f_files <= EXT4_INODE_LIMITS["physical-domain.img"]
        ):
            raise ValueError("actual retained physical-domain filesystem geometry differs")
        from crewshal.admission import _fields, _read
        from crewshal.linux_parent import _proc_root

        proc = _proc_root(self.reservation.observer.spec.boot_id)
        try:
            mount = _fields(_read(proc, f"{os.getpid()}/fdinfo/{root}")).get("mnt_id")
            rows = []
            for line in _read(proc, f"{os.getpid()}/mountinfo").decode("ascii").splitlines():
                before, separator, after = line.partition(" - ")
                fields = before.split()
                if fields and fields[0] == mount:
                    rows.append((fields, separator, after.split()))
            if len(rows) != 1:
                raise ValueError("actual retained physical-domain mount identity unavailable")
            fields, separator, super_fields = rows[0]
            if (
                len(fields) < 6
                or not separator
                or len(super_fields) != 3
                or fields[2] != f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}"
                or fields[3:5] != ["/", self.root]
                or super_fields[0] != "ext4"
                or super_fields[2].split(",").count("max_dir_size_kb=64") != 1
                or not {"rw", "nosuid", "nodev"} <= set(fields[5].split(","))
            ):
                raise ValueError("actual retained physical-domain mount growth controls differ")
        finally:
            os.close(proc)
        return result

    def verify(self) -> None:
        if self.jobs.pending is None:
            self.reservation.verify()
        else:
            self.reservation.verify_creation_job(self.jobs)
        self.reservation.verify_operational()
        if (
            "installation-parent" in self.handles
            and self._installation_parent(self.handles["installation-parent"])
            != self._installation_parent_identity
        ):
            raise ValueError("original installation parent identity differs")
        if "installation-root" in self.handles:
            root = os.fstat(self.handles["installation-root"])
            if (root.st_dev, root.st_ino) != self._installation_root_identity:
                raise ValueError("original installation root handle changed")
        if "directory" in self.handles:
            if self._directory(self.handles["directory"]) != self.directory_identity:
                raise ValueError("original backing directory identity differs")
        elif "installation-parent" not in self.handles:
            raise ValueError("original backing directory or installation parent missing")
        if (
            self.reservation is not self._owners[0]
            or self.jobs is not self._owners[1]
            or getattr(self.reservation, "_production", None) is not self
            or self.jobs.observer is not self.reservation.observer
            or self.jobs.group is not self.reservation.observer_group
            or self.jobs.aggregate is not self.reservation.aggregate
            or self.jobs.observer.spec.pid != os.getpid()
            or self.jobs.execution_group is not self.reservation._batch_timer.setup
            or self.jobs.batch_timer is not self.reservation._batch_timer
            or self.deadline != self._deadline
            or self.jobs.deadline != self._deadline
            or not time.monotonic() < self._deadline
        ):
            raise ValueError("original retained production identity/deadline differs")

    def _verify_transferred(self, name: str, descriptor: int) -> None:
        info = os.fstat(descriptor)
        if not fcntl.fcntl(descriptor, fcntl.F_GETFD) & fcntl.FD_CLOEXEC:
            raise ValueError("received descriptor must be close-on-exec")
        if name == "installation-root":
            parent_info = os.fstat(self.handles["installation-parent"])
            linked = os.stat(
                PurePosixPath(self.root).name,
                dir_fd=self.handles["installation-parent"],
                follow_symlinks=False,
            )
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o700
                or os.readlink(f"/proc/self/fd/{descriptor}") != self.root
                or info.st_dev != parent_info.st_dev
                or (info.st_dev, info.st_ino) != (linked.st_dev, linked.st_ino)
                or (info.st_dev, info.st_ino) == (parent_info.st_dev, parent_info.st_ino)
            ):
                raise ValueError("actual newly created installation root differs")
            self._installation_root_identity = (info.st_dev, info.st_ino)
        elif name == "directory":
            self.directory_identity = self._directory(descriptor)
            root = os.fstat(self.handles["installation-root"])
            linked = os.stat(
                "backing", dir_fd=self.handles["installation-root"], follow_symlinks=False
            )
            if (
                info.st_dev != root.st_dev
                or info.st_gid != 0
                or (info.st_dev, info.st_ino) != (linked.st_dev, linked.st_ino)
                or (info.st_dev, info.st_ino) == (root.st_dev, root.st_ino)
            ):
                raise ValueError("actual newly created backing directory differs")
        elif name == "namespace":
            path = os.readlink(f"/proc/self/fd/{descriptor}")
            if not stat.S_ISREG(info.st_mode) or not path.startswith("mnt:["):
                raise ValueError("received mount namespace FD differs")
            original = os.stat("/proc/self/ns/mnt")
            if (info.st_dev, info.st_ino) == (original.st_dev, original.st_ino):
                raise ValueError("new namespace must differ from observer namespace")
        elif name == "loop-control":
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(10, 237):
                raise ValueError("received Linux loop-control device differs")
        elif name == "physical-domain.img":
            parent = self.handles["installation-parent"]
            linked = os.stat(
                PurePosixPath(self.root).name + ".capacity.img",
                dir_fd=parent,
                follow_symlinks=False,
            )
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_nlink != 1
                or info.st_size != 0
                or (info.st_dev, info.st_ino) != (linked.st_dev, linked.st_ino)
            ):
                raise ValueError("actual new physical-domain backing custody differs")
        elif name in ("physical-domain-root", "physical-domain-directory"):
            loop = os.fstat(self.handles["loop:physical-domain.img"])
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or info.st_dev != loop.st_rdev
                or _filesystem_magic(descriptor) != 0xEF53
                or os.readlink(f"/proc/self/fd/{descriptor}")
                != self.root + ("/backing" if name.endswith("directory") else "")
            ):
                raise ValueError("actual new physical-domain mount custody differs")
            if name == "physical-domain-root":
                self._domain_root_identity = (info.st_dev, info.st_ino)
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
            self.channel.expected = (
                [] if getattr(self, "_domain_complete", False) else ["namespace", "loop-control"]
            )
            for name in BACKING_SIZES:
                self.channel.expected.extend([name, "loop:" + name])
            reply = self.jobs.run(
                self._create_child,
                {
                    self.handles["directory"],
                    self.channel.child.fileno(),
                    *(
                        self.handles[name]
                        for name in ("namespace", "loop-control")
                        if name in self.handles
                    ),
                },
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
        if getattr(self, "_domain_complete", False):
            _enter_owned_namespace(self.handles["namespace"])
            control = self.handles["loop-control"]
        else:
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
            self._attach_created_loop(name, size, backing, channel, control)

    def _attach_created_loop(
        self, name: str, size: int, backing: int, channel: _CreationChannel, control: int
    ) -> None:
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
            if getattr(self, "_domain_complete", False):
                self._verify_formatter_custody()
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

    def _verify_formatter_custody(self) -> None:
        original = self.handles["domain-formatter"]
        source = self._root_inputs["/usr/sbin/mkfs.ext4"]
        if (
            _metadata(os.fstat(original)) != self._domain_formatter_metadata
            or _metadata(os.fstat(source)) != self._domain_formatter_metadata
            or fcntl.fcntl(original, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
            or fcntl.fcntl(source, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
        ):
            raise ValueError("bootstrap formatter is not its original charged readonly source")

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
                _verify_ext4_growth(block, name, sizes[name])
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
            [
                "/usr/sbin/mkfs.ext4",
                "-q",
                "-F",
                "-m",
                "0",
                "-b",
                "4096",
                "-N",
                str(EXT4_INODE_LIMITS[name]),
                "/proc/self/fd/3",
            ],
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
            _mount_owned(
                f"/proc/self/fd/{loop}",
                lower_path,
                "ext4",
                f"max_dir_size_kb={DIRECTORY_GROWTH_KIB}",
            )
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
            execution_group=self.jobs.execution_group,
            batch_timer=self.jobs.batch_timer,
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

    def complete_installation(self) -> "EffectiveInstallation":
        """Consume preparation through actual original-object readback only.

        This does not qualify the changed helper, roles or runtime. No caller
        receipt or imported observed row can reconstruct this live producer.
        """
        if hasattr(self.reservation, "_installation"):
            raise ValueError("original installation proof consumed; no retry")
        proof = object.__new__(EffectiveInstallation)
        proof.production, proof.reservation = self, self.reservation
        proof.failed = False
        self.reservation._installation = proof
        try:
            from crewshal.durable import LiveStorageInstallationClaim

            self.verify()
            if (
                type(self.reservation.capacity_claim) is not LiveStorageInstallationClaim
                or self.reservation._batch_timer.validator is None
                or self.reservation._configuration.proxy_argv is not None
                or not getattr(self, "_domain_complete", False)
                or not getattr(self, "_auxiliary_complete", False)
                or not hasattr(self, "projected_inventory")
                or self._mount_channel.position != 10
                or set(self._ext4_metadata) != set(ALL_BACKING_SIZES)
                or type(self.reservation._storage_owner) is not LinuxPhysicalOwner
            ):
                raise ValueError("actual complete original installation custody unavailable")
            proof.physical = self.reservation._storage_owner
            proof.growth = self.journal_growth
            proof._owners = (self, self.reservation, proof.physical, proof.growth)
            proof._handles = dict(self.handles)
            proof._identities = {
                name: (os.fstat(fd).st_dev, os.fstat(fd).st_ino, os.fstat(fd).st_rdev)
                for name, fd in proof._handles.items()
            }
            proof._inputs = dict(self._root_inputs)
            proof._input_metadata = {
                name: _metadata(os.fstat(fd)) for name, fd in proof._inputs.items()
            }
            proof.jobs = BoundedStorageJobs(
                self.reservation.observer,
                self.reservation.observer_group,
                self.reservation.aggregate,
                self.reservation.batch_started + 570,
                execution_group=self.jobs.execution_group,
                batch_timer=self.jobs.batch_timer,
            )
            proof._jobs = proof.jobs
            proof._readback_jobs = proof.physical.retention_readback_jobs
            if proof._readback_jobs is None:
                raise ValueError("original bounded storage readback jobs unavailable")
            # This smaller inherited limit covers all later original setup,
            # namespace-parent, native and validator jobs. Never raise a limit.
            proof.growth.verify()
            connection = proof.growth.connection
            if (
                connection.in_transaction
                or connection.execute("PRAGMA page_count").fetchone()[0] * proof.growth.page_size
                > 131072
            ):
                raise ValueError("original journal cannot fit fixed payload growth bound")
            connection.execute(f"PRAGMA max_page_count={131072 // proof.growth.page_size}")
            _, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            if hard != PHYSICAL_DOMAIN_BYTES:
                raise ValueError("original observer preparation hard limit differs")
            resource.setrlimit(resource.RLIMIT_FSIZE, (131072, 131072))
            proof.growth.payload_bound = True
            proof.growth.verify()
            proof.verify()
            self.reservation.capacity_claim._store._retain_observed_installation(proof)
            self.reservation.verify_installation()
            return proof
        except BaseException as error:
            proof.failed = True
            self.failed = True
            self.reservation._retain_installation_refusal(error)
            raise ProductionRefusal(str(error), self) from error

    def _expected_loop(self, name: str, backing: os.stat_result) -> bytes:
        return LOOP_INFO64.pack(
            _encode_device(backing.st_dev),
            backing.st_ino,
            0,
            0,
            PHYSICAL_DOMAIN_BYTES if name == "physical-domain.img" else ALL_BACKING_SIZES[name],
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
            if name in getattr(self, "_ext4_metadata", {}):
                _verify_ext4_growth(os.pread(self.handles[name], 1024, 1024), name, size)
            loop = self.handles["loop:" + name]
            raw = bytearray(LOOP_INFO64.size)
            fcntl.ioctl(loop, LOOP_GET_STATUS64, raw, True)
            if raw != self._expected_loop(name, backing):
                raise ValueError("actual owned loop/backing kernel identity differs")
            result.extend(raw)
        return bytes(result)


class EffectiveInstallation:
    """Original physical/journal/root custody with repeated actual readback.

    Numerical bounds are conservative over retained representations, never free
    space or a release oracle. Payload admission still has separate installed
    identity, kernel-filter, role/network, stopped-native and qualification gates.
    """

    production: OwnedBackingProduction
    reservation: OwnedStorageReservation
    physical: LinuxPhysicalOwner
    jobs: BoundedStorageJobs
    failed: bool
    growth: "InstallationJournalGrowth"
    _owners: tuple[
        OwnedBackingProduction,
        OwnedStorageReservation,
        LinuxPhysicalOwner,
        "InstallationJournalGrowth",
    ]
    _handles: dict[str, int]
    _identities: dict[str, tuple[int, int, int]]
    _inputs: dict[str, int]
    _input_metadata: dict[str, tuple[int, ...]]
    _jobs: BoundedStorageJobs
    _readback_jobs: BoundedStorageJobs | None

    def __init__(self) -> None:
        raise ValueError("installation proof requires original producer readback")

    def __reduce__(self) -> NoReturn:
        raise TypeError("actual installation custody cannot be copied or exported")

    def require_effective_payload_growth(self) -> NoReturn:
        """Keep admission closed at the observed stock-runtime incompatibility.

        Retained volume/journal arithmetic is necessary but cannot establish a
        bound for anonymous shmem and additional payload namespace filesystems.
        The current shared-mmap denial also denies the pinned app-server's WAL
        index. No compatible independently retained enforcement is implemented.
        This refusal must be replaced by actual compatible readback, never a
        caller flag, parsed policy, successful command or imported journal row.
        """
        self.verify()
        error = ValueError(
            "effective payload storage admission closed: MAP_SHARED denial conflicts "
            "with stock app-server SQLite WAL; compatible shmem/namespace growth "
            "enforcement unavailable"
        )
        self.failed = True
        self.production.failed = True
        self.reservation._retain_installation_refusal(error)
        raise error

    def verify_custody(self) -> None:
        try:
            self._verify_custody()
        except BaseException as error:
            self.failed = True
            self.production.failed = True
            self.reservation._retain_installation_refusal(error)
            raise

    def _verify_custody(self) -> None:
        from crewshal.durable import LiveStorageInstallationClaim
        from crewshal.admission import _current_source

        owner, reservation = self.production, self.reservation
        if (
            self.failed
            or owner.failed
            or type(owner) is not OwnedBackingProduction
            or type(reservation) is not OwnedStorageReservation
            or type(self.physical) is not LinuxPhysicalOwner
            or getattr(reservation, "_installation", None) is not self
            or getattr(reservation, "_production", None) is not owner
            or reservation._storage_owner is not self.physical
            or owner.reservation is not reservation
            or self._owners != (owner, reservation, self.physical, self.growth)
            or owner.journal_growth is not self.growth
            or owner.handles != self._handles
            or owner._root_inputs != self._inputs
            or self.jobs is not self._jobs
            or self.jobs.failed
            or self.jobs.pending is not None
            or owner.jobs.failed
            or owner.jobs.pending is not None
            or self.jobs.observer is not reservation.observer
            or self.jobs.group is not reservation.observer_group
            or self.jobs.aggregate is not reservation.aggregate
            or self.jobs.batch_timer is not reservation._batch_timer
            or self.jobs.execution_group is not reservation._batch_timer.setup
            or self.jobs.deadline != reservation.batch_started + 570
            or self.physical.retention_readback_jobs is not self._readback_jobs
            or type(reservation.capacity_claim) is not LiveStorageInstallationClaim
            or not self.growth.payload_bound
        ):
            raise ValueError("original actual installation custody differs")
        _current_source(reservation._configuration)
        reservation._batch_timer.verify()
        self.growth.verify()
        owner._verify_formatter_custody()
        for name, fd in self._handles.items():
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino, info.st_rdev) != self._identities[name]:
                raise ValueError("actual original installation descriptor replaced")
        source_bytes = 0
        for name, fd in self._inputs.items():
            info = os.fstat(fd)
            if (
                _metadata(info) != self._input_metadata[name]
                or not stat.S_ISREG(info.st_mode)
                or info.st_uid != 0
                or info.st_gid != 0
                or info.st_mode & 0o7022
                or fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
            ):
                raise ValueError("actual retained installation source identity changed")
            source_bytes += max(info.st_size, info.st_blocks * 512)
        if source_bytes > ROOT_COPY_BYTES:
            raise ValueError("actual original source exceeds prepared growth bound")

    def verify_registered_job(self, jobs: BoundedStorageJobs) -> None:
        from crewshal.linux_freeze import OriginalVolumeFreeze

        frozen = getattr(self, "_freeze", None)
        if type(frozen) is OriginalVolumeFreeze and jobs is frozen.jobs:
            frozen.verify_registered_job(jobs)
            return
        if jobs is not self._jobs and jobs is not self._readback_jobs:
            raise ValueError("installed work requires original bounded readback job")
        self.verify_custody()

    def verify_registered_action(self, jobs: BoundedStorageJobs, action: object) -> None:
        from crewshal.linux_freeze import OriginalVolumeFreeze

        frozen = getattr(self, "_freeze", None)
        if type(frozen) is OriginalVolumeFreeze and jobs is frozen.jobs:
            frozen.verify_registered_action(jobs, action)
            return
        # No caller flag can turn an arbitrary action into post-installation
        # preparation. The only retained jobs are effect-free exact source methods.
        allowed = (
            (self._jobs, self, EffectiveInstallation._readback_child),
            (self._readback_jobs, self.physical, LinuxPhysicalOwner._readback_bytes),
        )
        if not any(
            jobs is job
            and getattr(action, "__self__", None) is owner
            and getattr(action, "__func__", None) is method
            for job, owner, method in allowed
        ):
            raise ValueError("installed action is not original fixed readback")
        self.verify_registered_job(jobs)

    def _readback_child(self) -> bytes:
        owner = self.production
        # All potentially blocking filesystem/kernel observations stay in the
        # admitted original setup role, within 30 seconds and the original cutoff.
        domain = owner._domain_readback_child()
        backings = owner._readback()
        projection = owner.handles["readonly-projection"]
        geometry = os.fstatvfs(projection)
        if not geometry.f_flag & os.ST_RDONLY:
            raise ValueError("actual original root projection is writable")
        owner.projected_inventory.verify()
        physical = self.physical._readback()
        if (
            self.physical.initial is None
            or physical.namespace != self.physical.initial.namespace
            or physical.keyring_state != "present"
            or set(physical.backing) != set(ALL_BACKING_SIZES)
            or set(physical.loops) != set(ALL_BACKING_SIZES)
            or set(physical.mounts) != set(owner.mounts)
        ):
            raise ValueError("actual complete installation kernel readback differs")
        role_geometry = {}
        for role, uid in ROLE_UIDS.items():
            lower = owner.handles["mounted:" + role + "-lower"]
            upper = owner.handles["mounted:" + role + "-upper"]
            info = os.fstat(upper)
            actual = os.fstatvfs(lower)
            size = ALL_BACKING_SIZES[role + ".img"]
            if (
                _filesystem_magic(lower) != 0xEF53
                or _filesystem_magic(upper) != 0xF15F
                or info.st_uid != uid
                or info.st_gid != uid
                or stat.S_IMODE(info.st_mode) != 0o700
                or actual.f_bsize != 4096
                or actual.f_frsize != 4096
                or not 0 < actual.f_blocks * 4096 <= size
                or not 11 <= actual.f_files <= EXT4_INODE_LIMITS[role + ".img"]
                or actual.f_files * (131072 + 65536) > size
            ):
                raise ValueError("actual role filesystem growth bound differs")
            role_geometry[role] = [actual.f_blocks, actual.f_files, actual.f_frsize]
        # Full original prepared allowance includes root plus three auth views.
        # Pool cardinality covers hidden/deleted-open small files and directory
        # metadata; large original root/backing exceptions are charged separately.
        # Charge source, readonly alias, every role representation and sealed
        # control bytes conservatively, even when physical blocks are shared.
        bound = (
            1073741824
            + 2 * ROOT_COPY_BYTES
            + PHYSICAL_DOMAIN_BYTES
            + EXT4_INODE_LIMITS["physical-domain.img"] * (131072 + 65536)
            + 3 * sum(ALL_BACKING_SIZES.values())
            + 16777216
            + 1073741824
            + 16777216
            + 128 * 262144
        )
        if bound > 8589934592:
            raise ValueError("complete retained growth exceeds original disk ceiling")
        return json.dumps(
            {
                "domain_loop": domain.hex(),
                "role_loops": backings.hex(),
                "physical": physical.model_dump(),
                "role_geometry": role_geometry,
                "root_flags": geometry.f_flag,
                "logical_bound": bound,
                "allocated_bound": bound,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    def verify(self) -> None:
        try:
            self._verify()
        except BaseException as error:
            self.failed = True
            self.production.failed = True
            self.reservation._retain_installation_refusal(error)
            raise

    def _verify(self) -> None:
        self.verify_custody()
        self.reservation.verify()
        keep = {
            *self._handles.values(),
            *self._inputs.values(),
            *self.physical.handles.values(),
            *self.physical._backing_handles.values(),
            self.production.projected_inventory.descriptor,
        }
        raw = self.jobs.run(self._readback_child, keep)
        self.verify_custody()
        actual = json.loads(raw)
        if (
            actual["domain_loop"] != self.production._domain_readback.hex()
            or actual["role_loops"]
            != b"".join(
                self.production._expected_loop(name, os.fstat(self._handles[name]))
                for name in ALL_BACKING_SIZES
            ).hex()
            or actual["logical_bound"] > 8589934592
            or actual["allocated_bound"] > 8589934592
        ):
            raise ValueError("independent actual installation readback changed")
        self.readback = raw
