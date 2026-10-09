"""Passive trusted-parent inventory binding and retained root readback.

This is not a parent entry point, installer, dynamic-loader proof or execution
gate. Inventory bytes are read as data; no program is imported or executed.
"""

import hashlib
import os
from pathlib import PurePosixPath
import stat
from typing import Literal

from pydantic import Field

from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.model import Contract


class RootEntry(Contract):
    kind: Literal["file", "directory", "symlink"]
    mode: int = Field(ge=0, le=0o7777)
    sha256: Digest | None = None
    target: str | None = None


class TrustedParentInventory(Contract):
    schema_version: Literal[1] = 1
    root: dict[str, RootEntry]
    parent_argv: list[str]
    entry_path: str
    entry_kind: Literal["native", "python"] = "native"
    helper_libraries: dict[str, Digest]
    execution_allowed: Literal[False] = False
    profile_qualified: Literal[False] = False


def _path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or "\x00" in value
        or not path.is_absolute()
        or str(path) != value
        or ".." in path.parts
    ):
        raise ValueError("inventory requires canonical absolute root paths")
    return path


def audit_parent_inventory(inventory: TrustedParentInventory) -> TrustedParentInventory:
    inventory = TrustedParentInventory.model_validate_json(inventory.model_dump_json())
    if not 1 <= len(inventory.root) <= 32768:
        raise ValueError("trusted root inventory exceeds count bound")
    for name, entry in inventory.root.items():
        path = _path(name)
        if entry.kind != "symlink" and entry.mode & 0o7022:
            raise ValueError("trusted root cannot grant group/world writes or special modes")
        if name != "/" and (
            str(path.parent) not in inventory.root
            or inventory.root[str(path.parent)].kind != "directory"
        ):
            raise ValueError("inventory requires every real parent directory")
        if entry.kind == "file":
            if entry.sha256 is None or entry.target is not None:
                raise ValueError("inventory file requires exact bytes only")
        elif entry.kind == "directory":
            if entry.sha256 is not None or entry.target is not None:
                raise ValueError("inventory directory cannot assert file bytes or target")
        else:
            # Resolve links against the copied root, never the host filesystem.
            if entry.sha256 is not None or not entry.target or "\x00" in entry.target:
                raise ValueError("inventory symlink requires exact target only")
            target = PurePosixPath(entry.target)
            parts: list[str] = [] if target.is_absolute() else list(path.parent.parts[1:])
            for part in target.parts:
                if part in ("/", "."):
                    continue
                if part == "..":
                    if not parts:
                        raise ValueError("inventory symlink escapes copied root")
                    parts.pop()
                else:
                    parts.append(part)
            resolved = "/" + "/".join(parts)
            if resolved not in inventory.root or inventory.root[resolved].kind == "symlink":
                raise ValueError("inventory symlink target missing or chained")
    if inventory.root.get("/") != RootEntry(kind="directory", mode=0o755):
        raise ValueError("trusted root requires explicit readonly directory inventory")
    argv = inventory.parent_argv
    if not argv or any(not value or "\x00" in value for value in argv):
        raise ValueError("trusted parent argv is missing or malformed")
    for name in (
        argv[0],
        inventory.entry_path,
        "/bin/crewshal-bootstrap",
        "/bin/setpriv",
        "/usr/bin/env",
    ):
        _path(name)
        required_entry = inventory.root.get(name)
        if required_entry is None or required_entry.kind != "file":
            raise ValueError("trusted parent/helper entry must be an inventoried real file")
    if inventory.entry_path not in argv or not inventory.root[argv[0]].mode & 0o111:
        raise ValueError("trusted parent entry and executable argv differ")
    if inventory.entry_kind == "python":
        if (
            argv != [argv[0], "-I", "-S", "-B", inventory.entry_path]
            or inventory.entry_path == argv[0]
        ):
            raise ValueError("trusted Python parent requires exact isolated source entry")
    elif inventory.entry_path != argv[0]:
        raise ValueError("trusted native parent requires its exact executable entry")
    if (
        len(inventory.helper_libraries) < 2
        or "/bin/crewshal-bootstrap" not in inventory.helper_libraries
    ):
        raise ValueError("explicit helper and library inventory required")
    for name, digest in inventory.helper_libraries.items():
        library_entry = inventory.root.get(name)
        if library_entry is None or library_entry.kind != "file" or library_entry.sha256 != digest:
            raise ValueError("helper/library inventory differs from copied root")
    return inventory


class RootInventory(Contract):
    entries: dict[str, RootEntry]


class HelperLibraryInventory(Contract):
    entries: dict[str, Digest]


def root_inventory_digest(inventory: TrustedParentInventory) -> Digest:
    return record_digest(RootInventory(entries=inventory.root))


def helper_library_inventory_digest(inventory: TrustedParentInventory) -> Digest:
    return record_digest(HelperLibraryInventory(entries=inventory.helper_libraries))


