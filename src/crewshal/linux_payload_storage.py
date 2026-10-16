"""Retain reviewed storage inputs and read actual compatible enforcement.

The source audit binds the original readonly root and exact kernel build.
Independent readback checks loaded policy bytes, inode geometry, and files.
Linux qualification and live acceptance remain separate required gates.
This module does not compile, load policy, launch processes, or release charges.
"""

import ctypes
from dataclasses import dataclass
import fcntl
import hashlib
import os
from pathlib import PurePosixPath
import re
import stat
import struct
import sys
from typing import TYPE_CHECKING, Literal, NoReturn

from pydantic import Field

from crewshal.contracts import Digest, record_digest
from crewshal.model import Contract, digest

if TYPE_CHECKING:
    from crewshal.linux_inventory import RetainedParentInventory
    from crewshal.linux_production import OwnedBackingProduction
    from crewshal.linux_setup import OwnedStorageReservation

AUDIT_PATH = "/opt/crewshal/storage-audit.json"
AUDIT_PROFILE: Literal["reviewed_zero_data_scaffold_inode147_embedded_memcg_v2"] = (
    "reviewed_zero_data_scaffold_inode147_embedded_memcg_v2"
)
AUDIT_SOURCE_NAMES = (
    "kernel/mm/shmem.c",
    "kernel/include/linux/shmem_fs.h",
    "kernel/fs/dcache.c",
    "kernel/mm/slub.c",
    "kernel/mm/memcontrol.c",
    "kernel/mm/slab.h",
    "kernel/mm/slab_common.c",
    "kernel/fs/inode.c",
    "kernel/include/linux/fs.h",
    "kernel/include/linux/memcontrol.h",
    "kernel/mm/page_counter.c",
    "kernel/kernel/cgroup/cgroup.c",
    "kernel/security/apparmor/apparmorfs.c",
    "kernel/security/apparmor/policy.c",
    "vendor/codex-rs/linux-sandbox/src/bwrap.rs",
    "vendor/codex-rs/linux-sandbox/src/bundled_bwrap.rs",
    "vendor/codex-rs/core/src/tools/handlers/apply_patch.rs",
    "vendor/codex-rs/core/src/tools/runtimes/apply_patch.rs",
    "vendor/codex-rs/core/src/tools/handlers/view_image.rs",
    "vendor/bubblewrap/bubblewrap.c",
    "vendor/bubblewrap/utils.c",
    "policy/parser/parser_main.c",
)


APPARMORFS_MAGIC = 0x5A3C69F0
POLICY_LIMIT = 2_097_152
PROCFS_MAGIC = 0x9FA0
SYSFS_MAGIC = 0x62656572
CGROUP2_MAGIC = 0x63677270
PROFILE_NAMES = (
    "crewshal-2d-native-storage-v1",
    "crewshal-2d-bwrap-storage-v1",
    "crewshal-2d-tool-storage-v1",
    "crewshal-2d-validator-storage-v1",
)

# The native and vendor setup roles execute only pinned trusted code. Explicit
# native setup paths permit stock bubblewrap scaffold creation after its pivot.
# Payload tools receive the restrictive stacked role at the first command exec.
# This proposal needs actual transition and complete growth qualification.
PROPOSED_POLICY = b"""abi <abi/4.0>,

profile crewshal-2d-native-storage-v1 flags=(chroot_relative,attach_disconnected) {
  userns,
  capability,
  network,
  mount,
  umount,
  pivot_root,
  signal,
  ptrace,
  / r,
  /** rm,
  /candidate/owned/ rwkm,
  /candidate/owned/** rwkm,
  /scratch/ rwkm,
  /scratch/** rwkm,
  /native-auth/ rwkm,
  /native-auth/** rwkm,
  /dev/null rw,
  /tmp/ rwkm,
  /tmp/** rwkm,
  /newroot/ rwkm,
  /newroot/** rwkm,
  /bindfile* rwkm,
  /oldroot/{scratch,candidate/owned}/ rwkm,
  /oldroot/{scratch,candidate/owned}/** rwkm,
  /proc/*/{uid_map,gid_map,setgroups} rw,
  /proc/sys/user/max_user_namespaces rw,
  deny /dev/zero rwklm,
  /opt/codex/codex-resources/bwrap Px -> "crewshal-2d-native-storage-v1//&crewshal-2d-bwrap-storage-v1",
  /{bin,usr/bin}/** ix,
  /opt/codex/bin/codex ix,
  /opt/codex/codex-resources/codex-linux-sandbox ix,
}

profile crewshal-2d-bwrap-storage-v1 flags=(chroot_relative,attach_disconnected) {
  userns,
  capability,
  network,
  mount,
  umount,
  pivot_root,
  signal,
  ptrace,
  / r,
  /** rwklm,
  deny /dev/zero rwklm,
  /** Px -> "crewshal-2d-native-storage-v1//&crewshal-2d-bwrap-storage-v1//&crewshal-2d-tool-storage-v1",
}

profile crewshal-2d-tool-storage-v1 flags=(chroot_relative) {
  deny userns,
  deny capability,
  deny mount,
  deny umount,
  deny pivot_root,
  / r,
  /** rm,
  deny /dev/zero rwklm,
  deny /native-auth/** rwklm,
  /candidate/owned/ rwkm,
  /candidate/owned/** rwkm,
  /scratch/ rwkm,
  /scratch/** rwkm,
  /dev/null rw,
  /** ix,
  network unix,
  signal (send, receive) peer=crewshal-2d-tool-storage-v1,
  signal (receive) peer=unconfined,
  signal (receive) peer=crewshal-2d-native-storage-v1,
  signal (receive) peer=crewshal-2d-bwrap-storage-v1,
  ptrace (readby) peer=unconfined,
}

profile crewshal-2d-validator-storage-v1 flags=(chroot_relative) {
  deny userns,
  deny capability,
  deny mount,
  deny umount,
  deny pivot_root,
  / r,
  /** rm,
  deny /dev/zero rwklm,
  deny /native-auth/** rwklm,
  /scratch/ rwkm,
  /scratch/** rwkm,
  /dev/null rw,
  /** ix,
  network unix,
  signal (send, receive) peer=crewshal-2d-validator-storage-v1,
  signal (receive) peer=unconfined,
  ptrace (readby) peer=unconfined,
}
"""

