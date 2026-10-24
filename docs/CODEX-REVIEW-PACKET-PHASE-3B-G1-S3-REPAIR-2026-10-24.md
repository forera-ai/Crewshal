# Codex review packet: Phase 3B G1 S3 repair, 2026-10-24

## Purpose and supersession

This packet asks Codex to re-review one repaired candidate. It supersedes the next-session
prompt in `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md`. That earlier packet
kept its dated text as history, but its continuation prompt was wrong in two ways. This packet
corrects both. The dated packet file is unchanged and stays historical.

This repair closes the finding in `docs/CODEX-AUDIT-PHASE-3B-G1-S3-REPAIR-2026-10-24.md`. That
audit is evidence of a prior session. Its text does not grant approval. Only your review does.

## Milestone and boundary

- Milestone: repair the saved Mac archive byte-count guard so a failed byte-count command
  cannot create a success-looking ledger record, then let Codex review it again.
- This is a documentation repair to one checked template block. It changes no source file,
  no test, no runtime behavior, and no frozen Phase 3A package byte.
- Scope is bounded to this guard. No new Phase 3B source milestone started. No publication ran.

## Base revision, branch, version

- Base revision (HEAD): `6279a2eb32714530beffab7e6425c3d41fbcfbb5`
- Branch: `codex/phase1-architecture` → `origin/codex/phase1-architecture`
- Package version: `0.27.3` in `pyproject.toml` and `src/crewshal/__init__.py` (synchronized).
  This session did not bump the version. No publication gate opened.

## Changed and created files

One existing untracked document was edited. Two new untracked documents were created.
All three Phase 3B candidate documents are untracked in Git, so `git diff` shows no tracked change. The edit is recorded by
its content hash change and the exact diff below.

| File | State | Hash change |
| --- | --- | --- |
| `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` | edited (untracked) | `a76f8fbb96ce03ed5afb8f3c4015750add0820dbf6f99061a7876a0401c8ed07` → `a47ca29a6168bab30b4f1fc21b22a78f4b981500e8aabb62b6e0d70989a8d103` |
| `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-24.md` | created (untracked) | new; this packet |
| `docs/CODEX-DELTA-PHASE-3B-G1-S3-REPAIR-2026-10-24.md` | created (untracked) | new; exact delta record |

Unchanged and preserved (hashes re-verified this session):
`docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` = `dbbc586a4ff6c3312fd547bd342fe264b7a489d2602630a0f567863abbf732b5`;
`docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md` = `8cc08de315418e2101581370991a566db19b5bbfc4f666669c294f391616d39e`;
`docs/CODEX-AUDIT-PHASE-3B-G1-S3-REPAIR-2026-10-24.md` = `fe58121401b007016e967b1f6d4ab4fb98a528fcfd61954e73a3d50e11fbd04f`.

## Exact diff (the repair)

The saved Mac archive block is at proposal lines 210-229 (fenced), working directory
`/Volumes/X10Pro/Crewshal`. The byte-count capture was one pipeline line. The pipeline reported
`tr`'s status, so a `wc` that prints a number and then exits nonzero set `BYTES` to that number
and exited 0 under `set -eu`. The repair captures `wc` alone and checks its status.
It then normalizes whitespace in a separate step. The digest capture now also
carries an explicit status guard. The separate digest status check and both format checks remain.

```diff
-BYTES="$(wc -c < "$ARCHIVE" | tr -d ' ')"                      # capture the byte count in a checked assignment
-DIGEST_LINE="$(shasum -a 256 "$ARCHIVE")"                      # capture the full digest output; no inner cut pipeline
+BYTES_RAW="$(wc -c < "$ARCHIVE")" || exit 1                    # capture the byte count alone; a failed wc aborts before any record
+BYTES="$(printf '%s' "$BYTES_RAW" | tr -d ' ')"                # strip surrounding whitespace from the captured count
+DIGEST_LINE="$(shasum -a 256 "$ARCHIVE")" || exit 1            # capture the full digest output; a failed digest command aborts before any record
```

No other line in the block changed. The `test -n "$BYTES"`, digit, 64-character, and hexadecimal
checks are byte-for-byte the same as before.

## Source-claim corrections

The 2026-10-23 packet (line 66) placed `refusal()` at `scripts/readback_native_full_v3.py:418`
and said `aggregate()` calls it at line 520. Both claims are false. I checked the live source at
HEAD this session. The correct facts are:

- `refusal()` is defined at `scripts/readback_native_full_v3.py:62`.
- `check_run()` is defined at `scripts/readback_native_full_v3.py:127`.
- `check_run()` calls `refusal(identity)` at `scripts/readback_native_full_v3.py:131`.
- `checks["qualification-refusal"]` is set at lines 132 (success path) and 423 (refusal path).
- There is no `aggregate()` function in that file. The aggregator is `readback()`, defined at
  `scripts/readback_native_full_v3.py:437`. Line 418 is `raise ValueError("storage limits unverified")`;
  line 520 is blank.

The inventory case-20 row (`docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md:91`) already gave the
correct location: `refusal()` at `readback_native_full_v3.py:62-102`. This packet repeats that
correct location and removes the invented `:418` and `aggregate()` at `:520` claims.

## Acceptance mapping

The task required four cases. I added one format-only case (4b) and a control run of the old
block. All runs used offline stubs in a temporary directory. No real repository input ran, and no
archive was built. The saved block was never run against the real checkout.

