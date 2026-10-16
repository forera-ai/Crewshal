"""Streaming cache hints do not grant memory or storage availability."""

from unittest.mock import Mock, call, patch
import unittest

from crewshal.linux_inventory import _discard_completed_pages


class StreamingFileCacheTests(unittest.TestCase):
    def setUp(self):
        pages = patch("crewshal.linux_inventory.os.sysconf", return_value=4096)
        pages.start()
        self.addCleanup(pages.stop)

    def test_small_source_files_discard_only_after_complete_read(self):
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch("crewshal.linux_inventory.os.posix_fadvise", create=True) as advise,
            patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
            patch("crewshal.linux_inventory.os.close") as close,
        ):
            _discard_completed_pages(14, 65536, 65537)
            advise.assert_not_called()
            _discard_completed_pages(14, 65537, 65537)
        advise.assert_called_once_with(14, 0, 69632, 4)
        close.assert_not_called()

    def test_small_written_files_flush_before_page_aligned_discard(self):
        actions = Mock()
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch("crewshal.linux_inventory.os.fdatasync", actions.sync, create=True),
            patch("crewshal.linux_inventory.os.posix_fadvise", actions.advise, create=True),
            patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
        ):
            for size in (1, 4096, 4_194_304):
                _discard_completed_pages(14, size, size, sync_written=True)
        self.assertEqual(
            actions.mock_calls,
            [
                call.sync(14),
                call.advise(14, 0, 4096, 4),
                call.sync(14),
                call.advise(14, 0, 4096, 4),
                call.sync(14),
                call.advise(14, 0, 4_194_304, 4),
            ],
        )

    def test_small_file_checkpoint_cannot_exceed_original_size(self):
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch("crewshal.linux_inventory.os.posix_fadvise", create=True) as advise,
        ):
            with self.assertRaisesRegex(ValueError, "original file bound"):
                _discard_completed_pages(14, 32, 31)
        advise.assert_not_called()

    def test_final_tail_uses_actual_kernel_page_geometry(self):
        for page in (16384, 65536):
            with (
                self.subTest(page=page),
                patch("crewshal.linux_inventory.sys.platform", "linux"),
                patch("crewshal.linux_inventory.os.sysconf", return_value=page),
                patch("crewshal.linux_inventory.os.posix_fadvise", create=True) as advise,
                patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
            ):
                _discard_completed_pages(14, 65537, 65537)
                advise.assert_called_once_with(14, 0, (65537 + page - 1) // page * page, 4)

    def test_copy_flushes_before_discarding_each_complete_window_and_final_tail(self):
        actions = Mock()
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch("crewshal.linux_inventory.os.fdatasync", actions.sync, create=True),
            patch("crewshal.linux_inventory.os.posix_fadvise", actions.advise, create=True),
            patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
        ):
            _discard_completed_pages(10, 65536, 8_388_609, sync_written=True)
            _discard_completed_pages(10, 4_194_304, 8_388_609, sync_written=True)
            _discard_completed_pages(10, 8_388_608, 8_388_609, sync_written=True)
            _discard_completed_pages(10, 8_388_609, 8_388_609, sync_written=True)
        self.assertEqual(
            actions.mock_calls,
            [
                call.sync(10),
                call.advise(10, 0, 4_194_304, 4),
                call.sync(10),
                call.advise(10, 4_194_304, 4_194_304, 4),
                call.sync(10),
                call.advise(10, 8_388_608, 4096, 4),
            ],
        )

    def test_read_hints_never_sync_or_close_original_handles(self):
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch("crewshal.linux_inventory.os.fdatasync", create=True) as sync,
            patch("crewshal.linux_inventory.os.close") as close,
            patch("crewshal.linux_inventory.os.posix_fadvise", create=True) as advise,
            patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
        ):
            _discard_completed_pages(12, 4_194_304, 9_000_000)
        sync.assert_not_called()
        close.assert_not_called()
        advise.assert_called_once_with(12, 0, 4_194_304, 4)

    def test_kernel_hint_failure_remains_unknown_and_does_not_extend_bounds(self):
        with (
            patch("crewshal.linux_inventory.sys.platform", "linux"),
            patch(
                "crewshal.linux_inventory.os.posix_fadvise",
                side_effect=OSError("unknown"),
                create=True,
            ),
            patch("crewshal.linux_inventory.os.POSIX_FADV_DONTNEED", 4, create=True),
        ):
            with self.assertRaises(OSError):
                _discard_completed_pages(12, 4_194_304, 9_000_000)
            with self.assertRaises(ValueError):
                _discard_completed_pages(12, 10_000_000, 9_000_000)
