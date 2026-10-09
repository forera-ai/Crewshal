"""Trusted offline collection into durable state; no runtime or validator launch.

The future qualified supervisor supplies observations through this coordinator-only
seam. Native output never supplies authority, process observations or check evidence.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self

from pydantic import model_validator

from crewshal.candidate import FrozenCandidate, _paths, freeze_candidate, scope_evidence
from crewshal.contracts import (
    Attempt,
    Binding,
    Digest,
    Evidence,
    Identifier,
    Record,
    Run,
    Task,
    Usage,
    cumulative_usage,
    record_digest,
)
from crewshal.model import digest
from crewshal.runtime import (
    STREAM_BYTES,
    CodexIdentity,
    ProcessObservation,
    RuntimeOutcome,
    normalize_codex,
)

if TYPE_CHECKING:
    from crewshal.durable import CoordinatorStore


def scope_digest(allowed_paths: list[str]) -> str:
    """Digest an explicit exact-path scope, independently retained before launch."""
    _paths(allowed_paths)
    return digest(
        json.dumps(
            {"schema_version": 1, "allowed_paths": sorted(allowed_paths)}, sort_keys=True
        ).encode()
    )


class CodexCollection(Record):
    """Private capture receipt preserving launch and resulting candidate bindings."""

    run_id: Identifier
    launch_binding: Binding
    binding: Binding
    initial: FrozenCandidate
    frozen: FrozenCandidate | None
    allowed_paths: list[str]
    identity: CodexIdentity
    expected_configuration: Digest
    observation: ProcessObservation
    outcome: RuntimeOutcome
    stdout: Digest
    stderr: Digest
    execution_allowed: Literal[False] = False

    @model_validator(mode="after")
    def continuity(self) -> Self:
        if (
            self.launch_binding.candidate != record_digest(self.initial)
            or self.launch_binding.scope != scope_digest(self.allowed_paths)
            or self.outcome.attempt.run_id != self.run_id
            or self.outcome.attempt.binding != self.launch_binding
        ):
            raise ValueError("collection does not bind launch snapshot, scope or attempt")
        expected = self.launch_binding.model_dump()
        if self.frozen is None:
            if self.outcome.status == "completed":
                raise ValueError("completed collection requires a frozen candidate")
        else:
            if self.outcome.status != "completed" or not self.observation.tree_stopped:
                raise ValueError("only a completely captured stopped worker can freeze")
            expected["candidate"] = record_digest(self.frozen)
        if self.binding != Binding.model_validate(expected):
            raise ValueError("collection may change only candidate binding")
        return self


def collect_codex_attempt(
    store: "CoordinatorStore",
    *,
    attempt_id: str,
    current: Binding,
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: FrozenCandidate,
    candidate: Path,
    frozen_target: Path,
    allowed_paths: list[str],
    identity: CodexIdentity,
    expected_configuration: str,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
) -> CodexCollection:
    """Collect terminal capture in one coordinator-owned transaction."""
    with store.transaction():
        return _collect_codex_attempt_locked(
            store,
            attempt_id=attempt_id,
            current=current,
            expected_run_version=expected_run_version,
            expected_attempt_version=expected_attempt_version,
            token=token,
            initial=initial,
            candidate=candidate,
            frozen_target=frozen_target,
            allowed_paths=allowed_paths,
            identity=identity,
            expected_configuration=expected_configuration,
            observation=observation,
            stdout=stdout,
            stderr=stderr,
        )


def _collect_codex_attempt_locked(
    store: "CoordinatorStore",
    *,
    attempt_id: str,
    current: Binding,
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: FrozenCandidate,
    candidate: Path,
    frozen_target: Path,
    allowed_paths: list[str],
    identity: CodexIdentity,
    expected_configuration: str,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
) -> CodexCollection:
    """Collect one acknowledged implementation without granting execution authority.

    This is a privileged package operation using the store's transaction primitives,
    not a worker import endpoint. Successful collection atomically persists terminal
    state, claims, usage, receipt and scope evidence, and rebinds run/attempt to the
    frozen manifest. Existing approvals stay at their original binding. Failures
    retain bounded logs and interrupt the run without freezing or retrying.

    Filesystem copies/artifacts are not transactional. A failed copy or SQL commit
    leaves owned artifacts for inspection; it never deletes paths or replays launch.
    Stable coordinator-owned directories and a trusted host are required.
    """
    if not store.connection.in_transaction:
        raise ValueError("collection requires an owned coordinator transaction")
    from crewshal.durable import Conflict

    current = Binding.model_validate_json(current.model_dump_json())
    initial = FrozenCandidate.model_validate_json(initial.model_dump_json())
    identity = CodexIdentity.model_validate_json(identity.model_dump_json())
    observation = ProcessObservation.model_validate_json(observation.model_dump_json())
    allowed_paths = list(allowed_paths)
    if current.candidate != record_digest(initial) or current.scope != scope_digest(allowed_paths):
        raise ValueError("initial snapshot or allowed scope differs from launch binding")
    if len(stdout) > STREAM_BYTES or len(stderr) > STREAM_BYTES:
        raise ValueError("collection requires bounded streams; reconcile overflow separately")
    if any(
        type(version) is not int or version < 1
        for version in (
            expected_run_version,
            expected_attempt_version,
        )
    ):
        raise Conflict("positive exact state versions required")
    for path in (candidate, frozen_target):
        resolved = path.resolve()
        if resolved.is_relative_to(store.directory) or store.directory.is_relative_to(resolved):
            raise ValueError("candidate and frozen target must exclude coordinator state")

    attempt, attempt_version = store.get("attempt", attempt_id, Attempt)
    if attempt is None:
        raise ValueError("collection requires a known attempt")
    store._lease(attempt.run_id, token)
    run, run_version = store.get("run", attempt.run_id, Run)
    if run is None:
        raise ValueError("collection requires a known run")
    if run_version != expected_run_version or attempt_version != expected_attempt_version:
        raise Conflict("collection state version changed")
    if (
        run.state != "ready"
        or attempt.state != "acknowledged"
        or attempt.role != "implementation"
        or not attempt.handle
        or run.binding != current
        or attempt.binding != current
    ):
        raise ValueError("collection requires current acknowledged implementation and ready run")
    task, _ = store.get("task", run.task_id, Task)
    if task is None or record_digest(task) != current.task:
        raise ValueError("collection task binding is stale")
    attempts = [item for item in store.records("attempt", Attempt) if item.run_id == run.id]
    if len(attempts) != 1 or attempts[0].id != attempt_id:
        raise ValueError("one implementation attempt only; no hidden retry or review rebind")
    if any(item.run_id == run.id for item in store.records("collection", CodexCollection)):
        raise ValueError("attempt collection cannot replay")
    # No previously captured evidence may be silently rebound to a new candidate.
    if any(item.run_id == run.id for item in store.records("evidence", Evidence)):
        raise ValueError("existing evidence cannot transfer to a new candidate")
    outcome = normalize_codex(
        attempt,
        current,
        identity,
        observation,
        stdout,
        stderr,
        expected_configuration=expected_configuration,
    )
    frozen = None
    binding = current
    if outcome.status == "completed":
        frozen = freeze_candidate(candidate, frozen_target, tree_stopped=observation.tree_stopped)
        binding = Binding.model_validate(
            {**current.model_dump(), "candidate": record_digest(frozen)}
        )
    collection = CodexCollection(
        id=f"collection:{digest(attempt.id.encode())}",
        run_id=run.id,
        launch_binding=current,
        binding=binding,
        initial=initial,
        frozen=frozen,
        allowed_paths=allowed_paths,
        identity=identity,
        expected_configuration=expected_configuration,
        observation=observation,
        outcome=outcome,
        stdout=digest(stdout),
        stderr=digest(stderr),
    )
    artifacts = {collection.stdout: stdout, collection.stderr: stderr}
    receipt = collection.model_dump_json().encode()
    artifacts[record_digest(collection)] = receipt
    scope = None
    if frozen is not None:
        scope, raw = scope_evidence(
            initial,
            frozen,
            binding,
            allowed_paths,
            evidence_id=f"scope:{digest(attempt.id.encode())}",
            run_id=run.id,
            attempt_id=attempt.id,
            observation=observation,
        )
        artifacts[digest(raw)] = raw
        artifacts[digest(b"")] = b""
        scope = Evidence.model_validate(
            {
                **scope.model_dump(),
                "artifacts": sorted(
                    {collection.stdout, collection.stderr, record_digest(collection)}
                ),
            }
        )
    for fingerprint, data in artifacts.items():
        store._artifact(fingerprint, data)
    terminal = Attempt.model_validate(
        {**outcome.attempt.model_dump(), "binding": binding.model_dump()}
    )
    store._put("attempt", attempt.id, terminal, attempt_version)
    store._put("collection", collection.id, collection, 0)
    for claim in outcome.claims:
        store._put("claim", claim.id, claim, 0)
    if outcome.usage is not None:
        existing = store.records("usage", Usage)
        cumulative_usage(
            [item.id for item in store.records("attempt", Attempt)], [*existing, outcome.usage]
        )
        store._put("usage", outcome.usage.id, outcome.usage, 0)
    if scope is not None:
        store._put("evidence", scope.id, scope, 0)
    state = "frozen" if frozen is not None else "interrupted"
    updated_run = Run.model_validate(
        {**run.model_dump(), "binding": binding.model_dump(), "state": state}
    )
    store._put("run", run.id, updated_run, run_version)
    if frozen is None:
        store.connection.execute("DELETE FROM lease")
    return collection
