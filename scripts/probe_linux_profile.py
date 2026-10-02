"""Frozen synthetic Linux substrate probes; never a product runtime launcher."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import uuid

from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)

IMAGE = "sha256:5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11"
CASES = tuple(MANDATORY_CASES[:8]) + ("environment-credentials",)
PAYLOAD = r"""set -eu
mkdir -p /scratch/home
[ "$(cat /input/read.txt)" = "synthetic-readable" ]
printf approved > /candidate/owned/existing.txt
printf new > /candidate/owned/new.txt
printf scratch > /scratch/temporary
if printf forbidden > /input/read.txt 2>/scratch/error; then exit 31; fi
printf 'allowed-grant\n'
for target in /outside/canary /original/canary /coordinator/canary; do
    if cat "$target" >/scratch/read 2>/scratch/error; then exit 32; fi
    if printf forbidden > "$target" 2>/scratch/error; then exit 33; fi
done
for target in "$HOST_FIXTURE/outside/canary" "$HOST_FIXTURE/original/canary" "$HOST_FIXTURE/coordinator/canary"; do
    if cat "$target" >/scratch/read 2>/scratch/error; then exit 34; fi
    if printf forbidden > "$target" 2>/scratch/error; then exit 35; fi
done
printf 'external-read\nexternal-write\noriginal-checkout\ncoordinator-state\n'
if cat /candidate/owned/absolute-link >/scratch/read 2>/scratch/error; then exit 36; fi
if printf forbidden > /candidate/owned/absolute-link 2>/scratch/error; then exit 37; fi
if cat /candidate/owned/relative-excluded-link >/scratch/read 2>/scratch/error; then exit 45; fi
if printf forbidden > /candidate/owned/relative-excluded-link 2>/scratch/error; then exit 46; fi
if printf forbidden > /candidate/owned/relative-link/read.txt 2>/scratch/error; then exit 38; fi
printf 'symlink-escape\n'
if printf forbidden > /candidate/owned/relative-link/new.txt 2>/scratch/error; then exit 39; fi
if printf forbidden > /candidate/owned/../../input/new.txt 2>/scratch/error; then exit 40; fi
printf 'new-file-escape\n'
if chmod 777 /input/read.txt 2>/scratch/error; then exit 41; fi
if rm /input/read.txt 2>/scratch/error; then exit 42; fi
if mv /input/read.txt /candidate/owned/moved.txt 2>/scratch/error; then exit 43; fi
if ln /input/read.txt /candidate/owned/hardlink.txt 2>/scratch/error; then exit 44; fi
printf 'metadata-escape\n'
[ -z "${CREWSHAL_SYNTHETIC_SECRET+x}" ]
[ -z "${SSH_AUTH_SOCK+x}" ]
[ -z "${ANTHROPIC_API_KEY+x}" ]
[ -z "${OPENAI_API_KEY+x}" ]
[ ! -e /var/run/docker.sock ]
[ ! -e /run/host-services/ssh-auth.sock ]
[ ! -e /root/.ssh ]
printf 'environment-credentials\n'
uname -r > /candidate/owned/kernel.txt
/bin/busybox 2>&1 | head -1 > /candidate/owned/toolchain.txt
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> dict[str, object]:
    result = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        result[str(path.relative_to(root))] = {
            "mode": info.st_mode,
            "links": info.st_nlink,
            "content": os.readlink(path)
            if path.is_symlink()
            else digest(path.read_bytes())
            if path.is_file()
            else None,
        }
    return result


def docker_capture(args: list[str], environment: dict[str, str]) -> dict[str, object]:
    argv = ["/opt/homebrew/bin/docker", *args]
    try:
        process = subprocess.run(argv, env=environment, capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"argv": argv, "exit": None, "error": str(error)}
    if max(len(process.stdout), len(process.stderr)) > 65536:
        return {"argv": argv, "exit": None, "error": "output limit exceeded"}
    return {
        "argv": argv,
        "exit": process.returncode,
        "stdout": process.stdout.decode(errors="replace"),
        "stderr": process.stderr.decode(errors="replace"),
    }


