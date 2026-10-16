"""Use fresh SQLite and projection FDs. Kernel validator checks remain synthetic."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal.contracts import Task, record_digest
from crewshal.integration import capture_original_validator_evidence
from crewshal.linux_bridge import ValidatorBridgeCustody
from crewshal.supervisor import CapturedProcess
from tests.acceptance.test_phase_2d_integration import Phase2DOriginalVolumeCollection, EMPTY


class Phase2DOriginalValidatorEvidence(unittest.TestCase):
    def setUp(self):
        self.fixture = Phase2DOriginalVolumeCollection()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.collection = self.fixture.collect()
        self.bridge = self.fixture.bridge
        task, _ = self.fixture.fixture.store.get("task", "task", Task)
        self.check = task.checks[0]
        self.custody = object.__new__(ValidatorBridgeCustody)
        self.custody.bridge = self.bridge
        self.bridge._validator_custody = self.custody
        self.custody.verify_capture = Mock()
        self.custody.observed_argv = list(self.check.argv)
        self.custody.observed_environment = EMPTY
        self.custody.observed_toolchain = self.check.toolchain
        self.custody.proc = SimpleNamespace(
            spec=SimpleNamespace(
                configuration=record_digest(self.bridge.lifetime.controls.configuration)
            )
        )
        original = self.bridge.native_capture
        self.custody.captured = CapturedProcess(
            original.observation,
            b"independent validator bytes\n",
            b"",
            original.initial,
            original.final,
            False,
            False,
        )
        self.bridge.installation.production._root_manifest = object()

    def capture(self, *, collection=None):
        with (
            patch("crewshal.candidate._root", side_effect=AssertionError("no path scan")),
            patch(
                "crewshal.linux_validator.validator_toolchain_digest",
                return_value=self.check.toolchain,
            ),
        ):
            return capture_original_validator_evidence(
                self.custody, collection or self.collection, self.check
            )

    def test_retained_projection_and_actual_capture_produce_check_without_path_or_flags(self):
        evidence = self.capture()
        self.assertEqual(evidence.status, "passed")
        self.assertEqual(evidence.binding, self.collection.binding)
        self.assertEqual(evidence.definition, self.check)
        self.assertEqual(evidence.attempt_id, self.collection.outcome.attempt.id)
        self.assertEqual(self.custody.verify_capture.call_count, 2)

    def test_changed_observed_environment_refuses_without_normalizing_to_approved_value(self):
        self.custody.observed_environment = "b" * 64
        with self.assertRaisesRegex(ValueError, "observed identity"):
            self.capture()

    def test_changed_toolchain_readback_refuses_actual_check_record(self):
        self.custody.observed_toolchain = "b" * 64
        with self.assertRaisesRegex(ValueError, "observed identity"):
            self.capture()

    def test_unrecorded_collection_cannot_supply_validator_binding(self):
        collection = self.collection.model_copy(update={"id": "unrecorded"})
        with self.assertRaisesRegex(ValueError, "collection"):
            self.capture(collection=collection)

    def test_changed_original_projection_refuses_before_evidence_record(self):
        (self.fixture.fixture.frozen / "README.md").write_bytes(b"mutated projection\n")
        with self.assertRaisesRegex(ValueError, "projection readback changed"):
            self.capture()

    def test_capture_overflow_remains_unknown_and_is_not_a_passed_check(self):
        self.custody.captured = CapturedProcess(
            self.custody.captured.observation,
            self.custody.captured.stdout,
            b"",
            self.custody.captured.initial,
            self.custody.captured.final,
            True,
            False,
        )
        with self.assertRaisesRegex(ValueError, "observed identity"):
            self.capture()


if __name__ == "__main__":
    unittest.main()