| Case | Stub behavior | Expected | Observed (bash 3.2.57) | Observed (zsh) |
| --- | --- | --- | --- | --- |
| 1 success | `wc` emits `18`, exit 0; `shasum` emits 64 hex, exit 0 | exit 0; one 3-field record | exit 0; ledger PRESENT, 1 record | exit 0; ledger PRESENT, 1 record |
| 2 failed byte count, no output | `wc` emits nothing, exit 9 | nonzero; no record | exit 1; ledger ABSENT | exit 1; ledger ABSENT |
| 3 failed byte count after numeric output | `wc` emits `18`, exit 9 | nonzero; no record | exit 1; ledger ABSENT | exit 1; ledger ABSENT |
| 4a failed digest output | `shasum` emits nothing, exit 1 | nonzero; no record | exit 1; ledger ABSENT | exit 1; ledger ABSENT |
| 4b truncated digest | `shasum` emits 63 hex, exit 0 | nonzero; no record | exit 1; ledger ABSENT | exit 1; ledger ABSENT |
| control: old block, case 3 | `wc` emits `18`, exit 9 | — | exit 0; ledger PRESENT, `bytes=18` (fault reproduced) | exit 0; ledger PRESENT, `bytes=18` (fault reproduced) |

Case 3 is the audit's P1 gap. The old block wrote a success-looking record after a failed `wc`.
The repaired block exits 1 before the append. The success case still writes exactly one complete
record (`archive=`, `bytes=`, `sha256=`).

## Commands and observed results

```
$ bash -n <repaired block> ; echo $?      # block content, proposal lines 211-228
0
$ zsh -n <repaired block> ; echo $?
0
$ sh driver-style stub harness (5 cases x 2 shells) + old-block control x 2 shells
see acceptance mapping table above
```

Static validation: the repaired block passes `bash -n` and `zsh -n` with exit 0. The exact block
text was extracted from the proposal (lines 211-228) and re-checked; both syntax checks passed.
The extracted block is identical in behavior to the verified harness copy (the only difference in
the scratch copy was a comment word on an unchanged line, which does not affect behavior). Stub
tests ran the exact proposal block through all five cases under both shells; results match the
table. `git diff --check` passed (exit 0).

Environment: macOS 27.2 arm64, CPython 3.12.15 not involved (shell-only repair), `/bin/bash`
3.2.57, `/bin/zsh`. Offline stubs only; no Docker, no guest, no network.

## Refusal and failure proof

For every failure case, the ledger file did not exist afterwards. No failure produced a
success-looking record. The success case produced exactly one three-field record and nothing more.
The guard fails closed: a missing byte count, a nonzero `wc`, a nonzero `shasum`, or a malformed
digest each aborts before the append.

## Remaining limits and blocked stages

- Stage S2 stays a checked template, not a bound command. `APPROVED_REVISION` stays forty zeroes;
  the HEAD equality check refuses to archive under it. No archive was built.
- Stages S2, S3, and S4 stay blocked. No guest action, no Linux test, no native turn, no
  evaluation row, and no paid-host action ran.
- Guest architecture and admission state stay unknown. All unknown guest facts and owner gates are
  preserved. ADR 0009 keeps local macOS development only.
- The two created documents and the edited proposal stay untracked. No commit or push ran.

## Review boundary (Hermes)

Hermes prepared this packet and stopped. Hermes did not commit and did not push. Publication stays
with Codex after an actual accepted review.

## Next-session prompt (supersedes the 2026-10-23 packet prompt)

Use this prompt only after Codex actually accepts this packet. It replaces the wrong prompt at the
end of `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md`.

Corrected prompt for Codex publication:

1. Read `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-24.md`,
   `docs/CODEX-DELTA-PHASE-3B-G1-S3-REPAIR-2026-10-24.md`, and the repaired
   `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` block at lines 210-229.
2. Confirm the content hash of the proposal is
   `a47ca29a6168bab30b4f1fc21b22a78f4b981500e8aabb62b6e0d70989a8d103` and that the diff matches
   the delta record.
3. Record your own accepted verdict in the Review outcome section below before any publication.
4. Codex performs publication only after that recorded acceptance: bump the semantic version in
   `pyproject.toml` and `src/crewshal/__init__.py` together, update `README.md`, `CHANGELOG.md`,
   and the `docs/HANDOFF.md` current-state section, commit, and push the current branch. Hermes
   does not commit or push. Do not publish if the diff and hashes do not match.
5. Do not start a new Phase 3B source milestone in the publication turn.

The filename correction: the historical packet is
`docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md` (it contains the word `PACKET`).
The 2026-10-23 prompt named `docs/CODEX-REVIEW-PHASE-3B-G1-S3-REPAIR-2026-10-23.md`, which does
not exist. This packet uses the correct name.

## Review outcome

Codex review on 2026-10-24: **APPROVE after two evidence wording corrections in this packet and its delta record.**
Codex reran the exact saved block with offline stubs under Bash and Zsh.
Both shells refused a `wc` that printed `18` and exited 9.
The success case wrote one three-field record.
Codex verified the proposal, inventory, and historical packet hashes against the recorded baseline.
The earlier packet's false source lines and continuation prompt remain historical and are superseded here.
No Linux or guest action ran. Publication still requires the version, README, changelog, and handoff ceremony.
The publication ceremony's offline wheel build failed because `setuptools==80.9.0` was absent from the local cache.
Codex did not claim an installed-package pass for this documentation checkpoint.
