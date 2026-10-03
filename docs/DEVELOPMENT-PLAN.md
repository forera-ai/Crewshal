# Crewshal phased development and acceptance plan

Owner declaration recorded: 2026-10-02. Consumer: owner and each implementation/test session. Status: initial bounded delivery plan; refine from evidence without silently weakening gates.

## Operating contract

Each row below is one separate session boundary. Phases 2A and 2B are complete; the next session **resumes blocked 2C**. Do not run several milestones in one chat merely because time remains. Start by reading [HANDOFF.md](HANDOFF.md), identify prerequisites, inspect the actual checkout, and state scope. Finish with a checkpoint, reproducible evidence, updated handoff and a complete next-session prompt. A failed required criterion leaves the milestone incomplete.

A milestone has four parts: plan the concrete change; implement only its scope; independently exercise its observable behavior; deliver evidence and handoff. Verification must include failure cases, not implementation-mirroring assertions. Tests should operate from a fresh checkout using synthetic fixtures and temporary state. Code from completed prerequisites may be required, but their generated artifacts or earlier test runs must not be required.

## Milestone map

| ID / session | Deliverable | Prerequisites | Independent acceptance / completion gate | Status |
|---|---|---|---|---|
| 0 | Evidence/audit, collision screening, narrowed hypothesis and evaluation proposal | Owner mission | Required reports exist; provenance/limitations visible; no copied private material or unsupported results | Complete |
| 1 | Minimal architecture and consequential ADR | 0 and owner authorization | Domain, discovery, adapters, capabilities, policy/risk/routing, evidence, security, recovery and usage defined; initial direction accepted | Complete |
| 2A | Installable Python foundation and passive discovery → correction → confirmed model | 1 | Offline acceptance suite and CLI workflow below; no command execution or runtime writes | Complete; 12 offline acceptance cases, wheel install and static checks passed on 2026-10-02; see HANDOFF.md |
| 2B | Durable state, pure gates and trusted evidence contracts | 2A | Crash/recovery fixtures, forged/stale evidence rejection, explicit unavailable/waiver states; deterministic suite | Complete; 21 offline acceptance cases, 33-case complete suite and installed-wheel/static checks passed on 2026-10-02; see HANDOFF.md |
| 2C | Reuse decision and execution-environment qualification | 2B | Existing execution seams assessed against frozen cases; chosen substrate passes containment probes; denied boundaries documented | Blocked; Docker Desktop connected, 9 filesystem/environment and 4 separate lifecycle/validator cases pass; separate synthetic network subset also passes twice; frozen SBX resource/configuration protocol assessed twice with help only; disposable Linux synthetic store preflight passes twice; temporary Ubuntu VPS KVM execution now demonstrated; operational SBX configuration, inner enforcement and request authority remain unqualified; see BROKER-ENVIRONMENT-ASSESSMENT.md |
| 2D | First real runtime and deterministic checks | 2C passed | Bounded live implementation produces candidate and coordinator-captured evidence; fake/offline adapter regressions pass | Planned; live authorization needed |
| 2E | Second runtime, independent review and full vertical slice | 2D | Both role assignments work on the same confirmed model; provider independence, disagreement/remediation and no-review low-risk path verified | Planned; live authorization needed |
| 3A | Frozen comparative evaluation package | 2E | Legally usable corpus, task/rubric/threshold/baseline/version manifests; four-stack coverage or prospective amendment; owner spend approval | Planned; evaluation gate |
| 3B | Calibration and protocol corrections | 3A | Development corpus runs with complete accounting; failures preserved; amended protocol frozen before hold-outs | Planned |
| 3C | Sealed evaluation and owner product decision | 3B | Frozen held-out execution, blind quality assessment, baseline comparison and unknown/failed-run accounting; GO/MODIFY/ABANDON decision | Planned |
| 4 | Conditional release readiness and delivery | Owner GO after 3C | Reproducible package/install, supported-platform CI, security/support limits, license/dependency review, release authorization | Conditional |

The proposed first slice is Python/TypeScript discovery and separately qualified Linux execution. Four-stack evaluation remains the target; expanding to Swift/.NET or amending the protocol must precede hold-out exposure. Do not convert a two-stack pilot into a four-stack portability claim.

## 2A — completed specification

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

## Phase 2C blocked checkpoint — 2026-10-02

Version 0.3.0 freezes 20 mandatory qualification criteria, assesses pinned public seams and verifies 11 offline refusal methods (44 complete package tests). The explicit Docker endpoint was unavailable; zero worker launches and zero containment probes occurred. Credential mediation and the malicious-payload runner remain unavailable. Phase 2C is not complete. The [qualification report](EXECUTION-QUALIFICATION.md) separates public-helper failures, fake/offline passes and unavailable whole-boundary probes. Resume with [the exact prompt and inputs](PHASE-2C-RESUME-PROMPT.md); 2D remains gated.

### Phase 2C Linux resumption — 2026-10-02

