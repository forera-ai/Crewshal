"""Fresh journal and output FDs exercise derivation, without a compiler or Linux installation."""

import hashlib
import os
import pickle
import time
import unittest
from unittest.mock import patch

from crewshal.contracts import BuildDerivationRecord, record_digest
from crewshal.durable import CoordinatorStore
from crewshal.linux_bootstrap import prepare_linux_bootstrap
from crewshal.linux_charged_build import RetainedBuildDerivation, verify_observer_configuration
from crewshal.linux_operational import (
    FrozenHelperBuild,
    FrozenInstallationInputs,
    OriginalInstallationDriver,
    RetainedCompilerStorage,
)
from crewshal.linux_setup import OwnedStorageReservation
from tests.acceptance import test_phase_2d_inventory as inventory_fixtures
from tests.acceptance import test_phase_2d_setup as setup_fixtures


class Phase2DChargedBuild(unittest.TestCase):
    def setUp(self):
        inventory = inventory_fixtures.Phase2DInventory()
        inventory.setUp()
        self.addCleanup(inventory.doCleanups)
        parent = setup_fixtures.Phase2DSetup()
        parent.setUp()
        self.addCleanup(parent.doCleanups)
        self.fixture = inventory
        names = (
            "libc.a",
            "libgcc.a",
            "libgcc_eh.a",
            "crt1.o",
            "crti.o",
            "crtn.o",
            "crtbeginT.o",
            "crtend.o",
            "cc1",
            "collect2",
            "as",
            "ld",
        )
        build = FrozenHelperBuild(
            compiler="/prepared/gcc",
            compiler_sha256="1" * 64,
            source="/prepared/bootstrap_helper.c",
            source_sha256=inventory.policy.helper_source,
            volume="/prepared/compiler",
            loop_device="/dev/loop123",
            backing="/prepared/compiler.img",
            toolchain_files={"/prepared/" + name: "2" * 64 for name in names},
        )
        configuration = inventory.compile(build_recipe_sha256=record_digest(build))
        inputs = self.initial = FrozenInstallationInputs(
            configuration=configuration,
            bootstrap=prepare_linux_bootstrap(
                configuration, helper_binary=inventory.policy.helper_binary
            ),
            inventory=inventory.spec,
            cgroup_parent="owned.slice/session.scope",
            batch_leaf="crewshal-2d-synthetic",
            observer_name="observer",
            journal="/prepared/state",
            installation_parent="/run",
            helper="/prepared/compiler/crewshal-bootstrap",
            formatter="/prepared/mkfs.ext4",
            formatter_sha256="3" * 64,
            sources={
                name: "/prepared/compiler/crewshal-bootstrap"
                if name == "/bin/crewshal-bootstrap"
                else "/prepared" + name
                for name in inventory.raw
            },
            helper_build=build,
            apparmor_namespace="/sys/kernel/security/apparmor/policy",
            apparmor_roles=tuple(
                (name, "synthetic-" + name) for name in ("native", "tool", "validator", "parent")
            ),
        )
        driver = self.driver = object.__new__(OriginalInstallationDriver)
        driver.inputs = inputs
        driver.handles = {}
        driver.origin = time.monotonic() - 1
        driver._origin = driver.origin
        driver._compiler_attempted = False
        driver.observer = parent.parent
        driver.observer.spec = driver.observer.spec.model_copy(
            update={"configuration": record_digest(configuration)}
        )
        driver._charged_build_input_payload = inputs.model_dump_json()
        driver.store = CoordinatorStore(inventory.root / "charged-state")
        self.addCleanup(driver.store.close)
        claim = driver.store.charge_storage_installation(
            "4" * 64,
            owner=record_digest(driver.observer.spec),
            configuration=record_digest(configuration),
            batch_started_monotonic=driver.origin,
        )
        reservation = driver.reservation = object.__new__(OwnedStorageReservation)
        reservation.observer = driver.observer
        reservation._capacity_claim = claim
        reservation._configuration = configuration
        reservation._configuration_digest = record_digest(configuration)
        claim.bind_reservation(reservation)
        driver.observer._storage_reservation = reservation
        compiler = driver.compiler_storage = object.__new__(RetainedCompilerStorage)
        compiler.reservation = reservation
        path = inventory.root / "new-helper"
        path.write_bytes(b"independently read compiled helper bytes")
        path.chmod(0o555)
        output = os.open(path, os.O_RDONLY)
        self.addCleanup(os.close, output)
        driver.handles["compiled-helper-output"] = output
        self.compiler_readback = patch.object(RetainedCompilerStorage, "verify")
        self.compiler_readback.start()
        self.addCleanup(self.compiler_readback.stop)
        self.actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        with patch("crewshal.linux_operational._open_path", return_value=output):
            driver._bind_compiled_helper()

    def bind(self):
        return RetainedBuildDerivation.bind(self.driver, self.initial)

    def test_actual_output_derives_only_helper_identities_under_original_full_charge(self):
        claim = self.driver.reservation.capacity_claim
        original = claim.record.model_dump_json()
        observer = self.driver.observer
        receipt = self.bind()
        receipt.verify()
        verify_observer_configuration(observer, self.driver.inputs.configuration)
        self.assertEqual(claim.record.model_dump_json(), original)
        self.assertEqual(claim.record.logical_bytes, 8589934592)
        self.assertEqual(claim.record.allocated_bytes, 8589934592)
        self.assertEqual(receipt.record.helper_binary, self.actual_hash)
        self.assertEqual(observer.spec.configuration, record_digest(self.initial.configuration))
        recorded, version = self.driver.store.get(
            "bootstrap_build", receipt.record.id, BuildDerivationRecord
        )
        self.assertEqual(recorded, receipt.record)
        self.assertEqual(version, 1)
        self.assertIs(receipt.output, self.driver.handles["compiled-helper-output"])

    def test_repeated_derivation_and_export_refuse_without_replacing_original(self):
        receipt = self.bind()
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()
        with self.assertRaises(TypeError):
            pickle.dumps(receipt)
        with self.assertRaises(ValueError):
            RetainedBuildDerivation()
        self.assertIs(self.driver.reservation._build_derivation, receipt)

    def test_nonderived_dispatch_change_refuses_and_retains_failed_receipt(self):
        self.driver.inputs.configuration.native_environment["FORGED"] = "changed"
        with self.assertRaisesRegex(ValueError, "nonderived dispatch"):
            self.bind()
        receipt = self.driver.reservation._build_derivation
        self.assertTrue(receipt.failed)
        os.fstat(receipt.output)
        self.assertEqual(self.driver.reservation.capacity_claim.record.logical_bytes, 8589934592)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()

    def test_nonderived_bootstrap_change_cannot_hide_behind_configuration_digest(self):
        self.driver.inputs.bootstrap.configuration = "5" * 64
        with self.assertRaisesRegex(ValueError, "nonderived bootstrap"):
            self.bind()
        self.assertTrue(self.driver.reservation._build_derivation.failed)

    def test_changed_original_output_refuses_without_a_new_derivation(self):
        receipt = self.bind()
        path = self.fixture.root / "new-helper"
        path.chmod(0o755)
        path.write_bytes(b"replaced compiler bytes")
        with self.assertRaisesRegex(ValueError, "bytes or retained identity"):
            receipt.verify()
        self.assertTrue(receipt.failed)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.bind()

    def test_journal_receipt_deletion_cannot_recreate_live_authority(self):
        receipt = self.bind()
        self.driver.store.connection.execute(
            "DELETE FROM records WHERE id=?", ("bootstrap_build:" + receipt.record.id,)
        )
        with self.assertRaisesRegex(ValueError, "journal receipt"):
            verify_observer_configuration(self.driver.observer, self.driver.inputs.configuration)
        self.assertTrue(receipt.failed)

    def test_final_configuration_requires_original_registered_derivation(self):
        with self.assertRaisesRegex(ValueError, "retained build derivation"):
            verify_observer_configuration(self.driver.observer, self.driver.inputs.configuration)
        receipt = self.bind()
        self.driver.reservation._build_derivation = object()
        with self.assertRaisesRegex(ValueError, "custody changed"):
            verify_observer_configuration(self.driver.observer, self.driver.inputs.configuration)
        self.assertTrue(receipt.failed)

    def test_compiler_refuses_before_opening_an_input_without_original_charge(self):
        self.driver.reservation = None
        with patch("crewshal.linux_operational._open_path") as acquire:
            with self.assertRaisesRegex(ValueError, "original full charge"):
                self.driver._compile_helper(self.initial.helper_build, object())
            acquire.assert_not_called()
            with self.assertRaisesRegex(ValueError, "consumed"):
                self.driver._compile_helper(self.initial.helper_build, object())
            acquire.assert_not_called()
