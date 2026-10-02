"""Offline failure cases for the synthetic lifecycle parent oracle."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from crewshal.qualification import Qualification, assess_qualification
from scripts.probe_linux_lifecycle import digest, lifecycle_passes, load_manifest, run_case


class Phase2CLifecycle(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]

    def report(self) -> dict:
        return json.loads(
            (self.root / "docs/qualification/phase-2c-lifecycle-v1-observed.json").read_text()
        )

    def test_terminal_or_activity_failure_cannot_pass_lifecycle(self) -> None:
        original = self.report()["observations"][0]
        self.assertTrue(lifecycle_passes(original, "cancel"))
        mutations = [
            lambda x: x["terminal"].update(Running=True),
            lambda x: x["terminal"].update(ExitCode=0),
            lambda x: x["terminal"].update(OOMKilled=True),
            lambda x: x.update(heartbeat_stopped=False),
            lambda x: x.update(heartbeat_before=0),
            lambda x: x.update(detached_descendant=False),
            lambda x: x.update(kill_exit=1),
            lambda x: x.update(removed=False),
            lambda x: x.update(protected_unchanged=False),
            lambda x: x.update(grant_verified=False),
            lambda x: x.update(termination_reason="completed"),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertFalse(lifecycle_passes(changed, "cancel"))

    def test_late_or_early_kill_does_not_establish_deadline(self) -> None:
        original = self.report()["observations"][1]
        self.assertTrue(lifecycle_passes(original, "deadline"))
        for seconds in (0, 4, 5.3, 10):
            changed = copy.deepcopy(original)
            changed["kill_requested_seconds"] = seconds
            self.assertFalse(lifecycle_passes(changed, "deadline"))

    def test_validator_exit_cannot_replace_candidate_integrity(self) -> None:
        original = self.report()["observations"][2]
        self.assertTrue(lifecycle_passes(original, "validator"))
        for field in ("validated", "protected_unchanged", "grant_verified", "removed"):
            changed = copy.deepcopy(original)
            changed[field] = False
            self.assertFalse(lifecycle_passes(changed, "validator"))

    def test_unsafe_grant_refuses_start_and_cleans_unique_handle(self) -> None:
        commands = []

        def fake_capture(argv: list[str], environment: dict) -> dict:
            commands.append(argv)
            return {"argv": argv, "exit": 0, "stdout": "[{}]" if argv[0] == "inspect" else ""}

        with tempfile.TemporaryDirectory() as name:
            with patch("scripts.probe_linux_lifecycle.docker_capture", fake_capture):
                result = run_case(Path(name), {}, "cancel")
        self.assertFalse(result["passed"])
        self.assertNotIn("start", [argv[0] for argv in commands])
        self.assertEqual(commands[-1][:2], ["rm", "--force"])
        self.assertTrue(commands[-1][2].startswith("crewshal-2c-lifecycle-"))

    def test_frozen_protocol_and_drift_refusal_before_creation(self) -> None:
        manifest = self.root / "docs/qualification/phase-2c-lifecycle-v1.json"
        expected = "930e601021f95e01488f10582feb5adadc4bdd76c566edbd34486d0feb93b2ef"
        self.assertEqual(digest(manifest.read_bytes()), expected)
        self.assertEqual(
            load_manifest(manifest, expected)["executed_subset"],
            ["descendant-escape", "cancellation", "deadline", "credential-free-validation"],
        )
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / "observation.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.probe_linux_lifecycle",
                    "--docker-host",
                    "unix:///synthetic/nonexistent",
                    "--manifest",
                    str(manifest),
                    "--manifest-sha256",
                    "0" * 64,
                    "--output",
                    str(output),
                ],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("prospectively frozen manifest digest mismatch", result.stderr)
            self.assertFalse(output.exists())

    def test_subset_never_promotes_unexercised_native_or_broker_cases(self) -> None:
        report = self.report()
        record = Qualification.model_validate(report["qualification"])
        passed = {result.case for result in record.results if result.status == "passed"}
        self.assertEqual(
            passed, {"descendant-escape", "cancellation", "deadline", "credential-free-validation"}
        )
        decision = assess_qualification(record, record.identity)
        self.assertEqual(decision.status, "denied")
        self.assertFalse(decision.execution_allowed)
        self.assertIsNone(record.identity.credential_design)
        changed = record.identity.model_copy(update={"configuration": "0" * 64})
        self.assertIn("stale qualification identity", assess_qualification(record, changed).reasons)


if __name__ == "__main__":
    unittest.main()
