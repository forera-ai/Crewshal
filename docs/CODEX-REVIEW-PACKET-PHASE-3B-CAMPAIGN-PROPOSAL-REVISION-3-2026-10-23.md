# Codex review packet — Phase 3B campaign proposal, revision 3 (G1 scope), 2026-10-23

Prepared by the Hermes crewshal profile for Codex review. No commit, no push, no publication authority claimed.
This is the single current review packet and the single current continuation-prompt location. The two earlier
packets (`docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-2026-10-23.md` and
`docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-2026-10-23.md`) are marked historical in place.

## Milestone and base

Milestone: one bounded documentation repair — close all six findings of
`docs/CODEX-AUDIT-PHASE-3B-CAMPAIGN-REVISION-3-2026-10-23.md` in
`docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md`, then produce this packet. Read-only local
planning; no host acted; nothing mounted, downloaded, booted, or installed.

Base revision: `6279a2eb32714530beffab7e6425c3d41fbcfbb5` (`git rev-parse HEAD`), branch
`codex/phase1-architecture`, package version 0.27.3 (`pyproject.toml` and `crewshal.__version__`, re-verified
this session). Git status after this session's writes: exactly eight untracked documents, no tracked changes.

## Changed files (all untracked; nothing tracked was touched)

1. `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` — six corrections applied in place
   (section 15 is the new correction log). The frozen package and every other document are untouched.
2. `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-2026-10-23.md` — HISTORICAL RECORD banner added; the
   superseded-prompt note now records that this packet was created by the follow-up session, not earlier.
3. `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-2026-10-23.md` — same historical marking and
   creation note; its acceptance rows remain annotated as inaccurate.
4. `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md` — this packet (new file).

No source, version, README, CHANGELOG, HANDOFF, ADR, frozen package, `SOUL.md`, or Hermes configuration was
modified. No `git add`, commit, or push. No test suite was run: this milestone changes no code, and broad test
discovery was explicitly out of scope.

## Acceptance mapping — the six audit findings

| # | Finding (audit section 15) | Repair in the proposal | Binding evidence |
|---|---|---|---|
| 1 | S1b invented `.tar.zst` names and a `diskutil mount <volume-path>` command; no device identity existed. | Section 2 row and stage S1b rewritten: image `/Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg`, volume `/Volumes/CrewshalPhase3BArchiveStage`, archive paths `<volume>/archives/<id>.blob`. Stage marked BLOCKED; no mount command is given; mounting stays an owner-only exact action. The unrelated Remaining-stage sparseimage is named and excluded. | `scripts/phase3b_capped_archive.py:225,299` (`archives/<id>.blob`); example hash of `archives/dotnet-sdk.blob` at `docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-BOUNDARY-2026-10-19.md:117`; image records at `docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-2026-10-19.md:20-21,68-69`; `ls /Volumes/` this session (volume unmounted); the `.dmg` present on disk (3,221,225,472 bytes). No `/dev/disk*` identity exists in any document (grep), so S1b is blocked per instruction. |
| 2 | S0b measured the transfer only after downloading it; no finite ceiling was derived first. | Sub-step S0b rewritten to BLOCKED before any request: download contract removed, zero transfer allowance preserved, binding closes only when the owner fixes a citable finite byte ceiling. Section 2 row, section 8 wheel row, section 9 cost line, decision 3, and U-13 aligned. | This session grepped every file under `docs/` for a wheel-closure ceiling: none exists. Local macOS install footprint measured with `du -sk`: 7,600 KiB across four `site-packages` directories — reference data for a different platform, not a ceiling. |
| 3 | S0 wrote into an unbound `evidence/` dir; the S2 row claimed bound commands while guest steps lacked `source/` creation and any exact archive command. | S0 first command is now `mkdir -p evidence`. The section 2 S2 row says only the Mac-side command is bound. Stage S2 gives the exact bound Mac-side `git archive` + `shasum` + ledger commands; guest steps are labeled a draft contract that must `mkdir -p source evidence wheels` before extraction; the transfer command stays unbound pending decision 5. | Proposal sections 5 (S0, S2) after repair; audit finding 3 text. |
| 4 | Baseline row mis-described the frozen JSON and G1 did not state whether actual baseline turns were in scope. | Section 3 baseline row corrected: `mandatory_actual_cases` is a list of ten case-id strings; `native_execution: "unavailable"` belongs to the two candidate records only; exactly one macOS `sandbox-exec` conformance command exists (`candidates[].fresh_source_conformance.command`). Section 9 adds "Actual baseline turns: G1 includes none"; S4 repeats it and stays blocked. | Re-verified this session: JSON parse → list, length 10; `sandbox-exec` occurs once in the whole file. |
| 5 | The proposal claimed `corpus.json` has no byte field while section 13 cited its byte counts. | Section 3 corpus row and section 13 entry 4 now agree: byte values live at `repositories[i].source_identity.archive_bytes`; record values stay separate from on-disk availability (closed until S1b). | Re-verified this session by parsing `corpus.json`: python-1 343,014; typescript-2 1,580,238; swift-1 655,699; dotnet-1 198,331; sum 2,777,282 — identical to the retained readback values. |
| 6 | The REVISION-3 packet that both older packets pointed to did not exist. | This file now exists as the single current packet and continuation-prompt location; both older packets carry HISTORICAL RECORD banners and dated notes that this file was created by this follow-up session. | `git status --porcelain=v1` after this write: eight `??` entries, no tracked modifications. |

