"""Owned setup and terminal lifetime source, never an operational entry point.

Every startup/kernel effect below requires separately qualified trusted callers
and the concrete project/session gate. Offline tests replace those effects.
Inherited sealed data is configuration, not authority or containment evidence.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import math
import os
from pathlib import PurePosixPath
import socket
import re
import resource
import stat
import struct
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Literal
from copy import deepcopy

from crewshal.admission import _wait_ready
from crewshal.admission import (
    AdmittedNative,
    NamespaceIdentity,
    _aggregate_readback,
    _current_source,
    _fields,
    _read,
    _stat_identity,
)
from crewshal.contracts import Digest, record_digest
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_bootstrap import ArmedDeadline, BootstrapPreparation, audit_linux_bootstrap
from crewshal.linux_envelope import (
    FILE_GROWTH_BYTES,
    native_working_directory,
    prepare_linux_envelope,
)
from crewshal.linux_inventory import (
    RetainedParentInventory,
    TrustedParentInventory,
    bind_parent_inventory,
)
from crewshal.linux_parent import (
    ObservedWatchdog,
    RetainedTrustedTask,
    TrustedTaskSpec,
    _attach,
    _move_self,
    _proc_root,
)
from crewshal.model import Contract, digest
from crewshal.supervisor import CgroupIdentity, OwnedCgroup, _counters

CAPABILITIES = "00000000002801c0"
CONTROL_BOUND = 262144

if TYPE_CHECKING:
    from crewshal.linux_early_timer import RetainedEarlyTimerRuntime
    from crewshal.linux_payload_storage import RetainedAppArmorExport
    from crewshal.linux_network import OwnedProviderNetworks
    from crewshal.linux_bridge import StoppedNativeBridge
    from crewshal.linux_production import EffectiveInstallation
    from crewshal.durable import (
        CoordinatorStore,
        LiveStorageCapacityClaim,
        LiveStorageInstallationClaim,
    )
    from crewshal.linux_storage import LinuxPhysicalOwner


@dataclass(frozen=True)
class StorageCharges:
    """Irreversible reservation of the original shared allowance, not extra capacity."""

    memory_bytes: int = 805306368
    tasks: int = 128
    logical_bytes: int = 8589934592
    allocated_bytes: int = 8589934592


class OwnedStorageReservation:
    """One live observer's retained full reservation; no receipt-based reconstruction.

    Trusted setup must mint this before storage creation and keep this exact
    object throughout the lifetime. This source contract cannot prove an absent
    producer's from-creation confinement or grant Linux execution authority.
    Charges never become available again, including after refusal or expiry.
    """

    _batch_timer: "OwnedBatchTimer"
    _installation: "EffectiveInstallation"
    _lane_contexts: tuple["RetainedLaneSetup", ...]

    def __init__(
        self,
        observer: RetainedTrustedTask,
        observer_group: OwnedCgroup,
        aggregate: OwnedCgroup,
        configuration: DispatchConfiguration,
        *,
        batch_started_monotonic: float,
        capacity_claim: "LiveStorageCapacityClaim | LiveStorageInstallationClaim | None" = None,
    ):
        now = time.monotonic()
        if (
            not math.isfinite(batch_started_monotonic)
            or not 0 < batch_started_monotonic <= now < batch_started_monotonic + 600
        ):
            raise ValueError("original storage reservation batch origin required")
        if getattr(observer, "_setup_started", False) or hasattr(observer, "_storage_reservation"):
            raise ValueError("storage reservation precedes setup and is one-shot")
        from crewshal.durable import LiveStorageCapacityClaim, LiveStorageInstallationClaim

        if type(capacity_claim) not in (LiveStorageCapacityClaim, LiveStorageInstallationClaim):
            raise ValueError("original irreversible live capacity claim required before creation")
        assert capacity_claim is not None
        if (
            type(capacity_claim) is LiveStorageInstallationClaim
            and getattr(observer, "_installation_charge", None) is not capacity_claim
        ):
            raise ValueError("installation requires original observer's upfront charge")
        self._capacity_claim = capacity_claim
        self.observer, self.observer_group, self.aggregate = observer, observer_group, aggregate
        self._owners = (observer, observer_group, aggregate)
        self._configuration = configuration
        self._configuration_digest = record_digest(configuration)
        self._charge_configuration_digest = self._configuration_digest
        self._observer_digest = record_digest(observer.spec)
        self._group_digest = record_digest(observer_group.identity)
        self._aggregate_digest = record_digest(aggregate.identity)
        self._batch_started = batch_started_monotonic
        self._origin = batch_started_monotonic
        self._handles = (
            observer.descriptor,
            observer.pidfd,
            observer_group.descriptor,
            aggregate.descriptor,
        )
        self._charges = StorageCharges()
        self._claim_attempted = False
        self._setup_lifetime: OwnedNamespaceSetup | None = None
        self._lifetime: OwnedNamespaceSetup | None = None
        self._retained: object | None = None
        self._storage_owner: object | None = None
        # Install before verification: even a refused admission burns this
        # observer's reservation, with no refund or later reconstructed attempt.
        setattr(observer, "_storage_reservation", self)
        capacity_claim.bind_reservation(self)
        self.verify()

    @property
    def charges(self) -> StorageCharges:
        # A refused or tampered live token cannot publish a smaller reservation.
        return StorageCharges()

    @property
    def batch_started_monotonic(self) -> float:
        return self._batch_started

    @property
    def batch_started(self) -> float:
        return self._batch_started

    @property
    def configuration(self) -> Digest:
        return self._configuration_digest

    @property
    def capacity_claim(self) -> "LiveStorageCapacityClaim | LiveStorageInstallationClaim":
        return self._capacity_claim

    def __reduce__(self) -> tuple[object, ...]:
        raise TypeError("live storage reservation cannot be copied or exported")

    def verify(self) -> None:
        self._verify(None)

    def verify_operational(self) -> None:
        """Require the original independent batch timer before creation effects."""
        timer = getattr(self, "_batch_timer", None)
        if type(timer) is not OwnedBatchTimer:
            raise ValueError(
                "original independent batch timer required before operational creation"
            )
        timer.verify()
        self.verify()
        from crewshal.durable import LiveStorageInstallationClaim

        if type(self._capacity_claim) is LiveStorageInstallationClaim and (
            self._capacity_claim.record.state != "preparing"
            or self._capacity_claim._terminal_attempted
        ):
            raise ValueError("installation preparation consumed; no retry or new work")

    def verify_installation(self) -> None:
        """Payload admission requires effective installation, never charge data.

        The bootstrap path deliberately stays closed until a concrete retained
        physical-domain/root/journal producer supplies complete combined growth
        readback. Even an imported 'observed' record cannot supply that owner.
        The existing preinstalled-domain path is unchanged.
        """
        self.verify()
        from crewshal.durable import LiveStorageInstallationClaim

        if type(self._capacity_claim) is LiveStorageInstallationClaim:
            from crewshal.linux_production import EffectiveInstallation

            proof = getattr(self, "_installation", None)
            if type(proof) is not EffectiveInstallation or proof.reservation is not self:
                raise ValueError(
                    "effective installed physical-domain/root/journal growth readback unavailable"
                )
            if (
                self._capacity_claim.record.state != "retained"
                or self._capacity_claim.record.installation != "observed"
                or not self._capacity_claim._terminal_attempted
            ):
                raise ValueError("original actual installation result not retained")
            proof.require_effective_payload_growth()

    def verify_output_admission(self) -> None:
        """Bounded persistent output, never renewed installation preparation."""
        from crewshal.linux_production import EffectiveInstallation
        from crewshal.durable import LiveStorageInstallationClaim

        self.verify()
        proof = getattr(self, "_installation", None)
        if type(proof) is not EffectiveInstallation or proof.reservation is not self:
            raise ValueError("output requires original retained actual installation")
        if (
            type(self._capacity_claim) is not LiveStorageInstallationClaim
            or self._capacity_claim.record.installation != "observed"
        ):
            raise ValueError("output requires observed installation")
        proof.verify_custody()

    def retain_unknown_installation(self) -> None:
        """Keep original handles/charges and consume incomplete preparation."""
        from crewshal.durable import LiveStorageInstallationClaim

        if type(self._capacity_claim) is not LiveStorageInstallationClaim:
            raise ValueError("unknown installation result requires original upfront claim")
        self._capacity_claim.retain_unknown(self)

    def _retain_installation_refusal(self, error: BaseException) -> None:
        from crewshal.durable import LiveStorageInstallationClaim

        if (
            type(self._capacity_claim) is LiveStorageInstallationClaim
            and not self._capacity_claim._terminal_attempted
        ):
            try:
                self.retain_unknown_installation()
            except BaseException as recording_error:
                error.add_note(f"installation outcome remains unknown: {recording_error}")

    def verify_creation_job(self, jobs: object) -> None:
        """Permit only this producer's independently pinned active child.

        Ordinary reservation verification still requires the observer alone.
        Caller PID sets or a transport message cannot grant this exception.
        """
        from crewshal.linux_storage import BoundedStorageJobs

        production = getattr(self, "_production", None)
        if (
            type(jobs) is not BoundedStorageJobs
            or production is None
            or production.jobs is not jobs
        ):
            raise ValueError("creation readback requires original retained producer/job")
        self._verify(jobs.verify_creation_child())

    def _verify(self, creation_child: int | None) -> None:
        if not time.monotonic() < self._batch_started + 600:
            raise ValueError("original storage reservation batch deadline exhausted")
        self._verify_identity()
        sample = self.observer_group.sample()
        expected = {self.observer.spec.pid}
        timer = getattr(self, "_batch_timer", None)
        if timer is not None:
            if type(timer) is not OwnedBatchTimer:
                raise ValueError("original retained batch timer differs")
            timer.verify()
            assert timer.task is not None
            expected.add(timer.task.spec.pid)
        production = getattr(self, "_production", None)
        execution_group = getattr(getattr(production, "jobs", None), "execution_group", None)
        if creation_child is not None and execution_group is None:
            expected.add(creation_child)
        if set(sample.direct_pids) != expected or not sample.populated:
            raise ValueError("storage reservation requires the sole retained live observer")

    def verify_idle_retention(self) -> None:
        """Observe idle custody after the batch; never admit work or release.

        This separate effect-free path does not relax live admission's cutoff.
        It requires the original exited/reaped helper and independently stopped
        operational roles, while preserving full charges and kernel unknowns.
        """
        self._verify_identity()
        timer = getattr(self, "_batch_timer", None)
        if type(timer) is not OwnedBatchTimer:
            raise ValueError("idle retention requires original batch helper")
        timer.verify_idle_retention()
        owners = (getattr(self, "_production", None), self._storage_owner)
        from crewshal.linux_production import OwnedBackingProduction
        from crewshal.linux_storage import BoundedStorageJobs, LinuxPhysicalOwner

        for owner in owners:
            if owner is None:
                continue
            if (
                not isinstance(owner, (OwnedBackingProduction, LinuxPhysicalOwner))
                or type(owner) not in (OwnedBackingProduction, LinuxPhysicalOwner)
                or owner.reservation is not self
            ):
                raise ValueError(
                    "idle retention requires original concrete production/storage owner"
                )
            if type(owner) is OwnedBackingProduction and owner._owners != (self, owner.jobs):
                raise ValueError("idle production owner/job identity differs")
            if type(owner) is LinuxPhysicalOwner and (
                owner.jobs is not owner._jobs
                or owner.retention_readback_jobs is not owner._retention_jobs
            ):
                raise ValueError("idle storage owner/job identity differs")
            for jobs in (
                getattr(owner, "jobs", None),
                getattr(owner, "retention_readback_jobs", None),
            ):
                if jobs is not None and (
                    type(jobs) is not BoundedStorageJobs
                    or jobs.observer is not self.observer
                    or jobs.group is not self.observer_group
                    or jobs.aggregate is not self.aggregate
                    or jobs.execution_group is not timer.setup
                    or jobs.batch_timer is not timer
                    or jobs.pending is not None
                    or jobs._creation_child is not None
                ):
                    raise ValueError("idle retention has unknown or changed operational job")
        lifetimes = (
            tuple(context.setup_lifetime for context in self._lane_contexts)
            if hasattr(self, "_lane_contexts")
            else (self._setup_lifetime,)
        )
        if any(
            lifetime is not None
            and (
                lifetime.storage_reservation is not self
                or lifetime.observer_group is not self.observer_group
                or lifetime.aggregate is not self.aggregate
                or lifetime.wrapper is None
                or lifetime.wrapper.poll() is None
            )
            for lifetime in lifetimes
        ):
            raise ValueError("idle retention has unknown or unreaped namespace wrapper")
        sample = self.observer_group.sample()
        if set(sample.direct_pids) != {self.observer.spec.pid} or not sample.populated:
            raise ValueError("idle retention requires only the original observer")
        # Resample after job/wrapper readback; neither a cached result nor an
        # empty storage scan can supply this process gate or physical closure.
        timer.verify_idle_retention()
        self._verify_identity()
        sample = self.observer_group.sample()
        if set(sample.direct_pids) != {self.observer.spec.pid} or not sample.populated:
            raise ValueError("idle observer repopulated during terminal readback")

    def _verify_identity(self) -> None:
        self._capacity_claim.verify_reservation(self)
        capacity = self._capacity_claim.record
        if (
            capacity.owner != self._observer_digest
            or capacity.configuration != self._charge_configuration_digest
            or capacity.batch_started_monotonic != self._origin
        ):
            raise ValueError("capacity claim differs from original observer/configuration/origin")
        from crewshal.durable import LiveStorageInstallationClaim

        if (
            type(self._capacity_claim) is LiveStorageInstallationClaim
            and getattr(self.observer, "_installation_charge", None) is not self._capacity_claim
        ):
            raise ValueError("installation charge lost original observer binding")
        if (
            any(
                a is not b
                for a, b in zip(
                    self._owners, (self.observer, self.observer_group, self.aggregate), strict=True
                )
            )
            or getattr(self.observer, "_storage_reservation", None) is not self
            or self._charges != StorageCharges()
            or self._batch_started != self._origin
            or self._handles
            != (
                self.observer.descriptor,
                self.observer.pidfd,
                self.observer_group.descriptor,
                self.aggregate.descriptor,
            )
            or record_digest(self._configuration) != self._configuration_digest
            or record_digest(self.observer.spec) != self._observer_digest
            or record_digest(self.observer_group.identity) != self._group_digest
            or record_digest(self.aggregate.identity) != self._aggregate_digest
            or self.observer.spec.configuration != self._charge_configuration_digest
        ):
            raise ValueError("retained storage reservation identity or configuration changed")
        if self._configuration_digest != self._charge_configuration_digest:
            from crewshal.linux_charged_build import verify_observer_configuration

            verify_observer_configuration(self.observer, self._configuration)
        elif getattr(self, "_build_derivation", None) is not None:
            raise ValueError("original helper derivation lost its final configuration")
        _current_source(self._configuration)
        _observer_placement(self.observer, self.observer_group, self.aggregate, ())
        _aggregate_readback(self.aggregate, self.observer_group)
        sample = self.observer_group.sample()
        if (
            any(sample.memory_events[key] for key in ("max", "oom", "oom_kill"))
            or sample.pids_events["max"]
        ):
            raise ValueError("storage reservation observer has resource-refusal history")

    def claim(self, lifetime: "OwnedNamespaceSetup") -> None:
        context = lifetime.lane_context
        if context is not None:
            if type(context) is not RetainedLaneSetup or context.claim_attempted:
                raise ValueError("original lane storage claim consumed; no retry")
            context.claim_attempted = True
            self.verify()
            context.verify_handles()
            if (
                context.reservation is not self
                or context.setup_lifetime is not lifetime
                or lifetime.storage_reservation is not self
                or lifetime.observer_group is not self.observer_group
                or lifetime.aggregate is not self.aggregate
                or lifetime.controls.configuration is not context.configuration
            ):
                raise ValueError("storage claim requires its original lane lifetime")
            context.claimed_lifetime = lifetime
            return
        if hasattr(self, "_lane_contexts"):
            raise ValueError("declared installation cannot claim a singular lifetime")
        if self._claim_attempted:
            raise ValueError("storage reservation claim is one-shot; no retry")
        self._claim_attempted = True
        self.verify()
        if (
            self._setup_lifetime is not lifetime
            or lifetime.storage_reservation is not self
            or lifetime.observer_group is not self.observer_group
            or lifetime.aggregate is not self.aggregate
            or record_digest(lifetime.controls.configuration) != self._configuration_digest
        ):
            raise ValueError("storage reservation requires its original namespace lifetime")
        self._lifetime = lifetime

    def retain(self, resource: object) -> None:
        contexts = getattr(self, "_lane_contexts", None)
        if contexts is not None:
            lifetime = getattr(resource, "lifetime", None)
            context = getattr(lifetime, "lane_context", None)
            if (
                type(context) is not RetainedLaneSetup
                or not any(owner is context for owner in contexts)
                or context.claimed_lifetime is not lifetime
                or context._retained is not None
            ):
                raise ValueError("original claimed lane retains one resource lifetime")
            context._retained = resource
            self.verify()
            context.verify_handles()
            return
        if self._lifetime is None or self._retained is not None:
            raise ValueError("claimed storage reservation retains exactly one resource lifetime")
        self._retained = resource
        self.verify()

    def pin_storage_owner(self, owner: object) -> None:
        """Own constructor refusals before descriptor acquisition/readback."""
        if self._storage_owner is not None:
            raise ValueError("storage owner handoff is one-shot; no reconstruction")
        self._storage_owner = owner
        self.verify()


def reserve_storage_installation(
    store: "CoordinatorStore",
    observer: RetainedTrustedTask,
    observer_group: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: DispatchConfiguration,
    *,
    batch_started_monotonic: float,
) -> OwnedStorageReservation:
    """One upfront original-owner charge; no storage effects or new origin.

    Burn the observer attempt before verification/commit, so a failed commit,
    missing/replaced journal or a fresh store cannot re-enter this attempt.
    The committed claim is retained before reservation construction, including
    constructor refusal. This permits preparation, never payload admission.
    """
    from crewshal.durable import CoordinatorStore

    if type(store) is not CoordinatorStore or type(observer) is not RetainedTrustedTask:
        raise ValueError("installation requires original concrete store and observer")
    if (
        hasattr(observer, "_installation_charge_attempted")
        or hasattr(observer, "_storage_reservation")
        or getattr(observer, "_setup_started", False)
    ):
        raise ValueError("original observer installation attempt consumed; no retry")
    setattr(observer, "_installation_charge_attempted", True)
    if (
        not math.isfinite(batch_started_monotonic)
        or not 0 < batch_started_monotonic <= time.monotonic() < batch_started_monotonic + 120
    ):
        raise ValueError("installation requires original unexpired startup origin")
    _current_source(configuration)
    _observer_placement(observer, observer_group, aggregate, ())
    _aggregate_readback(aggregate, observer_group)
    if observer.spec.configuration != record_digest(configuration):
        raise ValueError("installation observer configuration differs")
    scope = digest(prepare_linux_envelope(configuration).owned_root.encode())
    claim = store.charge_storage_installation(
        scope,
        owner=record_digest(observer.spec),
        configuration=record_digest(configuration),
        batch_started_monotonic=batch_started_monotonic,
    )
    setattr(observer, "_installation_charge", claim)
    try:
        return OwnedStorageReservation(
            observer,
            observer_group,
            aggregate,
            configuration,
            batch_started_monotonic=batch_started_monotonic,
            capacity_claim=claim,
        )
    except BaseException as error:
        # No creation has occurred, but the charge/attempt is still consumed.
        # Journal failure cannot replace the original refusal or permit retry.
        claim._terminal_attempted = True
        try:
            store._retain_unknown_installation(claim)
        except BaseException as recording_error:
            error.add_note(f"installation outcome remains unknown: {recording_error}")
        raise


LANE_IDS = ("qualification-1", "qualification-2", "live")
LANE_ROLES = ("setup", "supervisor", "worker", "validator")


class RetainedLaneSetup:
    """Retain one declared slot under the original observer, charge and timer."""

    reservation: OwnedStorageReservation
    lane_id: str
    setup: OwnedCgroup
    supervisor: OwnedCgroup
    worker: OwnedCgroup
    validator: OwnedCgroup
    setup_lifetime: "OwnedNamespaceSetup | None"
    claimed_lifetime: "OwnedNamespaceSetup | None"
    setup_attempted: bool
    claim_attempted: bool
    _groups: tuple[OwnedCgroup, ...]
    _identities: tuple[Digest, ...]
    _handles: tuple[int, ...]
    _reservation: OwnedStorageReservation
    _lane_id: str
    _registry: tuple["RetainedLaneSetup", ...]
    _configuration: DispatchConfiguration
    _configuration_digest: Digest
    _retained: object | None

    def __init__(self) -> None:
        raise ValueError("lane setup requires original predeclared retained roles")

    def __reduce__(self) -> tuple[object, ...]:
        raise TypeError("original lane setup cannot be copied or exported")

    @property
    def timer(self) -> "OwnedBatchTimer":
        timer = getattr(self.reservation, "_batch_timer", None)
        if type(timer) is not OwnedBatchTimer or not any(
            context is self for context in timer.lanes or ()
        ):
            raise ValueError("lane requires the one original complete-role batch timer")
        return timer

    @property
    def configuration(self) -> DispatchConfiguration:
        return self._configuration

    def verify_handles(self) -> None:
        self._verify_role_handles()
        self.reservation._verify_identity()

    def _verify_role_handles(self) -> None:
        """Verify lane custody without reentering the reservation's timer proof."""
        registered = getattr(self.reservation, "_lane_contexts", None)
        if (
            self.reservation is not self._reservation
            or self.lane_id != self._lane_id
            or self.configuration.lane_id != self.lane_id
            or record_digest(self.configuration) != self._configuration_digest
            or type(registered) is not tuple
            or registered is not self._registry
            or len(registered) != 3
            or tuple(context.lane_id for context in registered) != LANE_IDS
            or not any(context is self for context in registered)
            or self._groups != (self.setup, self.supervisor, self.worker, self.validator)
            or self._identities != tuple(record_digest(group.identity) for group in self._groups)
            or self._handles != tuple(group.descriptor for group in self._groups)
        ):
            raise ValueError("original declared lane context or role handles changed")
        for role, group in zip(LANE_ROLES, self._groups, strict=True):
            group._verify()
            if PurePosixPath(group.identity.relative_path).name != role + "--" + self.lane_id:
                raise ValueError("original lane role name differs")
            _aggregate_readback(self.reservation.aggregate, group)
            if role in ("setup", "supervisor"):
                _role_controls(group)
            else:
                sample = group.sample()
                if any(sample.memory_events.values()) or any(sample.pids_events.values()):
                    raise ValueError("original lane has resource-refusal history")


