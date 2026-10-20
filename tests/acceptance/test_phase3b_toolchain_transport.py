"""Local fixtures for the offline Phase 3B transport boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import phase3b_toolchain_transport as transport


class ToolchainTransport(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        (self.source / "tool" / "bin").mkdir(parents=True)
        (self.source / "tool" / "bin" / "run").write_bytes(b"fixture-data")
        (self.source / "tool" / "bin" / "alias").symlink_to("run")
        self.data = {
            "archive_ids": ["tool"],
            "content_bytes": 12,
            "directories": ["tool", "tool/bin"],
            "files": [
                {
                    "archive_id": "tool",
                    "path": "bin/run",
                    "bytes": 12,
                    "sha256": hashlib.sha256(b"fixture-data").hexdigest(),
                }
            ],
            "links": [{"path": "tool/bin/alias", "target": "run"}],
            "tree_sha256": "0" * 64,
        }
        (self.source / "manifest.json").write_text(json.dumps(self.data))

    def manifest(self) -> dict[str, object]:
        return transport.load_manifest(self.source / "manifest.json")

    def test_pack_and_stage_exact_fixture(self) -> None:
        manifest = self.manifest()
        transport.verify_source(self.source, manifest)
        output = self.root / "fixture.tar"
        packed = transport.pack_part(self.source, manifest, output)
        self.assertEqual(packed["sha256"], transport.digest(output))
        destination = self.root / "destination"
        destination.mkdir()
        total = [0]
        transport.stage_part(output, manifest, destination, total)
        self.assertEqual(total, [12])
        self.assertEqual((destination / "tool/bin/run").read_bytes(), b"fixture-data")
        self.assertEqual((destination / "tool/bin/alias").readlink().as_posix(), "run")

    def test_unsafe_paths_links_and_case_aliases_refuse(self) -> None:
        for value in ("../escape", "/absolute", "a//b", "a/./b", "a\\b"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                transport.safe_path(value)
        with self.assertRaises(ValueError):
            transport._link_target("tool/bin/alias", "../../../escape")
        data = self.data.copy()
        data["files"] = [
            *self.data["files"],
            {
                "archive_id": "tool",
                "path": "BIN/run",
                "bytes": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
            },
        ]
        (self.source / "manifest.json").write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "case alias"):
            self.manifest()

    def test_tamper_and_replacement_refuse(self) -> None:
        manifest = self.manifest()
        output = self.root / "fixture.tar"
        transport.pack_part(self.source, manifest, output)
        with self.assertRaises(FileExistsError):
            transport.pack_part(self.source, manifest, output)
        data = output.read_bytes()
        self.assertIn(b"fixture-data", data)
        output.write_bytes(data.replace(b"fixture-data", b"fixture-fail", 1))
        with self.assertRaises(ValueError):
            transport.verify_tar(output, manifest)

    def test_quota_stop_retains_partial_output(self) -> None:
        manifest = self.manifest()
        output = self.root / "fixture.tar"
        transport.pack_part(self.source, manifest, output)
        destination = self.root / "destination"
        destination.mkdir()
        actual = transport.shutil.disk_usage(destination)
        low = actual._replace(free=0)
        with patch.object(transport.shutil, "disk_usage", return_value=low):
            with self.assertRaisesRegex(ValueError, "floor"):
                transport.stage_part(output, manifest, destination, [0])
        self.assertTrue((destination / "tool/bin/run").exists())
        self.assertEqual((destination / "tool/bin/run").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
