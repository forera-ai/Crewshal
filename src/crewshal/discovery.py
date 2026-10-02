"""Bounded passive inspection. Repository text never reaches an execution API."""

import json
import os
from pathlib import Path, PurePosixPath
import time
import tomllib
from typing import Any

from crewshal.model import Fact, Notice, ProjectModel, Source, digest

EXCLUDED = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".crewshal",
    "artifacts",
    ".ssh",
    ".aws",
}
MANIFESTS = {"pyproject.toml", "package.json"}
INSTRUCTIONS = {"AGENTS.md", "CLAUDE.md"}
LOCKS = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"}


class Limits:
    def __init__(
        self,
        *,
        files: int = 2000,
        file_bytes: int = 262144,
        total_bytes: int = 2097152,
        depth: int = 12,
        seconds: float = 5.0,
    ):
        if min(files, file_bytes, total_bytes, depth, seconds) <= 0:
            raise ValueError("discovery limits must be positive")
        self.files = files
        self.file_bytes = file_bytes
        self.total_bytes = total_bytes
        self.depth = depth
        self.seconds = seconds


def discover(root: Path, limits: Limits | None = None) -> ProjectModel:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("repository must be a directory")
    limits = limits or Limits()
    deadline = time.monotonic() + limits.seconds
    notices: list[Notice] = []
    sources: dict[str, Source] = {}
    parsed: dict[str, dict[str, Any]] = {}
    visited = 0
    consumed = 0
    limited = False

    def notice(path: str, reason: str) -> None:
        notices.append(Notice(path=path, reason=reason))

    def walk(directory: Path, depth: int) -> None:
        nonlocal visited, consumed, limited
        relative_dir = directory.relative_to(root).as_posix()
        if depth > limits.depth:
            notice(relative_dir, "depth limit: subtree excluded")
            return
        try:
            entries = []
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    visited += 1
                    if visited > limits.files or time.monotonic() > deadline:
                        notice(relative_dir, "file count or time limit: inventory incomplete")
                        limited = True
                        return
                    entries.append(entry)
            for entry in sorted(entries, key=lambda item: item.name):
                if limited:
                    return
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if entry.is_symlink():
                    notice(relative, "symlink excluded (including repository escapes)")
                    continue
                if entry.name in EXCLUDED or entry.name.startswith(".env"):
                    notice(relative, "private/generated/vendor path excluded")
                    continue
                if entry.is_dir(follow_symlinks=False):
                    walk(path, depth + 1)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    notice(relative, "nonregular file excluded")
                    continue
                if entry.name not in MANIFESTS | INSTRUCTIONS | LOCKS:
                    if entry.name in {
                        "requirements.txt",
                        "setup.py",
                        "setup.cfg",
                        "tox.ini",
                        "pnpm-workspace.yaml",
                    } or relative.startswith(".github/workflows/"):
                        notice(relative, "unsupported format: not parsed or executed")
                    continue
                if time.monotonic() > deadline:
                    notice(relative, "time limit: inventory incomplete")
                    limited = True
                    return
                if path.stat().st_size > limits.file_bytes:
                    notice(relative, "file size limit: excluded")
                    continue
                if consumed + path.stat().st_size > limits.total_bytes:
                    notice(relative, "total byte limit: excluded")
                    continue
                # Refuse parent symlinks and the final symlink; never import repository Python.
                if path.resolve() != path or any(
                    parent.is_symlink() for parent in path.parents if parent.is_relative_to(root)
                ):
                    notice(relative, "path changed or symlink excluded")
                    continue
                descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(descriptor, "rb") as stream:
                    raw = stream.read(limits.file_bytes + 1)
                if len(raw) > limits.file_bytes or consumed + len(raw) > limits.total_bytes:
                    notice(relative, "read size limit: excluded")
                    continue
                consumed += len(raw)
                sources[relative] = Source(path=relative, digest=digest(raw), location="file")
                if entry.name in INSTRUCTIONS:
                    notice(relative, "untrusted instruction text retained as data; no authority")
                elif entry.name in MANIFESTS:
                    try:
                        text = raw.decode("utf-8")
                        data = (
                            tomllib.loads(text)
                            if entry.name == "pyproject.toml"
                            else json.loads(text)
                        )
                        if not isinstance(data, dict):
                            raise ValueError("manifest must be an object")
                        parsed[relative] = data
                    except (ValueError, UnicodeError, RecursionError) as error:
                        notice(relative, f"malformed manifest: {type(error).__name__}")
        except OSError as error:
            notice(relative_dir, f"unreadable inventory: {type(error).__name__}")

    walk(root, 0)
    facts: list[Fact] = []

    def add(
        key: str, kind: str, value: str | None, origin: str, dependencies: list[str], location: str
    ) -> None:
        facts.append(
            Fact.model_validate(
                {
                    "id": key,
                    "kind": kind,
                    "value": value,
                    "origin": origin,
                    "sources": [
                        sources[name].model_copy(update={"location": location})
                        for name in dependencies
                    ],
                }
            )
        )

    for name, data in sorted(parsed.items()):
        directory = PurePosixPath(name).parent.as_posix()
        is_python = name.endswith("pyproject.toml")
        add(
            f"{name}:stack",
            "stack",
            "python" if is_python else "typescript/javascript",
            "observed",
            [name],
            "manifest format",
        )
        project = data.get("project", {}) if is_python else data
        package_name = project.get("name") if isinstance(project, dict) else None
        add(
            f"{name}:package",
            "package",
            package_name if isinstance(package_name, str) else None,
            "observed" if isinstance(package_name, str) else "unknown",
            [name],
            "project.name/name",
        )
        add(f"{name}:boundary", "boundary", directory, "observed", [name], "manifest directory")
        commands: Any = data.get("scripts", {})
        if is_python:
            tools = data.get("tool", {})
            hatch = tools.get("hatch", {}) if isinstance(tools, dict) else {}
            envs = hatch.get("envs", {}) if isinstance(hatch, dict) else {}
            default = envs.get("default", {}) if isinstance(envs, dict) else {}
            commands = default.get("scripts", {}) if isinstance(default, dict) else {}
            if isinstance(tools, dict) and "pytest" in tools:
                add(
                    f"{name}:pytest",
                    "tool",
                    "pytest configuration",
                    "strong_inference",
                    [name],
                    "tool.pytest (configuration does not prove tool availability)",
                )
        else:
            dependencies = data.get("devDependencies", {})
            if isinstance(dependencies, dict) and "typescript" in dependencies:
                add(
                    f"{name}:typescript",
                    "tool",
                    "typescript",
                    "strong_inference",
                    [name],
                    "devDependencies.typescript (does not prove installed tool)",
                )
            workspaces = data.get("workspaces", [])
            if isinstance(workspaces, dict):
                workspaces = workspaces.get("packages", [])
            if workspaces:
                if not isinstance(workspaces, list) or not all(
                    isinstance(p, str) for p in workspaces
                ):
                    notice(name, "malformed workspace declaration")
                else:
                    for pattern in workspaces:
                        pure = PurePosixPath(pattern)
                        if pure.is_absolute() or ".." in pure.parts or "\\" in pattern:
                            notice(name, "workspace path escape excluded")
                            continue
                        members = [
                            member
                            for member in parsed
                            if member != name
                            and member.endswith("package.json")
                            and PurePosixPath(member).parent.is_relative_to(
                                PurePosixPath(directory)
                            )
                            and PurePosixPath(member)
                            .parent.relative_to(PurePosixPath(directory))
                            .match(pattern)
                        ]
                        if not members:
                            add(
                                f"{name}:workspace:{pattern}",
                                "boundary",
                                None,
                                "unknown",
                                [name],
                                f"workspaces:{pattern} (no supported member found)",
                            )
                        for member in sorted(members):
                            add(
                                f"{name}:workspace:{member}",
                                "boundary",
                                PurePosixPath(member).parent.as_posix(),
                                "observed",
                                [name, member],
                                f"workspaces:{pattern}",
                            )
        valid_commands = False
        if isinstance(commands, dict):
            for command_name, value in sorted(commands.items()):
                if isinstance(value, str) and value.strip() and "\x00" not in value:
                    valid_commands = True
                    add(
                        f"{name}:check:{command_name}",
                        "check",
                        value,
                        "observed",
                        [name],
                        f"tool.hatch.envs.default.scripts.{command_name}"
                        if is_python
                        else f"scripts.{command_name}",
                    )
                else:
                    notice(name, f"unsupported command value: {command_name}")
        else:
            notice(name, "malformed scripts: commands remain unresolved")
        if not valid_commands:
            add(f"{name}:check:unknown", "check", None, "unknown", [name], "no literal commands")
        locks = [
            path
            for path in sources
            if PurePosixPath(path).parent.as_posix() == directory
            and PurePosixPath(path).name in LOCKS
        ]
        if len(locks) > 1:
            add(
                f"{name}:package-manager",
                "tool",
                None,
                "unknown",
                [name, *sorted(locks)],
                "conflicting package-manager locks",
            )
    if not parsed:
        add(
            "project:stack",
            "stack",
            None,
            "unknown",
            sorted(sources),
            "no supported valid manifest",
        )
    if (root / ".github").is_dir() and not (root / ".github").is_symlink():
        add(
            "project:sensitive",
            "sensitive",
            ".github",
            "weak_inference",
            [],
            "conventional CI location; human confirmation required",
        )
    add("project:egress", "egress", None, "unknown", [], "no data-egress grant recorded")
    return ProjectModel(
        project_id=digest(os.fsencode(root)),
        inputs=list(sources.values()),
        facts=facts,
        notices=notices,
    )