def bind_parent_inventory(
    configuration: DispatchConfiguration,
    inventory: TrustedParentInventory,
    parent_argv: list[str],
    parent_executable: Digest,
    helper_binary: Digest | None,
) -> TrustedParentInventory:
    """Require explicit per-session digests; matching them supplies no authority."""
    inventory = audit_parent_inventory(inventory)
    bindings = configuration.linux_envelope
    if (
        bindings is None
        or bindings.parent_inventory_sha256 != record_digest(inventory)
        or bindings.root_inventory_sha256 != root_inventory_digest(inventory)
        or bindings.helper_library_inventory_sha256 != helper_library_inventory_digest(inventory)
        or inventory.parent_argv != parent_argv
        or inventory.root[parent_argv[0]].sha256 != parent_executable
        or inventory.root["/bin/crewshal-bootstrap"].sha256 != helper_binary
    ):
        raise ValueError("trusted parent/root/helper inventory binding differs")
    return inventory


def _metadata(info: os.stat_result) -> tuple[int, ...]:
    return tuple(
        getattr(info, name)
        for name in (
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
    )


class RetainedParentInventory:
    """Read-only pinned copied root. Caller owns its mount and qualification.

    Exact enumeration catches missing/extra files. Root ownership, no hardlinks,
    no cross-device directories, no followed links and before/after metadata
    checks constrain this readback. Effective readonly mount and loader closure
    still require independent Linux qualification.
    """

    def __init__(self, descriptor: int, inventory: TrustedParentInventory):
        self.inventory = audit_parent_inventory(inventory)
        self.descriptor = os.dup(descriptor)
        info = os.fstat(self.descriptor)
        self.identity = (info.st_dev, info.st_ino)
        if not stat.S_ISDIR(info.st_mode):
            self.close()
            raise ValueError("trusted inventory requires retained root directory")

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1

    def verify_task_root(self, proc_descriptor: int) -> None:
        """Compare kernel task root to retained copied-root identity, not PID text."""
        root = os.stat("root", dir_fd=proc_descriptor)
        if (root.st_dev, root.st_ino) != self.identity:
            raise ValueError("trusted parent task root differs from retained inventory")

    def verify(self) -> None:
        info = os.fstat(self.descriptor)
        if (info.st_dev, info.st_ino) != self.identity:
            raise ValueError("retained inventory root identity changed")
        seen: dict[str, RootEntry] = {}
        total = 0

        def visit(descriptor: int, path: str, depth: int) -> None:
            nonlocal total
            if depth > 64 or len(seen) >= 32768:
                raise ValueError("trusted inventory traversal bound exceeded")
            before = os.fstat(descriptor)
            if before.st_uid != 0 or before.st_gid != 0 or before.st_dev != self.identity[0]:
                raise ValueError("trusted inventory ownership or device differs")
            seen[path] = RootEntry(kind="directory", mode=stat.S_IMODE(before.st_mode))
            for name in sorted(os.listdir(descriptor)):
                if len(seen) >= 32768:
                    raise ValueError("trusted inventory count bound exceeded")
                child = path.rstrip("/") + "/" + name
                entry = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if entry.st_uid != 0 or entry.st_gid != 0:
                    raise ValueError("trusted inventory file owner differs")
                if stat.S_ISLNK(entry.st_mode):
                    seen[child] = RootEntry(
                        kind="symlink",
                        mode=stat.S_IMODE(entry.st_mode),
                        target=os.readlink(name, dir_fd=descriptor),
                    )
                else:
                    handle = os.open(
                        name,
                        os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                        dir_fd=descriptor,
                    )
                    try:
                        opened = os.fstat(handle)
                        if (
                            _metadata(opened) != _metadata(entry)
                            or opened.st_dev != self.identity[0]
                        ):
                            raise ValueError("inventory file identity changed or device differs")
                        if stat.S_ISDIR(opened.st_mode):
                            visit(handle, child, depth + 1)
                        elif stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1:
                            sha = hashlib.sha256()
                            while chunk := os.read(handle, 65536):
                                total += len(chunk)
                                if total > 1073741824:
                                    raise ValueError(
                                        "copied root exceeds prepared storage reservation"
                                    )
                                sha.update(chunk)
                            seen[child] = RootEntry(
                                kind="file",
                                mode=stat.S_IMODE(opened.st_mode),
                                sha256=sha.hexdigest(),
                            )
                        else:
                            raise ValueError(
                                "trusted inventory refuses special files and hardlinks"
                            )
                        if _metadata(os.fstat(handle)) != _metadata(opened):
                            raise ValueError("inventory bytes or metadata changed during readback")
                    finally:
                        os.close(handle)
                if _metadata(os.stat(name, dir_fd=descriptor, follow_symlinks=False)) != _metadata(
                    entry
                ):
                    raise ValueError("inventory entry changed during readback")
            if _metadata(os.fstat(descriptor)) != _metadata(before):
                raise ValueError("inventory directory changed during readback")

        visit(self.descriptor, "/", 0)
        if seen != self.inventory.root:
            raise ValueError("copied root contents differ from exact trusted inventory")
