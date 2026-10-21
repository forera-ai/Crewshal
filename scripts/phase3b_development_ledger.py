"""Build and check Phase 3B development coverage without running any task.

This ledger tracks planned units. It does not authenticate observations or grant
execution, spending, calibration, or hold-out access.
"""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from scripts import check_phase_3a_freeze as freeze


ROOT = Path(__file__).resolve().parents[1]
KIND = "phase3b-development-coverage-not-evidence"
ACTIVE_STATUSES = {"failed", "interrupted", "cancelled", "verified", "accepted-with-waiver"}
EVIDENCE_KIND = "phase3b-development-evidence-inventory-not-execution-proof"
ARTIFACT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


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


def check_evidence(ledger, bundle, artifact_dir, root=ROOT):
    """Check declared attempt coverage and local artifact bytes, not their truth."""
    coverage = validate(ledger, root)
    _, _, statuses = frozen_inputs(root)
    freeze.require(isinstance(bundle, dict), "evidence inventory must be an object")
    freeze.require(
        set(bundle)
        == {"schema_version", "record_kind", "package_content_sha256", "ledger_sha256", "attempts"},
        "evidence inventory fields mismatch",
    )
    freeze.require(
        type(bundle["schema_version"]) is int and bundle["schema_version"] == 1,
        "evidence inventory schema mismatch",
    )
    freeze.require(bundle["record_kind"] == EVIDENCE_KIND, "evidence inventory kind mismatch")
    freeze.require(
        bundle["package_content_sha256"] == ledger["package_content_sha256"],
        "evidence inventory package mismatch",
    )
    ledger_bytes = json.dumps(ledger, sort_keys=True, separators=(",", ":")).encode()
    freeze.require(
        bundle["ledger_sha256"] == hashlib.sha256(ledger_bytes).hexdigest(),
        "evidence inventory ledger mismatch",
    )
    expected = [
        (attempt_id, entry) for entry in ledger["rows"] for attempt_id in entry["attempt_ids"]
    ]
    attempts = bundle["attempts"]
    freeze.require(
        isinstance(attempts, list) and len(attempts) == len(expected),
        "evidence attempt coverage mismatch",
    )
    freeze.require(not Path(artifact_dir).is_symlink(), "artifact directory is a symlink")
    directory = os.open(artifact_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    checked_files = 0
    seen_files = set()
    try:
        for (attempt_id, entry), attempt in zip(expected, attempts, strict=True):
            freeze.require(
                isinstance(attempt, dict)
                and set(attempt)
                == {
                    "attempt_id",
                    "schedule_row_id",
                    "condition_sha256",
                    "outcome",
                    "reason",
                    "files",
                },
                "evidence attempt fields mismatch",
            )
            freeze.require(
                attempt["attempt_id"] == attempt_id
                and type(attempt["schedule_row_id"]) is int
                and attempt["schedule_row_id"] == entry["schedule_row_id"]
                and attempt["condition_sha256"] == entry["condition_sha256"],
                "evidence attempt schedule mismatch",
            )
            outcome = attempt["outcome"]
            freeze.require(
                isinstance(outcome, str) and outcome in statuses - {"planned", "not-attempted"},
                "evidence attempt outcome invalid",
            )
            freeze.require(
                isinstance(attempt["reason"], str) and 0 < len(attempt["reason"]) <= 2048,
                "evidence attempt needs a reason",
            )
            if attempt_id == entry["attempt_ids"][-1]:
                freeze.require(
                    outcome == entry["status"] and attempt["reason"] == entry["reason"],
                    "final attempt does not match ledger",
                )
            files = attempt["files"]
            freeze.require(isinstance(files, list) and files, "evidence attempt has no files")
            kinds = set()
            for item in files:
                freeze.require(
                    isinstance(item, dict) and set(item) == {"name", "kind", "bytes", "sha256"},
                    "evidence file fields mismatch",
                )
                name = item["name"]
                kind = item["kind"]
                freeze.require(
                    isinstance(name, str)
                    and ARTIFACT_NAME.fullmatch(name) is not None
                    and name not in {".", ".."}
                    and name not in seen_files,
                    "evidence file name invalid or reused",
                )
                freeze.require(
                    isinstance(kind, str) and ARTIFACT_NAME.fullmatch(kind) is not None,
                    "evidence file kind invalid",
                )
                freeze.require(
                    type(item["bytes"]) is int and 0 < item["bytes"] <= MAX_ARTIFACT_BYTES,
                    "evidence file size invalid",
                )
                freeze.require(
                    isinstance(item["sha256"], str)
                    and SHA256.fullmatch(item["sha256"]) is not None,
                    "evidence file digest invalid",
                )
                descriptor = os.open(
                    name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
                )
                try:
                    file_stat = os.fstat(descriptor)
                    freeze.require(stat.S_ISREG(file_stat.st_mode), "evidence file must be regular")
                    freeze.require(
                        file_stat.st_size == item["bytes"], "evidence file size mismatch"
                    )
                    digest = hashlib.sha256()
                    with os.fdopen(descriptor, "rb", closefd=False) as stream:
                        while chunk := stream.read(1024 * 1024):
                            digest.update(chunk)
                    freeze.require(
                        digest.hexdigest() == item["sha256"], "evidence file digest mismatch"
                    )
                    freeze.require(
                        os.fstat(descriptor).st_size == file_stat.st_size,
                        "evidence file size changed during read",
                    )
                finally:
                    os.close(descriptor)
                seen_files.add(name)
                kinds.add(kind)
                checked_files += 1
            freeze.require("run" in kinds, "evidence attempt lacks a run file")
    finally:
        os.close(directory)
    return {
        **coverage,
        "attempts_indexed": len(attempts),
        "evidence_files_checked": checked_files,
        "evidence_inventory_checked": True,
        "evidence_verified": False,
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
    evidence = commands.add_parser("check-evidence", help="Check a local evidence inventory")
    evidence.add_argument("ledger", type=Path)
    evidence.add_argument("inventory", type=Path)
    evidence.add_argument("artifact_dir", type=Path)
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps(build(), indent=2, sort_keys=True))
    elif args.command == "check":
        print(json.dumps(validate(read_ledger(args.ledger)), sort_keys=True))
    else:
        print(
            json.dumps(
                check_evidence(
                    read_ledger(args.ledger), read_ledger(args.inventory), args.artifact_dir
                ),
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
