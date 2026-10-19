# Phase 3B halted archive continuation boundary

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `fd5fdf7332224c2d0d47d06ef2e6227a216dbf9b`.
Status: blocked. No archive body request or owner decision is admitted by this record.

## Verified custody

All 168 indexed files matched their recorded size and SHA-256. The entry worktree was clean.
The mounted APFS stage volume and its image remain in place. The original SQLite receipt remains halted.
The receipt passed `PRAGMA quick_check` and has SHA-256 `9cd1b85273ca68a29d156a35556b7dbf0cc8944da8ec5db3e26c15812c1f93f4`.
It records eight attempts, including the failed `dotnet-sdk` attempt, and no incomplete read.
Its original script binding remains `79c547bcaecdd3ef85a1b4618cbb71b29f8fe28c93f2106380058c36079c14c4`.
The repaired script has SHA-256 `e67c93816da58c242880c631b6f436c75011cf098e317c7a29ca2f1edb104f91`.
That difference prevents the repaired script from resuming the original receipt.
The original script source is not in the entry revision. This review compared the recorded binding, current source, and local tests.

The retained `dotnet-sdk` file has 204,124,866 bytes and SHA-256 `b91b19f6bafd1184913082d135f575dd9faa53767b84d836c063ce52e8fab430`.
Its SHA-512 matches the value in the single admission ledger.
This independent file check does not change the failed transport receipt or restore attempt authority.
The seven successful archives retain their recorded receipts and file hashes.
The four source inventories retain their earlier frozen extractor results.

The image has 3,221,225,472 logical bytes and 285,446,144 allocated bytes.
The mounted volume has 3,221,184,512 bytes. Retained files total 268,468,780 logical bytes.
The guest and VM allocation did not change during this review.
No guest readback was made.

## Digest research

