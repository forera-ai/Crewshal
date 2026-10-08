"""Independent synthetic acceptance: no adapters, network, credentials or launchers."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

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
    Verdict,
    Waiver,
    cumulative_usage,
    record_digest,
)
from crewshal.discovery import discover
from crewshal.durable import APPLICATION_ID, Conflict, CoordinatorStore
from crewshal.gates import evaluate
from crewshal.model import HumanDecision, ProjectModel, decide, digest, model_digest, reconcile
from crewshal.state import ModelStore

NOW = datetime(2026, 10, 2, tzinfo=timezone.utc)
LOG = b"synthetic coordinator capture\n"
EMPTY = digest(b"")


class Phase2B(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repository = self.base / "repo"
        self.repository.mkdir()
        (self.repository / "package.json").write_text(
            '{"name":"fixture","scripts":{"test":"false"}}'
        )
        self.model = discover(self.repository)
        self.directory = self.base / "state"
        self.store = self.open_store()
        self.store.save_project(self.model, 0)
        self.check = CheckDefinition(
            id="test", argv=["false"], cwd=".", environment=EMPTY, toolchain=EMPTY
        )
        self.task = Task(id="task", requirement="Synthetic acceptance only", checks=[self.check])
        self.store.create_task(self.task)
        self.binding = Binding(
            model=model_digest(self.model),
            task=record_digest(self.task),
            policy=EMPTY,
            scope=EMPTY,
            candidate=EMPTY,
        )
        self.run = Run(id="run", task_id=self.task.id, binding=self.binding)
        self.store.create_run(self.run, self.model.project_id)
        self.store.acquire(self.run.id, "owner-lease")

    def open_store(self, directory=None, **kwargs):
        store = CoordinatorStore(directory or self.directory, **kwargs)
        self.addCleanup(store.close)
        return store

    def replace(self, record, **changes):
        return type(record).model_validate({**record.model_dump(), **changes})

    def attempt(
        self, identifier="worker", role="implementation", provider="provider-a", model="model-a"
    ):
        attempt = Attempt(
            id=identifier,
            run_id=self.run.id,
            binding=self.binding,
            role=role,
            provider=provider,
            model=model,
            state="intent",
        )
        self.store.launch_intent(attempt, "owner-lease")
        acknowledged = self.replace(attempt, state="acknowledged", handle=f"synthetic:{identifier}")
        self.store.record_attempt(acknowledged, 1, "owner-lease")
        complete = self.replace(
            acknowledged, state="completed", process_exit=0, runtime_result="completed"
        )
        self.store.record_attempt(complete, 2, "owner-lease")
        return complete

    def evidence(self, identifier, gate, attempt, status="passed", **changes):
        kind = "check" if gate.startswith("check:") else gate
        item = Evidence(
            id=identifier,
            run_id=self.run.id,
            attempt_id=attempt.id,
            binding=self.binding,
            kind=kind,
            gate=gate,
            status=status,
            definition=self.check if kind == "check" else None,
            started=NOW,
            ended=NOW,
            exit_code=0 if kind == "check" else None,
            stdout=digest(LOG),
            stderr=EMPTY,
            provider=attempt.provider if kind == "review" else None,
            model=attempt.model if kind == "review" else None,
        )
        return self.replace(item, **changes)

    def capture(self, item):
        self.store.capture(
            item,
            "owner-lease",
            stdout=LOG if item.stdout is not None else None,
            stderr=b"" if item.stderr is not None else None,
        )

    def ready_evidence(
        self, *, provider="provider-b", model="model-b", check_status="passed", review=True
    ):
        worker = self.attempt()
        self.store.owner_approval(
            Approval(
                id="approval",
                run_id=self.run.id,
                binding=self.binding,
                owner="fixture-owner",
                reason="bounded synthetic test",
            )
        )
        self.store.transition(self.run.id, 1, "frozen", "owner-lease")
        self.store.transition(self.run.id, 2, "validating", "owner-lease")
        self.capture(
            self.evidence(
                "check",
                "check:test",
                worker,
                check_status,
                exit_code=1 if check_status == "failed" else 0,
            )
        )
        self.capture(self.evidence("scope", "scope", worker))
        if review:
            reviewer = self.attempt("reviewer", "review", provider, model)
            self.capture(self.evidence("review", "review", reviewer))
        return worker

    def verdict(self, current=None):
        return self.store.verdict(
            self.run.id, self.model.project_id, current or self.binding, "owner-lease"
        )

    def test_closed_versioned_records_reject_malformed_unknown_and_boolean_versions(self):
        examples = [
            self.task,
            self.run,
            self.binding,
            Usage(id="u", attempt_id="a", event_id="e", sequence=0, provenance="runtime_reported"),
        ]
        for item in examples:
            with self.subTest(contract=type(item).__name__):
                with self.assertRaises(ValueError):
                    type(item).model_validate({**item.model_dump(), "worker_approval": True})
                if "schema_version" in item.model_dump():
                    for version in (True, 2, "1"):
                        with self.assertRaises(ValueError):
                            self.replace(item, schema_version=version)
        for value in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                Usage(
                    id="u",
                    attempt_id="a",
                    event_id="e",
                    sequence=value,
                    provenance="runtime_reported",
                )

    def test_database_schema_refusal_preserves_bytes(self):
        for version in (0, 3, 999):
            directory = self.base / f"schema-{version}"
            directory.mkdir(mode=0o700)
            path = directory / "coordinator.sqlite3"
            with sqlite3.connect(path) as database:
                database.execute(f"PRAGMA user_version={version}")
                database.execute(f"PRAGMA application_id={APPLICATION_ID}")
            path.chmod(0o600)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                self.open_store(directory, migrate=True)
            self.assertEqual(path.read_bytes(), before)
        malformed = self.base / "malformed"
        malformed.mkdir(mode=0o700)
        path = malformed / "coordinator.sqlite3"
        path.write_bytes(b"not sqlite")
        path.chmod(0o600)
        with self.assertRaises(sqlite3.DatabaseError):
            self.open_store(malformed)
        self.assertEqual(path.read_bytes(), b"not sqlite")

    def legacy_database(self, directory, payload):
        directory.mkdir(mode=0o700)
        path = directory / "coordinator.sqlite3"
        with sqlite3.connect(path) as database:
            database.executescript("""
                CREATE TABLE records(id TEXT PRIMARY KEY,kind TEXT NOT NULL,version INTEGER NOT NULL CHECK(version>0),payload TEXT NOT NULL);
                CREATE TABLE events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,record_id TEXT NOT NULL,version INTEGER NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL,UNIQUE(record_id,version));
                CREATE TABLE lease(singleton INTEGER PRIMARY KEY CHECK(singleton=1),run_id TEXT NOT NULL,token TEXT NOT NULL);
            """)
            database.execute(f"PRAGMA application_id={APPLICATION_ID}")
            database.execute("PRAGMA user_version=1")
            database.execute(
                "INSERT INTO records VALUES(?,?,?,?)",
                (f"project:{self.model.project_id}", "project", 1, payload),
            )
            database.execute(
                "INSERT INTO events(record_id,version,kind,payload) VALUES(?,?,?,?)",
                (f"project:{self.model.project_id}", 1, "project", payload),
            )
        path.chmod(0o600)
        return path

    def test_supported_migration_backs_up_before_change_and_preserves_events(self):
        directory = self.base / "old"
        path = self.legacy_database(directory, self.model.model_dump_json())
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.open_store(directory)
        self.assertEqual(path.read_bytes(), before)
        migrated = self.open_store(directory, migrate=True)
        self.assertEqual(
            migrated.get("project", self.model.project_id, ProjectModel), (self.model, 1)
        )
        self.assertEqual(
            migrated.connection.execute("SELECT sequence,version FROM events").fetchall()[0][:],
            (1, 1),
        )
        self.assertEqual(migrated.backup_path.stat().st_mode & 0o777, 0o600)
        with sqlite3.connect(migrated.backup_path) as backup:
            self.assertEqual(backup.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertEqual(
                backup.execute("SELECT payload FROM records").fetchone()[0],
                self.model.model_dump_json(),
            )

    def test_failed_migration_rolls_back_with_recoverable_backup(self):
        directory = self.base / "invalid-old"
        path = self.legacy_database(directory, '{"schema_version":99}')
        with self.assertRaises(ValueError):
            self.open_store(directory, migrate=True)
        with sqlite3.connect(path) as database:
            self.assertEqual(database.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertNotIn(
                "payload_digest", [row[1] for row in database.execute("PRAGMA table_info(records)")]
            )
            self.assertEqual(
                database.execute("SELECT payload FROM records").fetchone()[0],
                '{"schema_version":99}',
            )
        self.assertEqual(len(list(directory.glob("*.bak"))), 1)

    def test_explicit_phase_2a_json_migration_preserves_decisions_and_invalidates_changes(self):
        directory = self.base / "json-state"
        directory.mkdir(mode=0o700)
        model = decide(
            self.model,
            [
                HumanDecision(
                    fact_id="package.json:package",
                    action="correct",
                    value="owner-name",
                    reason="human",
                ),
                HumanDecision(fact_id="package.json:package", action="confirm", reason="human"),
            ],
        )
        legacy = ModelStore(self.repository, directory).path
        legacy.write_text(model.public_json())
        legacy.chmod(0o600)
        before = legacy.read_bytes()
        with self.assertRaises(ValueError):
            ModelStore(self.repository, directory).load()
        facade = ModelStore(self.repository, directory, migrate=True)
        self.assertEqual(facade.load(), model)
        self.assertEqual(legacy.read_bytes(), before)
        self.assertEqual(ModelStore(self.repository, directory).load(), model)
        (self.repository / "package.json").write_text('{"name":"changed"}')
        fresh = reconcile(discover(self.repository), model)
        fact = next(f for f in fresh.facts if f.id == "package.json:package")
        self.assertEqual(fact.decision, "pending")
        self.assertEqual(fact.history[-1].action, "invalidate")
        facade.save(fresh)
        self.assertEqual(legacy.read_bytes(), before)
        # Informational repository exports cannot become external state implicitly.
        (self.repository / "export.json").write_text(model.public_json())
        with self.assertRaises(ValueError):
            ModelStore(self.repository, self.repository, migrate=True)

    def test_two_writer_compare_and_update_preserves_winner_and_ordered_events(self):
        first = ModelStore(self.repository, self.directory)
        second = ModelStore(self.repository, self.directory)
        self.assertEqual(first.load(), self.model)
        self.assertEqual(second.load(), self.model)
        winner = decide(
            self.model,
            [
                HumanDecision(
                    fact_id="package.json:package", action="confirm", reason="first writer"
                )
            ],
        )
        first.save(winner)
        before = self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        with self.assertRaises(Conflict):
            second.save(self.model)
        self.assertEqual(ModelStore(self.repository, self.directory).load(), winner)
        self.assertEqual(
            self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], before
        )
        events = self.store.connection.execute(
            "SELECT sequence,version FROM events WHERE kind='project' ORDER BY sequence"
        ).fetchall()
        self.assertEqual([row[1] for row in events], [1, 2])
        self.assertEqual([row[0] for row in events], sorted({row[0] for row in events}))

    def test_transaction_rollback_and_process_crash_never_leave_half_transition(self):
        count = self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        with self.assertRaises(RuntimeError), self.store.transaction():
            self.store._put("project", self.model.project_id, self.model, 1)
            raise RuntimeError("synthetic crash before commit")
        self.assertEqual(self.store.get("project", self.model.project_id, ProjectModel)[1], 1)
        self.assertEqual(
            self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], count
        )
        code = """
