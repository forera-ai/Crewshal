"""Collect Phase 2D evidence in the original outer observer.

Parsed records cannot reconstruct original process or storage custody.
This module supplies no approval, credential, retry, or replacement owner.
"""

import json
import os
import time
from typing import NoReturn

from crewshal.contracts import Approval, Verdict, record_digest
from crewshal.dispatch import CodexDispatch
from crewshal.integration import (
    CodexCollection,
    capture_original_validator_evidence,
    collect_original_volume_codex,
)
from crewshal.linux_bridge import (
    QualificationTreeCustody,
    StoppedNativeBridge,
    ValidatorBridgeCustody,
    finish_original_parent,
    receive_stopped_validator,
    send_validator_views,
)
from crewshal.linux_fixture_inputs import OriginalFixtureInputs
from crewshal.linux_operational import OriginalInstallationDriver
from crewshal.linux_network import OwnedProviderNetworks
from crewshal.linux_qualification_fixture import (
    FrozenQualificationFixture,
    QUALIFICATION_LANES,
    RetainedSyntheticExclusions,
    RetainedTLSBrokerLifetime,
    _catalog,
    verify_frozen_qualification_markers,
    verify_native_probe_output,
)
from crewshal.model import digest
from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)
from crewshal.runtime_batch import AFTER
from crewshal.linux_schedule import OwnedThreeLaneSchedule


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _directory_identity(root: int, path: str) -> tuple[int, int]:
    """Read an exact inventoried directory without following a parent link."""
    descriptor = os.dup(root)
    try:
        for name in path.split("/"):
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=descriptor
            )
            os.close(descriptor)
            descriptor = child
        info = os.fstat(descriptor)
        return info.st_dev, info.st_ino
    finally:
        os.close(descriptor)


def _require_original(driver: OriginalInstallationDriver) -> None:
    if (
        type(driver) is not OriginalInstallationDriver
        or driver.failed
        or driver.reservation is None
        or driver.observer is None
        or driver.installation is None
        or driver.timer is None
        or driver.store is None
        or driver.reservation.observer is not driver.observer
        or driver.installation.reservation is not driver.reservation
        or driver.installation.growth.store is not driver.store
        or driver.timer.reservation is not driver.reservation
        or driver.origin != driver.reservation.batch_started
        or driver.timer.cutoff_ns != int(driver.origin * 1_000_000_000) + 570_000_000_000
        or driver.timer.end_ns != int(driver.origin * 1_000_000_000) + 600_000_000_000
    ):
        raise ValueError("complete original observer, installation, store, and timer required")
    driver.reservation.verify_installation()
    driver.timer.verify()
    if time.monotonic() >= driver.origin + 570:
        raise ValueError("original operational cutoff expired")


