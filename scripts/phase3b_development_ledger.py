"""Build and check Phase 3B development coverage without running any task.

This ledger tracks planned units. It does not authenticate observations or grant
execution, spending, calibration, or hold-out access.
"""

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

from scripts import check_phase_3a_freeze as freeze


ROOT = Path(__file__).resolve().parents[1]
KIND = "phase3b-development-coverage-not-evidence"
ACTIVE_STATUSES = {"failed", "interrupted", "cancelled", "verified", "accepted-with-waiver"}
EVIDENCE_KIND = "phase3b-development-evidence-inventory-not-execution-proof"
MEASUREMENT_KIND = "phase3b-development-measurement-claims-not-execution-proof"
EVIDENCE_FIELDS = {"name", "kind", "bytes", "sha256"}
ARTIFACT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


def nonnegative_number(value):
    return (type(value) is int and value >= 0) or (
        type(value) is float and math.isfinite(value) and value >= 0
    )


def measurement_source_fields(record):
    """Name populated observations that need a declared local source file."""
    fields = {"date", "outcome", "reason"}
    for group, keys in (
        ("unit", ("operation_id", "repository_revision")),
        ("identity", tuple(key for key in record["identity"] if key != "frozen_package_sha256")),
        ("effort", tuple(record["effort"])),
        (
            "usage",
            (
                "new_input_tokens",
                "cached_input_tokens",
                "cache_write_tokens",
                "output_tokens",
                "reasoning_tokens",
                "provenance",
            ),
        ),
    ):
        fields.update(f"{group}.{key}" for key in keys if record[group][key] is not None)
    for group in ("measured_cost", "estimated_cost", "subscription_quota"):
        fields.update(
            f"usage.{group}.{key}"
            for key, value in record["usage"][group].items()
            if value is not None
        )
    fields.update(key for key in ("checks", "claims", "review", "waivers") if record[key])
    return fields


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
                    isinstance(item, dict) and set(item) == EVIDENCE_FIELDS,
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


