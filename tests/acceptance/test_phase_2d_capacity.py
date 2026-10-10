"""Synthetic irreversible capacity denial; no Linux, credentials or launchers."""

from concurrent.futures import ThreadPoolExecutor
import copy
from pathlib import Path
import threading
import tempfile
import unittest
import sqlite3

from crewshal.contracts import StorageCapacityDomain
from crewshal.durable import Conflict, CoordinatorStore, LiveStorageCapacityClaim, SCHEMA_VERSION


INSTALLATION = "a" * 64
OWNER = "b" * 64
CONFIGURATION = "c" * 64
DOMAIN = "fixed-installed-pool"


class Phase2DCapacity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "private-journal"
        self.store = self.open_store()

    def open_store(self):
        store = CoordinatorStore(self.directory)
        self.addCleanup(store.close)
        return store

    def installed_fixture(self):
        # Data fixture only: no source API supplies or proves installed capacity.
        record = StorageCapacityDomain(id=DOMAIN, installation=INSTALLATION, state="installed")
        with self.store.transaction():
            self.store._put("storage_capacity", DOMAIN, record, 0)

    def claim(self, store=None, **changes):
        arguments = {
            "expected_version": 1,
            "installation": INSTALLATION,
            "owner": OWNER,
            "configuration": CONFIGURATION,
            "batch_started_monotonic": 100.0,
        }
        arguments.update(changes)
        return (store or self.store).claim_storage_capacity(DOMAIN, **arguments)

    def test_absent_domain_or_fresh_database_never_initializes_available_capacity(self):
        with self.assertRaisesRegex(ValueError, "unknown, not free"):
            self.claim()
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM records").fetchone()[0], 0
        )
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM events").fetchone()[0], 0
        )

    def test_committed_claim_keeps_full_charges_and_existing_schema(self):
        self.installed_fixture()
        claim = self.claim()
        claim.verify()
        self.assertEqual(
            (
                claim.record.memory_bytes,
                claim.record.tasks,
                claim.record.logical_bytes,
                claim.record.allocated_bytes,
            ),
            (805306368, 128, 8589934592, 8589934592),
        )
        self.assertEqual(claim.record.batch_started_monotonic, 100.0)
        self.assertEqual(claim.record.state, "retained")
        self.assertEqual(
            self.store.connection.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION
        )
        self.assertEqual(
            self.store.connection.execute(
                "SELECT version FROM events ORDER BY sequence"
            ).fetchall()[0][0],
            1,
        )
        self.assertEqual(len(self.store.connection.execute("SELECT * FROM events").fetchall()), 2)

    def test_second_handle_and_restart_cannot_reclaim_or_reconstruct_live_claim(self):
        self.installed_fixture()
        claim = self.claim()
        other = self.open_store()
        with self.assertRaisesRegex(Conflict, "fully charged"):
            self.claim(other, owner="d" * 64, batch_started_monotonic=200.0)
        restarted = self.open_store()
        with self.assertRaisesRegex(Conflict, "fully charged"):
            self.claim(restarted)
        record, version = restarted.get("storage_capacity", DOMAIN, StorageCapacityDomain)
        self.assertEqual(version, 2)
        self.assertEqual(record, claim.record)
        with self.assertRaises(ValueError):
            LiveStorageCapacityClaim()

    def test_concurrent_claimants_commit_exactly_one_complete_claim(self):
        self.installed_fixture()
        barrier = threading.Barrier(2)

        def contender(owner):
            store = CoordinatorStore(self.directory)
            try:
                barrier.wait(timeout=5)
                try:
                    self.claim(store, owner=owner)
                except Conflict:
                    return "denied"
                return "charged"
            finally:
                store.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(contender, [OWNER, "d" * 64]))
        self.assertCountEqual(outcomes, ["charged", "denied"])
        self.assertEqual(self.store._storage_capacity(DOMAIN)[1], 2)
        self.assertEqual(len(self.store.connection.execute("SELECT * FROM events").fetchall()), 2)

    def test_live_claim_binds_one_strong_reservation_without_refund(self):
        self.installed_fixture()
        claim = self.claim()
        reservation = object()
        claim.bind_reservation(reservation)
        claim.verify_reservation(reservation)
        with self.assertRaisesRegex(ValueError, "already binds"):
            claim.bind_reservation(object())
        with self.assertRaisesRegex(ValueError, "original retained"):
            claim.verify_reservation(object())
        with self.assertRaisesRegex(ValueError, "cannot be copied"):
            copy.copy(claim)
        detached = claim.record
        detached.owner = "d" * 64
        self.assertEqual(claim.record.owner, OWNER)
        with self.assertRaises(Conflict):
            self.claim()

    def test_failed_binding_still_burns_live_token(self):
        self.installed_fixture()
        claim = self.claim()
        self.store.connection.execute("DELETE FROM events WHERE version=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            claim.bind_reservation(object())
        with self.assertRaisesRegex(ValueError, "already binds"):
            claim.bind_reservation(object())

    def test_matching_denial_data_cannot_reconstruct_original_live_token(self):
        self.installed_fixture()
        claim = self.claim()
        original_reservation = object()
        claim.bind_reservation(original_reservation)
        reconstructed = object.__new__(LiveStorageCapacityClaim)
        reconstructed.__dict__.update(claim.__dict__)
        reconstructed._reservation = None
        # All retained row/hash/path/schema data agree; only live identity differs.
        self.assertEqual(reconstructed.record, claim.record)
        with self.assertRaisesRegex(ValueError, "original minted live token"):
            reconstructed.verify()
        attempted_reservation = object()
        with self.assertRaisesRegex(ValueError, "original minted live token"):
            reconstructed.bind_reservation(attempted_reservation)
        self.assertIs(reconstructed._reservation, attempted_reservation)
        with self.assertRaisesRegex(ValueError, "already binds"):
            reconstructed.bind_reservation(object())
        claim.verify_reservation(original_reservation)
        other = self.open_store()
        with self.assertRaisesRegex(Conflict, "fully charged"):
            self.claim(other)

    def test_incomplete_installation_journal_refuses_before_claim(self):
        self.installed_fixture()
        self.store.connection.execute("DELETE FROM events")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.claim()
        self.assertEqual(self.store.get("storage_capacity", DOMAIN, StorageCapacityDomain)[1], 1)

    def test_missing_retained_event_refuses_live_readback_and_restart(self):
        self.installed_fixture()
        claim = self.claim()
        self.store.connection.execute("DELETE FROM events WHERE version=2")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            claim.verify()
        with self.assertRaisesRegex(ValueError, "ordered events disagree"):
            CoordinatorStore(self.directory)

    def test_reset_or_changed_installation_journal_is_not_a_new_domain(self):
        self.installed_fixture()
        claim = self.claim()
        with self.store.transaction():
            self.store._put(
                "storage_capacity",
                DOMAIN,
                StorageCapacityDomain(id=DOMAIN, installation=INSTALLATION, state="installed"),
                2,
            )
        with self.assertRaisesRegex(ValueError, "unsupported transition"):
            claim.verify()
        with self.assertRaisesRegex(ValueError, "unsupported transition"):
            self.claim()

    def test_installation_mismatch_cannot_claim_another_pool(self):
        self.installed_fixture()
        with self.assertRaisesRegex(ValueError, "installation differs"):
            self.claim(installation="d" * 64)
        self.assertEqual(self.store.get("storage_capacity", DOMAIN, StorageCapacityDomain)[1], 1)

    def test_replaced_journal_denies_live_claim_even_with_copied_valid_records(self):
        self.installed_fixture()
        claim = self.claim()
        replacement = self.directory / "replacement.sqlite3"
        replacement.write_bytes(self.store.path.read_bytes())
        replacement.chmod(0o600)
        replacement.replace(self.store.path)
        with self.assertRaisesRegex(ValueError, "replaced"):
            claim.verify()
        with self.assertRaisesRegex(ValueError, "replaced"):
            self.claim()

    def test_changed_durability_control_denies_live_claim(self):
        self.installed_fixture()
        claim = self.claim()
        self.store.connection.execute("PRAGMA synchronous=OFF")
        with self.assertRaisesRegex(ValueError, "durability controls differ"):
            claim.verify()

    def test_failed_event_commit_returns_no_claim_or_partial_record(self):
        self.installed_fixture()

        def reject_event(action, table, *_):
            return (
                sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_INSERT and table == "events"
                else sqlite3.SQLITE_OK
            )

        self.store.connection.set_authorizer(reject_event)
        with self.assertRaises(sqlite3.DatabaseError):
            self.claim()
        self.store.connection.set_authorizer(None)
        record, version = self.store._storage_capacity(DOMAIN)
        self.assertEqual(version, 1)
        self.assertEqual(record.state, "installed")
        self.assertEqual(len(self.store.connection.execute("SELECT * FROM events").fetchall()), 1)

    def test_claim_data_cannot_change_original_ceilings_or_accept_noninteger_charges(self):
        for field, value in (("tasks", 129), ("logical_bytes", 1), ("tasks", 128.0)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                StorageCapacityDomain.model_validate(
                    {"id": DOMAIN, "installation": INSTALLATION, "state": "installed", field: value}
                )


if __name__ == "__main__":
    unittest.main()
