"""Retain three sequential lanes under one original installation charge.

This controller creates no process, filesystem, namespace, credential, or request.
Its owner must supply the actual installed lane contexts and independent timer.
Qualification data never supplies operational or spend authority.
"""

import os
from typing import NoReturn, Protocol
from weakref import WeakKeyDictionary

from crewshal.admission import _wait_ready
from crewshal.admission import _fields, _read
from crewshal.contracts import record_digest
from crewshal.durable import LiveStorageInstallationClaim
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_bridge import ValidatorBridgeCustody
from crewshal.linux_setup import OwnedBatchTimer, OwnedNamespaceSetup, OwnedStorageReservation
from crewshal.qualification import Qualification, QualificationIdentity, assess_qualification
from crewshal.supervisor import OwnedCgroup, _counters

LANE_IDS = ("qualification-1", "qualification-2", "live")


class RetainedLaneContext(Protocol):
    """Original setup custody supplies these retained fields, never parsed data."""

    lane_id: str
    reservation: OwnedStorageReservation
    setup: OwnedCgroup
    supervisor: OwnedCgroup
    worker: OwnedCgroup
    validator: OwnedCgroup

    @property
    def timer(self) -> OwnedBatchTimer: ...

    @property
    def configuration(self) -> DispatchConfiguration: ...

    def verify_handles(self) -> None: ...


_SCHEDULES: WeakKeyDictionary[LiveStorageInstallationClaim, "OwnedThreeLaneSchedule"] = (
    WeakKeyDictionary()
)


def _verify_empty_roles(context: RetainedLaneContext) -> None:
    for group in (context.setup, context.supervisor, context.worker, context.validator):
        group._verify()
        if (
            group._read("cgroup.procs")
            or _counters(group._read("cgroup.events"), {"populated"})["populated"] != 0
            or any(_counters(group._read("memory.events"), {"max", "oom", "oom_kill"}).values())
            or any(_counters(group._read("pids.events"), {"max"}).values())
        ):
            raise ValueError("original lane role terminal state remains unknown")


def _verify_terminal(context: RetainedLaneContext, custody: ValidatorBridgeCustody) -> None:
    """Read parent exit, positive reap, and every actual lane role independently."""
    bridge = custody.bridge
    lifetime = bridge.lifetime
    if (
        type(custody) is not ValidatorBridgeCustody
        or getattr(bridge, "_validator_custody", None) is not custody
        or bridge.failed
        or getattr(custody, "_parent_finish_sent", False) is not True
        or getattr(custody, "captured", None) is not getattr(custody, "_captured_owner", None)
        or custody.captured.observation.exit_code is None
        or lifetime.wrapper is None
        or lifetime.wrapper.poll() is None
    ):
        raise ValueError("original lane parent exit and validator custody remain unknown")
    captured = custody.captured
    if custody._capture_record != (
        captured.stdout,
        captured.stderr,
        captured.observation.model_dump_json(),
        captured.initial.model_dump_json(),
        captured.final.model_dump_json() if captured.final is not None else None,
        captured.overflow,
        captured.stop_error,
    ):
        raise ValueError("original retained validator capture changed")
    bridge._verify_capture_data()
    parent = bridge.parent
    parent.verify_handles()
    bridge.native.verify_exited()
    bridge.watchdog.verify_handles()
    custody.proc.verify_exited()
    custody.watchdog.verify_handles()
    for task in (parent, bridge.native, bridge.watchdog, custody.proc, custody.watchdog):
        if (
            not _wait_ready([task.pidfd], [], [], 0)[0]
            or _fields(_read(bridge.host_proc, f"self/fdinfo/{task.pidfd}")).get("Pid") != "-1"
        ):
            raise ValueError("original lane parent or validator positive reap remains unknown")
    _verify_empty_roles(context)


