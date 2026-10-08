"""Verify archived research; optionally recheck fresh pinned archive data, never execute it."""

import argparse
import hashlib
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_HASH = "edd86e2f21559e190723fd884c3a1dced161a555afdff85c5921ed45e7d6d56e"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inline_build_info(binary):
    marker = b"\xff Go buildinf:"
    offset = binary.find(marker)
    require(offset >= 0, "missing Go build information")
    require(binary[offset + 15] & 2, "unsupported pointer build-information format")
    cursor = offset + 32

    def read_string():
        nonlocal cursor
        length = shift = 0
        while True:
            require(cursor < len(binary) and shift < 64, "invalid build string length")
            value = binary[cursor]
            cursor += 1
            length |= (value & 127) << shift
            if value < 128:
                break
            shift += 7
        require(cursor + length <= len(binary), "truncated build string")
        result = binary[cursor : cursor + length]
        cursor += length
        return result

    version = read_string().decode()
    framed = read_string()
    require(len(framed) >= 32, "missing module framing")
    return version, framed[16:-16].decode().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="optional fresh public pinned tar.gz")
    args = parser.parse_args()
    record = json.loads(
        (ROOT / "docs/qualification/phase-2c-sbx-storage-research-v1.json").read_text()
    )
    for flag in ("execution_allowed", "native_start_allowed", "operational_manifest_frozen"):
        require(record[flag] is False, "research cannot grant execution or freeze")
    require(record["archive_sha256"] == ARCHIVE_HASH, "archive identity changed")
    for binding in record["source_bindings"]:
        path = (ROOT / binding["path"]).resolve()
        require(path.is_relative_to(ROOT / "docs/qualification"), "binding escaped evidence")
        data = path.read_bytes()
        require(len(data) == binding["bytes"], "source byte count changed")
        require(hashlib.sha256(data).hexdigest() == binding["sha256"], "source bytes changed")
    for name in ("provenance", "sbom"):
        statement = json.loads(
            (ROOT / f"docs/qualification/phase-2c-sbx-storage-{name}-v1.json").read_text()
        )
        require(statement["subject"][0]["digest"]["sha256"] == ARCHIVE_HASH, "wrong subject")
    dependency = next(
        item
        for item in record["dependencies"]
        if item["module"] == "github.com/containerd/containerd/v2"
    )
    require(
        dependency["replacement"]["module"] == "github.com/docker/docker-next-containerd/v2"
        and dependency["replacement"]["version"] == "v2.3.5-internal.2",
        "upstream containerd cannot replace the recorded fork",
    )
    if args.archive:
        with args.archive.open("rb") as handle:
            require(
                hashlib.file_digest(handle, "sha256").hexdigest() == ARCHIVE_HASH,
                "unapproved archive bytes",
            )
        require(args.archive.stat().st_size == record["archive_bytes"], "wrong archive size")
        with tarfile.open(args.archive, "r:gz") as archive:
            names = [member.name for member in archive.getmembers()]
            require(len(names) == len(set(names)), "duplicate archive names")
            for binding in record["bundle"]:
                member = archive.getmember(binding["path"])
                require(member.isfile() and member.size == binding["bytes"], "wrong member")
                with archive.extractfile(member) as handle:
                    data = handle.read()
                require(hashlib.sha256(data).hexdigest() == binding["sha256"], "member changed")
                if member.name == "docker-sbx/sbx":
                    version, lines = inline_build_info(data)
                    require(version == record["go_version"], "Go version changed")
                    require(record["main_module"] in lines, "main module changed")
                    require(
                        all(line in lines for line in record["build_settings"]),
                        "build metadata changed",
                    )
                    require(
                        "=>\tgithub.com/docker/docker-next-containerd/v2\tv2.3.5-internal.2\t"
                        in lines,
                        "private replacement missing",
                    )
                    require(
                        all(signal.encode() in data for signal in record["string_signals"]),
                        "recorded literal missing",
                    )
                    require(
                        all(
                            symbol.encode() + b"\0" in data for symbol in record["storage_symbols"]
                        ),
                        "recorded symbol missing",
                    )
    print(
        json.dumps(
            {
                "source_statement_bindings_verified": len(record["source_bindings"]),
                "fresh_archive_verified": bool(args.archive),
                "bundled_code_executed": False,
                "execution_allowed": False,
                "native_start_allowed": False,
                "operational_manifest_frozen": False,
                "qualification_status": "denied; research readback only",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
