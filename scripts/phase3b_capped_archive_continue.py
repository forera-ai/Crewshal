"""Separate, fail-closed transport for the halted Phase 3B archive stage.

This command has no request authority until the admission ledger records a new
owner decision. It never writes the original receipt or an attempted archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import phase3b_capped_archive as original


MANIFEST = original.MANIFEST
CHUNK = original.CHUNK
MAX_REDIRECTS = original.MAX_REDIRECTS
RECEIPT_CAP = 16_777_216
PAGE_SIZE = 4096
MAX_PAGES = (RECEIPT_CAP // 2 - 65_536) // PAGE_SIZE
TOOL_VERSION = "phase3b-capped-archive-continuation-v1"
ATTEMPTED = frozenset(
    ("dotnet-1", "python-1", "swift-1", "typescript-2", "rtk", "cpython", "node", "dotnet-sdk")
)


class ContinuationError(Exception):
    pass


def _safe_error(error: Exception) -> str:
    if isinstance(error, (ContinuationError, original.StageError)):
        return str(error)
    return type(error).__name__


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _ledger() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any], str]:
    stage, objects = original._manifest(require_admitted=False)
    data = json.loads(MANIFEST.read_text())
    plan = data["archive_continuation"]
    ids = plan["unattempted_ids"]
    if len(ids) != 8 or len(set(ids)) != 8 or set(ids) != set(objects) - ATTEMPTED:
        raise ContinuationError("continuation object set differs from the original scope")
    if sum(objects[name]["cap"] for name in ids) != plan["unattempted_object_caps_total_bytes"]:
        raise ContinuationError("continuation caps differ from the admission ledger")
    if plan["original_scope_sha256"] != original._spec_hash(stage, objects):
        raise ContinuationError("original scope binding changed")
    if plan["original_receipt_halted"] is not True or plan["original_failed_id"] != "dotnet-sdk":
        raise ContinuationError("original failure binding changed")
    if (
        plan["prior_full_charge_bytes"] != 8_589_934_592
        or plan["current_stage_conservative_charge_bytes"] != 311_183_922
        or plan["original_stage_transfer_cap_bytes"] != 2_232_012_187
        or plan["new_receipt_logical_cap_bytes"] != RECEIPT_CAP
    ):
        raise ContinuationError("continuation accounting changed")
    if any(
        stage[key] != 0
        for key in (
            "guest_disk_growth_cap_bytes",
            "vm_plus_iso_growth_cap_bytes",
            "paid_host_usd_cap",
            "metered_api_usd_cap",
            "native_turn_cap",
        )
    ):
        raise ContinuationError("closed operational caps changed")
    return stage, objects, plan, _hash(MANIFEST)


def _authority(plan: dict[str, Any]) -> None:
    if plan.get("owner_decision") != "approved exact halted archive continuation":
        raise ContinuationError("separate owner decision is missing")
    if plan.get("body_requests_admitted") is not True:
        raise ContinuationError("continuation body requests are closed")
    if plan.get("transport_script_sha256") != _hash(Path(__file__)):
        raise ContinuationError("transport source differs from reviewed hash")


def _original(
    root: Path, receipt: Path, plan: dict[str, Any], objects: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    if receipt != root / "receipt.sqlite3" or receipt.is_symlink() or not receipt.is_file():
        raise ContinuationError("original receipt path changed")
    if _hash(receipt) != plan["original_receipt_sha256"]:
        raise ContinuationError("original receipt SHA-256 changed")
    connection = sqlite3.connect(f"file:{receipt}?mode=ro&immutable=1", uri=True)
    try:
        if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise ContinuationError("original receipt integrity failed")
        meta = dict(connection.execute("SELECT key,value FROM meta"))
        if (
            meta.get("spec_sha256") != plan["original_scope_sha256"]
            or meta.get("script_sha256")
            != json.loads(MANIFEST.read_text())["archive_evidence_stage"][
                "original_transport_script_sha256"
            ]
            or meta.get("halted") != "1"
            or meta.get("root") != str(root)
        ):
            raise ContinuationError("original receipt binding changed")
        attempts = list(connection.execute("SELECT id,status,body_bytes,sha256 FROM attempts"))
        if {row[0] for row in attempts} != ATTEMPTED or len(attempts) != 8:
            raise ContinuationError("original attempt set changed")
        for identifier, status, count, digest in attempts:
            if status != ("failed" if identifier == "dotnet-sdk" else "ok"):
                raise ContinuationError("original attempt status changed")
            archive = root / "archives" / f"{identifier}.blob"
            if archive.is_symlink() or not archive.is_file() or archive.stat().st_size != count:
                raise ContinuationError("retained archive changed")
            actual = _hash(archive)
            if identifier == "dotnet-sdk":
                if actual != plan["retained_dotnet_sdk"]["sha256"]:
                    raise ContinuationError("retained SDK hash changed")
                if not original._digest_matches(
                    objects[identifier]["digest"], actual, _sha512(archive)
                ):
                    raise ContinuationError("retained SDK digest changed")
            elif actual != digest:
                raise ContinuationError("retained verified archive changed")
        if connection.execute("SELECT COUNT(*) FROM reads WHERE actual IS NULL").fetchone()[0]:
            raise ContinuationError("original receipt has an incomplete read")
        measured = {
            kind: count
            for kind, count in connection.execute(
                "SELECT class,COALESCE(SUM(actual),0) FROM reads GROUP BY class"
            )
        }
        if measured.get("archive", 0) != int(meta["archive_body_bytes"]) or measured.get(
            "other", 0
        ) != int(meta["other_body_bytes"]):
            raise ContinuationError("original byte counters changed")
        recorded = json.loads(MANIFEST.read_text())["archive_evidence_stage"]
        if (
            sum(row[2] for row in attempts) != sum(measured.values())
            or int(meta["archive_body_bytes"]) != recorded["archive_body_bytes_retrieved"]
        ):
            raise ContinuationError("original stage accounting changed")
        return {"meta": meta, "attempts": attempts}
    finally:
        connection.close()


def _sha512(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _connect(root: Path) -> sqlite3.Connection:
    path = root / "continuation.sqlite3"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_PAGES * PAGE_SIZE:
        raise ContinuationError("continuation receipt is absent or exceeds its cap")
    if any((root / (path.name + suffix)).exists() for suffix in ("-journal", "-wal", "-shm")):
        raise ContinuationError("continuation receipt has an unfinished journal")
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=FULL")
    if connection.execute("PRAGMA page_size").fetchone()[0] != PAGE_SIZE:
        raise ContinuationError("continuation receipt page size changed")
    connection.execute(f"PRAGMA max_page_count={MAX_PAGES}")
    if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
        raise ContinuationError("continuation receipt integrity failed")
    return connection


def _meta(connection: sqlite3.Connection) -> dict[str, str]:
    return dict(connection.execute("SELECT key,value FROM meta"))


def _set(connection: sqlite3.Connection, **values: object) -> None:
    connection.executemany(
        "UPDATE meta SET value=? WHERE key=?", [(str(value), key) for key, value in values.items()]
    )


def _storage(root: Path, image: Path, stage: dict[str, Any]) -> None:
    original._storage(root, image, stage)
    receipt = root / "continuation.sqlite3"
    footprint = sum(
        path.stat().st_size
        for path in (
            receipt,
            *(root / (receipt.name + suffix) for suffix in ("-journal", "-wal", "-shm")),
        )
        if path.exists()
    )
    if footprint > RECEIPT_CAP:
        raise ContinuationError("continuation receipt cap reached")


def _reserve_space(root: Path, required: int) -> None:
    volume = os.statvfs(root)
    if volume.f_bavail * volume.f_frsize < required:
        raise ContinuationError("stage volume lacks reserved archive and receipt space")


def _preflight(
    connection: sqlite3.Connection,
    root: Path,
    stage: dict[str, Any],
    objects: dict[str, dict[str, Any]],
    plan: dict[str, Any],
    manifest_hash: str,
    receipt: Path,
) -> tuple[dict[str, str], dict[str, Any]]:
    _authority(plan)
    values = _meta(connection)
    expected = {
        "manifest_sha256": manifest_hash,
        "original_receipt_sha256": plan["original_receipt_sha256"],
        "original_scope_sha256": plan["original_scope_sha256"],
        "script_sha256": _hash(Path(__file__)),
        "root": str(root),
        "ids_json": json.dumps(plan["unattempted_ids"], separators=(",", ":")),
        "tool_version": TOOL_VERSION,
    }
    if any(values.get(key) != value for key, value in expected.items()):
        raise ContinuationError("continuation receipt binding changed")
    if values.get("halted") != "0":
        raise ContinuationError("continuation receipt is halted")
    if connection.execute("SELECT COUNT(*) FROM reads WHERE actual IS NULL").fetchone()[0]:
        raise ContinuationError("continuation has an incomplete read reservation")
    if connection.execute("SELECT COUNT(*) FROM attempts WHERE status='started'").fetchone()[0]:
        raise ContinuationError("continuation has an incomplete attempt")
    original_state = _original(root, receipt, plan, objects)
    if values.get("image") != original_state["meta"]["image"]:
        raise ContinuationError("continuation image binding changed")
    _storage(root, Path(values["image"]), stage)
    receipt_remaining = RECEIPT_CAP - (root / "continuation.sqlite3").stat().st_size
    measured = {
        kind: count
        for kind, count in connection.execute(
            "SELECT class,COALESCE(SUM(actual),0) FROM reads GROUP BY class"
        )
    }
    for kind in ("archive", "other"):
        if measured.get(kind, 0) != int(values[f"{kind}_body_bytes"]):
            raise ContinuationError("continuation read counters changed")
    if connection.execute("SELECT COALESCE(SUM(body_bytes),0) FROM attempts").fetchone()[0] != sum(
        measured.values()
    ):
        raise ContinuationError("continuation attempt counters changed")
    if connection.execute("SELECT COALESCE(SUM(body_bytes),0) FROM responses").fetchone()[0] != sum(
        measured.values()
    ):
        raise ContinuationError("continuation response counters changed")
    attempt_rows = list(connection.execute("SELECT id,status,sha256 FROM attempts"))
    ids = {row[0] for row in attempt_rows}
    if not ids.issubset(set(plan["unattempted_ids"])):
        raise ContinuationError("continuation contains an attempted or unknown ID")
    remaining_caps = sum(
        objects[name]["cap"] for name in plan["unattempted_ids"] if name not in ids
    )
    _reserve_space(root, remaining_caps + receipt_remaining)
    for identifier, state, digest in attempt_rows:
        if state != "ok":
            raise ContinuationError("continuation contains a failed attempt")
        archive = root / "archives" / f"{identifier}.blob"
        if archive.is_symlink() or not archive.is_file() or _hash(archive) != digest:
            raise ContinuationError("continuation verified archive changed")
    if (
        float(original_state["meta"]["active_seconds"]) + float(values["active_seconds"])
        >= stage["active_seconds_cap"]
    ):
        raise ContinuationError("cumulative active-time cap reached")
    if time.time() - float(values["start_epoch"]) >= stage["elapsed_seconds_cap"]:
        raise ContinuationError("continuation elapsed-time cap reached")
    return values, original_state


def prepare(root: Path, image: Path, receipt: Path) -> dict[str, Any]:
    stage, objects, plan, manifest_hash = _ledger()
    _authority(plan)
    root = root.resolve(strict=True)
    image = image.resolve(strict=True)
    if receipt.is_symlink():
        raise ContinuationError("original receipt path changed")
    receipt = receipt.resolve(strict=True)
    original_state = _original(root, receipt, plan, objects)
    if image != Path(original_state["meta"]["image"]):
        raise ContinuationError("stage image differs from original receipt")
    _storage(root, image, stage)
    _reserve_space(
        root, sum(objects[name]["cap"] for name in plan["unattempted_ids"]) + RECEIPT_CAP
    )
    db = root / "continuation.sqlite3"
    if db.exists() or db.is_symlink():
        raise ContinuationError("continuation receipt already exists")
    if time.time() - float(original_state["meta"]["start_epoch"]) < 0:
        raise ContinuationError("original clock origin is invalid")
    connection = sqlite3.connect(db)
    try:
        connection.execute(f"PRAGMA page_size={PAGE_SIZE}")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute(f"PRAGMA max_page_count={MAX_PAGES}")
        connection.executescript("""
            CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE attempts(id TEXT PRIMARY KEY,status TEXT NOT NULL,
                body_bytes INTEGER NOT NULL DEFAULT 0,sha256 TEXT,error TEXT);
            CREATE TABLE responses(id TEXT NOT NULL,hop INTEGER NOT NULL,
                url_sha256 TEXT NOT NULL,http_status INTEGER NOT NULL,
                location_sha256 TEXT,body_bytes INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(id,hop));
            CREATE TABLE reads(sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL,hop INTEGER NOT NULL,class TEXT NOT NULL,
                reserved INTEGER NOT NULL,actual INTEGER);
        """)
        values = {
            "manifest_sha256": manifest_hash,
            "original_receipt_sha256": plan["original_receipt_sha256"],
            "original_scope_sha256": plan["original_scope_sha256"],
            "script_sha256": _hash(Path(__file__)),
            "tool_version": TOOL_VERSION,
            "root": str(root),
            "image": str(image),
            "ids_json": json.dumps(plan["unattempted_ids"], separators=(",", ":")),
            "start_epoch": str(time.time()),
            "active_seconds": "0",
            "archive_body_bytes": "0",
            "other_body_bytes": "0",
            "halted": "0",
        }
        connection.executemany("INSERT INTO meta VALUES (?,?)", values.items())
        connection.commit()
    finally:
        connection.close()
    return {
        "status": "prepared",
        "receipt": str(db),
        "script_sha256": values["script_sha256"],
        "manifest_sha256": manifest_hash,
    }


def _read(
    connection: sqlite3.Connection,
    response: Any,
    identifier: str,
    hop: int,
    kind: str,
    requested: int,
    stage: dict[str, Any],
    item_cap: int,
    original_bytes: int,
    root: Path,
    image: Path,
) -> bytes:
    values = _meta(connection)
    archive = int(values["archive_body_bytes"])
    other = int(values["other_body_bytes"])
    if kind == "archive":
        item_used = connection.execute(
            "SELECT COALESCE(SUM(actual),0) FROM reads WHERE id=? AND class='archive'",
            (identifier,),
        ).fetchone()[0]
        remaining = min(
            item_cap - item_used,
            stage["archive_response_body_cap_bytes"] - original_bytes - archive,
            stage["stage_transfer_cap_bytes"]
            - original_bytes
            - archive
            - stage["other_response_body_reserve_bytes"],
        )
    else:
        remaining = stage["other_response_body_reserve_bytes"] - other
    if remaining <= 0:
        raise ContinuationError("response body budget is exhausted")
    space = os.statvfs(root)
    free = space.f_bavail * space.f_frsize
    if free <= 0:
        raise ContinuationError("stage volume has no free space")
    length = min(requested, remaining, free)
    if length <= 0:
        raise ContinuationError("response body or storage budget is exhausted")
    _storage(root, image, stage)
    with connection:
        cursor = connection.execute(
            "INSERT INTO reads(id,hop,class,reserved) VALUES (?,?,?,?)",
            (identifier, hop, kind, length),
        )
    # Missing actual marks a crash reservation. A later request always refuses it.
    try:
        chunk = bytes(response.read(length))
    except Exception:
        with connection:
            _set(
                connection,
                halted=1,
                **{kind + "_body_bytes": (archive if kind == "archive" else other) + length},
            )
        raise
    with connection:
        connection.execute(
            "UPDATE reads SET actual=? WHERE sequence=?", (len(chunk), cursor.lastrowid)
        )
        _set(
            connection,
            **{kind + "_body_bytes": (archive if kind == "archive" else other) + len(chunk)},
        )
        connection.execute(
            "UPDATE attempts SET body_bytes=body_bytes+? WHERE id=?", (len(chunk), identifier)
        )
        connection.execute(
            "UPDATE responses SET body_bytes=body_bytes+? WHERE id=? AND hop=?",
            (len(chunk), identifier, hop),
        )
    return chunk


def _swift_key_check(plan: dict[str, Any], signature: Path, key: Path) -> None:
    binding = plan["digest_inputs"]["swift"]
    if (
        _hash(signature) != binding["signature_sha256"]
        or _hash(key) != binding["signer_key_sha256"]
    ):
        raise ContinuationError("pinned Swift signature or key changed")
    if shutil.which("gpg") is None:
        raise ContinuationError("GPG is unavailable for Swift signature verification")
    with tempfile.TemporaryDirectory() as home:
        os.chmod(home, 0o700)
        imported = subprocess.run(
            ["gpg", "--batch", "--homedir", home, "--import", str(key)],
            capture_output=True,
            check=False,
        )
        if imported.returncode:
            raise ContinuationError("Swift signing key import failed")
        fingerprint = subprocess.run(
            ["gpg", "--batch", "--homedir", home, "--with-colons", "--fingerprint"],
            capture_output=True,
            check=False,
        )
        if (
            fingerprint.returncode
            or binding["signer_fingerprint"].encode() not in fingerprint.stdout
        ):
            raise ContinuationError("Swift signing key fingerprint changed")


def _verify_swift(path: Path, plan: dict[str, Any], signature: Path, key: Path) -> None:
    _swift_key_check(plan, signature, key)
    with tempfile.TemporaryDirectory() as home:
        os.chmod(home, 0o700)
        imported = subprocess.run(
            ["gpg", "--batch", "--homedir", home, "--import", str(key)],
            capture_output=True,
            check=False,
        )
        if imported.returncode:
            raise ContinuationError("Swift signing key import failed")
        verified = subprocess.run(
            ["gpg", "--batch", "--homedir", home, "--verify", str(signature), str(path)],
            capture_output=True,
            check=False,
        )
        if verified.returncode:
            raise ContinuationError("Swift archive signature verification failed")


def fetch(
    root: Path,
    identifier: str,
    *,
    swift_signature: Path | None = None,
    swift_key: Path | None = None,
) -> dict[str, Any]:
    stage, objects, plan, manifest_hash = _ledger()
    _authority(plan)
    if identifier in ATTEMPTED or identifier not in plan["unattempted_ids"]:
        raise ContinuationError("ID was attempted or is outside the continuation")
    item = objects[identifier]
    expected = item["digest"]
    if identifier == "bun":
        expected = "sha256:" + plan["digest_inputs"]["bun"]["sha256"]
    if identifier == "dotnet-targeting-pack-net8":
        expected = "sha512:" + plan["digest_inputs"][identifier]["sha512_base64"]
    if identifier == "swift":
        if (
            plan.get("swift_signature_first_approved") is not True
            or swift_signature is None
            or swift_key is None
        ):
            raise ContinuationError("Swift signature-first approval and pinned inputs are required")
        _swift_key_check(plan, swift_signature, swift_key)
    elif not expected:
        raise ContinuationError("trusted archive digest is missing")
    root = root.resolve(strict=True)
    receipt = root / "receipt.sqlite3"
    connection = _connect(root)
    try:
        values, old = _preflight(connection, root, stage, objects, plan, manifest_hash, receipt)
        if connection.execute("SELECT 1 FROM attempts WHERE id=?", (identifier,)).fetchone():
            raise ContinuationError("one attempt per continuation URL has already been consumed")
        destination = root / "archives" / f"{identifier}.blob"
        if destination.exists() or destination.is_symlink():
            raise ContinuationError("archive path already exists")
        image = Path(values["image"])
        with connection:
            connection.execute(
                "INSERT INTO attempts(id,status) VALUES (?,?)", (identifier, "started")
            )
        started = time.monotonic()
        opener = build_opener(original.NoRedirect())
        current = item["url"]
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        size = 0
        try:
            for hop in range(MAX_REDIRECTS + 1):
                parsed = urlsplit(current)
                if (
                    parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.username
                    or parsed.password
                ):
                    raise ContinuationError("redirect target is not an acceptable HTTPS URL")
                request = Request(
                    current, headers={"Accept-Encoding": "identity", "User-Agent": TOOL_VERSION}
                )
                try:
                    response = opener.open(request, timeout=60)
                except HTTPError as error:
                    response = error
                with response:
                    code = response.status
                    location = response.headers.get("Location")
                    with connection:
                        connection.execute(
                            "INSERT INTO responses VALUES (?,?,?,?,?,0)",
                            (
                                identifier,
                                hop,
                                hashlib.sha256(current.encode()).hexdigest(),
                                code,
                                hashlib.sha256(location.encode()).hexdigest() if location else None,
                            ),
                        )
                    if code in (301, 302, 303, 307, 308) or code != 200:
                        while _read(
                            connection,
                            response,
                            identifier,
                            hop,
                            "other",
                            CHUNK,
                            stage,
                            item["cap"],
                            int(old["meta"]["archive_body_bytes"]),
                            root,
                            image,
                        ):
                            continue
                        if code not in (301, 302, 303, 307, 308):
                            raise ContinuationError(f"archive request returned HTTP {code}")
                        if not location:
                            raise ContinuationError("redirect has no Location")
                        current = urljoin(current, location)
                        continue
                    with destination.open("xb") as output:
                        while size < item["cap"]:
                            chunk = _read(
                                connection,
                                response,
                                identifier,
                                hop,
                                "archive",
                                min(CHUNK, item["cap"] - size),
                                stage,
                                item["cap"],
                                int(old["meta"]["archive_body_bytes"]),
                                root,
                                image,
                            )
                            if not chunk:
                                break
                            output.write(chunk)
                            output.flush()
                            os.fsync(output.fileno())
                            size += len(chunk)
                            sha256.update(chunk)
                            sha512.update(chunk)
                            _storage(root, image, stage)
                            if (
                                float(old["meta"]["active_seconds"])
                                + float(values["active_seconds"])
                                + time.monotonic()
                                - started
                                >= stage["active_seconds_cap"]
                            ):
                                raise ContinuationError("cumulative active-time cap reached")
                            if (
                                time.time() - float(values["start_epoch"])
                                >= stage["elapsed_seconds_cap"]
                            ):
                                raise ContinuationError("continuation elapsed-time cap reached")
                    if item["exact_size"] is not None and size != item["exact_size"]:
                        raise ContinuationError("archive length differs from recorded count")
                    if identifier == "swift":
                        assert swift_signature is not None and swift_key is not None
                        _verify_swift(destination, plan, swift_signature, swift_key)
                    elif not original._digest_matches(
                        expected, sha256.hexdigest(), sha512.hexdigest()
                    ):
                        raise ContinuationError("archive digest differs from trusted value")
                    with connection:
                        connection.execute(
                            "UPDATE attempts SET status='ok',sha256=? WHERE id=?",
                            (sha256.hexdigest(), identifier),
                        )
                        _set(
                            connection,
                            active_seconds=float(values["active_seconds"])
                            + time.monotonic()
                            - started,
                        )
                    return {
                        "id": identifier,
                        "status": "verified",
                        "bytes": size,
                        "sha256": sha256.hexdigest(),
                        "archive_body_bytes": int(_meta(connection)["archive_body_bytes"]),
                        "other_body_bytes": int(_meta(connection)["other_body_bytes"]),
                    }
            raise ContinuationError("redirect limit exceeded")
        except Exception as error:
            with connection:
                connection.execute(
                    "UPDATE attempts SET status='failed',error=? WHERE id=?",
                    (_safe_error(error), identifier),
                )
                _set(
                    connection,
                    halted=1,
                    active_seconds=float(values["active_seconds"]) + time.monotonic() - started,
                )
            raise
    finally:
        connection.close()


def status(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    connection = _connect(root)
    try:
        values = _meta(connection)
        return {
            "status": "halted" if values.get("halted") != "0" else "prepared",
            "meta": values,
            "attempts": [
                dict(zip(("id", "status", "body_bytes", "sha256", "error"), row))
                for row in connection.execute(
                    "SELECT id,status,body_bytes,sha256,error FROM attempts ORDER BY rowid"
                )
            ],
        }
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    preparation = sub.add_parser("prepare")
    preparation.add_argument("--root", type=Path, required=True)
    preparation.add_argument("--image", type=Path, required=True)
    preparation.add_argument("--original-receipt", type=Path, required=True)
    state = sub.add_parser("status")
    state.add_argument("--root", type=Path, required=True)
    retrieval = sub.add_parser("fetch")
    retrieval.add_argument("--root", type=Path, required=True)
    retrieval.add_argument("--id", required=True)
    retrieval.add_argument("--swift-signature", type=Path)
    retrieval.add_argument("--swift-key", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.root, args.image, args.original_receipt)
        elif args.command == "status":
            result = status(args.root)
        else:
            result = fetch(
                args.root, args.id, swift_signature=args.swift_signature, swift_key=args.swift_key
            )
    except Exception as error:
        print(f"continuation refused: {_safe_error(error)}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
