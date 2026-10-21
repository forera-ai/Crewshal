"""Build and check Phase 3B development coverage without running any task.

This ledger tracks planned units. It does not authenticate observations or grant
execution, spending, calibration, or hold-out access.
"""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import stat

from scripts import check_phase_3a_freeze as freeze


ROOT = Path(__file__).resolve().parents[1]
KIND = "phase3b-development-coverage-not-evidence"
ACTIVE_STATUSES = {"failed", "interrupted", "cancelled", "verified", "accepted-with-waiver"}


def frozen_inputs(root):
    package = freeze.verify(root)
    schedule = freeze.parse(freeze.read(root, f"{freeze.PACKAGE}/schedule.json"))
    protocol = freeze.parse(freeze.read(root, f"{freeze.PACKAGE}/protocol.json"))
    rows = [row for row in schedule["rows"] if row["split"] == "development"]
    freeze.require(len(rows) == 192, "development schedule count mismatch")
    freeze.require(len(schedule["rows"]) - len(rows) == 576, "sealed schedule count mismatch")
    return package["content_sha256"], rows, set(protocol["failure_accounting"]["statuses"])


def build(root=ROOT):
    package_sha256, rows, _ = frozen_inputs(root)
    return {
        "schema_version": 1,
        "record_kind": KIND,
        "package_content_sha256": package_sha256,
        "execution_allowed": False,
        "spend_authorized": False,
        "rows": [
            {
                "schedule_row_id": row["ordinal"],
                "condition_sha256": row["condition_sha256"],
                "status": "planned",
                "reason": None,
                "attempt_ids": [],
            }
            for row in rows
        ],
    }


def validate(ledger, root=ROOT):
    package_sha256, schedule_rows, statuses = frozen_inputs(root)
    freeze.require(isinstance(ledger, dict), "ledger must be an object")
    freeze.require(
        set(ledger)
        == {
            "schema_version",
            "record_kind",
            "package_content_sha256",
            "execution_allowed",
            "spend_authorized",
            "rows",
        },
        "ledger fields mismatch",
    )
    freeze.require(
        type(ledger["schema_version"]) is int and ledger["schema_version"] == 1,
        "ledger schema mismatch",
    )
    freeze.require(ledger["record_kind"] == KIND, "ledger kind mismatch")
    freeze.require(ledger["package_content_sha256"] == package_sha256, "frozen package mismatch")
    freeze.require(
        ledger["execution_allowed"] is False and ledger["spend_authorized"] is False,
        "ledger grants authority",
    )
    rows = ledger["rows"]
    freeze.require(
        isinstance(rows, list) and len(rows) == len(schedule_rows), "development coverage mismatch"
    )
    counts = Counter()
    seen_attempts = set()
    for entry, scheduled in zip(rows, schedule_rows, strict=True):
        freeze.require(
            isinstance(entry, dict)
            and set(entry)
            == {"schedule_row_id", "condition_sha256", "status", "reason", "attempt_ids"},
            "row fields mismatch",
        )
        freeze.require(
            type(entry["schedule_row_id"]) is int
            and entry["schedule_row_id"] == scheduled["ordinal"]
            and entry["condition_sha256"] == scheduled["condition_sha256"],
            "schedule row mismatch",
        )
        status = entry["status"]
        freeze.require(isinstance(status, str) and status in statuses, "invalid status")
        reason = entry["reason"]
        attempts = entry["attempt_ids"]
        freeze.require(
            isinstance(attempts, list)
            and all(isinstance(item, str) and 0 < len(item) <= 128 for item in attempts)
            and len(attempts) == len(set(attempts)),
            "invalid attempt IDs",
        )
        freeze.require(not seen_attempts.intersection(attempts), "attempt ID reused across rows")
        seen_attempts.update(attempts)
        if status == "planned":
            freeze.require(reason is None and not attempts, "planned row has observations")
        else:
            freeze.require(
                isinstance(reason, str) and 0 < len(reason) <= 2048,
                "non-planned row needs a reason",
            )
        if status in ACTIVE_STATUSES:
            freeze.require(attempts, "attempted row needs an attempt ID")
        counts[status] += 1
    return {
        "development_rows": len(rows),
        "sealed_rows_read_only": 576,
        "status_counts": dict(sorted(counts.items())),
        "evidence_verified": False,
        "execution_allowed": False,
    }


def read_ledger(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        file_stat = os.fstat(descriptor)
        freeze.require(stat.S_ISREG(file_stat.st_mode), "ledger must be a regular file")
        freeze.require(0 < file_stat.st_size <= 2 * 1024 * 1024, "ledger exceeds size bound")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            content = stream.read(2 * 1024 * 1024 + 1)
        freeze.require(len(content) == file_stat.st_size, "ledger size changed during read")
        return freeze.parse(content)
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Print a planned development ledger to stdout")
    check = commands.add_parser("check", help="Check a local coverage ledger")
    check.add_argument("ledger", type=Path)
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps(build(), indent=2, sort_keys=True))
    else:
        print(json.dumps(validate(read_ledger(args.ledger)), sort_keys=True))


if __name__ == "__main__":
    main()
