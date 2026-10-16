"""Exercise real mapped-file custody with synthetic kernel task observations."""

import copy
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal import linux_installed as installed
from tests.acceptance import test_phase_2d_inventory as fixtures


class Phase2DInstalled(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.Phase2DInventory()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.root = fixture.retain()
        self.proc = fixture.root / "proc-fixture"
        self.proc.mkdir()
        (self.proc / "map_files").mkdir()
        self.file = fixture.root / "bin" / "trusted-parent"
        (self.proc / "map_files" / "1000-2000").symlink_to(self.file)
        self.task = SimpleNamespace(descriptor=os.open(self.proc, os.O_RDONLY | os.O_DIRECTORY))
        self.addCleanup(os.close, self.task.descriptor)
        self.write_maps()

    def write_maps(self, *, name="/bin/trusted-parent", inode=None, suffix=""):
        info = self.file.stat()
        major, minor = os.major(info.st_dev), os.minor(info.st_dev)
        (self.proc / "maps").write_text(
            f"1000-2000 r-xp 00000000 {major:02x}:{minor:02x} "
            f"{info.st_ino if inode is None else inode} {name}{suffix}\n"
            "3000-4000 r-xp 00000000 00:00 0 [vdso]\n"
        )

    def kernel_seam(self):
        # Kernel task identity, root ownership and readonly mount observations
        # are synthetic. Mapping FD opens, inode equality and hashes are real.
        original, original_stat = os.fstat, os.stat

        def metadata(value):
            return SimpleNamespace(
                **{
                    name: (0 if name in {"st_uid", "st_gid"} else getattr(value, name))
                    for name in dir(value)
                    if name.startswith("st_")
                }
            )

        def observed(fd):
            return metadata(original(fd))

        self.enterContext(
            patch.object(
                installed.os, "stat", side_effect=lambda *a, **k: metadata(original_stat(*a, **k))
            )
        )

        return (
            patch.object(installed.RetainedInstalledImages, "_task"),
            patch.object(installed.os, "fstat", side_effect=observed),
            patch.object(
                installed.os, "fstatvfs", return_value=SimpleNamespace(f_flag=os.ST_RDONLY)
            ),
        )

    def retain(self):
        one, two, three = self.kernel_seam()
        with one, two, three:
            return installed.retain_installed_images(self.task, self.root)

    def close_handles(self, owner):
        for fd in set(owner.handles.values()):
            os.close(fd)

    def test_maps_pin_the_original_inode_and_recheck_real_file_bytes(self):
        owner = self.retain()
        self.addCleanup(self.close_handles, owner)
        self.assertIs(self.task._installed_images, owner)
        self.assertEqual(os.fstat(owner.handles["1000-2000"]).st_ino, self.file.stat().st_ino)
        one, two, three = self.kernel_seam()
        with one, two, three:
            owner.verify()
        with self.assertRaisesRegex(TypeError, "cannot be copied"):
            copy.copy(owner)
        with self.assertRaisesRegex(ValueError, "one-shot"):
            self.retain()
        self.file.chmod(0o755)
        self.file.write_bytes(b"changed mapped file")
        self.file.chmod(0o555)
        one, two, three = self.kernel_seam()
        with one, two, three, self.assertRaisesRegex(ValueError, "bytes or metadata"):
            owner.verify()
        self.assertTrue(owner.failed)
        os.fstat(owner.handles["1000-2000"])

    def test_identical_replacement_bytes_do_not_replace_the_mapped_inode(self):
        alternative = self.fixture.root / "alternative"
        alternative.write_bytes(self.file.read_bytes())
        alternative.chmod(0o555)
        link = self.proc / "map_files" / "1000-2000"
        link.unlink()
        link.symlink_to(alternative)
        with self.assertRaisesRegex(installed.InstalledImageRefusal, "identity") as caught:
            self.retain()
        owner = caught.exception.owner
        self.addCleanup(self.close_handles, owner)
        self.assertIs(self.task._installed_images, owner)
        self.assertTrue(owner.failed)
        self.assertEqual(os.fstat(owner.handles["1000-2000"]).st_ino, alternative.stat().st_ino)

    def test_failure_after_open_keeps_the_original_mapped_descriptor(self):
        self.write_maps(name="/unlisted/library.so")
        with self.assertRaisesRegex(installed.InstalledImageRefusal, "absent") as caught:
            self.retain()
        owner = caught.exception.owner
        self.addCleanup(self.close_handles, owner)
        os.fstat(owner.handles["1000-2000"])
        self.assertIs(self.task._installed_images, owner)

    def test_missing_second_mapping_keeps_the_first_descriptor(self):
        with (self.proc / "maps").open("a") as output:
            info = self.file.stat()
            output.write(
                f"5000-6000 r--p 00000000 {os.major(info.st_dev):02x}:"
                f"{os.minor(info.st_dev):02x} {info.st_ino} /bin/trusted-parent\n"
            )
        with self.assertRaises(installed.InstalledImageRefusal) as caught:
            self.retain()
        owner = caught.exception.owner
        self.addCleanup(self.close_handles, owner)
        self.assertEqual(set(owner.handles), {"1000-2000", "5000-6000"})
        self.assertEqual(len(set(owner.handles.values())), 1)
        os.fstat(owner.handles["1000-2000"])

    def test_many_ranges_retain_one_file_descriptor_and_all_kernel_rows(self):
        info = self.file.stat()
        with (self.proc / "maps").open("a") as output:
            for index in range(140):
                start = 0x5000 + index * 0x2000
                address = f"{start:x}-{start + 0x1000:x}"
                (self.proc / "map_files" / address).symlink_to(self.file)
                output.write(
                    f"{address} r--p 00000000 {os.major(info.st_dev):02x}:"
                    f"{os.minor(info.st_dev):02x} {info.st_ino} /bin/trusted-parent\n"
                )
        owner = self.retain()
        self.addCleanup(self.close_handles, owner)
        self.assertEqual(len(owner.mappings), 141)
        self.assertEqual(len(owner.metadata), 141)
        self.assertEqual(len(set(owner.handles.values())), 1)

    def test_changed_mapping_set_and_unknown_kernel_maps_refuse(self):
        owner = self.retain()
        self.addCleanup(self.close_handles, owner)
        (self.proc / "maps").write_text(
            (self.proc / "maps").read_text().replace("1000-2000", "1000-2100")
        )
        one, two, three = self.kernel_seam()
        with one, two, three, self.assertRaisesRegex(ValueError, "mapping set changed"):
            owner.verify()
        for raw in (
            b"1000-2000 rwxp 00000000 00:00 0\n",
            b"1000-2000 r-xp 00000000 00:00 0 [unknown]\n",
            b"1000-2000 r-xp 00000000 00:00 3 /bin/parent (deleted)\n",
            b"1000-2000 r-xp 00000000 00:00 3 /bin/parent\\012alias\n",
            b"1000-2000 r-xp 00000000 00:00 3 /bin/parent\n"
            b"1800-2800 r-xp 00000000 00:00 3 /bin/parent\n",
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                installed._mappings(raw)

    def test_caller_created_task_refuses_before_mapping_acquisition(self):
        with self.assertRaises(installed.InstalledImageRefusal) as caught:
            # A caller-created task cannot supply concrete task custody.
            installed.retain_installed_images(self.task, self.root)
        self.assertEqual(caught.exception.owner.handles, {})
        with self.assertRaisesRegex(ValueError, "one-shot"):
            installed.retain_installed_images(self.task, self.root)


class KernelMapAddressTests(unittest.TestCase):
    def test_padded_maps_address_resolves_the_actual_map_files_name(self):
        from crewshal.linux_installed import _mappings

        rows = _mappings(b"00400000-00a0e000 r-xp 00000000 103:02 261741 /usr/bin/python3.12\n")
        self.assertEqual(set(rows), {"400000-a0e000"})
        self.assertEqual(rows["400000-a0e000"][2:], (261741, 0, "r-xp"))

    def test_numeric_overlap_still_refuses_after_address_normalization(self):
        from crewshal.linux_installed import _mappings

        with self.assertRaisesRegex(ValueError, "overlap"):
            _mappings(
                b"00400000-00a0e000 r-xp 00000000 103:02 1 /bin/a\n400000-a0e000 r-xp 00000000 103:02 1 /bin/a\n"
            )
