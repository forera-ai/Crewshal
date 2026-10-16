"""Finite synthetic Responses data for the two original qualification lanes.

The stock native app-server invokes its actual advertised handlers.
This source cannot forward an upstream request or process a live credential.
Captured responses do not replace independent parent or validator evidence.
"""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
import re
import socket
import ssl
import stat
import subprocess
import sys
import time
from array import array
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Literal, NoReturn

if TYPE_CHECKING:
    from crewshal.linux_freeze import OriginalVolumeFreeze
    from crewshal.linux_operational import OriginalInstallationDriver
    from crewshal.linux_setup import OwnedStorageReservation
    from crewshal.linux_inventory import RetainedParentInventory
    from crewshal.linux_parent import RetainedTrustedTask
    from crewshal.linux_installed import RetainedInstalledImages

if __name__ == "__main__":
    # CPython can add this locale after an empty-environment exec.
    if os.environ:
        if (
            sys.platform != "linux"
            or not sys.flags.isolated
            or not sys.flags.no_site
            or not sys.flags.dont_write_bytecode
            or dict(os.environ) != {"LC_CTYPE": "C.UTF-8"}
        ):
            raise ValueError("The isolated entry inherited an environment.")
        with open("/proc/self/environ", "rb") as inherited:
            if inherited.read(1):
                raise ValueError("The isolated entry inherited an environment.")
        del os.environ["LC_CTYPE"]
    if (
        sys.platform != "linux"
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or os.environ
        or sys.argv != ["/opt/crewshal/lib/crewshal/linux_qualification_fixture.py"]
    ):
        raise ValueError("broker requires exact isolated credential-free startup")
    sys.path.insert(0, "/opt/crewshal/lib")

from pydantic import Field, field_validator, model_validator

from crewshal.admission import _wait_ready
from crewshal.contracts import Digest, record_digest
from crewshal.model import Contract
from crewshal.supervisor import OwnedCgroup

QUALIFICATION_LANES = ("qualification-1", "qualification-2")
FILE_TOOLS = frozenset(("exec_command", "write_stdin", "apply_patch", "view_image"))
OTHER_TOOLS = frozenset(("request_user_input",))
REQUEST_BOUND = 65536
CAPTURE_BOUND = 65536
PROBE_PATH = "/input/phase-2d-probe.py"


class FrozenQualificationFixture(Contract):
    """The common plan pins both fixed cursors before the original batch."""

    configuration: Digest
    model: str = Field(min_length=1, max_length=128)
    probe_sha256: Digest
    expected_file_tools: list[Literal["exec_command", "write_stdin", "apply_patch", "view_image"]]
    synthetic_nonce: str = Field(pattern=r"^[a-f0-9]{32}$")
    candidate_marker_bytes: dict[str, str]
    scratch_marker_bytes: dict[str, str]

    @model_validator(mode="after")
    def exact_positive_marker_binding(self) -> "FrozenQualificationFixture":
        candidate = {
            "README.md": "phase-2d-after\n",
            "existing": "phase2d-modified\n",
            "new": "phase2d-created\n",
        }
        scratch = {"existing": "phase2d-modified\n", "new": "phase2d-created\n"}
        if "apply_patch" in self.expected_file_tools:
            candidate["patch-positive"] = "phase2d\n"
            scratch["patch-positive"] = "phase2d\n"
        if self.candidate_marker_bytes != candidate or self.scratch_marker_bytes != scratch:
            raise ValueError(
                "common fixture requires exact declared positive marker paths and bytes"
            )
        return self

    @field_validator("probe_sha256")
    @classmethod
    def current_probe_bytes(cls, value: str) -> str:
        if value != hashlib.sha256(qualification_probe_source()).hexdigest():
            raise ValueError("fixture probe must bind its exact current source bytes")
        return value

    @field_validator("expected_file_tools")
    @classmethod
    def exact_unique_tools(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)) or not {"exec_command", "write_stdin"}.issubset(value):
            raise ValueError("fixed qualification requires exact unique enabled native file tools")
        return value


def _json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate fixture JSON key")
        result[name] = value
    return result


def _request(body: bytes) -> dict[str, object]:
    if not 0 < len(body) <= REQUEST_BOUND:
        raise ValueError("original fixture request bound exceeded")
    value = json.loads(body, object_pairs_hook=_unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("fixture requires one actual request object")
    return value


def _catalog(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, list) or not 0 < len(value) <= 32:
        raise ValueError("actual native tool catalog is missing or exceeds bound")
    result: dict[str, dict[str, object]] = {}
    for tool in value:
        if not isinstance(tool, dict):
            raise ValueError("actual tool catalog entry is malformed")
        # Responses namespaces contain the same concrete native tool entries.
        nested = tool.get("tools") if tool.get("type") == "namespace" else [tool]
        if not isinstance(nested, list):
            raise ValueError("actual native namespace catalog is malformed")
        for item in nested:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ValueError("actual native tool name is missing")
            name = item["name"]
            if name in result or name not in FILE_TOOLS | OTHER_TOOLS:
                raise ValueError("actual catalog contains duplicate or unreviewed native tools")
            if item.get("type") not in ("function", "custom"):
                raise ValueError("actual native file tool wire type is unsupported")
            result[name] = item
    return result


def _output_items(value: dict[str, object]) -> dict[str, object]:
    items = value.get("input")
    if not isinstance(items, list) or len(items) > 256:
        raise ValueError("actual native response input is missing or exceeds bound")
    result = {}
    for item in items:
        if not isinstance(item, dict) or item.get("type") not in (
            "function_call_output",
            "custom_tool_call_output",
        ):
            continue
        call = item.get("call_id")
        if not isinstance(call, str) or call in result or "output" not in item:
            raise ValueError("actual native call output identity is malformed")
        if len(_json(item["output"])) > 8192:
            raise ValueError("actual native call output exceeds original capture bound")
        result[call] = item["output"]
    return result


def _strings(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_strings(item) for item in value)
    if isinstance(value, dict):
        return "\n".join(_strings(item) for item in value.values())
    return ""


def verify_native_probe_output(output: object) -> dict[str, object]:
    """Require the actual complete native output and every fixed negative observation."""
    text = _strings(output)
    if "Process exited with code 0" not in text:
        raise ValueError("actual qualification probe terminal exit remains unknown")
    reports = []
    for line in text.splitlines():
        if line.startswith("{"):
            try:
                value = json.loads(line, object_pairs_hook=_unique_pairs)
            except ValueError:
                continue
            if isinstance(value, dict) and "phase2d_complete" in value:
                reports.append(value)
    if len(reports) != 1:
        raise ValueError("actual complete native qualification report remains unknown")
    report = reports[0]
    filesystem_keys = {
        "storage-file-shared",
        "storage-private-anonymous",
        "storage-anonymous-shared-denied",
        "storage-dev-zero-denied",
        "storage-memfd-denied",
        *("read-" + str(index) for index in range(8)),
        *(
            operation + "-" + str(index)
            for operation in ("write", "chmod", "unlink", "rename", "link")
            for index in range(9)
        ),
        *("create-" + str(index) for index in range(7)),
        *(
            "instructions-" + operation + "-" + name
            for operation in ("empty", "write", "unlink")
            for name in ("AGENTS.md", "AGENTS.override.md")
        ),
    }
    network_keys = {"tcp", "udp", "dns", "ipv6"}
    environment_keys = {
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
    }
    if set(report) != {
        "filesystem",
        "network",
        "environment",
        "hooks-exit",
        "descendant",
        "phase2d_complete",
    }:
        raise ValueError("actual qualification report cases differ")
    descendant = report["descendant"]
    if not isinstance(descendant, dict) or set(descendant) != {"filesystem", "network"}:
        raise ValueError("actual detached descendant observations remain unknown")
    for observed, expected in (
        (report["filesystem"], filesystem_keys),
        (report["network"], network_keys),
        (report["environment"], environment_keys),
        (descendant["filesystem"], filesystem_keys),
        (descendant["network"], network_keys),
    ):
        if (
            not isinstance(observed, dict)
            or set(observed) != expected
            or any(value is not True for value in observed.values())
        ):
            raise ValueError(
                "actual native qualification denied operation failed or remains unknown"
            )
    if (
        report["phase2d_complete"] is not True
        or type(report["hooks-exit"]) is not int
        or report["hooks-exit"] != 0
    ):
        raise ValueError("actual qualification hook or completion observation differs")
    return report


def _call(name: str, identity: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "type": "function_call",
        "id": identity,
        "call_id": identity,
        "name": name,
        "arguments": _json(arguments).decode(),
    }


def _patch_call(
    catalog: dict[str, dict[str, object]], identity: str, patch: str
) -> dict[str, object]:
    if catalog["apply_patch"]["type"] == "custom":
        return {
            "type": "custom_tool_call",
            "id": identity,
            "call_id": identity,
            "name": "apply_patch",
            "input": patch,
        }
    return _call("apply_patch", identity, {"patch": patch})


def _sse(identity: str, model: str, items: list[dict[str, object]], terminal: bool) -> bytes:
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": identity, "model": model}}
    ]
    for index, item in enumerate(items):
        events += [
            {"type": "response.output_item.added", "output_index": index, "item": item},
            {"type": "response.output_item.done", "output_index": index, "item": item},
        ]
    events.append(
        {
            "type": "response.completed",
            "response": {
                "id": identity,
                "model": model,
                "status": "completed",
                "output": items,
                "end_turn": terminal,
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            },
        }
    )
    result = b"".join(
        b"event: " + str(event["type"]).encode() + b"\ndata: " + _json(event) + b"\n\n"
        for event in events
    )
    if len(result) > CAPTURE_BOUND:
        raise ValueError("fixed fixture response exceeds original output bound")
    return result