def reserve_lane_setups(
    reservation: OwnedStorageReservation,
    groups: dict[str, dict[str, OwnedCgroup]],
) -> tuple[RetainedLaneSetup, ...]:
    """Pin exactly three disjoint role sets before the original timer or installation."""
    if (
        type(reservation) is not OwnedStorageReservation
        or hasattr(reservation, "_lane_contexts")
        or hasattr(reservation, "_lane_inputs")
        or (
            hasattr(reservation, "_batch_timer")
            and getattr(reservation._batch_timer, "_early_roles", None) is None
        )
        or getattr(reservation.observer, "_setup_started", False)
        or tuple(groups) != LANE_IDS
        or any(tuple(roles) != LANE_ROLES for roles in groups.values())
    ):
        raise ValueError("original three-lane declaration missing, repeated or reordered")
    reservation.verify()
    setattr(reservation, "_lane_inputs", groups)
    contexts: list[RetainedLaneSetup] = []
    setattr(reservation, "_partial_lane_contexts", contexts)
    for lane_id, roles in groups.items():
        context = object.__new__(RetainedLaneSetup)
        context.reservation = context._reservation = reservation
        context.lane_id = context._lane_id = lane_id
        payload = deepcopy(reservation._configuration.model_dump(mode="json"))
        payload["lane_id"] = lane_id
        context._configuration = DispatchConfiguration.model_validate(payload)
        context._configuration_digest = record_digest(context._configuration)
        context._retained = None
        context.setup, context.supervisor, context.worker, context.validator = (
            roles[role] for role in LANE_ROLES
        )
        context._groups = (context.setup, context.supervisor, context.worker, context.validator)
        context._identities = tuple(record_digest(group.identity) for group in context._groups)
        context._handles = tuple(group.descriptor for group in context._groups)
        context.setup_lifetime = context.claimed_lifetime = None
        context.setup_attempted = context.claim_attempted = False
        contexts.append(context)
    retained = tuple(contexts)
    # Keep each supplied original group before any later independent readback.
    setattr(reservation, "_lane_contexts", retained)
    for context in retained:
        context._registry = retained
    identities = [
        (group.identity.device, group.identity.inode)
        for context in retained
        for group in context._groups
    ]
    if len(set(identities)) != 12 or any(
        identity
        in (
            (reservation.aggregate.identity.device, reservation.aggregate.identity.inode),
            (reservation.observer_group.identity.device, reservation.observer_group.identity.inode),
        )
        for identity in identities
    ):
        raise ValueError("original lane roles are not disjoint")
    for context in retained:
        context.verify_handles()
    timer = getattr(reservation, "_batch_timer", None)
    if timer is not None:
        from crewshal.linux_early_timer import bind_early_timer_lanes

        bind_early_timer_lanes(timer, retained, groups)
    return retained


