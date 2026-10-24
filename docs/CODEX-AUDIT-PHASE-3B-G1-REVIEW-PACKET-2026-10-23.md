# Codex audit — Phase 3B G1 review packet

Date: 2026-10-23. Review outcome: changes required before the proposal is a reliable campaign command set.

## Scope and verified state

Codex reviewed `finish-g1-revision-3-review-packet-2-local-e8.json` and the eight untracked planning documents.
Hermes completed the missing revision-3 review packet and corrected the six findings from the previous audit.
No tracked source, version, frozen input, guest, or paid service changed in this session.
There is no source code diff to review. This is a document and operational-command audit.

## Findings

1. **P1 — The Mac source-archive command is not runnable.**
   The proposal calls `git archive ... <HEAD>` an exact bound command.
   `zsh -n` reports `parse error near '>'` for that line.
   The following `shasum` command does not write `g1_delivery_ledger.txt` or record a byte count.
   Replace the placeholder with a quoted revision variable and write the digest and size to the ledger.
   Keep S2 blocked until the command passes a static syntax check and its output path is bound.

2. **P2 — G1 scope and quota requests conflict.**
   The proposal says G1 runs zero actual baseline and native turns.
   It still lists S4 baseline conformance as a G1 stage and asks for subscription-quota acceptance.
   Move S4 actual runs and their quota decision to the later admitted stage.
   If G1 needs a native turn for S3, state its exact purpose and a bounded count before approval.

3. **P2 — The continuation prompt stops safe local progress.**
   The review packet tells Hermes to make no edit when the owner has not answered a host decision.
   S3 still needs a local case-to-driver inventory and argument contracts.
   That source preparation can proceed without a guest, download, or owner approval.
   Give the next session one bounded local readiness milestone instead of an idle status loop.

## Verified progress

The revision-3 packet exists and marks both older packets as historical.
The proposal now describes the frozen baseline and selected archive records accurately.
S0b, S1b, S2, S3, and S4 remain blocked where their inputs are unknown.
No host approval or publication is justified by this audit.

## Next boundary

Correct the two proposal defects and the continuation prompt.
Then prepare a bounded local S3 driver inventory for Codex review.