Version 0.4.0 resolves the endpoint prerequisite and adds a prospectively frozen cached-Alpine substrate subset. Two final fresh-fixture runs pass nine bounded filesystem/environment criteria; earlier oracle/variant issues remain recorded. Five independent offline checks bring the complete suite to 49 tests. Eleven mandatory whole-boundary cases still remain unavailable; Phase 2C is incomplete and writes stay denied. See [Linux evidence](LINUX-SUBSTRATE-PROBES.md). Resume remaining probes and credential mediation, not Phase 2D.

### Phase 2C lifecycle resumption — 2026-10-02

Version 0.5.0 adds a separately frozen synthetic shell lifecycle/validator subset. Two fresh-fixture runs pass detached-descendant, cancellation, deadline initiation and credential-free validation criteria. Six independent offline failure/refusal methods bring the complete suite to 55 tests. The earlier nine-case filesystem/environment record remains separate; complementary observations are not a combined qualification. Seven criterion categories still lack whole-boundary evidence: network-egress, repository-hooks, global-hooks, mcp-plugins-instructions, credential-mediation, configuration-binding and qualification-refusal. Native coding runtime conformance is also unproved for the observed process cases. No broker design has been accepted or tested. Full Phase 2C remains denied; resume 2C, not 2D.

### Phase 2C network resumption — 2026-10-02

Version 0.6.0 adds a separately frozen synthetic network subset: two local dual-stack sinks, IPv4/IPv6 TCP/UDP/DNS-wire payloads, twelve denied attempts and positive controls before/after. Two v3 fresh-fixture runs pass; v1/v2 pre-client failures and source snapshots remain recorded. Eight offline refusal/falsification methods bring the full suite to 63 tests. The official SBX archive was prepared and help/version inspected offline under owner-approved bounds. Its advertised sandbox minimum and untested outer/inner resource mapping require a prospective protocol; no daemon, login or credential store was accessed. Native runtime network/configuration, accepted synthetic-tested credential mediation and whole-runtime binding/refusal still lack evidence. Full 2C remains denied. See [network checkpoint](NETWORK-SUBSTRATE-PROBES.md); next session resumes 2C only.

### Phase 2C prospective resource/configuration resumption — 2026-10-02

Version 0.7.0 freezes a help-only SBX assessment protocol while preserving all original grants/criteria and the 128 MiB worker ceiling. Direct mapping conflicts with the advertised 512 MiB minimum; a separate outer proposal remains pending. Synthetic HOME does not isolate macOS Keychain. Two pinned help-only assessments succeed, with no new operational category qualified. Seven offline refusal methods bring the full suite to 70 tests. Complete native/broker qualification requires a disposable credential domain, independently enforced inner worker, prospective operational identities/configuration and observed caller/request authority. See [protocol and refusal evidence](SBX-PROTOCOL-ASSESSMENT.md); Phase 2D remains gated.

### Phase 2C disposable broker-store environment — 2026-10-02

Version 0.8.0 demonstrates the Linux SBX file-store fallback twice in separate unprivileged, network-none Ubuntu containers with synthetic secrets only. The credential-store domain is disposable and separate from macOS Keychain, but the observed host lacks a KVM device/sysfs entry and does not qualify an operational SBX sandbox. Eight offline refusal/oracle methods bring the full suite to 78 tests. Prior v1/v2 oracle failures remain recorded. All original twenty whole-runtime results remain unavailable in this profile. Supply a disposable KVM-capable Ubuntu host or separate macOS credential domain and approve the pending outer envelope; then freeze and test the native/request-authority boundaries. See [the exact evidence and next gate](BROKER-ENVIRONMENT-ASSESSMENT.md). Phase 2C remains blocked; 2D is gated.

### Phase 2C temporary KVM host capability — 2026-10-02

Version 0.8.1 records two frozen trusted 1 MiB x86 HLT executions on an owner-supplied temporary Ubuntu 24.04.5 VPS. KVM API 12, VM/vCPU creation and exit reason 5 pass. A supplementary non-KVM-user device access attempt is denied. Final process/FD inventories find no SBX/QEMU process or remaining KVM VM/vCPU handle; no remote file/package was created and SSH is disconnected. This demonstrates host hardware access only, not SBX, broker authority, native configuration or inner resource enforcement. The owner plans to delete the host; reverify any replacement before use. Full 2C remains blocked. See [host evidence](KVM-HOST-ASSESSMENT.md).

### Phase 2C operational preparation and resource decision — 2026-10-02

Version 0.8.2 prepares the official x86_64 SBX bundle locally and matches the published release digest, without executing bundled programs. The [operational proposal](SBX-OPERATIONAL-PROPOSAL.md) specifies concrete resource ceilings and the required freeze-before-start sequence. Current disposable host access and owner resource approval remain pending. All 78 offline tests pass; no operational/native probe or new whole-runtime criterion passes. Phase 2C remains blocked and 2D stays gated.

