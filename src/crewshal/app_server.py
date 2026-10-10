"""Finite pinned Codex app-server protocol; no process or execution authority.

The caller owns deadlines, stdin closure, raw process exit and terminal readback.
Account metadata and quota observations do not establish unique account continuity.
Sandbox readback does not establish effective credential isolation. Qualification
must establish a fresh native home without a preloaded .env, the actual stock
arg0 helper grant and effective file/proc/FD denial independently.
"""

import json
from typing import Literal, Self

from pydantic import ConfigDict, JsonValue, model_validator

from crewshal import __version__
from crewshal.contracts import Digest
from crewshal.model import Contract

MAX_PROTOCOL_BYTES = 65536
MAX_PROTOCOL_EVENTS = 1024

SUBSCRIPTION_PERMISSIONS: dict[str, JsonValue] = {
    "filesystem": {
        ":minimal": "read",
        "/opt/codex": "read",
        "/input": "read",
        "/candidate/owned": "write",
        "/scratch": "write",
        "/native-auth/auth.json": "deny",
        "/native-auth/config.toml": "deny",
        "/native-control": "deny",
    },
    "network": {"enabled": False},
}
SUBSCRIPTION_STARTUP_SETTINGS: dict[str, JsonValue] = {
    "default_permissions": "crewshal",
    "model_provider": "openai",
    "forced_login_method": "chatgpt",
    "cli_auth_credentials_store": "file",
    "model_providers.openai.requires_openai_auth": True,
    "model_providers.openai.supports_websockets": False,
    "model_providers.openai.request_max_retries": 0,
    "model_providers.openai.stream_max_retries": 0,
    "features.unbounded_connection_retries": False,
    # Override literal table: pinned CLI splits dotted keys, including filename dots.
    "permissions.crewshal.filesystem": SUBSCRIPTION_PERMISSIONS["filesystem"],
    "permissions.crewshal.network.enabled": False,
}


def _leaves(value: dict[str, object], prefix: str = "") -> dict[str, object]:
    result: dict[str, object] = {}
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(item, dict):
            result.update(_leaves(item, path))
        else:
            result[path] = item
    return result


class AppServerProtocolError(ValueError):
    """Terminal protocol refusal; the exchange cannot be retried."""


def _encode(value: object) -> bytes:
    try:
        return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True).encode()
    except (ValueError, TypeError, RecursionError) as error:
        raise AppServerProtocolError("non-finite or unsupported configuration") from error


def _same(actual: object, expected: object) -> bool:
    """JSON type identity matters: false must never satisfy a zero retry ceiling."""
    return _encode(actual) == _encode(expected)


_PERMISSIONS_BASELINE = _encode(SUBSCRIPTION_PERMISSIONS)
_STARTUP_BASELINE = _encode(SUBSCRIPTION_STARTUP_SETTINGS)


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise AppServerProtocolError("expected JSON object")
    return value


def _string(value: object) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise AppServerProtocolError("expected nonempty literal")
    return value


