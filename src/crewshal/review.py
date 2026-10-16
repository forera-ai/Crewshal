"""Coordinate risk, independent review, human decisions, and fresh remediation."""

from pathlib import Path, PurePosixPath
import difflib
from typing import TYPE_CHECKING, Literal

from pydantic import Field, model_validator

from crewshal.candidate import FrozenCandidate, _root, _scan, freeze_candidate
from crewshal.claude import (
    RuntimeIdentity,
    RuntimeRequest,
    normalize_runtime,
    prepare_runtime_contract,
)
from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    Digest,
    Evidence,
    Identifier,
    Record,
    Run,
    Task,
    Usage,
    Waiver,
    cumulative_usage,
    record_digest,
)
from crewshal.integration import CodexCollection, _stored_task, scope_digest
from crewshal.model import Contract, ProjectModel, digest, model_digest
from crewshal.qualification_bundle import _json
from crewshal.runtime import ProcessObservation, RuntimeOutcome

if TYPE_CHECKING:
    from crewshal.durable import CoordinatorStore

Risk = Literal["low", "ordinary", "high"]
RISK_ORDER: tuple[Risk, ...] = ("low", "ordinary", "high")


def path_risk(paths: list[str]) -> Risk:
    """Use a conservative risk floor for the supported Python and TypeScript slice."""
    sensitive = {
        ".github",
        ".gitlab",
        "auth",
        "authentication",
        "authorization",
        "security",
        "migrations",
        "persistence",
        "contracts",
        "api",
        "infra",
        "infrastructure",
        "ci",
        "deploy",
        "dependencies",
        "durable",
        "storage",
        "database",
    }
    manifests = {
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "uv.lock",
        "requirements.txt",
        "requirements-dev.lock",
        "dockerfile",
        "compose.yaml",
    }
    result: Risk = "low"
    for name in paths:
        path = PurePosixPath(name.lower())
        tokens = {
            part for component in path.parts for part in component.replace("-", "_").split("_")
        }
        tokens.add(path.stem)
        if tokens & sensitive or path.name in manifests or path.suffix in {".sql", ".tf"}:
            return "high"
        if path.suffix not in {".md", ".rst", ".txt"}:
            result = "ordinary"
    return result


class WorkflowPlan(Record):
    run_id: Identifier
    binding: Binding
    allowed_paths: list[str]
    risk: Risk


class PlanningApproval(Approval):
    plan: Digest


class ReviewBaseline(Record):
    run_id: Identifier
    binding: Binding
    chunks: dict[str, list[Digest]]


def capture_baseline(
    store: "CoordinatorStore",
    run: Run,
    root: Path,
    initial: FrozenCandidate,
) -> None:
    """Keep initial bytes for the independent diff before the implementation starts."""
    if store.get("workflow", run.id, WorkflowPlan)[0] is None:
        return
    observed, contents = _scan(_root(root))
    if observed != initial:
        raise ValueError("initial candidate changed before baseline capture")
    chunks: dict[str, list[str]] = {}
    for name, data in contents.items():
        chunks[name] = []
        for offset in range(0, len(data), 65536):
            raw = data[offset : offset + 65536]
            fingerprint = digest(raw)
            store._artifact(fingerprint, raw)
            chunks[name].append(fingerprint)
    baseline = ReviewBaseline(id=run.id, run_id=run.id, binding=run.binding, chunks=chunks)
    store._put("review_baseline", baseline.id, baseline, 0)
    if _scan(_root(root))[0] != initial:
        raise ValueError("initial candidate changed during baseline capture")


