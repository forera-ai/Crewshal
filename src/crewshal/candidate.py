"""Credential-free offline candidate preparation and trusted validator capture.

No commands run here. Copies and manifests are not sandboxes; a live validator
still requires the separately qualified readonly mount and process boundary.
"""

import os
from pathlib import Path
import stat
from typing import Literal

from pydantic import Field, model_validator

from crewshal.contracts import Binding, CheckDefinition, Digest, Evidence, record_digest
from crewshal.model import Contract, digest
from crewshal.qualification_bundle import BoundArtifact
from crewshal.runtime import ProcessObservation, STREAM_BYTES

CANDIDATE_BYTES = 16777216
MAX_ENTRIES = 2000


class CandidateFile(Contract):
    path: str
    kind: Literal["file", "directory"]
    mode: int = Field(ge=0, le=0o777)
    size: int = Field(ge=0, le=CANDIDATE_BYTES)
    sha256: Digest


class FrozenCandidate(Contract):
    schema_version: Literal[1] = 1
    files: list[CandidateFile] = Field(max_length=MAX_ENTRIES)
    execution_allowed: Literal[False] = False

    @model_validator(mode="after")
    def manifest(self) -> "FrozenCandidate":
        _paths([file.path for file in self.files])
        if [file.path for file in self.files] != sorted(file.path for file in self.files):
            raise ValueError("candidate manifest must be sorted")
        if sum(file.size for file in self.files) > CANDIDATE_BYTES:
            raise ValueError("candidate logical byte limit exceeded")
        for file in self.files:
            if file.kind == "directory" and (file.size != 0 or file.sha256 != digest(b"")):
                raise ValueError("directory manifest must not contain file content")
        return self


def _paths(paths: list[str]) -> None:
    aliases: dict[str, str] = {}
    if len(paths) > MAX_ENTRIES or len(paths) != len(set(paths)):
        raise ValueError("duplicate paths or candidate entry limit exceeded")
    for name in paths:
        BoundArtifact(path=name, sha256=digest(b""))
        parts = name.split("/")
        if any(part.casefold() == ".git" for part in parts):
            raise ValueError("Git metadata is excluded from candidate")
        for index in range(1, len(parts) + 1):
            prefix = "/".join(parts[:index])
            key = prefix.casefold()
            if key in aliases and aliases[key] != prefix:
                raise ValueError("candidate case aliases")
            aliases[key] = prefix


def _root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("source must be a real directory")
    return path.resolve(strict=True)


def _verify_root(root: Path, descriptor: int) -> None:
    linked = os.stat(root, follow_symlinks=False)
    actual = os.fstat(descriptor)
    if not stat.S_ISDIR(linked.st_mode) or (linked.st_dev, linked.st_ino) != (
        actual.st_dev,
        actual.st_ino,
    ):
        raise ValueError("source root changed during capture")


def _retain_root(path: Path) -> tuple[Path, int]:
    root = _root(path)
    before = os.stat(root, follow_symlinks=False)
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        actual = os.fstat(descriptor)
        if (before.st_dev, before.st_ino) != (actual.st_dev, actual.st_ino):
            raise ValueError("source root changed during open")
        _verify_root(root, descriptor)
        return root, descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _target(source: Path, target: Path) -> Path:
    if target.exists() or target.is_symlink():
        raise ValueError("candidate target must not exist")
    # Target parent must already exist. Canonical aliases cannot create a copy
    # inside source, original checkout or a parent of source.
    target = target.parent.resolve(strict=True) / target.name
    if target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError("candidate target must be separate from source")
    return target


def _entry_fd(root_fd: int, name: str) -> tuple[CandidateFile, bytes]:
    """Walk only retained directory FDs; ancestor swaps cannot follow aliases."""
    BoundArtifact(path=name, sha256=digest(b""))
    parent = os.dup(root_fd)
    try:
        parts = name.split("/")
        for part in parts[:-1]:
            info = os.stat(part, dir_fd=parent, follow_symlinks=False)
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("candidate symlink or non-directory ancestor refused")
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=parent,
            )
            actual = os.fstat(next_fd)
            if (info.st_dev, info.st_ino) != (actual.st_dev, actual.st_ino):
                os.close(next_fd)
                raise ValueError("candidate ancestor changed during open")
            os.close(parent)
            parent = next_fd
        info = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("candidate symlinks are refused")
        mode = stat.S_IMODE(info.st_mode)
        if mode & ~0o777:
            raise ValueError("candidate special permission bits refused")
        if stat.S_ISDIR(info.st_mode):
            return CandidateFile(
                path=name, kind="directory", mode=mode, size=0, sha256=digest(b"")
            ), b""
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > CANDIDATE_BYTES:
            raise ValueError("candidate must contain bounded regular files without hardlinks")
        descriptor = os.open(
            parts[-1],
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
            dir_fd=parent,
        )
        with os.fdopen(descriptor, "rb") as file:
            before = os.fstat(file.fileno())
            fields = ("st_mode", "st_size", "st_mtime_ns", "st_ctime_ns", "st_nlink")
            if (before.st_dev, before.st_ino) != (info.st_dev, info.st_ino) or tuple(
                getattr(before, field) for field in fields
            ) != tuple(getattr(info, field) for field in fields):
                raise ValueError("candidate changed during open")
            data = file.read(CANDIDATE_BYTES + 1)
            after = os.fstat(file.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or len(data) != before.st_size
            or len(data) > CANDIDATE_BYTES
            or tuple(getattr(before, field) for field in fields)
            != tuple(getattr(after, field) for field in fields)
        ):
            raise ValueError("candidate changed during capture")
        return CandidateFile(
            path=name, kind="file", mode=mode, size=len(data), sha256=digest(data)
        ), data
    finally:
        os.close(parent)


