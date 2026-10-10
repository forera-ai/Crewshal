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
    from crewshal.dispatch import CodexDispatch
    from crewshal.linux_freeze import OriginalVolumeFreeze
    from crewshal.linux_bridge import StoppedNativeBridge


# The host bridge retains actual native proc/pidfd custody, but has not received
# the original namespace parent's NativeAdmissionReceipt. No host packet can
# manufacture that receipt or complete installed admission qualification.
ORIGINAL_VOLUME_COLLECTION_UNRESOLVED = ("original_namespace_admission_receipt_transport",)


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
    frozen_owner: "OriginalVolumeFreeze | None" = None,
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
    if frozen_owner is None:
        for path in (candidate, frozen_target):
            resolved = path.resolve()
            if resolved.is_relative_to(store.directory) or store.directory.is_relative_to(resolved):
                raise ValueError("candidate and frozen target must exclude coordinator state")
    else:
        from crewshal.linux_freeze import OriginalVolumeFreeze

        if (
            type(frozen_owner) is not OriginalVolumeFreeze
            or frozen_owner.installation.growth.store is not store
            or getattr(frozen_owner.installation, "_freeze", None) is not frozen_owner
            or str(candidate) != frozen_owner.installation.production.root + "/candidate-upper"
            or str(frozen_target) != frozen_owner.installation.production.root + "/validator-frozen"
        ):
            raise ValueError("collection requires original observer/store/volume custody")
        frozen_owner.verify_projection()

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
        if frozen_owner is None:
            frozen = freeze_candidate(
                candidate, frozen_target, tree_stopped=observation.tree_stopped
            )
        else:
            # The original observer's retained actual readonly projection owns
            # this copy. A path, tree_stopped flag or parsed manifest cannot
            # substitute for its repeated kernel/task/inode/content readback.
            frozen_owner.verify_projection()
            frozen = frozen_owner.manifest
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


