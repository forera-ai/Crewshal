# Phase 3B capped archive stage halted

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `f11e1b40b63d8b4e33a3b321a421a1293c231598`.
Status: blocked after a transport digest-parser failure. No further body request is admitted.

## Decision and fixed scope

The owner approved the exact [sixteen-URL stage](PHASE-3B-CAPPED-ARCHIVE-STAGE-2026-10-19.md) in this Codex chat.
The approval retained every URL, per-object cap, 2,232,012,187-byte stage transfer cap, and zero guest growth.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records the decision and observed charges.
It keeps CMake, Ninja, dependency packages, guests, Linux tests, native turns, and evaluation rows outside this stage.

## Local controls and observed result

All 164 entry-index files matched their recorded size and SHA-256.
The local transport tests passed six cases before retrieval.
They covered redirect and error bodies, mismatch stops, missing digests, receipt changes, and object caps.
Strict mypy and Ruff passed for the transport source.
The fixed raw disk image limits the mounted APFS volume to 3,221,184,512 bytes.
The image has a fixed logical size of 3,221,225,472 bytes, below the 4,294,967,296-byte Mac allocation cap.
The transport stores archives, partial data, and SQLite receipts inside that image.
The receipt records attempts, response hops, body reads, and conservative incomplete-read reservations.
The original transport script had SHA-256 `79c547bcaecdd3ef85a1b4618cbb71b29f8fe28c93f2106380058c36079c14c4`.

Four source archives matched their recorded lengths and SHA-256 values.
The frozen extractor matched their inventories and produced 1,082 files with 7,567,354 content bytes.
The `rtk`, `cpython`, and `node` archives matched their recorded lengths and trusted digests.
The `.NET SDK` transfer retained 204,124,866 bytes.
An independent read matched its recorded SHA-512 exactly.
The transport marked that attempt failed because it parsed a hexadecimal SHA-512 as Base64.
The parser now distinguishes hexadecimal SHA-512 from npm Base64 integrity values.
The current repaired source passed a direct check for both forms, but it has not run in this stage.
The original receipt remains failed and halted. The owner-approved one-attempt rule forbids a retry under this grant.

| Measure | Observed or charged value |
| --- | ---: |
| Successful source archive attempts | 4 |
| Successful tool archive attempts | 3 |
| Failed `.NET SDK` transport receipt | 1 |
| Unattempted selected URLs | 8 |
| Actual archive response body bytes | 260,852,274 |
| Actual other response body bytes | 0 |
| Full other-body reserve charged | 50,331,648 |
| Conservative new-stage transfer charge | 311,183,922 |
| Prior full transfer charge retained | 8,589,934,592 |
| Conservative cumulative transfer charge | 8,901,118,514 |
| Retained logical file bytes at readback | 268,468,780 |
| Image allocated bytes at readback | 285,446,144 |
| Guest and VM allocation growth | 0 |
| Paid host and metered API cost | USD 0 |

The retained image and receipt remain outside Git.
The receipt contains temporary signed redirect URLs. Do not publish the receipt or raw URLs.
The current script SHA-256 is recorded in the admission ledger.
Three unattempted tool archives still lack trusted digests: `bun`, `swift`, and `dotnet-targeting-pack-net8`.
No missing digest became a verified archive.

## Reproduction and limits

The environment was Darwin 27.2.0 arm64 with local Python 3.14.8 and RTK 0.51.0.
The project virtual environment ran the transport and frozen extractor.

| Command or check | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | Clean entry worktree at the revision above. |
| SHA-256 and size check of `PHASE-3B-CAPPED-ARCHIVE-INPUTS-2026-10-19.json` | 164 files matched; zero failures. |
| `rtk proxy diskutil image create blank --format RAW --size 3221225472 --volumeName CrewshalPhase3BArchiveStage --fs APFS ...` | Created one fixed local image. |
| `rtk proxy diskutil image attach --nobrowse --mountPoint /Volumes/CrewshalPhase3BArchiveStage ...` | Mounted one isolated APFS volume. |
| Mounted-volume and image `stat`/`statvfs` readback | Volume 3,221,184,512 bytes; image logical 3,221,225,472 bytes. |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_capped_archive tests.acceptance.test_phase3b_extract_source -q` | Ten local tests passed after the parser repair. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_capped_archive.py tests/acceptance/test_phase3b_capped_archive.py` | Passed. |
| `rtk proxy .venv/bin/mypy --strict scripts/phase3b_capped_archive.py` | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units retained digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`. |
| Eight `scripts/phase3b_capped_archive.py fetch` attempts | Seven transport receipts passed; the `.NET SDK` receipt failed and halted the stage. |
| Four `scripts/phase3b_extract_source.py` calls | Four frozen source inventories matched. |

The original transport did not establish a complete successful stage.
The repaired script has local test evidence only. It cannot reopen the halted receipt.
Archive metadata and digest matches do not establish safe tool members, executable hashes, dependencies, or Linux conformance.
The three tool archives without trusted digests remain closed.
No guest, Linux test, provider request, Jev call, native turn, or evaluation row ran.
Subscription quota debit for this chat remains unknown.
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Provider identities, effective commands, B1 conformance, Phase 3B calibration, and Phase 3C remain unknown or closed.

## Next boundary

The next session must first preserve and verify this halted receipt and retained data.
It must prepare a new exact continuation decision for unattempted objects and the repaired transport.
It must obtain trusted digests for the three missing tool archives before their body requests.
It must not retry the consumed `.NET SDK` URL under the original grant.
Any resumed transfer needs an explicit owner decision and a fresh, verified accounting and storage plan.
