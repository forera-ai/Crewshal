"""Private SQLite coordinator state, CAS transactions and non-executing recovery."""

from contextlib import contextmanager
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile
from typing import TYPE_CHECKING, Iterator, NoReturn, TypeVar

if TYPE_CHECKING:
    from crewshal.linux_setup import OwnedStorageReservation

from crewshal.contracts import (
    Approval,
    Attempt,
    Binding,
    Claim,
    Evidence,
    Record,
    Run,
    StorageCapacityDomain,
    StorageInstallationCharge,
    Task,
    Usage,
    Verdict,
    Waiver,
    cumulative_usage,
    record_digest,
)
from crewshal.gates import evaluate
from crewshal.admission import NativeAdmissionRecord
from crewshal.integration import CodexCollection
from crewshal.model import Contract, ProjectModel, digest, model_digest
from crewshal.supervisor import SupervisionReceipt

SCHEMA_VERSION = 2
APPLICATION_ID = 0x43525348
MAX_RECORD_BYTES = 4194304
INSTALLATION_DATABASE_BYTES = 16777216
INSTALLATION_OUTPUT_BYTES = 16777216
INSTALLATION_JOURNAL_FILE_BYTES = 1073741824
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
    "collection": CodexCollection,
    "supervision": SupervisionReceipt,
    "admission": NativeAdmissionRecord,
    "storage_capacity": StorageCapacityDomain,
    "storage_installation": StorageInstallationCharge,
}


class Conflict(ValueError):
    """The expected version or run lease no longer belongs to this writer."""


class LiveStorageCapacityClaim:
    """Live journal binding for denial only; cannot recreate retained handles."""

    _store: "CoordinatorStore"
    _path: Path
    _file_identity: tuple[int, int]
    _payload: str
    _reservation: object | None

    def __init__(self) -> None:
        raise ValueError("capacity claim requires its original committed store")

    def __reduce__(self) -> NoReturn:
        raise ValueError("capacity claim cannot be copied or exported")

    @property
    def record(self) -> StorageCapacityDomain:
        # Exposed data cannot mutate this claim's retained snapshot.
        return StorageCapacityDomain.model_validate_json(self._payload)

    def verify(self) -> None:
        self._store.verify_storage_capacity_claim(self)

    def bind_reservation(self, reservation: object) -> None:
        if reservation is None:
            raise ValueError("live retained reservation required")
        if self._reservation is not None:
            raise ValueError("original capacity claim already binds a retained reservation")
        # Bind before readback so a failed admission cannot reuse this live claim.
        self._reservation = reservation
        self.verify()

    def verify_reservation(self, reservation: object) -> None:
        if self._reservation is None or self._reservation is not reservation:
            raise ValueError("capacity claim requires its original retained reservation")
        self.verify()


class LiveStorageInstallationClaim:
    """Original upfront charge; terminal records cannot mint another live claim."""

    _store: "CoordinatorStore"
    _path: Path
    _file_identity: tuple[int, int]
    _payload: str
    _reservation: object | None
    _terminal_attempted: bool

    def __init__(self) -> None:
        raise ValueError("installation claim requires its original committed store")

    def __reduce__(self) -> NoReturn:
        raise ValueError("installation claim cannot be copied or exported")

    @property
    def record(self) -> StorageInstallationCharge:
        return StorageInstallationCharge.model_validate_json(self._payload)

    def verify(self) -> None:
        self._store.verify_storage_installation_claim(self)

    def bind_reservation(self, reservation: object) -> None:
        if reservation is None or self._reservation is not None:
            raise ValueError("installation claim requires one original retained reservation")
        self._reservation = reservation
        self.verify()

    def verify_reservation(self, reservation: object) -> None:
        if self._reservation is None or self._reservation is not reservation:
            raise ValueError("installation claim requires its original retained reservation")
        self.verify()

    def retain_unknown(self, reservation: object) -> None:
        """Consume a failed/incomplete installation; never accept caller readiness."""
        if self._terminal_attempted:
            raise ValueError("installation result is one-shot; no retry")
        self._terminal_attempted = True
        self.verify_reservation(reservation)
        self._store._retain_unknown_installation(self)


