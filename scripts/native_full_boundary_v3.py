"""Trusted parent oracles for the frozen synthetic native profile; no executor API."""

import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import stat
import subprocess
import time

EXPECTED = {
    "memory.max": "134217728",
    "memory.swap.max": "0",
    "cpu.max": "100000 100000",
    "pids.max": "32",
}
ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}


class BoundaryFailure(RuntimeError):
    def __init__(self, message, report):
        super().__init__(message)
        self.report = report


def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        item = path.lstat()
        row = {"mode": item.st_mode, "links": item.st_nlink, "size": item.st_size}
        if stat.S_ISREG(item.st_mode):
            with path.open("rb") as stream:
                row["sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
        elif stat.S_ISLNK(item.st_mode):
            row["target"] = os.readlink(path)
        elif not stat.S_ISDIR(item.st_mode):
            raise RuntimeError("special file in candidate snapshot")
        result[str(path.relative_to(root))] = row
    return result


def usage(root, group):
    """Count each visible or deleted-open inode once, independently of worker claims."""
    objects = {}
    device = root.stat().st_dev
    for path in [root, *root.rglob("*")]:
        try:
            item = path.lstat()
            objects[(item.st_dev, item.st_ino)] = item
        except FileNotFoundError:
            pass
    if group.exists():
        try:
            pids = (group / "cgroup.procs").read_text().split()
        except FileNotFoundError:
            pids = []
        for pid in pids:
            try:
                handles = list(Path("/proc", pid, "fd").iterdir())
            except (FileNotFoundError, ProcessLookupError):
                continue
            for handle in handles:
                try:
                    item = handle.stat()
                    if item.st_dev == device:
                        objects[(item.st_dev, item.st_ino)] = item
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    pass
    return {
        "logical": sum(item.st_size for item in objects.values()),
        "allocated": sum(item.st_blocks * 512 for item in objects.values()),
        "inodes": len(objects),
        "deleted_open": sum(item.st_nlink == 0 for item in objects.values()),
    }


def capture(argv, group, heartbeat=None, cancel=False):
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=ENV,
    )
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    selector = selectors.DefaultSelector()
    for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
        selector.register(stream, selectors.EVENT_READ, name)
    started = time.monotonic()
    observed = {}
    controls = []
    roles = []
    cancelled = False
    first_heartbeat = None
    report = {"argv": argv}
    try:
        while selector.get_map():
            elapsed = time.monotonic() - started
            if elapsed > 10:
                raise TimeoutError("boundary capture exceeds ten seconds")
            try:
                if group.exists():
                    sample = {name: (group / name).read_text().strip() for name in EXPECTED}
                    if sample != EXPECTED:
                        report["control_mismatch"] = {
                            "observed": sample,
                            "expected": EXPECTED.copy(),
                            "group": str(group),
                            "pids": (group / "cgroup.procs").read_text().split(),
                            "seconds": elapsed,
                        }
                        raise RuntimeError("boundary cgroup limits differ from frozen limits")
                    if sample not in controls:
                        controls.append(sample)
                    for pid in (group / "cgroup.procs").read_text().split():
                        try:
                            observed[pid] = (
                                Path("/proc", pid, "stat").read_text().rsplit(")", 1)[1].split()[19]
                            )
                            label = Path("/proc", pid, "attr/current").read_text().strip()
                            if "crewshal-native-tool-v1" in label:
                                status = {
                                    key: value.strip()
                                    for key, value in (
                                        line.split(":", 1)
                                        for line in Path("/proc", pid, "status")
                                        .read_text()
                                        .splitlines()
                                        if ":" in line
                                    )
                                    if key
                                    in ("Uid", "CapEff", "CapPrm", "CapAmb", "CapBnd", "NoNewPrivs")
                                }
                                row = {"pid": int(pid), "label": label, "status": status}
                                if row not in roles:
                                    roles.append(row)
                        except (FileNotFoundError, ProcessLookupError):
                            pass
                    report["last_resources"] = {
                        name: (group / name).read_text().strip()
                        for name in (
                            "pids.current",
                            "pids.events",
                            "memory.current",
                            "memory.events",
                        )
                    }
            except FileNotFoundError:
                pass
            if heartbeat is not None and heartbeat.exists() and heartbeat.stat().st_size:
                if first_heartbeat is None:
                    first_heartbeat = elapsed
                if cancel and not cancelled and elapsed - first_heartbeat >= 0.08:
                    subprocess.run(
                        ["/usr/bin/systemctl", "stop", group.name],
                        check=True,
                        capture_output=True,
                        timeout=1,
                        env=ENV,
                    )
                    cancelled = True
                    report["cancel_requested_seconds"] = elapsed
            for key, _ in selector.select(0.005):
                data = os.read(key.fileobj.fileno(), 4096)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                streams[key.data].extend(data)
                if len(streams[key.data]) > 65536:
                    raise RuntimeError("boundary output exceeds per-stream limit")
        report.update(
            exit=process.wait(timeout=1),
            seconds=time.monotonic() - started,
            controls=controls,
            roles=roles,
            stdout=streams["stdout"].decode(errors="replace"),
            stderr=streams["stderr"].decode(errors="replace"),
        )
    except Exception as error:
        report.update(
            stdout=streams["stdout"][:65536].decode(errors="replace"),
            stderr=streams["stderr"][:65536].decode(errors="replace"),
            seconds=time.monotonic() - started,
            controls=controls,
            roles=roles,
        )
        raise BoundaryFailure(str(error), report) from error
    finally:
        subprocess.run(
            ["/usr/bin/systemctl", "stop", group.name],
            capture_output=True,
            timeout=10,
            env=ENV,
        )
        if process.poll() is None:
            process.kill()
            process.wait(timeout=1)
        selector.close()
    if not controls:
        raise BoundaryFailure("independent boundary controls unavailable", report)
    if group.exists() and "populated 1" in (group / "cgroup.events").read_text():
        raise RuntimeError("boundary cgroup remains populated")
    for pid, birth in observed.items():
        try:
            if Path("/proc", pid, "stat").read_text().rsplit(")", 1)[1].split()[19] == birth:
                raise RuntimeError("observed boundary process survives termination")
        except (FileNotFoundError, ProcessLookupError):
            pass
    report["observed_processes_absent"] = True
    if heartbeat is not None:
        if first_heartbeat is None:
            raise BoundaryFailure("detached heartbeat never observed", report)
        before = heartbeat.read_bytes()
        time.sleep(0.08)
        if heartbeat.read_bytes() != before:
            raise RuntimeError("detached heartbeat continues after terminal capture")
        report["heartbeat_stopped"] = True
        report["heartbeat_bytes"] = len(before)
        if not roles:
            raise RuntimeError("native detached payload role unavailable")
        if cancel and not cancelled:
            raise RuntimeError("supervisor cancellation was not exercised")
        if not cancel and "timeout" not in report["stderr"].lower():
            raise BoundaryFailure("actual terminal timeout unavailable", report)
        if not cancel and report["seconds"] > 6:
            raise RuntimeError("five-second deadline plus one-second stop exceeded")
    return report


