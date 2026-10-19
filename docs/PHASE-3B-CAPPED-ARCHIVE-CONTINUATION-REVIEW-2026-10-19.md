# Phase 3B halted archive continuation review

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `901c46fefde60cb099f0cc383baf7bfc7e4051e6`.
Status: prepared for a separate owner decision. No continuation receipt or archive request exists.

## Fixed scope and custody

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) retains all sixteen original URLs and caps.
The original eight IDs remain consumed. The continuation can request only the eight unattempted IDs in that ledger.
The original receipt SHA-256 is `9cd1b85273ca68a29d156a35556b7dbf0cc8944da8ec5db3e26c15812c1f93f4`.
The original scope SHA-256 is `7286e3da3dee932f178108733bfaa6b111e1adba822b9628dfde7910b7da05cb`.
The original receipt remains read-only, failed, and halted. The SDK file remains independently verified data with a failed transport receipt.
The image, original archives, source inventories, and frozen Phase 3A package remain in place.
The receipt contains signed redirect URLs. Do not publish its raw content or those URLs.

The new transport is [the separate script](../scripts/phase3b_capped_archive_continue.py).
Its SHA-256 is `397c5647f8a74e05039b1e076fe4720b557533ee479aeb5327c78eea9fefbb76`.
It creates `continuation.sqlite3` only after a new owner decision appears in the ledger.
The new receipt binds the original receipt SHA-256, original scope, current manifest SHA-256, script SHA-256, image, root, and eight IDs.
It uses SQLite `DELETE` journaling, `FULL` synchronization, 4,096-byte pages, and a 2,032-page main-file limit.
It caps the combined receipt and journal footprint at 16,777,216 bytes and refuses an unfinished journal.
It records attempts, response hops, URL hashes, body classes, reserved reads, actual reads, counters, and terminal state.
It does not store or print signed redirect URLs.
It hashes all eight retained files before each new request. It treats the SDK receipt as failed.
It rejects every attempted ID before opening a network connection.

## Exact transfer and storage bounds

| Bound | Bytes or seconds | Stop condition |
| --- | ---: | --- |
| Unattempted archive bodies | 1,920,828,265 bytes | Each ID keeps its original cap. |
| All archive bodies, including original | 2,181,680,539 bytes | Stop before any read crosses the cap. |
| Redirect and error bodies | 50,331,648 bytes | Keep the full reserve charged. |
| All stage body traffic | 2,232,012,187 bytes | Stop before any read crosses the cap. |
| Prior transfer charge | 8,589,934,592 bytes | Keep the historical full charge. |
| Current conservative stage charge | 311,183,922 bytes | Keep the current full reserve and observed bodies. |
| Maximum cumulative charge | 10,821,946,779 bytes | No refund follows a failed attempt. |
| New receipt | 16,777,216 logical bytes | SQLite page limit and file-size check stop growth. |
| Batch retained data | 3,221,225,472 logical bytes | The fixed mounted volume and free-space checks enforce the bound. |
| Mac host allocation | 4,294,967,296 bytes | Image allocation readback must stay below the cap. |
| Guest and VM allocation growth | 0 bytes | No guest or VM command is admitted. |
| Cumulative active time | 7,200 seconds | Include the original receipt's 38.71709587611258 seconds. |
| New elapsed origin | 86,400 seconds | Begin only when `prepare` creates the new receipt. |

The observed retained files and every remaining object cap total 2,189,297,045 bytes.
The full new receipt allowance raises this to 2,206,074,261 bytes.
The recorded retained-data headroom is 1,015,151,211 bytes.
The recorded mounted-volume headroom is 1,015,110,251 bytes.
Before preparation and each request, the transport checks current volume space for all remaining object caps and receipt space.
It keeps the fixed image and zero guest growth. It creates no extraction or extra cache.

The transport reserves each response read before it calls the network stream.
A missing actual count blocks every later request. Failed requests retain partial files and halt the receipt.
Redirect and HTTP error bodies consume the existing other-body reserve.
A digest or signature failure keeps the attempt consumed. No URL retry, replacement, or charge refund is allowed.

## Trusted inputs and Swift amendment

