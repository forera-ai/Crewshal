"""Prospective Linux envelope fragments, never a launcher or kernel observation.

The accepted mechanisms still need an owned implementation and exact Linux
qualification. In particular these fragments cannot create the stopped native
Popen child required by admission. They must never be executed directly.
"""

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from crewshal.contracts import Digest, record_digest
from crewshal.model import Contract

if TYPE_CHECKING:
    from crewshal.dispatch import DispatchConfiguration


class LinuxEnvelopeBindings(Contract):
    """Prospective digests supplied explicitly; no effective readback or authority."""

    schema_version: Literal[1] = 1
    context: Digest
    root_inventory_sha256: Digest | None = None
    helper_library_inventory_sha256: Digest | None = None
    parent_inventory_sha256: Digest | None = None
    role_policy_sha256: Digest | None = None
    network_policy_sha256: Digest | None = None
    storage_policy_sha256: Digest | None = None
    deadline_policy_sha256: Digest | None = None
    bootstrap_policy_sha256: Digest | None = None
    recovery_policy_sha256: Digest | None = None
    credential_design_sha256: Digest | None = None
    financial_treatment_sha256: Digest | None = None


class EnvelopeMount(Contract):
    source: str
    target: str
    readonly: bool


def _stdio() -> list[Literal[0, 1, 2]]:
    return [0, 1, 2]


class BootstrapCheckpoint(Contract):
    """Required admission compatibility, not an observed or created checkpoint."""

    state: Literal["T"] = "T"
    tracer_pid: Literal[0] = 0
    threads: Literal[1] = 1
    child_fds: list[Literal[0, 1, 2]] = Field(default_factory=_stdio)
    worker_direct_processes: Literal[1] = 1
    parent_handle: Literal["native_subprocess_popen"] = "native_subprocess_popen"
    deadline_origin: Literal["before_worker_start"] = "before_worker_start"
    identities: list[str] = Field(
        default_factory=lambda: [
            "pidfd",
            "pid",
            "parent_pid",
            "start_ticks",
            "boot_id",
            "executable",
            "argv",
            "initial_environment",
            "cwd",
            "namespaces",
            "stdio_pipes",
            "worker_device_inode",
            "aggregate_device_inode_and_actual_ancestry",
        ]
    )


class LinuxEnvelopePreparation(Contract):
    schema_version: Literal[1] = 1
    configuration: Digest
    bindings: LinuxEnvelopeBindings
    owned_root: str
    unit_properties: dict[str, dict[str, str]]
    aggregate_controls: dict[str, str]
    worker_controls: dict[str, str]
    mounts: dict[str, list[EnvelopeMount]]
    native_argv: list[str]
    broker_argv: list[str] | None
    validator_argv: list[str]
    credential_input: Literal["separate_broker_stdin", "native_managed_private_home"] = (
        "separate_broker_stdin"
    )
    storage_mechanism: Literal["private_keyring_ext4_ecryptfs"] = "private_keyring_ext4_ecryptfs"
    storage_reservations: dict[str, int]
    reserved_disk_bytes: int
    checkpoint: BootstrapCheckpoint
    unresolved: list[str]
    bootstrap_implemented: Literal[False] = False
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False


def _properties(memory: int, tasks: int, seconds: int, grace: int) -> dict[str, str]:
    return {
        "MemoryMax": str(memory),
        "MemorySwapMax": "0",
        "TasksMax": str(tasks),
        "CPUQuota": "100%",
        "CPUQuotaPeriodSec": "100ms",
        "RuntimeMaxSec": f"{seconds}s",
        "TimeoutStopSec": f"{grace}s",
        "KillMode": "control-group",
        "SendSIGKILL": "yes",
        "Restart": "no",
        "Delegate": "no",
        "LimitCORE": "0",
        "Type": "exec",
    }


def _role_argv(
    mounts: list[EnvelopeMount],
    uid: int,
    command: list[str],
    environment: dict[str, str],
    *,
    network_denied: bool,
    cwd: str,
) -> list[str]:
    # A private root and mediated network must already exist in a trusted setup
    # namespace. This fragment intentionally does not guess namespace handles.
    argv = ["/usr/bin/bwrap"]
    for mount in mounts:
        argv.extend(["--ro-bind" if mount.readonly else "--bind", mount.source, mount.target])
    argv.extend(
        [
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--unshare-pid",
            "--unshare-ipc",
            "--unshare-uts",
            "--new-session",
            "--die-with-parent",
            "--clearenv",
            "--chdir",
            cwd,
        ]
    )
    if network_denied:
        argv.append("--unshare-net")
    for key, value in sorted(environment.items()):
        argv.extend(["--setenv", key, value])
    argv.extend(
        [
            "--cap-drop",
            "ALL",
            "--cap-add",
            "CAP_SETUID",
            "--cap-add",
            "CAP_SETGID",
            "--cap-add",
            "CAP_SETPCAP",
            "--",
            "/bin/setpriv",
            f"--reuid={uid}",
            f"--regid={uid}",
            "--clear-groups",
            "--bounding-set=-all",
            "--inh-caps=-all",
            "--ambient-caps=-all",
            "--no-new-privs",
            "--",
        ]
    )
    return argv + command


