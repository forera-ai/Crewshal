"""Extract one frozen Phase 3B source archive into a new private directory.

This command has no network path. The operator must admit and supply the archive.
It rejects links, special members, extra files, changed bytes, and unsafe paths.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tarfile


FROZEN = Path(__file__).resolve().parents[1] / "docs/evaluation/phase-3a-frozen"
SELECTED = frozenset({"python-1", "typescript-2", "swift-1", "dotnet-1"})
CHUNK = 1024 * 1024


def _load(name: str) -> dict[str, object]:
    return json.loads((FROZEN / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def extract(repository_id: str, archive: Path, output: Path) -> dict[str, object]:
    if repository_id not in SELECTED:
        raise ValueError("repository is outside the selected development set")
    corpus = next(row for row in _load("corpus.json")["repositories"] if row["id"] == repository_id)
    inventory = next(
        row
        for row in _load("source-inventories.json")["repositories"]
        if row["id"] == repository_id
    )
    source = corpus["source_identity"]
    if (
        archive.stat().st_size != source["archive_bytes"]
        or _sha256(archive) != source["archive_sha256"]
    ):
        raise ValueError("archive size or SHA-256 differs from the frozen source identity")
    expected = {row["path"]: row for row in inventory["files"]}
    if len(expected) != len(inventory["files"]):
        raise ValueError("frozen file inventory contains duplicate paths")
    prefix = corpus["repository"].split("/")[-1] + "-" + corpus["revision"]
    members: dict[str, tarfile.TarInfo] = {}
    with tarfile.open(archive, "r:gz") as source_archive:
        for member in source_archive:
            name = member.name.removesuffix("/")
            path = PurePosixPath(name)
            if (
                not name
                or path.is_absolute()
                or any(part in {"", ".", ".."} for part in name.split("/"))
                or str(path) != name
                or path.parts[0] != prefix
                or not (member.isdir() or member.isfile())
            ):
                raise ValueError("archive contains an unsafe member")
            relative = PurePosixPath(*path.parts[1:])
            if member.isdir():
                continue
            relative_name = str(relative)
            if (
                relative_name not in expected
                or relative_name in members
                or member.size != expected[relative_name]["bytes"]
            ):
                raise ValueError("archive member differs from the frozen file inventory")
            members[relative_name] = member
        if members.keys() != expected.keys():
            raise ValueError("archive file set differs from the frozen file inventory")

        parent = output.parent.resolve(strict=True)
        target_root = parent / output.name
        if output.name in {"", ".", ".."} or target_root.exists() or target_root.is_symlink():
            raise ValueError("output must be a new directory")
        target_root.mkdir(mode=0o700)
        rows = []
        for relative_name in sorted(members):
            member = members[relative_name]
            target = target_root.joinpath(*PurePosixPath(relative_name).parts)
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            stream = source_archive.extractfile(member)
            if stream is None:
                raise ValueError("regular archive member has no data")
            digest = hashlib.sha256()
            size = 0
            with stream, target.open("xb") as destination:
                while chunk := stream.read(CHUNK):
                    size += len(chunk)
                    if size > member.size:
                        raise ValueError("archive member exceeds its declared size")
                    destination.write(chunk)
                    digest.update(chunk)
            if size != member.size or digest.hexdigest() != expected[relative_name]["sha256"]:
                raise ValueError("extracted file differs from the frozen inventory")
            os.chmod(target, 0o700 if member.mode & 0o111 else 0o600)
            rows.append({"path": relative_name, "bytes": size, "sha256": digest.hexdigest()})
    serialized = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    inventory_digest = hashlib.sha256(serialized).hexdigest()
    if inventory_digest != inventory["source_inventory_sha256"]:
        raise ValueError("extracted inventory digest differs from the frozen inventory")
    return {
        "repository_id": repository_id,
        "archive_sha256": source["archive_sha256"],
        "source_inventory_sha256": inventory_digest,
        "files": len(rows),
        "content_bytes": sum(row["bytes"] for row in rows),
        "output": str(target_root),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_id", choices=sorted(SELECTED))
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(args.repository_id, args.archive, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
