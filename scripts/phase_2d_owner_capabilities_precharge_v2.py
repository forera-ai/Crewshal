"""Prepare the exact owner input capabilities after separate batch approval.

This entry does not compile, load AppArmor, authenticate, or start the observer.
Its input capabilities precede the original observer's installation work.
Every new path is exclusive. Failure leaves partial inputs in place.
"""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import tarfile


ARCHIVE = Path("/var/lib/crewshal-phase2d-owner-inputs-v2.tar")
INPUT = Path("/var/lib/crewshal-phase2d-input-v2")
STORAGE = Path("/var/lib/crewshal-phase2d-storage-v2")
ARCHIVE_SHA256 = "40a0b65cee3315476e6f12a382ebff8feb3014110c42295cb89f7607a3d63081"
MANIFEST_SHA256 = "6fd3071baf7fb21f1e8b44413a8fb996f0d3e0452e01503f6df17821bcd86822"
ARCHIVE_BYTES = 15923200
NATIVE = Path("/var/tmp/crewshal-native-qualification-v18/root/opt/codex")
NATIVE_FILES = {
    "bin/codex": "fbbaec80443919f86dd63648a0b62759cf6f1d0e09310602fde96885e0bceb3e",
    "codex-resources/bwrap": "c547cbdc762a70ed216789ffaa4c6c0e7d2beabe32245a498f8e365a9fc8dab4",
}
UNITS = (
    "crewshal-2d-20261012v1.slice",
    "crewshal-2d-20261013v2-observer.service",
)


def exact_file(path: Path, expected: str) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        if (
            not stat.S_ISREG(before.st_mode)
            or (before.st_uid, before.st_gid) != (0, 0)
            or before.st_nlink != 1
            or before.st_mode & 0o022
        ):
            raise ValueError("Owner input file has no exclusive protected identity.")
        sha = hashlib.sha256()
        while data := os.read(fd, 65536):
            sha.update(data)
        after = os.fstat(fd)
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if sha.hexdigest() != expected or any(
            getattr(before, field) != getattr(after, field) for field in fields
        ):
            raise ValueError("Owner input file bytes or identity changed.")
    finally:
        os.close(fd)


