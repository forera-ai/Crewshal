# Phase 3B capped archive continuation completion

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `7d504534e74b1a4f2aea7557025df2c68c0d5cbe`.
Status: All eight approved continuation requests passed their required archive checks. Further body requests are closed.

## Authority and fixed scope

The owner approved the seven exact digest-bound requests in this Codex chat.
The owner separately approved Swift signature-first verification under the pinned key and detached signature.
Both decisions approved a new SQLite receipt and a new 86,400-second elapsed origin.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and 7,200-second cumulative active cap remained fixed.
The original eight IDs remained consumed. No original URL was retried.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records both decisions and the final closure.

All 175 entry-index files matched their recorded sizes and SHA-256 values before the decision.
The transport SHA-256 matched `397c5647f8a74e05039b1e076fe4720b557533ee479aeb5327c78eea9fefbb76` before preparation.
The original receipt matched SHA-256 `9cd1b85273ca68a29d156a35556b7dbf0cc8944da8ec5db3e26c15812c1f93f4`.
Its read-only SQLite integrity check passed. It remained halted with eight original attempts and no incomplete read.
All eight retained archives matched their recorded sizes and SHA-256 values.
The mounted image, source inventories, original receipt, and original failed `.NET SDK` receipt remained intact.

## Commands and results

The reviewed `prepare` command created `continuation.sqlite3` only after the owner decisions entered the ledger.
It bound manifest SHA-256 `7e2b17bfc9409d01d606ebae3f081dfe5305c10032b9fbd115bd6227a1d78ffc`.
Each listed `fetch` command ran once, in this order. Each returned `verified`.

```sh
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py prepare --root /Volumes/CrewshalPhase3BArchiveStage --image /Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg --original-receipt /Volumes/CrewshalPhase3BArchiveStage/receipt.sqlite3
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id bun
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id dotnet-runtime-net8
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id dotnet-targeting-pack-net8
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id codex-wrapper
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id codex-native
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id claude-wrapper
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id claude-native
```

The operator fetched the exact Swift key and signature URLs from the admission ledger into local files outside Git.
The signature matched SHA-256 `b80abe59b6533c65c13ff3067f96474cf451adbdfa5d72ff167a1a7c84c7d480`.
The key matched SHA-256 `2ada84351b77be3a832bfb612c64cf3e22399c933645c490bab1f9fe18f3c229`.
An isolated GPG home identified fingerprint `52BB7E3DE28A71BE22EC05FFEF80A866B47A981F` before the Swift body request.
The Swift request then ran once. GPG verified the detached signature against the exact retained archive.
An independent isolated GPG check repeated that result after retrieval.

```sh
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py fetch --root /Volumes/CrewshalPhase3BArchiveStage --id swift --swift-signature /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.0.3.sig --swift-key /Volumes/X10Pro/Crewshal-Phase3B-Swift-6.x.asc
rtk proxy .venv/bin/python scripts/phase3b_capped_archive_continue.py status --root /Volumes/CrewshalPhase3BArchiveStage
```

| ID | Archive bytes | Verification |
| --- | ---: | --- |
| `bun` | 36,226,213 | Pinned SHA-256 matched. |
| `dotnet-runtime-net8` | 29,865,496 | Pinned SHA-512 matched. |
| `dotnet-targeting-pack-net8` | 6,845,027 | Pinned SHA-512 matched. |
| `codex-wrapper` | 4,904 | Pinned npm integrity matched. |
| `codex-native` | 155,715,063 | Pinned npm integrity matched. |
| `claude-wrapper` | 27,538 | Pinned npm integrity matched. |
| `claude-native` | 104,532,073 | Pinned npm integrity matched. |
| `swift` | 774,149,705 | Detached signature verified against the retained archive. |

The new receipt SHA-256 is `01df021749e72c6aba7e309e603a815d83d66e7026161fab9c43cb2a8bd9cf37`.
Its read-only SQLite integrity check passed. It records eight successful attempts and no incomplete read.
All eight retained continuation archives independently matched their receipt sizes and SHA-256 values.
The receipt records 1,107,366,019 new archive body bytes, zero other body bytes, and 95.51680779200979 active seconds.
The original receipt records 38.71709587611258 active seconds. Combined active time was 134.23390366812237 seconds.
The receipt status command calls the state `prepared` because the transport has no completed-state label.
The ledger now closes all further body requests.

## Storage, transfer, and cost

The prior 8,589,934,592-byte charge and original 311,183,922-byte conservative stage charge remain intact.
The original and continuation receipts record 1,368,218,293 total archive body bytes.
The unchanged 50,331,648-byte other-body reserve makes the final conservative stage charge 1,418,549,941 bytes.
The cumulative conservative transfer charge is 10,008,484,533 bytes under the 10,821,946,779-byte limit.
The two local Swift input files contain 2,509 bytes in total.
Their exact HTTP response traffic was not measured by the archive transport.
The full other-body reserve remains charged; no unused reserve was refunded.

The mounted volume reported 1,784,799,232 free bytes after the final archive.
Retained archive and source files totaled 1,375,785,647 bytes. The new receipt used 73,728 bytes.
The fixed image allocated 1,437,798,400 bytes under its 4,294,967,296-byte Mac cap.
The image retained its 3,221,225,472-byte logical size. No guest or VM command ran.
No signed redirect URL appears in this record or the new receipt.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat remains unknown.

## Local checks and limits

The environment was macOS 27.2 arm64, CPython 3.12.15, uv 0.9.24, and RTK 0.51.0.
The 22 local transport and extractor tests passed before preparation.
Ruff lint and strict mypy passed for the continuation transport.
The frozen Phase 3A checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
An offline wheel build and fresh offline installation passed at version `0.16.1`.
The installed `crewshal --help` command passed. The new exact input index matched all 178 listed files.
The original `.NET SDK` transport failure remains recorded. This continuation had no failed archive request.
No archive was extracted or executed in this stage.
Tool member safety, extraction bounds, dependencies, executable hashes, effective commands, providers, and B1 conformance remain unknown.
No CMake, Ninja, dependency package, guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

The delivery revision is the commit containing this record. Use the linked next prompt and exact input index after publication.
