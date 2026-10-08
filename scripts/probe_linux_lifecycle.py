"""Frozen no-model lifecycle probes, scoped to unique synthetic container handles."""

import argparse
import json
import os
from pathlib import Path
import platform
import tempfile
import time
import uuid

from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)
from scripts.probe_linux_profile import IMAGE, digest, docker_capture, snapshot, verify_grant

PROCESS_PAYLOAD = r"""set -eu
mkdir -p /scratch/home
setsid /bin/sh -c '
    /bin/sh -c '\''
        if cat /original/canary >/scratch/read 2>/scratch/error; then exit 51; fi
        if printf forbidden > /input/read.txt 2>/scratch/error; then exit 52; fi
        if wget -T 1 -O /scratch/network http://192.0.2.1/ 2>/scratch/error; then exit 53; fi
        [ -z "${CREWSHAL_SYNTHETIC_SECRET+x}" ]
        [ -z "${SSH_AUTH_SOCK+x}" ]
        printf "%s\n" "$$" > /candidate/owned/descendant.pid
        cat /proc/$$/status > /candidate/owned/descendant.status
        printf ready > /candidate/owned/ready
        while :; do printf x >> /candidate/owned/heartbeat; sleep 0.05; done
    '\'' &
    exit 0
' &
while :; do sleep 1; done
"""

VALIDATOR_PAYLOAD = r"""set -eu
mkdir -p /scratch/home
[ "$(cat /input/read.txt)" = "synthetic-frozen-candidate" ]
[ -z "${CREWSHAL_SYNTHETIC_SECRET+x}" ]
[ -z "${SSH_AUTH_SOCK+x}" ]
[ -z "${ANTHROPIC_API_KEY+x}" ]
[ -z "${OPENAI_API_KEY+x}" ]
[ ! -e /var/run/docker.sock ]
if printf forbidden > /input/read.txt 2>/scratch/error; then exit 54; fi
if wget -T 1 -O /scratch/network http://192.0.2.1/ 2>/scratch/error; then exit 55; fi
sha256sum /input/read.txt > /candidate/owned/candidate.sha256
printf validated > /candidate/owned/validated
"""

CASES = ("descendant-escape", "cancellation", "deadline", "credential-free-validation")
PAYLOADS = {"process": PROCESS_PAYLOAD, "validator": VALIDATOR_PAYLOAD}


