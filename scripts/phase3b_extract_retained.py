"""Bounded retained-archive extractor. The CLI remains closed until separate admission.

Tests supply synthetic archives to ``extract_batch``. Real retained inputs require an
updated admission ledger, an exact extractor hash, and a separate owner decision.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import posixpath
import stat
import sys
import tarfile
from typing import Any, Callable, IO
import unicodedata
import zipfile

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase3b_inspect_archive_members import inspect_archive  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json"
REPORT = ROOT / "docs/PHASE-3B-RETAINED-ARCHIVE-MEMBERS-2026-10-19.json"
FROZEN = ROOT / "docs/evaluation/phase-3a-frozen"
MOUNT = Path("/Volumes/CrewshalPhase3BArchiveStage")
FROZEN_CORPUS_SHA256 = "894f38d198b640bdda49d1adb40590d037e076a8bb547072f799c2f9f3f0a0fd"
FROZEN_INVENTORIES_SHA256 = "86a2efd86d84dc42b33dbc4fb9be6a9818b0fb90a3916bf0b225479d7877f48f"
SELECTED_IDS = frozenset(
    {
        "bun",
        "claude-wrapper",
        "codex-wrapper",
        "cpython",
        "dotnet-1",
        "dotnet-runtime-net8",
        "dotnet-targeting-pack-net8",
        "node",
        "python-1",
        "rtk",
        "swift-1",
        "typescript-2",
    }
)
EXCLUDED_IDS = frozenset({"swift", "dotnet-sdk", "codex-native", "claude-native"})
SOURCE_IDS = frozenset({"dotnet-1", "python-1", "swift-1", "typescript-2"})
CONTENT_CAP = 511_667_961
FREE_FLOOR = 536_870_912
CHUNK = 1024 * 1024
PINNED_ARCHIVES = {
    "bun": (36_226_213, "d1dbaa3e9af24549fad92bdbe4fb21fa53302cd048a8f004e85a240984c93d4d"),
    "claude-wrapper": (27_538, "08c6dfcf3dafcfd30e09b2926c596e274f0fa20844a5801ada7f1c8e6227157e"),
    "codex-wrapper": (4_904, "d84454cfa82f61add78b3270073c6e254923e89657c7f0dd1a88cc5659b4e0c0"),
    "cpython": (20_829_824, "c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a"),
    "dotnet-1": (198_331, "71a77a7c2eb4d1ffa1572c97c9050c673e16f24cdac19d5039ad79cad06a26dd"),
    "dotnet-runtime-net8": (
        29_865_496,
        "c1ab652d8c645f7311231a22b82ab93f1c1fef1bdaec166a333f81d3a595541c",
    ),
    "dotnet-targeting-pack-net8": (
        6_845_027,
        "968e8c027bc54350c10e1fbda9dc73389320002b2f1638f67b96e1ade278bf42",
    ),
    "node": (28_636_440, "08bfbf538bad0e8cbb0269f0173cca28d705874a67a22f60b57d99dc99e30050"),
    "python-1": (343_014, "edfa6cf117bbbe46f6690266a40389b08b12cbf87fad8664d349ebd6eea811a1"),
    "rtk": (4_483_862, "8d6d1aad9e69b42481eda7039507d1f7ee93698f87713cecd873d287c1931632"),
    "swift-1": (655_699, "45c952a441611e17d8c30de26c4a6b40eec483c07900d9faad2501539aa5c900"),
    "typescript-2": (1_580_238, "4754f74b4defcbaa9b8748406fcd3e974b756abf7824e8a1a4304ec9665e6ced"),
}


@dataclass(frozen=True)
class ArchiveSpec:
    archive_id: str
    archive_bytes: int
    archive_sha256: str
    report: dict[str, Any]
    source_prefix: str | None = None
    source_files: dict[str, dict[str, Any]] | None = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bound_policy() -> list[ArchiveSpec]:
    """Bind the selected IDs and bounds to the single admission ledger."""
    ledger = json.loads(LEDGER.read_text())
    proposal = ledger["archive_extraction_proposal"]
    if (
        len(proposal["selected_ids"]) != 12
        or set(proposal["selected_ids"]) != SELECTED_IDS
        or len(proposal["excluded_ids"]) != 4
        or set(proposal["excluded_ids"]) != EXCLUDED_IDS
        or proposal["selected_regular_content_upper_bytes"] != CONTENT_CAP
        or proposal["selected_regular_members"] != 11_019
        or proposal["selected_directory_members"] != 1_740
        or proposal["minimum_mounted_free_bytes"] != FREE_FLOOR
        or proposal["selected_symlink_members"] != 3
        or _sha256(REPORT) != ledger["archive_member_inspection"]["report_sha256"]
    ):
        raise ValueError("retained extraction policy differs from the admission ledger")
    rows = {row["id"]: row for row in json.loads(REPORT.read_text())["archives"]}
    selected = [rows[key] for key in SELECTED_IDS]
    counts = {
        kind: sum(row["counts"].get(kind, 0) for row in selected)
        for kind in ("regular", "directory", "symlink")
    }
    if (
        len(rows) != 16
        or set(PINNED_ARCHIVES) != SELECTED_IDS
        or sum(row["members"] for row in selected) != proposal["selected_members"]
        or counts != {"regular": 11_019, "directory": 1_740, "symlink": 3}
        or max(row["largest_regular_bytes"] for row in selected)
        != proposal["largest_selected_regular_member_bytes"]
        or sum(row["regular_content_upper_bytes"] for row in selected) != CONTENT_CAP
    ):
        raise ValueError("retained member report differs from the selected content bound")
    if (
        _sha256(FROZEN / "corpus.json") != FROZEN_CORPUS_SHA256
        or _sha256(FROZEN / "source-inventories.json") != FROZEN_INVENTORIES_SHA256
    ):
        raise ValueError("frozen source package differs from the pinned inputs")
    corpus = {
        row["id"]: row for row in json.loads((FROZEN / "corpus.json").read_text())["repositories"]
    }
    inventories = {
        row["id"]: row
        for row in json.loads((FROZEN / "source-inventories.json").read_text())["repositories"]
    }
    specs = []
    for archive_id in sorted(SELECTED_IDS):
        archive_bytes, archive_sha256 = PINNED_ARCHIVES[archive_id]
        report = rows[archive_id]
        if report["archive_bytes"] != archive_bytes:
            raise ValueError("retained archive length differs from the pinned identity")
        prefix = None
        files = None
        if archive_id in SOURCE_IDS:
            source = corpus[archive_id]
            if (
                source["source_identity"]["archive_sha256"] != archive_sha256
                or source["source_identity"]["archive_bytes"] != archive_bytes
            ):
                raise ValueError("source archive differs from the frozen identity")
            prefix = source["repository"].split("/")[-1] + "-" + source["revision"]
            files = {row["path"]: row for row in inventories[archive_id]["files"]}
            if len(files) != len(inventories[archive_id]["files"]):
                raise ValueError("frozen source inventory has duplicate paths")
        specs.append(ArchiveSpec(archive_id, archive_bytes, archive_sha256, report, prefix, files))
    return specs


def _normalize(name: str, archive_id: str) -> str | None:
    if archive_id == "dotnet-runtime-net8" and name == ".":
        return None
    if archive_id == "dotnet-runtime-net8":
        if not name.startswith("./"):
            raise ValueError(".NET member lacks its one leading dot component")
        name = name[2:]
    if (
        not name
        or name.startswith("/")
        or "\\" in name
        or "\x00" in name
        or any(part in {"", ".", ".."} for part in name.split("/"))
    ):
        raise ValueError("archive contains an unsafe path")
    return name


def _fold(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def _members(archive: Path, archive_format: str) -> list[tuple[str, str, int, str]]:
    result = []
    if archive_format == "zip":
        with zipfile.ZipFile(archive) as source:
            for zip_member in source.infolist():
                mode = stat.S_IFMT(zip_member.external_attr >> 16)
                kind = (
                    "directory"
                    if zip_member.is_dir()
                    else "regular"
                    if mode in {0, stat.S_IFREG}
                    else "special"
                )
                if zip_member.flag_bits & 1 or zip_member.compress_type not in {0, 8, 12, 14}:
                    raise ValueError("encrypted or unsupported ZIP member")
                result.append((zip_member.filename.rstrip("/"), kind, zip_member.file_size, ""))
    elif archive_format == "tar":
        with tarfile.open(archive, "r|*") as source:
            for tar_member in source:
                kind = (
                    "directory"
                    if tar_member.isdir()
                    else "regular"
                    if tar_member.isfile()
                    else "symlink"
                    if tar_member.issym()
                    else "special"
                )
                if tar_member.sparse:
                    raise ValueError("sparse archive member")
                result.append(
                    (tar_member.name.rstrip("/"), kind, tar_member.size, tar_member.linkname)
                )
    else:
        raise ValueError("unsupported archive format")
    return result


def _preflight(archive: Path, spec: ArchiveSpec) -> list[tuple[str, str, int, str]]:
    if spec.archive_id not in SELECTED_IDS or spec.archive_id in EXCLUDED_IDS:
        raise ValueError("archive is excluded from this batch")
    if (
        archive.is_symlink()
        or not archive.is_file()
        or archive.stat().st_size != spec.archive_bytes
        or _sha256(archive) != spec.archive_sha256
    ):
        raise ValueError("archive differs from its pinned length or SHA-256")
    observed = inspect_archive(archive)
    for key in (
        "format",
        "members",
        "counts",
        "regular_content_upper_bytes",
        "largest_regular_bytes",
        "member_metadata_sha256",
        "links",
    ):
        if observed[key] != spec.report[key]:
            raise ValueError("archive metadata differs from the retained member report")
    members = _members(archive, str(spec.report["format"]))
    seen: dict[str, str] = {}
    seen_parents: dict[str, str] = {}
    types: dict[str, str] = {}
    source_names: set[str] = set()
    links = (
        {(row["name"], row["target"]) for row in spec.report["links"]}
        if spec.archive_id == "node"
        else set()
    )
    if spec.archive_id == "node" and len(links) != 3:
        raise ValueError("Node requires exactly three recorded links")
    for raw_name, kind, size, target in members:
        name = _normalize(raw_name, spec.archive_id)
        if name is None:
            if kind != "directory":
                raise ValueError(".NET root marker is not a directory")
            continue
        folded = _fold(name)
        if folded in seen:
            raise ValueError("duplicate or case-alias member")
        if folded in seen_parents and seen_parents[folded] != name:
            raise ValueError("member aliases an existing parent")
        seen[folded] = name
        types[name] = kind
        if kind not in {"regular", "directory"} and not (
            kind == "symlink" and spec.archive_id == "node" and (raw_name, target) in links
        ):
            raise ValueError("archive contains an unapproved link or special member")
        if kind == "symlink":
            if target.startswith("/") or "\\" in target or "\x00" in target:
                raise ValueError("unsafe Node link target")
        if spec.source_files is not None and kind == "regular":
            if spec.source_prefix is None or not name.startswith(spec.source_prefix + "/"):
                raise ValueError("source member lies outside its frozen root")
            relative = name[len(spec.source_prefix) + 1 :]
            expected = spec.source_files.get(relative)
            if expected is None or expected["bytes"] != size:
                raise ValueError("source member differs from the frozen inventory")
            source_names.add(relative)
    if spec.source_files is not None and source_names != spec.source_files.keys():
        raise ValueError("source file set differs from the frozen inventory")
    for name, kind in types.items():
        parts = name.split("/")
        for i in range(1, len(parts)):
            parent = "/".join(parts[:i])
            if types.get(parent) not in {None, "directory"}:
                raise ValueError("member uses a non-directory parent")
            alias = seen.get(_fold(parent))
            if alias is not None and alias != parent:
                raise ValueError("member uses a case-alias parent")
            prior_parent = seen_parents.setdefault(_fold(parent), parent)
            if prior_parent != parent:
                raise ValueError("member uses a case-alias parent")
        if kind == "symlink":
            resolved = posixpath.normpath(
                posixpath.join(
                    posixpath.dirname(name),
                    next(t for n, k, s, t in members if _normalize(n, spec.archive_id) == name),
                )
            )
            if (
                resolved in {".", ".."}
                or resolved.startswith("../")
                or types.get(resolved) != "regular"
            ):
                raise ValueError("Node link must resolve directly to a regular member")
    return members


def _free_bytes(path: Path) -> int:
    info = os.statvfs(path)
    return info.f_bavail * info.f_frsize


def _open_dir(
    parent_fd: int, name: str, *, create: bool = True, free: Callable[[], int] | None = None
) -> int:
    if create:
        if free is not None and free() < FREE_FLOOR:
            raise ValueError("mounted free space fell below the floor")
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        if free is not None and free() < FREE_FLOOR:
            raise ValueError("mounted free space fell below the floor")
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)


def _parent_fd(
    root_fd: int, parts: list[str], *, create: bool = True, free: Callable[[], int] | None = None
) -> int:
    current = os.dup(root_fd)
    try:
        for part in parts:
            following = _open_dir(current, part, create=create, free=free)
            os.close(current)
            current = following
        return current
    except BaseException:
        os.close(current)
        raise


def _write_stream(
    root_fd: int,
    name: str,
    source: IO[bytes],
    declared: int,
    total: list[int],
    free: Callable[[], int],
) -> str:
    parts = name.split("/")
    parent_fd = _parent_fd(root_fd, parts[:-1], free=free)
    try:
        fd = os.open(
            parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd
        )
        try:
            written = 0
            digest = hashlib.sha256()
            while chunk := source.read(min(CHUNK, declared - written + 1)):
                if written + len(chunk) > declared or total[0] + len(chunk) > CONTENT_CAP:
                    raise ValueError("regular content exceeds its exact bound")
                if free() < FREE_FLOOR:
                    raise ValueError("mounted free space fell below the floor")
                view = memoryview(chunk)
                while view:
                    count = os.write(fd, view)
                    if count <= 0:
                        raise OSError("short archive output write")
                    written += count
                    total[0] += count
                    digest.update(view[:count])
                    view = view[count:]
                if free() < FREE_FLOOR:
                    raise ValueError("mounted free space fell below the floor")
            if written != declared:
                raise ValueError("regular member ended before its declared size")
            os.fsync(fd)
            return digest.hexdigest()
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


def _create_node_links(
    root_fd: int, members: list[tuple[str, str, int, str]], free: Callable[[], int]
) -> None:
    archive_fd = _open_dir(root_fd, "node", create=False)
    try:
        for raw_name, kind, _, target in members:
            if kind != "symlink":
                continue
            name = _normalize(raw_name, "node")
            assert name is not None
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
            dest_parent = _parent_fd(archive_fd, resolved.split("/")[:-1], create=False)
            try:
                fd = os.open(
                    resolved.split("/")[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dest_parent
                )
                try:
                    if not stat.S_ISREG(os.fstat(fd).st_mode):
                        raise ValueError("Node link target changed")
                    target_stat = os.fstat(fd)
                finally:
                    os.close(fd)
            finally:
                os.close(dest_parent)
            link_parent = _parent_fd(archive_fd, name.split("/")[:-1], free=free)
            try:
                if free() < FREE_FLOOR:
                    raise ValueError("mounted free space fell below the floor")
                os.symlink(target, name.split("/")[-1], dir_fd=link_parent)
                if free() < FREE_FLOOR:
                    raise ValueError("mounted free space fell below the floor")
                if os.readlink(name.split("/")[-1], dir_fd=link_parent) != target:
                    raise ValueError("Node link changed after creation")
                link_stat = os.stat(name.split("/")[-1], dir_fd=link_parent)
                if (link_stat.st_dev, link_stat.st_ino) != (target_stat.st_dev, target_stat.st_ino):
                    raise ValueError("Node link resolved destination changed")
            finally:
                os.close(link_parent)
    finally:
        os.close(archive_fd)


def _verify_output_tree(
    root_fd: int,
    specs: list[ArchiveSpec],
    plans: dict[str, list[tuple[str, str, int, str]]],
    rows: list[dict[str, object]],
) -> tuple[list[str], list[dict[str, str]], str]:
    file_rows = {(str(row["archive_id"]), str(row["path"])): row for row in rows}
    expected: dict[str, tuple[str, int, str]] = {}
    for spec in specs:
        expected[spec.archive_id] = ("directory", 0, "")
        for raw_name, kind, size, target in plans[spec.archive_id]:
            name = _normalize(raw_name, spec.archive_id)
            if name is None:
                continue
            path = spec.archive_id + "/" + name
            expected[path] = (kind, size, target)
            parts = path.split("/")
            for index in range(1, len(parts)):
                parent = "/".join(parts[:index])
                expected.setdefault(parent, ("directory", 0, ""))
    seen: set[str] = set()
    directories: list[str] = []
    links: list[dict[str, str]] = []
    digest = hashlib.sha256()

    def walk(directory_fd: int, prefix: str) -> None:
        with os.scandir(directory_fd) as entries:
            names = sorted(entry.name for entry in entries)
        for name in names:
            path = prefix + name
            if path not in expected or path in seen:
                raise ValueError("output tree contains an unexpected or duplicate name")
            seen.add(path)
            kind, size, target = expected[path]
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if kind == "directory":
                if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077:
                    raise ValueError("output directory changed before final readback")
                directories.append(path)
                child_fd = os.open(
                    name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd
                )
                try:
                    walk(child_fd, path + "/")
                finally:
                    os.close(child_fd)
                value = ""
            elif kind == "regular":
                if not stat.S_ISREG(info.st_mode) or info.st_size != size or info.st_mode & 0o177:
                    raise ValueError("regular output changed before final readback")
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
                try:
                    file_digest = hashlib.sha256()
                    with os.fdopen(os.dup(fd), "rb") as stream:
                        for chunk in iter(lambda: stream.read(CHUNK), b""):
                            file_digest.update(chunk)
                finally:
                    os.close(fd)
                archive_id, relative = path.split("/", 1)
                if file_digest.hexdigest() != file_rows[(archive_id, relative)]["sha256"]:
                    raise ValueError("regular output changed before final readback")
                value = file_digest.hexdigest()
            elif kind == "symlink":
                if (
                    not stat.S_ISLNK(info.st_mode)
                    or os.readlink(name, dir_fd=directory_fd) != target
                ):
                    raise ValueError("Node link changed before final readback")
                if not stat.S_ISREG(os.stat(name, dir_fd=directory_fd).st_mode):
                    raise ValueError("Node link resolved destination changed")
                links.append({"path": path, "target": target})
                value = target
            else:
                raise ValueError("output tree contains an unsupported member")
            digest.update(
                json.dumps([path, kind, size, value], separators=(",", ":")).encode() + b"\n"
            )

    if os.fstat(root_fd).st_mode & 0o077:
        raise ValueError("output root is not private")
    walk(root_fd, "")
    if seen != expected.keys():
        raise ValueError("output tree lacks an expected member")
    return directories, links, digest.hexdigest()


def extract_batch(
    archives: dict[str, Path],
    specs: list[ArchiveSpec],
    output: Path,
    *,
    free_bytes: Callable[[Path], int] = _free_bytes,
) -> dict[str, object]:
    """Extract admitted synthetic fixtures; retain a partial tree after any failure."""
    if set(archives) != {spec.archive_id for spec in specs} or len(specs) != len(archives):
        raise ValueError("archive IDs differ from the requested batch")
    plans = {spec.archive_id: _preflight(archives[spec.archive_id], spec) for spec in specs}
    if sum(int(spec.report["regular_content_upper_bytes"]) for spec in specs) > CONTENT_CAP:
        raise ValueError("batch regular content exceeds its exact bound")
    parent = output.parent
    if parent.is_symlink() or not parent.is_dir() or output.name in {"", ".", ".."}:
        raise ValueError("output parent must be an existing private directory")
    if free_bytes(parent) < FREE_FLOOR:
        raise ValueError("mounted free space is below the floor")
    parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.mkdir(output.name, mode=0o700, dir_fd=parent_fd)
        root_fd = os.open(
            output.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd
        )
    finally:
        os.close(parent_fd)
    total = [0]
    rows: list[dict[str, object]] = []
    try:
        if free_bytes(output) < FREE_FLOOR:
            raise ValueError("mounted free space fell below the floor")

        def free() -> int:
            return free_bytes(output)

        for spec in specs:
            archive_fd = _open_dir(root_fd, spec.archive_id, free=free)
            try:
                archive_start = total[0]
                written_digests: dict[str, str] = {}
                if spec.report["format"] == "tar":
                    with tarfile.open(archives[spec.archive_id], "r|*") as tar_source:
                        for tar_member, (raw_name, kind, size, _) in zip(
                            tar_source, plans[spec.archive_id], strict=True
                        ):
                            observed_kind = (
                                "directory"
                                if tar_member.isdir()
                                else "regular"
                                if tar_member.isfile()
                                else "symlink"
                                if tar_member.issym()
                                else "special"
                            )
                            if (
                                tar_member.name.rstrip("/") != raw_name
                                or tar_member.size != size
                                or observed_kind != kind
                            ):
                                raise ValueError("archive changed after preflight")
                            name = _normalize(raw_name, spec.archive_id)
                            if name is None:
                                continue
                            if kind == "directory":
                                fd = _parent_fd(archive_fd, name.split("/"), free=free)
                                os.close(fd)
                            elif kind == "regular":
                                tar_stream = tar_source.extractfile(tar_member)
                                if tar_stream is None:
                                    raise ValueError("regular tar member has no content")
                                with tar_stream:
                                    written_digests[name] = _write_stream(
                                        archive_fd,
                                        name,
                                        tar_stream,
                                        size,
                                        total,
                                        free,
                                    )
                else:
                    with zipfile.ZipFile(archives[spec.archive_id]) as zip_source:
                        for zip_member, (raw_name, kind, size, _) in zip(
                            zip_source.infolist(), plans[spec.archive_id], strict=True
                        ):
                            zip_mode = stat.S_IFMT(zip_member.external_attr >> 16)
                            observed_kind = (
                                "directory"
                                if zip_member.is_dir()
                                else "regular"
                                if zip_mode in {0, stat.S_IFREG}
                                else "special"
                            )
                            if (
                                zip_member.filename.rstrip("/") != raw_name
                                or zip_member.file_size != size
                                or observed_kind != kind
                            ):
                                raise ValueError("archive changed after preflight")
                            name = _normalize(raw_name, spec.archive_id)
                            if name is None:
                                continue
                            if kind == "directory":
                                fd = _parent_fd(archive_fd, name.split("/"), free=free)
                                os.close(fd)
                            elif kind == "regular":
                                with zip_source.open(zip_member) as zip_stream:
                                    written_digests[name] = _write_stream(
                                        archive_fd,
                                        name,
                                        zip_stream,
                                        size,
                                        total,
                                        free,
                                    )
                if total[0] - archive_start != spec.report["regular_content_upper_bytes"]:
                    raise ValueError("archive content differs from its exact bound")
                for raw_name, kind, size, _ in plans[spec.archive_id]:
                    name = _normalize(raw_name, spec.archive_id)
                    if name is None or kind != "regular":
                        continue
                    parent_fd = _parent_fd(archive_fd, name.split("/")[:-1], create=False)
                    try:
                        fd = os.open(
                            name.split("/")[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd
                        )
                        try:
                            if (
                                not stat.S_ISREG(os.fstat(fd).st_mode)
                                or os.fstat(fd).st_size != size
                            ):
                                raise ValueError("regular output changed before readback")
                            digest = hashlib.sha256()
                            with os.fdopen(os.dup(fd), "rb") as stream:
                                for chunk in iter(lambda: stream.read(CHUNK), b""):
                                    digest.update(chunk)
                        finally:
                            os.close(fd)
                    finally:
                        os.close(parent_fd)
                    if digest.hexdigest() != written_digests[name]:
                        raise ValueError("regular output changed before readback")
                    if spec.source_files is not None:
                        assert spec.source_prefix is not None
                        relative = name[len(spec.source_prefix) + 1 :]
                        if digest.hexdigest() != spec.source_files[relative]["sha256"]:
                            raise ValueError("regular output differs from frozen source inventory")
                    rows.append(
                        {
                            "archive_id": spec.archive_id,
                            "path": name,
                            "bytes": size,
                            "sha256": digest.hexdigest(),
                        }
                    )
                if free_bytes(output) < FREE_FLOOR:
                    raise ValueError("mounted free space fell below the floor")
            finally:
                os.close(archive_fd)
        for spec in specs:
            archive = archives[spec.archive_id]
            if (
                archive.stat().st_size != spec.archive_bytes
                or _sha256(archive) != spec.archive_sha256
            ):
                raise ValueError("archive changed during extraction")
        if "node" in plans:
            _create_node_links(root_fd, plans["node"], free)
        directories, links, tree_sha256 = _verify_output_tree(root_fd, specs, plans, rows)
        manifest = {
            "archive_ids": sorted(archives),
            "content_bytes": total[0],
            "directories": directories,
            "files": rows,
            "links": links,
            "tree_sha256": tree_sha256,
        }
        data = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        if free_bytes(output) < FREE_FLOOR:
            raise ValueError("mounted free space fell below the floor")
        if len(data) > 8 * 1024 * 1024:
            raise ValueError("bounded manifest exceeds eight MiB")
        fd = os.open(
            "manifest.json",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=root_fd,
        )
        try:
            remaining = memoryview(data)
            while remaining:
                count = os.write(fd, remaining)
                if count <= 0:
                    raise OSError("short manifest write")
                remaining = remaining[count:]
            os.fsync(fd)
        finally:
            os.close(fd)
        if free_bytes(output) < FREE_FLOOR:
            raise ValueError("mounted free space fell below the floor")
        return manifest
    finally:
        os.close(root_fd)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    ledger = json.loads(LEDGER.read_text())
    proposal = ledger["archive_extraction_proposal"]
    if (
        not proposal["extraction_admitted"]
        or not proposal["owner_extraction_decision"]
        or proposal["extractor_sha256"] != _sha256(Path(__file__))
    ):
        raise ValueError("retained archive extraction has no separate exact-hash admission")
    if (
        args.archive_root != MOUNT / "archives"
        or proposal["output_root"] is None
        or args.output != Path(proposal["output_root"])
        or args.output.parent != MOUNT
        or MOUNT.is_symlink()
        or not os.path.ismount(MOUNT)
    ):
        raise ValueError("retained archive or output path differs from the admitted mount path")
    specs = load_bound_policy()
    archives = {spec.archive_id: args.archive_root / (spec.archive_id + ".blob") for spec in specs}
    print(json.dumps(extract_batch(archives, specs, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
