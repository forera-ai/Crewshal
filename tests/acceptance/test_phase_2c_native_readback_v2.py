"""Independent stage-selection regressions from fresh synthetic observations."""

import copy
import unittest

from scripts.readback_native_full_v2 import instruction_evidence


class NativeReadbackStages(unittest.TestCase):
    def fixtures(self):
        request = {
            "tools": ["exec_command", "write_stdin", "request_user_input"],
            "instruction_injection_present": False,
        }
        record = {
            "fixture_requests_after_capture": [copy.deepcopy(request), copy.deepcopy(request)],
            "fixture_requests": [{"tools": [], "instruction_injection_present": True}],
        }
        role = {
            "global_instruction_view": {
                name: {"contents": "", "write": {"denied": True}, "unlink": {"denied": True}}
                for name in ("AGENTS.md", "AGENTS.override.md")
            }
        }
        return record, [copy.deepcopy(role) for _ in range(4)]

    def test_later_lifecycle_request_does_not_replace_workload_evidence(self):
        record, roles = self.fixtures()
        self.assertTrue(instruction_evidence(record, roles))

    def test_later_clean_request_cannot_hide_workload_injection(self):
        record, roles = self.fixtures()
        record["fixture_requests_after_capture"][0]["instruction_injection_present"] = True
        record["fixture_requests"] = []
        self.assertFalse(instruction_evidence(record, roles))

    def test_missing_workload_record_never_falls_back_to_lifecycle(self):
        record, roles = self.fixtures()
        del record["fixture_requests_after_capture"]
        with self.assertRaises(KeyError):
            instruction_evidence(record, roles)

    def test_extra_tool_or_mutable_global_instruction_refuses(self):
        record, roles = self.fixtures()
        record["fixture_requests_after_capture"][0]["tools"].append("unknown_file_tool")
        self.assertFalse(instruction_evidence(record, roles))
        record, roles = self.fixtures()
        roles[2]["global_instruction_view"]["AGENTS.override.md"]["unlink"]["denied"] = False
        self.assertFalse(instruction_evidence(record, roles))
