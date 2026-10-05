"""Create private, byte-bound vendor Python inputs for the synthetic Linux experiment.

Trusted disposable host only. Copies vendor files; performs no key, mount, package,
network, service, or runtime operation. Refuses existing destinations and >256 MiB.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
MAX_INPUT = 268435456
TOOLS = (
    "/usr/bin/python3.12",
    "/usr/bin/keyctl",
    "/usr/bin/mount",
    "/usr/bin/umount",
    "/usr/sbin/losetup",
    "/usr/sbin/mkfs.ext4",
    "/usr/bin/systemd-run",
    "/usr/bin/systemctl",
    "/usr/bin/ldd",
    "/bin/bash",
    "/usr/lib/systemd/systemd",
    "/usr/lib/systemd/systemd-executor",
)


def dependencies(binary):
    with binary.open("rb") as stream:
        if stream.read(4) != b"\x7fELF":
            return []  # The explicit helper list separately binds /bin/bash.
    result = subprocess.run(["/usr/bin/ldd", str(binary)], capture_output=True, timeout=10, env=ENV)
    if result.returncode or len(result.stdout) > 65536 or len(result.stderr) > 65536:
        raise RuntimeError("vendor dependency inventory unavailable")
    return [
        Path(path)
        for path in re.findall(r"(?:=>\s+|^\s*)(/\S+)\s+\(", result.stdout.decode(), re.MULTILINE)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        parser.error("profile requires observed aarch64 Linux and trusted root")
    destination = args.destination
    destination.mkdir(mode=0o700)
    root = destination / "root"
    root.mkdir(mode=0o755)
    bindings = {
        "architecture": os.uname().machine,
        "kernel_release": os.uname().release,
        "sha256": {},
        "input_logical_bytes": 0,
        "input_allocated_bytes": 0,
        "execution_allowed": False,
        "native_start_allowed": False,
    }

    def bind(path):
        path = Path(path)
        bindings["sha256"][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()

    def copy(source, target):
        size = source.stat().st_size
        bindings["input_logical_bytes"] += size
        if bindings["input_logical_bytes"] > MAX_INPUT:
            raise RuntimeError("private vendor input reserve exceeded")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != source.read_bytes():
                raise RuntimeError("input target collision")
            return
        shutil.copyfile(source, target)
        target.chmod(0o755 if os.access(source, os.X_OK) else 0o644)
        bindings["input_allocated_bytes"] += target.stat().st_blocks * 512
        bind(source)
        bind(target)

    stdlib = Path("/usr/lib/python3.12")
    for source in sorted(stdlib.rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts:
            copy(source, root / source.relative_to("/"))
    copy(Path("/usr/bin/python3.12"), root / "bin/python3")
    for folder in ("proc", "dev", "work", "sys", "tmp", "etc", "inputs"):
        (root / folder).mkdir(exist_ok=True)
    python_libraries = {
        path
        for binary in [Path("/usr/bin/python3.12"), *stdlib.rglob("*.so")]
        for path in dependencies(binary)
    }
    for path in sorted(python_libraries):
        copy(path, root / path.relative_to("/"))
    for source, target in (
        ("probe_storage_operations.py", "root/inputs/probe.py"),
        ("probe_storage_boundary.py", "root/inputs/boundary.py"),
        ("observe_linux_storage.py", "observe_linux_storage.py"),
        ("prepare_linux_storage.py", "prepare_linux_storage.py"),
    ):
        copy(args.source / source, destination / target)
    for tool in TOOLS:
        bind(tool)
        for dependency in dependencies(Path(tool)):
            bind(dependency)
    bind("/boot/vmlinuz-" + os.uname().release)
    bind("/boot/config-" + os.uname().release)
    bind("/etc/mke2fs.conf")
    bindings["copied_vendor_dependencies"] = [str(path) for path in sorted(python_libraries)]
    for path in destination.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)
    destination.chmod(0o700)
    with (destination / "bindings.json").open("x") as stream:
        json.dump(bindings, stream, indent=2, sort_keys=True)
    print(
        json.dumps(
            {
                "input_logical_bytes": bindings["input_logical_bytes"],
                "input_allocated_bytes": bindings["input_allocated_bytes"],
                "bound_files": len(bindings["sha256"]),
            }
        )
    )


if __name__ == "__main__":
    main()
