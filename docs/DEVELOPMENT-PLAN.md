# Crewshal phased development and acceptance plan

Owner declaration recorded: 2026-10-02. Consumer: owner and each implementation/test session. Status: initial bounded delivery plan; refine from evidence without silently weakening gates.

## Operating contract

Each row below is one separate session boundary. The current session closes Phase 1 and establishes this workflow; the next session is **2A**. Do not run several milestones in one chat merely because time remains. Start by reading [HANDOFF.md](HANDOFF.md), identify prerequisites, inspect the actual checkout, and state scope. Finish with a checkpoint, reproducible evidence, updated handoff and a complete next-session prompt. A failed required criterion leaves the milestone incomplete.

A milestone has four parts: plan the concrete change; implement only its scope; independently exercise its observable behavior; deliver evidence and handoff. Verification must include failure cases, not implementation-mirroring assertions. Tests should operate from a fresh checkout using synthetic fixtures and temporary state. Code from completed prerequisites may be required, but their generated artifacts or earlier test runs must not be required.

## Milestone map

| ID / session | Deliverable | Prerequisites | Independent acceptance / completion gate | Status |
|---|---|---|---|---|
| 0 | Evidence/audit, collision screening, narrowed hypothesis and evaluation proposal | Owner mission | Required reports exist; provenance/limitations visible; no copied private material or unsupported results | Complete |
| 1 | Minimal architecture and consequential ADR | 0 and owner authorization | Domain, discovery, adapters, capabilities, policy/risk/routing, evidence, security, recovery and usage defined; initial direction accepted | Complete |
| 2A | Installable Python foundation and passive discovery → correction → confirmed model | 1 | Offline acceptance suite and CLI workflow below; no command execution or runtime writes | Next |
| 2B | Durable state, pure gates and trusted evidence contracts | 2A | Crash/recovery fixtures, forged/stale evidence rejection, explicit unavailable/waiver states; deterministic suite | Planned |
| 2C | Reuse decision and execution-environment qualification | 2B | Existing execution seams assessed against frozen cases; chosen substrate passes containment probes; denied boundaries documented | Planned; write gate |
| 2D | First real runtime and deterministic checks | 2C passed | Bounded live implementation produces candidate and coordinator-captured evidence; fake/offline adapter regressions pass | Planned; live authorization needed |
| 2E | Second runtime, independent review and full vertical slice | 2D | Both role assignments work on the same confirmed model; provider independence, disagreement/remediation and no-review low-risk path verified | Planned; live authorization needed |
| 3A | Frozen comparative evaluation package | 2E | Legally usable corpus, task/rubric/threshold/baseline/version manifests; four-stack coverage or prospective amendment; owner spend approval | Planned; evaluation gate |
| 3B | Calibration and protocol corrections | 3A | Development corpus runs with complete accounting; failures preserved; amended protocol frozen before hold-outs | Planned |
| 3C | Sealed evaluation and owner product decision | 3B | Frozen held-out execution, blind quality assessment, baseline comparison and unknown/failed-run accounting; GO/MODIFY/ABANDON decision | Planned |
| 4 | Conditional release readiness and delivery | Owner GO after 3C | Reproducible package/install, supported-platform CI, security/support limits, license/dependency review, release authorization | Conditional |

The proposed first slice is Python/TypeScript discovery and separately qualified Linux execution. Four-stack evaluation remains the target; expanding to Swift/.NET or amending the protocol must precede hold-out exposure. Do not convert a two-stack pilot into a four-stack portability claim.

## 2A — next session specification

Deliver a small Python package and CLI entry point, a versioned project-model contract and supported manifest discovery. Implement the interactive discover/propose/correct/confirm/materialize path. Use maintained validation/parsing where appropriate, pin direct dependencies, and document a reproducible development setup. No runtime launcher, model call, container run, new provider SDK, speculative configuration collection or automatic repository mutation.

Acceptance cases:

- A synthetic Python repository and a synthetic TypeScript package/workspace produce manifest-backed stack/package facts and literal command candidates, with relative source locations and source digests.
- Strong/weak inference, unknown and confirmation remain distinct. Missing/conflicting manifests or commands are unresolved; discovery never invents an executable check or auto-confirms it.
- Repository instruction text suggesting shell execution is treated as data. A malicious script fixture is never executed. File/count/size limits and symlink escapes yield visible bounded errors/exclusions.
- Scripted interaction can correct/reject facts, confirm actionable items and inspect the resulting validated model. Noninteractive input may replay explicit human decisions but never silently approve defaults.
- Source changes invalidate dependent confirmed facts; unrelated file changes preserve relevant confirmations. Unsupported schema versions and malformed models are refused.
- Initialization preserves repository bytes and original dirty files. State belongs outside worker/repository authority; exports into the repository require an explicit option.
- A fresh install exposes help and the initialization workflow. The offline acceptance module creates all its own fixtures and passes without provider credentials or network access during test execution.

Required delivery: implement `tests.acceptance.test_phase_2a` (or record an equally explicit replacement before closing), run `python -m unittest tests.acceptance.test_phase_2a` and the appropriate complete offline suite, record the exact interpreter/dependency environment and commands. A planned command is not a passed test. Include install/CLI smoke checks and maintainable lint/type checks appropriate to the chosen package. Do not use held-out benchmark repositories as fixtures.

## Later acceptance contracts

**2B:** build `tests.acceptance.test_phase_2b` with temporary databases/artifacts. Prove schema refusal/migration safety, transaction ordering, two-writer conflict detection, launch-intent reconciliation without blind replay, candidate/model/policy digest invalidation, claim/evidence/verdict separation, required check status handling and explicit waivers. The suite must pass without adapters or containers. Unknown cost stays unknown; cumulative usage deduplicates.

**2C:** define a repeatable qualification harness before probes. First freeze cases and behavior-test or record limitations of existing Orchestrate/Orka seams; documentation alone cannot decide equivalence. Use synthetic no-model payloads to attempt external reads/writes, symlink escapes, unauthorized network, credential inheritance, injected hooks/MCP/config and descendant-process escape. Record OS, image/substrate/tool versions, exact grant and results. No host secrets in fixtures. Test unsafe/missing qualification keeps writes blocked. Credential mediation still needs a tested accepted design; do not assume a container supplies it. If any mandatory boundary fails, preserve a denied execution profile and stop for remediation.

**2D:** offline contract tests use recorded/synthetic event streams for malformed output, missing identity, timeouts, cancellation, quota/refusal and stale evidence. Separately, an owner-approved tightly budgeted live run must use a qualified profile, preserve the original checkout, produce a frozen candidate, run approved checks in a credential-free validator and reject mutation/false completion. Live logs stay private; public evidence is sanitized. Passing mocks does not qualify the real runtime.

**2E:** offline suite verifies independent provider identity, unavailable review blocking, scope/risk escalation, conflict handling and revalidation after remediation. Approved bounded live cases swap Codex/Claude Code roles against the same confirmed model and exhibit revision-bound review/evidence. A distinct session alone does not establish independence. Ordinary/high-risk and low-risk workflows exercise their different gates. Never automatically merge the candidate.

**3A–3C:** use the original [evaluation plan](../INITIAL-EVALUATION-PLAN.md). Freeze legal provenance, repository/task digests, runtime/provider/model/toolchain versions, baseline conformance, seeds/order/cache policy, blinded rubric, thresholds, failure accounting and budget before runs. Calibration amendments carry reasons and versions; never tune against already exposed sealed tasks. Summaries distinguish actual/estimated/quota accounting and report unsupported combinations. Final completion requires an owner decision, not favorable selected demos.

**4:** only after an owner GO decision. Release tests run against built artifacts and a clean supported environment, not an editable development checkout alone. Document unsupported platforms/capabilities, threat-model limits and installation/recovery behavior. Publish only after explicit release authorization.

## Evidence and delivery format

Every closure appends a session ledger entry in HANDOFF.md: milestone, date/session identity when known, base and delivery revision, changes, acceptance cases and exact commands/results, environment, artifacts, limitations, unresolved gates and next scope. Large/private logs live outside the public repository with sanitized summaries; do not commit secrets or private source. Record whether a check was passed, failed, skipped, unavailable or not run. An offline test and a live qualification are different evidence.

Update milestone status only when required gates pass. Preserve past entries and replace only the current-state/next-prompt sections. Check links, Git diff and status; commit a coherent milestone checkpoint. Push/PR/release follows separately applicable authorization. If interrupted or blocked, record partial work and the minimal resumption conditions rather than claiming completion.
