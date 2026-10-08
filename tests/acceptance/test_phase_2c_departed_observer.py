"""Fresh portable fixtures for disappearing observation targets; no guest execution."""

import errno
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.native_full_boundary_v6 import departed_observation, observed_text


class DepartedObserver(unittest.TestCase):
    def test_error_preserves_exact_read_object(self):
        path = Path("/synthetic/attr/current")
        with patch.object(Path, "read_text", side_effect=OSError(errno.ENODEV, "gone")):
            with self.assertRaises(OSError) as raised:
                observed_text(path)
        self.assertEqual(raised.exception.filename, str(path))
        self.assertEqual(raised.exception.errno, errno.ENODEV)

    def test_dead_or_removed_process_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            proc = root / "proc"
            process = proc / "123"
            process.mkdir(parents=True)
            error = OSError(errno.ENODEV, "gone", str(process / "attr/current"))
            for state in ("S", "R", "Z", "X", "x"):
                (process / "stat").write_text("123 (name with spaces) " + state + " 0")
                report = {}
                allowed = departed_observation(error, root / "group", report, proc)
                self.assertEqual(allowed, state in ("Z", "X", "x"))
                if allowed:
                    self.assertEqual(
                        report["departed_observer_reads"][0]["verified_state"], "dead-process"
                    )
            (process / "stat").unlink()
            self.assertTrue(departed_observation(error, root / "group", {}, proc))

    def test_empty_group_requires_recursive_population_check(self):
        with tempfile.TemporaryDirectory() as folder:
            group = Path(folder) / "group"
            group.mkdir()
            error = OSError(errno.ENODEV, "gone", str(group / "memory.current"))
            for pids, populated in (("123", 1), ("", 1), ("123", 0), ("", 0)):
                (group / "cgroup.procs").write_text(pids)
                (group / "cgroup.events").write_text(f"populated {populated}\n")
                self.assertEqual(departed_observation(error, group, {}), not pids and not populated)
            (group / "cgroup.events").unlink()
            self.assertFalse(departed_observation(error, group, {}))
            (group / "cgroup.procs").unlink()
            group.rmdir()
            self.assertTrue(departed_observation(error, group, {}))

    def test_unrelated_or_unreadable_targets_never_qualify(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            proc = root / "proc"
            process = proc / "123"
            process.mkdir(parents=True)
            (process / "stat").write_text("123 (process) Z 0")
            for error in (
                OSError(errno.EACCES, "denied", str(process / "attr/current")),
                OSError(errno.ENODEV, "gone"),
                OSError(errno.ENODEV, "gone", str(root / "unrelated")),
                OSError(errno.ENODEV, "gone", str(proc / "self/attr/current")),
            ):
                self.assertFalse(departed_observation(error, root / "group", {}, proc))
            with patch.object(
                Path, "read_text", side_effect=PermissionError(errno.EACCES, "denied")
            ):
                with self.assertRaises(PermissionError):
                    departed_observation(
                        OSError(errno.ENODEV, "gone", str(process / "attr/current")),
                        root / "group",
                        {},
                        proc,
                    )