def _review_diff(store: "CoordinatorStore", collection: CodexCollection, root: Path) -> str:
    baseline, _ = store.get("review_baseline", collection.run_id, ReviewBaseline)
    if baseline is None or baseline.binding != collection.launch_binding:
        raise ValueError("review requires the original captured baseline")
    observed, after = _scan(_root(root))
    if observed != collection.frozen:
        raise ValueError("frozen candidate changed before diff capture")
    before: dict[str, bytes] = {}
    expected_files = {f.path: f for f in collection.initial.files if f.kind == "file"}
    if set(baseline.chunks) != set(expected_files):
        raise ValueError("baseline file inventory changed")
    for name, chunks in baseline.chunks.items():
        for fingerprint in chunks:
            store._verify_artifact(fingerprint)
        raw = b"".join((store.directory / "artifacts" / chunk).read_bytes() for chunk in chunks)
        if len(raw) != expected_files[name].size or digest(raw) != expected_files[name].sha256:
            raise ValueError("baseline file content changed")
        before[name] = raw
    result = ""
    for name in sorted(before.keys() | after.keys()):
        old, new = before.get(name, b""), after.get(name, b"")
        if old == new:
            continue
        if b"\x00" in old or b"\x00" in new:
            result += f"Binary change {name}: {digest(old)} {digest(new)}\n"
        else:
            result += "".join(
                difflib.unified_diff(
                    old.decode("utf-8", errors="replace").splitlines(keepends=True),
                    new.decode("utf-8", errors="replace").splitlines(keepends=True),
                    fromfile=f"before/{name}",
                    tofile=f"after/{name}",
                )
            )
        if len(result.encode()) > 65536:
            raise ValueError("review diff exceeds the bounded request limit")
    return result


class ReviewReport(Contract):
    decision: Literal["approve", "request_changes"]
    findings: list[str] = Field(max_length=100)

    @model_validator(mode="after")
    def consistent(self) -> "ReviewReport":
        if any(not item.strip() or len(item) > 4096 for item in self.findings):
            raise ValueError("review findings must contain bounded text")
        if (self.decision == "approve") != (not self.findings):
            raise ValueError("review decision and findings disagree")
        return self


class ReviewRequest(Record):
    run_id: Identifier
    binding: Binding
    native: RuntimeRequest
    project: ProjectModel
    task: Task
    initial: FrozenCandidate
    frozen: FrozenCandidate
    changed_paths: list[str]
    diff: str = Field(max_length=65536)
    checks: list[Evidence]
    check_logs: dict[str, str]
    instruction: Literal[
        "Review the frozen candidate against the task and captured checks. Return ReviewReport JSON."
    ] = "Review the frozen candidate against the task and captured checks. Return ReviewReport JSON."
    execution_allowed: Literal[False] = False


class ReviewCapture(Record):
    run_id: Identifier
    binding: Binding
    request: Digest
    outcome: RuntimeOutcome
    report: ReviewReport | None
    stdout: Digest
    stderr: Digest
    execution_allowed: Literal[False] = False


class ReviewResolution(Approval):
    review: Digest
    action: Literal["accept_risk", "remediate", "stop"]


class Remediation(Record):
    run_id: Identifier
    binding: Binding
    resolution: Digest
    next_run_id: Identifier
    next_binding: Binding


def configure_workflow(store: "CoordinatorStore", plan: WorkflowPlan, token: str) -> None:
    """Record the task risk before implementation starts."""
    plan = WorkflowPlan.model_validate_json(plan.model_dump_json())
    with store.transaction():
        store._lease(plan.run_id, token)
        run, _ = store.get("run", plan.run_id, Run)
        task = _stored_task(store, plan.run_id)
        if (
            run is None
            or run.state != "ready"
            or run.binding != plan.binding
            or plan.binding.scope != scope_digest(plan.allowed_paths)
            or RISK_ORDER.index(plan.risk) < RISK_ORDER.index(path_risk(plan.allowed_paths))
            or (plan.risk != "low" and not (task.review_required and task.independent_provider))
            or (plan.risk != "low" and not task.checks)
            or any(a.run_id == run.id for a in store.records("attempt", Attempt))
        ):
            raise ValueError(
                "workflow requires current scope, risk, and required independent review"
            )
        store._put("workflow", run.id, plan, 0)


def approve_planning(store: "CoordinatorStore", approval: PlanningApproval) -> None:
    """Record an explicit human planning decision for the exact plan."""
    approval = PlanningApproval.model_validate_json(approval.model_dump_json())
    with store.transaction():
        plan, _ = store.get("workflow", approval.run_id, WorkflowPlan)
        run, _ = store.get("run", approval.run_id, Run)
        if (
            plan is None
            or run is None
            or run.state != "ready"
            or approval.binding != run.binding
            or approval.plan != record_digest(plan)
        ):
            raise ValueError("planning approval requires the current ready plan")
        store._put("planning", approval.id, approval, 0)


