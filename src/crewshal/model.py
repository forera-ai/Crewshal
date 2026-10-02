"""Versioned, closed contracts; confirmation never replaces provenance."""

import hashlib
import json
from pathlib import PurePosixPath
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)

    @field_validator("schema_version", mode="before", check_fields=False)
    @classmethod
    def integer_version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("schema_version must be an integer, not a coercible value")
        return value


class Source(Contract):
    path: str
    digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    location: str

    @field_validator("path")
    @classmethod
    def relative(cls, value: str) -> str:
        path = PurePosixPath(value)
        if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
            raise ValueError("source path must be repository-relative")
        return value


class Decision(Contract):
    action: Literal["correct", "confirm", "reject", "invalidate"]
    value: str | None
    reason: str = Field(min_length=1)


class Fact(Contract):
    id: str = Field(min_length=1)
    kind: Literal["stack", "package", "boundary", "check", "tool", "sensitive", "egress"]
    value: str | None
    origin: Literal["observed", "strong_inference", "weak_inference", "unknown"]
    sources: list[Source]
    decision: Literal["pending", "confirmed", "rejected"] = "pending"
    history: list[Decision] = Field(default_factory=list)

    @field_validator("value")
    @classmethod
    def literal(cls, value: str | None) -> str | None:
        if value is not None and (not value.strip() or "\x00" in value):
            raise ValueError("fact value must be a nonempty literal without NUL")
        return value

    @model_validator(mode="after")
    def confirmation(self) -> Self:
        if self.decision == "confirmed":
            if self.value is None:
                raise ValueError("unknown value cannot be confirmed")
            if not self.history or self.history[-1].action != "confirm":
                raise ValueError("confirmation requires an explicit decision record")
            if self.history[-1].value != self.value:
                raise ValueError("confirmation must bind the current value")
        if self.origin == "unknown" and self.value is not None:
            if not any(item.action == "correct" for item in self.history):
                raise ValueError("unknown proposal requires explicit correction")
        return self


class Notice(Contract):
    path: str
    reason: str


class ProjectModel(Contract):
    schema_version: Literal[1] = 1
    project_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    inputs: list[Source]
    facts: list[Fact]
    notices: list[Notice]

    @model_validator(mode="after")
    def unique(self) -> Self:
        if len({fact.id for fact in self.facts}) != len(self.facts):
            raise ValueError("duplicate fact IDs")
        inputs = {source.path: source.digest for source in self.inputs}
        if len(inputs) != len(self.inputs):
            raise ValueError("duplicate discovery inputs")
        for fact in self.facts:
            for source in fact.sources:
                if inputs.get(source.path) != source.digest:
                    raise ValueError("fact provenance must match a discovery input")
        return self

    @property
    def unresolved(self) -> list[str]:
        return [fact.id for fact in self.facts if fact.decision == "pending"]

    def public_json(self) -> str:
        data = self.model_dump()
        return json.dumps(data, indent=2, sort_keys=True) + "\n"


class HumanDecision(Contract):
    fact_id: str
    action: Literal["correct", "confirm", "reject"]
    value: str | None = None
    reason: str = Field(min_length=1)


class DecisionBatch(Contract):
    schema_version: Literal[1]
    model_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    decisions: list[HumanDecision]


def model_digest(model: ProjectModel) -> str:
    return digest(model.model_dump_json().encode())


def decide(model: ProjectModel, decisions: list[HumanDecision]) -> ProjectModel:
    result = model.model_copy(deep=True)
    by_id = {fact.id: fact for fact in result.facts}
    for item in decisions:
        if item.fact_id not in by_id:
            raise ValueError(f"unknown fact ID: {item.fact_id}")
        fact = by_id[item.fact_id]
        data = fact.model_dump()
        if item.action == "correct":
            if not item.value or not item.value.strip() or "\x00" in item.value:
                raise ValueError("correction requires a nonempty literal value")
            data["value"] = item.value
            data["decision"] = "pending"
        else:
            if item.value is not None:
                raise ValueError("only corrections accept a value")
            if item.action == "confirm" and data["value"] is None:
                raise ValueError("correct unknown facts before confirming")
            data["decision"] = "confirmed" if item.action == "confirm" else "rejected"
        data["history"].append(
            Decision(action=item.action, value=data["value"], reason=item.reason).model_dump()
        )
        by_id[item.fact_id] = Fact.model_validate(data)
    result.facts = list(by_id.values())
    return ProjectModel.model_validate(result.model_dump())


def reconcile(fresh: ProjectModel, previous: ProjectModel | None) -> ProjectModel:
    if previous is None:
        return fresh
    if fresh.project_id != previous.project_id:
        raise ValueError("state belongs to another project")
    old = {fact.id: fact for fact in previous.facts}
    for index, fact in enumerate(fresh.facts):
        prior = old.get(fact.id)
        if prior is None:
            continue
        if fact.sources == prior.sources and fact.origin == prior.origin:
            fresh.facts[index] = prior.model_copy(deep=True)
        else:
            fact.history = [
                *prior.history,
                Decision(action="invalidate", value=fact.value, reason="dependent source changed"),
            ]
    for fact_id in sorted(old.keys() - {fact.id for fact in fresh.facts}):
        fresh.notices.append(
            Notice(path=fact_id, reason="fact removed; prior decision invalidated")
        )
    return ProjectModel.model_validate(fresh.model_dump())
