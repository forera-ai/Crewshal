# Crewshal rolling handoff and project memory

Last updated: 2026-10-02. Consumer: the next session and owner. This is the continuity record; [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines independently testable milestone gates. Preserve the session ledger when updating current state.

## Current state

- Repository: `prooshani/Crewshal`; display name Crewshal, pronounced like crucial; Apache-2.0.
- Phase 0 complete. Phase 1 initial architecture direction accepted through the owner's instruction to continue on 2026-10-02. Session-based delivery plan established. **Next milestone: 2A.**
- Accepted direction: local Python coordinator, versioned models, SQLite state, Codex/Claude Code adapters, independent provider review where required, trusted revision-bound evidence and qualified isolation. No runtime implementation exists at this checkpoint.
- Owner declaration: each phase or major portion gets a separate session, tracked achievements, independent acceptance checks, updated handoff and next-session prompt. AGENTS.md makes this persistent for future sessions.
- Boundaries: clean independent work; preserve private-source confidentiality; no paid runs, agent writes, evaluation or publication without their applicable gates. Four-stack evaluation remains later work.
- Current branch at preparation: `codex/phase1-architecture`. Initial published main revision: `04d6f68e1914285fc660606348cd0a5616d1152f`. Local milestone checkpoints follow; remote publication has not been performed for these changes.
- Local checkout is named Crewshal. The desktop project's saved path still reported the old Foreman directory during preparation. Open the actual Crewshal checkout when starting the next session; do not create another repo or overwrite a checkout to compensate.

## Start-of-session procedure

1. Open the Crewshal checkout. Read AGENTS.md, this document, DEVELOPMENT-PLAN.md and the relevant architecture/ADRs. Check branch, HEAD, status and graph freshness; preserve unrelated dirty work.
2. Name one active milestone and its prerequisites. Verify the prior checkpoint and acceptance evidence instead of assuming completion from chat.
3. Implement, test and deliver only that scope. Update this handoff and the plan, checkpoint the work, provide the next standalone session prompt and stop at the boundary.

## Achievement ledger

### Phase 0 / initial repository — 2026-10-01

Delivered AUDIT.md, COMPETITIVE-LANDSCAPE.md, PRODUCT-HYPOTHESIS.md, INITIAL-EVALUATION-PLAN.md, naming ADR, README, Apache-2.0 and repository initialization. Public initial checkpoint: `04d6f68e1914285fc660606348cd0a5616d1152f`. Name collision screening was bounded, not legal clearance. Proprietary predecessor evidence is owner-only, not publicly reproducible. No product performance/security benchmark passed or was claimed.

### Phase 1 / architecture and session workflow — 2026-10-02

Delivered Phase 0 closure, architecture, consequential ADR, updated status documents, persistent AGENTS.md, development plan and this rolling handoff. Owner authorized continuing after presentation and required separate sessions. The architecture covers the mission's domain/discovery/adapters/capabilities/workflow/policy/evidence/risk/routing/security/state/observability areas.

Evidence: local Codex/Claude CLI version/help inspection, current primary documentation and source review supported feasibility only. Documentation verification: an inline Python checker passed for all 12 Markdown files (local links, balanced fences, whitespace, milestone IDs and architecture topic coverage); `rtk proxy git diff --check` and `rtk proxy git diff --cached --check` passed. The initial topic check found that the domain heading lacked an explicit label; the heading was clarified and the checker rerun successfully. There are no executable runtime tests at this milestone; isolation, credential treatment, runtime contracts and comparative advantage remain unproved. No model calls, paid benchmarks, container probes or private credential inspection were performed. Local Git delivery revision is recorded by the milestone commit containing this entry; resolve it with `git log -1 --format=%H -- docs/HANDOFF.md` at this checkpoint rather than embedding a self-referential hash here.

## Open gates and risks

- 2A/2B are offline implementation gates. No agent execution should be added early.
- 2C must qualify the complete execution boundary and decide reuse from behavior evidence. Credential mediation is unresolved; a Docker executable is not evidence of containment.
- 2D/2E need explicit bounded live-run authority and resource ceilings. Missing provider identity blocks strict independence.
- 3A needs legal corpus selection, baseline conformance, frozen criteria and spending approval. Numerical thresholds remain proposals.
- Swift/.NET execution support is not delivered. Hold-outs stay sealed. Release/product expansion remain owner decisions.

## Next-session prompt — Phase 2A

```text
Continue Crewshal in its existing checkout (currently /Volumes/X10Pro/Crewshal). This is a new session for milestone 2A only: the Python foundation and passive discovery → human correction/confirmation → validated project model.

Read AGENTS.md, docs/HANDOFF.md, docs/DEVELOPMENT-PLAN.md, docs/ARCHITECTURE.md and docs/decisions/0002-minimal-architecture.md. Check HEAD/branch/status and codebase graph freshness. Use the existing local architecture checkpoint; preserve unrelated changes. Do not assume the stale Foreman desktop path is the checkout.

The owner has accepted the initial architecture direction and authorized bounded implementation. Implement a minimal installable Python package/CLI with versioned typed contracts, manifest-backed Python/TypeScript discovery, explicit provenance/inference/unknowns, interactive correction and confirmation, coordinator-owned state, and narrow invalidation. Follow all 2A acceptance cases in the development plan. Create a standalone offline acceptance module, synthetic fixtures and reproducible setup; run the acceptance suite, relevant full offline suite and install/CLI checks. Tests must need no provider credentials, network or previous run artifacts.

Do not implement runtime launchers, call models, inspect credential stores, execute repository scripts, run containers, expose hold-outs, copy private Forge material, merge or publish. Unknowns must remain explicit. Limit work to 2A; no automatic transition into 2B.

At closure, record exact checks/results/environment, limitations, base/delivery Git checkpoint and artifacts in docs/HANDOFF.md; update milestone status in docs/DEVELOPMENT-PLAN.md and README.md. Make a coherent local commit after verification, leave publication separate, and provide a full next-session prompt for 2B. If a required gate fails, record incomplete/blocked status and a precise resumption prompt instead of declaring completion. Stop after 2A delivery.
```
