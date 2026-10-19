# Phase 3B retained archive extraction and storage proposal

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `9a00dcff8c7505d465b44916a28a87b1333eaa1d`.
Status: The proposal is complete. Extraction and execution remain closed.

## Scope and existing custody

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) remains the authority for admission.
The [member report](PHASE-3B-RETAINED-ARCHIVE-MEMBERS-2026-10-19.json) supplies the proposed content bounds.
The original receipt remains halted with its failed `.NET SDK` attempt.
The continuation receipt retains eight successful attempts and no incomplete read.
Both receipts passed read-only SQLite `quick_check` and matched their pinned SHA-256 values.
All 16 archive lengths and SHA-256 values matched the receipts or retained SDK entry.
The fixed image retained its 3,221,225,472-byte logical size and 1,437,798,400-byte allocation.
The mounted volume reported 3,221,184,512 total bytes and 1,784,799,232 free bytes.
No archive, receipt, image, or frozen Phase 3A byte changed during this review.

## One proposed extraction batch

Select these 12 archive IDs: `bun`, `claude-wrapper`, `codex-wrapper`, `cpython`, `dotnet-1`, `dotnet-runtime-net8`, `dotnet-targeting-pack-net8`, `node`, `python-1`, `rtk`, `swift-1`, and `typescript-2`.
These archives contain 12,762 members: 11,019 regular files, 1,740 directories, and three Node symlinks.
Their declared regular content totals 511,667,961 bytes. Their largest regular member is 117,532,552 bytes.
The selected compressed archives already occupy 129,696,586 bytes inside the retained image.
Do not copy archive bodies to a second staging area.

Exclude `swift`, `dotnet-sdk`, `codex-native`, and `claude-native` from this batch.
They remain verified retained data, and their combined regular content is 3,859,951,638 bytes.
The full 4,371,619,599-byte regular content sum cannot fit the fixed image with existing files.
The excluded archives need a separate capacity and safety review before any later extraction.
This batch provides data preparation only. It does not make a runtime or toolchain usable.

The prior inspection counted 1,375,908,527 bytes of existing retained files.
Adding selected regular content gives 1,887,576,488 logical file bytes, before new metadata and link targets.
That leaves 1,333,648,984 bytes under the 3,221,225,472-byte retained logical cap.
The current mounted free space minus selected regular content is 1,273,131,271 bytes.
Keep at least 536,870,912 mounted free bytes during every operation.
This leaves 736,260,359 bytes for filesystem allocation overhead, directory entries, links, manifests, and partial output.
The free-space floor is a stop condition, not a prediction of APFS overhead.
The fixed image also bounds Mac host allocation below its 4,294,967,296-byte cap.
Guest and VM allocation growth stays zero.

## Proposed extractor rules

Before writing, verify each selected archive's pinned length and SHA-256 again.
Preflight every member and its normalized destination against the member report and the frozen source inventory where applicable.
Reject absolute paths, parent components, empty components, backslashes, NUL, duplicates, case-fold collisions, hard links, special members, and sparse files.
Reject ZIP encryption and unsupported compression methods.
Create one new exclusive staging root inside the existing mounted volume.
Use directory-relative operations that refuse symlink parents and refuse replacement of any existing file.
Write regular content once into that root, with an exact per-member declared-size limit and a 511,667,961-byte batch content limit.
Use private file and directory modes. Do not apply archive ownership, extended attributes, or executable mode.
Count every partial file against the batch content limit and mounted free-space floor.
On any failure, stop and retain the partial tree for read-only review.
Do not retry extraction or remove partial output without a separate approved recovery plan.
Publish a bounded manifest only after all selected output names, sizes, and content digests pass readback.
Renaming a completed staging root must not duplicate its data.

For `dotnet-runtime-net8`, accept exactly one leading `./` component and strip it before destination checks.
Treat the tar root entry `.` as a directory marker and create no output for it.
Reject any other `.` component or repeated prefix, and reject every normalized collision before writing.
Apply the same rule to `dotnet-sdk` only in a later separately admitted batch.

The three Node links resolve to regular members inside its archive, with no link chain.
Permit only their exact recorded name and target pairs after every regular file passes readback.
Resolve targets within the staged tree and refuse symlink parents, missing targets, chains, or changed paths.
Create links last with no replacement, then verify their stored target text and resolved destination.
The 37 Swift links resolve inside its archive, including six links with one or two intermediate links.
Swift is excluded. The proposed extractor must refuse a Swift archive in this batch.
A later Swift plan must bind chain resolution, target types, and a larger storage bound.

## Admission and limits

This document grants no extraction authority. A later source implementation needs local synthetic tests and a separate extraction decision.
The later decision must bind the exact extractor hash, selected IDs, output root, quota readback, partial-output policy, and stop rules.
It must also confirm that the fixed image has enough current free space before the first write.
Any changed archive, member report, receipt, or quota readback cancels this proposed batch.
No tool installation, archived tool execution, CMake, Ninja, dependency package, guest action, Linux test, native turn, or evaluation row belongs here.

The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and receipt histories remain unchanged.
No URL was retried and no body request was made.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative conservative charge remain unchanged.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No Jev call ran because the project permits no paid model call in this milestone.
Executable hashes, effective commands, resolved providers, and B1 conformance remain unknown.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

## Checks and limits of evidence

The host was macOS 27.2 arm64 with system Python 3.14.8, project Python 3.12.15, and RTK 0.51.0.
The entry worktree was clean at `9a00dcff8c7505d465b44916a28a87b1333eaa1d`.
All 182 entry-index files matched their recorded sizes and SHA-256 values.
Read-only receipt queries returned `ok`, eight attempts per receipt, and the original failed status.
Streaming SHA-256 checks matched all 16 archive files.
Read-only `stat`, `statvfs`, and tar metadata checks supplied the image, free-space, and link results.
Node's three links resolved directly to regular members.
Swift's 37 links resolved to 35 regular members and two directories; six use link chains.
The member report's selected counts and sums reproduced exactly.
The frozen Phase 3A checker passed without reading sealed contents.

The main commands were `rtk proxy git status --short --branch`, `rtk proxy find /Volumes/CrewshalPhase3BArchiveStage -maxdepth 2 -type f -print`, and `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py`.
Read-only Python scripts checked the input index, SQLite receipts, archive streams, image `stat`, mounted `statvfs`, and tar link targets.
`rtk proxy python3 -m json.tool docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` and `rtk proxy git diff --check` passed.
The final proposal arithmetic check confirmed that all pre-existing admission-ledger fields remained unchanged.

Metadata checks do not prove that extraction will fit or preserve path safety in an untested implementation.
No output allocation, archive extraction, installation, Linux action, or executable conformance was observed.
No installed-package check ran because this planning milestone permits no installation.
The planned free-space floor and fail-closed write rules need implementation and local tests before an extraction decision.
Use the [next prompt](PHASE-3B-RETAINED-EXTRACTION-NEXT-SESSION-2026-10-19.md) and [exact input index](PHASE-3B-RETAINED-EXTRACTION-INPUTS-2026-10-19.json) for that source milestone.
