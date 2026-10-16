"""Offline broker wire checks do not establish Linux installation acceptance."""

import hashlib
import os
from pathlib import Path
import tempfile
import time
import unittest

from crewshal.contracts import record_digest
from crewshal.linux_qualification_fixture import (
    FrozenQualificationTLS,
    RetainedTLSBrokerLifetime,
    _broker_controls,
    _json,
    _progress_record,
)
from crewshal.supervisor import CgroupIdentity, OwnedCgroup
from tests.acceptance import test_phase_2d_qualification_fixture as fixtures


def _plan() -> FrozenQualificationTLS:
    return FrozenQualificationTLS(
        fixture=fixtures._plan(),
        certificate_sha256="c" * 64,
        private_key_sha256="d" * 64,
        zstd_library_sha256="e" * 64,
        listener_addresses={
            "qualification-1": ("10.203.0.1", 443),
            "qualification-2": ("10.203.1.1", 443),
        },
        peer_addresses={"qualification-1": "10.203.0.2", "qualification-2": "10.203.1.2"},
        bootstrap_replies={
            "/backend-api/wham/usage": "{}",
            "/backend-api/codex/models?client_version=0.160.1": "{}",
        },
    )


def _record(plan: FrozenQualificationTLS, origin: float, lane: str) -> dict[str, object]:
    catalog = fixtures._tools()
    return {
        "lane": lane,
        "plan": record_digest(plan),
        "fixture": record_digest(plan.fixture),
        "origin": origin,
        "catalog": catalog if lane == "qualification-1" else None,
        "catalog_sha256": hashlib.sha256(_json(catalog)).hexdigest(),
        "outputs": {lane + "-stdin": fixtures._complete_output()},
        "bootstrap": sorted(plan.bootstrap_replies),
    }


class TLSBrokerWireTests(unittest.TestCase):
    def test_actual_raw_tool_list_is_preserved_in_both_original_lane_records(self) -> None:
        plan, origin = _plan(), time.monotonic()
        first = _record(plan, origin, "qualification-1")
        observed = _progress_record(_json(first), plan, origin, "qualification-1", None)
        self.assertEqual(observed, first)
        second = _record(plan, origin, "qualification-2")
        observed = _progress_record(
            _json(second), plan, origin, "qualification-2", first["catalog"]
        )
        self.assertEqual(observed, second)
        self.assertIsNone(observed["catalog"])

    def test_changed_identity_bootstrap_or_catalog_refuses(self) -> None:
        plan, origin = _plan(), time.monotonic()
        for field, replacement in (
            ("lane", "live"),
            ("plan", "f" * 64),
            ("fixture", "f" * 64),
            ("origin", origin + 0.001),
            ("origin", True),
            ("bootstrap", []),
            ("catalog", {}),
            ("catalog_sha256", "f" * 64),
        ):
            value = _record(plan, origin, "qualification-1")
            value[field] = replacement
            with self.subTest(field=field, value=replacement), self.assertRaises(ValueError):
                _progress_record(_json(value), plan, origin, "qualification-1", None)

    def test_second_lane_cannot_replace_original_catalog(self) -> None:
        plan, origin = _plan(), time.monotonic()
        value = _record(plan, origin, "qualification-2")
        value["catalog"] = fixtures._tools()
        with self.assertRaisesRegex(ValueError, "cannot replace"):
            _progress_record(_json(value), plan, origin, "qualification-2", fixtures._tools())
        value["catalog"] = None
        with self.assertRaisesRegex(ValueError, "differ"):
            _progress_record(_json(value), plan, origin, "qualification-2", fixtures._tools()[:2])

    def test_missing_failed_or_incomplete_native_report_remains_unknown(self) -> None:
        plan, origin = _plan(), time.monotonic()
        for output in (
            {},
            {"qualification-1-stdin": "Process exited with code 0\n{}"},
            {"qualification-1-stdin": "Process running with session ID 1"},
        ):
            value = _record(plan, origin, "qualification-1")
            value["outputs"] = output
            with self.subTest(output=output), self.assertRaises(ValueError):
                _progress_record(_json(value), plan, origin, "qualification-1", None)

    def test_duplicate_progress_keys_refuse(self) -> None:
        plan, origin = _plan(), time.monotonic()
        raw = _json(_record(plan, origin, "qualification-1"))
        raw = b'{"lane":"qualification-1",' + raw[1:]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            _progress_record(raw, plan, origin, "qualification-1", None)

    def test_caller_cannot_construct_or_launch_an_unowned_broker(self) -> None:
        with self.assertRaisesRegex(ValueError, "original installation"):
            RetainedTLSBrokerLifetime()
        with self.assertRaisesRegex(ValueError, "one-shot"):
            RetainedTLSBrokerLifetime.launch(
                object(), _plan(), {}, certificate_fd=1, private_key_fd=2, zstd_library_fd=3
            )

    def test_broker_uses_its_original_64_mib_16_task_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = {
                "memory.max": "67108864",
                "pids.max": "16",
                "memory.swap.max": "0",
                "cpu.max": "100000 100000",
                "cgroup.type": "domain",
                "cgroup.events": "populated 0\nfrozen 0\n",
                "cgroup.procs": "",
                "memory.events": "max 0\noom 0\noom_kill 0\n",
                "pids.events": "max 0\n",
            }
            for name, value in controls.items():
                (root / name).write_text(value)
            descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            info = os.fstat(descriptor)
            group = OwnedCgroup(
                descriptor,
                CgroupIdentity(
                    relative_path="offline/broker", device=info.st_dev, inode=info.st_ino
                ),
            )
            os.close(descriptor)
            try:
                _broker_controls(group, empty=True)
                (root / "memory.max").write_text("134217728")
                with self.assertRaisesRegex(ValueError, "controls differ"):
                    _broker_controls(group, empty=True)
                (root / "memory.max").write_text("67108864")
                (root / "memory.events").write_text("max 1\noom 0\noom_kill 0\n")
                with self.assertRaisesRegex(ValueError, "resource refusal"):
                    _broker_controls(group, empty=True)
            finally:
                group.close()


if __name__ == "__main__":
    unittest.main()
