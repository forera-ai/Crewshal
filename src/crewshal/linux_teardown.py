"""Owned physical teardown ordering source; no qualified storage adapter.

The retained storage owner must independently observe actual private mount,
anonymous keyring, loop/backing and residual-holder identities. Concrete Linux source retains unknown reference closure; its effective
containment and bounded calls remain qualification gaps. Caller text or
prospective resource hashes cannot supply this owner. Offline tests substitute
only that kernel seam and process observations, never execute host cleanup.
"""

from dataclasses import dataclass
import math
import os
import stat
from pathlib import PurePosixPath
import time
from typing import Literal, Protocol

from pydantic import Field

from crewshal.admission import NamespaceIdentity
from crewshal.contracts import record_digest
from crewshal.linux_envelope import prepare_linux_envelope
from crewshal.linux_parent import RetainedTrustedTask
from crewshal.linux_setup import (
    OwnedNamespaceSetup,
    terminal_namespace_setup,
    _terminal_task_exited,
)
from crewshal.model import Contract
from crewshal.supervisor import OwnedCgroup, _counters


class FileIdentity(Contract):
    device: int = Field(ge=0)
    inode: int = Field(gt=0)


class MountIdentity(Contract):
    mount_id: int = Field(gt=0)
    parent_id: int = Field(gt=0)
    target: str
    filesystem: Literal["ecryptfs", "ext4"]
    device: str


class LoopIdentity(Contract):
    device: FileIdentity
    rdev: int = Field(gt=0)
    backing: FileIdentity
    backing_name: str
    offset: Literal[0] = 0
    size_limit: int = Field(gt=0, le=8589934592)


class PhysicalState(Contract):
    """Independent storage readback, including explicit unknown residual state."""

    namespace: NamespaceIdentity
    mounts: dict[str, MountIdentity]
    private_keyring: int = Field(gt=0)
    keyring_state: Literal["present", "revoked", "unknown"] = "unknown"
    loops: dict[str, LoopIdentity]
    backing: dict[str, FileIdentity]
    extra_mount_aliases: int | None = Field(default=None, ge=0)
    extra_open_holders: int | None = Field(default=None, ge=0)


class PhysicalOwner(Protocol):
    """Trusted retained kernel owner, not a worker plugin or imported manifest.

    No lazy/forced unmount, ambient keyring operation, host block-device action,
    recursive path removal or new deadline is permitted. Readback must cover
    other retained namespaces and deleted-open/alias references. Operations
    must use pinned ownership and obey the supplied absolute cleanup deadline.
    Absent/unknown kernel readback must raise or retain None, never infer absence
    from access denial, errno text, process emptiness or command exit success.
    """

    def readback(self) -> PhysicalState: ...

    def verify_retention(self, reservation: object) -> None: ...

    def unmount(self, mount: MountIdentity, deadline: float) -> None: ...

    def revoke_private_keyring(self, serial: int, deadline: float) -> None: ...

    def detach_loop(self, loop: LoopIdentity, deadline: float) -> None: ...

    def remove_backing(self, name: str, identity: FileIdentity, deadline: float) -> None: ...


@dataclass(frozen=True)
class PhysicalTeardownObservation:
    physical_released: bool
    roles_released: tuple[str, ...]
    handles_released: bool
    errors: tuple[str, ...]
    # Observer/aggregate, exact qualification and the next live gate remain.
    resources_reusable: Literal[False] = False


@dataclass(frozen=True)
class PhysicalRetentionObservation:
    """Terminal retention evidence only; candidate/validator gates are separate."""

    terminal_verified: bool
    physical_release: Literal["unknown"] = "unknown"
    errors: tuple[str, ...] = ()
    resources_reusable: Literal[False] = False