def _entry(root: Path, name: str) -> tuple[CandidateFile, bytes]:
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        return _entry_fd(root_fd, name)
    finally:
        os.close(root_fd)


def _scan_fd(root_fd: int) -> tuple[FrozenCandidate, dict[str, bytes]]:
    names: list[str] = []
    pending = [("", os.dup(root_fd))]
    try:
        while pending:
            prefix, directory = pending.pop()
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        name = prefix + entry.name
                        names.append(name)
                        if len(names) > MAX_ENTRIES:
                            raise ValueError("candidate entry limit exceeded")
                        info = os.stat(entry.name, dir_fd=directory, follow_symlinks=False)
                        if stat.S_ISDIR(info.st_mode):
                            child = os.open(
                                entry.name,
                                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory,
                            )
                            actual = os.fstat(child)
                            if (info.st_dev, info.st_ino) != (actual.st_dev, actual.st_ino):
                                os.close(child)
                                raise ValueError("candidate directory changed during scan")
                            pending.append((name + "/", child))
            finally:
                os.close(directory)
        _paths(names)
        records: list[CandidateFile] = []
        contents: dict[str, bytes] = {}
        total = 0
        for name in sorted(names):
            record, data = _entry_fd(root_fd, name)
            total += record.size
            if total > CANDIDATE_BYTES:
                raise ValueError("candidate logical byte limit exceeded")
            records.append(record)
            if record.kind == "file":
                contents[name] = data
        return FrozenCandidate(files=records), contents
    finally:
        for _, descriptor in pending:
            os.close(descriptor)


def _scan(root: Path) -> tuple[FrozenCandidate, dict[str, bytes]]:
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        return _scan_fd(descriptor)
    finally:
        os.close(descriptor)


def _copy(target: Path, manifest: FrozenCandidate, contents: dict[str, bytes]) -> None:
    target.mkdir(mode=0o700)
    # Retain failed copies for inspection; never remove caller-owned paths.
    directories = [record for record in manifest.files if record.kind == "directory"]
    for record in sorted(directories, key=lambda record: record.path.count("/")):
        (target / record.path).mkdir(mode=0o700, parents=True, exist_ok=True)
    for record in manifest.files:
        if record.kind == "file":
            path = target / record.path
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            with os.fdopen(descriptor, "wb") as file:
                file.write(contents[record.path])
                file.flush()
                os.fsync(file.fileno())
            path.chmod(record.mode)
    for record in sorted(directories, key=lambda record: record.path.count("/"), reverse=True):
        (target / record.path).chmod(record.mode)


def prepare_candidate(source: Path, target: Path, included_paths: list[str]) -> FrozenCandidate:
    """Copy only coordinator-selected files, including explicitly included dirty bytes.

    This neither discovers an approved snapshot nor executes repository instructions.
    Caller must supply stable source and keep coordinator state outside worker views.
    """
    source, descriptor = _retain_root(source)
    try:
        target = _target(source, target)
        _verify_root(source, descriptor)
        _paths(included_paths)
        records: dict[str, CandidateFile] = {}
        contents: dict[str, bytes] = {}
        total = 0
        for name in included_paths:
            record, data = _entry_fd(descriptor, name)
            if record.kind != "file":
                raise ValueError("included paths must name files explicitly")
            total += len(data)
            if total > CANDIDATE_BYTES:
                raise ValueError("candidate logical byte limit exceeded")
            records[name] = record
            contents[name] = data
            parts = name.split("/")
            for index in range(1, len(parts)):
                parent = "/".join(parts[:index])
                parent_record, _ = _entry_fd(descriptor, parent)
                records[parent] = parent_record
        manifest = FrozenCandidate(files=sorted(records.values(), key=lambda record: record.path))
        _verify_root(source, descriptor)
        _copy(target, manifest, contents)
        if _scan(target)[0] != manifest:
            raise ValueError("prepared copy differs from approved snapshot")
        for record in manifest.files:
            if _entry_fd(descriptor, record.path)[0] != record:
                raise ValueError("original changed during candidate preparation")
        _verify_root(source, descriptor)
        return manifest
    finally:
        os.close(descriptor)


