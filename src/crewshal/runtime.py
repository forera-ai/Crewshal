"""Bounded Codex event/terminal seam. No subprocess, tool loop or launch authority.

All identities and process observations come from the trusted coordinator. Native
stdout, including command exits and assistant prose, supplies claims only.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Literal, Self

from pydantic import Field, ValidationError, model_validator

from crewshal.contracts import Attempt, Binding, Claim, Digest, Identifier, Provider, Usage
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import _json

if TYPE_CHECKING:
    from crewshal.contracts import Task
    from crewshal.qualification import Qualification, QualificationIdentity

STREAM_BYTES = 65536
MAX_EVENTS = 1024


class CodexIdentity(Contract):
    runtime: Literal["codex"]
    version: Literal["0.160.1"]
    provider: Provider
    model: Identifier
    configuration: Digest

    @model_validator(mode="after")
    def canonical(self) -> Self:
        if self.model.strip() != self.model or not self.model.strip():
            raise ValueError("model identity must be canonical")
        return self


class ProcessObservation(Contract):
    """Trusted complete capture/stop observations, never parsed from worker output."""

    started: datetime
    ended: datetime
    elapsed_seconds: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    exit_code: int | None
    termination: (
        Literal["timeout", "cancelled", "quota", "refusal", "signal", "interrupted"] | None
    ) = None
    stdout_complete: bool
    stderr_complete: bool
    tree_stopped: bool

    @model_validator(mode="after")
    def times(self) -> Self:
        if self.started.tzinfo is None or self.ended.tzinfo is None or self.ended < self.started:
            raise ValueError("process capture requires ordered timezone-aware times")
        return self


class NativeEvent(Contract):
    attempt_id: Identifier
    sequence: int = Field(ge=0)
    type: Identifier
    payload: dict[str, object]


class RuntimeOutcome(Contract):
    status: Literal[
        "completed",
        "failed",
        "malformed",
        "identity_unavailable",
        "stale",
        "capture_limit",
        "incomplete_capture",
        "timeout",
        "cancelled",
        "quota",
        "refusal",
        "signal",
        "interrupted",
    ]
    attempt: Attempt
    events: list[NativeEvent] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    usage: Usage | None = None
    execution_allowed: Literal[False] = False


def _keys(value: object, required: set[str], optional: set[str] | None = None) -> dict[str, object]:
    if not isinstance(value, dict) or not required <= value.keys():
        raise ValueError("missing event fields")
    if value.keys() - required - (optional or set()):
        raise ValueError("unknown event fields")
    return value


def _string(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError("missing or malformed event identity")
    return value


def _text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("event text must be a string")
    return value


def _usage(value: object, attempt: Attempt, sequence: int) -> Usage:
    fields = {
        "input_tokens": "input_tokens",
        "cached_input_tokens": "cached_input_tokens",
        "cache_write_input_tokens": "cache_write_tokens",
        "output_tokens": "output_tokens",
        "reasoning_output_tokens": "reasoning_tokens",
    }
    data = _keys(value, set(), set(fields))
    counters: dict[str, int] = {}
    for key, number in data.items():
        if type(number) is not int or number < 0:
            raise ValueError("usage requires nonnegative integer counters")
        counters[fields[key]] = number
    return Usage.model_validate(
        {
            "id": f"usage:{digest(attempt.id.encode())}:{sequence}",
            "attempt_id": attempt.id,
            "event_id": f"native:{sequence}",
            "sequence": sequence,
            "provenance": "runtime_reported",
            **counters,
        }
    )


def normalize_codex(
    attempt: Attempt,
    current: Binding,
    identity: CodexIdentity,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
    *,
    expected_configuration: str | None = None,
) -> RuntimeOutcome:
    """Normalize one recorded native turn; completion is not a project verdict.

    The caller binds the effective configuration separately. This is not a runtime
    identity probe, isolation observation or provider billing attestation.
    """
    attempt = Attempt.model_validate_json(attempt.model_dump_json())
    current = Binding.model_validate_json(current.model_dump_json())
    identity = CodexIdentity.model_validate_json(identity.model_dump_json())
    observation = ProcessObservation.model_validate_json(observation.model_dump_json())

    def result(status: str, **data: object) -> RuntimeOutcome:
        state = (
            "completed"
            if status == "completed"
            else (
                "cancelled"
                if status == "cancelled"
                else "interrupted"
                if status in {"interrupted", "incomplete_capture"}
                else "failed"
            )
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

    if attempt.binding != current or (
        expected_configuration is None or identity.configuration != expected_configuration
    ):
        # A configuration must be supplied independently, not inferred from this stream.
        return result("stale")
    if (
        attempt.state != "acknowledged"
        or not attempt.handle
        or attempt.role != "implementation"
        or not attempt.provider
        or not attempt.model
        or attempt.provider != identity.provider
        or attempt.model != identity.model
    ):
        return result("identity_unavailable")
    if len(stdout) > STREAM_BYTES or len(stderr) > STREAM_BYTES:
        return result("capture_limit")
    if (
        not observation.stdout_complete
        or not observation.stderr_complete
        or not observation.tree_stopped
    ):
        return result("incomplete_capture")
    if observation.termination is not None:
        return result(observation.termination)
    if observation.elapsed_seconds > 5.0:
        return result("timeout")
    if observation.exit_code is None:
        return result("incomplete_capture")
    if observation.exit_code != 0:
        return result("failed")
    if not stdout.endswith(b"\n"):
        return result("incomplete_capture")
    normalized: list[NativeEvent] = []
    claims: list[Claim] = []
    usage: Usage | None = None
    started = False
    turn = False
    terminal = False
    final_message = False
    failed = False
    active: dict[str, tuple[str, str | None]] = {}
    finished: set[str] = set()
    try:
        lines = stdout.splitlines()
        if not lines or len(lines) > MAX_EVENTS:
            raise ValueError("event count outside bound")
        for sequence, line in enumerate(lines):
            data = _json(line)
            if not isinstance(data, dict) or terminal:
                raise ValueError("event after terminal or malformed object")
            kind = _string(data.get("type"))
            if kind == "thread.started":
                data = _keys(data, {"type", "thread_id"})
                _string(data["thread_id"])
                if started or sequence != 0:
                    raise ValueError("duplicate or reordered thread")
                started = True
            elif not started:
                raise ValueError("thread identity missing")
            elif kind == "turn.started":
                _keys(data, {"type"})
                if turn:
                    raise ValueError("duplicate turn")
                turn = True
            elif kind in {"turn.completed", "turn.failed"}:
                if not turn or active:
                    raise ValueError("incomplete turn or items")
                if kind == "turn.completed":
                    _keys(data, {"type"}, {"usage"})
                    if "usage" in data:
                        usage = _usage(data["usage"], attempt, sequence)
                    if not final_message:
                        raise ValueError("missing final result")
                else:
                    _keys(data, {"type", "error"})
                    error = _keys(data["error"], {"message"})
                    _text(error["message"])
                    failed = True
                terminal = True
            elif kind == "error":
                _keys(data, {"type", "message"})
                _text(data["message"])
                failed = True
            elif kind in {"item.started", "item.updated", "item.completed"}:
                _keys(data, {"type", "item"})
                item = data["item"]
                if not isinstance(item, dict):
                    raise ValueError("item must be an object")
                item_id, item_type = _string(item.get("id")), _string(item.get("type"))
                command: str | None = None
                if item_type == "command_execution":
                    _keys(
                        item, {"id", "type", "command", "aggregated_output", "exit_code", "status"}
                    )
                    command = _string(item["command"])
                    report = _text(item["aggregated_output"])
                    exit_code, status = item["exit_code"], item["status"]
                    if exit_code is not None and type(exit_code) is not int:
                        raise ValueError("command exit must be an integer")
                    if kind == "item.completed":
                        if status not in {"completed", "failed"} or exit_code is None:
                            raise ValueError("incomplete command result")
                        failed |= status == "failed" or exit_code != 0
                    elif status != "in_progress" or exit_code is not None:
                        raise ValueError("invalid running command")
                elif item_type in {"agent_message", "reasoning"}:
                    _keys(item, {"id", "type", "text"})
                    report = _text(item["text"])
                    if item_type == "agent_message" and kind == "item.completed":
                        final_message = bool(report.strip())
                elif item_type == "error":
                    _keys(item, {"id", "type", "message"})
                    report = _text(item["message"])
                    failed = True
                else:
                    raise ValueError("unsupported native item type")
                if not turn and item_type != "error":
                    raise ValueError("item before turn")
                if item_id in finished:
                    raise ValueError("replayed completed item")
                if kind == "item.started":
                    if item_id in active:
                        raise ValueError("replayed started item")
                    active[item_id] = (item_type, command)
                elif kind == "item.updated":
                    if active.get(item_id) != (item_type, command):
                        raise ValueError("unknown or changed item")
                else:
                    if item_id in active and active[item_id] != (item_type, command):
                        raise ValueError("changed item identity")
                    if item_type == "command_execution" and item_id not in active:
                        raise ValueError("command completion without start")
                    active.pop(item_id, None)
                    finished.add(item_id)
                    if item_type != "error":
                        claims.append(
                            Claim(
                                id=f"claim:{digest(attempt.id.encode())}:{sequence}",
                                attempt_id=attempt.id,
                                report=report,
                            )
                        )
            else:
                raise ValueError("unsupported native event type")
            normalized.append(
                NativeEvent(attempt_id=attempt.id, sequence=sequence, type=kind, payload=data)
            )
    except (ValueError, ValidationError, RecursionError, UnicodeError):
        return result("malformed")
    if failed:
        return result("failed", events=normalized, claims=claims)
    if not terminal:
        return result("incomplete_capture", events=normalized, claims=claims)
    return result("completed", events=normalized, claims=claims, usage=usage)


class CodexRequest(Contract):
    """Inert task bundle for the qualified native CLI; not a launch command."""

    schema_version: Literal[1] = 1
    attempt_id: Identifier
    binding: Binding
    identity: CodexIdentity
    requirement: str = Field(min_length=1, max_length=65536)
    deadline_seconds: Literal[5] = 5
    stream_bytes: Literal[65536] = 65536
    execution_allowed: Literal[False] = False


def prepare_codex_request(
    task: "Task",
    attempt: Attempt,
    current: Binding,
    identity: CodexIdentity,
    qualification: "Qualification | None",
    current_qualification: "QualificationIdentity",
) -> CodexRequest:
    """Build data only after exact identity checks; still requires an execution gate.

    Qualification must be supplied through the trusted coordinator. The live
    launcher/authority record and profile reproduction are intentionally pending;
    this API cannot use qualification as permission or replay a fixture driver.
    """
    from crewshal.contracts import Task, record_digest
    from crewshal.qualification import Qualification, QualificationIdentity, assess_qualification

    task = Task.model_validate_json(task.model_dump_json())
    attempt = Attempt.model_validate_json(attempt.model_dump_json())
    current = Binding.model_validate_json(current.model_dump_json())
    identity = CodexIdentity.model_validate_json(identity.model_dump_json())
    current_qualification = QualificationIdentity.model_validate_json(
        current_qualification.model_dump_json()
    )
    if qualification is not None:
        qualification = Qualification.model_validate_json(qualification.model_dump_json())
    if (
        assess_qualification(qualification, current_qualification).status
        != "qualified_for_later_authorization"
    ):
        raise ValueError("missing, stale or failed qualification")
    if (
        current_qualification.host_os != "linux"
        or current_qualification.architecture != "aarch64"
        or current_qualification.runtime != f"codex-rust-v{identity.version}"
        or current_qualification.configuration != identity.configuration
    ):
        raise ValueError("runtime/configuration/platform differs from qualified profile")
    if (
        attempt.binding != current
        or current.task != record_digest(task)
        or attempt.role != "implementation"
        or attempt.state != "intent"
        or attempt.handle is not None
        or attempt.process_exit is not None
        or attempt.runtime_result != "unknown"
        or attempt.provider != identity.provider
        or attempt.model != identity.model
    ):
        raise ValueError("task, attempt or provider/model identity is stale or unresolved")
    return CodexRequest(
        attempt_id=attempt.id, binding=current, identity=identity, requirement=task.requirement
    )
