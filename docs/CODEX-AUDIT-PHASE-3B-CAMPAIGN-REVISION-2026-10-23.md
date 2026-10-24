# Codex audit — Phase 3B campaign proposal revision

Date: 2026-10-23. Review outcome: changes required before owner approval or publication.

## Scope

Codex reviewed the 95-message Hermes export `repair-phase-3b-campaign-proposal-local-16.json`.
Codex compared the three changed planning documents with the repository and the earlier export.
No tracked source changed. A source code diff review does not apply.
Hermes ran 12 local fixture tests with exit 0. It made no guest or paid-host action.

## Findings

1. **P1 — The campaign still lacks executable stage commands.**
   S2 leaves source delivery and its working directory unbound.
   Its guest commands require `rtk`, but S2 checks only for `python3`.
   S3 explicitly defers every probe driver command to S1.
   S4 gives no launch or conformance command.
   These gaps fail the plan's claim that every stage gives exact commands and inputs.
   Do not ask the owner to approve host action from this revision.

2. **P1 — The retrieval request ignores retained selected archives.**
   The readback inventory lists `dotnet-1`, `python-1`, `swift-1`, and `typescript-2`.
   Their recorded archive bytes total 2,777,282.
   The proposal requests a new network allowance to retrieve those same four archives.
   First verify their current availability and digests through an approved later readback.
   Keep unresolved dependency downloads separate, with a finite ceiling before approval.

3. **P1 — The correction log attributes claims to revision 1 that it never made.**
   The earlier export contains no 96,154,107,538-byte figure and no four-day duration.
   Revision 1 cited `baseline-conformance.json`; it did not say that record was absent.
   The proposal, old review packet, and revision packet now repeat these false withdrawal claims.
   Remove those entries. Preserve the actual corrections with exact original wording.

4. **P2 — The test classification is broader than its evidence.**
   The 12 passing tests cover three Phase 2C fixture modules only.
   A search for skip markers cannot classify all acceptance modules as platform independent.
   Several Phase 2D modules patch Linux platform values and kernel interfaces.
   Review the actual test effects and classify each proposed module or bounded group.
   Keep live Linux probes distinct from synthetic fixture tests.

5. **P2 — The resource rules disagree.**
   S2 stops below a parked 16 GiB proposed floor, while S1 says no floor is approved.
   The decision list allows the owner to set another floor.
   Make every conditional stop use the limit the owner actually approves.
   Keep the current approval value unknown until that decision is recorded.

6. **P2 — The old review packet still gives an unsafe continuation prompt.**
   Its original prompt allows host observation after obsolete D-A through D-E decisions.
   An appended correction log does not retire that instruction.
   Mark the old prompt superseded and point to one current prompt.

## Verified progress

Hermes corrected the B1 draft and frozen P contract references.
It narrowed the document to G1 and kept G2, G3, and sealed evaluation closed.
It separated a local VMware campaign from any paid droplet proposal.
It did not commit, push, use a guest, retrieve a toolchain, or execute an evaluation row.

## Next boundary

Repair these findings in one local planning session.
Keep all host actions closed until Codex reviews a complete, bounded plan.