def check_measurements(ledger, bundle, root=ROOT):
    """Check schedule and accounting claims without authenticating a run."""
    coverage = validate(ledger, root)
    _, schedule_rows, statuses = frozen_inputs(root)
    template = freeze.parse(freeze.read(root, f"{freeze.PACKAGE}/measurement-template.json"))
    freeze.require(isinstance(bundle, dict), "measurement bundle must be an object")
    freeze.require(
        set(bundle)
        == {
            "schema_version",
            "record_kind",
            "package_content_sha256",
            "ledger_sha256",
            "inventory_sha256",
            "records",
        },
        "measurement bundle fields mismatch",
    )
    freeze.require(
        type(bundle["schema_version"]) is int and bundle["schema_version"] == 1,
        "measurement bundle schema mismatch",
    )
    freeze.require(bundle["record_kind"] == MEASUREMENT_KIND, "measurement bundle kind mismatch")
    freeze.require(
        bundle["package_content_sha256"] == ledger["package_content_sha256"],
        "measurement bundle package mismatch",
    )
    ledger_bytes = json.dumps(ledger, sort_keys=True, separators=(",", ":")).encode()
    freeze.require(
        bundle["ledger_sha256"] == hashlib.sha256(ledger_bytes).hexdigest(),
        "measurement bundle ledger mismatch",
    )
    freeze.require(
        isinstance(bundle["inventory_sha256"], str)
        and SHA256.fullmatch(bundle["inventory_sha256"]) is not None,
        "measurement inventory digest invalid",
    )
    expected = [
        (attempt_id, entry, scheduled)
        for entry, scheduled in zip(ledger["rows"], schedule_rows, strict=True)
        for attempt_id in entry["attempt_ids"]
    ]
    records = bundle["records"]
    freeze.require(
        isinstance(records, list) and len(records) == len(expected),
        "measurement attempt coverage mismatch",
    )
    counts = Counter()
    for (attempt_id, entry, scheduled), record in zip(expected, records, strict=True):
        freeze.require(
            isinstance(record, dict)
            and set(record) == set(template) | {"evidence_refs", "source_refs"},
            "measurement fields mismatch",
        )
        refs = record["evidence_refs"]
        freeze.require(isinstance(refs, list) and bool(refs), "measurement evidence refs missing")
        names = set()
        kinds = set()
        for ref in refs:
            freeze.require(
                isinstance(ref, dict) and set(ref) == EVIDENCE_FIELDS,
                "measurement evidence ref fields mismatch",
            )
            name = ref["name"]
            kind = ref["kind"]
            freeze.require(
                isinstance(name, str)
                and ARTIFACT_NAME.fullmatch(name) is not None
                and name not in {".", ".."}
                and name not in names,
                "measurement evidence ref name invalid or reused",
            )
            freeze.require(
                isinstance(kind, str) and ARTIFACT_NAME.fullmatch(kind) is not None,
                "measurement evidence ref kind invalid",
            )
            freeze.require(
                type(ref["bytes"]) is int and 0 < ref["bytes"] <= MAX_ARTIFACT_BYTES,
                "measurement evidence ref size invalid",
            )
            freeze.require(
                isinstance(ref["sha256"], str) and SHA256.fullmatch(ref["sha256"]) is not None,
                "measurement evidence ref digest invalid",
            )
            names.add(name)
            kinds.add(kind)
        freeze.require("run" in kinds, "measurement evidence refs lack a run file")
        freeze.require(
            record["record_kind"] == MEASUREMENT_KIND
            and record["status"] == "unverified-development-claim"
            and record["execution_allowed"] is False
            and record["spend_authorized"] is False
            and record["package_id"] == template["package_id"]
            and record["annotation_method"] == template["annotation_method"],
            "measurement claims authority or kind mismatch",
        )
        freeze.require(isinstance(record["date"], str), "measurement date invalid")
        try:
            valid_date = date.fromisoformat(record["date"]).isoformat() == record["date"]
        except ValueError:
            valid_date = False
        freeze.require(valid_date, "measurement date invalid")
        unit = record["unit"]
        freeze.require(
            isinstance(unit, dict) and set(unit) == set(template["unit"]),
            "measurement unit fields mismatch",
        )
        for key, value in {
            "attempt_id": attempt_id,
            "schedule_row_id": scheduled["ordinal"],
            "condition": scheduled["condition"],
            "repetition": scheduled["repetition"],
            "repository_id": scheduled["repository_id"],
            "role_assignment": scheduled["role_assignment"],
            "task_id": scheduled["task_id"],
        }.items():
            freeze.require(
                type(unit[key]) is type(value) and unit[key] == value,
                "measurement unit schedule mismatch",
            )
        for key in ("operation_id", "repository_revision"):
            value = unit[key]
            freeze.require(
                value is None or (isinstance(value, str) and 0 < len(value) <= 128),
                "measurement unit identity invalid",
            )
        outcome = record["outcome"]
        freeze.require(
            isinstance(outcome, str) and outcome in statuses - {"planned", "not-attempted"},
            "measurement outcome invalid",
        )
        reason = record["reason"]
        freeze.require(
            isinstance(reason, str) and 0 < len(reason) <= 2048, "measurement reason invalid"
        )
        if attempt_id == entry["attempt_ids"][-1]:
            freeze.require(
                outcome == entry["status"] and reason == entry["reason"],
                "final measurement does not match ledger",
            )
        identity = record["identity"]
        freeze.require(
            isinstance(identity, dict) and set(identity) == set(template["identity"]),
            "measurement identity fields mismatch",
        )
        freeze.require(
            identity["frozen_package_sha256"] == ledger["package_content_sha256"],
            "measurement frozen package mismatch",
        )
        for key, value in identity.items():
            if key != "frozen_package_sha256":
                freeze.require(
                    value is None
                    or (isinstance(value, str) and SHA256.fullmatch(value) is not None),
                    "measurement identity digest invalid",
                )
        if scheduled["condition"] != "P":
            freeze.require(
                identity["confirmed_model_sha256"] is None,
                "baseline claims a Crewshal project model",
            )
        if scheduled["condition"] == "B0":
            freeze.require(identity["review_identity_sha256"] is None, "B0 claims a reviewer")
        effort = record["effort"]
        freeze.require(
            isinstance(effort, dict) and set(effort) == set(template["effort"]),
            "measurement effort fields mismatch",
        )
        integer_effort = {
            "context_bytes",
            "correction_count",
            "dispatches",
            "retries",
            "review_loops",
        }
        for key, value in effort.items():
            if value is not None:
                valid = (
                    type(value) is int and value >= 0
                    if key in integer_effort
                    else nonnegative_number(value)
                )
                freeze.require(valid, "measurement effort invalid")
        usage = record["usage"]
        freeze.require(
            isinstance(usage, dict) and set(usage) == set(template["usage"]),
            "measurement usage fields mismatch",
        )
        freeze.require(type(usage["unknown_usage"]) is bool, "unknown usage flag invalid")
        freeze.require(
            usage["deduplication_key"] == template["usage"]["deduplication_key"]
            and usage["cumulative_snapshot_rule"] == template["usage"]["cumulative_snapshot_rule"],
            "usage accounting rule changed",
        )
        token_keys = (
            "new_input_tokens",
            "cached_input_tokens",
            "cache_write_tokens",
            "output_tokens",
            "reasoning_tokens",
        )
        for key in token_keys:
            value = usage[key]
            freeze.require(
                value is None or (type(value) is int and value >= 0), "usage token count invalid"
            )
        if usage["unknown_usage"] is False:
            freeze.require(
                all(usage[key] is not None for key in token_keys)
                and isinstance(usage["provenance"], str)
                and bool(usage["provenance"].strip()),
                "complete usage claim lacks counters or provenance",
            )
        else:
            freeze.require(
                usage["provenance"] is None
                or (isinstance(usage["provenance"], str) and bool(usage["provenance"].strip())),
                "usage provenance invalid",
            )
        for key, fields in {
            "measured_cost": ("amount", "currency", "billing_evidence"),
            "estimated_cost": (
                "amount",
                "currency",
                "formula",
                "pricing_source",
                "pricing_timestamp",
            ),
            "subscription_quota": ("value", "unit", "source"),
        }.items():
            part = usage[key]
            freeze.require(
                isinstance(part, dict) and set(part) == set(template["usage"][key]),
                "usage cost fields mismatch",
            )
            amount_key = "value" if key == "subscription_quota" else "amount"
            amount = part[amount_key]
            freeze.require(
                amount is None or nonnegative_number(amount),
                "usage amount invalid",
            )
            if amount is not None:
                freeze.require(
                    all(
                        isinstance(part[field], str) and bool(part[field].strip())
                        for field in fields
                        if field != amount_key
                    ),
                    "usage amount lacks provenance",
                )
            else:
                freeze.require(
                    all(part[field] is None for field in fields if field != amount_key),
                    "usage metadata lacks amount",
                )
        freeze.require(
            isinstance(record["checks"], list)
            and isinstance(record["claims"], list)
            and isinstance(record["waivers"], list)
            and (record["review"] is None or isinstance(record["review"], dict)),
            "measurement detail fields invalid",
        )
        sources = record["source_refs"]
        freeze.require(
            isinstance(sources, dict) and set(sources) == measurement_source_fields(record),
            "measurement source fields mismatch",
        )
        for field, source_names in sources.items():
            freeze.require(
                isinstance(source_names, list)
                and bool(source_names)
                and all(isinstance(name, str) for name in source_names)
                and len(source_names) == len(set(source_names))
                and set(source_names) <= names,
                f"measurement source file invalid for {field}",
            )
        counts[outcome] += 1
    return {
        **coverage,
        "measurement_attempts_checked": len(records),
        "measurement_outcome_counts": dict(sorted(counts.items())),
        "measurement_claims_checked": True,
        "evidence_verified": False,
        "execution_allowed": False,
    }


