"""Assemble reviewed local data. This script performs no Linux operation."""

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import zipfile


def prepare(inputs: Path, output: Path, source: Path) -> None:
    if output.exists():
        raise ValueError("immutable input output must be new")
    output.mkdir(mode=0o700)
    records: dict[str, dict[str, object]] = {}

    def write(name: str, data: bytes, mode: int = 0o444) -> None:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or str(path) != name:
            raise ValueError("canonical relative immutable input path required")
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(mode)
        records[name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "mode": mode,
        }

    for wheel in sorted((inputs / "wheels").glob("*.whl")):
        if wheel.name.startswith("setuptools-"):
            continue
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if name.endswith("/") or ".dist-info/" in name:
                    continue
                write("lib/" + name, archive.read(name))
    for path in sorted((source / "src/crewshal").glob("*")):
        if path.suffix in {".py", ".c"}:
            write("lib/crewshal/" + path.name, path.read_bytes())
    for path in sorted((inputs / "assets").rglob("*")):
        if path.is_file():
            write("assets/" + str(path.relative_to(inputs / "assets")), path.read_bytes())
    archive_path = inputs / "official-codex-package-v1.tar.gz"
    expected = "dff0954438fa455c2197ddb1f421d8d68625d98de610f76bedb6e5bc837ea35b"
    with archive_path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError("official native archive differs from the reviewed input")
    with tarfile.open(archive_path) as archive:
        for name in (
            "bin/codex",
            "codex-resources/bwrap",
            "codex-path/rg",
            "codex-resources/zsh/bin/zsh",
        ):
            member = archive.getmember(name)
            if not member.isfile():
                raise ValueError("reviewed native member is not a regular file")
            stream = archive.extractfile(member)
            assert stream is not None
            write("native/" + name, stream.read(), 0o555)
    for name in (
        "synthetic-tls-cert.pem",
        "synthetic-tls-key.pem",
        "synthetic-model-response-v2.json",
    ):
        write("fixtures/" + name, (inputs / name).read_bytes())
    write("manifest.json", json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    for path in sorted(output.rglob("*"), reverse=True):
        if path.is_dir():
            path.chmod(0o555)
    output.chmod(0o555)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    prepare(args.inputs.resolve(strict=True), args.output, args.source.resolve(strict=True))


if __name__ == "__main__":
    main()