def check_planning(store: "CoordinatorStore", run: Run) -> None:
    plan, _ = store.get("workflow", run.id, WorkflowPlan)
    if plan is None:
        return
    if plan.binding != run.binding:
        raise ValueError("workflow plan binding changed")
    if plan.risk == "high" and not any(
        a.run_id == run.id and a.binding == run.binding and a.plan == record_digest(plan)
        for a in store.records("planning", PlanningApproval)
    ):
        raise ValueError("high risk requires explicit human planning approval")


def _collection(
    store: "CoordinatorStore",
    collection_id: str,
    current: Binding,
    candidate_root: Path,
) -> tuple[CodexCollection, Run]:
    collection, _ = store.get("collection", collection_id, CodexCollection)
    if collection is None or collection.frozen is None:
        raise ValueError("review requires a frozen implementation")
    run, _ = store.get("run", collection.run_id, Run)
    if (
        run is None
        or run.state not in {"frozen", "validating"}
        or run.binding != current
        or collection.binding != current
        or _scan(_root(candidate_root))[0] != collection.frozen
    ):
        raise ValueError("review requires the current unchanged frozen candidate")
    attempt, _ = store.get("attempt", collection.outcome.attempt.id, Attempt)
    if attempt != Attempt.model_validate(
        {
            **collection.outcome.attempt.model_dump(),
            "binding": current.model_dump(),
        }
    ):
        raise ValueError("implementation capture changed")
    for fingerprint in (collection.stdout, collection.stderr, record_digest(collection)):
        store._verify_artifact(fingerprint)
    return collection, run


def prepare_review(
    store: "CoordinatorStore",
    *,
    collection_id: str,
    current: Binding,
    project_id: str,
    attempt: Attempt,
    identity: RuntimeIdentity,
    expected_configuration: str,
    candidate_root: Path,
    reviewer_root: Path,
    token: str,
) -> ReviewRequest:
    """Copy current source and checks into a fresh review view, then commit one intent.

    The request excludes implementation claims and conversation.
    The external reviewer must receive a qualified read-only view during operational use.
    This function starts no process and grants no execution authority.
    """
    with store.transaction():
        collection, run = _collection(store, collection_id, current, candidate_root)
        store._lease(run.id, token)
        task = _stored_task(store, run.id)
        model, _ = store.get("project", project_id, ProjectModel)
        if model is None or model_digest(model) != current.model or model.unresolved:
            raise ValueError("review requires the same confirmed project model")
        native = prepare_runtime_contract(task, attempt, current, identity, role="review")
        if attempt.run_id != run.id or identity.configuration != expected_configuration:
            raise ValueError("review identity or configuration differs")
        implementations = [a for a in store.records("attempt", Attempt) if a.run_id == run.id]
        if any(a.role == "review" for a in implementations):
            raise ValueError("review already attempted; automatic retry is disabled")
        if task.independent_provider and (
            not identity.provider
            or not identity.model
            or any(
                not a.provider or not a.model or a.provider == identity.provider
                for a in implementations
            )
        ):
            raise ValueError("independent resolved provider identity is unavailable")
        if not any(
            a.run_id == run.id and a.binding == current for a in store.records("approval", Approval)
        ):
            raise ValueError("current owner approval required before review")
        resolved = reviewer_root.resolve()
        if resolved.is_relative_to(store.directory) or store.directory.is_relative_to(resolved):
            raise ValueError("review view must exclude coordinator state")
        checks = [
            e
            for e in store.records("evidence", Evidence)
            if e.run_id == run.id and e.kind == "check"
        ]
        if len(checks) != len(task.checks) or any(
            sum(e.definition == check for e in checks) != 1 for check in task.checks
        ):
            raise ValueError("review requires all approved required check captures")
        diff = _review_diff(store, collection, candidate_root)
        logs: dict[str, str] = {}
        for check in checks:
            if check.binding != current:
                raise ValueError("review cannot use stale checks")
            for fingerprint in (check.stdout, check.stderr, *check.artifacts):
                if fingerprint is not None:
                    store._verify_artifact(fingerprint)
                    logs[fingerprint] = (
                        (store.directory / "artifacts" / fingerprint)
                        .read_bytes()
                        .decode("utf-8", errors="replace")
                    )
        assert collection.frozen is not None
        frozen = freeze_candidate(candidate_root, reviewer_root, tree_stopped=True)
        if frozen != collection.frozen:
            raise ValueError("review copy changed")
        before = {f.path: f for f in collection.initial.files}
        after = {f.path: f for f in frozen.files}
        request = ReviewRequest(
            id=attempt.id,
            run_id=run.id,
            binding=current,
            native=native,
            project=model,
            task=task,
            initial=collection.initial,
            frozen=frozen,
            changed_paths=sorted(
                p for p in before.keys() | after.keys() if before.get(p) != after.get(p)
            ),
            checks=checks,
            check_logs=logs,
            diff=diff,
        )
        store._artifact(record_digest(request), request.model_dump_json().encode())
        store._put("review_request", request.id, request, 0)
        store._put("attempt", attempt.id, attempt, 0)
        return request


