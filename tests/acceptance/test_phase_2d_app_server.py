"""Offline finite exchange checks; synthetic messages confer no execution authority."""

import json
import unittest

from crewshal.app_server import (
    MAX_PROTOCOL_BYTES,
    MAX_PROTOCOL_EVENTS,
    AppServerExchange,
    AppServerProfile,
    AppServerProtocolError,
    SUBSCRIPTION_PERMISSIONS,
    SUBSCRIPTION_STARTUP_SETTINGS,
    _leaves,
)


def line(value):
    return json.dumps(value).encode() + b"\n"


def config():
    result = {}
    for path, value in SUBSCRIPTION_STARTUP_SETTINGS.items():
        keys = path.split(".")
        target = result
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = json.loads(json.dumps(value))
    return result


def config_response():
    settings = config()
    metadata = {"name": {"type": "sessionFlags"}, "version": "opaque-test-version"}
    return {
        "config": settings,
        "origins": {key: metadata for key in _leaves(config())},
        "layers": [dict(metadata, config=settings)],
    }


def profile():
    return AppServerProfile(
        model="gpt-6.1-sol",
        requirement="Produce the fixed artifact.",
        account_reference="a" * 64,
        expected_account={"type": "chatgpt", "email": None, "planType": "plus"},
        codex_home="/native-auth",
        thread_params={
            "model": "gpt-6.1-sol",
            "modelProvider": "openai",
            "cwd": "/candidate/owned",
            "approvalPolicy": "never",
            "ephemeral": True,
            "config": {},
        },
        permission_profile=SUBSCRIPTION_PERMISSIONS,
        expected_config=config(),
        expected_thread={
            "model": "gpt-6.1-sol",
            "modelProvider": "openai",
            "cwd": "/candidate/owned",
            "approvalPolicy": "never",
            "approvalsReviewer": "user",
            "sandbox": {
                "type": "workspaceWrite",
                "writableRoots": ["/scratch"],
                "networkAccess": False,
                "excludeSlashTmp": True,
                "excludeTmpdirEnvVar": True,
            },
        },
    )


def thread():
    return {
        "id": "thread-1",
        "modelProvider": "openai",
        "cwd": "/candidate/owned",
        "ephemeral": True,
        "turns": [],
        "cliVersion": "0.160.1",
        "createdAt": 0,
        "updatedAt": 0,
        "preview": "",
        "projectId": None,
        "sessionId": "session-1",
        "source": "appServer",
        "status": {"type": "idle"},
    }


def turn(status="inProgress", identity="turn-1"):
    return {"id": identity, "items": [], "status": status, "error": None}


def response(exchange, identity, result):
    return exchange.feed(line({"id": identity, "result": result}))


def notification(exchange, method, params):
    return exchange.feed(line({"method": method, "params": params}))


def to_thread(exchange):
    exchange.start()
    response(
        exchange,
        1,
        {
            "codexHome": "/native-auth",
            "platformFamily": "unix",
            "platformOs": "linux",
            "userAgent": "codex/0.160.1",
        },
    )
    response(exchange, 2, config_response())
    response(exchange, 3, {"account": profile().expected_account, "requiresOpenaiAuth": True})
    response(
        exchange, 4, {"rateLimits": {"primary": {"usedPercent": 25}}, "ordinaryUsageAllowed": None}
    )


def to_turn(exchange):
    to_thread(exchange)
    response(exchange, 5, dict(profile().expected_thread, thread=thread()))


