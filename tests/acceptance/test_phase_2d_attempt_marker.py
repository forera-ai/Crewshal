"""Fresh journal and inode tests do not establish Linux process placement."""

import os
from pathlib import Path
import pickle
import tempfile
import unittest
from unittest.mock import patch

from crewshal.contracts import record_digest
from crewshal.durable import CoordinatorStore
from crewshal.linux_attempt import FrozenAttemptMarker, consume_original_marker
from crewshal.linux_operational import OriginalInstallationDriver
from crewshal.linux_setup import reserve_storage_installation
from tests.acceptance import test_phase_2d_charged_build as build_fixtures
from tests.acceptance import test_phase_2d_setup as setup_fixtures


class OriginalAttemptMarkerTests(unittest.TestCase):
    def setUp(self):
        self.build_fixture = build_fixtures.Phase2DChargedBuild()
        self.build_fixture.setUp()
        self.addCleanup(self.build_fixture.doCleanups)
        self.setup_fixture = setup_fixtures.Phase2DSetup()
        self.setup_fixture.setUp()
        self.addCleanup(self.setup_fixture.doCleanups)
        self.setup_fixture.external_observer()
        driver = self.driver = OriginalInstallationDriver(self.build_fixture.initial)
        driver.observer = self.setup_fixture.parent
        driver.observer.spec = driver.observer.spec.model_copy(
            update={"configuration": record_digest(driver.inputs.configuration)}
        )
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        self.store = driver.store = CoordinatorStore(self.root / "fresh-original-charge")
        self.addCleanup(self.store.close)
        driver.reservation = reserve_storage_installation(
            self.store,
            driver.observer,
            self.setup_fixture.observer_group,
            self.setup_fixture.aggregate,
            driver.inputs.configuration,
            batch_started_monotonic=driver.origin,
        )
        driver.reservation._installation_driver = driver
        self.marker = FrozenAttemptMarker(
            parent=str(self.root),
            leaf="phase2d-" + "a" * 32 + ".consumed",
            plan_sha256="b" * 64,
        )
        self.parent = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.parent)
        self.kernel_fstat = os.fstat

        def synthetic_root_owner(descriptor):
            values = list(self.kernel_fstat(descriptor))
            values[4:6] = [0, 0]
            return os.stat_result(values)

        self.owner_patch = patch(
            "crewshal.linux_attempt.os.fstat", side_effect=synthetic_root_owner
        )
        self.owner_patch.start()
        self.addCleanup(self.owner_patch.stop)
        self.path_patch = patch("crewshal.linux_operational._open_path", return_value=self.parent)
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def consume(self):
        result = consume_original_marker(self.driver, self.marker)
        self.addCleanup(os.close, self.driver.handles["attempt-marker"])
        return result

    def test_exclusive_marker_follows_both_irreversible_original_charges(self):
        original = self.driver.reservation.capacity_claim.record.model_dump_json()
        owner = self.consume()
        owner.verify()
        self.assertEqual(self.driver.reservation.capacity_claim.record.model_dump_json(), original)
        self.assertEqual(self.driver.reservation.capacity_claim.record.logical_bytes, 8589934592)
        self.assertEqual(self.driver.reservation.capacity_claim.record.allocated_bytes, 8589934592)
        raw = (self.root / self.marker.leaf).read_bytes()
        self.assertIn(self.marker.plan_sha256.encode(), raw)
        self.assertIn(self.driver.reservation.capacity_claim.record.id.encode(), raw)
        self.assertIsNone(self.driver.timer)
        self.assertFalse(self.driver._compiler_attempted)

    def test_unregistered_or_copied_driver_cannot_create_a_marker(self):
        self.driver.reservation._installation_driver = object()
        with self.assertRaisesRegex(ValueError, "original full charge"):
            self.consume()
        self.assertFalse((self.root / self.marker.leaf).exists())

    def test_preexisting_marker_consumes_the_attempt_and_preserves_the_full_charge(self):
        (self.root / self.marker.leaf).write_bytes(b"Earlier consumed attempt.")
        claim = self.driver.reservation.capacity_claim
        with self.assertRaises(FileExistsError):
            self.consume()
        self.assertTrue(hasattr(self.driver, "_attempt_marker_owner"))
        with self.assertRaisesRegex(ValueError, "original full charge"):
            self.consume()
        self.assertEqual(claim.record.logical_bytes, 8589934592)
        self.assertEqual((self.root / self.marker.leaf).read_bytes(), b"Earlier consumed attempt.")

    def test_changed_marker_bytes_cannot_supply_original_custody(self):
        owner = self.consume()
        (self.root / self.marker.leaf).write_bytes(b"Changed marker.")
        with self.assertRaisesRegex(ValueError, "retained bytes"):
            owner.verify()

    def test_repeated_marker_or_export_cannot_create_another_attempt(self):
        owner = self.consume()
        with self.assertRaises(ValueError):
            self.consume()
        with self.assertRaises(TypeError):
            pickle.dumps(owner)

    def test_timer_role_or_build_effect_must_not_precede_the_marker(self):
        for attribute, value in (
            ("timer", object()),
            ("_compiler_attempted", True),
            ("groups", {"broker": object()}),
            ("handles", {"compiled-helper-output": 123}),
        ):
            original = getattr(self.driver, attribute)
            setattr(self.driver, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                self.consume()
            setattr(self.driver, attribute, original)
            self.assertFalse((self.root / self.marker.leaf).exists())