def collect_review(
    store: "CoordinatorStore",
    *,
    request_id: str,
    current: Binding,
    expected_configuration: str,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
    candidate_root: Path,
    reviewer_root: Path,
    expected_attempt_version: int,
    token: str,
) -> ReviewCapture:
    """Capture one reviewer judgment without accepting its claims as check evidence."""
    with store.transaction():
        request, _ = store.get("review_request", request_id, ReviewRequest)
        if request is None or request.binding != current:
            raise ValueError("current review request required")
        store._lease(request.run_id, token)
        run, _ = store.get("run", request.run_id, Run)
        attempt, version = store.get("attempt", request_id, Attempt)
        if (
            run is None
            or run.binding != current
            or run.state not in {"frozen", "validating"}
            or attempt is None
            or attempt.binding != current
            or attempt.state != "acknowledged"
            or type(expected_attempt_version) is not int
            or version != expected_attempt_version
            or _scan(_root(candidate_root))[0] != request.frozen
            or _scan(_root(reviewer_root))[0] != request.frozen
            or expected_configuration != request.native.identity.configuration
        ):
            raise ValueError("review state, configuration, or frozen candidate changed")
        store._verify_artifact(record_digest(request))
        outcome = normalize_runtime(
            attempt,
            current,
            request.native.identity,
            observation,
            stdout,
            stderr,
            expected_configuration=expected_configuration,
            role="review",
        )
        report = None
        if outcome.status == "completed":
            try:
                report = ReviewReport.model_validate(_json(outcome.claims[-1].report.encode()))
            except (ValueError, IndexError, UnicodeError, RecursionError):
                outcome = RuntimeOutcome.model_validate(
                    {
                        **outcome.model_dump(),
                        "status": "malformed",
                        "attempt": {
                            **outcome.attempt.model_dump(),
                            "state": "failed",
                            "runtime_result": "failed",
                        },
                    }
                )
        capture = ReviewCapture(
            id=request_id,
            run_id=run.id,
            binding=current,
            request=record_digest(request),
            outcome=outcome,
            report=report,
            stdout=digest(stdout),
            stderr=digest(stderr),
        )
        status = "passed" if report is not None and report.decision == "approve" else "failed"
        termination: str | None = observation.termination
        if outcome.status != "completed":
            if outcome.status in {"timeout", "cancelled", "quota", "signal", "interrupted"}:
                termination = outcome.status
                status = "terminated"
            else:
                status = "failed" if outcome.status == "failed" else "unavailable"
        evidence = Evidence.model_validate(
            {
                "id": f"review:{request_id}",
                "run_id": run.id,
                "attempt_id": attempt.id,
                "binding": current.model_dump(),
                "kind": "review",
                "gate": "review",
                "status": status,
                "provider": attempt.provider,
                "model": attempt.model,
                "started": observation.started,
                "ended": observation.ended,
                "termination": termination if termination != "refusal" else None,
                "stdout": capture.stdout,
                "stderr": capture.stderr,
                "artifacts": [record_digest(request), record_digest(capture)],
                "blocking_findings": report.findings if report is not None else [],
            }
        )
        for fingerprint, raw in (
            (capture.stdout, stdout),
            (capture.stderr, stderr),
            (record_digest(capture), capture.model_dump_json().encode()),
        ):
            store._artifact(fingerprint, raw)
        store._put("attempt", attempt.id, outcome.attempt, version)
        store._put("review_capture", capture.id, capture, 0)
        store._put("evidence", evidence.id, evidence, 0)
        for claim in outcome.claims:
            store._put("claim", claim.id, claim, 0)
        if outcome.usage is not None:
            cumulative_usage(
                [a.id for a in store.records("attempt", Attempt)],
                [*store.records("usage", Usage), outcome.usage],
            )
            store._put("usage", outcome.usage.id, outcome.usage, 0)
        if (
            _scan(_root(candidate_root))[0] != request.frozen
            or _scan(_root(reviewer_root))[0] != request.frozen
        ):
            raise ValueError("candidate changed during review capture")
        return capture


