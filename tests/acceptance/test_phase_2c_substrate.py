"""Independent inspection of substrate grants, observations and failure fixtures."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.probe_linux_profile import snapshot, verify_grant


class Phase2CSubstrate(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]

    def load(self, name: str) -> dict:
        return json.loads((self.root / "docs/qualification" / name).read_text())

    def test_frozen_v4_preserves_all_mandatory_cases_and_grants(self) -> None:
        old = self.load("phase-2c-v1.json")
        current = self.load("phase-2c-substrate-v4.json")
        self.assertEqual(current["mandatory_cases"], old["mandatory_cases"])
        self.assertEqual(current["grant"], old["grant"])
        self.assertEqual(
            current["harness"],
            hashlib.sha256((self.root / "scripts/probe_linux_profile.py").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            hashlib.sha256(
                (self.root / "docs/qualification/phase-2c-substrate-v4.json").read_bytes()
            ).hexdigest(),
            "6f4c5a568f89ad16fa6b5754247938bb816ae6c8cb71fd2b12746f95b0af4db1",
        )

    def test_observations_do_not_promote_unexercised_boundaries(self) -> None:
        old = self.load("phase-2c-substrate-v2-observed.json")
        self.assertFalse(old["approved_writes_observed"])
        self.assertEqual(old["decision"]["status"], "denied")
        current = self.load("phase-2c-substrate-v4-observed.json")
        cases = {x["case"]: x["status"] for x in current["qualification"]["results"]}
        self.assertEqual(sum(x == "passed" for x in cases.values()), 9)
        for case in (
            "network-egress",
            "repository-hooks",
            "global-hooks",
            "mcp-plugins-instructions",
            "descendant-escape",
            "cancellation",
            "deadline",
            "credential-mediation",
            "credential-free-validation",
            "configuration-binding",
            "qualification-refusal",
        ):
            self.assertEqual(cases[case], "unavailable")
        self.assertTrue(current["effective_grant_verified"])
        self.assertTrue(current["protected_fixtures_unchanged"])
        self.assertTrue(current["fixture_container_removed"])
        self.assertEqual(current["decision"]["status"], "denied")
        self.assertFalse(current["decision"]["execution_allowed"])
        self.assertIsNone(current["qualification"]["identity"]["credential_design"])
        terminal = next(
            command
            for command in current["commands"]
            if command["argv"][1:3] == ["inspect", "--format"]
        )
        state = json.loads(terminal["stdout"])
        self.assertFalse(state["Running"])
        self.assertEqual(state["ExitCode"], 0)
        self.assertEqual(
            current["owned_files"]["relative-excluded-link"]["content"], "../../original/canary"
        )
        self.assertEqual(current["owned_files"]["relative-link"]["content"], "../../input")
        self.assertEqual(
            current["owned_files"]["moved.txt"]["content"],
            hashlib.sha256(b"synthetic-readable").hexdigest(),
        )

    def test_effective_grant_rejects_engine_weakening(self) -> None:
        report = self.load("phase-2c-substrate-v4-observed.json")
        command = next(
            x
            for x in report["commands"]
            if x["argv"][1] == "inspect" and x["argv"][2] != "--format"
        )
        original = json.loads(command["stdout"])[0]
        self.assertTrue(verify_grant(original, Path("<synthetic-root>")))
        mutations = [
            lambda x: x["HostConfig"].update(NetworkMode="host"),
            lambda x: x["HostConfig"].update(ReadonlyRootfs=False),
            lambda x: x["HostConfig"].update(Privileged=True),
            lambda x: x["HostConfig"].update(PidsLimit=0),
            lambda x: x["HostConfig"].update(SecurityOpt=["seccomp=unconfined"]),
            lambda x: x["HostConfig"].update(PidMode="host"),
            lambda x: x["Config"].update(User="0"),
            lambda x: x["Config"]["Env"].append("SYNTHETIC_SECRET=not-real"),
            lambda x: x["Mounts"].append(
                {
                    "Type": "bind",
                    "Source": "/synthetic/home",
                    "Destination": "/home",
                    "RW": True,
                }
            ),
            lambda x: x["Mounts"][0].update(RW=True),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                changed = copy.deepcopy(original)
                mutate(changed)
                self.assertFalse(verify_grant(changed, Path("<synthetic-root>")))

    def test_parent_snapshot_detects_byte_mode_link_and_new_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            file = root / "original"
            file.write_text("synthetic-dirty")
            before = snapshot(root)
            file.write_text("tampered")
            self.assertNotEqual(snapshot(root), before)
            file.write_text("synthetic-dirty")
            self.assertEqual(snapshot(root), before)
            file.chmod(0o600)
            self.assertNotEqual(snapshot(root), before)
            file.chmod(0o644)
            os.link(file, root / "new-hardlink")
            self.assertNotEqual(snapshot(root), before)
            (root / "new-hardlink").unlink()
            (root / "new-file").write_text("new")
            self.assertNotEqual(snapshot(root), before)

    def test_manifest_drift_refuses_before_worker_creation(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / "report.json"
            process = subprocess.run(
                [
                    sys.executable,
                    str(self.root / "scripts/probe_linux_profile.py"),
                    "--docker-host",
                    "unix:///synthetic/does-not-exist",
                    "--manifest",
                    str(self.root / "docs/qualification/phase-2c-substrate-v4.json"),
                    "--manifest-sha256",
                    "0" * 64,
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("prospectively frozen manifest digest mismatch", process.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
