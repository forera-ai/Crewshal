"""Fresh portable record fixtures; no Linux, VMware or native runtime execution."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from pydantic import ValidationError

from crewshal.qualification import MANDATORY_CASES
from crewshal.qualification_bundle import (
    MAX_FILE_BYTES,
    BoundArtifact,
    audit_bundle,
)


class Phase2CBundle(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        protocol_bytes = (
            Path(__file__).resolve().parents[2] / "docs/qualification/phase-2c-v1.json"
        ).read_bytes()
        self.protocol = json.loads(protocol_bytes)
        protocol = self.save("protocol.json", protocol_bytes)
        sources = {}
        for field in ("source", "fixture_source", "payload_source", "policy"):
            sources[field] = self.save(field + ".txt", ("synthetic " + field).encode())
        self.profile = {
            "original_protocol_sha256": protocol["sha256"],
            "original_grant": self.protocol["grant"],
            "original_limits": self.protocol["limits"],
            "mandatory_cases": self.protocol["mandatory_cases"],
            "execution_allowed": False,
            "native_start_allowed": False,
            "additional_sources": {},
        }
        for field, artifact in sources.items():
            self.profile[field] = artifact["path"]
            self.profile[field + "_sha256"] = artifact["sha256"]
        profile = self.save_json("profile.json", self.profile)
        self.identity = {
            "host_os": "synthetic-platform",
            "host_kernel": "synthetic-kernel",
            "architecture": "synthetic-architecture",
            "substrate": "synthetic-isolation",
            "substrate_version": "synthetic-version",
            "image": "1" * 64,
            "runtime": "synthetic-native",
            "toolchain": "2" * 64,
            "configuration": profile["sha256"],
            "grant": "3" * 64,
            "harness": "4" * 64,
            "manifest": protocol["sha256"],
            "credential_design": "5" * 64,
        }
        self.records = [
            {
                "schema_version": 1,
                "id": "fresh-" + str(number),
                "identity": self.identity.copy(),
                "results": [
                    {"case": case, "status": "passed", "observation": "synthetic only"}
                    for case in MANDATORY_CASES
                ],
                "execution_allowed": False,
            }
            for number in (1, 2)
        ]
        self.bundle = {
            "schema_version": 1,
            "protocol": protocol,
            "profile": profile,
            "current_identity": self.identity,
            "runs": [
                self.save_json("run-" + str(index) + ".json", record)
                for index, record in enumerate(self.records)
            ],
            "artifacts": list(sources.values()),
            "execution_allowed": False,
        }

    def save(self, name: str, data: bytes) -> dict[str, str]:
        (self.root / name).write_bytes(data)
        return {"path": name, "sha256": hashlib.sha256(data).hexdigest()}

    def save_json(self, name: str, value: object) -> dict[str, str]:
        return self.save(name, json.dumps(value, sort_keys=True).encode())

    def audit(self):
        self.save_json("bundle.json", self.bundle)
        before = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        result = audit_bundle(self.root)
        self.assertEqual(
            before, {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        )
        self.assertFalse(result.runtime_verified)
        self.assertFalse(result.execution_allowed)
        return result

    def replace_record(self, index: int) -> None:
        self.bundle["runs"][index] = self.save_json(
            "run-" + str(index) + ".json", self.records[index]
        )

    def replace_profile(self) -> None:
        profile = self.save_json(self.bundle["profile"]["path"], self.profile)
        self.bundle["profile"] = profile
        self.identity["configuration"] = profile["sha256"]
        for index, record in enumerate(self.records):
            record["identity"] = self.identity.copy()
            self.replace_record(index)

    def test_complete_records_are_only_consistent_and_files_stay_unchanged(self) -> None:
        result = self.audit()
        self.assertEqual(result.status, "consistent_records")
        self.assertEqual(result.run_ids, ["fresh-1", "fresh-2"])

    def test_platform_identity_is_data_not_a_request_for_platform_tests(self) -> None:
        for platform in ("Darwin", "Linux", "Windows"):
            with self.subTest(platform=platform):
                self.identity["host_os"] = platform
                for index, record in enumerate(self.records):
                    record["identity"] = self.identity.copy()
                    self.replace_record(index)
                self.assertEqual(self.audit().status, "consistent_records")

    def test_complementary_historical_subsets_cannot_combine_into_completion(self) -> None:
        complete = self.records[0]["results"]
        self.records[0]["results"] = complete[:10]
        self.records[1]["results"] = complete[10:]
        self.replace_record(0)
        self.replace_record(1)
        self.assertEqual(self.audit().status, "denied")

    def test_changed_profile_in_either_run_denies(self) -> None:
        self.records[1]["identity"]["configuration"] = "6" * 64
        self.replace_record(1)
        self.assertEqual(self.audit().status, "denied")

    def test_each_failure_unavailability_and_omission_in_second_run_denies(self) -> None:
        results = self.records[1]["results"]
        for index, case in enumerate(MANDATORY_CASES):
            for status in ("failed", "unavailable", "missing"):
                with self.subTest(case=case, status=status):
                    self.records[1]["results"] = [item.copy() for item in results]
                    if status == "missing":
                        del self.records[1]["results"][index]
                    else:
                        self.records[1]["results"][index]["status"] = status
                    self.replace_record(1)
                    self.assertEqual(self.audit().status, "denied")

    def test_duplicate_run_bytes_and_duplicate_ids_deny(self) -> None:
        self.bundle["runs"][1] = self.save("another.json", (self.root / "run-0.json").read_bytes())
        self.assertEqual(self.audit().status, "denied")
        self.records[1]["id"] = self.records[0]["id"]
        self.replace_record(1)
        self.assertEqual(self.audit().status, "denied")

    def test_unbound_or_mutated_source_denies(self) -> None:
        self.bundle["artifacts"] = self.bundle["artifacts"][1:]
        self.assertEqual(self.audit().status, "denied")
        self.bundle["artifacts"].append(self.save("source.txt", b"substituted source"))
        self.assertEqual(self.audit().status, "denied")

    def test_altered_original_grant_limits_case_text_or_flags_deny(self) -> None:
        for field, value in (
            ("original_grant", {}),
            ("original_limits", {"memory_bytes": 268435456}),
            ("mandatory_cases", []),
            ("execution_allowed", True),
            ("native_start_allowed", True),
        ):
            original = self.profile[field]
            with self.subTest(field=field):
                self.profile[field] = value
                self.replace_profile()
                self.assertEqual(self.audit().status, "denied")
            self.profile[field] = original

    def test_forged_execution_boolean_version_and_extra_fields_deny(self) -> None:
        for field, value in (
            ("execution_allowed", True),
            ("execution_allowed", 0),
            ("schema_version", True),
            ("schema_version", 2),
            ("extra_authority", "run"),
        ):
            original = self.bundle.copy()
            with self.subTest(field=field, value=value):
                self.bundle[field] = value
                self.assertEqual(self.audit().status, "denied")
            self.bundle = original

    def test_missing_record_and_oversized_file_deny(self) -> None:
        (self.root / "run-1.json").unlink()
        self.assertEqual(self.audit().status, "denied")
        self.bundle["runs"][1] = self.save("run-1.json", b"x" * (MAX_FILE_BYTES + 1))
        self.assertEqual(self.audit().status, "denied")

    def test_duplicate_json_members_deny(self) -> None:
        self.bundle["runs"][1] = self.save("run-1.json", b'{"id":"first","id":"second"}')
        self.assertEqual(self.audit().status, "denied")

    def test_portable_path_escapes_and_windows_devices_deny(self) -> None:
        for path in (
            "../outside",
            "/absolute",
            "C:/outside",
            "foo\\bar",
            "foo/../bar",
            "foo//bar",
            "./bar",
            "CON",
            "aux.txt",
            "dir/LPT1.json",
            "bar.",
            "bar ",
        ):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                BoundArtifact(path=path, sha256="0" * 64)

    def test_case_aliases_deny_even_on_case_sensitive_filesystems(self) -> None:
        self.bundle["artifacts"].append({"path": "SOURCE.txt", "sha256": "0" * 64})
        self.assertEqual(self.audit().status, "denied")

    def test_artifact_symlink_denies(self) -> None:
        path = self.root / "source.txt"
        path.unlink()
        try:
            path.symlink_to(self.root / "fixture_source.txt")
        except OSError as error:
            self.skipTest("symlink creation unavailable: " + str(error))
        self.assertEqual(self.audit().status, "denied")

    def test_missing_bundle_denies(self) -> None:
        result = audit_bundle(self.root)
        self.assertEqual(result.status, "denied")
        self.assertFalse(result.execution_allowed)

    def test_declared_source_is_never_executed(self) -> None:
        marker = self.root / "executed"
        artifact = self.save("source.txt", f"open({str(marker)!r}, 'w').write('executed')".encode())
        self.bundle["artifacts"][0] = artifact
        self.profile["source_sha256"] = artifact["sha256"]
        self.replace_profile()
        self.assertEqual(self.audit().status, "consistent_records")
        self.assertFalse(marker.exists())

    def test_total_bundle_bytes_are_bounded(self) -> None:
        for number in range(9):
            self.bundle["artifacts"].append(self.save(f"large-{number}.bin", b"x" * MAX_FILE_BYTES))
        result = self.audit()
        self.assertEqual(result.status, "denied")
        self.assertIn("bundle byte limit exceeded", result.reasons)

    def test_deeply_nested_malformed_input_denies(self) -> None:
        self.save("bundle.json", b"[" * 2000 + b"]" * 2000)
        self.assertEqual(audit_bundle(self.root).status, "denied")

    def test_null_and_conflicting_source_bindings_deny(self) -> None:
        self.profile["policy"] = "missing-policy.txt"
        self.profile["policy_sha256"] = None
        self.replace_profile()
        self.assertEqual(self.audit().status, "denied")
        self.profile["policy"] = "policy.txt"
        self.profile["policy_sha256"] = self.bundle["artifacts"][3]["sha256"]
        self.profile["additional_sources"] = {"missing.txt": None}
        self.replace_profile()
        self.assertEqual(self.audit().status, "denied")
        self.profile["additional_sources"] = {"source.txt": "0" * 64}
        self.replace_profile()
        self.assertEqual(self.audit().status, "denied")

    def test_numeric_contract_values_cannot_be_replaced_by_booleans(self) -> None:
        self.profile["original_limits"] = {**self.protocol["limits"], "cpus": True}
        self.replace_profile()
        self.assertEqual(self.audit().status, "denied")

    def test_run_execution_flag_requires_literal_false(self) -> None:
        for value in (0, True, None):
            with self.subTest(value=value):
                self.records[1]["execution_allowed"] = value
                self.replace_record(1)
                self.assertEqual(self.audit().status, "denied")

    def test_policy_paths_cannot_hide_aliases_during_resolution(self) -> None:
        for name in ("./policy.txt", "policy.txt/.", "././policy.txt"):
            with self.subTest(path=name):
                self.profile["policy"] = name
                self.replace_profile()
                self.assertEqual(self.audit().status, "denied")
        (self.root / "policies").mkdir()
        self.bundle["artifacts"][3] = self.save("policies/policy.txt", b"synthetic policy")
        for name in ("policies//policy.txt", "policies/./policy.txt", "policies/policy.txt/"):
            with self.subTest(path=name):
                self.profile["policy"] = name
                self.replace_profile()
                self.assertEqual(self.audit().status, "denied")

    def test_directory_case_aliases_deny(self) -> None:
        for directory, filename in (("Sources", "first.txt"), ("sources", "second.txt")):
            (self.root / directory).mkdir(exist_ok=True)
            self.bundle["artifacts"].append(
                self.save(directory + "/" + filename, b"synthetic additional source")
            )
        self.assertEqual(self.audit().status, "denied")

    def test_nested_profile_policy_and_shared_directories_remain_valid(self) -> None:
        (self.root / "profiles/policies").mkdir(parents=True)
        self.bundle["artifacts"][3] = self.save("profiles/policies/policy.txt", b"synthetic policy")
        self.profile["policy"] = "policies/policy.txt"
        self.bundle["profile"]["path"] = "profiles/profile.json"
        self.replace_profile()
        self.bundle["artifacts"].append(
            self.save("profiles/policies/extra.txt", b"synthetic additional source")
        )
        self.assertEqual(self.audit().status, "consistent_records")

    def test_nonfinite_profile_json_denies(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.profile["diagnostic_seconds"] = value
                self.replace_profile()
                result = self.audit()
                self.assertEqual(result.status, "denied")
        self.profile["diagnostic_seconds"] = "NaN and Infinity are literal text"
        self.replace_profile()
        self.assertEqual(self.audit().status, "consistent_records")

    def test_json_exponent_overflow_denies(self) -> None:
        for number in ("1e999", "-1e999"):
            with self.subTest(number=number):
                self.profile["diagnostic_seconds"] = "overflow-placeholder"
                data = (
                    json.dumps(self.profile, sort_keys=True)
                    .encode()
                    .replace(b'"overflow-placeholder"', number.encode())
                )
                profile = self.save("profile.json", data)
                self.bundle["profile"] = profile
                self.identity["configuration"] = profile["sha256"]
                for index, record in enumerate(self.records):
                    record["identity"] = self.identity.copy()
                    self.replace_record(index)
                self.assertEqual(self.audit().status, "denied")
        self.profile["diagnostic_seconds"] = 0.125
        self.replace_profile()
        self.assertEqual(self.audit().status, "consistent_records")


if __name__ == "__main__":
    unittest.main()