def load_manifest(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError("prospectively frozen manifest digest mismatch")
    manifest = json.loads(raw)
    original = json.loads((path.parent / "phase-2c-v1.json").read_text())
    if (
        manifest["mandatory_cases"] != original["mandatory_cases"]
        or manifest["grant"] != original["grant"]
        or manifest["limits"] != original["limits"]
        or [case["id"] for case in manifest["mandatory_cases"]] != list(MANDATORY_CASES)
        or manifest["image"] != IMAGE
        or manifest["harness"] != digest(Path(__file__).read_bytes())
        or manifest["helper"]
        != digest(Path(__file__).with_name("probe_linux_profile.py").read_bytes())
        or manifest["qualification_module"]
        != digest(Path(__file__).parents[1].joinpath("src/crewshal/qualification.py").read_bytes())
        or manifest["payloads"] != {key: digest(value.encode()) for key, value in PAYLOADS.items()}
    ):
        raise ValueError("frozen protocol/source/image/payload mismatch")
    return manifest


def create_argv(root: Path, container: str) -> list[str]:
    return [
        "create",
        "--pull=never",
        "--name",
        container,
        "--label",
        "crewshal.qualification=2c-lifecycle",
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


def lifecycle_passes(observation: dict, mode: str) -> bool:
    """Parent oracle requires real process activity and engine terminal agreement."""
    terminal = observation.get("terminal", {})
    common = (
        observation.get("grant_verified") is True
        and observation.get("protected_unchanged") is True
        and observation.get("removed") is True
        and terminal.get("Running") is False
        and terminal.get("OOMKilled") is False
    )
    if mode == "validator":
        return common and terminal.get("ExitCode") == 0 and observation.get("validated") is True
    return (
        common
        and terminal.get("ExitCode") == 137
        and observation.get("ready") is True
        and observation.get("heartbeat_before", 0) > 0
        and observation.get("heartbeat_stopped") is True
        and observation.get("kill_exit") == 0
        and observation.get("detached_descendant") is True
        and observation.get("termination_reason")
        == ("cancelled" if mode == "cancel" else "timeout")
        and (mode == "cancel" or 4.9 <= observation.get("kill_requested_seconds", 100) <= 5.2)
    )


def run_case(parent: Path, environment: dict[str, str], mode: str) -> dict:
    root = parent / mode
    root.mkdir()
    for part in ("input", "owned", "original"):
        (root / part).mkdir(mode=0o755)
    (root / "owned").chmod(0o777)
    candidate = "synthetic-frozen-candidate" if mode == "validator" else "synthetic-readable"
    (root / "input/read.txt").write_text(candidate)
    (root / "input/probe.sh").write_text(
        VALIDATOR_PAYLOAD if mode == "validator" else PROCESS_PAYLOAD
    )
    (root / "original/canary").write_text("synthetic-excluded-dirty")
    protected = {part: snapshot(root / part) for part in ("input", "original")}
    container = "crewshal-2c-lifecycle-" + uuid.uuid4().hex
    commands = []

    def command(argv: list[str]) -> dict:
        result = docker_capture(argv, environment)
        commands.append(result)
        return result

    observation = {"mode": mode, "commands": commands, "grant_verified": False}
    try:
        created = command(create_argv(root, container))
        if created.get("exit") != 0:
            return observation
        inspected = command(["inspect", container])
        if inspected.get("exit") != 0:
            return observation
        info = json.loads(inspected["stdout"])[0]
        observation["grant_verified"] = verify_grant(info, root)
        observation["image"] = info["Image"]
        if not observation["grant_verified"]:
            return observation
        started_at = time.monotonic()
        if command(["start", container]).get("exit") != 0:
            return observation
        ready_path = root / "owned" / ("validated" if mode == "validator" else "ready")
        heartbeat = root / "owned/heartbeat"
        stop_at = started_at + 5
        while time.monotonic() < stop_at:
            if ready_path.exists() and (
                mode == "validator" or (heartbeat.exists() and heartbeat.stat().st_size > 0)
            ):
                break
            time.sleep(min(0.02, max(0, stop_at - time.monotonic())))
        observation["ready"] = ready_path.exists()
        if mode != "validator":
            observation["heartbeat_before"] = heartbeat.stat().st_size if heartbeat.exists() else 0
            top = command(["top", container, "-eo", "pid,ppid,sid,args"])
            observation["process_table"] = top.get("stdout", "")
            # The payload records PID in its own namespace. Engine top independently proves
            # a non-PID-1 shell remains in a session distinct from the original shell.
            rows = [line.split(None, 3) for line in str(top.get("stdout", "")).splitlines()[1:]]
            shells = [row for row in rows if len(row) == 4 and "/bin/sh" in row[3]]
            observation["detached_descendant"] = (
                top.get("exit") == 0
                and len(shells) >= 2
                and len({row[2] for row in shells}) >= 2
                and (root / "owned/descendant.pid").exists()
            )
            if mode == "deadline":
                while time.monotonic() < stop_at:
                    time.sleep(min(0.02, max(0, stop_at - time.monotonic())))
            observation["kill_requested_seconds"] = time.monotonic() - started_at
            observation["termination_reason"] = "cancelled" if mode == "cancel" else "timeout"
            observation["kill_exit"] = command(["kill", "--signal=KILL", container]).get("exit")
            terminal = command(["inspect", "--format", "{{json .State}}", container])
            observation["terminal"] = (
                json.loads(terminal["stdout"]) if terminal.get("exit") == 0 else {}
            )
            sizes = []
            for _ in range(3):
                sizes.append(heartbeat.stat().st_size if heartbeat.exists() else 0)
                time.sleep(0.1)
            observation["heartbeat_samples_after"] = sizes
            observation["heartbeat_stopped"] = len(set(sizes)) == 1 and sizes[0] > 0
        else:
            if not ready_path.exists():
                observation["error"] = "validator did not finish before deadline"
                return observation
            waited = command(["wait", container])
            terminal = command(["inspect", "--format", "{{json .State}}", container])
            observation["terminal"] = (
                json.loads(terminal["stdout"]) if terminal.get("exit") == 0 else {}
            )
            sha = root / "owned/candidate.sha256"
            observation["validated"] = (
                waited.get("exit") == 0
                and waited.get("stdout", "").strip() == "0"
                and ready_path.exists()
                and ready_path.read_text() == "validated"
                and sha.exists()
                and sha.read_text().split()[0] == digest(candidate.encode())
            )
    except (OSError, ValueError, KeyError, IndexError) as error:
        observation["error"] = str(error)
    finally:
        cleanup = command(["rm", "--force", container])
        observation["removed"] = cleanup.get("exit") == 0
        observation["protected_unchanged"] = all(
            snapshot(root / part) == before for part, before in protected.items()
        )
        observation["owned_files"] = snapshot(root / "owned")
        observation["passed"] = lifecycle_passes(observation, mode)
    return observation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker-host", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.docker_host.startswith("unix:///") or args.output.exists():
        parser.error("explicit local socket and nonexistent output required")
    try:
        manifest = load_manifest(args.manifest, args.manifest_sha256)
    except (ValueError, KeyError) as error:
        parser.error(str(error))
    with tempfile.TemporaryDirectory(prefix="crewshal-lifecycle-") as name:
        parent = Path(name)
        environment = {
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "HOME": name,
            "DOCKER_CONFIG": name,
            "DOCKER_HOST": args.docker_host,
            "CREWSHAL_SYNTHETIC_SECRET": "synthetic-never-real",
            "SSH_AUTH_SOCK": "/synthetic/nonexistent-agent.sock",
        }
        server = docker_capture(["version", "--format", "{{json .Server}}"], environment)
        observations = [
            run_case(parent, environment, mode) for mode in ("cancel", "deadline", "validator")
        ]
        statuses = {
            "descendant-escape": all(o["passed"] for o in observations[:2]),
            "cancellation": observations[0]["passed"],
            "deadline": observations[1]["passed"],
            "credential-free-validation": observations[2]["passed"],
        }
        identity = QualificationIdentity(
            host_os=platform.platform(),
            host_kernel=platform.release(),
            architecture=platform.machine(),
            substrate="docker-desktop-linux-lifecycle-subset",
            substrate_version=digest(json.dumps(server, sort_keys=True).encode()),
            image=IMAGE.removeprefix("sha256:"),
            runtime="synthetic-busybox-shell-only",
            toolchain=digest(IMAGE.encode()),
            configuration=digest(
                json.dumps(
                    {
                        "endpoint": args.docker_host,
                        "create": create_argv(Path("<synthetic-root>"), "<fixture-container>"),
                        "payloads": manifest["payloads"],
                    },
                    sort_keys=True,
                ).encode()
            ),
            grant=digest(json.dumps(manifest["grant"], sort_keys=True).encode()),
            harness=manifest["harness"],
            manifest=args.manifest_sha256,
        )
        record = Qualification(
            id="phase-2c-lifecycle-subset",
            identity=identity,
            results=[
                ProbeResult(
                    case=case,
                    status=("passed" if statuses[case] else "failed")
                    if case in statuses
                    else "unavailable",
                    observation="Synthetic process/validator and independent engine/parent observations; no native runtime or broker"
                    if case in statuses
                    else "Outside this subset; no promotion of previous observations",
                )
                for case in MANDATORY_CASES
            ],
        )
        report = {
            "schema_version": 1,
            "qualification": record.model_dump(mode="json"),
            "decision": assess_qualification(record, identity).model_dump(mode="json"),
            "server": server,
            "observations": observations,
            "scope": "Four bounded synthetic lifecycle/validator cases; HTTP denial is not full network-egress qualification",
        }
        normalized = json.dumps(report, indent=2).replace(name, "<synthetic-root>")
        for observation in observations:
            for command in observation["commands"]:
                for argument in command["argv"]:
                    if argument.startswith("crewshal-2c-lifecycle-"):
                        normalized = normalized.replace(argument, "<fixture-container>")
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(normalized + "\n")
    print(
        "Lifecycle subset passed" if all(statuses.values()) else "Lifecycle subset failed",
        "; full Phase 2C remains denied.",
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
