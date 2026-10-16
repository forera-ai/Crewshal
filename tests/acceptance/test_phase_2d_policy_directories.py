"""Kernel directory counters cannot serve as frozen profile identities."""

import hashlib
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal.linux_operational import OriginalInstallationDriver
from crewshal.linux_payload_storage import PROFILE_NAMES


class InstalledPolicyDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "profiles").mkdir()
        (self.root / "revision").write_bytes(b"12\n")
        for index, name in enumerate(PROFILE_NAMES):
            directory = self.root / "profiles" / (name + "." + str(800 + index))
            directory.mkdir()
            (directory / "name").write_text(name + "\n")
        self.owner = object.__new__(OriginalInstallationDriver)
        self.owner.origin = time.monotonic()
        self.owner.inputs = SimpleNamespace(apparmor_roles=tuple((n, n) for n in PROFILE_NAMES))
        self.owner.handles = {"apparmor-namespace": os.open(self.root, os.O_RDONLY)}
        self.addCleanup(self.close_handles)
        check = patch("crewshal.linux_payload_storage._require_apparmorfs")
        check.start()
        self.addCleanup(check.stop)

    def close_handles(self):
        for fd in set(self.owner.handles.values()):
            os.close(fd)

    def test_actual_names_and_original_fds_bind_unpredicted_kernel_counters(self):
        roles = self.owner._retain_installed_policy_roles()
        self.assertEqual(
            roles, tuple((name, name + "." + str(800 + i)) for i, name in enumerate(PROFILE_NAMES))
        )
        for _, directory in roles:
            retained = os.fstat(self.owner.handles["installed-policy-directory:" + directory])
            current = (self.root / "profiles" / directory).stat()
            self.assertEqual((retained.st_dev, retained.st_ino), (current.st_dev, current.st_ino))
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.owner._retain_installed_policy_roles()

    def test_duplicate_actual_name_refuses_and_retains_partial_fds(self):
        directory = self.root / "profiles" / (PROFILE_NAMES[0] + ".9999")
        directory.mkdir()
        (directory / "name").write_text(PROFILE_NAMES[0])
        with self.assertRaisesRegex(ValueError, "unique directory"):
            self.owner._retain_installed_policy_roles()
        self.assertGreater(len(self.owner.handles), 2)
        with self.assertRaisesRegex(ValueError, "consumed"):
            self.owner._retain_installed_policy_roles()

    def test_missing_actual_role_and_changed_explicit_directory_refuse(self):
        self.owner.inputs.apparmor_roles = tuple((name, "different.123") for name in PROFILE_NAMES)
        with self.assertRaisesRegex(ValueError, "directory differs"):
            self.owner._retain_installed_policy_roles()

    def event_reads(self):
        original = os.read
        revision = (self.root / "revision").stat()

        def read(descriptor, length):
            part = original(descriptor, length)
            current = os.fstat(descriptor)
            if not part and (current.st_dev, current.st_ino) == (revision.st_dev, revision.st_ino):
                raise BlockingIOError(11, "no later policy revision")
            return part

        return patch("os.read", side_effect=read)

    def test_role_discovery_reads_current_revision_without_waiting_for_another(self):
        with self.event_reads():
            roles = self.owner._retain_installed_policy_roles()
        self.assertEqual({name for name, directory in roles}, set(PROFILE_NAMES))

    def test_policy_load_reads_current_revision_without_waiting_for_another(self):
        for directory in (self.root / "profiles").iterdir():
            (directory / "name").unlink()
            directory.rmdir()
        data = b"frozen synthetic policy"
        policy = self.root / "policy.binary"
        policy.write_bytes(data)
        self.owner.handles["installed-compiled-policy"] = os.open(policy, os.O_RDONLY)
        result, output = os.pipe()
        self.addCleanup(os.close, result)
        self.owner.handles["apparmor-load"] = output
        self.owner.inputs.helper_build = SimpleNamespace(policy_build=object())
        self.owner.derived_storage_audit = SimpleNamespace(
            policy_binary_sha256=hashlib.sha256(data).hexdigest()
        )
        with self.event_reads():
            self.assertEqual(self.owner._load_frozen_policy_child(), b"loaded-frozen-absent-policy")
        self.assertEqual(os.read(result, len(data)), data)
