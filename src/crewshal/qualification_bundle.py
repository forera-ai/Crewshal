"""Portable, read-only qualification-record audit; never runtime qualification."""

import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Literal, NoReturn
import unicodedata

from pydantic import Field, ValidationError, field_validator

from crewshal.contracts import Digest
from crewshal.model import Contract
from crewshal.qualification import Qualification, QualificationIdentity, assess_qualification

PROTOCOL_SHA256 = "fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563"
MAX_FILE_BYTES = 1048576
MAX_BUNDLE_BYTES = 8388608
WINDOWS_RESERVED_NAMES = {"con", "prn", "aux", "nul", "clock$"} | {
    name + str(number) for name in ("com", "lpt") for number in range(1, 10)
}


class BoundArtifact(Contract):
    path: str = Field(min_length=1, max_length=1024, pattern=r"^[A-Za-z0-9_./-]+$")
    sha256: Digest

    @field_validator("path")
    @classmethod
    def portable_relative_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if (
            path.is_absolute()
            or any(part in ("", ".", "..") for part in value.split("/"))
            or any(character in value for character in ("\\", ":", "\x00"))
            or str(path) != value
            or any(
                part.endswith((".", " "))
                or part.split(".", 1)[0].casefold() in WINDOWS_RESERVED_NAMES
                for part in path.parts
            )
        ):
            raise ValueError("artifact path must be a normalized portable relative path")
        return value


class QualificationBundle(Contract):
    schema_version: Literal[1]
    protocol: BoundArtifact
    profile: BoundArtifact
    current_identity: QualificationIdentity
    runs: list[BoundArtifact] = Field(min_length=2, max_length=2)
    artifacts: list[BoundArtifact] = Field(max_length=128)
    execution_allowed: Literal[False]

    @field_validator("execution_allowed", mode="before")
    @classmethod
    def false_only(cls, value: object) -> object:
        if value is not False:
            raise ValueError("execution_allowed must be false")
        return value


class BundleAudit(Contract):
    status: Literal["consistent_records", "denied"]
    reasons: list[str]
    run_ids: list[str] = Field(default_factory=list)
    runtime_verified: Literal[False] = False
    execution_allowed: Literal[False] = False


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _reject_constant(value: str) -> NoReturn:
    raise ValueError("nonfinite JSON number: " + value)


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number exceeds finite float range")
    return number


def _json(data: bytes) -> object:
    return json.loads(
        data,
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
        parse_float=_finite_float,
    )


def _same_json(left: object, right: object) -> bool:
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