UNRESOLVED = (
    "exact_policy_parser_binary_and_source_to_binary_provenance",
    "actual_no_new_privs_native_bwrap_tool_stacked_transitions",
    "all_zero_device_aliases_and_inherited_descriptor_exclusion",
    "legacy_mknod_and_vendor_setup_device_creation_compatibility",
    "trusted_native_and_bwrap_scaffold_logical_and_allocated_growth_bounds",
    "actual_target_kernel_source_resident_inode_and_inline_symlink_geometry",
    "exact_vendor_source_to_binary_and_no_data_bearing_scaffold_route",
    "compatible_shared_anonymous_mapping_filter_and_effective_readback",
    "every_enabled_native_file_tool_and_twenty_original_cases_twice",
)


def proposed_policy() -> tuple[bytes, Digest, tuple[str, ...]]:
    """Return source data and explicit missing checks without loading policy."""
    return PROPOSED_POLICY, digest(PROPOSED_POLICY), UNRESOLVED


def _identity(descriptor: int) -> tuple[int, int]:
    value = os.fstat(descriptor)
    if not stat.S_ISDIR(value.st_mode):
        raise ValueError("retained AppArmor policy directory differs")
    return value.st_dev, value.st_ino


def _require_apparmorfs(descriptor: int) -> None:
    _require_filesystem(descriptor, APPARMORFS_MAGIC)


def _require_filesystem(descriptor: int, expected: int) -> None:
    if sys.platform != "linux" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise ValueError("actual AppArmor policy filesystem readback unavailable")
    # Linux statfs begins with a native long filesystem type. Reserve more than
    # the supported 64-bit structure so the kernel cannot overrun this buffer.
    buffer = ctypes.create_string_buffer(256)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.fstatfs(ctypes.c_int(descriptor), ctypes.byref(buffer)):
        raise OSError(ctypes.get_errno(), "AppArmor policy filesystem readback failed")
    if ctypes.c_ulong.from_buffer(buffer).value != expected:
        raise ValueError("retained source filesystem type differs")


def _read(descriptor: int, path: str, limit: int, *, follow: bool = False) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | (0 if follow else os.O_NOFOLLOW)
    value = os.open(path, flags, dir_fd=descriptor)
    try:
        _require_apparmorfs(value)
        data = bytearray()
        while len(data) <= limit:
            try:
                part = os.read(value, min(65_536, limit + 1 - len(data)))
            except BlockingIOError:
                if not data:
                    raise
                break
            if not part:
                break
            data += part
        if len(data) > limit:
            raise ValueError("actual AppArmor policy export exceeds its bound")
        return bytes(data)
    finally:
        os.close(value)


@dataclass(frozen=True)
class AppArmorExportObservation:
    namespace_identity: tuple[int, int]
    namespace_revision: int
    binary_sha256: Digest
    role_identities: tuple[tuple[str, tuple[int, int]], ...]
    process_label: str