def collect_original_volume_codex(
    store: "CoordinatorStore",
    bridge: "StoppedNativeBridge",
    dispatch: "CodexDispatch",
    *,
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: FrozenCandidate,
    allowed_paths: list[str],
) -> CodexCollection:
    """Persist original parent capture only in its retaining outer observer.

    This source supplies no namespace entry, launch or authority. The fixed
    bridge independently retains actual host proc/pidfd/stdio identities before
    payload release, and terminal capture before the original volume is frozen.
    The child cannot receive, copy, reopen or replace the original SQLite store.
    """
    from crewshal.dispatch import CodexDispatch, prepare_dispatch_configuration
    from crewshal.durable import Conflict, CoordinatorStore
    from crewshal.linux_bridge import StoppedNativeBridge
    from crewshal.linux_freeze import OriginalVolumeFreeze
    from crewshal.supervisor import SupervisionReceipt

    if type(bridge) is not StoppedNativeBridge or getattr(bridge, "_collection_attempted", False):
        raise ValueError("original observer collection unavailable or consumed")
    setattr(bridge, "_collection_attempted", True)
    try:
        if (
            type(store) is not CoordinatorStore
            or bridge.installation.growth.store is not store
            or getattr(bridge.installation, "_bridge", None) is not bridge
        ):
            raise ValueError("original observer store/bridge custody differs")
        bridge.verify_capture()
        dispatch = CodexDispatch.model_validate_json(dispatch.model_dump_json())
        request, configuration = dispatch.request, dispatch.configuration
        subscription = configuration.native_interface == "app_server_stdio"
        if configuration.task_digest is None or configuration.launch_binding is None:
            raise ValueError("unbound dispatch configuration")
        captured = getattr(bridge, "native_capture", None)
        frozen = getattr(bridge, "freeze", None)
        if (
            bridge.failed
            or bridge.stage != 3
            or captured is None
            or type(frozen) is not OriginalVolumeFreeze
            or frozen.installation is not bridge.installation
            or dispatch.configuration != bridge.lifetime.controls.configuration
            or record_digest(dispatch.configuration) != bridge.native.spec.configuration
            or type(bridge.native.spec.pid) is not int
            or bridge.native.spec.pid <= 0
            or captured.initial.identity != bridge.lifetime.worker.identity
            or captured.final is None
            or captured.final.identity != bridge.lifetime.worker.identity
        ):
            raise ValueError("original captured native/dispatch/volume binding differs")
        frozen.verify_projection()
        with store.transaction():
            attempt, attempt_version = store.get("attempt", request.attempt_id, Attempt)
            if attempt is None:
                raise ValueError("known acknowledged attempt required")
            store._lease(attempt.run_id, token)
            run, run_version = store.get("run", attempt.run_id, Run)
            if (run_version, attempt_version) != (expected_run_version, expected_attempt_version):
                raise Conflict("original observer collection state version changed")
            if (
                run is None
                or run.state != "ready"
                or attempt.state != "acknowledged"
                or not attempt.handle
                or attempt.binding != request.binding
                or run.binding != request.binding
                or attempt.role != "implementation"
                or attempt.provider != request.identity.provider
                or attempt.model != request.identity.model
            ):
                raise ValueError("original observer launch/attempt binding differs")
            task, _ = store.get("task", run.task_id, Task)
            if (
                task is None
                or configuration
                != prepare_dispatch_configuration(
                    configuration.selection,
                    preparation_digest=configuration.preparation_digest,
                    task=task,
                    binding=request.binding,
                    linux_envelope=configuration.linux_envelope,
                    app_server_profile=configuration.app_server_profile,
                )
                or request.identity.configuration != record_digest(configuration)
                or dispatch.qualification.configuration != request.identity.configuration
                or dispatch.task_digest != record_digest(task)
                or request.requirement != task.requirement
                or (not subscription and request.requirement + "\n" != configuration.native_stdin)
                or (
                    subscription
                    and (
                        configuration.app_server_profile is None
                        or request.requirement != configuration.app_server_profile.requirement
                    )
                )
                or request.identity.native_interface != configuration.native_interface
                or request.identity.app_server_profile != configuration.app_server_profile
                or configuration.selection.provider != request.identity.provider
                or configuration.selection.model != request.identity.model
                or configuration.selection.destination is None
                or configuration.selection.billing_mode == "unresolved"
                or configuration.selection.credential_treatment
                != ("native_managed_private_home" if subscription else "external_scoped_channel")
                or dispatch.qualification.host_os != "linux"
                or dispatch.qualification.architecture != "aarch64"
                or dispatch.qualification.runtime != "codex-rust-v0.160.1"
                or len(task.checks) != 1
                or task.checks[0].argv != configuration.validator_argv
                or task.checks[0].cwd != "."
                or task.review_required
                or task.independent_provider
            ):
                raise ValueError("original observer source/task/configuration changed")
            if (
                request.binding.candidate != record_digest(initial)
                or request.binding.scope != scope_digest(allowed_paths)
                or allowed_paths != ["README.md"]
            ):
                raise ValueError("original observer snapshot/scope differs")
            bridge.verify_capture()
            collection = _collect_codex_attempt_locked(
                store,
                attempt_id=dispatch.request.attempt_id,
                current=dispatch.request.binding,
                expected_run_version=expected_run_version,
                expected_attempt_version=expected_attempt_version,
                token=token,
                initial=initial,
                candidate=Path(bridge.installation.production.root + "/candidate-upper"),
                frozen_target=Path(bridge.installation.production.root + "/validator-frozen"),
                allowed_paths=allowed_paths,
                identity=dispatch.request.identity,
                expected_configuration=record_digest(dispatch.configuration),
                observation=captured.observation,
                stdout=captured.stdout,
                stderr=captured.stderr,
                frozen_owner=frozen,
            )
            bridge.verify_capture()
            receipt = SupervisionReceipt(
                id=f"supervision:{digest(attempt.id.encode())}",
                run_id=run.id,
                attempt_id=attempt.id,
                handle=attempt.handle,
                pid=bridge.native.spec.pid,
                dispatch=record_digest(dispatch),
                collection=record_digest(collection),
                # Missing original namespace receipt remains explicit. Actual
                # host custody cannot substitute for its admission identity.
                admission=None,
                initial=captured.initial,
                final=captured.final,
                observation=captured.observation,
                stdout=collection.stdout,
                stderr=collection.stderr,
                overflow=captured.overflow,
                stop_error=captured.stop_error,
            )
            fingerprint = record_digest(receipt)
            store._artifact(fingerprint, receipt.model_dump_json().encode())
            store._put("supervision", receipt.id, receipt, 0)
            if collection.frozen is not None:
                evidence, version = store.get(
                    "evidence", f"scope:{digest(attempt.id.encode())}", Evidence
                )
                if evidence is None:
                    raise ValueError("original frozen collection requires scope evidence")
                evidence = Evidence.model_validate(
                    {
                        **evidence.model_dump(),
                        "artifacts": sorted({*evidence.artifacts, fingerprint}),
                    }
                )
                store._put("evidence", evidence.id, evidence, version)
            bridge.verify_capture()
            frozen.verify_projection()
            return collection
    except BaseException as error:
        bridge.failed = True
        bridge.installation.reservation._retain_installation_refusal(error)
        raise
