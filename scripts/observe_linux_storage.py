"""Trusted, synthetic eCryptfs experiment; explicitly supplied disposable Linux only.

Requires a prospectively bound private input tree, systemd aggregate slice and
anonymous keyctl session. It is not a Crewshal runtime launcher or admission gate.
Never reads ambient keyrings, formats host disks, or launches SBX.
"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import stat
import subprocess
import time
import traceback

CASES = (
    "truncate",
    "seek-write",
    "pwrite",
    "mmap",
    "preallocate",
    "copy-range",
    "reflink",
    "hole-punch",
    "hardlink",
    "deleted-open",
    "metadata",
)
ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
LIMIT = 65536


def command(argv, data=None):
    result = subprocess.run(argv, input=data, capture_output=True, timeout=10, env=ENV)
    if len(result.stdout) > LIMIT or len(result.stderr) > LIMIT:
        raise RuntimeError("trusted helper output exceeded bound")
    if result.returncode:
        raise RuntimeError(
            f"helper {Path(argv[0]).name} exit {result.returncode}: {result.stderr.decode(errors='replace')[:512]}"
        )
    return result.stdout.decode().strip()


def inventory(root):
    rows = []
    for directory, _, names in os.walk(root, followlinks=False):
        for name in names:
            path = Path(directory) / name
            item = path.lstat()
            rows.append(
                {
                    "path": str(path.relative_to(root)),
                    "device": item.st_dev,
                    "inode": item.st_ino,
                    "logical_bytes": item.st_size,
                    "allocated_bytes": item.st_blocks * 512,
                    "links": item.st_nlink,
                    "mode": item.st_mode,
                    "uid": item.st_uid,
                    "gid": item.st_gid,
                }
            )
    return rows


def fd_sample(pid):
    rows = []
    try:
        paths = list(Path(f"/proc/{pid}/fd").iterdir())
    except FileNotFoundError:
        return rows
    for path in paths:
        try:
            target = os.readlink(path)
            if not target.startswith("/work/"):
                continue
            item = path.stat()
            if not stat.S_ISREG(item.st_mode):
                continue
            row = {
                "fd": path.name,
                "path": target,
                "device": item.st_dev,
                "inode": item.st_ino,
                "logical_bytes": item.st_size,
                "allocated_bytes": item.st_blocks * 512,
                "links": item.st_nlink,
            }
            with open(path, "rb", buffering=0) as stream:
                row["last_byte_hex"] = os.pread(stream.fileno(), 1, max(0, item.st_size - 1)).hex()
                row["first_byte_hex"] = os.pread(stream.fileno(), 1, 0).hex()
                row["middle_byte_hex"] = os.pread(stream.fileno(), 1, item.st_size // 2).hex()
            rows.append(row)
        except (FileNotFoundError, ProcessLookupError):
            continue
    return rows


def controls(slice_name):
    group = command(["systemctl", "show", slice_name, "-p", "ControlGroup", "--value"])
    root = Path("/sys/fs/cgroup" + group)
    return {
        name: (root / name).read_text().strip()
        for name in ("memory.max", "memory.swap.max", "cpu.max", "pids.max", "cgroup.events")
    }


def verify_inputs(directory):
    manifest = json.loads((directory / "bindings.json").read_text())
    for path, digest in manifest["sha256"].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise RuntimeError("prospective input identity mismatch")
    if manifest["architecture"] != "aarch64" or os.uname().machine != "aarch64":
        raise RuntimeError("profile is bound only to observed aarch64 ABI")
    return manifest


def seccomp_filter():
    library = ctypes.CDLL("/lib/aarch64-linux-gnu/libseccomp.so.2")
    library.seccomp_init.argtypes = [ctypes.c_uint32]
    library.seccomp_init.restype = ctypes.c_void_p
    library.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    library.seccomp_syscall_resolve_name.restype = ctypes.c_int
    library.seccomp_rule_add.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
    ]
    library.seccomp_rule_add.restype = ctypes.c_int
    library.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
    library.seccomp_release.argtypes = [ctypes.c_void_p]
    context = library.seccomp_init(0x7FFF0000)
    if not context:
        raise RuntimeError("vendor seccomp context unavailable")
    fd = os.memfd_create("crewshal-synthetic-filter", os.MFD_CLOEXEC)
    try:
        for name in (
            "keyctl",
            "add_key",
            "request_key",
            "mount",
            "umount2",
            "fsopen",
            "fsconfig",
            "fsmount",
            "move_mount",
            "open_tree",
            "mount_setattr",
            "setns",
            "unshare",
            "clone3",
            "ptrace",
            "process_vm_readv",
            "process_vm_writev",
            "bpf",
            "perf_event_open",
        ):
            number = library.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or library.seccomp_rule_add(context, 0x50001, number, 0) != 0:
                raise RuntimeError("vendor seccomp syscall binding unavailable: " + name)

        class Comparison(ctypes.Structure):
            _fields_ = [
                ("arg", ctypes.c_uint),
                ("op", ctypes.c_uint),
                ("a", ctypes.c_uint64),
                ("b", ctypes.c_uint64),
            ]

        library.seccomp_rule_add_array.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(Comparison),
        ]
        clone = library.seccomp_syscall_resolve_name(b"clone")
        for flag in (0x20000, 0x2000000, 0x4000000, 0x8000000, 0x10000000, 0x20000000, 0x40000000):
            comparison = Comparison(0, 7, flag, flag)
            if (
                library.seccomp_rule_add_array(context, 0x50001, clone, 1, ctypes.byref(comparison))
                != 0
            ):
                raise RuntimeError("vendor namespace syscall filter unavailable")
        if library.seccomp_export_bpf(context, fd) != 0:
            raise RuntimeError("vendor BPF export unavailable")
        os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except BaseException:
        os.close(fd)
        raise
    finally:
        library.seccomp_release(context)


def descendants(pid):
    found, pending = [], [pid]
    while pending and len(found) < 128:
        parent = pending.pop()
        try:
            children = Path(f"/proc/{parent}/task/{parent}/children").read_text().split()
        except FileNotFoundError:
            continue
        for child in children:
            number = int(child)
            if number not in found:
                found.append(number)
                pending.append(number)
    return found


def payload(root, base, upper, lower, loop, key, slice_name, tag, argv, deadline):
    fd = seccomp_filter()
    filter_digest = hashlib.sha256(os.pread(fd, 65536, 0)).hexdigest()
    args = [
        "/usr/bin/bwrap",
        "--ro-bind",
        str(root),
        "/",
        "--bind",
        str(upper),
        "/work",
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
        "LC_ALL",
        "C",
        "--cap-drop",
        "ALL",
        "--cap-add",
        "CAP_SETUID",
        "--cap-add",
        "CAP_SETGID",
        "--cap-add",
        "CAP_SETPCAP",
        "--seccomp",
        str(fd),
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
        "-S",
        "-B",
    ] + argv
    started = time.monotonic()
    process = subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        pass_fds=(fd,),
        start_new_session=True,
        env=ENV,
    )
    os.close(fd)
    selector = selectors.DefaultSelector()
    for stream in (process.stdout, process.stderr):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    buffers = {process.stdout: bytearray(), process.stderr: bytearray()}
    samples, last_sample, owned_pids, placement = [], None, {process.pid}, {}
    failure = None
    try:
        while selector.get_map():
            if time.monotonic() >= min(started + 10, deadline):
                failure = "deadline"
                break
            for pid in descendants(process.pid):
                owned_pids.add(pid)
                try:
                    placement[str(pid)] = Path(f"/proc/{pid}/cgroup").read_text().strip()
                    sample = fd_sample(pid)
                except (FileNotFoundError, ProcessLookupError):
                    continue
                signature = json.dumps([pid, sample], sort_keys=True)
                if sample and signature != last_sample:
                    samples.append(
                        {
                            "elapsed_seconds": round(time.monotonic() - started, 3),
                            "pid": pid,
                            "namespace_pids": [
                                int(value)
                                for line in Path(f"/proc/{pid}/status").read_text().splitlines()
                                if line.startswith("NSpid:")
                                for value in line.split()[1:]
                            ],
                            "files": sample,
                        }
                    )
                    last_sample = signature
                    if len(samples) >= 256:
                        failure = "observer sample bound"
                        break
            for item, _ in selector.select(0.025):
                chunk = os.read(item.fileobj.fileno(), 4096)
                if not chunk:
                    selector.unregister(item.fileobj)
                else:
                    buffers[item.fileobj].extend(chunk)
                    if len(buffers[item.fileobj]) > LIMIT:
                        failure = "stream bound"
                        break
            if failure:
                break
    finally:
        if failure:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=2)
        selector.close()
        process.stdout.close()
        process.stderr.close()
    # bubblewrap's PID namespace is torn down when its reaper exits.
    stop_deadline = time.monotonic() + 1
    while (
        any(Path(f"/proc/{pid}").exists() for pid in owned_pids)
        and time.monotonic() < stop_deadline
    ):
        time.sleep(0.01)
    remaining = [pid for pid in owned_pids if Path(f"/proc/{pid}").exists()]
    if remaining:
        raise RuntimeError("owned payload process remained live")
    output = bytes(buffers[process.stdout][:LIMIT]).decode(errors="replace")
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        result = None
    return {
        "label": tag,
        "wrapper_pid": process.pid,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "exit": process.returncode,
        "failure": failure,
        "stdout": output,
        "stderr": bytes(buffers[process.stderr][:LIMIT]).decode(errors="replace"),
        "result": result,
        "fd_samples": samples,
        "post_stop_pids": remaining,
        "placement": placement,
        "filter_sha256": filter_digest,
        "upper": inventory(upper),
        "lower": inventory(lower),
        "lower_free_bytes": os.statvfs(lower).f_bavail * os.statvfs(lower).f_frsize,
    }


def run_fixture(inputs, slice_name, number, whole_deadline):
    start = time.monotonic()
    base = Path(f"/run/crewshal-storage-fixture-{os.getpid()}-{number}")
    base.mkdir(mode=0o700)
    lower, upper, image = base / "lower", base / "upper", base / "image"
    lower.mkdir()
    upper.mkdir()
    keys, loop, mounts = [], None, []
    record = {"fixture": number, "cases": [], "cleanup": {}, "errors": [], "key_handles": []}
    try:
        # @s is exclusively the anonymous session supplied by keyctl session -.
        ring = command(["keyctl", "id", "@s"])
        if command(["keyctl", "list", "@s"]) != "keyring is empty":
            raise RuntimeError("new session ring is not empty")
        record["session_ring"] = ring
        master_name = "crewshal-master-" + os.urandom(8).hex()
        master = command(["keyctl", "padd", "user", master_name, "@s"], os.urandom(32))
        keys.append(master)
        signature = os.urandom(8).hex()
        token = command(
            [
                "keyctl",
                "add",
                "encrypted",
                signature,
                "new ecryptfs user:" + master_name + " 64",
                "@s",
            ]
        )
        keys.append(token)
        record["key_handles"] = list(keys)
        record["new_key_descriptions"] = [command(["keyctl", "describe", key]) for key in keys]
        with image.open("xb") as stream:
            stream.truncate(33554432)
        command(["mkfs.ext4", "-q", "-F", "-m", "0", str(image)])
        loop = command(["losetup", "--find", "--show", "--nooverlap", str(image)])
        if command(["losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(image):
            raise RuntimeError("loop backing identity differs")
        record["loop"] = loop
        command(["mount", "-i", "-t", "ext4", "-o", "nodev,nosuid,noexec", loop, str(lower)])
        mounts.append(lower)
        options = (
            "nodev,nosuid,noexec,ecryptfs_sig="
            + signature
            + ",ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_mount_auth_tok_only"
        )
        command(["mount", "-i", "-t", "ecryptfs", "-o", options, str(lower), str(upper)])
        mounts.append(upper)
        os.chown(upper, 65534, 65534)
        os.chmod(upper, 0o700)
        record["mounts"] = [
            line
            for line in Path("/proc/self/mountinfo").read_text().splitlines()
            if str(base) in line
        ]
        record["controls"] = controls(slice_name)
        expected = {
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "128",
        }
        if any(record["controls"][key] != value for key, value in expected.items()):
            raise RuntimeError("effective aggregate controller mismatch")
        if time.monotonic() - start > 120:
            raise RuntimeError("fixture startup exceeded 120 seconds")
        root = inputs / "root"
        bypass = payload(
            root,
            base,
            upper,
            lower,
            loop,
            token,
            slice_name,
            f"{os.getpid()}-{number}-boundary",
            [
                "/inputs/boundary.py",
                "--lower",
                str(lower),
                "--observer",
                str(os.getpid()),
                "--loop",
                loop,
                "--key",
                token,
            ],
            whole_deadline - 30,
        )
        record["boundary"] = bypass
        if not bypass["result"] or bypass["exit"] != 0:
            raise RuntimeError("boundary payload did not establish its limited denials")
        if bypass["result"]["file_size_limit"] != [-1, -1]:
            raise RuntimeError("unexpected file-size limit")
        shutil.rmtree(upper / "metadata-extra")
        for size in (8388608, 41943040):
            for case in CASES:
                if time.monotonic() >= whole_deadline - 40:
                    raise RuntimeError("new work refused at cleanup reserve")
                name = f"{case}-{size}"
                item = payload(
                    root,
                    base,
                    upper,
                    lower,
                    loop,
                    token,
                    slice_name,
                    f"{os.getpid()}-{number}-{name}",
                    [
                        "/inputs/probe.py",
                        "--directory",
                        "/work/" + name,
                        "--case",
                        case,
                        "--bytes",
                        str(size),
                        "--hold-seconds",
                        "2",
                    ],
                    whole_deadline - 30,
                )
                item.update({"case": case, "requested_bytes": size})
                record["cases"].append(item)
                directory = upper / name
                if directory.is_dir():
                    shutil.rmtree(directory)
                os.sync()
                item["after_case_cleanup"] = {"upper": inventory(upper), "lower": inventory(lower)}
                if item["failure"] or not item["result"]:
                    raise RuntimeError("case unavailable; fixture stopped")
        record["image"] = inventory(base)[0:1]
    except Exception as error:
        record["errors"].append({"type": type(error).__name__, "message": str(error)[:1024]})
    finally:
        cleanup = record["cleanup"]
        cleanup["unmounts"] = []
        for mount in reversed(mounts):
            try:
                command(["umount", str(mount)])
                cleanup["unmounts"].append({"view": mount.name, "unmounted": True})
            except Exception as error:
                cleanup["unmounts"].append(
                    {"view": mount.name, "unmounted": False, "error": str(error)[:512]}
                )
        unmounted = all(row["unmounted"] for row in cleanup["unmounts"])
        if loop and unmounted:
            try:
                if command(["losetup", "--noheadings", "--output", "BACK-FILE", loop]) != str(
                    image
                ):
                    raise RuntimeError("cleanup loop identity changed")
                command(["losetup", "--detach", loop])
                check = subprocess.run(["losetup", loop], capture_output=True, timeout=2, env=ENV)
                cleanup["loop_detached"] = check.returncode != 0
            except Exception as error:
                cleanup["loop_detached"] = False
                cleanup["loop_error"] = str(error)[:512]
        cleanup["keys"] = []
        for key in reversed(keys):
            try:
                command(["keyctl", "revoke", key])
                command(["keyctl", "unlink", key, "@s"])
                cleanup["keys"].append({"handle": key, "revoked_unlinked": True})
            except Exception as error:
                cleanup["keys"].append(
                    {"handle": key, "revoked_unlinked": False, "error": str(error)[:512]}
                )
        cleanup["new_session_after"] = command(["keyctl", "list", "@s"])
        if unmounted and (not loop or cleanup.get("loop_detached")):
            shutil.rmtree(base)
            cleanup["owned_files_absent"] = not base.exists()
        else:
            cleanup["owned_files_absent"] = False
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--slice", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--fixture", type=int, choices=(1, 2))
    parser.add_argument("--deadline", type=float)
    args = parser.parse_args()

    def interrupted(signum, frame):
        raise RuntimeError("aggregate cleanup reserve signal")

    signal.signal(signal.SIGTERM, interrupted)
    if os.geteuid() != 0 or not args.slice.startswith("crewshal-storage-") or args.report.exists():
        parser.error("requires trusted root, exclusively named aggregate and new report")
    report = {
        "schema_version": 1,
        "execution_allowed": False,
        "native_start_allowed": False,
        "operational_manifest_frozen": False,
        "qualification_status": "diagnostic only; denied",
        "fixtures": [],
        "errors": [],
    }
    try:
        report["bindings"] = verify_inputs(args.inputs)
        own_namespace = os.readlink("/proc/self/ns/mnt")
        host_namespace = os.readlink("/proc/1/ns/mnt")
        if own_namespace == host_namespace:
            raise RuntimeError("observer mount namespace is not private")
        command(["mount", "--make-rprivate", "/"])
        report["observer_mount_namespace"] = own_namespace
        report["host_mount_namespace"] = host_namespace
        if args.fixture:
            if (
                args.deadline is None
                or not time.monotonic() < args.deadline <= time.monotonic() + 600
            ):
                raise RuntimeError("invalid inherited whole-experiment deadline")
            record = run_fixture(args.inputs, args.slice, args.fixture, args.deadline)
            with args.report.open("x") as stream:
                json.dump(record, stream, sort_keys=True, indent=2)
            os.chmod(args.report, 0o644)
            return 0 if not record["errors"] and record["cleanup"].get("owned_files_absent") else 2
        deadline = time.monotonic() + 600
        for number in (1, 2):
            child_report = args.report.with_name(args.report.name + f".fixture-{number}")
            if child_report.exists():
                raise RuntimeError("child report already exists")
            child = subprocess.run(
                [
                    "keyctl",
                    "session",
                    "-",
                    "/usr/bin/python3",
                    "-I",
                    "-S",
                    "-B",
                    str(Path(__file__).resolve()),
                    "--inputs",
                    str(args.inputs),
                    "--slice",
                    args.slice,
                    "--report",
                    str(child_report),
                    "--fixture",
                    str(number),
                    "--deadline",
                    str(deadline),
                ],
                capture_output=True,
                timeout=max(1, deadline - time.monotonic()),
                env=ENV,
            )
            if len(child.stdout) > LIMIT or len(child.stderr) > LIMIT:
                raise RuntimeError("child observer output exceeded bound")
            fixture = json.loads(child_report.read_text())
            fixture["observer_exit"] = child.returncode
            fixture["observer_stderr"] = child.stderr.decode(errors="replace")
            report["fixtures"].append(fixture)
            if fixture["errors"] or not fixture["cleanup"].get("owned_files_absent"):
                break
    except Exception as error:
        report["errors"].append({"type": type(error).__name__, "message": str(error)[:1024]})
        traceback.print_exc()
    with args.report.open("x") as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
    os.chmod(args.report, 0o644)  # Synthetic, public evidence; never secret key material.
    print(
        json.dumps(
            {
                "fixtures": len(report["fixtures"]),
                "errors": report["errors"],
                "report_sha256": hashlib.sha256(args.report.read_bytes()).hexdigest(),
            }
        )
    )
    return (
        0
        if len(report["fixtures"]) == 2 and not any(row["errors"] for row in report["fixtures"])
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
