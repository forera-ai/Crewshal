"""Run one finite Phase 2D batch through its original retained owners.

The input is data. It cannot replace process, storage, or authentication custody.
The owner must approve these exact inputs before this entry runs.
"""

import json
import os
import socket
import signal
import stat
import sys
import time
from typing import Literal, NoReturn

from pydantic import Field, model_validator

from crewshal.admission import _wait_ready
from crewshal.candidate import FrozenCandidate, _entry_fd
from crewshal.contracts import Approval, Attempt, Binding, Digest, Run, Task, record_digest
from crewshal.dispatch import CodexDispatch, prepare_dispatch_configuration
from crewshal.integration import scope_digest
from crewshal.linux_batch import (
    OriginalQualificationCollector,
    _require_original,
    accept_original_live,
    capture_original_live,
    finish_original_lane,
)
from crewshal.linux_bootstrap import prepare_linux_bootstrap
from crewshal.linux_envelope import LinuxEnvelopeBindings
from crewshal.linux_auth import FrozenAuthenticationPlan, authenticate_original_live
from crewshal.linux_attempt import FrozenAttemptMarker
from crewshal.linux_bridge import (
    StoppedNativeBridge,
    prepare_stopped_native_bridge,
    receive_stopped_validator,
    send_validator_views,
)
from crewshal.linux_network import OwnedProviderNetworks, ProviderNetworkPlan, _inventory_file
from crewshal.linux_operational import FrozenInstallationInputs, OriginalInstallationDriver
from crewshal.linux_qualification_fixture import (
    FrozenQualificationFixture,
    FrozenQualificationTLS,
    RetainedSyntheticExclusions,
    RetainedTLSBrokerLifetime,
    qualification_probe_source,
)
from crewshal.linux_schedule import OwnedThreeLaneSchedule
from crewshal.linux_setup import RetainedLaneSetup, create_namespace_setup, prepare_namespace_setup
from crewshal.linux_storage import BoundedStorageJobs
from crewshal.linux_inventory import root_inventory_digest, helper_library_inventory_digest
from crewshal.linux_validator import validator_toolchain_digest
from crewshal.model import Contract, ProjectModel, digest, model_digest
from crewshal.qualification import (
    MANDATORY_CASES,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)
from crewshal.qualification_bundle import PROTOCOL_SHA256
from crewshal.runtime import CodexIdentity, prepare_codex_request
from crewshal.runtime_batch import AFTER, BEFORE, REQUIREMENT


