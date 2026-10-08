"""Pure verdict rules over a coordinator-owned snapshot, never worker exports."""

from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    CheckDefinition,
    Evidence,
    Run,
    Task,
    Verdict,
    Waiver,
)
from crewshal.contracts import record_digest


def evaluate(
    run: Run,
    task: Task,
    current: Binding,
    approvals: list[Approval],
    attempts: list[Attempt],
    evidence: list[Evidence],
    waivers: list[Waiver],
) -> Verdict:
    """Caller must supply trusted records; the durable store resolves all IDs itself."""
    gates: dict[str, str] = {}
    if run.binding != current or current.task != record_digest(task) or run.task_id != task.id:
        gates["binding"] = "stale"
    if not any(a.run_id == run.id and a.binding == current for a in approvals):
        gates["approval"] = "missing"
    if run.state not in {"frozen", "validating", "verdict"}:
        gates["candidate"] = "not_frozen"
    by_attempt = {a.id: a for a in attempts if a.run_id == run.id and a.binding == current}
    implementations = [a for a in by_attempt.values() if a.role == "implementation"]
    complete = [
        a
        for a in implementations
        if a.state == "completed" and a.process_exit == 0 and a.runtime_result == "completed"
    ]
    # Conservative: failed or uncertain attempts cannot be hidden by a later success.
    if not complete or len(complete) != len(implementations):
        gates["implementation"] = "incomplete"
    valid: list[Evidence] = []
    for item in evidence:
        attempt = by_attempt.get(item.attempt_id)
        if item.run_id != run.id or item.binding != current or attempt is None:
            gates["evidence_integrity"] = "stale_or_unbound"
            continue
        if (
            attempt.state != "completed"
            or attempt.process_exit != 0
            or attempt.runtime_result != "completed"
        ):
            gates["evidence_integrity"] = "incomplete_attempt"
            continue
        if item.kind == "review" and (
            attempt.role != "review"
            or item.provider != attempt.provider
            or item.model != attempt.model
        ):
            gates["evidence_integrity"] = "review_identity_mismatch"
            continue
        if item.kind != "review" and attempt.role != "implementation":
            gates["evidence_integrity"] = "role_mismatch"
            continue
        valid.append(item)

    required: dict[str, CheckDefinition | None] = {
        f"check:{check.id}": check for check in task.checks
    }
    required["scope"] = None
    if task.review_required:
        required["review"] = None
    for name, definition in required.items():
        matches = [item for item in valid if item.gate == name]
        expected_kind = "check" if name.startswith("check:") else name
        if not matches:
            gates[name] = "missing"
        elif len(matches) != 1:
            gates[name] = "contradictory"
        else:
            item = matches[0]
            if item.kind != expected_kind or (
                definition is not None and item.definition != definition
            ):
                gates[name] = "definition_mismatch"
            else:
                gates[name] = item.status
                if item.blocking_findings:
                    gates[name] = "blocking_findings"
                if name == "review" and task.independent_provider:
                    identities = [a.provider for a in implementations]
                    if (
                        not item.provider
                        or not item.model
                        or any(not a.provider or not a.model for a in implementations)
                    ):
                        gates[name] = "identity_unavailable"
                    elif item.provider in identities:
                        gates[name] = "not_independent"

    failures = {name for name, status in gates.items() if status != "passed"}
    applied: list[str] = []
    # Integrity, approval, scope and lifecycle cannot be waived by a completion waiver.
    for name in sorted(failures & (set(required) - {"scope"})):
        matching = [
            w for w in waivers if w.run_id == run.id and w.binding == current and w.gate == name
        ]
        if len(matching) == 1:
            applied.append(matching[0].id)
            failures.remove(name)
    status = "blocked"
    if not failures:
        status = "accepted_with_waiver" if applied else "verified"
    elif any(a.state == "cancelled" for a in implementations):
        status = "cancelled"
    elif run.state == "interrupted" or any(a.state == "interrupted" for a in implementations):
        status = "interrupted"
    elif any(value in {"failed", "terminated"} for value in gates.values()):
        status = "failed"
    return Verdict.model_validate(
        {
            "id": f"verdict:{run.id}",
            "run_id": run.id,
            "binding": current.model_dump(),
            "status": status,
            "gates": gates,
            "evidence_ids": [item.id for item in valid],
            "waiver_ids": applied,
        }
    )