def prepare() -> None:
    # CPython can add this locale after an empty-environment exec.
    if os.environ:
        if (
            sys.platform != "linux"
            or not sys.flags.isolated
            or not sys.flags.no_site
            or not sys.flags.dont_write_bytecode
            or dict(os.environ) != {"LC_CTYPE": "C.UTF-8"}
        ):
            raise ValueError("The isolated entry inherited an environment.")
        with open("/proc/self/environ", "rb") as inherited:
            if inherited.read(1):
                raise ValueError("The isolated entry inherited an environment.")
        del os.environ["LC_CTYPE"]
    if (
        sys.platform != "linux"
        or platform.machine() != "aarch64"
        or os.uname().release != "7.0.0-38-generic"
        or (os.getuid(), os.getgid()) != (0, 0)
        or os.environ
        or sys.version_info[:2] != (3, 12)
    ):
        raise ValueError("The exact isolated root Linux owner entry is required.")
    os.umask(0o077)
    exact_file(ARCHIVE, ARCHIVE_SHA256)
    if ARCHIVE.stat().st_size != ARCHIVE_BYTES:
        raise ValueError("The owner input archive size changed.")
    exact_file(
        Path("/usr/bin/python3.12"),
        "c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960",
    )
    for name, sha in NATIVE_FILES.items():
        exact_file(NATIVE / name, sha)
    if any(path.exists() for path in (INPUT, STORAGE)) or any(
        (Path("/etc/systemd/system") / unit).exists() for unit in UNITS[1:]
    ):
        raise ValueError("The original owner capabilities are already present.")
    with tarfile.open(ARCHIVE, "r:") as archive:
        raw_manifest = archive.extractfile("owner-input-manifest.json")
        if raw_manifest is None:
            raise ValueError("The exact owner input manifest is missing.")
        raw = raw_manifest.read(65537)
        if len(raw) > 65536 or hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
            raise ValueError("The owner input manifest changed.")
        manifest = json.loads(raw)
        members = archive.getmembers()
        if (
            len(members) != len(manifest) + 1
            or len(members) > 256
            or len({member.name for member in members}) != len(members)
            or {member.name for member in members} != {*manifest, "owner-input-manifest.json"}
            or sum(member.size for member in members) > 16777216
        ):
            raise ValueError("The exact finite owner input inventory changed.")
        INPUT.mkdir(mode=0o700)
        for member in members:
            name = PurePosixPath(member.name)
            if (
                not member.isfile()
                or name.is_absolute()
                or ".." in name.parts
                or str(name) != member.name
                or (member.uid, member.gid) != (0, 0)
            ):
                raise ValueError("Owner input requires a canonical regular file.")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("The owner input file stream is missing.")
            data = stream.read(member.size + 1)
            if member.name != "owner-input-manifest.json":
                expected = manifest[member.name]
                if (
                    len(data) != expected["bytes"]
                    or hashlib.sha256(data).hexdigest() != expected["sha256"]
                ):
                    raise ValueError("The owner input member differs from its manifest.")
            path = INPUT / member.name
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                view = memoryview(data)
                while view:
                    written = os.write(fd, view)
                    if written <= 0:
                        raise ValueError("The original owner input write is incomplete.")
                    view = view[written:]
                os.fchmod(fd, 0o400 if member.name == "batch.json" else 0o444)
                os.fsync(fd)
            finally:
                os.close(fd)
    for name in NATIVE_FILES:
        target = INPUT / "native" / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        target.touch(mode=0o444, exist_ok=False)
    for path in sorted(INPUT.rglob("*"), reverse=True):
        if path.is_dir():
            path.chmod(0o555)
    STORAGE.mkdir(mode=0o700)
    (STORAGE / "crewshal-phase2d-markers-v1").mkdir(mode=0o700)
    for unit in UNITS:
        text = (INPUT / unit).read_text()
        if unit.endswith(".service"):
            text += "".join(
                "BindReadOnlyPaths="
                + str(NATIVE / name)
                + ":/run/crewshal-phase2d-input-v1/native/"
                + name
                + "\n"
                for name in NATIVE_FILES
            )
        if unit.endswith(".service"):
            text += (
                "BindReadOnlyPaths=" + str(NATIVE / "codex-resources/bwrap") + ":/usr/bin/bwrap\n"
            )
        path = Path("/etc/systemd/system") / unit
        if unit.endswith(".slice"):
            exact_file(path, "52443082382567f718676a9a884a5cc364925d7ed10705a41f94534b8d1dcf40")
            if path.read_text() != text:
                raise ValueError("The retained original aggregate unit changed.")
            continue
        with path.open("x") as stream:
            stream.write(text)
        path.chmod(0o644)
    subprocess.run(["/usr/bin/systemctl", "daemon-reload"], check=True, env={})
    subprocess.run(["/usr/bin/systemctl", "is-active", "--quiet", UNITS[0]], check=True, env={})
    group = Path("/sys/fs/cgroup/crewshal.slice/crewshal-2d.slice") / UNITS[0]
    for key, expected in {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "pids.max": "128",
        "cpu.max": "100000 100000",
    }.items():
        if (group / key).read_text().strip() != expected:
            raise ValueError("The original owner aggregate control differs.")
    (group / "cgroup.subtree_control").write_text("+memory +pids +cpu")
    parent = group.parent
    if not {"memory", "pids", "cpu"} <= set(
        (parent / "cgroup.subtree_control").read_text().split()
    ):
        raise ValueError("The original owner parent controllers are not enabled.")
    print(
        json.dumps(
            {"owner_inputs_prepared": True, "observer_started": False, "compiler_started": False}
        )
    )


if __name__ == "__main__":
    prepare()
