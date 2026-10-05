"""Fresh refusal/readback tests; these do not qualify Linux or a native runtime."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.observe_linux_storage import inventory, verify_inputs


class StorageObserverTests(unittest.TestCase):
    def test_changed_bound_bytes_refuse_before_any_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.write_bytes(b"original")
            (root / "bindings.json").write_text(
                json.dumps(
                    {
                        "architecture": "aarch64",
                        "sha256": {str(source): hashlib.sha256(source.read_bytes()).hexdigest()},
                    }
                )
            )
            source.write_bytes(b"replacement")
            with patch("scripts.observe_linux_storage.subprocess.run") as helper:
                with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                    verify_inputs(root)
                helper.assert_not_called()
            self.assertEqual(source.read_bytes(), b"replacement")

    def test_unbound_architecture_refuses_without_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bindings.json").write_text(
                json.dumps({"architecture": "unbound", "sha256": {}})
            )
            with patch("scripts.observe_linux_storage.subprocess.run") as helper:
                with self.assertRaisesRegex(RuntimeError, "aarch64 ABI"):
                    verify_inputs(root)
                helper.assert_not_called()

    def test_independent_inventory_keeps_alias_identity_and_does_not_follow_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            owned = root / "owned"
            owned.mkdir()
            source = owned / "source"
            source.write_bytes(b"synthetic")
            os.link(source, owned / "alias")
            outside = root / "outside"
            outside.write_bytes(b"private outside bytes")
            os.symlink(outside, owned / "link")
            rows = {item["path"]: item for item in inventory(owned)}
            self.assertEqual(set(rows), {"source", "alias", "link"})
            for key in ("device", "inode", "logical_bytes", "allocated_bytes"):
                self.assertEqual(rows["source"][key], rows["alias"][key])
            self.assertEqual(rows["source"]["links"], 2)
            self.assertEqual(rows["link"]["logical_bytes"], len(str(outside).encode()))
            self.assertEqual(outside.read_bytes(), b"private outside bytes")


if __name__ == "__main__":
    unittest.main()
