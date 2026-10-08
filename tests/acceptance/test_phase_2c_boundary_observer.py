"""Portable synthetic cgroup observations; no Linux execution or prior artifacts."""

from pathlib import Path
import tempfile
import unittest

from scripts.native_full_boundary_v5 import EXPECTED, sample_controls


class BoundaryObserver(unittest.TestCase):
    def write(self, group, controls, populated):
        for name, value in controls.items():
            (group / name).write_text(value)
        (group / "cgroup.procs").write_text("123\n" if populated else "")
        (group / "cgroup.events").write_text("populated " + str(int(populated)) + "\n")

    def test_empty_setup_defaults_are_recorded_without_qualifying(self):
        with tempfile.TemporaryDirectory() as folder:
            group = Path(folder)
            defaults = {key: "max 100000" if key == "cpu.max" else "max" for key in EXPECTED}
            self.write(group, defaults, False)
            report = {}
            self.assertIsNone(sample_controls(group, report, 0.003))
            self.assertEqual(report["empty_setup_controls"][0]["observed"], defaults)
            self.write(group, EXPECTED, True)
            self.assertEqual(sample_controls(group, report, 0.01), EXPECTED)

    def test_empty_expected_controls_alone_cannot_qualify(self):
        with tempfile.TemporaryDirectory() as folder:
            group = Path(folder)
            self.write(group, EXPECTED, False)
            self.assertIsNone(sample_controls(group, {}, 0.01))

    def test_every_populated_controller_mismatch_still_refuses(self):
        with tempfile.TemporaryDirectory() as folder:
            group = Path(folder)
            for key in EXPECTED:
                altered = {**EXPECTED, key: "max 100000" if key == "cpu.max" else "max"}
                self.write(group, altered, True)
                report = {}
                with self.assertRaisesRegex(RuntimeError, "limits differ"):
                    sample_controls(group, report, 0.01)
                self.assertEqual(report["control_mismatch"]["observed"], altered)

    def test_descendant_population_cannot_hide_behind_empty_root_pid_list(self):
        with tempfile.TemporaryDirectory() as folder:
            group = Path(folder)
            self.write(group, {**EXPECTED, "memory.swap.max": "max"}, True)
            (group / "cgroup.procs").write_text("")
            with self.assertRaisesRegex(RuntimeError, "limits differ"):
                sample_controls(group, {}, 0.01)