## Checks run (all local, read-only)

- `git rev-parse HEAD`, `git branch --show-current`, `git status --porcelain=v1` — base and cleanliness above;
  every changed file is untracked.
- Targeted greps of the repaired proposal — no active mount command, no `.tar.zst` archive name, and no S0b
  go-ahead remains outside correction-log narration (lines 47, 138, 166–169, 434–438 are the corrected text).
- JSON parses of `baseline-conformance.json` and `corpus.json`, `sed` line checks of the three source records,
  `ls /Volumes/`, and `du -sk` — outputs quoted in the table above.
- Deferred by design: all Linux checks (ADR 0009), the whole campaign execution, any host action.

## Remaining blockers (unchanged scope; no blocker was silently closed)

- S1b: attach identity (disk identifier/device node) unknown → blocked; owner-only mount approval required.
- S0b: no finite wheel-closure ceiling derivable locally → blocked; zero transfer allowance preserved.
- S2: transport (decision 5) and host (decision 1) unselected; guest commands remain a draft contract.
- S3: per-case containment probe drivers unknown (U-11).
- S4: Linux runner definition and numeric limits unbound; G1 includes zero actual baseline turns.
- The proposal remains **not approval-ready for host action** until the section 2 blockers close.

## Continuation prompt (single current version, after Codex review)

> Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal`. Read `AGENTS.md`,
> `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md` current state, ADR 0009, the six findings of
> `docs/CODEX-AUDIT-PHASE-3B-CAMPAIGN-REVISION-3-2026-10-23.md`, and the repaired proposal with this packet.
> Verify HEAD, branch, version, and Git status; preserve every untracked file. Apply Codex's verdict on this
> packet. If the owner has answered any decision in proposal section 12, bind only that stage: record the
> exact new identities (device node, byte ceiling, transport, host) in the proposal, change nothing else, and
> stop before any host action. If no owner answer exists, make no edit and return this packet unchanged with
> one line per open blocker. Do not mount, download, boot, inspect a guest, use a droplet, or run Linux tests.
> Do not commit or push.

## Preservation statement

This session changed no tracked file and created only untracked planning documents. Dated records in the two
older packets were preserved byte for byte except the appended banners and notes listed above. The frozen
Phase 3A package and private sealed-task custody were not touched, mounted, or exposed.