def resolve_review(store: "CoordinatorStore", resolution: ReviewResolution, token: str) -> None:
    """Keep the review disagreement and the human decision as separate records."""
    resolution = ReviewResolution.model_validate_json(resolution.model_dump_json())
    with store.transaction():
        store._lease(resolution.run_id, token)
        run, _ = store.get("run", resolution.run_id, Run)
        captures = [
            r
            for r in store.records("review_capture", ReviewCapture)
            if r.run_id == resolution.run_id
        ]
        if (
            run is None
            or run.binding != resolution.binding
            or len(captures) != 1
            or record_digest(captures[0]) != resolution.review
            or captures[0].report is None
            or captures[0].report.decision != "request_changes"
            or any(r.run_id == run.id for r in store.records("review_resolution", ReviewResolution))
        ):
            raise ValueError("resolution requires one current unresolved review disagreement")
        store._put("review_resolution", resolution.id, resolution, 0)
        if resolution.action == "accept_risk":
            waiver = Waiver(
                id=f"review-resolution:{resolution.id}",
                run_id=run.id,
                binding=run.binding,
                gate="review",
                owner=resolution.owner,
                residual_risk=resolution.reason,
            )
            store._put("waiver", waiver.id, waiver, 0)
        elif resolution.action == "stop":
            _, version = store.get("run", run.id, Run)
            store._put(
                "run",
                run.id,
                Run.model_validate(
                    {
                        **run.model_dump(),
                        "state": "interrupted",
                    }
                ),
                version,
            )
            store.connection.execute("DELETE FROM lease")


def workflow_gates(store: "CoordinatorStore", run: Run, current: Binding) -> dict[str, str]:
    """Add risk and conflict gates that a generic completion waiver cannot remove."""
    gates: dict[str, str] = {}
    plan, _ = store.get("workflow", run.id, WorkflowPlan)
    if plan is not None:
        collections = [
            c for c in store.records("collection", CodexCollection) if c.run_id == run.id
        ]
        if len(collections) != 1 or collections[0].launch_binding != plan.binding:
            gates["workflow"] = "plan_binding_changed"
        else:
            collection = collections[0]
            before = {f.path: f for f in collection.initial.files}
            after = {f.path: f for f in collection.frozen.files} if collection.frozen else {}
            changed = [p for p in before.keys() | after.keys() if before.get(p) != after.get(p)]
            if RISK_ORDER.index(path_risk(changed)) > RISK_ORDER.index(plan.risk):
                gates["risk"] = "escalated_replan_required"
        if plan.risk == "high" and not any(
            a.run_id == run.id and a.binding == plan.binding and a.plan == record_digest(plan)
            for a in store.records("planning", PlanningApproval)
        ):
            gates["planning"] = "missing"
    captures = [c for c in store.records("review_capture", ReviewCapture) if c.run_id == run.id]
    task = _stored_task(store, run.id)
    if plan is not None and task.review_required and len(captures) != 1:
        gates["review_availability"] = "missing"
    for capture in captures:
        store._verify_artifact(record_digest(capture))
        request, _ = store.get("review_request", capture.id, ReviewRequest)
        if (
            request is None
            or capture.request != record_digest(request)
            or capture.binding != current
        ):
            gates["review_integrity"] = "stale"
            continue
        store._verify_artifact(record_digest(request))
        checks = [
            e
            for e in store.records("evidence", Evidence)
            if e.run_id == run.id and e.kind == "check"
        ]
        if request.checks != checks:
            gates["review_integrity"] = "check_snapshot_changed"
        task = _stored_task(store, run.id)
        implementations = [
            a
            for a in store.records("attempt", Attempt)
            if a.run_id == run.id and a.role == "implementation"
        ]
        if task.independent_provider and any(
            not a.provider or a.provider == request.native.identity.provider
            for a in implementations
        ):
            gates["review_integrity"] = "not_independent"
        if capture.report is None:
            gates["review_capture"] = "unavailable"
        elif capture.report.decision == "request_changes":
            resolutions = [
                r
                for r in store.records("review_resolution", ReviewResolution)
                if r.run_id == run.id
                and r.binding == current
                and r.review == record_digest(capture)
            ]
            if len(resolutions) != 1 or resolutions[0].action != "accept_risk":
                gates["review_conflict"] = "human_decision_required"
    return gates