def _validate_profile(profile: "AppServerProfile") -> None:
    for value in (profile.model, profile.requirement, profile.codex_home):
        _string(value)
    if not profile.codex_home.startswith("/"):
        raise AppServerProtocolError("native auth home must be absolute")
    account = profile.expected_account
    if set(account) != {"type", "email", "planType"} or account["type"] != "chatgpt":
        raise AppServerProtocolError("only managed subscription account metadata is supported")
    if account["email"] is not None:
        _string(account["email"])
    _string(account["planType"])
    if profile.expected_account_id is not None:
        _string(profile.expected_account_id)
    params = profile.thread_params
    allowed = {
        "model",
        "modelProvider",
        "cwd",
        "approvalPolicy",
        "approvalsReviewer",
        "sandbox",
        "ephemeral",
        "config",
    }
    if not set(params) <= allowed:
        raise AppServerProtocolError("unsupported thread configuration")
    if (
        params.get("model") != profile.model
        or params.get("modelProvider") != "openai"
        or params.get("approvalPolicy") != "never"
        or params.get("ephemeral") is not True
    ):
        raise AppServerProtocolError("thread must bind model, provider, no approval and ephemeral")
    cwd = _string(params.get("cwd"))
    if cwd != "/candidate/owned":
        raise AppServerProtocolError("fixed task cwd must be the owned candidate")
    expected = profile.expected_thread
    required = {"model", "modelProvider", "cwd", "approvalPolicy", "approvalsReviewer", "sandbox"}
    if not required <= set(expected) or not set(expected) <= required | {
        "reasoningEffort",
        "serviceTier",
        "instructionSources",
        "disabledPluginIds",
    }:
        raise AppServerProtocolError("exact thread control readback is required")
    if any(
        key not in expected or not _same(expected[key], params[key])
        for key in ("model", "modelProvider", "cwd", "approvalPolicy")
    ):
        raise AppServerProtocolError("contradictory thread readback")
    sandbox = _object(expected["sandbox"])
    if not _same(
        sandbox,
        {
            "type": "workspaceWrite",
            "writableRoots": ["/scratch"],
            "networkAccess": False,
            "excludeSlashTmp": True,
            "excludeTmpdirEnvVar": True,
        },
    ):
        raise AppServerProtocolError("pinned legacy sandbox projection differs")
    if (
        "approvalsReviewer" in params
        and params["approvalsReviewer"] != expected["approvalsReviewer"]
    ):
        raise AppServerProtocolError("approval reviewer contradicts readback")
    if "sandbox" in params or params.get("config", {}) != {}:
        raise AppServerProtocolError(
            "thread overrides cannot replace the managed permission profile"
        )
    config = profile.expected_config
    permissions = _object(config.get("permissions"))
    if config.get("default_permissions") != "crewshal" or not _same(
        permissions.get("crewshal"), profile.permission_profile
    ):
        raise AppServerProtocolError("managed permission profile config binding is required")
    if (
        _encode(SUBSCRIPTION_PERMISSIONS) != _PERMISSIONS_BASELINE
        or _encode(SUBSCRIPTION_STARTUP_SETTINGS) != _STARTUP_BASELINE
        or _encode(profile.permission_profile) != _PERMISSIONS_BASELINE
    ):
        raise AppServerProtocolError("exact bounded filesystem/network policy is required")
    leaves = _leaves(_object(config))
    if any(
        key not in leaves or not _same(leaves[key], value)
        for key, value in _leaves(_object(SUBSCRIPTION_STARTUP_SETTINGS)).items()
    ):
        raise AppServerProtocolError("subscription transport/startup controls must be bound")
    if len(_encode(profile.model_dump(mode="json"))) > MAX_PROTOCOL_BYTES:
        raise AppServerProtocolError("configuration exceeds protocol bound")


class AppServerProfile(Contract):
    """Declarative input, never launch permission or credential-denial evidence."""

    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True, frozen=True)
    model: str
    requirement: str
    account_reference: Digest
    expected_account: dict[str, JsonValue]
    codex_home: Literal["/native-auth"] = "/native-auth"
    thread_params: dict[str, JsonValue]
    expected_thread: dict[str, JsonValue]
    permission_profile: dict[str, JsonValue]
    expected_config: dict[str, JsonValue]
    expected_account_id: str | None = None

    @model_validator(mode="after")
    def supported(self) -> Self:
        _validate_profile(self)
        return self


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AppServerProtocolError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> object:
    raise AppServerProtocolError("non-finite JSON number")


