"""Proposed fixture-only native sandbox capability probe; never qualification."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import subprocess
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
    # Extend a fresh v1 data preparation only; this proposed profile has not run.
    prior = base / "manifest-compat-v9.json"
    manifest = json.loads(prior.read_text())
    for path, expected in manifest["bindings"].items():
        if digest(path) != expected:
            raise RuntimeError("prior binding changed: " + path)
    helper = Path("/run/crewshal-direct-mechanism-v5.py")
    spec = importlib.util.spec_from_file_location("owned_mechanism", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = base / "root"
    copied = [(Path("/usr/bin/bwrap"), root / "bin/bwrap-outer")]
    copied.extend(
        (library, root / library.relative_to("/"))
        for library in module.dependencies(Path("/usr/bin/bwrap"))
    )
    for source, target in copied:
        value = digest(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if digest(target) != value:
                raise RuntimeError("new dependency conflicts with existing bytes")
        else:
            with source.open("rb") as src, target.open("xb") as dst:
                while chunk := src.read(1048576):
                    dst.write(chunk)
            target.chmod(0o755 if os.access(source, os.X_OK) else 0o644)
        manifest["bindings"][str(source)] = value
        manifest["bindings"][str(target)] = value
    policy = Path("/run/crewshal-native-apparmor-proposal-v3.profile")
    if digest(policy) != "e20e454cbcf45fc26e8641707a4d2db751a9f86d9b6af81b33e2be605bb994fb":
        raise RuntimeError("proposed policy changed")
    for path in (
        policy,
        Path(__file__).resolve(),
        Path("/usr/sbin/apparmor_parser"),
        Path("/etc/apparmor.d/abi/4.0"),
    ):
        manifest["bindings"][str(path)] = digest(path)
    for library in module.dependencies(Path("/usr/sbin/apparmor_parser")):
        manifest["bindings"][str(library)] = digest(library)
    alias = root / "tmp"
    if not alias.is_symlink() or os.readlink(alias) != "/scratch":
        raise RuntimeError("prior scratch alias changed")
    manifest["owned_symlinks"] = {str(alias): "/scratch"}
    manifest["prepared_inventory"] = module.inventory(base)
    manifest["scope"] = (
        "prospective trusted tiny sandbox capability probe with fixture-only role policy; no full qualification"
    )
    for key in ("logical", "allocated"):
        if manifest["prepared_inventory"][key] > 1073741824:
            raise RuntimeError("prepared vendor reservation exceeded")
    path = base / "manifest-compat-v10.json"
    with path.open("x") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(
        json.dumps({"manifest_sha256": digest(path), "inventory": manifest["prepared_inventory"]})
    )


def run(base, expected):
    profiles = Path("/sys/kernel/security/apparmor/profiles").read_text().splitlines()
    for name in ("crewshal-native-bwrap-v1", "crewshal-native-tool-v1"):
        if name + " (enforce)" not in profiles:
            raise RuntimeError("required owner-approved fixture role policy is not enforcing")
    if digest(base / "manifest-compat-v10.json") != expected:
        raise RuntimeError("manifest changed")
    manifest = json.loads((base / "manifest-compat-v10.json").read_text())
    for path, value in manifest["bindings"].items():
        if digest(path) != value:
            raise RuntimeError("bound input changed: " + path)
    for path, target in manifest.get("owned_symlinks", {}).items():
        if os.readlink(path) != target:
            raise RuntimeError("scratch alias changed")
    root = base / "root"
    records = []
    commands = [
        [
            "/opt/codex/bin/codex",
            "sandbox",
            "--permission-profile",
            ":workspace",
            "-C",
            "/scratch",
            "--",
            "/bin/python3",
            "-I",
            "-B",
            "-c",
            "import os,json,ctypes,time; from pathlib import Path\nPath('/scratch/tiny').write_text('tiny')\nr={'tiny':Path('/scratch/tiny').read_text(),'uid':os.geteuid(),'label':Path('/proc/self/attr/current').read_text().strip(),'status':{k:v for k,v in (line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line) if k in ('CapEff','CapPrm','CapAmb','CapBnd','NoNewPrivs')},'ns':{n:os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','pid','net')}}\ntry:\n f=os.memfd_create('synthetic-capability',0); os.write(f,b'x'); os.close(f); r['memfd_denied']=False\nexcept OSError as e:r['memfd_denied']=e.errno==1\nlibc=ctypes.CDLL(None,use_errno=True); x=libc.unshare(0x10000000); r['userns_denied']=x==-1 and ctypes.get_errno()==1\nprint(json.dumps(r),flush=True); time.sleep(.1)\n",
        ]
    ]
    for fixture in (1, 2):
        for index, command in enumerate(commands):
            unit = f"crewshalnativecompatv10-f{fixture}-c{index}.service"
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
                "--property=MountAPIVFS=yes",
                "--property=ProtectProc=invisible",
                "--property=InaccessiblePaths=/sys /dev/shm",
                "--property=NoNewPrivileges=yes",
                "--property=RestrictNamespaces=user mnt pid net ipc uts",
                "--property=MemoryMax=134217728",
                "--property=MemorySwapMax=0",
                "--property=CPUQuota=100%",
                "--property=TasksMax=32",
                "--property=RuntimeMaxSec=5s",
                "--property=TimeoutStopSec=1s",
                "--property=KillMode=control-group",
                "--property=LimitFSIZE=65536",
                "--property=SystemCallFilter=~memfd_create shmget shmat linkat setxattr lsetxattr fsetxattr mknodat keyctl add_key request_key",
                "--property=SystemCallErrorNumber=EPERM",
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
                with (base / "compat-v10.json").open("w") as f:
                    json.dump(
                        {
                            "manifest_sha256": expected,
                            "records": records,
                            "scope": "trusted sandbox tiny-file and one-byte memfd capability discovery only; no hostile exhaustion, agent dispatch or broker qualification",
                            "execution_allowed": False,
                            "native_start_allowed": False,
                            "credential_mediation_qualified": False,
                        },
                        f,
                        indent=2,
                    )
    print(json.dumps({"records": len(records), "observed_sha256": digest(base / "compat-v10.json")}))


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
