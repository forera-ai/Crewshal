# Phase 3B retained archive member inspection

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `00e061ad161063470054c67efa87feaf2273b835`.
Status: The bounded read-only member inspection is complete. Extraction and execution remain closed.

## Custody and method

All 178 entry-index files matched their recorded byte counts and SHA-256 values before inspection.
The original and continuation receipts matched their recorded SHA-256 values.
Read-only SQLite checks returned `ok`, eight attempts per receipt, and zero incomplete reads.
The original `.NET SDK` attempt remains failed. The continuation receipt records eight successful attempts.
All 16 retained archive lengths and SHA-256 values matched the receipts or the retained SDK ledger entry.
The Swift signature and key files retained their pinned SHA-256 values.
This session did not repeat GPG verification; the completion record contains the prior independent signature checks.

The image remained mounted at `/Volumes/CrewshalPhase3BArchiveStage`.
Its logical size was 3,221,225,472 bytes, and its allocated size was 1,437,798,400 bytes.
The mounted volume reported 3,221,184,512 total bytes and 1,784,799,232 free bytes.
No inspection command wrote to the image, archives, receipts, source files, or Swift verification inputs.

`scripts/phase3b_inspect_archive_members.py` streamed tar metadata and read ZIP central directories.
It did not extract member data or launch any retained executable.
It capped each archive at 200,000 members and 15,000,000,000 regular content bytes.
The [machine-readable report](PHASE-3B-RETAINED-ARCHIVE-MEMBERS-2026-10-19.json) records counts, examples, every link, and member metadata digests.
Its SHA-256 is `da7c20e5be010d317e02a04e9a00a1279fc854a0244a805b7021c855da5c04d5`.
The single [admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) references that report.

## Member counts and content bounds

The final column sums declared logical sizes of regular files in each archive.
It bounds regular file content for an extractor that rejects links and special members.
It does not bound directory metadata, allocation blocks, caches, or installed dependencies.

| Archive ID | Members | Regular | Directories | Links | Regular content upper bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| `bun` | 2 | 1 | 1 | 0 | 92,743,312 |
| `claude-native` | 4 | 4 | 0 | 0 | 234,021,698 |
| `claude-wrapper` | 7 | 7 | 0 | 0 | 184,119 |
| `codex-native` | 46 | 46 | 0 | 0 | 401,682,212 |
| `codex-wrapper` | 3 | 3 | 0 | 0 | 13,206 |
| `cpython` | 4,935 | 4,578 | 357 | 0 | 101,715,479 |
| `dotnet-1` | 348 | 281 | 67 | 0 | 1,152,465 |
| `dotnet-runtime-net8` | 195 | 188 | 7 | 0 | 78,708,249 |
| `dotnet-sdk` | 5,439 | 4,623 | 816 | 0 | 593,859,529 |
| `dotnet-targeting-pack-net8` | 351 | 351 | 0 | 0 | 39,366,330 |
| `node` | 5,929 | 4,808 | 1,118 | 3 | 182,036,840 |
| `python-1` | 173 | 147 | 26 | 0 | 947,826 |
| `rtk` | 1 | 1 | 0 | 0 | 9,333,072 |
| `swift-1` | 236 | 194 | 42 | 0 | 1,549,662 |
| `swift` | 1,727 | 1,535 | 155 | 37 | 2,630,388,199 |
| `typescript-2` | 582 | 460 | 122 | 0 | 3,917,401 |
| **Total** | **19,978** | **17,227** | **2,711** | **40** | **4,371,619,599** |

All 5,634 `.NET SDK` and `.NET runtime` members contain a `.` path component.
Examples include `.` and `./host/fxr`; the strict source extractor would reject these names.
No member name had an absolute path, parent component, empty component, backslash, or NUL.
No archive had duplicate raw or normalized names, case-fold collisions, hard links, or special members.
The ZIP archives had no encrypted members or unsupported compression method.
The tar archives reported no sparse members.

Node contains three symlinks. Swift contains 37 symlinks.
All 40 lexical link targets resolve inside their archive root, but no link is approved for extraction.
The report lists every link name and target. It does not prove safe link resolution after filesystem changes.
No tool archive has a complete approved extraction policy or filesystem allocation bound.

The 4,371,619,599-byte regular content sum exceeds the 3,221,225,472-byte retained-data cap.
Adding that sum to the current 1,375,908,527 retained file bytes gives 5,747,528,126 bytes.
Swift regular content alone exceeds current mounted free space.
Any extraction plan must select a bounded subset and account for filesystem overhead.

## Commands, results, and limits

The host was macOS 27.2 arm64 with CPython 3.12.15 and RTK 0.51.0.
The inspection used local Python standard-library `tarfile` and `zipfile` readers.

| Check | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | Clean entry worktree on the current branch. |
| Size and SHA-256 check of `PHASE-3B-CAPPED-ARCHIVE-COMPLETE-INPUTS-2026-10-19.json` | 178 files passed. |
| Read-only SQLite `PRAGMA quick_check` and attempt queries | Both receipts returned `ok`; the original remains failed and halted. |
| Streaming SHA-256 of 16 archives and both receipts | All expected lengths and digests matched. |
| `rtk proxy diskutil info /Volumes/CrewshalPhase3BArchiveStage` and image `stat` | Fixed image and mounted-volume sizes matched the prior completion record. |
| `rtk proxy .venv/bin/python scripts/phase3b_inspect_archive_members.py /Volumes/CrewshalPhase3BArchiveStage/archives` | 16 archives and 19,978 members inspected; no extraction. |
| Independent Python metadata scan | Member counts, regular byte sums, and metadata digests matched the report. |
| Synthetic tar and ZIP metadata fixtures | Unsafe paths, duplicate names, escaping links, special members, and byte counts passed. |
| Ruff lint, Ruff format, and strict mypy on the inspector | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units retained the frozen digest. |
| `rtk proxy uv build --offline --wheel` | Built version `0.16.2`. |
| Fresh offline wheel install with dependencies and installed CLI help | Passed. |
| `rtk proxy git diff --check` | Passed. |
| Post-inspection archive, receipt, and image readback | All 16 archive digests, both receipt digests, and image size and allocation matched. |

An initial isolated `--no-deps` install could not start the CLI because `pydantic` was absent.
An offline install of the wheel with dependencies fixed that check.

No archive body request, URL retry, extraction, installation, archived tool execution, or guest action ran.
No CMake, Ninja, dependency package, Linux test, native turn, provider request, or evaluation row ran.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
The original 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative charge remain intact.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
Guest and VM allocation growth remained zero.
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain null or unknown.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

The delivery revision is the commit containing this record.
Use the linked next prompt and exact input index after publication.