def check_provenance(ledger, inventory, measurements, artifact_dir, root=ROOT):
    """Bind local measurement claims to inventory bytes without authenticating their source."""
    evidence = check_evidence(ledger, inventory, artifact_dir, root)
    measured = check_measurements(ledger, measurements, root)
    inventory_bytes = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
    freeze.require(
        measurements["inventory_sha256"] == hashlib.sha256(inventory_bytes).hexdigest(),
        "measurement inventory mismatch",
    )
    linked_files = 0
    for attempt, record in zip(inventory["attempts"], measurements["records"], strict=True):
        freeze.require(
            record["evidence_refs"] == attempt["files"],
            "measurement evidence refs differ from inventory",
        )
        freeze.require(
            record["outcome"] == attempt["outcome"] and record["reason"] == attempt["reason"],
            "measurement outcome differs from evidence inventory",
        )
        linked_files += len(record["evidence_refs"])
    return {
        **measured,
        "evidence_files_checked": evidence["evidence_files_checked"],
        "measurement_evidence_files_linked": linked_files,
        "provenance_links_checked": True,
        "evidence_verified": False,
        "execution_allowed": False,
    }


def read_content_file(directory, item):
    """Read one inventory-bound regular file without following a link."""
    descriptor = os.open(
        item["name"], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
    )
    try:
        file_stat = os.fstat(descriptor)
        freeze.require(stat.S_ISREG(file_stat.st_mode), "content file must be regular")
        freeze.require(file_stat.st_size == item["bytes"], "content file size mismatch")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            content = stream.read(item["bytes"] + 1)
        freeze.require(len(content) == item["bytes"], "content file size changed during read")
        freeze.require(
            hashlib.sha256(content).hexdigest() == item["sha256"],
            "content file digest mismatch",
        )
        freeze.require(
            os.fstat(descriptor).st_size == file_stat.st_size,
            "content file size changed during read",
        )
        return content
    finally:
        os.close(descriptor)