def start_remediation(
    store: "CoordinatorStore",
    *,
    resolution_id: str,
    project_id: str,
    next_run_id: str,
    task: Task,
    candidate_root: Path,
    target: Path,
    token: str,
) -> Run:
    """Create a separate candidate and run after an explicit human remediation decision."""
    with store.transaction():
        resolution, _ = store.get("review_resolution", resolution_id, ReviewResolution)
        if resolution is None or resolution.action != "remediate":
            raise ValueError("explicit human remediation decision required")
        store._lease(resolution.run_id, token)
        collections = [
            c for c in store.records("collection", CodexCollection) if c.run_id == resolution.run_id
        ]
        if len(collections) != 1:
            raise ValueError("one original collection required")
        collection, previous = _collection(
            store, collections[0].id, resolution.binding, candidate_root
        )
        model, _ = store.get("project", project_id, ProjectModel)
        previous_task = _stored_task(store, previous.id)
        plan, _ = store.get("workflow", previous.id, WorkflowPlan)
        if (
            model is None
            or model_digest(model) != previous.binding.model
            or plan is None
            or next_run_id == previous.id
            or task.id == previous.task_id
            or (previous_task.review_required and not task.review_required)
            or (previous_task.independent_provider and not task.independent_provider)
            or any(check not in task.checks for check in previous_task.checks)
            or (plan.risk != "low" and not (task.review_required and task.independent_provider))
            or any(
                r.resolution == record_digest(resolution)
                for r in store.records("remediation", Remediation)
            )
        ):
            raise ValueError("remediation requires a fresh task and current confirmed model")
        scopes = [
            e
            for e in store.records("evidence", Evidence)
            if e.run_id == previous.id and e.kind == "scope"
        ]
        if len(scopes) != 1 or scopes[0].status != "passed":
            raise ValueError("scope escalation requires a new approved plan")
        resolved = target.resolve()
        if resolved.is_relative_to(store.directory) or store.directory.is_relative_to(resolved):
            raise ValueError("remediation candidate must exclude coordinator state")
        initial = freeze_candidate(candidate_root, target, tree_stopped=True)
        if initial != collection.frozen:
            raise ValueError("remediation copy differs")
        binding = Binding.model_validate(
            {**previous.binding.model_dump(), "task": record_digest(task)}
        )
        run = Run(id=next_run_id, task_id=task.id, binding=binding)
        store._put("task", task.id, task, 0)
        store._put("run", run.id, run, 0)
        new_plan = WorkflowPlan(
            id=run.id,
            run_id=run.id,
            binding=binding,
            allowed_paths=plan.allowed_paths,
            risk=plan.risk,
        )
        store._put("workflow", run.id, new_plan, 0)
        record = Remediation(
            id=resolution.id,
            run_id=previous.id,
            binding=previous.binding,
            resolution=record_digest(resolution),
            next_run_id=run.id,
            next_binding=binding,
        )
        store._put("remediation", record.id, record, 0)
        _, version = store.get("run", previous.id, Run)
        store._put(
            "run",
            previous.id,
            Run.model_validate({**previous.model_dump(), "state": "interrupted"}),
            version,
        )
        store.connection.execute("UPDATE lease SET run_id=? WHERE run_id=?", (run.id, previous.id))
        return run
