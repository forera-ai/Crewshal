"""Pinned SBX help-only assessment; no daemon, login, secret store or worker launch."""

import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile

from scripts.probe_linux_profile import digest

BINARY_SHA256 = "cca2b8379897afa957f6f0fbe98ff45724ddb10e135f1b575232581fdc3caad3"
PARENT_SHA256 = "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
COMMANDS = (
    ("version",),
    ("create", "--help"),
    ("daemon", "start", "--help"),
    ("exec", "--help"),
    ("secret", "set-custom", "--help"),
    ("settings", "--help"),
)
SOURCES = {
    "scripts/assess_sbx_protocol.py",
    "scripts/probe_linux_profile.py",
    "docs/SBX-RESOURCE-CONFIGURATION-PROTOCOL.md",
}
SANDBOX = "(version 1)(allow default)(deny network*)"


def load_manifest(path: Path, expected: str) -> dict:
    """Refuse changed requirements before invoking even the help-only binary."""
    if digest(path.read_bytes()) != expected:
        raise ValueError("prospectively frozen manifest digest mismatch")
    manifest = json.loads(path.read_text())
    root = Path(__file__).resolve().parents[1]
    parent = root / "docs/qualification/phase-2c-v1.json"
    original = json.loads(parent.read_text())
    if (
        type(manifest.get("schema_version")) is not int
        or manifest["schema_version"] != 1
        or manifest.get("parent_manifest") != PARENT_SHA256
        or digest(parent.read_bytes()) != PARENT_SHA256
        or any(manifest.get(key) != original[key] for key in ("grant", "limits", "mandatory_cases"))
        or manifest.get("binary_sha256") != BINARY_SHA256
        or manifest.get("commands") != [list(c) for c in COMMANDS]
        or set(manifest.get("sources", {})) != SOURCES
        or manifest["sources"] != {p: digest((root / p).read_bytes()) for p in SOURCES}
        or manifest.get("assessment") != "help-only; no operational authority"
        or manifest.get("outer_proposal")
        != {"memory_bytes": 536870912, "cpus": 1, "approval": "pending", "launch_allowed": False}
    ):
        raise ValueError("frozen protocol/source/resource/command mismatch")
    return manifest


def capture(binary: Path, arguments: tuple[str, ...], home: Path) -> dict:
    if arguments not in COMMANDS:
        raise ValueError("command outside help-only allowlist")
    argv = ["/usr/bin/sandbox-exec", "-p", SANDBOX, str(binary), *arguments]
    try:
        result = subprocess.run(
            argv,
            cwd=home,
            env={"HOME": str(home), "XDG_CONFIG_HOME": str(home), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"arguments": list(arguments), "exit": None, "error": "help command unavailable"}
    if max(len(result.stdout), len(result.stderr)) > 65536:
        return {"arguments": list(arguments), "exit": None, "error": "help output limit exceeded"}
    return {
        "arguments": list(arguments),
        "exit": result.returncode,
        "stdout": result.stdout.decode(errors="replace"),
        "stderr": result.stderr.decode(errors="replace"),
    }


def assess(commands: list[dict]) -> dict:
    """Help availability cannot establish nested enforcement or broker authority."""
    names = [tuple(c.get("arguments", [])) for c in commands]
    successful = names == list(COMMANDS) and all(c.get("exit") == 0 for c in commands)
    create = next(
        (c.get("stdout", "") for c in commands if c.get("arguments") == ["create", "--help"]), ""
    )
    advertised = successful and "Minimum: 512 MiB" in create
    return {
        "help_complete": successful,
        "advertised_outer_minimum_bytes": 536870912 if advertised else None,
        "frozen_worker_memory_bytes": 134217728,
        "direct_worker_mapping": "incompatible advertised minimum" if advertised else "unavailable",
        "nested_worker_mapping": "unavailable; no independently enforced inner worker observed",
        "credential_store_isolation": "unavailable; synthetic HOME does not isolate macOS Keychain",
        "request_authority": "unavailable; sentinel masking is not caller authorization evidence",
        "operational_launch_allowed": False,
        "execution_allowed": False,
        "status": "denied",
    }


def run_assessment(binary: Path, manifest: Path, expected: str) -> dict:
    frozen = load_manifest(manifest, expected)
    if binary.is_symlink() or not binary.is_file() or digest(binary.read_bytes()) != BINARY_SHA256:
        raise ValueError("pinned SBX binary mismatch")
    if platform.system() != "Darwin":
        raise ValueError("help assessment requires recorded macOS network-denial wrapper")
    with tempfile.TemporaryDirectory(prefix="crewshal-sbx-assessment-") as name:
        commands = [capture(binary, c, Path(name)) for c in COMMANDS]
    return {
        "schema_version": 1,
        "manifest_sha256": expected,
        "binary_sha256": BINARY_SHA256,
        "sources": frozen["sources"],
        "environment": "empty inherited environment; synthetic HOME/XDG_CONFIG_HOME; network denied",
        "host": {
            "os": platform.platform(),
            "kernel": platform.release(),
            "architecture": platform.machine(),
        },
        "commands": commands,
        "decision": assess(commands),
        "daemon_started": False,
        "login_attempted": False,
        "secret_commands_executed": False,
        "worker_launched": False,
        "mandatory_results": [
            {"case": c["id"], "status": "unavailable"} for c in frozen["mandatory_cases"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Reserve the observation before any subprocess; do not overwrite files or links.
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        try:
            report = run_assessment(args.binary, args.manifest, args.manifest_sha256)
        except ValueError as error:
            report = {"status": "refused", "reason": str(error), "execution_allowed": False}
        stream.write(json.dumps(report, indent=2) + "\n")
    print("SBX protocol assessment complete; operational qualification denied.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
