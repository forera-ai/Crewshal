"""Fresh upfront-charge denial fixtures; no Linux or launcher effects."""

from concurrent.futures import ThreadPoolExecutor
import copy
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from crewshal import linux_setup as setup
from crewshal import linux_production as production
from crewshal import linux_storage as storage
from crewshal.contracts import StorageInstallationCharge
from crewshal.durable import Conflict, CoordinatorStore, LiveStorageInstallationClaim
from tests.acceptance import test_phase_2d_setup as fixtures
from tests.acceptance import test_phase_2d_batch_timer as timer_fixtures


class Phase2DInstallationJournal(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "original-journal"
        self.store = self.open_store()

    def open_store(self):
        store = CoordinatorStore(self.directory)
        self.addCleanup(store.close)
        return store

    def charge(self, store=None):
        return (store or self.store).charge_storage_installation(
            "original-installation-scope",
            owner="a" * 64,
            configuration="b" * 64,
            batch_started_monotonic=100.0,
        )

    def test_precharge_connect_failure_closes_known_birth_fd_without_removing_files(self):
        directory = self.directory.parent / "failed-precharge"
        original_open = os.open
        acquired = []

        def opening(path, *args, **kwargs):
            handle = original_open(path, *args, **kwargs)
            if path == directory:
                acquired.append(handle)
            return handle

        with (
            patch("crewshal.durable.os.open", side_effect=opening),
            patch(
                "crewshal.durable.sqlite3.connect",
                side_effect=sqlite3.OperationalError("fixture connect refusal"),
            ),
            self.assertRaisesRegex(sqlite3.OperationalError, "fixture connect refusal"),
        ):
            CoordinatorStore(directory)
        self.assertEqual(len(acquired), 1)
        with self.assertRaises(OSError):
            os.fstat(acquired[0])
        self.assertTrue(directory.is_dir())
        self.assertTrue((directory / "coordinator.sqlite3").is_file())
        # This failure precedes any installation charge/capability. Closing the
        # known constructor-local FD cannot release a retained installed domain.
        self.assertEqual(self.store._storage_installation_claims, {})

    def test_precharge_pragma_failure_closes_connection_and_known_birth_fd(self):
        directory = self.directory.parent / "failed-pragma"
        original_connect, original_open = sqlite3.connect, os.open
        acquired, connections = [], []

        def opening(path, *args, **kwargs):
            handle = original_open(path, *args, **kwargs)
            if path == directory:
                acquired.append(handle)
            return handle

        def connecting(*args, **kwargs):
            connection = original_connect(*args, **kwargs)
            connections.append(connection)
            connection.set_authorizer(
                lambda action, *_: sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_PRAGMA
                else sqlite3.SQLITE_OK
            )
            return connection

        with (
            patch("crewshal.durable.os.open", side_effect=opening),
            patch("crewshal.durable.sqlite3.connect", side_effect=connecting),
            self.assertRaises(sqlite3.DatabaseError),
        ):
            CoordinatorStore(directory)
        self.assertEqual(len(acquired), 1)
        with self.assertRaises(OSError):
            os.fstat(acquired[0])
        with self.assertRaises(sqlite3.ProgrammingError):
            connections[0].execute("SELECT 1")
        self.assertTrue(directory.is_dir())

    def test_charge_is_complete_committed_denial_not_installed_capacity(self):
        claim = self.charge()
        another = self.open_store()
        record, version = another.get(
            "storage_installation", claim.record.id, StorageInstallationCharge
        )
        self.assertEqual(record, claim.record)
        self.assertEqual(version, 1)
        self.assertEqual((record.state, record.installation), ("preparing", "unknown"))
        self.assertEqual(
            (record.memory_bytes, record.tasks, record.logical_bytes, record.allocated_bytes),
            (805306368, 128, 8589934592, 8589934592),
        )
        self.assertEqual(another.connection.execute("SELECT count(*) FROM events").fetchone()[0], 1)
        with self.assertRaises(Conflict):
            self.charge(another)

    def test_two_writers_commit_only_one_original_scope_charge(self):
        barrier = threading.Barrier(2)

        def writer(_):
            store = CoordinatorStore(self.directory)
            try:
                barrier.wait(timeout=5)
                try:
                    self.charge(store)
                except Conflict:
                    return "denied"
                return "charged"
            finally:
                store.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertCountEqual(list(executor.map(writer, range(2))), ["charged", "denied"])
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM events").fetchone()[0], 1
        )

    def test_copy_reconstruction_restart_or_changed_journal_cannot_recover_claim(self):
        claim = self.charge()
        reservation = object()
        claim.bind_reservation(reservation)
        with self.assertRaisesRegex(ValueError, "cannot be copied"):
            copy.copy(claim)
        copied = object.__new__(LiveStorageInstallationClaim)
        copied.__dict__.update(claim.__dict__)
        with self.assertRaisesRegex(ValueError, "original minted"):
            copied.verify()
        with self.assertRaises(Conflict):
            self.charge(self.open_store())
        replacement = self.directory / "replacement"
        replacement.write_bytes(self.store.path.read_bytes())
        replacement.chmod(0o600)
        replacement.replace(self.store.path)
        with self.assertRaisesRegex(ValueError, "replaced"):
            claim.verify()
        self.assertIs(claim._reservation, reservation)

    def test_unknown_result_consumes_same_claim_without_refund_or_new_token(self):
        claim = self.charge()
        reservation = object()
        claim.bind_reservation(reservation)
        claim.retain_unknown(reservation)
        self.assertEqual((claim.record.state, claim.record.installation), ("retained", "unknown"))
        claim.verify_reservation(reservation)
        self.assertIs(self.store._storage_installation_claims[claim.record.id], claim)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            claim.retain_unknown(reservation)
        with self.assertRaises(Conflict):
            self.charge(self.open_store())
        with self.assertRaisesRegex(ValueError, "one original"):
            claim.bind_reservation(object())

    def test_missing_events_changed_origin_or_reset_denies_original_readback(self):
        claim = self.charge()
        with self.store.transaction():
            changed = StorageInstallationCharge.model_validate(
                {**claim.record.model_dump(), "batch_started_monotonic": 200, "state": "retained"}
            )
            self.store._put("storage_installation", claim.record.id, changed, 1)
        with self.assertRaisesRegex(ValueError, "origin changed"):
            claim.verify()
        self.store.connection.execute("DELETE FROM events WHERE version=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            claim.verify()
        with self.assertRaisesRegex(ValueError, "ordered events disagree"):
            self.open_store()

    def test_failed_commit_returns_no_claim_and_original_store_cannot_retry(self):
        def reject_event(action, table, *_):
            return (
                sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_INSERT and table == "events"
                else sqlite3.SQLITE_OK
            )

        self.store.connection.set_authorizer(reject_event)
        with self.assertRaises(sqlite3.DatabaseError):
            self.charge()
        self.store.connection.set_authorizer(None)
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM records").fetchone()[0], 0
        )
        self.assertEqual(self.store._storage_installation_claims, {})
        with self.assertRaisesRegex(Conflict, "attempt consumed"):
            self.charge()

    def test_record_flags_and_noninteger_charges_supply_no_available_state(self):
        for changes in (
            {"state": "available"},
            {"tasks": 128.0},
            {"logical_bytes": 1},
            {"installation": "observed"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                StorageInstallationCharge.model_validate(
                    {
                        "id": "scope",
                        "owner": "a" * 64,
                        "configuration": "b" * 64,
                        "batch_started_monotonic": 100,
                        **changes,
                    }
                )


class Phase2DInstallationReservation(unittest.TestCase):
    def setUp(self):
        f = fixtures.Phase2DSetup()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.external_observer()
        self.f = f
        self.store = CoordinatorStore(f.f.root / "original-journal")
        self.addCleanup(self.store.close)
        self.origin = time.monotonic() - 1

    def reserve(self, store=None):
        return setup.reserve_storage_installation(
            store or self.store,
            self.f.parent,
            self.f.observer_group,
            self.f.aggregate,
            self.f.configuration,
            batch_started_monotonic=self.origin,
        )

    def test_full_charge_precedes_reservation_verification_and_failure_keeps_original_owner(self):
        original = setup.OwnedStorageReservation.verify
        seen = []

        def refuse(reservation):
            claim = reservation.capacity_claim
            claim.verify_reservation(reservation)
            seen.append(claim.record)
            self.assertIs(self.f.parent._installation_charge, claim)
            self.assertEqual(
                self.store.connection.execute("SELECT count(*) FROM events").fetchone()[0], 1
            )
            raise ValueError("synthetic installation refusal")

        with patch.object(setup.OwnedStorageReservation, "verify", refuse):
            with self.assertRaisesRegex(ValueError, "synthetic installation refusal"):
                self.reserve()
        reservation = self.f.parent._storage_reservation
        self.assertEqual(len(seen), 1)
        self.assertEqual(reservation.charges, setup.StorageCharges())
        self.assertEqual(reservation.capacity_claim.record.state, "retained")
        original(reservation)
        with self.assertRaisesRegex(ValueError, "attempt consumed"):
            self.reserve()

    def test_unknown_installation_denies_payload_before_wrapper_and_keeps_all_handles(self):
        reservation = self.reserve()
        handles = reservation._handles
        with patch.object(setup.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(ValueError, "growth readback unavailable"):
                setup.create_namespace_setup(
                    self.f.parent,
                    self.f.observer_group,
                    self.f.aggregate,
                    self.f.setup_group,
                    self.f.supervisor,
                    self.f.worker,
                    self.f.configuration,
                    self.f.preparation,
                    self.f.plan,
                    storage_reservation=reservation,
                )
            launch.assert_not_called()
        self.assertFalse(getattr(self.f.parent, "_setup_started", False))
        self.assertEqual(reservation._handles, handles)
        reservation.retain_unknown_installation()
        reservation.verify()
        self.assertEqual(reservation.charges, setup.StorageCharges())

    def test_missing_journal_and_fresh_store_cannot_replace_original_observer_attempt(self):
        reservation = self.reserve()
        self.store.path.unlink()
        with self.assertRaises(FileNotFoundError):
            reservation.verify()
        fresh = CoordinatorStore(self.f.f.root / "fresh-journal")
        self.addCleanup(fresh.close)
        with self.assertRaisesRegex(ValueError, "attempt consumed"):
            self.reserve(fresh)
        self.assertEqual(fresh.connection.execute("SELECT count(*) FROM records").fetchone()[0], 0)
        self.assertEqual(reservation.charges, setup.StorageCharges())

    def test_actual_original_timer_and_origin_allow_only_preparation_then_no_further_work(self):
        # Independently created fixture, not a reused prior reservation/timer.
        f = timer_fixtures.Phase2DBatchTimer()
        f.setUp(installation=True)
        self.addCleanup(f.doCleanups)
        reservation = f.reservation
        with f.effective_readback():
            reservation.verify_operational()
            with self.assertRaisesRegex(ValueError, "growth readback unavailable"):
                reservation.verify_installation()
            reservation.retain_unknown_installation()
            with self.assertRaisesRegex(ValueError, "preparation consumed"):
                reservation.verify_operational()
            reservation.verify()
        self.assertIs(reservation._batch_timer, f.timer)
        self.assertEqual(f.timer.cutoff_ns - f.timer.origin_ns, 570_000_000_000)
        self.assertEqual(f.timer.end_ns - f.timer.origin_ns, 600_000_000_000)
        self.assertEqual(reservation.charges, setup.StorageCharges())

    def test_failed_commit_consumes_observer_even_when_journal_has_no_charge(self):
        self.store.connection.execute("PRAGMA synchronous=OFF")
        with self.assertRaisesRegex(ValueError, "durability controls differ"):
            self.reserve()
        self.store.connection.execute("PRAGMA synchronous=FULL")
        with self.assertRaisesRegex(ValueError, "attempt consumed"):
            self.reserve()
        self.assertFalse(hasattr(self.f.parent, "_storage_reservation"))

    def test_missing_original_timer_denies_key_operation_and_consumes_unknown_charge(self):
        reservation = self.reserve()
        with patch.object(storage, "_keyctl") as kernel:
            with self.assertRaises(storage.KeyringCreationRefusal) as caught:
                storage.AnonymousKeyring.create(reservation=reservation)
            kernel.assert_not_called()
        self.assertIs(caught.exception.ring, reservation._private_ring)
        self.assertEqual(reservation.capacity_claim.record.state, "retained")
        self.assertEqual(reservation.capacity_claim.record.installation, "unknown")
        self.assertEqual(reservation.charges, setup.StorageCharges())
        with self.assertRaisesRegex(ValueError, "one-shot"):
            storage.AnonymousKeyring.create(reservation=reservation)

    def test_serialized_observed_result_does_not_supply_effective_installer(self):
        reservation = self.reserve()
        claim = reservation.capacity_claim
        observed = StorageInstallationCharge.model_validate(
            {**claim.record.model_dump(), "state": "retained", "installation": "observed"}
        )
        # Deliberately insert matching denial data, not an actual installer.
        with self.store.transaction():
            self.store._put("storage_installation", observed.id, observed, 1)
        claim._payload = observed.model_dump_json()
        claim.verify_reservation(reservation)
        with self.assertRaisesRegex(ValueError, "growth readback unavailable"):
            reservation.verify_installation()
        self.assertIs(self.f.parent._storage_reservation, reservation)
        self.assertIs(claim._reservation, reservation)

    def test_private_key_constructor_refusal_consumes_charge_before_any_key_effect(self):
        reservation = self.reserve()
        ring = object.__new__(storage.AnonymousKeyring)
        with patch.object(production, "_add_private_key") as kernel:
            with self.assertRaisesRegex(ValueError, "original independent batch timer"):
                production.PrivateEcryptfsKeys(reservation, ring)
            kernel.assert_not_called()
        keys = reservation._ecryptfs_keys
        self.assertTrue(keys.failed)
        self.assertIs(keys.ring, ring)
        self.assertEqual(reservation.capacity_claim.record.state, "retained")
        self.assertEqual(reservation.capacity_claim.record.installation, "unknown")
        with self.assertRaisesRegex(ValueError, "one-shot"):
            keys.create()
        self.assertEqual(reservation.charges, setup.StorageCharges())


class Phase2DInstallationDirectory(unittest.TestCase):
    def test_unqualified_parent_refuses_before_child_with_original_charge_and_handles_retained(
        self,
    ):
        f = timer_fixtures.Phase2DBatchTimer()
        f.setUp(installation=True)
        self.addCleanup(f.doCleanups)
        descriptor = os.open(f.f.f.root, os.O_RDONLY)
        self.addCleanup(os.close, descriptor)
        with f.effective_readback():
            jobs = storage.BoundedStorageJobs(
                f.f.parent,
                f.f.observer_group,
                f.f.aggregate,
                time.monotonic() + 20,
                execution_group=f.f.setup_group,
                batch_timer=f.timer,
            )
            with patch.object(
                production.os, "fork", side_effect=AssertionError("real fork forbidden")
            ) as fork:
                with self.assertRaises(production.ProductionRefusal) as caught:
                    production.OwnedBackingProduction(
                        f.reservation,
                        None,
                        jobs,
                        installation_parent_fd=descriptor,
                    )
                fork.assert_not_called()
            owner = caught.exception.production
            self.addCleanup(os.close, owner.handles["installation-parent"])
            self.assertIs(f.reservation._production, owner)
            self.assertEqual(owner.original_installation_parent, descriptor)
            self.assertEqual(
                os.fstat(owner.handles["installation-parent"]).st_ino, os.fstat(descriptor).st_ino
            )
            self.assertEqual(f.reservation.capacity_claim.record.installation, "unknown")
            self.assertEqual(f.reservation.capacity_claim.record.state, "retained")
            self.assertEqual(f.reservation.charges, setup.StorageCharges())
            with self.assertRaisesRegex(ValueError, "one-shot"):
                production.OwnedBackingProduction(
                    f.reservation, None, jobs, installation_parent_fd=descriptor
                )

    def producer(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.root = "/private-original/session"
        owner.handles = {"installation-parent": 101}
        owner._installation_parent = Mock()
        owner._directory_channel = SimpleNamespace(transfer=Mock())
        return owner

    def test_root_custody_ack_precedes_backing_creation_with_no_path_retry(self):
        owner = self.producer()
        events = []
        owner._installation_parent.side_effect = lambda fd: events.append(("readback", fd))
        owner._directory_channel.transfer.side_effect = lambda name, fd: events.append(
            ("custody", name, fd)
        )
        with (
            patch.object(
                production.os,
                "mkdir",
                side_effect=lambda name, mode, **kw: events.append(("mkdir", name, kw["dir_fd"])),
            ),
            patch.object(production.os, "open", side_effect=[102, 103]) as open_directory,
        ):
            self.assertEqual(owner._prepare_directory_child(), b"directory-prepared")
        self.assertEqual(
            events,
            [
                ("readback", 101),
                ("mkdir", "session", 101),
                ("custody", "installation-root", 102),
                ("mkdir", "backing", 102),
                ("custody", "directory", 103),
            ],
        )
        self.assertEqual(open_directory.call_count, 2)
        self.assertTrue(
            all(call.args[1] & production.os.O_NOFOLLOW for call in open_directory.call_args_list)
        )

    def test_failed_root_transfer_prevents_backing_effects_and_path_collision_is_not_retried(self):
        owner = self.producer()
        owner._directory_channel.transfer.side_effect = ValueError("unknown actual FD handoff")
        with (
            patch.object(production.os, "mkdir") as mkdir,
            patch.object(production.os, "open", return_value=102),
        ):
            with self.assertRaisesRegex(ValueError, "unknown actual FD"):
                owner._prepare_directory_child()
        self.assertEqual(mkdir.call_count, 1)
        with (
            patch.object(production.os, "mkdir", side_effect=FileExistsError) as mkdir,
            patch.object(production.os, "open") as open_directory,
        ):
            with self.assertRaises(FileExistsError):
                owner._prepare_directory_child()
        mkdir.assert_called_once()
        open_directory.assert_not_called()


class Phase2DInstallationJournalGrowth(unittest.TestCase):
    """Real SQLite/output fixtures; retained Linux task and limits are synthetic."""

    def setUp(self):
        fixture = timer_fixtures.Phase2DBatchTimer()
        fixture.setUp(installation=True, outer_observer=True)
        self.addCleanup(fixture.doCleanups)
        self.enterContext(fixture.effective_readback())
        self.enterContext(
            patch(
                "crewshal.durable.os.fstatvfs",
                return_value=SimpleNamespace(f_bsize=4096, f_frsize=4096),
            )
        )
        self.fixture = fixture
        self.reservation = fixture.reservation
        self.store = self.reservation.capacity_claim._store
        self.limits = fixture.f.bridge.parent_path / "limits"
        self.limits.write_text("Max file size 1073741824 1073741824 bytes\n")
        info = self.store.path.stat()
        self.lock_rows = fixture.f.bridge.proc_root / "locks"
        self.lock_record = (
            f"1: POSIX  ADVISORY  WRITE {os.getpid()} "
            f"{os.major(info.st_dev):02x}:{os.minor(info.st_dev):02x}:{info.st_ino} "
            "1073741824 1073742335\n"
        )
        self.lock_rows.write_text(self.lock_record)
        proc = patch(
            "crewshal.linux_parent._proc_root",
            side_effect=lambda boot: os.open(
                fixture.f.bridge.proc_root, os.O_RDONLY | os.O_DIRECTORY
            ),
        )
        proc.start()
        self.addCleanup(proc.stop)
        self.addCleanup(self.close_fixture_descriptors)

    def close_fixture_descriptors(self):
        growth = self.store._storage_growth
        retained = set()
        if growth is not None:
            for descriptor in growth.descriptors:
                os.close(descriptor)
                retained.add(descriptor)
        birth = self.store._directory_birth_fd
        if birth >= 0 and birth not in retained:
            os.close(birth)
        self.store._directory_birth_fd = -1

    def bind(self):
        return self.store.bind_installation_journal(self.reservation)

    def sealed_output_fixture(self):
        """Synthetic installation admission; actual SQLite/files remain fresh."""
        growth = self.bind()
        self.store.connection.execute(f"PRAGMA max_page_count={131072 // growth.page_size}")
        self.limits.write_text("Max file size 131072 131072 bytes\n")
        growth.payload_bound = True
        admission = patch.object(self.reservation, "verify_output_admission")
        admission.start()
        self.addCleanup(admission.stop)
        growth.verify()
        return growth

    def test_original_connection_holds_exclusive_lock_and_page_limit_is_effective(self):
        growth = self.bind()
        growth.verify()
        other = sqlite3.connect(self.store.path, timeout=0)
        self.addCleanup(other.close)
        with self.assertRaisesRegex(sqlite3.OperationalError, "locked"):
            other.execute("BEGIN IMMEDIATE")
        # Actual SQLite writes, not an asserted pragma or a mocked disk-full result.
        self.store.connection.execute("CREATE TABLE fill (payload BLOB)")
        with self.assertRaisesRegex(sqlite3.DatabaseError, "full"):
            for _ in range(20):
                self.store.connection.execute("INSERT INTO fill VALUES (zeroblob(1048576))")
        self.assertLessEqual(self.store.path.stat().st_size, 16777216)
        growth.verify()
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()

    def test_original_journal_identity_and_observer_limits_are_resampled(self):
        growth = self.bind()
        for content in (
            "Max file size 1073741824 unlimited bytes\n",
            "Max file size 1073741824 1073741824 bytes\n" * 2,
            "Max file size 1073741825 1073741825 bytes\n",
        ):
            with self.subTest(content=content):
                self.limits.write_text(content)
                with self.assertRaisesRegex(ValueError, "file limits differ"):
                    growth.verify()
        self.limits.write_text("Max file size 1073741824 1073741824 bytes\n")
        replacement = self.store.directory / "replacement"
        replacement.write_bytes(self.store.path.read_bytes())
        replacement.chmod(0o600)
        replacement.replace(self.store.path)
        with self.assertRaisesRegex(ValueError, "readback differs"):
            growth.verify()
        os.fstat(growth.database_fd)

    def test_lock_flag_and_empty_or_wrong_kernel_rows_do_not_prove_exclusion(self):
        growth = self.bind()
        for rows in (
            "",
            self.lock_record.replace("WRITE", "READ"),
            self.lock_record.replace("1073742335", "1073742334"),
            self.lock_record.replace(f" {os.getpid()} ", f" {os.getpid() + 1} "),
            self.lock_record.replace("POSIX", "FLOCK"),
            self.lock_record.replace("1073741824", "1073741825"),
        ):
            with self.subTest(rows=rows):
                self.lock_rows.write_text(rows)
                with self.assertRaisesRegex(ValueError, "exclusive lock readback unavailable"):
                    growth.verify()
        self.lock_rows.write_text(self.lock_record)
        growth.verify()

    def test_changed_sqlite_controls_refuse_without_capacity_or_payload_admission(self):
        growth = self.bind()
        for pragma, changed, original in (
            ("max_page_count", 8192, 4096),
            ("temp_store", 1, 2),
            ("synchronous", 0, 2),
        ):
            with self.subTest(pragma=pragma):
                self.store.connection.execute(f"PRAGMA {pragma}={changed}")
                with self.assertRaisesRegex(ValueError, "growth controls differ"):
                    growth.verify()
                self.store.connection.execute(f"PRAGMA {pragma}={original}")
        growth.verify()
        with self.assertRaisesRegex(ValueError, "growth readback unavailable"):
            self.reservation.verify_installation()
        self.assertEqual(self.reservation.charges, setup.StorageCharges())

    def test_capture_charge_precedes_write_and_partial_output_stays_retained(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        data = b"partial output"
        fingerprint = digest(data)
        with patch("crewshal.durable.os.fsync", side_effect=OSError("synthetic sync refusal")):
            with self.assertRaisesRegex(OSError, "synthetic sync refusal"):
                self.store._artifact(fingerprint, data)
        self.assertEqual(growth.output_charge, 135168)
        self.assertEqual(growth.artifact_charges, {fingerprint: 135168})
        paths = list(self.store.directory.joinpath("artifacts").iterdir())
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].read_bytes(), data)
        self.assertEqual(os.pread(growth.descriptors[-1], len(data), 0), data)
        with self.assertRaises(FileNotFoundError):
            self.store._artifact(fingerprint, data)
        self.assertEqual(growth.output_charge, 135168)

    def test_finite_output_budget_is_not_refunded_or_reconstructed(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        for number in range(124):
            data = bytes([number])
            self.store._artifact(digest(data), data)
        self.assertEqual(growth.output_charge, 16760832)
        existing = set(self.store.directory.joinpath("artifacts").iterdir())
        with self.assertRaisesRegex(ValueError, "output capacity exhausted"):
            self.store._artifact(digest(b"overflow"), b"overflow")
        self.assertEqual(set(self.store.directory.joinpath("artifacts").iterdir()), existing)
        with self.assertRaisesRegex(TypeError, "cannot be copied"):
            copy.copy(growth)
        self.assertEqual(growth.output_charge, 16760832)

    def test_preparation_outputs_refuse_before_directory_or_inode_creation(self):
        from crewshal.model import digest

        growth = self.bind()
        with self.assertRaisesRegex(ValueError, "sealed original file limits"):
            self.store._artifact(digest(b"preparation"), b"preparation")
        self.assertFalse(self.store.directory.joinpath("artifacts").exists())
        self.assertEqual(growth.output_charge, 0)

    def test_small_output_reserves_full_retained_inode_growth(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        data = b"small retained output"
        self.store._artifact(digest(data), data)
        descriptor = growth.descriptors[-1]
        os.ftruncate(descriptor, 131072)
        self.assertEqual(os.fstat(descriptor).st_size, 131072)
        self.assertEqual(growth.output_charge, 135168)
        growth.verify()
        with self.assertRaises(ValueError):
            self.store._artifact(digest(data), data)
        self.assertEqual(growth.output_charge, 135168)

    def test_preexisting_leaf_with_large_inode_cannot_mint_installation_growth(self):
        original_init = CoordinatorStore.__init__

        def preexisting(store, directory, *, migrate=False):
            if directory.name == "installation-journal":
                directory.mkdir(mode=0o700)
                sibling = directory / "preexisting-control.bin"
                with sibling.open("wb") as stream:
                    stream.truncate(8589934593)
                sibling.chmod(0o600)
            original_init(store, directory, migrate=migrate)

        other = Phase2DInstallationJournalGrowth()
        self.addCleanup(other.doCleanups)
        with patch.object(CoordinatorStore, "__init__", preexisting):
            other.setUp()
        self.assertFalse(other.store._created_directory)
        self.assertTrue(other.store._created_journal)
        self.assertGreater(
            other.store.directory.joinpath("preexisting-control.bin").stat().st_size,
            8589934592,
        )
        with self.assertRaisesRegex(ValueError, "birth/output custody unknown"):
            other.bind()
        self.assertTrue(other.store._storage_growth.failed)
        self.assertEqual(other.reservation.charges, setup.StorageCharges())
        with self.assertRaisesRegex(ValueError, "consumed"):
            other.bind()

    def test_fresh_journal_retains_birth_directory_before_database_and_binding(self):
        birth = self.store._directory_birth_fd
        self.assertGreaterEqual(birth, 0)
        info = os.fstat(birth)
        self.assertEqual((info.st_dev, info.st_ino), self.store._directory_birth_identity)
        growth = self.bind()
        self.assertEqual(growth.directory_fd, birth)
        self.assertIn(birth, growth.descriptors)
        self.store.close()
        self.assertEqual(os.fstat(birth).st_ino, info.st_ino)

    def test_new_leaf_replacement_preserving_database_inode_refuses_original_custody(self):
        directory = self.store.directory
        retained = directory.with_name("retained-original-journal-directory")
        directory.rename(retained)
        directory.mkdir(mode=0o700)
        retained.joinpath(self.store.path.name).rename(self.store.path)
        with self.assertRaisesRegex(ValueError, "newly created journal directory replaced"):
            self.bind()
        growth = self.store._storage_growth
        self.assertTrue(growth.failed)
        self.assertEqual(growth.directory_fd, self.store._directory_birth_fd)
        self.assertNotEqual(os.fstat(growth.directory_fd).st_ino, directory.stat().st_ino)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()

    def test_same_content_replacement_cannot_reuse_retained_output_inode(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        data = b"independently retained output"
        fingerprint = digest(data)
        self.store._artifact(fingerprint, data)
        original = growth.artifact_handles[fingerprint]
        original_info = os.fstat(original)
        path = self.store.directory / "artifacts" / fingerprint
        path.rename(path.with_name(".retained-original"))
        path.write_bytes(data)
        path.chmod(0o600)
        self.assertNotEqual(path.stat().st_ino, original_info.st_ino)
        with self.assertRaisesRegex(ValueError, "original retained output inode"):
            self.store._artifact(fingerprint, data)
        self.assertEqual(os.pread(original, len(data), 0), data)
        self.assertEqual(growth.output_charge, 135168)

    def test_actual_retained_output_growth_and_metadata_are_resampled(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        fingerprint = digest(b"original")
        self.store._artifact(fingerprint, b"original")
        original = growth.artifact_handles[fingerprint]
        os.ftruncate(original, 131072)
        growth.verify()
        os.ftruncate(original, 131073)
        with self.assertRaisesRegex(ValueError, "retained output inode growth"):
            growth.verify()
        self.assertEqual(growth.output_charge, 135168)
        self.assertEqual(os.fstat(original).st_size, 131073)
        # Local fixture restoration tests each independent metadata refusal;
        # it does not restore an operational admission or release authority.
        os.ftruncate(original, 131072)
        os.fchmod(original, 0o640)
        with self.assertRaisesRegex(ValueError, "retained output inode growth"):
            growth.verify()
        os.fchmod(original, 0o600)
        path = self.store.directory / "artifacts" / fingerprint
        os.link(path, path.with_name(".retained-alias"))
        with self.assertRaisesRegex(ValueError, "retained output inode growth"):
            growth.verify()

    def test_writer_duplication_failure_retains_actual_acquired_output_fd(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        fingerprint = digest(b"unknown writer acquisition")
        original_dup = os.dup

        def refuse_writer(descriptor):
            if descriptor in growth.artifact_handles.values():
                raise OSError("synthetic writer duplication failure")
            return original_dup(descriptor)

        with patch("crewshal.durable.os.dup", side_effect=refuse_writer):
            with self.assertRaisesRegex(OSError, "writer duplication failure"):
                self.store._artifact(fingerprint, b"unknown writer acquisition")
        original = growth.artifact_handles[fingerprint]
        self.assertIn(original, growth.descriptors)
        self.assertEqual(os.fstat(original).st_size, 0)
        self.assertEqual(growth.output_charge, 135168)
        self.assertEqual(len(list(self.store.directory.joinpath("artifacts").iterdir())), 1)
        with self.assertRaises(FileNotFoundError):
            self.store._artifact(fingerprint, b"unknown writer acquisition")

    def test_metadata_acquisition_failure_keeps_actual_output_before_first_readback(self):
        from crewshal.model import digest

        growth = self.sealed_output_fixture()
        fingerprint = digest(b"unknown output metadata")
        original_stat = os.fstat

        def refuse_output_readback(descriptor):
            if descriptor in growth.artifact_handles.values():
                raise OSError("synthetic initial output metadata refusal")
            return original_stat(descriptor)

        with patch("crewshal.durable.os.fstat", side_effect=refuse_output_readback):
            with self.assertRaisesRegex(OSError, "initial output metadata refusal"):
                self.store._artifact(fingerprint, b"unknown output metadata")
        original = growth.artifact_handles[fingerprint]
        self.assertIn(original, growth.descriptors)
        self.assertEqual(original_stat(original).st_size, 0)
        self.assertEqual(growth.output_charge, 135168)
        with self.assertRaisesRegex(ValueError, "output acquisition remains unknown"):
            growth.verify()
        with self.assertRaisesRegex(ValueError, "output acquisition remains unknown"):
            self.store._artifact(fingerprint, b"unknown output metadata")

    def test_unknown_birth_or_limits_consume_binding_and_retain_charge(self):
        self.limits.write_text("Max file size unlimited unlimited bytes\n")
        with self.assertRaisesRegex(ValueError, "file limits differ"):
            self.bind()
        growth = self.store._storage_growth
        self.assertTrue(growth.failed)
        self.assertIs(growth.reservation, self.reservation)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        self.assertEqual(self.reservation.capacity_claim.record.installation, "unknown")
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()
        for descriptor in growth.descriptors:
            os.fstat(descriptor)

    def test_persist_journal_keeps_original_inode_across_real_transactions(self):
        growth = self.bind()
        original = os.fstat(growth.journal_fd)
        self.store.connection.execute("CREATE TABLE transaction_fixture(value TEXT)")
        for number in range(5):
            with self.store.transaction():
                self.store.connection.execute(
                    "INSERT INTO transaction_fixture VALUES(?)", (str(number),)
                )
            growth.verify()
            linked = Path(str(self.store.path) + "-journal").stat()
            self.assertEqual((linked.st_dev, linked.st_ino), (original.st_dev, original.st_ino))
        replacement = self.store.directory / "different-journal"
        replacement.write_bytes(b"different original inode")
        replacement.chmod(0o600)
        replacement.replace(Path(str(self.store.path) + "-journal"))
        with self.assertRaisesRegex(ValueError, "readback differs"):
            growth.verify()
        self.assertEqual(os.fstat(growth.journal_fd).st_ino, original.st_ino)

    def test_volume_readback_alone_cannot_open_incompatible_payload_growth_admission(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.reservation, owner.failed = self.reservation, False
        self.reservation._production = owner
        proof = object.__new__(production.EffectiveInstallation)
        proof.production, proof.reservation, proof.failed = owner, self.reservation, False
        self.reservation._installation = proof
        with patch.object(proof, "verify") as actual_volume_seam:
            with self.assertRaisesRegex(ValueError, "MAP_SHARED denial conflicts"):
                self.store._retain_observed_installation(proof)
            actual_volume_seam.assert_called_once()
        self.assertTrue(proof.failed)
        self.assertTrue(owner.failed)
        self.assertEqual(self.reservation.capacity_claim.record.installation, "unknown")
        self.assertEqual(self.reservation.capacity_claim.record.state, "retained")
        self.assertTrue(self.reservation.capacity_claim._terminal_attempted)
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.store._retain_observed_installation(proof)

    def test_incomplete_installation_consumes_charge_before_tightening_or_ready_record(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.reservation = self.reservation
        owner.failed = False
        owner.verify = Mock()
        self.reservation._production = owner
        with patch.object(production.resource, "setrlimit") as limits:
            with self.assertRaisesRegex(
                production.ProductionRefusal, "complete original installation"
            ):
                owner.complete_installation()
            limits.assert_not_called()
            with self.assertRaisesRegex(ValueError, "consumed"):
                owner.complete_installation()
        self.assertTrue(self.reservation._installation.failed)
        self.assertEqual(self.reservation.capacity_claim.record.installation, "unknown")
        self.assertEqual(self.reservation.capacity_claim.record.state, "retained")
        self.assertEqual(self.reservation.charges, setup.StorageCharges())
        with self.assertRaises(ValueError):
            self.reservation.verify_installation()


class Phase2DPhysicalDomainSource(unittest.TestCase):
    """Fresh file/proc data with explicit synthetic mount/device/job seams."""

    def test_domain_objects_pin_namespace_and_backing_before_mutation(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.root = "/run/original-domain"
        owner.handles = {"installation-parent": 101}
        events = []
        owner._domain_channel = SimpleNamespace(
            transfer=lambda name, fd: events.append(("custody", name, fd))
        )
        owner._attach_created_loop = Mock(
            side_effect=lambda *args: events.append(("attach", args[:3]))
        )
        with (
            patch.object(
                production,
                "_unshare_mount_namespace",
                side_effect=lambda: events.append(("namespace",)),
            ),
            patch.object(
                production, "_namespace_is_private", side_effect=lambda: events.append(("private",))
            ),
            patch.object(production.os, "open", side_effect=[102, 103, 104]),
            patch.object(
                production.os,
                "ftruncate",
                side_effect=lambda fd, size: events.append(("truncate", fd, size)),
            ),
        ):
            self.assertEqual(owner._domain_objects_child(), b"domain-objects-created")
        self.assertEqual(
            events,
            [
                ("namespace",),
                ("custody", "namespace", 102),
                ("private",),
                ("custody", "loop-control", 103),
                ("custody", "physical-domain.img", 104),
                ("truncate", 104, 1073741824),
                ("attach", ("physical-domain.img", 1073741824, 104)),
            ],
        )

    def test_domain_custody_refusal_never_truncates_or_attaches(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.root = "/run/original-domain"
        owner.handles = {"installation-parent": 101}
        owner._domain_channel = SimpleNamespace(
            transfer=Mock(side_effect=[None, None, ValueError("unknown custody")])
        )
        owner._attach_created_loop = Mock()
        with (
            patch.object(production, "_unshare_mount_namespace"),
            patch.object(production, "_namespace_is_private"),
            patch.object(production.os, "open", side_effect=[102, 103, 104]),
            patch.object(production.os, "ftruncate") as truncate,
        ):
            with self.assertRaisesRegex(ValueError, "unknown custody"):
                owner._domain_objects_child()
        truncate.assert_not_called()
        owner._attach_created_loop.assert_not_called()

    def test_constructor_admission_refusal_consumes_domain_without_any_kernel_effect(self):
        owner = object.__new__(production.OwnedBackingProduction)
        owner.handles = {"installation-root": 101}
        owner.attempted = owner.failed = False
        owner.reservation = object()
        owner.verify = Mock(side_effect=ValueError("original admission refused"))
        with patch.object(production.resource, "setrlimit") as limits:
            with self.assertRaisesRegex(production.ProductionRefusal, "original admission refused"):
                owner.install_physical_domain(None, 102)
            with self.assertRaisesRegex(ValueError, "no retry"):
                owner.install_physical_domain(None, 102)
        self.assertTrue(owner.failed)
        self.assertEqual(owner.handles, {"installation-root": 101})
        limits.assert_not_called()

    def domain_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        image = root / "domain.img"
        with image.open("wb") as stream:
            stream.truncate(1073741824)
        descriptor = os.open(image, os.O_RDWR)
        self.addCleanup(os.close, descriptor)
        block = bytearray(1024)
        block[:4] = (8192).to_bytes(4, "little")
        block[4:8] = (262144).to_bytes(4, "little")
        block[24:28] = (2).to_bytes(4, "little")
        block[56:58] = b"\x53\xef"
        os.pwrite(descriptor, block, 1024)
        owner = object.__new__(production.OwnedBackingProduction)
        owner.root = "/run/original-domain"
        owner.handles = {
            "physical-domain.img": descriptor,
            "loop:physical-domain.img": 101,
            "physical-domain-root": 102,
            "namespace": 103,
        }
        owner.reservation = SimpleNamespace(
            observer=SimpleNamespace(spec=SimpleNamespace(boot_id="synthetic-boot"))
        )
        raw = bytes(production.LOOP_INFO64.size)
        owner._expected_loop = Mock(return_value=raw)
        device = image.stat().st_dev
        original_stat = production.os.fstat

        def metadata(fd):
            if fd == 101:
                return SimpleNamespace(st_rdev=device)
            if fd == 102:
                return SimpleNamespace(st_dev=device, st_uid=0, st_gid=0, st_mode=0o40700)
            return original_stat(fd)

        geometry = SimpleNamespace(f_bsize=4096, f_frsize=4096, f_blocks=260000, f_files=8192)
        proc = root / "proc"
        (proc / str(os.getpid()) / "fdinfo").mkdir(parents=True)
        (proc / str(os.getpid()) / "fdinfo" / "102").write_text("mnt_id: 77\n")
        mountinfo = proc / str(os.getpid()) / "mountinfo"
        row = f"77 1 {os.major(device)}:{os.minor(device)} / {owner.root} rw,nosuid,nodev - ext4 /dev/loop0 rw,max_dir_size_kb=64\n"
        mountinfo.write_text(row)
        stack = self.enterContext(__import__("contextlib").ExitStack())
        stack.enter_context(patch.object(production, "_enter_owned_namespace"))
        stack.enter_context(patch.object(production, "_filesystem_magic", return_value=0xEF53))
        stack.enter_context(patch.object(production.os, "fstat", side_effect=metadata))
        stack.enter_context(patch.object(production.os, "fstatvfs", return_value=geometry))
        ioctl = stack.enter_context(
            patch.object(
                production.fcntl,
                "ioctl",
                side_effect=lambda fd, op, buf, mutate: buf.__setitem__(slice(None), raw),
            )
        )
        stack.enter_context(
            patch(
                "crewshal.linux_parent._proc_root",
                side_effect=lambda boot: os.open(proc, os.O_RDONLY | os.O_DIRECTORY),
            )
        )
        return owner, image, descriptor, block, geometry, mountinfo, row, ioctl

    def test_actual_domain_header_and_positive_mount_readback_require_original_geometry(self):
        owner, image, descriptor, block, geometry, mountinfo, row, ioctl = self.domain_fixture()
        self.assertEqual(owner._domain_readback_child(), bytes(production.LOOP_INFO64.size))
        for count in (10, 8193):
            with self.subTest(inodes=count):
                block[:4] = count.to_bytes(4, "little")
                os.pwrite(descriptor, block, 1024)
                with self.assertRaisesRegex(ValueError, "inode geometry"):
                    owner._domain_readback_child()
        self.assertEqual(image.stat().st_size, 1073741824)

    def test_requested_mount_flags_and_free_space_do_not_supply_domain_readback(self):
        owner, image, descriptor, block, geometry, mountinfo, row, ioctl = self.domain_fixture()
        for changed in (
            "",
            row + row,
            row.replace("max_dir_size_kb=64", "max_dir_size_kb=0"),
            row.replace("max_dir_size_kb=64", "max_dir_size_kb=64,max_dir_size_kb=64"),
            row.replace("rw,nosuid,nodev", "rw,nodev"),
            row.replace("ext4", "tmpfs"),
        ):
            with self.subTest(row=changed):
                mountinfo.write_text(changed)
                with self.assertRaisesRegex(ValueError, "mount identity|growth controls"):
                    owner._domain_readback_child()
        mountinfo.write_text(row)
        geometry.f_blocks = 262145
        with self.assertRaisesRegex(ValueError, "filesystem geometry"):
            owner._domain_readback_child()
        os.fstat(descriptor)

    def test_changed_domain_backing_or_kernel_loop_keeps_unknown_and_refuses(self):
        owner, image, descriptor, block, geometry, mountinfo, row, ioctl = self.domain_fixture()
        ioctl.side_effect = lambda fd, op, buf, mutate: buf.__setitem__(
            slice(None), b"x" * len(buf)
        )
        with self.assertRaisesRegex(ValueError, "loop binding differs"):
            owner._domain_readback_child()
        os.ftruncate(descriptor, 1073741825)
        with self.assertRaisesRegex(ValueError, "backing exceeds fixed bound"):
            owner._domain_readback_child()
        os.fstat(descriptor)


class Phase2DCombinedGrowthSource(unittest.TestCase):
    """Bound arithmetic and refusal checks with explicit synthetic kernel data."""

    def setUp(self):
        self.proof = object.__new__(production.EffectiveInstallation)
        self.owner = SimpleNamespace(
            handles={"readonly-projection": 203},
            _domain_readback_child=Mock(return_value=bytes(production.LOOP_INFO64.size)),
            _readback=Mock(return_value=bytes(5 * production.LOOP_INFO64.size)),
            projected_inventory=SimpleNamespace(verify=Mock()),
            mounts={
                role + suffix: "/run/original/" + role + suffix
                for role in production.ROLE_UIDS
                for suffix in ("-lower", "-upper")
            },
        )
        self.proof.production = self.owner
        self.namespace = SimpleNamespace(device=1, inode=2)
        self.state = SimpleNamespace(
            namespace=self.namespace,
            keyring_state="present",
            backing=dict.fromkeys(production.ALL_BACKING_SIZES),
            loops=dict.fromkeys(production.ALL_BACKING_SIZES),
            mounts=dict(self.owner.mounts),
            model_dump=lambda: {"namespace": {"device": 1, "inode": 2}},
        )
        self.proof.physical = SimpleNamespace(
            initial=SimpleNamespace(namespace=self.namespace),
            _readback=Mock(return_value=self.state),
        )
        self.metadata, self.geometry = {}, {203: SimpleNamespace(f_flag=os.ST_RDONLY)}
        for index, (role, uid) in enumerate(production.ROLE_UIDS.items()):
            lower, upper = 60 + index, 70 + index
            self.owner.handles["mounted:" + role + "-lower"] = lower
            self.owner.handles["mounted:" + role + "-upper"] = upper
            self.metadata[upper] = SimpleNamespace(st_uid=uid, st_gid=uid, st_mode=0o40700)
            self.geometry[lower] = SimpleNamespace(
                f_bsize=4096,
                f_frsize=4096,
                f_blocks=production.ALL_BACKING_SIZES[role + ".img"] // 4096,
                f_files=production.EXT4_INODE_LIMITS[role + ".img"],
            )
        self.enterContext(
            patch.object(production.os, "fstat", side_effect=lambda fd: self.metadata[fd])
        )
        self.enterContext(
            patch.object(production.os, "fstatvfs", side_effect=lambda fd: self.geometry[fd])
        )
        self.enterContext(
            patch.object(
                production,
                "_filesystem_magic",
                side_effect=lambda fd: 0xEF53 if fd < 70 else 0xF15F,
            )
        )

    def test_every_representation_is_charged_below_original_total_without_measured_free_space(self):
        import json

        result = json.loads(self.proof._readback_child())
        self.assertLessEqual(result["logical_bound"], 8589934592)
        self.assertEqual(result["logical_bound"], result["allocated_bound"])
        self.assertGreater(result["logical_bound"], 6 * 1073741824)
        self.assertEqual(set(result["role_geometry"]), set(production.ROLE_UIDS))
        self.owner.projected_inventory.verify.assert_called_once()
        self.proof.physical._readback.assert_called_once()

    def test_missing_original_kernel_objects_and_writable_root_refuse(self):
        self.geometry[203].f_flag = 0
        with self.assertRaisesRegex(ValueError, "root projection is writable"):
            self.proof._readback_child()
        self.geometry[203].f_flag = os.ST_RDONLY
        self.state.keyring_state = "unknown"
        with self.assertRaisesRegex(ValueError, "kernel readback differs"):
            self.proof._readback_child()
        self.state.keyring_state = "present"
        self.state.loops.pop("candidate.img")
        with self.assertRaisesRegex(ValueError, "kernel readback differs"):
            self.proof._readback_child()

    def test_role_inode_size_permissions_and_geometry_must_actually_fit(self):
        for mutate in (
            lambda: setattr(self.geometry[61], "f_files", 65),
            lambda: setattr(self.geometry[61], "f_bsize", 8192),
            lambda: setattr(self.geometry[61], "f_blocks", 4097),
            lambda: setattr(self.metadata[71], "st_uid", 0),
        ):
            with self.subTest(mutate=mutate):
                self.geometry[61] = SimpleNamespace(
                    f_bsize=4096, f_frsize=4096, f_blocks=4096, f_files=64
                )
                self.metadata[71] = SimpleNamespace(st_uid=65534, st_gid=65534, st_mode=0o40700)
                mutate()
                with self.assertRaisesRegex(ValueError, "role filesystem growth bound"):
                    self.proof._readback_child()

    def test_serialized_data_and_arbitrary_actions_cannot_mint_installed_jobs(self):
        with self.assertRaisesRegex(ValueError, "original producer"):
            production.EffectiveInstallation()
        with self.assertRaisesRegex(TypeError, "cannot be copied"):
            copy.copy(self.proof)
        self.proof._jobs = object()
        self.proof._readback_jobs = object()
        self.proof.verify_custody = Mock()
        with self.assertRaisesRegex(ValueError, "original fixed readback"):
            self.proof.verify_registered_action(self.proof._jobs, lambda: b"caller ready")
        self.proof.verify_custody.assert_not_called()


if __name__ == "__main__":
    unittest.main()
