"""External model facade with explicit legacy import and durable CAS writes."""

import os
from pathlib import Path

from crewshal.durable import CoordinatorStore, private_path

from crewshal.model import ProjectModel, digest

MAX_RECORD_BYTES = 4194304


def default_state() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    return base / "crewshal"


class ModelStore:
    def __init__(self, repository: Path, directory: Path, *, migrate: bool = False):
        private_path(directory)
        repository = repository.resolve(strict=True)
        self.directory = directory.resolve()
        if self.directory.is_relative_to(repository):
            raise ValueError("coordinator state must be outside the repository")
        self.path = self.directory / f"{digest(os.fsencode(repository))}.json"
        self.project_id = digest(os.fsencode(repository))
        self.version = 0
        self.migrate = migrate

    def load(self) -> ProjectModel | None:
        private_path(self.path)
        if not self.directory.exists():
            return None
        store = CoordinatorStore(self.directory, migrate=self.migrate)
        try:
            model, self.version = store.get("project", self.project_id, ProjectModel)
            if model is None and self.path.exists():
                if not self.migrate:
                    raise ValueError("legacy JSON state requires explicit --migrate-state")
                model = load_model(self.path)
                if model.project_id != self.project_id:
                    raise ValueError("legacy model belongs to another project")
                # Preserve the original private JSON byte-for-byte as the import backup.
                self.version = store.save_project(model, 0)
            return model
        finally:
            store.close()

    def save(self, model: ProjectModel) -> None:
        private_path(self.path)
        if model.project_id != self.project_id:
            raise ValueError("model belongs to another project")
        store = CoordinatorStore(self.directory, migrate=self.migrate)
        try:
            self.version = store.save_project(model, self.version)
        finally:
            store.close()


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
