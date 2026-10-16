"""Exercise observer custody refusal without a Linux or provider operation."""

import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from crewshal.linux_batch import (
    OriginalQualificationCollector,
    _directory_identity,
    _require_original,
    accept_original_live,
    capture_original_live,
    finish_original_lane,
)
from crewshal.linux_bridge import StoppedNativeBridge
from crewshal.qualification import QualificationIdentity
import tests.acceptance.test_phase_2d_qualification_fixture as fixtures


def _identity() -> QualificationIdentity:
    return QualificationIdentity(
        host_os="linux",
        host_kernel="pinned",
        architecture="aarch64",
        substrate="bubblewrap",
        substrate_version="0.11.0",
        image="a" * 64,
        runtime="codex-rust-v0.160.1",
        toolchain="b" * 64,
        configuration="c" * 64,
        grant="d" * 64,
        harness="e" * 64,
        manifest="f" * 64,
        credential_design="0" * 64,
    )


class OriginalBatchTests(unittest.TestCase):
    def test_parsed_or_flagged_driver_cannot_supply_original_ownership(self) -> None:
        for value in (True, SimpleNamespace(accepted=True), {"installed": True}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "complete original"):
                _require_original(value)  # type: ignore[arg-type]

    def test_qualification_refuses_parsed_bridge_and_live_lane(self) -> None:
        with self.assertRaisesRegex(ValueError, "original bridge"):
            OriginalQualificationCollector(
                None, SimpleNamespace(), fixtures._plan(), _identity(), None, None, None
            )  # type: ignore[arg-type]
        bridge = object.__new__(StoppedNativeBridge)
        for lane in ("live", "unlisted"):
            bridge.lane_context = SimpleNamespace(lane_id=lane)  # type: ignore[assignment]
            with self.subTest(lane=lane), self.assertRaisesRegex(ValueError, "refuses live"):
                OriginalQualificationCollector(
                    None, bridge, fixtures._plan(), _identity(), None, None, None
                )  # type: ignore[arg-type]

    def test_failed_collector_retains_original_slot_and_cannot_be_replaced(self) -> None:
        bridge = object.__new__(StoppedNativeBridge)
        context = SimpleNamespace(lane_id="qualification-1")
        bridge.lane_context = context  # type: ignore[assignment]
        with patch.object(
            OriginalQualificationCollector,
            "verify",
            side_effect=ValueError("independent readback failed"),
        ):
            with self.assertRaisesRegex(ValueError, "independent readback"):
                OriginalQualificationCollector(
                    None, bridge, fixtures._plan(), _identity(), None, None, None
                )  # type: ignore[arg-type]
        retained = context._qualification_collector
        self.assertTrue(retained.failed)
        with self.assertRaisesRegex(ValueError, "no replacement"):
            OriginalQualificationCollector(
                None, bridge, fixtures._plan(), _identity(), None, None, None
            )  # type: ignore[arg-type]
        self.assertIs(context._qualification_collector, retained)

    def test_failed_collection_consumes_original_attempt_without_reset(self) -> None:
        collector = object.__new__(OriginalQualificationCollector)
        collector.consumed = collector.failed = False
        with patch.object(collector, "verify", side_effect=ValueError("kernel state unknown")):
            with self.assertRaisesRegex(ValueError, "kernel state unknown"):
                collector.collect(None)  # type: ignore[arg-type]
        self.assertTrue(collector.consumed)
        self.assertTrue(collector.failed)
        with self.assertRaisesRegex(ValueError, "no retry"):
            collector.collect(None)  # type: ignore[arg-type]

    def test_directory_identity_refuses_intermediate_link_and_uses_original_fd(self) -> None:
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            (root / "home" / "owner").mkdir(parents=True)
            (root / "alias").symlink_to("home", target_is_directory=True)
            descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                expected = (root / "home" / "owner").stat()
                self.assertEqual(
                    _directory_identity(descriptor, "home/owner"),
                    (expected.st_dev, expected.st_ino),
                )
                with self.assertRaises(OSError):
                    _directory_identity(descriptor, "alias/owner")
                root.rename(root.with_name(root.name + "-moved"))
                try:
                    self.assertEqual(
                        _directory_identity(descriptor, "home/owner"),
                        (expected.st_dev, expected.st_ino),
                    )
                finally:
                    root.with_name(root.name + "-moved").rename(root)
            finally:
                os.close(descriptor)

    def test_live_and_finish_operations_refuse_flags_before_effects(self) -> None:
        with self.assertRaisesRegex(ValueError, "complete original"):
            capture_original_live(
                True,
                None,
                None,
                expected_run_version=1,
                expected_attempt_version=1,
                token="unused",
                initial=None,
            )  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "complete original"):
            accept_original_live(True, None, None, None, project_id="unused", token="unused")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "original schedule"):
            finish_original_lane(True, None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
