"""Offline falsification checks for frozen synthetic network observations."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crewshal.qualification import Qualification, assess_qualification
from scripts.network_client import packet
from scripts.probe_linux_network import (
    client_passes,
    load_manifest,
    network_passes,
    run_probe,
    verify_grant,
)
from scripts.probe_linux_profile import digest


class Phase2CNetwork(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]

    def report(self) -> dict:
        return json.loads(
            (self.root / "docs/qualification/phase-2c-network-v3-observed.json").read_text()
        )

    def test_zero_traffic_without_working_bracketing_controls_cannot_pass(self) -> None:
        original = self.report()
        self.assertTrue(network_passes(original))
        for label in ("before", "after"):
            changed = copy.deepcopy(original)
            changed["clients"][label]["result"]["outcomes"][0]["echo"] = False
            self.assertFalse(network_passes(changed))
        changed = copy.deepcopy(original)
        changed["sink_events"] = []
        self.assertFalse(network_passes(changed))

    def test_incomplete_duplicate_or_sent_denied_attempts_cannot_pass(self) -> None:
        original = self.report()["clients"]["denied"]
        self.assertTrue(client_passes(original, "denied"))
        for mutate in (
            lambda x: x["result"]["outcomes"].pop(),
            lambda x: x["result"]["outcomes"].append(x["result"]["outcomes"][0]),
            lambda x: x["result"]["outcomes"][0].update(sent=True),
            lambda x: x["result"]["outcomes"][0].update(connected=True),
            lambda x: x["result"]["outcomes"][0].update(payload_hex="00"),
            lambda x: x["result"]["outcomes"][0].update(family="unknown"),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertFalse(client_passes(changed, "denied"))

    def test_sink_receipts_and_zero_delta_are_independent_required_evidence(self) -> None:
        original = self.report()
        for mutate in (
            lambda x: x.update(events_after_denial=13),
            lambda x: x["sink_events"].append({"payload_hex": "666f7262696464656e"}),
            lambda x: x["sink_events"].pop(),
            lambda x: x["sink_events"][0].update(payload_hex="00"),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertFalse(network_passes(changed))

    def test_terminal_integrity_and_cleanup_cannot_be_replaced_by_child_claims(self) -> None:
        original = self.report()
        for field in (
            "sink_grants_verified",
            "sink_heartbeat_advanced",
            "sink_inputs_unchanged",
            "network_verified",
            "cleanup_ok",
        ):
            changed = copy.deepcopy(original)
            changed[field] = False
            self.assertFalse(network_passes(changed))
        for mutate in (
            lambda x: x["terminal"].update(ExitCode=1),
            lambda x: x["terminal"].update(Running=True),
            lambda x: x["terminal"].update(Pid=42),
            lambda x: x["terminal"].update(OOMKilled=True),
            lambda x: x.update(deadline_exceeded=True),
            lambda x: x.update(protected_unchanged=False),
        ):
            changed = copy.deepcopy(original)
            mutate(changed["clients"]["denied"])
            self.assertFalse(network_passes(changed))

    def test_widened_engine_grant_refuses_before_start(self) -> None:
        original = self.report()["clients"]["denied"]["inspection"]
        root = Path("<synthetic-root>/denied")
        self.assertTrue(verify_grant(original, root, "none", "denied"))
        for mutate in (
            lambda x: x["HostConfig"].update(NetworkMode="bridge"),
            lambda x: x["HostConfig"].update(ReadonlyRootfs=False),
            lambda x: x["HostConfig"].update(Privileged=True),
            lambda x: x["HostConfig"].update(CapDrop=[]),
            lambda x: x["HostConfig"].update(PidsLimit=64),
            lambda x: x["HostConfig"].update(Tmpfs={}),
            lambda x: x["Mounts"].append(
                {"Type": "bind", "Source": "/host", "Destination": "/host", "RW": True}
            ),
            lambda x: x["Config"]["Env"].append("OPENAI_API_KEY=synthetic"),
            lambda x: x["Config"].update(Cmd=["/input/other.py"]),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertFalse(verify_grant(changed, root, "none", "denied"))
        commands = []

        def fake(argv: list[str], environment: dict) -> dict:
            commands.append(argv)
            stdout = (
                '[{"Internal":true,"EnableIPv6":true,"Driver":"bridge"}]'
                if argv[:2] == ["network", "inspect"]
                else "[{}]"
            )
            return {"exit": 0, "stdout": stdout}

        with (
            tempfile.TemporaryDirectory() as name,
            patch("scripts.probe_linux_network.docker_capture", fake),
        ):
            result = run_probe(Path(name), {})
        self.assertFalse(result["passed"])
        self.assertNotIn("start", [c[0] for c in commands])
        self.assertTrue(any(c[:2] == ["rm", "--force"] for c in commands))

    def test_frozen_source_and_original_criteria_drift_refuse(self) -> None:
        path = self.root / "docs/qualification/phase-2c-network-v3.json"
        expected = "82df51dd5acd305602b2cb826bbd56d305e5669c15e0d71c06c9f007bdf36eef"
        self.assertEqual(load_manifest(path, expected)["executed_subset"], ["network-egress"])
        for field in ("mandatory_cases", "sources"):
            changed = json.loads(path.read_text())
            if field == "mandatory_cases":
                changed[field][8]["criterion"] = "Allow egress"
            else:
                changed[field].pop("scripts/network_sink.py")
            with tempfile.TemporaryDirectory() as name:
                altered = Path(name) / "manifest.json"
                altered.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, "frozen protocol/source/image mismatch"):
                    load_manifest(altered, digest(altered.read_bytes()))
        with self.assertRaisesRegex(ValueError, "manifest digest mismatch"):
            load_manifest(path, "0" * 64)
        for version in (1, 2):
            manifest = json.loads(
                (self.root / f"docs/qualification/phase-2c-network-v{version}.json").read_text()
            )
            archived = self.root / f"docs/qualification/phase-2c-network-v{version}-runner.txt"
            self.assertEqual(
                digest(archived.read_bytes()), manifest["sources"]["scripts/probe_linux_network.py"]
            )

    def test_dns_payload_is_standard_query_wire_with_explicit_synthetic_name(self) -> None:
        query = packet("denied", "primary", "ipv6", "dns")
        self.assertEqual(query[:12], bytes.fromhex("2c0101000001000000000000"))
        self.assertEqual(
            query[12:],
            b"\x06denied\x07primary\x04ipv6\x03dns\x09synthetic\x07invalid\x00\x00\x01\x00\x01",
        )

    def test_subset_and_stale_identity_never_authorize_runtime(self) -> None:
        record = Qualification.model_validate(self.report()["qualification"])
        self.assertEqual(
            {p.case for p in record.results if p.status == "passed"}, {"network-egress"}
        )
        self.assertIsNone(record.identity.credential_design)
        decision = assess_qualification(record, record.identity)
        self.assertEqual(decision.status, "denied")
        self.assertFalse(decision.execution_allowed)
        current = record.identity.model_copy(update={"image": "0" * 64})
        self.assertIn("stale qualification identity", assess_qualification(record, current).reasons)


if __name__ == "__main__":
    unittest.main()
