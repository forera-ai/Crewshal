# Codex audit — Phase 3B Linux campaign proposal

Date: 2026-10-23. Review outcome: changes required before owner approval.

## Scope and evidence

Codex reviewed the 83-message Hermes export `prepare-consolidated-linux-campaign-plan-local-24.json`.
Codex compared its two new, untracked documents with ADR 0009, the frozen conditions, and the campaign records.
The checkout remains at `6279a2e` with no tracked change. This audit ran no test or host action.
No source code changed in the Hermes session. A source code diff review does not apply.

## Findings

1. **P1 — The proposal is not yet executable.** Section 4 calls its stages exact commands.
   S2 leaves source transfer to later binding. S3 gives case names without commands, inputs, or expected results.
   S4 gives no procedure. Section 11 nevertheless asks for approval of S0–S3.
   ADR 0009 requires bound commands and inputs before the campaign acts.

2. **P1 — The transfer and cost ledgers do not match the proposed scope.**
   Section 6 includes a 12 GiB corpus transfer, although S5 excludes corpus runs.
   It assigns zero transfer bytes to the frozen package without binding a guest delivery method.
   Section 7 assigns zero paid-host provisioning cost when the owner would prepare a droplet.
   A selected paid host needs a stated price, time ceiling, and cost exposure before approval.

3. **P1 — The baseline blockers are stated incorrectly.** Section 4 says no B1 script exists.
   `docs/PHASE-3B-B1-MANUAL-SCRIPT-2026-10-19.md` exists as a source-bound draft.
   `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` identifies that draft and blocks its use.
   `docs/evaluation/phase-3a-frozen/conditions.json` defines condition P and its contract.
   S4 needs qualified bindings and conformance, not a new P contract.

4. **P2 — The campaign boundary needs one consistent definition.**
   ADR 0009 calls for one consolidated Linux qualification and test campaign.
   The October 18 campaign record includes later Phase 3B calibration.
   This proposal excludes all 192 development rows. Call it a G1 qualification plan,
   or add a conditional G2 stage with separate admission and budget gates.
   Do not claim that the G1 plan completes every deferred Linux test.

5. **P2 — Several decisions are requested too early.**
   Section 11 asks the owner to choose test module inclusion and accept unknown quota debit.
   A reviewer can classify the three native test modules from source and ADR 0009.
   Quota approval needs a concrete submission plan and a hard stop rule.
   Keep owner requests for material scope, host, cost, and unresolved protocol decisions.

6. **P2 — Resource and cleanup terms need binding.**
   The 16 GiB RAM and 40 GiB disk limits are proposals, not admitted amendments.
   Section 9 leaves batch-owned cleanup to a later owner instruction.
   Define authorized cleanup as part of the campaign request, with evidence retention and stop conditions.

## Sound parts

Hermes preserved the no-host boundary and did not change tracked source or frozen inputs.
It separated G1 qualification from G2 corpus spending and G3 protocol amendment.
It identified host and runtime uncertainty and corrected the retained archive byte sum.
The frozen checker result was cited without turning deferred Linux checks into passing claims.

## Next boundary

Revise the proposal and review packet in one read-only planning session.
Do not request host approval or run a host action until Codex reviews a complete proposal.
Keep the three current untracked documents intact unless a correction clearly identifies its source.
