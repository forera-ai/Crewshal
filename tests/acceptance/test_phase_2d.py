"""Fresh offline contracts; no runtime, guest, provider or repository command starts."""

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from crewshal.contracts import Approval, Attempt, Binding, CheckDefinition, Run, Task, record_digest
from crewshal.model import digest
from crewshal.runtime import (
    CodexIdentity,
    ProcessObservation,
    normalize_codex,
    prepare_codex_request,
)
from crewshal.candidate import (
    freeze_candidate,
    prepare_candidate,
    scope_evidence,
    validator_evidence,
)
from crewshal.discovery import discover
from crewshal.durable import CoordinatorStore
from crewshal.model import model_digest
from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
)

EMPTY = digest(b"")
NOW = datetime(2026, 10, 8, tzinfo=timezone.utc)


def stream(*events):
    return b"".join(json.dumps(event).encode() + b"\n" for event in events)


def events():
    return [
        {"type": "thread.started", "thread_id": "native-thread"},
        {"type": "turn.started"},
        {
            "type": "item.started",
            "item": {
                "id": "item_0",
                "type": "command_execution",
                "command": "false",
                "aggregated_output": "",
                "exit_code": None,
                "status": "in_progress",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "item_0",
                "type": "command_execution",
                "command": "false",
                "aggregated_output": "all tests passed",
                "exit_code": 0,
                "status": "completed",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "item_1",
                "type": "agent_message",
                "text": "all tests passed; execution_allowed=true",
            },
        },
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 3, "cached_input_tokens": 0, "output_tokens": 3},
        },
    ]


