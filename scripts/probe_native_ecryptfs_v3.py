"""Trusted native compatibility diagnostic using existing kernel storage; not qualification."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import time

ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
BASE = Path("/var/tmp/crewshal-native-discovery-v1")
SLICE = "crewshalnativediscoveryv1.slice"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def command(argv, data=None):
    r = subprocess.run(argv, input=data, capture_output=True, env=ENV, timeout=10)
    if max(len(r.stdout), len(r.stderr)) > 65536:
        raise RuntimeError("helper output exceeds bound")
    if r.returncode:
        raise RuntimeError(Path(argv[0]).name + ": " + r.stderr.decode(errors="replace")[:512])
    return r.stdout.decode().strip()


def stop_unit(unit):
    result = subprocess.run(
        ["/usr/bin/systemctl", "stop", unit], capture_output=True, timeout=10, env=ENV
    )
    if max(len(result.stdout), len(result.stderr)) > 65536:
        raise RuntimeError("stop capture exceeds ceiling")
    group = Path("/sys/fs/cgroup") / SLICE / unit
    if group.exists() and "populated 1" in (group / "cgroup.events").read_text():
        raise RuntimeError("owned worker remains populated")


def controls(path):
    return {
        n: (path / n).read_text().strip()
        for n in ("memory.max", "memory.swap.max", "cpu.max", "pids.max")
    }


def prepare():
    prior = BASE / "manifest-compat-v22.json"
    m = json.loads(prior.read_text())
    for p, h in m["bindings"].items():
        if digest(p) != h:
            raise RuntimeError("prior binding changed: " + p)
    helper = Path("/run/crewshal-direct-mechanism-v5.py")
    spec = importlib.util.spec_from_file_location("bound_mechanism", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for p in (
        Path(__file__).resolve(),
        Path("/usr/bin/nsenter"),
        Path("/usr/bin/keyctl"),
        Path("/usr/sbin/mkfs.ext4"),
        Path("/usr/sbin/losetup"),
        Path("/usr/bin/mount"),
        Path("/usr/bin/umount"),
        Path("/usr/bin/bwrap"),
        Path("/usr/bin/setpriv"),
    ):
        m["bindings"][str(p)] = digest(p)
        for library in module.dependencies(p) if p.read_bytes()[:4] == b"\x7fELF" else ():
            m["bindings"][str(library)] = digest(library)
    m["scope"] = (
        "Trusted native compatibility on fresh eCryptfs scratch only; no complete qualification"
    )
    target = BASE / "manifest-native-ecryptfs-v3.json"
    with target.open("x") as f:
        json.dump(m, f, indent=2, sort_keys=True)
    print(json.dumps({"manifest_sha256": digest(target)}))


def run(expected, number):
    manifest = BASE / "manifest-native-ecryptfs-v3.json"
    if digest(manifest) != expected:
        raise RuntimeError("manifest changed")
    for p, h in json.loads(manifest.read_text())["bindings"].items():
        if digest(p) != h:
            raise RuntimeError("binding changed: " + p)
    root = BASE / "root"
    owned = BASE / f"ecryptfs-v3-f{number}"
    owned.mkdir(mode=0o700)
    image = owned / "image"
    lower = owned / "lower"
    upper = owned / "upper"
    lower.mkdir()
    upper.mkdir()
    mounts = []
    keys = []
    loop = None
    unit = f"crewshalnativecryptv3-f{number}.service"
    report = {
        "fixture": number,
        "scope": "Trusted native compatibility only",
        "execution_allowed": False,
        "native_start_allowed": False,
        "manifest_sha256": expected,
        "cleanup": {},
        "errors": [],
    }
    started = time.monotonic()
    try:
        if command(["/usr/bin/keyctl", "list", "@s"]) != "keyring is empty":
            raise RuntimeError("anonymous ring not empty")
        name = "crewshal-native-master-" + os.urandom(8).hex()
        keys.append(command(["/usr/bin/keyctl", "padd", "user", name, "@s"], os.urandom(32)))
        signature = os.urandom(8).hex()
        keys.append(
            command(
                [
                    "/usr/bin/keyctl",
                    "add",
                    "encrypted",
                    signature,
                    "new ecryptfs user:" + name + " 64",
                    "@s",
                ]
            )
        )
        with image.open("xb") as f:
            f.truncate(33554432)
        command(["/usr/sbin/mkfs.ext4", "-q", "-F", "-m", "0", str(image)])
        loop = command(["/usr/sbin/losetup", "--find", "--show", "--nooverlap", str(image)])
        if command(["/usr/sbin/losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(
            image
        ):
            raise RuntimeError("loop identity changed")
        command(
            ["/usr/bin/mount", "-i", "-t", "ext4", "-o", "nodev,nosuid,noexec", loop, str(lower)]
        )
        mounts.append(lower)
        command(
            [
                "/usr/bin/mount",
                "-i",
                "-t",
                "ecryptfs",
                "-o",
                "nodev,nosuid,noexec,ecryptfs_sig="
                + signature
                + ",ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_mount_auth_tok_only",
                str(lower),
                str(upper),
            ]
        )
        mounts.append(upper)
        os.chown(upper, 65534, 65534)
        upper.chmod(0o700)
        report["mounts"] = [
            s for s in Path("/proc/self/mountinfo").read_text().splitlines() if str(owned) in s
        ]
        report["aggregate_controls"] = controls(Path("/sys/fs/cgroup") / SLICE)
        if report["aggregate_controls"] != {
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "128",
        }:
            raise RuntimeError("aggregate controls changed")
        if time.monotonic() - started > 120:
            raise RuntimeError("startup ceiling exceeded")
        wrapper = [
            "/usr/bin/nsenter",
            "--mount=/proc/" + str(os.getpid()) + "/ns/mnt",
            "--",
            "/usr/bin/bwrap",
            "--ro-bind",
            str(root),
            "/",
            "--bind",
            str(upper),
            "/scratch",
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--unshare-pid",
            "--unshare-net",
            "--unshare-ipc",
            "--unshare-uts",
            "--new-session",
            "--die-with-parent",
            "--clearenv",
            "--setenv",
            "HOME",
            "/scratch",
            "--setenv",
            "CODEX_HOME",
            "/scratch",
            "--setenv",
            "PATH",
            "/opt/codex/codex-path:/bin:/usr/bin",
            "--cap-drop",
            "ALL",
            "--cap-add",
            "CAP_SETUID",
            "--cap-add",
            "CAP_SETGID",
            "--cap-add",
            "CAP_SETPCAP",
            "--",
            "/bin/setpriv",
            "--reuid=65534",
            "--regid=65534",
            "--clear-groups",
            "--bounding-set=-all",
            "--inh-caps=-all",
            "--ambient-caps=-all",
            "--no-new-privs",
            "/bin/python3",
            "-I",
            "-B",
            "/input/native_fixed_response_fixture_v4.py",
        ]
        argv = [
            "/usr/bin/systemd-run",
            "--unit=" + unit,
            "--slice=" + SLICE,
            "--wait",
            "--pipe",
            "--collect",
            "-p",
            "MemoryMax=134217728",
            "-p",
            "MemorySwapMax=0",
            "-p",
            "CPUQuota=100%",
            "-p",
            "TasksMax=32",
            "-p",
            "RuntimeMaxSec=5s",
            "-p",
            "TimeoutStopSec=1s",
            "-p",
            "KillMode=control-group",
            "-p",
            "LimitFSIZE=infinity",
            "-p",
            "SystemCallFilter=~memfd_create shmget shmat linkat setxattr lsetxattr fsetxattr mknodat keyctl add_key request_key",
            "-p",
            "SystemCallErrorNumber=EPERM",
            *wrapper,
        ]
        report["argv"] = argv
        p = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV
        )
        selector = selectors.DefaultSelector()
        streams = {"stdout": bytearray(), "stderr": bytearray()}
        for n, s in [("stdout", p.stdout), ("stderr", p.stderr)]:
            selector.register(s, selectors.EVENT_READ, n)
        group = Path("/sys/fs/cgroup") / SLICE / unit
        samples = []
        begin = time.monotonic()
        try:
            while selector.get_map():
                if time.monotonic() - begin > 10:
                    raise TimeoutError("capture deadline")
                if group.exists() and (group / "cgroup.procs").read_text().strip():
                    try:
                        c = controls(group)
                        if c not in samples:
                            samples.append(c)
                    except FileNotFoundError:
                        pass
                for k, _ in selector.select(0.005):
                    b = os.read(k.fileobj.fileno(), 4096)
                    if not b:
                        selector.unregister(k.fileobj)
                        continue
                    streams[k.data].extend(b)
                    if len(streams[k.data]) > 65536:
                        raise RuntimeError("capture output ceiling")
            report.update(
                exit=p.wait(timeout=1),
                stdout=streams["stdout"].decode(),
                stderr=streams["stderr"].decode(),
                worker_controls=samples,
                worker_seconds=round(time.monotonic() - begin, 3),
            )
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()
            selector.close()
            stop_unit(unit)
        report["upper_inventory"] = [
            {
                "path": str(p.relative_to(upper)),
                "size": p.lstat().st_size,
                "allocated": p.lstat().st_blocks * 512,
            }
            for p in upper.rglob("*")
        ]
        report["lower_inventory"] = [
            {
                "path": str(p.relative_to(lower)),
                "size": p.lstat().st_size,
                "allocated": p.lstat().st_blocks * 512,
            }
            for p in lower.rglob("*")
        ]
        if not samples or any(
            c
            != {
                "memory.max": "134217728",
                "memory.swap.max": "0",
                "cpu.max": "100000 100000",
                "pids.max": "32",
            }
            for c in samples
        ):
            raise RuntimeError("worker controls unavailable or changed")
        if report["exit"] != 0:
            raise RuntimeError("native compatibility worker refused")
        result = json.loads(report["stdout"])
        report["tiny_workflow_passed"] = result["exit"] == 0 and result["tiny"] == "tiny"
        if not report["tiny_workflow_passed"]:
            raise RuntimeError("native tiny workflow refused")
    except Exception as e:
        report["errors"].append({"type": type(e).__name__, "message": str(e)[:1024]})
    finally:
        stop_unit(unit)
        report["cleanup"]["unmounts"] = []
        for mount in reversed(mounts):
            try:
                command(["/usr/bin/umount", str(mount)])
                report["cleanup"]["unmounts"].append({"view": mount.name, "unmounted": True})
            except Exception as e:
                report["cleanup"]["unmounts"].append(
                    {"view": mount.name, "unmounted": False, "error": str(e)[:512]}
                )
        unmounted = all(x["unmounted"] for x in report["cleanup"]["unmounts"])
        if loop and unmounted:
            if command(["/usr/sbin/losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(
                image
            ):
                raise RuntimeError("cleanup loop identity changed")
            command(["/usr/sbin/losetup", "--detach", loop])
            report["cleanup"]["loop_detached"] = True
        for key in reversed(keys):
            command(["/usr/bin/keyctl", "revoke", key])
            command(["/usr/bin/keyctl", "unlink", key, "@s"])
        report["cleanup"]["anonymous_ring_empty"] = (
            command(["/usr/bin/keyctl", "list", "@s"]) == "keyring is empty"
        )
        if unmounted and (not loop or report["cleanup"].get("loop_detached")):
            shutil.rmtree(owned)
        report["cleanup"]["owned_files_absent"] = not owned.exists()
        report["seconds"] = round(time.monotonic() - started, 3)
        with (BASE / f"native-ecryptfs-v3-f{number}.json").open("x") as f:
            json.dump(report, f, indent=2)
    print(
        json.dumps(
            {
                "errors": report["errors"],
                "tiny_workflow_passed": report.get("tiny_workflow_passed", False),
                "seconds": report["seconds"],
            }
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["prepare", "run"])
    p.add_argument("--manifest-sha256")
    p.add_argument("--fixture", type=int, choices=[1, 2])
    a = p.parse_args()
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        p.error("supplied aarch64 root test role required")
    if a.mode == "prepare":
        prepare()
    else:

        def interrupted(signum, frame):
            raise RuntimeError("trusted driver cleanup reserve signal")

        signal.signal(signal.SIGTERM, interrupted)
        run(a.manifest_sha256, a.fixture)