class AppServerTests(unittest.TestCase):
    def test_six_fixed_requests_and_one_initialized_notification(self):
        exchange = AppServerExchange.from_profile(profile())
        output = [json.loads(exchange.start())]
        output.extend(
            map(
                json.loads,
                response(
                    exchange,
                    1,
                    {
                        "codexHome": "/native-auth",
                        "platformFamily": "unix",
                        "platformOs": "linux",
                        "userAgent": "codex/0.160.1",
                    },
                ),
            )
        )
        output.extend(map(json.loads, response(exchange, 2, config_response())))
        output.extend(
            map(
                json.loads,
                response(
                    exchange,
                    3,
                    {
                        "account": profile().expected_account,
                        "requiresOpenaiAuth": True,
                    },
                ),
            )
        )
        output.extend(map(json.loads, response(exchange, 4, {"rateLimits": {}})))
        output.extend(
            map(
                json.loads,
                response(
                    exchange,
                    5,
                    dict(
                        profile().expected_thread,
                        thread=thread(),
                    ),
                ),
            )
        )
        response(exchange, 6, {"turn": turn()})
        self.assertEqual([value["id"] for value in output if "id" in value], [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            [value["method"] for value in output],
            [
                "initialize",
                "initialized",
                "config/read",
                "account/read",
                "account/rateLimits/read",
                "thread/start",
                "turn/start",
            ],
        )
        self.assertEqual(output[3]["params"], {"refreshToken": False})
        self.assertEqual(
            output[-1]["params"],
            {
                "threadId": "thread-1",
                "input": [{"type": "text", "text": profile().requirement}],
            },
        )
        self.assertFalse(exchange.protocol_completed)
        notification(
            exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
        )
        self.assertTrue(exchange.protocol_completed)
        self.assertFalse(hasattr(exchange, "process_success"))

    def test_notifications_before_response_bind_and_reconcile(self):
        exchange = AppServerExchange(profile())
        to_thread(exchange)
        notification(exchange, "thread/started", {"thread": thread()})
        response(exchange, 5, dict(profile().expected_thread, thread=thread()))
        notification(exchange, "turn/started", {"threadId": "thread-1", "turn": turn()})
        notification(
            exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
        )
        self.assertFalse(exchange.protocol_completed)
        response(exchange, 6, {"turn": turn()})
        self.assertTrue(exchange.protocol_completed)

    def test_provisional_foreign_turn_refused(self):
        exchange = AppServerExchange(profile())
        to_turn(exchange)
        notification(exchange, "turn/started", {"threadId": "thread-1", "turn": turn()})
        with self.assertRaises(AppServerProtocolError):
            response(exchange, 6, {"turn": turn(identity="foreign")})

    def test_replay_errors_server_requests_and_ids_refused_terminally(self):
        for message in (
            {"id": 1, "error": {"code": -1}},
            {"id": 1, "method": "item/commandExecution/requestApproval", "params": {}},
            {"id": True, "result": {}},
            {"id": "1", "result": {}},
            {"id": 2, "result": {}},
        ):
            with self.subTest(message=message):
                exchange = AppServerExchange(profile())
                exchange.start()
                with self.assertRaises(AppServerProtocolError):
                    exchange.feed(line(message))
                with self.assertRaises(AppServerProtocolError):
                    exchange.start()

    def test_duplicate_nan_invalid_utf8_and_partial_lines_refused(self):
        for raw in (
            b'{"id":1,"id":1,"result":{}}\n',
            b'{"id":1,"result":{"n":NaN}}\n',
            b"\xff\n",
            b"{}",
            b"{}\n{}\n",
        ):
            with self.subTest(raw=raw):
                exchange = AppServerExchange(profile())
                exchange.start()
                with self.assertRaises(AppServerProtocolError):
                    exchange.feed(raw)

    def test_exact_home_and_thread_controls(self):
        exchange = AppServerExchange(profile())
        exchange.start()
        with self.assertRaises(AppServerProtocolError):
            response(
                exchange,
                1,
                {
                    "codexHome": "/ambient",
                    "platformFamily": "unix",
                    "platformOs": "linux",
                    "userAgent": "codex",
                },
            )
        for key, value in (
            ("model", "other"),
            ("sandbox", {"type": "dangerFullAccess"}),
            ("approvalPolicy", "on-request"),
        ):
            with self.subTest(key=key):
                exchange = AppServerExchange(profile())
                to_thread(exchange)
                result = dict(profile().expected_thread, thread=thread())
                result[key] = value
                with self.assertRaises(AppServerProtocolError):
                    response(exchange, 5, result)

    def test_metadata_not_unique_identity_quota_account_optional(self):
        exchange = AppServerExchange(profile())
        to_thread(exchange)  # Missing unique account ID remains unknown, not fabricated.
        self.assertFalse(hasattr(exchange, "account_identity_verified"))
        data = profile().model_dump()
        data["expected_account_id"] = "trusted-reference"
        exchange = AppServerExchange(AppServerProfile.model_validate(data))
        exchange.start()
        response(
            exchange,
            1,
            {
                "codexHome": "/native-auth",
                "platformFamily": "unix",
                "platformOs": "linux",
                "userAgent": "codex",
            },
        )
        response(exchange, 2, config_response())
        response(exchange, 3, {"account": profile().expected_account, "requiresOpenaiAuth": True})
        with self.assertRaises(AppServerProtocolError):
            response(exchange, 4, {"rateLimits": {}})

    def test_profile_mutation_refused(self):
        parameters = profile()
        exchange = AppServerExchange(parameters)
        parameters.thread_params["cwd"] = "/foreign"
        with self.assertRaises(AppServerProtocolError):
            exchange.start()

    def test_config_read_refuses_disabled_foreign_or_unknown_origins(self):
        for fault in ("missing_origin", "foreign", "disabled", "version", "policy", "bool"):
            with self.subTest(fault=fault):
                exchange = AppServerExchange(profile())
                exchange.start()
                response(
                    exchange,
                    1,
                    {
                        "codexHome": "/native-auth",
                        "platformFamily": "unix",
                        "platformOs": "linux",
                        "userAgent": "codex",
                    },
                )
                result = config_response()
                if fault == "missing_origin":
                    del result["origins"]["default_permissions"]
                elif fault == "foreign":
                    result["origins"]["default_permissions"] = {
                        "name": {"type": "user", "file": "/ambient/config.toml"},
                        "version": "opaque-test-version",
                    }
                elif fault == "disabled":
                    result["layers"][0]["disabledReason"] = "not trusted"
                elif fault == "version":
                    result["layers"][0]["version"] = "different"
                elif fault == "policy":
                    result["config"]["permissions"]["crewshal"]["filesystem"]["/native-auth"] = (
                        "read"
                    )
                else:
                    result["config"]["model_providers"]["openai"]["request_max_retries"] = False
                with self.assertRaises(AppServerProtocolError):
                    response(exchange, 2, result)

    def test_turn_cannot_complete_before_request(self):
        exchange = AppServerExchange(profile())
        to_thread(exchange)
        with self.assertRaises(AppServerProtocolError):
            notification(
                exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
            )

    def test_repeated_delta_text_is_data_not_replayed_lifecycle(self):
        exchange = AppServerExchange(profile())
        to_turn(exchange)
        response(exchange, 6, {"turn": turn()})
        data = {"threadId": "thread-1", "turnId": "turn-1", "itemId": "i", "delta": "same"}
        notification(exchange, "item/agentMessage/delta", data)
        notification(exchange, "item/agentMessage/delta", data)
        notification(
            exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
        )
        self.assertTrue(exchange.protocol_completed)

    def test_unfinished_items_and_unsupported_terminal_context_refused(self):
        for fault in ("unfinished", "unsupported", "no_start"):
            with self.subTest(fault=fault):
                exchange = AppServerExchange(profile())
                to_turn(exchange)
                response(exchange, 6, {"turn": turn()})
                params = {
                    "threadId": "thread-1",
                    "turnId": "turn-1",
                    "item": {"id": "item-1", "type": "reasoning"},
                }
                if fault == "unfinished":
                    notification(exchange, "item/started", dict(params, startedAtMs=0))
                terminal = turn("completed")
                if fault == "unsupported":
                    terminal["items"] = [{"id": "item-1", "type": "mcpToolCall"}]
                with self.assertRaises(AppServerProtocolError):
                    if fault == "no_start":
                        notification(exchange, "item/completed", dict(params, completedAtMs=0))
                    else:
                        notification(
                            exchange, "turn/completed", {"threadId": "thread-1", "turn": terminal}
                        )

    def test_permission_table_preserves_helper_path_without_home_read_grant(self):
        filesystem = SUBSCRIPTION_PERMISSIONS["filesystem"]
        self.assertNotIn("/native-auth", filesystem)
        self.assertEqual(filesystem["/native-auth/auth.json"], "deny")
        self.assertEqual(filesystem["/native-auth/config.toml"], "deny")
        self.assertIsInstance(
            SUBSCRIPTION_STARTUP_SETTINGS["permissions.crewshal.filesystem"], dict
        )
        self.assertNotIn(
            "permissions.crewshal.filesystem./native-auth/auth.json", SUBSCRIPTION_STARTUP_SETTINGS
        )

    def test_auth_recovery_cannot_overlap_or_leave_completion_pending(self):
        for fault in ("duplicate", "completion"):
            with self.subTest(fault=fault):
                exchange = AppServerExchange(profile())
                to_turn(exchange)
                response(exchange, 6, {"turn": turn()})
                params = {
                    "threadId": "thread-1",
                    "turnId": "turn-1",
                    "provider": "OpenAI",
                    "message": "recovery",
                }
                notification(exchange, "modelProvider/authRecoveryStarted", params)
                with self.assertRaises(AppServerProtocolError):
                    if fault == "duplicate":
                        notification(exchange, "modelProvider/authRecoveryStarted", params)
                    else:
                        notification(
                            exchange,
                            "turn/completed",
                            {"threadId": "thread-1", "turn": turn("completed")},
                        )

    def test_unrestricted_or_contradictory_profile_refused(self):
        for change in ("danger", "override", "extra", "cwd"):
            data = profile().model_dump()
            if change == "danger":
                data["expected_thread"]["sandbox"] = {"type": "dangerFullAccess"}
            elif change == "override":
                data["thread_params"]["sandbox"] = "read-only"
            elif change == "cwd":
                data["thread_params"]["cwd"] = "/native-auth"
                data["expected_thread"]["cwd"] = "/native-auth"
            else:
                data["thread_params"]["dynamicTools"] = []
            with self.assertRaises(ValueError):
                AppServerProfile.model_validate(data)

    def test_message_and_byte_bounds(self):
        exchange = AppServerExchange(profile())
        exchange.start()
        with self.assertRaises(AppServerProtocolError):
            exchange.feed(b" " * MAX_PROTOCOL_BYTES + b"\n")
        exchange = AppServerExchange(profile())
        to_thread(exchange)
        for _ in range(MAX_PROTOCOL_EVENTS - 4):
            notification(exchange, "warning", {"message": "x"})
        with self.assertRaises(AppServerProtocolError):
            notification(exchange, "warning", {"message": "x"})

    def test_completion_does_not_accept_extra_data_or_failed_turn(self):
        exchange = AppServerExchange(profile())
        to_turn(exchange)
        response(exchange, 6, {"turn": turn()})
        notification(
            exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
        )
        with self.assertRaises(AppServerProtocolError):
            notification(
                exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
            )
        self.assertFalse(exchange.protocol_completed)
        exchange = AppServerExchange(profile())
        to_turn(exchange)
        with self.assertRaises(AppServerProtocolError):
            notification(
                exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("failed")}
            )

    def test_finite_auth_recovery_pairs_do_not_cap_per_turn_requests(self):
        exchange = AppServerExchange(profile())
        to_turn(exchange)
        response(exchange, 6, {"turn": turn()})
        params = {
            "threadId": "thread-1",
            "turnId": "turn-1",
            "provider": "OpenAI",
            "message": "recovery",
        }
        for _ in range(4):
            notification(exchange, "modelProvider/authRecoveryStarted", params)
            notification(exchange, "modelProvider/authRecoveryCompleted", params)
        notification(
            exchange, "turn/completed", {"threadId": "thread-1", "turn": turn("completed")}
        )
        self.assertTrue(exchange.protocol_completed)

    def test_foreign_or_unsupported_tool_notifications_refused(self):
        for method, params in (
            (
                "item/agentMessage/delta",
                {"threadId": "foreign", "turnId": "turn-1", "itemId": "i", "delta": "x"},
            ),
            (
                "item/started",
                {
                    "threadId": "thread-1",
                    "turnId": "turn-1",
                    "item": {"id": "i", "type": "mcpToolCall"},
                },
            ),
            ("model/rerouted", {"threadId": "thread-1", "turnId": "turn-1"}),
        ):
            with self.subTest(method=method):
                exchange = AppServerExchange(profile())
                to_turn(exchange)
                with self.assertRaises(AppServerProtocolError):
                    notification(exchange, method, params)


if __name__ == "__main__":
    unittest.main()
