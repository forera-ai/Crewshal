"""Create compiler storage under the original charge and early batch timer."""

import ctypes
import fcntl
import os
from pathlib import PurePosixPath
import stat
import struct
import time
from typing import NoReturn, TYPE_CHECKING, cast
from weakref import WeakKeyDictionary

from pydantic import ValidationInfo, field_validator

from crewshal.contracts import Digest
from crewshal.linux_production import (
    _CreationChannel,
    OwnedBackingProduction,
    LOOP_CTL_GET_FREE,
    LOOP_SET_FD,
    LOOP_SET_STATUS64,
    _encode_device,
)
from crewshal.linux_storage import BoundedStorageJobs, LOOP_INFO64
from crewshal.model import Contract

if TYPE_CHECKING:
    from crewshal.linux_operational import OriginalInstallationDriver, FrozenHelperBuild
    from crewshal.supervisor import OwnedCgroup
    from crewshal.linux_setup import OwnedBatchTimer, OwnedStorageReservation

_VOLUMES: WeakKeyDictionary["OriginalInstallationDriver", "OriginalCompilerVolume"] = (
    WeakKeyDictionary()
)
FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


class FrozenCompilerVolumeRecipe(Contract):
    """The immutable recipe precedes the creation of fresh kernel inodes."""

    formatter: str
    formatter_sha256: Digest
    loop_allocator: str = "/dev/loop-control"
    bytes: int = 16777216
    maximum_inodes: int = 128

    @field_validator("formatter", "loop_allocator")
    @classmethod
    def path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if not path.is_absolute() or str(path) != value or ".." in path.parts:
            raise ValueError("canonical compiler constructor input required")
        return value

    @field_validator("bytes", "maximum_inodes", "loop_allocator")
    @classmethod
    def fixed(cls, value: object, info: ValidationInfo) -> object:
        expected = {"bytes": 16777216, "maximum_inodes": 128, "loop_allocator": "/dev/loop-control"}
        if value != expected[str(info.field_name)]:
            raise ValueError("original compiler storage constructor limit changed")
        return value