class OwnedBatchTimer:
    """Original observer's independent timer, charged to its existing role.

    This unqualified source retains the actual helper/proc/pidfd/lifeline and
    pinned operational groups. It never kills the observer or aggregate and
    never releases storage. Missing, expired or changed readback denies creation.
    """

    resources_reusable: Literal[False] = False
    operational_ready: Literal[False] = False
    _early_runtime: "RetainedEarlyTimerRuntime"
    _early_source: int
    _early_origin: int
    _early_transport: dict[str, int]

    def __init__(
        self,
        reservation: OwnedStorageReservation,
        setup: OwnedCgroup,
        supervisor: OwnedCgroup,
        worker: OwnedCgroup,
        *,
        validator: OwnedCgroup | None = None,
        lanes: tuple[RetainedLaneSetup, ...] | None = None,
        early_groups: dict[str, dict[str, OwnedCgroup]] | None = None,
        early_broker: OwnedCgroup | None = None,
    ):
        if hasattr(reservation, "_batch_timer"):
            raise ValueError("independent batch timer is one-shot; no retry or replacement")
        self.reservation, self.setup, self.supervisor, self.worker = (
            reservation,
            setup,
            supervisor,
            worker,
        )
        self.validator = validator
        self.lanes = lanes
        self._lane_owners = lanes
        self._early_roles: tuple[OwnedCgroup, ...] | None = None
        if early_groups is not None:
            if (
                lanes is not None
                or tuple(early_groups) != LANE_IDS
                or any(tuple(roles) != LANE_ROLES for roles in early_groups.values())
                or type(early_broker) is not OwnedCgroup
                or (setup, supervisor, worker, validator)
                != tuple(early_groups[LANE_IDS[0]][role] for role in LANE_ROLES)
            ):
                raise ValueError("early batch timer requires the exact original role mapping")
            self._early_inputs = early_groups
            self._early_mapping = early_groups
            self._early_roles = tuple(
                early_groups[lane][role] for lane in LANE_IDS for role in LANE_ROLES
            ) + (early_broker,)
            self._early_role_owners = self._early_roles
            self._early_handles = tuple(group.descriptor for group in self._early_roles)
            self._early_configuration = reservation.configuration
        if lanes is not None and (
            getattr(reservation, "_lane_contexts", None) is not lanes
            or len(lanes) != 3
            or (setup, supervisor, worker, validator)
            != (lanes[0].setup, lanes[0].supervisor, lanes[0].worker, lanes[0].validator)
        ):
            raise ValueError("batch timer requires original declared lane tuple")
        self._owners = (reservation, setup, supervisor, worker, validator)
        self._groups = tuple(group.identity for group in self.operational_groups)
        self.origin_ns = int(reservation.batch_started_monotonic * 1_000_000_000)
        self._origin = self.origin_ns
        self.cutoff_ns = self.origin_ns + 570_000_000_000
        self.end_ns = self.origin_ns + 600_000_000_000
        self.lifeline = self.helper = -1
        self._helper_identity: tuple[int, int, int] | None = None
        self.lifeline_identity: tuple[int, int] | None = None
        self.process: subprocess.Popen[bytes] | None = None
        self.task: RetainedTrustedTask | None = None
        self._birth: tuple[RetainedTrustedTask | None, subprocess.Popen[bytes] | None] = (
            None,
            None,
        )
        self._task_digest: Digest | None = None
        self.failed = False
        self.complete = False
        # Pin before the first effect, including partial attachment failures.
        setattr(reservation, "_batch_timer", self)

    def __reduce__(self) -> tuple[object, ...]:
        raise TypeError("live batch timer cannot be copied or exported")

    @property
    def operational_groups(self) -> tuple[OwnedCgroup, ...]:
        if self._early_roles is not None:
            return self._early_roles
        if self.lanes is not None:
            return tuple(group for context in self.lanes for group in context._groups)
        groups = (self.setup, self.supervisor, self.worker)
        return groups if self.validator is None else (*groups, self.validator)

    def _verify_validator(self) -> None:
        if self._early_roles is not None:
            from crewshal.linux_early_timer import verify_early_timer_roles

            verify_early_timer_roles(self)
            return
        if self.lanes is not None:
            if (
                self.lanes is not self._lane_owners
                or getattr(self.reservation, "_lane_contexts", None) is not self.lanes
            ):
                raise ValueError("original batch lane tuple changed")
            for context in self.lanes:
                context.verify_handles()
            return
        if self.validator is not None:
            if (
                type(self.validator) is not OwnedCgroup
                or PurePosixPath(self.validator.identity.relative_path).name != "validator"
                or self.validator.identity
                in [
                    group.identity
                    for group in (
                        self.setup,
                        self.supervisor,
                        self.worker,
                        self.reservation.observer_group,
                    )
                ]
            ):
                raise ValueError("original independent validator role differs")
            _aggregate_readback(self.reservation.aggregate, self.validator)
            sample = self.validator.sample()
            if any(sample.memory_events.values()) or any(sample.pids_events.values()):
                raise ValueError("original validator has resource-refusal history")

    def _verify_identity(self) -> None:
        reservation = self.reservation
        if (
            any(
                a is not b
                for a, b in zip(
                    self._owners,
                    (reservation, self.setup, self.supervisor, self.worker, self.validator),
                    strict=True,
                )
            )
            or getattr(reservation, "_batch_timer", None) is not self
            or self._groups != tuple(g.identity for g in self.operational_groups)
            or self.origin_ns != self._origin
            or self._origin != int(reservation.batch_started_monotonic * 1_000_000_000)
            or self.cutoff_ns != self._origin + 570_000_000_000
            or self.end_ns != self._origin + 600_000_000_000
            or not self.complete
            or self.task is None
            or self.process is None
            or self.task is not self._birth[0]
            or self.process is not self._birth[1]
            or record_digest(self.task.spec) != self._task_digest
            or self.process.pid != self.task.spec.pid
            or self.task.spec.parent_pid != reservation.observer.spec.pid
            or self.task.spec.configuration
            != (
                self._early_configuration
                if self._early_roles is not None
                else reservation.configuration
            )
            or self.task.spec.cgroup != reservation.observer_group.identity
            or self.task.spec.namespaces != reservation.observer.spec.namespaces
        ):
            raise ValueError("original batch timer identity or operational cutoff differs")
        self._verify_validator()
        if self._early_roles is not None:
            from crewshal.linux_early_timer import _RUNTIMES

            runtime = _RUNTIMES.get(self)
            if runtime is None or runtime is not getattr(self, "_early_runtime", None):
                raise ValueError("original early timer runtime custody differs")
            runtime.verify()
        helper = os.fstat(self.helper)
        lifeline = os.fstat(self.lifeline)
        if (
            self._helper_identity != (self.helper, helper.st_dev, helper.st_ino)
            or not stat.S_ISREG(helper.st_mode)
            or fcntl.fcntl(self.helper, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
            or self.lifeline_identity != (lifeline.st_dev, lifeline.st_ino)
            or not stat.S_ISFIFO(lifeline.st_mode)
            or fcntl.fcntl(self.lifeline, fcntl.F_GETFL) & os.O_ACCMODE != os.O_WRONLY
        ):
            raise ValueError("original helper/lifeline descriptor custody differs")

    def verify_idle_retention(self) -> None:
        """Require independent original helper cessation and stopped roles.

        This is process/accounting observation only. Original storage handles
        and every kernel reference unknown remain retained, never reusable.
        """
        self._verify_identity()
        assert self.task is not None and self.process is not None
        if time.monotonic_ns() < self.end_ns:
            raise ValueError("idle retention cannot replace the original live batch")
        self.task.verify_handles()
        root = _proc_root(self.task.spec.boot_id)
        try:
            if (
                os.readlink(f"self/fd/{self.task.pidfd}", dir_fd=root) != "anon_inode:[pidfd]"
                or not _terminal_task_exited(self.task)
                or self.process.poll() is None
                or _fields(_read(root, f"self/fdinfo/{self.task.pidfd}")).get("Pid") != "-1"
            ):
                raise ValueError("original batch helper exit/reap remains unknown")
        finally:
            os.close(root)
        reservation = self.reservation
        _observer_placement(
            reservation.observer,
            reservation.observer_group,
            reservation.aggregate,
            self.operational_groups,
        )
        _aggregate_readback(reservation.aggregate, reservation.observer_group)
        _topology(reservation.aggregate, self.setup, self.supervisor, self.worker)
        for group in self.operational_groups:
            if (
                group._read("cgroup.procs")
                or _counters(group._read("cgroup.events"), {"populated"})["populated"] != 0
            ):
                raise ValueError("original operational role is not independently stopped")
        self.task.verify_handles()

    def verify(self) -> None:
        self._verify_identity()
        reservation = self.reservation
        assert self.task is not None and self.process is not None
        if self.failed or self.process.poll() is not None or time.monotonic_ns() >= self.cutoff_ns:
            raise ValueError("original batch timer identity or operational cutoff differs")
        _observer_placement(
            reservation.observer,
            reservation.observer_group,
            reservation.aggregate,
            self.operational_groups,
        )
        _aggregate_readback(reservation.aggregate, reservation.observer_group)
        _topology(reservation.aggregate, self.setup, self.supervisor, self.worker)
        self.task.verify(reservation.observer_group.identity)
        if self._early_roles is not None:
            from crewshal.linux_early_timer import verify_early_timer_readback

            verify_early_timer_readback(self)
            self.task.verify(reservation.observer_group.identity)
            return
        info = os.fstat(self.lifeline)
        if self.lifeline_identity != (info.st_dev, info.st_ino) or not stat.S_ISFIFO(info.st_mode):
            raise ValueError("original batch observer lifeline differs")
        if fcntl.fcntl(self.lifeline, fcntl.F_GETFL) & os.O_ACCMODE != os.O_WRONLY:
            raise ValueError("original batch observer lifeline direction differs")
        directory = os.open(
            "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.task.descriptor
        )
        try:
            group_pairs = [("3", self.worker), ("4", self.supervisor), ("5", self.setup)]
            lifeline_number, timer_number = ("6", "9")
            if self.validator is not None:
                group_pairs.append(("6", self.validator))
                lifeline_number, timer_number = ("7", "10")
            if self.lanes is not None:
                group_pairs = [
                    (str(number), group)
                    for number, group in enumerate(
                        (
                            group
                            for context in self.lanes
                            for group in (
                                context.worker,
                                context.supervisor,
                                context.setup,
                                context.validator,
                            )
                        ),
                        3,
                    )
                ]
                lifeline_number, timer_number = ("15", "18")
            expected_fds = {
                "0",
                "1",
                "2",
                lifeline_number,
                timer_number,
                *(number for number, _ in group_pairs),
            }
            if set(os.listdir(directory)) != expected_fds:
                raise ValueError("batch timer actual descriptor inventory differs")
            for number, group in group_pairs:
                actual = os.stat(number, dir_fd=directory)
                if (actual.st_dev, actual.st_ino) != (group.identity.device, group.identity.inode):
                    raise ValueError("batch timer operational group handle differs")
                flags = int(_fields(_read(self.task.descriptor, f"fdinfo/{number}"))["flags"], 8)
                if flags & os.O_ACCMODE != os.O_RDONLY:
                    raise ValueError("batch timer operational directory direction differs")
            if (
                os.readlink(timer_number, dir_fd=directory) != "anon_inode:[timerfd]"
                or os.readlink(lifeline_number, dir_fd=directory) != f"pipe:[{info.st_ino}]"
                or int(
                    _fields(_read(self.task.descriptor, f"fdinfo/{lifeline_number}"))["flags"], 8
                )
                & (os.O_ACCMODE | os.O_NONBLOCK)
                != os.O_RDONLY
            ):
                raise ValueError("batch timer actual timer/lifeline handles differ")
            for number in ("0", "1", "2"):
                actual = os.stat(number, dir_fd=directory)
                if not stat.S_ISCHR(actual.st_mode) or actual.st_rdev != os.makedev(1, 3):
                    raise ValueError("batch timer stdio must be the verified null device")
        finally:
            os.close(directory)
        before = time.monotonic_ns()
        timer = _fields(_read(self.task.descriptor, f"fdinfo/{timer_number}"))
        after = time.monotonic_ns()
        match = re.fullmatch(r"\(([0-9]+), ([0-9]+)\)", timer.get("it_value", ""))
        if match is None:
            raise ValueError("batch timer remaining timer malformed")
        seconds, nanos = map(int, match.groups())
        remaining = seconds * 1_000_000_000 + nanos
        if (
            nanos >= 1_000_000_000
            or remaining <= 0
            or after < before
            or timer.get("clockid") != "1"
            or timer.get("ticks") != "0"
            or timer.get("settime flags") != "01"
            or timer.get("it_interval") != "(0, 0)"
            or int(timer.get("flags", "0"), 8) & (os.O_ACCMODE | os.O_NONBLOCK | os.O_CLOEXEC)
            != os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC
            or not before + remaining <= self.cutoff_ns <= after + remaining
        ):
            raise ValueError("batch timer effective deadline differs from original reserve")
        self.task.verify(reservation.observer_group.identity)


class BatchTimerRefusal(ValueError):
    def __init__(self, reason: str, lifetime: OwnedBatchTimer):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False
        lifetime.reservation._retain_installation_refusal(self)


def create_owned_batch_timer(
    reservation: OwnedStorageReservation,
    setup: OwnedCgroup,
    supervisor: OwnedCgroup,
    worker: OwnedCgroup,
    preparation: BootstrapPreparation,
    helper_descriptor: int,
    *,
    validator: OwnedCgroup | None = None,
    lanes: tuple[RetainedLaneSetup, ...] | None = None,
) -> OwnedBatchTimer:
    """Unqualified finite creation; no compiler, installation or authority API.

    The installed helper/loader and actual fork/FD/controller behavior must be
    qualified in the separately approved batch. Retain every partial lifetime.
    """
    configuration = reservation._configuration
    preparation = audit_linux_bootstrap(configuration, preparation)
    reservation.verify()
    operational: tuple[OwnedCgroup, ...] = (
        (setup, supervisor, worker) if validator is None else (setup, supervisor, worker, validator)
    )
    if lanes is not None:
        if getattr(reservation, "_lane_contexts", None) is not lanes:
            raise ValueError("batch timer requires original lane declaration")
        operational = tuple(group for context in lanes for group in context._groups)
    _observer_placement(
        reservation.observer,
        reservation.observer_group,
        reservation.aggregate,
        operational,
    )
    _topology(reservation.aggregate, setup, supervisor, worker)
    if preparation.policy.helper_binary is None or any(
        group._read("cgroup.procs")
        or _counters(group._read("cgroup.events"), {"populated"})["populated"]
        for group in operational
    ):
        raise ValueError("batch timer requires current helper and empty original operational roles")
    if getattr(reservation.observer, "_setup_started", False):
        raise ValueError("batch timer must precede operational setup")
    lifetime = OwnedBatchTimer(
        reservation, setup, supervisor, worker, validator=validator, lanes=lanes
    )
    capsule = reading = ready_read = ready_write = -1
    startup_end = min(
        time.monotonic() + 30, reservation.batch_started + 120, reservation.batch_started + 570
    )
    try:
        lifetime._verify_validator()
        lifetime.helper = os.dup(helper_descriptor)
        before = os.fstat(lifetime.helper)
        lifetime._helper_identity = (lifetime.helper, before.st_dev, before.st_ino)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != 0
            or before.st_mode & 0o022
            or not before.st_mode & 0o111
            or not 0 < before.st_size <= 134217728
        ):
            raise ValueError("batch timer requires the retained installed trusted helper")
        sha = hashlib.sha256()
        offset = 0
        while offset < before.st_size:
            if time.monotonic() >= startup_end:
                raise ValueError("original batch timer startup deadline exhausted")
            chunk = os.pread(lifetime.helper, min(65536, before.st_size - offset), offset)
            if not chunk:
                raise ValueError("installed batch helper read incomplete")
            sha.update(chunk)
            offset += len(chunk)
        after = os.fstat(lifetime.helper)
        keys = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_uid",
            "st_gid",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if sha.hexdigest() != preparation.policy.helper_binary or any(
            getattr(before, key) != getattr(after, key) for key in keys
        ):
            raise ValueError("installed batch timer helper bytes/identity differ")
        add, get, seals = _seals()
        capsule = getattr(os, "memfd_create")(
            "crewshal-original-batch-origin",
            getattr(os, "MFD_CLOEXEC") | getattr(os, "MFD_ALLOW_SEALING"),
        )
        if os.write(capsule, struct.pack("=Q", lifetime.origin_ns)) != 8:
            raise ValueError("original batch origin write incomplete")
        fcntl.fcntl(capsule, add, seals)
        if fcntl.fcntl(capsule, get) != seals:
            raise ValueError("original batch origin seal readback differs")
        reading, lifetime.lifeline = getattr(os, "pipe2")(os.O_CLOEXEC)
        info = os.fstat(lifetime.lifeline)
        lifetime.lifeline_identity = (info.st_dev, info.st_ino)
        ready_read, ready_write = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
        inputs = (
            worker.descriptor,
            supervisor.descriptor,
            setup.descriptor,
            *((validator.descriptor,) if validator is not None else ()),
            reading,
            ready_write,
            capsule,
        )
        mode = "--batch-timer-fds" if validator is None else "--batch-timer-validator-fds"
        if lanes is not None:
            inputs = (
                *(
                    group.descriptor
                    for context in lanes
                    for group in (
                        context.worker,
                        context.supervisor,
                        context.setup,
                        context.validator,
                    )
                ),
                reading,
                ready_write,
                capsule,
            )
            mode = "--batch-timer-lanes-fds"
        argv = ["/bin/crewshal-bootstrap", mode, *map(str, inputs)]
        lifetime.process = subprocess.Popen(
            argv,
            executable=f"/proc/self/fd/{lifetime.helper}",
            pass_fds=(*inputs, lifetime.helper),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={},
            cwd="/",
            close_fds=True,
        )
        os.close(reading)
        reading = -1
        os.close(ready_write)
        ready_write = -1
        root = _proc_root(reservation.observer.spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, lifetime.process.pid)
            pid, _, parent, ticks = _stat_identity(_read(descriptor, "stat"))
            spec = TrustedTaskSpec(
                configuration=reservation.configuration,
                pid=pid,
                parent_pid=parent,
                start_ticks=ticks,
                boot_id=reservation.observer.spec.boot_id,
                cgroup=reservation.observer_group.identity,
                namespaces=reservation.observer.spec.namespaces,
                executable=preparation.policy.helper_binary,
                argv=argv,
                environment={},
                capabilities=reservation.observer.spec.capabilities,
                placement="outer_observer",
                cwd="/",
            )
            lifetime.task = RetainedTrustedTask(descriptor, pidfd, spec)
            lifetime._birth = (lifetime.task, lifetime.process)
            lifetime._task_digest = record_digest(lifetime.task.spec)
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)
        raw = bytearray()
        while True:
            if time.monotonic() >= startup_end or lifetime.process.poll() is not None:
                raise ValueError("original batch timer startup deadline exhausted")
            if not _wait_ready([ready_read], [], [], min(0.001, startup_end - time.monotonic()))[0]:
                continue
            chunk = os.read(ready_read, 129)
            raw.extend(chunk)
            if len(raw) > 128:
                raise ValueError("batch timer readiness exceeds bounded record")
            if not chunk:
                break
        if raw != f"BATCH {lifetime.origin_ns} {lifetime.cutoff_ns} {lifetime.end_ns}\n".encode():
            raise ValueError("batch timer readiness differs from original sealed origin")
        lifetime.complete = True
        reservation.verify_operational()
        return lifetime
    except BaseException as error:
        lifetime.failed = True
        raise BatchTimerRefusal(str(error), lifetime) from error
    finally:
        for handle in (capsule, reading, ready_read, ready_write):
            if handle >= 0:
                os.close(handle)


