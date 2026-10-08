"""Synthetic, no-model assessment of the pinned public Orka helper seam."""

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

REVISION = "9e366915fc6cd6ede5aa47ac7a3b418a32ff528b"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    head = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    if head != REVISION:
        parser.error("public Orka revision mismatch")
    subprocess.run(
        ["git", "-C", str(source), "diff", "--exit-code", "HEAD", "--", "scripts"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    sys.path.insert(0, str(source / "scripts"))
    module = importlib.import_module("native_gateway")
    environment = {
        "PATH": "/synthetic/bin",
        "ANTHROPIC_API_KEY": "synthetic-old",
        "CREWSHAL_SYNTHETIC_OTHER_SECRET": "synthetic-not-real",
        "SSH_AUTH_SOCK": "/synthetic/agent.sock",
    }
    child = module.claude_child_environment(
        environment,
        "synthetic-broker-token",
        "http://synthetic.invalid",
    )
    settings = {"hooks": {"PreToolUse": [{"command": "synthetic-never-executed"}]}}
    command = module.claude_launch_arguments(
        ["claude", "--settings", json.dumps(settings)],
        "synthetic-broker-token",
        "http://synthetic.invalid",
    )
    effective = json.loads(command[command.index("--settings") + 1])
    report = {
        "revision": head,
        "native_gateway_sha256": hashlib.sha256(
            (source / "scripts/native_gateway.py").read_bytes(),
        ).hexdigest(),
        "checks": {
            "provider_key_replaced": child["ANTHROPIC_API_KEY"] == "synthetic-broker-token",
            "ambient_other_secret_excluded": "CREWSHAL_SYNTHETIC_OTHER_SECRET" not in child,
            "ssh_agent_excluded": "SSH_AUTH_SOCK" not in child,
            "injected_hook_removed": "hooks" not in effective,
        },
        "runtime_launches": 0,
        "provider_calls": 0,
        "scope": "Pure helper behavior only; no filesystem/network/process qualification",
    }
    print(json.dumps(report, indent=2))
    return 2 if not all(report["checks"].values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
