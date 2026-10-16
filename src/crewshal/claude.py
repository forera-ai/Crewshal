"""Normalize bounded Claude Code streams. This module cannot start a process."""

import json
from typing import Literal

from pydantic import Field, model_validator

from crewshal.contracts import (
    Attempt,
    Binding,
    Claim,
    Digest,
    Identifier,
    Provider,
    Task,
    record_digest,
)
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import _json
from crewshal.runtime import (
    MAX_EVENTS,
    STREAM_BYTES,
    CodexIdentity,
    CodexRequest,
    NativeEvent,
    ProcessObservation,
    RuntimeOutcome,
    _usage,
    normalize_codex,
    prepare_codex_contract,
)


class ClaudeIdentity(Contract):
    runtime: Literal["claude"]
    version: Literal["2.1.278"]
    provider: Provider
    model: Identifier
    configuration: Digest
    native_interface: Literal["stream_json"] = "stream_json"

    @model_validator(mode="after")
    def canonical(self) -> "ClaudeIdentity":
        if self.model.strip() != self.model or not self.model.strip():
            raise ValueError("model identity must be canonical")
        return self


class ClaudeRequest(Contract):
    schema_version: Literal[1] = 1
    attempt_id: Identifier
    binding: Binding
    identity: ClaudeIdentity
    requirement: str = Field(min_length=1, max_length=65536)
    deadline_seconds: Literal[5] = 5
    stream_bytes: Literal[65536] = 65536
    execution_allowed: Literal[False] = False


def prepare_claude_contract(
    task: Task,
    attempt: Attempt,
    current: Binding,
    identity: ClaudeIdentity,
    *,
    role: Literal["implementation", "review"] = "implementation",
) -> ClaudeRequest:
    """Return checked request data without execution authority."""
    task = Task.model_validate_json(task.model_dump_json())
    attempt = Attempt.model_validate_json(attempt.model_dump_json())
    current = Binding.model_validate_json(current.model_dump_json())
    identity = ClaudeIdentity.model_validate_json(identity.model_dump_json())
    if (
        attempt.binding != current
        or current.task != record_digest(task)
        or attempt.role != role
        or attempt.state != "intent"
        or attempt.handle is not None
        or attempt.process_exit is not None
        or attempt.runtime_result != "unknown"
        or attempt.provider != identity.provider
        or attempt.model != identity.model
    ):
        raise ValueError("request requires current task, identity and unused intent")
    return ClaudeRequest(
        attempt_id=attempt.id,
        binding=current,
        identity=identity,
        requirement=task.requirement,
    )


