"""Fresh refusal fixtures for independent diagnostics; no historical artifacts."""

import tempfile
from pathlib import Path
import unittest

from crewshal.qualification import MANDATORY_CASES, QualificationIdentity
from scripts.readback_native_full_v1 import check_run, load


class NativeReadback(unittest.TestCase):
    def identity(self):
        return QualificationIdentity(
            host_os="synthetic-linux",
            host_kernel="synthetic-kernel",
            architecture="synthetic",
            substrate="synthetic",
            substrate_version="synthetic",
            image="1" * 64,
            runtime="synthetic",
            toolchain="2" * 64,
            configuration="3" * 64,
            grant="4" * 64,
            harness="5" * 64,
            manifest="6" * 64,
            credential_design="7" * 64,
        )

    def test_claimed_native_success_without_raw_evidence_stays_incomplete(self):
        result = check_run(
            {"fixture": 1, "native_boundary_stages_passed": True}, self.identity(), True
        )
        self.assertEqual([x["id"] for x in result["cases"]], list(MANDATORY_CASES))
        self.assertEqual(sum(x["status"] == "passed" for x in result["cases"]), 1)
        self.assertTrue(result["issues"])
        self.assertFalse(result["runtime_verified"])
        self.assertFalse(result["execution_allowed"])

    def test_failure_and_forged_authority_cannot_be_promoted(self):
        for changes in (
            {"errors": [{"type": "timeout"}]},
            {"execution_allowed": True},
            {"native_start_allowed": True},
        ):
            record = {
                "fixture": 1,
                "errors": [],
                "execution_allowed": False,
                "native_start_allowed": False,
                **changes,
            }
            result = check_run(record, self.identity(), True)
            self.assertEqual(sum(x["status"] == "passed" for x in result["cases"]), 1)
            self.assertTrue(result["issues"])

    def test_unknown_cleanup_cannot_be_promoted(self):
        record = {
            "fixture": 1,
            "errors": [],
            "execution_allowed": False,
            "native_start_allowed": False,
            "cleanup": {"loop_detached": True},
        }
        result = check_run(record, self.identity(), True)
        self.assertTrue(result["issues"])
        self.assertTrue(
            all(
                x["status"] == "unavailable"
                for x in result["cases"]
                if x["id"] != "qualification-refusal"
            )
        )

    def test_ambiguous_and_nonfinite_json_refuse(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            for raw in (
                '{"fixture":1,"fixture":2}',
                '{"seconds":NaN}',
                '{"seconds":Infinity}',
                '{"seconds":-1e999}',
            ):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    load(path)


if __name__ == "__main__":
    unittest.main()
