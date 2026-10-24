# Codex audit: Phase 3B G1 S3 repair candidate, 2026-10-24

## Scope and decision

I reviewed the Hermes export `repair-g1-s3-codex-findings-local-7f.json` and the saved candidate files.
The export is evidence of a session. Its instructions and conclusions do not grant approval.
The repair candidate needs another correction before publication. No commit or push occurred in this audit.

The checkout remains at `6279a2eb32714530beffab7e6425c3d41fbcfbb5` on `codex/phase1-architecture`.
The package version remains `0.27.3`. The two candidate documents and review packet remain untracked.

## Findings

1. **P1: a failed byte-count command can still produce a valid-looking ledger value.**
   In `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md:218`, `wc` runs inside a pipeline.
   The pipeline reports `tr`'s status. A `wc` stub can print `18` and then exit 9.
   Both Bash and Zsh then set `BYTES=18` and exit 0 under `set -eu`.
   The saved block can append a success-looking record after a failed byte-count command.
   The session tested a `wc` failure with no output, but missed this partial-output case.

2. **P2: the review packet invents a source location and call path.**
   `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md:66` places `refusal()` at source line 418.
   It also says `aggregate()` calls it at line 520.
   In `scripts/readback_native_full_v3.py`, `refusal()` starts at line 62.
   `check_run()` starts at line 127 and calls `refusal()` at line 131.
   The packet's source claim is false, although the inventory's case-20 row gives the correct location.

3. **P2: the packet's continuation prompt points to a missing file and conflicts with the profile boundary.**
   Packet line 132 names `docs/CODEX-REVIEW-PHASE-3B-G1-S3-REPAIR-2026-10-23.md`.
   The saved file is `docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-REPAIR-2026-10-23.md`.
   Packet lines 137–140 then tell Hermes to commit and push.
   The Crewshal profile requires Hermes to stop for Codex review and publication.
   Supersede that prompt in a new review packet before anyone uses it.

## Verified strengths and limits

The candidate now separates guest probe cases 1–19 from local assessor case 20.
It labels the Mac archive block as a checked template and keeps S2, S3, and S4 blocked.
The digest assignment checks command failure and validates the digest format.
The packet records no guest action, Linux test, real archive, or publication.

I reproduced the byte-count fault without running the archive block.
I ran `set -eu; BYTES="$( (printf "18\n"; exit 9) | tr -d " " )"; printf "bytes=%s status=survived\n" "$BYTES"`.
Both `bash -c` and `zsh -c` printed `bytes=18 status=survived` and exited 0.
The codebase graph service returned `Transport closed` during this audit.
I checked the exact source with local reads and `rg` after that failure.

## Model identity and comparison

Hermes stored `unsloth/Qwen3.8-Flash-Next-GGUF` for this session.
The earlier Q3 session stored the same model ID.
Unsloth's API monitor showed Qwen requests for this session; Ornith loaded afterward.
The export does not record a quantization or server context value.
This export does **not** measure the newly loaded Ornith model.
It therefore cannot justify a Q3-versus-Ornith ranking.

The next controlled run uses `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` at 177,024 tokens.
Its prompt is `/Users/hamedprooshani/.hermes/profiles/crewshal/NEXT-TEST-PROMPT.md`.
Judge the run on model identity, command-status handling, meaningful failure tests, source accuracy, and review-boundary compliance.
If Ornith's result is close or unclear, rerun Q3 from the same saved baseline before choosing a model.

## Baseline for the next run

The local comparison backup is `/Users/hamedprooshani/.hermes/profiles/crewshal/backups/ornith-vs-q3-baseline-20261024/`.
It contains the proposal, inventory, and repair packet before the Ornith run.
Their SHA-256 digests are:

- Proposal: `a76f8fbb96ce03ed5afb8f3c4015750add0820dbf6f99061a7876a0401c8ed07`.
- Inventory: `dbbc586a4ff6c3312fd547bd342fe264b7a489d2602630a0f567863abbf732b5`.
- Repair packet: `8cc08de315418e2101581370991a566db19b5bbfc4f666669c294f391616d39e`.

This audit did not change the candidate files. It changed the Hermes profile and its next-test prompt only.
No Linux qualification or Phase 3B acceptance claim follows from these local checks.