class OriginalQualificationCollector:
    """Derive twenty cases from original process, tool, and filesystem custody."""

    def __init__(
        self,
        driver: OriginalInstallationDriver,
        bridge: StoppedNativeBridge,
        fixture: FrozenQualificationFixture,
        identity: QualificationIdentity,
        exclusions: RetainedSyntheticExclusions,
        networks: OwnedProviderNetworks,
        broker: RetainedTLSBrokerLifetime,
    ):
        if type(bridge) is not StoppedNativeBridge:
            raise ValueError("qualification collector requires the original bridge")
        context = bridge.lane_context
        if context is None or context.lane_id not in QUALIFICATION_LANES:
            raise ValueError("qualification collector refuses live or undeclared lanes")
        if hasattr(context, "_qualification_collector"):
            raise ValueError("original qualification collector consumed; no replacement")
        self.driver, self.bridge = driver, bridge
        self.fixture = FrozenQualificationFixture.model_validate_json(fixture.model_dump_json())
        self.identity = QualificationIdentity.model_validate_json(identity.model_dump_json())
        self.exclusions, self.networks, self.broker = exclusions, networks, broker
        self._owners = driver, bridge, exclusions, networks, broker
        self._payloads = self.fixture.model_dump_json(), self.identity.model_dump_json()
        self.failed = self.consumed = False
        self.progress: bytes | None = None
        self.result: Qualification | None = None
        setattr(context, "_qualification_collector", self)
        try:
            self.verify()
        except BaseException:
            self.failed = True
            raise

    def __reduce__(self) -> NoReturn:
        raise TypeError("original qualification collector cannot be copied or exported")

    def verify(self) -> None:
        _require_original(self.driver)
        bridge, reservation = self.bridge, self.driver.reservation
        assert reservation is not None
        context = bridge.lane_context
        if (
            self.failed
            or self._owners != (self.driver, bridge, self.exclusions, self.networks, self.broker)
            or context is None
            or getattr(context, "_qualification_collector", None) is not self
            or bridge.installation is not self.driver.installation
            or bridge.installation.reservation is not reservation
            or self._payloads != (self.fixture.model_dump_json(), self.identity.model_dump_json())
            or self.fixture.configuration != record_digest(self.driver.inputs.configuration)
            or self.identity.configuration != record_digest(context.configuration)
            or self.exclusions.origin != self.driver.origin
            or type(self.exclusions) is not RetainedSyntheticExclusions
            or type(self.networks) is not OwnedProviderNetworks
            or self.networks.reservation is not reservation
            or getattr(reservation, "_provider_networks", None) is not self.networks
            or type(getattr(self.driver.production, "_fixture_inputs", None))
            is not OriginalFixtureInputs
            or not self.driver.production._fixture_inputs.complete
            or type(self.broker) is not RetainedTLSBrokerLifetime
            or self.broker.driver is not self.driver
            or not self.broker.ready
            or self.broker.failed
            or self.broker.plan.fixture != self.fixture
        ):
            raise ValueError("original qualification source, lane, or independent custody differs")
        bridge._verify_original()
        self.exclusions.verify_unchanged()
        root = self.driver.production.projected_inventory
        root.verify()
        for name, path in {
            "outside": "outside",
            "original": "original",
            "coordinator": "coordinator",
            "input": "input",
            "host-home": "home/owner",
        }.items():
            if self.exclusions.identities[name] != _directory_identity(root.descriptor, path):
                raise ValueError("synthetic exclusion descriptor belongs to another installed root")
        self.networks.verify_custody()
        self.broker._custody()

    def collect(
        self,
        custody: ValidatorBridgeCustody,
    ) -> Qualification:
        """Consume actual trusted broker progress after independent kernel readback."""
        if self.consumed:
            raise ValueError("original qualification collection consumed; no retry")
        self.consumed = True
        try:
            self.verify()
            bridge = self.bridge
            context = bridge.lane_context
            assert context is not None
            lane = context.lane_id
            progress = self.broker.read_lane(lane)
            first = json.loads(self.broker.records[0])
            catalog = first["catalog"]
            tools = _catalog(catalog)
            if "view_image" in tools:
                raise ValueError(
                    "enabled view_image requires reviewed actual positive and negative image output validation"
                )
            if type(custody) is not ValidatorBridgeCustody or custody.bridge is not bridge:
                raise ValueError("qualification requires original validator custody")
            bridge.verify_capture()
            bridge.verify_admission()
            custody.verify_capture()
            captured = custody.captured
            if (
                captured.observation.exit_code != 0
                or captured.overflow
                or captured.stop_error
                or captured.stdout != b"phase-2d-check: passed\n"
                or captured.stderr
                or not captured.observation.tree_stopped
                or custody.observed_environment != digest(b"")
                or custody.observed_argv != bridge.lifetime.controls.configuration.validator_argv
            ):
                raise ValueError("actual credential-free validator acceptance remains unknown")
            trees = getattr(bridge, "qualification_trees", None)
            if (
                type(trees) is not list
                or len(trees) != 2
                or any(type(tree) is not QualificationTreeCustody for tree in trees)
                or [tree.ordinal for tree in trees] != [1, 2]
            ):
                raise ValueError("both original cancellation and deadline trees required")
            for tree in trees:
                tree.verify_terminal()
            if (
                type(progress) is not dict
                or set(progress)
                != {
                    "lane",
                    "plan",
                    "fixture",
                    "catalog_sha256",
                    "catalog",
                    "outputs",
                    "bootstrap",
                    "origin",
                }
                or progress["lane"] != lane
                or progress["origin"] != self.driver.origin
                or progress["fixture"] != record_digest(self.fixture)
                or progress["catalog_sha256"] != digest(_canonical(catalog))
                or progress["bootstrap"]
                != ["/backend-api/codex/models?client_version=0.160.1", "/backend-api/wham/usage"]
                or set(tools) & {"exec_command", "write_stdin", "apply_patch", "view_image"}
                != set(self.fixture.expected_file_tools)
                or type(progress["outputs"]) is not dict
            ):
                raise ValueError("actual native tool catalog or finite broker capture differs")
            outputs = progress["outputs"]
            assert isinstance(outputs, dict)
            if lane + "-stdin" not in outputs:
                raise ValueError("actual native write_stdin probe output is missing")
            report = verify_native_probe_output(outputs[lane + "-stdin"])
            verify_frozen_qualification_markers(bridge.freeze, self.fixture)
            self.networks.readback()
            self.exclusions.verify_unchanged()
            self.progress = _canonical(progress)
            evidence = {
                "configuration": record_digest(bridge.lifetime.controls.configuration),
                "admission": record_digest(bridge.verify_admission()),
                "frozen": record_digest(bridge.freeze.manifest),
                "catalog": digest(_canonical(catalog)),
                "broker": digest(self.progress),
                "native_probe": digest(_canonical(report)),
                "validator_stdout": digest(captured.stdout),
                "validator_environment": custody.observed_environment,
                "validator_toolchain": custody.observed_toolchain,
                "exclusions": digest(self.exclusions._before),
                "cancellation": digest(trees[0].heartbeat_bytes),
                "deadline": digest(trees[1].heartbeat_bytes),
            }
            observation = _canonical(evidence).decode()
            record = Qualification(
                id="phase2d:" + lane + ":" + digest(self.progress),
                identity=self.identity,
                results=[
                    ProbeResult(case=case, status="passed", observation=observation)
                    for case in MANDATORY_CASES
                ],
            )
            if (
                assess_qualification(record, self.identity).status
                != "qualified_for_later_authorization"
            ):
                raise ValueError("complete original qualification identity remains unresolved")
            # Exercise the actual refusal function with missing, stale, and duplicate records.
            stale = self.identity.model_copy(update={"configuration": "0" * 64})
            missing = record.model_copy(update={"results": record.results[:-1]})
            duplicate = record.model_copy(update={"results": record.results + [record.results[0]]})
            if any(
                assess_qualification(value, expected).status != "denied"
                for value, expected in (
                    (None, self.identity),
                    (record, stale),
                    (missing, self.identity),
                    (duplicate, self.identity),
                )
            ):
                raise ValueError("actual qualification refusal function accepted an invalid record")
            self.verify()
            self.result = record
            return record
        except BaseException:
            self.failed = True
            raise