@dataclass(frozen=True)
class RetainedAppArmorExport:
    """Read current roles through one original namespace FD on every check.

    The original export FD remains readable after the parent drops privilege.
    Current role targets and the namespace revision detect obsolete exports.
    A label, pathname, hash file, or loader exit alone cannot pass this check.
    """

    namespace: int
    namespace_identity: tuple[int, int]
    namespace_revision: int
    expected_binary: bytes
    roles: tuple[tuple[str, str, tuple[int, int]], ...]
    raw_export: int
    raw_export_identity: tuple[int, int]

    @classmethod
    def retain(
        cls,
        namespace: int,
        expected_binary: bytes,
        roles: tuple[tuple[str, str], ...],
    ) -> "RetainedAppArmorExport":
        if not roles:
            raise ValueError("bounded compiled AppArmor policy and exact roles required")
        directory = roles[0][1]
        if re.fullmatch(r"[A-Za-z0-9_.-]+", directory) is None:
            raise ValueError("exact AppArmor role directory required")
        raw_export = os.open(
            "profiles/" + directory + "/raw_data",
            os.O_RDONLY | os.O_CLOEXEC,
            dir_fd=namespace,
        )
        # Retain the actual export on refusal. The original owner keeps custody.
        return cls.retain_inherited(namespace, expected_binary, roles, raw_export)

    @classmethod
    def retain_inherited(
        cls,
        namespace: int,
        expected_binary: bytes,
        roles: tuple[tuple[str, str], ...],
        raw_export: int,
    ) -> "RetainedAppArmorExport":
        if (
            not isinstance(expected_binary, bytes)
            or not expected_binary
            or len(expected_binary) > POLICY_LIMIT
            or not roles
        ):
            raise ValueError("bounded compiled AppArmor policy and exact roles required")
        if len(roles) != len({name for name, _ in roles}):
            raise ValueError("duplicate AppArmor role")
        _require_apparmorfs(namespace)
        revision = cls._revision(namespace)
        identities = []
        for name, directory in roles:
            if name not in PROFILE_NAMES or re.fullmatch(r"[A-Za-z0-9_.-]+", directory) is None:
                raise ValueError("exact AppArmor role directory required")
            descriptor = os.open(
                "profiles/" + directory,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=namespace,
            )
            try:
                _require_apparmorfs(descriptor)
                identities.append((name, directory, _identity(descriptor)))
            finally:
                os.close(descriptor)
        retained = cls(
            namespace,
            _identity(namespace),
            revision,
            expected_binary,
            tuple(identities),
            raw_export,
            cls._export_identity(raw_export),
        )
        retained.check_policy()
        return retained

    @staticmethod
    def _export_identity(descriptor: int) -> tuple[int, int]:
        _require_apparmorfs(descriptor)
        value = os.fstat(descriptor)
        if (
            not stat.S_ISREG(value.st_mode)
            or (fcntl.fcntl(descriptor, fcntl.F_GETFL) & os.O_ACCMODE) != os.O_RDONLY
        ):
            raise ValueError("original readonly AppArmor export required")
        return value.st_dev, value.st_ino

    def _read_export(self) -> bytes:
        if self._export_identity(self.raw_export) != self.raw_export_identity:
            raise ValueError("original AppArmor export identity changed")
        result = bytearray()
        while len(result) <= POLICY_LIMIT:
            part = os.pread(
                self.raw_export, min(65_536, POLICY_LIMIT + 1 - len(result)), len(result)
            )
            if not part:
                break
            result += part
        if len(result) > POLICY_LIMIT:
            raise ValueError("actual AppArmor policy export exceeds its bound")
        return bytes(result)

    @staticmethod
    def _revision(namespace: int) -> int:
        raw = _read(namespace, "revision", 32)
        if re.fullmatch(rb"[0-9]{1,19}\n", raw) is None:
            raise ValueError("actual AppArmor namespace revision is malformed")
        return int(raw)

    def check_policy(self) -> None:
        _require_apparmorfs(self.namespace)
        if _identity(self.namespace) != self.namespace_identity or (
            self._revision(self.namespace) != self.namespace_revision
        ):
            raise ValueError("original AppArmor namespace or revision changed")
        for name, directory, identity in self.roles:
            descriptor = os.open(
                "profiles/" + directory,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=self.namespace,
            )
            try:
                _require_apparmorfs(descriptor)
                if _identity(descriptor) != identity:
                    raise ValueError("loaded AppArmor role directory changed")
                if _read(descriptor, "name", 256) != (name + "\n").encode():
                    raise ValueError("loaded AppArmor role name differs")
                if _read(descriptor, "mode", 32) != b"enforce\n":
                    raise ValueError("loaded AppArmor role is not enforcing")
                current = os.stat("raw_data", dir_fd=descriptor, follow_symlinks=True)
                if (
                    not stat.S_ISREG(current.st_mode)
                    or (current.st_dev, current.st_ino) != self.raw_export_identity
                ):
                    raise ValueError("current AppArmor export target differs")
            finally:
                os.close(descriptor)
        if self._read_export() != self.expected_binary:
            raise ValueError("actual loaded AppArmor binary policy differs")
        if self._revision(self.namespace) != self.namespace_revision:
            raise ValueError("AppArmor policy changed during independent readback")

    def check_process(self, proc: int, expected_label: str) -> AppArmorExportObservation:
        self.check_policy()
        if not expected_label or "\n" in expected_label or "\x00" in expected_label:
            raise ValueError("exact enforcing process label required")
        components = expected_label.split("//&")
        retained_names = {name for name, _, _ in self.roles}
        if len(components) != len(set(components)) or any(
            name not in retained_names for name in components
        ):
            raise ValueError("process label does not contain the retained AppArmor roles")
        # This descriptor belongs to the caller's already retained proc handle.
        descriptor = os.open(
            "attr/apparmor/current", os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=proc
        )
        try:
            raw = os.read(descriptor, 4097)
            if len(raw) > 4096 or raw != (expected_label + " (enforce)\n").encode():
                raise ValueError("actual process AppArmor label differs")
        finally:
            os.close(descriptor)
        self.check_policy()
        return AppArmorExportObservation(
            self.namespace_identity,
            self.namespace_revision,
            digest(self.expected_binary),
            tuple((name, identity) for name, _, identity in self.roles),
            expected_label,
        )


