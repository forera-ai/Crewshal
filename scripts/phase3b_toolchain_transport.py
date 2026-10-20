"""Build and stage a bounded offline transport for the retained Phase 3B outputs.

The production commands require separate admission. Importable functions support
small synthetic fixtures without a guest or the retained archives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess
import tarfile
import unicodedata
from typing import Any


CHUNK = 1024 * 1024
CONTENT_CAP = 4_371_619_599
TAR_CAP = 5_368_709_120
ISO_CAP = 6_442_450_944
HOST_FREE_FLOOR = 68_719_476_736
GUEST_FREE_FLOOR = 42_949_672_960
SOURCE_SPECS = (
    (
        "part-12",
        Path("/Volumes/CrewshalPhase3BArchiveStage/extracted-12-v1"),
        "13e41f6e8156afd0e4284af200a1ac99f89b46aae7fbfd8f012933d5b56b4529",
    ),
    (
        "part-4",
        Path("/Volumes/CrewshalPhase3BRemainingStage/extracted-4-v1"),
        "4075234d7996789333e62cd082b7c408abed38a26d0fd5d3fff2de666f39e79d",
    ),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(CHUNK):
            value.update(block)
    return value.hexdigest()


def safe_path(name: str) -> str:
    if (
        not name
        or name.startswith("/")
        or "\\" in name
        or "\x00" in name
        or any(part in {"", ".", ".."} for part in name.split("/"))
    ):
        raise ValueError(f"unsafe transport path: {name!r}")
    return name


def _link_target(path: str, target: str) -> str:
    if not target or target.startswith("/") or "\\" in target or "\x00" in target:
        raise ValueError("unsafe link target")
    parts = path.split("/")[:-1]
    for part in target.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise ValueError("link leaves transport root")
            parts.pop()
        else:
            parts.append(part)
    return safe_path("/".join(parts))


def load_manifest(path: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    if expected_sha256 is not None and digest(path) != expected_sha256:
        raise ValueError("output manifest digest differs")
    data: dict[str, Any] = json.loads(path.read_text())
    if set(data) != {
        "archive_ids",
        "content_bytes",
        "directories",
        "files",
        "links",
        "tree_sha256",
    }:
        raise ValueError("unexpected output manifest fields")
    ids = data["archive_ids"]
    if len(ids) != len(set(ids)) or any(safe_path(item) != item or "/" in item for item in ids):
        raise ValueError("invalid archive IDs")
    files: dict[str, dict[str, Any]] = {}
    for row in data["files"]:
        if set(row) != {"archive_id", "bytes", "path", "sha256"}:
            raise ValueError("unexpected file entry")
        if row["archive_id"] not in ids or not isinstance(row["bytes"], int) or row["bytes"] < 0:
            raise ValueError("invalid file entry")
        name = safe_path(row["archive_id"] + "/" + safe_path(row["path"]))
        if name in files:
            raise ValueError("duplicate file")
        files[name] = row
    directories = {safe_path(name) for name in data["directories"]}
    if len(directories) != len(data["directories"]):
        raise ValueError("duplicate directory")
    links: dict[str, str] = {}
    for row in data["links"]:
        if set(row) != {"path", "target"}:
            raise ValueError("unexpected link entry")
        name = safe_path(row["path"])
        if name in links:
            raise ValueError("duplicate link")
        links[name] = row["target"]
    all_names = list(files) + list(directories) + list(links)
    if len(all_names) != len(set(all_names)):
        raise ValueError("file, directory, or link collision")
    folded: set[str] = set()
    for name in all_names:
        alias = unicodedata.normalize("NFC", name).casefold()
        if alias in folded:
            raise ValueError("case alias in output manifest")
        folded.add(alias)
        for parent in PurePosixPath(name).parents:
            if str(parent) == ".":
                break
            if str(parent) not in directories:
                raise ValueError("missing parent directory")
    if sum(row["bytes"] for row in files.values()) != data["content_bytes"]:
        raise ValueError("content count differs")
    for name, target in links.items():
        resolved = _link_target(name, target)
        if resolved not in files and resolved not in directories and resolved not in links:
            raise ValueError("link target is absent")
    return data


def _expected(
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], set[str], dict[str, str]]:
    files = {row["archive_id"] + "/" + row["path"]: row for row in manifest["files"]}
    return (
        files,
        set(manifest["directories"]),
        {row["path"]: row["target"] for row in manifest["links"]},
    )


def verify_source(root: Path, manifest: dict[str, Any]) -> None:
    files, directories, links = _expected(manifest)
    seen_files: set[str] = set()
    seen_dirs: set[str] = set()
    seen_links: set[str] = set()
    for current, names, filenames in os.walk(root, followlinks=False):
        parent = Path(current)
        if parent != root:
            seen_dirs.add(parent.relative_to(root).as_posix())
        for name in names + filenames:
            path = parent / name
            rel = path.relative_to(root).as_posix()
            mode = path.lstat().st_mode
            if rel == "manifest.json" and stat.S_ISREG(mode):
                continue
            if stat.S_ISLNK(mode):
                if rel not in links or os.readlink(path) != links[rel]:
                    raise ValueError("source link differs")
                seen_links.add(rel)
                if name in names:
                    names.remove(name)
            elif stat.S_ISREG(mode):
                row = files.get(rel)
                if (
                    row is None
                    or path.stat().st_size != row["bytes"]
                    or digest(path) != row["sha256"]
                ):
                    raise ValueError("source file differs")
                seen_files.add(rel)
            elif stat.S_ISDIR(mode):
                if rel not in directories:
                    raise ValueError("extra source directory")
            else:
                raise ValueError("special source member")
    if seen_files != set(files) or seen_dirs != directories or seen_links != set(links):
        raise ValueError("source tree inventory differs")


def _tar_info(name: str, kind: bytes, size: int = 0, target: str = "") -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.type = kind
    info.size = size
    info.linkname = target
    info.mode = 0o700 if kind == tarfile.DIRTYPE else 0o600
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    return info


def _tar_total_bytes(directory: Path) -> int:
    return sum(path.stat().st_size for path in directory.glob("*.tar"))


def pack_part(root: Path, manifest: dict[str, Any], output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(output)
    if (
        shutil.disk_usage(output.parent).free
        < HOST_FREE_FLOOR + manifest["content_bytes"] + 8_388_608
    ):
        raise ValueError("host free space cannot retain floor")
    files, directories, links = _expected(manifest)
    try:
        with tarfile.open(output, "x", format=tarfile.PAX_FORMAT) as archive:
            for name in sorted(directories):
                archive.addfile(_tar_info(name, tarfile.DIRTYPE))
            for name in sorted(files):
                row = files[name]
                if _tar_total_bytes(output.parent) + row["bytes"] + 8_388_608 > TAR_CAP:
                    raise ValueError("combined transport tars exceed cap")
                if (
                    shutil.disk_usage(output.parent).free
                    < HOST_FREE_FLOOR + row["bytes"] + 8_388_608
                ):
                    raise ValueError("host free space fell below prospective floor")
                with (root / name).open("rb") as source:
                    archive.addfile(_tar_info(name, tarfile.REGTYPE, row["bytes"]), source)
                if output.stat().st_size > TAR_CAP:
                    raise ValueError("transport tar exceeds cap")
                if _tar_total_bytes(output.parent) > TAR_CAP:
                    raise ValueError("combined transport tars exceed cap")
                if shutil.disk_usage(output.parent).free < HOST_FREE_FLOOR:
                    raise ValueError("host free space fell below floor")
            for name, target in sorted(links.items()):
                archive.addfile(_tar_info(name, tarfile.SYMTYPE, target=target))
        if output.stat().st_size > TAR_CAP:
            raise ValueError("transport tar exceeds cap")
        if _tar_total_bytes(output.parent) > TAR_CAP:
            raise ValueError("combined transport tars exceed cap")
        verify_tar(output, manifest)
        return {"bytes": output.stat().st_size, "sha256": digest(output)}
    except Exception:
        # Retain partial output for diagnosis. A later attempt needs a new decision.
        raise


def verify_tar(path: Path, manifest: dict[str, Any]) -> None:
    files, directories, links = _expected(manifest)
    seen_files: set[str] = set()
    seen_dirs: set[str] = set()
    seen_links: set[str] = set()
    total = 0
    with tarfile.open(path, "r:") as archive:
        for member in archive:
            name = safe_path(member.name.removesuffix("/") if member.isdir() else member.name)
            if member.isdir():
                if name not in directories or name in seen_dirs:
                    raise ValueError("unexpected tar directory")
                seen_dirs.add(name)
            elif member.isfile():
                row = files.get(name)
                if row is None or name in seen_files or member.size != row["bytes"]:
                    raise ValueError("unexpected tar file")
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError("missing tar stream")
                value = hashlib.sha256()
                size = 0
                while block := source.read(CHUNK):
                    value.update(block)
                    size += len(block)
                if size != member.size or value.hexdigest() != row["sha256"]:
                    raise ValueError("tar content differs")
                total += size
                seen_files.add(name)
            elif member.issym():
                if name not in links or name in seen_links or member.linkname != links[name]:
                    raise ValueError("unexpected tar link")
                seen_links.add(name)
            else:
                raise ValueError("unsupported tar member")
    if seen_files != set(files) or seen_dirs != directories or seen_links != set(links):
        raise ValueError("tar inventory differs")
    if total != manifest["content_bytes"]:
        raise ValueError("tar content bound differs")


def stage_part(path: Path, manifest: dict[str, Any], destination: Path, total: list[int]) -> None:
    files, directories, links = _expected(manifest)
    verify_tar(path, manifest)
    for name in sorted(directories, key=lambda value: (value.count("/"), value)):
        (destination / name).mkdir(mode=0o700)
    with tarfile.open(path, "r:") as archive:
        for member in archive:
            if not member.isfile():
                continue
            name = safe_path(member.name)
            row = files[name]
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("missing tar stream")
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(destination / name, flags, 0o600)
            with os.fdopen(descriptor, "wb") as output:
                value = hashlib.sha256()
                size = 0
                while block := source.read(CHUNK):
                    if total[0] + len(block) > CONTENT_CAP:
                        raise ValueError("guest content exceeds cap")
                    if shutil.disk_usage(destination).free < GUEST_FREE_FLOOR + len(block):
                        raise ValueError("guest free space below prospective floor")
                    output.write(block)
                    size += len(block)
                    total[0] += len(block)
                    value.update(block)
                    if shutil.disk_usage(destination).free < GUEST_FREE_FLOOR:
                        raise ValueError("guest free space below floor")
            if size != row["bytes"] or value.hexdigest() != row["sha256"]:
                raise ValueError("guest file differs")
    for name, target in sorted(links.items()):
        _link_target(name, target)
        os.symlink(target, destination / name)
    for name in links:
        (destination / name).resolve(strict=True).relative_to(destination.resolve())


def _run() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("check")
    pack = sub.add_parser("pack")
    pack.add_argument("destination", type=Path)
    iso = sub.add_parser("iso")
    iso.add_argument("bundle", type=Path)
    iso.add_argument("output", type=Path)
    stage = sub.add_parser("stage")
    stage.add_argument("bundle", type=Path)
    stage.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.mode in {"check", "pack"}:
        manifests = []
        for label, root, expected in SOURCE_SPECS:
            manifest = load_manifest(root / "manifest.json", expected)
            verify_source(root, manifest)
            manifests.append((label, root, manifest))
        if sum(x[2]["content_bytes"] for x in manifests) != CONTENT_CAP:
            raise ValueError("selected content bound differs")
        if args.mode == "check":
            print(
                json.dumps(
                    {"parts": len(manifests), "content_bytes": CONTENT_CAP, "status": "matched"}
                )
            )
            return
        args.destination.mkdir(mode=0o700)
        parts = []
        for label, root, manifest in manifests:
            output = args.destination / (label + ".tar")
            item = pack_part(root, manifest, output)
            target = args.destination / (label + "-manifest.json")
            shutil.copyfile(root / "manifest.json", target)
            parts.append(
                {
                    "label": label,
                    "tar": output.name,
                    "manifest": target.name,
                    "manifest_sha256": digest(target),
                    **item,
                }
            )
        shutil.copyfile(Path(__file__), args.destination / "phase3b_toolchain_transport.py")
        bundle = {"version": 1, "content_bytes": CONTENT_CAP, "parts": parts}
        (args.destination / "bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")
        print(json.dumps(bundle, sort_keys=True))
        return
    if args.mode == "iso":
        if args.output.exists():
            raise FileExistsError(args.output)
        expected_names = {
            "part-12.tar",
            "part-4.tar",
            "part-12-manifest.json",
            "part-4-manifest.json",
            "phase3b_toolchain_transport.py",
            "bundle.json",
        }
        if {path.name for path in args.bundle.iterdir()} != expected_names:
            raise ValueError("transport directory differs")
        if any(not path.is_file() or path.is_symlink() for path in args.bundle.iterdir()):
            raise ValueError("transport directory has nonregular member")
        if digest(args.bundle / "phase3b_toolchain_transport.py") != digest(Path(__file__)):
            raise ValueError("transport script differs")
        if _tar_total_bytes(args.bundle) > TAR_CAP:
            raise ValueError("combined transport tars exceed cap")
        if shutil.disk_usage(args.output.parent).free < HOST_FREE_FLOOR + ISO_CAP:
            raise ValueError("host free space cannot retain ISO floor")
        bundle = json.loads((args.bundle / "bundle.json").read_text())
        if bundle["version"] != 1 or bundle["content_bytes"] != CONTENT_CAP:
            raise ValueError("transport bundle differs")
        if [item["label"] for item in bundle["parts"]] != [x[0] for x in SOURCE_SPECS]:
            raise ValueError("transport part list differs")
        for item, (label, _, expected) in zip(bundle["parts"], SOURCE_SPECS, strict=True):
            if item["tar"] != label + ".tar" or item["manifest"] != label + "-manifest.json":
                raise ValueError("transport filename differs")
            if item["manifest_sha256"] != expected:
                raise ValueError("transport manifest pin differs")
            manifest = load_manifest(args.bundle / item["manifest"], expected)
            path = args.bundle / item["tar"]
            if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
                raise ValueError("transport tar differs before ISO build")
            verify_tar(path, manifest)

        def limit_file() -> None:
            resource.setrlimit(resource.RLIMIT_FSIZE, (ISO_CAP, ISO_CAP))

        subprocess.run(
            ["hdiutil", "makehybrid", "-udf", "-o", str(args.output), str(args.bundle)],
            check=True,
            preexec_fn=limit_file,
        )
        if args.output.stat().st_size > ISO_CAP:
            raise ValueError("transport ISO exceeds cap")
        if shutil.disk_usage(args.output.parent).free < HOST_FREE_FLOOR:
            raise ValueError("host free space fell below floor")
        print(json.dumps({"iso_bytes": args.output.stat().st_size, "sha256": digest(args.output)}))
        return
    bundle = json.loads((args.bundle / "bundle.json").read_text())
    if bundle["version"] != 1 or bundle["content_bytes"] != CONTENT_CAP:
        raise ValueError("transport bundle differs")
    if [item["label"] for item in bundle["parts"]] != [x[0] for x in SOURCE_SPECS]:
        raise ValueError("transport part list differs")
    loaded = []
    for item, (label, _, expected) in zip(bundle["parts"], SOURCE_SPECS, strict=True):
        if item["tar"] != label + ".tar" or item["manifest"] != label + "-manifest.json":
            raise ValueError("transport filename differs")
        if item["manifest_sha256"] != expected:
            raise ValueError("transport manifest pin differs")
        manifest = load_manifest(args.bundle / item["manifest"], expected)
        path = args.bundle / item["tar"]
        if (
            path.stat().st_size != item["bytes"]
            or path.stat().st_size > TAR_CAP
            or digest(path) != item["sha256"]
        ):
            raise ValueError("transport tar pin differs")
        verify_tar(path, manifest)
        loaded.append((path, manifest))
    if shutil.disk_usage(args.destination.parent).free < GUEST_FREE_FLOOR + CONTENT_CAP:
        raise ValueError("guest free space cannot retain floor")
    args.destination.mkdir(mode=0o700)
    total = [0]
    for path, manifest in loaded:
        stage_part(path, manifest, args.destination, total)
    if total[0] != CONTENT_CAP:
        raise ValueError("guest content readback differs")
    print(json.dumps({"status": "staged", "content_bytes": total[0]}))


if __name__ == "__main__":
    _run()
