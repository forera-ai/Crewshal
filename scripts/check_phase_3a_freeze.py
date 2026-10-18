"""Verify the frozen source package. This checker grants no execution authority."""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat


PACKAGE = "docs/evaluation/phase-3a-frozen"
NAMES = {
    "README.md",
    "annotation-a.json",
    "annotation-b.json",
    "baseline-conformance.json",
    "conditions.json",
    "corpus.json",
    "development-adjudication.json",
    "development-tasks.json",
    "execution-admission.json",
    "measurement-template.json",
    "owner-decisions.json",
    "package-review-b.json",
    "protocol.json",
    "rubric.json",
    "runtime-selections.json",
    "schedule.json",
    "sealed-commitments.json",
    "source-inventories.json",
    "supplemental-fixtures.json",
}
RELATED = {
    "INITIAL-EVALUATION-PLAN.md",
    "docs/decisions/0008-agent-annotation-and-phase-3a-freeze.md",
    "scripts/check_phase_3a_freeze.py",
    "tests/acceptance/test_phase_3a_freeze.py",
}
SHA = re.compile(r"[0-9a-f]{64}\Z")
STACKS = {"python", "typescript", "swift", "dotnet"}
CONDITIONS = {"B0", "B1", "B2", "P"}
ROLES = {"A-implements", "B-implements"}
MAX_BYTES = 8 * 1024 * 1024


class FreezeError(ValueError):
    """The package lacks consistent frozen evidence."""


def require(value, reason):
    if not value:
        raise FreezeError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise FreezeError(f"nonfinite JSON number: {value}")


def parse(content):
    try:
        result = json.loads(content, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise FreezeError("invalid JSON") from error
    require(isinstance(result, dict), "JSON root must be an object")
    require(type(result.get("schema_version")) is int, "schema version must be an integer")
    require(result["schema_version"] == 1, "unsupported schema version")
    pending = [result]
    while pending:
        item = pending.pop()
        if isinstance(item, float):
            require(math.isfinite(item), "nonfinite JSON number")
        elif isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return result


def safe_path(value):
    require(isinstance(value, str) and bool(value), "invalid path")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and str(path) == value
        and not any(part in {".", ".."} for part in path.parts)
        and "\\" not in value
        and "\x00" not in value,
        "unsafe relative path",
    )
    return path.parts


def read(root, relative):
    """Open each component without following links. Read regular bounded files."""
    parts = safe_path(relative)
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in parts[:-1]:
            child = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        try:
            observed = os.fstat(descriptor)
            require(stat.S_ISREG(observed.st_mode), "artifact must be a regular file")
            require(0 < observed.st_size <= MAX_BYTES, "artifact exceeds size bound")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                content = stream.read(MAX_BYTES + 1)
            require(len(content) == observed.st_size, "artifact size changed during read")
            return content
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def expected_schedule(tasks, sealed, protocol):
    result = []
    selected = set(protocol["design"]["development_repository_ids"])
    groups = [
        ("development", [row for row in tasks if row["repository_id"] in selected], 2),
        ("sealed", sealed, 3),
    ]
    for split, entries, repetitions in groups:
        blocks = []
        for task in entries:
            for repetition in range(1, repetitions + 1):
                for role in sorted(ROLES):
                    key = f"310016|{task['repository_id']}|{task['id']}|{repetition}|{role}"
                    block = []
                    for condition in sorted(CONDITIONS):
                        condition_key = key + "|" + condition
                        block.append(
                            {
                                "split": split,
                                "repository_id": task["repository_id"],
                                "task_id": task["id"],
                                "repetition": repetition,
                                "role_assignment": role,
                                "condition": condition,
                                "block_key": key,
                                "block_sha256": digest(key.encode()),
                                "condition_key": condition_key,
                                "condition_sha256": digest(condition_key.encode()),
                                "status": "planned",
                                "execution_allowed": False,
                            }
                        )
                    blocks.append((digest(key.encode()), key, block))
        for _, _, block in sorted(blocks):
            result.extend(
                sorted(block, key=lambda row: (row["condition_sha256"], row["condition_key"]))
            )
    for ordinal, row in enumerate(result, 1):
        row["ordinal"] = ordinal
    return result


