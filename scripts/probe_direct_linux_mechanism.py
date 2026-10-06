"""Bounded synthetic tmpfs/cgroup experiment, never a product runtime launcher.

Prepare freezes installed bytes before the separately invoked two-fixture run.
No native CLI, credential, provider, existing mount or repository is admitted.
"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import shutil
import stat
import subprocess
import time

ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
TOOLS = ("bwrap", "setpriv", "systemd-run", "systemctl", "unshare", "mount", "umount")
MAX_INPUT = 268435456
PAYLOAD = r"""
import errno,json,os,resource,signal,sys,time
from pathlib import Path
mode=sys.argv[1]
if mode=='hold':
 f=open('/candidate/owned/deleted','w+b'); f.write(b'deleted-open'); f.flush()
 os.unlink('/candidate/owned/deleted')
 item=os.fstat(f.fileno())
 print(json.dumps({'pid':os.getpid(),'fd':f.fileno(),'inode':item.st_ino,
                   'device':item.st_dev,'logical':item.st_size}),flush=True)
 time.sleep(30)
elif mode=='deadline':
 child=os.fork()
 if child==0:
  os.setsid()
  while True:
   with open('/scratch/heartbeat','ab') as f: f.write(b'.')
   time.sleep(.05)
 while True: time.sleep(30)
elif mode=='allocation':
 signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
 result={}
 for folder in ['/candidate/owned','/scratch']:
  created=0
  try:
   for n in range(256):
    Path(folder+'/'+str(n)).write_bytes(b'x'*65536); created+=1
   raise AssertionError('physical bound bypassed')
  except OSError as e: assert e.errno==errno.ENOSPC
  result[folder]=created
 print(json.dumps(result),flush=True)
 time.sleep(30)
else:
 signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
 result={'input':Path('/input/canary').read_text(),'uid':os.geteuid(),
         'fsize':resource.getrlimit(resource.RLIMIT_FSIZE),'denials':{}}
 for name,path,action in [('readonly','/input/canary','write'),
                          ('outside','/outside/canary','read'),
                          ('coordinator','/coordinator/canary','read')]:
  try:
   if action=='write': Path(path).write_text('bad')
   else: Path(path).read_bytes()
   result['denials'][name]=False
  except OSError: result['denials'][name]=True
 for folder in ['/candidate/owned','/scratch']:
  p=Path(folder)/'small'; p.write_bytes(b'pilot'); assert p.read_bytes()==b'pilot'
  oversized=Path(folder)/'sparse'
  try:
   with oversized.open('wb') as f: f.truncate(65537)
   raise AssertionError('hard length bound bypassed')
  except OSError as e: assert e.errno==errno.EFBIG
  oversized.unlink(); p.unlink()
  files=[]
  try:
   for n in range(300):
    p=Path(folder)/str(n); p.write_bytes(b''); files.append(p)
   raise AssertionError('inode bound bypassed')
  except OSError as e: assert e.errno==errno.ENOSPC
  result[folder]={'created_before_inode_exhaustion':len(files)}
  for p in files: p.unlink()
 print(json.dumps(result),flush=True)
