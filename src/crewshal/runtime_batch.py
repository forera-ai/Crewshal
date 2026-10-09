"""Materialize the single Phase 2D preparation bundle; never dispatch a runtime."""

import json
import os
from pathlib import Path
import stat
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator

from crewshal.candidate import FrozenCandidate, _scan, prepare_candidate
from crewshal.contracts import Digest, Identifier, Provider, record_digest
from crewshal.durable import private_path
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import BoundArtifact, _json, _Reader

MODEL_SOURCE: Literal["https://developers.openai.com/api/docs/models/gpt-6.1-sol"] = (
    "https://developers.openai.com/api/docs/models/gpt-6.1-sol"
)
BEFORE = b"phase-2d-before\n"
AFTER = b"phase-2d-after\n"
REQUIREMENT = "Replace README.md content with exactly phase-2d-after followed by one newline. Change no other path."
CHECK_SOURCE = b'''"""Trusted synthetic Phase 2D byte check; no imports from candidate."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("phase-2d-check: candidate path required", file=sys.stderr)
    raise SystemExit(2)
try:
    actual = (Path(sys.argv[1]) / "README.md").read_bytes()
except OSError:
    print("phase-2d-check: README unavailable", file=sys.stderr)
    raise SystemExit(1)
if actual != b"phase-2d-after\\n":
    print("phase-2d-check: README bytes differ", file=sys.stderr)
    raise SystemExit(1)
print("phase-2d-check: passed")
'''


class PreparationSelection(Contract):
    """Explicit project/session choices, not availability, credentials or authority.

    No ambient configuration is consulted. A destination is requested data egress,
    not an approved route; billing and credential labels are not enforcement.
    """

    schema_version: Literal[1] = 1
    project: Identifier
    session: Identifier
    model: Identifier
    provider: Provider | None = None
    destination: str | None = Field(default=None, max_length=2048)
    billing_mode: Literal["unresolved", "api_metered", "subscription_quota"] = "unresolved"
    credential_treatment: Literal["unresolved", "external_scoped_channel"] = "unresolved"

    @field_validator("project", "session", "model")
    @classmethod
    def canonical_label(cls, value: str) -> str:
        if not value.strip() or value.strip() != value or not value.isprintable():
            raise ValueError("selection labels must be canonical printable literals")
        if value.startswith("-"):
            raise ValueError("selection labels must not be command options")
        return value

    @field_validator("destination")
    @classmethod
    def public_destination(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if any(char.isspace() or not char.isprintable() for char in value):
            raise ValueError("destination must be a literal HTTPS endpoint")
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or "\\" in value
        ):
            raise ValueError("destination requires HTTPS without credentials, query or fragment")
        # Access validates a malformed/out-of-range port without making a request.
        _ = parsed.port
        return value


class BatchPreparation(Contract):
    schema_version: Literal[1] = 1
    milestone: Literal["2D"] = "2D"
    owner_model_label: Literal["Sol6.1"] | None = "Sol6.1"
    mode: Literal["batch_preparation_only"] = "batch_preparation_only"
    documented_model: Literal["gpt-6.1-sol"] | None = "gpt-6.1-sol"
    model_source: Literal["https://developers.openai.com/api/docs/models/gpt-6.1-sol"] | None = (
        "https://developers.openai.com/api/docs/models/gpt-6.1-sol"
    )
    native_runtime: Literal["codex-rust-v0.160.1"] = "codex-rust-v0.160.1"
    selection: PreparationSelection | None = None
    artifacts: list[BoundArtifact] = Field(min_length=1, max_length=32)
    historical_references: list[BoundArtifact] = Field(min_length=1, max_length=32)
    unresolved: list[str] = Field(min_length=1)
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False

    @model_validator(mode="after")
    def selection_and_paths(self) -> "BatchPreparation":
        for items in (self.artifacts, self.historical_references):
            names = [item.path.casefold() for item in items]
            if len(names) != len(set(names)):
                raise ValueError("preparation artifact paths must be unique")
        if self.selection is not None:
            if self.owner_model_label is not None:
                raise ValueError("explicit selection must not inherit owner model label")
            known_model = self.selection.model == "gpt-6.1-sol"
            if self.documented_model != ("gpt-6.1-sol" if known_model else None) or (
                self.model_source != (MODEL_SOURCE if known_model else None)
            ):
                raise ValueError("model documentation does not match selection")
        return self