import os, sqlite3, sys
database=sqlite3.connect(sys.argv[1],isolation_level=None)
database.execute('BEGIN IMMEDIATE')
database.execute('UPDATE records SET version=version+1 WHERE kind=?',('project',))
database.execute('INSERT INTO events(record_id,version,kind,payload) SELECT id,version,kind,payload FROM records WHERE kind=?',('project',))
os._exit(37)
"""
        crashed = subprocess.run([sys.executable, "-c", code, str(self.store.path)])
        self.assertEqual(crashed.returncode, 37)
        recovered = self.open_store()
        self.assertEqual(
            recovered.get("project", self.model.project_id, ProjectModel), (self.model, 1)
        )
        self.assertEqual(
            recovered.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], count
        )

    def test_lease_and_state_versions_refuse_second_coordinator_and_blind_takeover(self):
        other = self.open_store()
        with self.assertRaises(Conflict):
            other.acquire(self.run.id, "second")
        with self.assertRaises(Conflict):
            other.transition(self.run.id, 1, "frozen", "second")
        self.store.transition(self.run.id, 1, "frozen", "owner-lease")
        with self.assertRaises(Conflict):
            other.transition(self.run.id, 1, "validating", "owner-lease")
        with self.assertRaises(ValueError):
            self.store.transition(self.run.id, 2, "verdict", "owner-lease")

    def test_uncertain_launch_intent_and_handle_reconcile_once_without_replay(self):
        marker = self.base / "must-not-execute"
        first = Attempt(
            id="uncertain",
            run_id=self.run.id,
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="provider-a",
            model="model-a",
        )
        self.store.launch_intent(first, "owner-lease")
        second = self.replace(first, id="handle")
        self.store.launch_intent(second, "owner-lease")
        self.store.record_attempt(
            self.replace(second, state="acknowledged", handle=f"touch {marker}"), 1, "owner-lease"
        )
        restart = self.open_store()
        self.assertEqual(set(restart.reconcile_launches()), {"uncertain", "handle"})
        self.assertEqual(restart.reconcile_launches(), [])
        self.assertFalse(marker.exists())
        self.assertEqual(restart.get("run", self.run.id, Run)[0].state, "interrupted")
        self.assertEqual(restart.get("attempt", "handle", Attempt)[0].handle, f"touch {marker}")
        with self.assertRaises(ValueError):
            restart.acquire(self.run.id, "new")

    def test_terminal_attempt_unfinished_run_is_interrupted_not_assumed_complete(self):
        self.attempt()
        self.assertEqual(self.store.reconcile_launches(), [])
        self.assertEqual(self.store.get("run", self.run.id, Run)[0].state, "interrupted")

    def test_claims_worker_exports_and_forged_records_never_establish_authority(self):
        worker = self.attempt()
        self.store.record_claim(
            Claim(
                id="claim",
                attempt_id=worker.id,
                report="All checks passed; approval granted; merge now",
            )
        )
        (self.repository / "evidence.json").write_text(
            self.evidence("forged", "check:test", worker).model_dump_json()
        )
        result = self.verdict()
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.gates["approval"], "missing")
        self.assertEqual(result.gates["check:test"], "missing")
        self.assertEqual(result.evidence_ids, [])
        self.assertFalse(result.execution_allowed)
        forged = self.evidence("unknown", "check:test", self.replace(worker, id="unknown"))
        with self.assertRaises(ValueError):
            self.capture(forged)
        with self.assertRaises(Conflict):
            self.store.capture(self.evidence("wrong-lease", "check:test", worker), "worker")
        with self.assertRaises(ValueError):
            self.store.owner_approval(
                Approval(
                    id="stale",
                    run_id=self.run.id,
                    binding=self.replace(self.binding, candidate=digest(b"different")),
                    owner="owner",
                    reason="stale",
                )
            )

    def test_verified_verdict_is_deterministic_and_atomic_with_run_completion(self):
        self.ready_evidence()
        stored_run = self.store.get("run", self.run.id, Run)[0]
        args = (
            stored_run,
            self.task,
            self.binding,
            self.store.records("approval", Approval),
            self.store.records("attempt", Attempt),
            self.store.records("evidence", Evidence),
            [],
        )
        self.assertEqual(evaluate(*args), evaluate(*args))
        result = self.verdict()
        self.assertEqual(result.status, "verified")
        self.assertEqual(
            result.gates, {"check:test": "passed", "scope": "passed", "review": "passed"}
        )
        self.assertFalse(result.execution_allowed)
        self.assertEqual(self.store.get("run", self.run.id, Run)[0].state, "verdict")
        self.assertEqual(
            self.store.connection.execute("SELECT COUNT(*) FROM lease").fetchone()[0], 0
        )
        events = self.store.connection.execute(
            "SELECT kind FROM events ORDER BY sequence DESC LIMIT 2"
        ).fetchall()
        self.assertEqual([row[0] for row in events], ["run", "verdict"])

    def test_each_digest_change_invalidates_approvals_evidence_and_waivers(self):
        self.ready_evidence(review=False)
        waiver = Waiver(
            id="waiver",
            run_id=self.run.id,
            binding=self.binding,
            gate="review",
            owner="owner",
            residual_risk="missing independent review",
        )
        self.store.owner_waiver(waiver)
        run = self.store.get("run", self.run.id, Run)[0]
        for field in ("model", "task", "policy", "scope", "candidate"):
            current = self.replace(self.binding, **{field: digest(field.encode())})
            result = evaluate(
                run,
                self.task,
                current,
                self.store.records("approval", Approval),
                self.store.records("attempt", Attempt),
                self.store.records("evidence", Evidence),
                [waiver],
            )
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.gates["binding"], "stale")
            self.assertEqual(result.waiver_ids, [])
        changed_model = decide(
            self.model,
            [
                HumanDecision(
                    fact_id="package.json:package", action="confirm", reason="changed model"
                )
            ],
        )
        self.store.save_project(changed_model, 1)
        with self.assertRaises(ValueError):
            self.verdict()

    def test_required_check_states_stay_distinct_and_waivers_never_relabel_pass(self):
        self.ready_evidence(review=False, check_status="unavailable")
        first = self.verdict()
        self.assertEqual(first.status, "blocked")
        self.assertEqual(first.gates["check:test"], "unavailable")
        for gate in ("review", "check:test"):
            self.store.owner_waiver(
                Waiver(
                    id=f"waiver-{gate}",
                    run_id=self.run.id,
                    binding=self.binding,
                    gate=gate,
                    owner="named-owner",
                    residual_risk="evidence not passing",
                )
            )
        result = self.verdict()
        self.assertEqual(result.status, "accepted_with_waiver")
        self.assertEqual(result.gates["check:test"], "unavailable")
        self.assertEqual(result.gates["review"], "missing")
        self.assertEqual(len(result.waiver_ids), 2)

    def test_failed_skipped_terminated_and_incomplete_checks_cannot_verify(self):
        worker = self.ready_evidence(check_status="failed")
        result = self.verdict()
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.gates["check:test"], "failed")
        run = self.store.get("run", self.run.id, Run)[0]
        evidence = self.store.records("evidence", Evidence)
        for status in ("skipped", "unavailable", "terminated"):
            changed = [
                self.replace(
                    e, status=status, termination="timeout" if status == "terminated" else None
                )
                if e.kind == "check"
                else e
                for e in evidence
            ]
            result = evaluate(
                run,
                self.task,
                self.binding,
                self.store.records("approval", Approval),
                self.store.records("attempt", Attempt),
                changed,
                [],
            )
            self.assertNotEqual(result.status, "verified")
            self.assertEqual(result.gates["check:test"], status)
        for changes in ({"exit_code": 1}, {"stdout": None}, {"termination": "timeout"}):
            with self.assertRaises(ValueError):
                self.evidence("bad", "check:test", worker, **changes)
        with self.assertRaises(ValueError):
            self.evidence(
                "bad-time", "scope", worker, ended=datetime(2025, 1, 1, tzinfo=timezone.utc)
            )

    def test_contradictory_checks_wrong_definitions_and_scope_fail_closed(self):
        worker = self.ready_evidence()
        self.capture(self.evidence("conflict", "check:test", worker, "failed", exit_code=1))
        result = self.verdict()
        self.assertEqual(result.gates["check:test"], "contradictory")
        self.assertEqual(result.status, "blocked")
        run = self.store.get("run", self.run.id, Run)[0]
        original = [e for e in self.store.records("evidence", Evidence) if e.id != "conflict"]
        altered = [
            self.replace(e, definition=self.replace(self.check, argv=["true"]))
            if e.kind == "check"
            else e
            for e in original
        ]
        result = evaluate(
            run,
            self.task,
            self.binding,
            self.store.records("approval", Approval),
            self.store.records("attempt", Attempt),
            altered,
            [],
        )
        self.assertEqual(result.gates["check:test"], "definition_mismatch")
        scope_failed = [
            self.replace(e, status="failed", blocking_findings=["escaped scope"])
            if e.kind == "scope"
            else e
            for e in original
        ]
        waiver = Waiver(
            id="scope-waiver",
            run_id=self.run.id,
            binding=self.binding,
            gate="scope",
            owner="owner",
            residual_risk="scope escaped",
        )
        result = evaluate(
            run,
            self.task,
            self.binding,
            self.store.records("approval", Approval),
            self.store.records("attempt", Attempt),
            scope_failed,
            [waiver],
        )
        self.assertEqual(result.gates["scope"], "blocking_findings")
        self.assertEqual(result.waiver_ids, [])

    def test_review_independence_requires_known_matching_provider_and_model(self):
        self.ready_evidence()
        run = self.store.get("run", self.run.id, Run)[0]
        original_attempts = self.store.records("attempt", Attempt)
        original_evidence = self.store.records("evidence", Evidence)
        for provider, model, expected in (
            (None, "model-b", "identity_unavailable"),
            ("provider-a", "model-b", "not_independent"),
            ("provider-b", None, "identity_unavailable"),
        ):
            attempts = [
                self.replace(a, provider=provider, model=model) if a.role == "review" else a
                for a in original_attempts
            ]
            evidence = [
                self.replace(e, provider=provider, model=model) if e.kind == "review" else e
                for e in original_evidence
            ]
            result = evaluate(
                run,
                self.task,
                self.binding,
                self.store.records("approval", Approval),
                attempts,
                evidence,
                [],
            )
            self.assertEqual(result.gates["review"], expected)
            self.assertEqual(result.status, "blocked")
        missing_worker_identity = [
            self.replace(a, provider=None) if a.role == "implementation" else a
            for a in original_attempts
        ]
        self.assertEqual(
            evaluate(
                run,
                self.task,
                self.binding,
                self.store.records("approval", Approval),
                missing_worker_identity,
                original_evidence,
                [],
            ).gates["review"],
            "identity_unavailable",
        )
        fake = [
            self.replace(e, provider="provider-c") if e.kind == "review" else e
            for e in original_evidence
        ]
        self.assertEqual(
            evaluate(
                run,
                self.task,
                self.binding,
                self.store.records("approval", Approval),
                original_attempts,
                fake,
                [],
            ).gates["evidence_integrity"],
            "review_identity_mismatch",
        )

    def test_inconsistent_attempt_exit_and_runtime_result_cannot_complete(self):
        self.ready_evidence()
        run = self.store.get("run", self.run.id, Run)[0]
        for changes in (
            {"process_exit": 1},
            {"runtime_result": "failed"},
            {"state": "interrupted"},
            {"state": "cancelled"},
        ):
            attempts = [
                self.replace(a, **changes) if a.role == "implementation" else a
                for a in self.store.records("attempt", Attempt)
            ]
            result = evaluate(
                run,
                self.task,
                self.binding,
                self.store.records("approval", Approval),
                attempts,
                self.store.records("evidence", Evidence),
                [],
            )
            self.assertNotEqual(result.status, "verified")
            self.assertEqual(result.gates["implementation"], "incomplete")

    def test_capture_requires_actual_private_bytes_and_rejects_tampering(self):
        worker = self.attempt()
        item = self.evidence("check", "check:test", worker)
        with self.assertRaises(ValueError):
            self.store.capture(item, "owner-lease")
        with self.assertRaises(ValueError):
            self.store.capture(item, "owner-lease", stdout=b"worker-forged", stderr=b"")
        self.capture(item)
        artifact = self.directory / "artifacts" / digest(LOG)
        self.assertEqual(artifact.stat().st_mode & 0o777, 0o600)
        artifact.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.verdict()
        self.assertIsNone(
            self.store.get(
                "verdict",
                f"verdict:{self.run.id}",
                Verdict,
            )[0]
        )

    def test_private_database_rejects_symlinks_permissions_and_mutated_payload(self):
        self.assertEqual(self.directory.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.store.path.stat().st_mode & 0o777, 0o600)
        linked = self.base / "linked"
        linked.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.open_store(linked)
        self.store.connection.execute("UPDATE records SET payload=? WHERE kind='project'", ("{}",))
        with self.assertRaises(ValueError):
            self.store.get("project", self.model.project_id, ProjectModel)
        self.store.path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.open_store()

    def test_usage_deduplicates_cumulative_snapshots_and_keeps_unknown_cost_unknown(self):
        self.attempt()
        first = Usage(
            id="u1",
            attempt_id="worker",
            event_id="e1",
            sequence=1,
            provenance="runtime_reported",
            input_tokens=10,
            output_tokens=2,
            estimated_cost_microusd=3,
        )
        second = self.replace(
            first,
            id="u2",
            event_id="e2",
            sequence=2,
            input_tokens=20,
            output_tokens=4,
            estimated_cost_microusd=6,
        )
        self.store.record_usage(second)
        self.store.record_usage(first)
        count = self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.store.record_usage(second)
        self.assertEqual(
            self.store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], count
        )
        result = cumulative_usage(["worker"], self.store.records("usage", Usage) + [second])
        self.assertEqual(result["input_tokens"], 20)
        self.assertEqual(result["output_tokens"], 4)
        self.assertEqual(result["estimated_cost_microusd"], 6)
        self.assertIsNone(result["measured_cost_microusd"])
        self.assertIsNone(result["subscription_quota"])
        for conflicting in (
            self.replace(second, input_tokens=21),
            self.replace(second, id="other"),
            self.replace(second, id="u3", event_id="e3", sequence=3, input_tokens=5),
        ):
            with self.assertRaises(ValueError):
                self.store.record_usage(conflicting)
        reviewer = self.attempt("reviewer", "review", "provider-b")
        total = cumulative_usage(["worker", reviewer.id], self.store.records("usage", Usage))
        self.assertIsNone(total["input_tokens"])
        self.store.record_usage(
            Usage(
                id="u-review",
                attempt_id=reviewer.id,
                event_id="e1",
                sequence=1,
                provenance="provider_measured",
                input_tokens=7,
                output_tokens=1,
                measured_cost_microusd=8,
            )
        )
        total = cumulative_usage(["worker", reviewer.id], self.store.records("usage", Usage))
        self.assertEqual(total["input_tokens"], 27)
        self.assertIsNone(total["measured_cost_microusd"])


if __name__ == "__main__":
    unittest.main()