def semantics(data):
    decisions = data["owner-decisions.json"]
    answers = {
        "annotation-method": "Approve the agent method and delegation.",
        "bounded-selections": "Approve these bounded selections.",
        "zero-spending": "Record zero spending; require approval before Phase 3B execution.",
    }
    approvals = decisions["approvals"]
    require(len(approvals) == 3, "three owner answers are required")
    require({r["id"]: r["answer"] for r in approvals} == answers, "owner answer mismatch")
    require(
        digest(canonical(approvals)) == decisions["approval_text_sha256"], "approval hash mismatch"
    )
    budget = decisions["approved_budget"]
    for key in (
        "estimated_cost_allowance",
        "measured_cost_allowance",
        "paid_host_allowance",
        "subscription_quota_allowance",
    ):
        require(type(budget[key]) is int and budget[key] == 0, "zero budget is required")
    require(budget["calibration_allowed"] is False, "calibration is not authorized")
    require(budget["sealed_execution_allowed"] is False, "sealed execution is not authorized")
    for name, document in data.items():
        if "execution_allowed" in document:
            require(document["execution_allowed"] is False, f"execution authority in {name}")
        if "spend_authorized" in document:
            require(document["spend_authorized"] is False, f"spending authority in {name}")
    admission = data["execution-admission.json"]
    for key in ("phase_3b_execution_allowed", "phase_3c_execution_allowed"):
        require(admission[key] is False, "evaluation admission must remain closed")
    corpus = data["corpus.json"]["repositories"]
    require(len(corpus) == 12 and len({r["id"] for r in corpus}) == 12, "corpus count mismatch")
    require(Counter(r["stack"] for r in corpus) == dict.fromkeys(STACKS, 3), "four stacks required")
    development = {r["id"] for r in corpus if r["split"] == "development"}
    holdouts = {r["id"] for r in corpus if r["split"] == "holdout"}
    require(len(development) == 8 and len(holdouts) == 4, "split count mismatch")
    require(len({r["repository"] for r in corpus}) == 12, "repository split overlap")
    require({r["stack"] for r in corpus if r["id"] in holdouts} == STACKS, "heldout stack missing")
    sources = data["source-inventories.json"]["repositories"]
    require({r["id"] for r in sources} == development, "development sources missing")
    source_map = {r["id"]: r for r in sources}
    for source in sources:
        require(
            digest(canonical(source["files"])) == source["source_inventory_sha256"],
            "inventory digest mismatch",
        )
        paths = [entry["path"] for entry in source["files"]]
        require(paths == sorted(set(paths)), "inventory order or duplicate path")
        for entry in source["files"]:
            safe_path(entry["path"])
            require(SHA.fullmatch(entry["sha256"]), "invalid source digest")
    a, b = data["annotation-a.json"], data["annotation-b.json"]
    require(a["annotator"] != b["reviewer"], "independent annotation identities required")
    require(b["independence"]["annotation_a_accessed"] is False, "annotation independence lost")
    for annotation in (a, b):
        require(
            {r["id"] for r in annotation["repositories"]} == development | holdouts,
            "annotation coverage missing",
        )
        for row in annotation["repositories"]:
            if row["id"] in development:
                expected_fields = (
                    set(data["rubric.json"]["annotation_fields"])
                    if annotation is a
                    else {
                        "baseline",
                        "build",
                        "ci",
                        "generated",
                        "license",
                        "lint",
                        "locks",
                        "package_manager",
                        "provenance",
                        "sensitive",
                        "services",
                        "stack",
                        "test",
                        "third_party",
                        "toolchain",
                        "workspace",
                    }
                )
                require(set(row["fields"]) == expected_fields, "annotation fields missing")
            else:
                require("fields" not in row, "heldout annotation content exposed")
                require(
                    SHA.fullmatch(row["raw_record_sha256"]), "heldout annotation commitment missing"
                )
    adjudication = data["development-adjudication.json"]
    require(adjudication["human_ground_truth"] is False, "false human annotation claim")
    require(
        {r["id"] for r in adjudication["repositories"]} == development,
        "development adjudication missing",
    )
    for row in adjudication["repositories"]:
        require(
            set(row["fields"]) == set(data["rubric.json"]["annotation_fields"]),
            "adjudication fields missing",
        )
        for field in row["fields"].values():
            require(
                field["resolution"]
                and field["rationale"]
                and set(field["originals"]) == {"A", "B"},
                "adjudication decision missing",
            )
    tasks = data["development-tasks.json"]["tasks"]
    require(len(tasks) == 24 and len({t["id"] for t in tasks}) == 24, "development tasks missing")
    require(
        Counter(t["repository_id"] for t in tasks) == dict.fromkeys(development, 3),
        "development task distribution",
    )
    for task in tasks:
        source = source_map[task["repository_id"]]
        require(task["source_revision"] == source["revision"], "task revision mismatch")
        require(
            task["initial_source_inventory_sha256"] == source["source_inventory_sha256"],
            "task source mismatch",
        )
        require(
            task["requirement"] and task["checks"] and task["acceptance"],
            "task contract incomplete",
        )
        require(task["allowed_paths"], "task scope missing")
        for path in task["allowed_paths"]:
            safe_path(path)
        for case in task["acceptance"]:
            require(case["input"] and case["expected"] and case["oracle"], "task oracle incomplete")
        for check in task["checks"]:
            require(check["argv"] and check["status"] == "not-run", "false check observation")
    sealed = data["sealed-commitments.json"]
    require(sealed["complete_artifacts"] is True, "sealed artifacts incomplete")
    require(sealed["verification"]["integrity"] == "passed", "sealed integrity missing")
    require(SHA.fullmatch(sealed["adjudication"]["sha256"]), "private adjudication missing")
    require(SHA.fullmatch(sealed["blinded_condition_map"]["sha256"]), "blind mapping missing")
    require({r["id"] for r in sealed["sources"]} == holdouts, "sealed sources missing")
    require(
        len(sealed["tasks"]) == 24 and len({t["id"] for t in sealed["tasks"]}) == 24,
        "sealed tasks missing",
    )
    require(
        Counter(t["repository_id"] for t in sealed["tasks"]) == dict.fromkeys(holdouts, 6),
        "sealed task distribution",
    )
    sealed_sources = {r["id"]: r for r in sealed["sources"]}
    for task in sealed["tasks"]:
        require(re.fullmatch(r"s3a-[0-9a-f]{20}", task["id"]), "sealed ID must be opaque")
        require(
            not {"requirement", "allowed_paths", "acceptance", "oracle_source"} & task.keys(),
            "sealed task content exposed",
        )
        for key in (
            "requirement_sha256",
            "acceptance_sha256",
            "allowed_scope_sha256",
            "risk_annotation_sha256",
            "task_bundle_sha256",
            "oracle_source_sha256",
        ):
            require(SHA.fullmatch(task[key]), "sealed commitment missing")
        require(
            task["source_inventory_sha256"]
            == sealed_sources[task["repository_id"]]["source_inventory_sha256"],
            "sealed source mismatch",
        )
    runtime = data["runtime-selections.json"]
    require(
        sorted((r["id"], r["implementation"], r["review"]) for r in runtime["role_assignments"])
        == [("A-implements", "A", "B"), ("B-implements", "B", "A")],
        "role assignment mismatch",
    )
    require({r["id"] for r in runtime["runtimes"]} == {"A", "B"}, "runtime pair missing")
    for selected in runtime["runtimes"]:
        require(
            selected["live_conformance"] == "unavailable" and selected["runtime_executed"] is False,
            "false native observation",
        )
        require(
            digest(canonical(selected["configuration"])) == selected["configuration_sha256"],
            "configuration hash mismatch",
        )
        for key in (
            "resolved_model",
            "resolved_provider",
            "actual_executable_sha256",
            "effective_configuration_sha256",
        ):
            require(selected[key] is None, "future identity fabricated")
    for condition in data["conditions.json"]["conditions"]:
        require(condition["native_conformance"] == "unavailable", "false baseline qualification")
        content = {key: value for key, value in condition.items() if key != "contract_sha256"}
        require(
            digest(canonical(content)) == condition["contract_sha256"], "condition hash mismatch"
        )
    require(
        {r["id"] for r in data["conditions.json"]["conditions"]} == CONDITIONS, "condition missing"
    )
    protocol = data["protocol.json"]
    design = protocol["design"]
    require(design["development_shape"] == [4, 3, 2, 4, 2], "development shape mismatch")
    require(design["sealed_shape"] == [4, 6, 3, 4, 2], "sealed shape mismatch")
    require(
        design["planned_counts"] == {"development": 192, "sealed": 576, "total": 768},
        "planned counts mismatch",
    )
    require(
        set(design["conditions"]) == CONDITIONS and set(design["role_assignments"]) == ROLES,
        "design factors mismatch",
    )
    require(
        set(design["development_repository_ids"])
        == {"python-1", "typescript-2", "swift-1", "dotnet-1"},
        "calibration selection mismatch",
    )
    require(
        protocol["status"] == "frozen" and protocol["ordering"]["seed"] == 310016,
        "protocol selection missing",
    )
    require(
        protocol["analysis"]["primary_model_cost_metric"]["name"]
        == "estimated_api_equivalent_cost_usd",
        "cost metric missing",
    )
    require(
        data["schedule.json"]["rows"] == expected_schedule(tasks, sealed["tasks"], protocol),
        "planned schedule mismatch",
    )
    require(len(data["schedule.json"]["rows"]) == 768, "planned units missing")
    require(
        all(f["status"] == "resolved" for f in data["package-review-b.json"]["findings"]),
        "review finding remains open",
    )