class FiniteQualificationResponses:
    """Each immutable lane consumes exactly three original stock-provider requests."""

    def __init__(self, plan: FrozenQualificationFixture, original_origin: float) -> None:
        if not 0 < original_origin <= time.monotonic() < original_origin + 570:
            raise ValueError("original fixture batch origin is missing or expired")
        self.plan = FrozenQualificationFixture.model_validate_json(plan.model_dump_json())
        self._plan_digest = record_digest(self.plan)
        self.origin = original_origin
        self._origin = original_origin
        self.cursors = {lane: 0 for lane in QUALIFICATION_LANES}
        self.catalog: bytes | None = None
        self.outputs: dict[str, dict[str, object]] = {lane: {} for lane in QUALIFICATION_LANES}
        self.sent_calls: dict[str, tuple[str, ...]] = {lane: () for lane in QUALIFICATION_LANES}
        self.failed_lanes: set[str] = set()

    def synthetic_authorization(self, lane: str) -> str:
        if lane not in QUALIFICATION_LANES:
            raise ValueError("fixture refuses live lane and real authentication")
        return "Bearer crewshal-phase2d-synthetic-" + lane + "-" + self.plan.synthetic_nonce

    def respond(self, lane: str, path: str, authorization: str, body: bytes) -> bytes:
        if lane in self.failed_lanes:
            raise ValueError("original fixture refusal cannot reset its consumed cursor")
        try:
            return self._respond(lane, path, authorization, body)
        except BaseException:
            if lane in QUALIFICATION_LANES:
                self.failed_lanes.add(lane)
            raise

    def _respond(self, lane: str, path: str, authorization: str, body: bytes) -> bytes:
        if (
            lane not in QUALIFICATION_LANES
            or path != "/backend-api/codex/responses"
            or authorization != self.synthetic_authorization(lane)
            or record_digest(self.plan) != self._plan_digest
            or self.origin != self._origin
            or time.monotonic() >= self.origin + 570
            or self.cursors[lane] >= 3
        ):
            raise ValueError(
                "fixture lane, stock endpoint, synthetic authentication, or origin differs"
            )
        value = _request(body)
        if value.get("model") != self.plan.model or value.get("stream") is not True:
            raise ValueError("actual stock-provider model or streaming mode differs")
        catalog = _catalog(value.get("tools"))
        if set(catalog) & FILE_TOOLS != set(self.plan.expected_file_tools):
            raise ValueError("actual enabled file tools differ from frozen reviewed policy")
        catalog_bytes = _json(value["tools"])
        if len(catalog_bytes) > 32768:
            raise ValueError("actual enabled native catalog exceeds original capture bound")
        if self.catalog is None:
            if lane != "qualification-1":
                raise ValueError("original first qualification catalog is missing")
            self.catalog = catalog_bytes
        elif self.catalog != catalog_bytes:
            raise ValueError("actual native tool catalog differs between original requests")
        output = _output_items(value)
        if not set(self.sent_calls[lane]).issubset(output) or not set(output).issubset(
            set(self.outputs[lane]) | set(self.sent_calls[lane])
        ):
            raise ValueError("actual previous native handler outputs remain unknown")
        # Retain actual native outputs. They are data, not admission authority.
        self.outputs[lane].update(output)
        if len(_json(self.outputs)) + len(catalog_bytes) + 4096 > CAPTURE_BOUND:
            raise ValueError("actual native output capture exceeds original shared bound")
        index = self.cursors[lane]
        self.cursors[lane] += 1
        if index == 0:
            items = [
                _call(
                    "exec_command",
                    lane + "-entry",
                    {
                        "cmd": "/bin/python3 -I -B " + PROBE_PATH + " entry && exec /bin/sh",
                        "tty": True,
                        "yield_time_ms": 1,
                        "max_output_tokens": 256,
                    },
                )
            ]
        elif index == 1:
            text = _strings(output[lane + "-entry"])
            matches = re.findall(r"Process running with session ID ([0-9]+)", text)
            if len(matches) != 1:
                raise ValueError("actual original exec_command session remains unknown")
            items = [
                _call(
                    "write_stdin",
                    lane + "-stdin",
                    {
                        "session_id": int(matches[0]),
                        "chars": "exec /bin/python3 -I -B " + PROBE_PATH + " workload\n",
                        "yield_time_ms": 1000,
                        "max_output_tokens": 2048,
                    },
                )
            ]
            if "apply_patch" in catalog:
                for number, target in enumerate(
                    (
                        "/candidate/owned/patch-positive",
                        "/scratch/patch-positive",
                        "/outside/patch-denied",
                        "/original/patch-denied",
                        "/coordinator/patch-denied",
                        "/input/patch-denied",
                        "/scratch/absolute-parent/patch-denied",
                        "/scratch/relative-parent/patch-denied",
                        "/candidate/owned/../patch-denied",
                    )
                ):
                    patch = "*** Begin Patch\n*** Add File: " + target + "\n+phase2d\n*** End Patch"
                    items.append(_patch_call(catalog, lane + "-patch-" + str(number), patch))
            if "view_image" in catalog:
                for number, target in enumerate(
                    (
                        "/input/positive.png",
                        "/outside/positive.png",
                        "/coordinator/positive.png",
                        "/scratch/absolute-image",
                        "/scratch/relative-image",
                    )
                ):
                    items.append(
                        _call("view_image", lane + "-image-" + str(number), {"path": target})
                    )
        else:
            verify_native_probe_output(output[lane + "-stdin"])
            items = [
                {
                    "type": "message",
                    "id": lane + "-complete",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "Phase 2D fixture complete."}],
                }
            ]
        self.sent_calls[lane] = tuple(str(item["call_id"]) for item in items if "call_id" in item)
        return _sse(lane + "-response-" + str(index), self.plan.model, items, index == 2)

    def captured(self) -> bytes:
        if self.failed_lanes or self.cursors != {lane: 3 for lane in QUALIFICATION_LANES}:
            raise ValueError("both original qualification fixture cursors must finish once")
        result = _json(
            {
                "plan": self._plan_digest,
                "catalog_sha256": hashlib.sha256(self.catalog or b"").hexdigest(),
                "catalog": json.loads(self.catalog or b"null"),
                "outputs": self.outputs,
                "origin": self._origin,
            }
        )
        if len(result) > CAPTURE_BOUND:
            raise ValueError("complete fixture evidence exceeds original capture bound")
        return result


class FrozenQualificationTLS(Contract):
    """Both qualification listeners use one pinned synthetic stock-host certificate."""

    fixture: FrozenQualificationFixture
    certificate_sha256: Digest
    private_key_sha256: Digest
    zstd_library_sha256: Digest
    listener_addresses: dict[str, tuple[str, int]]
    peer_addresses: dict[str, str]
    bootstrap_replies: dict[str, str]

    @field_validator("bootstrap_replies")
    @classmethod
    def fixed_stock_bootstrap_replies(cls, value: dict[str, str]) -> dict[str, str]:
        if set(value) != {
            "/backend-api/wham/usage",
            "/backend-api/codex/models?client_version=0.160.1",
        }:
            raise ValueError("both exact pinned stock bootstrap endpoints required")
        for reply in value.values():
            if not 0 < len(reply.encode()) <= REQUEST_BOUND:
                raise ValueError("fixed stock bootstrap reply exceeds original bound")
            if not isinstance(json.loads(reply, object_pairs_hook=_unique_pairs), dict):
                raise ValueError("fixed stock bootstrap reply requires one JSON object")
        return value

    @field_validator("listener_addresses")
    @classmethod
    def two_fixed_tls_addresses(
        cls, value: dict[str, tuple[str, int]]
    ) -> dict[str, tuple[str, int]]:
        if set(value) != set(QUALIFICATION_LANES) or len(set(value.values())) != 2:
            raise ValueError("original fixture requires two distinct fixed qualification listeners")
        for address, port in value.values():
            if (
                port != 443
                or socket.inet_ntop(socket.AF_INET, socket.inet_pton(socket.AF_INET, address))
                != address
            ):
                raise ValueError("original fixture requires canonical fixed IPv4 TLS addresses")
        return value

    @field_validator("peer_addresses")
    @classmethod
    def two_fixed_peers(cls, value: dict[str, str]) -> dict[str, str]:
        if set(value) != set(QUALIFICATION_LANES) or len(set(value.values())) != 2:
            raise ValueError("original fixture requires two distinct fixed qualification peers")
        for address in value.values():
            if (
                socket.inet_ntop(socket.AF_INET, socket.inet_pton(socket.AF_INET, address))
                != address
            ):
                raise ValueError("original fixture requires canonical fixed IPv4 peers")
        return value


