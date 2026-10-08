"""Fresh capture fixtures; reset stages must never rewrite earlier observations."""

import unittest

from scripts.probe_native_full_v14 import capture_observations


class CaptureSnapshot(unittest.TestCase):
    def test_lifecycle_clear_preserves_original_workload_requests(self):
        live = [{"tool_outputs": []}, {"tool_outputs": [{"exit": 0}]}]
        captured = capture_observations(live)
        live.clear()
        live.append({"tool_outputs": [], "stage": "deadline"})
        self.assertEqual(captured, [{"tool_outputs": []}, {"tool_outputs": [{"exit": 0}]}])

    def test_nested_later_change_preserves_captured_configuration(self):
        live = [{"tools": ["exec_command"], "instruction_markers": []}]
        captured = capture_observations(live)
        live[0]["tools"].append("injected_tool")
        live[0]["instruction_markers"].append("injected_instruction")
        self.assertEqual(captured, [{"tools": ["exec_command"], "instruction_markers": []}])
