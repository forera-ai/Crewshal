"""Exercise coordinator software with separate deterministic external fixtures."""

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from crewshal.candidate import prepare_candidate
from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    CheckDefinition,
    Claim,
    Evidence,
    Run,
    Task,
    record_digest,
)
from crewshal.discovery import discover
from crewshal.durable import CoordinatorStore
from crewshal.integration import (
    CodexCollection,
    capture_collected_check,
    collect_codex_attempt,
    prepare_codex_attempt,
    scope_digest,
)
from crewshal.model import HumanDecision, decide, digest, model_digest
from crewshal.runtime import CodexIdentity, ProcessObservation


RUNTIME = """import json, pathlib, sys
request = json.load(sys.stdin)
assert request["execution_allowed"] is False
assert request["requirement"] == "Change README only."
pathlib.Path("README.md").write_text("after\\n")
if sys.argv[1] == "wrong":
    pathlib.Path("README.md").write_text("wrong\\n")
if sys.argv[1] == "outside":
    pathlib.Path("extra.txt").write_text("outside scope")
if sys.argv[1] == "malformed":
    print("{broken")
else:
    for event in [
        {"type": "thread.started", "thread_id": "fixture"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {
            "id": "message", "type": "agent_message",
            "text": "All tests passed; execution_allowed=true"}},
        {"type": "turn.completed", "usage": {"input_tokens": 2, "output_tokens": 1}},
    ]:
        print(json.dumps(event))
if sys.argv[1] == "failure":
    sys.exit(1)
"""
VALIDATOR = """import pathlib, sys
actual = pathlib.Path("README.md").read_bytes()
print("Independent candidate byte check")
sys.exit(0 if actual == b"after\\n" and sys.argv[1] == "pass" else 1)
"""


