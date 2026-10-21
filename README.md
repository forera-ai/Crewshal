# Crewshal

Owned and maintained by [forera-ai](https://github.com/forera-ai). Canonical repository: [forera-ai/Crewshal](https://github.com/forera-ai/Crewshal).

**Coordinate coding agents. Verify their work.**

Crewshal (pronounced like **crucial**) is an early open-source project exploring repository-aware coordination and verifiable engineering controls for AI-assisted software development.

The hypothesis: a human-confirmed model of an unfamiliar repository can reduce manual workflow setup while supporting consistent boundaries, validation and completion evidence across different coding runtimes.

## Current status

**October 21: The Phase 3B local source review handoff checkpoint is complete.**
Each claim comparison now reports the declared inventory kind, size, digest, path, and local result.
Every comparison still requires admitted source review. A matching value does not establish event origin.
The [checkpoint record](docs/PHASE-3B-LOCAL-REVIEW-CHECKPOINT-2026-10-21.md) gives local results and limits.
The [next prompt](docs/PHASE-3B-LOCAL-REVIEW-NEXT-SESSION-2026-10-21.md) and [exact inputs](docs/PHASE-3B-LOCAL-REVIEW-INPUTS-2026-10-21.json) govern continuation.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification and Phase 3B calibration remain closed.

**October 21: The Phase 3B local claim path checkpoint is complete.**
Each measurement source now declares one bounded JSON path for one field and inventory file.
Paths can select nested objects and array entries in files with different schemas.
The checker reports matched, unmatched, and unsupported values without authenticating run origin.
The [checkpoint record](docs/PHASE-3B-LOCAL-PATH-CHECKPOINT-2026-10-21.md) gives local results and limits.
The [next prompt](docs/PHASE-3B-LOCAL-PATH-NEXT-SESSION-2026-10-21.md) and [exact inputs](docs/PHASE-3B-LOCAL-PATH-INPUTS-2026-10-21.json) govern continuation.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification and Phase 3B calibration remain closed.

**October 21: The Phase 3B local claim content checkpoint is complete.**
The `check-contents` command compares declared claims with matching paths in local JSON files.
It reports exact matches, unmatched values, and unsupported formats for each field and file.
It checks inventory digests before each comparison and keeps `evidence_verified: false`.
The [checkpoint record](docs/PHASE-3B-LOCAL-CONTENT-CHECKPOINT-2026-10-21.md) gives local results and limits.
The [next prompt](docs/PHASE-3B-LOCAL-CONTENT-NEXT-SESSION-2026-10-21.md) and [exact inputs](docs/PHASE-3B-LOCAL-CONTENT-INPUTS-2026-10-21.json) govern continuation.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification and Phase 3B calibration remain closed.

**October 21: The Phase 3B local source attribution checkpoint is complete.**
Measurement records now map populated observations to named evidence files through `source_refs`.
The checker rejects missing, repeated, or undeclared file names, including for zero values.
The [checkpoint record](docs/PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-CHECKPOINT-2026-10-21.md) gives local results and limits.
The [next prompt](docs/PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-NEXT-SESSION-2026-10-21.md) and [exact inputs](docs/PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-INPUTS-2026-10-21.json) govern continuation.
Local file links do not authenticate execution. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. Linux qualification and calibration remain closed.

**October 21: The Phase 3B local provenance checkpoint is complete.**
The [development ledger](scripts/phase3b_development_ledger.py) binds each measurement record to declared inventory files.
The `check-provenance` command checks inventory digests, local artifact bytes, and attempt outcomes.
It cannot authenticate artifact origins or execution. See the [checkpoint record](docs/PHASE-3B-LOCAL-PROVENANCE-CHECKPOINT-2026-10-21.md).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification and Phase 3B calibration remain closed.

**October 21: The Phase 3B local measurement checkpoint is complete.**
The [development ledger](scripts/phase3b_development_ledger.py) checks measurement claims against declared attempts and the frozen schedule.
The `check-measurements` command rejects missing attempts, changed row identities, false final outcomes, and incomplete usage claims.
It keeps measured cost, estimated cost, and subscription quota separate.
It does not authenticate execution or grant authority. See the [checkpoint record](docs/PHASE-3B-LOCAL-MEASUREMENTS-CHECKPOINT-2026-10-21.md).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification and Phase 3B calibration remain closed.

**October 21: The Phase 3B local evidence inventory checkpoint is complete.**
The [development ledger](scripts/phase3b_development_ledger.py) now checks declared attempts against local artifact sizes and SHA-256 hashes.
The `check-evidence` command rejects missing attempts, changed files, unsafe names, and mismatched final outcomes.
It does not prove that an artifact came from an admitted run. It always reports `evidence_verified: false`.
The [checkpoint record](docs/PHASE-3B-LOCAL-EVIDENCE-CHECKPOINT-2026-10-21.md) gives the commands, fixture results, and limits.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native execution, and Phase 3B calibration remain closed.

**October 21: The first Phase 3B local software checkpoint is complete.**
The [development ledger check](scripts/phase3b_development_ledger.py) creates and checks one planned entry for each of the 192 development rows.
It binds each entry to the frozen Phase 3A package and rejects missing, changed, or repeated schedule rows.
It grants no execution authority and verifies no run evidence.
The [checkpoint record](docs/PHASE-3B-LOCAL-LEDGER-CHECKPOINT-2026-10-21.md) gives local commands and limits.
All 192 rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native execution, and Phase 3B calibration remain closed.

**October 21: Phase 3B local development is paused at the Linux gate.**
The owner stopped guest checks and asked for local development only.
The [stop record](docs/PHASE-3B-LOCAL-DEVELOPMENT-BOUNDARY-2026-10-21.md) records the completed host transport and the suspended clone.
The guest staging command was not submitted. The single admission ledger closes further guest action.
Local synthetic tests pass. The 192 development rows remain planned, and the 576 sealed rows remain unexposed.
Phase 3B calibration and acceptance remain open until the owner instructs the consolidated Linux campaign.

**October 20: One offline toolchain staging attempt is approved.**
The owner approved the [exact proposal](docs/PHASE-3B-OFFLINE-TOOLCHAIN-STAGING-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one host transport and one isolated clone stage.
The action has not started. Archived tool execution, Linux qualification, native turns, and evaluation remain closed.

**October 20: Offline toolchain staging has a bounded proposal.**
The [proposal](docs/PHASE-3B-OFFLINE-TOOLCHAIN-STAGING-PROPOSAL-2026-10-20.md) binds two verified output trees and one isolated clone stage.
The local transport script passes four synthetic tests, Ruff, and mypy. Both retained output trees match their pinned manifests.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no transport creation or guest action yet.
Archived tool execution, Linux qualification, native turns, and evaluation remain closed.

**October 20: The offline Ubuntu package installation completed.**
The [completion record](docs/PHASE-3B-OFFLINE-INSTALLATION-COMPLETION-2026-10-20.md) verifies one approved resume and install.
All 101 cached package versions match the installed versions. APT returned exit zero.
The clone is off. Original guest custody and host limits pass.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes further guest action.
Archived tools, Linux qualification, native turns, and evaluation remain closed.

**October 20: One offline installation resume is approved.**
The owner approved the [exact resume proposal](docs/PHASE-3B-OFFLINE-INSTALLATION-RESUME-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one saved-state resume and one offline install.
The clone network and sharing stay disconnected. All execution and evaluation gates remain closed.

**October 20: The approved offline installation stopped at VMware suspension.**
The [stop record](docs/PHASE-3B-OFFLINE-INSTALLATION-SUSPEND-2026-10-20.md) closes one clone start before installation.
The clone is suspended with network and sharing disabled. No installation command ran.
The [resume proposal](docs/PHASE-3B-OFFLINE-INSTALLATION-RESUME-PROPOSAL-2026-10-20.md) needs a separate owner decision.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest action.
Archived tools, Linux qualification, native turns, and evaluation remain closed.

**October 20: One offline Ubuntu package installation is approved.**
The owner approved the [exact installation proposal](docs/PHASE-3B-OFFLINE-PACKAGE-INSTALLATION-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one isolated clone start and one cached-package install.
The clone network remains disconnected. Archived tools, Linux tests, native turns, and evaluation remain closed.

**October 20: The storage-gated Ubuntu package retrieval completed.**
The [completion record](docs/PHASE-3B-APT-STORAGE-RETRY-COMPLETION-2026-10-20.md) verifies 101 cached packages and all 101 hashes.
The new conservative network charge was 116,542,541 bytes. The cumulative charge is 10,125,027,074 bytes.
The clone is off with network and sharing disabled. No package was installed.
The [offline installation proposal](docs/PHASE-3B-OFFLINE-PACKAGE-INSTALLATION-PROPOSAL-2026-10-20.md) needs a separate owner decision.
Archived tools, Linux qualification, native turns, and evaluation remain closed.

**October 20: One storage-gated APT retry is approved.**
The owner approved the [exact retry proposal](docs/PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one clone start and one download-only attempt.
Recheck the 64 GiB host free-space floor before start and network connection.
Installation, Linux qualification, native turns, and evaluation remain closed.

**October 20: The isolated APT attempt stopped at the host storage floor.**
The [stop record](docs/PHASE-3B-APT-ISOLATION-STORAGE-STOP-2026-10-20.md) closes one start and an owner reboot.
Offline checks passed twice. The host fell below 64 GiB free before network connection.
The clone is off. No package transfer or installation occurred.
Host space later recovered, but the [exact retry proposal](docs/PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md) needs a separate owner decision.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest action.

**October 20: One isolated APT package retrieval is approved.**
The owner approved the [exact one-start proposal](docs/PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits offline isolation checks before one download-only attempt.
The unused 167,772,160-byte conservative allowance remains the new transfer ceiling.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.

**October 20: The approved Ubuntu package retrieval stopped before network connection.**
The [completion record](docs/PHASE-3B-PACKAGE-RETRIEVAL-HOOK-STOP-2026-10-20.md) records configured APT hooks and an orderly clone shutdown.
No package was retrieved. The new network charge was zero. The historical conservative charge remains unchanged.
The [isolated APT proposal](docs/PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md) needs a separate owner decision.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: One bounded Ubuntu package retrieval is approved.**
The owner approved the [exact one-start proposal](docs/PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one download-only attempt in the separate clone.
The new conservative transfer allowance is 167,772,160 bytes. The prior charge remains unchanged.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.

**October 20: One bounded Ubuntu package retrieval decision is pending.**
The [proposal](docs/PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md) covers one isolated clone start and download-only APT.
It proposes 167,772,160 bytes of additional conservative network charge for 101 listed package objects.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no network or guest action yet.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.

**October 20: The approved offline package resolution capture completed once.**
The [completion record](docs/PHASE-3B-OFFLINE-RESOLUTION-COMPLETION-2026-10-20.md) records the guest commands, results, shutdown, and limits.
The offline APT list resolved 101 package objects totaling 111,245,650 bytes. Its largest object was 18,708,214 bytes.
The clone is off. Its network and sharing remain disabled. The original guest hashes still match.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes further guest starts and transfer.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: One offline package resolution capture is approved.**
The owner approved the [exact one-start proposal](docs/PHASE-3B-OFFLINE-RESOLUTION-PROPOSAL-2026-10-20.md).
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits only the proposal's read-only commands in the isolated clone.
Package retrieval, installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: The approved offline package snapshot completed once.**
The [completion record](docs/PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-COMPLETION-2026-10-20.md) records eight read-only commands and a successful APT simulation.
The clone is off. Its network and sharing remain disabled. The original guest hashes still match.
The full package table was not captured. Transfer and installation need a new concrete decision.
Use the [continuation prompt](docs/PHASE-3B-POST-SNAPSHOT-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-POST-SNAPSHOT-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: One offline Ubuntu package snapshot is approved.**
The owner approved the [exact one-start proposal](docs/PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-PROPOSAL-2026-10-20.md).
The [single admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits only read-only package queries in the separate clone.
Package retrieval, installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: The approved separate guest passed its capacity check.**
The [completion record](docs/PHASE-3B-SEPARATE-GUEST-CAPACITY-COMPLETION-2026-10-20.md) records one clone, one start, and an orderly shutdown.
Ubuntu arm64 showed four CPUs, 17,760,559,104 memory bytes, and 55,519,887,360 free guest bytes.
The clone used 4,921,806,848 allocated host bytes. Both historical guests remained unchanged.
Package retrieval, installation, Linux qualification, archived tool execution, and evaluation need separate admission.
Use the [continuation prompt](docs/PHASE-3B-POST-CLONE-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-POST-CLONE-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: All sixteen retained archive inventories have read-only output bindings.**
The [toolchain readback](docs/PHASE-3B-TOOLCHAIN-READBACK-COMPLETION-2026-10-20.md) confirms 1,368,218,293 compressed bytes and 4,371,619,599 regular content bytes.
It binds both output manifests and keeps installed executable hashes, effective commands, and providers unknown.
The guest decision remains open. No guest, installer, archived tool, native turn, or evaluation row ran.
Use the [next prompt](docs/PHASE-3B-TOOLCHAIN-READBACK-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-TOOLCHAIN-READBACK-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: Phase 3B guest admission needs a new owner decision.**
The [read-only review](docs/PHASE-3B-POST-EXTRACTION-ADMISSION-REVIEW-2026-10-20.md) records source dependencies and current VMware custody.
Both historical guests contain suspended-state files. The Phase 3B VM and ISO now use 25,752,367,104 allocated host bytes.
The [separate-guest proposal](docs/PHASE-3B-SEPARATE-GUEST-CAPACITY-PROPOSAL-2026-10-20.md) defines one bounded clone attempt.
The single ledger keeps that attempt, installation, Linux tests, and evaluation closed pending exact decisions.
Use the [next prompt](docs/PHASE-3B-GUEST-DECISION-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-GUEST-DECISION-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: The approved four-archive extraction completed once.**
The [completion record](docs/PHASE-3B-REMAINING-EXTRACTION-COMPLETION-2026-10-20.md) records the commands, readback, costs, and limits.
The new output contains 6,208 verified regular files, 3,859,951,638 content bytes, and 37 Swift links.
All 16 archive hashes, both receipt hashes, both output manifests, and frozen Phase 3A checks passed.
The new image stayed below its 7 GiB allocation cap. Mounted and host free space stayed above their floors.
The single ledger closes further extraction. Installation, guest work, Linux tests, and evaluation remain closed.
Use the [next prompt](docs/PHASE-3B-POST-REMAINING-EXTRACTION-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-POST-REMAINING-EXTRACTION-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: Four remaining archives passed local extractor source checks.**
The [source checkpoint](docs/PHASE-3B-REMAINING-EXTRACTOR-SOURCE-2026-10-20.md) records 52 tests and four read-only archive preflights.
The [proposal](docs/PHASE-3B-REMAINING-ARCHIVE-PROPOSAL-2026-10-20.md) binds one new image and one extraction attempt.
The single ledger keeps image creation and extraction closed until the owner approves that exact proposal.
The prior twelve-archive output, all 16 archives, both receipts, and frozen Phase 3A custody remain intact.
Installation, archived tool execution, guests, Linux tests, and evaluation remain closed.
Use the [next prompt](docs/PHASE-3B-REMAINING-EXTRACTION-DECISION-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-REMAINING-EXTRACTOR-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 20: The approved bounded retained extraction completed once.**
The follow-up `0.17.2` ledger correction distinguishes completed extraction from the remaining campaign blockers.
The [completion record](docs/PHASE-3B-RETAINED-EXTRACTION-COMPLETION-2026-10-20.md) records its checks and limits.
The output contains twelve selected archives, 11,019 verified regular files, and three recorded Node links.
The regular content totals 511,667,961 bytes. Mounted free space stayed above the required floor.
Both receipts, all 16 archives, the fixed image, and frozen Phase 3A custody passed read-only checks.
The [single ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes further extraction.
Installation, archived tool execution, guests, Linux tests, and evaluation remain closed.
Use the [next prompt](docs/PHASE-3B-POST-EXTRACTION-NEXT-SESSION-2026-10-20.md) and [exact inputs](docs/PHASE-3B-POST-EXTRACTION-INPUTS-2026-10-20.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 19: Local retained extractor source acceptance passed.**
The [source checkpoint](docs/PHASE-3B-RETAINED-EXTRACTOR-SOURCE-2026-10-19.md) binds twelve archive IDs and the exact content and free-space limits.
Nineteen synthetic extractor tests and 22 related tests passed. All retained inputs passed read-only custody checks.
The [single admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) still denies extraction.
The [separate decision proposal](docs/PHASE-3B-RETAINED-EXTRACTION-DECISION-2026-10-19.md) defines one possible extraction attempt.
No retained archive was extracted, installed, or executed. No guest, Linux test, native turn, or evaluation row ran.
Use the [next prompt](docs/PHASE-3B-RETAINED-EXTRACTION-DECISION-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-RETAINED-EXTRACTOR-SOURCE-INPUTS-2026-10-19.json) after the owner resolves that decision.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 19: A bounded retained extraction proposal is ready for source work.**
The [proposal](docs/PHASE-3B-RETAINED-EXTRACTION-PROPOSAL-2026-10-19.md) selects 12 archives with 511,667,961 regular content bytes.
It keeps four large archives retained and sets a 536,870,912-byte mounted free-space floor.
The single [admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) keeps extraction, installation, and execution closed.
Both receipts, all 16 archives, and the fixed image passed read-only custody checks.
Use the [next prompt](docs/PHASE-3B-RETAINED-EXTRACTION-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-RETAINED-EXTRACTION-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 19: Read-only inspection covered all 16 retained archives.**
The [inspection record](docs/PHASE-3B-RETAINED-ARCHIVE-INSPECTION-2026-10-19.md) records 19,978 members and regular content bounds.
Both `.NET` tarballs contain noncanonical `./` paths. Node and Swift contain 40 links in total.
The combined 4,371,619,599-byte regular content bound exceeds the current retained-data cap.
No archive was extracted or executed. Use the [next prompt](docs/PHASE-3B-RETAINED-ARCHIVE-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-RETAINED-ARCHIVE-INPUTS-2026-10-19.json).
All body requests, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

**October 19: The approved archive continuation retrieved and verified all eight remaining archives.**
Seven archives matched pinned digests. Swift passed detached-signature verification under the pinned key.
The original failed receipt remains halted. The new receipt records eight successful attempts and no incomplete read.
The [completion record](docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-COMPLETION-2026-10-19.md) gives commands, hashes, charges, and limits.
The cumulative conservative charge is 10,008,484,533 bytes. All further body requests are closed.
Use the [next prompt](docs/PHASE-3B-CAPPED-ARCHIVE-COMPLETE-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAPPED-ARCHIVE-COMPLETE-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.

**October 19: The halted archive continuation is ready for a separate owner decision.**
The new transport binds the original halted receipt and rejects all eight attempted IDs before network access.
Twelve offline tests cover redirects, errors, crash reservations, receipt changes, digest failures, and quota stops.
The [review record](docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-REVIEW-2026-10-19.md) fixes the receipt, commands, charges, and stop rules.
Swift still lacks a trusted full archive digest. The review proposes pinned signature-first verification.
No continuation receipt or selected archive body request exists. The prior 8,589,934,592-byte and current 311,183,922-byte charges remain intact.
Use the [next prompt](docs/PHASE-3B-CAPPED-ARCHIVE-REVIEW-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAPPED-ARCHIVE-REVIEW-INPUTS-2026-10-19.json).
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.

**October 19: The halted archive stage remains closed after custody and digest review.**
All 168 continuation inputs matched their recorded size and SHA-256.
The retained `.NET SDK` file matched its recorded length and SHA-512. Its original receipt remains failed.
The repaired transport passed local checks, but its hash differs from the original receipt binding.
Official sources supplied Bun and .NET targeting pack checksum inputs. Swift still lacks a bound archive digest.
The [continuation boundary](docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-BOUNDARY-2026-10-19.md) records the proposed new receipt and fixed charges.
Use the [next prompt](docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-INPUTS-2026-10-19.json).
No new archive body request or owner decision is admitted. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.

**October 19: The approved capped archive stage halted after a transport parser failure.**
The owner approved the exact sixteen-URL stage and its fixed caps.
Four source archives and three tool archives passed size and digest checks.
The frozen extractor matched all four source inventories.
The `.NET SDK` file matched its official SHA-512, but the transport recorded a false failure.
The repaired parser passed local tests. The original receipt remains halted, and no further body request is admitted.
The [boundary record](docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-2026-10-19.md) records 260,852,274 actual body bytes and a 311,183,922-byte conservative charge.
Use the [next prompt](docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 19: A capped archive evidence stage is ready for one owner scope decision.**
The [single admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now separates this exact stage from the full campaign.
The [stage proposal](docs/PHASE-3B-CAPPED-ARCHIVE-STAGE-2026-10-19.md) limits sixteen URLs and caps new transfer at 2,232,012,187 bytes.
It caps retained logical data at 3,221,225,472 bytes and adds no guest or VM allocation.
The stage needs owner approval and verified transport and storage controls before any archive body request.
The full Linux campaign remains blocked by archive, Ubuntu, dependency, and operational gates.
Use the [next prompt](docs/PHASE-3B-CAPPED-ARCHIVE-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAPPED-ARCHIVE-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

**October 19: Exact campaign batch closure remains blocked after Ubuntu and npm metadata review.**
The [single admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records ten tool package or archive byte counts and four source archive byte counts.
The [latest boundary](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-METADATA-BOUNDARY-2026-10-19.md) records four missing npm counts and unresolved archive and dependency closures.
The known prospective subtotal is 1,118,368,549 bytes. It is a lower bound, not an admission ceiling.
The old transfer balance remains zero. The exact batch cannot support a changed-limit approval request.
Use the [next prompt](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-CONTINUATION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-METADATA-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identities, native baselines, Phase 3B calibration, and Phase 3C remain closed.

**October 19: Exact campaign batch closure remains blocked after read-only metadata checks.**
The [single admission ledger](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now binds eight tool archive byte counts and four source archive byte counts.
The [latest boundary](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-BLOCKED-2026-10-19.md) records six missing tool byte counts and unverified archive and dependency closures.
The known prospective archive subtotal is 1,107,938,715 bytes. It is a lower bound, not an admission ceiling.
The old transfer allowance has zero conservative remaining balance. No changed-limit approval request is ripe.
Use the [next prompt](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAMPAIGN-BATCH-CLOSURE-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identities, native baselines, Phase 3B calibration, and Phase 3C remain closed.

**October 19: Consolidated Linux campaign admission remains blocked.**
The [campaign manifest](docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) binds four source archives, a candidate extractor, and the B1 stage order.
The [boundary record](docs/PHASE-3B-CAMPAIGN-ADMISSION-BOUNDARY-2026-10-19.md) records missing toolchain, dependency, launch, and resource bounds.
The old transfer allowance still has zero conservative remaining balance.
No changed-limit approval was requested because the exact batch is incomplete.
Use the [next prompt](docs/PHASE-3B-CAMPAIGN-ADMISSION-NEXT-SESSION-2026-10-19.md) and [exact inputs](docs/PHASE-3B-CAMPAIGN-ADMISSION-INPUTS-2026-10-19.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identities, native baselines, Phase 3B calibration, and Phase 3C remain closed.

**October 18: Core source work is ready for consolidated Linux campaign admission.**
The [source-ready record](docs/PHASE-3B-SOURCE-READY-2026-10-18.md) reports 196 passing Mac tests and unchanged frozen Phase 3A bytes.
The fresh offline wheel passed the same 196 tests.
The [campaign plan](docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-2026-10-18.md) records later limits, input binding, qualification, and cleanup.
Linux tests remain deferred. The old transfer allowance has zero conservative remaining balance.
Use the [next prompt](docs/PHASE-3B-SOURCE-READY-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-SOURCE-READY-INPUTS-2026-10-18.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native baselines, and provider identity remain unknown. Phase 3B calibration and Phase 3C have not started.

**October 18: Local Mac development precedes all remaining Linux tests.**
The owner stopped Linux testing during development under [ADR 0009](docs/decisions/0009-local-development-before-consolidated-linux-testing.md).
Use the local macOS checkout for remaining source work and deterministic offline checks.
The [current order record](docs/PHASE-3B-LOCAL-DEVELOPMENT-ORDER-2026-10-18.md) preserves operational limits and unknowns.
The [next prompt](docs/PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-LOCAL-DEVELOPMENT-INPUTS-2026-10-18.json) govern continuation.
The earlier Linux toolchain prompt is dated history. Phase 3B calibration and Phase 3C remain closed.

**October 18: Phase 3B toolchain amendment remains blocked after a second read-only review.**
The [current boundary](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-BOUNDARY-2026-10-18.md) records exact known ledgers and failed guest console access.
The [candidate manifest](docs/PHASE-3B-LINUX-ARM64-TOOLCHAIN-MANIFEST-2026-10-18.json) pins available official metadata and marks missing admission fields unknown.
The proposed 16 GiB guest-visible RAM rule, 40 GiB VM-plus-ISO ceiling, and 16 GiB cumulative transfer ceiling need owner approval.
The old 8 GiB transfer allowance remains fully charged under conservative accounting.
No retrieval, installation, VM change, provider request, or calibration occurred.
Use the [next prompt](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-CONTINUATION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-CONTINUATION-INPUTS-2026-10-18.json).
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: Phase 3B toolchain amendment remains blocked after official artifact review.**
The [current checkpoint](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-CHECKPOINT-2026-10-18.md) records the exact transfer ledger and new vendor metadata.
The installer transfer remains unknown, so the approved 8 GiB transfer allowance has zero conservative remaining balance.
The guest-visible RAM and storage interpretation still require owner approval.
Exact archive bytes, extraction bounds, dependencies, and executable hashes remain incomplete.
The frozen package and 135 starting input hashes pass read-only checks.
Use the [next prompt](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-TOOLCHAIN-AMENDMENT-INPUTS-2026-10-18.json).
No installation, provider request, calibration, or sealed exposure occurred.
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: Phase 3B toolchain preparation remains blocked.**
The frozen package checker passes with 23 artifacts and 768 planned units.
The Ubuntu guest remains disconnected. Its selected tools are still absent, and its guest-visible RAM is below 16 GiB.
Installer logs show rounded fetch totals, but they do not establish exact transfer bytes.
The [amendment draft](docs/PHASE-3B-TOOLCHAIN-PREPARATION-BLOCKED-2026-10-18.md) proposes a guest-visible RAM rule and separate infrastructure ledger.
It also records official artifact candidates and missing digests, sizes, dependencies, and install commands.
The draft is incomplete and grants no installation or retrieval authority.
Use the [next prompt](docs/PHASE-3B-TOOLCHAIN-PREPARATION-NEXT-SESSION-2026-10-18.md) and [exact input index](docs/PHASE-3B-TOOLCHAIN-PREPARATION-INPUTS-2026-10-18.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed. Operational admission and Phase 3C remain closed.

**October 18: Phase 3B guest capacity readback stops on missing tools.**
The owner signed in to the separate Ubuntu guest without sharing its password.
The guest reports Linux arm64, four online CPUs, and 55,538,384,896 bytes free on `/var/tmp`.
Its 16 GiB VM configuration yields 16,728,174,592 guest-visible memory bytes.
RTK and eight selected tools are absent. Installed Python 3.12.3 differs from selected 3.12.15.
The [readback record](docs/PHASE-3B-GUEST-CAPACITY-READBACK-BLOCKED-2026-10-18.md) gives commands, results, costs, and limits.
Use the [next prompt](docs/PHASE-3B-GUEST-CAPACITY-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-GUEST-CAPACITY-INPUTS-2026-10-18.json).
The guest network remains disconnected. No tool installation, qualification, or calibration ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: The separate Phase 3B guest completed installation and reached login.**
The owner entered the new account credentials. The Ubuntu guest reached its login prompt after reboot.
The agent disconnected its network and installation media. The owner must sign in before guest capacity readback.
The installer's security-update transfer is unknown. The VM bundle and ISO directory together occupy more than 8 GiB.
No further retrieval can pass the approved accounting gate until these amounts and limits are resolved.
The [boot record](docs/PHASE-3B-GUEST-BOOT-BLOCKED-2026-10-18.md) gives exact observations, commands, costs, and unknowns.
Use the [next prompt](docs/PHASE-3B-GUEST-BOOT-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-GUEST-BOOT-INPUTS-2026-10-18.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: Separate Phase 3B guest reaches the Ubuntu account step.**
The owner controls the previous VMware guest and will manage its state.
A separate, nonshared Ubuntu arm64 guest has four virtual CPUs, 16 GiB RAM, and a 64 GB virtual disk.
The official Ubuntu Server 24.04.5 arm64 ISO passed its SHA-256 check.
The installer selected a 62.948 GB ext4 root partition and awaits owner entry of new account credentials.
Guest capacity readback, toolchains, native controls, provider identities, baselines, and calibration remain unverified.
The [guest record](docs/PHASE-3B-GUEST-PREPARATION-2026-10-18.md) gives commands, observations, limits, and costs.
Use the [next prompt](docs/PHASE-3B-GUEST-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-GUEST-INPUTS-2026-10-18.json).
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: Phase 3B limits approved; local guest capacity blocks preparation.**
The owner explicitly resumed platform and live qualification and approved the [Phase 3B batch limits](docs/PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md), including unknown subscription quota debit.
The selected local VMware Ubuntu VM was powered off and configured with 8 GiB RAM.
The proposal requires 16 GiB RAM before preparation, so no guest startup or calibration ran.
The [capacity record](docs/PHASE-3B-ADMISSION-CAPACITY-BLOCKED-2026-10-18.md) gives exact commands, results, and limits.
Use the [next prompt](docs/PHASE-3B-ADMISSION-CAPACITY-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-ADMISSION-CAPACITY-INPUTS-2026-10-18.json).
Operational admission and Phase 3C remain closed. Earlier dated entries remain historical records.

**October 18: Phase 3B admission proposal published; calibration remains closed.**
The frozen Phase 3A package and all 120 starting file hashes passed read-only checks.
The focused offline suite passed 108 tests.
The [admission proposal](docs/PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md) defines selected units, commands, controls, limits, and cleanup.
The owner has not approved Phase 3B spending or resumed platform and live qualification.
No calibration or sealed evaluation ran.
Use the [continuation prompt](docs/PHASE-3B-ADMISSION-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-ADMISSION-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3A complete; the source evaluation package is frozen.**
The owner approved agent annotation, delegated bounded selections, and selected zero evaluation spending.
The package retains twelve pinned repositories, all four stacks, independent annotations, and attributed adjudication.
It fixes 24 development tasks and 24 sealed task commitments under separate custody.
B0, B1, B2, P, both role assignments, thresholds, accounting, and 768 planned units are fixed.
Accepted ADR 0008 separates package acceptance from deferred native and platform qualification.
Operational admission stays closed. Phase 3B execution requires separate approval and qualified controls.
No calibration or sealed evaluation ran. Earlier dated entries remain historical records.
Use [the frozen package](docs/evaluation/phase-3a-frozen/README.md) and [completion report](docs/PHASE-3A-COMPLETION-2026-10-18.md).
Continue with [the Phase 3B prompt](docs/PHASE-3B-NEXT-SESSION-2026-10-18.md) and [exact inputs](docs/PHASE-3B-INPUTS-2026-10-18.json).

**October 16: Phase 3A preparation checkpoint; freeze blocked.**
The proposed package records 12 pinned public corpus candidates and preserves all four stacks.
It defines B0, B1, B2, P, both role assignments, task contracts, independent annotation, protocol proposals, and separate usage categories.
Fourteen fresh offline tests check package integrity and refusal behavior through existing interfaces.
Owner decisions, independent annotations, sealed task commitments, exact live identities, baseline conformance, and spending approval remain missing.
Operational execution admission remains closed. Phase 3A remains incomplete, and Phase 3B has not started.
Use [the package](docs/evaluation/phase-3a/README.md), [owner decisions](docs/PHASE-3A-OWNER-DECISIONS-2026-10-16.md), and [continuation prompt](docs/PHASE-3A-CONTINUATION-2026-10-16.md).
See [the preparation report](docs/PHASE-3A-PREPARATION-2026-10-16.md) for verification and limitations.
Earlier dated status entries remain historical records.

**October 16: Phase 2E software complete; platform and live qualification deferred.**
Both runtime role assignments pass deterministic external fixtures through the production coordinator.
The second adapter uses existing candidate capture, SQLite state, checks, evidence, and verdict rules.
Required review enforces resolved provider independence and the same confirmed project model.
Risk gates preserve planning approval, actual scope escalation, human conflict decisions, and fresh remediation evidence.
Source and installed-wheel suites each pass 1,305 test occurrences, including 57 Phase 2E methods.
All 49 packaged source files match the checkout.
Operational execution admission remains closed.
See [the completion report](docs/PHASE-2E-SOFTWARE-COMPLETION-2026-10-16.md) and [verification](docs/qualification/phase-2e-software-verification-20261016.json).
Phase 3A prepares the comparative evaluation package in a separate session.
Use [its prompt](docs/PHASE-3A-NEXT-SESSION-2026-10-16.md) and [exact input files](docs/PHASE-3A-INPUTS-2026-10-16.json).
No Phase 3A implementation or evaluation occurred.
Earlier dated status entries remain historical records.

**October 16: Phase 2D software complete; platform and live qualification deferred.**
The actual coordinator workflow passes deterministic external runtime and validator fixtures.
Checked request preparation and atomic validator capture join the existing candidate, evidence, durable state, and verdict code.
Source and fresh installed-wheel suites each pass 1,248 test occurrences, including 26 new core cases.
All 47 packaged source files match the checkout.
Operational execution admission remains closed.
See [the software completion report](docs/PHASE-2D-SOFTWARE-COMPLETION-2026-10-16.md) and [verification](docs/qualification/phase-2d-software-verification-20261016.json).
Use [the Phase 2E prompt](docs/PHASE-2E-NEXT-SESSION-2026-10-16.md) and [exact input files](docs/PHASE-2E-INPUTS-2026-10-16.json) next.
Phase 2E implementation has not started.
Earlier dated status entries remain historical records.

**October 15: Phase 2D is active and unblocked for core software development.**
[Accepted ADR 0007](docs/decisions/0007-core-development-before-platform-qualification.md) moves platform adaptation and live qualification after core development.
[The revised plan](docs/DEVELOPMENT-PLAN.md) requires a complete production coordinator workflow with deterministic external runtime and validator fixtures.
[The next-session prompt](docs/PHASE-2D-CORE-NEXT-SESSION-2026-10-15.md) directs implementation and verification.
Operational execution admission remains closed; platform support and live acceptance remain unverified.
Earlier blocked-status paragraphs below describe dated history.

Source checkpoint: **0.15.2**. Package registry publication remains unauthorized. See [CHANGELOG.md](CHANGELOG.md) for version history.

**October 11: Phase 2D remains blocked.** [The current report](docs/PHASE-2D-BLOCKED-2026-10-11.md) gives four causes and the exact continuation inputs. Fresh source checks pass all 863 offline tests, including 722 Phase 2D tests. Linux and live acceptance remain incomplete. The owner requires ASD-STE100 for human communication. Version 0.12.0 remains unchanged; this report is uncommitted. Earlier status paragraphs are dated records.

The owner explicitly authorized publishing the current blocked Phase 2D source checkpoint on October 10. [Version 0.12.0 checkpoint and publication evidence](docs/PHASE-2D-EFFECTIVE-OWNERSHIP-CHECKPOINT-2026-10-10.md) supersede earlier conditional publication statements for this checkpoint only. Phase 2D remains incomplete/unqualified; installation admission stays closed. [Next-session prompt and exact file list](docs/PHASE-2D-NEXT-SESSION-2026-10-10.md) continue the same effective ownership milestone. Branch publication grants no operational, spend, release/reuse, merge, deployment, package-registry or Phase 2E authority. Earlier status paragraphs below are dated history.

[Current effective-ownership blocker](docs/PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md): retained physical/journal/root, original-volume freeze, parent/observer capture bridge and separate validator source are prepared. Pinned stock app-server SQLite WAL requires shared file mappings that the current shmem filter denies. Full effective growth and installed parent/validator identities remain incomplete; bootstrap installation admission explicitly retains unknown and stays closed. All **863 / 722 Phase 2D offline methods** pass in source and fresh installed wheel. See the reproducible compatibility driver and immutable verification in that guide. Source remains unqualified/uncommitted at 0.11.0; no compiler, operational Linux/live run, commit/push or Phase 2E occurred. Earlier status paragraphs below are dated history.

[Accepted upfront installation bootstrap](docs/PHASE-2D-INSTALLATION-BOOTSTRAP-2026-10-10.md): the owner approved the same-original-observer lifecycle in [ADR 0006](docs/decisions/0006-upfront-installation-charge.md). Source commits a distinct full charge before creation, keeps unknown outcomes/handles, and permits one bounded root/backing-directory custody sequence under the original timer. **699 offline methods** pass; effective installed capacity/growth is still missing, so the new charge path deliberately denies native/validator admission. Full Phase 2D remains incomplete/unqualified and subsequent source uncommitted. No architecture decision remains pending for bootstrap; earlier pending statements below are dated history.

[Current growth/installation boundary](docs/PHASE-2D-GROWTH-BOUNDARY-2026-10-10.md): source adds inherited file-limit and actual ext4 inode/directory readback; three regression methods reproduce twelve predecessor failures. All **681 source offline methods** pass. Full 2D remains incomplete/unqualified. [One concrete original-owner installation-bootstrap decision](docs/PHASE-2D-INSTALLATION-BOOTSTRAP-DECISION-2026-10-10.md) is pending; the lifecycle amendment is unimplemented. Original limits, charges, handles and remaining Linux/live gates remain intact. Current additional source is uncommitted at 0.11.0; the following status paragraphs are dated history.

[Latest October 10 continuation](docs/PHASE-2D-TIMER-SYNTAX-PASS-2026-10-10.md): the explicitly approved 13411-byte timer syntax check passes, and all three syntax invocations are consumed. Separate idle-retention source verifies original helper cessation/reap and stopped operational roles without relaxing live admission or charges. **674 offline tests** pass in source and installed wheel. Full 2D remains incomplete and unqualified; effective capacity/growth, original frozen volume/validator and exact Linux/live gates remain unfinished. Current additional changes are uncommitted at 0.11.0; earlier pending statements below are history.

The owner authorized publishing the current verified 2D source and continuing development on October 10. [Version 0.11.0 checkpoint, authority and continuation](docs/PHASE-2D-CHECKPOINT-2026-10-10.md) supersedes the earlier conditional publication statements for this checkpoint only. Phase 2D remains incomplete and source unqualified; branch publication supplies no runtime, release or reuse authority.

Checkpoint `758079b` is pushed. [Continued timer and child-placement source](docs/PHASE-2D-BATCH-TIMER-2026-10-10.md) keeps the original observer outside stopped roles, binds operational jobs/readback to the original timer and setup, and preserves the fixed reserve without another recovery wait. All **669 offline tests** pass in source and installed wheel. The changed 13411-byte helper is uncompiled; one additional frozen syntax check awaits approval. Child birth/terminal mechanics, installed capacity/growth, actual frozen volume/validator and exact Linux/live qualification remain unfinished. Current additional changes are uncommitted at 0.11.0. Earlier status paragraphs and version references below describe dated history.

The preceding 0.10.0 source round implements accepted retention, official subscription preparation and owned filesystem/root/view production. [The latest October 10 record](docs/PHASE-2D-SYNTAX-PASS-2026-10-10.md) records the explicitly approved additional Ubuntu syntax check: unchanged 8011 C bytes pass, with empty stdout/stderr; both attempts remain consumed. Source tightens retained native/watchdog/parent readback before and after freeze and fixes canonical auth/validator mount directory creation. Reproduced false-stop, absent-target and concurrent-repopulation paths now refuse; complete source verification is in the linked ledger. Installed physical capacity/journal/growth, actual owned readonly frozen-view/validator and terminal timer mechanics, installed identities and exact Linux/live qualification remain unfinished. Phase 2D is incomplete and source unqualified. Syntax success supplies no broader runtime authority; commit/push follows full acceptance.

**Phases 0, 1, 2A, 2B and 2C complete.** Passive discovery, confirmed project models, private SQLite state, recovery contracts and deterministic evidence gates are implemented. Published 0.9.0 has **141 offline tests**. The 0.10.0 source checkpoint adds **332 Phase 2D offline methods** (473 complete tests); its required live gate remains incomplete. See [the checkpoint, current prompt and required inputs](docs/PHASE-2D-SOURCE-CHECKPOINT-2026-10-09.md) and [storage-owner evidence](docs/PHASE-2D-LINUX-STORAGE-OWNER.md).

The accepted direct Linux qualification route passes all **20 original cases twice on one complete v18 profile**, using the pinned native Codex runtime, official Responses proxy and synthetic local provider fixture. Both actual native file tools, `exec_command` and `write_stdin`, are exercised. Original grants and resource limits remain unchanged. The independent reader checks full records, source/configuration bindings, containment, credential mediation, validator isolation, cancellation and deadlines. See [the complete assessment and reproduction commands](docs/PHASE-2C-COMPLETION-ASSESSMENT.md).

Qualification applies to the observed local Linux aarch64 profile. Windows and macOS runtime compatibility remains unverified. Historical native/proxy subsets, failures and prepared variants remain intact; they do not combine into this pass. The lost v5 cause and original cleanup remain unknown. Current continuation cleanup is independently observed; the VM remains running and SSH is disconnected.

The [portable record audit](docs/PHASE-2C-OFFLINE-AUDIT.md) adds bounded offline consistency checks and refuses altered, incomplete or malformed bundles. Every audit and qualification decision retains false execution permission; the audit also always returns false runtime verification. No operational runtime launcher, production agent write, paid model call, deployment or registry release is included. Phase 2D needs its separate execution authorization.

Unpublished [Phase 2D offline work](docs/PHASE-2D-OFFLINE-CONTRACTS.md) adds inert pinned-Codex request/event normalization, disposable candidate/freeze manifests, scope comparison and trusted validator capture integrated with private SQLite evidence. The [Sol6.1 preparation bundle](docs/PHASE-2D-BATCH-PREPARATION.md) now materializes exact fixture/check bytes and a non-launchable dispatch template under the owner’s “Batch preparation only” scope. [Per-project/session selection and readback](docs/PHASE-2D-SESSION-SELECTION.md) adds explicit model/route choices with context-bound integrity refusal and no global or ambient selection. Production runtime/check execution remains unstarted. The [execution preparation](docs/PHASE-2D-EXECUTION-GATE.md) records missing production dispatch, exact live identities and execution/spend gates. Earlier preparation records were produced at 0.9.0; current maintenance version is 0.9.2. No Phase 2D implementation commit/push occurs before its complete acceptance gate.

[Coordinator capture integration](docs/PHASE-2D-PRODUCTION-CAPTURE.md) now binds a changed frozen candidate to durable state while retaining launch provenance, refusing old candidate approval transfer, and requiring final candidate/capture readback. Its 18 fresh tests also cover actual SQLite rollback and mutation after successful validation. This source integration launches no process and does not qualify production supervision or live execution.

[Source-bound dispatch preparation](docs/PHASE-2D-DISPATCH-PREPARATION.md) compiles literal pinned-native/proxy argv, separate task stdin and the prospective empty environment, then joins independently audited preparation to exact task/source/context/qualification bindings. Fourteen new methods reject altered settings, stale qualification and expanded fixture authority. The resulting data cannot launch; Linux supervision and the separately approved live gate remain missing.

The proposal uses a local Python coordinator with Codex and Claude Code adapters, subject to capability and isolation qualification. Implementation proceeds in bounded sessions. Agent writes require execution qualification; paid evaluation requires a confirmed protocol and spending ceiling.

[Bounded supervisor source](docs/PHASE-2D-SUPERVISOR-SOURCE.md) now captures an already admitted worker through separate bounded pipes, a retained child handle and independently read cgroup controls/population. It stops only the pinned owned subtree and persists the readback with terminal collection in one transaction. Twenty-four fresh offline cases use real descriptor/file/SQLite operations with explicitly synthetic child, clock and kernel-stop effects. No launcher or qualified production envelope is delivered; preparation-only scope and the separate execution/spend gate remain controlling.

[Physical teardown ordering and trusted parent inventory source](docs/PHASE-2D-OWNED-TEARDOWN.md) binds exact parent entry/copied-root/helper-library bytes, reads retained root contents and orders owned mount/keyring/loop/backing, FD and cgroup release only after independent terminal readback. Forty-six fresh methods pass; twenty current sources bind dispatch. Unknown cleanup stops later effects and retains remaining handles; every reuse result stays false. At that boundary, concrete Linux storage-owner source, actual parent installation/loader identity, effective controls, exact qualification and separate live acceptance remained missing. No real startup or kernel effect occurred.

[Retained Linux storage-owner source](docs/PHASE-2D-LINUX-STORAGE-OWNER.md) now reads pinned namespace/mount/keyring/loop/backing identities and supplies fixed-deadline operation source. Empty reference scans remain unknown: effective closure of taskless namespaces and asynchronous/deleted-open kernel references is still missing, so actual physical teardown is blocked. Forty-six added methods bring offline coverage to 332 Phase 2D / 473 complete tests; twenty-one sources bind dispatch. No fork, compiler, startup, kernel operation or live qualification occurred.

[Owned setup and terminal process lifetime source](docs/PHASE-2D-OWNED-SETUP.md) adds sealed retained controls, bounded observer/setup/supervisor/worker siblings under the original aggregate, namespace-local parent attachment, fixed-FD watchdog creation before worker creation and one-grace terminal readback. Thirty-five fresh methods pass; eighteen current sources bind dispatch. The original stopped native admission and ceilings remain unchanged. Physical mount/key/backing cleanup, qualified parent/root/helper inventories, effective containment, exact Linux qualification and the separate live gate remain missing. Every reuse/authority result stays false; no real startup, C compilation or host effect occurred.

[Parent/watchdog bridge source](docs/PHASE-2D-PARENT-WATCHDOG.md) verifies retained namespace-parent/watchdog identities, effective timer/kill/lifeline readback and readiness before direct Popen creation through inherited worker placement. Initial traced attachment remains separate from unchanged native admission. Twenty-three fresh methods passed; seventeen source files bound dispatch at that earlier boundary. All kernel/startup effects were synthetic. Its remaining setup/lifetime work is continued in the owned setup guide; helper compilation, effective containment and exact Linux/live qualification remain missing. Startup and spend stay disabled.

[Owned bootstrap source](docs/PHASE-2D-OWNED-BOOTSTRAP.md) adds a packaged, uncompiled Linux helper and bounded helper-to-native exec-stop handoff ending at unchanged stopped admission. Separate watchdog source arms the original five-second timer before readiness; Python refuses reset/stale acknowledgements and recovers only retained owned workers. Twenty-five fresh methods passed offline; sixteen source files bound dispatch at that earlier source boundary. Kernel/child/timer effects remain synthetic. Qualified namespace-resident direct-Popen placement, actual watchdog/containment enforcement, Linux helper compilation and approved live acceptance remain missing; all readiness/authority flags stay false.

## Intended workflow

[Linux envelope preparation](docs/PHASE-2D-LINUX-ENVELOPE.md) binds prospective role/mount/argv, original systemd/controller ceilings, storage reservations and unchanged stopped-native checkpoint requirements to each project/session dispatch. Eighteen fresh methods exercise exact readback and refusal. Fourteen package sources bound configuration at that earlier preparation boundary; prospective hashes supply no effective enforcement or startup authority. Production bootstrap/deadline/recovery, exact Linux qualification and separately approved live acceptance remain missing. Version stays 0.9.2; no implementation commit/push occurs at this incomplete boundary.

[Durable admission/collection linkage](docs/PHASE-2D-ADMISSION-COLLECTION.md) now persists the retained native receipt with supervised collection in one SQLite transaction. Private scope/supervision links and final readback reject stale or altered receipt/clock/identity and missing admission evidence. Fifteen fresh offline cases cover real rollback and restart; process/kernel effects are synthetic. Maintenance version stays 0.9.2; Phase 2D implementation remains uncommitted pending complete offline and separately approved live acceptance.

1. Inspect an unfamiliar repository without executing its instructions.
2. Propose project facts, validation commands and engineering boundaries with provenance and uncertainty.
3. Ask the human operator to correct and confirm the project model.
4. Coordinate bounded work through existing coding runtimes.
5. Capture deterministic checks and independent review where required.
6. Support completion with evidence tied to the candidate revision.

Steps 1–3 are implemented for the bounded Python/TypeScript formats documented in [the development guide](docs/DEVELOPMENT.md). [Durable state and evidence rules](docs/STATE-AND-GATES.md) support the contracts for steps 4–6; those steps still have no runtime launcher or check executor. The owner retains authority over consequential actions. Implementation is clean and independent; proprietary predecessor code, prompts, configurations and artifacts are excluded.

Historical SBX investigation: the owner [approved the exact operational resource envelope](docs/RESOURCE-APPROVAL-AND-FREEZE-STATUS.md). A [new current host and immutable candidate artifacts](docs/CURRENT-HOST-IDENTITY-PREPARATION.md) are verified. Package **0.8.8** records [approved bounded discovery and actual supported-create refusal](docs/GUEST-DISCOVERY-ASSESSMENT.md). Prospective aggregate/controller/device bounds are observed in fresh private services; KVM HLT passes twice per service after an initial device-policy failure. Both mountless SBX create attempts return `401 Unauthorized` requiring Docker sign-in. Login is excluded by the approved discovery scope, so no SBX guest, complete operational freeze or inner qualification is delivered. Historical discovery/resource approval is resolved; current host retention is superseded by the 2026-10-05 cost policy. Historical profiles remain immutable. Version 0.8.10 preserves exact executed-source trailing bytes through narrowly scoped whitespace attributes; no host rerun or qualification change.

## Development sessions

The October 8 ownership transfer is recorded in [the transfer checkpoint](docs/REPOSITORY-TRANSFER-2026-10-08.md). Version 0.9.1 changes repository ownership metadata only; it does not complete or publish pending Phase 2D implementation.

Work proceeds one phase or major milestone per session. Read the [rolling handoff](docs/HANDOFF.md), [development plan](docs/DEVELOPMENT-PLAN.md), [current Phase 2D continuation and exact inputs](docs/PHASE-2D-CONTINUATION-2026-10-08.md), and [preserved Phase 2C input index](docs/PHASE-2C-ACTIVE-CONTINUATION.md). [AGENTS.md](AGENTS.md) records the persistent session contract. The owner's October 8 local VMware resumption superseded the earlier test stop. That qualification batch is complete. The owner authorized committing and pushing the verified Phase 2D source checkpoint on October 9. This authorizes branch publication only; resume effective reference closure in 2D, not 2E.

Each completed milestone ends with version, README, changelog and handoff updates, followed by a commit and remote branch push. See [the standing publishing rules](AGENTS.md). Development stops at the milestone boundary.

## Try passive initialization

Python 3.12+ is required; macOS arm64/Python 3.12.14 is the verified environment. From this checkout:

```sh
rtk proxy uv venv --python python3.12 .venv
rtk proxy uv pip install --python .venv/bin/python --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python .venv/bin/python --no-deps -e .
rtk proxy .venv/bin/crewshal --help
rtk proxy .venv/bin/crewshal init /path/to/repository --interactive
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_substrate
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_lifecycle
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_network
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_protocol
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_broker_environment
```

Without `--interactive` or an explicit decision batch, facts remain pending. No discovered command runs. State stays outside the target repository; exports require `--export` and never become execution approvals. See [setup, limits and verification](docs/DEVELOPMENT.md).

Existing Phase 2A JSON state requires explicit `--migrate-state` on `init` or `show`; the original private JSON remains unchanged as a backup. New writes use SQLite. Unknown database/record versions are refused. No verdict or qualification record grants execution; production runtime startup and agent writes require separate authorization in Phase 2D.

## Research and decisions

- [Product hypothesis and owner brief](PRODUCT-HYPOTHESIS.md)
- [Competitive landscape and naming](COMPETITIVE-LANDSCAPE.md)
- [Predecessor concept audit](AUDIT.md)
- [Initial evaluation plan](INITIAL-EVALUATION-PLAN.md)
- [Phase 0 closure and remaining gates](docs/PHASE-0-CLOSURE.md)
- [Accepted minimal architecture](docs/ARCHITECTURE.md)
- [Accepted architecture decision](docs/decisions/0002-minimal-architecture.md)
- [Accepted name and repository initialization](docs/decisions/0001-name-and-repository.md)

The current recommendation is to narrow the product to confirmed repository adaptation and portable evidence, and evaluate it against simpler workflows and existing tools before broader development.

## Get the repository

```sh
git clone https://github.com/forera-ai/Crewshal.git
cd Crewshal
```

Use **Crewshal** as the display name and `crewshal` for local command and package identifiers. The package has not been published or its index name reserved.

## Contributing

Contributions should follow the active milestone and its acceptance gates. Open an issue to discuss architecture or runtime changes before submitting them. Keep private source, credentials and raw confidential run artifacts out of the repository.

## License

[Apache License 2.0](LICENSE). Copyright 2026 forera.ai and contributors.

[Retained native admission source](docs/PHASE-2D-NATIVE-ADMISSION.md) now checks a stopped child through pinned proc/pidfd handles, exact native role/configuration/executable/namespace and pipe identity, actual worker/aggregate ancestry and original resource controls. Twenty-eight fresh offline cases bring unpublished coverage to 124 Phase 2D methods / 265 tests. Kernel/proc/child effects are synthetic; Linux operation, envelope/bootstrap, hard deadline, receipt persistence and separately approved live acceptance remain unqualified. Preparation-only scope persists.

## Phase 2D candidate preparation — 2026-10-13

Version 0.13.0 is an unreleased source candidate.
Phase 2D has not passed Linux or live acceptance.
The candidate includes the accepted three lanes, charged builds, original timer, and retained installation and validation owners.
Publication remains conditional on complete Phase 2D acceptance.
See [the input contract](docs/PHASE-2D-EXECUTABLE-BATCH-INPUTS-2026-10-12.md) for the remaining operational requirements.


Phase 2D continuation, October 13: the corrected source and fresh wheel pass 1158 test occurrences and 1142 unique methods.
All 47 packaged files match current source.
Independent readback passes 33 actual mapped ranges after the kernel address spelling correction.
Actual installation, both twenty-case qualifications, and live acceptance remain incomplete.
[The exact v8 operational proposal](docs/PHASE-2D-MAPPING-CONTINUATION-2026-10-13.md) requires a separate combined reservation exception.
No new C or AppArmor compilation, login, live turn, publication, or Phase 2E work has occurred.
# October 13 private executable preparation

The approved v8 batch refused Ubuntu's 116-link env inode before either compiler started.
The original observer retains its fourth full charge, timer, empty compiler volume, handles, clock, and unknown result.
The [exact private file continuation](docs/PHASE-2D-SINGLE-LINK-CONTINUATION-2026-10-13.md) supplies identical bytes through a private read-only binding.
The production single-link check remains unchanged.
All 227 new archive members pass local hash and size checks.
Both 1158-test suite results remain current because all production and test source hashes remain unchanged.
The new batch requires its exact 40 GiB combined reservation exception.
Phase 2D remains incomplete. Version 0.13.0 remains unreleased.

## October 13 build mapping correction

The v9 C executable reached its original trace stop, then its separate mapping reader refused a padded kernel address.
The consumed C process, zero-byte outputs, fifth full charge, timer, handles, clock, and unknown result remain retained.
The build reader now uses the shared strict numeric parser.
Both complete source and fresh-wheel suites pass 1161 tests.
Independent reader execution passes all 33 retained kernel ranges without another compiler execution.
The [exact additional batch](docs/PHASE-2D-BUILD-MAPPING-CONTINUATION-2026-10-13.md) requires a 48 GiB reservation and additional C compiler exception.
Phase 2D remains incomplete. Candidate version 0.13.0 remains unreleased.

## October 13 operational decline

The owner declined the exact v10 additional batch and its reservation and compiler exception.
No v10 operational command ran, and no additional charge was created.
Fresh readback preserves all five prior journal hashes and current original custody identities.
IPv4 forwarding remains zero.
Both complete suites pass 1161 tests, but actual Phase 2D acceptance remains incomplete.
Candidate version 0.13.0 remains unreleased. No publication or Phase 2E work occurred.

## October 13 next-session context

The [next-session prompt](docs/PHASE-2D-NEXT-SESSION-2026-10-13.md) and exact input manifest preserve the owner decline and current Phase 2D boundary.
The accompanying public context ZIP includes current source, tests, accepted decisions, and dated evidence.
Private capabilities and operational archives remain outside the bundle.
Context preparation supplies no additional operational or publication authority.