class AppServerExchange:
    """One initialize/config/account/quota/thread/turn exchange, without I/O or retries."""

    def __init__(self, profile: AppServerProfile) -> None:
        AppServerProfile.model_validate_json(profile.model_dump_json())
        _validate_profile(profile)
        self._profile = profile
        self._snapshot = _encode(profile.model_dump(mode="json"))
        self._started = False
        self._failed = False
        self._next = 1
        self._bytes = 0
        self._events = 0
        self._thread_id: str | None = None
        self._turn_id: str | None = None
        self._seen: set[str] = set()
        self._item_started: set[str] = set()
        self._item_completed: set[str] = set()
        self._pending_completion = False
        self._completed = False
        self._auth_recovering = False

    @classmethod
    def from_profile(cls, profile: AppServerProfile) -> Self:
        return cls(profile)

    @property
    def protocol_completed(self) -> bool:
        return self._completed and not self._failed

    @property
    def thread_id(self) -> str | None:
        return self._thread_id

    @property
    def turn_id(self) -> str | None:
        return self._turn_id

    def _guard(self) -> None:
        if self._failed:
            raise AppServerProtocolError("exchange already refused")
        if _encode(self._profile.model_dump(mode="json")) != self._snapshot:
            raise AppServerProtocolError("configuration changed during exchange")

    def _message(self, method: str, params: object, request_id: int | None = None) -> bytes:
        data: dict[str, object] = {"method": method, "params": params}
        if request_id is not None:
            data["id"] = request_id
        return _encode(data) + b"\n"

    def start(self) -> bytes:
        try:
            self._guard()
            if self._started:
                raise AppServerProtocolError("initialize cannot replay")
            self._started = True
            return self._message(
                "initialize",
                {
                    "clientInfo": {"name": "crewshal", "version": __version__},
                    "capabilities": {"experimentalApi": False},
                },
                1,
            )
        except ValueError:
            self._failed = True
            raise

    def feed(self, raw: bytes) -> tuple[bytes, ...]:
        try:
            self._guard()
            if not self._started or self._completed:
                raise AppServerProtocolError("message outside active exchange")
            if not isinstance(raw, bytes) or not raw.endswith(b"\n") or raw.count(b"\n") != 1:
                raise AppServerProtocolError("one complete JSONL line is required")
            self._bytes += len(raw)
            self._events += 1
            if self._bytes > MAX_PROTOCOL_BYTES or self._events > MAX_PROTOCOL_EVENTS:
                raise AppServerProtocolError("protocol capture bound exceeded")
            data = _object(
                json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
            )
            if "id" in data:
                if set(data) != {"id", "result"}:
                    raise AppServerProtocolError("error or server request refused")
                if type(data["id"]) is not int or data["id"] != self._next:
                    raise AppServerProtocolError("unexpected or replayed response ID")
                return self._response(_object(data["result"]))
            if set(data) != {"method", "params"}:
                raise AppServerProtocolError("unsupported message envelope")
            self._notification(_string(data["method"]), _object(data["params"]))
            return ()
        except (ValueError, UnicodeError, RecursionError, TypeError) as error:
            self._failed = True
            if isinstance(error, AppServerProtocolError):
                raise
            raise AppServerProtocolError("invalid protocol JSON") from error

    def _response(self, result: dict[str, object]) -> tuple[bytes, ...]:
        phase = self._next
        output: tuple[bytes, ...]
        if phase == 1:
            if (
                result.get("codexHome") != self._profile.codex_home
                or result.get("platformFamily") != "unix"
                or result.get("platformOs") != "linux"
            ):
                raise AppServerProtocolError("native home or Linux readback mismatch")
            _string(result.get("userAgent"))
            output = (
                self._message("initialized", {}),
                self._message(
                    "config/read",
                    {
                        "includeLayers": True,
                        "cwd": self._profile.thread_params["cwd"],
                    },
                    2,
                ),
            )
        elif phase == 2:
            config = _object(result.get("config"))
            origins = _object(result.get("origins"))
            layers = result.get("layers")
            if not isinstance(layers, list):
                raise AppServerProtocolError("included config layers unavailable")
            if any(
                key not in config or not _same(config[key], value)
                for key, value in self._profile.expected_config.items()
            ):
                raise AppServerProtocolError("managed config readback mismatch")
            versions: set[str] = set()
            for raw_layer in layers:
                layer = _object(raw_layer)
                if layer.get("name") == {"type": "sessionFlags"}:
                    if layer.get("disabledReason") is not None:
                        raise AppServerProtocolError("managed session layer is disabled")
                    versions.add(_string(layer.get("version")))
                    _object(layer.get("config"))
            if not versions:
                raise AppServerProtocolError("managed session layer unavailable")
            for path in _leaves(_object(self._profile.expected_config)):
                origin = _object(origins.get(path))
                if (
                    origin.get("name") != {"type": "sessionFlags"}
                    or _string(origin.get("version")) not in versions
                ):
                    raise AppServerProtocolError("managed setting origin mismatch")
            output = (self._message("account/read", {"refreshToken": False}, 3),)
        elif phase == 3:
            if result.get("requiresOpenaiAuth") is not True or not _same(
                result.get("account"), self._profile.expected_account
            ):
                raise AppServerProtocolError("subscription metadata mismatch")
            output = (
                self._message(
                    "account/rateLimits/read",
                    {
                        "supportsLunaReserve": False,
                        "excludeResetCreditDetails": True,
                    },
                    4,
                ),
            )
        elif phase == 4:
            self._quota(result)
            if (
                self._profile.expected_account_id is not None
                and result.get("accountId") != self._profile.expected_account_id
            ):
                raise AppServerProtocolError("quota account reference unavailable or changed")
            if result.get("ordinaryUsageAllowed") is False:
                raise AppServerProtocolError("backend refuses ordinary usage")
            output = (self._message("thread/start", self._profile.thread_params, 5),)
        elif phase == 5:
            if any(
                key not in result or not _same(result[key], value)
                for key, value in self._profile.expected_thread.items()
            ):
                raise AppServerProtocolError("thread control readback mismatch")
            self._thread(_object(result.get("thread")))
            output = (
                self._message(
                    "turn/start",
                    {
                        "threadId": self._thread_id,
                        "input": [{"type": "text", "text": self._profile.requirement}],
                    },
                    6,
                ),
            )
        elif phase == 6:
            self._turn(_object(result.get("turn")))
            self._completed = self._pending_completion
            output = ()
        else:
            raise AppServerProtocolError("extra response refused")
        self._next += 1
        return output

    def _bind(self, kind: str, value: object) -> None:
        identity = _string(value)
        current = self._thread_id if kind == "thread" else self._turn_id
        if current is not None and current != identity:
            raise AppServerProtocolError("foreign thread or turn")
        if kind == "thread":
            self._thread_id = identity
        else:
            self._turn_id = identity

    def _thread(self, thread: dict[str, object]) -> None:
        self._bind("thread", thread.get("id"))
        if (
            thread.get("cliVersion") != "0.160.1"
            or thread.get("source") != "appServer"
            or "projectId" not in thread
            or not isinstance(thread.get("preview"), str)
        ):
            raise AppServerProtocolError("pinned native thread context unavailable")
        _string(thread.get("sessionId"))
        for name in ("createdAt", "updatedAt"):
            if type(thread.get(name)) is not int:
                raise AppServerProtocolError("thread timestamp unavailable")
        status = _object(thread.get("status"))
        if status.get("type") not in {"idle", "active"} or status.get("activeFlags", []) != []:
            raise AppServerProtocolError("thread context failed or requests intervention")
        if (
            thread.get("modelProvider") != "openai"
            or thread.get("cwd") != self._profile.thread_params["cwd"]
            or thread.get("ephemeral") is not True
            or thread.get("turns") != []
        ):
            raise AppServerProtocolError("thread identity context mismatch")
        if thread.get("model") not in (None, self._profile.model):
            raise AppServerProtocolError("thread model changed")

    def _turn(self, turn: dict[str, object]) -> None:
        self._bind("turn", turn.get("id"))
        if turn.get("status") not in {"inProgress", "completed"} or turn.get("error") is not None:
            raise AppServerProtocolError("turn failed or unsupported")
        items = turn.get("items")
        if not isinstance(items, list):
            raise AppServerProtocolError("turn items unavailable")
        for value in items:
            item = _object(value)
            _string(item.get("id"))
            if item.get("type") not in {
                "userMessage",
                "agentMessage",
                "reasoning",
                "commandExecution",
                "fileChange",
            }:
                raise AppServerProtocolError("unsupported terminal native item")

    def _quota(self, params: dict[str, object]) -> None:
        permission = params.get("ordinaryUsageAllowed")
        if permission is not None and type(permission) is not bool:
            raise AppServerProtocolError("invalid backend ordinary usage observation")
        snapshot = _object(params.get("rateLimits"))
        snapshots = [snapshot]
        buckets = params.get("rateLimitsByLimitId")
        if buckets is not None:
            snapshots.extend(_object(value) for value in _object(buckets).values())
        for entry in snapshots:
            for name in ("primary", "secondary"):
                window = entry.get(name)
                if window is None:
                    continue
                used = _object(window).get("usedPercent")
                if type(used) is not int or not 0 <= used <= 100:
                    raise AppServerProtocolError("invalid observed quota percentage")

    def _once(self, method: str) -> None:
        if method in self._seen:
            raise AppServerProtocolError("replayed lifecycle notification")
        self._seen.add(method)

    def _notification(self, method: str, params: dict[str, object]) -> None:
        if self._next < 2:
            raise AppServerProtocolError("notification before initialization")
        if self._pending_completion:
            raise AppServerProtocolError("notification after final turn")
        if method == "account/updated":
            if (
                params.get("authMode") != "chatgpt"
                or params.get("planType") != self._profile.expected_account["planType"]
            ):
                raise AppServerProtocolError("account context changed or unavailable")
            return
        if method == "account/rateLimits/updated":
            self._quota(params)
            return
        if method == "warning":
            _string(params.get("message"))
            if params.get("threadId") is not None:
                self._linked(params, turn=False)
            return
        if method == "thread/started":
            if self._next not in {5, 6}:
                raise AppServerProtocolError("thread lifecycle outside request")
            self._once(method)
            self._thread(_object(params.get("thread")))
            return
        if method == "thread/status/changed":
            self._linked(params, turn=False)
            status = _object(params.get("status"))
            if status.get("type") not in {"idle", "active"} or status.get("activeFlags", []) != []:
                raise AppServerProtocolError("thread requests intervention or failed")
            return
        if method in {"turn/started", "turn/completed"}:
            if self._next < 6:
                raise AppServerProtocolError("turn lifecycle before turn request")
            self._linked(params, turn=False)
            self._once(method)
            turn = _object(params.get("turn"))
            self._turn(turn)
            if method == "turn/started" and turn.get("status") != "inProgress":
                raise AppServerProtocolError("started turn is not in progress")
            if method == "turn/completed":
                if (
                    turn.get("status") != "completed"
                    or self._auth_recovering
                    or self._item_started != self._item_completed
                ):
                    raise AppServerProtocolError(
                        "non-completed turn or unfinished native lifecycle"
                    )
                self._pending_completion = True
                self._completed = self._next == 7
            return
        self._linked(params, turn=True)
        if method in {"modelProvider/authRecoveryStarted", "modelProvider/authRecoveryCompleted"}:
            # Pinned AuthRecoveryEvent serializes provider.info().name, not its ID.
            if params.get("provider") != "OpenAI":
                raise AppServerProtocolError("foreign authentication provider")
            _string(params.get("message"))
            starting = method.endswith("Started")
            if starting == self._auth_recovering:
                raise AppServerProtocolError("unpaired authentication recovery")
            self._auth_recovering = starting
        elif method in {"item/started", "item/completed"}:
            item = _object(params.get("item"))
            identity = _string(item.get("id"))
            if item.get("type") not in {
                "userMessage",
                "agentMessage",
                "reasoning",
                "commandExecution",
                "fileChange",
            }:
                raise AppServerProtocolError("unsupported native tool context")
            seen = self._item_started if method == "item/started" else self._item_completed
            if identity in seen:
                raise AppServerProtocolError("replayed item lifecycle")
            if method == "item/completed" and identity not in self._item_started:
                raise AppServerProtocolError("completed item lacks started lifecycle")
            seen.add(identity)
        elif method in {
            "item/agentMessage/delta",
            "item/commandExecution/outputDelta",
            "item/fileChange/outputDelta",
            "item/reasoning/summaryTextDelta",
            "item/reasoning/textDelta",
        }:
            _string(params.get("itemId"))
            if not isinstance(params.get("delta"), str):
                raise AppServerProtocolError("invalid item delta")
        elif method == "thread/tokenUsage/updated":
            _object(params.get("tokenUsage"))
        elif method in {
            "turn/diff/updated",
            "turn/plan/updated",
            "item/reasoning/summaryPartAdded",
            "item/fileChange/patchUpdated",
        }:
            # Data only: never a tool request, execution result or release proof.
            pass
        else:
            raise AppServerProtocolError("unsupported notification")

    def _linked(self, params: dict[str, object], *, turn: bool) -> None:
        minimum = 6 if turn else 5
        if self._next < minimum or self._pending_completion:
            raise AppServerProtocolError("turn notification outside active turn")
        self._bind("thread", params.get("threadId"))
        if turn:
            self._bind("turn", params.get("turnId"))
