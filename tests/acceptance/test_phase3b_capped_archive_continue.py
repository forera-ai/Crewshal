"""Offline checks for the separate halted-stage continuation receipt."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import phase3b_capped_archive_continue as continuation


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


class ContinueTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.root = base / "stage"
        (self.root / "archives").mkdir(parents=True)
        self.root = self.root.resolve()
        self.image = base / "stage.dmg"
        self.image.write_bytes(b"image")
        self.image = self.image.resolve()
        self.manifest = base / "manifest.json"
        self.body = b"safe archive"
        self.stage = {
            "archive_response_body_cap_bytes": 128,
            "other_response_body_reserve_bytes": 16,
            "stage_transfer_cap_bytes": 144,
            "active_seconds_cap": 7200,
            "elapsed_seconds_cap": 86400,
        }
        self.objects: dict[str, dict[str, object]] = {}
        for identifier in continuation.ATTEMPTED:
            body = identifier.encode()[:1]
            (self.root / "archives" / f"{identifier}.blob").write_bytes(body)
            self.objects[identifier] = {
                "url": f"https://example.test/{identifier}",
                "cap": len(body),
                "exact_size": len(body),
                "digest": "sha256:" + hashlib.sha256(body).hexdigest(),
            }
        self.objects["candidate"] = {
            "url": "https://example.test/candidate",
            "cap": len(self.body),
            "exact_size": len(self.body),
            "digest": "sha256:" + hashlib.sha256(self.body).hexdigest(),
        }
        self.plan: dict[str, object] = {
            "original_scope_sha256": "scope",
            "original_receipt_halted": True,
            "original_failed_id": "dotnet-sdk",
            "unattempted_ids": ["candidate"],
            "retained_dotnet_sdk": {"sha256": hashlib.sha256(b"d").hexdigest()},
            "digest_inputs": {},
        }
        self.manifest.write_text(
            json.dumps(
                {
                    "archive_evidence_stage": {
                        "original_transport_script_sha256": "original-script",
                        "archive_body_bytes_retrieved": 8,
                    }
                }
            )
        )
        self.receipt = self.root / "receipt.sqlite3"
        connection = sqlite3.connect(self.receipt)
        connection.executescript("""
            CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
            CREATE TABLE attempts(id TEXT PRIMARY KEY,status TEXT,body_bytes INTEGER,sha256 TEXT);
            CREATE TABLE reads(class TEXT,actual INTEGER);
        """)
        connection.executemany(
            "INSERT INTO meta VALUES (?,?)",
            {
                "spec_sha256": "scope",
                "script_sha256": "original-script",
                "halted": "1",
                "root": str(self.root),
                "image": str(self.image),
                "start_epoch": str(time.time() - 100),
                "active_seconds": "1",
                "archive_body_bytes": "8",
                "other_body_bytes": "0",
            }.items(),
        )
        for identifier in continuation.ATTEMPTED:
            body = (self.root / "archives" / f"{identifier}.blob").read_bytes()
            connection.execute(
                "INSERT INTO attempts VALUES (?,?,?,?)",
                (
                    identifier,
                    "failed" if identifier == "dotnet-sdk" else "ok",
                    1,
                    None if identifier == "dotnet-sdk" else hashlib.sha256(body).hexdigest(),
                ),
            )
        connection.execute("INSERT INTO reads VALUES ('archive',8)")
        connection.commit()
        connection.close()
        self.plan["original_receipt_sha256"] = continuation._hash(self.receipt)
        self.patches = [
            patch.object(continuation, "MANIFEST", self.manifest),
            patch.object(
                continuation,
                "_ledger",
                side_effect=lambda: (self.stage, self.objects, self.plan, "manifest-hash"),
            ),
            patch.object(continuation, "_authority"),
            patch.object(continuation, "_storage"),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        continuation.prepare(self.root, self.image, self.receipt)

    def test_redirect_and_archive_are_counted_without_url_disclosure(self) -> None:
        opener = Opener(
            [
                Response(302, b"old", "https://cdn.example.test/signed?secret=value"),
                Response(200, self.body),
            ]
        )
        with patch.object(continuation, "build_opener", return_value=opener):
            result = continuation.fetch(self.root, "candidate")
        self.assertEqual(result["bytes"], len(self.body))
        self.assertEqual(result["other_body_bytes"], 3)
        self.assertEqual(opener.calls, 2)
        self.assertNotIn("secret", str(continuation.status(self.root)))
        with self.assertRaisesRegex(continuation.ContinuationError, "one attempt"):
            continuation.fetch(self.root, "candidate")

    def test_error_body_halts_and_preserves_charge(self) -> None:
        opener = Opener([Response(404, b"missing")])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "HTTP 404"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(continuation.status(self.root)["status"], "halted")
        self.assertEqual(continuation.status(self.root)["meta"]["other_body_bytes"], "7")

    def test_network_error_does_not_record_signed_url(self) -> None:
        class FailingOpener:
            def open(self, request, timeout):
                raise OSError("https://cdn.example.test/signed?secret=value")

        with patch.object(continuation, "build_opener", return_value=FailingOpener()):
            with self.assertRaises(OSError):
                continuation.fetch(self.root, "candidate")
        state = continuation.status(self.root)
        self.assertEqual(state["status"], "halted")
        self.assertEqual(state["attempts"][0]["error"], "OSError")
        self.assertNotIn("secret", str(state))

    def test_digest_failure_halts_and_retains_partial_file(self) -> None:
        opener = Opener([Response(200, b"wrong archive")])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "digest differs"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(continuation.status(self.root)["status"], "halted")
        self.assertTrue((self.root / "archives/candidate.blob").exists())

    def test_original_receipt_change_refuses_before_network(self) -> None:
        with sqlite3.connect(self.receipt) as connection:
            connection.execute("UPDATE meta SET value='0' WHERE key='halted'")
        opener = Opener([Response(200, self.body)])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(
                continuation.ContinuationError, "original receipt SHA-256 changed"
            ):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(opener.calls, 0)

    def test_incomplete_crash_reservation_refuses_before_network(self) -> None:
        with sqlite3.connect(self.root / "continuation.sqlite3") as connection:
            connection.execute(
                "INSERT INTO reads(id,hop,class,reserved) VALUES ('candidate',0,'archive',4)"
            )
        opener = Opener([Response(200, self.body)])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "incomplete read"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(opener.calls, 0)

    def test_unfinished_journal_refuses_before_network(self) -> None:
        (self.root / "continuation.sqlite3-journal").write_bytes(b"crash")
        opener = Opener([Response(200, self.body)])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "unfinished journal"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(opener.calls, 0)

    def test_all_eight_attempted_ids_refuse_before_network(self) -> None:
        opener = Opener([Response(200, self.body)])
        with patch.object(continuation, "build_opener", return_value=opener):
            for identifier in continuation.ATTEMPTED:
                with self.subTest(identifier=identifier):
                    with self.assertRaisesRegex(continuation.ContinuationError, "attempted"):
                        continuation.fetch(self.root, identifier)
        self.assertEqual(opener.calls, 0)

    def test_aggregate_cap_halts_before_excess_read(self) -> None:
        self.stage["archive_response_body_cap_bytes"] = 12
        self.stage["stage_transfer_cap_bytes"] = 28
        response = Response(200, self.body)
        opener = Opener([response])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "budget is exhausted"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(continuation.status(self.root)["meta"]["archive_body_bytes"], "4")
        self.assertEqual(response.stream.read(), self.body[4:])

    def test_changed_continuation_receipt_refuses_before_network(self) -> None:
        with sqlite3.connect(self.root / "continuation.sqlite3") as connection:
            connection.execute("UPDATE meta SET value='changed' WHERE key='manifest_sha256'")
        opener = Opener([Response(200, self.body)])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "receipt binding changed"):
                continuation.fetch(self.root, "candidate")
        self.assertEqual(opener.calls, 0)

    def test_swift_signature_packet_alone_never_admits_body(self) -> None:
        self.plan["unattempted_ids"] = ["candidate", "swift"]
        self.objects["swift"] = {
            "url": "https://example.test/swift",
            "cap": 20,
            "exact_size": 20,
            "digest": None,
        }
        opener = Opener([Response(200, b"unverified")])
        with patch.object(continuation, "build_opener", return_value=opener):
            with self.assertRaisesRegex(continuation.ContinuationError, "signature-first approval"):
                continuation.fetch(self.root, "swift")
        self.assertEqual(opener.calls, 0)


class AuthorityTest(unittest.TestCase):
    def test_old_approval_does_not_open_new_transport(self) -> None:
        with self.assertRaisesRegex(continuation.ContinuationError, "separate owner decision"):
            continuation._authority({"owner_decision": None, "body_requests_admitted": False})


if __name__ == "__main__":
    unittest.main()
