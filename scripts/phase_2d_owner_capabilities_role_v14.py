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
import sqlite3
import subprocess
import sys
import tarfile


ARCHIVE = Path("/var/lib/crewshal-phase2d-owner-inputs-v14.tar")
INPUT = Path("/var/lib/crewshal-phase2d-input-v14")
STORAGE = Path("/var/lib/crewshal-phase2d-storage-v14")
ARCHIVE_SHA256 = "82a82f00daa84ac35859c397d0857ff4a8432aa524518e99a0e651488c617046"
MANIFEST_SHA256 = "3e83875b8a3fe7297dfa748631ab068e4cfd4a40a5287eb8e4d9dcff2ef63485"
ARCHIVE_BYTES = 26583040
NATIVE = Path("/var/tmp/crewshal-native-qualification-v18/root/opt/codex")
NATIVE_FILES = {
    "bin/codex": "fbbaec80443919f86dd63648a0b62759cf6f1d0e09310602fde96885e0bceb3e",
    "codex-resources/bwrap": "c547cbdc762a70ed216789ffaa4c6c0e7d2beabe32245a498f8e365a9fc8dab4",
}
UNITS = (
    "crewshal-2d-20261015v14.slice",
    "crewshal-2d-20261015v14-observer.service",
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
    prior = (
        (
            2,
            "8da77577ceb30d96c9e82ee72fa004a3157d34b02ce2efabaf1ffb1f08ca59a8",
            "56b0945cfb4a6d31d1b811eb9e5e6e0db844b116aceb61544de990684973870d",
        ),
        (
            3,
            "962a3c23383981728557e1d3fe04bf0439581af7582f839629a86a70549a75ad",
            "dd4ef6d86f7e7fb37decae74161edfb16cd2bc3a3c240eef781f36390f862f38",
        ),
    )
    prior = (
        *prior,
        (
            4,
            "86f685083042a03b3f27bb0eee436d9d1c04ecf2f88ba8985c91673b54b43e1f",
            "cd1e79c5526119601e0c46f03ea5b537f82d218e475c9ba75d67e9e27552b886",
        ),
    )
    if not all(
        Path("/proc/" + str(pid)).exists() for pid in (5553, 5555, 6476, 6478, 7157, 7159, 7168)
    ):
        raise ValueError("The original observer and stopped timer are no longer retained.")
    original_db = os.stat("/proc/5553/fd/15")
    retained_db = Path(
        "/var/lib/crewshal-phase2d-storage-v4/crewshal-phase2d-journal-v1/coordinator.sqlite3"
    ).stat()
    if (original_db.st_dev, original_db.st_ino) != (retained_db.st_dev, retained_db.st_ino):
        raise ValueError("The original live journal FD identity changed.")
    prior = (
        *prior,
        (
            5,
            "ebcd9bd415699d422390a13670c85a0f9479168a9da1d1b89d9681016d8a20a5",
            "94c0af7a0a9bc133f4648919a0cc96e5f3400861b56de0a8918e88c1f2ef38d0",
        ),
    )
    current_db = os.stat("/proc/6476/fd/15")
    previous_db = Path(
        "/var/lib/crewshal-phase2d-storage-v5/crewshal-phase2d-journal-v1/coordinator.sqlite3"
    ).stat()
    if (current_db.st_dev, current_db.st_ino) != (previous_db.st_dev, previous_db.st_ino):
        raise ValueError("The second live journal FD identity changed.")
    latest_db = os.stat("/proc/7157/fd/15")
    original_latest_db = Path(
        "/var/lib/crewshal-phase2d-storage-v6/crewshal-phase2d-journal-v1/coordinator.sqlite3"
    ).stat()
    if (latest_db.st_dev, latest_db.st_ino) != (
        original_latest_db.st_dev,
        original_latest_db.st_ino,
    ):
        raise ValueError("The third live journal FD identity changed.")
    compiler_pidfd = Path("/proc/7157/fdinfo/468").read_text()
    if not any(row.split() == ["Pid:", "7168"] for row in compiler_pidfd.splitlines()):
        raise ValueError("The consumed compiler pidfd identity changed.")
    prior = (
        *prior,
        (
            6,
            "737d4446eeeb79f63b710f2e418d2148d0a7b962f1556b0abcb1c61f877c10f7",
            "2e2afaf143b8e98d88dada60d1bec20197a52d8b7f0122193d641cf8455a2716",
        ),
    )
    for version, expected_sha, configuration in prior:
        previous = Path(
            f"/var/lib/crewshal-phase2d-storage-v{version}/crewshal-phase2d-journal-v1/coordinator.sqlite3"
        )
        exact_file(previous, expected_sha)
        with sqlite3.connect("file:" + str(previous) + "?mode=ro", uri=True) as journal:
            journal.execute("PRAGMA query_only=ON")
            records = journal.execute("SELECT kind,payload FROM records").fetchall()
            if len(records) != 1 or records[0][0] != "storage_installation":
                raise ValueError("An original full charge is missing.")
            charge = json.loads(records[0][1])
            expected = {
                "state": "retained",
                "installation": "unknown",
                "memory_bytes": 805306368,
                "tasks": 128,
                "logical_bytes": 8589934592,
                "allocated_bytes": 8589934592,
                "configuration": configuration,
            }
            if any(charge.get(key) != value for key, value in expected.items()):
                raise ValueError("An original charge or unknown result changed.")
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
        (Path("/etc/systemd/system") / unit).exists() for unit in UNITS
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
            or sum(member.size for member in members) > 33554432
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
                os.fchmod(
                    fd,
                    0o400
                    if member.name == "batch.json"
                    else 0o555
                    if member.name == "root-data/usr/bin/env"
                    else 0o444,
                )
                os.fsync(fd)
            finally:
                os.close(fd)
    exclusive_env = INPUT / "root-data/usr/bin/env"
    exact_file(
        exclusive_env,
        "ebaaf26ce64d3409229f771954aff321f7d5ef004da77019173132c1f1a9fd91",
    )
    if stat.S_IMODE(exclusive_env.stat().st_mode) != 0o555:
        raise ValueError("The exact private env executable mode differs.")
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
        if unit.endswith(".service"):
            text += (
                "BindReadOnlyPaths=" + str(exclusive_env) + ":/usr/lib/cargo/bin/coreutils/env\n"
            )
        path = Path("/etc/systemd/system") / unit
        with path.open("x") as stream:
            stream.write(text)
        path.chmod(0o644)
    subprocess.run(["/usr/bin/systemctl", "daemon-reload"], check=True, env={})
    subprocess.run(["/usr/bin/systemctl", "start", UNITS[0]], check=True, env={})
    subprocess.run(
        [
            "/usr/bin/systemctl",
            "set-property",
            "--runtime",
            "crewshal-2d.slice",
            "MemoryMax=805306368",
            "MemorySwapMax=0",
            "TasksMax=128",
            "CPUQuota=100%",
            "CPUQuotaPeriodSec=100ms",
        ],
        check=True,
        env={},
    )
    common = Path("/sys/fs/cgroup/crewshal.slice/crewshal-2d.slice")
    for key, value in {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "pids.max": "128",
        "cpu.max": "100000 100000",
    }.items():
        if (common / key).read_text().strip() != value:
            raise ValueError("The common original kernel ceiling differs.")

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