class NamespaceSetupPreparation(Contract):
    configuration: Digest
    lane_id: Literal["qualification-1", "qualification-2", "live"] | None = None
    bootstrap: Digest
    parent_argv: list[str]
    parent_executable: Digest
    namespace_argv: list[str]
    control_fds: dict[str, int]
    validator_control: bool = False
    bridge_control: bool = False
    policy_control: bool = False
    network_control: bool = False
    setup_controls: dict[str, str]
    parent_inventory: TrustedParentInventory | None = None
    unresolved: list[str]
    execution_allowed: Literal[False] = False
    profile_qualified: Literal[False] = False


def prepare_namespace_setup(
    configuration: DispatchConfiguration,
    bootstrap: BootstrapPreparation,
    parent_argv: list[str],
    parent_executable: Digest,
    *,
    parent_inventory: TrustedParentInventory | None = None,
    validator_control: bool = False,
    bridge_control: bool = False,
    policy_control: bool = False,
    network_control: bool = False,
) -> NamespaceSetupPreparation:
    """Passive trusted-parent fragment. It never substitutes for native argv."""
    bootstrap = audit_linux_bootstrap(configuration, bootstrap)
    if bridge_control and not validator_control:
        raise ValueError("original bridge requires independent validator control")
    if policy_control and not bridge_control:
        raise ValueError("loaded policy control requires original bridge and validator")
    if network_control and not policy_control:
        raise ValueError("retained provider network requires loaded policy control")
    if (
        parent_inventory is None
        and configuration.linux_envelope is not None
        and configuration.linux_envelope.parent_inventory_sha256 is not None
    ):
        raise ValueError("bound parent inventory cannot be omitted from namespace setup")
    if parent_inventory is not None:
        parent_inventory = bind_parent_inventory(
            configuration,
            parent_inventory,
            parent_argv,
            parent_executable,
            bootstrap.policy.helper_binary,
        )
    if (
        not parent_argv
        or not PurePosixPath(parent_argv[0]).is_absolute()
        or any(not value or "\x00" in value for value in parent_argv)
        or parent_argv[0] in {"/opt/codex/bin/codex", "/usr/bin/bwrap", "/bin/crewshal-bootstrap"}
    ):
        raise ValueError("explicit qualified namespace-parent program required")
    envelope = prepare_linux_envelope(configuration)
    command = ["/usr/bin/bwrap"]
    for mount in envelope.mounts["native"]:
        # The shm overmount must follow bwrap's fresh /dev, as in the envelope.
        if mount.target != "/dev/shm":
            command += ["--ro-bind" if mount.readonly else "--bind", mount.source, mount.target]
    # Only this privileged setup parent needs source views for later role
    # sandboxes. Their separately constructed roots do not project this view.
    command += ["--bind", envelope.owned_root, envelope.owned_root]
    if configuration.lane_id is not None:
        vendor = next(mount.source for mount in envelope.mounts["native"] if mount.target == "/")
        command += ["--ro-bind", vendor, vendor]
    command += [
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--unshare-pid",
        *([] if network_control else ["--unshare-net"]),
        "--unshare-ipc",
        "--unshare-uts",
        "--new-session",
        "--die-with-parent",
        "--clearenv",
        "--chdir",
        native_working_directory(configuration),
    ]
    for mount in envelope.mounts["native"]:
        if mount.target == "/dev/shm":
            command += ["--ro-bind", mount.source, mount.target]
    command += ["--cap-drop", "ALL"]
    for name in ("SETGID", "SETUID", "SETPCAP", "SYS_PTRACE", "SYS_ADMIN"):
        command += ["--cap-add", "CAP_" + name]
    # Bwrap introduces PWD even with clearenv. Remove it before the exact parent.
    command += [
        "--",
        "/usr/bin/env",
        "-i",
        "/bin/setpriv",
        "--reuid=0",
        "--regid=0",
        "--clear-groups",
        "--inh-caps=-all",
        "--ambient-caps=-all",
        "--no-new-privs",
        "--",
        *parent_argv,
    ]
    return NamespaceSetupPreparation(
        configuration=record_digest(configuration),
        lane_id=configuration.lane_id,
        bootstrap=record_digest(bootstrap),
        parent_argv=list(parent_argv),
        parent_executable=parent_executable,
        namespace_argv=command,
        control_fds={
            "sealed_configuration": 3,
            "aggregate": 4,
            "setup": 5,
            "supervisor": 6,
            "worker": 7,
            **({"validator": 8} if validator_control else {}),
            **({"bridge": 9} if bridge_control else {}),
            **({"apparmor_namespace": 10, "compiled_policy": 11} if policy_control else {}),
            **({"provider_network": 12} if network_control else {}),
            **({"apparmor_export": 13} if network_control else {}),
        },
        validator_control=validator_control,
        bridge_control=bridge_control,
        policy_control=policy_control,
        network_control=network_control,
        setup_controls=dict(envelope.aggregate_controls),
        parent_inventory=parent_inventory,
        unresolved=[
            "qualified_parent_program_and_root_library_inventory",
            "exact_bwrap_init_wrapper_fd_and_role_readback",
            "mediated_network_policy_in_fresh_namespace_before_worker",
            "owned_storage_mount_key_backing_terminal_cleanup",
            *bootstrap.unresolved,
        ],
    )


