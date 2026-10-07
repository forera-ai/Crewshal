"""Remove only the session-owned native diagnostic fixture after independent inspection."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

BASE = Path("/var/tmp/crewshal-native-discovery-v1")
INPUTS = Path("/tmp/crewshal-native-input-v1")
ENV = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin", "LC_ALL": "C"}
EXPECTED = {
    "crewshal-native-bwrap-v1": "7c9bb1831ed79c3b6d8ec117ae1d0156b2e670b1b7185ff8ffa451e4f1b7eba6",
    "crewshal-native-tool-v1": "de739b03eec825f9997229675c98f8aae801389baeeb847b6dfc6597fb67646f",
}

def command(argv):
    result = subprocess.run(argv, env=ENV, capture_output=True, timeout=10)
    if len(result.stdout) > 65536 or len(result.stderr) > 65536:
        raise RuntimeError("cleanup output ceiling exceeded")
    if result.returncode:
        raise RuntimeError("cleanup command refused")
    return result.stdout.decode()

def references():
    matches = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        entries = [process / n for n in ("cwd", "root", "exe")]
        try:
            entries.extend((process / "fd").iterdir())
        except (FileNotFoundError, PermissionError):
            pass
        for entry in entries:
            try:
                target = os.readlink(entry)
            except (FileNotFoundError, PermissionError, OSError):
                continue
            if any(target.startswith(str(p) + "/") or target == str(p)
                   for p in (BASE, INPUTS)):
                matches.append({"pid": int(process.name), "handle": entry.name})
    return matches

def main():
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        raise RuntimeError("requires supplied disposable aarch64 root role")
    for directory in (BASE, INPUTS):
        if directory.is_symlink() or directory.resolve() != directory:
            raise RuntimeError("owned fixture path changed")
    before = references()
    if before:
        raise RuntimeError("fixture handles remain")
    mounts = [line.split()[4] for line in Path("/proc/self/mountinfo").read_text().splitlines()]
    if any(m == str(BASE) or m.startswith(str(BASE) + "/") for m in mounts):
        raise RuntimeError("owned fixture mount remains")
    for name, expected in EXPECTED.items():
        paths = list(Path("/sys/kernel/security/apparmor/policy/profiles").glob(name + ".*/sha256"))
        if len(paths) != 1 or paths[0].read_text().strip() != expected:
            raise RuntimeError("owned loaded policy identity changed")
    policy = Path("/run/crewshal-native-apparmor-proposal-v3.profile")
    if hashlib.sha256(policy.read_bytes()).hexdigest() != "e20e454cbcf45fc26e8641707a4d2db751a9f86d9b6af81b33e2be605bb994fb":
        raise RuntimeError("owned policy source changed")
    command(["/usr/sbin/apparmor_parser", "--config-file", "/dev/null", "--skip-cache",
             "--remove", "--jobs", "1", "--max-jobs", "1", str(policy)])
    for directory in (BASE, INPUTS):
        shutil.rmtree(directory)
    owned = [Path("/run/crewshal-native-discovery-v1.py"),
             Path("/run/crewshal-direct-mechanism-v5.py")]
    owned += [Path(f"/run/crewshal-native-compatibility-v{v}.py") for v in range(2, 11)]
    owned += [Path(f"/run/crewshal-native-apparmor-proposal-v{v}.profile") for v in range(2, 5)]
    owned += [Path(f"/tmp/crewshal-native-{kind}-compat-v{v}.json")
              for kind in ("manifest", "observed") for v in range(2, 11)]
    owned += [Path("/tmp/crewshal-native-audit-v9-v10.txt")]
    for path in owned:
        path.unlink(missing_ok=True)
    remaining = [line for line in Path("/sys/kernel/security/apparmor/profiles").read_text().splitlines()
                 if line.startswith("crewshal-native-")]
    result = {"scope": "owned native diagnostic fixture cleanup only",
              "before_process_fd_references": before, "after_process_fd_references": references(),
              "owned_fixture_paths_remaining": [str(p) for p in (BASE, INPUTS) if p.exists()],
              "owned_loaded_profiles_remaining": remaining,
              "global_userns_restriction": Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns").read_text().strip(),
              "execution_allowed": False, "native_start_allowed": False}
    print(json.dumps(result))
    if remaining or result["after_process_fd_references"] or result["owned_fixture_paths_remaining"]:
        raise RuntimeError("cleanup incomplete")

if __name__ == "__main__":
    main()
