"""Receive one frozen owner input archive after separate operational approval."""

import hashlib
import json
import os
import resource
import signal
import sys


PATH = "/var/lib/crewshal-phase2d-owner-inputs-v9.tar"
BYTES = 26572800
SHA256 = "3f41f8df1643643be1e40874eeb75dbdb0e4d90247f80dc16fb56aeaf2fd22b9"


def upload() -> None:
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
    if sys.platform != "linux" or (os.getuid(), os.getgid()) != (0, 0) or os.environ:
        raise ValueError("The isolated Linux root owner entry is required.")
    os.umask(0o077)
    resource.setrlimit(resource.RLIMIT_FSIZE, (33554432, 33554432))
    signal.alarm(30)
    fd = os.open(PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    sha, count = hashlib.sha256(), 0
    try:
        while data := sys.stdin.buffer.read(65536):
            count += len(data)
            if count > BYTES:
                raise ValueError("The original owner input archive exceeds its exact bound.")
            sha.update(data)
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise ValueError("The original owner input write is incomplete.")
                view = view[written:]
        os.fsync(fd)
        if count != BYTES or sha.hexdigest() != SHA256:
            raise ValueError("The original owner input archive bytes differ.")
    finally:
        os.close(fd)
    signal.alarm(0)
    print(json.dumps({"owner_input_bytes": count, "sha256": sha.hexdigest()}))


if __name__ == "__main__":
    upload()