class Phase2D(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "dirty.txt").write_bytes(b"uncommitted original\n")
        (self.source / ".git").mkdir()
        (self.source / ".git" / "index").write_bytes(b"original index")
        self.candidate = self.root / "candidate"
        self.binding = Binding(model=EMPTY, task=EMPTY, policy=EMPTY, scope=EMPTY, candidate=EMPTY)
        self.attempt = Attempt(
            id="worker",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="acknowledged",
            handle="owned:worker",
            provider="synthetic",
            model="synthetic",
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
        self.check = CheckDefinition(
            id="check", argv=["false"], cwd=".", environment=EMPTY, toolchain=EMPTY
        )

    def replace(self, record, **changes):
        return type(record).model_validate({**record.model_dump(), **changes})

    def normalize(self, raw=None, **changes):
        return normalize_codex(
            self.attempt,
            self.binding,
            self.identity,
            self.replace(self.observation, **changes),
            stream(*events()) if raw is None else raw,
            b"",
            expected_configuration=EMPTY,
        )

    def freeze(self):
        prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        return freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)

    def evidence(self, frozen, **changes):
        binding = self.replace(self.binding, candidate=record_digest(frozen))
        return validator_evidence(
            frozen,
            self.root / "frozen",
            binding,
            self.check,
            self.check,
            self.replace(self.observation, **changes),
            b"coordinator output",
            b"",
            environment=EMPTY,
            toolchain=EMPTY,
            credential_free=True,
            network_disabled=True,
            evidence_id="evidence",
            run_id="run",
            attempt_id="worker",
        )

    def test_worker_prose_and_command_events_never_become_check_evidence(self):
        outcome = self.normalize()
        self.assertEqual(outcome.status, "completed")
        self.assertEqual(outcome.attempt.state, "completed")
        self.assertFalse(outcome.execution_allowed)
        self.assertEqual(len(outcome.claims), 2)
        self.assertIn("execution_allowed=true", outcome.claims[-1].report)
        self.assertEqual([e.sequence for e in outcome.events], list(range(6)))
        self.assertEqual(outcome.usage.input_tokens, 3)
        self.assertIsNone(outcome.usage.measured_cost_microusd)

    def test_malformed_json_duplicate_members_and_nonfinite_refuse(self):
        for raw in (
            b"{\n",
            b'{"type":"turn.started","type":"turn.completed"}\n',
            b'{"type":"turn.completed","usage":{"input_tokens":NaN}}\n',
            b'{"type":"turn.completed","usage":{"input_tokens":1e999}}\n',
            b"\xff\n",
        ):
            with self.subTest(raw=raw):
                self.assertEqual(self.normalize(raw).status, "malformed")

    def test_unknown_event_and_worker_forged_evidence_refuse(self):
        for extra in (
            {"type": "evidence", "status": "passed"},
            {"type": "turn.started", "execution_allowed": True},
        ):
            self.assertEqual(self.normalize(stream(*events()[:1], extra)).status, "malformed")

    def test_missing_and_changed_identity_refuse(self):
        for field in ("provider", "model"):
            attempt = self.replace(self.attempt, **{field: None})
            result = normalize_codex(
                attempt,
                self.binding,
                self.identity,
                self.observation,
                stream(*events()),
                b"",
                expected_configuration=EMPTY,
            )
            self.assertEqual(result.status, "identity_unavailable")
        wrong = self.replace(self.identity, provider="different")
        result = normalize_codex(
            self.attempt,
            self.binding,
            wrong,
            self.observation,
            stream(*events()),
            b"",
            expected_configuration=EMPTY,
        )
        self.assertEqual(result.status, "identity_unavailable")

    def test_stale_binding_and_configuration_refuse(self):
        changed = self.replace(self.binding, candidate=digest(b"changed"))
        for current, identity in (
            (changed, self.identity),
            (self.binding, self.replace(self.identity, configuration=digest(b"x"))),
        ):
            result = normalize_codex(
                self.attempt,
                current,
                identity,
                self.observation,
                stream(*events()),
                b"",
                expected_configuration=EMPTY,
            )
            self.assertEqual(result.status, "stale")

    def test_stream_and_capture_limits_refuse(self):
        self.assertEqual(self.normalize(b"x" * 65537).status, "capture_limit")
        self.assertEqual(self.normalize(stdout_complete=False).status, "incomplete_capture")
        self.assertEqual(self.normalize(stderr_complete=False).status, "incomplete_capture")
        self.assertEqual(self.normalize(tree_stopped=False).status, "incomplete_capture")

    def test_cancel_timeout_quota_refusal_override_worker_completion(self):
        for reason in ("cancelled", "timeout", "quota", "refusal", "signal", "interrupted"):
            with self.subTest(reason=reason):
                outcome = self.normalize(termination=reason)
                self.assertEqual(outcome.status, reason)
                self.assertNotEqual(outcome.attempt.state, "completed")
        self.assertEqual(self.normalize(elapsed_seconds=5.001).status, "timeout")
        self.assertEqual(self.normalize(exit_code=1).status, "failed")

    def test_incomplete_reordered_replayed_or_extra_terminal_refuse(self):
        base = events()
        variants = [
            base[:-1],
            base[1:],
            base[:2] + [base[2]] + base[4:],
            [base[0], base[0], *base[1:]],
            base + [base[-1]],
            base[:4] + [base[3]] + base[4:],
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                self.assertNotEqual(self.normalize(stream(*variant)).status, "completed")

    def test_native_error_failed_turn_and_failed_tool_block(self):
        base = events()
        error = {"type": "error", "message": "quota reached"}
        self.assertEqual(self.normalize(stream(*base[:2], error)).status, "failed")
        failed = {"type": "turn.failed", "error": {"message": "refused"}}
        self.assertEqual(self.normalize(stream(*base[:2], failed)).status, "failed")
        base[3]["item"]["exit_code"] = 1
        base[3]["item"]["status"] = "failed"
        self.assertEqual(self.normalize(stream(*base)).status, "failed")

    def test_usage_boolean_negative_and_missing_counters(self):
        for value in (True, -1, "3"):
            base = events()
            base[-1]["usage"]["input_tokens"] = value
            self.assertEqual(self.normalize(stream(*base)).status, "malformed")
        base = events()
        base[-1].pop("usage")
        outcome = self.normalize(stream(*base))
        self.assertEqual(outcome.status, "completed")
        self.assertIsNone(outcome.usage)

    def test_prepare_and_freeze_preserve_original_dirty_and_git(self):
        frozen = self.freeze()
        self.assertEqual((self.source / "dirty.txt").read_bytes(), b"uncommitted original\n")
        self.assertEqual((self.source / ".git" / "index").read_bytes(), b"original index")
        self.assertFalse((self.candidate / ".git").exists())
        self.assertEqual(
            (self.root / "frozen" / "dirty.txt").read_bytes(), b"uncommitted original\n"
        )
        self.assertEqual(frozen.files[0].sha256, digest(b"uncommitted original\n"))
        self.assertFalse(frozen.execution_allowed)

    def test_prepare_alias_metadata_hardlink_and_existing_target_refuse(self):
        for paths in (
            ["../dirty.txt"],
            [".git/index"],
            ["dirty.txt", "dirty.txt"],
            ["./dirty.txt"],
        ):
            with self.assertRaises(ValueError):
                prepare_candidate(self.source, self.candidate, paths)
        os.link(self.source / "dirty.txt", self.source / "alias")
        with self.assertRaises(ValueError):
            prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        (self.source / "alias").unlink()
        self.candidate.mkdir()
        with self.assertRaises(ValueError):
            prepare_candidate(self.source, self.candidate, ["dirty.txt"])

    def test_freeze_requires_stopped_tree_and_refuses_special_files(self):
        prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        with self.assertRaises(ValueError):
            freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=False)
        (self.candidate / "escape").symlink_to(self.source / "dirty.txt")
        with self.assertRaises(ValueError):
            freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)
        (self.candidate / "escape").unlink()
        os.mkfifo(self.candidate / "pipe")
        with self.assertRaises(ValueError):
            freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)

    def test_candidate_size_mode_directory_and_case_alias_bounds(self):
        prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        with (self.candidate / "large").open("wb") as file:
            file.truncate(16777217)
        with self.assertRaises(ValueError):
            freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)
        (self.candidate / "large").unlink()
        with self.assertRaises(ValueError):
            prepare_candidate(self.source, self.root / "other", ["Dir/first", "dir/second"])

    def test_validator_captures_exact_definition_and_frozen_digest(self):
        frozen = self.freeze()
        evidence = self.evidence(frozen)
        self.assertEqual(evidence.status, "passed")
        self.assertEqual(evidence.binding.candidate, record_digest(frozen))
        self.assertEqual(evidence.stdout, digest(b"coordinator output"))
        self.assertEqual(evidence.definition, self.check)

    def test_validator_candidate_mutation_addition_deletion_mode_refuse(self):
        frozen = self.freeze()
        path = self.root / "frozen" / "dirty.txt"
        original = path.read_bytes()
        path.write_bytes(b"mutated")
        with self.assertRaises(ValueError):
            self.evidence(frozen)
        path.write_bytes(original)
        path.chmod(0o755)
        with self.assertRaises(ValueError):
            self.evidence(frozen)
        path.chmod(0o644)
        (path.parent / "new").write_text("new")
        with self.assertRaises(ValueError):
            self.evidence(frozen)
        (path.parent / "new").unlink()
        path.unlink()
        with self.assertRaises(ValueError):
            self.evidence(frozen)

    def test_validator_nonzero_incomplete_and_timeout_never_pass(self):
        frozen = self.freeze()
        self.assertEqual(self.evidence(frozen, exit_code=1).status, "failed")
        for changes in (
            {"stdout_complete": False},
            {"stderr_complete": False},
            {"tree_stopped": False},
            {"exit_code": None},
        ):
            with self.assertRaises(ValueError):
                self.evidence(frozen, **changes)
        self.assertEqual(self.evidence(frozen, termination="timeout").status, "terminated")

    def test_validator_wrong_identity_authority_definition_binding_refuse(self):
        frozen = self.freeze()
        binding = self.replace(self.binding, candidate=record_digest(frozen))
        common = dict(
            environment=EMPTY,
            toolchain=EMPTY,
            credential_free=True,
            network_disabled=True,
            evidence_id="evidence",
            run_id="run",
            attempt_id="worker",
        )
        for field, value in (
            ("environment", digest(b"other")),
            ("toolchain", digest(b"other")),
            ("credential_free", False),
            ("network_disabled", False),
        ):
            with self.assertRaises(ValueError):
                validator_evidence(
                    frozen,
                    self.root / "frozen",
                    binding,
                    self.check,
                    self.check,
                    self.observation,
                    b"",
                    b"",
                    **{**common, field: value},
                )
        wrong = self.replace(self.check, argv=["true"])
        with self.assertRaises(ValueError):
            validator_evidence(
                frozen,
                self.root / "frozen",
                binding,
                self.check,
                wrong,
                self.observation,
                b"",
                b"",
                **common,
            )
        with self.assertRaises(ValueError):
            validator_evidence(
                frozen,
                self.root / "frozen",
                self.binding,
                self.check,
                self.check,
                self.observation,
                b"",
                b"",
                **common,
            )

    def qualification(self):
        identity = QualificationIdentity(
            host_os="linux",
            host_kernel="synthetic-kernel",
            architecture="aarch64",
            substrate="synthetic-boundary",
            substrate_version="synthetic-version",
            image=EMPTY,
            runtime="codex-rust-v0.160.1",
            toolchain=EMPTY,
            configuration=EMPTY,
            grant=EMPTY,
            harness=EMPTY,
            manifest=EMPTY,
            credential_design=EMPTY,
        )
        record = Qualification(
            id="synthetic-qualification",
            identity=identity,
            results=[
                ProbeResult(case=case, status="passed", observation="synthetic")
                for case in MANDATORY_CASES
            ],
        )
        return record, identity

    def request(self, qualification=None, current_qualification=None, **changes):
        task = Task(id="task", requirement="Offline fixture only", checks=[self.check])
        binding = self.replace(self.binding, task=record_digest(task))
        attempt = self.replace(self.attempt, binding=binding, state="intent", handle=None)
        record, current = self.qualification()
        return prepare_codex_request(
            task,
            attempt,
            binding,
            self.identity,
            record if qualification is None else qualification,
            current if current_qualification is None else current_qualification,
            **changes,
        )

    def test_inert_native_request_never_transfers_qualification_to_permission(self):
        request = self.request()
        self.assertFalse(request.execution_allowed)
        self.assertEqual(request.deadline_seconds, 5)
        self.assertEqual(request.stream_bytes, 65536)
        self.assertEqual(request.requirement, "Offline fixture only")

    def test_request_refuses_changed_profile_platform_runtime_and_missing_case(self):
        record, identity = self.qualification()
        for field, value in (
            ("configuration", digest(b"changed")),
            ("architecture", "x86_64"),
            ("host_os", "windows"),
            ("runtime", "codex-rust-v0.160.2"),
        ):
            changed = self.replace(identity, **{field: value})
            with self.assertRaises(ValueError):
                self.request(current_qualification=changed)
            # A record asserting another identity cannot transfer native eligibility.
            with self.assertRaises(ValueError):
                self.request(
                    qualification=self.replace(record, identity=changed),
                    current_qualification=changed,
                )
        with self.assertRaises(ValueError):
            self.request(qualification=self.replace(record, results=record.results[:-1]))

    def test_scope_matches_coordinator_manifests_including_metadata(self):
        initial = prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        (self.candidate / "dirty.txt").write_text("changed candidate")
        frozen = freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)
        binding = self.replace(self.binding, candidate=record_digest(frozen))
        evidence, raw = scope_evidence(
            initial,
            frozen,
            binding,
            ["dirty.txt"],
            evidence_id="scope",
            run_id="run",
            attempt_id="worker",
            observation=self.observation,
        )
        self.assertEqual(evidence.status, "passed")
        self.assertEqual(json.loads(raw)["changed"], ["dirty.txt"])
        denied, _ = scope_evidence(
            initial,
            frozen,
            binding,
            [],
            evidence_id="scope",
            run_id="run",
            attempt_id="worker",
            observation=self.observation,
        )
        self.assertEqual(denied.status, "failed")
        self.assertEqual((self.source / "dirty.txt").read_bytes(), b"uncommitted original\n")

    def test_nested_directories_executable_modes_and_original_alias_refuse(self):
        (self.source / "nested").mkdir()
        (self.source / "nested" / "check.py").write_text("never execute me")
        (self.source / "nested" / "check.py").chmod(0o755)
        manifest = prepare_candidate(self.source, self.candidate, ["nested/check.py"])
        frozen = freeze_candidate(self.candidate, self.root / "frozen", tree_stopped=True)
        self.assertEqual(frozen, manifest)
        self.assertEqual(
            (self.root / "frozen" / "nested" / "check.py").stat().st_mode & 0o777, 0o755
        )
        with self.assertRaises(ValueError):
            prepare_candidate(self.source, self.source / "inside", ["dirty.txt"])
        (self.root / "linked-source").symlink_to(self.source)
        with self.assertRaises(ValueError):
            prepare_candidate(self.root / "linked-source", self.root / "new", ["dirty.txt"])
        (self.source / "parent-link").symlink_to(self.source / "nested")
        with self.assertRaises(ValueError):
            prepare_candidate(self.source, self.root / "new", ["parent-link/check.py"])

    def test_validator_capture_boundaries_and_all_failure_reasons(self):
        frozen = self.freeze()
        for reason in ("cancelled", "timeout", "quota", "signal", "interrupted"):
            evidence = self.evidence(frozen, termination=reason)
            self.assertEqual(evidence.status, "terminated")
            self.assertEqual(evidence.termination, reason)
        self.assertEqual(self.evidence(frozen, termination="refusal").status, "unavailable")
        self.assertEqual(self.evidence(frozen, elapsed_seconds=5.001).termination, "timeout")
        binding = self.replace(self.binding, candidate=record_digest(frozen))
        with self.assertRaises(ValueError):
            validator_evidence(
                frozen,
                self.root / "frozen",
                binding,
                self.check,
                self.check,
                self.observation,
                b"x" * 65537,
                b"",
                environment=EMPTY,
                toolchain=EMPTY,
                credential_free=True,
                network_disabled=True,
                evidence_id="large",
                run_id="run",
                attempt_id="worker",
            )

    def test_private_store_rechecks_real_captures_and_ignores_native_claims(self):
        frozen = self.freeze()
        model = discover(self.source)
        task = Task(
            id="task",
            requirement="Synthetic deterministic capture",
            checks=[self.check],
            review_required=False,
            independent_provider=False,
        )
        binding = self.replace(
            self.binding,
            candidate=record_digest(frozen),
            task=record_digest(task),
            model=model_digest(model),
        )
        with closing(CoordinatorStore(self.root / "state")) as store:
            store.save_project(model, 0)
            store.create_task(task)
            run = Run(id="run", task_id=task.id, binding=binding)
            store.create_run(run, model.project_id)
            store.acquire(run.id, "lease")
            store.owner_approval(
                Approval(
                    id="owner",
                    run_id=run.id,
                    binding=binding,
                    owner="synthetic-owner",
                    reason="Offline fixture",
                )
            )
            intent = self.replace(self.attempt, binding=binding, state="intent", handle=None)
            store.launch_intent(intent, "lease")
            acknowledged = self.replace(intent, state="acknowledged", handle="synthetic:owned")
            store.record_attempt(acknowledged, 1, "lease")
            outcome = normalize_codex(
                acknowledged,
                binding,
                self.identity,
                self.observation,
                stream(*events()),
                b"",
                expected_configuration=EMPTY,
            )
            store.record_attempt(outcome.attempt, 2, "lease")
            for claim in outcome.claims:
                store.record_claim(claim)
            store.transition(run.id, 1, "frozen", "lease")
            self.assertEqual(
                store.verdict(run.id, model.project_id, binding, "lease").status, "blocked"
            )
            evidence = validator_evidence(
                frozen,
                self.root / "frozen",
                binding,
                self.check,
                self.check,
                self.observation,
                b"actual captured bytes",
                b"",
                environment=EMPTY,
                toolchain=EMPTY,
                credential_free=True,
                network_disabled=True,
                evidence_id="check",
                run_id=run.id,
                attempt_id=acknowledged.id,
            )
            with self.assertRaises(ValueError):
                store.capture(evidence, "lease", stdout=b"forged success", stderr=b"")
            store.capture(evidence, "lease", stdout=b"actual captured bytes", stderr=b"")
            scope, raw = scope_evidence(
                frozen,
                frozen,
                binding,
                [],
                evidence_id="scope",
                run_id=run.id,
                attempt_id=acknowledged.id,
                observation=self.observation,
            )
            store.capture(scope, "lease", stdout=raw, stderr=b"")
            store.transition(run.id, 2, "validating", "lease")
            artifact = store.directory / "artifacts" / evidence.stdout
            artifact.write_bytes(b"mutated capture")
            with self.assertRaises(ValueError):
                store.verdict(run.id, model.project_id, binding, "lease")
            artifact.write_bytes(b"actual captured bytes")
            verdict = store.verdict(run.id, model.project_id, binding, "lease")
            self.assertEqual(verdict.status, "verified")
            self.assertFalse(verdict.execution_allowed)

    def test_read_atime_change_does_not_invalidate_unchanged_candidate_bytes(self):
        original_fstat = os.fstat
        count = 0

        def fstat(descriptor):
            nonlocal count
            info = original_fstat(descriptor)
            count += 1
            if count == 2:
                values = {name: getattr(info, name) for name in dir(info) if name.startswith("st_")}
                values["st_atime"] += 1
                values["st_atime_ns"] += 1000000000
                return SimpleNamespace(**values)
            return info

        with patch("crewshal.candidate.os.fstat", side_effect=fstat):
            prepare_candidate(self.source, self.candidate, ["dirty.txt"])
        self.assertEqual((self.candidate / "dirty.txt").read_bytes(), b"uncommitted original\n")

    def test_remaining_capture_and_required_configuration_refusals(self):
        self.assertEqual(self.normalize(exit_code=None).status, "incomplete_capture")
        self.assertEqual(
            self.normalize(stream(*events()).rstrip(b"\n")).status, "incomplete_capture"
        )
        missing = normalize_codex(
            self.attempt, self.binding, self.identity, self.observation, stream(*events()), b""
        )
        self.assertEqual(missing.status, "stale")
        limit = normalize_codex(
            self.attempt,
            self.binding,
            self.identity,
            self.observation,
            stream(*events()),
            b"x" * 65537,
            expected_configuration=EMPTY,
        )
        self.assertEqual(limit.status, "capture_limit")
        long_id = self.replace(self.attempt, id="x" * 256)
        outcome = normalize_codex(
            long_id,
            self.binding,
            self.identity,
            self.observation,
            stream(*events()),
            b"",
            expected_configuration=EMPTY,
        )
        self.assertEqual(outcome.status, "completed")
        self.assertTrue(all(len(claim.id) <= 256 for claim in outcome.claims))
