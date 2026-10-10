"""Fresh subscription preparation/terminal fixtures, never live qualification."""

import json
from datetime import datetime, timedelta, timezone
import unittest
import tomllib
from unittest.mock import patch

from crewshal.app_server import AppServerProfile
from crewshal.contracts import record_digest
from crewshal.dispatch import prepare_codex_dispatch, prepare_dispatch_configuration
from crewshal.runtime import CodexIdentity, ProcessObservation, normalize_codex
from crewshal.runtime_batch import PreparationSelection, REQUIREMENT, prepare_runtime_batch
from tests.acceptance import test_phase_2d_app_server as protocol
from tests.acceptance import test_phase_2d_dispatch as fixtures


class SubscriptionPreparation(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Phase2DDispatch("test_unresolved_selection_stays_inert")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        self.selection = PreparationSelection(
            project="fixture",
            session="subscription",
            model="gpt-6.1-sol",
            provider="openai",
            destination="https://subscription.invalid/backend-api/codex",
            billing_mode="subscription_quota",
            credential_treatment="native_managed_private_home",
        )
        draft = prepare_dispatch_configuration(self.selection)
        expected_config = {}
        for index, argument in enumerate(draft.native_argv):
            if argument != "-c":
                continue
            key, raw = draft.native_argv[index + 1].split("=", 1)
            target = expected_config
            parts = key.split(".")
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            target[parts[-1]] = tomllib.loads("value=" + raw)["value"]
        self.profile = AppServerProfile.model_validate(
            {
                **protocol.profile().model_dump(),
                "requirement": REQUIREMENT,
                "expected_account_id": "synthetic-owned-account",
                "expected_config": expected_config,
            }
        )
        self.bundle = f.root / "subscription-bundle"
        self.expected = prepare_runtime_batch(
            f.references, self.bundle, f.expected.historical_references, selection=self.selection
        )
        initial = json.loads((self.bundle / "initial-manifest.json").read_text())
        from crewshal.candidate import FrozenCandidate

        self.binding = f.replace(
            f.binding, candidate=record_digest(FrozenCandidate.model_validate(initial))
        )
        self.configuration = prepare_dispatch_configuration(
            self.selection,
            preparation_digest=record_digest(self.expected),
            task=f.task,
            binding=self.binding,
            app_server_profile=self.profile,
        )
        self.identity = CodexIdentity(
            runtime="codex",
            version="0.160.1",
            provider="openai",
            model=self.selection.model,
            configuration=record_digest(self.configuration),
            native_interface="app_server_stdio",
            app_server_profile=self.profile,
        )
        self.attempt = f.replace(
            f.attempt, binding=self.binding, provider="openai", model=self.selection.model
        )
        self.qualified_identity = f.replace(
            f.qualified_identity, configuration=record_digest(self.configuration)
        )
        self.qualification = f.replace(f.qualification, identity=self.qualified_identity)

    def prepare(self, **changes):
        f = self.fixture
        args = dict(
            selection=self.selection,
            configuration=self.configuration,
            task=f.task,
            attempt=self.attempt,
            current=self.binding,
            identity=self.identity,
            qualification=self.qualification,
            current_qualification=self.qualified_identity,
        )
        return prepare_codex_dispatch(
            f.references, self.bundle, self.expected, **{**args, **changes}
        )

    def test_managed_route_has_no_proxy_key_or_exec_argv(self):
        with patch("subprocess.Popen", side_effect=AssertionError("no native")):
            plan = self.prepare()
        config = plan.configuration
        self.assertEqual(
            config.native_argv[:5],
            ["/opt/codex/bin/codex", "app-server", "--listen", "stdio://", "--strict-config"],
        )
        self.assertEqual(config.native_stdin, "")
        self.assertIsNone(config.proxy_argv)
        self.assertEqual(config.native_environment["CODEX_HOME"], "/native-auth")
        for literal in [
            "features.unbounded_connection_retries=false",
            "model_providers.openai.supports_websockets=false",
            "model_providers.openai.request_max_retries=0",
            "model_providers.openai.stream_max_retries=0",
            'default_permissions="crewshal"',
        ]:
            self.assertIn(literal, config.native_argv)
        filesystem = self.profile.expected_config["permissions"]["crewshal"]["filesystem"]
        self.assertEqual(filesystem["/native-auth/auth.json"], "deny")
        self.assertEqual(filesystem["/native-auth/config.toml"], "deny")
        self.assertNotIn("/native-auth", filesystem)
        for flag in ["exec", "--json", "--ignore-user-config", "--ignore-rules", "-"]:
            self.assertNotIn(flag, config.native_argv)
        self.assertFalse(plan.execution_allowed)
        self.assertFalse(plan.spend_authorized)
        self.assertEqual(config.limits.automatic_retries, 0)

    def test_missing_profile_cannot_prepare_qualified_request(self):
        config = prepare_dispatch_configuration(
            self.selection,
            preparation_digest=record_digest(self.expected),
            task=self.fixture.task,
            binding=self.binding,
        )
        self.assertIsNone(config.app_server_profile)
        self.assertFalse(config.execution_allowed)
        with self.assertRaises(ValueError):
            self.prepare(configuration=config)

    def test_altered_auth_route_profile_or_deadline_refuses(self):
        for setting in [
            next(
                value
                for value in self.configuration.native_argv
                if value.startswith("permissions.crewshal.filesystem=")
            ),
            "features.unbounded_connection_retries=false",
            "model_providers.openai.supports_websockets=false",
        ]:
            argv = list(self.configuration.native_argv)
            argv[argv.index(setting)] = setting.rsplit("=", 1)[0] + "=true"
            with self.subTest(setting=setting), self.assertRaises(ValueError):
                self.prepare(
                    configuration=self.fixture.replace(self.configuration, native_argv=argv)
                )
        changed = AppServerProfile.model_validate(
            {
                **self.profile.model_dump(),
                "account_reference": "b" * 64,
            }
        )
        with self.assertRaises(ValueError):
            self.prepare(identity=self.fixture.replace(self.identity, app_server_profile=changed))

    def test_mismatched_task_and_model_profile_refuse(self):
        with self.assertRaises(ValueError):
            prepare_dispatch_configuration(self.selection, app_server_profile=protocol.profile())
        with self.assertRaises(ValueError):
            prepare_dispatch_configuration(self.fixture.selection, app_server_profile=self.profile)

    def test_metered_or_other_provider_cannot_take_managed_route(self):
        for field, value in [("billing_mode", "api_metered"), ("provider", "other")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prepare_dispatch_configuration(
                    self.fixture.replace(self.selection, **{field: value})
                )

    def test_readback_cannot_omit_a_disabled_native_feature(self):
        data = self.profile.model_dump()
        del data["expected_config"]["features"]["hooks"]
        profile = AppServerProfile.model_validate(data)
        with self.assertRaisesRegex(ValueError, "every startup override"):
            prepare_dispatch_configuration(self.selection, app_server_profile=profile)

    def test_unknown_account_never_prepares_or_completes_runtime(self):
        profile = AppServerProfile.model_validate(
            {
                **self.profile.model_dump(),
                "expected_account_id": None,
            }
        )
        config = prepare_dispatch_configuration(
            self.selection,
            preparation_digest=record_digest(self.expected),
            task=self.fixture.task,
            binding=self.binding,
            app_server_profile=profile,
        )
        identity = self.fixture.replace(
            self.identity, configuration=record_digest(config), app_server_profile=profile
        )
        with self.assertRaisesRegex(ValueError, "bound account identity"):
            self.prepare(configuration=config, identity=identity)
        self.identity = identity
        self.configuration = config
        self.assertEqual(self.normalize().status, "identity_unavailable")

    def transcript(self):
        p = self.profile
        from crewshal.app_server import _leaves

        version = "sha256:" + "a" * 64
        config_read = {
            "config": p.expected_config,
            "origins": {
                key: {"name": {"type": "sessionFlags"}, "version": version}
                for key in _leaves(p.expected_config)
            },
            "layers": [
                {
                    "name": {"type": "sessionFlags"},
                    "version": version,
                    "config": p.expected_config,
                    "disabledReason": None,
                }
            ],
        }
        values = [
            {
                "id": 1,
                "result": {
                    "codexHome": "/native-auth",
                    "platformFamily": "unix",
                    "platformOs": "linux",
                    "userAgent": "codex/0.160.1",
                },
            },
            {"id": 2, "result": config_read},
            {"id": 3, "result": {"account": p.expected_account, "requiresOpenaiAuth": True}},
            {
                "id": 4,
                "result": {
                    "rateLimits": {},
                    "ordinaryUsageAllowed": None,
                    "accountId": "synthetic-owned-account",
                },
            },
            {"id": 5, "result": {**p.expected_thread, "thread": protocol.thread()}},
            {"id": 6, "result": {"turn": protocol.turn()}},
            {
                "method": "turn/completed",
                "params": {"threadId": "thread-1", "turn": protocol.turn("completed")},
            },
        ]
        return b"".join(protocol.line(value) for value in values)

    def normalize(self, stdout=None, **changes):
        now = datetime(2026, 10, 9, tzinfo=timezone.utc)
        observation = ProcessObservation(
            started=now,
            ended=now + timedelta(seconds=1),
            elapsed_seconds=1,
            exit_code=0,
            stdout_complete=True,
            stderr_complete=True,
            tree_stopped=True,
        )
        return normalize_codex(
            self.fixture.replace(self.attempt, state="acknowledged", handle="owned-native"),
            self.binding,
            self.identity,
            self.fixture.replace(observation, **changes),
            self.transcript() if stdout is None else stdout,
            b"",
            expected_configuration=record_digest(self.configuration),
        )

    def test_rpc_completion_requires_actual_terminal_capture(self):
        self.assertEqual(self.normalize().status, "completed")
        for changed in [
            {"exit_code": None},
            {"tree_stopped": False},
            {"stdout_complete": False},
            {"stderr_complete": False},
            {"exit_code": -9},
            {"elapsed_seconds": 5.01},
            {"termination": "timeout"},
        ]:
            with self.subTest(changed=changed):
                self.assertNotEqual(self.normalize(**changed).status, "completed")

    def test_legacy_or_replayed_rpc_never_completes_subscription_capture(self):
        self.assertEqual(
            self.normalize(b'{"type":"thread.started","thread_id":"one"}\n').status, "malformed"
        )
        replay = self.transcript() + protocol.line({"id": 6, "result": {"turn": protocol.turn()}})
        self.assertEqual(self.normalize(replay).status, "malformed")
        self.assertEqual(self.normalize(self.transcript()[:-1]).status, "incomplete_capture")


if __name__ == "__main__":
    unittest.main()