def capture_original_live(
    driver: OriginalInstallationDriver,
    bridge: StoppedNativeBridge,
    dispatch: CodexDispatch,
    *,
    expected_run_version: int,
    expected_attempt_version: int,
    token: str,
    initial: object,
) -> tuple[CodexCollection, ValidatorBridgeCustody]:
    """Collect the actual live candidate and run its original private validator."""
    from crewshal.candidate import FrozenCandidate

    _require_original(driver)
    if (
        type(bridge) is not StoppedNativeBridge
        or bridge.installation is not driver.installation
        or bridge.lane_context is None
        or bridge.lane_context.lane_id != "live"
        or type(dispatch) is not CodexDispatch
        or type(initial) is not FrozenCandidate
        or dispatch.configuration != bridge.lifetime.controls.configuration
        or driver.store is None
    ):
        raise ValueError("actual live dispatch and original candidate custody required")
    bridge.receive_capture()
    collection = collect_original_volume_codex(
        driver.store,
        bridge,
        dispatch,
        expected_run_version=expected_run_version,
        expected_attempt_version=expected_attempt_version,
        token=token,
        initial=initial,
        allowed_paths=["README.md"],
    )
    if collection.outcome.status != "completed" or collection.frozen is None:
        raise ValueError("actual live completion and frozen candidate remain unknown")
    manifest = collection.frozen
    if (
        len(manifest.files) != 1
        or manifest.files[0].path != "README.md"
        or manifest.files[0].sha256 != digest(AFTER)
    ):
        raise ValueError("actual live frozen candidate differs from the approved exact-byte task")
    send_validator_views(bridge)
    custody = receive_stopped_validator(bridge)
    custody.receive_capture()
    from crewshal.contracts import Run, Task

    run, _ = driver.store.get("run", collection.run_id, Run)
    if run is None:
        raise ValueError("actual live run is missing from the original store")
    recorded_task, _ = driver.store.get("task", run.task_id, Task)
    if recorded_task is None or len(recorded_task.checks) != 1:
        raise ValueError("actual live task requires its one frozen approved check")
    evidence = capture_original_validator_evidence(custody, collection, recorded_task.checks[0])
    driver.store.capture(
        evidence, token, stdout=custody.captured.stdout, stderr=custody.captured.stderr
    )
    return collection, custody


