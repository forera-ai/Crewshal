"""Fixed synthetic hostile workload; actual native dispatch and parent oracles required."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def deny(action):
    try:
        action()
    except OSError as error:
        return {"denied": True, "errno": error.errno}
    return {"denied": False}


def observe():
    spec = importlib.util.spec_from_file_location("negative", "/input/native-negative.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.observe()
    result["filesystem"] = {}
    result["global_instruction_view"] = {}
    for name in ("AGENTS.md", "AGENTS.override.md"):
        path = Path("/scratch") / name
        result["global_instruction_view"][name] = {
            "contents": path.read_text(),
            "write": deny(lambda: path.write_text("Synthetic global injection: changed")),
            "unlink": deny(path.unlink),
        }
    result["input"] = Path("/input/canary").read_bytes().decode()
    for name, path in {
        "outside": "/outside/canary",
        "dirty": "/original/dirty.py",
        "git": "/original/.git/config",
        "database": "/coordinator/state.db",
        "artifact": "/coordinator/artifact",
        "readonly": "/input/canary",
        "absolute_link": "/candidate/owned/absolute-link",
        "relative_link": "/candidate/owned/relative-link",
    }.items():
        p = Path(path)
        if name != "readonly":
            result["filesystem"][name + "_read"] = deny(p.read_bytes)
        result["filesystem"][name + "_write"] = deny(lambda: p.write_bytes(b"escape"))
        if name in ("absolute_link", "relative_link"):
            continue
        result["filesystem"][name + "_chmod"] = deny(lambda: p.chmod(0o777))
        result["filesystem"][name + "_unlink"] = deny(p.unlink)
        result["filesystem"][name + "_rename"] = deny(lambda: p.rename("/scratch/escape"))
        result["filesystem"][name + "_link"] = deny(lambda: os.link(p, "/scratch/escape-link"))
    for path in (
        "/candidate/owned/absolute-parent/new",
        "/candidate/owned/relative-parent/new",
        "/candidate/owned/../new",
        "/outside/new",
        "/original/new",
        "/coordinator/new",
        "/input/new",
    ):
        result["filesystem"]["new_" + path] = deny(lambda: Path(path).write_bytes(b"escape"))
    return result


def workload():
    started = time.monotonic()
    stages = []

    def checkpoint(stage):
        stages.append({"stage": stage, "seconds": round(time.monotonic() - started, 6)})
        temporary = Path("/scratch/payload-progress.tmp")
        temporary.write_text(json.dumps(stages))
        temporary.replace("/scratch/payload-progress.json")

    result_hooks = {"positive": {}, "negative": {}, "runtime_environment": {}}
    for role, path in (
        ("repository", "/input/checkout/.git/hooks"),
        ("global", "/input/global-git-hooks"),
    ):
        marker = Path("/scratch") / (role + "-hook-sentinel")
        command = ["/bin/git", "-c", "core.hooksPath=" + path, "hook", "run", "pre-commit"]
        positive = subprocess.run(command, capture_output=True, timeout=1)
        assert positive.returncode == 0, positive.stderr
        assert marker.read_bytes() == b"hook"
        result_hooks["positive"][role] = {
            "exit": positive.returncode,
            "sentinel": marker.read_text(),
        }
        marker.unlink()
    runtime_marker = Path("/scratch/runtime-hook-sentinel")
    positive = subprocess.run(["/bin/sh", "/input/runtime-hook.sh"], capture_output=True, timeout=1)
    assert positive.returncode == 0 and runtime_marker.read_bytes() == b"hook"
    result_hooks["positive"]["runtime"] = {
        "exit": positive.returncode,
        "sentinel": runtime_marker.read_text(),
    }
    runtime_marker.unlink()
    for key in ("BASH_ENV", "ENV", "PYTHONSTARTUP", "GIT_CONFIG", "GIT_CONFIG_SYSTEM"):
        result_hooks["runtime_environment"][key] = key in os.environ
        assert key not in os.environ
    effective = subprocess.run(
        ["/bin/git", "config", "--show-origin", "--get", "core.hooksPath"],
        capture_output=True,
        timeout=1,
    )
    assert (
        effective.returncode == 0
        and effective.stdout.decode().strip() == "command line:\t/dev/null"
    ), effective.stdout
    ignored = subprocess.run(
        ["/bin/git", "hook", "run", "--ignore-missing", "pre-commit"],
        capture_output=True,
        timeout=1,
    )
    assert ignored.returncode == 0, ignored.stderr
    assert all(
        not (Path("/scratch") / (role + "-hook-sentinel")).exists()
        for role in ("repository", "global", "runtime")
    )
    result_hooks["negative"] = {
        "effective_hooks_path": effective.stdout.decode().strip(),
        "hook_exit": ignored.returncode,
        "sentinels_absent": True,
    }
    checkpoint("hooks-complete")
    checkpoint("observe-start")
    result = observe()
    result["hooks"] = result_hooks
    checkpoint("observe-complete")
    for directory in ("/candidate/owned", "/scratch"):
        p = Path(directory) / "existing"
        assert p.read_bytes() == b"original-owned"
        p.write_bytes(b"modified-owned")
        p = Path(directory) / "new-owned"
        p.write_bytes(b"new-owned")
        assert p.read_bytes() == b"new-owned"
    checkpoint("allowed-writes-complete")
    for role, session in (("child", False), ("setsid_child", True)):
        child = subprocess.run(
            [sys.executable, "-I", "-B", __file__, role],
            capture_output=True,
            timeout=1,
            start_new_session=session,
        )
        assert child.returncode == 0, child.stderr
        result[role] = json.loads(child.stdout)
        checkpoint(role + "-complete")
    result["storage"] = {}
    for folder, length in (("/candidate/owned", 16777216), ("/scratch", 33554432)):
        checkpoint(folder + "-storage-start")
        target = Path(folder) / "oversized"
        with target.open("xb", buffering=0) as f:
            result["storage"][folder + "_truncate"] = deny(lambda: f.truncate(length + 1))
            result["storage"][folder + "_seek"] = deny(
                lambda: (f.seek(length), f.write(b"x"), f.flush())
            )
        target.unlink()
        checkpoint(folder + "-sparse-complete")
        for action, value in (
            ("link", lambda: os.link(Path(folder) / "existing", Path(folder) / "alias")),
            ("xattr", lambda: os.setxattr(Path(folder) / "existing", "user.unbounded", b"x")),
        ):
            result["storage"][folder + "_" + action] = deny(value)
        exhausted = Path(folder) / "allocated-exhaustion"
        written = 0
        error_number = None
        with exhausted.open("xb", buffering=0) as stream:
            for _ in range(length // 65536 + 1):
                try:
                    written += stream.write(b"x" * 65536)
                except OSError as error:
                    error_number = error.errno
                    break
        result["storage"][folder + "_allocated"] = {
            "denied": error_number == 28,
            "errno": error_number,
            "written": written,
        }
        exhausted.unlink()
        checkpoint(folder + "-allocation-complete")
    # The independent observer must find this live deleted inode through the actual cgroup.
    deleted = Path("/candidate/owned/deleted-held")
    with deleted.open("w+b") as f:
        f.write(b"x" * 1048576)
        f.flush()
        deleted.unlink()
        st = os.fstat(f.fileno())
        Path("/scratch/deleted-ready.json").write_text(
            json.dumps(
                {
                    "inode": st.st_ino,
                    "device": st.st_dev,
                    "logical": st.st_size,
                    "fd": f.fileno(),
                    "namespace_pid": os.getpid(),
                }
            )
        )
        time.sleep(0.2)
    checkpoint("all-observations-complete")
    result["stage_timings"] = stages
    Path("/scratch/full-observations.json").write_text(json.dumps(result))
    Path("/scratch/native-tiny").write_bytes(b"tiny")
    time.sleep(0.15)


def lifecycle():
    if os.fork() == 0:
        os.setsid()
        while True:
            with open("/scratch/heartbeat", "ab") as f:
                f.write(b".")
            time.sleep(0.02)
    while True:
        time.sleep(30)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "workload"
    if mode == "workload":
        workload()
    elif mode == "entry":
        result = observe()
        for folder in ("/candidate/owned", "/scratch"):
            marker = Path(folder) / "exec-entry"
            marker.write_bytes(b"exec-entry")
            assert marker.read_bytes() == b"exec-entry"
        Path("/scratch/exec-entry-observations.json").write_text(json.dumps(result))
    elif mode in ("cancellation", "deadline"):
        lifecycle()
    else:
        result = observe()
        if mode == "child":
            child = subprocess.run(
                [sys.executable, "-I", "-B", __file__, "grandchild"],
                capture_output=True,
                timeout=1,
                start_new_session=True,
            )
            assert child.returncode == 0, child.stderr
            result["grandchild"] = json.loads(child.stdout)
        print(json.dumps(result))
