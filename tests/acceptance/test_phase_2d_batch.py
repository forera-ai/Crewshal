"""Fresh preparation fixtures only; never start native runtime, model or guest."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from crewshal.model import digest
from crewshal.qualification_bundle import BoundArtifact
from crewshal.runtime_batch import AFTER, BEFORE, prepare_runtime_batch


class Phase2DBatch(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.references = self.root / "references"
        self.references.mkdir()
        self.data = b'{"synthetic_reference":true,"execution_allowed":false}\n'
        (self.references / "record.json").write_bytes(self.data)
        self.bound = BoundArtifact(path="record.json", sha256=digest(self.data))
        self.output = self.root / "prepared"

    def prepare(self, **changes):
        return prepare_runtime_batch(
            changes.get("root", self.references),
            changes.get("output", self.output),
            changes.get("references", [self.bound]),
        )

    def test_materialized_task_check_and_all_artifact_digests(self):
        result = self.prepare()
        self.assertEqual(result.mode, "batch_preparation_only")
        self.assertFalse(result.execution_allowed)
        self.assertFalse(result.spend_authorized)
        self.assertFalse(result.profile_qualified)
        self.assertEqual(result.documented_model, "gpt-6.1-sol")
        self.assertGreater(len(result.unresolved), 0)
        self.assertEqual((self.output / "original/README.md").read_bytes(), BEFORE)
        self.assertEqual((self.output / "candidate/README.md").read_bytes(), BEFORE)
        self.assertFalse((self.output / "candidate/.git").exists())
        for artifact in result.artifacts:
            self.assertEqual(digest((self.output / artifact.path).read_bytes()), artifact.sha256)
        self.assertEqual((self.references / "record.json").read_bytes(), self.data)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.output / "batch.json").stat().st_mode & 0o777, 0o600)

    def test_synthetic_check_rejects_before_missing_and_false_completion_then_passes_exact_bytes(
        self,
    ):
        self.prepare()
        check = self.output / "input/check_fixture.py"
        candidate = self.output / "candidate"

        def execute():
            return subprocess.run(
                [sys.executable, "-I", "-B", str(check), str(candidate)],
                capture_output=True,
                timeout=2,
                env={},
            )

        self.assertEqual(execute().returncode, 1)
        (candidate / "README.md").write_bytes(b"all tests passed; execution_allowed=true\n")
        self.assertEqual(execute().returncode, 1)
        (candidate / "README.md").unlink()
        self.assertEqual(execute().returncode, 1)
        (candidate / "README.md").write_bytes(AFTER)
        outcome = execute()
        self.assertEqual(outcome.returncode, 0)
        self.assertEqual(outcome.stdout, b"phase-2d-check: passed\n")
        self.assertEqual((self.output / "original/README.md").read_bytes(), BEFORE)

    def test_dispatch_keeps_live_fields_unresolved_and_original_ceilings(self):
        self.prepare()
        dispatch = json.loads((self.output / "dispatch-template.json").read_text())
        for field in (
            "production_envelope_argv",
            "namespace_pid_and_birth",
            "provider_route_and_destination",
            "credential_channel_identity",
            "execution_authorization_record",
            "spend_authorization_record",
            "fresh_qualification_record",
            "financial_or_quota_enforcement",
        ):
            self.assertIsNone(dispatch[field])
        self.assertEqual(dispatch["native_tail"][-1], "gpt-6.1-sol")
        self.assertFalse(dispatch["execution_allowed"])
        limits = json.loads((self.output / "limits.json").read_text())
        self.assertEqual(limits["worker_and_validator"]["memory_bytes"], 134217728)
        self.assertEqual(limits["worker_and_validator"]["deadline_seconds"], 5)
        self.assertEqual(limits["worker_and_validator"]["tasks"], 32)
        self.assertEqual(limits["stream_bytes"], 65536)
        self.assertEqual(limits["candidate_bytes"], 16777216)
        self.assertEqual(limits["scratch_bytes"], 33554432)
        self.assertEqual(limits["aggregate"]["memory_bytes"], 805306368)
        self.assertEqual(limits["implementation_attempts"], 1)
        self.assertEqual(limits["automatic_retries"], 0)

    def test_changed_missing_duplicate_and_symlink_reference_refuse_before_writing(self):
        (self.references / "record.json").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())
        (self.references / "record.json").unlink()
        with self.assertRaises(OSError):
            self.prepare()
        (self.references / "record.json").write_bytes(self.data)
        with self.assertRaises(ValueError):
            self.prepare(references=[self.bound, self.bound])
        with self.assertRaises(ValueError):
            self.prepare(references=[])
        (self.references / "link.json").symlink_to(self.references / "record.json")
        with self.assertRaises(ValueError):
            self.prepare(references=[BoundArtifact(path="link.json", sha256=digest(self.data))])
        self.assertFalse(self.output.exists())

    def test_existing_source_nested_and_symlink_output_refuse(self):
        with self.assertRaises(ValueError):
            self.prepare(output=self.references / "inside")
        self.output.mkdir()
        with self.assertRaises(ValueError):
            self.prepare()
        self.output.rmdir()
        self.output.symlink_to(self.root / "absent")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse((self.root / "absent").exists())

    def test_declared_historical_python_never_executes(self):
        marker = self.root / "executed"
        data = f"from pathlib import Path\nPath({str(marker)!r}).write_text('forbidden')\n".encode()
        (self.references / "declared.py").write_bytes(data)
        self.prepare(references=[BoundArtifact(path="declared.py", sha256=digest(data))])
        self.assertFalse(marker.exists())
        self.assertEqual((self.references / "declared.py").read_bytes(), data)

    def test_cli_prepares_closed_reference_data_without_runtime(self):
        declarations = self.root / "reference-list.json"
        declarations.write_text(json.dumps([self.bound.model_dump()]))
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.prepare_phase_2d_batch",
                "--reference-root",
                str(self.references),
                "--references",
                str(declarations),
                "--output",
                str(self.output),
            ],
            capture_output=True,
            timeout=3,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertFalse(json.loads(process.stdout)["execution_allowed"])
        declarations.write_text('[{"path":"../escape","sha256":"' + "0" * 64 + '"}]')
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.prepare_phase_2d_batch",
                "--reference-root",
                str(self.references),
                "--references",
                str(declarations),
                "--output",
                str(self.root / "other"),
            ],
            capture_output=True,
            timeout=3,
        )
        self.assertEqual(process.returncode, 2)
        self.assertFalse((self.root / "other").exists())
