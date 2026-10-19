# Phase 3B remaining archive extractor source checkpoint

Date: 2026-10-20. Branch: `codex/phase1-architecture`.
Entry revision: `e5a73c5c125476182910b938b0571dbe0c8039c9`.
Status: Local source acceptance passed. New image creation and extraction remain closed.

## Scope and evidence

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) binds four remaining archive IDs.
It binds 7,216 members, 3,859,951,638 regular content bytes, and a 536,870,912-byte mounted free-space floor.
It binds a proposed 6,442,450,944-byte image and a 7,516,192,768-byte allocated host cap.
The extractor SHA-256 is `4043988a069e2c9436eb990271b7ee634610a309f77637d30d246ae80a6e7995`.
The new test SHA-256 is `fd28da7e0fb484e9f81b4a312a9c425d96296c60969a4d84a850b1f651927124`.
The prior retained extractor file and its recorded SHA-256 did not change.

The new extractor binds the exact archive lengths, hashes, and member report.
It accepts one leading `./` only for the `.NET SDK` tarball and ignores its root marker.
It accepts only 37 recorded Swift links after regular file readback.
Swift links may form bounded chains or end at a directory.
It rejects escaping or cyclic links, unsafe paths, aliases, sparse files, hard links, and special members.
It creates a private output root without replacement and retains partial output after failure.
It checks content, mounted free space, host free space, and image allocation during writes.
It verifies output files and links before publishing its manifest.
Its CLI requires an exact owner decision, source hash, output path, and two image mount identities.

Read-only preflight passed for `claude-native`, `codex-native`, `dotnet-sdk`, and `swift`.
An independent Swift link audit resolved all 37 links without an escape or cycle.
Thirty-five links resolve to regular files, and two resolve to directories.
No archived tool executed.

## Commands and results

The host was macOS 27.2 arm64. The project Python was 3.12.15, and RTK was 0.51.0.
The entry worktree was clean and matched its remote branch.
All 194 indexed entry files matched their recorded sizes and SHA-256 values.

| Check | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_extract_remaining tests.acceptance.test_phase3b_extract_retained tests.acceptance.test_phase3b_extract_source tests.acceptance.test_phase3b_capped_archive tests.acceptance.test_phase3b_capped_archive_continue` | 52 local tests passed. |
| `rtk proxy .venv/bin/python -m ruff check scripts/phase3b_extract_remaining.py tests/acceptance/test_phase3b_extract_remaining.py tests/acceptance/test_phase3b_extract_retained.py` | Passed. |
| `rtk proxy .venv/bin/python -m ruff format --check scripts/phase3b_extract_remaining.py tests/acceptance/test_phase3b_extract_remaining.py tests/acceptance/test_phase3b_extract_retained.py` | Passed. |
| `rtk proxy .venv/bin/python -m mypy --strict scripts/phase3b_extract_remaining.py` | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units kept their frozen digest. |
| `rtk proxy uv build --offline --wheel` | Built `crewshal-0.18.0-py3-none-any.whl` without network access. |
| Read-only receipt, archive, fixed-image, and old manifest checks | Both receipts, all 16 archives, the image, and the old output manifest matched. |

The first Swift link audit required regular final targets and flagged two valid directory links.
The corrected audit resolved all 37 links and reported zero issues.
An existing test still expected the completed first extraction decision to be null.
The corrected test asserts one completed attempt and closed further admission. All 52 tests passed.

## Costs, limits, and next decision

The new image and mount paths did not exist at this checkpoint.
The host reported 147,892,584,448 free bytes. The old mounted volume reported 1,274,007,552 free bytes.
The fixed image retained 3,221,225,472 logical bytes and 1,929,318,400 allocated bytes.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative charge remain intact.
No archive body request, URL retry, retained extraction, installation, guest, Linux test, native turn, provider request, or evaluation row ran.
Guest and VM growth was zero. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.

Synthetic tests and read-only preflight do not prove success on a new mounted image.
No installed-package test ran because this extractor is a standalone script and archived tool installation stays closed.
The [separate proposal](PHASE-3B-REMAINING-ARCHIVE-PROPOSAL-2026-10-20.md) binds one image creation and one extraction attempt.
Do not create the image or extract until the owner approves that exact proposal.
Installation, archived tool execution, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The delivery revision is the commit containing this record.