def _readonly_file(descriptor: int, expected: str, bound: int) -> None:
    before = os.fstat(descriptor)
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or (before.st_uid, before.st_gid) != (0, 0)
        or before.st_mode & 0o022
        or not 0 < before.st_size <= bound
        or not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY
    ):
        raise ValueError("fixture requires its actual pinned readonly original file")
    raw = os.pread(descriptor, before.st_size + 1, 0)
    after = os.fstat(descriptor)
    fields = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_uid",
        "st_gid",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    if (
        len(raw) != before.st_size
        or hashlib.sha256(raw).hexdigest() != expected
        or any(getattr(before, field) != getattr(after, field) for field in fields)
    ):
        raise ValueError("fixture readonly source bytes or original identity changed")


def decode_zstd_request(body: bytes, library_fd: int) -> bytes:
    """Use the retained reviewed library with fixed compressed and decoded bounds."""
    import ctypes

    if not 0 < len(body) <= REQUEST_BOUND:
        raise ValueError("compressed fixture request exceeds original bound")
    library = ctypes.CDLL("/proc/self/fd/" + str(library_fd))
    library.ZSTD_decompress.argtypes = (
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_size_t,
    )
    library.ZSTD_decompress.restype = ctypes.c_size_t
    library.ZSTD_isError.argtypes = (ctypes.c_size_t,)
    library.ZSTD_isError.restype = ctypes.c_uint
    destination = ctypes.create_string_buffer(REQUEST_BOUND)
    source = ctypes.create_string_buffer(body)
    length = library.ZSTD_decompress(destination, REQUEST_BOUND, source, len(body))
    if library.ZSTD_isError(length) or not 0 < length <= REQUEST_BOUND:
        raise ValueError("decoded fixture request is malformed or exceeds original bound")
    return destination.raw[:length]


def _http_request(channel: ssl.SSLSocket, deadline: float) -> tuple[str, dict[str, str], bytes]:
    received = bytearray()
    while b"\r\n\r\n" not in received:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("original fixture connection deadline exhausted")
        channel.settimeout(remaining)
        chunk = channel.recv(16385 - len(received))
        if not chunk:
            raise ValueError("original fixture HTTP headers remain incomplete")
        received.extend(chunk)
        if len(received) > 16384:
            raise ValueError("original fixture HTTP headers exceed bound")
    raw_headers, raw_body = bytes(received).split(b"\r\n\r\n", 1)
    lines = raw_headers.decode("ascii").split("\r\n")
    method, _, endpoint = lines[0].partition(" ")
    endpoint, _, protocol = endpoint.partition(" ")
    if protocol != "HTTP/1.1" or (method, endpoint) not in (
        ("POST", "/backend-api/codex/responses"),
        ("GET", "/backend-api/wham/usage"),
        ("GET", "/backend-api/codex/models?client_version=0.160.1"),
    ):
        raise ValueError("fixture permits only the fixed stock HTTPS Responses endpoint")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        name, separator, value = line.partition(":")
        name = name.lower()
        if not separator or name in headers or not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("original fixture HTTP header identity differs")
        headers[name] = value.strip()
    length = headers.get("content-length", "0" if method == "GET" else "")
    if (
        headers.get("host") != "chatgpt.com"
        or not re.fullmatch(r"[0-9]{1,5}", length)
        or not (
            0 <= int(length) <= REQUEST_BOUND
            if method == "GET"
            else 0 < int(length) <= REQUEST_BOUND
        )
        or (method == "GET" and int(length) != 0)
        or "transfer-encoding" in headers
        or len(raw_body) > int(length)
    ):
        raise ValueError("original stock HTTPS authority or request length differs")
    received = bytearray(raw_body)
    while len(received) < int(length):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("original fixture body deadline exhausted")
        channel.settimeout(remaining)
        chunk = channel.recv(int(length) - len(received))
        if not chunk:
            raise ValueError("original fixture HTTP body remains incomplete")
        received.extend(chunk)
    return endpoint, headers, bytes(received)


def serve_qualification_tls(
    plan: FrozenQualificationTLS,
    original_origin: float,
    broker: OwnedCgroup,
    listeners: dict[str, socket.socket],
    certificate_fd: int,
    private_key_fd: int,
    zstd_library_fd: int,
    progress_fd: int,
    *,
    ready_callback: Callable[[], None] | None = None,
) -> bytes:
    """Serve six finite synthetic requests in the original bounded broker process."""
    plan = FrozenQualificationTLS.model_validate_json(plan.model_dump_json())
    if type(broker) is not OwnedCgroup or set(listeners) != set(QUALIFICATION_LANES):
        raise ValueError("original broker and both retained fixture listeners required")
    broker._verify()
    if (
        broker._read("memory.max") != "67108864"
        or broker._read("pids.max") != "16"
        or broker._read("memory.swap.max") != "0"
        or broker._read("cpu.max") != "100000 100000"
    ):
        raise ValueError("original broker limits differ")
    proc = os.open("/proc/self", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        descriptor = os.open("cgroup", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=proc)
        try:
            if (
                os.read(descriptor, 65537).strip()
                != ("0::/" + broker.identity.relative_path).encode()
            ):
                raise ValueError("original fixture process is outside its retained broker role")
        finally:
            os.close(descriptor)
    finally:
        os.close(proc)
    _readonly_file(certificate_fd, plan.certificate_sha256, 65536)
    _readonly_file(private_key_fd, plan.private_key_sha256, 65536)
    _readonly_file(zstd_library_fd, plan.zstd_library_sha256, 2097152)
    pipe_info = os.fstat(progress_fd)
    if (
        not stat.S_ISFIFO(pipe_info.st_mode)
        or fcntl.fcntl(progress_fd, fcntl.F_GETFL) & os.O_ACCMODE != os.O_WRONLY
    ):
        raise ValueError("original fixture progress requires its retained write pipe")
    progress_identity = (pipe_info.st_dev, pipe_info.st_ino)
    os.set_blocking(progress_fd, False)
    progress_bytes = 0
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_alpn_protocols(["http/1.1"])
    context.load_cert_chain(
        "/proc/self/fd/" + str(certificate_fd), "/proc/self/fd/" + str(private_key_fd)
    )
    # Load the exact retained decoder before independent mapped-file admission.
    import ctypes

    decoder = ctypes.CDLL("/proc/self/fd/" + str(zstd_library_fd))
    if not decoder.ZSTD_decompress or not decoder.ZSTD_isError:
        raise ValueError("original fixture decoder symbols remain unknown")
    fixture = FiniteQualificationResponses(plan.fixture, original_origin)
    consumed_bootstrap: dict[str, set[str]] = {lane: set() for lane in QUALIFICATION_LANES}
    originals = {}
    for lane, listener in listeners.items():
        if (
            type(listener) is not socket.socket
            or listener.family != socket.AF_INET
            or listener.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_STREAM
            or listener.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) != 1
            or listener.getsockname() != plan.listener_addresses[lane]
        ):
            raise ValueError("original fixture listener identity or frozen address differs")
        info = os.fstat(listener.fileno())
        originals[lane] = (listener.fileno(), info.st_dev, info.st_ino)
    if ready_callback is not None:
        ready_callback()
    while fixture.cursors != {lane: 3 for lane in QUALIFICATION_LANES}:
        remaining = original_origin + 570 - time.monotonic()
        if remaining <= 0:
            raise ValueError("original fixture batch cutoff exhausted")
        pending = [listeners[lane] for lane in QUALIFICATION_LANES if fixture.cursors[lane] < 3]
        ready = _wait_ready(pending, [], [], min(remaining, 0.05))[0]
        for listener in ready:
            lane = next(name for name, value in listeners.items() if value is listener)
            info = os.fstat(listener.fileno())
            if originals[lane] != (listener.fileno(), info.st_dev, info.st_ino):
                raise ValueError("original fixture listener FD changed")
            connection, peer = listener.accept()
            try:
                if peer[0] != plan.peer_addresses[lane]:
                    raise ValueError("fixture refuses an unbound or live peer")
                connection_deadline = min(original_origin + 570, time.monotonic() + 0.5)
                connection.settimeout(max(0.001, connection_deadline - time.monotonic()))
                with context.wrap_socket(connection, server_side=True) as channel:
                    path, headers, body = _http_request(channel, connection_deadline)
                    if headers.get("authorization") != fixture.synthetic_authorization(lane):
                        raise ValueError("fixture refuses real or unbound authentication")
                    if path in plan.bootstrap_replies:
                        if path in consumed_bootstrap[lane] or body or fixture.cursors[lane]:
                            raise ValueError(
                                "original stock bootstrap request consumed or misplaced"
                            )
                        consumed_bootstrap[lane].add(path)
                        response = plan.bootstrap_replies[path].encode()
                        content_type = b"application/json"
                    else:
                        encoding = headers.get("content-encoding", "identity")
                        if encoding == "zstd":
                            body = decode_zstd_request(body, zstd_library_fd)
                        elif encoding != "identity":
                            raise ValueError("stock fixture request encoding is unsupported")
                        response = fixture.respond(lane, path, headers["authorization"], body)
                        content_type = b"text/event-stream"
                    channel.sendall(
                        b"HTTP/1.1 200 OK\r\nContent-Type: " + content_type + b"\r\n"
                        b"Connection: close\r\nContent-Length: "
                        + str(len(response)).encode()
                        + b"\r\n\r\n"
                        + response
                    )
                    if fixture.cursors[lane] == 3 and path == "/backend-api/codex/responses":
                        info = os.fstat(progress_fd)
                        if (info.st_dev, info.st_ino) != progress_identity:
                            raise ValueError("original fixture progress pipe changed")
                        record = (
                            _json(
                                {
                                    "lane": lane,
                                    "plan": record_digest(plan),
                                    "fixture": fixture._plan_digest,
                                    "catalog_sha256": hashlib.sha256(
                                        fixture.catalog or b""
                                    ).hexdigest(),
                                    "catalog": json.loads(fixture.catalog or b"null")
                                    if lane == "qualification-1"
                                    else None,
                                    "outputs": fixture.outputs[lane],
                                    "bootstrap": sorted(consumed_bootstrap[lane]),
                                    "origin": original_origin,
                                }
                            )
                            + b"\n"
                        )
                        if progress_bytes + len(record) > CAPTURE_BOUND:
                            raise ValueError(
                                "original fixture combined progress capture exceeds bound"
                            )
                        offset = 0
                        while offset < len(record):
                            remaining = original_origin + 570 - time.monotonic()
                            if remaining <= 0:
                                raise ValueError("original fixture progress deadline exhausted")
                            if _wait_ready([], [progress_fd], [], min(remaining, 0.01))[1]:
                                offset += os.write(progress_fd, record[offset:])
                        progress_bytes += len(record)
            finally:
                connection.close()
    return fixture.captured()