class OwnedPhysicalResources:
    """Retain actual ownership before teardown; never reconstruct from a receipt.

    Constructor is a trusted setup seam, not proof of kernel ownership. All
    states are deep snapshots. Pinned namespace/storage descriptors are private
    duplicates; caller descriptors cannot be accidentally closed or recycled.
    The namespace parent/watchdog and wrapper lifetimes are separately retained.
    Setup must close the original backing FDs after this transfer; residual
    holders readback must include every FD except these listed private copies.
    """

    def __init__(
        self,
        lifetime: OwnedNamespaceSetup,
        owner: PhysicalOwner,
        namespace_fd: int,
        storage_fds: dict[str, int],
        unmount_order: list[str],
        *,
        batch_started_monotonic: float,
    ):
        now = time.monotonic()
        if lifetime.physical_teardown_claimed:
            raise ValueError("owned namespace already claimed physical teardown; no reconstruction")
        if not math.isfinite(batch_started_monotonic) or not 0 < batch_started_monotonic <= now:
            raise ValueError("original monotonic batch origin required")
        self.lifetime, self.owner = lifetime, owner
        self.configuration = record_digest(lifetime.controls.configuration)
        self.batch_started = batch_started_monotonic
        self.cleanup_deadline: float | None = None
        self.started = False
        self.failure: tuple[str, ...] = ()
        self.resources_reusable = False
        self.reservation = lifetime.storage_reservation
        if self.reservation is not None:
            if self.reservation.batch_started != batch_started_monotonic:
                raise ValueError("retained storage reservation batch origin differs")
            self.reservation.claim(lifetime)
            # A failed constructor remains owned; never reconstruct it from
            # terminal receipt data or drop the last handles on an exception.
            self.reservation.retain(self)
            owner.verify_retention(self.reservation)
        self.state = PhysicalState.model_validate_json(owner.readback().model_dump_json())
        state = self.state
        self.state_digest = record_digest(state)
        info = os.fstat(namespace_fd)
        if (info.st_dev, info.st_ino) != (state.namespace.device, state.namespace.inode):
            raise ValueError("physical owner mount namespace descriptor differs")
        root = prepare_linux_envelope(lifetime.controls.configuration).owned_root
        if (
            not state.mounts
            or not state.loops
            or not state.backing
            or state.keyring_state != "present"
            or (
                self.reservation is None
                and (state.extra_mount_aliases != 0 or state.extra_open_holders != 0)
            )
            or len(unmount_order) != len(set(unmount_order))
            or set(unmount_order) != set(state.mounts)
            or len({mount.mount_id for mount in state.mounts.values()}) != len(state.mounts)
            or len({mount.target for mount in state.mounts.values()}) != len(state.mounts)
        ):
            raise ValueError(
                "complete owned physical inventory and absence of extra holders required"
            )
        ids = {mount.mount_id: name for name, mount in state.mounts.items()}
        for name, mount in state.mounts.items():
            path = PurePosixPath(mount.target)
            if (
                not path.is_relative_to(root)
                or str(path) != mount.target
                or ".." in path.parts
                or "\x00" in mount.target
                or str(path) == root
            ):
                raise ValueError("physical mount must stay inside exact owned session root")
            parent = ids.get(mount.parent_id)
            if parent is not None and unmount_order.index(name) >= unmount_order.index(parent):
                raise ValueError("owned child mount must be released before its parent")
        kinds = [state.mounts[name].filesystem for name in unmount_order]
        if "ecryptfs" not in kinds or "ext4" not in kinds or kinds != sorted(kinds):
            raise ValueError("all encrypted uppers must precede ext4 backing unmounts")
        if set(storage_fds) != set(state.backing):
            raise ValueError("every owned backing file needs its retained descriptor")
        for name, identity in state.backing.items():
            if (
                not name
                or PurePosixPath(name).name != name
                or name in (".", "..")
                or "\x00" in name
            ):
                raise ValueError("owned backing requires a single relative leaf name")
            info = os.fstat(storage_fds[name])
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
                or (info.st_dev, info.st_ino) != (identity.device, identity.inode)
            ):
                raise ValueError("owned backing descriptor identity differs")
        if len({(f.device, f.inode) for f in state.backing.values()}) != len(state.backing):
            raise ValueError("owned backing identities must be distinct")
        if {loop.backing_name for loop in state.loops.values()} != set(state.backing):
            raise ValueError("loop/backing inventory must be complete")
        for loop in state.loops.values():
            if loop.backing != state.backing[loop.backing_name]:
                raise ValueError("owned loop backing identity differs")
        self.order = tuple(unmount_order)
        self.descriptors: dict[str, int] = {}
        try:
            self.namespace_fd = os.dup(namespace_fd)
            self.descriptors["namespace"] = self.namespace_fd
            for name, descriptor in storage_fds.items():
                self.descriptors["backing:" + name] = os.dup(descriptor)
        except BaseException:
            for descriptor in self.descriptors.values():
                os.close(descriptor)
            raise
        self._owned_descriptors = dict(self.descriptors)
        self._released_backing: set[str] = set()
        bind = getattr(owner, "bind_backing_handles", None)
        if bind is not None:
            bind({name: self.descriptors["backing:" + name] for name in state.backing})

    def _verify_handles(self) -> None:
        if (
            record_digest(self.state) != self.state_digest
            or self.descriptors != self._owned_descriptors
        ):
            raise ValueError("retained physical inventory or descriptor set changed")
        info = os.fstat(self.namespace_fd)
        if (info.st_dev, info.st_ino) != (self.state.namespace.device, self.state.namespace.inode):
            raise ValueError("retained physical namespace identity changed")
        for name, identity in self.state.backing.items():
            if name in self._released_backing:
                continue
            info = os.fstat(self.descriptors["backing:" + name])
            if (info.st_dev, info.st_ino) != (identity.device, identity.inode):
                raise ValueError("retained physical backing identity changed")


