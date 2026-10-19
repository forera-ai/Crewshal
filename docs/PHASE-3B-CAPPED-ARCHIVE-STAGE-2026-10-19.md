# Phase 3B capped archive evidence stage

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `692eaecd93ddb66d9e9aa918f4c403e26979c88b`.
Status: prepared for one owner scope decision. No transfer or guest action is admitted.

## Purpose and exact scope

Read-only metadata cannot supply safe archive members or exact compressed npm tarball sizes.
This stage would acquire archive bodies under fixed limits, then verify their bytes and safe members.
It is a separate evidence stage before the consolidated Linux campaign.
It grants no guest access, installation, native turn, evaluation row, or package release.

The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) names 16 selected URLs.
Eight tool URLs have recorded byte counts: `rtk`, `cpython`, `node`, `bun`, `swift`, `dotnet-sdk`, `dotnet-runtime-net8`, and `dotnet-targeting-pack-net8`.
Four selected source URLs have recorded byte counts and SHA-256 values.
Four npm URLs have integrity values but no compressed byte counts.
The CMake and Ninja package URLs remain unbound. This stage excludes their bodies.
It also excludes dependency packages, signatures, provider calls, and all other URLs.

| Resource | Exact proposed ceiling | Basis and stop rule |
| --- | ---: | --- |
| Twelve known archives | 1,107,938,715 bytes | Each response stops at its recorded byte count. Metadata is a candidate count, not verified content. |
| Four npm archives | 268,435,456 bytes each | Each response stops at this policy cap. The digest must match before use. |
| Sixteen archive response bodies | 2,181,680,539 bytes total | One request attempt per URL. No retry or replacement URL. |
| Other response bodies and protocol allowance | 50,331,648 bytes total | This is a reserve, not permission to add artifacts. Count redirects, errors, and metadata against it. |
| New stage transfer | 2,232,012,187 bytes total | Stop before a read that would exceed either the object cap or aggregate cap. |
| Cumulative transfer | 10,821,946,779 bytes total | Charge the prior 8,589,934,592 bytes in full. Do not refund unknown installer bytes. |
| Batch-owned retained data | 3,221,225,472 logical bytes | Include partial files, archives, extracts, receipts, and caches. Use an effective quota before transfer. |
| New Mac host allocation | 4,294,967,296 bytes | Include the isolated stage store and its filesystem overhead. Verify an effective bound before transfer. |
| Guest disk growth | 0 bytes | Do not enter, inspect, or change either guest. |
| VM-plus-ISO allocation growth | 0 bytes | Preserve the last recorded 9,093,566,464-byte allocation without a new readback. |
| New paid infrastructure and metered API | USD 0 each | Do not use a droplet or provider API. |
| Native subscription submissions | 0 | Do not start a runtime turn. |
| Active and elapsed stage time | 7,200 and 86,400 seconds | Stop at either limit. |

The 2,181,680,539-byte archive cap is the sum of twelve candidate counts and four policy caps.
Charge the separate 50,331,648-byte reserve in full, even if its measured use is lower.
This reserve covers response traffic outside successful archive bodies.
The stage cannot use the old transfer balance, which is zero under conservative accounting.
The proposed limits are new authority only after an explicit owner decision.

## Required controls before the first body request

1. Bind and test a transport that counts every response body byte, including redirect and error bodies.
2. Enforce each object cap, the aggregate cap, one attempt per URL, and no replacement URL.
3. Refuse a request when the counter or receipt is missing, changed, or incomplete.
4. Prove an isolated storage quota and the Mac allocation ceiling with local readback.
5. Preserve partial data and charges after a failure. Do not retry under the same grant.
6. Bind the exact command, tool version, output root, and receipt schema before transfer.

These controls are requirements, not verified current capabilities.
No current download command satisfies this stage's complete accounting and storage contract.
An owner decision on ceilings alone cannot bypass the control checks.

After an admitted transfer, verify each known archive's actual length and trusted digest where available.
The Bun and Swift archive digests remain unknown. Keep those bodies quarantined until trusted signatures or checksums pass.
Verify safe archive members and bounded extracted size before using any tool archive.
Run `scripts/phase3b_extract_source.py` on a selected source archive only after its transfer and SHA-256 pass.
Keep its output inside the retained-data quota.
Record all failed or unknown observations without changing frozen Phase 3A bytes.

## Next gate and owner decision

This stage does not close Ubuntu packages or repository dependencies.
Their exact snapshots, transfer caps, storage caps, installed closures, and licenses need a later review.
The full campaign's guest RAM, guest disk, and VM-plus-ISO amendments remain unapproved.
The 192 development rows stay planned. The 576 sealed rows stay unexposed.

The concrete decision is whether to approve only this 16-URL archive evidence stage.
Approval would set the numeric limits above, subject to the six required controls.
Refusal or missing approval leaves all archive retrieval closed.
No dated approval reopens Linux work.

## Local verification and limits

The entry worktree was clean at the revision above.
All 162 indexed inputs matched their recorded size and SHA-256.
Four direct npm HTTP HEAD requests returned HTTP 200 but no `Content-Length` field.
The requests read headers only. Their response body transfer was zero.
Environment: Darwin 27.2.0 arm64, local Python 3.14.8, project Python 3.12.15, and RTK 0.51.0.

| Command or check | Result |
| --- | --- |
| `rtk proxy git status --short --branch` and `rtk proxy git rev-parse HEAD` | Clean entry worktree at the revision above. |
| SHA-256 and size check of the previous continuation index | 162 files matched; zero failures. |
| `rtk proxy curl -sSI --max-time 20` on four exact npm tarball URLs | Four HTTP 200 responses; all omitted `Content-Length`. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts, 768 planned units, unchanged digest. |
| JSON parsing and independent ledger arithmetic check | Passed for 16 URLs and every proposed transfer sum. |
| SHA-256 and size check of the new continuation index | 164 files matched; zero failures. |
| `rtk proxy git diff --check` | Passed. |

The HEAD header byte count was not measured. The stage's proposed charge includes no completed archive transfer.
No selected archive body, guest, Linux test, provider request, evaluation row, or Jev call ran.
Known paid-host and metered API cost was USD 0. Subscription quota debit for this chat is unknown.
Linux-specific acceptance modules were deferred, not passed.
Linux qualification, native baselines, provider identity, Phase 3B calibration, and Phase 3C remain closed.
