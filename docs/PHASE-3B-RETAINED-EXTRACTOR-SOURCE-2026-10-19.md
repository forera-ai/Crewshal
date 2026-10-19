# Phase 3B retained extractor source checkpoint

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `2c19bf3ad11b2d3618e0e6eaef3e314ec90f52f1`.
Status: Local source acceptance passed. Retained extraction remains closed.

## Scope and binding

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records the source candidate.
The extractor SHA-256 is `e31dd0a43d1323e85009311ec74cc85898ad49760f8d607326e9bc4b210540ae`.
The test SHA-256 is `40d5e37da9f6ad9b8e3dd9b50dddf34ebb12036121edbc96f44f1fc83b19d79c`.
The source reads the ledger and pinned member report before any admitted retained extraction.
It binds twelve selected IDs, 12,762 members, 511,667,961 regular content bytes, and a 536,870,912-byte free-space floor.
It rejects `swift`, `dotnet-sdk`, `codex-native`, and `claude-native` in this batch.
It accepts one leading `./` only for `dotnet-runtime-net8` and ignores its tar root marker.
It accepts only three recorded Node links after regular file readback.
It checks frozen source inventories for the four selected repository archives.

The extractor checks archive lengths and SHA-256 values before writing.
It compares member metadata against the pinned report and rejects unsafe paths, aliases, hard links, sparse files, and special members.
It refuses ZIP encryption and unsupported compression methods.
It creates one new output root and uses directory-relative operations without symlink parents or file replacement.
It counts partial writes against the content cap and checks mounted free space during writes and directory creation.
It leaves partial output in place after failure and publishes a manifest only after complete tree readback.
The CLI refuses retained extraction while the ledger decision, output root, and exact extractor hash are unset.

## Checks and results

The host was macOS 27.2 arm64. The project Python was 3.12.15, and RTK was 0.51.0.
The entry worktree was clean at the stated revision.
The exact input index verified 185 files by size and SHA-256 before source work.

| Check | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_extract_retained tests.acceptance.test_phase3b_extract_source tests.acceptance.test_phase3b_capped_archive tests.acceptance.test_phase3b_capped_archive_continue` | 41 local tests passed. |
| `rtk proxy .venv/bin/python -m ruff check scripts/phase3b_extract_retained.py tests/acceptance/test_phase3b_extract_retained.py` | Passed. |
| `rtk proxy .venv/bin/python -m ruff format --check scripts/phase3b_extract_retained.py tests/acceptance/test_phase3b_extract_retained.py` | Passed. |
| `rtk proxy .venv/bin/python -m mypy --strict scripts/phase3b_extract_retained.py` | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units retained their frozen digest. |
| `rtk proxy uv build --offline --wheel` | Built `crewshal-0.17.0-py3-none-any.whl` without network access. |
| `rtk proxy .venv/bin/python scripts/phase3b_extract_retained.py /tmp /tmp/out` | Refused because the ledger has no separate exact-hash admission. |
| `rtk proxy test ! -e /Volumes/CrewshalPhase3BArchiveStage/extracted-12-v1` | Passed; the proposed output root did not exist. |

Read-only Python checks verified both receipt SHA-256 values and SQLite `quick_check` results.
Each receipt still has eight attempts. The original `.NET SDK` attempt remains failed.
All 16 retained archive lengths and SHA-256 values matched their receipt or retained SDK entry.
The fixed image remained 3,221,225,472 logical bytes and 1,437,798,400 allocated bytes.
The mounted volume reported 1,784,799,232 free bytes.
The bound policy reproduced twelve IDs, 12,762 members, and 511,667,961 regular content bytes.

An initial combined test command named a nonexistent inspector test module.
The corrected command above passed all 41 relevant tests.
An initial strict mypy check found local type-name reuse. The final strict check passed.
The source code never extracted a retained archive or changed the image, archives, or receipts.

## Costs, limits, and next decision

The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative conservative charge remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No archive body request, Jev call, guest action, Linux test, native turn, provider request, or evaluation row ran.
Guest and VM allocation growth was zero.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, resolved providers, and B1 conformance remain unknown.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

Synthetic tests do not establish filesystem behavior on the retained image during extraction.
The current free-space readback does not guarantee later space or allocation overhead.
No installed-package check ran because this extractor is a standalone script and retained tool installation stays closed.
The [separate decision proposal](PHASE-3B-RETAINED-EXTRACTION-DECISION-2026-10-19.md) binds one attempt and its stop rules.
No retained extraction may start until the owner approves that exact decision and current readback passes.
Use the [next prompt](PHASE-3B-RETAINED-EXTRACTION-DECISION-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-RETAINED-EXTRACTOR-SOURCE-INPUTS-2026-10-19.json) for continuation.
The delivery revision is the commit containing this record.