def _synthetic_tree(descriptor: int) -> dict[str, tuple[object, ...]]:
    """Read an original synthetic directory without following its escape links."""
    root = os.fstat(descriptor)
    result: dict[str, tuple[object, ...]] = {}

    def visit(directory: int, prefix: str, depth: int) -> None:
        if depth > 4:
            raise ValueError("synthetic fixture directory depth exceeds original bound")
        names = sorted(os.listdir(directory))
        if len(names) + len(result) > 128:
            raise ValueError("synthetic fixture inode inventory exceeds original bound")
        for name in names:
            if not name or "/" in name or name in (".", ".."):
                raise ValueError("synthetic fixture directory name is malformed")
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if info.st_dev != root.st_dev:
                raise ValueError("synthetic fixture contains a foreign mount")
            path = prefix + name
            identity = (
                info.st_dev,
                info.st_ino,
                info.st_mode,
                info.st_uid,
                info.st_gid,
                info.st_nlink,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
            )
            if stat.S_ISREG(info.st_mode):
                if info.st_size > 65536 or info.st_nlink != 1:
                    raise ValueError("synthetic fixture file exceeds bound or has an alias")
                handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
                try:
                    raw = os.pread(handle, info.st_size + 1, 0)
                    observed = os.fstat(handle)
                    after = (
                        observed.st_dev,
                        observed.st_ino,
                        observed.st_mode,
                        observed.st_uid,
                        observed.st_gid,
                        observed.st_nlink,
                        observed.st_size,
                        observed.st_mtime_ns,
                        observed.st_ctime_ns,
                    )
                    if len(raw) != info.st_size or after != identity:
                        raise ValueError("synthetic fixture original file read differs")
                    result[path] = (*identity, hashlib.sha256(raw).hexdigest())
                finally:
                    os.close(handle)
            elif stat.S_ISDIR(info.st_mode):
                result[path] = identity
                handle = os.open(
                    name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=directory,
                )
                try:
                    visit(handle, path + "/", depth + 1)
                finally:
                    os.close(handle)
            elif stat.S_ISLNK(info.st_mode):
                target = os.readlink(name, dir_fd=directory)
                if len(target.encode()) > 4096:
                    raise ValueError("synthetic fixture link target exceeds bound")
                result[path] = (*identity, target)
            else:
                raise ValueError(
                    "synthetic fixture requires files, directories, and retained links"
                )

    visit(descriptor, "", 0)
    return result


class RetainedSyntheticExclusions:
    """The original parent independently checks synthetic excluded bytes and metadata."""

    def __init__(self, directories: dict[str, int], original_origin: float) -> None:
        if set(directories) != {"outside", "original", "coordinator", "input", "host-home"}:
            raise ValueError("complete original synthetic exclusions required")
        if not 0 < original_origin <= time.monotonic() < original_origin + 570:
            raise ValueError("original synthetic fixture origin is missing or expired")
        self.origin = self._origin = original_origin
        self.directories = dict(directories)
        self._directories = dict(directories)
        self.identities = {
            name: (os.fstat(handle).st_dev, os.fstat(handle).st_ino)
            for name, handle in directories.items()
        }
        self.before = {name: _synthetic_tree(handle) for name, handle in directories.items()}
        self._before = _json(self.before)

    def verify_unchanged(self) -> None:
        if (
            self.origin != self._origin
            or self.directories != self._directories
            or _json(self.before) != self._before
            or time.monotonic() >= self.origin + 570
        ):
            raise ValueError("original synthetic exclusion custody or deadline differs")
        for name, handle in self._directories.items():
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != self.identities[name] or _json(
                _synthetic_tree(handle)
            ) != _json(self.before[name]):
                raise ValueError(
                    "original synthetic excluded bytes, modes, links, or inventory changed"
                )


def verify_frozen_qualification_markers(
    frozen: OriginalVolumeFreeze, plan: FrozenQualificationFixture
) -> None:
    """Read each positive marker through the original actual readonly projection FD."""
    from crewshal.candidate import _entry_fd
    from crewshal.linux_freeze import OriginalVolumeFreeze

    if type(frozen) is not OriginalVolumeFreeze:
        raise ValueError("qualification markers require the original concrete frozen custody")
    context = getattr(frozen.lifetime, "lane_context", None)
    if context is None or context.lane_id not in QUALIFICATION_LANES:
        raise ValueError("qualification marker proof cannot replace live task acceptance")
    frozen.verify_projection()
    descriptor = frozen.handles["readonly-projection"]
    before = (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino)
    if not os.fstatvfs(descriptor).f_flag & os.ST_RDONLY:
        raise ValueError("qualification marker projection is not actually readonly")
    entries = {entry.path: entry for entry in frozen.manifest.files}
    if set(entries) != set(plan.candidate_marker_bytes):
        raise ValueError("actual qualification candidate contains undeclared paths")
    for path, expected in plan.candidate_marker_bytes.items():
        actual, raw = _entry_fd(descriptor, path)
        if actual != entries[path] or actual.kind != "file" or raw != expected.encode():
            raise ValueError("actual readonly qualification marker bytes or metadata differ")
    scratch_name = "mounted:" + context.lane_id + "--scratch-upper"
    scratch = frozen.installation.production.handles[scratch_name]
    scratch_info = os.fstat(scratch)
    if (
        not stat.S_ISDIR(scratch_info.st_mode)
        or (scratch_info.st_uid, scratch_info.st_gid) != (65534, 65534)
        or stat.S_IMODE(scratch_info.st_mode) != 0o700
    ):
        raise ValueError("original qualification scratch volume identity differs")
    scratch_entries = {}
    for path, expected in plan.scratch_marker_bytes.items():
        actual, raw = _entry_fd(scratch, path)
        if actual.kind != "file" or raw != expected.encode():
            raise ValueError("actual original scratch marker bytes or metadata differ")
        scratch_entries[path] = actual
    after = (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino)
    if before != after:
        raise ValueError("original readonly qualification marker root changed")
    frozen.verify_projection()
    for path, actual in scratch_entries.items():
        observed, raw = _entry_fd(scratch, path)
        if observed != actual or raw != plan.scratch_marker_bytes[path].encode():
            raise ValueError("original scratch marker changed during independent readback")


