# Four-archive extraction completion

Date: 2026-10-20. Status: Complete. This record closes one approved attempt.
The entry revision was `d440ae3eaeafc75c39745c2bf22e8909ba379aa1` on `codex/phase1-architecture`.
The owner approved the exact [proposal](PHASE-3B-REMAINING-ARCHIVE-PROPOSAL-2026-10-20.md) in this Codex chat on October 20.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records the decision and result.

## Environment and attempt

The local host ran macOS 27.2, build `26B5112a`, with Python 3.12.15.
The worktree was clean before the decision entry. No guest or VM action occurred.
All 200 indexed entry files matched their recorded sizes and SHA-256 values before the attempt.
Both receipts passed pinned SHA-256 and read-only SQLite checks. All 16 retained archives matched their pinned lengths and SHA-256 values.
The prior output manifest matched its pinned SHA-256. The fixed image had its recorded 3,221,225,472-byte logical size.
The host had 147,891,826,688 free bytes before image creation.

The following commands ran once, in order. Each command exited zero.

```sh
rtk proxy hdiutil create -size 6g -type SPARSE -fs 'Case-sensitive APFS' -volname CrewshalPhase3BRemainingStage /Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage
rtk proxy hdiutil attach -mountpoint /Volumes/CrewshalPhase3BRemainingStage -noautoopen /Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage
rtk proxy .venv/bin/python scripts/phase3b_extract_remaining.py /Volumes/CrewshalPhase3BArchiveStage/archives /Volumes/CrewshalPhase3BRemainingStage/extracted-4-v1
```

`hdiutil` reported a deprecation warning for the create and attach forms. Both operations succeeded.
Before extraction, the new mount had 6,210,732,032 free bytes and 6,232,694,784 total bytes.
The host had 147,878,187,008 free bytes. The new image used 13,635,584 allocated bytes.
The exact source and new image mount identities matched. The output root was absent before the first write.
The extractor source SHA-256 matched the ledger. Its one attempt exited zero.

## Independent readback

The output root is `/Volumes/CrewshalPhase3BRemainingStage/extracted-4-v1`.
The manifest SHA-256 is `4075234d7996789333e62cd082b7c408abed38a26d0fd5d3fff2de666f39e79d`.
The tree SHA-256 is `d9f8710e45ac59aaec9f174c64ee6437e1f6d52bea2974195a2ec83c9ee0e79b`.
An independent walk matched all 6,208 regular files, 3,859,951,638 content bytes, 989 output directories, and 37 Swift links.
It hashed every regular file and checked each link target inside the output root.
It checked the manifest, private file and directory modes, and the absence of extra members.
The first independent walk stopped because it treated `manifest.json` as an archive member.
The corrected walk treated it as the extractor's separate manifest and passed. No extraction retry occurred.
One custody command stopped because it used `.sparseimage` instead of the fixed image's `.dmg` suffix.
The corrected read-only command passed. It verified all 16 archive hashes, both receipt hashes, and eight attempts per receipt.
Both receipts passed SQLite `quick_check`. The original `.NET SDK` receipt remains failed and halted.
The prior twelve-archive manifest retained SHA-256 `13e41f6e8156afd0e4284af200a1ac99f89b46aae7fbfd8f012933d5b56b4529`.
The fixed image retained its 3,221,225,472-byte logical size. Its measured allocation was 1,931,333,632 bytes.
The earlier preflight measured 1,929,318,400 allocated bytes. The reason for this 2,015,232-byte change is unknown.
No intentional write targeted the fixed image. Archive, receipt, and prior manifest bytes matched their pinned hashes.
The frozen Phase 3A checker passed with 23 artifacts and 768 planned units.

The new image used 3,891,281,920 allocated host bytes after extraction.
The new mount had 2,331,660,288 free bytes. The host had 143,998,521,344 free bytes.
These measures passed the 7,516,192,768-byte image cap, 536,870,912-byte mounted floor, and 21,474,836,480-byte host floor.
Guest and VM allocation growth was zero. Known paid-host and metered API cost was USD 0.
No archive body request, URL retry, native turn, provider request, or evaluation row occurred.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative conservative charge remain unchanged.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.

## Remaining Phase 3B work

The single ledger closes further image creation and extraction attempts.
Installation, archived tool execution, guests, Linux tests, native turns, and evaluation remain closed.
CMake, Ninja, Ubuntu packages, and repository dependency closures still need exact admission work.
The consolidated campaign needs concrete changed resource limits and owner decisions before it acts.
Executable hashes, effective commands, providers, and B1 conformance remain null until observed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Use the [next prompt](PHASE-3B-POST-REMAINING-EXTRACTION-NEXT-SESSION-2026-10-20.md) and its exact input index.
