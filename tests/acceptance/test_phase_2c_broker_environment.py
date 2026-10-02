"""Offline refusal and independent-oracle checks; not live broker qualification."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import probe_broker_environment as probe


class Phase2CBrokerEnvironment(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]
    manifest = root / "docs/qualification/phase-2c-broker-environment-v3.json"

    def test_existing_report_and_dangling_symlink_refuse_before_probe(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / "report.json"
            output.write_bytes(b"preserved evidence")
            for path in (output, Path(name) / "link.json"):
                if path != output:
                    path.symlink_to(Path(name) / "missing")
                arguments = [
                    "probe",
                    "--bundle",
                    name,
                    "--manifest",
                    str(self.manifest),
                    "--manifest-sha256",
                    "0" * 64,
                    "--docker-host",
                    "unix:///synthetic.sock",
                    "--output",
                    str(path),
                ]
                with patch("sys.argv", arguments), patch.object(probe, "run_probe") as run:
                    with self.assertRaises(FileExistsError):
                        probe.main()
                    run.assert_not_called()
            self.assertEqual(output.read_bytes(), b"preserved evidence")

    def test_failed_command_and_missing_fallback_notice_cannot_pass_store(self) -> None:
        commands = [{"arguments": list(c), "exit": 0} for c in probe.COMMANDS]
        commands[3]["stdout"] = "provider.crewshal.invalid CREWSHAL_SYNTHETIC_API_KEY"
        state = {"credential_blob_present": True, "private_directory": True}
        self.assertFalse(probe.assess(commands, state, True, True)["file_store_observed"])
        commands[2]["stderr"] = "No keychain detected"
        commands[2]["exit"] = None
        self.assertFalse(probe.assess(commands, state, True, True)["file_store_observed"])

    def test_store_success_never_grants_broker_or_worker_authority(self) -> None:
        commands = [{"arguments": list(c), "exit": 0} for c in probe.COMMANDS]
        commands[2]["stderr"] = "No keychain detected"
        commands[3]["stdout"] = "provider.crewshal.invalid CREWSHAL_SYNTHETIC_API_KEY"
        state = {"credential_blob_present": True, "private_directory": True}
        result = probe.assess(commands, state, True, True)
        self.assertTrue(result["file_store_observed"])
        self.assertEqual(result["status"], "denied")
        self.assertFalse(result["execution_allowed"])
        self.assertFalse(result["local_sandbox_available"])
        self.assertIn("unavailable", result["request_authority"])

    def test_failed_or_incomplete_oracles_and_cleanup_cannot_pass_store(self) -> None:
        commands = [{"arguments": list(c), "exit": 0} for c in probe.COMMANDS]
        commands[2]["stderr"] = "No keychain detected"
        commands[3]["stdout"] = "provider.crewshal.invalid CREWSHAL_SYNTHETIC_API_KEY"
        state = {"credential_blob_present": True, "private_directory": True}
        for c, s, grant, removed in (
            (commands[:-1], state, True, True),
            (commands[::-1], state, True, True),
            (commands, {}, True, True),
            (commands, {**state, "private_directory": False}, True, True),
            (commands, state, False, True),
            (commands, state, True, False),
        ):
            self.assertFalse(probe.assess(c, s, grant, removed)["file_store_observed"])

    def test_manifest_drift_refuses_before_docker(self) -> None:
        original = json.loads(self.manifest.read_text())
        for mutate in (
            lambda m: m.update(schema_version=True),
            lambda m: m["limits"].update(memory_bytes=536870912),
            lambda m: m["grant"].update(network=["provider.crewshal.invalid"]),
            lambda m: m["mandatory_cases"].pop(),
            lambda m: m.update(sandbox_launch_allowed=True),
            lambda m: m["commands"].append(["login"]),
            lambda m: m["environment"].update(SSH_AUTH_SOCK="/real/agent"),
            lambda m: m["host_limits"].update(memory_bytes=536870912),
            lambda m: m["sources"].update({"scripts/probe_broker_environment.py": "0" * 64}),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            with tempfile.TemporaryDirectory() as name:
                path = Path(name) / "manifest.json"
                path.write_text(json.dumps(changed))
                with patch.object(probe.subprocess, "run") as execute:
                    with self.assertRaisesRegex(ValueError, "protocol mismatch"):
                        probe.run_probe(
                            Path(name),
                            path,
                            probe.digest(path.read_bytes()),
                            "unix:///synthetic/engine.sock",
                        )
                    execute.assert_not_called()

    def test_unknown_bundle_and_remote_endpoint_refuse_before_docker(self) -> None:
        with tempfile.TemporaryDirectory() as name, patch.object(probe.subprocess, "run") as run:
            for endpoint, message in (
                ("tcp://remote:2375", "local Unix"),
                ("unix:///synthetic/engine.sock", "bundle identity"),
            ):
                with self.assertRaisesRegex(ValueError, message):
                    probe.run_probe(
                        Path(name),
                        self.manifest,
                        probe.digest(self.manifest.read_bytes()),
                        endpoint,
                    )
            run.assert_not_called()

    def test_effective_engine_privilege_mount_environment_and_resource_drift_refuse(self) -> None:
        record = json.loads(
            (
                self.root / "docs/qualification/phase-2c-broker-environment-v3-observed.json"
            ).read_text()
        )
        info = record["inspect_before"]
        bundle = Path("<pinned-bundle>")
        self.assertTrue(probe.verify_grant(info, bundle))
        for mutate in (
            lambda x: x["HostConfig"].update(Privileged=True),
            lambda x: x["HostConfig"].update(NetworkMode="bridge"),
            lambda x: x["HostConfig"].update(Memory=536870912),
            lambda x: x["HostConfig"].update(PidsLimit=128),
            lambda x: x["HostConfig"].update(CapAdd=["SYS_ADMIN"]),
            lambda x: x["HostConfig"].update(Devices=[{"PathOnHost": "/dev/kvm"}]),
            lambda x: x["Config"]["Env"].append("OPENAI_API_KEY=synthetic"),
            lambda x: x["Mounts"][0].update(RW=True),
            lambda x: x["Mounts"].append(
                {"Type": "bind", "Source": "/real/home", "Destination": "/host", "RW": False}
            ),
        ):
            changed = copy.deepcopy(info)
            mutate(changed)
            self.assertFalse(probe.verify_grant(changed, bundle))

    def test_frozen_records_preserve_twenty_cases_and_failed_first_oracle(self) -> None:
        manifest = probe.load_manifest(self.manifest, probe.digest(self.manifest.read_bytes()))
        original = json.loads((self.root / "docs/qualification/phase-2c-v1.json").read_text())
        for key in ("grant", "limits", "mandatory_cases"):
            self.assertEqual(manifest[key], original[key])
        v1 = json.loads(
            (
                self.root / "docs/qualification/phase-2c-broker-environment-v1-observed.json"
            ).read_text()
        )
        self.assertFalse(v1["decision"]["file_store_observed"])
        for suffix in ("observed", "repeat"):
            report = json.loads(
                (
                    self.root / f"docs/qualification/phase-2c-broker-environment-v3-{suffix}.json"
                ).read_text()
            )
            self.assertEqual(report["manifest_sha256"], probe.digest(self.manifest.read_bytes()))
            self.assertTrue(report["decision"]["file_store_observed"])
            self.assertTrue(report["fixture_removed"])
            self.assertEqual(
                [c["case"] for c in report["mandatory_results"]],
                [c["id"] for c in original["mandatory_cases"]],
            )
            self.assertTrue(all(c["status"] == "unavailable" for c in report["mandatory_results"]))


if __name__ == "__main__":
    unittest.main()