def _bounded_source(descriptor: int, path: str, limit: int, filesystem: int) -> bytes:
    value = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=descriptor)
    try:
        _require_filesystem(value, filesystem)
        parts = bytearray()
        while len(parts) <= limit:
            part = os.read(value, min(65_536, limit + 1 - len(parts)))
            if not part:
                break
            parts += part
        if len(parts) > limit:
            raise ValueError("kernel source readback exceeds its bound")
        return bytes(parts)
    finally:
        os.close(value)


def _bounded_source_digest(descriptor: int, path: str, limit: int, filesystem: int) -> Digest:
    """Hash an actual kernel export without two complete resident copies."""
    value = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=descriptor)
    try:
        _require_filesystem(value, filesystem)
        result, size = hashlib.sha256(), 0
        while True:
            part = os.read(value, min(65_536, limit + 1 - size))
            if not part:
                break
            size += len(part)
            if size > limit:
                raise ValueError("kernel source readback exceeds its bound")
            result.update(part)
        if not size:
            raise ValueError("actual target kernel build export is empty")
        return result.hexdigest()
    finally:
        os.close(value)


def _decimal(raw: bytes) -> int:
    if re.fullmatch(rb"[0-9]{1,19}\n", raw) is None:
        raise ValueError("actual kernel numeric readback is malformed")
    return int(raw)


def _btf_struct_sizes(sysfs: int) -> tuple[int, int]:
    """Read actual target type sizes without an external executable."""
    descriptor = os.open(
        "kernel/btf/vmlinux", os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=sysfs
    )
    try:
        _require_filesystem(descriptor, SYSFS_MAGIC)
        raw = os.pread(descriptor, 24, 0)
        if len(raw) != 24:
            raise ValueError("actual kernel BTF header is incomplete")
        magic, version, flags, header, type_offset, type_length, string_offset, string_length = (
            struct.unpack("<HBBIIIII", raw)
        )
        if (
            magic != 0xEB9F
            or version != 1
            or flags
            or header != 24
            or type_offset != 0
            or string_offset != type_length
            or not type_length
            or not string_length
            or header + string_offset + string_length > 67_108_864
        ):
            raise ValueError("actual kernel BTF sections differ")
        # All Linux BTF kinds through ENUM64 have fixed, bounded record shapes.
        shapes = {
            1: (4, 0),
            2: (0, 0),
            3: (12, 0),
            4: (0, 12),
            5: (0, 12),
            6: (0, 8),
            7: (0, 0),
            8: (0, 0),
            9: (0, 0),
            10: (0, 0),
            11: (0, 0),
            12: (0, 0),
            13: (0, 8),
            14: (4, 0),
            15: (0, 12),
            16: (0, 0),
            17: (4, 0),
            18: (0, 0),
            19: (0, 12),
        }
        position, end = header + type_offset, header + type_offset + type_length
        found: dict[str, int] = {}
        cached_start, cached = -1, b""
        while position < end:
            if not cached_start <= position <= cached_start + len(cached) - 12:
                cached_start = position
                cached = os.pread(descriptor, min(65_536, end - position), position)
            record = cached[position - cached_start : position - cached_start + 12]
            if len(record) != 12:
                raise ValueError("actual kernel BTF type record is incomplete")
            name_offset, info, size = struct.unpack("<III", record)
            kind, count = (info >> 24) & 31, info & 65535
            if kind not in shapes:
                raise ValueError("actual kernel BTF type kind is unsupported")
            fixed, repeated = shapes[kind]
            following = position + 12 + fixed + repeated * count
            if following > end:
                raise ValueError("actual kernel BTF type record exceeds its section")
            if kind == 4:
                if name_offset >= string_length:
                    raise ValueError("actual kernel BTF struct name exceeds its section")
                name = os.pread(
                    descriptor,
                    min(256, string_length - name_offset),
                    header + string_offset + name_offset,
                ).split(b"\0", 1)[0]
                if name in (b"slabobj_ext", b"shmem_inode_info"):
                    key = name.decode()
                    if key in found or not 0 < size <= 65_536:
                        raise ValueError("actual kernel BTF inode or extension layout differs")
                    found[key] = size
            position = following
        if position != end or set(found) != {"slabobj_ext", "shmem_inode_info"}:
            raise ValueError("actual kernel BTF inode or extension type is absent")
        return found["slabobj_ext"], found["shmem_inode_info"]
    finally:
        os.close(descriptor)


