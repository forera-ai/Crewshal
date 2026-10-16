"""Finite original-observer installation source for a separately approved batch.

This module does not authorize execution, authentication, or subscription use.
Installation readback does not replace qualification or live acceptance.
Every partial object stays with its original driver after refusal.
"""

import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import resource
import signal
import stat
import struct
import sys
import time
from typing import NoReturn, Self, TYPE_CHECKING
from weakref import WeakKeyDictionary

from pydantic import Field, field_validator, model_validator

from crewshal.admission import _wait_ready
from crewshal.admission import NamespaceIdentity, _fields, _read, _stat_identity
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.durable import CoordinatorStore
from crewshal.linux_bootstrap import (
    BootstrapPreparation,
    audit_linux_bootstrap,
    bootstrap_policy,
    prepare_linux_bootstrap,
)
from crewshal.linux_inventory import (
    TrustedParentInventory,
    audit_parent_inventory,
    helper_library_inventory_digest,
    root_inventory_digest,
    _discard_completed_pages,
)
from crewshal.linux_parent import RetainedTrustedTask, TrustedTaskSpec
from crewshal.linux_installed import _mappings
from crewshal.linux_production import OwnedBackingProduction, PrivateEcryptfsKeys
from crewshal.linux_setup import (
    OwnedStorageReservation,
    reserve_lane_setups,
    reserve_storage_installation,
)
from crewshal.linux_storage import AnonymousKeyring, BoundedStorageJobs
from crewshal.linux_compiler_volume import FrozenCompilerVolumeRecipe, OriginalCompilerVolume
from crewshal.linux_early_timer import FrozenEarlyTimerRuntime, create_owned_early_batch_timer
from crewshal.linux_payload_storage import (
    PROPOSED_POLICY,
    RetainedAppArmorExport,
    StorageSourceAudit,
)
from crewshal.model import Contract, digest
from crewshal.supervisor import CgroupIdentity, OwnedCgroup

if TYPE_CHECKING:
    from crewshal.linux_attempt import FrozenAttemptMarker
    from crewshal.linux_qualification_fixture import FrozenQualificationFixture

LANES = ("qualification-1", "qualification-2", "live")
ROLES = ("setup", "supervisor", "worker", "validator")
DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
COMPILER_LOGICAL_BYTES = 167772160
COMPILER_ALLOCATED_BYTES = 50331648
OWNER_AGGREGATE_UNIT = "crewshal-2d-20261012v1.slice"
OWNER_OBSERVER_UNIT = "crewshal-2d-20261012v1-observer.service"
OWNER_CGROUP_PARENT = "crewshal.slice/crewshal-2d.slice"
_COMPILER_STORAGE: WeakKeyDictionary["OriginalInstallationDriver", "RetainedCompilerStorage"] = (
    WeakKeyDictionary()
)


class RetainedCompilerStorage:
    """Original compiler volume custody supplies actual bounds, never a flag."""

    driver: "OriginalInstallationDriver"
    setup: OwnedCgroup
    _owners: tuple["OriginalInstallationDriver", OwnedCgroup]
    _origin: float
    _geometry: tuple[bytes, int]
    _handles: dict[str, int]
    _identities: dict[str, tuple[int, int, int]]
    reservation: object | None
    _volume_creator: OriginalCompilerVolume | None

    def __init__(self) -> None:
        raise ValueError("compiler storage requires original driver creation custody")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original compiler storage cannot be copied or exported")

    @classmethod
    def retain(
        cls, driver: "OriginalInstallationDriver", setup: OwnedCgroup
    ) -> "RetainedCompilerStorage":
        if type(driver) is not OriginalInstallationDriver or driver in _COMPILER_STORAGE:
            raise ValueError("original compiler storage is one-shot")
        retained = object.__new__(cls)
        retained.driver, retained.setup = driver, setup
        retained._owners = (driver, setup)
        retained._origin = driver.origin
        retained._geometry = driver._compiler_geometry
        retained._handles = {
            name: driver.handles[name]
            for name in (
                "compiler-volume",
                "compiler-loop",
                "compiler-backing",
                "compiler",
                "compiler-source",
            )
        }
        retained._identities = {
            name: (os.fstat(fd).st_dev, os.fstat(fd).st_ino, os.fstat(fd).st_rdev)
            for name, fd in retained._handles.items()
        }
        retained.reservation = None
        retained._volume_creator = getattr(driver, "compiler_volume", None)
        if retained._volume_creator is not None:
            if (
                type(retained._volume_creator) is not OriginalCompilerVolume
                or retained._volume_creator.driver is not driver
                or retained._volume_creator.setup is not setup
            ):
                raise ValueError("compiler storage has no original charged volume constructor")
            retained._volume_creator.verify()
        _COMPILER_STORAGE[driver] = retained
        driver.compiler_storage = retained
        if driver.reservation is None or driver.observer is not driver.reservation.observer:
            raise ValueError("compiler storage requires its original upfront charge")
        driver.reservation.verify()
        if hasattr(driver.reservation, "_compiler_storage"):
            raise ValueError("original compiler storage binding already exists")
        retained.reservation = driver.reservation
        setattr(driver.reservation, "_compiler_storage", retained)
        return retained

    @property
    def logical_bytes(self) -> int:
        return COMPILER_LOGICAL_BYTES

    @property
    def allocated_bytes(self) -> int:
        return COMPILER_ALLOCATED_BYTES

    def bind(self, reservation: object) -> None:
        if self.reservation is not None or self.driver.reservation is not reservation:
            raise ValueError("compiler storage requires the original installation reservation")
        self.reservation = reservation
        if hasattr(reservation, "_compiler_storage"):
            raise ValueError("original compiler storage binding already exists")
        setattr(reservation, "_compiler_storage", self)
        self.verify()

    def verify(self) -> None:
        driver, setup = self._owners
        if self._volume_creator is not None:
            if getattr(driver, "compiler_volume", None) is not self._volume_creator:
                raise ValueError("original compiler volume constructor was replaced")
            self._volume_creator.verify()
        observed_exit = driver._compiler_exit
        task_handles = driver._compiler_task_handles
        if (
            driver is not self.driver
            or setup is not self.setup
            or _COMPILER_STORAGE.get(driver) is not self
            or driver.compiler_storage is not self
            or driver.origin != self._origin
            or driver._compiler_geometry != self._geometry
            or driver.compiler_child is not None
            or observed_exit is None
            or task_handles is None
            or observed_exit[0] != task_handles[0]
            or not os.WIFEXITED(observed_exit[1])
            or os.WEXITSTATUS(observed_exit[1]) != 0
        ):
            raise ValueError("original compiler owner, terminal state, or volume differs")
        assert task_handles is not None
        _, pidfd, device, inode = task_handles
        info = os.fstat(pidfd)
        if (
            driver.handles.get("compiler-pidfd") != pidfd
            or (info.st_dev, info.st_ino) != (device, inode)
            or not _wait_ready([pidfd], [], [], 0)[0]
        ):
            raise ValueError("original compiler retained terminal pidfd changed")
        proc = os.open("/proc", DIRECTORY_FLAGS)
        try:
            if _fields(_read(proc, f"self/fdinfo/{pidfd}")).get("Pid") != "-1":
                raise ValueError("original compiler positive reap remains unknown")
        finally:
            os.close(proc)
        if self.reservation is not None and (
            self.reservation is not driver.reservation
            or getattr(self.reservation, "_compiler_storage", None) is not self
            or getattr(self.reservation, "observer", None) is not driver.observer
        ):
            raise ValueError("original compiler reservation or observer binding differs")
        for name, descriptor in self._handles.items():
            info = os.fstat(descriptor)
            if (
                driver.handles.get(name) != descriptor
                or (info.st_dev, info.st_ino, info.st_rdev) != self._identities[name]
            ):
                raise ValueError("original compiler retained handle changed")
        backing = os.fstat(self._handles["compiler-backing"])
        if backing.st_size != 16777216 or backing.st_nlink != 1:
            raise ValueError("original compiler backing bound changed")
        status = bytearray(232)
        fcntl.ioctl(self._handles["compiler-loop"], 0x4C05, status, True)
        device, inode, _, offset, size = struct.unpack_from("=QQQQQ", status)
        build = driver.inputs.helper_build
        expected_loop_size = (
            16777216 if build is not None and build.volume_constructor is not None else 0
        )
        if (device, inode, offset, size) != (backing.st_dev, backing.st_ino, 0, expected_loop_size):
            raise ValueError("original compiler loop range changed")
        raw = os.pread(self._handles["compiler-loop"], 1024, 1024)
        volume = os.fstat(self._handles["compiler-volume"])
        loop = os.fstat(self._handles["compiler-loop"])
        if _stable_ext4_geometry(raw) != self._geometry[0] or volume.st_dev != loop.st_rdev:
            raise ValueError("original compiler filesystem or mount changed")
        vfs = os.fstatvfs(self._handles["compiler-volume"])
        if (
            vfs.f_files != self._geometry[1]
            or vfs.f_blocks * vfs.f_frsize > 16777216
            or not vfs.f_flag & os.ST_RDONLY
        ):
            raise ValueError("original compiler total growth bound changed")
        build = driver.inputs.helper_build
        expected = (
            {"crewshal-bootstrap"}
            if build is None or build.policy_build is None
            else {"crewshal-bootstrap", "policy.binary", "storage-audit.json"}
        )
        formatter_entries = {"lost+found"} if self._volume_creator is not None else set()
        if set(os.listdir(self._handles["compiler-volume"])) != expected | formatter_entries:
            raise ValueError("original compiler artifact inventory changed")
        if build is not None and build.policy_build is not None:
            terminal, task = driver._policy_exit, driver._policy_task_handles
            if (
                terminal is None
                or task is None
                or terminal[0] != task[0]
                or not os.WIFEXITED(terminal[1])
                or os.WEXITSTATUS(terminal[1]) != 0
            ):
                raise ValueError("original policy positive reap or successful exit remains unknown")
            info = os.fstat(task[1])
            if (
                driver.handles.get("policy-pidfd") != task[1]
                or (info.st_dev, info.st_ino) != task[2:]
                or not _wait_ready([task[1]], [], [], 0)[0]
            ):
                raise ValueError("original policy terminal pidfd identity changed")
            proc = os.open("/proc", DIRECTORY_FLAGS)
            try:
                if _fields(_read(proc, f"self/fdinfo/{task[1]}")).get("Pid") != "-1":
                    raise ValueError("original policy positive reap remains unknown")
            finally:
                os.close(proc)
            self._verify_setup_role()
        for name in expected:
            fd = driver.handles["build-output:" + name]
            retained, current = (
                os.fstat(fd),
                os.stat(name, dir_fd=self._handles["compiler-volume"], follow_symlinks=False),
            )
            if (retained.st_dev, retained.st_ino) != (
                current.st_dev,
                current.st_ino,
            ) or not 0 < retained.st_size <= 1048576:
                raise ValueError("original pinned build output custody changed")

    def _verify_setup_role(self) -> None:
        """Retain role controls after the original build processes have exited."""
        from crewshal.linux_setup import _role_controls

        _role_controls(self.setup)