def freeze_candidate(source: Path, target: Path, *, tree_stopped: bool) -> FrozenCandidate:
    """Capture a stopped disposable candidate into a separate coordinator copy."""
    if tree_stopped is not True:
        raise ValueError("worker tree must be independently stopped before freeze")
    source, descriptor = _retain_root(source)
    try:
        target = _target(source, target)
        _verify_root(source, descriptor)
        manifest, contents = _scan_fd(descriptor)
        _verify_root(source, descriptor)
        _copy(target, manifest, contents)
        if _scan_fd(descriptor)[0] != manifest or _scan(target)[0] != manifest:
            raise ValueError("candidate changed during freeze")
        _verify_root(source, descriptor)
        return manifest
    finally:
        os.close(descriptor)


def validator_evidence(
    frozen: FrozenCandidate,
    validator_copy: Path,
    binding: Binding,
    approved: CheckDefinition,
    observed: CheckDefinition,
    observation: ProcessObservation,
    stdout: bytes,
    stderr: bytes,
    *,
    environment: str,
    toolchain: str,
    credential_free: bool,
    network_disabled: bool,
    evidence_id: str,
    run_id: str,
    attempt_id: str,
) -> Evidence:
    """Trusted capture seam for a separately observed validator, never worker events.

    Observed argv/cwd/environment/toolchain and containment come from the trusted
    supervisor. This pure capture does not attest them or execute the check.
    """
    frozen = FrozenCandidate.model_validate_json(frozen.model_dump_json())
    binding = Binding.model_validate_json(binding.model_dump_json())
    approved = CheckDefinition.model_validate_json(approved.model_dump_json())
    observed = CheckDefinition.model_validate_json(observed.model_dump_json())
    observation = ProcessObservation.model_validate_json(observation.model_dump_json())
    if binding.candidate != record_digest(frozen) or _scan(_root(validator_copy))[0] != frozen:
        raise ValueError("stale or mutated frozen candidate")
    if (
        approved != observed
        or environment != approved.environment
        or toolchain != approved.toolchain
    ):
        raise ValueError("validator command or identity differs from approved definition")
    if credential_free is not True or network_disabled is not True:
        raise ValueError("validator requires separate credential-free denied-network authority")
    if (
        not observation.stdout_complete
        or not observation.stderr_complete
        or not observation.tree_stopped
    ):
        raise ValueError("validator capture or tree stop incomplete")
    if len(stdout) > STREAM_BYTES or len(stderr) > STREAM_BYTES:
        raise ValueError("validator stream bound exceeded")
    if observation.exit_code is None and observation.termination is None:
        raise ValueError("validator exit missing")
    termination = observation.termination
    if observation.elapsed_seconds > 5.0 and termination is None:
        termination = "timeout"
    if termination == "refusal":
        status = "unavailable"
        evidence_termination = None
    else:
        status = (
            "terminated" if termination else "passed" if observation.exit_code == 0 else "failed"
        )
        evidence_termination = termination
    return Evidence.model_validate(
        {
            "id": evidence_id,
            "run_id": run_id,
            "attempt_id": attempt_id,
            "binding": binding.model_dump(),
            "kind": "check",
            "gate": f"check:{approved.id}",
            "status": status,
            "definition": approved.model_dump(),
            "started": observation.started,
            "ended": observation.ended,
            "exit_code": observation.exit_code,
            "termination": evidence_termination,
            "stdout": digest(stdout),
            "stderr": digest(stderr),
        }
    )


def scope_evidence(
    initial: FrozenCandidate,
    frozen: FrozenCandidate,
    binding: Binding,
    allowed_paths: list[str],
    *,
    evidence_id: str,
    run_id: str,
    attempt_id: str,
    observation: ProcessObservation,
) -> tuple[Evidence, bytes]:
    """Compare coordinator manifests, never a worker-authored diff or success claim."""
    import json

    initial = FrozenCandidate.model_validate_json(initial.model_dump_json())
    frozen = FrozenCandidate.model_validate_json(frozen.model_dump_json())
    binding = Binding.model_validate_json(binding.model_dump_json())
    observation = ProcessObservation.model_validate_json(observation.model_dump_json())
    _paths(allowed_paths)
    if binding.candidate != record_digest(frozen) or not observation.tree_stopped:
        raise ValueError("scope requires current frozen candidate and stopped tree")
    before = {record.path: record for record in initial.files}
    after = {record.path: record for record in frozen.files}
    changed = sorted(
        name for name in before.keys() | after.keys() if before.get(name) != after.get(name)
    )
    outside = sorted(set(changed) - set(allowed_paths))
    raw = (
        json.dumps({"changed": changed, "outside_scope": outside}, sort_keys=True) + "\n"
    ).encode()
    evidence = Evidence.model_validate(
        {
            "id": evidence_id,
            "run_id": run_id,
            "attempt_id": attempt_id,
            "binding": binding.model_dump(),
            "kind": "scope",
            "gate": "scope",
            "status": "failed" if outside else "passed",
            "started": observation.started,
            "ended": observation.ended,
            "stdout": digest(raw),
            "stderr": digest(b""),
            "blocking_findings": [f"outside approved scope: {name}" for name in outside],
        }
    )
    return evidence, raw