@dataclass(frozen=True)
class ScaffoldKernelObservation:
    aggregate_identity: tuple[int, int]
    proc_identity: tuple[int, int]
    sysfs_identity: tuple[int, int]
    inode_cache_identity: tuple[int, int]
    memory_bytes: int
    inode_object_bytes: int
    inode_slab_bytes: int
    kernel_release: str
    kernel_notes_sha256: Digest
    kernel_btf_sha256: Digest
    command_line_sha256: Digest
    original_memory_max: int
    original_task_max: int
    conditional_scaffold_logical_bytes: int
    page_bytes: int
    inode_slab_order: int
    slab_extension_bytes: int
    original_legacy_inode_slots: int


@dataclass(frozen=True)
class RetainedScaffoldKernel:
    """Read original controls and actual kernel geometry without granting startup.

    The conditional bound requires qualified vendor setup routes. Those routes
    must create only zero-length files, directories, and cached short symlinks.
    Each inode contributes at most 147 logical bytes, including its parent entry.
    Short symlink targets use separate kernel objects, not filesystem data extents.
    Their targets must contain at most 127 bytes, excluding the terminating zero.
    Actual slab geometry must store accounting extensions inside every new slab.
    The initial cache slot count covers old slabs with missing extensions.
    The original memory limit and exception reserve bound later inode slots.
    Resident kernel inodes cannot use swap. Retained objects remain in the bound.

    Exact target kernel source must prove this geometry and object residency.
    A BTF digest or configuration file alone cannot establish that proof.
    """

    aggregate: int
    aggregate_identity: tuple[int, int]
    proc: int
    proc_identity: tuple[int, int]
    sysfs: int
    sysfs_identity: tuple[int, int]
    inode_cache: int
    inode_cache_identity: tuple[int, int]
    original: ScaffoldKernelObservation

    @classmethod
    def retain(
        cls, aggregate: int, proc: int, sysfs: int, inode_cache: int
    ) -> "RetainedScaffoldKernel":
        identities = tuple(_identity(value) for value in (aggregate, proc, sysfs, inode_cache))
        current = cls._observe(aggregate, proc, sysfs, inode_cache, identities)
        return cls(
            aggregate,
            identities[0],
            proc,
            identities[1],
            sysfs,
            identities[2],
            inode_cache,
            identities[3],
            current,
        )

    @staticmethod
    def _observe(
        aggregate: int,
        proc: int,
        sysfs: int,
        inode_cache: int,
        identities: tuple[tuple[int, int], ...],
        legacy_inode_slots: int | None = None,
    ) -> ScaffoldKernelObservation:
        for value, kind, identity in zip(
            (aggregate, proc, sysfs, inode_cache),
            (CGROUP2_MAGIC, PROCFS_MAGIC, SYSFS_MAGIC, SYSFS_MAGIC),
            identities,
            strict=True,
        ):
            _require_filesystem(value, kind)
            if _identity(value) != identity:
                raise ValueError("original storage kernel source identity changed")
        controls = {
            name: _bounded_source(aggregate, name, 32, CGROUP2_MAGIC)
            for name in ("memory.max", "memory.swap.max", "pids.max", "cgroup.type")
        }
        if controls != {
            "memory.max": b"805306368\n",
            "memory.swap.max": b"0\n",
            "pids.max": b"128\n",
            "cgroup.type": b"domain\n",
        }:
            raise ValueError("original aggregate storage controls differ")
        memory = _bounded_source(proc, "meminfo", 16_384, PROCFS_MAGIC)
        match = re.findall(rb"^MemTotal:[ \t]+([0-9]{1,19}) kB$", memory, re.MULTILINE)
        if len(match) != 1 or int(match[0]) <= 0:
            raise ValueError("actual global physical memory readback differs")
        memory_bytes = int(match[0]) * 1024
        current_cache = os.open(
            "kernel/slab/shmem_inode_cache",
            os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC,
            dir_fd=sysfs,
        )
        try:
            _require_filesystem(current_cache, SYSFS_MAGIC)
            if _identity(current_cache) != identities[3]:
                raise ValueError("actual shmem inode cache identity differs")
        finally:
            os.close(current_cache)
        object_bytes = _decimal(_bounded_source(inode_cache, "object_size", 32, SYSFS_MAGIC))
        slab_bytes = _decimal(_bounded_source(inode_cache, "slab_size", 32, SYSFS_MAGIC))
        if object_bytes < 588 or slab_bytes < object_bytes or slab_bytes > 65_536:
            raise ValueError("actual shmem inode geometry cannot bound resident objects")
        order = _decimal(_bounded_source(inode_cache, "order", 32, SYSFS_MAGIC))
        page_bytes = int(os.sysconf("SC_PAGE_SIZE"))
        extensions, btf_inode_bytes = _btf_struct_sizes(sysfs)
        if (
            page_bytes not in (4096, 16384, 65536)
            or order > 3
            or extensions != 8
            or btf_inode_bytes != object_bytes
            or any(
                ((page_bytes << value) // slab_bytes * slab_bytes + extensions - 1)
                // extensions
                * extensions
                + ((page_bytes << value) // slab_bytes) * extensions
                > page_bytes << value
                for value in range(4)
            )
        ):
            raise ValueError("actual slab geometry cannot preserve embedded memory accounting")
        if legacy_inode_slots is None:
            slots = _bounded_source(inode_cache, "total_objects", 16_384, SYSFS_MAGIC)
            if re.fullmatch(rb"[0-9]{1,19}(?: N[0-9]+=[0-9]+)*\n", slots) is None:
                raise ValueError("actual initial shmem inode slot count differs")
            legacy_inode_slots = int(slots.split()[0])
        if legacy_inode_slots < 0 or legacy_inode_slots * object_bytes > memory_bytes:
            raise ValueError("actual initial shmem inode slots exceed physical memory")
        release = _bounded_source(proc, "sys/kernel/osrelease", 256, PROCFS_MAGIC)
        if re.fullmatch(rb"[A-Za-z0-9_.+~-]{1,255}\n", release) is None:
            raise ValueError("actual kernel release readback differs")
        command_line = _bounded_source(proc, "cmdline", 16_384, PROCFS_MAGIC)
        if b"\x00" in command_line or not command_line.endswith(b"\n"):
            raise ValueError("actual kernel command line readback differs")
        if any(
            token.startswith(b"cgroup_disable=")
            and b"memory" in token
            or token.startswith(b"cgroup.memory=")
            and b"nokmem" in token
            for token in command_line.split()
        ):
            raise ValueError("kernel memory controller accounting is disabled")
        notes = _bounded_source_digest(sysfs, "kernel/notes", 1_048_576, SYSFS_MAGIC)
        btf = _bounded_source_digest(sysfs, "kernel/btf/vmlinux", 67_108_864, SYSFS_MAGIC)
        return ScaffoldKernelObservation(
            identities[0],
            identities[1],
            identities[2],
            identities[3],
            memory_bytes,
            object_bytes,
            slab_bytes,
            release[:-1].decode(),
            notes,
            btf,
            digest(command_line),
            805_306_368,
            128,
            legacy_inode_slots * 147
            + ((805_306_368 + 128 * 262_144) * 147 + object_bytes - 1) // object_bytes,
            page_bytes,
            order,
            extensions,
            legacy_inode_slots,
        )

    def check(self) -> ScaffoldKernelObservation:
        current = self._observe(
            self.aggregate,
            self.proc,
            self.sysfs,
            self.inode_cache,
            (
                self.aggregate_identity,
                self.proc_identity,
                self.sysfs_identity,
                self.inode_cache_identity,
            ),
            self.original.original_legacy_inode_slots,
        )
        if current != self.original:
            raise ValueError("retained storage kernel geometry or build changed")
        return current


class StorageSourceAudit(Contract):
    """Frozen source review inputs, bound before the original reservation.

    The review record must explain every permitted stock setup route, inode
    geometry, resident kernel allocation, and original exception allowance.
    This record alone grants no admission. The producer must match installed
    files, loaded policy, running kernel exports, and retained physical custody.
    """

    schema_version: Literal[2] = 2
    review_profile: Literal["reviewed_zero_data_scaffold_inode147_embedded_memcg_v2"] = (
        AUDIT_PROFILE
    )
    review_record_sha256: Digest
    policy_source_sha256: Digest
    policy_binary_sha256: Digest
    policy_parser_executable_sha256: Digest
    policy_parser_package_record_sha256: Digest
    native_release: Literal["0.160.1"] = "0.160.1"
    native_source_ref: Literal["rust-v0.160.1"] = "rust-v0.160.1"
    native_executable_sha256: Digest
    native_sandbox_sha256: Digest
    bubblewrap_release: Literal["0.11.0"] = "0.11.0"
    bubblewrap_executable_sha256: Digest
    kernel_package: str = Field(min_length=1, max_length=256, pattern=r"^[A-Za-z0-9_.+~-]+$")
    kernel_package_record_sha256: Digest
    kernel_release: str = Field(min_length=1, max_length=255, pattern=r"^[A-Za-z0-9_.+~-]+$")
    kernel_notes_sha256: Digest
    kernel_btf_sha256: Digest
    source_files: dict[str, Digest]


@dataclass(frozen=True)
class RetainedAuditFile:
    path: str
    descriptor: int
    metadata: tuple[int, ...]
    sha256: Digest


def _vendor_target(path: str, target: str) -> str:
    """Resolve one inventoried alias inside the original readonly root."""
    link = PurePosixPath(target)
    parts = [] if link.is_absolute() else list(PurePosixPath(path).parent.parts[1:])
    for name in link.parts:
        if name in ("/", "."):
            continue
        if name == "..":
            if not parts:
                raise ValueError("audited vendor alias escapes the original root")
            parts.pop()
        else:
            parts.append(name)
    return "/" + "/".join(parts)


def _audit_file(
    root: int,
    path: str,
    expected: Digest,
    custody: dict[str, RetainedAuditFile],
    name: str,
) -> RetainedAuditFile:
    from crewshal.linux_inventory import _metadata

    parts = path.split("/")
    if not path.startswith("/") or any(part in ("", ".", "..") for part in parts[1:]):
        raise ValueError("canonical original storage audit path required")
    current = os.dup(root)
    try:
        for name in parts[1:-1]:
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current
            )
            os.close(current)
            current = child
        value = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
    finally:
        os.close(current)
    retained = RetainedAuditFile(path, value, _metadata(os.fstat(value)), expected)
    # Retain each acquired file before its first readback. A refusal must keep
    # its exact original inode instead of dropping partial evidence custody.
    custody[name] = retained
    _check_audit_file(root, retained)
    return retained


def _check_audit_file(root: int, value: RetainedAuditFile) -> None:
    from crewshal.linux_inventory import _metadata

    info = os.fstat(value.descriptor)
    if (
        _metadata(info) != value.metadata
        or not stat.S_ISREG(info.st_mode)
        or info.st_uid != 0
        or info.st_gid != 0
        or info.st_nlink != 1
        or info.st_mode & 0o7022
        or not 0 < info.st_size <= 469_762_048
        or not os.fstatvfs(value.descriptor).f_flag & os.ST_RDONLY
        or not os.fstatvfs(root).f_flag & os.ST_RDONLY
    ):
        raise ValueError("original readonly storage audit file custody differs")
    result, offset = hashlib.sha256(), 0
    while offset < info.st_size:
        part = os.pread(value.descriptor, min(65_536, info.st_size - offset), offset)
        if not part:
            raise ValueError("original storage audit file ended before its bound")
        result.update(part)
        offset += len(part)
    if (
        result.hexdigest() != value.sha256
        or _metadata(os.fstat(value.descriptor)) != value.metadata
    ):
        raise ValueError("original storage audit file bytes changed")
    # Reopen through the original root to exclude an obsolete retained inode.
    current = os.dup(root)
    try:
        for name in value.path.split("/")[1:-1]:
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current
            )
            os.close(current)
            current = child
        now = os.stat(value.path.rsplit("/", 1)[-1], dir_fd=current, follow_symlinks=False)
        if _metadata(now) != value.metadata:
            raise ValueError("current storage audit root file identity differs")
    finally:
        os.close(current)