def verify_grant(info: dict, root: Path) -> bool:
    """Check effective engine grant, independently of the child payload."""
    host = info.get("HostConfig", {})
    config = info.get("Config", {})
    binds = [mount for mount in info.get("Mounts", []) if mount.get("Type") == "bind"]
    expected = {
        (str(root / "input"), "/input", False),
        (str(root / "owned"), "/candidate/owned", True),
    }
    actual = {(m.get("Source"), m.get("Destination"), m.get("RW")) for m in binds}
    other_mounts = [m for m in info.get("Mounts", []) if m.get("Type") != "bind"]
    return (
        host.get("NetworkMode") == "none"
        and host.get("ReadonlyRootfs") is True
        and host.get("Privileged") is False
        and host.get("CapDrop") == ["ALL"]
        and host.get("PidsLimit") == 32
        and host.get("Memory") == 134217728
        and host.get("NanoCpus") == 1000000000
        and host.get("SecurityOpt") in (["no-new-privileges"], ["no-new-privileges:true"])
        and not host.get("PidMode")
        and host.get("IpcMode") == "private"
        and not host.get("PortBindings")
        and not host.get("Devices")
        and len(binds) == 2
        and actual == expected
        and all(
            m.get("Type") == "tmpfs" and m.get("Destination") == "/scratch" for m in other_mounts
        )
        and set(host.get("Tmpfs", {})) == {"/scratch"}
        and config.get("User") == "65532:65532"
        and config.get("Entrypoint") == ["/bin/sh"]
        and config.get("Cmd") == ["/input/probe.sh"]
        and set(config.get("Env", []))
        == {
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "HOME=/scratch/home",
            f"HOST_FIXTURE={root}",
        }
        and info.get("Image") == IMAGE
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker-host", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.docker_host.startswith("unix:///"):
        parser.error("qualification requires an explicit local Unix socket")
    if digest(args.manifest.read_bytes()) != args.manifest_sha256:
        parser.error("prospectively frozen manifest digest mismatch")
    manifest = json.loads(args.manifest.read_text())
    if manifest.get("image") != IMAGE or manifest.get("harness") != digest(
        Path(__file__).read_bytes()
    ):
        parser.error("image/harness differs from prospective frozen manifest")
    if (
        manifest.get("parent_manifest")
        != "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
    ):
        parser.error("parent qualification protocol mismatch")
    if [case["id"] for case in manifest["mandatory_cases"]] != list(MANDATORY_CASES):
        parser.error("mandatory cases changed")
    if args.output.exists():
        parser.error("observation path already exists")
    with tempfile.TemporaryDirectory(prefix="crewshal-substrate-") as name:
        root = Path(name)
        environment = {
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "HOME": name,
            "DOCKER_CONFIG": name,
            "DOCKER_HOST": args.docker_host,
            "CREWSHAL_SYNTHETIC_SECRET": "synthetic-never-real",
            "SSH_AUTH_SOCK": "/synthetic/nonexistent-agent.sock",
            "ANTHROPIC_API_KEY": "synthetic-parent-only",
            "OPENAI_API_KEY": "synthetic-parent-only",
        }
        for directory in ("input", "owned", "outside", "original", "coordinator"):
            (root / directory).mkdir(mode=0o755)
        (root / "owned").chmod(0o777)
        (root / "input/read.txt").write_text("synthetic-readable")
        (root / "input/probe.sh").write_text(PAYLOAD)
        (root / "owned/existing.txt").write_text("before")
        (root / "owned/existing.txt").chmod(0o666)
        (root / "owned/absolute-link").symlink_to("/original/canary")
        (root / "owned/relative-link").symlink_to("../../input", target_is_directory=True)
        (root / "owned/relative-excluded-link").symlink_to("../../original/canary")
        for directory in ("outside", "original", "coordinator"):
            (root / directory / "canary").write_text("synthetic-excluded")
        # Synthetic original dirty bytes and metadata are coordinator-only.
        (root / "original/.git").mkdir()
        (root / "original/.git/HEAD").write_text("synthetic-git-metadata")
        protected = {
            part: snapshot(root / part) for part in ("input", "outside", "original", "coordinator")
        }
        commands = []
        server = docker_capture(["version", "--format", "{{json .Server}}"], environment)
        commands.append(server)
        container = "crewshal-2c-" + uuid.uuid4().hex
        argv = [
            "create",
            "--pull=never",
            "--name",
            container,
            "--label",
            "crewshal.qualification=2c",
            "--network=none",
            "--read-only",
            "--user=65532:65532",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--pids-limit=32",
            "--memory=128m",
            "--cpus=1",
            "--log-driver=none",
            "--entrypoint=/bin/sh",
            "--mount",
            f"type=bind,src={root / 'input'},dst=/input,readonly",
            "--mount",
            f"type=bind,src={root / 'owned'},dst=/candidate/owned",
            "--tmpfs",
            "/scratch:rw,noexec,nosuid,nodev,size=16777216,mode=1777",
            "--env",
            "HOME=/scratch/home",
            "--env",
            f"HOST_FIXTURE={root}",
            IMAGE,
            "/input/probe.sh",
        ]
        observation = None
        inspected = None
        cleanup = None
        effective_grant = False
        try:
            created = docker_capture(argv, environment)
            commands.append(created)
            if created.get("exit") == 0:
                inspected = docker_capture(["inspect", container], environment)
                commands.append(inspected)
                if inspected.get("exit") == 0:
                    effective_grant = verify_grant(json.loads(inspected["stdout"])[0], root)
                if not effective_grant:
                    raise ValueError("effective container grant differs from frozen requirements")
                observation = docker_capture(["start", "--attach", container], environment)
                commands.append(observation)
                terminal = docker_capture(
                    ["inspect", "--format", "{{json .State}}", container], environment
                )
                commands.append(terminal)
        finally:
            # Only the unique fixture handle is removed; existing user containers are untouched.
            cleanup = docker_capture(["rm", "--force", container], environment)
            commands.append(cleanup)
        unchanged = all(snapshot(root / part) == before for part, before in protected.items())
        approved_writes = (
            (root / "owned/existing.txt").read_text() == "approved"
            and (root / "owned/new.txt").is_file()
            and (root / "owned/new.txt").read_text() == "new"
            and not (root / "owned/hardlink.txt").exists()
        )
        success = (
            observation is not None
            and observation.get("exit") == 0
            and effective_grant
            and unchanged
            and approved_writes
            and cleanup.get("exit") == 0
            and observation.get("stdout", "").splitlines() == list(CASES)
        )
        kernel = (root / "owned/kernel.txt").read_text().strip() if success else "unavailable"
        toolchain = (root / "owned/toolchain.txt").read_text().strip() if success else "unavailable"
        # These are deliberately partial substrate observations, not runtime qualification.
        results = [
            ProbeResult(
                case=case,
                status=("passed" if success else "failed") if case in CASES else "unavailable",
                observation=(
                    "Synthetic shell attempts plus independent parent bytes/modes/link and grant checks"
                    if case in CASES and success
                    else "Synthetic probe or independent fixture verification did not pass"
                    if case in CASES
                    else "Not exercised by filesystem/environment subset; full runtime/broker qualification remains required"
                ),
            )
            for case in MANDATORY_CASES
        ]
        normalized = json.dumps(commands, sort_keys=True).replace(name, "<synthetic-root>")
        identity = QualificationIdentity(
            host_os=platform.platform(),
            host_kernel=platform.release(),
            architecture=platform.machine(),
            substrate="docker-desktop-linux-substrate-subset",
            substrate_version=digest(json.dumps(server, sort_keys=True).encode()),
            image=IMAGE.removeprefix("sha256:"),
            runtime=f"synthetic-shell:{toolchain}",
            toolchain=digest((kernel + toolchain).encode()),
            configuration=digest(
                json.dumps({"create": argv, "endpoint": args.docker_host}, sort_keys=True)
                .replace(name, "<synthetic-root>")
                .replace(container, "<fixture-container>")
                .encode()
            ),
            grant=digest(json.dumps(manifest["grant"], sort_keys=True).encode()),
            harness=digest(Path(__file__).read_bytes()),
            manifest=digest(args.manifest.read_bytes()),
        )
        record = Qualification(id="phase-2c-substrate-subset", identity=identity, results=results)
        report = {
            "schema_version": 1,
            "qualification": record.model_dump(mode="json"),
            "decision": assess_qualification(record, identity).model_dump(mode="json"),
            "commands": json.loads(normalized),
            "kernel": kernel,
            "toolchain": toolchain,
            "effective_grant_verified": effective_grant,
            "owned_files": snapshot(root / "owned"),
            "protected_fixtures_unchanged": unchanged,
            "approved_writes_observed": approved_writes,
            "fixture_container_removed": cleanup.get("exit") == 0,
            "scope": "9 filesystem/environment cases only; no product runtime or credential broker",
        }
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print("Subset passed" if success else "Subset failed", "; full Phase 2C remains denied.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
