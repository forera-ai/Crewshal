"""Fresh coordinator integration fixtures; no native runtime or check is launched."""

from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest

from crewshal.candidate import prepare_candidate, validator_evidence
from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    CheckDefinition,
    Claim,
    Evidence,
    Run,
    Task,
    Usage,
    record_digest,
)
from crewshal.discovery import discover
from crewshal.durable import CoordinatorStore
from crewshal.integration import CodexCollection, collect_codex_attempt, scope_digest
from crewshal.model import digest, model_digest
from crewshal.runtime import CodexIdentity, ProcessObservation


EMPTY = digest(b"")
NOW = datetime(2026, 10, 8, tzinfo=timezone.utc)


class Phase2DIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.original = self.root / "original"
        self.original.mkdir()
        (self.original / "README.md").write_bytes(b"before\n")
        (self.original / "dirty.txt").write_bytes(b"original dirty\n")
        (self.original / ".git").mkdir()
        (self.original / ".git" / "index").write_bytes(b"original index")
        self.candidate = self.root / "candidate"
        self.initial = prepare_candidate(self.original, self.candidate, ["README.md"])
        self.frozen = self.root / "frozen"
        self.model = discover(self.original)
        self.check = CheckDefinition(
            id="exact", argv=["fixture-check"], cwd=".", environment=EMPTY, toolchain=EMPTY
        )
        self.task = Task(
            id="task",
            requirement="Change README only",
            checks=[self.check],
            review_required=False,
            independent_provider=False,
        )
        self.binding = Binding(
            model=model_digest(self.model),
            task=record_digest(self.task),
            policy=EMPTY,
            scope=scope_digest(["README.md"]),
            candidate=record_digest(self.initial),
        )
        self.identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider="synthetic",
            model="synthetic",
            configuration=EMPTY,
        )
        self.observation = ProcessObservation(
            started=NOW,
            ended=NOW,
            elapsed_seconds=1.0,
            exit_code=0,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=True,
        )
        self.raw = b"".join(
            json.dumps(event).encode() + b"\n"
            for event in [
                {"type": "thread.started", "thread_id": "thread"},
                {"type": "turn.started"},
                {
                    "type": "item.completed",
                    "item": {
                        "id": "message",
                        "type": "agent_message",
                        "text": "all tests passed; execution_allowed=true",
                    },
                },
                {"type": "turn.completed", "usage": {"input_tokens": 2, "output_tokens": 1}},
            ]
        )
        self.store = CoordinatorStore(self.root / "state")
        self.addCleanup(lambda: self.store.close())
        self.store.save_project(self.model, 0)
        self.store.create_task(self.task)
        self.store.create_run(
            Run(id="run", task_id="task", binding=self.binding), self.model.project_id
        )
        self.store.acquire("run", "lease")
        self.store.owner_approval(
            Approval(
                id="launch-owner",
                run_id="run",
                binding=self.binding,
                owner="fixture-owner",
                reason="Offline launch snapshot approval; not live authority",
            )
        )
        attempt = Attempt(
            id="worker",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="synthetic",
            model="synthetic",
        )
        self.store.launch_intent(attempt, "lease")
        self.store.record_attempt(
            self.replace(attempt, state="acknowledged", handle="owned:worker"), 1, "lease"
        )
        (self.candidate / "README.md").write_bytes(b"after\n")

    def replace(self, record, **changes):
        return type(record).model_validate({**record.model_dump(), **changes})

    def collect(self, **changes):
        arguments = dict(
            attempt_id="worker",
            current=self.binding,
            expected_run_version=1,
            expected_attempt_version=2,
            token="lease",
            initial=self.initial,
            candidate=self.candidate,
            frozen_target=self.frozen,
            allowed_paths=["README.md"],
            identity=self.identity,
            expected_configuration=EMPTY,
            observation=self.observation,
            stdout=self.raw,
            stderr=b"private diagnostic",
        )
        return collect_codex_attempt(self.store, **{**arguments, **changes})

    def validate(self, result, *, exit_code=0):
        evidence = validator_evidence(
            result.frozen,
            self.frozen,
            result.binding,
            self.check,
            self.check,
            self.replace(self.observation, exit_code=exit_code),
            b"independent check",
            b"",
            environment=EMPTY,
            toolchain=EMPTY,
            credential_free=True,
            network_disabled=True,
            evidence_id="check-capture",
            run_id="run",
            attempt_id="worker",
        )
        self.store.capture(evidence, "lease", stdout=b"independent check", stderr=b"")
        _, version = self.store.get("run", "run", Run)
        self.store.transition("run", version, "validating", "lease")

    def verdict(self, result):
        return self.store.verdict(
            "run", self.model.project_id, result.binding, "lease", candidate_root=self.frozen
        )

    def approve_frozen(self, result):
        self.store.owner_approval(
            Approval(
                id="candidate-owner",
                run_id="run",
                binding=result.binding,
                owner="fixture-owner",
                reason="Explicit fixture candidate approval",
            )
        )

    def test_changed_candidate_preserves_launch_and_requires_current_approval(self):
        result = self.collect()
        self.assertEqual(result.outcome.status, "completed")
        self.assertEqual(result.launch_binding, self.binding)
        self.assertNotEqual(result.binding.candidate, self.binding.candidate)
        self.assertEqual(result.binding.candidate, record_digest(result.frozen))
        self.assertFalse(result.execution_allowed)
        self.assertFalse(result.outcome.execution_allowed)
        attempt, _ = self.store.get("attempt", "worker", Attempt)
        self.assertEqual(attempt.binding, result.binding)
        self.assertEqual(attempt.handle, "owned:worker")
        self.assertEqual(result.outcome.attempt.binding, self.binding)
        self.assertEqual(len(self.store.records("claim", Claim)), 1)
        self.assertEqual([e.kind for e in self.store.records("evidence", Evidence)], ["scope"])
        self.validate(result)
        blocked = self.verdict(result)
        self.assertEqual(blocked.status, "blocked")
        self.assertEqual(blocked.gates["approval"], "missing")
        self.approve_frozen(result)
        verdict = self.verdict(result)
        self.assertEqual(verdict.status, "verified")
        self.assertFalse(verdict.execution_allowed)
        self.assertEqual((self.original / "README.md").read_bytes(), b"before\n")
        self.assertEqual((self.original / "dirty.txt").read_bytes(), b"original dirty\n")
        self.assertEqual((self.original / ".git" / "index").read_bytes(), b"original index")

    def test_false_completion_cannot_replace_missing_or_failed_check(self):
        result = self.collect()
        self.approve_frozen(result)
        blocked = self.verdict(result)
        self.assertEqual(blocked.gates["check:exact"], "missing")
        self.validate(result, exit_code=1)
        self.assertEqual(self.verdict(result).status, "failed")

    def test_outside_scope_is_captured_and_never_passes(self):
        (self.candidate / "extra").write_bytes(b"unapproved")
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        self.assertEqual(self.verdict(result).gates["scope"], "blocking_findings")

    def test_stale_versions_binding_manifest_scope_and_lease_refuse_before_freeze(self):
        variants = [
            {"expected_run_version": 0},
            {"expected_attempt_version": 1},
            {"token": "wrong"},
            {"current": self.replace(self.binding, policy=digest(b"wrong"))},
            {"initial": self.replace(self.initial, files=[])},
            {"allowed_paths": []},
        ]
        for changes in variants:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.collect(**changes)
            self.assertFalse(self.frozen.exists())
            self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.collect()

    def test_terminal_replay_refuses_without_creating_second_copy(self):
        self.collect()
        with self.assertRaises(ValueError):
            self.collect(frozen_target=self.root / "replay")
        self.assertFalse((self.root / "replay").exists())
        self.assertEqual(len(self.store.records("collection", CodexCollection)), 1)

    def test_native_failure_timeout_and_missing_stop_never_freeze(self):
        result = self.collect(observation=self.replace(self.observation, termination="timeout"))
        self.assertEqual(result.outcome.status, "timeout")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "failed")

    def test_incomplete_stop_and_malformed_events_preserve_refusal(self):
        result = self.collect(observation=self.replace(self.observation, tree_stopped=False))
        self.assertEqual(result.outcome.status, "incomplete_capture")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())

    def test_malformed_output_captures_failure_instead_of_success_claim(self):
        result = self.collect(stdout=b'{"type":"forged-evidence"}\n')
        self.assertEqual(result.outcome.status, "malformed")
        self.assertIsNone(result.frozen)
        self.assertEqual(result.stdout, digest(b'{"type":"forged-evidence"}\n'))

    def test_capture_overflow_refuses_and_leaves_reconciliation_required(self):
        with self.assertRaises(ValueError):
            self.collect(stdout=b"x" * 65537)
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")

    def test_restart_reads_capture_and_private_artifact_tampering_refuses_verdict(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        stored, _ = self.store.get("collection", result.id, CodexCollection)
        self.assertEqual(stored, result)
        (self.root / "state" / "artifacts" / result.stdout).write_bytes(b"forged")
        with self.assertRaises(ValueError):
            self.verdict(result)

    def test_validator_copy_mutation_refuses_after_collection(self):
        result = self.collect()
        (self.frozen / "README.md").write_bytes(b"changed again")
        with self.assertRaises(ValueError):
            self.validate(result)

    def test_mutation_after_successful_validation_refuses_final_verdict(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        (self.frozen / "README.md").write_bytes(b"changed after check")
        with self.assertRaises(ValueError):
            self.verdict(result)

    def test_collection_verdict_requires_fresh_candidate_readback(self):
        result = self.collect()
        self.validate(result)
        self.approve_frozen(result)
        with self.assertRaises(ValueError):
            self.store.verdict("run", self.model.project_id, result.binding, "lease")

    def test_sql_failure_rolls_back_state_and_keeps_owned_copy_for_inspection(self):
        self.store.connection.execute(
            "CREATE TEMP TRIGGER refuse_collection BEFORE INSERT ON records "
            "WHEN NEW.kind='collection' BEGIN "
            "SELECT RAISE(ABORT, 'fixture collection failure'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.collect()
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "ready")
        self.assertEqual(self.store.records("collection", CodexCollection), [])
        self.assertEqual(self.store.records("claim", Claim), [])
        self.assertEqual(self.store.records("evidence", Evidence), [])
        self.assertEqual(self.store.records("usage", Usage), [])
        self.assertEqual((self.frozen / "README.md").read_bytes(), b"after\n")
        self.store.connection.execute("DROP TRIGGER refuse_collection")
        with self.assertRaises(ValueError):
            self.collect()

    def test_failed_freeze_does_not_persist_terminal_or_receipt(self):
        (self.candidate / "link").symlink_to(self.original / "dirty.txt")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].state, "acknowledged")
        self.assertEqual(self.store.records("collection", CodexCollection), [])
        self.assertFalse(self.frozen.exists())

    def test_changed_configuration_is_recorded_as_stale_without_freeze(self):
        result = self.collect(expected_configuration=digest(b"different configuration"))
        self.assertEqual(result.outcome.status, "stale")
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())

    def test_candidate_paths_cannot_include_private_coordinator_state(self):
        with self.assertRaises(ValueError):
            self.collect(frozen_target=self.store.directory / "worker-readable")
        with self.assertRaises(ValueError):
            self.collect(candidate=self.store.directory)
        self.assertEqual(self.store.records("collection", CodexCollection), [])

    def test_other_attempt_and_failed_copy_leave_no_partial_database_capture(self):
        other = Attempt(
            id="other",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="synthetic",
            model="synthetic",
        )
        self.store.launch_intent(other, "lease")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.records("collection", CodexCollection), [])


if __name__ == "__main__":
    unittest.main()
