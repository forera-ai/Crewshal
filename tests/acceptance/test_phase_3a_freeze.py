"""Verify frozen public artifacts and fresh deterministic refusal cases."""

from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    CheckDefinition,
    Evidence,
    Run,
    Task,
    record_digest,
)
from crewshal.discovery import discover
from crewshal.gates import evaluate


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "phase3a_freeze", ROOT / "scripts/check_phase_3a_freeze.py"
)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
PACKAGE = checker.PACKAGE


class Phase3AFreeze(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "copy"
        index = json.loads((ROOT / PACKAGE / "package-index.json").read_text())
        for name in [row["path"] for row in index["files"]] + [f"{PACKAGE}/package-index.json"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def load(self, name):
        return json.loads((self.root / PACKAGE / name).read_text())

    def save(self, name, value):
        (self.root / PACKAGE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    def reindex(self):
        # Repair dependent references so each negative case reaches its semantic gate.
        for _ in range(5):
            changed = False
            for name in sorted(checker.NAMES - {"README.md"}):
                document = self.load(name)
                pending = [document]
                modified = False
                while pending:
                    item = pending.pop()
                    if isinstance(item, dict):
                        path = item.get("path")
                        if (
                            isinstance(path, str)
                            and path.startswith(PACKAGE + "/")
                            and "sha256" in item
                        ):
                            observed = checker.digest((self.root / path).read_bytes())
                            if item["sha256"] != observed:
                                item["sha256"] = observed
                                modified = True
                        pending.extend(item.values())
                    elif isinstance(item, list):
                        pending.extend(item)
                if modified:
                    self.save(name, document)
                    changed = True
            if not changed:
                break
        else:
            self.fail("Fixture reference graph did not converge.")
        index = self.load("package-index.json")
        for row in index["files"]:
            content = (self.root / row["path"]).read_bytes()
            row.update(bytes=len(content), sha256=checker.digest(content))
        index["content_sha256"] = checker.digest(checker.canonical(index["files"]))
        self.save("package-index.json", index)

    def refused(self, expression):
        with self.assertRaisesRegex((ValueError, OSError), expression):
            checker.verify(self.root)

    def test_final_package_is_consistent_without_execution_authority(self):
        result = checker.verify(self.root)
        self.assertEqual(result["planned_units"], 768)
        self.assertIs(result["execution_allowed"], False)
        self.assertIs(result["phase_3b_execution_allowed"], False)

    def test_changed_artifact_refuses_before_semantic_use(self):
        with (self.root / PACKAGE / "protocol.json").open("ab") as stream:
            stream.write(b" ")
        self.refused("artifact byte mismatch")

    def test_unindexed_package_artifact_is_rejected(self):
        (self.root / PACKAGE / "unindexed.txt").write_text("Synthetic unindexed content.\n")
        self.refused("unindexed package artifact")

    def test_duplicate_json_keys_are_rejected(self):
        for content in (
            b'{"schema_version":1,"schema_version":1}',
            b'{"schema_version":1,"nested":{"a":1,"a":2}}',
        ):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "duplicate"):
                checker.parse(content)

    def test_nonfinite_numbers_are_rejected_including_overflow(self):
        for number in ("NaN", "Infinity", "-Infinity", "1e9999"):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, "nonfinite"):
                checker.parse('{"schema_version":1,"value":' + number + "}")

    def test_boolean_and_unknown_schema_versions_are_rejected(self):
        for version in (True, 2, 1.0):
            with (
                self.subTest(version=version),
                self.assertRaisesRegex(ValueError, "schema version"),
            ):
                checker.parse(json.dumps({"schema_version": version}))

    def test_paths_cannot_escape_or_alias(self):
        for path in ("../outside", "/outside", "a/../b", "a//b", "a/./b", "a\\b", ""):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "path"):
                checker.read(self.root, path)

    def test_symlink_artifacts_are_not_read(self):
        path = self.root / PACKAGE / "protocol.json"
        content = path.read_bytes()
        other = self.root.parent / "outside.json"
        other.write_bytes(content)
        path.unlink()
        path.symlink_to(other)
        self.refused("Too many levels|symbolic link")

    def test_directory_symlinks_are_not_followed(self):
        (self.root / "alias").symlink_to(self.root / PACKAGE, target_is_directory=True)
        with self.assertRaises(OSError):
            checker.read(self.root, "alias/protocol.json")

    def test_fifo_artifact_is_refused_without_waiting_for_a_writer(self):
        path = self.root / PACKAGE / "protocol.json"
        path.unlink()
        os.mkfifo(path)
        self.refused("regular file")

    def test_rehashed_role_labels_cannot_hide_one_implementation_runtime(self):
        data = self.load("runtime-selections.json")
        data["role_assignments"][1]["implementation"] = "A"
        self.save("runtime-selections.json", data)
        self.reindex()
        self.refused("role assignment mismatch")

    def test_rehashed_design_shape_must_match_the_planned_schedule(self):
        data = self.load("protocol.json")
        data["design"]["sealed_shape"] = [1, 1, 1, 1, 1]
        self.save("protocol.json", data)
        self.reindex()
        self.refused("sealed shape mismatch")

    def test_rehashed_spending_authority_is_rejected(self):
        data = self.load("owner-decisions.json")
        data["approved_budget"]["subscription_quota_allowance"] = 1
        self.save("owner-decisions.json", data)
        self.reindex()
        self.refused("zero budget")

    def test_rehashed_owner_answer_change_is_rejected(self):
        data = self.load("owner-decisions.json")
        data["approvals"][0]["answer"] = "Implied approval."
        data["approval_text_sha256"] = checker.digest(checker.canonical(data["approvals"]))
        self.save("owner-decisions.json", data)
        self.reindex()
        self.refused("owner answer mismatch")

    def test_rehashed_execution_permission_is_rejected(self):
        data = self.load("execution-admission.json")
        data["phase_3b_execution_allowed"] = True
        self.save("execution-admission.json", data)
        self.reindex()
        self.refused("admission must remain closed")

    def test_rehashed_missing_sealed_commitment_is_rejected(self):
        data = self.load("sealed-commitments.json")
        data["tasks"][0]["requirement_sha256"] = ""
        self.save("sealed-commitments.json", data)
        self.reindex()
        self.refused("sealed commitment missing")

    def test_rehashed_sealed_content_is_rejected(self):
        data = self.load("sealed-commitments.json")
        data["tasks"][0]["requirement"] = "Synthetic disclosure."
        self.save("sealed-commitments.json", data)
        self.reindex()
        self.refused("sealed task content exposed")

    def test_rehashed_missing_duplicate_or_wrong_role_schedule_is_rejected(self):
        original = self.load("schedule.json")
        for mutation in ("missing", "duplicate", "role"):
            data = json.loads(json.dumps(original))
            if mutation == "missing":
                data["rows"].pop()
            elif mutation == "duplicate":
                data["rows"][-1] = data["rows"][0]
            else:
                data["rows"][0]["role_assignment"] = "A-only"
            self.save("schedule.json", data)
            self.reindex()
            with self.subTest(mutation=mutation):
                self.refused("schedule mismatch")

    def test_rehashed_annotation_exposure_is_rejected(self):
        data = self.load("annotation-b.json")
        data["independence"]["annotation_a_accessed"] = True
        self.save("annotation-b.json", data)
        self.reindex()
        self.refused("independence lost")

    def test_rehashed_fabricated_native_identity_is_rejected(self):
        data = self.load("runtime-selections.json")
        data["runtimes"][0]["actual_executable_sha256"] = "0" * 64
        self.save("runtime-selections.json", data)
        self.reindex()
        self.refused("future identity fabricated")

    def test_rehashed_incomplete_task_oracle_is_rejected(self):
        data = self.load("development-tasks.json")
        data["tasks"][0]["acceptance"][0]["expected"] = ""
        self.save("development-tasks.json", data)
        self.reindex()
        self.refused("task oracle incomplete")

    def test_fresh_no_harness_fixture_preserves_unknown_check(self):
        fixture = self.load("supplemental-fixtures.json")["fixtures"][1]
        source = self.root.parent / "no-harness"
        source.mkdir()
        for name, content in fixture["files"].items():
            (source / name).write_text(content)
        model = discover(source)
        checks = [fact for fact in model.facts if fact.kind == "check"]
        self.assertTrue(checks)
        self.assertTrue(all(fact.value is None for fact in checks))
        self.assertTrue(all(fact.decision == "pending" for fact in checks))

    def test_fresh_red_fixture_cannot_be_erased_by_unrelated_success(self):
        fixture = self.load("supplemental-fixtures.json")["fixtures"][0]
        source = self.root.parent / "known-red"
        source.mkdir()
        for name, content in fixture["files"].items():
            (source / name).write_text(content)
        command = [
            sys.executable,
            "-I",
            "-m",
            "unittest",
            "discover",
            "-s",
            ".",
            "-p",
            "test_red.py",
        ]
        result = subprocess.run(
            command, cwd=source, env={"HOME": str(source)}, capture_output=True, timeout=10
        )
        self.assertEqual(result.returncode, fixture["expected_exit_code"])
        self.assertIn(fixture["required_diagnostic"].encode(), result.stderr)
        empty = checker.digest(b"")
        check = CheckDefinition(
            id="baseline-red", argv=command, cwd=".", environment=empty, toolchain=empty
        )
        task = Task(
            id="red-task",
            requirement="Preserve red evidence.",
            checks=[check],
            review_required=False,
            independent_provider=False,
        )
        binding = Binding(
            model=empty, task=record_digest(task), policy=empty, scope=empty, candidate=empty
        )
        run = Run(id="fixture-run", task_id=task.id, binding=binding, state="frozen")
        attempt = Attempt(
            id="fixture-attempt",
            run_id=run.id,
            binding=binding,
            role="implementation",
            state="completed",
            process_exit=0,
            runtime_result="completed",
        )
        now = datetime(2026, 10, 18, tzinfo=timezone.utc)
        red = Evidence(
            id="red",
            run_id=run.id,
            attempt_id=attempt.id,
            binding=binding,
            kind="check",
            gate="check:baseline-red",
            status="failed",
            definition=check,
            started=now,
            ended=now,
            exit_code=result.returncode,
            stdout=checker.digest(result.stdout),
            stderr=checker.digest(result.stderr),
        )
        scope = Evidence(
            id="scope",
            run_id=run.id,
            attempt_id=attempt.id,
            binding=binding,
            kind="scope",
            gate="scope",
            status="passed",
            started=now,
            ended=now,
            stdout=empty,
            stderr=empty,
        )
        unrelated = red.model_copy(
            update={
                "id": "unrelated",
                "gate": "check:unrelated",
                "status": "passed",
                "exit_code": 0,
            }
        )
        approval = Approval(
            id="fixture-approval",
            run_id=run.id,
            binding=binding,
            owner="fixture-owner",
            reason="Synthetic fixture only.",
        )
        verdict = evaluate(run, task, binding, [approval], [attempt], [red, scope, unrelated], [])
        self.assertEqual(verdict.status, "failed")
        self.assertEqual(verdict.gates["check:baseline-red"], "failed")
        self.assertIn(red.id, verdict.evidence_ids)
        self.assertIs(verdict.execution_allowed, False)


if __name__ == "__main__":
    unittest.main()
