"""Offline checks for the prospective Phase 3B source extractor."""

import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts import phase3b_extract_source as extractor


class Phase3BSourceExtraction(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "source.tar.gz"
        self.data = b"hello\n"
        row = {
            "path": "README.md",
            "bytes": len(self.data),
            "sha256": hashlib.sha256(self.data).hexdigest(),
        }
        inventory_digest = hashlib.sha256(
            json.dumps([row], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.corpus = {
            "repositories": [
                {
                    "id": "python-1",
                    "repository": "pallets/click",
                    "revision": "abc",
                    "source_identity": {},
                }
            ]
        }
        self.inventory = {
            "repositories": [
                {
                    "id": "python-1",
                    "files": [row],
                    "source_inventory_sha256": inventory_digest,
                }
            ]
        }
        original = extractor._load
        extractor._load = lambda name: (self.corpus if name == "corpus.json" else self.inventory)
        self.addCleanup(setattr, extractor, "_load", original)

    def _archive(self, *, link: bool = False, extra: bool = False) -> None:
        with tarfile.open(self.archive, "w:gz") as archive:
            regular = tarfile.TarInfo("click-abc/README.md")
            regular.size = len(self.data)
            archive.addfile(regular, io.BytesIO(self.data))
            if link:
                member = tarfile.TarInfo("click-abc/escape")
                member.type = tarfile.SYMTYPE
                member.linkname = "/etc/passwd"
                archive.addfile(member)
            if extra:
                member = tarfile.TarInfo("click-abc/extra.txt")
                member.size = 1
                archive.addfile(member, io.BytesIO(b"x"))
        self.corpus["repositories"][0]["source_identity"] = {
            "archive_bytes": self.archive.stat().st_size,
            "archive_sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
        }

    def test_exact_archive_extracts_and_matches_inventory(self) -> None:
        self._archive()
        result = extractor.extract("python-1", self.archive, self.root / "output")
        self.assertEqual(result["files"], 1)
        self.assertEqual((self.root / "output/README.md").read_bytes(), self.data)

    def test_symbolic_link_refuses_before_output_creation(self) -> None:
        self._archive(link=True)
        with self.assertRaisesRegex(ValueError, "unsafe member"):
            extractor.extract("python-1", self.archive, self.root / "output")
        self.assertFalse((self.root / "output").exists())

    def test_extra_file_refuses_before_output_creation(self) -> None:
        self._archive(extra=True)
        with self.assertRaisesRegex(ValueError, "frozen file inventory"):
            extractor.extract("python-1", self.archive, self.root / "output")
        self.assertFalse((self.root / "output").exists())


if __name__ == "__main__":
    unittest.main()
