# Codex delta record: Phase 3B G1 S3 byte-count guard repair, 2026-10-24

This record captures the exact byte-level delta of the G1 S3 repair candidate. It accompanies
`docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-24.md`. It changes no other file.

## File edited

`docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` (untracked in Git).

Content hash before: `a76f8fbb96ce03ed5afb8f3c4015750add0820dbf6f99061a7876a0401c8ed07`
Content hash after:  `a47ca29a6168bab30b4f1fc21b22a78f4b981500e8aabb62b6e0d70989a8d103`

Because the file is untracked, `git diff` shows no tracked change. The delta is the hash change
above plus the exact lines below.

## Exact changed lines

Location: the S2 checked-template Mac archive block, fenced at proposal lines 210 and 229,
working directory `/Volumes/X10Pro/Crewshal`. Two old lines became three new lines.

Removed:

```
BYTES="$(wc -c < "$ARCHIVE" | tr -d ' ')"                      # capture the byte count in a checked assignment
DIGEST_LINE="$(shasum -a 256 "$ARCHIVE")"                      # capture the full digest output; no inner cut pipeline
```

Added:

```
BYTES_RAW="$(wc -c < "$ARCHIVE")" || exit 1                    # capture the byte count alone; a failed wc aborts before any record
BYTES="$(printf '%s' "$BYTES_RAW" | tr -d ' ')"                # strip surrounding whitespace from the captured count
DIGEST_LINE="$(shasum -a 256 "$ARCHIVE")" || exit 1            # capture the full digest output; a failed digest command aborts before any record
```

Unchanged lines that follow (kept byte-for-byte):

```
DIGEST="${DIGEST_LINE%% *}"                                    # the first whitespace-delimited field is the digest
test -n "$BYTES" || exit 1                                     # fail closed when the byte count is missing
case "$BYTES" in *[!0-9]*) exit 1 ;; esac                      # byte count must be digits only
test "${#DIGEST}" -eq 64 || exit 1                             # digest must be exactly 64 characters
case "$DIGEST" in *[!0-9a-f]*) exit 1 ;; esac                  # digest must be hexadecimal only
```

## Root cause

The old byte-count line ran `wc` inside a pipeline. Under `set -eu` (no `pipefail`), the pipeline
status is the last command's status (`tr`). A `wc` stub that prints a plausible number and then
exits nonzero leaves `BYTES` set to that number, and the pipeline exits 0. The later digit check
then passes, and the block appends a success-looking record. The audit
(`docs/CODEX-AUDIT-PHASE-3B-G1-S3-REPAIR-2026-10-24.md`, finding 1, P1) identified this. The prior
session tested only a `wc` failure with no output.

## Fix behavior

`wc` now runs alone in its own command substitution, and `|| exit 1` guards its status directly.
A nonzero `wc` — whether it printed nothing or a number first — aborts the block before the
append. Whitespace normalization moved to a separate `printf | tr` step after the checked
`wc` command. It cannot mask the byte-count command status. The `shasum` capture gained the same
explicit `|| exit 1` status guard. The separate digest status check and both digest format checks
are preserved unchanged.

## Verification evidence

Syntax (exact block extracted from the proposal, lines 211-228):

```
bash -n  → exit 0
zsh -n   → exit 0
```

Offline stub runs (temporary directories; fake `git`, `wc`, `shasum`; no real archive, no repo
input). Two shells, `/bin/bash` 3.2.57 and `/bin/zsh`, gave identical results.

| Case | `wc` / `shasum` stub | Block exit | Ledger after |
| --- | --- | --- | --- |
| success | `wc`→`18` exit 0; `shasum`→64 hex exit 0 | 0 | PRESENT, exactly 1 three-field record |
| failed byte count, no output | `wc`→(none) exit 9 | 1 | ABSENT |
| failed byte count after numeric output | `wc`→`18` exit 9 | 1 | ABSENT |
| failed digest output | `shasum`→(none) exit 1 | 1 | ABSENT |
| truncated digest | `shasum`→63 hex exit 0 | 1 | ABSENT |
| control — old block, "after numeric output" | `wc`→`18` exit 9 | 0 | PRESENT, `bytes=18` (fault reproduced) |

Every failure left no ledger file. The success case wrote exactly one complete record. The old
block control reproduced the fault: it wrote `bytes=18` after a failed `wc`.

## Preserved and excluded

- The inventory `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` is unchanged (hash
  `dbbc586a4ff6c3312fd547bd342fe264b7a489d2602630a0f567863abbf732b5`).
- The historical packet `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md` is
  unchanged (hash `8cc08de315418e2101581370991a566db19b5bbfc4f666669c294f391616d39e`).
- Stages S2, S3, and S4 stay blocked. No guest, no Linux test, no native turn, no evaluation row,
  no paid host, no credential access. No commit or push. ADR 0009 local-development boundary held.