def verify(root):
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in safe_path(PACKAGE):
            child = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        require(
            set(os.listdir(directory)) == NAMES | {"package-index.json"},
            "unindexed package artifact",
        )
    finally:
        os.close(directory)
    index = parse(read(root, f"{PACKAGE}/package-index.json"))
    require(index["status"] == "frozen", "package is not frozen")
    require(
        index["execution_allowed"] is False and index["spend_authorized"] is False,
        "index grants authority",
    )
    files = index["files"]
    expected = {f"{PACKAGE}/{name}" for name in NAMES} | RELATED
    require(len(files) == len(expected), "artifact count mismatch")
    require({row["path"] for row in files} == expected, "artifact membership mismatch")
    require(digest(canonical(files)) == index["content_sha256"], "index digest mismatch")
    documents = {}
    observed_hashes = {}
    total = 0
    for row in files:
        content = read(root, row["path"])
        require(
            type(row["bytes"]) is int and row["bytes"] == len(content), "artifact byte mismatch"
        )
        require(digest(content) == row["sha256"], "artifact hash mismatch")
        observed_hashes[row["path"]] = row["sha256"]
        total += len(content)
        require(total <= 32 * 1024 * 1024, "package exceeds size bound")
        if row["path"].startswith(PACKAGE + "/") and row["path"].endswith(".json"):
            documents[Path(row["path"]).name] = parse(content)
    require(
        digest(read(root, "INITIAL-EVALUATION-PLAN.md"))
        == "ab74f7c04ee2f0894cc95445edef618ce3227ef1d754e5d312af4d1d5ea03acd",
        "initial proposed plan changed",
    )
    pending = list(documents.values())
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            path = item.get("path")
            if isinstance(path, str) and path.startswith(PACKAGE + "/") and "sha256" in item:
                require(
                    item["sha256"] == observed_hashes.get(path), "cross-artifact reference mismatch"
                )
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    semantics(documents)
    return {
        "status": "consistent-frozen-source-package",
        "artifacts": len(files),
        "planned_units": 768,
        "execution_allowed": False,
        "phase_3b_execution_allowed": False,
        "content_sha256": index["content_sha256"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).absolute().parents[1])
    arguments = parser.parse_args()
    try:
        result = verify(arguments.root)
    except (FreezeError, OSError, KeyError, TypeError, RecursionError) as error:
        parser.exit(1, f"Package refused: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