### Phase 2C replacement-host readiness — 2026-10-02

Version 0.8.3 records owner confirmation that the temporary VPS was deleted. The first replacement passes two frozen trusted KVM HLT runs but fails memory admission; a second owner-supplied replacement passes KVM twice and sampled memory/disk headroom. Matching Linux SBX version/help succeeds twice with prospectively source-bound capture. See [first refusal](REPLACEMENT-HOST-ASSESSMENT.md) and [current preflight](AMD64-HOST-PREFLIGHT.md). Resource approval, operational identities and effective quotas/inner controls remain unresolved. A [readiness checklist](PHASE-2C-READINESS.md) and bound non-executable snapshot preserve known artifact identities, enumerate unresolved operational bindings and specify independent inner-enforcement acceptance before native startup. All 78 offline tests pass; hardware diagnostics pass; operational identity freeze and inner qualification remain unavailable. No original manifest/grant changes or new whole-runtime passes. Phase 2C remains blocked; resolve resource approval and the operational bindings/controls, not Phase 2D.

### Phase 2C resource approval checkpoint — 2026-10-02

Version 0.8.4 records direct owner approval of the unchanged [operational envelope](RESOURCE-APPROVAL-AND-FREEZE-STATUS.md) in a separate digest-bound record. Historical proposal/readiness inputs remain immutable. Current host access was requested but not supplied; no remote connection or operational/native probe ran. Complete identity freeze, effective aggregate/quota controls and inner enforcement remain unavailable. All 78 offline tests pass; resource approval is authority evidence, not containment evidence. Resume 2C from current authorized host access without asking again about unchanged ceilings. Phase 2D remains gated.

### Phase 2C current-host and immutable artifact preparation — 2026-10-03

Version 0.8.5 verifies the newly supplied disposable host twice and prepares immutable SBX/Codex candidate bytes without daemon/native execution. See [current preparation](CURRENT-HOST-IDENTITY-PREPARATION.md). Host retention is an explicit owner instruction; no deletion guidance at intermediate boundaries. Full operational identity/configuration freeze and inner enforcement remain blocked. A [bounded network-denied daemon/settings diagnostic](DAEMON-CONFIG-DIAGNOSTIC-PROPOSAL.md) awaits a narrow owner exception to the complete-freeze-before-creation gate; it has not run. Final owned-unit/process/KVM inventories are empty and verified preparation artifacts are retained. All 78 network-denied offline tests pass. No original grant, case or previous profile changes; no Phase 2D work.

### Phase 2C bounded daemon/settings diagnostic — 2026-10-03

Version 0.8.6 records owner continuation on the supplied droplet and two executions of the exact bounded daemon/settings source. See [the assessment and limitations](DAEMON-CONFIG-DIAGNOSTIC-ASSESSMENT.md). Identical effective settings and trusted host-service controller/namespace observations are reproduced; both scoped final inventories are empty. No VM, image load, worker, validator, store or provider request runs. Complete operational identities/controls and caller/request authority remain unavailable, so inner enforcement is not run and full 2C stays denied. Preserve the original profiles/grants and keep the droplet; resolve supported inner controls and complete the prospective manifest before qualification. No new unchanged-envelope or diagnostic decision is needed; no Phase 2D work.

### Phase 2C private configuration and host quota controls — 2026-10-03

Version 0.8.7 reproduces private effective configuration twice and records source-bound host XFS quota prerequisites. Physical quota reaches exact allocated ceilings but permits oversized sparse logical files. A separate combined RLIMIT_FSIZE/inode quota/hardlink-denial host prototype passes bounded logical regular-file oracles in two fresh fixtures. Its 512 KiB per-file limit and native compatibility remain unqualified; no inner criterion is promoted. Preserve parser/oracle/capture failures and all original profiles. The [control assessment](CONTROL-RESOLUTION-ASSESSMENT.md) and [proposed trusted infrastructure-discovery ordering amendment](PHASE-2C-INFRASTRUCTURE-DISCOVERY-DECISION.md) identify the smallest pending owner gate. No VM or native runtime runs; complete freeze, inner qualification and caller/request authority remain unavailable. Keep the same host and prepared artifacts. Resume 2C only; 2D remains gated.

### Phase 2C approved discovery admission — 2026-10-03

Version 0.8.8 records direct discovery ordering approval and source-bound admission variants. Initial device denial is preserved; corrected private services observe original aggregate ceilings and pass trusted HLT twice each. Actual mountless SBX create returns Docker authentication-required refusal in both fresh fixtures. The approved scope excludes login and requires stopping on that prerequisite. No SBX guest, complete freeze or inner run is claimed. See [the exact assessment](GUEST-DISCOVERY-ASSESSMENT.md). Smallest next capability is separately authorized isolated Docker authentication or an officially supported unauthenticated path; do not request a new droplet or resolved resource/discovery approval. Keep existing host/artifacts; 2D remains gated.
