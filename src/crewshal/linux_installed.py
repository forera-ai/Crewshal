"""Retain mapped executable files from the original task and copied root.

This readback checks current mappings. It does not prove future loader behavior.
It grants no execution, release, or resource reuse authority.
"""

import hashlib
import os
import re
import stat
from typing import TYPE_CHECKING, NoReturn, TypeAlias

from crewshal.admission import _read
from crewshal.linux_inventory import RetainedParentInventory, _metadata, _discard_completed_pages

if TYPE_CHECKING:
    from crewshal.admission import RetainedProc
    from crewshal.linux_parent import RetainedTrustedTask
    from crewshal.linux_validator import RetainedValidatorProc
    from crewshal.linux_auth import OriginalAuthenticationProc

    MappedTask: TypeAlias = (
        RetainedTrustedTask | RetainedProc | RetainedValidatorProc | OriginalAuthenticationProc
    )


def _mappings(raw: bytes) -> dict[str, tuple[str, int, int, int, str]]:
    """Parse bounded kernel rows. Reject ambiguous or unlisted executable maps."""
    if not raw or len(raw) > 262144 or not raw.endswith(b"\n"):
        raise ValueError("installed mapping readback is missing or exceeds its bound")
    result: dict[str, tuple[str, int, int, int, str]] = {}
    last_end = 0
    for line in raw.decode("ascii").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) < 5 or len(result) >= 4096:
            raise ValueError("installed mapping row or count differs")
        address, permissions, offset, device, inode = fields[:5]
        if (
            not re.fullmatch(r"[0-9a-f]+-[0-9a-f]+", address)
            or not re.fullmatch(r"[r-][w-][x-][ps]", permissions)
            or not re.fullmatch(r"[0-9a-f]+", offset)
            or not re.fullmatch(r"[0-9a-f]+:[0-9a-f]+", device)
            or not re.fullmatch(r"[0-9]+", inode)
        ):
            raise ValueError("installed mapping kernel fields differ")
        start, end = (int(value, 16) for value in address.split("-"))
        if start < last_end or end <= start:
            raise ValueError("installed mapping ranges overlap or repeat")
        last_end = end
        name = fields[5] if len(fields) == 6 else ""
        number = int(inode)
        if number == 0:
            if "x" in permissions and not (
                name in {"[vdso]", "[vsyscall]"}
                and permissions == "r-xp"
                and int(offset, 16) == 0
                and device == "00:00"
            ):
                raise ValueError("installed task has an unlisted executable anonymous mapping")
            continue
        if not name.startswith("/") or "\\" in name or " (deleted)" in name:
            raise ValueError("installed mapping path is ambiguous or deleted")
        major, minor = (int(value, 16) for value in device.split(":"))
        canonical = f"{start:x}-{end:x}"
        result[canonical] = (name, os.makedev(major, minor), number, int(offset, 16), permissions)
    if not result:
        raise ValueError("installed task has no observed file mappings")
    return result


class InstalledImageRefusal(ValueError):
    def __init__(self, message: str, owner: "RetainedInstalledImages"):
        super().__init__(message)
        self.owner = owner