class InstallationJournalGrowth:
    """Live original journal/output custody, never a physical capacity receipt.

    SQLite's page ceiling is connection-local. Exclusive lifetime locking and
    the original observer's independently read hard file limit are both required;
    the pragma alone cannot establish a bound for another connection. No release,
    reconstruction or refund is provided. Failed output charges stay consumed.
    """

    store: "CoordinatorStore"
    reservation: "OwnedStorageReservation"
    claim: LiveStorageInstallationClaim
    connection: sqlite3.Connection
    descriptors: list[int]
    artifact_charges: dict[str, int]
    artifact_handles: dict[str, int]
    artifact_identities: dict[str, tuple[int, int]]
    output_charge: int
    directory_fd: int
    database_fd: int
    journal_fd: int
    directory_identity: tuple[int, int]
    database_identity: tuple[int, int]
    journal_identity: tuple[int, int]
    page_size: int
    failed: bool
    payload_bound: bool

    def __init__(self) -> None:
        raise ValueError("journal growth requires its original charged store")

    def __reduce__(self) -> NoReturn:
        raise TypeError("live journal growth cannot be copied or exported")

    def verify(self) -> None:
        from crewshal.admission import _read
        from crewshal.linux_parent import _proc_root
        from crewshal.linux_setup import OwnedStorageReservation

        reservation = self.reservation
        if (
            self.failed
            or type(reservation) is not OwnedStorageReservation
            or self.store._storage_growth is not self
            or self.store.connection is not self.connection
            or reservation.capacity_claim is not self.claim
            or self.claim._reservation is not reservation
            or self.claim._store is not self.store
            or self.store._directory_birth_fd != self.directory_fd
            or self.store._directory_birth_identity != self.directory_identity
        ):
            raise ValueError("original retained journal growth identity differs")
        observer = reservation.observer
        if observer.spec.placement != "outer_observer" or observer.spec.pid != os.getpid():
            raise ValueError("journal growth requires the original outer observer")
        observer.verify(reservation.observer_group.identity)
        rows = [
            row.split()
            for row in _read(observer.descriptor, "limits").decode("ascii").splitlines()
            if row.startswith("Max file size")
        ]
        file_bound = 131072 if self.payload_bound else INSTALLATION_JOURNAL_FILE_BYTES
        database_bound = 131072 if self.payload_bound else INSTALLATION_DATABASE_BYTES
        if rows != [
            [
                "Max",
                "file",
                "size",
                str(file_bound),
                str(file_bound),
                "bytes",
            ]
        ]:
            raise ValueError("actual original observer journal file limits differ")
        directory = os.fstat(self.directory_fd)
        database = os.fstat(self.database_fd)
        linked_directory = self.store.directory.stat()
        linked_database = self.store.path.stat()
        journal = os.fstat(self.journal_fd)
        linked_journal = Path(str(self.store.path) + "-journal").stat()
        if (
            (directory.st_dev, directory.st_ino) != self.directory_identity
            or (linked_directory.st_dev, linked_directory.st_ino) != self.directory_identity
            or (database.st_dev, database.st_ino) != self.database_identity
            or (linked_database.st_dev, linked_database.st_ino) != self.database_identity
            or not stat.S_ISDIR(directory.st_mode)
            or not stat.S_ISREG(database.st_mode)
            or directory.st_uid != os.getuid()
            or database.st_uid != os.getuid()
            or stat.S_IMODE(directory.st_mode) != 0o700
            or stat.S_IMODE(database.st_mode) != 0o600
            or database.st_nlink != 1
            or database.st_size > database_bound
            or database.st_blocks * 512 > file_bound
            or (journal.st_dev, journal.st_ino) != self.journal_identity
            or (linked_journal.st_dev, linked_journal.st_ino) != self.journal_identity
            or not stat.S_ISREG(journal.st_mode)
            or journal.st_uid != os.getuid()
            or stat.S_IMODE(journal.st_mode) != 0o600
            or journal.st_nlink != 1
            or journal.st_size > file_bound
            or journal.st_blocks * 512 > file_bound
        ):
            raise ValueError("actual retained journal directory/database readback differs")
        root = _proc_root(observer.spec.boot_id)
        try:
            # fdinfo on an independently opened database FD omits the locks on
            # SQLite's different struct file. Use positive kernel lock records
            # bound to the pinned inode and independently verified original task.
            lock_rows = _read(root, "locks").decode("ascii")
        finally:
            os.close(root)
        intervals = []
        for line in lock_rows.splitlines():
            match = re.fullmatch(
                r"\d+: POSIX\s+ADVISORY\s+WRITE\s+(\d+) "
                r"([0-9a-fA-F]+):([0-9a-fA-F]+):(\d+) (\d+) (\d+)",
                line,
            )
            if match is None:
                continue
            pid, major, minor, inode, start, end = match.groups()
            if (int(pid), int(major, 16), int(minor, 16), int(inode)) == (
                observer.spec.pid,
                os.major(database.st_dev),
                os.minor(database.st_dev),
                database.st_ino,
            ):
                intervals.append((int(start), int(end)))
        covered = 1073741824
        for start, end in sorted(intervals):
            if start <= covered <= end:
                covered = end + 1
        if covered < 1073742336:
            raise ValueError("actual original SQLite exclusive lock readback unavailable")
        expected = {
            "journal_mode": "persist",
            "locking_mode": "exclusive",
            "temp_store": 2,
            "synchronous": 2,
            "page_size": self.page_size,
            "max_page_count": database_bound // self.page_size,
        }
        if any(
            self.connection.execute(f"PRAGMA {key}").fetchone()[0] != value
            for key, value in expected.items()
        ):
            raise ValueError("actual SQLite journal growth controls differ")
        if self.connection.execute("PRAGMA page_count").fetchone()[0] > expected["max_page_count"]:
            raise ValueError("actual SQLite database exceeds original growth bound")
        if self.output_charge != sum(self.artifact_charges.values()) or not (
            0 <= self.output_charge <= INSTALLATION_OUTPUT_BYTES
        ):
            raise ValueError("original irreversible output charges differ")
        if set(self.artifact_handles) != set(self.artifact_identities) or not set(
            self.artifact_handles
        ) <= set(self.artifact_charges):
            raise ValueError("original output acquisition remains unknown")
        for fingerprint, descriptor in self.artifact_handles.items():
            output = os.fstat(descriptor)
            if (
                (output.st_dev, output.st_ino) != self.artifact_identities[fingerprint]
                or not stat.S_ISREG(output.st_mode)
                or output.st_uid != os.getuid()
                or stat.S_IMODE(output.st_mode) != 0o600
                or output.st_nlink != 1
                or not 0 <= output.st_size <= 131072
                or output.st_blocks * 512 > 131072
            ):
                raise ValueError("actual retained output inode growth or identity differs")

    def charge_artifact(self, fingerprint: str, data: bytes) -> None:
        if self.payload_bound:
            self.reservation.verify_output_admission()
            if len(data) > 131072:
                raise ValueError("installed output exceeds original hard file limit")
        else:
            self.reservation.verify_operational()
            # Preparation has the larger inherited image/journal file limit.
            # An output FD acquired there could subsequently grow to that limit;
            # initial content length is not an effective inode capacity bound.
            raise ValueError("installation output requires sealed original file limits")
        self.verify()
        if fingerprint in self.artifact_charges:
            # A charge with no successfully retained output is a failed attempt,
            # not permission to create that representation again.
            self.store._verify_artifact(fingerprint)
            return
        # Charge the retained inode's full potential growth, including a metadata
        # block, even for empty/failed outputs. Writable aliases remain retained.
        charge = 4096 + 131072
        if self.output_charge + charge > INSTALLATION_OUTPUT_BYTES:
            raise ValueError("original installation output capacity exhausted; no retry or refund")
        self.artifact_charges[fingerprint] = charge
        self.output_charge += charge


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
        # A persisted denial record cannot mint a replacement live capability.
        # Keep each original token strongly retained in its original store.
        self._storage_capacity_claims: dict[str, LiveStorageCapacityClaim] = {}
        self._storage_installation_claims: dict[str, LiveStorageInstallationClaim] = {}
        self._storage_installation_attempts: set[str] = set()
        self._storage_growth: InstallationJournalGrowth | None = None
        self._directory_birth_fd = -1
        self._directory_birth_identity: tuple[int, int] | None = None
        self._created_directory = False
        try:
            private_path(directory)
            directory.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            try:
                directory.mkdir(mode=0o700)
            except FileExistsError:
                pass
            else:
                self._created_directory = True
                # Retain the actual new leaf before database creation. Existing
                # private directories remain supported for ordinary legacy stores.
                self._directory_birth_fd = os.open(
                    directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
                )
                birth = os.fstat(self._directory_birth_fd)
                self._directory_birth_identity = (birth.st_dev, birth.st_ino)
            private_path(directory)
            self.directory = directory.resolve()
            if self._created_directory:
                linked_birth = self.directory.stat()
                if (linked_birth.st_dev, linked_birth.st_ino) != self._directory_birth_identity:
                    raise ValueError(
                        "original new journal directory changed before database creation"
                    )
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
            # Query temporaries stay in the original coordinator's memory envelope.
            # This does not establish a disk bound or grant installation admission.
            self.connection.execute("PRAGMA temp_store=MEMORY")
            info = self.path.stat()
            self._capacity_store_identity = (info.st_dev, info.st_ino)
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
            self._created_journal = created
        except BaseException:
            connection = getattr(self, "connection", None)
            if connection is not None:
                connection.close()
            if self._directory_birth_fd >= 0:
                os.close(self._directory_birth_fd)
                self._directory_birth_fd = -1
            raise

    def close(self) -> None:
        self.connection.close()
        if self._storage_growth is None and self._directory_birth_fd >= 0:
            os.close(self._directory_birth_fd)
            self._directory_birth_fd = -1

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

    def _storage_capacity(self, identifier: str) -> tuple[StorageCapacityDomain, int]:
        record, version = self.get("storage_capacity", identifier, StorageCapacityDomain)
        if record is None:
            raise ValueError("missing installed capacity domain is unknown, not free")
        rows = self.connection.execute(
            "SELECT version,kind,payload FROM events WHERE record_id=? ORDER BY sequence",
            (f"storage_capacity:{identifier}",),
        ).fetchall()
        if version not in (1, 2) or [row[0] for row in rows] != list(range(1, version + 1)):
            raise ValueError("capacity journal is incomplete or has an unsupported transition")
        history = []
        for row in rows:
            if row[1] != "storage_capacity":
                raise ValueError("capacity journal kind differs")
            item = StorageCapacityDomain.model_validate_json(row[2])
            if item.id != identifier:
                raise ValueError("capacity journal identity differs")
            history.append(item)
        row = self.connection.execute(
            "SELECT payload FROM records WHERE id=?", (f"storage_capacity:{identifier}",)
        ).fetchone()
        if history[0].state != "installed" or history[-1] != record or rows[-1][2] != row[0]:
            raise ValueError("capacity record and original installation journal disagree")
        if version == 1 and record.state != "installed":
            raise ValueError("capacity domain lacks its original installation record")
        if version == 2:
            original = history[0].model_dump()
            current = record.model_dump()
            for name in ("state", "owner", "configuration", "batch_started_monotonic"):
                original.pop(name)
                current.pop(name)
            if record.state != "retained" or current != original:
                raise ValueError("capacity domain was reset or its installation changed")
        return record, version

    def claim_storage_capacity(
        self,
        domain_id: str,
        *,
        expected_version: int,
        installation: str,
        owner: str,
        configuration: str,
        batch_started_monotonic: float,
    ) -> LiveStorageCapacityClaim:
        """Burn one preexisting installed domain before any storage effect.

        There is deliberately no initialization, refund, retry or release API.
        The real producer must independently bind this journal and installation
        to its fixed physical capacity domain; record contents do not do that.
        """
        if type(expected_version) is not int or expected_version != 1:
            raise Conflict("only the original installed capacity version can be claimed")
        self._verify_capacity_store()
        with self.transaction():
            record, version = self._storage_capacity(domain_id)
            if version != expected_version or record.state != "installed":
                raise Conflict("capacity remains fully charged; no retry or reuse")
            if record.installation != installation:
                raise ValueError("capacity installation differs from exact installed domain")
            retained = StorageCapacityDomain.model_validate(
                {
                    **record.model_dump(),
                    "state": "retained",
                    "owner": owner,
                    "configuration": configuration,
                    "batch_started_monotonic": batch_started_monotonic,
                }
            )
            self._put("storage_capacity", domain_id, retained, expected_version)
        # No claim object exists until the full synchronous transaction commits.
        claim = object.__new__(LiveStorageCapacityClaim)
        claim._store = self
        claim._path = self.path
        claim._file_identity = self._capacity_store_identity
        claim._payload = retained.model_dump_json()
        claim._reservation = None
        self._storage_capacity_claims[domain_id] = claim
        claim.verify()
        return claim

    def _verify_capacity_store(self) -> None:
        private_path(self.path)
        info = self.path.stat()
        if (info.st_dev, info.st_ino) != self._capacity_store_identity:
            raise ValueError("original capacity journal file was replaced")
        if (
            self.connection.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID
            or self.connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION
            or self.connection.execute("PRAGMA synchronous").fetchone()[0] != 2
        ):
            raise ValueError("capacity journal identity or full durability controls differ")
        if self._storage_growth is not None:
            self._storage_growth.verify()

    def bind_installation_journal(self, reservation: object) -> "InstallationJournalGrowth":
        """Pin one original journal's controls after charge, before storage effects.

        The operational installer must first independently install/read the
        original observer's file-size limit. This supplies only journal/output
        custody; it cannot substitute for the physical-domain installation gate.

        Exclusive leaf creation excludes preexisting sibling data without a
        negative scan. It does not exclude later concurrent privileged mutation,
        prove global capacity or qualify trusted-root confinement; the concrete
        operational lifetime still requires those independent boundaries.
        """
        from crewshal.linux_setup import OwnedStorageReservation

        if type(reservation) is not OwnedStorageReservation:
            raise ValueError("journal growth requires original concrete reservation")
        if self._storage_growth is not None:
            raise ValueError("original journal growth binding consumed; no retry")
        claim = reservation.capacity_claim
        if type(claim) is not LiveStorageInstallationClaim or claim._store is not self:
            raise ValueError("journal growth requires original upfront installation claim")
        reservation.verify_operational()
        claim.verify_reservation(reservation)
        growth = object.__new__(InstallationJournalGrowth)
        growth.store, growth.reservation = self, reservation
        growth.claim, growth.connection = claim, self.connection
        growth.descriptors = []
        growth.artifact_charges = {}
        growth.artifact_handles = {}
        growth.artifact_identities = {}
        growth.output_charge = 0
        growth.failed = False
        growth.payload_bound = False
        self._storage_growth = growth
        try:
            if (
                not self._created_journal
                or not self._created_directory
                or self._directory_birth_fd < 0
                or self._directory_birth_identity is None
                or self.backup_path is not None
                or self.connection.in_transaction
                or self.connection.execute("PRAGMA journal_mode").fetchone()[0] != "delete"
                or self.connection.execute("PRAGMA temp_store").fetchone()[0] != 2
                or self.directory.joinpath("artifacts").exists()
            ):
                raise ValueError("journal birth/output custody unknown; no reconstruction")
            growth.directory_fd = self._directory_birth_fd
            growth.descriptors.append(growth.directory_fd)
            growth.database_fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            growth.descriptors.append(growth.database_fd)
            directory_info = os.fstat(growth.directory_fd)
            linked_directory = self.directory.stat()
            if (directory_info.st_dev, directory_info.st_ino) != self._directory_birth_identity or (
                linked_directory.st_dev,
                linked_directory.st_ino,
            ) != self._directory_birth_identity:
                raise ValueError("original newly created journal directory replaced")
            geometry = os.fstatvfs(growth.directory_fd)
            if geometry.f_bsize != 4096 or geometry.f_frsize != 4096:
                raise ValueError("original journal requires actual 4096-byte allocation geometry")
            growth.directory_identity = self._directory_birth_identity
            growth.database_identity = self._capacity_store_identity
            growth.page_size = self.connection.execute("PRAGMA page_size").fetchone()[0]
            if growth.page_size not in (512, 1024, 2048, 4096, 8192, 16384, 32768, 65536):
                raise ValueError("actual SQLite page geometry unavailable")
            self.connection.execute("PRAGMA locking_mode=EXCLUSIVE")
            self.connection.execute("PRAGMA journal_mode=PERSIST")
            self.connection.execute(
                f"PRAGMA max_page_count={INSTALLATION_DATABASE_BYTES // growth.page_size}"
            )
            # EXCLUSIVE locking mode takes effect on an actual write lock and
            # keeps it across commits. Never infer exclusion from a mode flag.
            self.connection.execute("BEGIN EXCLUSIVE")
            # A no-op UPDATE may be optimized away and produce no journal.
            # Write the unchanged schema metadata, then positively retain the
            # actual PERSIST journal. Missing readback consumes this attempt.
            self.connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            self.connection.execute("COMMIT")
            growth.journal_fd = os.open(
                str(self.path) + "-journal", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
            )
            growth.descriptors.append(growth.journal_fd)
            journal_info = os.fstat(growth.journal_fd)
            growth.journal_identity = (journal_info.st_dev, journal_info.st_ino)
            growth.verify()
        except BaseException as error:
            growth.failed = True
            reservation._retain_installation_refusal(error)
            raise
        return growth

    def verify_storage_capacity_claim(self, claim: LiveStorageCapacityClaim) -> None:
        if type(claim) is not LiveStorageCapacityClaim or claim._store is not self:
            raise ValueError("capacity claim requires its original live store")
        if self._storage_capacity_claims.get(claim.record.id) is not claim:
            raise ValueError("capacity claim is not the original minted live token")
        if self.path != claim._path:
            raise ValueError("capacity journal path changed")
        self._verify_capacity_store()
        info = self.path.stat()
        if (info.st_dev, info.st_ino) != claim._file_identity:
            raise ValueError("capacity journal identity changed")
        with self.transaction():
            record, version = self._storage_capacity(claim.record.id)
            if version != 2 or record.model_dump_json() != claim._payload:
                raise ValueError("original retained capacity claim no longer matches journal")

    def charge_storage_installation(
        self,
        scope: str,
        *,
        owner: str,
        configuration: str,
        batch_started_monotonic: float,
    ) -> LiveStorageInstallationClaim:
        """Commit full denial before effects, without claiming physical capacity.

        Operational callers must use the original-observer reservation factory.
        This journal seam alone cannot identify a physical domain or recreate
        an attempt through a fresh journal. Failed admission is not retryable.
        """
        if scope in self._storage_installation_attempts:
            raise Conflict("original installation attempt consumed; no retry")
        self._storage_installation_attempts.add(scope)
        record = StorageInstallationCharge(
            id=scope,
            owner=owner,
            configuration=configuration,
            batch_started_monotonic=batch_started_monotonic,
        )
        self._verify_capacity_store()
        with self.transaction():
            if self.get("storage_installation", scope, StorageInstallationCharge)[0] is not None:
                raise Conflict("installation remains fully charged; no retry or reuse")
            if self.connection.execute(
                "SELECT 1 FROM events WHERE record_id=?", (f"storage_installation:{scope}",)
            ).fetchone():
                raise ValueError("missing installation record is unknown, not free")
            self._put("storage_installation", scope, record, 0)
        claim = object.__new__(LiveStorageInstallationClaim)
        claim._store = self
        claim._path = self.path
        claim._file_identity = self._capacity_store_identity
        claim._payload = record.model_dump_json()
        claim._reservation = None
        claim._terminal_attempted = False
        self._storage_installation_claims[scope] = claim
        claim.verify()
        return claim

    def _storage_installation(self, identifier: str) -> tuple[StorageInstallationCharge, int]:
        record, version = self.get("storage_installation", identifier, StorageInstallationCharge)
        rows = self.connection.execute(
            "SELECT version,kind,payload FROM events WHERE record_id=? ORDER BY version",
            (f"storage_installation:{identifier}",),
        ).fetchall()
        if (
            record is None
            or version not in (1, 2)
            or [row[0] for row in rows] != list(range(1, version + 1))
        ):
            raise ValueError("installation journal is missing, incomplete or reset")
        history = []
        for row in rows:
            if row[1] != "storage_installation":
                raise ValueError("installation journal kind differs")
            history.append(StorageInstallationCharge.model_validate_json(row[2]))
        raw = self.connection.execute(
            "SELECT payload FROM records WHERE id=?", (f"storage_installation:{identifier}",)
        ).fetchone()[0]
        original = history[0]
        if (
            original.id != identifier
            or original.state != "preparing"
            or original.installation != "unknown"
            or history[-1] != record
            or rows[-1][2] != raw
            or (version == 1 and record.state != "preparing")
        ):
            raise ValueError("installation charge and original journal disagree")
        if version == 2:
            before, after = original.model_dump(), record.model_dump()
            for field in ("state", "installation"):
                before.pop(field)
                after.pop(field)
            if record.state != "retained" or before != after:
                raise ValueError("original installation charge, owner or origin changed")
        return record, version

    def verify_storage_installation_claim(self, claim: LiveStorageInstallationClaim) -> None:
        if type(claim) is not LiveStorageInstallationClaim or claim._store is not self:
            raise ValueError("installation claim requires original live store")
        if self._storage_installation_claims.get(claim.record.id) is not claim:
            raise ValueError("installation claim is not original minted live token")
        if self.path != claim._path or self._capacity_store_identity != claim._file_identity:
            raise ValueError("installation journal identity changed")
        self._verify_capacity_store()
        with self.transaction():
            record, _ = self._storage_installation(claim.record.id)
            if record.model_dump_json() != claim._payload:
                raise ValueError("original installation charge no longer matches journal")

    def _retain_unknown_installation(self, claim: LiveStorageInstallationClaim) -> None:
        self.verify_storage_installation_claim(claim)
        with self.transaction():
            record, version = self._storage_installation(claim.record.id)
            if version != 1:
                raise Conflict("installation result already consumed")
            retained = StorageInstallationCharge.model_validate(
                {**record.model_dump(), "state": "retained", "installation": "unknown"}
            )
            self._put("storage_installation", record.id, retained, 1)
        claim._payload = retained.model_dump_json()
        claim.verify()

    def _retain_observed_installation(self, proof: object) -> None:
        """Consume the charge only for its original actual installation owner."""
        from crewshal.linux_production import EffectiveInstallation

        if type(proof) is not EffectiveInstallation:
            raise ValueError("observed installation requires original concrete readback")
        claim = proof.reservation.capacity_claim
        if type(claim) is not LiveStorageInstallationClaim or claim._store is not self:
            raise ValueError("observed installation original store differs")
        if claim._terminal_attempted:
            raise ValueError("installation result consumed; no retry")
        proof.require_effective_payload_growth()
        claim._terminal_attempted = True
        self.verify_storage_installation_claim(claim)
        with self.transaction():
            record, version = self._storage_installation(claim.record.id)
            if version != 1:
                raise Conflict("original installation result consumed")
            retained = StorageInstallationCharge.model_validate(
                {**record.model_dump(), "state": "retained", "installation": "observed"}
            )
            self._put("storage_installation", record.id, retained, 1)
        claim._payload = retained.model_dump_json()
        proof.verify()

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
        growth = self._storage_growth
        if growth is not None:
            growth.charge_artifact(fingerprint, data)
        directory = self.directory / "artifacts"
        private_path(directory)
        directory.mkdir(mode=0o700, exist_ok=True)
        path = directory / fingerprint
        private_path(path)
        if path.exists():
            self._verify_artifact(fingerprint)
            return
        descriptor, name = tempfile.mkstemp(prefix=".capture-", dir=directory)
        if growth is not None:
            # Keep actual output custody before its first write. A failed write
            # keeps the partial file/FD and its entire irreversible charge.
            growth.artifact_handles[fingerprint] = descriptor
            growth.descriptors.append(descriptor)
            info = os.fstat(descriptor)
            growth.artifact_identities[fingerprint] = (info.st_dev, info.st_ino)
            # Closing a writer duplicate never closes the original custody FD.
            descriptor = os.dup(descriptor)
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
            if growth is None:
                Path(name).unlink(missing_ok=True)

    def _verify_artifact(self, fingerprint: str) -> None:
        directory = self.directory / "artifacts"
        private_path(directory)
        path = directory / fingerprint
        private_path(path)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            growth = self._storage_growth
            if growth is not None:
                original = growth.artifact_handles.get(fingerprint)
                identity = growth.artifact_identities.get(fingerprint)
                opened = os.fstat(stream.fileno())
                if (
                    original is None
                    or identity is None
                    or (
                        opened.st_dev,
                        opened.st_ino,
                    )
                    != identity
                    or (os.fstat(original).st_dev, os.fstat(original).st_ino) != identity
                ):
                    raise ValueError("stored capture requires its original retained output inode")
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

    def verdict(
        self,
        run_id: str,
        project_id: str,
        current: Binding,
        token: str,
        *,
        candidate_root: Path | None = None,
    ) -> Verdict:
        with self.transaction():
            self._lease(run_id, token)
            run, version = self.get("run", run_id, Run)
            model, _ = self.get("project", project_id, ProjectModel)
            if run is None or model is None or model_digest(model) != current.model:
                raise ValueError("current model binding mismatch")
            task, _ = self.get("task", run.task_id, Task)
            if task is None:
                raise ValueError("task missing")
            collections = [
                item
                for item in self.records("collection", CodexCollection)
                if item.run_id == run_id
            ]
            if collections:
                from crewshal.candidate import _root, _scan

                if len(collections) != 1 or candidate_root is None:
                    raise ValueError(
                        "collected implementation requires exact frozen candidate readback"
                    )
                collection = collections[0]
                attempt, _ = self.get("attempt", collection.outcome.attempt.id, Attempt)
                expected_attempt = Attempt.model_validate(
                    {
                        **collection.outcome.attempt.model_dump(),
                        "binding": collection.binding.model_dump(),
                    }
                )
                if (
                    collection.binding != current
                    or collection.frozen is None
                    or collection.outcome.status != "completed"
                    or attempt != expected_attempt
                    or _scan(_root(candidate_root))[0] != collection.frozen
                ):
                    raise ValueError("collected implementation or frozen candidate changed")
                for collection_fingerprint in (
                    collection.stdout,
                    collection.stderr,
                    record_digest(collection),
                ):
                    self._verify_artifact(collection_fingerprint)
                admissions = [
                    item
                    for item in self.records("admission", NativeAdmissionRecord)
                    if item.run_id == run_id
                ]
                linked = [
                    item
                    for item in self.records("supervision", SupervisionReceipt)
                    if item.run_id == run_id and item.admission is not None
                ]
                if admissions or linked:
                    if len(admissions) != 1 or len(linked) != 1:
                        raise ValueError("admitted collection linkage missing or ambiguous")
                    admission, supervision = admissions[0], linked[0]
                    scope, _ = self.get(
                        "evidence", f"scope:{digest(admission.attempt_id.encode())}", Evidence
                    )
                    if (
                        admission.attempt_id != collection.outcome.attempt.id
                        or supervision.attempt_id != admission.attempt_id
                        or supervision.handle != admission.handle
                        or supervision.dispatch != admission.dispatch
                        or supervision.collection != record_digest(collection)
                        or supervision.admission != record_digest(admission)
                        or supervision.pid != admission.receipt.spec.pid
                        or supervision.initial.identity != admission.receipt.spec.worker
                        or supervision.observation.started != admission.receipt.started
                        or supervision.stdout != collection.stdout
                        or supervision.stderr != collection.stderr
                        or scope is None
                        or not {record_digest(admission), record_digest(supervision)}
                        <= set(scope.artifacts)
                    ):
                        raise ValueError("admitted collection linkage changed")
                    self._verify_artifact(record_digest(admission))
                    self._verify_artifact(record_digest(supervision))
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
