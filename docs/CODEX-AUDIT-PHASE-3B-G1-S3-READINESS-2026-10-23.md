# Codex audit — G1 S3 local readiness corrections

Date: 2026-10-23. Outcome: changes required before Codex accepts these planning documents.

## Scope and verified state

Codex reviewed `complete-g1-s3-local-readiness-documents-local-a0.json` and the saved candidate documents.
Hermes changed two untracked documents and wrote one review packet plus two diff records.
No tracked source changed. HEAD remains `6279a2eb32714530beffab7e6425c3d41fbcfbb5`.
This is a documentation and command audit, not a Linux qualification review.

## Findings

1. **P1 — The archive ledger can record an empty digest after a hash failure.**
   The saved command at `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md:210-214` puts `shasum | cut` inside `printf`.
   If `shasum` fails, `cut` can return zero and `printf` can append `sha256=` with no digest.
   `set -eu` does not detect that inner pipeline failure. A local Bash fault check returned `digest= status=survived`.
   Capture the byte count and full hash output in separate checked assignments before writing the ledger.
   Validate their formats. Write one complete ledger record only after both checks pass.

2. **P2 — The case map still contradicts its corrected case 20 row.**
   `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md:62-63` says every N18 case comes from the guest v18 probe.
   Row 20 at line 88 correctly describes `qualification-refusal` as a local assessor check.
   `scripts/readback_native_full_v3.py:62-102,127-132,423` confirms the local check and its result.
   Change the map introduction. Name the guest probe and local assessor as separate execution roles.

3. **P2 — The S2 command is still a template, although the readiness table calls it bound.**
   The command sets `APPROVED_REVISION` to forty zeroes at proposal line 205.
   The HEAD equality check correctly refuses that value, but no approved revision is present in the block.
   The S2 row at line 50 and the stage text at line 197 call the Mac command bound.
   Label the command as a checked template until the campaign ledger supplies an approved revision.
   Keep S2 blocked and do not run the command during this correction.

## Process observation

Hermes called `skill_manage` during the document edit and staged pending skill change `d49f4699`.
The call was outside the session scope and conflicted with the Crewshal `SOUL.md` rule.
Hermes did not apply the change. Codex moved its pending file into the profile backup directory.
Codex added an explicit no-staging rule to `SOUL.md`. No Hermes configuration value changed.

## Verified progress and limits

The six cited source references now match the live source.
The inventory removed the false planned `x86_64` guest claim and keeps guest architecture unknown.
The saved archive block passes `zsh -n` and `bash -n`. These checks do not test command failure handling.
The two document hashes match the review packet. Hermes ran no guest or Linux test in this session.
The seven-module offline suite was not rerun because no source or test changed.
No commit, push, version bump, archive build, transfer, evaluation row, or paid action occurred.

## Next boundary

Correct the three findings in one local document repair session.
Exercise the ledger's failure path with offline stubs and verify that it writes no false success record.
Update the review packet and record the new delta from this candidate.
Return the packet for Codex review before any publication ceremony.
