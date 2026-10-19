"""Synthetic local acceptance for the bounded retained extractor."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts import phase3b_extract_retained as extractor
from scripts.phase3b_inspect_archive_members import inspect_archive


class RetainedExtractor(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "stage"

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

    def test_regular_tar_readback_and_private_modes(self) -> None:
        path, spec = self.tar("bun", [("pkg", "directory", b""), ("pkg/tool", "regular", b"hello")])
        result = self.run_batch(path, spec)
        self.assertEqual(result["content_bytes"], 5)
        self.assertEqual((self.output / "bun/pkg/tool").read_bytes(), b"hello")
        self.assertEqual(json.loads((self.output / "manifest.json").read_text()), result)
        self.assertEqual((self.output / "bun/pkg/tool").stat().st_mode & 0o777, 0o600)

    def test_zip_readback(self) -> None:
        path = self.root / "bun.blob"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as source:
            source.writestr("pkg/tool", b"zip")
        spec = extractor.ArchiveSpec(
            "bun",
            path.stat().st_size,
            hashlib.sha256(path.read_bytes()).hexdigest(),
            inspect_archive(path),
        )
        self.run_batch(path, spec)
        self.assertEqual((self.output / "bun/pkg/tool").read_bytes(), b"zip")

    def test_unsafe_paths_refuse_before_output(self) -> None:
        for bad in ("../escape", "/absolute", "a//b", "a/./b", "a/../b", "a\\b"):
            with self.subTest(name=bad):
                path, spec = self.tar("bun", [(bad, "regular", b"x")])
                with self.assertRaisesRegex(ValueError, "unsafe path"):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_case_aliases_and_non_directory_parent_refuse(self) -> None:
        cases = [
            [("File", "regular", b"x"), ("file", "regular", b"y")],
            [("caf\u00e9", "regular", b"x"), ("cafe\u0301", "regular", b"y")],
            [("Foo/a", "regular", b"x"), ("foo/b", "regular", b"y")],
            [("file", "regular", b"x"), ("file/child", "regular", b"y")],
        ]
        for members in cases:
            with self.subTest(members=members):
                path, spec = self.tar("bun", members)
                with self.assertRaises(ValueError):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_unapproved_links_and_special_members_refuse(self) -> None:
        for kind in ("symlink", "hardlink", "special"):
            with self.subTest(kind=kind):
                path, spec = self.tar("bun", [("link", kind, "target")])
                with self.assertRaisesRegex(ValueError, "unapproved link or special"):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_only_three_recorded_node_links_follow_regular_readback(self) -> None:
        base = "node-v22.14.0-linux-arm64"
        pairs = [
            ("npm", "../lib/node_modules/npm/bin/npm-cli.js"),
            ("npx", "../lib/node_modules/npm/bin/npx-cli.js"),
            ("corepack", "../lib/node_modules/corepack/dist/corepack.js"),
        ]
        files = [(base + "/" + target[3:], "regular", b"x") for _, target in pairs]
        links = [(base + "/bin/" + name, "symlink", target) for name, target in pairs]
        path, spec = self.tar("node", files + links)
        result = self.run_batch(path, spec)
        self.assertEqual(len(result["files"]), 3)
        for name, target in pairs:
            self.assertEqual(
                (self.output / "node" / base / "bin" / name).readlink().as_posix(), target
            )

    def test_node_link_chain_or_changed_pair_refuses(self) -> None:
        pairs = [("a", "../target"), ("b", "a"), ("c", "../target")]
        members = [("pkg/target", "regular", b"x")]
        members += [("pkg/bin/" + name, "symlink", target) for name, target in pairs]
        path, spec = self.tar("node", members)
        with self.assertRaisesRegex(ValueError, "directly to a regular member"):
            self.run_batch(path, spec)
        self.assertFalse(self.output.exists())

    def test_node_links_wait_for_every_archive_readback(self) -> None:
        node_members = [("pkg/target", "regular", b"node")]
        node_members += [
            ("pkg/bin/" + name, "symlink", "../target") for name in ("npm", "npx", "corepack")
        ]
        node_path, node_spec = self.tar("node", node_members)
        source_path, source_spec = self.tar("swift-1", [("project-abc/file", "regular", b"source")])
        source_spec = extractor.ArchiveSpec(
            source_spec.archive_id,
            source_spec.archive_bytes,
            source_spec.archive_sha256,
            source_spec.report,
            "project-abc",
            {"file": {"bytes": 6, "sha256": "0" * 64}},
        )
        with self.assertRaisesRegex(ValueError, "frozen source inventory"):
            extractor.extract_batch(
                {"node": node_path, "swift-1": source_path},
                [node_spec, source_spec],
                self.output,
            )
        self.assertFalse((self.output / "node/pkg/bin/npm").is_symlink())
        self.assertFalse((self.output / "manifest.json").exists())

    def test_dotnet_single_leading_dot_and_root_marker(self) -> None:
        path, spec = self.tar(
            "dotnet-runtime-net8", [(".", "directory", b""), ("./host/tool", "regular", b"net")]
        )
        self.run_batch(path, spec)
        self.assertEqual((self.output / "dotnet-runtime-net8/host/tool").read_bytes(), b"net")
        for bad in ("host/tool", "././host/tool", "./host/../tool"):
            with self.subTest(name=bad):
                self.output = self.root / "new-stage"
                path, spec = self.tar("dotnet-runtime-net8", [(bad, "regular", b"net")])
                with self.assertRaises(ValueError):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_excluded_archives_refuse(self) -> None:
        for archive_id in extractor.EXCLUDED_IDS:
            with self.subTest(archive_id=archive_id):
                path, spec = self.tar(archive_id, [("file", "regular", b"x")])
                with self.assertRaisesRegex(ValueError, "excluded"):
                    self.run_batch(path, spec)
                self.assertFalse(self.output.exists())

    def test_length_digest_and_report_changes_refuse(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"x")])
        changed = extractor.ArchiveSpec("bun", spec.archive_bytes, "0" * 64, spec.report)
        with self.assertRaisesRegex(ValueError, "pinned length or SHA-256"):
            self.run_batch(path, changed)
        changed = extractor.ArchiveSpec(
            "bun", spec.archive_bytes, spec.archive_sha256, {**spec.report, "members": 2}
        )
        with self.assertRaisesRegex(ValueError, "member report"):
            self.run_batch(path, changed)
        self.assertFalse(self.output.exists())

    def test_frozen_source_inventory_binding(self) -> None:
        path, spec = self.tar("swift-1", [("project-abc/file", "regular", b"known")])
        expected = {"file": {"bytes": 5, "sha256": hashlib.sha256(b"known").hexdigest()}}
        spec = extractor.ArchiveSpec(
            spec.archive_id,
            spec.archive_bytes,
            spec.archive_sha256,
            spec.report,
            "project-abc",
            expected,
        )
        self.run_batch(path, spec)
        self.assertEqual((self.output / "swift-1/project-abc/file").read_bytes(), b"known")
        self.output = self.root / "new-stage"
        expected["file"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "frozen source inventory"):
            self.run_batch(path, spec)
        self.assertFalse((self.output / "manifest.json").exists())

    def test_quota_stop_retains_partial_tree(self) -> None:
        data = b"x" * (extractor.CHUNK + 7)
        path, spec = self.tar("bun", [("large", "regular", data)])

        def free(_path: Path) -> int:
            partial = self.output / "bun/large"
            if partial.exists() and partial.stat().st_size >= extractor.CHUNK:
                return extractor.FREE_FLOOR - 1
            return extractor.FREE_FLOOR + 1

        with self.assertRaisesRegex(ValueError, "free space"):
            self.run_batch(path, spec, free_bytes=free)
        self.assertEqual((self.output / "bun/large").stat().st_size, extractor.CHUNK)
        self.assertFalse((self.output / "manifest.json").exists())

    def test_short_write_failure_retains_partial_tree(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"content")])
        original_write = extractor.os.write
        calls = 0

        def interrupted_write(fd: int, data: bytes | memoryview) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                return original_write(fd, data[:2])
            raise OSError("synthetic interrupted write")

        with mock.patch.object(extractor.os, "write", side_effect=interrupted_write):
            with self.assertRaisesRegex(OSError, "synthetic interrupted write"):
                self.run_batch(path, spec)
        self.assertEqual((self.output / "bun/file").read_bytes(), b"co")
        self.assertFalse((self.output / "manifest.json").exists())

    def test_free_space_refusal_creates_no_output(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"x")])
        with self.assertRaisesRegex(ValueError, "free space"):
            self.run_batch(path, spec, free_bytes=lambda _path: extractor.FREE_FLOOR - 1)
        self.assertFalse(self.output.exists())

    def test_existing_output_refuses_without_replacement(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"new")])
        self.output.mkdir()
        (self.output / "keep").write_bytes(b"old")
        with self.assertRaises(FileExistsError):
            self.run_batch(path, spec)
        self.assertEqual((self.output / "keep").read_bytes(), b"old")

    def test_injected_symlink_parent_refuses_without_external_write(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"new")])
        outside = self.root / "outside"
        outside.mkdir()
        injected = False

        def free(_path: Path) -> int:
            nonlocal injected
            if not injected and self.output.is_dir():
                (self.output / "bun").symlink_to(outside, target_is_directory=True)
                injected = True
            return extractor.FREE_FLOOR + 1

        with self.assertRaises(OSError):
            self.run_batch(path, spec, free_bytes=free)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.output / "manifest.json").exists())

    def test_unexpected_output_name_blocks_manifest(self) -> None:
        path, spec = self.tar("bun", [("file", "regular", b"x")])
        injected = False

        def free(_path: Path) -> int:
            nonlocal injected
            if not injected and (self.output / "bun/file").is_file():
                (self.output / "bun/extra").write_bytes(b"unexpected")
                injected = True
            return extractor.FREE_FLOOR + 1

        with self.assertRaisesRegex(ValueError, "unexpected or duplicate name"):
            self.run_batch(path, spec, free_bytes=free)
        self.assertEqual((self.output / "bun/extra").read_bytes(), b"unexpected")
        self.assertFalse((self.output / "manifest.json").exists())

    def test_real_cli_closed_after_approved_attempt(self) -> None:
        proposal = json.loads(extractor.LEDGER.read_text())["archive_extraction_proposal"]
        self.assertFalse(proposal["extraction_admitted"])
        self.assertEqual(proposal["completed_attempts"], 1)
        self.assertIsNotNone(proposal["owner_extraction_decision"])
        self.assertEqual(proposal["extractor_sha256"], extractor._sha256(Path(extractor.__file__)))


if __name__ == "__main__":
    unittest.main()
