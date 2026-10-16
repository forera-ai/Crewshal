"""Read real files with synthetic AppArmor and seal observations. No policy loads."""

from dataclasses import replace
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crewshal.admission import NamespaceIdentity
from crewshal.linux_payload_storage import PROFILE_NAMES, RetainedAppArmorExport
from crewshal import linux_setup as setup
from crewshal.model import digest
from tests.acceptance import test_phase_2d_setup as fixtures


class Phase2DPolicyTransport(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Phase2DSetup()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.raw = b"synthetic compiled policy"
        (self.root / "policy").write_bytes(self.raw)
        self.namespace = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.capsule = os.open(self.root / "policy", os.O_RDONLY)
        self.addCleanup(os.close, self.namespace)
        self.addCleanup(os.close, self.capsule)
        info = os.fstat(self.namespace)
        plan = self.fixture.plan.model_copy(update={"policy_control": True})
        self.controls = setup.InheritedControls(
            configuration=self.fixture.configuration,
            bootstrap=self.fixture.preparation,
            setup=plan,
            boot_id=self.fixture.parent.spec.boot_id,
            outer_namespaces=self.fixture.parent.spec.namespaces,
            groups={},
            apparmor_namespace=NamespaceIdentity(device=info.st_dev, inode=info.st_ino),
            compiled_policy_sha256=digest(self.raw),
            apparmor_roles=[
                (name, "profile" + str(index), NamespaceIdentity(device=1, inode=index + 1))
                for index, name in enumerate(PROFILE_NAMES)
            ],
        )
        self.policy = RetainedAppArmorExport(
            self.namespace,
            (info.st_dev, info.st_ino),
            1,
            self.raw,
            tuple(
                (name, "profile" + str(index), (1, index + 1))
                for index, name in enumerate(PROFILE_NAMES)
            ),
            self.capsule,
            (os.fstat(self.capsule).st_dev, os.fstat(self.capsule).st_ino),
        )
        self.addCleanup(self.cleanup_retained)

    def cleanup_retained(self):
        value = setup._NAMESPACE_POLICIES.pop(id(self.controls), None)
        if value:
            for descriptor in value[1]:
                os.close(descriptor)

    def patches(self):
        actual_dup, actual_close, actual_fstat = os.dup, os.close, os.fstat

        def duplicate(number):
            return actual_dup(
                self.namespace if number == 10 else self.export if number == 13 else self.capsule
            )

        def close(number):
            if number not in (10, 11, 13):
                actual_close(number)

        def fstat(number):
            value = actual_fstat(number)
            return os.stat_result(
                (
                    value.st_mode,
                    value.st_ino,
                    value.st_dev,
                    value.st_nlink,
                    0,
                    0,
                    value.st_size,
                    value.st_atime,
                    value.st_mtime,
                    value.st_ctime,
                )
            )

        return (
            patch.object(setup.os, "dup", side_effect=duplicate),
            patch.object(setup.os, "close", side_effect=close),
            patch.object(setup.os, "fstat", side_effect=fstat),
            patch.object(setup, "_seals", return_value=(100, 101, 15)),
            patch.object(
                setup.fcntl,
                "fcntl",
                side_effect=lambda fd, operation: 15 if operation == 101 else os.O_RDONLY,
            ),
            patch.object(RetainedAppArmorExport, "retain", return_value=self.policy),
            patch.object(RetainedAppArmorExport, "retain_inherited", return_value=self.policy),
        )

    def receive(self):
        a, b, c, d, e, f, g = self.patches()
        with a, b, c, d, e, f, g:
            return setup.receive_namespace_policy(self.controls)

    def export_controls(self):
        (self.root / "export").write_bytes(self.raw)
        self.export = os.open(self.root / "export", os.O_RDONLY)
        self.addCleanup(os.close, self.export)
        info = os.fstat(self.export)
        self.controls = self.controls.model_copy(
            update={
                "setup": self.controls.setup.model_copy(update={"network_control": True}),
                "apparmor_export": NamespaceIdentity(device=info.st_dev, inode=info.st_ino),
            }
        )
        self.policy = replace(
            self.policy, raw_export=self.export, raw_export_identity=(info.st_dev, info.st_ino)
        )

    def test_original_raw_export_fd13_reaches_retained_policy_without_reopening(self):
        self.export_controls()
        a, b, c, d, e, f, g = self.patches()
        with a, b, c, d, e, f as reopen, g as inherited:
            self.assertIs(setup.receive_namespace_policy(self.controls), self.policy)
        reopen.assert_not_called()
        inherited.assert_called_once()
        _, handles, _ = setup._NAMESPACE_POLICIES[id(self.controls)]
        self.assertEqual(len(handles), 3)
        self.assertEqual(inherited.call_args.args[3], handles[2])
        self.assertEqual(os.pread(handles[2], len(self.raw), 0), self.raw)

    def test_changed_raw_export_inode_refuses_and_keeps_all_original_inputs(self):
        self.export_controls()
        self.controls = self.controls.model_copy(
            update={
                "apparmor_export": NamespaceIdentity(device=1, inode=2),
            }
        )
        with self.assertRaisesRegex(ValueError, "export identity"):
            self.receive()
        _, handles, policy = setup._NAMESPACE_POLICIES[id(self.controls)]
        self.assertIsNone(policy)
        self.assertEqual(len(handles), 3)
        for descriptor in handles:
            os.fstat(descriptor)

    def test_exact_policy_inputs_keep_original_namespace_and_two_retained_fds(self):
        self.assertIs(self.receive(), self.policy)
        original, handles, policy = setup._NAMESPACE_POLICIES[id(self.controls)]
        self.assertIs(original, self.controls)
        self.assertIs(policy, self.policy)
        self.assertEqual(len(handles), 2)
        self.assertEqual(os.pread(handles[1], len(self.raw), 0), self.raw)

    def test_mutated_compiled_bytes_refuse_and_keep_both_handles(self):
        (self.root / "policy").write_bytes(b"changed compiled policy")
        with self.assertRaisesRegex(ValueError, "compiled policy"):
            self.receive()
        _, handles, policy = setup._NAMESPACE_POLICIES[id(self.controls)]
        self.assertIsNone(policy)
        self.assertEqual(len(handles), 2)
        for descriptor in handles:
            os.fstat(descriptor)

    def test_actual_profile_directory_identity_cannot_be_replaced_by_label(self):
        self.policy = replace(
            self.policy,
            roles=tuple((name, directory, (1, 99)) for name, directory, _ in self.policy.roles),
        )
        with self.assertRaisesRegex(ValueError, "directory identity"):
            self.receive()

    def test_refusal_consumes_original_inputs_and_does_not_reopen(self):
        (self.root / "policy").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.receive()
        with patch.object(setup.os, "dup") as duplicate:
            with self.assertRaisesRegex(ValueError, "consumed"):
                setup.receive_namespace_policy(self.controls)
            duplicate.assert_not_called()