def content_claim(record, field):
    value = record
    for key in field.split("."):
        value = value[key]
    return value


def compare_json_content(content, field, claimed):
    """Compare a claim only with its matching path in a JSON object."""

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"non-finite JSON value: {value}")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("non-finite JSON number")
        return number

    try:
        source = json.loads(
            content,
            object_pairs_hook=unique_pairs,
            parse_constant=reject_constant,
            parse_float=finite_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
        return "unsupported", "invalid_json"
    if not isinstance(source, dict):
        return "unsupported", "non_object_json"
    for key in field.split("."):
        if not isinstance(source, dict) or key not in source:
            return "unmatched", "path_missing"
        source = source[key]
    if type(source) is type(claimed) and source == claimed:
        return "matched", "exact_value"
    return "unmatched", "value_differs"


def check_contents(ledger, inventory, measurements, artifact_dir, root=ROOT):
    """Report exact local JSON matches without authenticating observation origin."""
    provenance = check_provenance(ledger, inventory, measurements, artifact_dir, root)
    freeze.require(not Path(artifact_dir).is_symlink(), "artifact directory is a symlink")
    directory = os.open(artifact_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    results = []
    try:
        for attempt, record in zip(inventory["attempts"], measurements["records"], strict=True):
            files = {item["name"]: item for item in attempt["files"]}
            for field, names in sorted(record["source_refs"].items()):
                claimed = content_claim(record, field)
                for name in names:
                    item = files[name]
                    if not name.lower().endswith(".json"):
                        status, detail = "unsupported", "non_json_format"
                    else:
                        content = read_content_file(directory, item)
                        status, detail = compare_json_content(content, field, claimed)
                    results.append(
                        {
                            "attempt_id": attempt["attempt_id"],
                            "field": field,
                            "file": name,
                            "status": status,
                            "detail": detail,
                        }
                    )
    finally:
        os.close(directory)
    counts = Counter(item["status"] for item in results)
    return {
        **provenance,
        "content_checks": results,
        "content_status_counts": dict(sorted(counts.items())),
        "content_matches_are_execution_evidence": False,
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
    evidence = commands.add_parser("check-evidence", help="Check a local evidence inventory")
    evidence.add_argument("ledger", type=Path)
    evidence.add_argument("inventory", type=Path)
    evidence.add_argument("artifact_dir", type=Path)
    measurements = commands.add_parser("check-measurements", help="Check local measurement claims")
    measurements.add_argument("ledger", type=Path)
    measurements.add_argument("measurements", type=Path)
    provenance = commands.add_parser("check-provenance", help="Check local claim and file links")
    provenance.add_argument("ledger", type=Path)
    provenance.add_argument("inventory", type=Path)
    provenance.add_argument("measurements", type=Path)
    provenance.add_argument("artifact_dir", type=Path)
    contents = commands.add_parser(
        "check-contents", help="Compare local JSON claims at matching paths"
    )
    contents.add_argument("ledger", type=Path)
    contents.add_argument("inventory", type=Path)
    contents.add_argument("measurements", type=Path)
    contents.add_argument("artifact_dir", type=Path)
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps(build(), indent=2, sort_keys=True))
    elif args.command == "check":
        print(json.dumps(validate(read_ledger(args.ledger)), sort_keys=True))
    elif args.command == "check-evidence":
        print(
            json.dumps(
                check_evidence(
                    read_ledger(args.ledger), read_ledger(args.inventory), args.artifact_dir
                ),
                sort_keys=True,
            )
        )
    elif args.command == "check-measurements":
        print(
            json.dumps(
                check_measurements(read_ledger(args.ledger), read_ledger(args.measurements)),
                sort_keys=True,
            )
        )
    elif args.command == "check-provenance":
        print(
            json.dumps(
                check_provenance(
                    read_ledger(args.ledger),
                    read_ledger(args.inventory),
                    read_ledger(args.measurements),
                    args.artifact_dir,
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            json.dumps(
                check_contents(
                    read_ledger(args.ledger),
                    read_ledger(args.inventory),
                    read_ledger(args.measurements),
                    args.artifact_dir,
                ),
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
