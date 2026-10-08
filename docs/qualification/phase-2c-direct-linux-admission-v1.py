"""Read-only local Linux feasibility inventory; never launch a worker or grant execution."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def main():
    result = {
        "schema_version": 1,
        "scope": "read-only admission inventory; not enforcement or qualification",
        "platform": sys.platform,
        "execution_allowed": False,
        "native_start_allowed": False,
        "operational_manifest_frozen": False,
        "host_mutated": False,
    }
    if sys.platform != "linux":
        result["status"] = "unavailable; requires an existing owner-accessible Linux shell"
        print(json.dumps(result, indent=2))
        return 2
    result["kernel"] = os.uname().release
    result["architecture"] = os.uname().machine
    result["effective_uid"] = os.geteuid()
    result["python_version"] = sys.version.split()[0]
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["kernel_interfaces"] = {}
    for name, path in {
        "controllers": "/sys/fs/cgroup/cgroup.controllers",
        "filesystems": "/proc/filesystems",
        "self_cgroup": "/proc/self/cgroup",
    }.items():
        data = Path(path).read_bytes()
        if len(data) > 16384:
            raise ValueError("admission interface exceeds 16384 bytes")
        result["kernel_interfaces"][name] = data.decode()
    result["helpers"] = {}
    for name in ("bwrap", "setpriv", "systemd-run", "timeout", "mount", "umount"):
        found = shutil.which(name, path="/usr/bin:/usr/sbin:/bin:/sbin")
        if found is None:
            result["helpers"][name] = None
            continue
        with Path(found).open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        result["helpers"][name] = {"path": found, "sha256": digest}
    result["status"] = "inventory_only; effective controls and complete identities unresolved"
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
