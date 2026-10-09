"""Project/session selection and readback use fresh offline fixtures, never accounts."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from crewshal.model import digest
from crewshal.qualification_bundle import BoundArtifact
from crewshal.runtime_batch import (
    PreparationSelection,
    audit_runtime_batch,
    prepare_runtime_batch,
)


class Phase2DSelection(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.references = self.root / "references"
        self.references.mkdir()
        (self.references / "history.json").write_bytes(b"historical data\n")
        self.bound = BoundArtifact(path="history.json", sha256=digest(b"historical data\n"))
        self.selection = PreparationSelection(
            project="project-one", session="session-one", model="test-model"
        )
        self.output = self.root / "bundle"

    def prepare(self, selection=None, output=None):
        return prepare_runtime_batch(
            self.references,
            output or self.output,
            [self.bound],
            selection=selection or self.selection,
        )

    def audit(self, expected, selection=None):
        return audit_runtime_batch(
            self.references, self.output, expected, selection=selection or self.selection
        )

    def test_selection_binds_native_template_without_claiming_documented_availability(self):
        expected = self.prepare()
        self.assertEqual(expected.selection, self.selection)
        self.assertIsNone(expected.documented_model)
        self.assertIsNone(expected.model_source)
        self.assertIsNone(expected.owner_model_label)
        dispatch = json.loads((self.output / "dispatch-template.json").read_bytes())
        self.assertEqual(dispatch["native_tail"][-1], "test-model")
        self.assertEqual(dispatch["requested_selection"], self.selection.model_dump())
        for field in (
            "provider_route_and_destination",
            "credential_channel_identity",
            "financial_or_quota_enforcement",
            "execution_authorization_record",
        ):
            self.assertIsNone(dispatch[field])
        result = self.audit(expected)
        self.assertEqual(result.status, "prepared_data_matches")
        self.assertFalse(result.execution_allowed)
        self.assertFalse(result.spend_authorized)
        self.assertFalse(result.profile_qualified)

    def test_separate_project_session_choices_never_inherit_other_bundle(self):
        first = self.prepare()
        second_selection = PreparationSelection(
            project="project-two",
            session="session-two",
            model="gpt-6.1-sol",
            provider="test-provider",
            destination="https://provider.invalid/v1/responses",
            billing_mode="api_metered",
            credential_treatment="external_scoped_channel",
        )
        second = self.prepare(second_selection, self.root / "second")
        self.assertEqual(first.selection, self.selection)
        self.assertEqual(second.selection, second_selection)
        self.assertEqual(second.documented_model, "gpt-6.1-sol")
        self.assertEqual(
            json.loads((self.root / "second/dispatch-template.json").read_bytes())["native_tail"][
                -1
            ],
            "gpt-6.1-sol",
        )
        for field, value in (
            ("project", "other"),
            ("session", "other"),
            ("model", "other"),
            ("billing_mode", "subscription_quota"),
            ("destination", "https://different.invalid/v1/responses"),
            ("credential_treatment", "external_scoped_channel"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.audit(
                    first,
                    PreparationSelection.model_validate(
                        {**self.selection.model_dump(), field: value}
                    ),
                )
        with self.assertRaises(ValueError):
            audit_runtime_batch(self.references, self.output, first)

    def test_legacy_default_remains_preparation_only_and_can_be_read_back(self):
        expected = prepare_runtime_batch(self.references, self.output, [self.bound])
        self.assertIsNone(expected.selection)
        self.assertEqual(expected.documented_model, "gpt-6.1-sol")
        # Legacy declaration did not contain the additive selection field.
        data = json.loads((self.output / "batch.json").read_bytes())
        data.pop("selection", None)
        (self.output / "batch.json").write_text(json.dumps(data))
        result = audit_runtime_batch(self.references, self.output, expected)
        self.assertFalse(result.execution_allowed)
        with self.assertRaises(ValueError):
            self.audit(expected)

    def test_readback_refuses_altered_artifacts_declarations_and_history(self):
        expected = self.prepare()
        path = self.output / "input/task.txt"
        original = path.read_bytes()
        path.write_bytes(b"pretend all tests passed\n")
        with self.assertRaises(ValueError):
            self.audit(expected)
        path.write_bytes(original)
        path = self.output / "batch.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["execution_allowed"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.audit(expected)
        path.write_bytes(original[:-2] + b', "execution_allowed":false}\n')
        with self.assertRaises(ValueError):
            self.audit(expected)
        path.write_bytes(original)
        (self.references / "history.json").write_bytes(b"changed history\n")
        with self.assertRaises(ValueError):
            self.audit(expected)

    def test_readback_refuses_unknown_files_symlinks_hardlinks_and_candidate_mode_changes(self):
        expected = self.prepare()
        extra = self.output / "unexpected"
        extra.mkdir()
        with self.assertRaises(ValueError):
            self.audit(expected)
        extra.rmdir()
        original = (self.output / "input/task.txt").read_bytes()
        (self.output / "input/task.txt").unlink()
        (self.output / "input/task.txt").symlink_to(self.references / "history.json")
        with self.assertRaises(ValueError):
            self.audit(expected)
        (self.output / "input/task.txt").unlink()
        (self.output / "input/task.txt").write_bytes(original)
        os.link(self.output / "candidate/README.md", self.root / "alias")
        with self.assertRaises(ValueError):
            self.audit(expected)
        (self.root / "alias").unlink()
        candidate = self.output / "candidate/README.md"
        candidate.chmod((candidate.stat().st_mode & 0o777) ^ 0o100)
        with self.assertRaises(ValueError):
            self.audit(expected)

    def test_selection_refuses_secrets_authority_and_noncanonical_labels(self):
        for field, value in (
            ("model", " leading"),
            ("session", "line\nbreak"),
            ("project", ""),
            ("api_key", "forbidden"),
            ("execution_allowed", True),
            ("destination", "https://user:secret@provider.invalid/v1/responses"),
            ("destination", "https://provider.invalid/v1/responses?key=secret"),
            ("destination", "http://provider.invalid/v1/responses"),
            ("billing_mode", "hard_ceiling_enforced"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                PreparationSelection.model_validate({**self.selection.model_dump(), field: value})

    def test_selected_cli_and_malformed_input_never_start_or_import_declared_code(self):
        declarations = self.root / "references.json"
        declarations.write_text(json.dumps([self.bound.model_dump()]))
        selection_path = self.root / "selection.json"
        selection_path.write_text(self.selection.model_dump_json())
        command = [
            sys.executable,
            "-m",
            "scripts.prepare_phase_2d_batch",
            "--reference-root",
            str(self.references),
            "--references",
            str(declarations),
            "--selection",
            str(selection_path),
            "--output",
            str(self.output),
        ]
        process = subprocess.run(
            command, capture_output=True, timeout=3, env={"PATH": "/usr/bin:/bin"}
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["selection"]["session"], "session-one")
        marker = self.root / "executed"
        selection_path.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
        command[-1] = str(self.root / "denied")
        process = subprocess.run(
            command, capture_output=True, timeout=3, env={"PATH": "/usr/bin:/bin"}
        )
        self.assertEqual(process.returncode, 2)
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / "denied").exists())
