"""Fresh synthetic storage diagnostic checks; no Linux/SBX qualification claim."""

import errno
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.probe_storage_operations import MAX_BYTES, probe
from scripts.assess_storage_budget import CEILING, assess


class Phase2CStorage(unittest.TestCase):
    def budget(self, objects: list) -> dict:
        return {
            "schema_version": 1,
            "ceiling": {"logical_bytes": CEILING, "allocated_bytes": CEILING},
            "objects": objects,
            "execution_allowed": False,
            "native_start_allowed": False,
        }

    def test_backing_and_mounted_views_are_charged_separately(self) -> None:
        # Two 4 GiB views already fill 8 GiB; historical preparation makes it overflow.
        result = assess(
            self.budget(
                [
                    {"id": "upper", "logical_bytes": 4294967296, "allocated_bytes": 0},
                    {"id": "lower", "logical_bytes": 4294967296, "allocated_bytes": 0},
                    {
                        "id": "preparation",
                        "logical_bytes": 2053107620,
                        "allocated_bytes": 2053181440,
                    },
                ]
            )
        )
        self.assertEqual(result["status"], "arithmetic_refused")
        self.assertEqual(result["totals"]["logical_bytes"], 10643042212)
        self.assertIn("logical_bytes: exceeds original ceiling by 2053107620", result["reasons"])

    def test_allocated_and_logical_ceilings_are_independent(self) -> None:
        for dimension in ("logical_bytes", "allocated_bytes"):
            item = {"id": "disk", "logical_bytes": 0, "allocated_bytes": 0}
            item[dimension] = CEILING + 1
            result = assess(self.budget([item]))
            self.assertEqual(result["reasons"], [f"{dimension}: exceeds original ceiling by 1"])

    def test_unknown_allocation_is_not_zero_or_admission(self) -> None:
        result = assess(
            self.budget(
                [
                    {"id": "disk", "logical_bytes": 1, "allocated_bytes": None},
                ]
            )
        )
        self.assertEqual(result["status"], "arithmetic_refused")
        self.assertEqual(result["reasons"], ["disk: unresolved allocated_bytes"])

    def test_invalid_bytes_duplicate_ids_and_permission_flags_refuse(self) -> None:
        for amount in (True, -1, "1"):
            with self.assertRaises(ValueError):
                assess(self.budget([{"id": "disk", "logical_bytes": amount, "allocated_bytes": 0}]))
        item = {"id": "same", "logical_bytes": 1, "allocated_bytes": 1}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            assess(self.budget([item, item]))
        plan = self.budget([item])
        plan["execution_allowed"] = True
        with self.assertRaises(ValueError):
            assess(plan)

    def test_budget_at_exact_boundary_still_cannot_qualify(self) -> None:
        result = assess(
            self.budget(
                [
                    {"id": "all", "logical_bytes": CEILING, "allocated_bytes": CEILING},
                ]
            )
        )
        self.assertEqual(result["status"], "arithmetic_within_ceiling_only")
        self.assertFalse(result["execution_allowed"])
        self.assertIn("unproved", result["qualification_status"])

    def test_budget_cli_reports_refusal_and_rejects_oversized_input(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            plan_path = Path(root) / "plan.json"
            plan_path.write_text(
                json.dumps(
                    self.budget(
                        [
                            {"id": "too-big", "logical_bytes": CEILING + 1, "allocated_bytes": 0},
                        ]
                    )
                )
            )
            command = [sys.executable, "-m", "scripts.assess_storage_budget", str(plan_path)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "arithmetic_refused")
            plan_path.write_bytes(b" " * 65537)
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertIn("exceeds 65536 bytes", result.stderr)

    def test_growth_operations_record_real_size_and_data_without_qualification(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            for case in ("truncate", "seek-write", "pwrite", "mmap"):
                directory = Path(root) / case
                record = probe(directory, case, 1048576)
                self.assertEqual(record["status"], "operation_completed")
                self.assertEqual(record["files"]["target"]["logical_bytes"], 1048576)
                self.assertEqual((directory / "target").stat().st_size, 1048576)
                if case != "truncate":
                    with (directory / "target").open("rb") as source:
                        source.seek(1048575)
                        self.assertEqual(source.read(1), b"Z")
                self.assertFalse(record["execution_allowed"])
                self.assertFalse(record["native_start_allowed"])

    def test_deleted_open_charge_survives_directory_disappearance(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            record = probe(Path(root) / "deleted", "deleted-open", 65536)
            self.assertEqual(record["status"], "operation_completed")
            self.assertTrue(record["directory_entry_absent_while_open"])
            self.assertEqual(record["unlinked_open_file"]["logical_bytes"], 65536)
            self.assertEqual(record["unlinked_open_file"]["links"], 0)
            self.assertEqual(record["remaining_entries"], [])

    def test_hardlink_alias_does_not_become_second_storage_object(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            record = probe(Path(root) / "linked", "hardlink", 65536)
            self.assertEqual(record["status"], "operation_completed")
            self.assertTrue(record["alias_same_inode"])
            self.assertEqual(record["files"]["target"]["links"], 2)

    def test_existing_directory_or_symlink_refuses_without_touching_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / "existing"
            directory.mkdir()
            sentinel = directory / "sentinel"
            sentinel.write_bytes(b"preserve")
            alias = Path(root) / "alias"
            alias.symlink_to(directory)
            for target in (directory, alias):
                with self.assertRaises(FileExistsError):
                    probe(target, "truncate", 65536)
            self.assertEqual(sentinel.read_bytes(), b"preserve")
            self.assertEqual(sorted(path.name for path in directory.iterdir()), ["sentinel"])

    def test_invalid_case_and_size_refuse_before_directory_creation(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / "never"
            for case, size in (
                ("exec", 1),
                ("truncate", True),
                ("truncate", 0),
                ("truncate", MAX_BYTES + 1),
            ):
                with self.assertRaises(ValueError):
                    probe(directory, case, size)
                self.assertFalse(directory.exists())
            for hold in (True, -1, 3):
                with self.assertRaises(ValueError):
                    probe(directory, "truncate", 1, hold)
                self.assertFalse(directory.exists())

    def test_optional_operations_preserve_unavailable_or_real_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            for case in ("preallocate", "copy-range", "reflink", "hole-punch", "metadata"):
                record = probe(Path(root) / case, case, 65536)
                self.assertIn(record["status"], ("operation_completed", "operation_error"))
                if record["status"] == "operation_error":
                    self.assertIsInstance(record["errno"], int)
                    self.assertIn(record["errno"], errno.errorcode)
                else:
                    if case in ("copy-range", "reflink"):
                        self.assertTrue(record["last_byte_matches"])
                    if case == "metadata":
                        self.assertTrue(record["xattr_matches"])
                self.assertFalse(record["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
