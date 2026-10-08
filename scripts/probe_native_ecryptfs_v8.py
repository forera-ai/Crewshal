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
import stat
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
    prior = BASE / "manifest-native-ecryptfs-v7.json"
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
        Path("/run/crewshal-native-response-fixture-v7.py"),
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
    m["worker_cpu_affinity"] = min(os.sched_getaffinity(0))
    m["scope"] = (
        "Trusted native compatibility on fresh eCryptfs scratch only; no complete qualification"
    )
    target = BASE / "manifest-native-ecryptfs-v8.json"
    with target.open("x") as f:
        json.dump(m, f, indent=2, sort_keys=True)
    print(json.dumps({"manifest_sha256": digest(target)}))


def run(expected, number):
    manifest = BASE / "manifest-native-ecryptfs-v8.json"
    if digest(manifest) != expected:
        raise RuntimeError("manifest changed")
    for p, h in json.loads(manifest.read_text())["bindings"].items():
        if digest(p) != h:
            raise RuntimeError("binding changed: " + p)
    cpu = json.loads(manifest.read_text())["worker_cpu_affinity"]
    if cpu not in os.sched_getaffinity(0):
        raise RuntimeError("bound CPU unavailable")
    root = BASE / "root"
    owned = BASE / f"ecryptfs-v8-f{number}"
    owned.mkdir(mode=0o700)
    image = owned / "image"
    lower = owned / "lower"
    upper = owned / "upper"
    lower.mkdir()
    upper.mkdir()
    mounts = []
    keys = []
    loop = None
    unit = f"crewshalnativecryptv8-f{number}.service"
    report = {
        "fixture": number,
        "scope": "Trusted native compatibility only",
        "execution_allowed": False,
        "native_start_allowed": False,
        "manifest_sha256": expected,
        "cleanup": {},
        "errors": [],
    }
    server = None
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
        spec = importlib.util.spec_from_file_location(
            "fixed_responses", "/run/crewshal-native-response-fixture-v7.py"
        )
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        server = fixture.start()
        wrapper = [
            "/usr/bin/nsenter",
            "--mount=/proc/" + str(os.getpid()) + "/ns/mnt",
            "--net=/proc/" + str(os.getpid()) + "/ns/net",
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
            "TOKIO_WORKER_THREADS",
            "1",
            "--setenv",
            "RAYON_NUM_THREADS",
            "1",
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
        ] + fixture.native_command(server.server_port)

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
            "CPUAffinity=" + str(cpu),
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
        supervisor_stopped = False
        samples = []
        begin = time.monotonic()
        try:
            while selector.get_map():
                if time.monotonic() - begin > 10:
                    raise TimeoutError("capture deadline")
                if group.exists() and (group / "cgroup.procs").read_text().strip():
                    try:
                        c = controls(group)
                        thread_names = {}
                        for pid in (group / "cgroup.procs").read_text().split():
                            try:
                                for task in Path("/proc", pid, "task").iterdir():
                                    name = (task / "comm").read_text().strip()
                                    thread_names[name] = thread_names.get(name, 0) + 1
                            except (FileNotFoundError, ProcessLookupError):
                                pass
                        if sum(thread_names.values()) >= report.get(
                            "thread_inventory_peak_count", 0
                        ):
                            report["thread_inventory_peak_count"] = sum(thread_names.values())
                            report["thread_inventory_peak"] = thread_names
                        report["worker_last_resources"] = {
                            n: (group / n).read_text().strip()
                            for n in (
                                "pids.current",
                                "pids.events",
                                "memory.current",
                                "memory.events",
                            )
                        }
                        report["worker_peak_tasks_observed"] = max(
                            report.get("worker_peak_tasks_observed", 0),
                            int((group / "pids.current").read_text()),
                        )
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
                if not supervisor_stopped:
                    events = []
                    for line in streams["stdout"].splitlines():
                        try:
                            events.append(json.loads(line))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
                    task_completed = any(
                        e.get("type") == "item.completed"
                        and e.get("item", {}).get("type") == "command_execution"
                        and e.get("item", {}).get("exit_code") == 0
                        for e in events
                    )
                    turn_completed = any(e.get("type") == "turn.completed" for e in events)
                    if task_completed and turn_completed:
                        fd = os.open(
                            upper / "native-tiny",
                            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                        )
                        try:
                            st = os.fstat(fd)
                            data = os.pread(fd, 8, 0)
                            if (
                                not stat.S_ISREG(st.st_mode)
                                or st.st_nlink != 1
                                or st.st_uid != 65534
                                or st.st_size != 4
                                or data != b"tiny"
                            ):
                                raise RuntimeError("independent live artifact mismatch")
                            report["live_artifact"] = {
                                "logical": st.st_size,
                                "allocated": st.st_blocks * 512,
                                "uid": st.st_uid,
                                "gid": st.st_gid,
                                "links": st.st_nlink,
                                "sha256": hashlib.sha256(data).hexdigest(),
                            }
                            report["verified_work_seconds"] = round(time.monotonic() - begin, 3)
                            stop_unit(unit)
                            report["supervisor_stop_after_verified_work"] = True
                            supervisor_stopped = True
                        finally:
                            os.close(fd)
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
        report["fixture_requests"] = fixture.requests
        report["tiny_exists_before_exit_check"] = (upper / "native-tiny").exists()
        if not report.get("supervisor_stop_after_verified_work") or report["worker_seconds"] > 5:
            raise RuntimeError("verified task or supervised termination refused")
        report["fixture_requests"] = fixture.requests
        report["tiny_workflow_passed"] = (upper / "native-tiny").is_file() and (
            upper / "native-tiny"
        ).read_bytes() == b"tiny"
        report["tiny_sha256"] = (
            digest(upper / "native-tiny") if (upper / "native-tiny").exists() else None
        )
        if not report["tiny_workflow_passed"]:
            raise RuntimeError("native tiny workflow refused")
    except Exception as e:
        report["errors"].append({"type": type(e).__name__, "message": str(e)[:1024]})
    finally:
        stop_unit(unit)
        if server is not None:
            server.shutdown()
            server.server_close()
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
        with (BASE / f"native-ecryptfs-v8-f{number}.json").open("x") as f:
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