class InheritedControls(Contract):
    configuration: DispatchConfiguration
    bootstrap: BootstrapPreparation
    setup: NamespaceSetupPreparation
    boot_id: str
    outer_namespaces: dict[str, NamespaceIdentity]
    groups: dict[str, CgroupIdentity]
    batch_origin_ns: int | None = None
    bridge_identity: NamespaceIdentity | None = None
    apparmor_namespace: NamespaceIdentity | None = None
    compiled_policy_sha256: Digest | None = None
    apparmor_roles: list[tuple[str, str, NamespaceIdentity]] | None = None
    provider_network: NamespaceIdentity | None = None
    apparmor_export: NamespaceIdentity | None = None


def _validator_role_name(configuration: DispatchConfiguration) -> str:
    lane = configuration.lane_id
    return "validator" if lane is None else "validator--" + lane


def _role_controls(group: OwnedCgroup) -> None:
    group._verify()
    for name, expected in {
        "memory.max": "805306368",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "pids.max": "128",
        "cgroup.type": "domain",
    }.items():
        if group._read(name) != expected:
            raise ValueError("setup/supervisor controls differ from original aggregate ceiling")
    for name, keys in (("memory.events", {"max", "oom", "oom_kill"}), ("pids.events", {"max"})):
        if any(_counters(group._read(name), keys)[key] for key in keys):
            raise ValueError("setup/supervisor has resource-refusal history")


def _topology(
    aggregate: OwnedCgroup, setup: OwnedCgroup, supervisor: OwnedCgroup, worker: OwnedCgroup
) -> None:
    if (
        len({(g.identity.device, g.identity.inode) for g in (aggregate, setup, supervisor, worker)})
        != 4
    ):
        raise ValueError("setup roles require distinct retained groups")
    for group in (setup, supervisor, worker):
        _aggregate_readback(aggregate, group)
    _role_controls(setup)
    _role_controls(supervisor)
    worker.sample()


def _seals() -> tuple[int, int, int]:
    if sys.platform != "linux" or not hasattr(os, "memfd_create"):
        raise ValueError("Linux sealed control transport unavailable")
    return (
        getattr(fcntl, "F_ADD_SEALS"),
        getattr(fcntl, "F_GET_SEALS"),
        sum(
            getattr(fcntl, key)
            for key in ("F_SEAL_WRITE", "F_SEAL_GROW", "F_SEAL_SHRINK", "F_SEAL_SEAL")
        ),
    )


def _capsule(controls: InheritedControls) -> int:
    add, get, seals = _seals()
    raw = controls.model_dump_json().encode()
    if not 0 < len(raw) <= CONTROL_BOUND:
        raise ValueError("inherited configuration exceeds sealed transport bound")
    create = getattr(os, "memfd_create")
    handle: int = create(
        "crewshal-owned-controls", getattr(os, "MFD_CLOEXEC") | getattr(os, "MFD_ALLOW_SEALING")
    )
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(handle, raw[offset:])
            if written <= 0:
                raise ValueError("inherited configuration write incomplete")
            offset += written
        fcntl.fcntl(handle, add, seals)
        if fcntl.fcntl(handle, get) != seals:
            raise ValueError("inherited configuration seals differ")
        return handle
    except BaseException:
        os.close(handle)
        raise


def _compiled_policy_capsule(raw: bytes) -> int:
    from crewshal.linux_payload_storage import POLICY_LIMIT

    if not raw or len(raw) > POLICY_LIMIT:
        raise ValueError("compiled policy capsule exceeds its original bound")
    add, get, seals = _seals()
    descriptor = getattr(os, "memfd_create")(
        "crewshal-original-compiled-policy",
        getattr(os, "MFD_ALLOW_SEALING") | getattr(os, "MFD_CLOEXEC"),
    )
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(descriptor, raw[offset:])
            if written <= 0:
                raise ValueError("compiled policy capsule write incomplete")
            offset += written
        fcntl.fcntl(descriptor, add, seals)
        if fcntl.fcntl(descriptor, get) != seals:
            raise ValueError("compiled policy capsule seals differ")
        readonly = os.open(f"/proc/self/fd/{descriptor}", os.O_RDONLY | os.O_CLOEXEC)
        if fcntl.fcntl(readonly, get) != seals:
            os.close(readonly)
            raise ValueError("readonly compiled policy capsule seals differ")
        return readonly
    finally:
        os.close(descriptor)


_NAMESPACE_POLICIES: dict[
    int, tuple[InheritedControls, list[int], "RetainedAppArmorExport | None"]
] = {}


