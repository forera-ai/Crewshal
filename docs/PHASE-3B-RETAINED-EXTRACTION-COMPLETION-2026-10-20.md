# Phase 3B retained extraction completion

Date: 2026-10-20. Branch: `codex/phase1-architecture`.
Entry revision: `a3f48ead823ff2fe3a1b04a409753be7e380e849`.
The owner approved the exact one-attempt decision in the current Codex chat on 2026-10-19.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records that decision and closes further extraction.

## Action and result

The host was macOS 27.2 arm64. The project Python was 3.12.15, and RTK was 0.51.0.
The entry worktree was clean and matched its remote branch.
All 191 indexed source inputs matched their recorded sizes and SHA-256 values.
The extractor SHA-256 matched `e31dd0a43d1323e85009311ec74cc85898ad49760f8d607326e9bc4b210540ae`.
Both receipts passed pinned SHA-256 and read-only SQLite `quick_check` checks before the first write.
Each receipt retained eight attempts. The original `.NET SDK` attempt remained failed.
All 16 archive lengths and hashes matched their recorded values before the first write.
The fixed image measured 3,221,225,472 logical bytes, and the mounted volume had 1,828,544,512 free bytes.
The output root did not exist.

The owner-approved command ran once:

```sh
rtk proxy .venv/bin/python scripts/phase3b_extract_retained.py /Volumes/CrewshalPhase3BArchiveStage/archives /Volumes/CrewshalPhase3BArchiveStage/extracted-12-v1
```

The command exited zero. Its JSON output contained 11,019 file entries and was too large for direct display.
The command wrote 511,667,961 regular content bytes in twelve selected archives.
It created three recorded Node links and a private `0700` output root.
The output manifest SHA-256 is `13e41f6e8156afd0e4284af200a1ac99f89b46aae7fbfd8f012933d5b56b4529`.
Its tree SHA-256 is `ea3f193c5811d591f4e0e78bf07f1bd527e4d7f22d28479fe68c46d499dcf3a2`.
The manifest lists 1,779 output directories, including implied directories.
The pinned archive report lists 1,740 explicit directory members.

An independent read-only check matched every manifest file length and SHA-256.
It matched all three link targets and the full 511,667,961-byte readback.
It found zero missing or mismatched files. Mounted free space was 1,273,950,208 bytes.
That exceeded the 536,870,912-byte floor by 737,079,296 bytes.
A later readback found 1,274,007,552 free bytes. APFS allocation can change between readbacks.
The image retained its 3,221,225,472-byte logical size and used 1,929,318,400 allocated bytes.

Post-extraction checks again matched both receipt hashes and SQLite integrity results.
They matched all 16 retained archive hashes, including the separately pinned failed `.NET SDK` body.
The frozen Phase 3A checker passed with 23 artifacts, 768 planned units, and the established digest.
Its execution flags remained false.

## Failures, costs, and limits

The first post-extraction custody script expected a SHA-256 in the failed `.NET SDK` receipt row.
That historical row has a null SHA-256. The corrected read-only script used the ledger's pinned digest.
It passed all 16 archive checks. No extraction retry occurred.

Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative conservative charge remain intact.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
No archive body request or URL retry occurred. No receipt, source archive, fixed image, or frozen Phase 3A file changed.
Guest and VM growth was zero. No guest, Linux test, native turn, provider request, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Installation, archived tool execution, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

The output tree is retained outside Git. Its manifest is a local custody record.
This check establishes local extraction integrity only. It does not qualify archived binaries or Linux behavior.
The next milestone needs a separate concrete decision before installation or archived tool execution.
Use the [next prompt](PHASE-3B-POST-EXTRACTION-NEXT-SESSION-2026-10-20.md) and its exact input index.
The delivery revision is the commit containing this record.