def prepare_runtime_batch(
    reference_root: Path,
    output: Path,
    references: list[BoundArtifact],
    *,
    selection: PreparationSelection | None = None,
) -> BatchPreparation:
    """Produce reviewable fixture/check/template data in a new private directory.

    Historical references supply byte continuity only. They never qualify this new
    model/upstream/dispatch identity. No authority file or credential is imported.
    """
    if selection is not None:
        selection = PreparationSelection.model_validate_json(selection.model_dump_json())
    selected_model = selection.model if selection is not None else "gpt-6.1-sol"
    if output.exists() or output.is_symlink():
        raise ValueError("preparation output must not exist")
    source = reference_root.resolve(strict=True)
    output = output.parent.resolve(strict=True) / output.name
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError("preparation must be outside reference checkout")
    references = [BoundArtifact.model_validate_json(item.model_dump_json()) for item in references]
    names = [item.path.casefold() for item in references]
    if not references or len(references) > 32 or len(names) != len(set(names)):
        raise ValueError("historical reference set must be nonempty, bounded and unique")
    reader = _Reader(source)
    # Verify all references before writing. No declared code is executed.
    for reference in references:
        reader.bound(reference)
    output.mkdir(mode=0o700)
    private_path(output)
    original = output / "original"
    original.mkdir(mode=0o700)
    (original / "README.md").write_bytes(BEFORE)
    (original / "dirty-marker.txt").write_bytes(b"original uncommitted marker\n")
    (original / ".git").mkdir(mode=0o700)
    (original / ".git" / "fixture-metadata").write_bytes(b"synthetic original metadata\n")
    initial = prepare_candidate(original, output / "candidate", ["README.md"])
    fixture = {
        "requirement": REQUIREMENT,
        "included_paths": ["README.md"],
        "writable_paths": ["README.md"],
        "initial_candidate_sha256": record_digest(initial),
        "expected_readme_sha256": digest(AFTER),
        "original_integrity": {
            "README.md": digest(BEFORE),
            "dirty-marker.txt": digest(b"original uncommitted marker\n"),
            ".git/fixture-metadata": digest(b"synthetic original metadata\n"),
        },
        "live_repository_git_identity": None,
        "review_required": False,
        "risk_reason": "synthetic documentation-only exact-byte task",
        "execution_allowed": False,
    }
    limits = {
        "worker_and_validator": {
            "memory_bytes": 134217728,
            "swap_bytes": 0,
            "cpu_count": 1,
            "tasks": 32,
            "deadline_seconds": 5,
            "stop_grace_seconds": 1,
        },
        "aggregate": {
            "memory_bytes": 805306368,
            "swap_bytes": 0,
            "cpu_count": 1,
            "tasks": 128,
            "logical_disk_bytes": 8589934592,
            "allocated_disk_bytes": 8589934592,
        },
        "candidate_bytes": 16777216,
        "scratch_bytes": 33554432,
        "stream_bytes": 65536,
        "capture_seconds": 10,
        "startup_seconds": 120,
        "batch_seconds": 600,
        "cleanup_reserve_seconds": 30,
        "implementation_attempts": 1,
        "automatic_retries": 0,
        "execution_allowed": False,
    }
    dispatch = {
        "status": "template_not_launchable",
        "mechanisms": [
            "systemd/cgroup-v2",
            "nsenter",
            "bubblewrap",
            "setpriv",
            "native Codex sandbox",
            "official fixed-upstream Responses proxy",
        ],
        "native_tail": [
            "/opt/codex/bin/codex",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--color",
            "never",
            "--json",
            "-C",
            "/scratch/checkout",
            "--add-dir",
            "/candidate/owned",
            "--add-dir",
            "/scratch",
            "-s",
            "workspace-write",
            "-m",
            selected_model,
        ],
        "task_stdin": REQUIREMENT + "\n",
        "validator_argv": [
            "/bin/python3",
            "-I",
            "-B",
            "/input/check_fixture.py",
            "/candidate/owned",
        ],
        "validator_cwd": ".",
        "required_native_configuration": {
            "request_max_retries": 0,
            "stream_max_retries": 0,
            "inherited_configuration": False,
            "hooks": False,
            "plugins": False,
            "mcp": False,
            "skills": False,
            "global_instructions": False,
            "login_shell": False,
            "additional_agents": False,
            "web_search": False,
        },
        "required_validator_authority": {
            "uid": 65531,
            "readonly_candidate": True,
            "separate_scratch": True,
            "credential_free": True,
            "network_disabled": True,
        },
        "production_envelope_argv": None,
        "loaded_roles_and_helpers": None,
        "namespace_pid_and_birth": None,
        "provider_route_and_destination": None,
        "credential_channel_identity": None,
        "financial_or_quota_enforcement": None,
        "execution_authorization_record": None,
        "spend_authorization_record": None,
        "fresh_qualification_record": None,
        "effective_configuration_digest": None,
        "execution_allowed": False,
    }
    if selection is not None:
        dispatch["requested_selection"] = selection.model_dump()
    payloads = {
        "input/check_fixture.py": CHECK_SOURCE,
        "input/expected-README.md": AFTER,
        "input/task.txt": (REQUIREMENT + "\n").encode(),
        "initial-manifest.json": (initial.model_dump_json(indent=2) + "\n").encode(),
        "fixture.json": (json.dumps(fixture, indent=2, sort_keys=True) + "\n").encode(),
        "limits.json": (json.dumps(limits, indent=2, sort_keys=True) + "\n").encode(),
        "dispatch-template.json": (json.dumps(dispatch, indent=2, sort_keys=True) + "\n").encode(),
    }
    for name, data in payloads.items():
        path = output / name
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    artifact_names = [
        *payloads,
        "original/README.md",
        "original/dirty-marker.txt",
        "original/.git/fixture-metadata",
        "candidate/README.md",
    ]
    preparation = BatchPreparation(
        selection=selection,
        owner_model_label=None if selection is not None else "Sol6.1",
        documented_model="gpt-6.1-sol" if selected_model == "gpt-6.1-sol" else None,
        model_source=MODEL_SOURCE if selected_model == "gpt-6.1-sol" else None,
        artifacts=[
            BoundArtifact(path=name, sha256=digest((output / name).read_bytes()))
            for name in sorted(artifact_names)
        ],
        historical_references=references,
        unresolved=[
            "owner approved batch preparation only; no startup/spend authority",
            "requested provider destination, billing/quota and credential choices are not approved or observed",
            "model selection/documentation does not establish pinned CLI/account availability",
            "production envelope, role/configuration/source/grant identities not frozen",
            "new profile needs exact independent qualification; v18 cannot transfer",
            "fresh Linux identities/controllers/storage/cleanup unobserved",
            "real live fixture Git identity and confirmed model/task/check unbound",
        ],
    )
    (output / "batch.json").write_text(preparation.model_dump_json(indent=2) + "\n")
    (output / "batch.json").chmod(0o600)
    return preparation