class OriginalCompilerVolume:
    """Every received handle remains retained after failure or unknown results."""

    driver: "OriginalInstallationDriver"
    build: "FrozenHelperBuild"
    setup: "OwnedCgroup"
    reservation: "OwnedStorageReservation"
    timer: "OwnedBatchTimer"
    _owners: tuple[object, ...]
    _origin: float
    _recipe: str
    failed: bool
    complete: bool
    attempted: bool
    deadline: float
    jobs: BoundedStorageJobs
    channel: _CreationChannel
    container: str

    def __reduce__(self) -> NoReturn:
        raise TypeError("original compiler volume cannot be copied or exported")

    def __init__(
        self, driver: "OriginalInstallationDriver", build: "FrozenHelperBuild", setup: "OwnedCgroup"
    ) -> None:
        from crewshal.linux_operational import _open_path, _hash_file

        assert driver.observer is not None

        if (
            driver in _VOLUMES
            or driver.reservation is None
            or driver.timer is None
            or build.volume_constructor is None
        ):
            raise ValueError("original charged compiler volume constructor unavailable or consumed")
        self.driver, self.build, self.setup = driver, build, setup
        self.reservation, self.timer = driver.reservation, driver.timer
        self._owners = driver, self.reservation, self.timer, setup
        self._origin, self._recipe = driver.origin, build.model_dump_json()
        self.failed = False
        self.complete = False
        self.attempted = False
        self.handles: dict[str, int] = {}
        self.received: list[int] = []
        self._identities: dict[str, tuple[int, int, int]] = {}
        self.deadline = min(driver.origin + 120, driver.origin + 570)
        self.jobs = BoundedStorageJobs(
            driver.observer,
            self.reservation.observer_group,
            self.reservation.aggregate,
            self.deadline,
            execution_group=setup,
            batch_timer=self.timer,
        )
        self.channel = _CreationChannel(cast(OwnedBackingProduction, self))
        _VOLUMES[driver] = self
        driver.compiler_volume = self
        self.reservation.verify()
        self.timer.verify()
        volume, backing = PurePosixPath(build.volume), PurePosixPath(build.backing)
        if (
            volume.parent != backing.parent
            or volume.parent.parent != PurePosixPath("/run")
            or volume.name != "volume"
            or backing.name != "compiler.img"
        ):
            raise ValueError("compiler volume requires its exact new private /run container")
        self.container = str(volume.parent)
        self.handles["parent"] = _open_path("/run", directory=True)
        self.handles["formatter"] = _open_path(build.volume_constructor.formatter)
        _hash_file(
            self.handles["formatter"], build.volume_constructor.formatter_sha256, self.deadline
        )
        if not os.fstatvfs(self.handles["formatter"]).f_flag & os.ST_RDONLY:
            raise ValueError("original formatter runtime remains writable")
        self._identities = {name: self._identity(fd) for name, fd in self.handles.items()}

    @staticmethod
    def _identity(fd: int) -> tuple[int, int, int]:
        info = os.fstat(fd)
        return info.st_dev, info.st_ino, info.st_rdev

    def verify(self) -> None:
        if (
            self.failed
            or _VOLUMES.get(self.driver) is not self
            or getattr(self.driver, "compiler_volume", None) is not self
            or self._owners != (self.driver, self.reservation, self.timer, self.setup)
            or self.driver.origin != self._origin
            or self.build.model_dump_json() != self._recipe
        ):
            raise ValueError("original compiler volume custody changed")
        self.reservation.capacity_claim.verify_reservation(self.reservation)
        if time.monotonic_ns() >= self.timer.end_ns:
            self.timer.verify_idle_retention()
        else:
            self.timer.verify()
        for name, identity in self._identities.items():
            if self._identity(self.handles[name]) != identity:
                raise ValueError("original compiler creation handle changed")
        if self.complete:
            self.verify_formatter_directory()
            self._verify_attached_loop()
            backing, loop, volume = (
                os.fstat(self.handles[name]) for name in ("backing", "loop", "volume")
            )
            if (
                backing.st_size != 16777216
                or backing.st_nlink != 1
                or volume.st_dev != loop.st_rdev
            ):
                raise ValueError("original compiler storage bound or mount differs")
            raw = os.pread(self.handles["loop"], 1024, 1024)
            if (
                len(raw) != 1024
                or struct.unpack_from("<H", raw, 56)[0] != 0xEF53
                or not 0 < struct.unpack_from("<I", raw)[0] <= 128
            ):
                raise ValueError("actual compiler ext4 inode geometry differs")
            vfs = os.fstatvfs(self.handles["volume"])
            if vfs.f_files > 128 or vfs.f_blocks * vfs.f_frsize > 16777216:
                raise ValueError("actual compiler filesystem allocation ceiling differs")

    def verify_formatter_directory(self) -> None:
        """Keep the original empty directory linked without releasing its handle."""
        fd = self.handles["lost+found"]
        original = os.fstat(fd)
        linked = os.stat("lost+found", dir_fd=self.handles["volume"], follow_symlinks=False)
        if (
            not stat.S_ISDIR(original.st_mode)
            or self._identity(fd) != self._identities["lost+found"]
            or (original.st_dev, original.st_ino, original.st_rdev)
            != (linked.st_dev, linked.st_ino, linked.st_rdev)
            or original.st_nlink == 0
            or os.listdir(fd)
        ):
            raise ValueError("original linked empty formatter directory changed")

    def _verify_transferred(self, name: str, fd: int) -> None:
        info = os.fstat(fd)
        if name not in {"loop", "loop-control"} and (
            info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022
        ):
            raise ValueError("original compiler object grants outside write authority")
        if name == "backing":
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != 0:
                raise ValueError("compiler backing must be pinned before its first growth")
        elif name == "loop":
            if not stat.S_ISBLK(info.st_mode) or os.major(info.st_rdev) != 7:
                raise ValueError("actual compiler selected loop device differs")
            status = bytearray(232)
            try:
                fcntl.ioctl(fd, 0x4C05, status, True)
            except OSError as error:
                if error.errno != 6:
                    raise
            else:
                raise ValueError("compiler selected loop is already attached; retry refuses")
        elif name == "loop-control":
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != os.makedev(10, 237):
                raise ValueError("actual compiler loop allocator differs")
        elif name in {"container", "mountpoint", "volume", "lost+found"}:
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("actual compiler directory FD differs")
            if name == "volume":
                loop = os.fstat(self.handles["loop"])
                raw = os.pread(self.handles["loop"], 1024, 1024)
                if (
                    info.st_dev != loop.st_rdev
                    or len(raw) != 1024
                    or struct.unpack_from("<H", raw, 56)[0] != 0xEF53
                    or not 0 < struct.unpack_from("<I", raw)[0] <= 128
                ):
                    raise ValueError("actual newly mounted compiler ext4 geometry differs")
            if name == "lost+found" and info.st_dev != os.fstat(self.handles["volume"]).st_dev:
                raise ValueError(
                    "actual formatter directory is outside the original compiler volume"
                )
            if name == "lost+found" and os.listdir(fd):
                raise ValueError("fresh formatter lost+found is not empty")
        else:
            raise ValueError("unexpected compiler storage creation stage")
        self._identities[name] = self._identity(fd)

    def create(self) -> None:
        if self.attempted or self.failed:
            raise ValueError("original compiler volume creation is consumed; retry refuses")
        self.attempted = True
        try:
            self.verify()
            self.channel.open()
            self.channel.expected = ["container", "mountpoint", "backing", "loop-control", "loop"]
            assert self.channel.child is not None
            if (
                self.jobs.run(
                    self._objects_child,
                    {self.handles["parent"], self.channel.child.fileno()},
                    transfer=self.channel,
                )
                != b"compiler-objects-created"
                or self.channel.position != 5
            ):
                raise ValueError("original compiler object handoff remains partial")
            self._verify_attached_loop()
            self.jobs.run(
                self._formatter_child,
                {self.handles["formatter"], self.handles["loop"], self.handles["backing"]},
                _format_output=True,
            )
            self.channel.expected.extend(["volume", "lost+found"])
            if (
                self.jobs.run(
                    self._mount_child,
                    {self.handles["loop"], self.handles["mountpoint"], self.channel.child.fileno()},
                    transfer=self.channel,
                )
                != b"compiler-volume-mounted"
                or self.channel.position != 7
            ):
                raise ValueError("original compiler mount handoff remains partial")
            self.complete = True
            self.verify()
            for name, source in (
                ("compiler-volume", "volume"),
                ("compiler-backing", "backing"),
                ("compiler-loop", "loop"),
            ):
                self.driver.handles[name] = self.handles[source]
        except BaseException as error:
            self.failed = True
            self.reservation._retain_installation_refusal(error)
            raise

    def _verify_attached_loop(self) -> None:
        backing = os.fstat(self.handles["backing"])
        if backing.st_size != 16777216 or backing.st_nlink != 1:
            raise ValueError("actual original compiler backing growth differs")
        raw = bytearray(232)
        fcntl.ioctl(self.handles["loop"], 0x4C05, raw, True)
        device, inode, _, offset, size = struct.unpack_from("=QQQQQ", raw)
        if (device, inode, offset, size) != (backing.st_dev, backing.st_ino, 0, 16777216):
            raise ValueError("actual original compiler loop attachment or range differs")

    def _objects_child(self) -> bytes:
        os.mkdir(PurePosixPath(self.container).name, 0o700, dir_fd=self.handles["parent"])
        container = os.open(
            PurePosixPath(self.container).name, FLAGS, dir_fd=self.handles["parent"]
        )
        self.channel.transfer("container", container)
        os.mkdir("volume", 0o700, dir_fd=container)
        mountpoint = os.open("volume", FLAGS, dir_fd=container)
        self.channel.transfer("mountpoint", mountpoint)
        backing = os.open(
            "compiler.img",
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
            dir_fd=container,
        )
        self.channel.transfer("backing", backing)
        os.ftruncate(backing, 16777216)
        control = os.open("/dev/loop-control", os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
        self.channel.transfer("loop-control", control)
        number = fcntl.ioctl(control, LOOP_CTL_GET_FREE)
        if not isinstance(number, int) or not 0 <= number < 1048576:
            raise ValueError("bounded original compiler free loop identity unavailable")
        loop = os.open(f"/dev/loop{number}", os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
        self.channel.transfer("loop", loop)
        fcntl.ioctl(loop, LOOP_SET_FD, backing)
        info = os.fstat(backing)
        raw = LOOP_INFO64.pack(
            _encode_device(info.st_dev),
            info.st_ino,
            0,
            0,
            16777216,
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
        return b"compiler-objects-created"

    def _formatter_child(self) -> bytes:
        formatter, loop = self.handles["formatter"], self.handles["loop"]
        os.set_inheritable(formatter, True)
        os.set_inheritable(loop, True)
        assert self.build.volume_constructor is not None
        os.execve(
            f"/proc/self/fd/{formatter}",
            [
                self.build.volume_constructor.formatter,
                "-F",
                "-q",
                "-t",
                "ext4",
                "-b",
                "4096",
                "-N",
                "128",
                "-m",
                "0",
                "-O",
                "^has_journal",
                "-E",
                "lazy_itable_init=0,lazy_journal_init=0",
                f"/proc/self/fd/{loop}",
            ],
            {},
        )
        raise ValueError("fixed compiler formatter must exec")

    def _mount_child(self) -> bytes:
        target = f"/proc/self/fd/{self.handles['mountpoint']}"
        source = f"/proc/self/fd/{self.handles['loop']}"
        if (
            ctypes.CDLL(None, use_errno=True).mount(
                ctypes.c_char_p(source.encode()),
                ctypes.c_char_p(target.encode()),
                ctypes.c_char_p(b"ext4"),
                ctypes.c_ulong(2 | 4),
                None,
            )
            != 0
        ):
            raise OSError(ctypes.get_errno(), "original compiler mount refused")
        volume = os.open(self.build.volume, FLAGS)
        self.channel.transfer("volume", volume)
        os.fchmod(volume, 0o700)
        lost = os.open("lost+found", FLAGS, dir_fd=volume)
        self.channel.transfer("lost+found", lost)
        current = os.stat("lost+found", dir_fd=volume, follow_symlinks=False)
        if self._identity(lost) != (current.st_dev, current.st_ino, current.st_rdev) or os.listdir(
            lost
        ):
            raise ValueError("original empty formatter directory changed")
        # A deleted retained inode prevents the filesystem read-only remount.
        # Keep this empty directory linked under the same original handle.
        return b"compiler-volume-mounted"
