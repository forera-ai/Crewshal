"""Consume one approved batch marker after the original full storage charge."""

import json
import os
import stat
from typing import TYPE_CHECKING, NoReturn

from pydantic import Field, field_validator

from crewshal.contracts import Digest, record_digest
from crewshal.model import Contract

if TYPE_CHECKING:
    from crewshal.linux_operational import OriginalInstallationDriver
    from crewshal.linux_setup import OwnedStorageReservation


class FrozenAttemptMarker(Contract):
    parent: str
    leaf: str = Field(pattern=r"^phase2d-[0-9a-f]{32}\.consumed$")
    plan_sha256: Digest

    @field_validator("parent")
    @classmethod
    def exact_parent(cls, value: str) -> str:
        from pathlib import PurePosixPath

        path = PurePosixPath(value)
        if not path.is_absolute() or str(path) != value or ".." in path.parts or "\x00" in value:
            raise ValueError("one-use marker requires one exact absolute parent")
        return value


class OriginalAttemptMarker:
    """Retain the exact marker inode and the charge that precedes its creation."""

    _owners: tuple[
        "OriginalInstallationDriver", FrozenAttemptMarker, "OwnedStorageReservation", int, int
    ]
    _payload: str
    _bytes: bytes
    _parent_identity: tuple[int, int, int]
    _marker_identity: tuple[int, int, int]

    def __init__(self) -> None:
        raise ValueError("attempt marker requires its original charged driver")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original attempt marker cannot be exported")

    def verify(self) -> None:
        driver, marker, reservation, parent, descriptor = self._owners
        if (
            getattr(driver, "_attempt_marker_owner", None) is not self
            or driver.reservation is not reservation
            or getattr(reservation, "_installation_driver", None) is not driver
            or driver.observer is not reservation.observer
            or marker.model_dump_json() != self._payload
            or driver.origin != reservation.batch_started
            or driver.handles.get("attempt-marker-parent") != parent
            or driver.handles.get("attempt-marker") != descriptor
            or os.fstat(parent)[:3] != self._parent_identity
            or os.fstat(descriptor)[:3] != self._marker_identity
            or os.pread(descriptor, len(self._bytes) + 1, 0) != self._bytes
        ):
            raise ValueError("original attempt marker, charge, or retained bytes changed")
        reservation.verify()
        linked = os.stat(marker.leaf, dir_fd=parent, follow_symlinks=False)
        actual = os.fstat(descriptor)
        if (
            (linked.st_dev, linked.st_ino) != (actual.st_dev, actual.st_ino)
            or actual.st_nlink != 1
            or (actual.st_uid, actual.st_gid, stat.S_IMODE(actual.st_mode)) != (0, 0, 0o600)
        ):
            raise ValueError("original one-use marker inode or ownership differs")


def consume_original_marker(
    driver: "OriginalInstallationDriver", marker: FrozenAttemptMarker
) -> OriginalAttemptMarker:
    """Create one marker after charging and before role, timer, or build effects."""
    from crewshal.durable import LiveStorageInstallationClaim
    from crewshal.linux_operational import OriginalInstallationDriver, _open_path

    if (
        type(driver) is not OriginalInstallationDriver
        or driver.reservation is None
        or driver.observer is None
        or driver.store is None
        or driver.failed
        or driver.reservation.observer is not driver.observer
        or getattr(driver.reservation, "_installation_driver", None) is not driver
        or type(driver.reservation.capacity_claim) is not LiveStorageInstallationClaim
        or driver.reservation.capacity_claim._store is not driver.store
        or hasattr(driver, "_attempt_marker_owner")
        or driver.groups.keys() - {driver.inputs.batch_leaf, driver.inputs.observer_name}
        or driver.timer is not None
        or driver._compiler_attempted
        or "compiled-helper-output" in driver.handles
    ):
        raise ValueError(
            "one-use marker requires the original full charge before all later effects"
        )
    owner = object.__new__(OriginalAttemptMarker)
    setattr(driver, "_attempt_marker_owner", owner)
    frozen = FrozenAttemptMarker.model_validate_json(marker.model_dump_json())
    driver.reservation.verify()
    if driver.reservation.capacity_claim.record.configuration != record_digest(
        driver.inputs.configuration
    ):
        raise ValueError("one-use marker charge differs from the original frozen configuration")
    parent = _open_path(frozen.parent, directory=True)
    driver.handles["attempt-marker-parent"] = parent
    info = os.fstat(parent)
    if (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (0, 0, 0o700):
        raise ValueError("one-use marker parent must be private and root-owned")
    descriptor = os.open(
        frozen.leaf,
        os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
        0o600,
        dir_fd=parent,
    )
    driver.handles["attempt-marker"] = descriptor
    payload = json.dumps(
        {
            "plan": frozen.plan_sha256,
            "origin": driver.origin,
            "charge": driver.reservation.capacity_claim.record.id,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    owner._owners = driver, frozen, driver.reservation, parent, descriptor
    owner._payload = frozen.model_dump_json()
    owner._bytes = payload
    owner._parent_identity = os.fstat(parent)[:3]
    owner._marker_identity = os.fstat(descriptor)[:3]
    if os.write(descriptor, payload) != len(payload):
        raise ValueError("original one-use marker write remains unknown")
    os.fsync(descriptor)
    os.fsync(parent)
    owner.verify()
    return owner
