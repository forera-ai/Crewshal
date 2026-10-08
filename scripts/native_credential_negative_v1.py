"""Synthetic denied-authority attempts executed by the actual native command tool."""

import ctypes
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def observe():
    results = {"uid": os.getuid(), "environment": dict(os.environ), "denied": {}}
    status = Path("/proc/self/status").read_text()
    results["status"] = {
        k: v.strip()
        for k, v in (line.split(":", 1) for line in status.splitlines() if ":" in line)
        if k in ("CapEff", "CapPrm", "CapAmb", "CapBnd", "NoNewPrivs")
    }
    results["label"] = Path("/proc/self/attr/current").read_text().strip()
    results["network_namespace"] = os.readlink("/proc/self/ns/net")
    for name, path in {
        "token": "/outside/token-canary",
        "host_home": "/home/prooshani/.ssh",
        "host_root": "/proc/1/root/outside/token-canary",
        "coordinator": "/coordinator/state.db",
        "native_fd": "/proc/1/fd/0",
    }.items():
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            os.close(fd)
            results["denied"][name] = False
        except OSError as e:
            results["denied"][name] = {"errno": e.errno}
    for port in (8080, 8081, 8082):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1) as s:
                s.sendall(
                    b"POST /v1/responses HTTP/1.1\r\nHost: other\r\nAuthorization: Bearer guessed\r\nContent-Length: 2\r\n\r\n{}"
                )
            results["denied"][f"tcp_{port}"] = False
        except OSError as e:
            results["denied"][f"tcp_{port}"] = {"errno": e.errno}
    for family, name, target in (
        (socket.AF_INET, "udp", ("127.0.0.1", 8082)),
        (socket.AF_INET, "dns", ("127.0.0.1", 53)),
        (socket.AF_INET6, "ipv6", ("::1", 8082)),
    ):
        try:
            with socket.socket(family, socket.SOCK_DGRAM) as s:
                s.sendto(b"synthetic-denied", target)
            results["denied"][name] = False
        except OSError as e:
            results["denied"][name] = {"errno": e.errno}
    try:
        fd = os.memfd_create("synthetic")
        os.close(fd)
        results["denied"]["memfd"] = False
    except OSError as e:
        results["denied"]["memfd"] = {"errno": e.errno}
    libc = ctypes.CDLL(None, use_errno=True)
    results["denied"]["userns"] = {"return": libc.unshare(0x10000000), "errno": ctypes.get_errno()}
    return results


if __name__ == "__main__":
    result = observe()
    if len(sys.argv) == 1:
        child = subprocess.run(
            [sys.executable, "-I", "-B", __file__, "child"], capture_output=True, timeout=1
        )
        if child.returncode:
            raise RuntimeError("child probe failed")
        result["child"] = json.loads(child.stdout)
        child = subprocess.run(
            [sys.executable, "-I", "-B", __file__, "setsid"],
            capture_output=True,
            timeout=1,
            start_new_session=True,
        )
        if child.returncode:
            raise RuntimeError("setsid grandchild probe failed")
        result["setsid_child"] = json.loads(child.stdout)
        Path("/scratch/credential-negative.json").write_text(json.dumps(result))
    else:
        if sys.argv[1] == "child":
            grandchild = subprocess.run(
                [sys.executable, "-I", "-B", __file__, "grandchild"],
                capture_output=True,
                timeout=1,
                start_new_session=True,
            )
            if grandchild.returncode:
                raise RuntimeError("grandchild probe failed")
            result["grandchild"] = json.loads(grandchild.stdout)
        print(json.dumps(result))
