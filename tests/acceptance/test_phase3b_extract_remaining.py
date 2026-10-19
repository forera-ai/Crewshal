"""Synthetic checks for the closed four-archive extractor candidate."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import plistlib
import tarfile
import tempfile
import unittest
from unittest import mock

from scripts import phase3b_extract_remaining as extractor
from scripts.phase3b_inspect_archive_members import inspect_archive


class RemainingExtractor(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "output"

    def tar(
        self, archive_id: str, members: list[tuple[str, str, bytes | str]]
    ) -> tuple[Path, extractor.ArchiveSpec]:
        path = self.root / (archive_id + ".blob")
        with tarfile.open(path, "w:gz") as source:
            for name, kind, value in members:
                member = tarfile.TarInfo(name)
                if kind == "regular":
                    assert isinstance(value, bytes)
                    member.size = len(value)
                    source.addfile(member, io.BytesIO(value))
                elif kind == "directory":
                    member.type = tarfile.DIRTYPE
                    source.addfile(member)
                elif kind == "symlink":
                    member.type = tarfile.SYMTYPE
                    assert isinstance(value, str)
                    member.linkname = value
                    source.addfile(member)
                elif kind == "hardlink":
                    member.type = tarfile.LNKTYPE
                    member.linkname = str(value)
                    source.addfile(member)
                else:
                    member.type = tarfile.FIFOTYPE
                    source.addfile(member)
        spec = extractor.ArchiveSpec(
            archive_id,
            path.stat().st_size,
            hashlib.sha256(path.read_bytes()).hexdigest(),
            inspect_archive(path),
        )
        return path, spec

    def run_batch(
        self, path: Path, spec: extractor.ArchiveSpec, **kwargs: object
    ) -> dict[str, object]:
        return extractor.extract_batch({spec.archive_id: path}, [spec], self.output, **kwargs)  # type: ignore[arg-type]

    def swift_members(self) -> list[tuple[str, str, bytes | str]]:
        members: list[tuple[str, str, bytes | str]] = [
            ("pkg/regular", "regular", b"swift"),
            ("pkg/dir", "directory", b""),
        ]
        members += [(f"pkg/link-{i:02d}", "symlink", "regular") for i in range(34)]
        members += [
            ("pkg/link-34", "symlink", "link-33"),
            ("pkg/link-35", "symlink", "link-34"),
            ("pkg/link-36", "symlink", "dir"),
        ]
        return members

    def test_four_archive_policy_and_closed_admission(self) -> None:
        self.assertEqual(
            {spec.archive_id for spec in extractor.load_bound_policy()}, extractor.SELECTED_IDS
        )
        proposal = json.loads(extractor.LEDGER.read_text())["archive_extraction_remaining"]
        self.assertFalse(proposal["extraction_admitted"])
        self.assertFalse(proposal["new_image_creation_admitted"])
        with mock.patch("sys.argv", ["extract", str(self.root), str(self.output)]):
            with self.assertRaisesRegex(ValueError, "no separate exact-hash admission"):
                extractor.main()
        self.assertFalse(self.output.exists())

    def test_mount_identity_must_match_exact_image(self) -> None:
        image = self.root / "image.sparseimage"
        image.write_bytes(b"image")
        info = {
            "images": [
                {
                    "image-path": str(image),
                    "system-entities": [{"mount-point": str(self.root)}],
                }
            ]
        }
        with (
            mock.patch.object(extractor.os.path, "ismount", return_value=True),
            mock.patch.object(
                extractor.subprocess, "check_output", return_value=plistlib.dumps(info)
            ),
        ):
            self.assertTrue(extractor._mount_is_image(self.root, image))
            self.assertFalse(extractor._mount_is_image(self.root / "other", image))
            self.assertFalse(extractor._mount_is_image(self.root, self.root / "missing"))

    def test_regular_readback_and_private_output(self) -> None:
        path, spec = self.tar("codex-native", [("pkg/tool", "regular", b"native")])
        result = self.run_batch(path, spec)
        self.assertEqual(result["content_bytes"], 6)
        self.assertEqual((self.output / "codex-native/pkg/tool").read_bytes(), b"native")
        self.assertEqual(
            (self.output / "manifest.json").read_bytes(),
            json.dumps(result, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        )
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)

    def test_dotnet_one_leading_dot_and_root_marker(self) -> None:
        path, spec = self.tar(
            "dotnet-sdk", [(".", "directory", b""), ("./host/tool", "regular", b"net")]
        )
        self.run_batch(path, spec)
        self.assertEqual((self.output / "dotnet-sdk/host/tool").read_bytes(), b"net")
        for name in ("host/tool", "././host/tool", "./host/../tool"):
            with self.subTest(name=name):
                self.output = self.root / "new-output"
                path, spec = self.tar("dotnet-sdk", [(name, "regular", b"net")])
                with self.assertRaises(ValueError):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_swift_exact_links_include_chains_and_directory(self) -> None:
        path, spec = self.tar("swift", self.swift_members())
        result = self.run_batch(path, spec)
        self.assertEqual(len(result["links"]), 37)
        self.assertEqual((self.output / "swift/pkg/link-35").read_bytes(), b"swift")
        self.assertTrue((self.output / "swift/pkg/link-36").is_dir())

    def test_swift_links_wait_for_every_archive_readback(self) -> None:
        swift_path, swift_spec = self.tar("swift", self.swift_members())
        native_path, native_spec = self.tar(
            "codex-native", [("large", "regular", b"x" * (extractor.CHUNK + 7))]
        )

        def free(_path: Path) -> int:
            partial = self.output / "codex-native/large"
            if partial.exists() and partial.stat().st_size >= extractor.CHUNK:
                return extractor.FREE_FLOOR - 1
            return extractor.FREE_FLOOR + 1

        with self.assertRaisesRegex(ValueError, "free space"):
            extractor.extract_batch(
                {"swift": swift_path, "codex-native": native_path},
                [swift_spec, native_spec],
                self.output,
                free_bytes=free,
            )
        self.assertFalse((self.output / "swift/pkg/link-00").is_symlink())
        self.assertFalse((self.output / "manifest.json").exists())

    def test_swift_escape_cycle_and_missing_target_refuse(self) -> None:
        changes = [
            ("../../escape", "escapes"),
            ("link-36", "cycle"),
            ("missing", "lacks"),
        ]
        for target, error in changes:
            with self.subTest(target=target):
                members = self.swift_members()
                members[-1] = ("pkg/link-36", "symlink", target)
                if target == "link-36":
                    members[-2] = ("pkg/link-35", "symlink", "link-36")
                path, spec = self.tar("swift", members)
                with self.assertRaisesRegex(ValueError, error):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_unsafe_paths_aliases_and_special_members_refuse(self) -> None:
        cases: list[list[tuple[str, str, bytes | str]]] = [
            [("../escape", "regular", b"x")],
            [("File", "regular", b"x"), ("file", "regular", b"y")],
            [("file", "regular", b"x"), ("file/child", "regular", b"y")],
            [("link", "hardlink", "file")],
            [("fifo", "special", b"")],
        ]
        for members in cases:
            with self.subTest(members=members):
                path, spec = self.tar("codex-native", members)
                with self.assertRaises(ValueError):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_digest_and_content_cap_refuse_before_output(self) -> None:
        path, spec = self.tar("claude-native", [("file", "regular", b"abc")])
        changed = extractor.ArchiveSpec(spec.archive_id, spec.archive_bytes, "0" * 64, spec.report)
        with self.assertRaisesRegex(ValueError, "pinned length or SHA-256"):
            self.run_batch(path, changed)
        with mock.patch.object(extractor, "CONTENT_CAP", 2):
            with self.assertRaisesRegex(ValueError, "exact bound"):
                self.run_batch(path, spec)
        self.assertFalse(self.output.exists())

    def test_quota_stop_keeps_partial_output(self) -> None:
        data = b"x" * (extractor.CHUNK + 7)
        path, spec = self.tar("claude-native", [("large", "regular", data)])

        def free(_path: Path) -> int:
            partial = self.output / "claude-native/large"
            if partial.exists() and partial.stat().st_size >= extractor.CHUNK:
                return extractor.FREE_FLOOR - 1
            return extractor.FREE_FLOOR + 1

        with self.assertRaisesRegex(ValueError, "free space"):
            self.run_batch(path, spec, free_bytes=free)
        self.assertEqual((self.output / "claude-native/large").stat().st_size, extractor.CHUNK)
        self.assertFalse((self.output / "manifest.json").exists())

    def test_partial_write_and_existing_output_never_replace(self) -> None:
        path, spec = self.tar("claude-native", [("file", "regular", b"content")])
        original_write = extractor.os.write
        calls = 0

        def interrupted(fd: int, data: bytes | memoryview) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                return original_write(fd, data[:2])
            raise OSError("synthetic interrupted write")

        with mock.patch.object(extractor.os, "write", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.run_batch(path, spec)
        self.assertEqual((self.output / "claude-native/file").read_bytes(), b"co")
        self.output = self.root / "existing"
        self.output.mkdir()
        marker = self.output / "marker"
        marker.write_text("original")
        with self.assertRaises(FileExistsError):
            self.run_batch(path, spec)
        self.assertEqual(marker.read_text(), "original")
