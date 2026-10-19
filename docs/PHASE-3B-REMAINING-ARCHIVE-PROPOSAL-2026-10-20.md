# Proposed decision: one bounded extraction of four remaining archives

Date: 2026-10-20. Status: Approved and completed once. See the [completion record](PHASE-3B-REMAINING-EXTRACTION-COMPLETION-2026-10-20.md).
The prior twelve-archive extraction completed once. Its admission remains closed.
This proposal covers only `swift`, `dotnet-sdk`, `codex-native`, and `claude-native`.
Use the [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) for this decision.

## Bound inputs and local acceptance

The four retained archives total 1,238,521,707 compressed bytes.
Their pinned member report records 7,216 members and 3,859,951,638 regular content bytes.
It records 6,208 regular files, 971 directories, and 37 Swift links.
The largest regular member is 248,966,648 bytes.
The `.NET SDK` tarball uses one leading `./` on its members and a root `.` directory marker.
The extractor removes that one leading component and emits no file for the root marker.

Read-only preflight matched all four retained archive lengths, hashes, metadata digests, and member rules.
An independent Swift link check resolved all 37 links inside the archive.
It found 35 links to regular files and two links to directories.
The longest chain has three links. No chain escapes or cycles.
The extractor creates links only after regular content readback.
It rejects unsafe paths, case aliases, hard links, sparse files, special members, and unrecorded links.
It retains partial output on failure and writes a manifest only after complete readback.
Local synthetic tests and static checks must pass again before an admitted attempt.

## Exact proposed image and attempt

Create one new sparse image at `/Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage`.
Set its logical size to 6,442,450,944 bytes with case-sensitive APFS.
Mount it only at `/Volumes/CrewshalPhase3BRemainingStage`.
Permit at most 7,516,192,768 allocated host bytes for this new image.
Keep at least 21,474,836,480 host bytes free.
Require at least 4,933,693,462 mounted bytes free before the first output write.
Keep at least 536,870,912 mounted bytes free at every extractor stop check.
The logical image leaves 2,045,628,394 bytes for allocation overhead after content and the free floor.
These bounds do not guarantee successful extraction. Stop when a measured bound fails.
Guest and VM allocation growth remains zero.

Before creating the image, verify the exact source index, Git state, both receipt hashes, and read-only SQLite integrity.
Verify all 16 archive hashes, the fixed image, the new image path absence, and current host free space.
Verify the exact extractor SHA-256 and the single ledger fields.
After a separate owner approval, record that decision in the ledger.
Run these commands once, in this order:

```sh
rtk proxy hdiutil create -size 6g -type SPARSE -fs 'Case-sensitive APFS' -volname CrewshalPhase3BRemainingStage /Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage
rtk proxy hdiutil attach -mountpoint /Volumes/CrewshalPhase3BRemainingStage -noautoopen /Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage
rtk proxy .venv/bin/python scripts/phase3b_extract_remaining.py /Volumes/CrewshalPhase3BArchiveStage/archives /Volumes/CrewshalPhase3BRemainingStage/extracted-4-v1
```

The CLI binds both mount points to their exact image paths before writing.
It reads only the four pinned files from the existing archive mount.
It creates only the new output root and manifest on the new image.
It checks the image allocation cap and both free-space floors during extraction.
It must stop on changed input, unsafe member, quota failure, or readback mismatch.
Retain a partial image and tree after failure. Do not retry, rename, or delete them without a new decision.

## Authority and limits

This proposed decision permits one new image creation and one extraction attempt only.
It does not approve installation, archived tool execution, guest access, Linux tests, native turns, providers, or evaluation rows.
It does not change the fixed image, retained archive files, either receipt, or frozen Phase 3A bytes.
Do not request an archive body or retry a consumed URL.
Keep the original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and receipt histories intact.
Keep the prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative charge intact.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain null until observed.
Further Phase 3B installation and Linux scope still need separate concrete decisions after this attempt.
