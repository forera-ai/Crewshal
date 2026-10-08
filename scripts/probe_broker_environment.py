"""Isolated Linux SBX store preflight; no sandbox, login or provider operation."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SHA256 = "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
IMAGE = "sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60"
BINARY_SHA256 = "247f30d8bc7dcce615235024eac43a4ad0d1730a94ff650d52a6e57bad401060"
TOKEN = "crewshal-synthetic-broker-preflight-never-real"
ENVIRONMENT = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/scratch/home",
    "XDG_CONFIG_HOME": "/scratch/config",
    "XDG_RUNTIME_DIR": "/scratch/runtime",
    "LD_LIBRARY_PATH": "/opt/sbx",
}
COMMANDS = (
    ("version",),
    ("secret", "set-custom", "--help"),
    (
        "secret",
        "set-custom",
        "--host",
        "provider.crewshal.invalid",
        "--env",
        "CREWSHAL_SYNTHETIC_API_KEY",
        "--value",
        TOKEN,
    ),
    ("secret", "ls"),
)
HOST_LIMITS = {
    "memory_bytes": 134217728,
    "cpus": 1,
    "pids": 32,
    "scratch_bytes": 33554432,
    "command_seconds": 10,
    "total_seconds": 60,
}
STATE_COMMAND = (
    "mkdir -p /scratch/home /scratch/config /scratch/runtime; "
    "chmod 700 /scratch/home /scratch/config /scratch/runtime; "
    "cat /etc/os-release; uname -r; "
    "if test -c /dev/kvm; then echo kvm-device-present; else echo kvm-device-absent; fi; "
    "if test -e /sys/class/misc/kvm; then echo kvm-sysfs-present; "
    "else echo kvm-sysfs-absent; fi; "
    "test ! -e /run/dbus/system_bus_socket && echo system-secret-service-socket-absent; "
    "test ! -e /var/run/docker.sock && echo engine-socket-absent"
)
STORE_COMMAND = (
    "find /scratch -type f -printf '%p %m\\n'; "
    "find /scratch -type d -printf '%p %m\\n'; "
    "grep -rlF 'crewshal-synthetic-broker-preflight-never-real' /scratch; "
    "find /scratch -type f -name secretpass -size +0c -printf 'credential-blob:%p\\n'; "
    'for path in /proc/[0-9]*/comm; do printf "process:"; cat "$path"; done'
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_manifest(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError("prospective manifest digest mismatch")
    manifest = json.loads(raw)
    original_raw = (ROOT / "docs/qualification/phase-2c-v1.json").read_bytes()
    original = json.loads(original_raw)
    if (
        digest(original_raw) != ORIGINAL_SHA256
        or type(manifest.get("schema_version")) is not int
        or manifest["schema_version"] != 1
        or manifest.get("parent_manifest") != ORIGINAL_SHA256
        or any(manifest.get(k) != original[k] for k in ("grant", "limits", "mandatory_cases"))
        or manifest.get("image") != IMAGE
        or manifest.get("binary_sha256") != BINARY_SHA256
        or manifest.get("commands") != [list(c) for c in COMMANDS]
        or manifest.get("environment") != ENVIRONMENT
        or manifest.get("host_limits") != HOST_LIMITS
        or manifest.get("state_command") != STATE_COMMAND
        or manifest.get("store_command") != STORE_COMMAND
        or manifest.get("sandbox_launch_allowed") is not False
        or manifest.get("sources")
        != {"scripts/probe_broker_environment.py": digest(Path(__file__).read_bytes())}
    ):
        raise ValueError("frozen broker environment protocol mismatch")
    return manifest


def verify_grant(info: dict, bundle: Path) -> bool:
    host, config = info.get("HostConfig", {}), info.get("Config", {})
    mounts = info.get("Mounts", [])
    binds = [m for m in mounts if m.get("Type") == "bind"]
    return (
        info.get("Image") == IMAGE
        and host.get("NetworkMode") == "none"
        and host.get("ReadonlyRootfs") is True
        and host.get("Privileged") is False
        and host.get("CapDrop") == ["ALL"]
        and host.get("SecurityOpt") in (["no-new-privileges"], ["no-new-privileges:true"])
        and host.get("Memory") == 134217728
        and host.get("NanoCpus") == 1000000000
        and host.get("PidsLimit") == 32
        and host.get("IpcMode") == "private"
        and not host.get("PidMode")
        and not host.get("Devices")
        and not host.get("DeviceRequests")
        and not host.get("CapAdd")
        and not host.get("PortBindings")
        and len(binds) == 1
        and binds[0].get("Source") == str(bundle)
        and binds[0].get("Destination") == "/opt/sbx"
        and binds[0].get("RW") is False
        and all(m.get("Type") in ("bind", "tmpfs") for m in mounts)
        and set(host.get("Tmpfs", {})) == {"/scratch"}
        and host["Tmpfs"]["/scratch"] == "rw,noexec,nosuid,nodev,size=33554432,mode=1777"
        and config.get("User") == "65532:65532"
        and config.get("Entrypoint") == ["/bin/sleep"]
        and config.get("Cmd") == ["60"]
        and set(config.get("Env", []))
        == {"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
    )


def assess(commands: list[dict], state: dict, grant: bool, removed: bool) -> dict:
    complete = (
        grant
        and removed
        and len(commands) == len(COMMANDS)
        and all(
            c.get("arguments") == list(a) and c.get("exit") == 0
            for c, a in zip(commands, COMMANDS, strict=False)
        )
    )
    return {
        "status": "denied",
        "cli_complete": complete,
        "file_store_observed": complete
        and state.get("credential_blob_present") is True
        and state.get("private_directory") is True
        and "No keychain detected" in commands[2].get("stderr", "")
        and "provider.crewshal.invalid" in commands[3].get("stdout", "")
        and "CREWSHAL_SYNTHETIC_API_KEY" in commands[3].get("stdout", ""),
        "local_sandbox_available": False,
        "request_authority": "unavailable; no broker request or worker exercised",
        "execution_allowed": False,
    }


def run_probe(bundle: Path, manifest_path: Path, expected: str, endpoint: str) -> dict:
    manifest = load_manifest(manifest_path, expected)
    if not endpoint.startswith("unix:///"):
        raise ValueError("explicit local Unix endpoint required")
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("real extracted bundle required")
    if any(p.is_symlink() for p in bundle.rglob("*")):
        raise ValueError("bundle symlinks refused")
    actual = {
        str(p.relative_to(bundle)): digest(p.read_bytes()) for p in bundle.rglob("*") if p.is_file()
    }
    if actual != manifest.get("bundle_files") or actual.get("sbx") != BINARY_SHA256:
        raise ValueError("pinned bundle identity mismatch")
    commands, transcript = [], []
    container = "crewshal-broker-" + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="crewshal-broker-oracle-") as name:
        started = time.monotonic()
        environment = {
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "HOME": name,
            "DOCKER_CONFIG": name,
            "DOCKER_HOST": endpoint,
        }

        def docker(arguments: list[str]) -> dict:
            try:
                if arguments[0] not in ("rm", "ps") and time.monotonic() - started >= 60:
                    raise ValueError("broker environment experiment deadline exceeded")
                p = subprocess.run(
                    ["/opt/homebrew/bin/docker", *arguments],
                    env=environment,
                    capture_output=True,
                    timeout=10,
                )
                result = {
                    "argv": arguments,
                    "exit": p.returncode,
                    "stdout": p.stdout.decode(errors="replace"),
                    "stderr": p.stderr.decode(errors="replace"),
                }
                if max(len(p.stdout), len(p.stderr)) > 65536:
                    result = {"argv": arguments, "exit": None, "error": "output limit exceeded"}
            except (OSError, subprocess.TimeoutExpired) as error:
                result = {"argv": arguments, "exit": None, "error": str(error)}
            transcript.append(result)
            return result

        server = docker(["version", "--format", "{{json .Server}}"])
        create = [
            "create",
            "--pull=never",
            "--name",
            container,
            "--label=crewshal.qualification=broker-environment",
            "--network=none",
            "--read-only",
            "--user=65532:65532",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--pids-limit=32",
            "--memory=128m",
            "--cpus=1",
            "--log-driver=none",
            "--entrypoint=/bin/sleep",
            "--mount",
            f"type=bind,src={bundle},dst=/opt/sbx,readonly",
            "--tmpfs",
            "/scratch:rw,noexec,nosuid,nodev,size=33554432,mode=1777",
            IMAGE,
            "60",
        ]
        grant, removed, state, host_state = False, False, {}, {}
        before = None
        try:
            created = docker(create)
            if created.get("exit") != 0:
                raise ValueError("fixture creation unavailable")
            inspected = docker(["inspect", container])
            if inspected.get("exit") == 0:
                before = json.loads(inspected["stdout"])[0]
                grant = verify_grant(before, bundle)
            if not grant:
                raise ValueError("effective broker host grant mismatch before start")
            if docker(["start", container]).get("exit") != 0:
                raise ValueError("fixture start unavailable")
            host_state = docker(["exec", container, "/bin/sh", "-c", STATE_COMMAND])
            for arguments in COMMANDS:
                result = docker(
                    [
                        "exec",
                        container,
                        "/usr/bin/env",
                        "-i",
                        *[f"{k}={v}" for k, v in ENVIRONMENT.items()],
                        "/opt/sbx/sbx",
                        *arguments,
                    ]
                )
                commands.append(
                    {
                        "arguments": list(arguments),
                        **{k: v for k, v in result.items() if k != "argv"},
                    }
                )
                if result.get("exit") != 0:
                    break
            oracle = docker(["exec", container, "/bin/sh", "-c", STORE_COMMAND])
            state = {"oracle": oracle}
            if oracle.get("exit") == 0:
                lines = oracle.get("stdout", "").splitlines()
                state.update(
                    plaintext_token_observed=any(
                        line.startswith("/scratch/") and " " not in line for line in lines
                    ),
                    credential_blob_present=any(
                        line.startswith("credential-blob:/scratch/config/com.docker.sandboxes/")
                        for line in lines
                    ),
                    private_directory="/scratch/config/com.docker.sandboxes 700" in lines,
                    daemon_present_at_oracle=any(
                        line in ("process:sandboxd", "process:sbx") for line in lines
                    ),
                )
            after = docker(["inspect", container])
            grant = (
                grant
                and after.get("exit") == 0
                and verify_grant(json.loads(after["stdout"])[0], bundle)
            )
        finally:
            cleanup = docker(["rm", "--force", container])
            inventory = docker(["ps", "-aq", "--filter", "name=^/" + container + "$"])
            removed = (
                cleanup.get("exit") == 0
                and inventory.get("exit") == 0
                and not inventory.get("stdout", "").strip()
            )
        report = {
            "schema_version": 1,
            "manifest_sha256": expected,
            "sources": manifest["sources"],
            "image": IMAGE,
            "binary_sha256": BINARY_SHA256,
            "server": server,
            "effective_grant_verified": grant,
            "fixture_removed": removed,
            "host_state": host_state,
            "commands": commands,
            "store_state": state,
            "inspect_before": before,
            "transcript": transcript,
            "decision": assess(commands, state, grant, removed),
            "mandatory_results": [
                {"case": c["id"], "status": "unavailable"} for c in manifest["mandatory_cases"]
            ],
            "sandbox_launches": 0,
            "login_attempted": False,
            "host_credential_store_accessed": False,
        }
        normalized = (
            json.dumps(report)
            .replace(str(bundle), "<pinned-bundle>")
            .replace(name, "<synthetic-home>")
        )
        return json.loads(normalized)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--docker-host", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Refuse existing evidence, including dangling symlinks, before any fixture operation.
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        try:
            report = run_probe(args.bundle, args.manifest, args.manifest_sha256, args.docker_host)
        except (OSError, ValueError, KeyError) as error:
            report = {"status": "refused", "reason": str(error), "execution_allowed": False}
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("Broker environment preflight recorded; full Phase 2C remains denied.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
