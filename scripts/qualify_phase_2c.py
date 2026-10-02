"""Bounded Phase 2C preflight. Stops denied before unavailable worker probes.

This is a qualification utility, not a runtime launcher. A working daemon does
not implement the still-unqualified probe runner or credential broker.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

import pydantic
import pydantic_core
import crewshal
import crewshal.qualification

from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)

FROZEN_MANIFEST = "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"


def fingerprint(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def capture(argv: list[str], environment: dict[str, str]) -> dict[str, object]:
    """Trusted version/health commands only; ten seconds and private temp output."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.Popen(argv, env=environment, stdout=stdout, stderr=stderr)
        except OSError as error:
            return {"argv": argv, "status": "unavailable", "error": str(error)}
        try:
            code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
            return {"argv": argv, "status": "unavailable", "error": "preflight timeout"}
        stdout.seek(0)
        stderr.seek(0)
        raw_out, raw_err = stdout.read(65537), stderr.read(65537)
        if max(len(raw_out), len(raw_err)) > 65536:
            return {"argv": argv, "status": "unavailable", "error": "output limit exceeded"}
        return {
            "argv": argv,
            "exit": code,
            "stdout": raw_out.decode(errors="replace"),
            "stderr": raw_err.decode(errors="replace"),
            "stdout_digest": fingerprint(raw_out),
            "stderr_digest": fingerprint(raw_err),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.manifest.read_bytes()
    if fingerprint(raw) != FROZEN_MANIFEST:
        parser.error("frozen manifest digest mismatch; amend prospectively before probes")
    manifest = json.loads(raw)
    if [item["id"] for item in manifest["mandatory_cases"]] != list(MANDATORY_CASES):
        parser.error("mandatory cases differ from the frozen protocol")
    # The coordinator alone queries its explicit local endpoint. No socket is
    # mounted into a worker; no Docker context/credential config is read.
    with tempfile.TemporaryDirectory(prefix="crewshal-2c-home-") as home:
        environment = {
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "HOME": home,
            "DOCKER_CONFIG": home,
            "DOCKER_HOST": "unix:///var/run/docker.sock",
        }
        docker = shutil.which("docker", path=environment["PATH"]) or "/nonexistent/docker"
        client = capture([docker, "--version"], environment)
        server = capture([docker, "version", "--format", "{{json .Server}}"], environment)
        os_version = (
            capture(["/usr/bin/sw_vers"], environment)
            if platform.system() == "Darwin"
            else {"host": platform.platform()}
        )
        available = server.get("exit") == 0 and server.get("stdout") not in ("", "null\n")
        identity = QualificationIdentity(
            host_os=platform.platform(),
            host_kernel=platform.release(),
            architecture=platform.machine(),
            substrate="linux-container-docker",
            substrate_version=str(server["stdout"]).strip() if available else None,
            # No image/runtime/broker has been selected or qualified.
            toolchain=fingerprint(
                json.dumps(
                    {
                        "python": sys.version,
                        "crewshal": crewshal.__version__,
                        "pydantic": pydantic.__version__,
                        "pydantic_core": pydantic_core.__version__,
                        "docker_client": client,
                    },
                    sort_keys=True,
                ).encode()
            ),
            configuration=fingerprint(
                json.dumps(
                    {**environment, "HOME": "<synthetic>", "DOCKER_CONFIG": "<synthetic>"},
                    sort_keys=True,
                ).encode()
            ),
            grant=fingerprint(json.dumps(manifest["grant"], sort_keys=True).encode()),
            harness=fingerprint(
                Path(__file__).read_bytes() + Path(crewshal.qualification.__file__).read_bytes()
            ),
            manifest=fingerprint(raw),
        )
        reason = (
            "Linux daemon unavailable at explicit local endpoint; no worker launched"
            if not available
            else "Daemon available; worker probe runner and accepted credential mediation unavailable"
        )
        results = [
            ProbeResult(case=name, status="unavailable", observation=reason)
            for name in MANDATORY_CASES
        ]
        record = Qualification(id="phase-2c-preflight", identity=identity, results=results)
        report = {
            "schema_version": 1,
            "qualification": record.model_dump(mode="json"),
            "decision": assess_qualification(record, identity).model_dump(mode="json"),
            "preflight": {"os": os_version, "client": client, "server": server},
            "limits": manifest["limits"],
            "worker_launches": 0,
            "containment_probes_run": 0,
        }
        # Exclusive private output avoids overwriting evidence or repository data.
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(f"DENIED: {reason}. Writes disabled. Report: {args.output}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
