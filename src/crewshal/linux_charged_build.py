"""Derive exact helper and policy identities under the original irreversible charge."""

import fcntl
import os
import time
from typing import NoReturn, TYPE_CHECKING, cast
from weakref import WeakKeyDictionary

from crewshal.contracts import record_digest, BuildDerivationRecord
from crewshal.dispatch import DispatchConfiguration
from crewshal.linux_inventory import (
    audit_parent_inventory,
    root_inventory_digest,
    helper_library_inventory_digest,
    _metadata,
)
from crewshal.linux_bootstrap import (
    bootstrap_policy,
    prepare_linux_bootstrap,
    audit_linux_bootstrap,
)
from crewshal.linux_parent import RetainedTrustedTask

if TYPE_CHECKING:
    from crewshal.linux_operational import (
        OriginalInstallationDriver,
        FrozenInstallationInputs,
        RetainedCompilerStorage,
    )
    from crewshal.linux_setup import OwnedStorageReservation
    from crewshal.durable import LiveStorageInstallationClaim

_DERIVATIONS: WeakKeyDictionary["OwnedStorageReservation", "RetainedBuildDerivation"] = (
    WeakKeyDictionary()
)


def verify_observer_configuration(
    observer: RetainedTrustedTask, configuration: DispatchConfiguration
) -> None:
    """Accept unchanged identity or the original registered helper derivation."""
    if observer.spec.configuration == record_digest(configuration):
        return
    owner = getattr(observer, "_storage_reservation", None)
    from crewshal.linux_setup import OwnedStorageReservation

    if type(owner) is not OwnedStorageReservation:
        raise ValueError("original observer configuration has no original reservation")
    derivation = _DERIVATIONS.get(owner)
    if type(derivation) is not RetainedBuildDerivation or derivation.observer is not observer:
        raise ValueError("original observer configuration has no retained build derivation")
    derivation.verify()
    if derivation.final_configuration != configuration:
        raise ValueError("original observer derived configuration differs")


