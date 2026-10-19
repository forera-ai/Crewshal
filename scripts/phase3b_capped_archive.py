"""One-attempt, charged archive transport for the approved Phase 3B evidence stage."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MANIFEST = Path(__file__).resolve().parents[1] / "docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json"
PROPOSAL = Path(__file__).resolve().parents[1] / "docs/PHASE-3B-CAPPED-ARCHIVE-STAGE-2026-10-19.md"
APPROVED_SPEC_SHA256 = "7286e3da3dee932f178108733bfaa6b111e1adba822b9628dfde7910b7da05cb"
APPROVED_PROPOSAL_SHA256 = "5e2ffccf1fcc8aac716eb2d83c3c060a91a9d088f20929aceeef9a6186fae365"
CHUNK = 1024 * 1024
MAX_REDIRECTS = 5
TOOL_VERSION = "phase3b-capped-archive-v1"


class StageError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _manifest(*, require_admitted: bool = True) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = json.loads(MANIFEST.read_text())
    stage = manifest["archive_evidence_stage"]
    tools = {row["id"]: row for row in manifest["toolchain"]["selected_artifacts"]}
    sources = {row["id"]: row for row in manifest["development"]["selected_sources"]}
    objects = {}
    for name in stage["known_tool_ids"] + stage["npm_ids"]:
        item = tools[name]
        objects[name] = {
            "url": item["exact_url"],
            "cap": item["archive_bytes"] or stage["npm_per_object_policy_cap_bytes"],
            "exact_size": item["archive_bytes"],
            "digest": item["digest"],
            "kind": "tool",
        }
    for name in stage["source_ids"]:
        item = sources[name]
        objects[name] = {
            "url": item["archive_url"],
            "cap": item["archive_bytes"],
            "exact_size": item["archive_bytes"],
            "digest": "sha256:" + item["archive_sha256"],
            "kind": "source",
        }
    if len(objects) != 16 or len(set(objects)) != 16:
        raise StageError("stage object set differs from the approved sixteen URLs")
    if sum(x["cap"] for x in objects.values()) != stage["archive_response_body_cap_bytes"]:
        raise StageError("stage object caps differ from the admission ledger")
    if stage["archive_response_body_cap_bytes"] + stage["other_response_body_reserve_bytes"] != stage["stage_transfer_cap_bytes"]:
        raise StageError("stage transfer arithmetic differs from the admission ledger")
    if stage["owner_decision"] != "approved exact stage" or (require_admitted and not stage["body_requests_admitted"]):
        raise StageError("owner decision or body admission is missing")
    if _spec_hash(stage, objects) != APPROVED_SPEC_SHA256:
        raise StageError("stage scope differs from the approved URLs or caps")
    if hashlib.sha256(PROPOSAL.read_bytes()).hexdigest() != APPROVED_PROPOSAL_SHA256:
        raise StageError("approved stage proposal changed")
    if any(stage[key] != 0 for key in (
        "guest_disk_growth_cap_bytes", "vm_plus_iso_growth_cap_bytes",
        "paid_host_usd_cap", "metered_api_usd_cap", "native_turn_cap",
    )):
        raise StageError("closed operational caps changed")
    return stage, objects


def _spec_hash(stage: dict[str, Any], objects: dict[str, dict[str, Any]]) -> str:
    caps = {key: stage[key] for key in (
        "archive_response_body_cap_bytes", "other_response_body_reserve_bytes",
        "stage_transfer_cap_bytes", "batch_retained_logical_cap_bytes",
        "new_mac_host_allocation_cap_bytes", "active_seconds_cap", "elapsed_seconds_cap",
    )}
    return hashlib.sha256(_json({"caps": caps, "objects": objects}).encode()).hexdigest()


def _image_allocated(image: Path) -> int:
    if not image.is_file() or image.is_symlink():
        raise StageError("stage image is missing or is a symbolic link")
    return max(image.stat().st_size, image.stat().st_blocks * 512)


def _storage(root: Path, image: Path, stage: dict[str, Any]) -> dict[str, int]:
    if not root.is_dir() or root.is_symlink() or root.stat().st_dev == root.parent.stat().st_dev:
        raise StageError("stage root is not an isolated mounted volume")
    volume = os.statvfs(root)
    total = volume.f_blocks * volume.f_frsize
    if total > stage["batch_retained_logical_cap_bytes"]:
        raise StageError("mounted volume exceeds the retained-data cap")
    allocated = _image_allocated(image)
    if allocated > stage["new_mac_host_allocation_cap_bytes"]:
        raise StageError("stage image exceeds the Mac allocation cap")
    return {"volume_bytes": total, "image_allocated_bytes": allocated}


def _connect(root: Path) -> sqlite3.Connection:
    database = root / "receipt.sqlite3"
    if database.is_symlink() or not database.is_file():
        raise StageError("stage receipt is missing or is a symbolic link")
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=FULL")
    if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
        raise StageError("stage receipt integrity failed")
    return connection


def _meta(connection: sqlite3.Connection) -> dict[str, str]:
    return dict(connection.execute("SELECT key, value FROM meta"))


def _set_meta(connection: sqlite3.Connection, **values: object) -> None:
    connection.executemany(
        "UPDATE meta SET value=? WHERE key=?",
        [(str(value), key) for key, value in values.items()],
    )


def init(root: Path, image: Path) -> dict[str, Any]:
    stage, objects = _manifest(require_admitted=False)
    root = root.resolve(strict=True)
    image = image.resolve(strict=True)
    sizes = _storage(root, image, stage)
    if any(root.iterdir()):
        raise StageError("stage root is not empty")
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    db = root / "receipt.sqlite3"
    connection = sqlite3.connect(db)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.executescript("""
            CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE attempts(
                id TEXT PRIMARY KEY, url TEXT NOT NULL, status TEXT NOT NULL,
                body_bytes INTEGER NOT NULL DEFAULT 0, sha256 TEXT,
                final_url TEXT, http_status INTEGER, error TEXT
            );
            CREATE TABLE reads(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL,
                hop INTEGER NOT NULL, class TEXT NOT NULL, reserved INTEGER NOT NULL,
                actual INTEGER, FOREIGN KEY(id) REFERENCES attempts(id)
            );
            CREATE TABLE responses(
                id TEXT NOT NULL, hop INTEGER NOT NULL, requested_url TEXT NOT NULL,
                http_status INTEGER NOT NULL, location TEXT,
                body_bytes INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(id, hop), FOREIGN KEY(id) REFERENCES attempts(id)
            );
        """)
        now = time.time()
        values = {
            "spec_sha256": _spec_hash(stage, objects),
            "script_sha256": script_hash,
            "tool_version": TOOL_VERSION,
            "root": str(root), "image": str(image),
            "start_epoch": str(now), "active_seconds": "0",
            "archive_body_bytes": "0", "other_body_bytes": "0",
            "halted": "0",
        }
        connection.executemany("INSERT INTO meta VALUES (?,?)", values.items())
        connection.commit()
        (root / "archives").mkdir(mode=0o700)
    finally:
        connection.close()
    return {"status": "initialized", "root": str(root), "image": str(image), **sizes,
            "spec_sha256": values["spec_sha256"], "script_sha256": script_hash}


def _admit(connection: sqlite3.Connection, root: Path, image: Path,
           stage: dict[str, Any], objects: dict[str, dict[str, Any]]) -> dict[str, str]:
    values = _meta(connection)
    expected = {
        "spec_sha256": _spec_hash(stage, objects),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "root": str(root), "image": str(image), "tool_version": TOOL_VERSION,
    }
    if any(values.get(k) != v for k, v in expected.items()):
        raise StageError("stage binding or receipt changed")
    if values.get("halted") != "0" or connection.execute(
        "SELECT COUNT(*) FROM reads WHERE actual IS NULL"
    ).fetchone()[0]:
        raise StageError("stage receipt is halted or has an incomplete read")
    if connection.execute("SELECT COUNT(*) FROM attempts WHERE status='started'").fetchone()[0]:
        raise StageError("stage has an incomplete attempt")
    for kind in ("archive", "other"):
        measured = connection.execute(
            "SELECT COALESCE(SUM(actual),0) FROM reads WHERE class=?", (kind,)
        ).fetchone()[0]
        if measured != int(values[kind + "_body_bytes"]):
            raise StageError("stage byte counter differs from its read receipts")
    attempt_total = connection.execute("SELECT COALESCE(SUM(body_bytes),0) FROM attempts").fetchone()[0]
    response_total = connection.execute("SELECT COALESCE(SUM(body_bytes),0) FROM responses").fetchone()[0]
    if attempt_total != response_total or attempt_total != sum(
        int(values[k + "_body_bytes"]) for k in ("archive", "other")
    ):
        raise StageError("stage response receipts differ from byte counters")
    _storage(root, image, stage)
    if time.time() - float(values["start_epoch"]) >= stage["elapsed_seconds_cap"]:
        raise StageError("stage elapsed-time cap reached")
    if float(values["active_seconds"]) >= stage["active_seconds_cap"]:
        raise StageError("stage active-time cap reached")
    for identifier, state, digest in connection.execute("SELECT id, status, sha256 FROM attempts"):
        if state == "ok":
            archive_path = root / "archives" / (identifier + ".blob")
            if archive_path.is_symlink() or not archive_path.is_file():
                raise StageError("verified archive is missing or changed")
            verified = hashlib.sha256()
            with archive_path.open("rb") as stream:
                while chunk := stream.read(CHUNK):
                    verified.update(chunk)
            if verified.hexdigest() != digest:
                raise StageError("verified archive changed after its receipt")
    return values


def _read_charged(connection: sqlite3.Connection, response: Any, identifier: str,
                  hop: int, kind: str, length: int, stage: dict[str, Any]) -> bytes:
    values = _meta(connection)
    archive = int(values["archive_body_bytes"])
    other = int(values["other_body_bytes"])
    cap = stage["archive_response_body_cap_bytes"] if kind == "archive" else stage["other_response_body_reserve_bytes"]
    used = archive if kind == "archive" else other
    remaining = min(cap - used, stage["stage_transfer_cap_bytes"] - archive - other)
    if remaining <= 0:
        raise StageError("response body budget is exhausted")
    length = min(length, remaining)
    with connection:
        cursor = connection.execute(
            "INSERT INTO reads(id, hop, class, reserved) VALUES (?,?,?,?)",
            (identifier, hop, kind, length),
        )
    # A crash after this reservation leaves a full conservative charge and blocks reuse.
    try:
        chunk = bytes(response.read(length))
    except Exception:
        with connection:
            _set_meta(connection, halted=1,
                      **{kind + "_body_bytes": used + length})
        raise
    with connection:
        connection.execute("UPDATE reads SET actual=? WHERE sequence=?", (len(chunk), cursor.lastrowid))
        _set_meta(connection, **{kind + "_body_bytes": used + len(chunk)})
        connection.execute("UPDATE attempts SET body_bytes=body_bytes+? WHERE id=?", (len(chunk), identifier))
        connection.execute("UPDATE responses SET body_bytes=body_bytes+? WHERE id=? AND hop=?",
                           (len(chunk), identifier, hop))
    return chunk


def _digest_matches(expected: str | None, sha256: str, sha512: str) -> bool:
    if not expected:
        raise StageError("trusted archive digest is missing")
    algorithm, value = expected.split(":", 1)
    if algorithm == "sha256":
        return sha256 == value.lower()
    if algorithm == "sha512":
        if re.fullmatch(r"[0-9a-fA-F]{128}", value):
            return sha512 == value.lower()
        try:
            return bytes.fromhex(sha512) == base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error):
            raise StageError("trusted SHA-512 digest has an invalid encoding") from None
    raise StageError("unsupported trusted archive digest")


def fetch(root: Path, identifier: str) -> dict[str, Any]:
    stage, objects = _manifest()
    if identifier not in objects:
        raise StageError("object is outside the sixteen-URL stage")
    item = objects[identifier]
    if not item["digest"]:
        raise StageError("trusted archive digest is missing")
    root = root.resolve(strict=True)
    connection = _connect(root)
    image = Path(_meta(connection)["image"])
    _admit(connection, root, image, stage, objects)
    if connection.execute("SELECT 1 FROM attempts WHERE id=?", (identifier,)).fetchone():
        raise StageError("one attempt per URL has already been consumed")
    destination = root / "archives" / (identifier + ".blob")
    if destination.exists() or destination.is_symlink():
        raise StageError("archive path already exists")
    with connection:
        connection.execute("INSERT INTO attempts(id,url,status) VALUES (?,?,?)",
                           (identifier, item["url"], "started"))
    started = time.monotonic()
    opener = build_opener(NoRedirect())
    current = item["url"]
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    size = 0
    try:
        for hop in range(MAX_REDIRECTS + 1):
            parsed = urlsplit(current)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise StageError("redirect target is not an acceptable HTTPS URL")
            request = Request(current, headers={"Accept-Encoding": "identity", "User-Agent": TOOL_VERSION})
            try:
                response = opener.open(request, timeout=60)
            except HTTPError as error:
                response = error
            with response:
                status = response.status
                location = response.headers.get("Location")
                with connection:
                    connection.execute(
                        "INSERT INTO responses(id,hop,requested_url,http_status,location) VALUES (?,?,?,?,?)",
                        (identifier, hop, current, status, location),
                    )
                if status in (301, 302, 303, 307, 308):
                    while _read_charged(connection, response, identifier, hop, "other", CHUNK, stage):
                        continue
                    if not location:
                        raise StageError("redirect has no Location")
                    current = urljoin(current, location)
                    continue
                if status != 200:
                    while _read_charged(connection, response, identifier, hop, "other", CHUNK, stage):
                        continue
                    raise StageError(f"archive request returned HTTP {status}")
                with destination.open("xb") as output:
                    while True:
                        remaining = item["cap"] - size
                        if remaining <= 0:
                            # Read one byte only when no budget remains is forbidden.
                            # EOF cannot be proved under this cap; exact-size responses need a matching digest.
                            break
                        length = min(CHUNK, remaining)
                        chunk = _read_charged(connection, response, identifier, hop, "archive", length, stage)
                        if not chunk:
                            break
                        output.write(chunk)
                        output.flush()
                        os.fsync(output.fileno())
                        size += len(chunk)
                        sha256.update(chunk)
                        sha512.update(chunk)
                        _storage(root, image, stage)
                        if time.monotonic() - started + float(_meta(connection)["active_seconds"]) >= stage["active_seconds_cap"]:
                            raise StageError("stage active-time cap reached")
                        if time.time() - float(_meta(connection)["start_epoch"]) >= stage["elapsed_seconds_cap"]:
                            raise StageError("stage elapsed-time cap reached")
                if item["exact_size"] is not None and size != item["exact_size"]:
                    raise StageError("archive length differs from the recorded count")
                if not _digest_matches(item["digest"], sha256.hexdigest(), sha512.hexdigest()):
                    raise StageError("archive digest differs from the trusted value")
                with connection:
                    connection.execute("UPDATE attempts SET status='ok',sha256=?,final_url=?,http_status=? WHERE id=?",
                                       (sha256.hexdigest(), current, status, identifier))
                    _set_meta(connection, active_seconds=float(_meta(connection)["active_seconds"]) + time.monotonic() - started)
                return {"id": identifier, "status": "verified", "bytes": size,
                        "sha256": sha256.hexdigest(), "path": str(destination),
                        "final_url": current, "archive_body_bytes": int(_meta(connection)["archive_body_bytes"]),
                        "other_body_bytes": int(_meta(connection)["other_body_bytes"])}
        raise StageError("redirect limit exceeded")
    except Exception as error:
        with connection:
            connection.execute("UPDATE attempts SET status='failed',error=? WHERE id=?", (str(error), identifier))
            _set_meta(connection, halted=1,
                      active_seconds=float(_meta(connection)["active_seconds"]) + time.monotonic() - started)
        raise
    finally:
        connection.close()


def status(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    connection = _connect(root)
    try:
        stage, objects = _manifest(require_admitted=False)
        values = _meta(connection)
        if values.get("spec_sha256") != _spec_hash(stage, objects):
            raise StageError("stage receipt differs from the approved scope")
        rows = [dict(zip(("id", "status", "body_bytes", "sha256", "error"), row))
                for row in connection.execute("SELECT id,status,body_bytes,sha256,error FROM attempts ORDER BY id")]
        responses = [dict(zip(("id", "hop", "requested_url", "http_status", "location", "body_bytes"), row))
                     for row in connection.execute(
                         "SELECT id,hop,requested_url,http_status,location,body_bytes FROM responses ORDER BY id,hop"
                     )]
        incomplete = connection.execute("SELECT COUNT(*) FROM reads WHERE actual IS NULL").fetchone()[0]
        return {"status": "halted" if values.get("halted") != "0" or incomplete else "open",
                "meta": values, "attempts": rows, "responses": responses, "incomplete_reads": incomplete}
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("init")
    create.add_argument("--root", type=Path, required=True)
    create.add_argument("--image", type=Path, required=True)
    transfer = commands.add_parser("fetch")
    transfer.add_argument("--root", type=Path, required=True)
    transfer.add_argument("--id", required=True)
    report = commands.add_parser("status")
    report.add_argument("--root", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        if arguments.command == "init":
            result = init(arguments.root, arguments.image)
        elif arguments.command == "fetch":
            result = fetch(arguments.root, arguments.id)
        else:
            result = status(arguments.root)
        print(_json(result))
        return 0
    except (StageError, OSError, sqlite3.Error, ValueError) as error:
        print(_json({"status": "failed", "error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
