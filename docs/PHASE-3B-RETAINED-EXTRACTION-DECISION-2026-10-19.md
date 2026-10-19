# Proposed decision: one bounded retained extraction attempt

Date: 2026-10-19. Status: Proposed; no extraction is admitted.

## Exact proposed action

Approve one local extraction attempt for the twelve selected IDs in the [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json).
Use extractor SHA-256 `e31dd0a43d1323e85009311ec74cc85898ad49760f8d607326e9bc4b210540ae`.
Read archives only from `/Volumes/CrewshalPhase3BArchiveStage/archives`.
Create only `/Volumes/CrewshalPhase3BArchiveStage/extracted-12-v1` as a new exclusive output root.
The output root did not exist at the source checkpoint.
Permit at most 511,667,961 regular content bytes and keep 536,870,912 mounted free bytes at every stop check.
Keep the fixed 3,221,225,472-byte image and zero guest or VM growth.

Before the first write, repeat SHA-256 checks for both receipts and all 16 archives.
Check both receipts in read-only SQLite mode and confirm the original failed history.
Confirm the fixed image size, current mounted free space, output root absence, and source hash.
Keep the original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both historical charges unchanged.
Update only `archive_extraction_proposal` in the single ledger with the exact owner decision, output root, hash, and admission flag.
Run this command once after those checks:

```sh
rtk proxy .venv/bin/python scripts/phase3b_extract_retained.py /Volumes/CrewshalPhase3BArchiveStage/archives /Volumes/CrewshalPhase3BArchiveStage/extracted-12-v1
```

Stop on any changed input, quota failure, unsafe member, readback mismatch, or incomplete output.
Retain any partial tree for read-only review. Do not retry, rename, or delete it without a separate recovery decision.
Do not install, run archived tools, boot guests, run Linux tests, make provider calls, or start evaluation rows.
Do not retrieve archive bodies or retry consumed URLs.

## Limits and owner decision

The current mounted free readback is 1,784,799,232 bytes.
Subtracting selected regular content gives 1,273,131,271 bytes before allocation overhead.
The 536,870,912-byte floor leaves 736,260,359 bytes for overhead and partial output.
These calculations do not prove that the operation will fit on the mounted filesystem.
The extractor stops if observed free space crosses the floor.

Approval of this document would permit the one extraction attempt only.
It would not approve installation, archived tool execution, Linux qualification, Phase 3B calibration, or Phase 3C.
The owner decision is currently absent. The ledger keeps extraction admission false.