def _stable_ext4_geometry(raw: bytes) -> bytes:
    if len(raw) != 1024:
        raise ValueError("complete original compiler superblock required")
    return b"".join(
        raw[start:end]
        for start, end in ((0, 8), (20, 28), (32, 44), (56, 58), (76, 80), (84, 104), (336, 340))
    )


class FrozenBuildFilesystem(Contract):
    """The recipe binds the exact pre-existing compiler storage objects."""

    volume_device: int = Field(ge=0)
    volume_inode: int = Field(gt=0)
    backing_device: int = Field(ge=0)
    backing_inode: int = Field(gt=0)
    loop_device: int = Field(ge=0)
    loop_inode: int = Field(gt=0)
    loop_rdev: int = Field(gt=0)
    geometry_sha256: Digest
    inodes: int = Field(gt=0, le=128)


class FrozenPolicyBuild(Contract):
    """Only stdout compilation may produce the reviewed AppArmor policy."""

    parser: str
    parser_sha256: Digest
    source: str
    source_sha256: Digest
    argv: list[str] = Field(min_length=1, max_length=64)
    environment: dict[str, str]
    files: dict[str, Digest]
    include_files: dict[str, Digest]
    audit_template: StorageSourceAudit

    @model_validator(mode="after")
    def frozen_policy(self) -> Self:
        for path in (self.parser, self.source, *self.files, *self.include_files):
            _canonical_path(path)
        if (
            self.source_sha256 != digest(PROPOSED_POLICY)
            or self.audit_template.policy_source_sha256 != self.source_sha256
            or self.audit_template.policy_parser_executable_sha256 != self.parser_sha256
            or self.files.get(self.parser) != self.parser_sha256
            or not self.include_files
            or len(self.files) + len(self.include_files) > 512
            or self.environment
            or self.argv[0] != self.parser
            or not {"--skip-kernel-load", "--stdout", "--skip-cache", "--skip-read-cache"}
            <= set(self.argv)
            or "--config-file=/dev/null" not in self.argv
            or any(
                value in {"--replace", "--add", "--remove", "--write-cache"} for value in self.argv
            )
            or any(
                value
                not in {
                    "--skip-kernel-load",
                    "--stdout",
                    "--skip-cache",
                    "--skip-read-cache",
                    "--config-file=/dev/null",
                    "--jobs=1",
                    "--max-jobs=1",
                    "--zstd-compress-level=none",
                }
                and not value.startswith(
                    ("--base=", "--Include=", "--kernel-features=", "--override-policy-abi=")
                )
                for value in self.argv[1:]
            )
            or self.argv.count("--zstd-compress-level=none") != 1
            or self.argv.count("--config-file=/dev/null") != 1
            or len([value for value in self.argv if value.startswith("--base=")]) != 1
            or len([value for value in self.argv if value.startswith("--kernel-features=")]) != 1
            or len([value for value in self.argv if value.startswith("--override-policy-abi=")])
            != 1
            or "--jobs=1" not in self.argv
            or "--max-jobs=1" not in self.argv
        ):
            raise ValueError(
                "frozen policy compilation must avoid kernel, cache, and ambient configuration"
            )
        for prefix in ("--kernel-features=", "--override-policy-abi="):
            path = next(
                value.removeprefix(prefix) for value in self.argv if value.startswith(prefix)
            )
            _canonical_path(path)
            if path not in self.include_files:
                raise ValueError(
                    "frozen parser ABI or kernel feature input is missing from its immutable closure"
                )
        return self