"""


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def command(argv, timeout=10):
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    try:
        out, err = proc.communicate(timeout=timeout)
        if len(out) > 65536 or len(err) > 65536 or proc.returncode:
            raise RuntimeError(f"helper refused: {Path(argv[0]).name}: {err[:512]!r}")
        return out.decode().strip()
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def dependencies(path):
    result = set()
    for line in command(["/usr/bin/ldd", str(path)]).splitlines():
        for word in line.split():
            if word.startswith("/") and Path(word).is_file():
                result.add(Path(word))
    return result


def prepare(base):
    base.mkdir(mode=0o700)
    root = base / "root"
    root.mkdir()
    bindings = {}
    total = 0

    def bind(path):
        bindings[str(path)] = digest(path)

    def copy(source, destination):
        nonlocal total
        if destination.exists():
            if digest(source) != digest(destination):
                raise RuntimeError("copy collision")
            return
        total += source.stat().st_size
        if total > MAX_INPUT:
            raise RuntimeError("copied input reserve exceeded")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        destination.chmod(0o755 if os.access(source, os.X_OK) else 0o644)
        bind(source)
        bind(destination)

    stdlib = Path("/usr/lib/python3.12")
    binaries = [Path("/usr/bin/python3.12"), Path("/usr/bin/setpriv")]
    for source in sorted(stdlib.rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts:
            copy(source, root / source.relative_to("/"))
    for source, target in zip(binaries, ("bin/python3", "bin/setpriv"), strict=True):
        copy(source, root / target)
    for binary in [*binaries, *stdlib.rglob("*.so")]:
        for library in dependencies(binary):
            copy(library, root / library.relative_to("/"))
    for name in TOOLS:
        path = Path(shutil.which(name, path=ENV["PATH"]) or "/missing-helper")
        bind(path)
        for library in dependencies(path):
            bind(library)
    for path in ("/usr/bin/ldd", "/bin/sh", "/lib/aarch64-linux-gnu/libseccomp.so.2"):
        bind(path)
    for name in ("vmlinuz", "config"):
        bind("/boot/" + name + "-" + os.uname().release)
    bind(Path(__file__).resolve())
    for directory in ("input", "candidate/owned", "scratch", "proc", "dev", "sys", "etc"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "input/payload.py").write_text(PAYLOAD)
    (root / "input/canary").write_text("read-only synthetic input")
    bind(root / "input/payload.py")
    bind(root / "input/canary")
    ledger = inventory(base)
    if ledger["logical"] > MAX_INPUT or ledger["allocated"] > MAX_INPUT:
        raise RuntimeError("prepared tree exceeds reservation")
    manifest = {
        "architecture": os.uname().machine,
        "kernel": os.uname().release,
        "bindings": bindings,
        "prepared_inventory": ledger,
        "limits": {
            "worker_memory": 134217728,
            "worker_pids": 32,
            "fsize": 65536,
            "candidate_inodes": 128,
            "scratch_inodes": 256,
        },
        "execution_allowed": False,
        "native_start_allowed": False,
    }
    with (base / "manifest.json").open("x") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(
        json.dumps(
            {
                "manifest_sha256": digest(base / "manifest.json"),
                "bound_files": len(bindings),
                "inventory": ledger,
            }
        )
    )


def inventory(base):
    seen = set()
    result = {"logical": 0, "allocated": 0, "inodes": 0}
    for path in [base, *base.rglob("*")]:
        item = path.lstat()
        key = (item.st_dev, item.st_ino)
        if key not in seen:
            seen.add(key)
            result["logical"] += item.st_size
            result["allocated"] += item.st_blocks * 512
            result["inodes"] += 1
    return result


def filter_fd():
    lib = ctypes.CDLL("/lib/aarch64-linux-gnu/libseccomp.so.2")
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    lib.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
    context = lib.seccomp_init(0x7FFF0000)
    if not context:
        raise RuntimeError("seccomp initialization refused")
    fd = os.memfd_create("synthetic-filter", os.MFD_CLOEXEC)
    try:
        for name in (
            "mount",
            "umount2",
            "unshare",
            "setns",
            "keyctl",
            "add_key",
            "request_key",
            "ptrace",
            "process_vm_readv",
            "process_vm_writev",
            "fsopen",
            "fsmount",
            "fsconfig",
            "open_tree",
            "move_mount",
            "mount_setattr",
            "bpf",
            "perf_event_open",
            "setxattr",
            "lsetxattr",
            "fsetxattr",
            "mknod",
            "mknodat",
        ):
            number = lib.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or lib.seccomp_rule_add(context, 0x50001, number, 0):
                raise RuntimeError("syscall filter refused: " + name)
        # ENOSYS lets supported libc thread creation fall back to filtered clone.
        number = lib.seccomp_syscall_resolve_name(b"clone3")
        if lib.seccomp_rule_add(context, 0x50026, number, 0):
            raise RuntimeError("clone3 filter refused")

        class Comparison(ctypes.Structure):
            _fields_ = [
                ("arg", ctypes.c_uint),
                ("op", ctypes.c_uint),
                ("a", ctypes.c_uint64),
                ("b", ctypes.c_uint64),
            ]

        lib.seccomp_rule_add_array.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(Comparison),
        ]
        number = lib.seccomp_syscall_resolve_name(b"clone")
        for flag in (0x20000, 0x2000000, 0x4000000, 0x8000000, 0x10000000, 0x20000000, 0x40000000):
            comparison = Comparison(0, 7, flag, flag)
            if lib.seccomp_rule_add_array(context, 0x50001, number, 1, ctypes.byref(comparison)):
                raise RuntimeError("namespace clone filter refused")
        if lib.seccomp_export_bpf(context, fd):
            raise RuntimeError("BPF export refused")
        os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except BaseException:
        os.close(fd)
        raise
    finally:
        lib.seccomp_release(context)


def controls(group):
    return {
        n: (group / n).read_text().strip()
        for n in ("memory.max", "memory.swap.max", "cpu.max", "pids.max", "cgroup.events")
    }


def run(base, expected):
    if digest(base / "manifest.json") != expected:
        raise RuntimeError("manifest identity changed")
    manifest = json.loads((base / "manifest.json").read_text())
    if manifest["architecture"] != "aarch64" or manifest["kernel"] != os.uname().release:
        raise RuntimeError("substrate changed")
    for path, value in manifest["bindings"].items():
        if digest(path) != value:
            raise RuntimeError("bound input changed: " + path)
    relative = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
    group = Path("/sys/fs/cgroup" + relative)
    aggregate = controls(group)
    required = {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "128",
    }
    if any(aggregate[k] != v for k, v in required.items()):
        raise RuntimeError("aggregate admission refused")
    observer = group / "observer"
    worker = group / "worker"
    observer.mkdir()
    (observer / "cgroup.procs").write_text(str(os.getpid()))
    (group / "cgroup.subtree_control").write_text("+memory +cpu +pids")
    worker.mkdir()
    for name, value in {
        "memory.max": "134217728",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "32",
    }.items():
        (worker / name).write_text(value)
    command(["/usr/bin/mount", "--make-rprivate", "/"])
    records = []
    stop = time.monotonic() + 570
    try:
        for index in (1, 2):
            if time.monotonic() >= stop - 120:
                raise TimeoutError("fixture admission deadline")
            fixture = base / ("fixture-" + str(index))
            fixture.mkdir()
            candidate, scratch = fixture / "candidate", fixture / "scratch"
            candidate.mkdir()
            scratch.mkdir()
            mounted = []
            record = {"fixture": index, "aggregate": aggregate, "worker": controls(worker)}
            started = time.monotonic()
            try:
                for path, size, inodes in ((candidate, 4194304, 128), (scratch, 8388608, 256)):
                    command(
                        [
                            "/usr/bin/mount",
                            "-t",
                            "tmpfs",
                            "-o",
                            f"size={size},nr_inodes={inodes},nosuid,nodev,noexec,mode=0700,uid=65534,gid=65534",
                            "tmpfs",
                            str(path),
                        ]
                    )
                    mounted.append(path)
                for mode in ("bounds", "hold", "deadline", "allocation"):
                    fd = filter_fd()
                    argv = [
                        "/usr/bin/bwrap",
                        "--ro-bind",
                        str(base / "root"),
                        "/",
                        "--bind",
                        str(candidate),
                        "/candidate/owned",
                        "--bind",
                        str(scratch),
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
                        "--chdir",
                        "/candidate/owned",
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
                        "-B",
                        "/input/payload.py",
                        mode,
                    ]

                    def placement():
                        (worker / "cgroup.procs").write_text(str(os.getpid()))
                        resource.setrlimit(resource.RLIMIT_FSIZE, (65536, 65536))

                    proc = subprocess.Popen(
                        argv,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=ENV,
                        pass_fds=(fd,),
                        preexec_fn=placement,
                    )
                    os.close(fd)
                    sel = selectors.DefaultSelector()
                    output = {"stdout": bytearray(), "stderr": bytearray()}
                    for name, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
                        sel.register(stream, selectors.EVENT_READ, name)
                    deadline = time.monotonic() + 5
                    sampled = []
                    killed = False
                    try:
                        while sel.get_map():
                            if mode == "hold" and output["stdout"] and not sampled:
                                for pid in (worker / "cgroup.procs").read_text().split():
                                    for entry in Path("/proc/" + pid + "/fd").iterdir():
                                        try:
                                            if not os.readlink(entry).endswith(
                                                "/deleted (deleted)"
                                            ):
                                                continue
                                            item = entry.stat()
                                            if stat.S_ISREG(item.st_mode) and item.st_nlink == 0:
                                                sampled.append(
                                                    {
                                                        "inode": item.st_ino,
                                                        "device": item.st_dev,
                                                        "logical": item.st_size,
                                                        "allocated": item.st_blocks * 512,
                                                        "links": item.st_nlink,
                                                        "cgroup": Path("/proc/" + pid + "/cgroup")
                                                        .read_text()
                                                        .strip(),
                                                    }
                                                )
                                        except FileNotFoundError:
                                            pass
                            if (
                                time.monotonic() >= deadline
                                or (mode == "hold" and sampled)
                                or (mode == "allocation" and b"\n" in output["stdout"])
                            ):
                                (worker / "cgroup.kill").write_text("1")
                                killed = True
                            for key, _ in sel.select(0.02):
                                data = os.read(key.fileobj.fileno(), 4096)
                                if not data:
                                    sel.unregister(key.fileobj)
                                else:
                                    output[key.data].extend(data)
                                    if len(output[key.data]) > 65536:
                                        raise RuntimeError("worker output exceeds bound")
                            if time.monotonic() > deadline + 1:
                                raise TimeoutError("worker kill grace expired")
                        code = proc.wait(timeout=1)
                        record[mode] = {
                            "exit": code,
                            "killed": killed,
                            "deleted_open": sampled,
                            "stdout": output["stdout"].decode(),
                            "stderr": output["stderr"].decode(),
                            "candidate": inventory(candidate),
                            "scratch": inventory(scratch),
                            "terminal": (worker / "cgroup.events").read_text().strip(),
                        }
                        if mode == "allocation":
                            for folder, ceiling in ((candidate, 4194304), (scratch, 8388608)):
                                measured = inventory(folder)
                                if (
                                    measured["allocated"] > ceiling
                                    or measured["allocated"] < ceiling - 65536
                                ):
                                    raise RuntimeError("independent physical oracle refused")
                                for path in folder.iterdir():
                                    path.unlink()
                        if mode == "bounds":
                            parsed = json.loads(record[mode]["stdout"])
                            if (
                                code
                                or not all(parsed["denials"].values())
                                or parsed["fsize"] != [65536, 65536]
                            ):
                                raise RuntimeError("bounds probe refused")
                        elif not killed or (mode == "hold" and not sampled):
                            raise RuntimeError("lifecycle probe refused")
                        if mode == "hold":
                            parsed = json.loads(record[mode]["stdout"])
                            if not any(
                                all(row[k] == parsed[k] for k in ("inode", "device", "logical"))
                                and row["cgroup"].endswith(relative + "/worker")
                                for row in sampled
                            ):
                                raise RuntimeError("deleted-open independent identity refused")
                        if mode == "deadline":
                            heartbeat = scratch / "heartbeat"
                            previous = heartbeat.read_bytes()
                            time.sleep(0.1)
                            if heartbeat.read_bytes() != previous:
                                raise RuntimeError("detached heartbeat survived")
                            record["heartbeat_stopped"] = True
                        if "populated 0" not in record[mode]["terminal"]:
                            raise RuntimeError("worker remained populated")
                    finally:
                        (worker / "cgroup.kill").write_text("1")
                        proc.wait(timeout=1)
                        sel.close()
            finally:
                (worker / "cgroup.kill").write_text("1")
                for path in reversed(mounted):
                    command(["/usr/bin/umount", str(path)])
                candidate.rmdir()
                scratch.rmdir()
                fixture.rmdir()
                record["cleanup"] = {
                    "owned_mounts_removed": True,
                    "worker": (worker / "cgroup.events").read_text().strip(),
                }
                record["seconds"] = time.monotonic() - started
                records.append(record)
    finally:
        with (base / "observed.json").open("x") as f:
            json.dump(
                {
                    "manifest_sha256": expected,
                    "fixtures": records,
                    "execution_allowed": False,
                    "native_start_allowed": False,
                    "scope": "mechanism subset only; not native/broker qualification",
                },
                f,
                indent=2,
            )
    print(json.dumps({"fixtures": len(records), "observed_sha256": digest(base / "observed.json")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("base", type=Path)
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        parser.error("requires supplied test-only aarch64 Linux root role")
    if args.mode == "prepare":
        prepare(args.base)
    else:
        run(args.base, args.manifest_sha256)


if __name__ == "__main__":
    main()