def _remove_group(aggregate: OwnedCgroup, group: OwnedCgroup) -> None:
    """Pinned immediate child only. Never kill/remove the live observer aggregate."""
    aggregate._verify()
    group._verify()
    path = PurePosixPath(group.identity.relative_path)
    if path.parent != PurePosixPath(aggregate.identity.relative_path):
        raise ValueError("release group is not an owned immediate child")
    info = os.stat(path.name, dir_fd=aggregate.descriptor, follow_symlinks=False)
    if (info.st_dev, info.st_ino) != (group.identity.device, group.identity.inode):
        raise ValueError("release group path identity differs")
    if (
        group._read("cgroup.procs")
        or _counters(group._read("cgroup.events"), {"populated"})["populated"]
    ):
        raise ValueError("release group remains populated")
    os.rmdir(path.name, dir_fd=aggregate.descriptor)
    try:
        os.stat(path.name, dir_fd=aggregate.descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise ValueError("owned group removal was not independently observed")


def teardown_owned_physical_resources(
    resources: OwnedPhysicalResources,
    observer: RetainedTrustedTask,
    host_parent: RetainedTrustedTask,
    host_watchdog: RetainedTrustedTask,
) -> PhysicalTeardownObservation:
    """One attempt: terminal readback, storage, role removal, then owned FD release.

    A successful operation without its independent exact readback is unknown.
    Any failure stops later effects and retains remaining handles. No retry,
    disarm, one-second process grace reset or resource reuse is provided. The
    separately bounded observer and original aggregate remain alive/retained.
    """
    if resources.started or resources.lifetime.physical_teardown_claimed:
        return PhysicalTeardownObservation(
            False, (), False, resources.failure or ("physical teardown is one-shot",)
        )
    resources.started = True
    resources.lifetime.physical_teardown_claimed = True
    if resources.reservation is not None:
        resources.failure = ("retained storage reservation has no physical release authority",)
        return PhysicalTeardownObservation(False, (), False, resources.failure)
    released: list[str] = []
    physical = False
    lifetime = resources.lifetime
    expected = PhysicalState.model_validate_json(resources.state.model_dump_json())
    now = time.monotonic()
    owner_deadline = getattr(resources.owner, "cleanup_deadline", resources.batch_started + 600)
    if not isinstance(owner_deadline, (float, int)) or not math.isfinite(owner_deadline):
        resources.failure = ("retained storage-owner deadline unavailable",)
        return PhysicalTeardownObservation(False, (), False, resources.failure)
    resources.cleanup_deadline = min(resources.batch_started + 600, now + 30, owner_deadline)
    deadline = resources.cleanup_deadline

    def guard() -> None:
        if time.monotonic() >= deadline:
            raise ValueError("original batch/cleanup deadline exhausted")
        if record_digest(lifetime.controls.configuration) != resources.configuration:
            raise ValueError("physical teardown configuration changed")
        resources._verify_handles()
        terminal = terminal_namespace_setup(
            lifetime, observer, host_parent, host_watchdog, absolute_deadline=deadline
        )
        if terminal.errors or not all(
            (
                terminal.groups_empty,
                terminal.parent_exited,
                terminal.watchdog_exited,
                terminal.wrapper_reaped,
            )
        ):
            raise ValueError(
                "independent terminal parent/watchdog/wrapper and empty roles required"
            )
        observed = PhysicalState.model_validate_json(resources.owner.readback().model_dump_json())
        if (
            observed != expected
            or observed.extra_mount_aliases != 0
            or observed.extra_open_holders != 0
        ):
            raise ValueError("physical ownership or release readback differs or remains unknown")

    try:
        guard()
        for name in resources.order:
            guard()
            resources.owner.unmount(expected.mounts[name], deadline)
            del expected.mounts[name]
            guard()
        guard()
        resources.owner.revoke_private_keyring(expected.private_keyring, deadline)
        expected.keyring_state = "revoked"
        guard()
        for name in sorted(expected.loops):
            guard()
            resources.owner.detach_loop(expected.loops[name], deadline)
            del expected.loops[name]
            guard()
        # Once loops and mounts are gone, release our backing FDs before unlink.
        # The trusted storage owner retains the pinned parent directory and must
        # verify each leaf's inode immediately before unlink. No deleted-open
        # backing can be called physically released from pathname absence alone.
        for name in sorted(expected.backing):
            guard()
            key = "backing:" + name
            descriptor = resources.descriptors.pop(key)
            resources._owned_descriptors.pop(key)
            resources._released_backing.add(name)
            os.close(descriptor)
            guard()
        for name in sorted(expected.backing):
            guard()
            resources.owner.remove_backing(name, expected.backing[name], deadline)
            del expected.backing[name]
            guard()
        physical = True
        for name in ("worker", "supervisor", "setup"):
            # No group readback through removed directory handles. Before each
            # removal, retain independent live observer and terminal task checks.
            if time.monotonic() >= deadline:
                raise ValueError("original batch/cleanup deadline exhausted")
            observer.verify(lifetime.observer_group.identity)
            if resources.owner.readback() != expected:
                raise ValueError("physical resources reappeared before cgroup release")
            if (
                not _terminal_task_exited(host_parent)
                or not _terminal_task_exited(host_watchdog)
                or lifetime.wrapper is None
                or lifetime.wrapper.poll() is None
            ):
                raise ValueError("terminal tasks changed before cgroup release")
            _remove_group(lifetime.aggregate, getattr(lifetime, name))
            released.append(name)
        if resources.owner.readback() != expected:
            raise ValueError("physical release readback changed before FD release")
        resources._verify_handles()
        # Every group removal was read back before closing identity handles.
        # Unknown close outcomes cannot be retried against recycled fd numbers.
        for name in list(resources.descriptors):
            descriptor = resources.descriptors.pop(name)
            os.close(descriptor)
        for task in (host_watchdog, host_parent):
            task.close()
        for name in released:
            getattr(lifetime, name).close()
        return PhysicalTeardownObservation(True, tuple(released), True, ())
    except (OSError, ValueError) as error:
        resources.failure = (str(error),)
        return PhysicalTeardownObservation(physical, tuple(released), False, resources.failure)


def retain_owned_physical_resources(
    resources: OwnedPhysicalResources,
    observer: RetainedTrustedTask,
    host_parent: RetainedTrustedTask,
    host_watchdog: RetainedTrustedTask,
) -> PhysicalRetentionObservation:
    """One bounded terminal attempt, with no physical effects or handle release.

    The live reservation must predate creation and retain the actual object.
    Unknown kernel references remain unknown; every original reservation stays
    charged, even when scans are empty. This does not authorize another job,
    allocation, cleanup, retry, release, qualification or candidate acceptance.
    """
    if resources.started or resources.lifetime.physical_teardown_claimed:
        return PhysicalRetentionObservation(False, errors=("storage terminal is one-shot",))
    resources.started = True
    resources.lifetime.physical_teardown_claimed = True
    reservation = resources.reservation
    try:
        if reservation is None:
            raise ValueError("original live storage reservation required")
        owner_deadline = getattr(
            resources.owner,
            "retention_deadline",
            getattr(resources.owner, "cleanup_deadline", None),
        )
        if not isinstance(owner_deadline, (int, float)) or not math.isfinite(owner_deadline):
            raise ValueError("original bounded storage-owner deadline required")
        deadline = min(resources.batch_started + 600, owner_deadline, time.monotonic() + 30)
        resources.cleanup_deadline = deadline

        def guard() -> None:
            if time.monotonic() >= deadline:
                raise ValueError("original batch/cleanup deadline exhausted")
            if record_digest(resources.lifetime.controls.configuration) != resources.configuration:
                raise ValueError("retained terminal configuration changed")
            reservation.verify()
            resources._verify_handles()
            resources.owner.verify_retention(reservation)

        guard()
        terminal = terminal_namespace_setup(
            resources.lifetime, observer, host_parent, host_watchdog, absolute_deadline=deadline
        )
        if terminal.errors or not all(
            (
                terminal.groups_empty,
                terminal.parent_exited,
                terminal.watchdog_exited,
                terminal.wrapper_reaped,
            )
        ):
            raise ValueError(
                "independent terminal parent/watchdog/wrapper and empty roles required"
            )
        guard()
        observed = resources.owner.readback()
        expected = resources.state
        if (
            observed.namespace != expected.namespace
            or observed.mounts != expected.mounts
            or observed.private_keyring != expected.private_keyring
            or observed.keyring_state != expected.keyring_state
            or observed.loops != expected.loops
            or observed.backing != expected.backing
            or observed.extra_mount_aliases not in (0, None)
            or observed.extra_open_holders not in (0, None)
        ):
            raise ValueError("retained storage changed or additional references were observed")
        guard()
        terminal = terminal_namespace_setup(
            resources.lifetime, observer, host_parent, host_watchdog, absolute_deadline=deadline
        )
        if terminal.errors or not all(
            (
                terminal.groups_empty,
                terminal.parent_exited,
                terminal.watchdog_exited,
                terminal.wrapper_reaped,
            )
        ):
            raise ValueError("terminal roles changed during retained storage readback")
        guard()
        return PhysicalRetentionObservation(True)
    except (OSError, ValueError) as error:
        resources.failure = (str(error),)
        return PhysicalRetentionObservation(False, errors=resources.failure)
