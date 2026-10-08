"""Trusted file-operation diagnostic, never a runtime launcher or qualification verdict.

Creates one new fixture directory. Leaves it for an independent observer. The caller
must supply external deadlines, resource controls, source bindings and scoped cleanup.
"""

import argparse
import ctypes
import errno
import fcntl
import json
import mmap
import os
from pathlib import Path
import platform
import time

CASES = (
    "truncate",
    "seek-write",
    "pwrite",
    "mmap",
    "preallocate",
    "copy-range",
    "reflink",
    "hole-punch",
    "hardlink",
    "deleted-open",
    "metadata",
)
MAX_BYTES = 67108864


def file_state(fd: int) -> dict:
    item = os.fstat(fd)
    return {
        "device": item.st_dev,
        "inode": item.st_ino,
        "logical_bytes": item.st_size,
        "allocated_bytes": item.st_blocks * 512,
        "links": item.st_nlink,
        "mode": item.st_mode & 0o777,
    }


def fallocate(fd: int, mode: int, size: int) -> None:
    if platform.system() != "Linux":
        raise OSError(errno.ENOSYS, "Linux fallocate unavailable")
    # ABI offsets are off_t (64 bits on the intended Linux x86_64/aarch64 hosts).
    library = ctypes.CDLL(None, use_errno=True)
    call = library.fallocate
    call.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_longlong, ctypes.c_longlong)
    call.restype = ctypes.c_int
    if call(fd, mode, 0, size) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def probe(directory: Path, case: str, size: int, hold_seconds: int = 0) -> dict:
    """Only synthetic bytes; refusal/errors remain observations, never passes."""
    if case not in CASES or type(size) is not int or not 1 <= size <= MAX_BYTES:
        raise ValueError("unknown case or byte count outside 1..67108864")
    if type(hold_seconds) is not int or not 0 <= hold_seconds <= 2:
        raise ValueError("observation hold must be an integer in 0..2 seconds")
    directory.mkdir(mode=0o700, exist_ok=False)
    descriptors = []
    result = {
        "schema_version": 1,
        "case": case,
        "requested_bytes": size,
        "platform": platform.system(),
        "architecture": platform.machine(),
        "pid": os.getpid(),
        "hold_seconds": hold_seconds,
        "status": "not_observed",
        "errno": None,
        "files": {},
        "execution_allowed": False,
        "native_start_allowed": False,
        "qualification_status": "denied; diagnostic only",
    }

    def create(name: str) -> int:
        fd = os.open(directory / name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        descriptors.append((name, fd))
        return fd

    try:
        fd = create("target")
        if case == "truncate":
            os.ftruncate(fd, size)
        elif case == "seek-write":
            os.lseek(fd, size - 1, os.SEEK_SET)
            if os.write(fd, b"Z") != 1:
                raise OSError(errno.EIO, "short synthetic write")
        elif case == "pwrite":
            if os.pwrite(fd, b"Z", size - 1) != 1:
                raise OSError(errno.EIO, "short synthetic write")
        elif case == "mmap":
            os.ftruncate(fd, size)
            with mmap.mmap(fd, size) as mapping:
                mapping[size - 1] = ord("Z")
                mapping.flush()
        elif case == "preallocate":
            fallocate(fd, 0, size)
        elif case in ("copy-range", "reflink"):
            source = create("source")
            # Deliberately sparse source; native copy/reflink must not reintroduce holes.
            os.ftruncate(source, size)
            os.pwrite(source, b"Z", size - 1)
            if case == "copy-range":
                if not hasattr(os, "copy_file_range"):
                    raise OSError(errno.ENOSYS, "copy_file_range unavailable")
                remaining = size
                while remaining:
                    copied = os.copy_file_range(source, fd, remaining)
                    if not copied:
                        raise OSError(errno.EIO, "short synthetic copy")
                    remaining -= copied
            else:
                if platform.system() != "Linux":
                    raise OSError(errno.ENOSYS, "Linux FICLONE unavailable")
                fcntl.ioctl(fd, 0x40049409, source)  # Linux FICLONE, _IOW(0x94, 9, int).
            result["last_byte_matches"] = os.pread(fd, 1, size - 1) == b"Z"
        elif case in ("hole-punch", "deleted-open"):
            block = b"Z" * min(size, 65536)
            remaining = size
            while remaining:
                written = os.write(fd, block[:remaining])
                if not written:
                    raise OSError(errno.EIO, "short synthetic write")
                remaining -= written
            os.fsync(fd)
            result["before"] = file_state(fd)
            if case == "hole-punch":
                fallocate(fd, 3, size)  # KEEP_SIZE | PUNCH_HOLE.
            else:
                (directory / "target").unlink()
                result["unlinked_open_file"] = file_state(fd)
                result["directory_entry_absent_while_open"] = not (directory / "target").exists()
        elif case == "hardlink":
            os.ftruncate(fd, size)
            os.link(directory / "target", directory / "alias")
            result["alias_same_inode"] = (directory / "alias").stat().st_ino == os.fstat(fd).st_ino
        elif case == "metadata":
            os.fchmod(fd, 0o600)
            os.symlink("target", directory / "symbolic")
            os.rename(directory / "target", directory / "renamed")
            if not hasattr(os, "setxattr") or not hasattr(os, "getxattr"):
                raise OSError(errno.ENOSYS, "extended attribute API unavailable")
            os.setxattr(directory / "renamed", "user.crewshal_test", b"synthetic")
            result["xattr_matches"] = (
                os.getxattr(directory / "renamed", "user.crewshal_test") == b"synthetic"
            )
        for _, opened in descriptors:
            os.fsync(opened)
        result["status"] = "operation_completed"
    except OSError as error:
        result["status"] = "operation_error"
        result["errno"] = error.errno
        result["errno_name"] = errno.errorcode.get(error.errno, "UNKNOWN")
    finally:
        # Observation window, not a deadline or proof that an observer sampled it.
        time.sleep(hold_seconds)
        for name, opened in descriptors:
            try:
                result["files"][name] = file_state(opened)
            finally:
                os.close(opened)
    # FD facts include deleted-open files before close. This list does not follow links.
    result["remaining_entries"] = sorted(path.name for path in directory.iterdir())
    result["observer_required"] = (
        "Independent lower-filesystem/quota/FD/namespace/controller readback and cleanup; "
        "successful or denied operation alone does not establish enforcement."
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True, help="new owned fixture path")
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--bytes", type=int, required=True)
    parser.add_argument("--hold-seconds", type=int, default=0, help="FD observation window, 0..2")
    arguments = parser.parse_args()
    try:
        result = probe(arguments.directory, arguments.case, arguments.bytes, arguments.hold_seconds)
    except (ValueError, OSError) as error:
        parser.exit(2, f"diagnostic refused: {error}\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "operation_completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