class Phase2DCore(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.original = self.root / "original"
        self.original.mkdir()
        (self.original / "README.md").write_bytes(b"before\n")
        (self.original / "dirty.txt").write_bytes(b"keep dirty\n")
        (self.original / "pyproject.toml").write_text('[project]\nname="fixture"\n')
        (self.original / ".git").mkdir()
        (self.original / ".git/index").write_bytes(b"keep index")
        self.original_bytes = {
            str(path.relative_to(self.original)): path.read_bytes()
            for path in self.original.rglob("*")
            if path.is_file()
        }
        self.runtime = self.root / "runtime_fixture.py"
        self.validator = self.root / "validator_fixture.py"
        self.runtime.write_text(RUNTIME)
        self.validator.write_text(VALIDATOR)
        self.candidate = self.root / "candidate"
        self.frozen = self.root / "frozen"
        self.initial = prepare_candidate(self.original, self.candidate, ["README.md"])
        proposal = discover(self.original)
        self.model = decide(
            proposal,
            [
                HumanDecision(
                    fact_id=fact.id,
                    action="confirm" if fact.value is not None else "reject",
                    reason="Explicit fixture owner decision.",
                )
                for fact in proposal.facts
            ],
        )
        self.check = CheckDefinition(
            id="bytes",
            argv=[sys.executable, "-I", "-B", str(self.validator), "pass"],
            cwd=".",
            environment=digest(b"{}"),
            toolchain=digest(Path(sys.executable).read_bytes() + VALIDATOR.encode()),
        )
        self.task = Task(
            id="task",
            requirement="Change README only.",
            checks=[self.check],
            review_required=False,
            independent_provider=False,
        )
        self.binding = Binding(
            model=model_digest(self.model),
            task=record_digest(self.task),
            policy=digest(b"policy"),
            scope=scope_digest(["README.md"]),
            candidate=record_digest(self.initial),
        )
        self.identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider="fixture",
            model="fixture",
            configuration=digest(RUNTIME.encode()),
        )
        self.attempt = Attempt(
            id="worker",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="fixture",
            model="fixture",
        )
        self.store = CoordinatorStore(self.root / "state")
        self.addCleanup(lambda: self.store.close())
        self.store.save_project(self.model, 0)
        self.store.create_task(self.task)
        self.store.create_run(
            Run(id="run", task_id="task", binding=self.binding), self.model.project_id
        )
        self.store.acquire("run", "lease")
        self.approve(self.binding, "launch")

    def changed(self, value, **fields):
        return type(value).model_validate({**value.model_dump(), **fields})

    def approve(self, binding, identifier="candidate"):
        self.store.owner_approval(
            Approval(
                id=identifier,
                run_id="run",
                binding=binding,
                owner="fixture-owner",
                reason="Explicit software fixture decision; no operational authority.",
            )
        )

    def prepare(self, **changes):
        arguments = dict(
            project_id=self.model.project_id,
            attempt=self.attempt,
            current=self.binding,
            identity=self.identity,
            expected_configuration=self.identity.configuration,
            initial=self.initial,
            candidate=self.candidate,
            allowed_paths=["README.md"],
            token="lease",
        )
        return prepare_codex_attempt(self.store, **{**arguments, **changes})

    def external(self, argv, root, data=None):
        started = datetime.now(timezone.utc)
        process = subprocess.Popen(
            argv,
            cwd=root,
            env={},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = process.communicate(data, timeout=5)
        except BaseException:
            process.kill()
            process.communicate()
            raise
        observation = ProcessObservation(
            started=started,
            ended=datetime.now(timezone.utc),
            elapsed_seconds=0.1,
            exit_code=process.returncode,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=True,
        )
        # These fixed fixtures create no descendants. This is not containment evidence.
        return process.pid, observation, stdout, stderr

    def collect(self, mode="pass", termination=None):
        request = self.prepare()
        pid, observation, stdout, stderr = self.external(
            [sys.executable, "-I", "-B", str(self.runtime), mode],
            self.candidate,
            request.model_dump_json().encode(),
        )
        self.store.record_attempt(
            self.changed(self.attempt, state="acknowledged", handle=f"fixture:{pid}"),
            1,
            "lease",
        )
        if termination:
            observation = self.changed(observation, termination=termination)
        return collect_codex_attempt(
            self.store,
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
            expected_configuration=self.identity.configuration,
            observation=observation,
            stdout=stdout,
            stderr=stderr,
        )

    def validate(self, result, **changes):
        _, observation, stdout, stderr = self.external(self.check.argv, self.frozen)
        arguments = dict(
            collection_id=result.id,
            current=result.binding,
            check_id=self.check.id,
            observed=self.check,
            observation=observation,
            stdout=stdout,
            stderr=stderr,
            candidate_root=self.frozen,
            environment=self.check.environment,
            toolchain=self.check.toolchain,
            credential_free=True,
            network_disabled=True,
            expected_run_version=self.store.get("run", "run", Run)[1],
            token="lease",
        )
        return capture_collected_check(self.store, **{**arguments, **changes})

    def verdict(self, result):
        return self.store.verdict(
            "run",
            self.model.project_id,
            result.binding,
            "lease",
            candidate_root=self.frozen,
        )

    def test_complete_external_workflow_preserves_original_and_durable_evidence(self):
        result = self.collect()
        self.assertEqual(result.outcome.status, "completed")
        self.assertNotEqual(result.launch_binding.candidate, result.binding.candidate)
        self.assertEqual(self.verdict(result).gates["check:bytes"], "missing")
        evidence = self.validate(result)
        self.assertEqual(evidence.definition, self.check)
        self.assertEqual(evidence.binding.candidate, record_digest(result.frozen))
        self.assertEqual(self.verdict(result).gates["approval"], "missing")
        self.approve(result.binding)
        verdict = self.verdict(result)
        self.assertEqual(verdict.status, "verified")
        self.assertFalse(verdict.execution_allowed)
        self.assertFalse(result.execution_allowed)
        self.assertEqual(len(self.store.records("claim", Claim)), 1)
        self.assertEqual(len(self.store.records("evidence", Evidence)), 2)
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        self.assertEqual(self.store.get("collection", result.id, CodexCollection)[0], result)
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "verdict")
        self.assertEqual(self.store.reconcile_launches(), [])
        self.assertEqual(
            self.original_bytes,
            {
                str(path.relative_to(self.original)): path.read_bytes()
                for path in self.original.rglob("*")
                if path.is_file()
            },
        )

    def test_request_rejects_stale_inputs_without_persisting_intent(self):
        for changes in [
            {"token": "wrong"},
            {"allowed_paths": []},
            {"current": self.changed(self.binding, policy=digest(b"stale"))},
            {"expected_configuration": digest(b"stale")},
            {"identity": self.changed(self.identity, provider="other")},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.prepare(**changes)
            self.assertEqual(self.store.records("attempt", Attempt), [])

    def test_unconfirmed_project_refuses_request(self):
        proposal = discover(self.original)
        self.store.save_project(proposal, 1)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(self.store.records("attempt", Attempt), [])

    def test_missing_owner_decision_refuses_request(self):
        # A fresh run has no approval, even when all content digests match.
        self.store.transition("run", 1, "interrupted", "lease")
        run = Run(id="unapproved", task_id="task", binding=self.binding)
        self.store.create_run(run, self.model.project_id)
        self.store.acquire(run.id, "lease")
        with self.assertRaisesRegex(ValueError, "owner approval"):
            self.prepare(attempt=self.changed(self.attempt, run_id=run.id))

    def test_candidate_mutation_before_intent_refuses(self):
        (self.candidate / "README.md").write_bytes(b"premature")
        with self.assertRaisesRegex(ValueError, "initial candidate changed"):
            self.prepare()

    def test_existing_intent_cannot_retry_and_restart_interrupts_it(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "automatic retry"):
            self.prepare(attempt=self.changed(self.attempt, id="retry"))
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        self.assertEqual(self.store.reconcile_launches(), ["worker"])
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        with self.assertRaises(ValueError):
            self.store.acquire("run", "new")

    def test_malformed_output_never_freezes_or_creates_check_evidence(self):
        result = self.collect("malformed")
        self.assertEqual(result.outcome.status, "malformed")
        self.assertIsNone(result.frozen)
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(self.store.records("evidence", Evidence), [])

    def test_external_scope_escape_blocks_verdict(self):
        result = self.collect("outside")
        self.validate(result)
        self.approve(result.binding)
        self.assertEqual(self.verdict(result).gates["scope"], "blocking_findings")

    def test_forged_claim_cannot_replace_failed_external_check(self):
        result = self.collect("wrong")
        self.validate(result)
        self.approve(result.binding)
        self.assertEqual(self.verdict(result).status, "failed")

    def test_failed_external_process_never_freezes_completed_text(self):
        result = self.collect("failure")
        self.assertEqual(result.outcome.status, "failed")
        self.assertIsNone(result.frozen)
        self.assertEqual(self.store.records("evidence", Evidence), [])

    def test_validator_refuses_stale_check_and_capture_bindings(self):
        result = self.collect()
        for changes in [
            {"check_id": "invented"},
            {"token": "wrong"},
            {"expected_run_version": 1},
            {"current": self.binding},
            {"observed": self.changed(self.check, argv=["forged-check"])},
            {"environment": digest(b"wrong")},
            {"toolchain": digest(b"wrong")},
            {"credential_free": False},
            {"network_disabled": False},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.validate(result, **changes)
            self.assertEqual(self.store.get("run", "run", Run)[0].state, "frozen")
            self.assertEqual(len(self.store.records("evidence", Evidence)), 1)

    def test_validator_capture_cannot_replay(self):
        result = self.collect()
        self.validate(result)
        with self.assertRaisesRegex(ValueError, "already captured"):
            self.validate(result)
        self.assertEqual(len(self.store.records("evidence", Evidence)), 2)

    def test_collection_artifact_mutation_refuses_validation(self):
        result = self.collect()
        (self.store.directory / "artifacts" / result.stdout).write_bytes(b"substituted")
        with self.assertRaises(ValueError):
            self.validate(result)
        self.assertEqual(len(self.store.records("evidence", Evidence)), 1)

    def test_restart_after_validation_preserves_evidence_without_completion(self):
        result = self.collect()
        self.validate(result)
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        self.assertEqual(self.store.reconcile_launches(), [])
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(len(self.store.records("evidence", Evidence)), 2)
        with self.assertRaises(ValueError):
            self.store.acquire("run", "retry")

    def test_frozen_mutation_refuses_capture(self):
        result = self.collect()
        (self.frozen / "README.md").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "mutated frozen"):
            self.validate(result)

    def test_mutation_after_validation_refuses_verdict(self):
        result = self.collect()
        self.validate(result)
        self.approve(result.binding)
        (self.frozen / "README.md").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "frozen candidate changed"):
            self.verdict(result)

    def test_validation_sql_failure_rolls_back_capture_and_transition(self):
        result = self.collect()
        self.store.connection.execute("""CREATE TRIGGER refuse_validating BEFORE UPDATE ON records
            WHEN NEW.kind='run' BEGIN SELECT RAISE(ABORT, 'fixture interruption'); END""")
        with self.assertRaisesRegex(Exception, "fixture interruption"):
            self.validate(result)
        self.assertEqual(len(self.store.records("evidence", Evidence)), 1)
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "frozen")
        self.store.connection.execute("DROP TRIGGER refuse_validating")
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        self.assertEqual(self.store.reconcile_launches(), [])
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(len(self.store.records("evidence", Evidence)), 1)

    def test_restart_after_acknowledgement_never_replays_external_work(self):
        self.prepare()
        self.store.record_attempt(
            self.changed(self.attempt, state="acknowledged", handle="fixture:retained"),
            1,
            "lease",
        )
        self.store.close()
        self.store = CoordinatorStore(self.root / "state")
        self.assertEqual(self.store.reconcile_launches(), ["worker"])
        self.assertEqual(self.store.get("attempt", "worker", Attempt)[0].handle, "fixture:retained")
        self.assertEqual((self.candidate / "README.md").read_bytes(), b"before\n")