class OwnedThreeLaneSchedule:
    """Consume three immutable retained slots without refund, reset, or retry."""

    def __init__(
        self,
        reservation: OwnedStorageReservation,
        timer: OwnedBatchTimer,
        contexts: tuple[RetainedLaneContext, RetainedLaneContext, RetainedLaneContext],
        identities: tuple[QualificationIdentity, QualificationIdentity, QualificationIdentity],
    ):
        if (
            type(reservation) is not OwnedStorageReservation
            or type(timer) is not OwnedBatchTimer
            or type(reservation.capacity_claim) is not LiveStorageInstallationClaim
        ):
            raise ValueError("three lanes require the original installation claim and timer")
        claim = reservation.capacity_claim
        assert isinstance(claim, LiveStorageInstallationClaim)
        if claim in _SCHEDULES:
            raise ValueError("original installation schedule is consumed; no replacement")
        self.reservation, self.timer, self.contexts = reservation, timer, contexts
        self.claim = claim
        self.identities = tuple(
            QualificationIdentity.model_validate_json(identity.model_dump_json())
            for identity in identities
        )
        self._identities = tuple(record_digest(identity) for identity in self.identities)
        self._configurations = tuple(context.configuration for context in contexts)
        self._configuration_payloads = tuple(
            configuration.model_dump_json() for configuration in self._configurations
        )
        self._owners = (reservation, timer, claim, contexts)
        self._origin = int(reservation.batch_started_monotonic * 1_000_000_000)
        self._roles = tuple(
            (context.setup, context.supervisor, context.worker, context.validator)
            for context in contexts
        )
        self._handles = tuple(
            (group.descriptor, os.fstat(group.descriptor).st_dev, os.fstat(group.descriptor).st_ino)
            for roles in self._roles
            for group in roles
        )
        self._lifetimes: list[OwnedNamespaceSetup | None] = [None, None, None]
        self._custodies: list[ValidatorBridgeCustody | None] = [None, None, None]
        self._qualifications: list[Qualification] = []
        self._qualification_payloads: list[str] = []
        self._next = 0
        self._active: RetainedLaneContext | None = None
        self._failed = False
        # Retain before verification. A refused original owner cannot mint another schedule.
        _SCHEDULES[claim] = self
        setattr(reservation, "_lane_schedule", self)
        try:
            self.verify()
        except BaseException:
            self._failed = True
            raise

    def __reduce__(self) -> NoReturn:
        raise TypeError("original three-lane schedule cannot be copied or exported")

    def verify(self) -> None:
        reservation, timer, claim, contexts = self._owners
        retained = getattr(reservation, "_lane_contexts", ())
        if (
            reservation is not self.reservation
            or timer is not self.timer
            or claim is not self.claim
            or contexts is not self.contexts
            or _SCHEDULES.get(claim) is not self
            or getattr(reservation, "_lane_schedule", None) is not self
            or self._failed
            or len(contexts) != 3
            or len(retained) != 3
            or any(a is not b for a, b in zip(contexts, retained, strict=True))
            or tuple(context.lane_id for context in contexts) != LANE_IDS
            or len({id(context) for context in contexts}) != 3
            or timer.reservation is not reservation
            or getattr(reservation, "_batch_timer", None) is not timer
            or timer.origin_ns != self._origin
            or timer.cutoff_ns != self._origin + 570_000_000_000
            or timer.end_ns != self._origin + 600_000_000_000
            or len(self.identities) != 3
            or tuple(record_digest(identity) for identity in self.identities) != self._identities
        ):
            raise ValueError("original three-lane owner, profile, order, or timer differs")
        claim.verify_reservation(reservation)
        reservation.verify()
        timer.verify()
        self._verify_profile()
        roles_now = tuple(
            (context.setup, context.supervisor, context.worker, context.validator)
            for context in contexts
        )
        if any(
            a is not b
            for old, new in zip(self._roles, roles_now, strict=True)
            for a, b in zip(old, new, strict=True)
        ):
            raise ValueError("original lane role pointers changed")
        handles = tuple(
            (group.descriptor, os.fstat(group.descriptor).st_dev, os.fstat(group.descriptor).st_ino)
            for roles in roles_now
            for group in roles
        )
        expected_timer_roles = tuple(group for roles in roles_now for group in roles)
        if timer._early_roles is not None:
            from crewshal.linux_early_timer import verify_early_timer_roles

            verify_early_timer_roles(timer)
            if timer._early_roles[:-1] != expected_timer_roles:
                raise ValueError("early timer lost the original twelve lane roles")
            expected_timer_roles += (timer._early_roles[-1],)
        if (
            handles != self._handles
            or len({(device, inode) for _, device, inode in handles}) != 12
            or {id(group) for group in timer.operational_groups}
            != {id(group) for group in expected_timer_roles}
            or len(timer.operational_groups) != len(expected_timer_roles)
        ):
            raise ValueError("original lane roles are shared, replaced, or absent from timer")
        for context in contexts:
            if context.reservation is not reservation or context.timer is not timer:
                raise ValueError("original lane owner or timer changed")
            context.verify_handles()
            if context is not self._active:
                _verify_empty_roles(context)
        for record, payload in zip(self._qualifications, self._qualification_payloads, strict=True):
            if record.model_dump_json() != payload:
                raise ValueError("retained qualification changed")

    def _verify_profile(self) -> None:
        """Audit exact profile fields. Only the declared lane name may differ."""
        master = self.reservation._configuration.model_dump(mode="json")
        if master.get("lane_id") is not None:
            raise ValueError("original installation requires its master profile")
        master.pop("lane_id", None)
        common_identity = self.identities[0].model_dump(mode="json")
        common_identity.pop("configuration")
        for index, context in enumerate(self.contexts):
            configuration = context.configuration
            identity = self.identities[index]
            if (
                type(configuration) is not DispatchConfiguration
                or configuration is not self._configurations[index]
                or configuration.model_dump_json() != self._configuration_payloads[index]
                or identity.configuration != record_digest(configuration)
            ):
                raise ValueError("actual retained lane configuration identity differs")
            profile = configuration.model_dump(mode="json")
            if profile.pop("lane_id", None) != LANE_IDS[index] or profile != master:
                raise ValueError(
                    "lane source, kernel, catalog, transport, or credential profile differs"
                )
            identity_profile = identity.model_dump(mode="json")
            identity_profile.pop("configuration")
            if identity_profile != common_identity:
                raise ValueError(
                    "lane qualification host, image, harness, or grant profile differs"
                )

    def activate(self, context: RetainedLaneContext) -> None:
        """Consume the next original slot before its owner starts any lane effect."""
        self.verify()
        if self._active is not None or self._next >= 3 or self.contexts[self._next] is not context:
            raise ValueError("lane activation is sequential and one-shot")
        if self._next == 2:
            if len(self._qualifications) != 2:
                raise ValueError("live lane requires two original complete qualifications")
            for index, record in enumerate(self._qualifications):
                if assess_qualification(record, self.identities[index]).status != (
                    "qualified_for_later_authorization"
                ):
                    raise ValueError("live lane qualification differs from the frozen profile")
        self._active = context

    def require_active(
        self, context: RetainedLaneContext, *, lifetime: OwnedNamespaceSetup | None = None
    ) -> None:
        """Require unused birth custody or the exact already retained active lifetime."""
        self.verify()
        if (
            context is not self._active
            or self._next >= 3
            or self.contexts[self._next] is not context
            or (
                self._lifetimes[self._next] is not None
                if lifetime is None
                else type(lifetime) is not OwnedNamespaceSetup
                or self._lifetimes[self._next] is not lifetime
            )
        ):
            raise ValueError("original active lane birth is missing or already consumed")

    def bind_lifetime(self, context: RetainedLaneContext, lifetime: OwnedNamespaceSetup) -> None:
        """Retain the actual namespace lifetime supplied by this exact active context."""
        self.verify()
        if (
            context is not self._active
            or type(lifetime) is not OwnedNamespaceSetup
            or self._lifetimes[self._next] is not None
            or lifetime.storage_reservation is not self.reservation
            or getattr(lifetime, "lane_context", None) is not context
            or any(
                getattr(lifetime, name) is not getattr(context, name)
                for name in ("setup", "supervisor", "worker", "validator")
            )
        ):
            raise ValueError("original lane namespace lifetime differs or was already bound")
        self._lifetimes[self._next] = lifetime

    def finish(
        self,
        context: RetainedLaneContext,
        custody: ValidatorBridgeCustody,
        qualification: Qualification | None = None,
    ) -> None:
        """Retain terminal custody and consume a result before admitting the next lane."""
        self.verify()
        if (
            context is not self._active
            or type(custody) is not ValidatorBridgeCustody
            or self._custodies[self._next] is not None
            or self._lifetimes[self._next] is None
            or custody.bridge.lifetime is not self._lifetimes[self._next]
        ):
            raise ValueError("original lane terminal custody differs or was already consumed")
        self._custodies[self._next] = custody
        try:
            _verify_terminal(context, custody)
            if self._next < 2:
                if type(qualification) is not Qualification:
                    raise ValueError("original lane requires a complete Qualification record")
                assert qualification is not None
                if assess_qualification(
                    qualification, self.identities[self._next]
                ).status != "qualified_for_later_authorization" or any(
                    qualification.id == old.id for old in self._qualifications
                ):
                    raise ValueError("original qualification is incomplete, stale, or repeated")
                self._qualifications.append(qualification)
                self._qualification_payloads.append(qualification.model_dump_json())
            elif qualification is not None:
                raise ValueError("live lane cannot manufacture another qualification result")
            self.timer.verify()
        except BaseException:
            self._failed = True
            raise
        self._next += 1
        self._active = None
