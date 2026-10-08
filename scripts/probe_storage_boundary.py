"""Synthetic Linux storage-boundary payload. No native runtime or authority grant."""

import argparse
import ctypes
import errno
import json
import os
from pathlib import Path
import resource
import socket


def attempt(action):
    try:
        action()
        return {"denied": False, "errno": None}
    except OSError as error:
        return {"denied": True, "errno": error.errno, "name": errno.errorcode.get(error.errno)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lower", required=True)
    parser.add_argument("--observer", type=int, required=True)
    parser.add_argument("--loop", required=True)
    parser.add_argument("--key", type=int, required=True)
    args = parser.parse_args()
    library = ctypes.CDLL(None, use_errno=True)

    def checked(call, *values):
        if call(*values) == -1:
            value = ctypes.get_errno()
            raise OSError(value, os.strerror(value))

    def open_read(path):
        with open(path, "rb") as stream:
            stream.read(1)

    def key_read():
        # AArch64 keyctl syscall. This payload refuses other architectures upstream.
        checked(library.syscall, ctypes.c_long(219), ctypes.c_long(11), args.key, 0, 0)

    def set_namespace():
        fd = os.open("/proc/self/ns/mnt", os.O_RDONLY)
        try:
            checked(library.setns, fd, 0)
        finally:
            os.close(fd)

    work_stat = Path("/work").stat()
    status = Path("/proc/self/status").read_text()
    cgroup = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
    result = {
        "work_stat": {
            "uid": work_stat.st_uid,
            "gid": work_stat.st_gid,
            "mode": work_stat.st_mode,
            "device": work_stat.st_dev,
            "inode": work_stat.st_ino,
        },
        "work_mount": [
            line
            for line in Path("/proc/self/mountinfo").read_text().splitlines()
            if " /work " in line
        ],
        "uid": os.getuid(),
        "gid": os.getgid(),
        "file_size_limit": list(resource.getrlimit(resource.RLIMIT_FSIZE)),
        "status": [
            line for line in status.splitlines() if line.startswith(("Cap", "NoNewPriv", "Seccomp"))
        ],
        "denials": {
            "lower": attempt(lambda: open_read(args.lower)),
            "observer_fd": attempt(lambda: open_read(f"/proc/{args.observer}/fd/0")),
            "loop": attempt(lambda: open_read(args.loop)),
            "key": attempt(key_read),
            "user_namespace": attempt(lambda: checked(library.unshare, 0x10000000)),
            "mount_namespace": attempt(lambda: checked(library.unshare, 0x20000)),
            "setns": attempt(set_namespace),
            "cgroup": attempt(
                lambda: Path("/sys/fs/cgroup" + cgroup + "/cgroup.procs").write_text(
                    str(os.getpid())
                )
            ),
        },
        "execution_allowed": False,
        "native_start_allowed": False,
    }

    def metadata():
        target = Path("/work/metadata-extra")
        target.mkdir(mode=0o700)
        file = target / "file"
        file.write_bytes(b"synthetic")
        os.chown(file, os.getuid(), os.getgid())
        os.rename(file, target / "renamed")
        with socket.socket(socket.AF_UNIX) as unix:
            unix.bind(str(target / "socket"))
            result["unix_socket_bound"] = True
        result["same_identity_chown"] = (target / "renamed").stat().st_uid == os.getuid()

    result["metadata_operation"] = attempt(metadata)
    print(json.dumps(result, sort_keys=True))
    return (
        0
        if all(item["denied"] for item in result["denials"].values())
        and not result["metadata_operation"]["denied"]
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
