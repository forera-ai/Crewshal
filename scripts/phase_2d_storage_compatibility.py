"""Reproduce the current source policy conflict offline, without kernel effects.

This evaluates the Python cBPF source, not an installed helper. Public upstream
call-chain evidence is recorded in the dated continuation; this driver neither
fetches nor executes vendor source. A successful driver exit means the report
was produced, never that the incompatible runtime profile was qualified.
"""

import hashlib
import json
from pathlib import Path
import struct

from crewshal.linux_bootstrap import payload_storage_filter


def evaluate(program: bytes, architecture: int, number: int, flags: int, fd: int) -> int:
    # seccomp_data: nr, arch, instruction_pointer, then six 64-bit arguments.
    data = struct.pack("=iI7Q", number, architecture, 0, 0, 4096, 3, flags, fd & ((1 << 64) - 1), 0)
    rows = tuple(struct.iter_unpack("=HBBI", program))
    pc, accumulator = 0, 0
    for _ in rows:
        code, yes, no, value = rows[pc]
        if code == 0x20:
            accumulator = struct.unpack_from("=I", data, value)[0]
        elif code == 0x54:
            accumulator &= value
        elif code in (0x15, 0x35):
            matches = accumulator == value if code == 0x15 else accumulator >= value
            pc += yes if matches else no
        elif code == 0x06:
            return value
        else:
            raise ValueError("unrecognized source cBPF instruction")
        pc += 1
    raise ValueError("source cBPF program did not terminate")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports = []
    for machine, architecture, number in (("x86_64", 0xC000003E, 9), ("aarch64", 0xC00000B7, 222)):
        program = payload_storage_filter(machine)
        cases = []
        for label, flags, fd in (
            ("bounded ordinary SQLite WAL index", 1, 42),
            ("dev-zero shmem", 1, 43),
            ("anonymous shared shmem", 0x21, -1),
            ("private anonymous mapping", 0x22, -1),
        ):
            decision = evaluate(program, architecture, number, flags, fd)
            cases.append(
                {
                    "input_semantics": label,
                    "flags": flags,
                    "fd": fd,
                    "decision": "allow" if decision == 0x7FFF0000 else "deny",
                    "seccomp_return": decision,
                }
            )
        if [case["decision"] for case in cases] != ["deny", "deny", "deny", "allow"]:
            raise ValueError("current source policy changed; compatibility report must be reviewed")
        reports.append(
            {
                "machine": machine,
                "program_bytes": len(program),
                "program_sha256": hashlib.sha256(program).hexdigest(),
                "cases": cases,
            }
        )
    helper = (root / "src/crewshal/bootstrap_helper.c").read_bytes()
    print(
        json.dumps(
            {
                "schema_version": 1,
                "classification": "offline source incompatibility; installed behavior unknown",
                "compatible": False,
                "execution_allowed": False,
                "runtime_verified": False,
                "compiler_invoked": False,
                "kernel_filter_loaded": False,
                "helper_bytes": len(helper),
                "helper_sha256": hashlib.sha256(helper).hexdigest(),
                "abis": reports,
                "missing_capability": "Allow bounded ordinary file-backed WAL mappings while effectively bounding anonymous/dev-zero shmem and additional payload namespace filesystems.",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
