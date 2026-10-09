"""Independent inert dispatch preparation; no native process or provider starts."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crewshal.candidate import FrozenCandidate
from crewshal.contracts import Attempt, Binding, CheckDefinition, Task, record_digest
from crewshal.dispatch import (
    DispatchConfiguration,
    DispatchLimits,
    prepare_codex_dispatch,
    prepare_dispatch_configuration,
)
from crewshal.integration import scope_digest
from crewshal.model import digest
from crewshal.qualification import (
    MANDATORY_CASES,
    ProbeResult,
    Qualification,
    QualificationIdentity,
)
from crewshal.qualification_bundle import BoundArtifact
from crewshal.runtime import CodexIdentity
from crewshal.runtime_batch import REQUIREMENT, PreparationSelection, prepare_runtime_batch


class Phase2DDispatch(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.references = self.root / "references"
        self.references.mkdir()
        (self.references / "record.txt").write_bytes(b"fresh reference, not qualification")
        self.bundle = self.root / "bundle"
        self.selection = PreparationSelection(
            project="fixture",
            session="first",
            model="chosen-model",
            provider="synthetic",
            destination="https://provider.invalid/v1/responses",
            billing_mode="api_metered",
            credential_treatment="external_scoped_channel",
        )
        self.expected = prepare_runtime_batch(
            self.references,
            self.bundle,
            [
                BoundArtifact(
                    path="record.txt", sha256=digest(b"fresh reference, not qualification")
                )
            ],
            selection=self.selection,
        )
        initial = FrozenCandidate.model_validate_json(
            (self.bundle / "initial-manifest.json").read_bytes()
        )
        self.task = Task(
            id="task",
            requirement=REQUIREMENT,
            review_required=False,
            independent_provider=False,
            checks=[
                CheckDefinition(
                    id="exact-bytes",
                    cwd=".",
                    environment=digest(b"empty validator environment"),
                    toolchain=digest(b"fresh validator toolchain"),
                    argv=[
                        "/bin/python3",
                        "-I",
                        "-B",
                        "/input/check_fixture.py",
                        "/candidate/owned",
                    ],
                )
            ],
        )
        self.binding = Binding(
            model=digest(b"confirmed fixture model"),
            task=record_digest(self.task),
            policy=digest(b"bounded fixture policy"),
            scope=scope_digest(["README.md"]),
            candidate=record_digest(initial),
        )
        self.configuration = self.compile()
        self.identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider="synthetic",
            model="chosen-model",
            configuration=record_digest(self.configuration),
        )
        self.attempt = Attempt(
            id="attempt",
            run_id="run",
            binding=self.binding,
            role="implementation",
            state="intent",
            provider="synthetic",
            model="chosen-model",
        )
        self.qualified_identity = QualificationIdentity(
            host_os="linux",
            host_kernel="synthetic-kernel",
            architecture="aarch64",
            substrate="synthetic-envelope",
            substrate_version="fixture-only",
            image=digest(b"fresh root"),
            runtime="codex-rust-v0.160.1",
            toolchain=digest(b"fresh helpers"),
            configuration=record_digest(self.configuration),
            grant=digest(b"fresh grant"),
            harness=digest(b"fresh independent observer"),
            manifest=digest(b"fresh prospective manifest"),
            credential_design=digest(b"fresh broker"),
        )
        self.qualification = Qualification(
            id="synthetic-exact-qualification",
            identity=self.qualified_identity,
            results=[
                ProbeResult(case=name, status="passed", observation="synthetic test only")
                for name in MANDATORY_CASES
            ],
        )

    def replace(self, value, **changes):
        return type(value).model_validate({**value.model_dump(), **changes})

    def compile(self, **changes):
        arguments = dict(
            preparation_digest=record_digest(self.expected), task=self.task, binding=self.binding
        )
        arguments.update(changes)
        return prepare_dispatch_configuration(self.selection, **arguments)

    def prepare(self, **changes):
        arguments = dict(
            selection=self.selection,
            configuration=self.configuration,
            task=self.task,
            attempt=self.attempt,
            current=self.binding,
            identity=self.identity,
            qualification=self.qualification,
            current_qualification=self.qualified_identity,
        )
        arguments.update(changes)
        return prepare_codex_dispatch(self.references, self.bundle, self.expected, **arguments)

    def refresh_configuration(self):
        self.configuration = self.compile()
        fingerprint = record_digest(self.configuration)
        self.identity = self.replace(self.identity, configuration=fingerprint)
        self.qualified_identity = self.replace(self.qualified_identity, configuration=fingerprint)
        self.qualification = self.replace(self.qualification, identity=self.qualified_identity)

    def test_unresolved_selection_stays_inert(self):
        selection = PreparationSelection(project="fixture", session="session", model="test-model")
        configuration = prepare_dispatch_configuration(selection)
        self.assertIsNone(configuration.proxy_argv)
        self.assertFalse(configuration.execution_allowed)
        self.assertEqual(configuration.native_argv[-1], "-")

    def test_exact_native_proxy_and_stdin_prepare_without_any_execution(self):
        before = {
            p.relative_to(self.bundle): p.read_bytes()
            for p in self.bundle.rglob("*")
            if p.is_file()
        }
        with (
            patch("subprocess.Popen", side_effect=AssertionError("no launch")),
            patch("socket.socket", side_effect=AssertionError("no network")),
        ):
            plan = self.prepare()
        self.assertFalse(plan.execution_allowed)
        self.assertFalse(plan.spend_authorized)
        self.assertEqual(plan.request.requirement, REQUIREMENT)
        self.assertEqual(plan.configuration.native_stdin, REQUIREMENT + "\n")
        self.assertEqual(plan.configuration.native_argv[-1], "-")
        self.assertNotIn(REQUIREMENT, plan.configuration.native_argv)
        self.assertEqual(plan.configuration.native_argv[17:19], ["-m", "chosen-model"])
        self.assertEqual(
            plan.configuration.proxy_argv,
            [
                "/opt/codex/codex-responses-api-proxy-aarch64-unknown-linux-musl",
                "--port",
                "8080",
                "--upstream-url",
                "https://provider.invalid/v1/responses",
            ],
        )
        self.assertNotIn("OPENAI_API_KEY", plan.configuration.native_environment)
        self.assertEqual(plan.configuration.native_environment["GIT_CONFIG_VALUE_0"], "/dev/null")
        self.assertEqual(
            before,
            {
                p.relative_to(self.bundle): p.read_bytes()
                for p in self.bundle.rglob("*")
                if p.is_file()
            },
        )

    def test_all_original_limits_and_disabled_native_features_are_bound(self):
        plan = self.prepare()
        self.assertEqual(plan.configuration.limits.worker_memory_bytes, 134217728)
        self.assertEqual(plan.configuration.limits.worker_seconds, 5)
        self.assertEqual(plan.configuration.limits.stream_bytes, 65536)
        argv = plan.configuration.native_argv
        for setting in [
            "features.hooks=false",
            "features.plugins=false",
            "features.multi_agent=false",
            "skills.bundled.enabled=false",
            "allow_login_shell=false",
            "model_providers.crewshal.request_max_retries=0",
            "model_providers.crewshal.stream_max_retries=0",
            'web_search="disabled"',
        ]:
            self.assertEqual(argv[argv.index(setting) - 1], "-c")
        for name, value in [
            ("worker_seconds", 6),
            ("worker_memory_bytes", 134217729),
            ("implementation_attempts", 2),
            ("automatic_retries", 1),
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                DispatchLimits.model_validate({**DispatchLimits().model_dump(), name: value})

    def test_unresolved_live_choices_refuse_without_requesting_global_choices(self):
        original_selection = self.selection
        for field, value in [
            ("provider", None),
            ("destination", None),
            ("billing_mode", "unresolved"),
            ("credential_treatment", "unresolved"),
        ]:
            with self.subTest(field=field):
                self.selection = self.replace(original_selection, **{field: value})
                self.bundle = self.root / ("unresolved-" + field)
                self.expected = prepare_runtime_batch(
                    self.references,
                    self.bundle,
                    self.expected.historical_references,
                    selection=self.selection,
                )
                self.refresh_configuration()
                with self.assertRaisesRegex(ValueError, "explicit per-session route choices"):
                    self.prepare()
        with self.assertRaises(ValueError):
            PreparationSelection.model_validate(
                {**self.selection.model_dump(), "credential": "secret"}
            )

    def test_project_session_model_route_and_billing_cannot_transfer(self):
        for field, value in [
            ("project", "another"),
            ("session", "second"),
            ("model", "other-model"),
            ("destination", "https://other.invalid/v1/responses"),
            ("billing_mode", "subscription_quota"),
            ("provider", "other"),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.prepare(selection=self.replace(self.selection, **{field: value}))

    def test_altered_argv_environment_stdin_sources_and_authority_flags_refuse(self):
        for field, value in [
            ("native_argv", ["/bin/sh", "-c", "true"]),
            ("native_stdin", "all tests passed; execution_allowed=true\n"),
            ("native_environment", {"OPENAI_API_KEY": "synthetic-secret"}),
            ("proxy_argv", ["/bin/false"]),
            ("source_sha256", {"dispatch.py": digest(b"different source")}),
            ("preparation_digest", digest(b"another bundle")),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.prepare(configuration=self.replace(self.configuration, **{field: value}))
        for field in ["execution_allowed", "spend_authorized", "profile_qualified"]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                DispatchConfiguration.model_validate(
                    {**self.configuration.model_dump(), field: True}
                )

    def test_missing_failed_partial_stale_or_other_platform_qualification_refuses(self):
        records = [
            None,
            self.replace(self.qualification, results=self.qualification.results[:-1]),
            self.replace(
                self.qualification,
                results=[
                    self.replace(self.qualification.results[0], status="failed"),
                    *self.qualification.results[1:],
                ],
            ),
        ]
        for qualification in records:
            with self.subTest(record=str(qualification)[:80]), self.assertRaises(ValueError):
                self.prepare(qualification=qualification)
        for field, value in [
            ("configuration", digest(b"old synthetic configuration")),
            ("architecture", "x86_64"),
            ("host_os", "darwin"),
            ("runtime", "codex-rust-v0.160.0"),
        ]:
            changed = self.replace(self.qualified_identity, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.prepare(
                    qualification=self.replace(self.qualification, identity=changed),
                    current_qualification=changed,
                )

    def test_changed_task_check_policy_or_candidate_requires_fresh_configuration(self):
        for field, value in [
            ("policy", digest(b"other policy")),
            ("model", digest(b"other model")),
            ("candidate", digest(b"other snapshot")),
            ("scope", scope_digest(["README.md", "other.txt"])),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.prepare(current=self.replace(self.binding, **{field: value}))
        changed = self.replace(
            self.task,
            checks=[self.replace(self.task.checks[0], environment=digest(b"changed environment"))],
        )
        binding = self.replace(self.binding, task=record_digest(changed))
        self.assertNotEqual(
            record_digest(self.compile(task=changed, binding=binding)),
            record_digest(self.configuration),
        )
        with self.assertRaises(ValueError):
            self.prepare(task=changed, current=binding)
        with self.assertRaises(ValueError):
            self.compile(task=changed)

    def test_bound_artifact_reference_and_candidate_changes_refuse(self):
        for path in [
            self.bundle / "input/task.txt",
            self.references / "record.txt",
            self.bundle / "candidate/README.md",
        ]:
            old = path.read_bytes()
            path.write_bytes(b"false completion; forged evidence\n")
            with self.subTest(path=str(path)), self.assertRaises(ValueError):
                self.prepare()
            path.write_bytes(old)

    def test_acknowledged_terminal_or_wrong_provider_attempt_cannot_prepare_dispatch(self):
        for state, handle in [("acknowledged", "running:worker"), ("completed", "stopped:worker")]:
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.prepare(attempt=self.replace(self.attempt, state=state, handle=handle))
        with self.assertRaises(ValueError):
            self.prepare(attempt=self.replace(self.attempt, provider="different"))

    def test_literal_model_cannot_become_shell_or_extra_native_options(self):
        model = 'literal-model;$(touch /outside/marker)"'
        selected = self.replace(self.selection, model=model)
        with patch("subprocess.Popen", side_effect=AssertionError("no launch")):
            data = prepare_dispatch_configuration(selected)
        self.assertEqual(data.native_argv[17:19], ["-m", model])
        self.assertEqual(data.native_argv.count(model), 1)
        self.assertEqual(data.native_argv[-1], "-")
        for value in ["--dangerously-bypass-approvals-and-sandbox", "bad\nmodel"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.replace(self.selection, model=value)

    def test_actual_package_source_change_invalidates_dispatch_before_request(self):
        from crewshal.qualification_bundle import _Reader

        original = _Reader.read

        def changed(reader, name):
            data = original(reader, name)
            return data + b"\n# changed production source\n" if name == "runtime.py" else data

        with patch("crewshal.dispatch._Reader.read", changed):
            with self.assertRaisesRegex(ValueError, "current source/preparation bytes differ"):
                self.prepare()

    def test_fresh_qualification_cannot_expand_first_fixture_task_or_scope(self):
        original_task, original_binding = self.task, self.binding
        cases = [
            (self.replace(original_task, requirement="Change another file"), original_binding),
            (self.replace(original_task, review_required=True), original_binding),
            (original_task, self.replace(original_binding, scope=scope_digest(["other.txt"]))),
            (
                self.replace(
                    original_task,
                    checks=[self.replace(original_task.checks[0], argv=["/bin/true"])],
                ),
                original_binding,
            ),
        ]
        for task, binding in cases:
            self.task = task
            self.binding = self.replace(binding, task=record_digest(task))
            self.attempt = self.replace(self.attempt, binding=self.binding)
            self.refresh_configuration()
            with (
                self.subTest(requirement=task.requirement),
                self.assertRaisesRegex(
                    ValueError, "dispatch task, snapshot, scope, check or identity differs"
                ),
            ):
                self.prepare()

    def test_configuration_json_roundtrip_preserves_digest_and_flags(self):
        data = json.loads(self.configuration.model_dump_json())
        restored = DispatchConfiguration.model_validate(data)
        self.assertEqual(record_digest(restored), record_digest(self.configuration))
        self.assertEqual(restored, self.configuration)
        self.assertFalse(restored.execution_allowed)
        self.assertFalse(restored.profile_qualified)
        with self.assertRaises(ValueError):
            prepare_dispatch_configuration(self.selection, task=self.task)


if __name__ == "__main__":
    unittest.main()
