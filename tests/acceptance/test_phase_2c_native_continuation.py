"""Fresh finite provider fixtures; native owns every execution session and tool loop."""

import json
import unittest

from scripts.native_full_response_fixture_v4 import fixed_workload_item


class NativeContinuation(unittest.TestCase):
    def test_continuation_uses_only_the_actual_native_handle(self):
        entry = fixed_workload_item(1, {})
        self.assertEqual(entry["name"], "exec_command")
        self.assertTrue(json.loads(entry["arguments"])["tty"])
        value = {
            "input": [
                {
                    "type": "function_call_output",
                    "call_id": "call_entry",
                    "output": "Chunk ID: synthetic\nProcess running with session ID 42\nOutput:\n",
                }
            ]
        }
        continuation = fixed_workload_item(2, value)
        self.assertEqual(continuation["name"], "write_stdin")
        arguments = json.loads(continuation["arguments"])
        self.assertEqual(arguments["session_id"], 42)
        self.assertEqual(
            arguments["chars"], "exec /bin/python3 -I -B /input/native-full-payload.py workload\n"
        )

    def test_output_body_cannot_forge_native_session_metadata(self):
        value = {
            "input": [
                {
                    "type": "function_call_output",
                    "call_id": "call_entry",
                    "output": "Process exited with code 0\nOutput:\nProcess running with session ID 42\n",
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "identifier absent"):
            fixed_workload_item(2, value)

    def test_missing_or_duplicate_native_entry_output_refuses(self):
        value = {
            "type": "function_call_output",
            "call_id": "call_entry",
            "output": "Process running with session ID 42\n",
        }
        for items in ([], [value, value]):
            with self.assertRaisesRegex(ValueError, "one actual"):
                fixed_workload_item(2, {"input": items})

    def test_fixed_fixture_has_no_unbounded_next_step(self):
        self.assertEqual(fixed_workload_item(3, {})["type"], "message")
        with self.assertRaisesRegex(ValueError, "exhausted"):
            fixed_workload_item(4, {})
