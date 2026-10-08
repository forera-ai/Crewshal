"""Read-only admission and invalidation checks before the prospective native batch."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE = Path("/var/tmp/crewshal-native-qualification-v17")
EXPECTED_ROLES = {
    "crewshal-native-tool-v1": "f96fb67936fcab509534ab180b512a8fd6a2eba0d59dc7fa92a2c50282e8e2ca",
    "crewshal-native-bwrap-v1": "0712da1298b44d54de8d9a6184ecd528c72cef5402ef57d6bc7f92578f092061",
}
EXPECTED_CONTROLS = {
    "memory.max": "805306368",
    "memory.swap.max": "0",
    "cpu.max": "100000 100000",
    "pids.max": "128",
}


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check(expected):
    manifest = BASE / "manifest-native-full-v17.json"
    if digest(manifest) != expected:
        raise RuntimeError("fresh full manifest mismatch")
    data = json.loads(manifest.read_text())
    for name, bound in data["bindings"].items():
        if digest(name) != bound:
            raise RuntimeError("bound input changed: " + name)
    profiles = Path("/sys/kernel/security/apparmor/policy/profiles")
    roles = {}
    for entry in profiles.iterdir():
        for role in EXPECTED_ROLES:
            if entry.name.startswith(role + "."):
                roles[role] = (entry / "sha256").read_text().strip()
    if roles != EXPECTED_ROLES:
        raise RuntimeError("loaded fixture-only role policy changed")
    if Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns").read_text().strip() != "1":
        raise RuntimeError("global user namespace restriction changed")
    group = Path("/sys/fs/cgroup/crewshalnativediscoveryv1.slice")
    controls = {name: (group / name).read_text().strip() for name in EXPECTED_CONTROLS}
    if controls != EXPECTED_CONTROLS:
        raise RuntimeError("original aggregate controls changed")
    protocol = Path("/run/crewshal-phase-2c-original-v1.json")
    if digest(protocol) != "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563":
        raise RuntimeError("original twenty-case protocol changed")
    profile = Path("/run/crewshal-native-full-profile-v17.json")
    policy = json.loads(profile.read_text())
    original = json.loads(protocol.read_text())
    if (
        policy["original_grant"] != original["grant"]
        or policy["original_limits"] != original["limits"]
    ):
        raise RuntimeError("original grant or limits differ")
    if policy["mandatory_cases"] != original["mandatory_cases"]:
        raise RuntimeError("original criterion text or order differs")
    return {
        "manifest_sha256": expected,
        "profile_sha256": digest(profile),
        "loaded_policy_sha256": roles,
        "aggregate_observed": controls,
        "kernel": os.uname().release,
        "architecture": os.uname().machine,
        "observer_sha256": digest(__file__),
        "original_protocol_sha256": digest(protocol),
        "global_userns_restriction": 1,
        "execution_allowed": False,
        "native_start_allowed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = check(args.expected)
    before = sorted(path.name for path in BASE.iterdir())
    invalid = subprocess.run(
        [
            "/usr/bin/python3",
            "-I",
            "-B",
            "/run/crewshal-native-full-v17.py",
            "run",
            "--fixture",
            "1",
            "--manifest-sha256",
            "0" * 64,
        ],
        capture_output=True,
        timeout=10,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    if invalid.returncode == 0 or b"manifest changed" not in invalid.stderr:
        raise RuntimeError("stale manifest did not refuse before fixture creation")
    if sorted(path.name for path in BASE.iterdir()) != before:
        raise RuntimeError("stale manifest refusal created fixture objects")
    result["stale_manifest_refusal"] = {
        "exit": invalid.returncode,
        "owned_inventory_unchanged": True,
        "stderr": invalid.stderr.decode(),
    }
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