def qualification_probe_source() -> bytes:
    """Return one fixed isolated probe for actual exec_command and write_stdin."""
    return b"""import errno
import json
import mmap
import os
from pathlib import Path
import socket
import subprocess
import sys

DENIALS = (errno.EACCES, errno.EPERM, errno.ENOENT, errno.EROFS)
READ_TARGETS = (
    "/outside/canary", "/original/dirty.py", "/original/.git/config",
    "/coordinator/state.db", "/coordinator/artifact", "/home/owner/auth.json",
    "/scratch/absolute-canary", "/scratch/relative-canary",
)
WRITE_TARGETS = READ_TARGETS + ("/input/canary",)
CREATE_TARGETS = (
    "/outside/phase2d-new", "/original/phase2d-new", "/coordinator/phase2d-new",
    "/input/phase2d-new", "/scratch/absolute-parent/phase2d-new",
    "/scratch/relative-parent/phase2d-new", "/candidate/owned/../phase2d-new",
)

def denied(action):
    try:
        action()
    except OSError as error:
        return error.errno in DENIALS
    return False

def storage():
    result = {}
    target = Path("/scratch/existing")
    original = target.read_bytes()
    fd = os.open(target, os.O_RDWR | os.O_CLOEXEC)
    try:
        os.ftruncate(fd, 4096)
        mapped = mmap.mmap(fd, 4096, flags=mmap.MAP_SHARED,
                           prot=mmap.PROT_READ | mmap.PROT_WRITE)
        try:
            marker = b"phase2d-shared-map"
            mapped[:len(marker)] = marker
            mapped.flush()
            result["storage-file-shared"] = os.pread(fd, len(marker), 0) == marker
        finally:
            mapped.close()
        os.pwrite(fd, original, 0)
        os.ftruncate(fd, len(original))
    finally:
        os.close(fd)
    mapped = mmap.mmap(-1, 4096, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS,
                       prot=mmap.PROT_READ | mmap.PROT_WRITE)
    try:
        mapped[0] = 1
        result["storage-private-anonymous"] = mapped[0] == 1
    finally:
        mapped.close()
    try:
        mapped = mmap.mmap(-1, 4096, flags=mmap.MAP_SHARED | mmap.MAP_ANONYMOUS,
                           prot=mmap.PROT_READ | mmap.PROT_WRITE)
    except OSError as error:
        result["storage-anonymous-shared-denied"] = error.errno in (errno.EACCES, errno.EPERM)
    else:
        result["storage-anonymous-shared-denied"] = False
        mapped.close()
    try:
        fd = os.open("/dev/zero", os.O_RDWR | os.O_CLOEXEC)
    except OSError as error:
        result["storage-dev-zero-denied"] = error.errno in DENIALS
    else:
        result["storage-dev-zero-denied"] = False
        os.close(fd)
    try:
        fd = os.memfd_create("crewshal-phase2d-negative-probe", os.MFD_CLOEXEC)
    except OSError as error:
        result["storage-memfd-denied"] = error.errno in (errno.EACCES, errno.EPERM)
    else:
        result["storage-memfd-denied"] = False
        os.close(fd)
    return result

def filesystem():
    result = storage()
    for index, target in enumerate(READ_TARGETS):
        result["read-" + str(index)] = denied(lambda: Path(target).read_bytes())
    for index, target in enumerate(WRITE_TARGETS):
        result["write-" + str(index)] = denied(lambda: Path(target).write_bytes(b"escape"))
        result["chmod-" + str(index)] = denied(lambda: os.chmod(target, 0o777))
        result["unlink-" + str(index)] = denied(lambda: os.unlink(target))
        result["rename-" + str(index)] = denied(
            lambda: os.rename(target, "/scratch/phase2d-stolen-" + str(index)))
        result["link-" + str(index)] = denied(
            lambda: os.link(target, "/scratch/phase2d-linked-" + str(index)))
    for index, target in enumerate(CREATE_TARGETS):
        result["create-" + str(index)] = denied(lambda: Path(target).write_bytes(b"escape"))
    for name in ("AGENTS.md", "AGENTS.override.md"):
        target = "/scratch/" + name
        result["instructions-empty-" + name] = Path(target).read_bytes() == b""
        result["instructions-write-" + name] = denied(lambda: Path(target).write_bytes(b"escape"))
        result["instructions-unlink-" + name] = denied(lambda: os.unlink(target))
    return result

def network():
    result = {}
    for label, family, kind, address in (
        ("tcp", socket.AF_INET, socket.SOCK_STREAM, ("192.0.2.1", 8082)),
        ("udp", socket.AF_INET, socket.SOCK_DGRAM, ("192.0.2.1", 8082)),
        ("dns", socket.AF_INET, socket.SOCK_DGRAM, ("192.0.2.1", 53)),
        ("ipv6", socket.AF_INET6, socket.SOCK_DGRAM, ("2001:db8::1", 8082)),
    ):
        channel = None
        try:
            channel = socket.socket(family, kind)
            channel.settimeout(0.04)
            if kind == socket.SOCK_STREAM:
                channel.connect(address)
                channel.sendall(b"phase2d-forbidden")
            else:
                channel.sendto(b"phase2d-forbidden", address)
            result[label] = False
        except OSError as error:
            result[label] = error.errno in DENIALS + (errno.ENETUNREACH, errno.EHOSTUNREACH)
        finally:
            if channel is not None:
                channel.close()
    return result

def environment():
    result = {}
    for name in (
        "PHASE2D_PARENT_SECRET", "SSH_AUTH_SOCK", "OPENAI_API_KEY",
        "BASH_ENV", "ENV", "PYTHONSTARTUP", "GIT_CONFIG", "GIT_CONFIG_SYSTEM",
    ):
        result[name] = name not in os.environ
    for name in (
        "/run/phase2d-ssh-agent", "/var/run/docker.sock",
        "/root/.codex/auth.json", "/home/owner/.codex/auth.json",
        "/native-auth/auth.json", "/native-auth/config.toml",
    ):
        result[name] = denied(lambda: Path(name).read_bytes())
    return result

def run():
    mode = sys.argv[1]
    if mode == "entry":
        if Path("/input/canary").read_bytes() != b"phase2d-input\\n":
            raise SystemExit(1)
        print("phase2d-entry", flush=True)
        return
    if mode == "descendant":
        os.setsid()
        print(json.dumps({"filesystem": filesystem(), "network": network()},
                         sort_keys=True, separators=(",", ":")), flush=True)
        return
    if mode == "grandchild":
        os.setsid()
        child = subprocess.run(
            ["/bin/python3", "-I", "-B", __file__, "descendant"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=0.8, check=False, env={}, close_fds=True)
        if child.returncode != 0 or len(child.stdout) > 8192 or child.stderr:
            raise SystemExit(1)
        print(child.stdout.decode(), end="", flush=True)
        return
    if mode != "workload":
        raise SystemExit(1)
    result = {"filesystem": filesystem(), "network": network(), "environment": environment()}
    readme = Path("/candidate/owned/README.md")
    if readme.read_bytes() != b"phase-2d-before\\n":
        raise SystemExit(1)
    readme.write_bytes(b"phase-2d-after\\n")
    for target in ("/candidate/owned/existing", "/scratch/existing"):
        if Path(target).read_bytes() != b"phase2d-owned\\n":
            raise SystemExit(1)
        Path(target).write_bytes(b"phase2d-modified\\n")
    for target in ("/candidate/owned/new", "/scratch/new"):
        Path(target).write_bytes(b"phase2d-created\\n")
    hooks = subprocess.run(
        ["/usr/bin/git", "hook", "run", "--ignore-missing", "pre-commit"],
        cwd="/scratch/checkout", stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=0.3, check=False,
        env=dict(os.environ), close_fds=True)
    result["hooks-exit"] = hooks.returncode
    child = subprocess.run(
        ["/bin/python3", "-I", "-B", __file__, "grandchild"],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=1, check=False, env={}, close_fds=True)
    if child.returncode != 0 or len(child.stdout) > 8192 or child.stderr:
        raise SystemExit(1)
    result["descendant"] = json.loads(child.stdout)
    result["phase2d_complete"] = True
    raw = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if len(raw) > 8192:
        raise SystemExit(1)
    print(raw, flush=True)

run()
"""


BROKER_ENTRY = "/opt/crewshal/lib/crewshal/linux_qualification_fixture.py"
BROKER_ARGV = ["/bin/python3", "-I", "-S", "-B", BROKER_ENTRY]


def _broker_controls(broker: OwnedCgroup, *, empty: bool) -> None:
    """Read the original role directly; worker-only sample limits do not apply."""
    from crewshal.supervisor import _counters

    broker._verify()
    expected = {
        "memory.max": "67108864",
        "pids.max": "16",
        "memory.swap.max": "0",
        "cpu.max": "100000 100000",
        "cgroup.type": "domain",
    }
    if any(broker._read(name) != value for name, value in expected.items()):
        raise ValueError("original broker controls differ")
    events = _counters(broker._read("cgroup.events"), {"populated", "frozen"})
    if events != {"populated": int(not empty), "frozen": 0}:
        raise ValueError("original broker population or freezer differs")
    for name, keys in (("memory.events", {"max", "oom", "oom_kill"}), ("pids.events", {"max"})):
        if any(_counters(broker._read(name), keys).values()):
            raise ValueError("original broker resource refusal remains retained")
    if empty and broker._read("cgroup.procs"):
        raise ValueError("original broker direct tasks remain retained")


