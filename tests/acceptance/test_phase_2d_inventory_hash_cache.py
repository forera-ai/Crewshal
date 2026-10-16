"""Fresh copied-root files. Readonly mount and UID observations are synthetic."""

from contextlib import contextmanager
import copy
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal import linux_inventory as inventory
from tests.acceptance import test_phase_2d_inventory as fixtures


class Phase2DInventoryHashCache(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Phase2DInventory()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.retain()

    @contextmanager
    def observed_root(self, *, readonly=False):
        real_stat, real_fstat = os.stat, os.fstat

        def owned(info):
            names = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_uid",
                "st_gid",
                "st_nlink",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
            values = {name: getattr(info, name) for name in names}
            values.update(st_uid=0, st_gid=0)
            return SimpleNamespace(**values)

        if readonly:
            self.owner._clean_mount = (str(self.fixture.root), "synthetic-original-mount")
        with (
            patch.object(inventory.os, "fstat", side_effect=lambda fd: owned(real_fstat(fd))),
            patch.object(
                inventory.os,
                "stat",
                side_effect=lambda *args, **kwargs: owned(real_stat(*args, **kwargs)),
            ),
            patch.object(
                inventory.os,
                "fstatvfs",
                return_value=SimpleNamespace(f_flag=os.ST_RDONLY if readonly else 0),
            ),
            patch.object(
                inventory.RetainedParentInventory, "verify_clean_current_mount", autospec=True
            ) as mount,
        ):
            yield mount

    def test_writable_producer_scan_never_populates_the_cache(self):
        real_read = os.read
        with self.observed_root(), patch.object(inventory.os, "read", wraps=real_read) as reads:
            self.owner.verify()
            first = reads.call_count
            self.owner.verify()
            self.assertGreater(reads.call_count, first)
        self.assertIsNone(self.owner._hash_context)
        self.assertEqual(self.owner._verified_hashes, {})
        self.assertNotIn(self.owner, inventory._READONLY_HASHES)

    def test_immutable_second_pass_checks_entries_without_reading_file_bytes(self):
        with self.observed_root(readonly=True) as mount:
            self.owner.verify()
            with patch.object(
                inventory.os, "read", side_effect=AssertionError("cached bytes must not be read")
            ):
                self.owner.verify()
            self.assertEqual(mount.call_count, 4)
        self.assertEqual(len(self.owner._verified_hashes), len(self.fixture.raw))
        with self.assertRaises(TypeError):
            self.owner._verified_hashes["/bin/trusted-parent"] = ((0,), "a" * 64)

    def test_changed_bytes_with_the_same_size_refuse_cached_identity(self):
        with self.observed_root(readonly=True):
            self.owner.verify()
            path = self.fixture.root / "bin/trusted-parent"
            path.chmod(0o755)
            path.write_bytes(b"x" * path.stat().st_size)
            path.chmod(0o555)
            with self.assertRaisesRegex(ValueError, "readonly inventory file changed"):
                self.owner.verify()

    def test_extra_and_missing_files_still_require_complete_enumeration(self):
        with self.observed_root(readonly=True):
            self.owner.verify()
            extra = self.fixture.root / "extra"
            extra.write_bytes(b"extra")
            with self.assertRaisesRegex(ValueError, "contents differ"):
                self.owner.verify()
            extra.unlink()
            (self.fixture.root / "lib/libc.so").unlink()
            with self.assertRaisesRegex(ValueError, "contents differ"):
                self.owner.verify()

    def test_changed_inventory_mount_and_root_fd_refuse_cache_use(self):
        with self.observed_root(readonly=True):
            self.owner.verify()
            original_mount = self.owner._clean_mount
            self.owner._clean_mount = (original_mount[0], "replacement-mount")
            with self.assertRaisesRegex(ValueError, "hash context changed"):
                self.owner.verify()
            self.owner._clean_mount = original_mount
            original_fd = self.owner.descriptor
            duplicate = os.dup(original_fd)
            try:
                self.owner.descriptor = duplicate
                with self.assertRaisesRegex(ValueError, "hash context changed"):
                    self.owner.verify()
            finally:
                self.owner.descriptor = original_fd
                os.close(duplicate)
            self.owner.inventory.root["/bin/trusted-parent"].sha256 = "a" * 64
            with self.assertRaisesRegex(ValueError, "root identity changed"):
                self.owner.verify()

    def test_copied_cache_cannot_supply_registered_original_custody(self):
        with self.observed_root(readonly=True):
            self.owner.verify()
            copied = copy.copy(self.owner)
            with self.assertRaisesRegex(ValueError, "hash context changed"):
                copied.verify()
            self.owner.verify()

    def test_mount_or_file_writability_change_refuses_the_existing_cache(self):
        with self.observed_root(readonly=True):
            self.owner.verify()
            with (
                patch.object(inventory.os, "fstatvfs", return_value=SimpleNamespace(f_flag=0)),
                self.assertRaisesRegex(ValueError, "became writable"),
            ):
                self.owner.verify()
            del self.owner._clean_mount
            with self.assertRaisesRegex(ValueError, "hash context changed"):
                self.owner.verify()


if __name__ == "__main__":
    unittest.main()
