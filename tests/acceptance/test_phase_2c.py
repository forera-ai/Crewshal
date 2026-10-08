"""Offline refusal fixtures, independently of live substrate qualification."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from pydantic import ValidationError

from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
    assess_qualification,
)


class Phase2C(unittest.TestCase):
    def setUp(self) -> None:
        self.identity = QualificationIdentity(
            host_os="synthetic-linux",
            host_kernel="synthetic-kernel",
            architecture="synthetic-architecture",
            substrate="synthetic-container",
            substrate_version="synthetic-version",
            image="1" * 64,
            runtime="synthetic",
            toolchain="2" * 64,
            configuration="3" * 64,
            grant="4" * 64,
            harness="5" * 64,
            manifest="6" * 64,
            credential_design="7" * 64,
        )
        self.results = [
            ProbeResult(case=case, status="passed", observation="synthetic fixture only")
            for case in MANDATORY_CASES
        ]

    def record(self, **changes: object) -> Qualification:
        return Qualification.model_validate(
            {
                "id": "synthetic",
                "identity": self.identity.model_dump(),
                "results": [item.model_dump() for item in self.results],
                **changes,
            }
        )

    def test_missing_qualification_denies(self) -> None:
        result = assess_qualification(None, self.identity)
        self.assertEqual(result.status, "denied")
        self.assertFalse(result.execution_allowed)

    def test_each_mandatory_failure_or_unavailable_denies(self) -> None:
        for case in MANDATORY_CASES:
            for status in ("failed", "unavailable"):
                with self.subTest(case=case, status=status):
                    results = [
                        {**item.model_dump(), "status": status if item.case == case else "passed"}
                        for item in self.results
                    ]
                    result = assess_qualification(self.record(results=results), self.identity)
                    self.assertEqual(result.status, "denied")
                    self.assertFalse(result.execution_allowed)

    def test_each_relevant_identity_change_invalidates(self) -> None:
        for field in QualificationIdentity.model_fields:
            with self.subTest(field=field):
                value = getattr(self.identity, field)
                changed = "8" * 64 if isinstance(value, str) and len(value) == 64 else "changed"
                current = QualificationIdentity.model_validate(
                    {
                        **self.identity.model_dump(),
                        field: changed,
                    }
                )
                result = assess_qualification(self.record(), current)
                self.assertEqual(result.status, "denied")
                self.assertFalse(result.execution_allowed)

    def test_missing_duplicate_extra_case_denies(self) -> None:
        cases = [
            self.results[:-1],
            self.results + [self.results[0]],
            self.results + [ProbeResult(case="unknown", status="passed", observation="fixture")],
        ]
        for results in cases:
            with self.subTest(results=len(results)):
                result = assess_qualification(
                    self.record(results=[item.model_dump() for item in results]),
                    self.identity,
                )
                self.assertEqual(result.status, "denied")

    def test_unresolved_profile_and_credential_design_deny(self) -> None:
        for field in ("substrate_version", "image", "runtime", "credential_design"):
            with self.subTest(field=field):
                identity = QualificationIdentity.model_validate(
                    {
                        **self.identity.model_dump(),
                        field: None,
                    }
                )
                record = self.record(identity=identity.model_dump())
                self.assertEqual(assess_qualification(record, identity).status, "denied")

    def test_success_is_only_later_authorization_eligibility(self) -> None:
        result = assess_qualification(self.record(), self.identity)
        self.assertEqual(result.status, "qualified_for_later_authorization")
        self.assertFalse(result.execution_allowed)

    def test_forged_execution_and_malformed_records_refused(self) -> None:
        for changes in (
            {"execution_allowed": True},
            {"schema_version": True},
            {"schema_version": 2},
            {"unexpected": "grant"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.record(**changes)
        record = self.record().model_copy(update={"execution_allowed": True})
        with self.assertRaises(ValidationError):
            assess_qualification(record, self.identity)

    def test_frozen_manifest_exact_case_set_and_criteria(self) -> None:
        path = Path(__file__).resolve().parents[2] / "docs/qualification/phase-2c-v1.json"
        manifest = json.loads(path.read_text())
        self.assertEqual(
            [case["id"] for case in manifest["mandatory_cases"]], list(MANDATORY_CASES)
        )
        self.assertTrue(all(case["criterion"] for case in manifest["mandatory_cases"]))
        self.assertEqual(manifest["grant"]["network"], [])
        self.assertEqual(manifest["grant"]["credentials"], [])

    def test_frozen_manifest_digest(self) -> None:
        path = Path(__file__).resolve().parents[2] / "docs/qualification/phase-2c-v1.json"
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563",
        )

    def test_preflight_refuses_amended_manifest_before_side_effect(self) -> None:
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "changed.json"
            manifest.write_text('{"mandatory_cases": []}')
            output = Path(directory) / "report.json"
            process = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts/qualify_phase_2c.py"),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("frozen manifest digest mismatch", process.stderr)
            self.assertFalse(output.exists())

    def test_preflight_command_failures_and_output_limits(self) -> None:
        from scripts.qualify_phase_2c import capture

        missing = capture(["/nonexistent/crewshal-synthetic"], {})
        self.assertEqual(missing["status"], "unavailable")
        failed = capture([sys.executable, "-I", "-c", "raise SystemExit(17)"], {})
        self.assertEqual(failed["exit"], 17)
        oversized = capture([sys.executable, "-I", "-c", "print('x' * 65537)"], {})
        self.assertEqual(oversized["status"], "unavailable")
        self.assertEqual(oversized["error"], "output limit exceeded")


if __name__ == "__main__":
    unittest.main()