def _progress_record(
    raw: bytes, plan: FrozenQualificationTLS, origin: float, lane: str, catalog: object | None
) -> dict[str, object]:
    value = _request(raw)
    if (
        set(value)
        != {
            "lane",
            "plan",
            "fixture",
            "catalog_sha256",
            "catalog",
            "outputs",
            "bootstrap",
            "origin",
        }
        or lane not in QUALIFICATION_LANES
        or value["lane"] != lane
        or value["plan"] != record_digest(plan)
        or value["fixture"] != record_digest(plan.fixture)
        or type(value["origin"]) not in (float, int)
        or value["origin"] != origin
        or value["bootstrap"] != sorted(plan.bootstrap_replies)
        or not isinstance(value["outputs"], dict)
    ):
        raise ValueError("original broker lane capture identity differs")
    actual_catalog = value["catalog"] if lane == QUALIFICATION_LANES[0] else catalog
    if lane == QUALIFICATION_LANES[1] and value["catalog"] is not None:
        raise ValueError("second original broker lane cannot replace the catalog")
    tools = _catalog(actual_catalog)
    if set(tools) & FILE_TOOLS != set(plan.fixture.expected_file_tools):
        raise ValueError("actual broker enabled native file tools differ")
    if value["catalog_sha256"] != hashlib.sha256(_json(actual_catalog)).hexdigest():
        raise ValueError("actual original broker catalog bytes differ")
    verify_native_probe_output(value["outputs"].get(lane + "-stdin"))
    return value


@dataclass(frozen=True)
class TLSBrokerTerminal:
    """Observed custody results do not supply qualification or spend authority."""

    plan: str
    original_origin: float
    catalog_sha256: str
    lane_records: tuple[bytes, bytes]
    launcher_exit: int
    broker_pid: int
    broker_start_ticks: int
    broker_directory: tuple[int, int]
    broker_pidfd: tuple[int, int]
    captured_sha256: str


class TLSBrokerRefusal(ValueError):
    def __init__(self, reason: str, owner: "RetainedTLSBrokerLifetime"):
        super().__init__(reason)
        self.owner = owner
        self.resources_reusable = False


