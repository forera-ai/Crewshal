# Crewshal rolling handoff and project memory

Last updated: 2026-10-02. Consumer: the next session and owner. This is the continuity record; [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines independently testable milestone gates. Preserve the session ledger when updating current state.

## Current state

- Repository: `prooshani/Crewshal`; display name Crewshal, pronounced like crucial; Apache-2.0.
- Phases 0, 1 and 2A complete. The initial architecture direction remains accepted. **Next milestone: 2B.**
- Accepted direction: local Python coordinator, versioned models, SQLite state, Codex/Claude Code adapters, independent provider review where required, trusted revision-bound evidence and qualified isolation. Phase 2A delivers passive discovery, explicit correction/confirmation and private external JSON model storage. SQLite orchestration and trusted evidence gates remain 2B; no runtime launcher exists.
- Owner declaration: each phase or major portion gets a separate session, tracked achievements, independent acceptance checks, updated handoff and next-session prompt. AGENTS.md makes this persistent for future sessions.
- Boundaries: clean independent work; preserve private-source confidentiality; no paid runs, agent writes, evaluation or publication without their applicable gates. Four-stack evaluation remains later work.
- Current local branch: `codex/phase1-architecture`. Initial published main revision: `04d6f68e1914285fc660606348cd0a5616d1152f`. Local milestone checkpoints follow; remote publication has not been performed for these changes.
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

### Phase 2A / Python foundation and passive initialization — 2026-10-02

Completed this milestone only. Base revision: `fa588e2d01e324399d01b1846fcea2dc26016631` on `codex/phase1-architecture`; checkout was clean. Delivery revision is the local milestone commit containing this entry; resolve it with `git log -1 --format=%H -- docs/HANDOFF.md` at this checkpoint. No push, PR, merge or release occurred.

Artifacts: installable `pyproject.toml`/src-layout `crewshal` package; closed schema-version-1 Pydantic contracts; bounded TOML/JSON discovery; explicit interactive and digest-bound decision replay; provenance-preserving correction/invalidation; private external model state and explicit non-overwriting exports; `tests.acceptance.test_phase_2a`; hash-locked `requirements-dev.lock`; [development/setup guide](DEVELOPMENT.md); updated README and milestone plan. Builds produced ignored `dist/crewshal-0.1.0.tar.gz` and `dist/crewshal-0.1.0-py3-none-any.whl`, not published artifacts.

Acceptance evidence, all confirmed:

1. Python/Hatch commands and TypeScript package/workspace fixtures produce literal candidates, relative manifest-key source locations and independently checked SHA-256 digests. Workspace facts depend on both root/member inputs.
2. Observed, strong/weak inference, unknown and pending/confirmed/rejected states stay separate. Empty/malformed inputs, absent commands/members and conflicting lockfiles remain visible unresolved data. Unknown confirmation without correction is refused.
3. Malicious instruction/setup/script fixtures never execute, even after a command candidate is explicitly confirmed. Symlink escape, private-file, file-count, per-file-size, aggregate-byte and nesting exclusions are visible.
4. Scripted interactive input corrects/rejects/confirms facts, preserves source provenance and inspects stored validated models. Noninteractive defaults stay pending; replay requires explicit local decisions bound to the current model. EOF, stale/malformed batches and unknown IDs refuse materialization.
5. Changed member manifests invalidate member/root-dependent workspace facts while unrelated root check confirmations survive. Unrelated file changes preserve decisions. Removed inputs revoke active facts; source mutation during interaction refuses save. Unsupported versions (including boolean coercion), extra fields, malformed JSON and unbound confirmations are refused.
6. Synthetic original/uncommitted file bytes remain identical after ordinary initialization; state is outside the repository with directory/file modes 0700/0600. State symlinks, repository-local state, path-escaping exports and overwriting existing files are refused. Explicit exports have no private root/state metadata and never become approvals.
7. Fresh built-wheel installation exposes help and actual console-entry-point initialization. Acceptance and full offline suites create all their own fixtures, with empty inherited environment, temporary home and OS-level network denial. No previous model/state artifacts or provider credentials are needed.

Exact verification and environment:

- Observed host: macOS 27.2, build 26B5091g, arm64. Interpreter: CPython 3.12.14 (`/opt/homebrew/opt/python@3.12/bin/python3.12`). uv 0.9.24; RTK 0.50.0. Direct runtime dependency Pydantic 2.12.5; Pydantic Core 2.41.5. Development dependencies mypy 1.18.2 and Ruff 0.14.1; build backend setuptools 80.9.0. All development/runtime transitive versions/hashes are recorded in requirements-dev.lock.
- Setup: `rtk proxy uv venv --python python3.12 .venv`; `rtk proxy uv pip install --python .venv/bin/python -e '.[dev]'`; `rtk proxy uv pip compile pyproject.toml --extra dev --generate-hashes --output-file requirements-dev.lock`. Package/dependency preparation used the package index; test execution did not.
- `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a`: passed during development; final artifact verification runs the expanded 12-case module below. No test count is inferred from earlier runs.
- `rtk proxy .venv/bin/ruff check src tests`: passed. `rtk proxy .venv/bin/ruff format --check src tests`: passed (9 files). `rtk proxy .venv/bin/mypy`: passed, strict, 6 source files. Repeated against the fresh verification environment.
- `rtk proxy uv build --offline`: built sdist and wheel successfully, using the cached pinned backend.
- Fresh verification directory: `/private/tmp/crewshal-2a-verify.EYFzX8`. `rtk proxy uv venv --python python3.12 "$crewshal_verify_dir/fresh"`; `rtk proxy uv pip install --offline --require-hashes --python "$crewshal_verify_dir/fresh/bin/python" -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python "$crewshal_verify_dir/fresh/bin/python" dist/crewshal-0.1.0-py3-none-any.whl`: passed after dependency-cache preparation. Application imports resolved to external site-packages, not editable src. Temporary directory is optional evidence, not a prerequisite for rerunning fixtures.
- With `crewshal_verify_dir` set to that external directory and its home created: `rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2a`: **12 tests passed**. Same wrapper with `-m unittest discover -s tests -t .`: **12 tests passed**. Installed `crewshal --help`: passed; console `crewshal init` is exercised by the acceptance module.
- Markdown local links/fences/whitespace and required current/next-milestone markers checked; `rtk proxy git diff --check` and staged diff check passed before commit. See [development guide](DEVELOPMENT.md) for reproducible setup and network-denial wrapper.
- Jev CLI live availability and a bounded offline-verification decision were checked successfully (decision probability 0.9). Jev was assistant workflow support explicitly requested by the owner, not product/runtime execution. Product tests call no model.
- Codebase-memory CLI was available throughout. Verify-tier startup graph generation was `2026-10-01T23:46:50Z`; refreshed after implementation. Structural search, both-direction CLI trace, exact source snippets and coverage checks informed inspection. Relevant production paths had no recorded gaps; changed test ranges were read directly and the final tree reindexed. Excluded metadata/caches are not runtime evidence; graph cleanliness is not completeness proof.

Failures retained and resolved: the first acceptance test failed because no package existed; subsequent schema refusal exposed Pydantic accepting `true` as literal version 1, fixed by an exact integer validator; one newly added test initially had a misplaced test-body tail (`NameError`), corrected before reruns. The first fresh offline hash-locked install lacked cached wheel archives, so it failed; dependency preparation populated the cache and a new environment then installed fully offline. The first staged whitespace check found a surplus blank line at the end of pyproject.toml; it was normalized and the staged check rerun. None of these failed attempts is counted as acceptance success.

Limitations: verified only on the recorded macOS/Python combination, not Linux/Windows or other Python versions. Discovery supports the documented bounded formats; YAML and other Python build systems remain visibly unsupported. Fingerprints are file-granular; discovery is not an atomic snapshot against adversarial concurrent mutation. Source digests do not prove truth. Exports retain literal repository values/human corrections and must be inspected before sharing; they carry no execution authority. Current JSON storage is atomic model replacement only, with no two-writer conflict detection, migrations, launch reconciliation or trusted evidence persistence. The network-denied test wrapper does not qualify worker execution. No execution adapter, provider SDK, benchmark, container probe, runtime credential-store inspection, hold-out exposure or private predecessor source was used. Agent writes remain disabled; 2C qualification and later owner gates are unchanged.

## Open gates and risks

- 2A passed its offline gate. 2B is the next offline implementation gate; no agent execution should be added early.
- 2C must qualify the complete execution boundary and decide reuse from behavior evidence. Credential mediation is unresolved; a Docker executable is not evidence of containment.
- 2D/2E need explicit bounded live-run authority and resource ceilings. Missing provider identity blocks strict independence.
- 3A needs legal corpus selection, baseline conformance, frozen criteria and spending approval. Numerical thresholds remain proposals.
- Swift/.NET execution support is not delivered. Hold-outs stay sealed. Release/product expansion remain owner decisions.

## Next-session prompt — Phase 2B

```text
Continue Crewshal in /Volumes/X10Pro/Crewshal. This is a new session for milestone 2B only: durable coordinator state, pure gates and trusted evidence contracts.

Read AGENTS.md, docs/HANDOFF.md, docs/DEVELOPMENT-PLAN.md, docs/DEVELOPMENT.md, docs/ARCHITECTURE.md and docs/decisions/0002-minimal-architecture.md. Check HEAD/branch/status and codebase graph project/generation/coverage. Use the existing Phase 2A local checkpoint; preserve unrelated changes. Do not use the stale Foreman desktop path or recreate the repository.

The owner accepted the initial architecture and authorized bounded offline implementation. First reproduce Phase 2A acceptance and install/CLI checks using the pinned setup. Implement only Phase 2B: SQLite coordinator-owned durable records and transactions, schema refusal and safe supported migration with backup, compare-and-update versions/two-writer conflict detection, ordered events and launch-intent reconciliation contracts without any actual launcher or blind replay. Preserve/migrate the Phase 2A external model and human-decision semantics explicitly; never trust a worker-editable export as approval.

Add versioned typed task/run/attempt, claim, evidence, verdict and usage contracts as required by the accepted architecture. Keep gates pure and deterministic. Bind approvals/evidence to exact model/task/policy/scope/candidate digests; reject forged, stale, contradictory or incomplete evidence. Required checks must distinguish passed, failed, skipped, unavailable and termination states. Waivers must identify owner/gate/residual risk and never relabel missing/failed evidence as passing. Missing mandatory provider identity must not establish review independence. Unknown usage/cost stays unknown; cumulative usage deduplicates by attempt/event identity. Avoid speculative adapters, schedulers or new model/tool loops.

Create tests.acceptance.test_phase_2b with independent synthetic temporary databases/artifacts and failure/crash fixtures covering every 2B criterion in the plan: schema refusal/migration safety, transaction ordering, two-writer conflicts, uncertain launch reconciliation without replay, digest invalidation, claim/evidence/verdict authority separation, required-check states, explicit waivers and deduplicated cumulative usage. Run python -m unittest tests.acceptance.test_phase_2b, the complete offline suite including 2A, lint/type checks and fresh install/CLI checks. Fixtures must require no provider credentials, network, containers, adapters or prior generated artifacts. Record exact interpreter/dependency environment and observed failures, not just planned commands.

Do not implement runtime launchers or execution-environment qualification, call product models, inspect credential stores, run repository scripts or containers, spend benchmark funds, expose hold-outs, copy private Forge material, publish, merge or release. Agent writes stay disabled until 2C passes. Limit work to 2B; no automatic transition to 2C.

At closure, append acceptance evidence, exact commands/results/environment, limitations, base/delivery checkpoints and artifacts to docs/HANDOFF.md without deleting prior achievements. Update milestone status in docs/DEVELOPMENT-PLAN.md and README.md, make a coherent verified local commit, and provide a full Phase 2C session prompt. If a required gate fails, record incomplete/blocked status and the smallest resumption condition instead. Stop after 2B delivery.
```
