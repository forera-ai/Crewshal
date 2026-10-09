"""Source-bound native/proxy dispatch data. No launcher or execution authority.

The Linux supervisor must still establish and qualify its envelope, credential
channel and effective controls. Native argv is never safe to run on the host.
"""

import json
from pathlib import Path
from typing import Literal

from crewshal.contracts import Attempt, Binding, Digest, Task, record_digest
from crewshal.integration import scope_digest
from crewshal.linux_envelope import LinuxEnvelopeBindings
from crewshal.model import Contract, digest
from crewshal.qualification import Qualification, QualificationIdentity
from crewshal.qualification_bundle import _json, _Reader
from crewshal.runtime import CodexIdentity, CodexRequest, prepare_codex_request
from crewshal.runtime_batch import (
    REQUIREMENT,
    BatchPreparation,
    PreparationSelection,
    audit_runtime_batch,
)

# These inputs are package source, not repository instructions or imported code.
SOURCE_FILES = (
    "dispatch.py",
    "admission.py",
    "linux_envelope.py",
    "linux_bootstrap.py",
    "linux_parent.py",
    "linux_setup.py",
    "linux_inventory.py",
    "linux_teardown.py",
    "linux_storage.py",
    "bootstrap_helper.c",
    "supervisor.py",
    "runtime.py",
    "runtime_batch.py",
    "integration.py",
    "candidate.py",
    "durable.py",
    "contracts.py",
    "gates.py",
    "model.py",
    "qualification.py",
    "qualification_bundle.py",
)


class DispatchLimits(Contract):
    worker_memory_bytes: Literal[134217728] = 134217728
    worker_swap_bytes: Literal[0] = 0
    worker_cpus: Literal[1] = 1
    worker_tasks: Literal[32] = 32
    worker_seconds: Literal[5] = 5
    stop_grace_seconds: Literal[1] = 1
    aggregate_memory_bytes: Literal[805306368] = 805306368
    aggregate_swap_bytes: Literal[0] = 0
    aggregate_cpus: Literal[1] = 1
    aggregate_tasks: Literal[128] = 128
    logical_disk_bytes: Literal[8589934592] = 8589934592
    allocated_disk_bytes: Literal[8589934592] = 8589934592
    candidate_bytes: Literal[16777216] = 16777216
    scratch_bytes: Literal[33554432] = 33554432
    stream_bytes: Literal[65536] = 65536
    capture_seconds: Literal[10] = 10
    startup_seconds: Literal[120] = 120
    batch_seconds: Literal[600] = 600
    cleanup_reserve_seconds: Literal[30] = 30
    implementation_attempts: Literal[1] = 1
    automatic_retries: Literal[0] = 0


class DispatchConfiguration(Contract):
    schema_version: Literal[1] = 1
    selection: PreparationSelection
    preparation_digest: Digest | None
    task_digest: Digest | None
    launch_binding: Binding | None
    source_sha256: dict[str, Digest]
    native_argv: list[str]
    native_stdin: str
    native_environment: dict[str, str]
    proxy_argv: list[str] | None
    proxy_credential_input: Literal["separate_broker_stdin"] = "separate_broker_stdin"
    validator_argv: list[str]
    limits: DispatchLimits
    linux_envelope: LinuxEnvelopeBindings | None = None
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False