The selected Bun archive has the official checksum `d1dbaa3e9af24549fad92bdbe4fb21fa53302cd048a8f004e85a240984c93d4d`.
The [official checksum file](https://github.com/oven-sh/bun/releases/download/bun-v1.2.2/SHASUMS256.txt) had 2,075 bytes and SHA-256 `4716baa1ae9c95fa12bcbfd983e96cbb8da60609ab3575ca0ad0178a74810618`.
Its detached signature was not verified. The archive itself remains unverified.
The [NuGet catalog](https://api.nuget.org/v3/catalog0/data/2024.11.12.18.26.32/microsoft.netcore.app.ref.8.0.11.json) gives the selected targeting pack's 6,845,027-byte count and SHA-512.
The ledger contains that exact Base64 digest. The archive remains unverified.

No trusted full SHA-256 or SHA-512 for the selected Swift archive was found in the official sources reviewed.
The [Swift installation guide](https://www.swift.org/install/linux/tarball/) instead requires a detached signature.
The [official key page](https://www.swift.org/keys/active/) identifies fingerprint `52BB7E3DE28A71BE22EC05FFEF80A866B47A981F`.
The official key file has SHA-256 `2ada84351b77be3a832bfb612c64cf3e22399c933645c490bab1f9fe18f3c229`.
The selected detached signature has 819 bytes and SHA-256 `b80abe59b6533c65c13ff3067f96474cf451adbdfa5d72ff167a1a7c84c7d480`.
The ledger pins both exact source URLs, byte hashes, and signer fingerprint.
The signature packet identifies a signer. It does not verify an archive that has not been retrieved.

The proposed amendment permits a Swift body request only after the owner separately approves signature-first verification.
The operator must provide the exact key and signature bytes as local files before that request.
The transport hashes both files, imports the key into an isolated temporary GPG home, and checks the full fingerprint before network access.
After transfer, GPG must verify the detached signature against the exact retained archive file.
Any missing file, hash change, wrong fingerprint, missing GPG, or failed verification consumes no new permission.
The Swift file remains quarantined until verification passes. The stage never extracts or executes it.
The transport does not fetch the key or signature. Their local supply and provenance remain a separate prerequisite.
`swift_signature_first_approved` remains `false` in the ledger until the owner decides this amendment.

## Exact commands after a separate approval

The current ledger sets `owner_decision` to `null` and `body_requests_admitted` to `false`.
The transport refuses `prepare` and `fetch` in this state.
After an exact owner decision, record the decision in the ledger and bind its new SHA-256 before preparation.
Use the current script SHA-256 above. Do not change the original stage decision or receipt.

```sh
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py prepare --root /Volumes/CrewshalPhase3BArchiveStage --image /Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg --original-receipt /Volumes/CrewshalPhase3BArchiveStage/receipt.sqlite3
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py status --root /Volumes/CrewshalPhase3BArchiveStage
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id bun
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id dotnet-runtime-net8
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id dotnet-targeting-pack-net8
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id codex-wrapper
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id codex-native
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id claude-wrapper
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id claude-native
```

Run each `fetch` command at most once. Stop the sequence after any failure or uncertain outcome.
Run the Swift command only if the owner approves signature-first verification and the two local inputs pass preflight:

```sh
rtk proxy shasum -a 256 /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.0.3.sig /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.x.asc
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id swift --swift-signature /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.0.3.sig --swift-key /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.x.asc
```

The two local Swift input paths are planned destinations. Neither file exists as a verified continuation input now.
No command above is approved for execution by this review record.

## Decision requested and remaining limits

The owner must decide whether to approve the exact seven digest-bound requests and the new receipt.
The same decision must state whether to approve Swift signature-first verification under the pinned inputs.
An approval must explicitly permit a new 86,400-second elapsed origin and retain the original cumulative active cap.
The original approval ended at the halt and does not cover this continuation.

No CMake, Ninja, dependency package, guest, Linux test, native turn, provider request, or evaluation row belongs to this decision.
Tool member safety, extraction bounds, executable hashes, effective commands, providers, and B1 conformance remain unknown.
The 192 development rows remain planned. The 576 sealed rows remain unexposed.
Phase 3B calibration, Linux qualification, and Phase 3C remain closed.

## Local verification and observed limits

The entry worktree was clean at the revision above. All 170 entry-index files matched size and SHA-256.
The environment was macOS 27.2 arm64, CPython 3.12.15, uv 0.9.24, and RTK 0.51.0.
The review-time admission ledger SHA-256 is `3247822e31dc7404ec62a5f6072694f5e7b2310e49c38fa360758e576293bcdb`.
An approved decision would change that manifest hash before `prepare` binds the new receipt.

| Command or check | Observed result |
| --- | --- |
| `rtk proxy git status --short --branch` and `rtk proxy git log -1` | Clean entry at `901c46fefde60cb099f0cc383baf7bfc7e4051e6`. |
| SHA-256 and size check of the 170-file entry index | Zero mismatches. |
| SHA-256 and size check of the 175-file review index | Zero mismatches. |
| Read-only original receipt hash, `PRAGMA quick_check`, and attempt summary | Recorded SHA-256 matched; eight attempts remained, including the failed SDK receipt. |
| Read-only stage storage readback | No continuation receipt; 268,468,780 retained file bytes; 3,221,184,512-byte mounted volume. |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_capped_archive_continue tests.acceptance.test_phase3b_capped_archive tests.acceptance.test_phase3b_extract_source -q` | 22 local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_capped_archive_continue.py tests/acceptance/test_phase3b_capped_archive_continue.py` | Passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_capped_archive_continue.py tests/acceptance/test_phase3b_capped_archive_continue.py` | Passed after formatting. |
| `rtk proxy .venv/bin/mypy --strict scripts/phase3b_capped_archive_continue.py` | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units retained the frozen digest. |
| `rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py prepare --root /Volumes/CrewshalPhase3BArchiveStage --image /Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg --original-receipt /Volumes/CrewshalPhase3BArchiveStage/receipt.sqlite3` | Refused before creating a receipt: `separate owner decision is missing`. |
| `rtk proxy uv build --offline --wheel`, offline wheel installation, installed version check, and installed CLI help | Passed with synchronized `0.16.0` version. |
| `rtk proxy git diff --check` | Passed. |

The current image has 3,221,225,472 logical bytes and 285,544,448 allocated bytes.
The allocation is 98,304 bytes above the previous readback. No continuation command wrote the image; the cause remains unknown.
The fixed image remains below the 4,294,967,296-byte Mac cap. No guest readback occurred.

An initial local test run found a fixture path mismatch. The fixture now resolves macOS temporary paths.
An initial CLI help run found a script import failure. The script now binds its repository import root.
The first format check required formatting both new files. All final checks pass.
The shell has no `python` command, so checks used `.venv/bin/python`.

No selected archive body, attempted URL retry, guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat is unknown.
Linux-specific tests were deferred, not passed. Swift key and signature files remain absent at their planned paths.