def current_qualification_manifest() -> Digest:
    """Bind the original cases and current fixture source without compiler outputs."""
    schema = json.dumps(
        FrozenQualificationFixture.model_json_schema(), sort_keys=True, separators=(",", ":")
    ).encode()
    return digest(
        json.dumps(
            {
                "schema_version": 1,
                "original_protocol_sha256": PROTOCOL_SHA256,
                "mandatory_cases": list(MANDATORY_CASES),
                "probe_sha256": digest(qualification_probe_source()),
                "fixture_schema_sha256": digest(schema),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    )


class ConditionalFrozenApproval(Contract):
    """Record the owner's exact conditional decision before native execution."""

    id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    launch_binding: Binding
    expected: FrozenCandidate
    owner: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def exact_candidate(self) -> "ConditionalFrozenApproval":
        if (
            len(self.expected.files) != 1
            or self.expected.files[0].path != "README.md"
            or self.expected.files[0].kind != "file"
            or self.expected.files[0].sha256 != digest(AFTER)
            or self.expected.files[0].size != len(AFTER)
            or self.expected.files[0].mode != 0o644
        ):
            raise ValueError("conditional approval requires the exact README bytes and metadata")
        return self

    def bind_actual(self, run_id: str, launch: Binding, actual: Binding) -> Approval:
        """Apply only the supplied conditional decision to its exact actual binding."""
        decision = type(self).model_validate_json(self.model_dump_json())
        expected = Binding.model_validate(
            {**decision.launch_binding.model_dump(), "candidate": record_digest(decision.expected)}
        )
        if run_id != decision.run_id or launch != decision.launch_binding or actual != expected:
            raise ValueError(
                "actual candidate does not satisfy the separate conditional owner decision"
            )
        return Approval(
            id=decision.id,
            run_id=run_id,
            binding=actual,
            owner=decision.owner,
            reason=decision.reason,
        )


class FrozenBatchInputs(Contract):
    """Freeze the finite sequence and all supplied owner decisions as data."""

    schema_version: Literal[1] = 1
    installation: FrozenInstallationInputs
    networks: ProviderNetworkPlan
    tls: FrozenQualificationTLS
    qualification: QualificationIdentity
    certificate_path: str
    private_key_path: str
    zstd_path: str
    project: ProjectModel
    task: Task
    run: Run
    attempt: Attempt
    implementation_approval: Approval
    frozen_approval: ConditionalFrozenApproval
    initial: FrozenCandidate
    lease_token: str = Field(min_length=1, max_length=128)
    # Authentication has its own closed source contract. No credential bytes
    # or paths can enter this public orchestration record.
    authentication: FrozenAuthenticationPlan
    one_use_parent: str
    one_use_leaf: str = Field(pattern=r"^phase2d-[0-9a-f]{32}\.consumed$")

    @model_validator(mode="after")
    def exact_chain(self) -> "FrozenBatchInputs":
        self.installation.verify_formatter_inventory()
        configuration = self.installation.configuration
        binding = self.run.binding
        if (
            configuration.lane_id is not None
            or self.installation.helper_build is None
            or self.installation.helper_build.policy_build is None
            or self.installation.early_timer is None
            or configuration.native_interface != "app_server_stdio"
            or configuration.selection.provider != "openai"
            or configuration.selection.billing_mode != "subscription_quota"
            or configuration.selection.credential_treatment != "native_managed_private_home"
            or configuration.selection.destination != "https://chatgpt.com/backend-api/codex"
            or configuration.app_server_profile is None
            or configuration.launch_binding != binding
            or configuration.task_digest != record_digest(self.task)
            or self.task.requirement != configuration.app_server_profile.requirement
            or len(self.task.checks) != 1
            or self.task.checks[0].argv != configuration.validator_argv
            or self.task.checks[0].cwd != "."
            or self.task.checks[0].environment != digest(b"")
            or self.task.checks[0].toolchain
            != validator_toolchain_digest(self.installation.inventory, configuration.validator_argv)
            or self.task.review_required
            or self.task.independent_provider
            or self.run.task_id != self.task.id
            or self.run.state != "ready"
            or binding.model != model_digest(self.project)
            or binding.task != record_digest(self.task)
            or binding.candidate != record_digest(self.initial)
            or binding.scope != scope_digest(["README.md"])
            or self.attempt.run_id != self.run.id
            or self.attempt.binding != binding
            or self.attempt.role != "implementation"
            or self.attempt.state != "intent"
            or self.attempt.handle is not None
            or self.attempt.process_exit is not None
            or self.attempt.runtime_result != "unknown"
            or self.attempt.provider != configuration.selection.provider
            or self.attempt.model != configuration.selection.model
            or self.implementation_approval.run_id != self.run.id
            or self.implementation_approval.binding != binding
            or self.frozen_approval.run_id != self.run.id
            or self.frozen_approval.launch_binding != binding
            or self.frozen_approval.id == self.implementation_approval.id
            or self.tls.fixture.configuration != record_digest(configuration)
            or self.tls.fixture.model != configuration.selection.model
            or self.qualification.configuration != record_digest(configuration)
            or self.qualification.manifest != current_qualification_manifest()
            or self.qualification.host_os != "linux"
            or self.qualification.architecture != "aarch64"
            or self.qualification.runtime != "codex-rust-v0.160.1"
            or self.networks.configuration_source
            != digest(
                json.dumps(
                    configuration.source_sha256, sort_keys=True, separators=(",", ":")
                ).encode()
            )
            or self.networks.qualification_transport != "original_two_lane_tls_v1"
            or self.authentication.configuration_source != self.networks.configuration_source
            or self.authentication.account_reference
            != configuration.app_server_profile.account_reference
            or self.one_use_leaf != "phase2d-" + self.tls.fixture.synthetic_nonce + ".consumed"
            or self.installation.inventory.entry_kind != "python"
            or self.installation.inventory.entry_path
            != "/opt/crewshal/lib/crewshal/linux_parent_entry.py"
            or self.installation.inventory.parent_argv
            != [
                "/bin/python3",
                "-I",
                "-S",
                "-B",
                "/opt/crewshal/lib/crewshal/linux_parent_entry.py",
            ]
        ):
            raise ValueError(
                "finite batch task, owner decisions, source, or three-lane profile differs"
            )
        if (
            len(self.initial.files) != 1
            or self.initial.files[0].path != "README.md"
            or self.initial.files[0].kind != "file"
            or self.initial.files[0].mode != 0o644
            or self.initial.files[0].size != len(BEFORE)
            or self.initial.files[0].sha256 != digest(BEFORE)
        ):
            raise ValueError(
                "original initial candidate requires the exact README bytes and metadata"
            )
        for path, expected_hash in (
            (self.certificate_path, self.tls.certificate_sha256),
            (self.private_key_path, self.tls.private_key_sha256),
            (self.zstd_path, self.tls.zstd_library_sha256),
            ("/usr/sbin/ip", self.networks.ip_binary),
            ("/usr/sbin/nft", self.networks.nft_binary),
        ):
            entry = self.installation.inventory.root.get(path)
            if entry is None or entry.kind != "file" or entry.sha256 != expected_hash:
                raise ValueError("TLS inputs must belong to the complete immutable root inventory")
        for name, expected_hash in configuration.source_sha256.items():
            entry = self.installation.inventory.root.get("/opt/crewshal/lib/crewshal/" + name)
            if entry is None or entry.kind != "file" or entry.sha256 != expected_hash:
                raise ValueError(
                    "installed package source differs from the exact current dispatch source"
                )
        for lane in self.networks.lanes[:2]:
            if (
                self.tls.listener_addresses[lane.lane_id] != (lane.host_address, 443)
                or self.tls.peer_addresses[lane.lane_id] != lane.private_address
            ):
                raise ValueError(
                    "finite TLS addresses differ from the original provider network plan"
                )
        if (
            not self.one_use_parent.startswith("/")
            or "/../" in self.one_use_parent
            or self.one_use_parent.endswith("/")
            or "\x00" in self.one_use_parent
        ):
            raise ValueError("one-use marker requires an exact private absolute parent")
        return self


class OwnerDecisionProposal(Contract):
    """Prepare literal decision text for the separate complete batch review."""

    owner: str = Field(min_length=1)
    implementation_id: str = Field(min_length=1)
    implementation_reason: str = Field(min_length=1)
    frozen_id: str = Field(min_length=1)
    frozen_reason: str = Field(min_length=1)


def assemble_frozen_batch(
    installation: FrozenInstallationInputs,
    networks: ProviderNetworkPlan,
    tls: FrozenQualificationTLS,
    qualification: QualificationIdentity,
    project: ProjectModel,
    task: Task,
    *,
    policy_sha256: Digest,
    run_id: str,
    attempt_id: str,
    decisions: OwnerDecisionProposal,
    certificate_path: str,
    private_key_path: str,
    zstd_path: str,
    one_use_parent: str,
    lease_token: str,
) -> FrozenBatchInputs:
    """Join exact supplied records offline. Do not observe, approve, write, or execute."""
    from crewshal.candidate import CandidateFile

    installation = FrozenInstallationInputs.model_validate_json(installation.model_dump_json())
    installation.verify_formatter_inventory()
    inventory = installation.inventory
    selected = installation.configuration
    if (
        selected.app_server_profile is None
        or selected.preparation_digest is None
        or selected.linux_envelope is None
        or installation.helper_build is None
        or installation.helper_build.policy_build is None
        or installation.early_timer is None
        or task.requirement != REQUIREMENT
        or len(task.checks) != 1
        or task.checks[0].argv != selected.validator_argv
        or task.checks[0].environment != digest(b"")
        or task.checks[0].toolchain
        != validator_toolchain_digest(inventory, selected.validator_argv)
    ):
        raise ValueError(
            "complete supplied build, timer, preparation, profile, and task records required"
        )
    initial = FrozenCandidate(
        files=[
            CandidateFile(
                path="README.md",
                kind="file",
                mode=0o644,
                size=len(BEFORE),
                sha256=digest(BEFORE),
            )
        ]
    )
    expected = FrozenCandidate(
        files=[
            CandidateFile(
                path="README.md",
                kind="file",
                mode=0o644,
                size=len(AFTER),
                sha256=digest(AFTER),
            )
        ]
    )
    binding = Binding(
        model=model_digest(project),
        task=record_digest(task),
        policy=policy_sha256,
        scope=scope_digest(["README.md"]),
        candidate=record_digest(initial),
    )
    # Reading the current owned source is part of offline preparation. It does
    # not reconstruct any Linux process, image, mount, or credential identity.
    draft = prepare_dispatch_configuration(
        selected.selection,
        preparation_digest=selected.preparation_digest,
        task=task,
        binding=binding,
        app_server_profile=selected.app_server_profile,
    )
    network_payload = networks.model_dump(mode="json")
    network_payload["configuration_source"] = digest(
        json.dumps(
            draft.source_sha256,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    )
    network_plan = ProviderNetworkPlan.model_validate(network_payload)
    envelope_payload = selected.linux_envelope.model_dump(mode="json")
    envelope_payload.update(
        {
            "context": record_digest(selected.selection),
            "root_inventory_sha256": root_inventory_digest(inventory),
            "parent_inventory_sha256": record_digest(inventory),
            "helper_library_inventory_sha256": helper_library_inventory_digest(inventory),
            "network_policy_sha256": record_digest(network_plan),
            "build_recipe_sha256": record_digest(installation.helper_build),
        }
    )
    configuration = prepare_dispatch_configuration(
        selected.selection,
        preparation_digest=selected.preparation_digest,
        task=task,
        binding=binding,
        linux_envelope=LinuxEnvelopeBindings.model_validate(envelope_payload),
        app_server_profile=selected.app_server_profile,
    )
    bootstrap = prepare_linux_bootstrap(
        configuration,
        helper_binary=installation.bootstrap.policy.helper_binary,
    )
    envelope_payload["bootstrap_policy_sha256"] = record_digest(bootstrap.policy)
    configuration = prepare_dispatch_configuration(
        selected.selection,
        preparation_digest=selected.preparation_digest,
        task=task,
        binding=binding,
        linux_envelope=LinuxEnvelopeBindings.model_validate(envelope_payload),
        app_server_profile=selected.app_server_profile,
    )
    bootstrap = prepare_linux_bootstrap(
        configuration,
        helper_binary=installation.bootstrap.policy.helper_binary,
    )
    installation_payload = installation.model_dump(mode="json")
    installation_payload["configuration"] = configuration.model_dump(mode="json")
    installation_payload["bootstrap"] = bootstrap.model_dump(mode="json")
    prepared_installation = FrozenInstallationInputs.model_validate_json(
        json.dumps(installation_payload)
    )
    tls_payload = tls.model_dump(mode="json")
    tls_payload["fixture"]["configuration"] = record_digest(configuration)
    prepared_tls = FrozenQualificationTLS.model_validate_json(json.dumps(tls_payload))
    qualification_payload = qualification.model_dump(mode="json")
    qualification_payload["configuration"] = record_digest(configuration)
    qualification_payload["manifest"] = current_qualification_manifest()
    profile = configuration.app_server_profile
    assert profile is not None
    return FrozenBatchInputs(
        installation=prepared_installation,
        networks=network_plan,
        tls=prepared_tls,
        qualification=QualificationIdentity.model_validate(qualification_payload),
        certificate_path=certificate_path,
        private_key_path=private_key_path,
        zstd_path=zstd_path,
        project=project,
        task=task,
        run=Run(id=run_id, task_id=task.id, binding=binding),
        attempt=Attempt(
            id=attempt_id,
            run_id=run_id,
            binding=binding,
            role="implementation",
            state="intent",
            provider=configuration.selection.provider,
            model=configuration.selection.model,
        ),
        implementation_approval=Approval(
            id=decisions.implementation_id,
            run_id=run_id,
            binding=binding,
            owner=decisions.owner,
            reason=decisions.implementation_reason,
        ),
        frozen_approval=ConditionalFrozenApproval(
            id=decisions.frozen_id,
            run_id=run_id,
            launch_binding=binding,
            expected=expected,
            owner=decisions.owner,
            reason=decisions.frozen_reason,
        ),
        initial=initial,
        lease_token=lease_token,
        authentication=FrozenAuthenticationPlan(
            configuration_source=network_plan.configuration_source,
            account_reference=profile.account_reference,
        ),
        one_use_parent=one_use_parent,
        one_use_leaf="phase2d-" + prepared_tls.fixture.synthetic_nonce + ".consumed",
    )


class OriginalLiveQualification:
    """Project the two original accepted lane proofs to their unchanged live profile."""

    def __init__(
        self,
        schedule: OwnedThreeLaneSchedule,
        collectors: tuple[OriginalQualificationCollector, OriginalQualificationCollector],
    ):
        if type(schedule) is not OwnedThreeLaneSchedule:
            raise ValueError("live qualification requires the original schedule")
        if hasattr(schedule, "_live_qualification"):
            raise ValueError("original live qualification projection consumed; no replacement")
        self.schedule, self.collectors = schedule, collectors
        self._owners = schedule, collectors
        self.failed = True
        setattr(schedule, "_live_qualification", self)
        if len(collectors) != 2 or any(
            type(value) is not OriginalQualificationCollector for value in collectors
        ):
            raise ValueError("both original qualification collectors required")
        self._sources = tuple(value.result for value in collectors)
        self._source_payloads = tuple(
            "" if value is None else value.model_dump_json() for value in self._sources
        )
        self.verify_sources()
        identity = schedule.identities[2]
        first = self._sources[0]
        assert first is not None
        evidence = json.dumps(
            {
                "source_qualifications": [record_digest(value) for value in self._sources if value],
                "configuration": record_digest(schedule.contexts[2].configuration),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        self.record = Qualification(
            id="phase2d:live-profile:" + digest(evidence.encode()),
            identity=identity,
            results=[value.model_copy(update={"observation": evidence}) for value in first.results],
        )
        self._payload = self.record.model_dump_json()
        self.failed = False
        self.verify()

    def __reduce__(self) -> NoReturn:
        raise TypeError("original live qualification custody cannot be copied or exported")

    def verify_sources(self) -> None:
        schedule = self.schedule
        schedule.verify()
        if (
            self._owners != (schedule, self.collectors)
            or getattr(schedule, "_live_qualification", None) is not self
            or schedule._next != 2
            or schedule._active not in (None, schedule.contexts[2])
            or len(schedule._qualifications) != 2
        ):
            raise ValueError("original two-lane terminal qualification custody differs")
        for index, collector in enumerate(self.collectors):
            source = self._sources[index]
            if (
                source is None
                or collector.failed
                or not collector.consumed
                or collector.result is not source
                or schedule._qualifications[index] is not source
                or collector.bridge.lane_context is not schedule.contexts[index]
                or source.model_dump_json() != self._source_payloads[index]
                or assess_qualification(source, schedule.identities[index]).status
                != "qualified_for_later_authorization"
            ):
                raise ValueError("missing, copied, changed, or stale original qualification")

    def verify(self) -> None:
        self.verify_sources()
        if (
            self.failed
            or self.record.model_dump_json() != self._payload
            or assess_qualification(self.record, self.schedule.identities[2]).status
            != "qualified_for_later_authorization"
        ):
            raise ValueError("original live qualification projection changed")


class OriginalFiniteBatch:
    """Retain every original effect and stop after actual Phase 2D acceptance."""

    schedule: OwnedThreeLaneSchedule
    networks: OwnedProviderNetworks

    def __init__(self, inputs: FrozenBatchInputs):
        self.inputs = FrozenBatchInputs.model_validate_json(inputs.model_dump_json())
        self._payload = self.inputs.model_dump_json()
        self.driver = OriginalInstallationDriver(
            self.inputs.installation,
            fixture=self.inputs.tls.fixture,
            attempt_marker=FrozenAttemptMarker(
                parent=self.inputs.one_use_parent,
                leaf=self.inputs.one_use_leaf,
                plan_sha256=record_digest(self.inputs),
            ),
        )
        setattr(self.driver, "_finite_batch", self)
        self.handles: dict[str, int] = {}
        self.listeners: dict[str, socket.socket] = {}
        self.bridges: list[StoppedNativeBridge] = []
        self.collectors: list[OriginalQualificationCollector] = []
        self.attempted = self.failed = False
        self.result: dict[str, object] | None = None
        self._active_result: bytes | None = None

    def __reduce__(self) -> NoReturn:
        raise TypeError("original finite batch custody cannot be copied or exported")

    def _launch_lane(self, context: RetainedLaneSetup) -> StoppedNativeBridge:
        driver = self.driver
        _require_original(driver)
        assert driver.installation is not None and driver.production is not None
        assert driver.observer is not None and driver.reservation is not None
        self.schedule.activate(context)
        bridge = prepare_stopped_native_bridge(driver.installation, lane_context=context)
        self.bridges.append(bridge)
        inventory = driver.production.projected_inventory
        inventory.verify()
        executable = inventory.inventory.root[inventory.inventory.parent_argv[0]].sha256
        if executable is None:
            raise ValueError("original namespace parent executable identity is missing")
        bootstrap = prepare_linux_bootstrap(
            context.configuration, helper_binary=driver.inputs.bootstrap.policy.helper_binary
        )
        preparation = prepare_namespace_setup(
            context.configuration,
            bootstrap,
            inventory.inventory.parent_argv,
            executable,
            parent_inventory=inventory.inventory,
            validator_control=True,
            bridge_control=True,
            policy_control=True,
            network_control=True,
        )
        lifetime = create_namespace_setup(
            driver.observer,
            driver.reservation.observer_group,
            driver.reservation.aggregate,
            context.setup,
            context.supervisor,
            context.worker,
            context.configuration,
            bootstrap,
            preparation,
            inventory=inventory,
            storage_reservation=driver.reservation,
            storage_owner=driver.installation.physical,
            validator=context.validator,
            bridge=bridge,
            lane_context=context,
            policy=driver.production._payload_storage.policy,
            networks=self.networks,
        )
        bridge.receive_watchdog(lifetime)
        bridge.receive_native()
        return bridge

    def _prepare_networks(self) -> None:
        driver = self.driver
        assert driver.production is not None
        assert driver.reservation is not None and driver.lanes is not None
        root = driver.production.projected_inventory
        host = os.open("/proc/self/ns/net", os.O_RDONLY | os.O_CLOEXEC)
        self.handles["host-network"] = host
        ip = _inventory_file(root, "/usr/sbin/ip")
        nft = _inventory_file(root, "/usr/sbin/nft")
        self.handles["network-ip"], self.handles["network-nft"] = ip, nft
        creation = BoundedStorageJobs(
            driver.observer,
            driver.reservation.observer_group,
            driver.reservation.aggregate,
            driver.origin + 120,
            execution_group=driver.lanes[0].setup,
            batch_timer=driver.timer,
        )
        readback = BoundedStorageJobs(
            driver.observer,
            driver.reservation.observer_group,
            driver.reservation.aggregate,
            driver.origin + 570,
            execution_group=driver.lanes[0].setup,
            batch_timer=driver.timer,
        )
        self.networks = OwnedProviderNetworks(
            driver.reservation,
            creation,
            self.inputs.networks,
            host,
            ip,
            nft,
            readback_jobs=readback,
            inventory=root,
        )
        self.networks.create()
        self.networks.readback()

    def _prepare_broker(self) -> None:
        driver = self.driver
        assert driver.production is not None
        root = driver.production.projected_inventory
        # The original fixture seed has already applied the registered build
        # derivation. No other fixture field can change here.
        fixture = driver.production._fixture_inputs.fixture
        initial = self.inputs.tls.fixture.model_dump(mode="json")
        final = fixture.model_dump(mode="json")
        initial.pop("configuration")
        final.pop("configuration")
        if initial != final or fixture.configuration != record_digest(driver.inputs.configuration):
            raise ValueError("derived fixture differs beyond the installed configuration identity")
        tls = FrozenQualificationTLS.model_validate(
            {**self.inputs.tls.model_dump(), "fixture": fixture}
        )
        for lane, address in tls.listener_addresses.items():
            channel = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM | getattr(socket, "SOCK_CLOEXEC")
            )
            self.listeners[lane] = channel
            channel.bind(address)
            channel.listen(1)
        certificate = _inventory_file(root, self.inputs.certificate_path)
        private_key = _inventory_file(root, self.inputs.private_key_path)
        zstd = _inventory_file(root, self.inputs.zstd_path)
        self.handles.update({"certificate": certificate, "private-key": private_key, "zstd": zstd})
        self.broker = RetainedTLSBrokerLifetime.launch(
            driver,
            tls,
            self.listeners,
            certificate_fd=certificate,
            private_key_fd=private_key,
            zstd_library_fd=zstd,
        )
        self.broker.require_ready()

    def _prepare_live_records(self) -> CodexDispatch:
        driver, plan = self.driver, self.inputs
        assert driver.store is not None
        context = self.schedule.contexts[2]
        initial_fd = driver.production.handles["mounted:live--candidate-upper"]
        if os.listdir(initial_fd) != ["README.md"]:
            raise ValueError("actual initial live candidate contains undeclared entries")
        entry, raw = _entry_fd(initial_fd, "README.md")
        if entry != plan.initial.files[0] or raw != BEFORE:
            raise ValueError("actual initial live candidate differs from the owner-approved task")
        driver.store.save_project(plan.project, 0)
        driver.store.create_task(plan.task)
        driver.store.create_run(plan.run, plan.project.project_id)
        driver.store.owner_approval(plan.implementation_approval)
        driver.store.acquire(plan.run.id, plan.lease_token)
        driver.store.launch_intent(plan.attempt, plan.lease_token)
        if len(self.collectors) != 2:
            raise ValueError("both original qualification collectors required before live dispatch")
        self.live_qualification = OriginalLiveQualification(
            self.schedule, (self.collectors[0], self.collectors[1])
        )
        configuration = context.configuration
        identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider=plan.attempt.provider,
            model=plan.attempt.model,
            configuration=record_digest(configuration),
            native_interface="app_server_stdio",
            app_server_profile=configuration.app_server_profile,
        )
        request = prepare_codex_request(
            plan.task,
            plan.attempt,
            plan.run.binding,
            identity,
            self.live_qualification.record,
            self.schedule.identities[2],
        )
        return CodexDispatch(
            request=request,
            configuration=configuration,
            qualification=self.schedule.identities[2],
            qualification_record_digest=record_digest(self.live_qualification.record),
            task_digest=record_digest(plan.task),
        )

    def run(self) -> dict[str, object]:
        """Consume the exact source plan once. Preserve every partial result after refusal."""
        if self.attempted:
            raise ValueError("original finite batch consumed; no retry")
        self.attempted = True
        try:
            if self.inputs.model_dump_json() != self._payload:
                raise ValueError("original frozen batch input changed")
            self.driver.install()
            driver = self.driver
            _require_original(driver)
            assert (
                driver.reservation is not None
                and driver.timer is not None
                and driver.lanes is not None
            )
            identities = tuple(
                QualificationIdentity.model_validate(
                    {
                        **self.inputs.qualification.model_dump(),
                        "configuration": record_digest(context.configuration),
                    }
                )
                for context in driver.lanes
            )
            self.schedule = OwnedThreeLaneSchedule(
                driver.reservation, driver.timer, driver.lanes, identities
            )
            self._prepare_networks()
            self._prepare_broker()
            root = driver.production.projected_inventory.descriptor
            exclusions = {}
            for name, path in {
                "outside": "outside",
                "original": "original",
                "coordinator": "coordinator",
                "input": "input",
                "host-home": "home/owner",
            }.items():
                descriptor = os.dup(root)
                self.handles["exclusion-start:" + name] = descriptor
                for component in path.split("/"):
                    descriptor = os.open(
                        component,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                        dir_fd=descriptor,
                    )
                    self.handles["exclusion:" + name + ":" + component] = descriptor
                exclusions[name] = descriptor
            self.exclusions = RetainedSyntheticExclusions(exclusions, driver.origin)
            for index, context in enumerate(driver.lanes[:2]):
                bridge = self._launch_lane(context)
                bridge.receive_capture()
                bridge.freeze.freeze()
                send_validator_views(bridge)
                custody = receive_stopped_validator(bridge)
                custody.receive_capture()
                collector = OriginalQualificationCollector(
                    driver,
                    bridge,
                    self.broker.plan.fixture,
                    identities[index],
                    self.exclusions,
                    self.networks,
                    self.broker,
                )
                self.collectors.append(collector)
                qualification = collector.collect(custody)
                assert driver.store is not None and collector.progress is not None
                driver.store._artifact(
                    record_digest(qualification), qualification.model_dump_json().encode()
                )
                driver.store._artifact(digest(collector.progress), collector.progress)
                finish_original_lane(self.schedule, custody, qualification)
            self.broker_terminal = self.broker.finish()
            self.exclusions.verify_unchanged()
            # This source seam must create and retain actual stock authentication
            # under this original owner. Parsed credentials cannot substitute.
            self.authentication = authenticate_original_live(
                driver, self.networks, self.inputs.authentication
            )
            self.authentication.verify()
            dispatch = self._prepare_live_records()
            self.live_qualification.verify()
            bridge = self._launch_lane(driver.lanes[2])
            collection, custody = capture_original_live(
                driver,
                bridge,
                dispatch,
                expected_run_version=1,
                expected_attempt_version=1,
                token=self.inputs.lease_token,
                initial=self.inputs.initial,
            )
            approval = self.inputs.frozen_approval.bind_actual(
                collection.run_id, collection.launch_binding, collection.binding
            )
            verdict = accept_original_live(
                driver,
                collection,
                custody,
                approval,
                project_id=self.inputs.project.project_id,
                token=self.inputs.lease_token,
            )
            finish_original_lane(self.schedule, custody)
            if self.schedule._next != 3 or self.schedule._active is not None:
                raise ValueError("all three original lane terminal results required")
            self.exclusions.verify_unchanged()
            self.networks.readback()
            self.result = {
                "schema_version": 1,
                "phase": "2D",
                "plan": record_digest(self.inputs),
                "origin": driver.origin,
                "qualification": [record_digest(value.result) for value in self.collectors],
                "qualification_records": [
                    value.result.model_dump(mode="json") for value in self.collectors
                ],
                "collection": record_digest(collection),
                "verdict": record_digest(verdict),
                "verdict_record": verdict.model_dump(mode="json"),
                "unique_account_continuity": "unknown",
                "execution_allowed": False,
                "stage": "active_work_verified_retention_pending",
            }
            result_bytes = json.dumps(self.result, sort_keys=True, separators=(",", ":")).encode()
            if len(result_bytes) > 65536:
                raise ValueError(
                    "complete original acceptance report exceeds its unchanged stream bound"
                )
            assert driver.store is not None
            driver.store._artifact(digest(result_bytes), result_bytes)
            self._active_result = result_bytes
            return self.result
        except BaseException as error:
            self.failed = True
            if self.driver.reservation is not None:
                self.driver.reservation._retain_installation_refusal(error)
            raise

    def finish_idle_retention(self) -> dict[str, object]:
        """Wait without new work, then read the original terminal custody after its end."""
        driver = self.driver
        if (
            getattr(driver, "_finite_batch", None) is not self
            or not self.attempted
            or self.failed
            or driver.failed
            or self.result is None
            or json.dumps(self.result, sort_keys=True, separators=(",", ":")).encode()
            != self._active_result
            or self.inputs.model_dump_json() != self._payload
            or driver.reservation is None
            or driver.observer is None
            or driver.timer is None
            or self.schedule._next != 3
            or self.schedule._active is not None
            or self.schedule.reservation is not driver.reservation
            or self.schedule.timer is not driver.timer
            or len(self.collectors) != 2
        ):
            raise ValueError("terminal retention requires the same original completed finite batch")
        if hasattr(self, "_idle_attempted"):
            raise ValueError("original terminal retention consumed; no retry")
        self._idle_attempted = True
        timer = driver.timer
        if timer.task is None or timer.process is None:
            raise ValueError("original timer process custody remains unknown")
        try:
            # The original timer remains the only deadline effector. These
            # bounded waits do not create, renew, or extend an active timer.
            while time.monotonic_ns() < timer.end_ns:
                remaining = (timer.end_ns - time.monotonic_ns()) / 1_000_000_000
                if remaining <= 0:
                    break
                if timer.process.poll() is None:
                    _wait_ready([timer.task.pidfd], [], [], min(remaining, 1.0))
                else:
                    time.sleep(min(remaining, 1.0))
            if timer.process.poll() is None:
                raise ValueError("original batch timer exit remains unknown at its original end")
            if timer.process.returncode != 0:
                raise ValueError("original batch timer terminal result failed")
            driver.reservation.verify_idle_retention()
            # Export observations only. Physical closure remains unknown; no
            # original resource is released, refunded, reopened, or reused.
            self.result["idle_retention"] = {
                "origin_ns": timer.origin_ns,
                "cutoff_ns": timer.cutoff_ns,
                "end_ns": timer.end_ns,
                "observed_ns": time.monotonic_ns(),
                "timer_pid": timer.task.spec.pid,
                "timer_reaped": True,
                "operational_roles_empty": True,
                "observer": record_digest(driver.observer.spec),
                "storage_state": "retained_unknown",
                "reusable": False,
            }
            self.result["stage"] = "verified_with_original_idle_retention"
            if len(json.dumps(self.result, sort_keys=True, separators=(",", ":")).encode()) > 65536:
                raise ValueError(
                    "final original retention report exceeds its unchanged stream bound"
                )
            return self.result
        except BaseException:
            self.failed = True
            raise


def read_frozen_inputs(path: str) -> tuple[FrozenBatchInputs, int]:
    """Read one bounded root-owned readonly plan without following its final link."""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    info = os.fstat(descriptor)
    if (
        not stat.S_ISREG(info.st_mode)
        or (info.st_uid, info.st_gid) != (0, 0)
        or stat.S_IMODE(info.st_mode) != 0o400
        or not 0 < info.st_size <= 8388608
        or not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY
    ):
        raise ValueError("operational plan requires bounded root-owned immutable bytes")
    raw = os.pread(descriptor, info.st_size + 1, 0)
    after = os.fstat(descriptor)
    if len(raw) != info.st_size or (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError("operational plan changed during independent readback")
    return FrozenBatchInputs.model_validate_json(raw), descriptor


def main() -> None:
    """Run only in the separately approved original isolated Linux observer."""
    # CPython can add this locale after an empty-environment exec.
    if os.environ:
        if (
            sys.platform != "linux"
            or not sys.flags.isolated
            or not sys.flags.no_site
            or not sys.flags.dont_write_bytecode
            or dict(os.environ) != {"LC_CTYPE": "C.UTF-8"}
        ):
            raise ValueError("The isolated entry inherited an environment.")
        with open("/proc/self/environ", "rb") as inherited:
            if inherited.read(1):
                raise ValueError("The isolated entry inherited an environment.")
        del os.environ["LC_CTYPE"]
    if (
        sys.platform != "linux"
        or os.getuid() != 0
        or os.getgid() != 0
        or os.environ
        or sys.version_info[:2] != (3, 12)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or len(sys.argv) != 2
    ):
        raise ValueError("finite observer requires isolated Linux root startup and one frozen plan")
    inputs, descriptor = read_frozen_inputs(sys.argv[1])
    owner = OriginalFiniteBatch(inputs)
    owner.handles["frozen-plan"] = descriptor
    # Keep the original owner reachable even if a later constructor refuses.
    globals()["_original_batch"] = owner
    try:
        owner.run()
        result = owner.finish_idle_retention()
    except BaseException as error:
        # Preserve the same original owner and partial FDs after refusal.
        # Raw exception data stays private; it may contain account metadata.
        globals()["_original_failure"] = error
        location = error.__traceback__
        while location is not None and location.tb_next is not None:
            location = location.tb_next
        causes = []
        from crewshal.linux_storage import StorageChildRefusal

        storage_failure = None
        cause: BaseException | None = error
        seen: set[int] = set()
        while cause is not None and id(cause) not in seen and len(causes) < 8:
            seen.add(id(cause))
            if type(cause) is StorageChildRefusal:
                storage_failure = cause.public_detail()
            trace = cause.__traceback__
            while trace is not None and trace.tb_next is not None:
                trace = trace.tb_next
            causes.append(
                {
                    "type": type(cause).__name__,
                    "source": None
                    if trace is None
                    else os.path.basename(trace.tb_frame.f_code.co_filename),
                    "line": None if trace is None else trace.tb_lineno,
                    "errno": cause.errno if isinstance(cause, OSError) else None,
                }
            )
            cause = cause.__cause__ or cause.__context__
        result = {
            "schema_version": 1,
            "phase": "2D",
            "stage": "refused_with_original_custody",
            "failure_causes": causes,
            "failure_type": type(error).__name__,
            "failure_source": (
                None if location is None else os.path.basename(location.tb_frame.f_code.co_filename)
            ),
            "failure_line": None if location is None else location.tb_lineno,
            "failure_errno": error.errno if isinstance(error, OSError) else None,
            "execution_allowed": False,
            "reusable": False,
        }
        if storage_failure is not None:
            result["storage_child_failure"] = storage_failure
    print(json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
    # The batch has ended. This original observer holds unknown resources.
    # No process, write, timer, job, or further admission starts here.
    while True:
        signal.pause()


def observer_entry_source() -> bytes:
    """Return the fixed isolated entry. This function does not execute it."""
    return b'''"""Start the approved original Phase 2D observer."""
import os
import stat
import sys
# CPython can add this locale after an empty-environment exec.
if os.environ:
    if (
        sys.platform != "linux"
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or dict(os.environ) != {"LC_CTYPE": "C.UTF-8"}
    ):
        raise ValueError("The isolated entry inherited an environment.")
    with open("/proc/self/environ", "rb") as inherited:
        if inherited.read(1):
            raise ValueError("The isolated entry inherited an environment.")
    del os.environ["LC_CTYPE"]
if (sys.platform != "linux" or os.getuid() != 0 or os.getgid() != 0 or os.environ
    or not sys.flags.isolated or not sys.flags.no_site or not sys.flags.dont_write_bytecode
    or sys.version_info[:2] != (3, 12)
    or sys.argv != ["/run/crewshal-phase2d-input-v1/observer-entry.py",
                    "/run/crewshal-phase2d-input-v1/batch.json"]):
    raise ValueError("exact isolated original observer startup required")
root = os.open("/run/crewshal-phase2d-input-v1/lib",
               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
info = os.fstat(root)
if ((info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (0, 0, 0o555)
    or not os.fstatvfs(root).f_flag & os.ST_RDONLY):
    raise ValueError("original observer runtime must be root-owned and readonly")
sys.path.insert(0, "/run/crewshal-phase2d-input-v1/lib")
from crewshal.linux_batch_entry import main
main()
'''


if __name__ == "__main__":
    main()