The official [Bun 1.2.2 release](https://github.com/oven-sh/bun/releases/expanded_assets/bun-v1.2.2) lists the selected archive and `SHASUMS256.txt`.
The checksum file gives `d1dbaa3e9af24549fad92bdbe4fb21fa53302cd048a8f004e85a240984c93d4d` for `bun-linux-aarch64.zip`.
Its 2,075 bytes have SHA-256 `4716baa1ae9c95fa12bcbfd983e96cbb8da60609ab3575ca0ad0178a74810618`.
The detached Bun checksum signature was not verified. The checksum is an official HTTPS release input, not a verified archive.

The [NuGet catalog entry](https://api.nuget.org/v3/catalog0/data/2024.11.12.18.26.32/microsoft.netcore.app.ref.8.0.11.json) gives package size 6,845,027 bytes.
It gives SHA-512 `oMIPTmsRuaFIosXYWzEHFCu2pQK0JdtkuQdT4j1szfZ8BVTHtYsBqWdjGV3u9uaWiJld6V7FanVVU+Z8HWFQ6Q==`.
The catalog states `SHA512`, and its size matches the existing object cap.
This metadata does not verify package content.

The [Swift installation guide](https://www.swift.org/install/linux/tarball/) requires a detached signature.
The [official Swift key page](https://www.swift.org/keys/active/) names fingerprint `52BB7E3DE28A71BE22EC05FFEF80A866B47A981F`.
The selected signature has 819 bytes and SHA-256 `b80abe59b6533c65c13ff3067f96474cf451adbdfa5d72ff167a1a7c84c7d480`.
The official key file has SHA-256 `2ada84351b77be3a832bfb612c64cf3e22399c933645c490bab1f9fe18f3c229`.
Its displayed fingerprint matches the official page, and the signature packet names its long key ID.
No trusted full Swift archive digest was found. The signature cannot verify archive content before retrieval.
Keep `swift` closed until a trusted digest is bound or a separate signature-first rule receives owner approval.

## Exact proposed continuation

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) retains the original sixteen URLs and all object caps.
It records eight unattempted IDs: `bun`, `swift`, `dotnet-runtime-net8`, `dotnet-targeting-pack-net8`, and four selected npm tarballs.
The unattempted object caps total 1,920,828,265 bytes.

| Unattempted ID | Original body cap, bytes |
| --- | ---: |
| `bun` | 36,226,213 |
| `swift` | 774,149,705 |
| `dotnet-runtime-net8` | 29,865,496 |
| `dotnet-targeting-pack-net8` | 6,845,027 |
| `codex-wrapper` | 268,435,456 |
| `codex-native` | 268,435,456 |
| `claude-wrapper` | 268,435,456 |
| `claude-native` | 268,435,456 |

The prior 8,589,934,592-byte charge and current 311,183,922-byte conservative charge remain unchanged.
The 50,331,648-byte other-body reserve is already charged in full.
The maximum cumulative charge stays 10,821,946,779 bytes if all remaining object caps are consumed.

A new continuation transport must use the repaired digest parser and the same exact URLs and caps.
It must pin its own source SHA-256 before a request. The original script and receipt remain historical evidence.
Create `continuation.sqlite3` on the mounted image. Never migrate or rewrite `receipt.sqlite3`.
Bind the new receipt to the original receipt SHA-256, original scope hash, manifest SHA-256, transport SHA-256, and eight unattempted IDs.
Import seven successful files as read-only verified references. Import the SDK file as independent verified data with its failed receipt status.
Never import an attempted ID as requestable. Recheck every retained file hash before each new request.
Keep the original receipt and archive files unchanged. Do not copy large files inside the image.

The new receipt must journal attempts, redirects, error bodies, reserved reads, actual reads, counters, and terminal state.
One durable attempt is allowed per unattempted URL. Missing or changed receipt data must stop before a request.
Count all response body bytes across both receipts against the original 2,232,012,187-byte stage cap.
Count new archive bodies against the remaining 1,920,828,265-byte sum and each original object cap.
Count redirect and error bodies against the existing 50,331,648-byte reserve.
Keep the original 7,200-second active cap cumulative. A new 86,400-second elapsed origin needs the separate owner decision.
Keep the fixed image, 3,221,225,472-byte retained limit, 4,294,967,296-byte Mac allocation limit, and zero guest growth.
Cap the new receipt and its journals at 16,777,216 logical bytes. Refuse a request if this bound cannot be enforced.
The current retained files, remaining archive caps, and new receipt cap total at most 2,206,074,261 logical bytes.
This leaves 1,015,151,211 bytes under the retained limit and 1,015,110,251 bytes on the mounted volume.
No extraction or extra cache is admitted by this continuation.
Before each read, check the remaining body and storage budgets. Halt on any failure or uncertain read.
Retain all partial bytes and conservative reservations. Do not retry, replace a URL, or refund a charge.

The continuation command interface is prospective. It does not exist or grant transfer authority.
After implementation, bind its hash and pass offline redirect, failure, crash, digest, and old-receipt refusal tests.
Use these exact command shapes only after a separate owner decision and successful preflight:

```sh
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py prepare --root /Volumes/CrewshalPhase3BArchiveStage --image /Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg --original-receipt /Volumes/CrewshalPhase3BArchiveStage/receipt.sqlite3
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py status --root /Volumes/CrewshalPhase3BArchiveStage
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id ID
```

Use `ID` once for each admitted unattempted object. The current plan admits no `ID` while Swift and the transport remain unresolved.
Do not fetch `dotnet-sdk` again. Do not extract or execute tool archives in this continuation.
Safe members, extraction bounds, dependencies, executable hashes, effective commands, providers, and B1 conformance remain unknown.

## Verification, costs, and limits

Environment: Darwin 27.2.0 arm64, local Python 3.14.8, project Python 3.12.15, and RTK 0.51.0.
The ten local transport and extractor tests passed. Ruff and strict mypy passed for the repaired transport.
The frozen Phase 3A checker passed with 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.

| Command or check | Result |
| --- | --- |
| `rtk proxy git status --short --branch` and `rtk proxy git rev-parse HEAD` | Clean entry worktree at the revision above. |
| SHA-256 and size check of `PHASE-3B-CAPPED-ARCHIVE-HALTED-INPUTS-2026-10-19.json` | All 168 files matched. |
| Read-only SQLite `PRAGMA quick_check` and attempt/counter query | Passed; eight attempts, one failed SDK receipt, and zero incomplete reads. |
| Read-only hash of `/Volumes/CrewshalPhase3BArchiveStage/archives/dotnet-sdk.blob` | Length and ledger SHA-512 matched. |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_capped_archive tests.acceptance.test_phase3b_extract_source -q` | Ten local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_capped_archive.py tests/acceptance/test_phase3b_capped_archive.py` | Passed. |
| `rtk proxy .venv/bin/mypy --strict scripts/phase3b_capped_archive.py` | Passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed with the digest above. |
| New 170-file input index and ledger arithmetic check | Passed with zero mismatches. |
| `rtk proxy git diff --check` | Passed. |

Read-only metadata requests did not fetch any selected archive body. Their network body total was not fully metered.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat is unknown.
No Jev call, guest access, Linux test, native turn, or evaluation row occurred.
Linux-specific tests remain deferred. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.

The next boundary must bind a trusted Swift archive digest or propose an exact signature-first amendment.
It must implement and test the new receipt and transport before seeking a new owner decision.
The prior approval cannot reopen the halted stage.