def native_working_directory(
    configuration: "DispatchConfiguration",
) -> Literal["/scratch/checkout", "/candidate/owned"]:
    """Exact route cwd data, never a filesystem or process observation."""
    if configuration.native_interface == "app_server_stdio":
        profile = configuration.app_server_profile
        if profile is None or profile.thread_params.get("cwd") != "/candidate/owned":
            raise ValueError("subscription envelope requires the exact fixed task profile/cwd")
        return "/candidate/owned"
    return "/scratch/checkout"


def prepare_linux_envelope(configuration: "DispatchConfiguration") -> LinuxEnvelopePreparation:
    """Compile only data from current exact dispatch and explicit context bindings.

    No process, signal, filesystem mutation, mount, account, policy load or socket
    is performed. Every effective control and bootstrap remains unresolved even
    if every prospective digest is present. Systemd properties are requirements;
    they are not a service invocation or proof of its timer's origin.
    """
    from crewshal.dispatch import DispatchConfiguration, prepare_dispatch_configuration

    configuration = DispatchConfiguration.model_validate_json(configuration.model_dump_json())
    bindings = configuration.linux_envelope
    if bindings is None:
        raise ValueError("explicit per-session Linux envelope bindings required")
    if bindings.context != record_digest(configuration.selection):
        raise ValueError("Linux envelope context differs from project/session selection")
    expected = prepare_dispatch_configuration(
        configuration.selection,
        preparation_digest=configuration.preparation_digest,
        linux_envelope=bindings,
        app_server_profile=configuration.app_server_profile,
    )
    expected = DispatchConfiguration.model_validate(
        {
            **expected.model_dump(),
            "task_digest": configuration.task_digest,
            "launch_binding": configuration.launch_binding,
        }
    )
    if configuration != expected:
        raise ValueError("Linux envelope dispatch or current source bytes differ")
    cwd = native_working_directory(configuration)
    if configuration.launch_binding is not None and (
        configuration.launch_binding.task != configuration.task_digest
    ):
        raise ValueError("Linux envelope task and launch binding differ")

    root = "/run/crewshal-2d-" + bindings.context
    vendor = root + "/readonly-root"
    empty = vendor + "/input/empty-global-instructions"
    readonly = [EnvelopeMount(source=vendor, target="/", readonly=True)]
    masks = [
        EnvelopeMount(source=empty, target="/scratch/AGENTS.md", readonly=True),
        EnvelopeMount(source=empty, target="/scratch/AGENTS.override.md", readonly=True),
    ]
    # Empty readonly /dev/shm is separately required; bwrap's fresh /dev must
    # never introduce an unaccounted writable tmpfs representation.
    shm = EnvelopeMount(source=vendor + "/dev/shm", target="/dev/shm", readonly=True)
    mounts = {
        "native": [
            *readonly,
            EnvelopeMount(
                source=root + "/candidate-upper", target="/candidate/owned", readonly=False
            ),
            EnvelopeMount(source=root + "/scratch-upper", target="/scratch", readonly=False),
            *masks,
        ],
        "broker": [*readonly],
        "validator": [
            *readonly,
            EnvelopeMount(
                source=root + "/validator-candidate", target="/candidate/owned", readonly=True
            ),
            EnvelopeMount(
                source=root + "/validator-scratch-upper", target="/scratch", readonly=False
            ),
        ],
    }
    subscription = configuration.native_interface == "app_server_stdio"
    if subscription:
        # Prospective only. The producer must retain/account this separate private
        # representation from creation. Never alias it beneath tool-writable roots.
        mounts["native"].append(
            EnvelopeMount(source=root + "/native-auth", target="/native-auth", readonly=False)
        )
    # Bind /dev/shm after --dev, rather than hiding it under the later dev mount.
    native = _role_argv(
        mounts["native"],
        65534,
        configuration.native_argv,
        configuration.native_environment,
        network_denied=False,
        cwd=cwd,
    )
    broker = (
        _role_argv(
            mounts["broker"], 65533, configuration.proxy_argv, {}, network_denied=False, cwd="/"
        )
        if configuration.proxy_argv is not None
        else None
    )
    validator = _role_argv(
        mounts["validator"],
        65531,
        configuration.validator_argv,
        {},
        network_denied=True,
        cwd="/candidate/owned",
    )
    for argv in (native, broker, validator):
        if argv is not None:
            index = argv.index("--dev") + 2
            argv[index:index] = ["--ro-bind", shm.source, shm.target]
    for role in mounts:
        mounts[role].append(shm)

    limits = configuration.limits
    units = {
        "worker": _properties(
            limits.worker_memory_bytes,
            limits.worker_tasks,
            limits.worker_seconds,
            limits.stop_grace_seconds,
        ),
        "validator": _properties(
            limits.worker_memory_bytes,
            limits.worker_tasks,
            limits.worker_seconds,
            limits.stop_grace_seconds,
        ),
        "broker": _properties(
            67108864,
            16,
            limits.batch_seconds - limits.cleanup_reserve_seconds,
            limits.stop_grace_seconds,
        ),
        "supervisor": _properties(
            limits.aggregate_memory_bytes,
            limits.aggregate_tasks,
            limits.batch_seconds - limits.cleanup_reserve_seconds,
            limits.cleanup_reserve_seconds,
        ),
    }
    units["supervisor"].update(PrivateMounts="yes", PrivateNetwork="yes")
    reservations = {
        "prepared": 1073741824,
        "candidate_each_representation": limits.candidate_bytes,
        "candidate_representations": 3,
        "scratch_each_representation": limits.scratch_bytes,
        "scratch_representations": 3,
        "validator_scratch_each_representation": limits.scratch_bytes,
        "validator_scratch_representations": 3,
        "frozen_validator_candidate": limits.candidate_bytes,
        "output": limits.candidate_bytes,
    }
    reserved = (
        reservations["prepared"]
        + reservations["output"]
        + reservations["frozen_validator_candidate"]
        + reservations["candidate_each_representation"] * reservations["candidate_representations"]
        + reservations["scratch_each_representation"] * reservations["scratch_representations"]
        + reservations["validator_scratch_each_representation"]
        * reservations["validator_scratch_representations"]
    )
    if reserved > min(limits.logical_disk_bytes, limits.allocated_disk_bytes):
        raise ValueError("Linux envelope reservations exceed original disk ceilings")
    unresolved = [
        name
        for name, value in bindings.model_dump().items()
        if name.endswith("_sha256") and value is None
    ]
    for name in ("provider", "destination"):
        if getattr(configuration.selection, name) is None:
            unresolved.append(name)
    for name in ("billing_mode", "credential_treatment"):
        if getattr(configuration.selection, name) == "unresolved":
            unresolved.append(name)
    if configuration.task_digest is None or configuration.launch_binding is None:
        unresolved.append("exact_task_and_launch_binding")
    unresolved.extend(
        [
            "bootstrap_implementation_and_stopped_checkpoint",
            "native_exec_identity_before_any_native_instruction",
            "owned_admission_failure_recovery",
            "deadline_origin_and_manager_readback",
            "private_keyring_loop_mount_and_role_readback",
            "storage_logical_allocated_alias_and_deleted_open",
            "native_tool_role_policy_and_transport_denial",
            "private_network_namespace_and_actor_egress",
            "credential_caller_separation_and_upstream_readback",
            "financial_enforcement_or_explicit_nonhard_exposure",
            "independent_validator_freeze_and_readback",
            "effective_controls_and_exact_qualification",
            "separate_owner_execution_and_spend_gate",
        ]
    )
    if subscription:
        unresolved.extend(
            [
                "private_native_auth_mount_identity_permissions_and_from_creation_accounting",
                "effective_native_auth_alias_proc_fd_and_inprocess_tool_denial",
                "fresh_native_home_no_preloaded_dotenv_and_stock_arg0_helper_view",
                "managed_subscription_http_refresh_route_and_account_quota_readback",
            ]
        )
    return LinuxEnvelopePreparation(
        configuration=record_digest(configuration),
        bindings=bindings,
        owned_root=root,
        unit_properties=units,
        worker_controls={
            "memory.max": "134217728",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "32",
            "cgroup.type": "domain",
        },
        aggregate_controls={
            "memory.max": "805306368",
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "pids.max": "128",
            "cgroup.type": "domain",
        },
        mounts=mounts,
        native_argv=native,
        broker_argv=broker,
        validator_argv=validator,
        credential_input=configuration.proxy_credential_input,
        storage_reservations=reservations,
        reserved_disk_bytes=reserved,
        checkpoint=BootstrapCheckpoint(),
        unresolved=unresolved,
    )


def audit_linux_envelope(
    configuration: "DispatchConfiguration",
    expected: LinuxEnvelopePreparation,
) -> LinuxEnvelopePreparation:
    """Recompute exact passive fragments; successful readback never enables use."""
    expected = LinuxEnvelopePreparation.model_validate_json(expected.model_dump_json())
    current = prepare_linux_envelope(configuration)
    if current != expected:
        raise ValueError("Linux envelope preparation differs from current exact dispatch")
    return current