class RetainedInstalledImages:
    """Keep every acquired mapping FD through unknown or failed readback."""

    task: "MappedTask"
    root: RetainedParentInventory
    failed: bool
    handles: dict[str, int]
    mappings: dict[str, tuple[str, int, int, int, str]]
    metadata: dict[str, tuple[int, ...]]
    _owners: tuple["MappedTask", RetainedParentInventory]

    def __init__(self) -> None:
        raise ValueError("installed images require original retained task readback")

    def __reduce__(self) -> NoReturn:
        raise TypeError("installed image custody cannot be copied or exported")

    def _task(self) -> None:
        from crewshal.admission import RetainedProc
        from crewshal.linux_parent import RetainedTrustedTask
        from crewshal.linux_validator import RetainedValidatorProc
        from crewshal.linux_auth import OriginalAuthenticationProc

        task = self.task
        if self._owners != (task, self.root):
            raise ValueError("installed image original root or task changed")
        if type(task) is RetainedTrustedTask:
            task.verify(task.spec.cgroup)
        elif type(task) is RetainedProc:
            task.verify_stopped()
        elif type(task) is RetainedValidatorProc:
            task.verify_state(traced=False)
        elif type(task) is OriginalAuthenticationProc:
            task.verify_stopped()
        else:
            raise ValueError("installed images require an original concrete task")
        if getattr(task, "_installed_images", None) is not self:
            raise ValueError("installed image original task custody changed")
        self.root.verify_task_root(task.descriptor)
        if not os.fstatvfs(self.root.descriptor).f_flag & os.ST_RDONLY:
            raise ValueError("installed mapped root is writable")

    def _root_file(self, name: str) -> int:
        entry = self.root.inventory.root.get(name)
        parts = name.split("/")[1:]
        if entry is None or entry.kind != "file" or any(part in {"", ".", ".."} for part in parts):
            raise ValueError("installed mapped file is absent from the exact copied root")
        current = os.dup(self.root.descriptor)
        try:
            for part in parts[:-1]:
                child = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=current,
                )
                os.close(current)
                current = child
            return os.open(
                parts[-1],
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                dir_fd=current,
            )
        finally:
            os.close(current)

    def _verify_file(
        self, address: str, mapping: tuple[str, int, int, int, str], *, hash_bytes: bool = True
    ) -> None:
        name, device, inode, _, _ = mapping
        handle = self.handles[address]
        before = os.fstat(handle)
        observed = os.stat("map_files/" + address, dir_fd=self.task.descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or (before.st_dev, before.st_ino) != (device, inode)
            or _metadata(observed) != _metadata(before)
            or before.st_uid != 0
            or before.st_gid != 0
            or before.st_mode & 0o7022
            or before.st_nlink != 1
            or before.st_size > 1073741824
            or os.fstatvfs(handle).f_flag & os.ST_RDONLY == 0
        ):
            raise ValueError("installed mapped file identity or protection differs")
        original = self._root_file(name)
        try:
            if _metadata(os.fstat(original)) != _metadata(before):
                raise ValueError("installed mapping does not use the retained copied-root inode")
        finally:
            os.close(original)
        if not hash_bytes:
            if address in self.metadata and self.metadata[address] != _metadata(before):
                raise ValueError("installed mapped file bytes or metadata changed")
            self.metadata[address] = _metadata(before)
            return
        sha = hashlib.sha256()
        position = 0
        while position < before.st_size:
            chunk = os.pread(handle, min(65536, before.st_size - position), position)
            if not chunk:
                raise ValueError("installed mapped file ended during readback")
            sha.update(chunk)
            position += len(chunk)
            _discard_completed_pages(handle, position, before.st_size)
        if (
            sha.hexdigest() != self.root.inventory.root[name].sha256
            or _metadata(os.fstat(handle)) != _metadata(before)
            or address in self.metadata
            and self.metadata[address] != _metadata(before)
        ):
            raise ValueError("installed mapped file bytes or metadata changed")
        self.metadata[address] = _metadata(before)

    def verify(self) -> None:
        try:
            if self.failed:
                raise ValueError("installed mapped-file readback previously failed")
            self._task()
            rows = _mappings(_read(self.task.descriptor, "maps", 262144))
            if rows != self.mappings or set(self.handles) != set(rows):
                raise ValueError("installed task mapping set changed")
            checked: set[tuple[str, int, int]] = set()
            for address, mapping in rows.items():
                identity = mapping[:3]
                self._verify_file(address, mapping, hash_bytes=identity not in checked)
                checked.add(identity)
            if _mappings(_read(self.task.descriptor, "maps", 262144)) != rows:
                raise ValueError("installed task mappings changed during readback")
            self._task()
        except BaseException:
            self.failed = True
            raise


def retain_installed_images(
    task: "MappedTask", root: RetainedParentInventory
) -> RetainedInstalledImages:
    """Bind before acquisition. Keep partial FDs when any check fails."""
    if type(root) is not RetainedParentInventory or hasattr(task, "_installed_images"):
        raise ValueError("installed mapping custody is one-shot and requires the original root")
    owner = object.__new__(RetainedInstalledImages)
    owner.task, owner.root = task, root
    owner._owners = (task, root)
    owner.failed = False
    owner.handles, owner.metadata, owner.mappings = {}, {}, {}
    setattr(task, "_installed_images", owner)
    try:
        owner._task()
        owner.mappings = _mappings(_read(task.descriptor, "maps", 262144))
        retained: dict[tuple[str, int, int], int] = {}
        for address, mapping in owner.mappings.items():
            identity = mapping[:3]
            if identity not in retained:
                retained[identity] = os.open(
                    "map_files/" + address,
                    os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC,
                    dir_fd=task.descriptor,
                )
            owner.handles[address] = retained[identity]
        owner.verify()
        return owner
    except BaseException as error:
        owner.failed = True
        raise InstalledImageRefusal(str(error), owner) from error
