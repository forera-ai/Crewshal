"""Offline checks do not establish operational Linux qualification."""

import hashlib
import os
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from crewshal.linux_operational import _canonical_path, _hash_file, _open_path, original_owner_units


class BuildMappingReadbackTests(unittest.TestCase):
    def test_build_readback_uses_numeric_kernel_directory_spelling(self) -> None:
        from crewshal.linux_operational import OriginalInstallationDriver

        driver = object.__new__(OriginalInstallationDriver)
        driver.handles = {}
        raw = b"00400000-00500000 r-xp 00000000 08:01 12 /compiler\n"
        with (
            patch("crewshal.linux_operational._read", return_value=raw),
            patch("crewshal.linux_operational.os.open", return_value=41) as opened,
            patch("crewshal.linux_operational._hash_file") as hashed,
            patch("crewshal.linux_operational.os.fstatvfs") as protection,
        ):
            protection.return_value.f_flag = os.ST_RDONLY
            driver._retain_build_maps("compiler", 17, {"/compiler": "a" * 64}, 29)
        opened.assert_called_once_with(
            "map_files/400000-500000", os.O_RDONLY | os.O_CLOEXEC, dir_fd=17
        )
        hashed.assert_called_once_with(41, "a" * 64, 29)
        self.assertEqual(driver.handles, {"compiler-map:400000-500000": 41})

    def test_build_readback_refuses_overlapping_ranges_before_acquiring_a_file(self) -> None:
        from crewshal.linux_operational import OriginalInstallationDriver

        driver = object.__new__(OriginalInstallationDriver)
        driver.handles = {}
        raw = (
            b"00400000-00500000 r-xp 00000000 08:01 12 /compiler\n"
            b"400000-500000 r-xp 00000000 08:01 12 /compiler\n"
        )
        with (
            patch("crewshal.linux_operational._read", return_value=raw),
            patch("crewshal.linux_operational.os.open") as opened,
        ):
            with self.assertRaisesRegex(ValueError, "overlap"):
                driver._retain_build_maps("compiler", 17, {"/compiler": "a" * 64}, 29)
        opened.assert_not_called()

    def test_build_readback_retains_acquired_fd_after_writable_mapping_refusal(self) -> None:
        from crewshal.linux_operational import OriginalInstallationDriver

        driver = object.__new__(OriginalInstallationDriver)
        driver.handles = {}
        raw = b"00400000-00500000 r-xp 00000000 08:01 12 /compiler\n"
        with (
            patch("crewshal.linux_operational._read", return_value=raw),
            patch("crewshal.linux_operational.os.open", return_value=41),
            patch("crewshal.linux_operational._hash_file"),
            patch("crewshal.linux_operational.os.fstatvfs") as protection,
        ):
            protection.return_value.f_flag = 0
            with self.assertRaisesRegex(ValueError, "writable"):
                driver._retain_build_maps("compiler", 17, {"/compiler": "a" * 64}, 29)
        self.assertEqual(driver.handles, {"compiler-map:400000-500000": 41})


