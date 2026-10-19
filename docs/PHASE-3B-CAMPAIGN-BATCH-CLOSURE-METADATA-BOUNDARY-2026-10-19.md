# Phase 3B exact campaign batch closure metadata boundary

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `779b2c17c23fa6bc3f6f0b4edd53ea3b10df9a7d`.
Status: blocked. No campaign operation or changed-limit request is admitted.

## Read-only result

All 159 continuation files matched their recorded byte counts and SHA-256 hashes. The entry worktree was clean.
The canonical remote was `https://github.com/forera-ai/Crewshal.git`.
The frozen Phase 3A checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
No frozen package byte changed.

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now records two Ubuntu package candidates.
[Ubuntu's CMake page](https://packages.ubuntu.com/noble/arm64/cmake/download) names `cmake_3.28.3-1build7_arm64.deb`.
It gives 10,305,022 bytes and SHA-256 `0bf2a58f636ad286e7f4552e709dfd1209a4d70056548a6c0c4965d7067e95a5`.
[Ubuntu's Ninja page](https://packages.ubuntu.com/noble/arm64/ninja-build/download) names `ninja-build_1.11.1-2_arm64.deb`.
It gives 124,812 bytes and SHA-256 `b261a758b0c07e7ffa0d56b34e577d5c2d0122aa14f806a176e9b2609b2706b0`.
These pages provide package metadata. No package body or exact Ubuntu repository snapshot was read.
The selected package URLs, installed versions, transitive packages, and installed closure remain unbound.

Official npm version metadata returned for all four selected runtime tarballs.
The four successful JSON responses totaled 12,488 bytes.
Their `dist` records gave integrity, tarball URLs, file counts, and unpacked sizes, but no compressed tarball byte counts.
An initial wrong-version Codex native query returned HTTP 404; the exact selected `0.160.1-linux-arm64` query returned HTTP 200.
An npm request with the compact metadata `Accept` header returned HTTP 406; the JSON request succeeded.
The web tool could not open the Ninja download page directly; its package-detail link opened the same page.
No npm tarball body was read. Unpacked sizes do not bound compressed tarball bytes or safe extraction.

Ten tool package or archive byte counts now appear in the ledger, alongside four selected source archive counts.
The ten tool counts total 1,115,591,267 bytes. The four source archives add 2,777,282 bytes.
The prospective known subtotal is 1,118,368,549 bytes. It is a lower bound, not a transfer ceiling.
Four npm tarballs still lack exact compressed byte counts.
Safe member inventories, extraction bounds, Ubuntu closure, and repository dependency closures remain unknown.
The source inventory's file bytes do not prove archive header safety, extraction space, or disk allocation.
The source extractor remains unrun against every selected archive because archive access and transfer remain closed.

## Resource and decision boundary

The original transfer ceiling is 8,589,934,592 bytes.
The known ISO and checksum used 3,825,518,142 bytes.
The unknown installer transfer keeps its full 4,764,416,450-byte conservative charge.
The original transfer balance remains zero bytes.

The proposed 17,179,869,184-byte cumulative ceiling would leave 8,589,934,592 bytes after the historical full charge.
Known prospective archives would leave 7,471,566,043 bytes of that proposed headroom.
This remainder excludes four npm tarballs, dependency packages, signatures, metadata, retries, and any other missing transfer.
It is not an approved allowance or an exact batch transfer upper bound.

The last recorded VM-plus-ISO host allocation was 9,093,566,464 bytes.
No current host allocation, future guest-disk growth bound, or retained batch-data upper bound was observed.
The proposed 17,179,869,184-byte guest-visible RAM rule and 42,949,672,960-byte infrastructure ceiling remain unapproved.
The retained-data interpretation and transfer increase also remain unapproved.
The exact batch is not reviewable, so no owner decision is requested.

The smallest missing capability is admitted access to exact archive bytes and pinned package snapshots under an independently bounded transfer stage.
That stage changes scope and needs a reviewable ceiling before an approval request.
Actual Linux executable hashes, effective native commands, provider identities, and B1 conformance remain later admitted observations.
Their fields remain null.

## Verification, costs, and limits

Environment: Darwin 27.2.0 arm64, Python 3.12.15, RTK 0.51.0.
The Crewshal graph generation was `2026-10-19T10:24:13Z`.
Coverage metadata recorded no issue for the extractor and its synthetic test.
This best-effort signal does not prove complete source coverage or Linux behavior.

| Command or check | Result |
| --- | --- |
| `rtk git status --short --branch` and `rtk proxy git rev-parse HEAD` | Clean entry worktree at the revision above. |
| SHA-256 and size check of every continuation-index file | 159 files matched; zero failures. |
| Read-only Ubuntu Noble arm64 download pages | CMake and Ninja candidate size and SHA-256 metadata recorded. |
| Read-only npm version JSON for four selected tarballs | Four HTTP 200 responses; compressed byte counts absent. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts and 768 planned units. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' .venv/bin/python -m unittest tests.acceptance.test_phase3b_extract_source` | Three synthetic tests passed. |
| JSON parsing, ledger arithmetic, synchronized versions, and `rtk proxy git diff --check` | Passed. |
| SHA-256 and size check of the new continuation index | 162 files matched; zero symbolic links. |

Read-only Ubuntu web response bytes were not measured.
No artifact body, selected source archive, guest, Linux test, installation, provider request, evaluation row, or Jev call ran.
No new campaign resource required cleanup.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat remains unknown.
Linux-specific acceptance modules remain deferred, not passing.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native baselines, provider identities, Phase 3B calibration, and Phase 3C acceptance remain closed.

Use the [next prompt](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-CONTINUATION-2026-10-19.md) and its exact input index.