def normalize_claude(
    attempt: Attempt,
    current: Binding,
    identity: ClaudeIdentity,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
    *,
    expected_configuration: str | None = None,
    role: Literal["implementation", "review"] = "implementation",
) -> RuntimeOutcome:
    """Keep runtime reports separate from trusted process observations and evidence.

    This strict stream subset requires an init event and one terminal result.
    Other event types fail closed until their conformance checks exist.
    Resolved provider identity comes from the trusted adapter configuration.
    A stream cannot establish provider identity or change that configuration.
    """
    attempt = Attempt.model_validate_json(attempt.model_dump_json())
    current = Binding.model_validate_json(current.model_dump_json())
    identity = ClaudeIdentity.model_validate_json(identity.model_dump_json())
    observation = ProcessObservation.model_validate_json(observation.model_dump_json())

    def result(status: str, **data: object) -> RuntimeOutcome:
        state = (
            "completed"
            if status == "completed"
            else "cancelled"
            if status == "cancelled"
            else "interrupted"
            if status in {"interrupted", "incomplete_capture"}
            else "failed"
        )
        terminal = Attempt.model_validate(
            {
                **attempt.model_dump(),
                "state": state,
                "process_exit": observation.exit_code,
                "runtime_result": "completed" if status == "completed" else "failed",
            }
        )
        return RuntimeOutcome.model_validate({"status": status, "attempt": terminal, **data})

    if attempt.binding != current or identity.configuration != expected_configuration:
        return result("stale")
    if (
        attempt.state != "acknowledged"
        or not attempt.handle
        or attempt.role != role
        or attempt.provider != identity.provider
        or attempt.model != identity.model
    ):
        return result("identity_unavailable")
    if len(stdout) > STREAM_BYTES or len(stderr) > STREAM_BYTES:
        return result("capture_limit")
    if not all(
        (observation.stdout_complete, observation.stderr_complete, observation.tree_stopped)
    ):
        return result("incomplete_capture")
    if observation.termination is not None:
        return result(observation.termination)
    if observation.elapsed_seconds > 5:
        return result("timeout")
    if observation.exit_code is None or not stdout.endswith(b"\n"):
        return result("incomplete_capture")
    if observation.exit_code != 0:
        return result("failed")
    events: list[NativeEvent] = []
    claims: list[Claim] = []
    session: str | None = None
    terminal = False
    identifiers: set[str] = set()
    active_tools: set[str] = set()
    finished_tools: set[str] = set()
    tool_failed = False
    try:
        lines = stdout.splitlines()
        if not lines or len(lines) > MAX_EVENTS:
            raise ValueError("event count outside bound")
        for sequence, line in enumerate(lines):
            data = _json(line)
            if not isinstance(data, dict) or terminal:
                raise ValueError("event after terminal or malformed object")
            kind = data.get("type")
            if not isinstance(kind, str):
                raise ValueError("missing event type")
            if sequence == 0:
                if (
                    kind != "system"
                    or data.get("subtype") != "init"
                    or not isinstance(data.get("session_id"), str)
                    or not data["session_id"]
                    or data.get("model") != identity.model
                ):
                    return result("identity_unavailable")
                session = data["session_id"]
            elif data.get("session_id") != session:
                raise ValueError("session identity changed")
            elif kind in {"assistant", "user"}:
                message = data.get("message")
                if not isinstance(message, dict) or not isinstance(message.get("content"), list):
                    raise ValueError("missing assistant content")
                for block in message["content"]:
                    if not isinstance(block, dict):
                        raise ValueError("unsupported assistant content")
                    block_type = block.get("type")
                    if kind == "assistant" and block_type == "text":
                        report = block.get("text")
                        if not isinstance(report, str):
                            raise ValueError("missing assistant text")
                    elif kind == "assistant" and block_type == "tool_use":
                        tool_id = block.get("id")
                        if (
                            not isinstance(tool_id, str)
                            or not tool_id
                            or tool_id in active_tools | finished_tools
                            or not isinstance(block.get("name"), str)
                            or not isinstance(block.get("input"), dict)
                        ):
                            raise ValueError("missing or replayed tool identity")
                        active_tools.add(tool_id)
                        report = json.dumps(block, sort_keys=True)
                    elif kind == "user" and block_type == "tool_result":
                        tool_id = block.get("tool_use_id")
                        if (
                            not isinstance(tool_id, str)
                            or tool_id not in active_tools
                            or not isinstance(block.get("content"), (str, list))
                            or type(block.get("is_error", False)) is not bool
                        ):
                            raise ValueError("unknown or malformed tool result")
                        active_tools.remove(tool_id)
                        finished_tools.add(tool_id)
                        tool_failed |= block.get("is_error", False)
                        report = json.dumps(block, sort_keys=True)
                    elif kind == "assistant" and block_type in {"thinking", "redacted_thinking"}:
                        # Preserve the bounded raw event without deriving authority or usage.
                        continue
                    else:
                        raise ValueError("unsupported native content block")
                    claims.append(
                        Claim(
                            id=f"claude:{digest(attempt.id.encode())}:{sequence}:{len(claims)}",
                            attempt_id=attempt.id,
                            report=report,
                        )
                    )
            elif kind == "result":
                if active_tools:
                    raise ValueError("terminal result leaves an unfinished tool")
                if type(data.get("is_error")) is not bool:
                    raise ValueError("missing terminal error status")
                if data["is_error"] or data.get("subtype") != "success" or tool_failed:
                    return result("failed", events=events, claims=claims)
                report = data.get("result")
                if not isinstance(report, str) or not report.strip():
                    raise ValueError("missing final result")
                claims.append(
                    Claim(
                        id=f"claude:{digest(attempt.id.encode())}:{sequence}:result",
                        attempt_id=attempt.id,
                        report=report,
                    )
                )
                raw_usage = data.get("usage", {})
                if not isinstance(raw_usage, dict):
                    raise ValueError("usage must be an object")
                mapping = {
                    "input_tokens": "input_tokens",
                    "output_tokens": "output_tokens",
                    "cache_read_input_tokens": "cached_input_tokens",
                    "cache_creation_input_tokens": "cache_write_input_tokens",
                }
                usage = _usage(
                    {mapping[key]: value for key, value in raw_usage.items() if key in mapping},
                    attempt,
                    sequence,
                )
                terminal = True
            else:
                raise ValueError("unsupported native event type")
            identifier = data.get("uuid")
            if not isinstance(identifier, str) or not identifier or identifier in identifiers:
                raise ValueError("missing or replayed event identity")
            identifiers.add(identifier)
            events.append(
                NativeEvent(
                    attempt_id=attempt.id,
                    sequence=sequence,
                    type=kind,
                    payload=data,
                )
            )
        if not terminal:
            return result("incomplete_capture", events=events, claims=claims)
        return result("completed", events=events, claims=claims, usage=usage)
    except (ValueError, UnicodeError, RecursionError, TypeError):
        return result("malformed")


RuntimeRequest = CodexRequest | ClaudeRequest
RuntimeIdentity = CodexIdentity | ClaudeIdentity


def prepare_runtime_contract(
    task: Task,
    attempt: Attempt,
    current: Binding,
    identity: RuntimeIdentity,
    *,
    role: Literal["implementation", "review"] = "implementation",
) -> RuntimeRequest:
    if isinstance(identity, CodexIdentity):
        return prepare_codex_contract(task, attempt, current, identity, role=role)
    return prepare_claude_contract(task, attempt, current, identity, role=role)


def normalize_runtime(
    attempt: Attempt,
    current: Binding,
    identity: RuntimeIdentity,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
    *,
    expected_configuration: str,
    role: Literal["implementation", "review"] = "implementation",
) -> RuntimeOutcome:
    if isinstance(identity, CodexIdentity):
        return normalize_codex(
            attempt,
            current,
            identity,
            observation,
            stdout,
            stderr,
            expected_configuration=expected_configuration,
            role=role,
        )
    return normalize_claude(
        attempt,
        current,
        identity,
        observation,
        stdout,
        stderr,
        expected_configuration=expected_configuration,
        role=role,
    )
