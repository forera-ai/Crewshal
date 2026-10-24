# Codex audit — Phase 3B G1 campaign revision 3

Date: 2026-10-23. Review outcome: changes required. Do not request owner approval for host action.

## Scope and verified state

Codex reviewed the 112-message Hermes export `repair-g1-campaign-evidence-local-e6.json`.
Codex compared the revised proposal and review packets with the repository records.
Hermes changed only untracked planning documents. It did not run a guest, retrieve an artifact, or change tracked source.
The export ended at its tool-call limit. Hermes listed unfinished work in its final response.
No source code diff exists for this session.

## Findings

1. **P1 — S1b archive verification cannot run as written.**
   `diskutil mount` requires a disk identifier or device node, not the absent mount path in the proposal.
   The retained archive scripts use `<id>.blob` under the recorded archive root.
   S1b instead hashes four `.tar.zst` names that the records do not identify.
   Bind the sparseimage path, mount command, actual archive paths, and read-only verification steps.
   Keep mounting closed until the owner authorizes that exact action.

2. **P1 — S0b requests a network download before its ceiling exists.**
   The proposal says `pip download` will establish the transfer ceiling after the download.
   A general go-ahead does not bind the maximum response bytes or dependency closure.
   Derive a finite cap from local records or metadata before any download request.
   If no cap can be derived locally, mark S0b blocked and preserve zero transfer allowance.

3. **P1 — S0 and S2 still omit commands needed for execution.**
   S0 writes to `evidence/` without creating or binding that directory.
   S2 describes `git archive` and source transfer but gives no exact command for either.
   The guest commands extract into `source/` without creating it.
   S2 therefore remains blocked; its readiness table must not say its commands are bound.

4. **P1 — Baseline and quota claims conflict with the frozen record and scope.**
   The ten `mandatory_actual_cases` are strings, not objects with `native_execution` fields.
   The `unavailable` values belong to candidate records.
   The frozen file records one macOS `sandbox-exec` conformance command, not one per case.
   Section 9 plans zero native turns while S4 still names B0/B1/B2/P conformance.
   State whether G1 includes actual baseline turns. Keep S4 blocked until its runner and limits are bound.

5. **P2 — The corpus byte claim contradicts the file.**
   `corpus.json` contains `source_identity.archive_bytes` for the selected archives.
   Sections 3 and 13 give opposite claims about those fields.
   Use the exact JSON paths and keep their values separate from current archive availability.

6. **P2 — The review handoff is incomplete.**
   Both older review packets point to a revision-3 packet that does not exist.
   Hermes explicitly left that packet and two factual corrections unfinished.
   Create one current packet after correcting the proposal.
   Mark older prompts superseded without claiming the missing packet is current.

## Progress worth retaining

Hermes corrected earlier false withdrawals and separated retained archives from new downloads.
It removed `rtk` from proposed guest commands and marked S3 and S4 blocked.
It kept Linux, evaluation, spend, and publication gates closed during this session.

## Next boundary

Complete the six corrections in one short local planning session.
Verify commands by static inspection only. Do not mount, download, boot, or run a guest.
