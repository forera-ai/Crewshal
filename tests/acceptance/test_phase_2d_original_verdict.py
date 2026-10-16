"""Verify the original frozen FD route without reopening a global mount path."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal.linux_freeze import OriginalVolumeFreeze
from tests.acceptance import test_phase_2d_integration as fixtures


class Phase2DOriginalVerdict(unittest.TestCase):
    def setUp(self):
        self.original = fixtures.Phase2DOriginalVolumeCollection()
        self.original.setUp()
        self.addCleanup(self.original.doCleanups)
        self.fixture = self.original.fixture
        self.result = self.original.collect()
        self.owner = self.original.bridge.freeze
        self.owner.installation.growth = SimpleNamespace(store=self.fixture.store)
        self.fixture.validate(self.result)
        self.fixture.approve_frozen(self.result)

    def verdict(self, owner):
        return self.fixture.store.verdict(
            "run",
            self.fixture.model.project_id,
            self.result.binding,
            "lease",
            frozen_owner=owner,
        )

    def test_exact_original_projection_verdict_never_reopens_global_path(self):
        with patch("crewshal.candidate._scan", side_effect=AssertionError("global path forbidden")):
            result = self.verdict(self.owner)
        self.assertEqual(result.status, "verified")
        self.assertFalse(result.execution_allowed)

    def test_copied_owner_and_caller_flag_cannot_supply_projection_custody(self):
        clone = object.__new__(OriginalVolumeFreeze)
        clone.__dict__.update(self.owner.__dict__)
        for substitute in (clone, True, SimpleNamespace(manifest=self.result.frozen)):
            with self.subTest(substitute=type(substitute)), self.assertRaises(ValueError):
                self.verdict(substitute)
        self.assertEqual(self.verdict(self.owner).status, "verified")

    def test_original_projection_requires_same_journal_and_collection(self):
        self.owner.installation.growth.store = object()
        with self.assertRaisesRegex(ValueError, "store or collection"):
            self.verdict(self.owner)

    def test_original_projection_changes_refuse_before_verdict(self):
        (self.fixture.frozen / "README.md").write_bytes(b"changed original projection")
        with self.assertRaises(ValueError):
            self.verdict(self.owner)

    def test_path_and_original_projection_cannot_supply_two_readbacks(self):
        with self.assertRaisesRegex(ValueError, "exact frozen candidate readback"):
            self.fixture.store.verdict(
                "run",
                self.fixture.model.project_id,
                self.result.binding,
                "lease",
                candidate_root=self.fixture.frozen,
                frozen_owner=self.owner,
            )