class FrozenHelperBuild(Contract):
    """One exact build uses a pre-existing private bounded ext4 volume."""

    compiler: str
    compiler_sha256: Digest
    source: str
    source_sha256: Digest
    volume: str
    loop_device: str
    backing: str
    toolchain_files: dict[str, Digest]
    argv: list[str] | None = None
    environment: dict[str, str] | None = None
    header_files: dict[str, Digest] = Field(default_factory=dict)
    runtime_files: dict[str, Digest] = Field(default_factory=dict)
    filesystem: FrozenBuildFilesystem | None = None
    policy_build: FrozenPolicyBuild | None = None
    volume_constructor: FrozenCompilerVolumeRecipe | None = None

    @model_validator(mode="after")
    def complete_closure(self) -> Self:
        if self.policy_build is None:
            return self
        if (
            self.argv is None
            or self.environment != {"TMPDIR": self.volume}
            or (self.filesystem is None and self.volume_constructor is None)
            or not self.header_files
            or self.runtime_files.get(self.compiler) != self.compiler_sha256
            or len(self.header_files) + len(self.runtime_files) + len(self.toolchain_files) > 512
            or self.argv[0] != self.compiler
            or "-nostdinc" not in self.argv
            or not {"-pipe", "-static", "-s", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror"}
            <= set(self.argv)
            or self.argv[-1] != "-"
            or self.argv.count("-o") != 1
            or self.argv[self.argv.index("-o") + 1] != "@original-helper-output"
        ):
            raise ValueError(
                "complete immutable helper, policy, runtime, header, and storage recipe required"
            )
        for path in (*self.header_files, *self.runtime_files):
            _canonical_path(path)
        return self

    @field_validator("compiler", "source", "volume", "loop_device", "backing")
    @classmethod
    def exact_path(cls, value: str) -> str:
        _canonical_path(value)
        return value

    @field_validator("toolchain_files")
    @classmethod
    def static_toolchain_closure(cls, value: dict[str, str]) -> dict[str, str]:
        required = {
            "libc.a",
            "libgcc.a",
            "libgcc_eh.a",
            "crt1.o",
            "crti.o",
            "crtn.o",
            "crtbeginT.o",
            "crtend.o",
            "cc1",
            "collect2",
        }
        names = {PurePosixPath(path).name for path in value}
        if (
            not required.issubset(names)
            or not names.intersection({"as", "aarch64-linux-gnu-as"})
            or not names.intersection({"ld", "aarch64-linux-gnu-ld.bfd"})
            or len(value) > 64
        ):
            raise ValueError("exact complete reviewed static compiler closure required")
        for path in value:
            _canonical_path(path)
        return value


class FrozenInstallationInputs(Contract):
    """Frozen data identifies inputs. It supplies no operational authority."""

    configuration: DispatchConfiguration
    bootstrap: BootstrapPreparation
    inventory: TrustedParentInventory
    cgroup_parent: str
    batch_leaf: str = Field(pattern=r"^crewshal-2d-[a-z0-9][a-z0-9.-]{0,63}$")
    observer_name: str = Field(pattern=r"^[A-Za-z0-9_.@-]{1,128}$")
    journal: str
    installation_parent: str
    helper: str
    formatter: str
    formatter_sha256: Digest
    sources: dict[str, str]
    helper_build: FrozenHelperBuild | None = None
    early_timer: "FrozenEarlyTimerRuntime | None" = None
    apparmor_namespace: str
    apparmor_roles: tuple[tuple[str, str], tuple[str, str], tuple[str, str], tuple[str, str]]

    def verify_formatter_inventory(self) -> None:
        """Check the original formatter binding before any installation charge."""
        entry = self.inventory.root.get("/usr/sbin/mkfs.ext4")
        if (
            entry is None
            or entry.kind != "file"
            or not entry.mode & 0o111
            or entry.sha256 != self.formatter_sha256
            or self.sources.get("/usr/sbin/mkfs.ext4") != self.formatter
        ):
            raise ValueError("frozen root requires the same original executable formatter input")

    @field_validator("cgroup_parent")
    @classmethod
    def exact_cgroup_parent(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or str(path) != value or not path.parts or ".." in path.parts:
            raise ValueError("canonical existing cgroup parent required")
        return value

    @field_validator("journal", "installation_parent", "helper", "formatter", "apparmor_namespace")
    @classmethod
    def exact_host_path(cls, value: str) -> str:
        _canonical_path(value)
        return value


def _canonical_path(value: str) -> None:
    path = PurePosixPath(value)
    if not path.is_absolute() or str(path) != value or ".." in path.parts or "\x00" in value:
        raise ValueError("canonical absolute frozen path required")


def original_owner_units(entry_path: str, plan_path: str) -> dict[str, str]:
    """Prepare exact owner units. This function does not install or start them."""
    for path in (entry_path, plan_path):
        _canonical_path(path)
        if not re.fullmatch(r"/[A-Za-z0-9_./-]+", path):
            raise ValueError("owner launcher paths require exact literal systemd arguments")
    slice_source = """[Unit]
Description=Crewshal original Phase 2D aggregate

[Slice]
MemoryAccounting=yes
MemoryMax=805306368
MemorySwapMax=0
TasksAccounting=yes
TasksMax=128
CPUAccounting=yes
CPUQuota=100%
CPUQuotaPeriodSec=100ms
"""
    observer_source = (
        """[Unit]
Description=Crewshal original Phase 2D observer
Requires=crewshal-2d-20261012v1.slice
After=crewshal-2d-20261012v1.slice

[Service]
Type=exec
User=root
Group=root
SupplementaryGroups=
Slice=crewshal-2d-20261012v1.slice
MemoryAccounting=yes
MemoryMax=134217728
MemorySwapMax=0
TasksAccounting=yes
TasksMax=32
CPUAccounting=yes
CPUQuota=100%
CPUQuotaPeriodSec=100ms
NoNewPrivileges=yes
ProtectSystem=strict
PrivateMounts=yes
ReadWritePaths=/run /sys/fs/cgroup/crewshal.slice/crewshal-2d.slice /sys/kernel/security/apparmor
BindPaths=/var/lib/crewshal-phase2d-storage-v1:/run
BindReadOnlyPaths=/var/lib/crewshal-phase2d-input-v1:/run/crewshal-phase2d-input-v1
WorkingDirectory=/
Environment=
LimitFSIZE=1073741824
LimitNOFILE=4096
Delegate=yes
Restart=no
KillMode=control-group
TimeoutStopSec=1
StandardInput=null
StandardOutput=journal
StandardError=journal
ExecStart=/usr/bin/env -i /usr/bin/python3.12 -I -S -B """
        + entry_path
        + " "
        + plan_path
        + "\n"
    )
    return {OWNER_AGGREGATE_UNIT: slice_source, OWNER_OBSERVER_UNIT: observer_source}


def _open_path(value: str, *, directory: bool = False, root_fd: int | None = None) -> int:
    """Walk real parents without following links or accepting writable ancestors."""
    _canonical_path(value)
    parts = PurePosixPath(value).parts[1:]
    descriptor = os.open("/", DIRECTORY_FLAGS) if root_fd is None else os.dup(root_fd)
    try:
        for index, part in enumerate(parts):
            last = index == len(parts) - 1
            child = os.open(
                part, DIRECTORY_FLAGS if not last or directory else FILE_FLAGS, dir_fd=descriptor
            )
            os.close(descriptor)
            descriptor = child
            info = os.fstat(descriptor)
            if info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
                raise ValueError("frozen input ancestor or file grants outside write authority")
        result, descriptor = descriptor, -1
        return result
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _hash_file(descriptor: int, expected: str, deadline: float) -> None:
    before = os.fstat(descriptor)
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or not 0 <= before.st_size <= 1073741824
    ):
        raise ValueError("bounded root-owned single-link frozen file required")
    sha, offset = hashlib.sha256(), 0
    while offset < before.st_size:
        if time.monotonic() >= deadline:
            raise ValueError("original installation startup deadline exhausted")
        chunk = os.pread(descriptor, min(65536, before.st_size - offset), offset)
        if not chunk:
            raise ValueError("frozen input read incomplete")
        sha.update(chunk)
        offset += len(chunk)
        _discard_completed_pages(descriptor, offset, before.st_size)
    after = os.fstat(descriptor)
    keys = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_uid",
        "st_gid",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    if sha.hexdigest() != expected or any(
        getattr(before, key) != getattr(after, key) for key in keys
    ):
        raise ValueError("frozen input bytes or retained identity changed")


def _output_digest(descriptor: int, deadline: float) -> str:
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= 1048576 or info.st_nlink != 1:
        raise ValueError("original build output size or inode differs")
    sha, offset = hashlib.sha256(), 0
    while offset < info.st_size:
        if time.monotonic() >= deadline:
            raise ValueError("original shared build deadline exhausted")
        chunk = os.pread(descriptor, min(65536, info.st_size - offset), offset)
        if not chunk:
            raise ValueError("original build output read incomplete")
        sha.update(chunk)
        offset += len(chunk)
    result = sha.hexdigest()
    _hash_file(descriptor, result, deadline)
    return result


class OperationalRefusal(ValueError):
    def __init__(self, reason: str, driver: "OriginalInstallationDriver"):
        super().__init__(reason)
        self.driver = driver


class OriginalInstallationDriver:
    """Create one installation from concrete current kernel objects, without retry."""

    reservation: "OwnedStorageReservation | None"
    compiler_volume: OriginalCompilerVolume

    def __init__(
        self,
        inputs: FrozenInstallationInputs,
        *,
        fixture: "FrozenQualificationFixture | None" = None,
        attempt_marker: "FrozenAttemptMarker | None" = None,
    ):
        self.attempt_marker = attempt_marker
        self.origin = time.monotonic()
        self.handles: dict[str, int] = {}
        if sys.platform == "linux":
            descriptor = os.open("/proc/self", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
            self.handles["origin-proc"] = descriptor
            pid, _, _, ticks = _stat_identity(_read(descriptor, "stat"))
            clock_offset = time.clock_gettime(getattr(time, "CLOCK_BOOTTIME")) - time.monotonic()
            if pid != os.getpid() or ticks <= 0 or abs(clock_offset) > 0.002:
                raise ValueError("original process clock base or birth identity remains unknown")
            # Kernel start ticks precede Python imports and preparation. This
            # conservative offset cannot extend the original process deadline.
            self.origin = ticks / os.sysconf("SC_CLK_TCK") - 0.002
            if not 0 < self.origin <= time.monotonic() < self.origin + 120:
                raise ValueError("original observer process startup origin expired")
        self.inputs = FrozenInstallationInputs.model_validate_json(inputs.model_dump_json())
        self._input_payload = self.inputs.model_dump_json()
        self.fixture = None
        self._fixture_payload = None
        if fixture is not None:
            from crewshal.linux_qualification_fixture import FrozenQualificationFixture

            self.fixture = FrozenQualificationFixture.model_validate_json(fixture.model_dump_json())
            self._fixture_payload = self.fixture.model_dump_json()
        self._origin = self.origin
        self.groups: dict[str, OwnedCgroup] = {}
        self.failed = False
        self.attempted = False
        self.observer: RetainedTrustedTask | None = None
        self.reservation = None
        self.timer = None
        self.production = None
        self.installation = None
        self.store = None
        self.keys = None
        self.ring = None
        self.lanes = None
        self.compiler_child: tuple[int, int] | None = None
        self.compiler_capture: tuple[bytes, bytes] | None = None
        self.compiler_storage: RetainedCompilerStorage | None = None
        self._compiler_attempted = False
        self._policy_attempted = False
        self._compiler_geometry: tuple[bytes, int] = (b"", 0)
        self._compiler_exit: tuple[int, int] | None = None
        self._compiler_task_handles: tuple[int, int, int, int] | None = None
        self._policy_exit: tuple[int, int] | None = None
        self._policy_task_handles: tuple[int, int, int, int] | None = None
        self._build_deadline: float | None = None

    def _attach_original_group(self, path: str, name: str) -> OwnedCgroup:
        descriptor = _open_path("/sys/fs/cgroup/" + path, directory=True)
        self.handles["cgroup:" + path] = descriptor
        info = os.fstat(descriptor)
        group = OwnedCgroup.attach(
            CgroupIdentity(relative_path=path, device=info.st_dev, inode=info.st_ino)
        )
        self.groups[name] = group
        return group

    def _compile_helper(self, build: FrozenHelperBuild, setup: OwnedCgroup) -> None:
        """Use fixed compiler arguments, original limits, and actual loop readback."""
        if self._compiler_attempted:
            raise ValueError("original compiler attempt consumed; no retry")
        self._compiler_attempted = True
        if self.reservation is None or self.observer is not self.reservation.observer:
            raise ValueError("compiler requires the original full charge before output")
        self.reservation.verify()
        if self.reservation.capacity_claim.record.configuration != record_digest(
            self.inputs.configuration
        ):
            raise ValueError("compiler requires its original frozen recipe charge")
        if signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
            raise ValueError("original compiler requires exclusive default child reaping")
        if build.policy_build is not None:
            if self.timer is None or (
                build.filesystem is None and build.volume_constructor is None
            ):
                raise ValueError(
                    "complete build requires the original early timer and filesystem recipe"
                )
            self.timer.verify()
        deadline = self._build_deadline = min(
            self.origin + 120, self.origin + 570, time.monotonic() + 30
        )
        compiler = _open_path(build.compiler)
        self.handles["compiler"] = compiler
        source = _open_path(build.source)
        self.handles["compiler-source"] = source
        _hash_file(compiler, build.compiler_sha256, deadline)
        _hash_file(source, build.source_sha256, deadline)
        if build.policy_build is not None and not os.fstatvfs(source).f_flag & os.ST_RDONLY:
            raise ValueError("original immutable helper source filesystem remains writable")
        if build.source_sha256 != self.inputs.bootstrap.policy.helper_source:
            raise ValueError("frozen compiler source differs from current helper source")
        for path, expected in {
            **build.toolchain_files,
            **build.header_files,
            **build.runtime_files,
        }.items():
            descriptor = _open_path(path)
            self.handles["compiler-input:" + path] = descriptor
            _hash_file(descriptor, expected, deadline)
            if build.policy_build is not None and not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY:
                raise ValueError(
                    "build input runtime, compiler, or header filesystem remains writable"
                )
        volume = (
            self.handles.get("compiler-volume") if build.volume_constructor is not None else None
        )
        if volume is None:
            volume = _open_path(build.volume, directory=True)
        self.handles["compiler-volume"] = volume
        if stat.S_IMODE(os.fstat(volume).st_mode) != 0o700:
            raise ValueError("compiler volume root must remain exclusively owned")
        formatter_entries = {"lost+found"} if build.volume_constructor is not None else set()
        if build.volume_constructor is not None:
            self.compiler_volume.verify_formatter_directory()
        if (
            set(os.listdir(volume)) != formatter_entries
            or self.inputs.helper != build.volume + "/crewshal-bootstrap"
        ):
            raise ValueError("compiler volume must be new, empty, and exclusively bound")
        backing = (
            self.handles.get("compiler-backing") if build.volume_constructor is not None else None
        )
        if backing is None:
            backing = _open_path(build.backing)
        self.handles["compiler-backing"] = backing
        before = os.fstat(backing)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != 16777216:
            raise ValueError("fixed 16 MiB compiler backing required")
        device = self.handles.get("compiler-loop") if build.volume_constructor is not None else None
        if device is None:
            device = _open_path(build.loop_device)
        self.handles["compiler-loop"] = device
        info = os.fstat(device)
        if not stat.S_ISBLK(info.st_mode) or os.major(info.st_rdev) != 7:
            raise ValueError("compiler requires the actual retained loop device")
        status = bytearray(232)
        fcntl.ioctl(device, 0x4C05, status, True)
        loop_device, loop_inode, _, offset, size = struct.unpack_from("=QQQQQ", status)
        expected_loop_size = 16777216 if build.volume_constructor is not None else 0
        if (loop_device, loop_inode, offset, size) != (
            before.st_dev,
            before.st_ino,
            0,
            expected_loop_size,
        ):
            raise ValueError("compiler loop backing identity or range differs")
        raw = os.pread(device, 1024, 1024)
        if len(raw) != 1024 or struct.unpack_from("<H", raw, 56)[0] != 0xEF53:
            raise ValueError("compiler volume requires actual ext4 geometry")
        inodes, blocks = struct.unpack_from("<II", raw)
        block_shift = struct.unpack_from("<I", raw, 24)[0]
        if block_shift > 2:
            raise ValueError("compiler ext4 block geometry differs")
        block_size = 1024 << block_shift
        if not 0 < inodes <= 128 or blocks * block_size > 16777216:
            raise ValueError("compiler total inode or allocation ceiling differs")
        mounted = os.fstat(volume)
        if mounted.st_dev != info.st_rdev:
            raise ValueError("compiler volume mount and actual loop device differ")
        vfs = os.fstatvfs(volume)
        if vfs.f_files != inodes or vfs.f_blocks * vfs.f_frsize > 16777216:
            raise ValueError("compiler live inode or allocation geometry differs")
        mount_device = f"{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}"
        with open("/proc/self/mountinfo", "rb") as stream:
            mount_rows = stream.read(65537)
        if len(mount_rows) > 65536:
            raise ValueError("compiler mount inventory exceeds bound")
        matches = []
        for line in mount_rows.decode("ascii").splitlines():
            before_separator, _, after_separator = line.partition(" - ")
            fields = before_separator.split()
            if len(fields) >= 6 and fields[4] == build.volume:
                matches.append((fields[2], fields[3], after_separator.split()[0]))
            elif len(fields) >= 6 and fields[4].startswith(build.volume + "/"):
                raise ValueError("compiler volume contains a foreign nested mount")
        if matches != [(mount_device, "/", "ext4")]:
            raise ValueError("compiler requires one complete exclusive ext4 root mount")
        self._compiler_geometry = (_stable_ext4_geometry(raw), inodes)
        if build.filesystem is not None:
            expected_fs = FrozenBuildFilesystem(
                volume_device=mounted.st_dev,
                volume_inode=mounted.st_ino,
                backing_device=before.st_dev,
                backing_inode=before.st_ino,
                loop_device=info.st_dev,
                loop_inode=info.st_ino,
                loop_rdev=info.st_rdev,
                geometry_sha256=digest(self._compiler_geometry[0]),
                inodes=inodes,
            )
            if expected_fs != build.filesystem:
                raise ValueError("original frozen compiler storage identity differs")
        names = (
            ("crewshal-bootstrap",)
            if build.policy_build is None
            else ("crewshal-bootstrap", "policy.binary", "storage-audit.json")
        )
        for name in names:
            fd = os.open(
                name,
                os.O_CREAT | os.O_EXCL | os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o755 if name == "crewshal-bootstrap" else 0o600,
                dir_fd=volume,
            )
            self.handles["build-output:" + name] = fd
        self.handles["compiled-helper-output"] = self.handles["build-output:crewshal-bootstrap"]
        RetainedCompilerStorage.retain(self, setup)
        # The one MiB hard file limit and 128 actual inodes bound total logical
        # compiler files at 128 MiB. Ext4 bounds allocation at 16 MiB.
        argv = build.argv or [
            build.compiler,
            "-pipe",
            "-static",
            "-s",
            "-O2",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-x",
            "c",
            "-o",
            "@original-helper-output",
            "-",
        ]
        output = self.handles["compiled-helper-output"]
        argv = [
            "/proc/self/fd/" + str(output) if item == "@original-helper-output" else item
            for item in argv
        ]
        self._run_build_process(
            "compiler",
            compiler,
            source,
            argv,
            build.environment or {"TMPDIR": build.volume},
            setup,
            deadline,
            {**build.runtime_files, build.compiler: build.compiler_sha256},
            inherit_output=output,
        )
        if build.policy_build is not None:
            self._compile_policy(build, setup, deadline)
        expected_names = (
            {"crewshal-bootstrap"}
            if build.policy_build is None
            else {"crewshal-bootstrap", "policy.binary", "storage-audit.json"}
        )
        if build.volume_constructor is not None:
            self.compiler_volume.verify_formatter_directory()
        if set(os.listdir(volume)) != expected_names | formatter_entries:
            raise ValueError("compiler artifacts differ from the exact original output inventory")
        for name in expected_names:
            fd = self.handles["build-output:" + name]
            original, current = os.fstat(fd), os.stat(name, dir_fd=volume, follow_symlinks=False)
            if (original.st_dev, original.st_ino) != (
                current.st_dev,
                current.st_ino,
            ) or not 0 < original.st_size <= 1048576:
                raise ValueError("original pre-write pinned output inode changed or exceeds bound")
        for path, expected in {
            **build.toolchain_files,
            **build.header_files,
            **build.runtime_files,
        }.items():
            _hash_file(self.handles["compiler-input:" + path], expected, deadline)
        self._seal_compiler_volume(build, setup)

    def _seal_compiler_volume(self, build: FrozenHelperBuild, setup: OwnedCgroup) -> None:
        """Prove build quiescence before sealing the original immutable outputs."""
        if setup._read("cgroup.procs") or "populated 1" in setup._read("cgroup.events"):
            raise ValueError("original build setup is not empty before sealing")
        libc = ctypes.CDLL(None, use_errno=True)
        if (
            libc.mount(
                None,
                ctypes.c_char_p(build.volume.encode()),
                None,
                ctypes.c_ulong(1 | 2 | 4 | 32),
                None,
            )
            != 0
        ):
            raise OSError(ctypes.get_errno(), "original compiler readonly remount refused")
        assert self.compiler_storage is not None
        self.compiler_storage.verify()

    def _run_build_process(
        self,
        name: str,
        executable: int,
        source: int,
        argv: list[str],
        environment: dict[str, str],
        setup: OwnedCgroup,
        deadline: float,
        runtime_files: dict[str, str],
        *,
        inherit_output: int | None = None,
        stdout_output: int | None = None,
    ) -> None:
        """Retain both stopped process identities before their output effects."""
        if deadline != self._build_deadline or time.monotonic() >= deadline:
            raise ValueError("original shared build interval changed or expired")
        if (
            self.inputs.helper_build is not None
            and self.inputs.helper_build.policy_build is not None
        ):
            if self.timer is None:
                raise ValueError("original early timer is missing")
            self.timer.verify()
        read_out, write_out = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        read_err, write_err = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        self.handles[name + "-stdout"], self.handles[name + "-stderr"] = read_out, read_err
        parent_pid = os.getpid()
        pid = os.fork()
        if pid == 0:
            try:
                libc = ctypes.CDLL(None, use_errno=True)
                if libc.prctl(1, int(signal.SIGKILL), 0, 0, 0) != 0 or os.getppid() != parent_pid:
                    os._exit(1)
                self._control(setup.descriptor, "cgroup.procs", str(os.getpid()))
                resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
                assert self.inputs.helper_build is not None
                os.chdir(self.inputs.helper_build.volume)
                os.kill(os.getpid(), signal.SIGSTOP)
                os.dup2(source, 0)
                if stdout_output is None:
                    os.dup2(write_out, 1)
                else:
                    writer = os.open(
                        "/proc/self/fd/" + str(stdout_output), os.O_WRONLY | os.O_CLOEXEC
                    )
                    original, actual = os.fstat(stdout_output), os.fstat(writer)
                    if (original.st_dev, original.st_ino) != (actual.st_dev, actual.st_ino):
                        os._exit(1)
                    os.dup2(writer, 1)
                os.dup2(write_err, 2)
                os.set_blocking(1, True)
                os.set_blocking(2, True)
                keep = {0, 1, 2, executable}
                if inherit_output is not None:
                    keep.add(inherit_output)
                    os.set_inheritable(inherit_output, True)
                os.set_inheritable(executable, True)
                for text in os.listdir("/proc/self/fd"):
                    handle = int(text)
                    if handle not in keep:
                        try:
                            os.close(handle)
                        except OSError:
                            pass
                if libc.ptrace(0, 0, None, None) != 0:
                    os._exit(1)
                os.execve("/proc/self/fd/" + str(executable), argv, environment)
            except BaseException:
                os._exit(1)
        os.close(write_out)
        os.close(write_err)
        self.compiler_child = (pid, -1)
        try:
            pidfd = getattr(os, "pidfd_open")(pid, 0)
            self.handles[name + "-pidfd"] = pidfd
            pidfd_info = os.fstat(pidfd)
            task = (pid, pidfd, pidfd_info.st_dev, pidfd_info.st_ino)
            if name == "compiler":
                self._compiler_task_handles = task
            else:
                self._policy_task_handles = task
            self.compiler_child = (pid, pidfd)
            status = self._wait_build_stop(pid, pidfd, deadline)
            if not os.WIFSTOPPED(status) or os.WSTOPSIG(status) != signal.SIGSTOP:
                raise ValueError("original build pre-exec stop differs")
            proc = os.open(f"/proc/{pid}", DIRECTORY_FLAGS)
            self.handles[name + "-proc"] = proc
            actual_pid, _, actual_parent, actual_start = _stat_identity(_read(proc, "stat"))
            if (
                actual_pid != pid
                or actual_parent != parent_pid
                or actual_start <= 0
                or _read(proc, "cgroup").strip() != ("0::/" + setup.identity.relative_path).encode()
                or _fields(_read(proc, "status")).get("NoNewPrivs") != "1"
                or getattr(resource, "prlimit")(pid, resource.RLIMIT_FSIZE) != (1048576, 1048576)
            ):
                raise ValueError("original build stopped role or hard limit differs")
            getattr(signal, "pidfd_send_signal")(pidfd, signal.SIGCONT)
            status = self._wait_build_stop(pid, pidfd, deadline)
            if not os.WIFSTOPPED(status) or os.WSTOPSIG(status) != signal.SIGTRAP:
                raise ValueError("actual build executable stop remains unknown")
            observed_exe = os.open("exe", os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
            self.handles[name + "-actual-executable"] = observed_exe
            left, right = os.fstat(executable), os.fstat(observed_exe)
            if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
                raise ValueError("actual build executable differs from the frozen executable FD")
            build = self.inputs.helper_build
            assert build is not None
            if name == "compiler":
                source_digest = build.source_sha256
            else:
                assert build.policy_build is not None
                source_digest = build.policy_build.source_sha256
            _hash_file(source, source_digest, deadline)
            expected_argv = b"\0".join(value.encode() for value in argv) + b"\0"
            expected_environment = b"".join(
                (key + "=" + value).encode() + b"\0" for key, value in environment.items()
            )
            stdin, original_source = os.stat("fd/0", dir_fd=proc), os.fstat(source)
            cwd, original_volume = (
                os.stat("cwd", dir_fd=proc),
                os.fstat(self.handles["compiler-volume"]),
            )
            if (
                _read(proc, "cmdline") != expected_argv
                or _read(proc, "environ") != expected_environment
                or (stdin.st_dev, stdin.st_ino) != (original_source.st_dev, original_source.st_ino)
                or (cwd.st_dev, cwd.st_ino) != (original_volume.st_dev, original_volume.st_ino)
            ):
                raise ValueError(
                    "actual build argv, environment, input source, or cwd differs from the frozen recipe"
                )
            if stdout_output is not None:
                original, current = os.fstat(stdout_output), os.stat("fd/1", dir_fd=proc)
                if (original.st_dev, original.st_ino) != (current.st_dev, current.st_ino):
                    raise ValueError(
                        "actual policy stdout differs from the original pre-write output inode"
                    )
            self._retain_build_maps(name, proc, runtime_files, deadline)
            if ctypes.CDLL(None, use_errno=True).ptrace(17, pid, None, None) != 0:
                raise OSError(ctypes.get_errno(), "original build exec stop detach refused")
            streams = {read_out: bytearray(), read_err: bytearray()}
            pending = set(streams)
            try:
                while pending:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise ValueError("original shared build deadline exhausted")
                    for descriptor in _wait_ready(list(pending), [], [], min(remaining, 0.01))[0]:
                        chunk = os.read(descriptor, 65537 - len(streams[descriptor]))
                        streams[descriptor].extend(chunk)
                        if len(streams[descriptor]) > 65536:
                            raise ValueError("build capture exceeds the original stream bound")
                        if not chunk:
                            pending.remove(descriptor)
                if not _wait_ready([pidfd], [], [], max(0, deadline - time.monotonic()))[0]:
                    raise ValueError("original build terminal state remains unknown")
                observed, terminal = os.waitpid(pid, os.WNOHANG)
                if observed != pid or not os.WIFEXITED(terminal) or os.WEXITSTATUS(terminal) != 0:
                    raise ValueError("original build positive reap or exit differs")
                if name == "compiler":
                    self._compiler_exit = observed, terminal
                else:
                    self._policy_exit = observed, terminal
                self.compiler_child = None
                if setup._read("cgroup.procs") or "populated 1" in setup._read("cgroup.events"):
                    raise ValueError("original build setup descendants remain retained")
            finally:
                if name == "compiler":
                    self.compiler_capture = bytes(streams[read_out]), bytes(streams[read_err])
                else:
                    self.policy_capture = bytes(streams[read_out]), bytes(streams[read_err])
        except BaseException:
            setup.stop()
            # Failure retains the exact child, pidfd, outputs, and full charge.
            raise

    def _wait_build_stop(self, pid: int, pidfd: int, deadline: float) -> int:
        while time.monotonic() < deadline:
            observed, status = os.waitpid(pid, os.WNOHANG | os.WUNTRACED)
            if observed == pid:
                return status
            _wait_ready([pidfd], [], [], min(0.001, max(0, deadline - time.monotonic())))
        raise ValueError("original build stopped identity remains unknown")

    def _retain_build_maps(
        self, name: str, proc: int, files: dict[str, str], deadline: float
    ) -> None:
        for address, mapping in _mappings(_read(proc, "maps", limit=262144)).items():
            path = mapping[0]
            if path not in files:
                raise ValueError("actual build mapped image is outside the frozen runtime closure")
            fd = os.open("map_files/" + address, os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
            self.handles[name + "-map:" + address] = fd
            _hash_file(fd, files[path], deadline)
            if not os.fstatvfs(fd).f_flag & os.ST_RDONLY:
                raise ValueError("actual build mapped image remains writable")

    def _compile_policy(
        self, build: FrozenHelperBuild, setup: OwnedCgroup, deadline: float
    ) -> None:
        if self._policy_attempted:
            raise ValueError("original policy compilation attempt consumed; no retry")
        self._policy_attempted = True
        policy = build.policy_build
        if policy is None or deadline != self._build_deadline:
            raise ValueError("original frozen policy recipe or shared interval differs")
        parser, source = _open_path(policy.parser), _open_path(policy.source)
        self.handles["policy-parser"], self.handles["policy-source"] = parser, source
        _hash_file(parser, policy.parser_sha256, deadline)
        _hash_file(source, policy.source_sha256, deadline)
        if not os.fstatvfs(source).f_flag & os.ST_RDONLY:
            raise ValueError("original immutable policy source filesystem remains writable")
        for path, expected in {**policy.files, **policy.include_files}.items():
            fd = _open_path(path)
            self.handles["policy-input:" + path] = fd
            _hash_file(fd, expected, deadline)
            if not os.fstatvfs(fd).f_flag & os.ST_RDONLY:
                raise ValueError("original policy input or runtime remains writable")
        output = self.handles["build-output:policy.binary"]
        self._run_build_process(
            "policy",
            parser,
            source,
            policy.argv,
            policy.environment,
            setup,
            deadline,
            policy.files,
            stdout_output=output,
        )
        policy_hash = _output_digest(output, deadline)
        audit = policy.audit_template.model_copy(update={"policy_binary_sha256": policy_hash})
        self.derived_storage_audit = audit
        self._audit_bytes = audit.model_dump_json().encode()
        if len(self._audit_bytes) > 65536:
            raise ValueError("original derived audit exceeds the fixed control bound")
        assert self.observer is not None and self.reservation is not None and self.timer is not None
        self.build_audit_jobs = BoundedStorageJobs(
            self.observer,
            self.reservation.observer_group,
            self.reservation.aggregate,
            deadline,
            execution_group=setup,
            batch_timer=self.timer,
        )
        if (
            self.build_audit_jobs.run(
                self._write_derived_audit_child, {self.handles["build-output:storage-audit.json"]}
            )
            != b"derived-audit-written"
        ):
            raise ValueError("original derived audit write remains partial")
        for path, expected in {**policy.files, **policy.include_files}.items():
            _hash_file(self.handles["policy-input:" + path], expected, deadline)

    def _write_derived_audit_child(self) -> bytes:
        resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
        fd = self.handles["build-output:storage-audit.json"]
        writer = os.open("/proc/self/fd/" + str(fd), os.O_WRONLY | os.O_CLOEXEC)
        original, current = os.fstat(fd), os.fstat(writer)
        if (original.st_dev, original.st_ino) != (
            current.st_dev,
            current.st_ino,
        ) or current.st_size != 0:
            raise ValueError("original audit output inode differs before its first write")
        if os.write(writer, self._audit_bytes) != len(self._audit_bytes):
            raise ValueError("original derived audit write remains partial")
        os.fsync(writer)
        return b"derived-audit-written"

    def _bind_compiled_helper(self) -> None:
        """Derive actual helper identities under the original observer and charge."""
        descriptor = self.handles.get("compiled-helper-output")
        if descriptor is None:
            descriptor = _open_path(self.inputs.helper)
            self.handles["compiled-helper-output"] = descriptor
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or not info.st_mode & 0o111
            or not 0 < info.st_size <= 1048576
        ):
            raise ValueError("actual bounded executable compiler output unavailable")
        sha, offset = hashlib.sha256(), 0
        while offset < info.st_size:
            if time.monotonic() >= self.origin + 120:
                raise ValueError("original compiler binding deadline exhausted")
            chunk = os.pread(descriptor, min(65536, info.st_size - offset), offset)
            if not chunk:
                raise ValueError("actual compiler output read incomplete")
            sha.update(chunk)
            offset += len(chunk)
        actual = sha.hexdigest()
        _hash_file(descriptor, actual, self.origin + 120)
        if self.inputs.sources.get("/bin/crewshal-bootstrap") != self.inputs.helper:
            raise ValueError("compiled helper and copied root source differ")
        payload = self.inputs.inventory.model_dump(mode="json")
        payload["root"]["/bin/crewshal-bootstrap"]["sha256"] = actual
        payload["helper_libraries"]["/bin/crewshal-bootstrap"] = actual
        audit = None
        if (
            self.inputs.helper_build is not None
            and self.inputs.helper_build.policy_build is not None
        ):
            audit = self.derived_storage_audit
            policy_hash = _output_digest(
                self.handles["build-output:policy.binary"], self.origin + 120
            )
            audit_hash = _output_digest(
                self.handles["build-output:storage-audit.json"], self.origin + 120
            )
            if audit.policy_binary_sha256 != policy_hash:
                raise ValueError("derived policy and original output bytes differ")
            payload["root"]["/opt/crewshal/storage-audit/policy.binary"]["sha256"] = policy_hash
            payload["root"]["/opt/crewshal/storage-audit.json"]["sha256"] = audit_hash
        inventory = audit_parent_inventory(TrustedParentInventory.model_validate(payload))
        configuration = self.inputs.configuration.model_dump(mode="json")
        if configuration["linux_envelope"] is None:
            raise ValueError("compiled helper requires explicit original envelope bindings")
        bindings = configuration["linux_envelope"]
        bindings["parent_inventory_sha256"] = record_digest(inventory)
        bindings["root_inventory_sha256"] = root_inventory_digest(inventory)
        bindings["helper_library_inventory_sha256"] = helper_library_inventory_digest(inventory)
        bindings["bootstrap_policy_sha256"] = record_digest(bootstrap_policy(actual))
        if audit is not None:
            bindings["storage_policy_sha256"] = record_digest(audit)
        final_configuration = DispatchConfiguration.model_validate(configuration)
        payload = self.inputs.model_dump(mode="json")
        payload["inventory"] = inventory.model_dump(mode="json")
        payload["configuration"] = final_configuration.model_dump(mode="json")
        payload["bootstrap"] = prepare_linux_bootstrap(
            final_configuration, helper_binary=actual
        ).model_dump(mode="json")
        self.inputs = FrozenInstallationInputs.model_validate_json(json.dumps(payload))
        self._input_payload = self.inputs.model_dump_json()

    def _load_frozen_policy_child(self) -> bytes:
        """The add interface refuses existing names; no replacement interface is used."""
        from crewshal.linux_payload_storage import PROFILE_NAMES, _require_apparmorfs

        namespace = self.handles["apparmor-namespace"]
        _require_apparmorfs(namespace)
        revision = RetainedAppArmorExport._revision(namespace)
        profiles = os.open("profiles", DIRECTORY_FLAGS, dir_fd=namespace)
        try:
            for directory in os.listdir(profiles):
                profile = os.open(directory, DIRECTORY_FLAGS, dir_fd=profiles)
                try:
                    if _read(profile, "name", 256).strip().decode() in PROFILE_NAMES:
                        raise ValueError(
                            "frozen storage profile already exists; replacement refuses"
                        )
                finally:
                    os.close(profile)
        finally:
            os.close(profiles)
        if RetainedAppArmorExport._revision(namespace) != revision:
            raise ValueError("actual AppArmor namespace changed before absent policy load")
        fd = self.handles["installed-compiled-policy"]
        data = os.pread(fd, 1048577, 0)
        if not data or len(data) > 1048576:
            raise ValueError("frozen installed policy binary exceeds build output bound")
        build = self.inputs.helper_build
        if build is None or build.policy_build is None:
            raise ValueError("original policy installation has no frozen build derivation")
        _hash_file(fd, self.derived_storage_audit.policy_binary_sha256, self.origin + 120)
        if os.write(self.handles["apparmor-load"], data) != len(data):
            raise ValueError("original frozen policy load remains partial")
        return b"loaded-frozen-absent-policy"

    def _retain_installed_policy_roles(self) -> tuple[tuple[str, str], ...]:
        """Pin actual kernel directory identities for the frozen profile names."""
        from crewshal.linux_payload_storage import PROFILE_NAMES, _require_apparmorfs

        if hasattr(self, "_policy_roles_attempted"):
            raise ValueError("original installed policy directory discovery consumed")
        self._policy_roles_attempted = True
        namespace = self.handles["apparmor-namespace"]
        _require_apparmorfs(namespace)
        revision = RetainedAppArmorExport._revision(namespace)
        profiles = os.open("profiles", DIRECTORY_FLAGS, dir_fd=namespace)
        self.handles["installed-policy-profiles"] = profiles
        found: dict[str, str] = {}
        requested = dict(self.inputs.apparmor_roles)
        if set(requested) != set(PROFILE_NAMES):
            raise ValueError("all four frozen original storage profile names required")
        directories = os.listdir(profiles)
        if len(directories) > 32768:
            raise ValueError("original kernel policy directory inventory exceeds bound")
        for directory in directories:
            if time.monotonic() >= self.origin + 120:
                raise ValueError("original installed policy directory deadline exhausted")
            if re.fullmatch(r"[A-Za-z0-9_.-]+", directory) is None:
                raise ValueError("kernel policy directory name is not canonical")
            if not any(
                directory == selected or directory.startswith(name + ".")
                for name, selected in requested.items()
            ):
                continue
            fd = os.open(directory, DIRECTORY_FLAGS, dir_fd=profiles)
            self.handles["installed-policy-directory:" + directory] = fd
            _require_apparmorfs(fd)
            name = _read(fd, "name", 256).strip().decode("ascii")
            if name in requested:
                if name in found or requested[name] not in {name, directory}:
                    raise ValueError("actual installed policy name or unique directory differs")
                found[name] = directory
        if (
            set(found) != set(PROFILE_NAMES)
            or RetainedAppArmorExport._revision(namespace) != revision
        ):
            raise ValueError("original installed policy directories remain unknown or changed")
        roles = tuple((name, found[name]) for name, _ in self.inputs.apparmor_roles)
        self._installed_policy_roles = roles
        return roles

    def __reduce__(self) -> NoReturn:
        raise TypeError("original installation driver cannot be copied or exported")

    def _control(self, directory: int, name: str, value: str) -> None:
        descriptor = os.open(name, os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode) or os.write(
                descriptor, value.encode()
            ) != len(value):
                raise ValueError("original cgroup control write incomplete")
        finally:
            os.close(descriptor)

    def _group(self, parent: int, name: str, relative: str, memory: int, tasks: int) -> OwnedCgroup:
        os.mkdir(name, 0o700, dir_fd=parent)
        descriptor = os.open(name, DIRECTORY_FLAGS, dir_fd=parent)
        self.handles["cgroup:" + relative] = descriptor
        for control, value in (
            ("memory.max", str(memory)),
            ("memory.swap.max", "0"),
            ("pids.max", str(tasks)),
            ("cpu.max", "100000 100000"),
        ):
            self._control(descriptor, control, value)
        info = os.fstat(descriptor)
        group = OwnedCgroup.attach(
            CgroupIdentity(relative_path=relative, device=info.st_dev, inode=info.st_ino)
        )
        self.groups[name] = group
        return group

    def _retain_observer(self, group: OwnedCgroup) -> RetainedTrustedTask:
        descriptor = os.open("/proc/self", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        self.handles["observer-proc"] = descriptor
        pid, _, parent, ticks = _stat_identity(_read(descriptor, "stat"))
        fields = _fields(_read(descriptor, "status"))
        namespaces = {}
        for name in ("mnt", "net", "pid", "user", "time"):
            info = os.stat("ns/" + name, dir_fd=descriptor)
            namespaces[name] = NamespaceIdentity(device=info.st_dev, inode=info.st_ino)
        executable = os.open("exe", os.O_RDONLY | os.O_CLOEXEC, dir_fd=descriptor)
        self.handles["observer-executable"] = executable
        info = os.fstat(executable)
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= 1073741824:
            raise ValueError("original observer executable exceeds bound")
        sha, offset = hashlib.sha256(), 0
        while offset < info.st_size:
            if time.monotonic() >= self.origin + 120:
                raise ValueError("original observer startup deadline exhausted")
            chunk = os.pread(executable, min(65536, info.st_size - offset), offset)
            if not chunk:
                raise ValueError("original observer executable read incomplete")
            sha.update(chunk)
            offset += len(chunk)
        argv = _read(descriptor, "cmdline").split(b"\0")
        if not argv or argv[-1] != b"" or _read(descriptor, "environ"):
            raise ValueError(
                "original observer requires exact argv and empty inherited environment"
            )
        boot = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
        spec = TrustedTaskSpec(
            configuration=record_digest(self.inputs.configuration),
            pid=pid,
            parent_pid=parent,
            start_ticks=ticks,
            boot_id=boot,
            cgroup=group.identity,
            namespaces=namespaces,
            executable=sha.hexdigest(),
            argv=[value.decode() for value in argv[:-1]],
            environment={},
            capabilities=fields["CapEff"],
            cwd="/",
            placement="outer_observer",
        )
        return RetainedTrustedTask.attach(spec)

    def install(self) -> None:
        """Run actual finite constructors. Do not accept caller readiness claims."""
        if self.attempted or self.failed:
            raise ValueError("original installation attempt consumed; no retry")
        self.attempted = True
        try:
            if self.inputs.model_dump_json() != self._input_payload or self.origin != self._origin:
                raise ValueError("original frozen installation inputs or origin changed")
            if (
                None if self.fixture is None else self.fixture.model_dump_json()
            ) != self._fixture_payload:
                raise ValueError("original frozen fixture input changed")
            if sys.platform != "linux" or os.getuid() != 0 or os.getgid() != 0 or os.environ:
                raise ValueError(
                    "approved Linux root entry requires an empty inherited environment"
                )
            if self.inputs.configuration.lane_id is not None:
                raise ValueError("installation requires the original common configuration")
            audit_linux_bootstrap(self.inputs.configuration, self.inputs.bootstrap)
            inventory = audit_parent_inventory(self.inputs.inventory)
            self.inputs.verify_formatter_inventory()
            expected = {name for name, entry in inventory.root.items() if entry.kind == "file"}
            if set(self.inputs.sources) != expected:
                raise ValueError("frozen input sources differ from complete root inventory")
            os.chdir("/")
            os.setgroups([])
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.prctl(38, 1, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), "original observer no-new-privileges refused")
            _, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            if hard != resource.RLIM_INFINITY and hard < 1073741824:
                raise ValueError(
                    "original observer cannot inherit the fixed preparation file ceiling"
                )
            resource.setrlimit(resource.RLIMIT_FSIZE, (1073741824, 1073741824))
            parent = _open_path("/sys/fs/cgroup/" + self.inputs.cgroup_parent, directory=True)
            self.handles["cgroup-parent"] = parent
            enabled = set(_read(parent, "cgroup.subtree_control").decode().split())
            if not {"memory", "pids", "cpu"} <= enabled:
                raise ValueError(
                    "owner-prepared cgroup parent lacks memory, pids, or CPU delegation"
                )
            relative = self.inputs.cgroup_parent + "/" + self.inputs.batch_leaf
            aggregate = self._attach_original_group(relative, self.inputs.batch_leaf)
            observer_path = relative + "/" + self.inputs.observer_name
            observer_group = self._attach_original_group(observer_path, self.inputs.observer_name)
            if any(
                aggregate._read(name) != value
                for name, value in (
                    ("memory.max", "805306368"),
                    ("memory.swap.max", "0"),
                    ("pids.max", "128"),
                    ("cpu.max", "100000 100000"),
                )
            ):
                raise ValueError("owner-prepared original aggregate controls differ")
            observer_group.sample()
            with open("/proc/self/cgroup", "rb") as stream:
                current_group = stream.read(4097)
            if current_group != f"0::/{observer_path}\n".encode():
                raise ValueError("observer must start in its original bounded role before Python")
            if not {"memory", "pids", "cpu"} <= set(
                aggregate._read("cgroup.subtree_control").split()
            ):
                raise ValueError("original aggregate lacks delegated lane controllers")
            self.observer = self._retain_observer(observer_group)
            journal = Path(self.inputs.journal)
            if journal.exists():
                raise ValueError("original installation requires a new exclusive journal directory")
            self.handles["journal-parent"] = _open_path(str(journal.parent), directory=True)
            self.store = CoordinatorStore(journal)
            self.reservation = reserve_storage_installation(
                self.store,
                self.observer,
                observer_group,
                aggregate,
                self.inputs.configuration,
                batch_started_monotonic=self.origin,
            )
            if hasattr(self.reservation, "_installation_driver"):
                raise ValueError(
                    "original storage reservation already belongs to its installation driver"
                )
            self.reservation._installation_driver = self
            if self.attempt_marker is not None:
                from crewshal.linux_attempt import consume_original_marker

                consume_original_marker(self, self.attempt_marker)
            roles = {
                lane: {
                    role: self._group(
                        aggregate.descriptor,
                        role + "--" + lane,
                        relative + "/" + role + "--" + lane,
                        805306368 if role in ("setup", "supervisor") else 134217728,
                        128 if role in ("setup", "supervisor") else 32,
                    )
                    for role in ROLES
                }
                for lane in LANES
            }
            self._group(aggregate.descriptor, "broker", relative + "/broker", 67108864, 16)
            if self.inputs.early_timer is None:
                raise ValueError("original operational entry requires the sole early batch timer")
            self.timer = create_owned_early_batch_timer(
                self.reservation, roles, self.groups["broker"], self.inputs.early_timer
            )
            if self.inputs.helper_build is not None:
                initial_inputs = self.inputs
                if (
                    self.inputs.configuration.linux_envelope is None
                    or self.inputs.configuration.linux_envelope.build_recipe_sha256
                    != record_digest(self.inputs.helper_build)
                ):
                    raise ValueError("original charge requires the exact immutable helper recipe")
                if self.inputs.helper_build.policy_build is None:
                    raise ValueError(
                        "operational installation requires the complete frozen policy build recipe"
                    )
                self._charged_build_input_payload = initial_inputs.model_dump_json()
                if self.inputs.helper_build.volume_constructor is not None:
                    if self.inputs.helper_build.loop_device != "/dev/loop-control":
                        raise ValueError(
                            "fresh compiler volume requires its frozen original loop allocator"
                        )
                    OriginalCompilerVolume(
                        self, self.inputs.helper_build, roles["qualification-1"]["setup"]
                    ).create()
                self._compile_helper(self.inputs.helper_build, roles["qualification-1"]["setup"])
                self._bind_compiled_helper()
                from crewshal.linux_charged_build import RetainedBuildDerivation

                self.build_derivation = RetainedBuildDerivation.bind(self, initial_inputs)
                inventory = audit_parent_inventory(self.inputs.inventory)
            self.lanes = reserve_lane_setups(self.reservation, roles)
            helper = _open_path(self.inputs.helper)
            self.handles["helper"] = helper
            if self.inputs.bootstrap.policy.helper_binary is None:
                raise ValueError("frozen compiled helper identity is missing")
            _hash_file(helper, self.inputs.bootstrap.policy.helper_binary, self.origin + 120)
            first = self.lanes[0]
            formatter = _open_path(self.inputs.formatter)
            self.handles["formatter"] = formatter
            _hash_file(formatter, self.inputs.formatter_sha256, self.origin + 120)
            sources = {}
            for name, host_path in self.inputs.sources.items():
                descriptor = _open_path(host_path)
                self.handles["source:" + name] = descriptor
                expected_hash = inventory.root[name].sha256
                assert expected_hash is not None
                _hash_file(descriptor, expected_hash, self.origin + 120)
                sources[name] = descriptor
            installation_parent = _open_path(self.inputs.installation_parent, directory=True)
            self.handles["installation-parent"] = installation_parent
            jobs = BoundedStorageJobs(
                self.observer,
                observer_group,
                aggregate,
                self.origin + 120,
                execution_group=first.setup,
                batch_timer=self.timer,
            )
            self.production = OwnedBackingProduction(
                self.reservation, None, jobs, installation_parent_fd=installation_parent
            )
            self.production.prepare_directory()
            self.production.install_physical_domain(inventory, formatter)
            self.production.create()
            self.production.create_auxiliary_backings()
            self.production.copy_root(inventory, sources)
            self.production.project_readonly_root()
            self.production.format_filesystems()
            self.ring = AnonymousKeyring.create(reservation=self.reservation)
            self.keys = PrivateEcryptfsKeys(self.reservation, self.ring)
            self.keys.create()
            self.production.mount_encrypted_views(self.keys)
            self.production.handoff_storage_owner()
            if self.fixture is not None:
                from crewshal.linux_fixture_inputs import (
                    OriginalFixtureInputs,
                    SyntheticQualificationAccount,
                    rebind_fixture_configuration,
                )

                rebound = rebind_fixture_configuration(self.fixture, self)
                self.fixture_inputs = OriginalFixtureInputs.seed(
                    self.production, rebound, SyntheticQualificationAccount()
                )
            if self.inputs.apparmor_namespace != "/sys/kernel/security/apparmor/policy":
                raise ValueError("original current AppArmor namespace interface required")
            apparmor_parent = _open_path("/sys/kernel/security/apparmor", directory=True)
            self.handles["apparmor-parent"] = apparmor_parent
            # This exact kernel interface is a magic link. The retained policy
            # reader verifies AppArmorfs and the current namespace independently.
            apparmor = os.open(
                "policy", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=apparmor_parent
            )
            self.handles["apparmor-namespace"] = apparmor
            proc = _open_path("/proc", directory=True)
            self.handles["host-proc"] = proc
            sysfs = _open_path("/sys", directory=True)
            self.handles["host-sysfs"] = sysfs
            slab_parent = _open_path("/sys/kernel/slab", directory=True)
            self.handles["kernel-slab-parent"] = slab_parent
            # The kernel can expose a merged cache through this exact alias.
            # The retainer independently checks sysfs and the cache identity.
            inode_cache = os.open(
                "shmem_inode_cache",
                os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC,
                dir_fd=slab_parent,
            )
            self.handles["shmem-inode-cache"] = inode_cache
            projected = self.production.projected_inventory
            projected.verify()
            policy_fd = _open_path(
                "/opt/crewshal/storage-audit/policy.binary", root_fd=projected.descriptor
            )
            self.handles["installed-compiled-policy"] = policy_fd
            load_fd = os.open(
                ".load", os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=apparmor_parent
            )
            self.handles["apparmor-load"] = load_fd
            if (
                jobs.run(
                    self._load_frozen_policy_child, {apparmor, apparmor_parent, policy_fd, load_fd}
                )
                != b"loaded-frozen-absent-policy"
            ):
                raise ValueError("original bounded policy installation result differs")
            policy_info = os.fstat(policy_fd)
            if not stat.S_ISREG(policy_info.st_mode) or not 0 < policy_info.st_size <= 2097152:
                raise ValueError("installed compiled storage policy exceeds bound")
            compiled_policy = os.pread(policy_fd, policy_info.st_size + 1, 0)
            if len(compiled_policy) != policy_info.st_size:
                raise ValueError("installed compiled storage policy read incomplete")
            self.production.retain_payload_storage(
                apparmor,
                compiled_policy,
                self._retain_installed_policy_roles(),
                proc,
                sysfs,
                inode_cache,
            )
            self.installation = self.production.complete_installation()
            self.reservation.verify_installation()
        except BaseException as error:
            self.failed = True
            if self.reservation is not None:
                self.reservation._retain_installation_refusal(error)
            raise OperationalRefusal(str(error), self) from error
