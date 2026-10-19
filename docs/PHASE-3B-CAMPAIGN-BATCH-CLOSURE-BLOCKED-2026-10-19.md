# Phase 3B exact campaign batch closure boundary

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `b5259f2505b74c4059ee72940463e18fa357d2a0`.
Status: blocked. No campaign operation or changed-limit request is admitted.

## Local result

All 156 files in the continuation index matched their recorded byte counts and SHA-256 hashes.
The worktree was clean at entry. The canonical remote was `forera-ai/Crewshal`.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
No frozen Phase 3A byte changed.

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now records seven additional exact HTTP `Content-Length` values.
The values came from `HEAD` requests to the selected URLs. No archive body was read.
The RTK release API gave the same size and the previously recorded digest.
The Bun release API gave the same size but no asset digest.

| Artifact | Observed archive bytes |
| --- | ---: |
| RTK 0.51.0 arm64 | 4,483,862 |
| Node.js 22.14.0 arm64 | 28,636,440 |
| Bun 1.2.2 arm64 | 36,226,213 |
| Swift 6.0.3 arm64 | 774,149,705 |
| .NET SDK 9.0.100 arm64 | 204,124,866 |
| .NET runtime 8.0.11 arm64 | 29,865,496 |
| .NET targeting pack 8.0.11 | 6,845,027 |

The earlier CPython archive count remains 20,829,824 bytes.
Eight known tool archives total 1,105,161,433 bytes.
Four frozen source archives add 2,777,282 bytes.
The 1,107,938,715-byte known prospective subtotal is a lower bound, not an admission ceiling.

Four npm tarball `HEAD` replies omitted `Content-Length`.
CMake and Ninja still lack pinned Ubuntu versions and package artifacts.
These six entries have no exact archive or package byte count in the ledger.
The npm version metadata reports unpacked size for one wrapper, but it does not bound its compressed tarball.

The frozen source inventory binds 1,082 files and 7,567,354 expanded content bytes across four selected repositories.
It does not prove archive header safety, directory members, extraction metadata, or disk allocation.
The extractor was not run against a selected archive because archive access and transfer remain closed.
Three network-denied synthetic extractor tests passed again.

The frozen Python constraints and TypeScript locks do not bind the bytes of their package archives.
The selected Swift and .NET repositories have no recognized lockfile in the frozen inventory.
No exact Noble arm64 repository snapshot or transitive Ubuntu package set is bound.
Package versions, digests, license results, download bytes, retained bytes, and read-only dependency snapshots remain unknown.

## Resource and decision boundary

The original transfer ceiling is 8,589,934,592 bytes.
The known ISO and checksum used 3,825,518,142 bytes.
The installer transfer has no exact count. Conservative accounting charges the remaining 4,764,416,450 bytes in full.
The current transfer balance is zero bytes.

The proposed 17,179,869,184-byte cumulative ceiling would leave 8,589,934,592 new bytes after that full historical charge.
Known prospective archives would leave 7,481,995,877 bytes within that proposed headroom.
This remainder does not account for six missing artifacts, package closures, signatures, metadata, or retries.
It is not an approved allowance or a transfer upper bound.

The last VM-plus-ISO allocation was 9,093,566,464 bytes.
No current host allocation, future guest-disk growth bound, or retained batch-data upper bound was obtained.
The proposed 16 GiB guest-visible memory rule, 40 GiB infrastructure ceiling, retained-data interpretation, and transfer increase remain unapproved.
The exact campaign batch is not reviewable. No owner decision is requested at this boundary.

The smallest missing input is admitted access to immutable archive bytes and exact package snapshots under an independently bounded transfer stage.
That stage requires a changed scope. It cannot be inferred from public headers or frozen source declarations.
Actual Linux executable hashes, effective native commands, provider identities, and B1 conformance remain later admitted observations.

## Verification and limits

Environment: Darwin 27.2.0 arm64, Python 3.12.15, RTK 0.51.0.
The Crewshal graph generation was `2026-10-19T09:38:02Z`.
Coverage metadata reported no recorded issue for the extractor, its test, and both dispatch source paths.
This best-effort result does not prove complete source coverage or Linux behavior.

| Command or check | Result |
| --- | --- |
| `rtk proxy git status --short --branch` and `rtk proxy git rev-parse HEAD` | Clean entry worktree; entry revision above. |
| SHA-256 and size check of every continuation-index file | 156 files matched; zero failures. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units. |
| Read-only GitHub release JSON for RTK and Bun | Exact asset sizes matched `HEAD`; Bun asset digest absent. |
| `HEAD` on eleven selected URLs | Seven exact lengths; four npm replies lacked lengths. No archive body read. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' .venv/bin/python -m unittest tests.acceptance.test_phase3b_extract_source` | Three tests passed. |
| `rtk proxy git diff --check` and JSON parsing | Passed after the ledger update. |

Read-only HTTP metadata response bytes were not measured. No artifact body or selected source archive was downloaded.
No guest, Linux test, installation, provider request, evaluation row, or Jev call ran.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat remains unknown.
Linux-specific acceptance modules remain deferred, not passing.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native baselines, provider identities, Phase 3B calibration, and Phase 3C acceptance remain closed.

Use the [next prompt](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-NEXT-SESSION-2026-10-19.md) and its exact input index.