class RetainedTLSBrokerLifetime:
    """Retain one synthetic broker from creation through independent terminal wait."""

    driver: "OriginalInstallationDriver"
    plan: FrozenQualificationTLS
    _plan_payload: str
    origin: float
    _origin: float
    reservation: "OwnedStorageReservation | None"
    broker: OwnedCgroup | None
    root: "RetainedParentInventory | None"
    handles: dict[str, int]
    identities: dict[str, tuple[int, int]]
    received: list[int]
    child: subprocess.Popen[bytes] | None
    task: "RetainedTrustedTask | None"
    launcher: "RetainedTrustedTask | None"
    images: "RetainedInstalledImages | None"
    failed: bool
    ready: bool
    finished: bool
    records: list[bytes]
    _retained_records: tuple[bytes, ...]
    pending: bytearray
    progress_bytes: int
    terminal: TLSBrokerTerminal | None
    listeners: dict[str, socket.socket]
    _owners: tuple[object, ...]
    control: socket.socket
    peer: socket.socket
    _ready_owners: tuple[object, ...] | None
    _ready_spec_payloads: tuple[str, str] | None

    def __init__(self) -> None:
        raise ValueError("TLS broker requires original installation creation custody")

    def __reduce__(self) -> NoReturn:
        raise TypeError("original TLS broker cannot be copied or exported")

    @classmethod
    def launch(
        cls,
        driver: object,
        tls_plan: FrozenQualificationTLS,
        listeners: dict[str, socket.socket],
        *,
        certificate_fd: int,
        private_key_fd: int,
        zstd_library_fd: int,
    ) -> "RetainedTLSBrokerLifetime":
        from crewshal.linux_operational import OriginalInstallationDriver
        from crewshal.linux_network import _inventory_file, _static_helper

        if type(driver) is not OriginalInstallationDriver or hasattr(driver, "_tls_broker"):
            raise ValueError("original qualification TLS broker launch is one-shot")
        owner = object.__new__(cls)
        owner.driver = driver
        owner.plan = FrozenQualificationTLS.model_validate_json(tls_plan.model_dump_json())
        owner._plan_payload = owner.plan.model_dump_json()
        owner.origin = driver.origin
        owner._origin = owner.origin
        owner.reservation = driver.reservation
        owner.broker = driver.groups.get("broker")
        owner.root = None if driver.production is None else driver.production.projected_inventory
        owner.handles = {}
        owner.identities = {}
        owner.received = []
        owner.child = None
        owner.task = owner.launcher = owner.images = None
        owner.failed = owner.ready = owner.finished = False
        owner.records = []
        owner._retained_records = ()
        owner.pending = bytearray()
        owner.progress_bytes = 0
        owner.terminal = None
        owner.listeners = dict(listeners)
        owner._owners = driver, owner.reservation, owner.broker, owner.root
        owner._ready_owners = owner._ready_spec_payloads = None
        setattr(driver, "_tls_broker", owner)
        try:
            owner._custody()
            assert owner.broker is not None and owner.root is not None
            if owner.plan.fixture.configuration != record_digest(driver.inputs.configuration):
                raise ValueError("fixture must bind the original common configuration")
            _broker_controls(owner.broker, empty=True)
            if set(listeners) != set(QUALIFICATION_LANES):
                raise ValueError("both original qualification listeners required")
            for lane, channel in listeners.items():
                if (
                    type(channel) is not socket.socket
                    or channel.family != socket.AF_INET
                    or channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_STREAM
                    or channel.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) != 1
                    or channel.getsockname() != owner.plan.listener_addresses[lane]
                ):
                    raise ValueError("original TLS listener identity or address differs")
                owner._retain("listener:" + lane, channel.fileno(), duplicate=True)
            for name, handle, expected, bound in (
                ("certificate", certificate_fd, owner.plan.certificate_sha256, 65536),
                ("private-key", private_key_fd, owner.plan.private_key_sha256, 65536),
                ("zstd", zstd_library_fd, owner.plan.zstd_library_sha256, 2097152),
            ):
                owner._retain(name, handle, duplicate=True)
                _readonly_file(owner.handles[name], expected, bound)
            entry = owner.root.inventory.root.get(BROKER_ENTRY)
            if entry is None or entry.kind != "file":
                raise ValueError("exact finite broker entry is absent from the copied root")
            owner._retain("helper", _inventory_file(owner.root, "/bin/crewshal-bootstrap"))
            _static_helper(owner.handles["helper"])
            read_ack, write_ack = getattr(os, "pipe2")(os.O_CLOEXEC)
            owner._retain("ack-read", read_ack)
            owner._retain("ack-write", write_ack)
            read_progress, write_progress = getattr(os, "pipe2")(os.O_CLOEXEC | os.O_NONBLOCK)
            owner._retain("progress-read", read_progress)
            owner._retain("progress-write", write_progress)
            local, remote = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            owner.control = local
            owner.peer = remote
            owner._retain("control", local.fileno(), duplicate=True)
            owner._retain("peer", remote.fileno(), duplicate=True)
            local.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_PASSCRED"), 1)
            capsule = _json(
                {
                    "plan": owner.plan.model_dump(mode="json"),
                    "origin": owner.origin,
                    "broker": owner.broker.identity.model_dump(mode="json"),
                }
            )
            if len(capsule) > REQUEST_BOUND:
                raise ValueError("original fixture capsule exceeds bound")
            capsule_fd = getattr(os, "memfd_create")("crewshal-qualification-broker", 1 | 2)
            owner._retain("capsule", capsule_fd)
            if os.write(capsule_fd, capsule) != len(capsule):
                raise ValueError("original fixture capsule write is incomplete")
            fcntl.fcntl(capsule_fd, getattr(fcntl, "F_ADD_SEALS"), 1 | 2 | 4 | 8)
            controls = [
                owner.broker.descriptor,
                owner.root.descriptor,
                capsule_fd,
                owner.handles["listener:qualification-1"],
                owner.handles["listener:qualification-2"],
                owner.handles["certificate"],
                owner.handles["private-key"],
                owner.handles["zstd"],
                owner.handles["peer"],
                read_ack,
                write_progress,
                driver.production.handles["namespace"],
            ]
            owner._custody()
            if time.monotonic() >= owner.origin + 120:
                raise ValueError("original TLS broker startup deadline exhausted")
            owner.child = subprocess.Popen(
                [
                    "/proc/self/fd/" + str(owner.handles["helper"]),
                    "--qualification-broker-fds",
                    *(str(handle) for handle in controls),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={},
                close_fds=True,
                pass_fds=tuple(controls) + (owner.handles["helper"],),
                cwd="/",
            )
            owner._retain("launcher-pidfd", getattr(os, "pidfd_open")(owner.child.pid, 0))
            owner._retain(
                "launcher-proc",
                os.open(
                    "/proc/" + str(owner.child.pid),
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                ),
            )
            # These are known parent copies, never unknown child identity handles.
            for name in ("ack-read", "progress-write", "peer"):
                os.close(owner.handles.pop(name))
                owner.identities.pop(name)
            remote.close()
            return owner
        except BaseException as error:
            owner._refuse(error)

    def _retain(self, name: str, descriptor: int, *, duplicate: bool = False) -> None:
        handle = os.dup(descriptor) if duplicate else descriptor
        self.handles[name] = handle
        info = os.fstat(handle)
        self.identities[name] = info.st_dev, info.st_ino

    def _refuse(self, error: BaseException) -> NoReturn:
        self.failed = True
        if self.reservation is not None:
            self.reservation._retain_installation_refusal(error)
        raise TLSBrokerRefusal(str(error), self) from error

    def _custody(self) -> None:
        from crewshal.linux_setup import OwnedStorageReservation
        from crewshal.linux_inventory import RetainedParentInventory

        if (
            self.failed
            or getattr(self.driver, "_tls_broker", None) is not self
            or self._owners != (self.driver, self.reservation, self.broker, self.root)
            or type(self.reservation) is not OwnedStorageReservation
            or type(self.broker) is not OwnedCgroup
            or type(self.root) is not RetainedParentInventory
            or self.driver.reservation is not self.reservation
            or self.driver.groups.get("broker") is not self.broker
            or self.driver.production is None
            or self.driver.production.projected_inventory is not self.root
            or self.origin != self._origin
            or self.origin != self.driver.origin
            or self.plan.model_dump_json() != self._plan_payload
            or tuple(self.records) != self._retained_records
            or not 0 < self.origin <= time.monotonic() < self.origin + 570
        ):
            raise ValueError("original TLS broker owner, plan, root, or deadline changed")
        assert self.reservation is not None and self.broker is not None and self.root is not None
        self.reservation.verify()
        self.reservation.observer.verify(self.reservation.observer_group.identity)
        self.root.verify()
        if (
            self.broker.identity.relative_path
            != self.reservation.aggregate.identity.relative_path + "/broker"
        ):
            raise ValueError("TLS broker is outside the original aggregate")
        if not os.fstatvfs(self.root.descriptor).f_flag & os.ST_RDONLY:
            raise ValueError("original TLS broker copied root is writable")
        for name, handle in self.handles.items():
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != self.identities[name]:
                raise ValueError("original TLS broker retained handle changed")
        if self._ready_owners is not None:
            if (
                self._ready_owners != (self.task, self.launcher, self.images)
                or self.task is None
                or self.launcher is None
                or self._ready_spec_payloads
                != (self.task.spec.model_dump_json(), self.launcher.spec.model_dump_json())
            ):
                raise ValueError("original TLS broker ready task custody changed")
        if hasattr(self, "control"):
            info = os.fstat(self.control.fileno())
            if (info.st_dev, info.st_ino) != self.identities["control"]:
                raise ValueError("original TLS broker control socket changed")

    def _packet(self, phase: str) -> dict[str, object]:
        from crewshal.admission import _fields

        deadline = self.origin + (120 if phase == "ready" else 570)
        while not _wait_ready(
            [self.control], [], [], min(0.05, max(0, deadline - time.monotonic()))
        )[0]:
            if time.monotonic() >= deadline:
                raise ValueError("original TLS broker packet deadline exhausted")
            self._custody()
            if self.child is None or self.child.poll() is not None:
                raise ValueError("original TLS broker packet remains unknown")
        raw, ancillary, flags, _ = self.control.recvmsg(
            4097, socket.CMSG_SPACE(12) + socket.CMSG_SPACE(12)
        )
        credentials = None
        rights: list[int] = []
        for level, kind, data in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                found = array("i")
                found.frombytes(data[: len(data) - len(data) % found.itemsize])
                rights.extend(found)
                self.received.extend(found)
            elif level == socket.SOL_SOCKET and kind == getattr(socket, "SCM_CREDENTIALS"):
                credentials = tuple(array("i", data))
            else:
                raise ValueError("original TLS broker ancillary data differs")
        value = _request(raw)
        if (
            flags
            or len(raw) > 4096
            or credentials is None
            or len(credentials) != 3
            or credentials[1:] != (0, 0)
            or value.get("phase") != phase
            or value.get("plan") != record_digest(self.plan)
            or value.get("origin") != self.origin
            or value.get("pid") != credentials[0]
        ):
            raise ValueError("actual original TLS broker packet identity differs")
        if phase == "ready":
            if len(rights) != 3:
                raise ValueError("original TLS broker birth descriptors remain unknown")
            for name, handle in zip(
                ("broker-proc", "broker-pidfd", "broker-mnt"), rights, strict=True
            ):
                self._retain(name, handle)
            proc = self.handles["broker-proc"]
            pidfd = self.handles["broker-pidfd"]
            with open("/proc/self/fdinfo/" + str(pidfd), "rb") as stream:
                fdinfo = _fields(stream.read(4097))
            if fdinfo.get("Pid") != str(credentials[0]):
                raise ValueError("original TLS broker pidfd birth differs")
            if not stat.S_ISDIR(os.fstat(proc).st_mode):
                raise ValueError("original TLS broker proc directory differs")
        elif rights or self.task is None or credentials[0] != self.task.spec.pid:
            raise ValueError("original TLS broker terminal birth identity differs")
        return value

    def _await_launcher_placement(self) -> None:
        from crewshal.admission import _read, _stat_identity

        if self.child is None or self.broker is None:
            raise ValueError("original TLS launcher birth remains unknown")
        proc = self.handles["launcher-proc"]
        pidfd = self.handles["launcher-pidfd"]
        for name, handle in (("launcher-proc", proc), ("launcher-pidfd", pidfd)):
            info = os.fstat(handle)
            if (info.st_dev, info.st_ino) != self.identities[name]:
                raise ValueError("original TLS launcher retained birth changed")
        initial = _stat_identity(_read(proc, "stat"))
        expected = ("0::/" + self.broker.identity.relative_path).encode()
        while time.monotonic() < self.origin + 120:
            current = _stat_identity(_read(proc, "stat"))
            if (
                current[0] != self.child.pid
                or current[2] != os.getpid()
                or (current[0], current[2], current[3]) != (initial[0], initial[2], initial[3])
                or _wait_ready([pidfd], [], [], 0)[0]
            ):
                raise ValueError("original TLS launcher placement remains unknown")
            if _read(proc, "cgroup").strip() == expected:
                return
            _wait_ready([], [], [], 0.001)
        raise ValueError("original TLS launcher startup deadline exhausted")

    def require_ready(self) -> None:
        from crewshal.admission import NamespaceIdentity, _read, _stat_identity
        from crewshal.linux_parent import RetainedTrustedTask, TrustedTaskSpec
        from crewshal.linux_installed import retain_installed_images

        try:
            if self.ready or self.finished:
                raise ValueError("original TLS broker readiness already consumed")
            # The trusted launcher places itself before creating the broker.
            # Do not validate sole-observer custody during that transition.
            self._await_launcher_placement()
            self._custody()
            assert (
                self.reservation is not None and self.root is not None and self.broker is not None
            )
            if time.monotonic() >= self.origin + 120:
                raise ValueError("original TLS broker startup deadline exhausted")
            packet = self._packet("ready")
            if set(packet) != {"phase", "plan", "origin", "pid"} or self.child is None:
                raise ValueError("original TLS broker ready packet differs")
            proc = self.handles["broker-proc"]
            pid, _, parent, ticks = _stat_identity(_read(proc, "stat"))
            observer = self.reservation.observer.spec
            launcher_proc = self.handles["launcher-proc"]
            launcher_pid, _, launcher_parent, launcher_ticks = _stat_identity(
                _read(launcher_proc, "stat")
            )
            if launcher_pid != self.child.pid or launcher_parent != os.getpid():
                raise ValueError("original TLS broker launcher birth differs")
            helper = self.root.inventory.root["/bin/crewshal-bootstrap"].sha256
            if helper is None:
                raise ValueError("original TLS broker launcher image is missing")
            if not isinstance(self.child.args, list) or any(
                not isinstance(arg, str) for arg in self.child.args
            ):
                raise ValueError("original TLS broker launcher argv differs")
            self.launcher = RetainedTrustedTask(
                launcher_proc,
                self.handles["launcher-pidfd"],
                TrustedTaskSpec(
                    configuration=record_digest(self.driver.inputs.configuration),
                    pid=launcher_pid,
                    parent_pid=os.getpid(),
                    start_ticks=launcher_ticks,
                    boot_id=observer.boot_id,
                    cgroup=self.broker.identity,
                    namespaces=observer.namespaces,
                    executable=helper,
                    argv=self.child.args,
                    environment={},
                    capabilities=observer.capabilities,
                    cwd="/",
                    placement="outer_observer",
                ),
            )
            self.launcher.verify(self.broker.identity)
            helper_info = os.fstat(self.handles["helper"])
            image_info = os.stat("exe", dir_fd=launcher_proc)
            if (helper_info.st_dev, helper_info.st_ino) != (image_info.st_dev, image_info.st_ino):
                raise ValueError("original TLS broker launcher uses another helper inode")
            namespaces = dict(observer.namespaces)
            info = os.fstat(self.handles["broker-mnt"])
            namespaces["mnt"] = NamespaceIdentity(device=info.st_dev, inode=info.st_ino)
            if (
                pid != packet["pid"]
                or parent != self.child.pid
                or namespaces["mnt"] == observer.namespaces["mnt"]
            ):
                raise ValueError("original TLS broker child or private mount differs")
            python = self.root.inventory.root["/bin/python3"].sha256
            if python is None:
                raise ValueError("original TLS broker exact Python image is missing")
            spec = TrustedTaskSpec(
                configuration=record_digest(self.driver.inputs.configuration),
                pid=pid,
                parent_pid=self.child.pid,
                start_ticks=ticks,
                boot_id=observer.boot_id,
                cgroup=self.broker.identity,
                namespaces=namespaces,
                executable=python,
                argv=BROKER_ARGV,
                environment={},
                capabilities=observer.capabilities,
                cwd="/",
                placement="outer_observer",
            )
            self.task = RetainedTrustedTask(
                self.handles["broker-proc"], self.handles["broker-pidfd"], spec
            )
            self.task.verify(self.broker.identity)
            _broker_controls(self.broker, empty=False)
            if set(self.broker._read("cgroup.procs").split()) != {str(pid), str(launcher_pid)}:
                raise ValueError("original broker contains an unexpected task")
            self.images = retain_installed_images(self.task, self.root)
            self._ready_owners = self.task, self.launcher, self.images
            self._ready_spec_payloads = (
                self.task.spec.model_dump_json(),
                self.launcher.spec.model_dump_json(),
            )
            self._custody()
            assert (
                self.broker is not None
                and self.task is not None
                and self.images is not None
                and self.child is not None
            )
            if time.monotonic() >= self.origin + 120:
                raise ValueError("original TLS broker startup deadline exhausted")
            if os.write(self.handles["ack-write"], b"R") != 1:
                raise ValueError("original TLS broker ready ACK remains unknown")
            self.ready = True
        except BaseException as error:
            self._refuse(error)

    def verify_ready(self) -> None:
        """Repeat actual readback without replacing or renewing the original readiness."""
        try:
            self._custody()
            if (
                not self.ready
                or self.finished
                or self.task is None
                or self.images is None
                or self.launcher is None
                or self.broker is None
                or self.reservation is None
            ):
                raise ValueError("original TLS broker ready custody is missing or terminal")
            self.task.verify(self.broker.identity)
            self.launcher.verify(self.broker.identity)
            self.images.verify()
            _broker_controls(self.broker, empty=False)
            if set(self.broker._read("cgroup.procs").split()) != {
                str(self.task.spec.pid),
                str(self.launcher.spec.pid),
            }:
                raise ValueError("original TLS broker has an unexpected direct task")
        except BaseException as error:
            self._refuse(error)

    def read_lane(self, lane_id: str) -> dict[str, object]:
        try:
            self._custody()
            if (
                not self.ready
                or self.finished
                or len(self.records) >= 2
                or lane_id != QUALIFICATION_LANES[len(self.records)]
            ):
                raise ValueError("original TLS broker lane capture order is consumed or invalid")
            while b"\n" not in self.pending:
                remaining = self.origin + 570 - time.monotonic()
                if remaining <= 0:
                    raise ValueError("original TLS broker capture deadline exhausted")
                if _wait_ready([self.handles["progress-read"]], [], [], min(remaining, 0.05))[0]:
                    part = os.read(
                        self.handles["progress-read"], CAPTURE_BOUND + 1 - self.progress_bytes
                    )
                    if not part:
                        raise ValueError("original TLS broker lane capture EOF is incomplete")
                    self.pending.extend(part)
                    self.progress_bytes += len(part)
                    if self.progress_bytes > CAPTURE_BOUND:
                        raise ValueError("original TLS broker combined capture exceeds bound")
                self._custody()
            raw, _, rest = self.pending.partition(b"\n")
            catalog = _request(self.records[0])["catalog"] if self.records else None
            value = _progress_record(bytes(raw), self.plan, self.origin, lane_id, catalog)
            self.records.append(bytes(raw))
            self._retained_records = tuple(self.records)
            self.pending = bytearray(rest)
            return value
        except BaseException as error:
            self._refuse(error)

    def finish(self) -> TLSBrokerTerminal:
        try:
            self._custody()
            assert (
                self.broker is not None
                and self.task is not None
                and self.images is not None
                and self.child is not None
            )
            if not self.ready or self.finished or len(self.records) != 2:
                raise ValueError("both original TLS broker lanes must finish once")
            packet = self._packet("terminal")
            if set(packet) != {"phase", "plan", "origin", "pid", "captured_sha256"}:
                raise ValueError("original TLS broker terminal packet differs")
            first, second = (_request(raw) for raw in self.records)
            captured = _json(
                {
                    "plan": record_digest(self.plan.fixture),
                    "catalog_sha256": first["catalog_sha256"],
                    "catalog": first["catalog"],
                    "outputs": {
                        QUALIFICATION_LANES[0]: first["outputs"],
                        QUALIFICATION_LANES[1]: second["outputs"],
                    },
                    "origin": self.origin,
                }
            )
            if (
                len(captured) > CAPTURE_BOUND
                or packet["captured_sha256"] != hashlib.sha256(captured).hexdigest()
            ):
                raise ValueError("original TLS broker complete capture readback differs")
            self.task.verify(self.broker.identity)
            self.images.verify()
            self._custody()
            if os.write(self.handles["ack-write"], b"T") != 1:
                raise ValueError("original TLS broker terminal ACK remains unknown")
            while self.child.poll() is None:
                self._custody()
                _wait_ready(
                    [self.handles["launcher-pidfd"]],
                    [],
                    [],
                    min(0.05, max(0, self.origin + 570 - time.monotonic())),
                )
            if (
                self.child.returncode != 0
                or not _wait_ready([self.task.pidfd], [], [], 0)[0]
                or not _wait_ready([self.handles["launcher-pidfd"]], [], [], 0)[0]
                or self.pending
                or os.read(self.handles["progress-read"], 1) != b""
            ):
                raise ValueError("original TLS broker positive wait or capture EOF remains unknown")
            _broker_controls(self.broker, empty=True)
            self.terminal = TLSBrokerTerminal(
                record_digest(self.plan),
                self.origin,
                str(first["catalog_sha256"]),
                (self.records[0], self.records[1]),
                self.child.returncode,
                self.task.spec.pid,
                self.task.spec.start_ticks,
                self.task.directory,
                self.task.pidfd_identity,
                hashlib.sha256(captured).hexdigest(),
            )
            self.finished = True
            return self.terminal
        except BaseException as error:
            self._refuse(error)


def _run_broker_entry() -> None:
    from crewshal.supervisor import CgroupIdentity

    info = os.fstat(5)
    seals = 1 | 2 | 4 | 8
    if (
        not stat.S_ISREG(info.st_mode)
        or not 0 < info.st_size <= REQUEST_BOUND
        or fcntl.fcntl(5, getattr(fcntl, "F_GET_SEALS")) != seals
    ):
        raise ValueError("original TLS broker sealed capsule differs")
    capsule = _request(os.pread(5, info.st_size + 1, 0))
    if set(capsule) != {"plan", "origin", "broker"}:
        raise ValueError("original TLS broker capsule fields differ")
    plan = FrozenQualificationTLS.model_validate(capsule["plan"])
    raw_origin = capsule["origin"]
    if type(raw_origin) not in (float, int):
        raise ValueError("original TLS broker capsule deadline differs")
    assert isinstance(raw_origin, (float, int))
    origin = float(raw_origin)
    if not 0 < origin <= time.monotonic() < origin + 570:
        raise ValueError("original TLS broker capsule deadline differs")
    broker = OwnedCgroup.attach_inherited(3, CgroupIdentity.model_validate(capsule["broker"]))
    control = socket.socket(fileno=11)
    listeners = {
        QUALIFICATION_LANES[0]: socket.socket(fileno=6),
        QUALIFICATION_LANES[1]: socket.socket(fileno=7),
    }

    def ack(expected: bytes) -> None:
        while time.monotonic() < origin + 570:
            if _wait_ready([12], [], [], min(0.05, origin + 570 - time.monotonic()))[0]:
                if os.read(12, 1) != expected:
                    raise ValueError("original TLS broker ACK differs or reached EOF")
                return
        raise ValueError("original TLS broker ACK deadline exhausted")

    def ready() -> None:
        proc = os.open("/proc/self", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        pidfd = getattr(os, "pidfd_open")(os.getpid(), 0)
        namespace = os.open("ns/mnt", os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
        raw = _json(
            {"phase": "ready", "plan": record_digest(plan), "origin": origin, "pid": os.getpid()}
        )
        if control.sendmsg(
            [raw], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array("i", [proc, pidfd, namespace]))]
        ) != len(raw):
            raise ValueError("original TLS broker birth transfer is incomplete")
        ack(b"R")

    captured = serve_qualification_tls(
        plan, origin, broker, listeners, 8, 9, 10, 13, ready_callback=ready
    )
    raw = _json(
        {
            "phase": "terminal",
            "plan": record_digest(plan),
            "origin": origin,
            "pid": os.getpid(),
            "captured_sha256": hashlib.sha256(captured).hexdigest(),
        }
    )
    if control.send(raw) != len(raw):
        raise ValueError("original TLS broker terminal transfer is incomplete")
    ack(b"T")


if __name__ == "__main__":
    _run_broker_entry()