def receive_namespace_policy(controls: InheritedControls) -> "RetainedAppArmorExport":
    """Retain actual fixed policy inputs once. Refusal retains every opened handle."""
    from crewshal.linux_payload_storage import POLICY_LIMIT, PROFILE_NAMES, RetainedAppArmorExport

    if not controls.setup.policy_control or id(controls) in _NAMESPACE_POLICIES:
        raise ValueError("original namespace policy inputs unavailable or consumed")
    retained: list[int] = []
    _NAMESPACE_POLICIES[id(controls)] = controls, retained, None
    try:
        namespace = os.dup(10)
        retained.append(namespace)
        capsule = os.dup(11)
        retained.append(capsule)
        raw_export = os.dup(13) if controls.setup.network_control else -1
        if raw_export >= 0:
            retained.append(raw_export)
        _, get, seals = _seals()
        info = os.fstat(capsule)
        identity = controls.apparmor_namespace
        observed = os.fstat(namespace)
        if (
            identity is None
            or not stat.S_ISDIR(observed.st_mode)
            or (observed.st_dev, observed.st_ino) != (identity.device, identity.inode)
            or fcntl.fcntl(namespace, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
            or not stat.S_ISREG(info.st_mode)
            or info.st_uid != 0
            or not 0 < info.st_size <= POLICY_LIMIT
            or fcntl.fcntl(capsule, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
            or fcntl.fcntl(capsule, get) != seals
        ):
            raise ValueError("original readonly sealed policy inputs differ")
        raw = os.pread(capsule, info.st_size + 1, 0)
        roles = controls.apparmor_roles
        if (
            len(raw) != info.st_size
            or digest(raw) != controls.compiled_policy_sha256
            or roles is None
            or tuple(name for name, _, _ in roles) != PROFILE_NAMES
        ):
            raise ValueError("original complete compiled policy or role inventory differs")
        role_names = tuple((name, directory) for name, directory, _ in roles)
        if raw_export >= 0:
            observed_export = os.fstat(raw_export)
            original_export = controls.apparmor_export
            if original_export is None or (observed_export.st_dev, observed_export.st_ino) != (
                original_export.device,
                original_export.inode,
            ):
                raise ValueError("original readonly AppArmor export identity changed")
            policy = RetainedAppArmorExport.retain_inherited(namespace, raw, role_names, raw_export)
        else:
            policy = RetainedAppArmorExport.retain(namespace, raw, role_names)
        if tuple(identity for _, _, identity in policy.roles) != tuple(
            (identity.device, identity.inode) for _, _, identity in roles
        ):
            raise ValueError("original AppArmor role directory identity changed")
        _NAMESPACE_POLICIES[id(controls)] = controls, retained, policy
        return policy
    finally:
        for descriptor in (10, 11):
            os.close(descriptor)
        if controls.setup.network_control:
            os.close(13)


_PARENT_NETWORKS: dict[int, tuple[InheritedControls, int]] = {}


def receive_namespace_network(controls: InheritedControls) -> int:
    from crewshal.linux_network import _net_namespace

    if not controls.setup.network_control or id(controls) in _PARENT_NETWORKS:
        raise ValueError("original parent provider network unavailable or consumed")
    descriptor = os.dup(12)
    _PARENT_NETWORKS[id(controls)] = controls, descriptor
    try:
        expected = controls.provider_network
        if expected is None or _net_namespace(descriptor) != (expected.device, expected.inode):
            raise ValueError("original parent provider network identity differs")
        return descriptor
    finally:
        os.close(12)


@dataclass
class OwnedNamespaceSetup:
    wrapper: subprocess.Popen[bytes] | None
    controls: InheritedControls
    aggregate: OwnedCgroup
    setup: OwnedCgroup
    supervisor: OwnedCgroup
    worker: OwnedCgroup
    observer_group: OwnedCgroup
    # The outer wrapper is never a native child handle. Physical resources are
    # not reusable from process observations; no unmount/key deletion is supplied.
    resources_reusable: Literal[False] = False
    recovery_deadline: float | None = None
    physical_teardown_claimed: bool = False
    storage_reservation: OwnedStorageReservation | None = None
    validator: OwnedCgroup | None = None
    lane_context: RetainedLaneSetup | None = None


class NamespaceSetupRefusal(ValueError):
    def __init__(self, reason: str, lifetime: OwnedNamespaceSetup):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False


def retained_setup_scope(
    reservation: OwnedStorageReservation,
    lifetime: OwnedNamespaceSetup | None = None,
    *,
    context: RetainedLaneSetup | None = None,
) -> OwnedStorageReservation | RetainedLaneSetup:
    """Select original custody. A lane name or receipt cannot select its owner."""
    if lifetime is not None:
        selected = getattr(lifetime, "lane_context", None)
        if context is not None and selected is not context:
            raise ValueError("original namespace lane context differs")
        context = selected
    contexts = getattr(reservation, "_lane_contexts", None)
    groups: tuple[OwnedCgroup, OwnedCgroup, OwnedCgroup, OwnedCgroup | None]
    if contexts is not None:
        if (
            type(context) is not RetainedLaneSetup
            or context.reservation is not reservation
            or not any(item is context for item in contexts)
        ):
            raise ValueError("original retained lane context required")
        context.verify_handles()
        from crewshal.linux_schedule import OwnedThreeLaneSchedule

        schedule = getattr(reservation, "_lane_schedule", None)
        if type(schedule) is not OwnedThreeLaneSchedule:
            raise ValueError("original lane schedule is unavailable")
        schedule.require_active(context, lifetime=lifetime)
        scope: OwnedStorageReservation | RetainedLaneSetup = context
        configuration = context.configuration
        groups = context.setup, context.supervisor, context.worker, context.validator
    else:
        if context is not None:
            raise ValueError("undeclared lane context cannot select original custody")
        scope = reservation
        configuration = reservation._configuration
        timer = reservation._batch_timer
        groups = timer.setup, timer.supervisor, timer.worker, timer.validator
    if lifetime is not None and (
        getattr(scope, "setup_lifetime" if context is not None else "_setup_lifetime", None)
        is not lifetime
        or lifetime.storage_reservation is not reservation
        or lifetime.controls.configuration != configuration
        or lifetime.aggregate is not reservation.aggregate
        or (lifetime.setup, lifetime.supervisor, lifetime.worker, lifetime.validator) != groups
        or lifetime.observer_group is not reservation.observer_group
    ):
        raise ValueError("original namespace lifetime or retained lane roles differ")
    return scope


def retained_lane_handle(lifetime: OwnedNamespaceSetup, name: str) -> str:
    """Use the exact declared lane for an original installed volume handle."""
    context = getattr(lifetime, "lane_context", None)
    if context is None:
        return "mounted:" + name
    if (
        type(context) is not RetainedLaneSetup
        or lifetime.controls.configuration is not context.configuration
    ):
        raise ValueError("original installed lane handle context differs")
    return "mounted:" + context.lane_id + "--" + name


def create_namespace_setup(
    observer: RetainedTrustedTask,
    observer_group: OwnedCgroup,
    aggregate: OwnedCgroup,
    setup: OwnedCgroup,
    supervisor: OwnedCgroup,
    worker: OwnedCgroup,
    configuration: DispatchConfiguration,
    bootstrap: BootstrapPreparation,
    preparation: NamespaceSetupPreparation,
    *,
    inventory: RetainedParentInventory | None = None,
    storage_reservation: OwnedStorageReservation | None = None,
    storage_owner: "LinuxPhysicalOwner | None" = None,
    validator: OwnedCgroup | None = None,
    bridge: "StoppedNativeBridge | None" = None,
    lane_context: RetainedLaneSetup | None = None,
    policy: "RetainedAppArmorExport | None" = None,
    networks: "OwnedProviderNetworks | None" = None,
) -> OwnedNamespaceSetup:
    """Unqualified source: fork wrapper/init inside setup, return observer outside.

    The root observer is single-threaded in a bounded aggregate sibling.
    The helper moves only its child into setup before namespace effects;
    the observer never enters a stopped role. The inherited child moves to the
    supervisor before creating the watchdog. No child is migrated by numeric PID.
    """
    schedule = None
    if lane_context is not None:
        from crewshal.linux_schedule import OwnedThreeLaneSchedule

        schedule = getattr(storage_reservation, "_lane_schedule", None)
        if (
            type(lane_context) is not RetainedLaneSetup
            or type(schedule) is not OwnedThreeLaneSchedule
            or lane_context.reservation is not storage_reservation
            or configuration is not lane_context.configuration
            or (setup, supervisor, worker, validator)
            != (
                lane_context.setup,
                lane_context.supervisor,
                lane_context.worker,
                lane_context.validator,
            )
            or lane_context.setup_attempted
        ):
            raise ValueError("namespace setup requires original unused active lane")
        schedule.require_active(lane_context)
        lane_context.verify_handles()
    elif configuration.lane_id is not None or getattr(storage_reservation, "_lane_contexts", None):
        raise ValueError("three-lane installation requires its exact active context")
    if storage_reservation is not None:
        # This check precedes wrapper/helper/native/watchdog/validator effects.
        # A preparing or serialized installation result cannot cross it.
        storage_reservation.verify_installation()
    expected = prepare_namespace_setup(
        configuration,
        bootstrap,
        preparation.parent_argv,
        preparation.parent_executable,
        parent_inventory=preparation.parent_inventory,
        validator_control=validator is not None,
        bridge_control=bridge is not None,
        policy_control=policy is not None,
        network_control=networks is not None,
    )
    if preparation.parent_inventory is not None:
        if inventory is None or inventory.inventory != preparation.parent_inventory:
            raise ValueError("bound setup requires its retained trusted root inventory")
        inventory.verify()
        if not os.fstatvfs(inventory.descriptor).f_flag & os.ST_RDONLY:
            raise ValueError("bound setup requires actual retained readonly root mount")
    elif inventory is not None:
        raise ValueError("retained root requires exact bound parent inventory")
    if (
        expected != preparation
        or bootstrap.policy.helper_binary is None
        or configuration.linux_envelope is None
        or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(bootstrap.policy)
    ):
        raise ValueError("namespace setup requires current exact source/helper bindings")
    _current_source(configuration)
    operational: tuple[OwnedCgroup, ...] = (
        (setup, supervisor, worker) if validator is None else (setup, supervisor, worker, validator)
    )
    _observer_placement(observer, observer_group, aggregate, operational)
    observer_configuration = (
        storage_reservation._configuration
        if lane_context is not None and storage_reservation is not None
        else configuration
    )
    from crewshal.linux_charged_build import verify_observer_configuration

    verify_observer_configuration(observer, observer_configuration)
    _aggregate_readback(aggregate, observer_group)
    observer_group.sample()
    observer_pids = {str(observer.spec.pid)}
    timer = getattr(storage_reservation, "_batch_timer", None)
    if timer is not None:
        if type(timer) is not OwnedBatchTimer:
            raise ValueError("namespace setup requires original batch timer")
        timer.verify()
        assert timer.task is not None
        if lane_context is not None:
            if lane_context.timer is not timer:
                raise ValueError("namespace setup lane timer differs")
        elif (
            timer.setup is not setup
            or timer.supervisor is not supervisor
            or timer.worker is not worker
            or timer.validator is not validator
        ):
            raise ValueError("namespace setup batch timer operational roles differ")
        observer_pids.add(str(timer.task.spec.pid))
    if set(observer_group._read("cgroup.procs").split()) != observer_pids:
        raise ValueError("bounded outer observer role must contain only original observer/timer")
    _topology(aggregate, setup, supervisor, worker)
    for group in operational:
        if (
            group._read("cgroup.procs")
            or _counters(group._read("cgroup.events"), {"populated"})["populated"]
        ):
            raise ValueError("owned namespace setup requires empty fresh role groups")
    if lane_context is None and getattr(observer, "_setup_started", False):
        raise ValueError("namespace setup is one-shot; no retry or reset")
    if storage_reservation is not None:
        storage_reservation.verify()
        if (
            storage_reservation.observer is not observer
            or storage_reservation.observer_group is not observer_group
            or storage_reservation.aggregate is not aggregate
            or (
                lane_context is None
                and storage_reservation._configuration_digest != record_digest(configuration)
            )
        ):
            raise ValueError("namespace setup storage reservation differs")
    if validator is not None:
        if (
            type(validator) is not OwnedCgroup
            or PurePosixPath(validator.identity.relative_path).name
            != _validator_role_name(configuration)
            or validator.identity
            in [group.identity for group in (aggregate, observer_group, setup, supervisor, worker)]
        ):
            raise ValueError("namespace setup original validator role differs")
        _aggregate_readback(aggregate, validator)
        validator.sample()
    namespace_fd: int | None = None
    if storage_owner is not None:
        from crewshal.linux_storage import LinuxPhysicalOwner

        if (
            type(storage_owner) is not LinuxPhysicalOwner
            or storage_reservation is None
            or storage_reservation._storage_owner is not storage_owner
        ):
            raise ValueError("namespace setup requires its original concrete storage owner")
        storage_owner.verify_retention(storage_reservation)
        namespace_fd = storage_owner.handles["namespace"]
    if validator is not None and namespace_fd is None:
        raise ValueError("validator control requires original installed storage namespace")
    if bridge is not None:
        from crewshal.linux_bridge import StoppedNativeBridge

        if (
            type(bridge) is not StoppedNativeBridge
            or storage_reservation is None
            or getattr(
                lane_context if lane_context is not None else storage_reservation._installation,
                "_bridge",
                None,
            )
            is not bridge
            or bridge.installation is not storage_reservation._installation
            or getattr(bridge, "lane_context", None) is not lane_context
            or validator is None
            or namespace_fd is None
        ):
            raise ValueError("namespace setup requires original stopped-native bridge")
        bridge._verify_original()
        if (
            bridge.child_channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            != socket.SOCK_SEQPACKET
        ):
            raise ValueError("original bridge socket type differs")
    network_fd: int | None = None
    if networks is not None:
        from crewshal.linux_network import OwnedProviderNetworks

        if (
            type(networks) is not OwnedProviderNetworks
            or networks.reservation is not storage_reservation
            or lane_context is None
        ):
            raise ValueError("original installed provider network owner required")
        networks.readback()
        network_fd = networks.namespaces[lane_context.lane_id]
    observer._setup_started = True
    if lane_context is not None:
        lane_context.setup_attempted = True
    controls = InheritedControls(
        configuration=configuration,
        bootstrap=bootstrap,
        setup=preparation,
        boot_id=observer.spec.boot_id,
        batch_origin_ns=timer.origin_ns if type(timer) is OwnedBatchTimer else None,
        bridge_identity=(
            NamespaceIdentity(
                device=os.fstat(bridge.child_channel.fileno()).st_dev,
                inode=os.fstat(bridge.child_channel.fileno()).st_ino,
            )
            if bridge is not None
            else None
        ),
        apparmor_namespace=(
            NamespaceIdentity(
                device=policy.namespace_identity[0], inode=policy.namespace_identity[1]
            )
            if policy is not None
            else None
        ),
        compiled_policy_sha256=digest(policy.expected_binary) if policy is not None else None,
        apparmor_export=(
            NamespaceIdentity(
                device=policy.raw_export_identity[0], inode=policy.raw_export_identity[1]
            )
            if policy is not None and network_fd is not None
            else None
        ),
        apparmor_roles=(
            [
                (name, directory, NamespaceIdentity(device=identity[0], inode=identity[1]))
                for name, directory, identity in policy.roles
            ]
            if policy is not None
            else None
        ),
        provider_network=(
            NamespaceIdentity(device=os.fstat(network_fd).st_dev, inode=os.fstat(network_fd).st_ino)
            if network_fd is not None
            else None
        ),
        outer_namespaces=observer.spec.namespaces,
        groups={
            name: group.identity
            for name, group in (
                ("aggregate", aggregate),
                ("setup", setup),
                ("supervisor", supervisor),
                ("worker", worker),
                *((("validator", validator),) if validator is not None else ()),
            )
        },
    )
    lifetime = OwnedNamespaceSetup(
        None,
        controls,
        aggregate,
        setup,
        supervisor,
        worker,
        observer_group,
        storage_reservation=storage_reservation,
        validator=validator,
        lane_context=lane_context,
    )
    if lane_context is not None:
        lane_context.setup_lifetime = lifetime
        assert schedule is not None
        schedule.bind_lifetime(lane_context, lifetime)
    elif storage_reservation is not None:
        storage_reservation._setup_lifetime = lifetime
    capsule = _capsule(controls)
    policy_capsule = -1
    try:
        if policy is not None:
            from crewshal.linux_payload_storage import RetainedAppArmorExport, PROFILE_NAMES

            if (
                type(policy) is not RetainedAppArmorExport
                or tuple(name for name, _, _ in policy.roles) != PROFILE_NAMES
            ):
                raise ValueError("original complete loaded AppArmor policy custody required")
            policy.check_policy()
            policy_capsule = _compiled_policy_capsule(policy.expected_binary)
            setattr(lifetime, "_apparmor_export", policy)
        descriptors = (
            capsule,
            aggregate.descriptor,
            setup.descriptor,
            supervisor.descriptor,
            worker.descriptor,
            *((validator.descriptor,) if validator is not None else ()),
            *((bridge.child_channel.fileno(),) if bridge is not None else ()),
            *((namespace_fd,) if namespace_fd is not None else ()),
            *((policy.namespace, policy_capsule) if policy is not None else ()),
            *((network_fd,) if network_fd is not None else ()),
            *((policy.raw_export,) if network_fd is not None and policy is not None else ()),
        )
        lifetime.wrapper = subprocess.Popen(
            [
                "/bin/crewshal-bootstrap",
                "--namespace-validator-bridge-policy-export-network-source-fds"
                if network_fd is not None
                else "--namespace-validator-bridge-policy-source-fds"
                if policy is not None
                else "--namespace-validator-bridge-source-fds"
                if bridge is not None
                else "--namespace-validator-source-fds"
                if validator is not None
                else "--namespace-source-fds"
                if namespace_fd is not None
                else "--namespace-fds",
                *(str(descriptor) for descriptor in descriptors),
                "--",
                *preparation.namespace_argv,
            ],
            # argv[0] remains the fixed namespace identity, while the
            # outer exec resolves the actual copied helper through custody.
            # C normalizes only its named controls and closes this extra
            # root FD before bwrap; it never reaches the namespace parent.
            executable=(
                f"/proc/self/fd/{inventory.descriptor}/bin/crewshal-bootstrap"
                if inventory is not None
                else "/bin/crewshal-bootstrap"
            ),
            pass_fds=(
                (*descriptors, inventory.descriptor) if inventory is not None else descriptors
            ),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={},
            close_fds=True,
            # The outer wrapper runs before bwrap constructs namespace-local
            # candidate/scratch targets. Only bwrap's --chdir establishes the
            # exact parent cwd; never require that path on the operator host.
            cwd="/",
        )
        # Only the helper child enters setup through its retained FD. The
        # original observer never joins a role that terminal recovery stops.
        _observer_placement(observer, observer_group, aggregate, operational)
        return lifetime
    except BaseException as error:
        raise NamespaceSetupRefusal(str(error), lifetime) from error
    finally:
        os.close(capsule)
        if policy_capsule >= 0:
            os.close(policy_capsule)


def _move_self_to_observer(observer: RetainedTrustedTask, group: OwnedCgroup) -> None:
    _move_self(group)
    observer.verify(group.identity)


def _observer_placement(
    observer: RetainedTrustedTask,
    group: OwnedCgroup,
    aggregate: OwnedCgroup,
    targets: tuple[OwnedCgroup, ...],
) -> None:
    observer.verify(group.identity)
    group._verify()
    aggregate._verify()
    if (
        observer.spec.pid != os.getpid()
        or observer.spec.cgroup != group.identity
        or group.identity in [target.identity for target in targets]
        or PurePosixPath(group.identity.relative_path).parent
        != PurePosixPath(aggregate.identity.relative_path)
    ):
        raise ValueError(
            "outer observer must remain in its owned aggregate sibling outside stopped roles"
        )
    handle = os.open(
        "..", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=group.descriptor
    )
    try:
        info = os.fstat(handle)
        if (info.st_dev, info.st_ino) != (aggregate.identity.device, aggregate.identity.inode):
            raise ValueError("outer observer actual aggregate ancestry differs")
    finally:
        os.close(handle)


def receive_namespace_controls() -> tuple[InheritedControls, dict[str, OwnedCgroup]]:
    """Read fixed sealed controls once, independently attach groups, close originals.

    The namespace parent must derive its own actual PID/start/namespace role,
    verify its program, move itself setup->supervisor and establish effective
    policies before creating the watchdog. Capsule data cannot assert that work.
    """
    _, get, seals = _seals()
    groups: dict[str, OwnedCgroup] = {}
    roles: tuple[str, ...] = ("aggregate", "setup", "supervisor", "worker")
    try:
        info = os.fstat(3)
        if (
            not stat.S_ISREG(info.st_mode)
            or not 0 < info.st_size <= CONTROL_BOUND
            or fcntl.fcntl(3, get) != seals
        ):
            raise ValueError("namespace control capsule must be bounded and immutable")
        raw = os.pread(3, info.st_size + 1, 0)
        if len(raw) != info.st_size:
            raise ValueError("namespace control capsule read incomplete")
        controls = InheritedControls.model_validate_json(raw)
        if controls.setup.validator_control:
            roles += ("validator",)
            if (
                controls.batch_origin_ns is None
                or not 0
                < controls.batch_origin_ns
                < time.monotonic_ns()
                < controls.batch_origin_ns + 570_000_000_000
            ):
                raise ValueError("original validator batch origin unavailable or exhausted")
        if set(controls.groups) != set(roles):
            raise ValueError("namespace control role inventory differs")
        if (
            prepare_namespace_setup(
                controls.configuration,
                controls.bootstrap,
                controls.setup.parent_argv,
                controls.setup.parent_executable,
                parent_inventory=controls.setup.parent_inventory,
                validator_control=controls.setup.validator_control,
                bridge_control=controls.setup.bridge_control,
                policy_control=controls.setup.policy_control,
                network_control=controls.setup.network_control,
            )
            != controls.setup
        ):
            raise ValueError("inherited namespace preparation differs")
        _current_source(controls.configuration)
        for number, name in enumerate(roles, 4):
            expected = controls.groups[name]
            observed = os.fstat(number)
            if not stat.S_ISDIR(observed.st_mode) or (observed.st_dev, observed.st_ino) != (
                expected.device,
                expected.inode,
            ):
                raise ValueError("inherited group descriptor differs from retained identity")
            groups[name] = OwnedCgroup.attach_inherited(number, expected)
        _topology(groups["aggregate"], groups["setup"], groups["supervisor"], groups["worker"])
        if "validator" in groups:
            validator = groups["validator"]
            if PurePosixPath(validator.identity.relative_path).name != _validator_role_name(
                controls.configuration
            ) or validator.identity in [groups[name].identity for name in roles[:-1]]:
                raise ValueError("inherited original validator role differs")
            _aggregate_readback(groups["aggregate"], validator)
            validator.sample()
        return controls, groups
    except BaseException:
        for group in groups.values():
            group.close()
        raise
    finally:
        for number in range(3, 4 + len(roles)):
            os.close(number)


class NamespaceParentRefusal(ValueError):
    def __init__(self, reason: str, parent: RetainedTrustedTask, groups: dict[str, OwnedCgroup]):
        super().__init__(reason)
        self.parent, self.groups = parent, groups
        self.resources_reusable = False


def _set_namespace_file_growth_limit() -> None:
    """Lower only the namespace parent before watchdog/native/tool inheritance.

    The original observer and backing/formatting jobs must not inherit this
    smaller payload limit. No retry or renewed deadline follows a refusal.
    """
    if sys.platform != "linux":
        raise ValueError("Linux namespace file growth control unavailable")
    limits = (FILE_GROWTH_BYTES, FILE_GROWTH_BYTES)
    resource.setrlimit(resource.RLIMIT_FSIZE, limits)
    if resource.getrlimit(resource.RLIMIT_FSIZE) != limits:
        raise ValueError("namespace file growth limit installation differs")


def enter_namespace_parent(
    controls: InheritedControls,
    groups: dict[str, OwnedCgroup],
    *,
    inventory: RetainedParentInventory | None = None,
) -> RetainedTrustedTask:
    """Derive namespace PID/start from procfs, then move only self to supervisor.

    Host and namespace PID numbers are deliberately never compared or passed
    as migration targets. The outer wrapper handle cannot be native admission.
    """
    if controls.setup.parent_inventory is not None:
        if inventory is None or inventory.inventory != controls.setup.parent_inventory:
            raise ValueError("namespace parent requires retained exact root inventory")
        bind_parent_inventory(
            controls.configuration,
            inventory.inventory,
            controls.setup.parent_argv,
            controls.setup.parent_executable,
            controls.bootstrap.policy.helper_binary,
        )
        inventory.verify()
    if set(groups) != set(controls.groups) or any(
        groups[name].identity != identity for name, identity in controls.groups.items()
    ):
        raise ValueError("namespace parent retained controls differ")
    _topology(groups["aggregate"], groups["setup"], groups["supervisor"], groups["worker"])
    if "validator" in groups:
        _aggregate_readback(groups["aggregate"], groups["validator"])
        sample = groups["validator"].sample()
        if (
            sample.populated
            or sample.direct_pids
            or any(sample.memory_events.values())
            or any(sample.pids_events.values())
        ):
            raise ValueError("namespace parent requires original empty validator role")
    if groups["supervisor"]._read("cgroup.procs") or groups["worker"].sample().populated:
        raise ValueError("namespace parent requires empty supervisor and worker")
    root = _proc_root(controls.boot_id)
    descriptor = pidfd = -1
    try:
        descriptor, pidfd = _attach(root, os.getpid())
        pid, _, parent_pid, start = _stat_identity(_read(descriptor, "stat"))
        namespaces: dict[str, NamespaceIdentity] = {}
        if set(controls.outer_namespaces) != {"mnt", "net", "pid", "user", "time"}:
            raise ValueError("namespace parent requires independently retained outer namespaces")
        for name in controls.outer_namespaces:
            observed = os.stat("ns/" + name, dir_fd=descriptor)
            namespaces[name] = NamespaceIdentity(device=observed.st_dev, inode=observed.st_ino)
        if controls.setup.network_control and namespaces["net"] != controls.provider_network:
            raise ValueError(
                "actual parent provider network differs from original retained namespace"
            )
        if any(
            namespaces[name] == controls.outer_namespaces[name] for name in ("mnt", "net", "pid")
        ):
            raise ValueError("namespace parent must differ from outer mount/network/PID namespaces")
        spec = TrustedTaskSpec(
            configuration=record_digest(controls.configuration),
            pid=pid,
            parent_pid=parent_pid,
            start_ticks=start,
            boot_id=controls.boot_id,
            cgroup=groups["supervisor"].identity,
            namespaces=namespaces,
            executable=controls.setup.parent_executable,
            argv=controls.setup.parent_argv,
            environment={},
            capabilities=CAPABILITIES,
            cwd=native_working_directory(controls.configuration),
        )
        parent = RetainedTrustedTask(descriptor, pidfd, spec)
    finally:
        for handle in (descriptor, pidfd, root):
            if handle >= 0:
                os.close(handle)
    try:
        if inventory is not None:
            inventory.verify_task_root(parent.descriptor)
        _set_namespace_file_growth_limit()
        parent.verify(groups["setup"].identity)
        _move_self(groups["supervisor"])
        parent.verify(groups["supervisor"].identity)
        if groups["supervisor"]._read("cgroup.procs").split() != [str(pid)]:
            raise ValueError("supervisor must contain only the namespace parent")
        return parent
    except BaseException as error:
        raise NamespaceParentRefusal(str(error), parent, groups) from error


@dataclass(frozen=True)
class TerminalObservation:
    worker_empty: bool
    watchdog_exited: bool
    watchdog_reaped: bool
    errors: tuple[str, ...]
    resources_reusable: Literal[False] = False


@dataclass(frozen=True)
class NamespaceTerminalObservation:
    groups_empty: bool
    parent_exited: bool
    watchdog_exited: bool
    wrapper_reaped: bool
    errors: tuple[str, ...]
    resources_reusable: Literal[False] = False


def _terminal_task_exited(task: RetainedTrustedTask) -> bool:
    task.verify_handles()
    exited = bool(_wait_ready([task.pidfd], [], [], 0)[0])
    task.verify_handles()
    return exited


def _terminal_topology(lifetime: OwnedNamespaceSetup) -> None:
    """Cleanup ownership is independent of a resource refusal or changed ceiling."""
    aggregate = lifetime.aggregate
    aggregate._verify()
    groups = {
        "aggregate": aggregate,
        "setup": lifetime.setup,
        "supervisor": lifetime.supervisor,
        "worker": lifetime.worker,
    }
    if lifetime.validator is not None:
        groups["validator"] = lifetime.validator
    if set(groups) != set(lifetime.controls.groups):
        raise ValueError("terminal retained role inventory differs")
    if any(group.identity != lifetime.controls.groups[name] for name, group in groups.items()):
        raise ValueError("terminal retained cgroup identities differ")
    if len({(g.identity.device, g.identity.inode) for g in groups.values()}) != len(groups):
        raise ValueError("terminal owned roles must remain distinct")
    for group in tuple(groups.values())[1:]:
        group._verify()
        if PurePosixPath(group.identity.relative_path).parent != PurePosixPath(
            aggregate.identity.relative_path
        ):
            raise ValueError("terminal owned role ancestry differs")
        handle = os.open(
            "..",
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=group.descriptor,
        )
        try:
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != (aggregate.identity.device, aggregate.identity.inode):
                raise ValueError("terminal actual owned ancestry differs")
        finally:
            os.close(handle)


def terminal_namespace_setup(
    lifetime: OwnedNamespaceSetup,
    observer: RetainedTrustedTask,
    host_parent: RetainedTrustedTask,
    host_watchdog: RetainedTrustedTask,
    *,
    recovery_already_attempted: bool = False,
    absolute_deadline: float | None = None,
) -> NamespaceTerminalObservation:
    """External recovery after parent loss; pinned groups only, one grace.

    Host-side task handles must be attached/qualified independently in the host
    procfs view. Namespace PID values or wrapper PIDs never substitute for them.
    Worker emptiness must be observed before stopping supervisor or setup. Mount,
    key and backing resources remain retained and cannot be reused from this.
    """
    if absolute_deadline is not None and (
        not math.isfinite(absolute_deadline) or time.monotonic() >= absolute_deadline
    ):
        return NamespaceTerminalObservation(
            False, False, False, False, ("original terminal deadline exhausted",)
        )
    _observer_placement(
        observer,
        lifetime.observer_group,
        lifetime.aggregate,
        (
            lifetime.setup,
            lifetime.supervisor,
            lifetime.worker,
            *((lifetime.validator,) if lifetime.validator is not None else ()),
        ),
    )
    if (
        host_parent.spec.cgroup != lifetime.supervisor.identity
        or host_watchdog.spec.cgroup != lifetime.supervisor.identity
        or host_parent.spec.pid == host_watchdog.spec.pid
        or host_watchdog.spec.parent_pid != host_parent.spec.pid
        or host_parent.spec.configuration != record_digest(lifetime.controls.configuration)
        or host_watchdog.spec.configuration != host_parent.spec.configuration
        or host_parent.spec.boot_id != observer.spec.boot_id
        or host_watchdog.spec.boot_id != observer.spec.boot_id
        or host_watchdog.spec.executable != lifetime.controls.bootstrap.policy.helper_binary
        or host_parent.spec.executable != lifetime.controls.setup.parent_executable
        or host_parent.spec.argv != lifetime.controls.setup.parent_argv
        or host_parent.spec.capabilities != CAPABILITIES
        or host_parent.spec.cwd != native_working_directory(lifetime.controls.configuration)
        or host_watchdog.spec.cwd != host_parent.spec.cwd
        or host_watchdog.spec.argv != ["/bin/crewshal-bootstrap", "--watchdog"]
        or host_watchdog.spec.capabilities != "0" * 16
        or host_parent.spec.namespaces != host_watchdog.spec.namespaces
    ):
        raise ValueError("external terminal task/configuration identities differ")
    _terminal_topology(lifetime)
    errors: list[str] = []
    first = lifetime.recovery_deadline is None
    if first:
        lifetime.recovery_deadline = time.monotonic() + (0 if recovery_already_attempted else 1)
        if absolute_deadline is not None:
            lifetime.recovery_deadline = min(lifetime.recovery_deadline, absolute_deadline)
        try:
            lifetime.worker.stop()
            if lifetime.validator is not None:
                lifetime.validator.stop()
        except (OSError, ValueError) as error:
            errors.append(str(error))
    empty = parent_exited = watchdog_exited = reaped = False
    roles_stopped = False
    assert lifetime.recovery_deadline is not None
    deadline = lifetime.recovery_deadline
    if absolute_deadline is not None:
        deadline = min(deadline, absolute_deadline)
    while True:
        if absolute_deadline is not None and time.monotonic() >= absolute_deadline:
            errors.append("original terminal deadline exhausted")
            break
        try:
            sample = lifetime.worker.sample()
            worker_empty = not sample.populated and not sample.direct_pids
            validator_empty = True
            if lifetime.validator is not None:
                validator_sample = lifetime.validator.sample()
                validator_empty = (
                    not validator_sample.populated and not validator_sample.direct_pids
                )
            if first and worker_empty and validator_empty and not roles_stopped and not errors:
                lifetime.supervisor.stop()
                lifetime.setup.stop()
                roles_stopped = True
            empty = (
                worker_empty
                and validator_empty
                and all(
                    not group._read("cgroup.procs")
                    and _counters(group._read("cgroup.events"), {"populated"})["populated"] == 0
                    for group in (lifetime.supervisor, lifetime.setup)
                )
            )
            parent_exited = _terminal_task_exited(host_parent)
            watchdog_exited = _terminal_task_exited(host_watchdog)
            reaped = lifetime.wrapper is not None and lifetime.wrapper.poll() is not None
            if empty and parent_exited and watchdog_exited and reaped:
                break
        except (OSError, ValueError) as error:
            errors.append(str(error))
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(0.001, remaining))
    return NamespaceTerminalObservation(
        empty, parent_exited, watchdog_exited, reaped, tuple(errors)
    )


class OwnedWatchdogLifetime:
    """Own every created handle, including a watcher not yet armed or attached."""

    def __init__(self, parent: RetainedTrustedTask, worker: OwnedCgroup, supervisor: OwnedCgroup):
        self.parent, self.worker, self.supervisor = parent, worker, supervisor
        self._owners = (parent, worker, supervisor)
        self.process: subprocess.Popen[bytes] | None = None
        self.task: RetainedTrustedTask | None = None
        self.observed: ObservedWatchdog | None = None
        self.kill = self.lifeline = -1
        self.lifeline_identity: tuple[int, int] | None = None
        self.recovery_deadline: float | None = None
        self.resources_reusable = False

    def verify_native_binding(self, admitted: AdmittedNative) -> None:
        """Read the actual original handoff before any collection/stop effect."""
        if (
            type(admitted) is not AdmittedNative
            or self._owners != (self.parent, self.worker, self.supervisor)
            or getattr(self.parent, "_watchdog_lifetime", None) is not self
            or self.observed is None
            or self.task is not self.observed.task
            or self.process is None
            or self.process.pid != self.task.spec.pid
            or self.parent.spec.configuration != record_digest(admitted.configuration)
            or self.task.spec.configuration != self.parent.spec.configuration
            or self.observed.deadline.configuration != self.parent.spec.configuration
            or self.observed.deadline.worker != self.worker.identity
            or self.observed.deadline.started != admitted.started
            or self.observed.deadline.started_monotonic != admitted.started_monotonic
        ):
            raise ValueError("original native/watchdog ownership missing or changed")
        anchor = getattr(self.parent, "_native_handoff", None)
        expected = (admitted, self.observed, self.worker, self.supervisor, admitted.aggregate)
        if (
            anchor is None
            or len(anchor) != len(expected)
            or any(actual is not required for actual, required in zip(anchor, expected))
        ):
            raise ValueError("original native handoff differs from freeze input")
        self.parent.verify(self.supervisor.identity)

    def verify_native_terminal(self, admitted: AdmittedNative, expected_exit: int) -> None:
        """Read the original handoff before freeze while retaining a live parent.

        This consumes no new grace, closes no handle and stops no process. The
        outer wrapper/setup and storage closure retain their separate gates.
        """
        self.verify_native_binding(admitted)
        admitted.verify_terminal(expected_exit)
        task, process = self.task, self.process
        if (
            task is None
            or process is None
            or not _terminal_task_exited(task)
            or process.poll() is None
        ):
            raise ValueError("original watchdog exit/reap remains unobserved")
        _aggregate_readback(admitted.aggregate, self.supervisor)
        _role_controls(self.supervisor)
        if self.supervisor._read("cgroup.procs").split() != [str(self.parent.spec.pid)]:
            raise ValueError("supervisor must retain only original parent before freeze")
        admitted.verify_terminal(expected_exit)
        self.parent.verify(self.supervisor.identity)

    def terminal(self, *, recovery_already_attempted: bool = False) -> TerminalObservation:
        """Close lifeline to stop, never disarm. Re-observation never resets grace.

        A previous handoff refusal consumes recovery grace; this API then only
        performs immediate readback. Retained handles survive every unknown
        result. Even terminal processes do not prove physical storage cleanup.
        """
        errors: list[str] = []
        if self.recovery_deadline is None:
            self.recovery_deadline = time.monotonic() + (0 if recovery_already_attempted else 1)
            # Never kill the worker while cleanup parent might still be inside it.
            try:
                self.parent.verify(self.supervisor.identity)
                if self.lifeline >= 0:
                    info = os.fstat(self.lifeline)
                    if (
                        not stat.S_ISFIFO(info.st_mode)
                        or (info.st_dev, info.st_ino) != self.lifeline_identity
                    ):
                        raise ValueError("terminal lifeline identity changed")
                    os.close(self.lifeline)
                    self.lifeline = -1
                self.worker.stop()
            except (OSError, ValueError) as error:
                errors.append(str(error))
        empty = exited = reaped = False
        while True:
            try:
                sample = self.worker.sample()
                empty = not sample.populated and not sample.direct_pids
                if self.task is not None:
                    exited = _terminal_task_exited(self.task)
                if self.process is not None:
                    reaped = self.process.poll() is not None
                if empty and exited and reaped:
                    break
            except (OSError, ValueError) as error:
                errors.append(str(error))
                break
            if time.monotonic() >= self.recovery_deadline:
                break
            time.sleep(0.001)
        return TerminalObservation(empty, exited, reaped, tuple(errors))


class WatchdogSetupRefusal(ValueError):
    def __init__(self, reason: str, lifetime: OwnedWatchdogLifetime):
        super().__init__(reason)
        self.lifetime = lifetime
        self.resources_reusable = False


def create_owned_watchdog(
    parent: RetainedTrustedTask,
    worker: OwnedCgroup,
    supervisor: OwnedCgroup,
    aggregate: OwnedCgroup,
    configuration: DispatchConfiguration,
    preparation: BootstrapPreparation,
) -> OwnedWatchdogLifetime:
    """Source-only direct watchdog creation before the existing worker bridge."""
    preparation = audit_linux_bootstrap(configuration, preparation)
    _current_source(configuration)
    if (
        preparation.policy.helper_binary is None
        or configuration.linux_envelope is None
        or configuration.linux_envelope.bootstrap_policy_sha256 != record_digest(preparation.policy)
    ):
        raise ValueError("watchdog requires exact current helper/policy binding")
    if (
        parent.spec.pid != os.getpid()
        or parent.spec.cgroup != supervisor.identity
        or parent.spec.configuration != record_digest(configuration)
        or parent.spec.capabilities != CAPABILITIES
        or parent.spec.cwd != native_working_directory(configuration)
    ):
        raise ValueError("watchdog requires the retained namespace parent's exact role")
    _aggregate_readback(aggregate, worker)
    _aggregate_readback(aggregate, supervisor)
    _role_controls(supervisor)
    parent.verify(supervisor.identity)
    if parent._watchdog_started:
        raise ValueError("watchdog creation is one-shot; no retry or reset")
    if supervisor._read("cgroup.procs").split() != [str(parent.spec.pid)]:
        raise ValueError("supervisor must contain only parent before watchdog creation")
    sample = worker.sample()
    if sample.populated or sample.direct_pids:
        raise ValueError("watchdog creation requires an empty worker")
    parent._watchdog_started = True
    lifetime = OwnedWatchdogLifetime(parent, worker, supervisor)
    setattr(parent, "_watchdog_lifetime", lifetime)
    reading = writing = ready_read = ready_write = -1
    origin_bound = time.monotonic_ns()
    started = datetime.now(timezone.utc)
    try:
        lifetime.kill = os.open(
            "cgroup.kill",
            os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=worker.descriptor,
        )
        pipe2 = getattr(os, "pipe2")
        reading, writing = pipe2(os.O_CLOEXEC)
        lifetime.lifeline, writing = writing, -1
        info = os.fstat(lifetime.lifeline)
        lifetime.lifeline_identity = (info.st_dev, info.st_ino)
        ready_read, ready_write = pipe2(os.O_CLOEXEC | os.O_NONBLOCK)
        lifetime.process = subprocess.Popen(
            [
                "/bin/setpriv",
                "--reuid=0",
                "--regid=0",
                "--clear-groups",
                "--bounding-set=-all",
                "--inh-caps=-all",
                "--ambient-caps=-all",
                "--no-new-privs",
                "--",
                "/bin/crewshal-bootstrap",
                "--watchdog-fds",
                str(lifetime.kill),
                str(reading),
                str(ready_write),
            ],
            pass_fds=(lifetime.kill, reading, ready_write),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=native_working_directory(configuration),
            env={},
            close_fds=True,
        )
        os.close(reading)
        reading = -1
        os.close(ready_write)
        ready_write = -1
        # Attach before reading readiness, retaining a pidfd even for malformed
        # acknowledgements. No process is identified from helper stdout text.
        root = _proc_root(parent.spec.boot_id)
        descriptor = pidfd = -1
        try:
            descriptor, pidfd = _attach(root, lifetime.process.pid)
            pid, _, parent_pid, start = _stat_identity(_read(descriptor, "stat"))
            spec = TrustedTaskSpec(
                configuration=record_digest(configuration),
                pid=pid,
                parent_pid=parent_pid,
                start_ticks=start,
                boot_id=parent.spec.boot_id,
                cgroup=supervisor.identity,
                namespaces=parent.spec.namespaces,
                executable=preparation.policy.helper_binary,
                argv=preparation.watchdog_argv,
                environment={},
                capabilities="0" * 16,
                cwd=native_working_directory(configuration),
            )
            lifetime.task = RetainedTrustedTask(descriptor, pidfd, spec)
        finally:
            for handle in (descriptor, pidfd, root):
                if handle >= 0:
                    os.close(handle)
        acknowledgement = bytearray()
        while True:
            if (
                time.monotonic_ns() >= origin_bound + 5_000_000_000
                or lifetime.process.poll() is not None
            ):
                raise ValueError("watchdog startup exhausted original five-second bound")
            readable = _wait_ready([ready_read], [], [], 0.001)[0]
            if not readable:
                continue
            chunk = os.read(ready_read, 81)
            acknowledgement.extend(chunk)
            if len(acknowledgement) > 80:
                raise ValueError("watchdog readiness exceeds bounded record")
            if not chunk:
                break
        deadline = ArmedDeadline.retain(
            lifetime.process,
            lifetime.lifeline,
            worker,
            configuration,
            bytes(acknowledgement),
            started=started,
        )
        if not origin_bound <= deadline.origin_ns:
            raise ValueError("watchdog origin predates owned creation")
        lifetime.observed = ObservedWatchdog(lifetime.task, deadline, lifetime.kill)
        lifetime.observed.check(worker, configuration)
        if set(supervisor._read("cgroup.procs").split()) != {
            str(parent.spec.pid),
            str(lifetime.process.pid),
        }:
            raise ValueError("supervisor watchdog population differs")
        return lifetime
    except BaseException as error:
        # No hidden second grace. Caller receives all handles and performs the
        # single terminal recovery explicitly, before any resource release.
        raise WatchdogSetupRefusal(str(error), lifetime) from error
    finally:
        for handle in (reading, writing, ready_read, ready_write):
            if handle >= 0:
                os.close(handle)