class _Reader:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("bundle root must be a directory")
        self.total_bytes = 0

    def read(self, name: str) -> bytes:
        BoundArtifact(path=name, sha256="0" * 64)
        path = self.root
        for part in PurePosixPath(name).parts:
            path = path / part
            item = path.lstat()
            if stat.S_ISLNK(item.st_mode):
                raise ValueError("artifact symlinks are refused")
        if not stat.S_ISREG(item.st_mode) or item.st_size > MAX_FILE_BYTES:
            raise ValueError("artifact must be a bounded regular file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        flags |= getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (before.st_dev, before.st_ino) != (item.st_dev, item.st_ino):
                raise ValueError("artifact identity changed during open")
            data = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or len(data) > MAX_FILE_BYTES
            or before.st_size != len(data)
            or (before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        ):
            raise ValueError("artifact changed or exceeded its bound")
        self.total_bytes += len(data)
        if self.total_bytes > MAX_BUNDLE_BYTES:
            raise ValueError("bundle byte limit exceeded")
        return data

    def bound(self, artifact: BoundArtifact) -> bytes:
        data = self.read(artifact.path)
        if hashlib.sha256(data).hexdigest() != artifact.sha256:
            raise ValueError("artifact digest mismatch: " + artifact.path)
        return data


def audit_bundle(root: Path) -> BundleAudit:
    """Audit two complete records separately; claims still need trusted runtime evidence.

    The caller supplies a trusted current identity in bundle.json. File hashes prove
    continuity, not authenticity or containment. This API has no execution seam.
    """
    run_ids: list[str] = []
    try:
        reader = _Reader(root)
        bundle = QualificationBundle.model_validate(_json(reader.read("bundle.json")))
        bound_files = [bundle.protocol, bundle.profile, *bundle.runs, *bundle.artifacts]
        paths = [artifact.path for artifact in bound_files]
        normalized_paths = [unicodedata.normalize("NFC", name).casefold() for name in paths]
        if len(paths) != len(set(normalized_paths)) or "bundle.json" in normalized_paths:
            raise ValueError("duplicate artifact paths")
        prefixes: dict[str, str] = {}
        for artifact_path in ["bundle.json", *paths]:
            parts = PurePosixPath(artifact_path).parts
            for length in range(1, len(parts) + 1):
                prefix = "/".join(parts[:length])
                key = prefix.casefold()
                if key in prefixes and prefixes[key] != prefix:
                    raise ValueError("artifact directory case aliases")
                prefixes[key] = prefix
        if bundle.protocol.sha256 != PROTOCOL_SHA256:
            raise ValueError("original protocol digest differs")
        protocol = _json(reader.bound(bundle.protocol))
        profile = _json(reader.bound(bundle.profile))
        if not isinstance(protocol, dict) or not isinstance(profile, dict):
            raise ValueError("protocol and profile must be objects")
        if (
            profile.get("original_protocol_sha256") != PROTOCOL_SHA256
            or not _same_json(profile.get("original_grant"), protocol["grant"])
            or not _same_json(profile.get("original_limits"), protocol["limits"])
            or not _same_json(profile.get("mandatory_cases"), protocol["mandatory_cases"])
            or profile.get("execution_allowed") is not False
            or profile.get("native_start_allowed") is not False
        ):
            raise ValueError("profile changed the original contract or denial flags")
        if (
            bundle.current_identity.configuration != bundle.profile.sha256
            or bundle.current_identity.manifest != PROTOCOL_SHA256
        ):
            raise ValueError("current identity is not bound to this profile and protocol")
        artifacts = {artifact.path: artifact.sha256 for artifact in bundle.artifacts}
        required: dict[str, str] = {}

        def require(name: object, digest: object) -> None:
            binding = BoundArtifact.model_validate({"path": name, "sha256": digest})
            if binding.path in required and required[binding.path] != binding.sha256:
                raise ValueError("conflicting profile source bindings")
            required[binding.path] = binding.sha256

        for field in ("source", "fixture_source", "payload_source"):
            name, digest = profile.get(field), profile.get(field + "_sha256")
            if not isinstance(name, str) or not isinstance(digest, str):
                raise ValueError("profile source binding is missing")
            require(name, digest)
        policy = profile.get("policy")
        if not isinstance(policy, str):
            raise ValueError("profile policy binding is missing")
        policy_binding = BoundArtifact.model_validate(
            {"path": policy, "sha256": profile.get("policy_sha256")}
        )
        policy_path = str(PurePosixPath(bundle.profile.path).parent / policy_binding.path)
        require(policy_path, policy_binding.sha256)
        additional = profile.get("additional_sources")
        if not isinstance(additional, dict):
            raise ValueError("additional source bindings are missing")
        for name, digest in additional.items():
            require(name, digest)
        for name, digest in required.items():
            if artifacts.get(name) != digest:
                raise ValueError("profile artifact is missing or differently bound: " + name)
        for artifact in bundle.artifacts:
            reader.bound(artifact)
        if bundle.runs[0].sha256 == bundle.runs[1].sha256:
            raise ValueError("a duplicate run cannot establish repetition")
        for artifact in bundle.runs:
            raw_record = _json(reader.bound(artifact))
            if not isinstance(raw_record, dict) or raw_record.get("execution_allowed") is not False:
                raise ValueError("run execution_allowed must be false")
            record = Qualification.model_validate(raw_record)
            if record.id in run_ids:
                raise ValueError("run IDs must be distinct")
            decision = assess_qualification(record, bundle.current_identity)
            if decision.status != "qualified_for_later_authorization":
                raise ValueError("run refused independently: " + "; ".join(decision.reasons))
            run_ids.append(record.id)
        return BundleAudit(status="consistent_records", reasons=[], run_ids=run_ids)
    except ValidationError:
        return BundleAudit(
            status="denied", reasons=["malformed bundle or run record"], run_ids=run_ids
        )
    except (OSError, ValueError, KeyError, RecursionError) as error:
        return BundleAudit(status="denied", reasons=[str(error)], run_ids=run_ids)
