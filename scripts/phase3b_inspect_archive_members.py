"""Read retained archive metadata without extracting member contents."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import stat
import tarfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

MAX_MEMBERS = 200_000
MAX_REGULAR_BYTES = 15_000_000_000


def _path_findings(name: str) -> list[str]:
    parts = name.rstrip("/").split("/")
    findings = []
    if not name or name.startswith("/"):
        findings.append("absolute_or_empty")
    if any(part in {"", ".", ".."} for part in parts):
        findings.append("noncanonical_path")
    if "." in parts:
        findings.append("dot_component")
    if ".." in parts:
        findings.append("parent_component")
    if "" in parts:
        findings.append("empty_component")
    if "\\" in name:
        findings.append("backslash_path")
    if "\x00" in name:
        findings.append("nul_path")
    return findings


def inspect_archive(archive: Path) -> dict[str, Any]:
    """Return bounded metadata for one verified local archive."""
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("archive must be a regular file")
    with archive.open("rb") as stream:
        is_zip = stream.read(4).startswith(b"PK")

    counts: Counter[str] = Counter()
    findings: Counter[str] = Counter()
    examples: dict[str, list[str]] = {}
    links: list[dict[str, Any]] = []
    seen: set[str] = set()
    seen_canonical: set[str] = set()
    seen_casefold: set[str] = set()
    metadata_digest = hashlib.sha256()
    regular_bytes = 0
    largest_regular_bytes = 0
    members = 0

    def add(name: str, kind: str, size: int, link_target: str = "") -> None:
        nonlocal members, regular_bytes, largest_regular_bytes
        members += 1
        if members > MAX_MEMBERS:
            raise ValueError("member count cap exceeded")
        if size < 0:
            raise ValueError("negative member size")
        normalized = name.rstrip("/")
        member_findings = _path_findings(normalized)
        if normalized in seen:
            member_findings.append("duplicate_name")
        seen.add(normalized)
        canonical = posixpath.normpath(normalized)
        if canonical in seen_canonical:
            member_findings.append("duplicate_canonical_name")
        seen_canonical.add(canonical)
        folded = canonical.casefold()
        if folded in seen_casefold:
            member_findings.append("casefold_collision")
        seen_casefold.add(folded)
        if kind == "regular":
            regular_bytes += size
            largest_regular_bytes = max(largest_regular_bytes, size)
            if regular_bytes > MAX_REGULAR_BYTES:
                raise ValueError("regular content cap exceeded")
        elif kind in {"symlink", "hardlink"}:
            member_findings.append(kind)
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), link_target)
                if kind == "symlink"
                else link_target
            )
            escapes = (
                link_target.startswith("/") or resolved in {"..", "."} or resolved.startswith("../")
            )
            if escapes:
                member_findings.append("escaping_link_target")
            links.append(
                {"name": name, "kind": kind, "target": link_target, "escapes_root": escapes}
            )
        elif kind == "special":
            member_findings.append("special_member")
        counts[kind] += 1
        for finding in set(member_findings):
            findings[finding] += 1
            sample = examples.setdefault(finding, [])
            if len(sample) < 4:
                sample.append(name)
        metadata_digest.update(
            json.dumps(
                [name, kind, size, link_target], ensure_ascii=True, separators=(",", ":")
            ).encode()
            + b"\n"
        )

    if is_zip:
        with zipfile.ZipFile(archive) as zip_source:
            for zip_member in zip_source.infolist():
                file_type = stat.S_IFMT(zip_member.external_attr >> 16)
                kind = (
                    "directory"
                    if zip_member.is_dir()
                    else "symlink"
                    if file_type == stat.S_IFLNK
                    else "regular"
                    if file_type in {0, stat.S_IFREG}
                    else "special"
                )
                add(zip_member.filename, kind, zip_member.file_size)
                if zip_member.flag_bits & 1:
                    findings["encrypted_member"] += 1
                if zip_member.compress_type not in {0, 8, 12, 14}:
                    findings["unsupported_zip_method"] += 1
    else:
        with tarfile.open(archive, mode="r|*") as tar_source:
            for tar_member in tar_source:
                kind = (
                    "directory"
                    if tar_member.isdir()
                    else "regular"
                    if tar_member.isfile()
                    else "symlink"
                    if tar_member.issym()
                    else "hardlink"
                    if tar_member.islnk()
                    else "special"
                )
                add(
                    tar_member.name,
                    kind,
                    tar_member.size,
                    tar_member.linkname if kind in {"symlink", "hardlink"} else "",
                )
                if tar_member.sparse:
                    findings["sparse_member"] += 1

    return {
        "id": archive.stem,
        "format": "zip" if is_zip else "tar",
        "archive_bytes": archive.stat().st_size,
        "members": members,
        "counts": dict(sorted(counts.items())),
        "regular_content_upper_bytes": regular_bytes,
        "largest_regular_bytes": largest_regular_bytes,
        "findings": dict(sorted(findings.items())),
        "finding_examples": examples,
        "links": links,
        "member_metadata_sha256": metadata_digest.hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_root", type=Path)
    args = parser.parse_args()
    root = args.archive_root
    if root.is_symlink() or not root.is_dir():
        raise ValueError("archive root must be a directory")
    paths = sorted(root.glob("*.blob"))
    if len(paths) != 16 or any(path.is_symlink() for path in paths):
        raise ValueError("expected exactly sixteen regular archives")
    rows = [inspect_archive(path) for path in paths]
    print(json.dumps({"schema_version": 1, "archives": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