def prepare_dispatch_configuration(
    selection: PreparationSelection,
    *,
    preparation_digest: str | None = None,
    task: Task | None = None,
    binding: Binding | None = None,
    linux_envelope: LinuxEnvelopeBindings | None = None,
) -> DispatchConfiguration:
    """Compile prospective data before qualification, including current source bytes.

    Missing choices remain missing. No ambient account/configuration or credential
    is inspected. Fields describe intended controls, not effective observations.
    The configuration digest must be bound by a fresh exact qualification later.
    """
    selection = PreparationSelection.model_validate_json(selection.model_dump_json())
    if linux_envelope is not None:
        linux_envelope = LinuxEnvelopeBindings.model_validate_json(linux_envelope.model_dump_json())
        if linux_envelope.context != record_digest(selection):
            raise ValueError("Linux envelope context differs from project/session selection")
    if (task is None) != (binding is None):
        raise ValueError("task and launch binding must be supplied together")
    if task is not None and binding is not None:
        task = Task.model_validate_json(task.model_dump_json())
        binding = Binding.model_validate_json(binding.model_dump_json())
        if binding.task != record_digest(task):
            raise ValueError("dispatch configuration task binding differs")
    native = [
        "/opt/codex/bin/codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--color",
        "never",
        "--json",
        "-C",
        "/scratch/checkout",
        "--add-dir",
        "/candidate/owned",
        "--add-dir",
        "/scratch",
        "-s",
        "workspace-write",
        "-m",
        selection.model,
    ]
    # Fixed internal transport provider; the selected real provider stays explicit
    # in selection/attempt identity. CLI options are literals, never shell text.
    settings: dict[str, str | int | bool] = {
        "approval_policy": "never",
        "model_provider": "crewshal",
        "model_providers.crewshal.name": "crewshal",
        "model_providers.crewshal.base_url": "http://127.0.0.1:8080/v1",
        "model_providers.crewshal.wire_api": "responses",
        "model_providers.crewshal.requires_openai_auth": False,
        "model_providers.crewshal.request_max_retries": 0,
        "model_providers.crewshal.stream_max_retries": 0,
        "features.shell_snapshot": False,
        "project_doc_max_bytes": 0,
        "features.sqlite": False,
        "thread_unload_delay_secs": 0,
        "agents.enabled": False,
        "features.goals": False,
        "features.memories": False,
        "features.multi_agent": False,
        "features.hooks": False,
        "features.view_image": False,
        "web_search": "disabled",
        "analytics.enabled": False,
        "feedback.enabled": False,
        "otel.exporter": "none",
        "otel.trace_exporter": "none",
        "otel.metrics_exporter": "none",
        "check_for_update_on_startup": False,
        "features.plugins": False,
        "features.remote_plugin": False,
        "features.recommended_plugins": False,
        "features.plugin_hooks": False,
        "features.apps": False,
        "skills.bundled.enabled": False,
        "skills.include_instructions": False,
        "features.skip_host_skill_discovery": True,
        "allow_login_shell": False,
    }
    for key, value in settings.items():
        native.extend(["-c", f"{key}={json.dumps(value, ensure_ascii=True)}"])
    native.append("-")
    reader = _Reader(Path(__file__).parent)
    return DispatchConfiguration(
        selection=selection,
        preparation_digest=preparation_digest,
        task_digest=record_digest(task) if task is not None else None,
        launch_binding=binding,
        source_sha256={name: digest(reader.read(name)) for name in SOURCE_FILES},
        native_argv=native,
        native_stdin=REQUIREMENT + "\n",
        native_environment={
            "HOME": "/scratch",
            "CODEX_HOME": "/scratch",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/input/empty-global-instructions",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": "/dev/null",
            "TOKIO_WORKER_THREADS": "1",
            "RAYON_NUM_THREADS": "1",
            "PATH": "/opt/codex/codex-path:/bin:/usr/bin",
        },
        proxy_argv=(
            [
                "/opt/codex/codex-responses-api-proxy-aarch64-unknown-linux-musl",
                "--port",
                "8080",
                "--upstream-url",
                selection.destination,
            ]
            if selection.destination is not None
            else None
        ),
        validator_argv=["/bin/python3", "-I", "-B", "/input/check_fixture.py", "/candidate/owned"],
        limits=DispatchLimits(),
        linux_envelope=linux_envelope,
    )


class CodexDispatch(Contract):
    schema_version: Literal[1] = 1
    request: CodexRequest
    configuration: DispatchConfiguration
    qualification: QualificationIdentity
    qualification_record_digest: Digest
    task_digest: Digest
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False


def prepare_codex_dispatch(
    reference_root: Path,
    bundle: Path,
    expected: BatchPreparation,
    *,
    selection: PreparationSelection,
    configuration: DispatchConfiguration,
    task: Task,
    attempt: Attempt,
    current: Binding,
    identity: CodexIdentity,
    qualification: Qualification | None,
    current_qualification: QualificationIdentity,
) -> CodexDispatch:
    """Join audited preparation to the existing qualified request seam, never launch.

    A qualified request is still preparation. This does not persist a launch intent,
    authenticate the owner, load Linux controls or obtain execution/spend authority.
    Missing supervisor/broker/validator capabilities remain blocking live gates.
    """
    audit = audit_runtime_batch(reference_root, bundle, expected, selection=selection)
    configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
    selected = configuration.selection
    if configuration != prepare_dispatch_configuration(
        selection,
        preparation_digest=audit.preparation_digest,
        task=task,
        binding=current,
        linux_envelope=configuration.linux_envelope,
    ):
        raise ValueError("dispatch configuration or current source/preparation bytes differ")
    if (
        selected.provider is None
        or selected.destination is None
        or selected.billing_mode == "unresolved"
        or selected.credential_treatment != "external_scoped_channel"
    ):
        raise ValueError("dispatch preparation requires explicit per-session route choices")
    task = Task.model_validate_json(task.model_dump_json())
    identity = CodexIdentity.model_validate_json(identity.model_dump_json())
    current = Binding.model_validate_json(current.model_dump_json())
    reader = _Reader(bundle)
    manifest = _json(reader.read("initial-manifest.json"))
    template = _json(reader.read("dispatch-template.json"))
    if not isinstance(template, dict) or (
        template.get("task_stdin") != configuration.native_stdin
        or template.get("validator_argv") != configuration.validator_argv
        or template.get("native_tail") != configuration.native_argv[:19]
    ):
        raise ValueError("dispatch template differs from pinned native/check interface")
    from crewshal.candidate import FrozenCandidate

    initial = FrozenCandidate.model_validate(manifest)
    if (
        identity.configuration != record_digest(configuration)
        or identity.provider != selected.provider
        or identity.model != selected.model
        or current.candidate != record_digest(initial)
        or current.scope != scope_digest(["README.md"])
        or task.requirement + "\n" != configuration.native_stdin
        or len(task.checks) != 1
        or task.checks[0].argv != configuration.validator_argv
        or task.checks[0].cwd != "."
        or task.review_required
        or task.independent_provider
    ):
        raise ValueError("dispatch task, snapshot, scope, check or identity differs")
    request = prepare_codex_request(
        task, attempt, current, identity, qualification, current_qualification
    )
    # prepare_codex_request already rejects a missing qualification.
    if qualification is None:
        raise ValueError("missing qualification")
    return CodexDispatch(
        request=request,
        configuration=configuration,
        qualification=current_qualification,
        qualification_record_digest=record_digest(qualification),
        task_digest=record_digest(task),
    )