class BatchAudit(Contract):
    status: Literal["prepared_data_matches"] = "prepared_data_matches"
    preparation_digest: Digest
    selection: PreparationSelection | None
    execution_allowed: Literal[False] = False
    spend_authorized: Literal[False] = False
    profile_qualified: Literal[False] = False


def audit_runtime_batch(
    reference_root: Path,
    output: Path,
    expected: BatchPreparation,
    *,
    selection: PreparationSelection | None = None,
) -> BatchAudit:
    """Read back preparation against an independently retained coordinator record.

    Never use the bundle's own declaration as its trusted expectation. This checks
    bytes/context, not authenticity, availability, live containment or permission.
    Stable coordinator-owned directories are assumed, as in candidate preparation.
    """
    expected = BatchPreparation.model_validate_json(expected.model_dump_json())
    if selection is not None:
        selection = PreparationSelection.model_validate_json(selection.model_dump_json())
    if expected.selection != selection:
        raise ValueError("preparation belongs to a different project/session selection")
    if output.is_symlink() or not output.is_dir():
        raise ValueError("preparation root must be a real directory")
    output = output.resolve(strict=True)
    reader = _Reader(output)
    declaration = _json(reader.read("batch.json"))
    if not isinstance(declaration, dict) or any(
        declaration.get(key) is not False
        for key in ("execution_allowed", "spend_authorized", "profile_qualified")
    ):
        raise ValueError("preparation authority flags must be false")
    if BatchPreparation.model_validate(declaration) != expected:
        raise ValueError("preparation differs from coordinator record")
    wanted = {item.path for item in expected.artifacts} | {"batch.json"}
    directories = {
        parent.as_posix() for name in wanted for parent in Path(name).parents if parent != Path(".")
    }
    pending = [output]
    observed: set[str] = set()
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                name = (directory / entry.name).relative_to(output).as_posix()
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode) and name in directories:
                    pending.append(directory / entry.name)
                elif stat.S_ISREG(info.st_mode) and name in wanted and info.st_nlink == 1:
                    pass
                else:
                    raise ValueError("unknown or aliased preparation entry: " + name)
                observed.add(name)
                if len(observed) > 64:
                    raise ValueError("preparation entry limit exceeded")
    if observed != wanted | directories:
        raise ValueError("preparation inventory incomplete")
    for item in expected.artifacts:
        reader.bound(item)
    historical = _Reader(reference_root)
    for item in expected.historical_references:
        historical.bound(item)
    manifest = FrozenCandidate.model_validate(_json(reader.read("initial-manifest.json")))
    if _scan(output / "candidate")[0] != manifest:
        raise ValueError("prepared candidate differs from initial manifest")
    fixture = _json(reader.read("fixture.json"))
    if not isinstance(fixture, dict) or fixture.get("initial_candidate_sha256") != record_digest(
        manifest
    ):
        raise ValueError("fixture initial candidate binding differs")
    dispatch = _json(reader.read("dispatch-template.json"))
    if not isinstance(dispatch, dict) or dispatch.get("requested_selection") != (
        selection.model_dump() if selection is not None else None
    ):
        raise ValueError("dispatch selection differs")
    return BatchAudit(preparation_digest=record_digest(expected), selection=selection)
