"""Synthetic qualification records. No record or result authorizes execution."""

from typing import Literal

from pydantic import Field

from crewshal.contracts import Digest, Identifier, Record
from crewshal.model import Contract

MANDATORY_CASES = (
    "allowed-grant",
    "external-read",
    "external-write",
    "original-checkout",
    "coordinator-state",
    "symlink-escape",
    "new-file-escape",
    "metadata-escape",
    "network-egress",
    "environment-credentials",
    "repository-hooks",
    "global-hooks",
    "mcp-plugins-instructions",
    "descendant-escape",
    "cancellation",
    "deadline",
    "credential-mediation",
    "credential-free-validation",
    "configuration-binding",
    "qualification-refusal",
)


class QualificationIdentity(Contract):
    host_os: Identifier
    host_kernel: Identifier
    architecture: Identifier
    substrate: Identifier
    substrate_version: Identifier | None = None
    image: Digest | None = None
    runtime: Identifier | None = None
    toolchain: Digest
    configuration: Digest
    grant: Digest
    harness: Digest
    manifest: Digest
    credential_design: Digest | None = None


class ProbeResult(Contract):
    case: Identifier
    status: Literal["passed", "failed", "unavailable"]
    observation: str = Field(min_length=1, max_length=65536)


class Qualification(Record):
    identity: QualificationIdentity
    results: list[ProbeResult] = Field(max_length=100)
    execution_allowed: Literal[False] = False


class QualificationDecision(Contract):
    status: Literal["denied", "qualified_for_later_authorization"]
    reasons: list[str]
    execution_allowed: Literal[False] = False


def assess_qualification(
    record: Qualification | None, current: QualificationIdentity
) -> QualificationDecision:
    """Trusted coordinator input only; not a worker import or execution gate."""
    reasons = []
    if record is None:
        reasons.append("missing qualification")
    else:
        # Revalidate even when a trusted caller used model_construct/model_copy.
        record = Qualification.model_validate_json(record.model_dump_json())
        current = QualificationIdentity.model_validate_json(current.model_dump_json())
        if record.identity != current:
            reasons.append("stale qualification identity")
        if any(
            getattr(current, name) is None
            for name in ("substrate_version", "image", "runtime", "credential_design")
        ):
            reasons.append("unresolved substrate/runtime/credential design")
        names = [item.case for item in record.results]
        if len(names) != len(set(names)):
            reasons.append("duplicate probe results")
        if set(names) != set(MANDATORY_CASES):
            reasons.append("mandatory case set mismatch")
        reasons.extend(
            f"{item.case}: {item.status}" for item in record.results if item.status != "passed"
        )
    return QualificationDecision(
        status="denied" if reasons else "qualified_for_later_authorization",
        reasons=reasons,
    )
