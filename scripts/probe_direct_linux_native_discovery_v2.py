"""Pinned, provider-free native version/help discovery; never agent qualification."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import selectors
import subprocess
import tarfile
import time

ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
ARCHIVES = {
    "codex-package-aarch64-unknown-linux-musl.tar.gz": "dff0954438fa455c2197ddb1f421d8d68625d98de610f76bedb6e5bc837ea35b",
    "codex-responses-api-proxy-aarch64-unknown-linux-musl.tar.gz": "75bcef0603b51ffca62877cc9368cf1937b8d4799e1367c33dc6963633f0d431",
}


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def prepare(base, inputs):
    helper = Path("/run/crewshal-direct-mechanism-v5.py")
    if digest(helper) != "175c7c76fac548c0cfe9fa6d6e1b7d0eff0539ccca2c4a64c68e9d2a1a635860":
        raise RuntimeError("helper source binding changed")
    spec = importlib.util.spec_from_file_location("owned_mechanism", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.prepare(base)
    manifest = json.loads((base / "manifest-v2.json").read_text())
    root = base / "root"
    copied = 0
    started = time.monotonic()
    for name, expected in ARCHIVES.items():
        source = inputs / name
        if digest(source) != expected:
            raise RuntimeError("vendor archive changed")
        manifest["bindings"][str(source)] = expected
        with tarfile.open(source, "r:gz") as tar:
            members = tar.getmembers()
            if len(members) > 20000:
                raise RuntimeError("archive member count exceeded")
            for member in members:
                path = PurePosixPath(member.name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or not (member.isfile() or member.isdir())
                ):
                    raise RuntimeError("unsafe vendor archive member")
                if member.isdir():
                    continue
                copied += member.size
                if copied > 1073741824 or time.monotonic() - started > 120:
                    raise RuntimeError("vendor preparation exceeded bound")
                target = root / "opt/codex" / str(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src, target.open("xb") as dst:
                    while chunk := src.read(1048576):
                        dst.write(chunk)
                if target.stat().st_size != member.size:
                    raise RuntimeError("vendor member size mismatch")
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
                manifest["bindings"][str(target)] = digest(target)
    manifest["bindings"][str(Path(__file__).resolve())] = digest(__file__)
    manifest["prepared_inventory"] = module.inventory(base)
    manifest["vendor_extracted_bytes"] = copied
    manifest["scope"] = (
        "trusted provider-free version/help only; not native/tool authority qualification"
    )
    # This preparation has not yet been frozen or used for discovery.
    (base / "manifest-v2.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "manifest_sha256": digest(base / "manifest-v2.json"),
                "inventory": manifest["prepared_inventory"],
                "bound_files": len(manifest["bindings"]),
            }
        )
    )


def run(base, expected):
    if digest(base / "manifest-v2.json") != expected:
        raise RuntimeError("manifest changed")
    manifest = json.loads((base / "manifest-v2.json").read_text())
    for path, value in manifest["bindings"].items():
        if digest(path) != value:
            raise RuntimeError("bound input changed: " + path)
    root = base / "root"
    records = []
    commands = [
        ["/opt/codex/bin/codex", "--version"],
        ["/opt/codex/bin/codex", "--help"],
        ["/opt/codex/bin/codex", "sandbox", "linux", "--help"],
        ["/opt/codex/codex-responses-api-proxy-aarch64-unknown-linux-musl", "--help"],
    ]
    for fixture in (1, 2):
        for index, command in enumerate(commands):
            unit = f"crewshalnativev2-f{fixture}-c{index}.service"
            argv = [
                "/usr/bin/systemd-run",
                "--unit=" + unit,
                "--slice=crewshalnativediscoveryv1.slice",
                "--wait",
                "--pipe",
                "--collect",
                "--property=User=65534",
                "--property=Group=65534",
                "--property=RootDirectory=" + str(root),
                "--property=WorkingDirectory=/input",
                "--property=ProtectSystem=strict",
                "--property=ProtectHome=yes",
                "--property=PrivateNetwork=yes",
                "--property=PrivateDevices=yes",
                "--property=NoNewPrivileges=yes",
                "--property=RestrictNamespaces=yes",
                "--property=MemoryMax=134217728",
                "--property=MemorySwapMax=0",
                "--property=CPUQuota=100%",
                "--property=TasksMax=32",
                "--property=RuntimeMaxSec=5s",
                "--property=TimeoutStopSec=1s",
                "--property=KillMode=control-group",
                "--property=LimitFSIZE=65536",
                "--property=TemporaryFileSystem=/scratch:size=8388608,nr_inodes=256,nodev,nosuid,noexec,mode=0755,uid=65534,gid=65534",
                "--setenv=HOME=/scratch",
                "--setenv=CODEX_HOME=/scratch",
                "--setenv=PATH=/opt/codex/codex-path:/bin:/usr/bin",
                *command,
            ]
            proc = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=ENV,
            )
            streams = {"stdout": bytearray(), "stderr": bytearray()}
            selector = selectors.DefaultSelector()
            for name, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
                selector.register(stream, selectors.EVENT_READ, name)
            group = Path("/sys/fs/cgroup/crewshalnativediscoveryv1.slice") / unit
            samples = []
            started = time.monotonic()
            try:
                while selector.get_map():
                    if time.monotonic() - started > 10:
                        raise TimeoutError("trusted capture exceeded command ceiling")
                    if group.exists() and (group / "cgroup.procs").read_text().strip():
                        try:
                            sample = {
                                n: (group / n).read_text().strip()
                                for n in ("memory.max", "memory.swap.max", "cpu.max", "pids.max")
                            }
                            if sample not in samples:
                                samples.append(sample)
                        except FileNotFoundError:
                            pass
                    for key, _ in selector.select(0.005):
                        chunk = os.read(key.fileobj.fileno(), 4096)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        streams[key.data].extend(chunk)
                        if len(streams[key.data]) > 65536:
                            raise RuntimeError("trusted capture stream exceeded ceiling")
                code = proc.wait(timeout=1)
                records.append(
                    {
                        "fixture": fixture,
                        "command": command,
                        "argv": argv,
                        "exit": code,
                        "seconds": time.monotonic() - started,
                        "controls": samples,
                        "stdout": streams["stdout"].decode(),
                        "stderr": streams["stderr"].decode(),
                    }
                )
                if code or not samples:
                    raise RuntimeError("trusted native discovery refused")
                required = {
                    "memory.max": "134217728",
                    "memory.swap.max": "0",
                    "cpu.max": "100000 100000",
                    "pids.max": "32",
                }
                if any(sample != required for sample in samples):
                    raise RuntimeError("native discovery limits changed")
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                selector.close()
                # A failing service is terminated too; no detached service survives capture.
                subprocess.run(
                    ["/usr/bin/systemctl", "stop", unit],
                    env=ENV,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
                with (base / "discovery-v2.json").open("w") as f:
                    json.dump(
                        {
                            "manifest_sha256": expected,
                            "records": records,
                            "scope": "trusted version/help; no agent/native tool dispatch",
                            "execution_allowed": False,
                            "native_start_allowed": False,
                            "credential_mediation_qualified": False,
                        },
                        f,
                        indent=2,
                    )
    print(
        json.dumps({"records": len(records), "observed_sha256": digest(base / "discovery-v2.json")})
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("base", type=Path)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        parser.error("requires supplied test-only aarch64 Linux root role")
    if args.mode == "prepare":
        prepare(args.base, args.inputs)
    else:
        run(args.base, args.manifest_sha256)


if __name__ == "__main__":
    main()