class RetainedBuildDerivation:
    """A parsed receipt cannot supply this original live compiler custody."""

    driver: "OriginalInstallationDriver"
    reservation: "OwnedStorageReservation"
    observer: RetainedTrustedTask
    initial: "FrozenInstallationInputs"
    final: "FrozenInstallationInputs"
    final_configuration: DispatchConfiguration
    _initial_payload: str
    _final_payload: str
    _observer_digest: str
    _claim: "LiveStorageInstallationClaim"
    _compiler: "RetainedCompilerStorage"
    _origin: float
    output: int
    _output_identity: tuple[int, int]
    outputs: dict[str, int]
    _output_identities: dict[str, tuple[int, int]]
    _processes: dict[str, tuple[int, int, int, int]]
    _owners: tuple[object, ...]
    failed: bool
    record: BuildDerivationRecord
    _sealed_outputs: dict[str, tuple[tuple[int, ...], str]]

    def __init__(self) -> None:
        raise ValueError("build derivation requires its original charged compiler")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original build derivation cannot be copied or exported")

    @classmethod
    def bind(
        cls,
        driver: "OriginalInstallationDriver",
        initial: "FrozenInstallationInputs",
    ) -> "RetainedBuildDerivation":
        from crewshal.linux_operational import OriginalInstallationDriver, RetainedCompilerStorage
        from crewshal.linux_setup import OwnedStorageReservation
        from crewshal.durable import LiveStorageInstallationClaim

        reservation = cast(OwnedStorageReservation, driver.reservation)
        if (
            type(driver) is not OriginalInstallationDriver
            or type(reservation) is not OwnedStorageReservation
            or reservation in _DERIVATIONS
            or type(reservation.capacity_claim) is not LiveStorageInstallationClaim
            or type(driver.compiler_storage) is not RetainedCompilerStorage
            or driver.compiler_storage.reservation is not reservation
            or driver.observer is not reservation.observer
            or driver.store is not reservation.capacity_claim._store
            or initial.helper_build is None
            or driver._charged_build_input_payload != initial.model_dump_json()
        ):
            raise ValueError("original charged build derivation unavailable or consumed")
        owner = object.__new__(cls)
        assert driver.observer is not None
        assert driver.compiler_storage is not None
        owner.driver, owner.reservation, owner.observer = driver, reservation, driver.observer
        owner.initial = type(initial).model_validate_json(initial.model_dump_json())
        owner.final = type(initial).model_validate_json(driver.inputs.model_dump_json())
        owner.final_configuration = owner.final.configuration
        owner._initial_payload, owner._final_payload = (
            owner.initial.model_dump_json(),
            owner.final.model_dump_json(),
        )
        owner._observer_digest = record_digest(owner.observer.spec)
        owner._claim = cast(LiveStorageInstallationClaim, reservation.capacity_claim)
        owner._compiler = driver.compiler_storage
        owner._origin = driver.origin
        owner.output = driver.handles["compiled-helper-output"]
        info = os.fstat(owner.output)
        owner._output_identity = (info.st_dev, info.st_ino)
        owner.outputs = {"crewshal-bootstrap": owner.output}
        owner._processes = {}
        if initial.helper_build.policy_build is not None:
            for name in ("policy.binary", "storage-audit.json"):
                owner.outputs[name] = driver.handles["build-output:" + name]
            if driver._compiler_task_handles is None or driver._policy_task_handles is None:
                raise ValueError("original helper and policy process custody missing")
            owner._processes = {
                "compiler": driver._compiler_task_handles,
                "policy": driver._policy_task_handles,
            }
        owner._output_identities = {
            name: (os.fstat(fd).st_dev, os.fstat(fd).st_ino) for name, fd in owner.outputs.items()
        }
        owner._owners = driver, reservation, owner.observer, owner._claim, owner._compiler
        owner.failed = False
        _DERIVATIONS[reservation] = owner
        setattr(reservation, "_build_derivation", owner)
        try:
            owner._verify_inputs()
            output_paths = {
                "crewshal-bootstrap": "/bin/crewshal-bootstrap",
                "policy.binary": "/opt/crewshal/storage-audit/policy.binary",
                "storage-audit.json": "/opt/crewshal/storage-audit.json",
            }
            owner._sealed_outputs = {
                name: (
                    _metadata(os.fstat(fd)),
                    cast(str, owner.final.inventory.root[output_paths[name]].sha256),
                )
                for name, fd in owner.outputs.items()
            }
            # The original claim and observer keep their initial identities.
            # Only this registered derivation may seal the final dispatch fields.
            reservation._configuration = owner.final_configuration
            reservation._configuration_digest = record_digest(owner.final_configuration)
            assert initial.helper_build is not None
            assert owner.final.bootstrap.policy.helper_binary is not None
            owner.record = BuildDerivationRecord(
                id="build:" + record_digest(initial.helper_build),
                original_charge_id=owner._claim.record.id,
                original_observer=owner._observer_digest,
                initial_configuration=record_digest(initial.configuration),
                final_configuration=record_digest(owner.final_configuration),
                recipe=record_digest(initial.helper_build),
                source=initial.helper_build.source_sha256,
                helper_binary=owner.final.bootstrap.policy.helper_binary,
                policy_source=None
                if initial.helper_build.policy_build is None
                else initial.helper_build.policy_build.source_sha256,
                policy_binary=None
                if initial.helper_build.policy_build is None
                else driver.derived_storage_audit.policy_binary_sha256,
                storage_audit=None
                if initial.helper_build.policy_build is None
                else record_digest(driver.derived_storage_audit),
                outputs=owner._output_identities,
                processes=owner._processes,
                storage_objects={}
                if initial.helper_build.volume_constructor is None
                else {
                    name: (
                        os.fstat(driver.handles[name]).st_dev,
                        os.fstat(driver.handles[name]).st_ino,
                        os.fstat(driver.handles[name]).st_rdev,
                    )
                    for name in ("compiler-volume", "compiler-backing", "compiler-loop")
                },
            )
            with owner._claim._store.transaction():
                owner._claim._store._put("bootstrap_build", owner.record.id, owner.record, 0)
            owner.verify()
            return owner
        except BaseException:
            owner.failed = True
            raise

    def _verify_inputs(self) -> None:
        from crewshal.linux_operational import _hash_file

        initial, final = self.initial, self.final
        audit_linux_bootstrap(initial.configuration, initial.bootstrap)
        build = initial.helper_build
        if build is None or initial.configuration.linux_envelope is None:
            raise ValueError("original immutable helper build recipe missing")
        recipe = record_digest(build)
        if (
            initial.configuration.linux_envelope.build_recipe_sha256 != recipe
            or self._claim.record.configuration != record_digest(initial.configuration)
            or self.observer.spec.configuration != record_digest(initial.configuration)
            or self._claim.record.owner != self._observer_digest
            or self._claim.record.batch_started_monotonic != self._origin
            or self._claim.record.logical_bytes != 8589934592
            or self._claim.record.allocated_bytes != 8589934592
        ):
            raise ValueError("original full charge does not bind the immutable build recipe")
        helper = final.bootstrap.policy.helper_binary
        if helper is None:
            raise ValueError("actual compiled helper identity missing")
        info = os.fstat(self.output)
        if (info.st_dev, info.st_ino) != self._output_identity:
            raise ValueError("original compiler output inode changed")
        timer = self.driver.timer if hasattr(self.driver, "timer") else None
        idle = timer is not None and time.monotonic_ns() >= timer.end_ns
        if idle:
            for name, fd in self.outputs.items():
                if (
                    name not in self._sealed_outputs
                    or _metadata(os.fstat(fd)) != self._sealed_outputs[name][0]
                    or not os.fstatvfs(fd).f_flag & os.ST_RDONLY
                    or fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDONLY
                ):
                    raise ValueError(
                        "original immutable build output changed during idle retention"
                    )
            if self._sealed_outputs["crewshal-bootstrap"][1] != helper:
                raise ValueError("original retained helper digest changed")
        else:
            _hash_file(self.output, helper, self._origin + 570)
        inventory = initial.inventory.model_dump(mode="json")
        inventory["root"]["/bin/crewshal-bootstrap"]["sha256"] = helper
        inventory["helper_libraries"]["/bin/crewshal-bootstrap"] = helper
        audit = None
        if build.policy_build is not None:
            policy = build.policy_build
            from crewshal.linux_operational import _output_digest
            from crewshal.model import digest

            policy_hash = (
                self._sealed_outputs["policy.binary"][1]
                if idle
                else _output_digest(self.outputs["policy.binary"], self._origin + 570)
            )
            audit = policy.audit_template.model_copy(update={"policy_binary_sha256": policy_hash})
            audit_bytes = audit.model_dump_json().encode()
            audit_hash = digest(audit_bytes)
            if idle:
                if self._sealed_outputs["storage-audit.json"][1] != audit_hash:
                    raise ValueError("original retained audit digest changed")
            else:
                _hash_file(self.outputs["storage-audit.json"], audit_hash, self._origin + 570)
            if (
                not idle
                and os.pread(self.outputs["storage-audit.json"], len(audit_bytes) + 1, 0)
                != audit_bytes
            ):
                raise ValueError("derived storage audit bytes differ from the frozen template")
            if (
                initial.inventory.root["/opt/crewshal/storage-audit.json"].sha256
                != digest(policy.audit_template.model_dump_json().encode())
                or initial.configuration.linux_envelope.storage_policy_sha256
                != record_digest(policy.audit_template)
                or initial.inventory.root["/opt/crewshal/storage-audit/policy.source"].sha256
                != policy.source_sha256
                or initial.inventory.root["/usr/sbin/apparmor_parser"].sha256
                != policy.parser_sha256
                or initial.inventory.root["/opt/crewshal/storage-audit/policy.binary"].sha256
                != policy.audit_template.policy_binary_sha256
            ):
                raise ValueError(
                    "initial charged root and audit do not bind the frozen policy recipe"
                )
            inventory["root"]["/opt/crewshal/storage-audit/policy.binary"]["sha256"] = policy_hash
            inventory["root"]["/opt/crewshal/storage-audit.json"]["sha256"] = audit_hash
        expected_inventory = audit_parent_inventory(
            type(initial.inventory).model_validate(inventory)
        )
        if expected_inventory != final.inventory:
            raise ValueError("build derivation changed a nonderived root inventory entry")
        configuration = initial.configuration.model_dump(mode="json")
        bindings = configuration["linux_envelope"]
        bindings["root_inventory_sha256"] = root_inventory_digest(expected_inventory)
        bindings["parent_inventory_sha256"] = record_digest(expected_inventory)
        bindings["helper_library_inventory_sha256"] = helper_library_inventory_digest(
            expected_inventory
        )
        bindings["bootstrap_policy_sha256"] = record_digest(bootstrap_policy(helper))
        if audit is not None:
            bindings["storage_policy_sha256"] = record_digest(audit)
        if DispatchConfiguration.model_validate(configuration) != final.configuration:
            raise ValueError("build derivation changed a nonderived dispatch field")
        if prepare_linux_bootstrap(final.configuration, helper_binary=helper) != final.bootstrap:
            raise ValueError("build derivation changed a nonderived bootstrap field")
        left, right = initial.model_dump(mode="json"), final.model_dump(mode="json")
        for value in (left, right):
            for name in ("configuration", "inventory", "bootstrap"):
                value.pop(name)
        if left != right:
            raise ValueError("build derivation changed an original installation input")

    def verify(self) -> None:
        try:
            if (
                self.failed
                or _DERIVATIONS.get(self.reservation) is not self
                or getattr(self.reservation, "_build_derivation", None) is not self
                or self._owners
                != (self.driver, self.reservation, self.observer, self._claim, self._compiler)
                or self.initial.model_dump_json() != self._initial_payload
                or self.final.model_dump_json() != self._final_payload
                or self.driver.inputs.model_dump_json() != self._final_payload
                or record_digest(self.observer.spec) != self._observer_digest
                or self.driver.origin != self._origin
                or self.driver.compiler_storage is not self._compiler
                or self.reservation.capacity_claim is not self._claim
                or self.reservation._configuration is not self.final_configuration
                or self.reservation._configuration_digest != record_digest(self.final_configuration)
                or self.driver.handles["compiled-helper-output"] != self.output
            ):
                raise ValueError("original charged helper derivation custody changed")
            for name, fd in self.outputs.items():
                info = os.fstat(fd)
                handle = (
                    "compiled-helper-output"
                    if name == "crewshal-bootstrap"
                    else "build-output:" + name
                )
                if (
                    self.driver.handles.get(handle) != fd
                    or (info.st_dev, info.st_ino) != self._output_identities[name]
                ):
                    raise ValueError("original build output FD custody changed")
            if (
                self.initial.helper_build is not None
                and self.initial.helper_build.policy_build is not None
            ):
                if self._processes != {
                    "compiler": self.driver._compiler_task_handles,
                    "policy": self.driver._policy_task_handles,
                }:
                    raise ValueError("original helper or policy process custody changed")
                if self.driver.timer is None:
                    raise ValueError("original early batch timer was lost")
                if time.monotonic_ns() >= self.driver.timer.end_ns:
                    self.driver.timer.verify_idle_retention()
                else:
                    self.driver.timer.verify()
            self._claim.verify_reservation(self.reservation)
            recorded, version = self._claim._store.get(
                "bootstrap_build", self.record.id, BuildDerivationRecord
            )
            if recorded != self.record or version != 1:
                raise ValueError("original charged build journal receipt changed")
            self._compiler.verify()
            self._verify_inputs()
        except BaseException:
            self.failed = True
            raise