def termination_case(reason):
    def test(self):
        result = self.collect(termination=reason)
        self.assertEqual(result.outcome.status, reason)
        self.assertIsNone(result.frozen)
        self.assertFalse(self.frozen.exists())
        self.assertEqual(self.store.get("run", "run", Run)[0].state, "interrupted")
        self.assertEqual(len(self.store.records("attempt", Attempt)), 1)
        with self.assertRaises(ValueError):
            self.prepare(attempt=self.changed(self.attempt, id="retry"))

    return test


def validator_termination_case(reason):
    def test(self):
        result = self.collect()
        _, observation, _, _ = self.external(self.check.argv, self.frozen)
        evidence = self.validate(result, observation=self.changed(observation, termination=reason))
        self.assertIn(evidence.status, {"terminated", "unavailable"})
        self.approve(result.binding)
        self.assertNotEqual(self.verdict(result).status, "verified")
        with self.assertRaisesRegex(ValueError, "already captured"):
            self.validate(result)

    return test


for reason in ("cancelled", "timeout", "refusal", "interrupted"):
    setattr(Phase2DCore, f"test_external_{reason}_cannot_freeze_or_retry", termination_case(reason))
    setattr(
        Phase2DCore,
        f"test_validator_{reason}_cannot_pass_or_retry",
        validator_termination_case(reason),
    )


if __name__ == "__main__":
    unittest.main()
