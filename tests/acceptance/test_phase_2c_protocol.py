"""Offline refusals for the prospective SBX resource/configuration protocol."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.assess_sbx_protocol import COMMANDS, assess, capture, load_manifest, run_assessment
from scripts.probe_linux_profile import digest


class Phase2CProtocol(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]
    manifest = root / "docs/qualification/phase-2c-sbx-protocol-v1.json"

    def commands(self) -> list[dict]:
        return [
            {"arguments": list(c), "exit": 0, "stdout": "Minimum: 512 MiB", "stderr": ""}
            for c in COMMANDS
        ]

    def test_help_and_minimum_cannot_qualify_nested_worker_or_credentials(self) -> None:
        result = assess(self.commands())
        self.assertTrue(result["help_complete"])
        self.assertEqual(result["advertised_outer_minimum_bytes"], 536870912)
        self.assertEqual(result["frozen_worker_memory_bytes"], 134217728)
        self.assertEqual(result["status"], "denied")
        self.assertFalse(result["operational_launch_allowed"])
        self.assertFalse(result["execution_allowed"])
        self.assertIn("unavailable", result["nested_worker_mapping"])
        self.assertIn("unavailable", result["request_authority"])

    def test_incomplete_failed_duplicate_or_reordered_help_is_unavailable(self) -> None:
        for mutate in (
            lambda x: x.pop(),
            lambda x: x[0].update(exit=1),
            lambda x: x.append(x[0]),
            lambda x: x.reverse(),
        ):
            commands = self.commands()
            mutate(commands)
            result = assess(commands)
            self.assertFalse(result["help_complete"])
            self.assertIsNone(result["advertised_outer_minimum_bytes"])
            self.assertEqual(result["status"], "denied")

    def test_operational_commands_refuse_without_spawning(self) -> None:
        for command in (("daemon", "start"), ("settings", "list"), ("login",), ("create", "shell")):
            with patch("scripts.assess_sbx_protocol.subprocess.run") as execute:
                with self.assertRaisesRegex(ValueError, "help-only allowlist"):
                    capture(Path("/synthetic/sbx"), command, Path("/synthetic/home"))
                execute.assert_not_called()

    def test_protocol_preserves_every_original_criterion_and_worker_limit(self) -> None:
        manifest = load_manifest(self.manifest, digest(self.manifest.read_bytes()))
        original = json.loads((self.root / "docs/qualification/phase-2c-v1.json").read_text())
        for key in ("grant", "limits", "mandatory_cases"):
            self.assertEqual(manifest[key], original[key])
        self.assertFalse(manifest["outer_proposal"]["launch_allowed"])
        self.assertEqual(manifest["outer_proposal"]["approval"], "pending")

    def test_changed_resource_config_sources_and_commands_refuse_before_capture(self) -> None:
        original = json.loads(self.manifest.read_text())
        for mutate in (
            lambda x: x["limits"].update(memory_bytes=536870912),
            lambda x: x["outer_proposal"].update(approval="accepted", launch_allowed=True),
            lambda x: x["commands"].append(["settings", "list"]),
            lambda x: x["grant"].update(configuration="inherit host settings"),
            lambda x: x["mandatory_cases"].pop(),
            lambda x: x["sources"].update({"scripts/assess_sbx_protocol.py": "0" * 64}),
            lambda x: x.update(schema_version=True),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            with tempfile.TemporaryDirectory() as name:
                altered = Path(name) / "manifest.json"
                altered.write_text(json.dumps(changed))
                with patch("scripts.assess_sbx_protocol.capture") as execute:
                    with self.assertRaisesRegex(ValueError, "frozen protocol"):
                        run_assessment(Path("/absent/sbx"), altered, digest(altered.read_bytes()))
                    execute.assert_not_called()

    def test_unknown_binary_and_manifest_refuse_before_capture(self) -> None:
        with patch("scripts.assess_sbx_protocol.capture") as execute:
            with self.assertRaisesRegex(ValueError, "manifest digest mismatch"):
                run_assessment(Path("/absent/sbx"), self.manifest, "0" * 64)
            with tempfile.TemporaryDirectory() as name:
                binary = Path(name) / "sbx"
                binary.write_bytes(b"untrusted binary")
                with self.assertRaisesRegex(ValueError, "binary mismatch"):
                    run_assessment(binary, self.manifest, digest(self.manifest.read_bytes()))
            execute.assert_not_called()

    def test_help_timeout_output_limit_and_environment_do_not_upgrade(self) -> None:
        import subprocess

        with patch("scripts.assess_sbx_protocol.subprocess.run") as execute:
            execute.side_effect = subprocess.TimeoutExpired("sbx", 10)
            result = capture(Path("/synthetic/sbx"), COMMANDS[0], Path("/synthetic/home"))
            self.assertIsNone(result["exit"])
            self.assertEqual(
                execute.call_args.kwargs["env"],
                {
                    "HOME": "/synthetic/home",
                    "XDG_CONFIG_HOME": "/synthetic/home",
                    "PATH": "/usr/bin:/bin",
                },
            )
            self.assertIn("(deny network*)", execute.call_args.args[0][2])
        with patch("scripts.assess_sbx_protocol.subprocess.run") as execute:
            execute.return_value = subprocess.CompletedProcess("sbx", 0, b"x" * 65537, b"")
            result = capture(Path("/synthetic/sbx"), COMMANDS[0], Path("/synthetic/home"))
            self.assertIsNone(result["exit"])
            self.assertEqual(result["error"], "help output limit exceeded")


if __name__ == "__main__":
    unittest.main()