def lifecycle(fixture, argv, upper, slice_path, suffix, mode):
    fixture.requests.clear()
    fixture.workload_mode = mode
    heartbeat = upper / "heartbeat"
    heartbeat.unlink(missing_ok=True)
    native_argv = list(argv)
    unit_arg = next(value for value in native_argv if value.startswith("--unit="))
    unit = unit_arg[7:].replace(".service", "-" + suffix + ".service")
    native_argv[native_argv.index(unit_arg)] = "--unit=" + unit
    result = capture(native_argv, slice_path / unit, heartbeat, mode == "cancellation")
    result["provider_requests"] = list(fixture.requests)
    heartbeat.unlink()
    return result


def validator(command, argv, owned, candidate, upper, mounts, signature, slice_path):
    frozen = owned / "frozen-candidate"
    shutil.copytree(candidate, frozen, symlinks=True)
    frozen.chmod(0o755)
    before = snapshot(frozen)
    source = snapshot(candidate)
    image = owned / "validator-image"
    lower = owned / "validator-lower"
    scratch = owned / "validator-upper"
    lower.mkdir()
    scratch.mkdir()
    with image.open("xb") as stream:
        stream.truncate(33554432)
    command(["/usr/sbin/mkfs.ext4", "-q", "-F", "-m", "0", str(image)])
    loop = command(["/usr/sbin/losetup", "--find", "--show", "--nooverlap", str(image)])
    try:
        if command(["/usr/sbin/losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(
            image
        ):
            raise RuntimeError("validator loop identity mismatch")
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
                str(scratch),
            ]
        )
        mounts.append(scratch)
        os.chown(scratch, 65531, 65531)
        scratch.chmod(0o700)
        native_index = argv.index("/opt/codex/bin/codex")
        validator_argv = list(argv[:native_index])
        unit_arg = next(value for value in validator_argv if value.startswith("--unit="))
        unit = unit_arg[7:].replace(".service", "-validator.service")
        validator_argv[validator_argv.index(unit_arg)] = "--unit=" + unit
        for old, new in ((str(candidate), str(frozen)), (str(upper), str(scratch))):
            index = validator_argv.index(old)
            validator_argv[index] = new
            if old == str(candidate):
                validator_argv[index - 1] = "--ro-bind"
        validator_argv[validator_argv.index("--reuid=65534")] = "--reuid=65531"
        validator_argv[validator_argv.index("--regid=65534")] = "--regid=65531"
        validator_argv.extend(
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
                "/input/native-full-validator.py",
            ]
        )
        result = capture(validator_argv, slice_path / unit)
        if result["exit"] != 0:
            raise RuntimeError("readonly validator execution refused: " + result["stderr"][:512])
        negative = json.loads(result["stdout"])
        if negative["uid"] != 65531 or "crewshal-native-tool-v1" not in negative["label"]:
            raise RuntimeError("independent validator payload role mismatch")
        if negative["candidate_read"] != "modified-owned":
            raise RuntimeError("validator could not read frozen candidate")
        if not negative["candidate_write"]["denied"] or not negative["candidate_new"]["denied"]:
            raise RuntimeError("validator could write frozen candidate")
        if any(not value["denied"] for value in negative["filesystem"].values()):
            raise RuntimeError("validator filesystem escape")
        if any(value is False for value in negative["denied"].values()):
            raise RuntimeError("validator credential or network escape")
        if negative["denied"]["userns"]["return"] != -1:
            raise RuntimeError("validator user namespace escape")
        if any(
            key in negative["environment"]
            for key in (
                "SYNTHETIC_PARENT_SECRET",
                "OPENAI_API_KEY",
                "SSH_AUTH_SOCK",
            )
        ):
            raise RuntimeError("validator inherited credential environment")
        if snapshot(frozen) != before or snapshot(candidate) != source:
            raise RuntimeError("validator changed frozen or worker candidate")
        result.update(
            observations=negative,
            candidate_before=before,
            frozen_candidate_sha256=hashlib.sha256(
                json.dumps(before, sort_keys=True).encode()
            ).hexdigest(),
            frozen_candidate_unchanged=True,
            separate_scratch=True,
        )
        return result
    finally:
        for mount in (scratch, lower):
            if mount in mounts:
                command(["/usr/bin/umount", str(mount)])
                mounts.remove(mount)
        if command(["/usr/sbin/losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(
            image
        ):
            raise RuntimeError("validator cleanup loop identity mismatch")
        command(["/usr/sbin/losetup", "--detach", loop])
