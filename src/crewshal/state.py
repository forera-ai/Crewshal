"""Minimal external model storage. Durable orchestration belongs to Phase 2B."""

import os
from pathlib import Path
import tempfile

from crewshal.model import ProjectModel, digest

MAX_RECORD_BYTES = 4194304


def default_state() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    return base / "crewshal"


class ModelStore:
    def __init__(self, repository: Path, directory: Path):
        if directory.is_symlink():
            raise ValueError("state directory cannot be a symlink")
        repository = repository.resolve(strict=True)
        self.directory = directory.resolve()
        if self.directory.is_relative_to(repository):
            raise ValueError("coordinator state must be outside the repository")
        self.path = self.directory / f"{digest(os.fsencode(repository))}.json"

    def load(self) -> ProjectModel | None:
        if self.path.is_symlink():
            raise ValueError("state record cannot be a symlink")
        if not self.path.exists():
            return None
        return load_model(self.path)

    def save(self, model: ProjectModel) -> None:
        # Validate again before crossing the serialization boundary.
        ProjectModel.model_validate(model.model_dump())
        if self.directory.is_symlink() or self.path.is_symlink():
            raise ValueError("state path changed to a symlink")
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.directory.stat().st_uid != os.getuid():
            raise ValueError("state directory must belong to the coordinator user")
        if self.directory.stat().st_mode & 0o077:
            raise ValueError("state directory must be private (chmod 700)")
        payload = model.public_json().encode()
        if len(payload) > MAX_RECORD_BYTES:
            raise ValueError("model exceeds state size limit")
        descriptor, temporary = tempfile.mkstemp(prefix=".model-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            Path(temporary).unlink(missing_ok=True)


def load_model(path: Path) -> ProjectModel:
    with path.open("rb") as stream:
        raw = stream.read(MAX_RECORD_BYTES + 1)
    if len(raw) > MAX_RECORD_BYTES:
        raise ValueError("model exceeds state size limit")
    return ProjectModel.model_validate_json(raw)


def export_model(repository: Path, relative: str, model: ProjectModel) -> None:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.name:
        raise ValueError("export requires a repository-relative file path")
    target = repository / path
    if target.is_symlink() or not target.resolve().is_relative_to(repository.resolve()):
        raise ValueError("export path escapes repository")
    if not target.parent.is_dir() or any(
        parent.is_symlink() for parent in target.parents if parent.is_relative_to(repository)
    ):
        raise ValueError("export parent must exist without symlinks")
    # Exclusive creation preserves all original files, including untracked/dirty files.
    with target.open("x", encoding="utf-8") as stream:
        stream.write(model.public_json())