class OperationalInputTests(unittest.TestCase):
    def test_owner_units_apply_original_limits_before_empty_environment_entry(self) -> None:
        units = original_owner_units(
            "/opt/crewshal/phase2d-entry.py", "/opt/crewshal/phase2d-plan.json"
        )
        aggregate = units["crewshal-2d-20261012v1.slice"]
        observer = units["crewshal-2d-20261012v1-observer.service"]
        self.assertIn("MemoryMax=805306368", aggregate)
        self.assertIn("TasksMax=128", aggregate)
        self.assertIn("MemoryMax=134217728", observer)
        self.assertIn("TasksMax=32", observer)
        self.assertNotIn("RuntimeMaxSec=", observer)
        self.assertIn("LimitNOFILE=4096", observer)
        self.assertIn("ProtectSystem=strict", observer)
        self.assertIn("PrivateMounts=yes", observer)
        self.assertIn(
            "ReadWritePaths=/run /sys/fs/cgroup/crewshal.slice/crewshal-2d.slice /sys/kernel/security/apparmor",
            observer,
        )
        self.assertIn("BindPaths=/var/lib/crewshal-phase2d-storage-v1:/run", observer)
        self.assertIn(
            "BindReadOnlyPaths=/var/lib/crewshal-phase2d-input-v1:/run/crewshal-phase2d-input-v1",
            observer,
        )
        self.assertIn("Restart=no", observer)
        self.assertIn("ExecStart=/usr/bin/env -i /usr/bin/python3.12 -I -S -B ", observer)
        with self.assertRaisesRegex(ValueError, "literal systemd"):
            original_owner_units("/opt/crewshal/entry.py;other", "/opt/crewshal/plan.json")

    def test_frozen_paths_refuse_parent_and_noncanonical_routes(self) -> None:
        for path in ("relative/file", "/tmp/../file", "/tmp//file", "/tmp/file\x00other"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                _canonical_path(path)

    def test_hash_reads_original_fd_and_detects_changed_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen"
            path.write_bytes(b"original helper\n")
            descriptor = os.open(path, os.O_RDONLY)
            try:
                sha = hashlib.sha256(path.read_bytes()).hexdigest()
                _hash_file(descriptor, sha, time.monotonic() + 1)
                path.write_bytes(b"changed helper\n")
                with self.assertRaisesRegex(ValueError, "bytes or retained identity"):
                    _hash_file(descriptor, sha, time.monotonic() + 1)
            finally:
                os.close(descriptor)

    def test_hash_refuses_hardlink_and_expired_original_deadline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen"
            path.write_bytes(b"helper")
            descriptor = os.open(path, os.O_RDONLY)
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            try:
                with self.assertRaisesRegex(ValueError, "deadline"):
                    _hash_file(descriptor, sha, time.monotonic() - 1)
                os.link(path, Path(directory) / "alias")
                with self.assertRaisesRegex(ValueError, "single-link"):
                    _hash_file(descriptor, sha, time.monotonic() + 1)
            finally:
                os.close(descriptor)

    def test_hash_refuses_a_file_changed_during_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen"
            original = b"h" * 70000
            path.write_bytes(original)
            descriptor = os.open(path, os.O_RDONLY)
            real_pread = os.pread

            def changed(handle: int, count: int, offset: int) -> bytes:
                chunk = real_pread(handle, count, offset)
                if offset == 0:
                    path.write_bytes(b"x" * len(original))
                return chunk

            try:
                with patch("crewshal.linux_operational.os.pread", side_effect=changed):
                    with self.assertRaisesRegex(ValueError, "bytes or retained identity"):
                        _hash_file(
                            descriptor, hashlib.sha256(original).hexdigest(), time.monotonic() + 1
                        )
            finally:
                os.close(descriptor)

    def test_open_refuses_symlink_parent_before_opening_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "real").mkdir()
            (root / "real" / "file").write_bytes(b"frozen")
            (root / "alias").symlink_to("real", target_is_directory=True)
            # The owner or outside-write check can refuse first on this host.
            with self.assertRaises((OSError, ValueError)):
                _open_path(str(root / "alias" / "file"))


class RetainedRootOpenTests(unittest.TestCase):
    def _owner_metadata(self, descriptor: int) -> SimpleNamespace:
        original = self._real_fstat(descriptor)
        return SimpleNamespace(st_uid=0, st_gid=0, st_mode=original.st_mode)

    def test_open_uses_retained_root_after_its_original_path_disappears(self) -> None:
        self._real_fstat = os.fstat
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "original"
            policy = old / "opt/crewshal/storage-audit/policy.binary"
            policy.parent.mkdir(parents=True)
            policy.write_bytes(b"frozen policy")
            root = os.open(old, os.O_RDONLY | os.O_DIRECTORY)
            old.rename(Path(directory) / "moved")
            try:
                with patch("crewshal.linux_operational.os.fstat", side_effect=self._owner_metadata):
                    descriptor = _open_path(
                        "/opt/crewshal/storage-audit/policy.binary", root_fd=root
                    )
                try:
                    self.assertEqual(os.read(descriptor, 64), b"frozen policy")
                finally:
                    os.close(descriptor)
                self.assertFalse(old.exists())
                self.assertTrue(os.fstat(root))
            finally:
                os.close(root)

    def test_retained_root_walk_refuses_links_and_writable_directories(self) -> None:
        self._real_fstat = os.fstat
        with tempfile.TemporaryDirectory() as directory:
            root_path = Path(directory)
            (root_path / "real").mkdir()
            (root_path / "real/policy").write_bytes(b"policy")
            (root_path / "alias").symlink_to("real", target_is_directory=True)
            root = os.open(root_path, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with patch("crewshal.linux_operational.os.fstat", side_effect=self._owner_metadata):
                    with self.assertRaises(OSError):
                        _open_path("/alias/policy", root_fd=root)
                    (root_path / "real").chmod(0o777)
                    with self.assertRaisesRegex(ValueError, "outside write"):
                        _open_path("/real/policy", root_fd=root)
            finally:
                os.close(root)
