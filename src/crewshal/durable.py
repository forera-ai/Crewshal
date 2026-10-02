"""Private SQLite coordinator state, CAS transactions and non-executing recovery."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
from typing import Iterator, TypeVar

from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    Claim,
    Evidence,
    Record,
    Run,
    Task,
    Usage,
    Verdict,
    Waiver,
    cumulative_usage,
    record_digest,
)
from crewshal.gates import evaluate
from crewshal.model import Contract, ProjectModel, digest, model_digest

SCHEMA_VERSION = 2
APPLICATION_ID = 0x43525348
MAX_RECORD_BYTES = 4194304
T = TypeVar("T", bound=Contract)
TYPES: dict[str, type[Contract]] = {
    "project": ProjectModel,
    "task": Task,
    "run": Run,
    "attempt": Attempt,
    "approval": Approval,
    "claim": Claim,
    "evidence": Evidence,
    "waiver": Waiver,
    "verdict": Verdict,
    "usage": Usage,
}


class Conflict(ValueError):
    """The expected version or run lease no longer belongs to this writer."""


def private_path(path: Path) -> None:
    # Parent aliases (including macOS /var and /tmp) are canonicalized by the
    # facade before repository exclusion. The directory/file itself cannot be a link.
    if path.is_symlink():
        raise ValueError("coordinator paths cannot be symlinks")
    if path.exists():
        info = path.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("coordinator path must be private and owned by coordinator")
        if not stat.S_ISDIR(info.st_mode) and (
            not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
        ):
            raise ValueError("coordinator file must be a regular file without hardlinks")


class CoordinatorStore:
    def __init__(self, directory: Path, *, migrate: bool = False):
        private_path(directory)
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        private_path(directory)
        self.directory = directory.resolve()
        self.path = self.directory / "coordinator.sqlite3"
        self.backup_path: Path | None = None
        private_path(self.path)
        for suffix in ("-journal", "-wal", "-shm"):
            private_path(Path(str(self.path) + suffix))
        created = False
        try:
            descriptor = os.open(
                self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600
            )
        except FileExistsError:
            pass
        else:
            os.close(descriptor)
            created = True
        self.connection = sqlite3.connect(
            self.path.as_uri() + "?mode=rw", uri=True, isolation_level=None, timeout=2
        )
        self.connection.row_factory = sqlite3.Row
        try:
            self.connection.execute("PRAGMA synchronous=FULL")
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            identity = self.connection.execute("PRAGMA application_id").fetchone()[0]
            if created:
                with self.transaction():
                    self.connection.execute(
                        "CREATE TABLE records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, "
                        "version INTEGER NOT NULL CHECK(version>0), payload TEXT NOT NULL, "
                        "payload_digest TEXT NOT NULL)"
                    )
                    self.connection.execute(
                        "CREATE TABLE events (sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "record_id TEXT NOT NULL, version INTEGER NOT NULL, kind TEXT NOT NULL, "
                        "payload TEXT NOT NULL, UNIQUE(record_id, version))"
                    )
                    self.connection.execute(
                        "CREATE TABLE lease (singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                        "run_id TEXT NOT NULL, token TEXT NOT NULL)"
                    )
                    self.connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
                    self.connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            elif identity != APPLICATION_ID or version not in {1, SCHEMA_VERSION}:
                raise ValueError("unsupported coordinator database schema or identity")
            elif version == 1:
                if not migrate:
                    raise ValueError("schema 1 requires explicit migration with backup")
                self._migrate()
            self._validate_schema()
        except BaseException:
            self.connection.close()
            raise

    def close(self) -> None:
        self.connection.close()

    def _validate_schema(self) -> None:
        expected = {
            "records": ["id", "kind", "version", "payload", "payload_digest"],
            "events": ["sequence", "record_id", "version", "kind", "payload"],
            "lease": ["singleton", "run_id", "token"],
        }
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        if tables != set(expected):
            raise ValueError("unexpected coordinator schema tables")
        if self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type IN ('trigger','view')"
        ).fetchone():
            raise ValueError("unexpected coordinator schema trigger/view")
        for table, columns in expected.items():
            info = self.connection.execute(f"PRAGMA table_info({table})").fetchall()
            actual = [row[1] for row in info]
            if actual != columns:
                raise ValueError("unexpected coordinator schema columns")
            integer_columns = {"version", "sequence", "singleton"}
            for row in info:
                if row[2] != ("INTEGER" if row[1] in integer_columns else "TEXT"):
                    raise ValueError("unexpected coordinator column type")
            primary = (
                "id" if table == "records" else "sequence" if table == "events" else "singleton"
            )
            if [row[1] for row in info if row[5]] != [primary]:
                raise ValueError("unexpected coordinator primary key")
        unique_events = False
        for index in self.connection.execute("PRAGMA index_list(events)").fetchall():
            if index[2] and [
                row[2]
                for row in self.connection.execute(
                    "SELECT * FROM pragma_index_info(?)", (index[1],)
                )
            ] == ["record_id", "version"]:
                unique_events = True
        if not unique_events:
            raise ValueError("ordered event uniqueness constraint missing")
        if self.connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("database integrity check failed")
        for row in self.connection.execute("SELECT * FROM records").fetchall():
            value = self._decode(row["kind"], row["payload"])
            identifier = (
                value.project_id if isinstance(value, ProjectModel) else getattr(value, "id")
            )
            if (
                row["id"] != f"{row['kind']}:{identifier}"
                or type(row["version"]) is not int
                or row["version"] < 1
                or row["payload_digest"] != digest(row["payload"].encode())
            ):
                raise ValueError("stored record identity/version/digest mismatch")
            history = self.connection.execute(
                "SELECT version,kind,payload FROM events WHERE record_id=? ORDER BY sequence",
                (row["id"],),
            ).fetchall()
            if [event[0] for event in history] != list(range(1, row["version"] + 1)) or tuple(
                history[-1]
            ) != (row["version"], row["kind"], row["payload"]):
                raise ValueError("record and ordered events disagree")
            for event in history:
                historical = self._decode(event[1], event[2])
                historical_id = (
                    historical.project_id
                    if isinstance(historical, ProjectModel)
                    else getattr(historical, "id")
                )
                if event[1] != row["kind"] or historical_id != identifier:
                    raise ValueError("event identity mismatch")
        if self.connection.execute(
            "SELECT 1 FROM events WHERE record_id NOT IN (SELECT id FROM records)"
        ).fetchone():
            raise ValueError("orphan coordinator event")

    @contextmanager
    def transaction(self) -> Iterator[None]:
        private_path(self.path)
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.connection.execute("COMMIT")
            except BaseException:
                self.connection.execute("ROLLBACK")
                raise
        except sqlite3.OperationalError as error:
            raise Conflict(f"coordinator transaction refused: {error}") from error

    def _migrate(self) -> None:
        # A separate read connection can back up the committed database while the
        # migration connection holds its write lock. No concurrent writer can slip in.
        with self.transaction():
            descriptor, name = tempfile.mkstemp(
                prefix="schema-1-", suffix=".sqlite3.bak", dir=self.directory
            )
            os.close(descriptor)
            self.backup_path = Path(name)
            source = sqlite3.connect(self.path)
            destination = sqlite3.connect(name)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()
            with self.backup_path.open("rb") as stream:
                os.fsync(stream.fileno())
            self.connection.execute(
                "ALTER TABLE records ADD COLUMN payload_digest TEXT NOT NULL DEFAULT ''"
            )
            for row in self.connection.execute("SELECT id, kind, payload FROM records").fetchall():
                self._decode(row["kind"], row["payload"])
                self.connection.execute(
                    "UPDATE records SET payload_digest=? WHERE id=?",
                    (digest(row["payload"].encode()), row["id"]),
                )
            for row in self.connection.execute("SELECT kind, payload FROM events"):
                self._decode(row["kind"], row["payload"])
            self._validate_schema()
            self.connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")

    def _decode(self, kind: str, payload: str) -> Contract:
        if kind not in TYPES or len(payload.encode()) > MAX_RECORD_BYTES:
            raise ValueError("unknown record kind or oversized record")
        return TYPES[kind].model_validate_json(payload)

    def get(self, kind: str, identifier: str, contract: type[T]) -> tuple[T | None, int]:
        if TYPES.get(kind) is not contract:
            raise ValueError("record contract does not match kind")
        row = self.connection.execute(
            "SELECT * FROM records WHERE id=?", (f"{kind}:{identifier}",)
        ).fetchone()
        if row is None:
            return None, 0
        if row["kind"] != kind or digest(row["payload"].encode()) != row["payload_digest"]:
            raise ValueError("record integrity mismatch")
        self._decode(kind, row["payload"])
        return contract.model_validate_json(row["payload"]), row["version"]

    def _put(self, kind: str, identifier: str, record: Contract, expected: int) -> int:
        if type(expected) is not int or expected < 0:
            raise ValueError("expected version must be a nonnegative integer")
        payload = record.model_dump_json()
        self._decode(kind, payload)
        key = f"{kind}:{identifier}"
        row = self.connection.execute("SELECT version FROM records WHERE id=?", (key,)).fetchone()
        actual = row[0] if row else 0
        if actual != expected:
            raise Conflict("state version conflict; reload before making another decision")
        version = actual + 1
        self.connection.execute(
            "INSERT INTO records VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
            "version=excluded.version,payload=excluded.payload,payload_digest=excluded.payload_digest",
            (key, kind, version, payload, digest(payload.encode())),
        )
        self.connection.execute(
            "INSERT INTO events(record_id,version,kind,payload) VALUES(?,?,?,?)",
            (key, version, kind, payload),
        )
        return version

    def save_project(self, model: ProjectModel, expected: int) -> int:
        with self.transaction():
            return self._put("project", model.project_id, model, expected)

    def _create(self, kind: str, record: Record) -> None:
        with self.transaction():
            self._put(kind, record.id, record, 0)

    def create_task(self, task: Task) -> None:
        self._create("task", task)

    def create_run(self, run: Run, project_id: str) -> None:
        with self.transaction():
            task, _ = self.get("task", run.task_id, Task)
            model, _ = self.get("project", project_id, ProjectModel)
            if (
                task is None
                or model is None
                or run.binding.task != record_digest(task)
                or run.binding.model != model_digest(model)
            ):
                raise ValueError("run does not bind stored task/model")
            if run.state != "ready":
                raise ValueError("new run must be ready")
            self._put("run", run.id, run, 0)

    def acquire(self, run_id: str, token: str) -> None:
        if not token.strip():
            raise ValueError("lease token required")
        with self.transaction():
            run, _ = self.get("run", run_id, Run)
            if run is None or run.state != "ready":
                raise ValueError("lease requires ready run")
            if self.connection.execute("SELECT 1 FROM lease").fetchone():
                raise Conflict("coordinator run already leased; reconcile before takeover")
            self.connection.execute("INSERT INTO lease VALUES(1,?,?)", (run_id, token))

    def _lease(self, run_id: str, token: str) -> None:
        row = self.connection.execute("SELECT run_id,token FROM lease").fetchone()
        if row is None or tuple(row) != (run_id, token):
            raise Conflict("run lease mismatch")

    def transition(self, run_id: str, expected: int, state: str, token: str) -> int:
        allowed = {
            "ready": {"frozen", "interrupted"},
            "frozen": {"validating", "interrupted"},
            "validating": {"interrupted"},
        }
        with self.transaction():
            self._lease(run_id, token)
            run, _ = self.get("run", run_id, Run)
            if run is None or state not in allowed.get(run.state, set()):
                raise ValueError("illegal run transition")
            updated = Run.model_validate({**run.model_dump(), "state": state})
            version = self._put("run", run_id, updated, expected)
            if state == "interrupted":
                self.connection.execute("DELETE FROM lease")
            return version

    def owner_approval(self, approval: Approval) -> None:
        self._bound_create("approval", approval)

    def owner_waiver(self, waiver: Waiver) -> None:
        self._bound_create("waiver", waiver)

    def _bound_create(self, kind: str, record: Approval | Waiver) -> None:
        with self.transaction():
            run, _ = self.get("run", record.run_id, Run)
            if run is None or run.binding != record.binding:
                raise ValueError("owner decision does not bind current run")
            self._put(kind, record.id, record, 0)

    def launch_intent(self, attempt: Attempt, token: str) -> None:
        with self.transaction():
            self._lease(attempt.run_id, token)
            run, _ = self.get("run", attempt.run_id, Run)
            if (
                run is None
                or run.binding != attempt.binding
                or attempt.state != "intent"
                or attempt.handle is not None
                or attempt.process_exit is not None
                or attempt.runtime_result != "unknown"
            ):
                raise ValueError("invalid launch intent")
            self._put("attempt", attempt.id, attempt, 0)

    def record_attempt(self, attempt: Attempt, expected: int, token: str) -> None:
        allowed = {
            "intent": {"acknowledged", "interrupted", "cancelled"},
            "acknowledged": {"completed", "failed", "interrupted", "cancelled"},
        }
        with self.transaction():
            self._lease(attempt.run_id, token)
            previous, _ = self.get("attempt", attempt.id, Attempt)
            if previous is None or attempt.state not in allowed.get(previous.state, set()):
                raise ValueError("illegal attempt transition")
            for field in ("run_id", "binding", "role", "provider", "model"):
                if getattr(previous, field) != getattr(attempt, field):
                    raise ValueError("attempt identity cannot change")
            if attempt.state == "acknowledged" and not attempt.handle:
                raise ValueError("acknowledgement requires execution handle")
            if previous.handle is not None and previous.handle != attempt.handle:
                raise ValueError("execution handle cannot change")
            self._put("attempt", attempt.id, attempt, expected)

    def record_claim(self, claim: Claim) -> None:
        with self.transaction():
            if self.get("attempt", claim.attempt_id, Attempt)[0] is None:
                raise ValueError("claim requires known attempt")
            self._put("claim", claim.id, claim, 0)

    def capture(
        self,
        evidence: Evidence,
        token: str,
        *,
        stdout: bytes | None = None,
        stderr: bytes | None = None,
        artifacts: dict[str, bytes] | None = None,
    ) -> None:
        """Trusted coordinator capture seam, not an import or worker tool."""
        with self.transaction():
            self._lease(evidence.run_id, token)
            # Revalidate before creating artifacts; model_construct is not authority.
            Evidence.model_validate_json(evidence.model_dump_json())
            attempt, _ = self.get("attempt", evidence.attempt_id, Attempt)
            if (
                attempt is None
                or attempt.run_id != evidence.run_id
                or attempt.binding != evidence.binding
            ):
                raise ValueError("evidence does not bind known attempt")
            supplied = dict(artifacts or {})
            if set(supplied) != set(evidence.artifacts):
                raise ValueError("captured artifact references do not match supplied bytes")
            for expected, data in ((evidence.stdout, stdout), (evidence.stderr, stderr)):
                if (expected is None) != (data is None) or (
                    data is not None and digest(data) != expected
                ):
                    raise ValueError("captured log digest does not match supplied bytes")
                if expected is not None and data is not None:
                    supplied[expected] = data
            for fingerprint, data in supplied.items():
                if digest(data) != fingerprint:
                    raise ValueError("captured artifact digest mismatch")
                self._artifact(fingerprint, data)
            self._put("evidence", evidence.id, evidence, 0)

    def _artifact(self, fingerprint: str, data: bytes) -> None:
        if len(data) > MAX_RECORD_BYTES:
            raise ValueError("captured artifact exceeds size limit")
        directory = self.directory / "artifacts"
        private_path(directory)
        directory.mkdir(mode=0o700, exist_ok=True)
        path = directory / fingerprint
        private_path(path)
        if path.exists():
            self._verify_artifact(fingerprint)
            return
        descriptor, name = tempfile.mkstemp(prefix=".capture-", dir=directory)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            Path(name).unlink(missing_ok=True)

    def _verify_artifact(self, fingerprint: str) -> None:
        directory = self.directory / "artifacts"
        private_path(directory)
        path = directory / fingerprint
        private_path(path)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            raw = stream.read(MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES or digest(raw) != fingerprint:
            raise ValueError("stored capture missing or changed")

    def records(self, kind: str, contract: type[T]) -> list[T]:
        identifiers = [
            row[0].removeprefix(f"{kind}:")
            for row in self.connection.execute(
                "SELECT id FROM records WHERE kind=? ORDER BY id", (kind,)
            )
        ]
        result = []
        for identifier in identifiers:
            record, _ = self.get(kind, identifier, contract)
            if record is not None:
                result.append(record)
        return result

    def reconcile_launches(self) -> list[str]:
        """Restart contract: every outstanding handle/intent is interrupted for inspection.

        No process is queried, killed, adopted or launched by this Phase 2B seam.
        Even a terminal attempt with an unfinished run requires inspection.
        """
        interrupted = []
        with self.transaction():
            for attempt in self.records("attempt", Attempt):
                if attempt.state in {"intent", "acknowledged"}:
                    _, version = self.get("attempt", attempt.id, Attempt)
                    updated = Attempt.model_validate(
                        {**attempt.model_dump(), "state": "interrupted"}
                    )
                    self._put("attempt", attempt.id, updated, version)
                    interrupted.append(attempt.id)
            row = self.connection.execute("SELECT run_id FROM lease").fetchone()
            if row:
                run, version = self.get("run", row[0], Run)
                if run is not None and run.state != "verdict":
                    updated_run = Run.model_validate({**run.model_dump(), "state": "interrupted"})
                    self._put("run", run.id, updated_run, version)
                self.connection.execute("DELETE FROM lease")
        return interrupted

    def record_usage(self, usage: Usage) -> None:
        with self.transaction():
            if self.get("attempt", usage.attempt_id, Attempt)[0] is None:
                raise ValueError("usage requires known attempt")
            previous, version = self.get("usage", usage.id, Usage)
            if previous is not None:
                if previous != usage:
                    raise ValueError("conflicting usage replay")
                return
            events = self.records("usage", Usage)
            matching = [
                e
                for e in events
                if e.attempt_id == usage.attempt_id and e.event_id == usage.event_id
            ]
            if matching:
                raise ValueError("duplicate attempt/event identity with different record ID")
            cumulative_usage(
                [usage.attempt_id],
                [e for e in events if e.attempt_id == usage.attempt_id] + [usage],
            )
            self._put("usage", usage.id, usage, version)

    def verdict(self, run_id: str, project_id: str, current: Binding, token: str) -> Verdict:
        with self.transaction():
            self._lease(run_id, token)
            run, version = self.get("run", run_id, Run)
            model, _ = self.get("project", project_id, ProjectModel)
            if run is None or model is None or model_digest(model) != current.model:
                raise ValueError("current model binding mismatch")
            task, _ = self.get("task", run.task_id, Task)
            if task is None:
                raise ValueError("task missing")
            captured = [e for e in self.records("evidence", Evidence) if e.run_id == run_id]
            for item in captured:
                for fingerprint in (item.stdout, item.stderr, *item.artifacts):
                    if fingerprint is not None:
                        self._verify_artifact(fingerprint)
            result = evaluate(
                run,
                task,
                current,
                [a for a in self.records("approval", Approval) if a.run_id == run_id],
                [a for a in self.records("attempt", Attempt) if a.run_id == run_id],
                captured,
                [w for w in self.records("waiver", Waiver) if w.run_id == run_id],
            )
            _, verdict_version = self.get("verdict", result.id, Verdict)
            self._put("verdict", result.id, result, verdict_version)
            if result.status in {"verified", "accepted_with_waiver"}:
                if run.state != "validating":
                    raise ValueError("final verdict requires validating run")
                updated = Run.model_validate({**run.model_dump(), "state": "verdict"})
                self._put("run", run_id, updated, version)
                self.connection.execute("DELETE FROM lease")
            return result
