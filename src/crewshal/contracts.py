"""Closed Phase 2B records. Parsing a record never grants authority."""

from datetime import datetime
import math
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from crewshal.model import Contract, digest

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Counter = Annotated[int, Field(ge=0)]
Provider = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9.-]*$")]


class Record(Contract):
    schema_version: Literal[1] = 1
    id: Identifier


class StorageCapacityDomain(Record):
    """Installed-domain data and irreversible denial, never storage authority.

    An installed record must originate from a separately qualified producer.
    Parsing, inserting or hashing this record proves no available capacity.
    """

    installation: Digest
    state: Literal["installed", "retained"]
    memory_bytes: Literal[805306368] = 805306368
    tasks: Literal[128] = 128
    logical_bytes: Literal[8589934592] = 8589934592
    allocated_bytes: Literal[8589934592] = 8589934592
    owner: Digest | None = None
    configuration: Digest | None = None
    batch_started_monotonic: float | None = None

    @field_validator("memory_bytes", "tasks", "logical_bytes", "allocated_bytes", mode="before")
    @classmethod
    def exact_capacity_integer(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("fixed capacity charges require exact integers")
        return value

    @model_validator(mode="after")
    def capacity_state(self) -> Self:
        fields = (self.owner, self.configuration, self.batch_started_monotonic)
        if self.state == "installed":
            if any(value is not None for value in fields):
                raise ValueError("installed-domain data cannot claim an owner")
        elif (
            any(value is None for value in fields)
            or self.batch_started_monotonic is None
            or not math.isfinite(self.batch_started_monotonic)
            or self.batch_started_monotonic <= 0
        ):
            raise ValueError("retained capacity requires exact owner and original origin")
        return self


class StorageInstallationCharge(Record):
    """Upfront denial accounting, never physical installation authority.

    The original observer consumes this charge before installation effects.
    Unknown and observed terminal outcomes both retain the full reservation.
    """

    state: Literal["preparing", "retained"] = "preparing"
    installation: Literal["unknown", "observed"] = "unknown"
    memory_bytes: Literal[805306368] = 805306368
    tasks: Literal[128] = 128
    logical_bytes: Literal[8589934592] = 8589934592
    allocated_bytes: Literal[8589934592] = 8589934592
    owner: Digest
    configuration: Digest
    batch_started_monotonic: float

    @field_validator("memory_bytes", "tasks", "logical_bytes", "allocated_bytes", mode="before")
    @classmethod
    def exact_capacity_integer(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("fixed installation charges require exact integers")
        return value

    @model_validator(mode="after")
    def installation_state(self) -> Self:
        if not math.isfinite(self.batch_started_monotonic) or self.batch_started_monotonic <= 0:
            raise ValueError("installation charge requires original finite positive origin")
        if self.state == "preparing" and self.installation != "unknown":
            raise ValueError("preparing charge cannot assert observed installation")
        return self


class Binding(Contract):
    model: Digest
    task: Digest
    policy: Digest
    scope: Digest
    candidate: Digest


class CheckDefinition(Contract):
    id: Identifier
    argv: list[str] = Field(min_length=1)
    cwd: str
    environment: Digest
    toolchain: Digest

    @model_validator(mode="after")
    def literal_command(self) -> Self:
        from pathlib import PurePosixPath

        path = PurePosixPath(self.cwd)
        if not self.cwd or path.is_absolute() or ".." in path.parts or "\\" in self.cwd:
            raise ValueError("check cwd must be repository-relative")
        if not self.argv[0].strip() or any("\x00" in arg for arg in self.argv):
            raise ValueError("check argv requires executable and no NUL")
        return self


class RuntimeIdentity(Record):
    provider: Provider | None = None
    model: str | None = None

    @field_validator("model")
    @classmethod
    def model_identity(cls, value: str | None) -> str | None:
        if value is not None and (not value.strip() or value != value.strip()):
            raise ValueError("model identity must be nonempty and canonical")
        return value


class Task(Record):
    requirement: str = Field(min_length=1)
    checks: list[CheckDefinition]
    review_required: bool = True
    independent_provider: bool = True

    @model_validator(mode="after")
    def unique_checks(self) -> Self:
        if len({item.id for item in self.checks}) != len(self.checks):
            raise ValueError("duplicate required checks")
        if self.independent_provider and not self.review_required:
            raise ValueError("independence requires review")
        return self


class Run(Record):
    task_id: Identifier
    binding: Binding
    state: Literal["ready", "frozen", "validating", "verdict", "interrupted"] = "ready"


class Attempt(RuntimeIdentity):
    run_id: Identifier
    binding: Binding
    role: Literal["implementation", "review"]
    state: Literal["intent", "acknowledged", "completed", "failed", "interrupted", "cancelled"]
    handle: str | None = None
    process_exit: int | None = None
    runtime_result: Literal["completed", "failed", "unknown"] = "unknown"


class Approval(Record):
    run_id: Identifier
    binding: Binding
    owner: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class Claim(Record):
    attempt_id: Identifier
    report: str = Field(max_length=65536)


class Evidence(RuntimeIdentity):
    run_id: Identifier
    attempt_id: Identifier
    binding: Binding
    kind: Literal["check", "review", "scope"]
    gate: Identifier
    status: Literal["passed", "failed", "skipped", "unavailable", "terminated"]
    definition: CheckDefinition | None = None
    started: datetime
    ended: datetime
    exit_code: int | None = None
    termination: Literal["timeout", "cancelled", "quota", "signal", "interrupted"] | None = None
    stdout: Digest | None = None
    stderr: Digest | None = None
    artifacts: list[Digest] = Field(default_factory=list)
    blocking_findings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def capture_consistency(self) -> Self:
        if self.started.tzinfo is None or self.ended.tzinfo is None:
            raise ValueError("capture times require timezone")
        if self.ended < self.started:
            raise ValueError("capture end precedes start")
        if self.status == "passed":
            if self.termination is not None or self.stdout is None or self.stderr is None:
                raise ValueError("passing evidence requires logs and no termination")
            if self.kind == "check" and (self.exit_code != 0 or self.definition is None):
                raise ValueError("passing check requires definition and zero exit")
            if self.kind != "check" and self.exit_code is not None:
                raise ValueError("non-command evidence cannot claim an exit code")
            if self.blocking_findings:
                raise ValueError("blocking findings contradict passing evidence")
        if self.status == "terminated" and self.termination is None:
            raise ValueError("terminated evidence requires reason")
        return self


class Waiver(Record):
    run_id: Identifier
    binding: Binding
    gate: Identifier
    owner: str = Field(min_length=1)
    residual_risk: str = Field(min_length=1)


class Verdict(Record):
    run_id: Identifier
    binding: Binding
    status: Literal[
        "verified", "accepted_with_waiver", "blocked", "failed", "interrupted", "cancelled"
    ]
    gates: dict[str, str]
    evidence_ids: list[str]
    waiver_ids: list[str]
    # Phase 2B is deliberately incapable of granting execution.
    execution_allowed: Literal[False] = False


class Usage(Record):
    attempt_id: Identifier
    event_id: Identifier
    sequence: Counter
    provenance: Literal["runtime_reported", "provider_measured"]
    input_tokens: Counter | None = None
    cached_input_tokens: Counter | None = None
    cache_write_tokens: Counter | None = None
    output_tokens: Counter | None = None
    reasoning_tokens: Counter | None = None
    measured_cost_microusd: Counter | None = None
    estimated_cost_microusd: Counter | None = None
    subscription_quota: Counter | None = None


def record_digest(record: Contract) -> str:
    return digest(record.model_dump_json().encode())


USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "measured_cost_microusd",
    "estimated_cost_microusd",
    "subscription_quota",
)


def cumulative_usage(attempt_ids: list[str], events: list[Usage]) -> dict[str, int | None]:
    """Latest cumulative snapshot per attempt, never sum repeated cumulative reports."""
    unique: dict[tuple[str, str], Usage] = {}
    latest: dict[str, Usage] = {}
    sequences: dict[tuple[str, int], Usage] = {}
    for event in events:
        key = (event.attempt_id, event.event_id)
        if event.attempt_id not in attempt_ids:
            raise ValueError("usage belongs to an unknown attempt")
        if key in unique and unique[key] != event:
            raise ValueError("conflicting usage replay")
        sequence_key = (event.attempt_id, event.sequence)
        if sequence_key in sequences and sequences[sequence_key] != event:
            raise ValueError("conflicting usage sequence")
        sequences[sequence_key] = event
        unique[key] = event
        if event.attempt_id not in latest or latest[event.attempt_id].sequence < event.sequence:
            latest[event.attempt_id] = event
    for attempt_id in attempt_ids:
        ordered = sorted(
            (event for event in unique.values() if event.attempt_id == attempt_id),
            key=lambda event: event.sequence,
        )
        for field in USAGE_FIELDS:
            known: int | None = None
            for event in ordered:
                value = getattr(event, field)
                if value is not None:
                    if known is not None and value < known:
                        raise ValueError("cumulative usage decreased")
                    known = value
    result: dict[str, int | None] = {}
    for field in USAGE_FIELDS:
        values = [getattr(latest[item], field) if item in latest else None for item in attempt_ids]
        result[field] = (
            None
            if any(value is None for value in values)
            else sum(value for value in values if value is not None)
        )
    return result