def finish_original_lane(
    schedule: OwnedThreeLaneSchedule,
    custody: ValidatorBridgeCustody,
    qualification: Qualification | None = None,
) -> None:
    """Wait for actual parent reaping before the original schedule consumes its slot."""
    if type(schedule) is not OwnedThreeLaneSchedule or type(custody) is not ValidatorBridgeCustody:
        raise ValueError("original schedule and validator terminal custody required")
    bridge = custody.bridge
    context = bridge.lane_context
    if context is None or context.reservation is not schedule.reservation:
        raise ValueError("original lane terminal custody belongs to another schedule")
    if context.lane_id in QUALIFICATION_LANES:
        collector = getattr(context, "_qualification_collector", None)
        if (
            type(collector) is not OriginalQualificationCollector
            or collector.bridge is not bridge
            or collector.failed
            or not collector.consumed
            or collector.result is not qualification
        ):
            raise ValueError("lane completion requires its original collected qualification")
        collector.verify()
    elif qualification is not None:
        raise ValueError("live lane cannot supply a synthetic qualification record")
    finish_original_parent(custody)
    wrapper = bridge.lifetime.wrapper
    if wrapper is None:
        raise ValueError("original namespace wrapper custody is missing")
    while wrapper.poll() is None:
        schedule.timer.verify()
        remaining = schedule.reservation.batch_started + 570 - time.monotonic()
        if remaining <= 0:
            raise ValueError("original parent exit remains unknown before cutoff")
        time.sleep(min(remaining, 0.001))
    if wrapper.returncode != 0:
        raise ValueError("original namespace parent completion failed")
    schedule.finish(context, custody, qualification)


def accept_original_live(
    driver: OriginalInstallationDriver,
    collection: CodexCollection,
    custody: ValidatorBridgeCustody,
    approval: Approval,
    *,
    project_id: str,
    token: str,
) -> Verdict:
    """Apply the separately supplied owner approval to the actual frozen binding."""
    _require_original(driver)
    if (
        type(collection) is not CodexCollection
        or type(custody) is not ValidatorBridgeCustody
        or type(approval) is not Approval
        or driver.store is None
        or custody.bridge.installation is not driver.installation
        or custody.bridge.lane_context is None
        or custody.bridge.lane_context.lane_id != "live"
        or approval.run_id != collection.run_id
        or approval.binding != collection.binding
        or collection.frozen != custody.bridge.freeze.manifest
        or getattr(custody, "_parent_finish_sent", False)
    ):
        raise ValueError("actual live frozen binding and separate owner approval required")
    custody.verify_capture()
    custody.bridge.freeze.verify_projection()
    driver.store.owner_approval(approval)
    verdict = driver.store.verdict(
        collection.run_id,
        project_id,
        collection.binding,
        token,
        frozen_owner=custody.bridge.freeze,
    )
    if verdict.status != "verified" or verdict.execution_allowed:
        raise ValueError("actual frozen-candidate and independent validator acceptance failed")
    return verdict