class RetainedPayloadStorage:
    """Keep policy, kernel, reviewed sources, and original producer together."""

    production: "OwnedBackingProduction"
    reservation: "OwnedStorageReservation"
    root: "RetainedParentInventory"
    _original: tuple["OwnedBackingProduction", "OwnedStorageReservation", "RetainedParentInventory"]
    files: dict[str, RetainedAuditFile]
    retained_sources: dict[str, int]
    failed: bool
    audit: StorageSourceAudit
    policy: RetainedAppArmorExport
    kernel: RetainedScaffoldKernel
    _bindings: tuple[
        StorageSourceAudit,
        RetainedAppArmorExport,
        RetainedScaffoldKernel,
        tuple[tuple[str, RetainedAuditFile], ...],
        tuple[tuple[str, int], ...],
    ]

    def __init__(self) -> None:
        raise ValueError("payload storage requires original producer readback")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original payload storage custody cannot be exported")

    @classmethod
    def retain(
        cls,
        production: "OwnedBackingProduction",
        namespace: int,
        compiled_policy: bytes,
        roles: tuple[tuple[str, str], ...],
        proc: int,
        sysfs: int,
        inode_cache: int,
    ) -> "RetainedPayloadStorage":
        from crewshal.linux_production import OwnedBackingProduction

        if type(production) is not OwnedBackingProduction or hasattr(
            production, "_payload_storage"
        ):
            raise ValueError("original payload storage producer already consumed or differs")
        result = object.__new__(cls)
        result.production = production
        result.reservation = production.reservation
        result.root = production.projected_inventory
        result._original = (production, production.reservation, result.root)
        result.files = {}
        result.retained_sources = {}
        result.failed = False
        setattr(production, "_payload_storage", result)
        try:
            for name, descriptor in (
                ("apparmor", namespace),
                ("proc", proc),
                ("sysfs", sysfs),
                ("inode-cache", inode_cache),
            ):
                result.retained_sources[name] = os.dup(descriptor)
            production.verify()
            result.root.verify()
            inventory = result.root.inventory.root
            entry = inventory.get(AUDIT_PATH)
            if entry is None or entry.kind != "file" or entry.sha256 is None:
                raise ValueError("frozen original storage audit manifest missing")
            value = _audit_file(
                result.root.descriptor, AUDIT_PATH, entry.sha256, result.files, AUDIT_PATH
            )
            if os.fstat(value.descriptor).st_size > 65_536:
                raise ValueError("frozen storage audit manifest exceeds control bound")
            raw = os.pread(value.descriptor, 65_537, 0)
            result.audit = StorageSourceAudit.model_validate_json(raw)
            bindings = production.reservation._configuration.linux_envelope
            if (
                bindings is None
                or bindings.storage_policy_sha256 != record_digest(result.audit)
                or result.audit.policy_source_sha256 != digest(PROPOSED_POLICY)
                or result.audit.policy_binary_sha256 != digest(compiled_policy)
                or not set(AUDIT_SOURCE_NAMES).issubset(result.audit.source_files)
                or len(result.audit.source_files) > 64
                or any(
                    not re.fullmatch(
                        r"(?:kernel|vendor|policy)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", name
                    )
                    or any(part in {".", ".."} for part in name.split("/"))
                    for name in result.audit.source_files
                )
                or {name for name, _ in roles} != set(PROFILE_NAMES)
                or any(
                    re.fullmatch(r"[A-Za-z0-9_.-]+", directory) is None for _, directory in roles
                )
            ):
                raise ValueError("original reviewed storage source or policy binding differs")
            expected = {
                "/opt/crewshal/storage-audit/review.json": result.audit.review_record_sha256,
                "/opt/crewshal/storage-audit/kernel-package.json": result.audit.kernel_package_record_sha256,
                "/opt/crewshal/storage-audit/policy.source": result.audit.policy_source_sha256,
                "/opt/crewshal/storage-audit/policy.binary": result.audit.policy_binary_sha256,
                "/usr/sbin/apparmor_parser": result.audit.policy_parser_executable_sha256,
                "/opt/crewshal/storage-audit/apparmor-parser-package.json": result.audit.policy_parser_package_record_sha256,
                "/opt/codex/bin/codex": result.audit.native_executable_sha256,
                "/opt/codex/codex-resources/codex-linux-sandbox": result.audit.native_sandbox_sha256,
                "/opt/codex/codex-resources/bwrap": result.audit.bubblewrap_executable_sha256,
                **{
                    "/opt/crewshal/storage-audit/sources/" + name: source
                    for name, source in result.audit.source_files.items()
                },
            }
            for path, source in expected.items():
                entry = inventory.get(path)
                target = path
                if (
                    path
                    in {
                        "/opt/codex/bin/codex",
                        "/opt/codex/codex-resources/codex-linux-sandbox",
                        "/opt/codex/codex-resources/bwrap",
                    }
                    and entry is not None
                    and entry.kind == "symlink"
                    and entry.target is not None
                ):
                    target = _vendor_target(path, entry.target)
                    entry = inventory.get(target)
                if entry is None or entry.kind != "file" or entry.sha256 != source:
                    raise ValueError("audited source or installed binary absent from original root")
                _audit_file(result.root.descriptor, target, source, result.files, path)
            raw_export = os.open(
                "profiles/" + roles[0][1] + "/raw_data",
                os.O_RDONLY | os.O_CLOEXEC,
                dir_fd=result.retained_sources["apparmor"],
            )
            result.retained_sources["apparmor-export"] = raw_export
            result.policy = RetainedAppArmorExport.retain_inherited(
                result.retained_sources["apparmor"], compiled_policy, roles, raw_export
            )
            result.kernel = RetainedScaffoldKernel.retain(
                production.reservation.aggregate.descriptor,
                result.retained_sources["proc"],
                result.retained_sources["sysfs"],
                result.retained_sources["inode-cache"],
            )
            result._bindings = (
                result.audit,
                result.policy,
                result.kernel,
                tuple(result.files.items()),
                tuple(result.retained_sources.items()),
            )
            result.check()
            return result
        except BaseException as error:
            result.failed = True
            production.failed = True
            production.reservation._retain_installation_refusal(error)
            raise

    def check(self) -> ScaffoldKernelObservation:
        try:
            owner, reservation, root = self._original
            if (
                self.failed
                or self.production is not owner
                or self.reservation is not reservation
                or self.root is not root
                or getattr(owner, "_payload_storage", None) is not self
                or getattr(reservation, "_production", None) is not owner
                or owner.projected_inventory is not root
                or self.audit is not self._bindings[0]
                or self.policy is not self._bindings[1]
                or self.kernel is not self._bindings[2]
                or tuple(self.files) != tuple(name for name, _ in self._bindings[3])
                or any(self.files[name] is not value for name, value in self._bindings[3])
                or tuple(self.retained_sources.items()) != self._bindings[4]
                or self.kernel.aggregate != reservation.aggregate.descriptor
                or self.kernel.aggregate_identity
                != (
                    reservation.aggregate.identity.device,
                    reservation.aggregate.identity.inode,
                )
            ):
                raise ValueError("original compatible payload storage custody differs")
            bindings = reservation._configuration.linux_envelope
            if bindings is None or bindings.storage_policy_sha256 != record_digest(self.audit):
                raise ValueError("original storage source audit configuration changed")
            root.verify()
            for retained in self.files.values():
                _check_audit_file(root.descriptor, retained)
            self.policy.check_policy()
            current = self.kernel.check()
            if (
                current.kernel_release != self.audit.kernel_release
                or current.kernel_notes_sha256 != self.audit.kernel_notes_sha256
                or current.kernel_btf_sha256 != self.audit.kernel_btf_sha256
            ):
                raise ValueError("running kernel differs from frozen reviewed source build")
            return current
        except BaseException as error:
            self.failed = True
            self.production.failed = True
            self.reservation._retain_installation_refusal(error)
            raise

    def check_process(self, proc: int, label: str) -> AppArmorExportObservation:
        self.check()
        return self.policy.check_process(proc, label)
