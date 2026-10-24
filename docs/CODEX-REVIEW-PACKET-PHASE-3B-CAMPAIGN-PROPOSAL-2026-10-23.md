# Codex review packet — Phase 3B consolidated Linux campaign proposal (2026-10-23)

**HISTORICAL RECORD (marked 2026-10-23 by the audit REVISION-3 follow-up session).** Superseded by revision 3
of the proposal and by `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md`. Do not
use any prompt in this file.

Prepared by Hermes under the Crewshal profile. This is a read-only planning deliverable. Nothing here is
committed or pushed. No host acted. Codex reviews; the owner decides.

## Milestone and boundary

Milestone: prepare one concrete consolidated Linux qualification and test campaign proposal under ADR
0009, answering gate G1 of the reviewed decision packet, without any host action, source change, or
version change. Acceptance: the proposal binds pinned inputs, exact commands, host options, identities,
resource ceilings, transfer and storage ledgers, duration, cost exposure, stop rules, and cleanup; marks
every unavailable input unknown; separates qualification from corpus runs, budget, amendment, and sealed
evaluation; and states the smallest owner decisions.

## Base revision and Git state (observed this session)

- Branch `codex/phase1-architecture`, tracking `origin/codex/phase1-architecture`.
- HEAD `6279a2eb32714530beffab7e6425c3d41fbcfbb5` ("test: verify Phase 3B measurement authority guard
  (v0.27.3)") — matches the expected checkpoint.
- Package version `0.27.3` at `pyproject.toml` line 7 and `src/crewshal/__init__.py` line 3, synchronized.
- `git status --short --branch`: clean except untracked files (below). No other unreviewed candidate was
  present, so the session proceeded per the continuation prompt.

## Changed files

- Tracked-file diff: empty. No tracked file changed. `git diff` is empty by construction.
- New untracked file (pre-existing, preserved): `docs/OWNER-DECISION-PACKET-PHASE-3B-REMAINING-GATES-2026-10-23.md`.
- New untracked files (this session's deliverables):
  - `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` — the campaign proposal.
  - `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-2026-10-23.md` — this packet.

## Records read (exact ranges)

1. `AGENTS.md` — full file (9,418 chars).
2. `/Users/hamedprooshani/.codex/RTK.md` — full file (730 chars).
3. `docs/HANDOFF.md` — heading map (`## Current state` at line 5, through line 1581), plus offset-5
   window of the current-state records; later targeted greps for deferred/Linux references.
4. `docs/decisions/0009-local-development-before-consolidated-linux-testing.md` — full file (2,871 chars).
5. `docs/OWNER-DECISION-PACKET-PHASE-3B-REMAINING-GATES-2026-10-23.md` — lines 1–80 (full). Read as
   evidence, not authorization.
6. `docs/DEVELOPMENT-PLAN.md` — lines 1–75 (Phase 3B boundary sections) and 550–629 (milestone map;
   Phase 3B row at line 566).
7. `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-2026-10-18.md`, `docs/PHASE-3B-LOCAL-DEVELOPMENT-BOUNDARY-2026-10-21.md`
   — full files.
8. `docs/PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md` — full file (240 lines): ceilings table, containment
   cases, cost classes reused in the new proposal.
9. `docs/PHASE-3B-LINUX-ARM64-TOOLCHAIN-MANIFEST-2026-10-18.json` and
   `docs/PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json` — full field walk (this session).
10. `docs/PHASE-3B-GUEST-PREPARATION-2026-10-18.md` — lines 1–45 and 46–130 (this session).
11. `docs/evaluation/phase-3a-frozen/corpus.json` — key inventory and one full repository entry shape
    (12 repositories; `archive_sha256` pinned, bytes not pinned).

## Commands run this session (exact, with results)

| Command | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | clean except `?? docs/OWNER-DECISION-PACKET-PHASE-3B-REMAINING-GATES-2026-10-23.md`; exit 0 |
| `rtk proxy git rev-parse HEAD; git log --oneline -3` | `6279a2e…`; exit 0 |
| `grep -n "__version__" src/crewshal/__init__.py; grep -n "^version" pyproject.toml` | both `0.27.3` |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | exit 0 (run earlier in this session; digest `4bd188de…` reported by the reviewed decision packet at same HEAD) |
| `ls docs/evaluation/phase-3a-frozen/` | 20 files (README + 19 JSON inputs) |
| `find /Volumes/X10Pro -maxdepth 2 -name "*.sparseimage"`; `ls -d …vmwarevm` | only the Remaining-stage sparseimage found; three guest bundles listed in the proposal |
| `ls /Volumes/` | `Macintosh HD`, `Recovery`, `X10Pro` — both Phase 3B stage volumes unmounted |
| JSON field walks (toolchain manifest, retained readback, corpus.json) via `.venv`/system python | values quoted in the proposal; exit 0 |
| `rtk proxy grep -rlE "platform\.system\|sys\.platform\|skipIf.*Linux\|skipUnless.*Linux" tests/` | six deferred Linux-specific modules named in stage S2 |
| `python3 -c "print(sum([...]))"` | computed toolchain archive sum 1,368,218,293 (corrected one wrong pre-patch figure in the proposal; correction applied and diff shown) |

No test module was executed this session. No broad discovery ran. The two exit-0 checker facts are cited
from the reviewed decision packet where not re-run here.

## Codebase graph evidence (codebase-memory skill, Verify tier)

- `list_projects`: project `Volumes-X10Pro-Crewshal`, branch `codex/phase1-architecture`.
- `check_index_coverage` (generation `2026-10-23T10:06:16Z`, recording complete) for
  `scripts/check_phase_3a_freeze.py`, `scripts/phase3b_development_ledger.py`,
  `scripts/phase3b_capped_archive_continue.py`, `scripts/phase3b_extract_remaining.py`,
  `src/crewshal/dispatch.py`, `src/crewshal/linux_bootstrap.py`,
  `tests/acceptance/test_phase3b_development_ledger.py`: all `no_recorded_issue`, freshness
  `metadata_match`. Best-effort signal only; no completeness claim.

## Deferred, not passing

The six Linux-specific acceptance modules named in stage S2 remain deferred under ADR 0009. Linux platform
conformance, Phase 3B calibration, and Phase 3C remain closed. No claim in the proposal says any of them
passes. The three `test_phase_2c_native_*` modules are flagged for reviewer choice (decision D-E).

## Claims-to-evidence check performed before writing

- "16 retained archives, upper bound 4,371,619,599" — read from the retained readback JSON this session.
- Per-archive byte list — printed from the same record this session; sum recomputed (1,368,218,293).
- "corpus.json pins 12 repositories; bytes not pinned" — printed key set of a repository entry this
  session (`archive_sha256` present, no byte field).
- Stage-volume mount state and sparseimage location — `ls /Volumes/` and `find` output this session.
- Guest bundle paths — `ls -d …vmwarevm` output this session. No guest was opened.
- ISO transfer 3,825,512,448 bytes and remaining-limit figure — quoted from the guest preparation record.

## Unknowns and risks (proposal section 10, U-1…U-12)

Host identity, guest capacity (recorded 8 GiB RAM stop), transport path, native-module inclusion, CLI
Linux arm64 availability, effective commands/digests/providers (null in pinned records), B1 script absence
and condition P contract, apt closure bytes, Archive-stage image location, quota debit reality, droplet
availability/price, and frozen runtime-selection reachability. The proposal never converts an unknown into
zero or a pass.

## Decision requests to the owner (proposal section 11)

D-A approve/amend the proposal; D-B host option A vs B plus who performs boot/resize/preparation; D-C
quota-debit acceptance or hard-cap proof; D-D B1 script and condition P; D-E native-module inclusion.
Corpus budget (G2), protocol amendment (G3), and sealed exposure (G4) are explicitly not requested.

## Preservation statement

No Linux guest, droplet, evaluation row, sealed row, credential store, or paid service was used. No tracked
file, version, or Git record changed. Both new files stay untracked for owner review. No commit or push
occurred and none will occur from this session.

## Continuation prompt (after Codex review and owner decisions)

**SUPERSEDED — do not use this prompt (Codex audit REVISION finding 6, corrected 2026-10-23).** It refers to
the withdrawn D-A…D-E decision set and can authorize host stages before their bindings close. The single
current continuation prompt is in
`docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md`. That packet did not exist
when this sentence was first written; the audit REVISION-3 follow-up session of 2026-10-23 created it.

> Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal`. Read `AGENTS.md`,
> `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md` current state, ADR 0009, and the reviewed
> `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` with its review packet. Apply the
> owner's D-A…D-E outcomes to the proposal. If any host action is now authorized, execute only stage S0 and
> the authorized host's stage S1 observation, record exact outputs, and stop at the next unauthorized
> boundary. Otherwise publish the reviewed proposal as a tracked document via Codex and stop. Make no other
> source change.

## Correction log — 2026-10-23 revision session (untracked)

The Codex audit of the proposal directed a bounded repair session. This session revised
`docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` in place (revision 2, G1 scope).
Corrections to this packet's own claims and to the proposal:

1. Withdrawn: "no B1 script exists." A draft exists at `docs/PHASE-3B-B1-MANUAL-SCRIPT-2026-10-19.md`,
   sha256 `c031a045af15436462fa3100c14f32bc06005db5b651d8d8282dadaf1e02e1e7`, ledger status
   "draft only; no B1 row may start" (`effective_native_command_bound: false`).
2. ~~Withdrawn: "no baseline conformance record exists."~~ **FALSE WITHDRAWAL — removed (Codex audit
   REVISION finding 3, corrected 2026-10-23).** Revision 1 never made that claim; its §S4 cited
   `docs/evaluation/phase-3a-frozen/baseline-conformance.json` directly. Only the B1 half of this entry was
   real (item 1). The record itself stands: 10 `mandatory_actual_cases`, all native/platform cases recorded
   unavailable.
3. Withdrawn: the evidence citation `development.proposed_quota_submission_ceiling (line 594)`. That key does not
   exist in the admission manifest. The real records are line 593 `subscription_quota_debit` and the nearby
   `subscription_turn_limits` (256/256).
4. Withdrawn: "six Linux-specific modules" exclusion list. Source inspection on 2026-10-23 found no platform skip
   marker in any of the 80 acceptance test modules; 37 import `crewshal.linux_*` through deterministic fixtures.
   The three Phase 2C native fixture modules (12 tests) passed locally: exit 0, 0.011 s
   (`rtk proxy env -u PYTHONPATH .venv/bin/python -m unittest tests.acceptance.test_phase_2c_native_continuation
   tests.acceptance.test_phase_2c_native_readback tests.acceptance.test_phase_2c_native_readback_v2`).
   **Amended per audit REVISION finding 4 (corrected counts, re-verified in the revision-3 session):** 79 test
   modules plus `__init__.py` (80 files); 38 reference `crewshal.linux_*`; 15 patch `crewshal.linux_*` internals;
   7 reference platform values; 27 launch real subprocesses. The classification is by actual effects and fixtures,
   not by skip-marker absence. Proposal section 6 holds the bounded-group table and reproduction commands.
5. Withdrawn: "12 GiB corpus transfer." The four selected `corpus.json` archives total 2,777,282 bytes
   (343,014 + 1,580,238 + 655,699 + 198,331), matching ledger `selected_source_archive_bytes`.
6. ~~Withdrawn: "96,154,107,538 retained archive bytes." That figure appears in no repository record; the volume
   `/Volumes/CrewshalPhase3BArchiveStage` is unmounted now (`du`: No such file or directory). Recorded values used
   instead: 1,368,218,293 compressed bytes and 4,371,619,599 regular content bytes for the 16 retained archives.~~
   **FALSE WITHDRAWAL — removed (Codex audit REVISION finding 3, corrected 2026-10-23).** Revision 1 never wrote
   "96,154,107,538"; grep of the revision-1 text in
   `/Users/hamedprooshani/Downloads/prepare-consolidated-linux-campaign-plan-local-24.json` (message 72) returns no
   match. The figure first appeared in this revision's own log. Revision 1's real retained-bytes history: it wrote
   "1,459,270,803 observed sum" and patched it in-session to "1,368,218,293 computed sum". The recorded readback
   values (1,368,218,293 compressed; 4,371,619,599 content upper bound) remain the ledger.
7. ~~Withdrawn: "up to four elapsed days." The proposal now uses the dated October 18 batch envelope, re-bound by the owner.~~
   **FALSE WITHDRAWAL — removed (Codex audit REVISION finding 3, corrected 2026-10-23).** Revision 1 never wrote
   "up to four elapsed days" (no grep match). Its only duration values were the per-unit ceilings ("8 h active /
   24 h wall", "600 s deadline", "900 s", "batch 14 days"), which later revisions kept as proposed values.
8. Title/scope reconciled: the document is now the G1 qualification plan (stages S0–S5); G2 corpus rows and G3 protocol
   amendment keep separate admission and budget gates; no claim of completing all deferred Linux tests.
9. Paid-host exposure reconciled: droplets are excluded from this campaign (owner's existing local VMware guest only);
   a droplet election would need its own batch proposal with cost exposure per the October 5 declaration.
10. Cleanup authority is now part of the campaign request, not deferred to later owner instruction.

## Remaining unknowns after revision

- Selected guest identity and its live RAM/CPU/disk observations (two guests exist; capacities differ).
- Retained-volume on-disk totals pending a mount readback, including the 305,722,916,608-byte free-space figure.
- Effective native commands, executable hashes, effective configuration, and provider identities for both CLIs (null in the retained inventory).
- The private delivery method for retained archives and the checkout into the guest.
- A positive network-retrieval allowance: current conservative balance is 0, so even the 2,777,282-byte corpus retrieval is blocked until owner approval.
- Subscription quota debit remains unknown; explicit owner acceptance with hard-stop rules is requested in the revised proposal.

Verified state this session: branch `codex/phase1-architecture`, HEAD `6279a2e`, version 0.27.3, four untracked docs (unchanged set).
No Linux test, guest, droplet, retrieval, evaluation row, paid service, credential access, commit, or push was performed.
