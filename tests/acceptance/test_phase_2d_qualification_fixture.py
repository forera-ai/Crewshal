"""Offline wire tests do not establish native Linux qualification."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest

from crewshal.linux_qualification_fixture import (
    FiniteQualificationResponses,
    FrozenQualificationFixture,
    FrozenQualificationTLS,
    RetainedSyntheticExclusions,
    _http_request,
    decode_zstd_request,
    qualification_probe_source,
    verify_native_probe_output,
)


def _tools() -> list[dict[str, object]]:
    return [
        {"type": "function", "name": "exec_command", "parameters": {}},
        {"type": "function", "name": "write_stdin", "parameters": {}},
        {"type": "custom", "name": "apply_patch", "format": {}},
        {"type": "function", "name": "view_image", "parameters": {}},
    ]


def _plan() -> FrozenQualificationFixture:
    return FrozenQualificationFixture(
        configuration="a" * 64,
        model="gpt-5.3-codex",
        probe_sha256=hashlib.sha256(qualification_probe_source()).hexdigest(),
        expected_file_tools=["exec_command", "write_stdin", "apply_patch", "view_image"],
        synthetic_nonce="b" * 32,
        candidate_marker_bytes={
            "README.md": "phase-2d-after\n",
            "existing": "phase2d-modified\n",
            "new": "phase2d-created\n",
            "patch-positive": "phase2d\n",
        },
        scratch_marker_bytes={
            "existing": "phase2d-modified\n",
            "new": "phase2d-created\n",
            "patch-positive": "phase2d\n",
        },
    )


def _body(outputs: dict[str, object], tools: list[dict[str, object]] | None = None) -> bytes:
    return json.dumps(
        {
            "model": "gpt-5.3-codex",
            "stream": True,
            "tools": tools if tools is not None else _tools(),
            "input": [
                {"type": "function_call_output", "call_id": call, "output": output}
                for call, output in outputs.items()
            ],
        }
    ).encode()


def _items(sse: bytes) -> list[dict[str, object]]:
    return [
        json.loads(line[6:])["item"]
        for line in sse.splitlines()
        if line.startswith(b"data: ")
        and json.loads(line[6:])["type"] == "response.output_item.done"
    ]


def _complete_output() -> str:
    filesystem = {"read-" + str(index): True for index in range(8)}
    filesystem.update(
        {
            name: True
            for name in (
                "storage-file-shared",
                "storage-private-anonymous",
                "storage-anonymous-shared-denied",
                "storage-dev-zero-denied",
                "storage-memfd-denied",
            )
        }
    )
    filesystem.update(
        {
            operation + "-" + str(index): True
            for operation in ("write", "chmod", "unlink", "rename", "link")
            for index in range(9)
        }
    )
    filesystem.update({"create-" + str(index): True for index in range(7)})
    filesystem.update(
        {
            "instructions-" + operation + "-" + name: True
            for operation in ("empty", "write", "unlink")
            for name in ("AGENTS.md", "AGENTS.override.md")
        }
    )
    network = {name: True for name in ("tcp", "udp", "dns", "ipv6")}
    environment = {
        name: True
        for name in (
            "PHASE2D_PARENT_SECRET",
            "SSH_AUTH_SOCK",
            "OPENAI_API_KEY",
            "BASH_ENV",
            "ENV",
            "PYTHONSTARTUP",
            "GIT_CONFIG",
            "GIT_CONFIG_SYSTEM",
            "/run/phase2d-ssh-agent",
            "/var/run/docker.sock",
            "/root/.codex/auth.json",
            "/home/owner/.codex/auth.json",
            "/native-auth/auth.json",
            "/native-auth/config.toml",
        )
    }
    report = {
        "filesystem": filesystem,
        "network": network,
        "environment": environment,
        "hooks-exit": 0,
        "descendant": {"filesystem": filesystem, "network": network},
        "phase2d_complete": True,
    }
    return "Process exited with code 0\n" + json.dumps(report, separators=(",", ":"))


class QualificationFixtureTests(unittest.TestCase):
    def test_actual_report_refuses_missing_failed_and_coerced_observations(self) -> None:
        verified = verify_native_probe_output(_complete_output())
        self.assertIs(verified["phase2d_complete"], True)
        for value in (False, 1, None):
            report = json.loads(_complete_output().split("\n", 1)[1])
            report["filesystem"]["read-0"] = value
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "failed or remains unknown"),
            ):
                verify_native_probe_output("Process exited with code 0\n" + json.dumps(report))
        with self.assertRaisesRegex(ValueError, "report remains unknown"):
            verify_native_probe_output("Process exited with code 0\n{}")

    def test_mapping_and_shared_memory_results_are_required_for_both_processes(self) -> None:
        for actor in ("parent", "descendant"):
            for name in (
                "storage-file-shared",
                "storage-private-anonymous",
                "storage-anonymous-shared-denied",
                "storage-dev-zero-denied",
                "storage-memfd-denied",
            ):
                for value in (False, None):
                    report = json.loads(_complete_output().split("\n", 1)[1])
                    observed = (
                        report["filesystem"]
                        if actor == "parent"
                        else report["descendant"]["filesystem"]
                    )
                    if value is None:
                        del observed[name]
                    else:
                        observed[name] = value
                    with (
                        self.subTest(actor=actor, name=name, value=value),
                        self.assertRaises(ValueError),
                    ):
                        verify_native_probe_output(
                            "Process exited with code 0\n" + json.dumps(report)
                        )

    def test_private_native_authentication_paths_require_actual_denial(self) -> None:
        for name in ("/native-auth/auth.json", "/native-auth/config.toml"):
            for value in (False, None):
                report = json.loads(_complete_output().split("\n", 1)[1])
                if value is None:
                    del report["environment"][name]
                else:
                    report["environment"][name] = value
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    verify_native_probe_output("Process exited with code 0\n" + json.dumps(report))

    def test_fixed_tls_plan_refuses_live_and_duplicate_listener_routes(self) -> None:
        values = {
            "fixture": _plan(),
            "certificate_sha256": "c" * 64,
            "private_key_sha256": "d" * 64,
            "zstd_library_sha256": "e" * 64,
            "listener_addresses": {
                "qualification-1": ("10.203.0.1", 443),
                "qualification-2": ("10.203.1.1", 443),
            },
            "peer_addresses": {"qualification-1": "10.203.0.2", "qualification-2": "10.203.1.2"},
            "bootstrap_replies": {
                "/backend-api/wham/usage": "{}",
                "/backend-api/codex/models?client_version=0.160.1": "{}",
            },
        }
        FrozenQualificationTLS.model_validate(values)
        values["listener_addresses"] = {
            "qualification-1": ("10.203.0.1", 443),
            "live": ("10.203.1.1", 443),
        }
        with self.assertRaisesRegex(ValueError, "qualification listeners"):
            FrozenQualificationTLS.model_validate(values)

    def test_http_parser_refuses_smuggling_and_nonstock_routes(self) -> None:
        class MemoryChannel:
            def __init__(self, raw: bytes) -> None:
                self.raw = raw

            def settimeout(self, remaining: float) -> None:
                if remaining <= 0:
                    raise ValueError("expired")

            def recv(self, maximum: int) -> bytes:
                result, self.raw = self.raw[:maximum], self.raw[maximum:]
                return result

        for headers in (
            b"POST /other HTTP/1.1\r\nHost: chatgpt.com\r\nContent-Length: 2",
            b"POST /backend-api/codex/responses HTTP/1.1\r\nHost: other.example\r\nContent-Length: 2",
            b"POST /backend-api/codex/responses HTTP/1.1\r\nHost: chatgpt.com\r\nContent-Length: 2\r\nContent-Length: 2",
            b"POST /backend-api/codex/responses HTTP/1.1\r\nHost: chatgpt.com\r\nContent-Length: 2\r\nTransfer-Encoding: chunked",
        ):
            with self.subTest(headers=headers), self.assertRaises(ValueError):
                _http_request(MemoryChannel(headers + b"\r\n\r\n{}"), time.monotonic() + 1)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "compressed fixture request"):
            decode_zstd_request(b"x" * 65537, -1)

    def test_parent_readback_detects_modified_bytes_mode_and_new_files(self) -> None:
        for change in ("bytes", "mode", "new"):
            with tempfile.TemporaryDirectory() as location:
                root = Path(location)
                handles = {}
                for name in ("outside", "original", "coordinator", "input", "host-home"):
                    (root / name).mkdir()
                    (root / name / "canary").write_bytes(b"synthetic only")
                    handles[name] = os.open(root / name, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    retained = RetainedSyntheticExclusions(handles, time.monotonic())
                    retained.verify_unchanged()
                    target = root / "outside" / "canary"
                    if change == "bytes":
                        target.write_bytes(b"changed")
                    elif change == "mode":
                        target.chmod(0o777)
                    else:
                        (root / "outside" / "new").write_bytes(b"escape")
                    with self.assertRaisesRegex(ValueError, "inventory changed"):
                        retained.verify_unchanged()
                finally:
                    for handle in handles.values():
                        os.close(handle)

    def test_probe_source_is_current_and_syntactically_complete(self) -> None:
        compile(qualification_probe_source(), "/input/phase-2d-probe.py", "exec")
        values = _plan().model_dump()
        values["probe_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "exact current source"):
            FrozenQualificationFixture.model_validate(values)

    def test_both_fixed_cursors_invoke_all_actual_enabled_file_tools_once(self) -> None:
        fixture = FiniteQualificationResponses(_plan(), time.monotonic())
        for lane in ("qualification-1", "qualification-2"):
            auth = fixture.synthetic_authorization(lane)
            first = _items(fixture.respond(lane, "/backend-api/codex/responses", auth, _body({})))
            self.assertEqual([item["name"] for item in first], ["exec_command"])
            outputs: dict[str, object] = {
                lane + "-entry": "Process running with session ID 719\nphase2d-entry"
            }
            second = _items(
                fixture.respond(lane, "/backend-api/codex/responses", auth, _body(outputs))
            )
            self.assertEqual(
                {item["name"] for item in second}, {"write_stdin", "apply_patch", "view_image"}
            )
            self.assertEqual(json.loads(str(second[0]["arguments"]))["session_id"], 719)
            self.assertEqual(sum(item["type"] == "custom_tool_call" for item in second), 9)
            outputs.update({str(item["call_id"]): "denied" for item in second})
            outputs[lane + "-stdin"] = _complete_output()
            third = _items(
                fixture.respond(lane, "/backend-api/codex/responses", auth, _body(outputs))
            )
            self.assertEqual([item["type"] for item in third], ["message"])
        record = json.loads(fixture.captured())
        self.assertEqual(set(record["outputs"]), {"qualification-1", "qualification-2"})
        with self.assertRaisesRegex(ValueError, "origin differs"):
            fixture.respond("qualification-1", "/backend-api/codex/responses", auth, _body({}))

    def test_refusal_consumes_lane_and_cannot_retry(self) -> None:
        fixture = FiniteQualificationResponses(_plan(), time.monotonic())
        lane = "qualification-1"
        auth = fixture.synthetic_authorization(lane)
        with self.assertRaisesRegex(ValueError, "synthetic authentication"):
            fixture.respond(
                lane, "/backend-api/codex/responses", "Bearer real-shaped-token", _body({})
            )
        with self.assertRaisesRegex(ValueError, "cannot reset"):
            fixture.respond(lane, "/backend-api/codex/responses", auth, _body({}))

    def test_live_lane_and_unreviewed_catalog_are_refused(self) -> None:
        fixture = FiniteQualificationResponses(_plan(), time.monotonic())
        with self.assertRaisesRegex(ValueError, "live lane"):
            fixture.synthetic_authorization("live")
        with self.assertRaisesRegex(ValueError, "synthetic authentication"):
            fixture.respond("live", "/backend-api/codex/responses", "", _body({}))
        with self.assertRaisesRegex(ValueError, "unreviewed native"):
            fixture.respond(
                "qualification-1",
                "/backend-api/codex/responses",
                fixture.synthetic_authorization("qualification-1"),
                _body({}, _tools() + [{"type": "function", "name": "unreviewed_file_tool"}]),
            )

    def test_changed_catalog_missing_output_and_duplicate_json_refuse(self) -> None:
        for mode in ("changed", "missing", "duplicate"):
            fixture = FiniteQualificationResponses(_plan(), time.monotonic())
            lane = "qualification-1"
            auth = fixture.synthetic_authorization(lane)
            fixture.respond(lane, "/backend-api/codex/responses", auth, _body({}))
            if mode == "changed":
                tools = _tools()
                tools[0]["description"] = "changed"
                body = _body({lane + "-entry": "Process running with session ID 7"}, tools)
            elif mode == "missing":
                body = _body({})
            else:
                body = b'{"model":"gpt-5.3-codex","model":"gpt-5.3-codex"}'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                fixture.respond(lane, "/backend-api/codex/responses", auth, body)

    def test_partial_or_forged_origin_capture_cannot_complete(self) -> None:
        fixture = FiniteQualificationResponses(_plan(), time.monotonic())
        with self.assertRaisesRegex(ValueError, "finish once"):
            fixture.captured()
        fixture.origin -= 1
        with self.assertRaisesRegex(ValueError, "origin differs"):
            fixture.respond(
                "qualification-1",
                "/backend-api/codex/responses",
                fixture.synthetic_authorization("qualification-1"),
                _body({}),
            )

    def test_original_request_and_capture_bounds_refuse_excess(self) -> None:
        fixture = FiniteQualificationResponses(_plan(), time.monotonic())
        with self.assertRaisesRegex(ValueError, "request bound"):
            fixture.respond(
                "qualification-1",
                "/backend-api/codex/responses",
                fixture.synthetic_authorization("qualification-1"),
                b" " * 65537,
            )
