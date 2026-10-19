"""Local transport accounting checks for the approved archive evidence stage."""

from __future__ import annotations

import base64
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import phase3b_capped_archive as archive


class Response:
    def __init__(self, status: int, body: bytes, location: str | None = None) -> None:
        self.status = status
        self.stream = io.BytesIO(body)
        self.headers = {"Location": location} if location else {}

    def read(self, count: int) -> bytes:
        return self.stream.read(count)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class Opener:
    def __init__(self, responses: list[Response]) -> None:
        self.responses = responses
        self.calls = 0

    def open(self, request, timeout):
        self.calls += 1
        return self.responses.pop(0)


class ArchiveStageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "stage"
        self.root.mkdir()
        self.image = Path(self.temporary.name) / "stage.dmg"
        self.image.write_bytes(b"image")
        self.body = b"safe archive"
        self.stage = {
            "archive_response_body_cap_bytes": 128,
            "other_response_body_reserve_bytes": 16,
            "stage_transfer_cap_bytes": 144,
            "batch_retained_logical_cap_bytes": 1024,
            "new_mac_host_allocation_cap_bytes": 1024,
            "active_seconds_cap": 7200,
            "elapsed_seconds_cap": 86400,
        }
        self.objects = {"source": {
            "url": "https://example.test/source.tar.gz", "cap": len(self.body),
            "exact_size": len(self.body), "digest": "sha256:" + hashlib.sha256(self.body).hexdigest(),
            "kind": "source",
        }}
        self.patches = [
            patch.object(archive, "_manifest", side_effect=lambda **kwargs: (self.stage, self.objects)),
            patch.object(archive, "_storage", return_value={"volume_bytes": 1024, "image_allocated_bytes": 1024}),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        archive.init(self.root, self.image)

    def test_redirect_body_and_archive_body_are_charged_and_retry_is_refused(self) -> None:
        opener = Opener([
            Response(302, b"old", "https://cdn.example.test/archive"),
            Response(200, self.body),
        ])
        with patch.object(archive, "build_opener", return_value=opener):
            result = archive.fetch(self.root, "source")
        self.assertEqual(result["bytes"], len(self.body))
        self.assertEqual(result["other_body_bytes"], 3)
        self.assertEqual(result["archive_body_bytes"], len(self.body))
        self.assertEqual(opener.calls, 2)
        self.assertEqual((self.root / "archives/source.blob").read_bytes(), self.body)
        with self.assertRaisesRegex(archive.StageError, "one attempt"):
            archive.fetch(self.root, "source")

    def test_mismatch_halts_and_retains_partial_charge(self) -> None:
        opener = Opener([Response(200, b"wrong archive")])
        with patch.object(archive, "build_opener", return_value=opener):
            with self.assertRaisesRegex(archive.StageError, "digest differs"):
                archive.fetch(self.root, "source")
        receipt = archive.status(self.root)
        self.assertEqual(receipt["status"], "halted")
        self.assertEqual(int(receipt["meta"]["archive_body_bytes"]), len(self.body))
        self.assertEqual(receipt["attempts"][0]["body_bytes"], len(self.body))
        self.assertTrue((self.root / "archives/source.blob").exists())
        with self.assertRaisesRegex(archive.StageError, "halted"):
            archive.fetch(self.root, "source")

    def test_missing_digest_refuses_before_attempt(self) -> None:
        previous = self.objects["source"]["digest"]
        self.objects["source"]["digest"] = None
        with self.assertRaisesRegex(archive.StageError, "digest is missing"):
            archive.fetch(self.root, "source")
        self.objects["source"]["digest"] = previous
        self.assertEqual(archive.status(self.root)["attempts"], [])

    def test_changed_receipt_refuses_before_attempt(self) -> None:
        self.objects["source"]["cap"] += 1
        opener = Opener([Response(200, self.body)])
        with patch.object(archive, "build_opener", return_value=opener):
            with self.assertRaisesRegex(archive.StageError, "binding or receipt changed"):
                archive.fetch(self.root, "source")
        self.assertEqual(opener.calls, 0)

    def test_error_body_is_charged_and_stage_halts(self) -> None:
        opener = Opener([Response(404, b"missing")])
        with patch.object(archive, "build_opener", return_value=opener):
            with self.assertRaisesRegex(archive.StageError, "HTTP 404"):
                archive.fetch(self.root, "source")
        receipt = archive.status(self.root)
        self.assertEqual(receipt["status"], "halted")
        self.assertEqual(int(receipt["meta"]["other_body_bytes"]), 7)
        self.assertEqual(receipt["responses"][0]["body_bytes"], 7)

    def test_object_cap_stops_without_reading_excess(self) -> None:
        response = Response(200, self.body + b"extra")
        opener = Opener([response])
        with patch.object(archive, "build_opener", return_value=opener):
            result = archive.fetch(self.root, "source")
        self.assertEqual(result["bytes"], len(self.body))
        self.assertEqual(response.stream.read(), b"extra")

    def test_sha512_hex_and_base64_integrity(self) -> None:
        sha256 = hashlib.sha256(self.body).hexdigest()
        sha512 = hashlib.sha512(self.body).hexdigest()
        integrity = base64.b64encode(bytes.fromhex(sha512)).decode()
        self.assertTrue(archive._digest_matches("sha512:" + sha512, sha256, sha512))
        self.assertTrue(archive._digest_matches("sha512:" + integrity, sha256, sha512))
        self.assertFalse(archive._digest_matches("sha512:" + "0" * 128, sha256, sha512))


if __name__ == "__main__":
    unittest.main()
