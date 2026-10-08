# Next-session prompt: Phase 2C

Phase 2C determines whether existing Orchestrate/Orka execution seams fit Crewshal's accepted contracts, then qualifies the selected execution boundary using frozen synthetic probes. Documentation or an installed Docker command cannot establish containment. A mandatory failure preserves a denied profile and leaves agent writes disabled.

## Initial prompt

```text
Continue Crewshal in /Volumes/X10Pro/Crewshal. This session is Phase 2C only: reuse decision and execution-environment qualification. Phase 2B is complete at package version 0.2.0. Do not begin Phase 2D.

Read the input files listed below. Follow AGENTS.md and docs/HANDOFF.md as authoritative project memory. Check HEAD/branch/status, graph project/generation and relevant coverage. Preserve unrelated changes. Use Crewshal's actual checkout, not the stale Foreman desktop path. Reproduce both acceptance modules, the complete offline suite, static checks and installed-wheel/CLI checks with the pinned setup before relying on the previous checkpoint.

Freeze a bounded repeatable qualification harness and mandatory cases before any probes. Assess the public Orchestrate and Orka execution seams against Crewshal's model/grant/evidence/recovery contracts. Behavior-test matching seams with synthetic no-model payloads; where a seam cannot be tested, record its exact limitation instead of claiming equivalence from documentation. Record pinned revisions, licenses/provenance, environment and observations. Prefer reuse when it fits; record concrete gaps before adding any minimal supervision needed for qualification. Do not copy private Forge code, prompts, schemas, paths or artifacts. Do not build an adapter or a new model/tool loop.

Qualify the chosen execution substrate with synthetic fixtures containing no host secrets. Cover denied external reads/writes; original-checkout and coordinator-state exclusion; symlink/new-file/metadata escapes; unauthorized network and data egress; credential/environment inheritance; injected repository/global hooks, MCP, plugins and instructions; descendant-process escape, cancellation and deadline enforcement. Test the exact read/write/scratch/network grant, effective configuration and credential-free validation boundary. A worktree is not isolation. A container executable or documentation is not qualification. Record OS, substrate/image digest, tool versions, exact commands/grants and passed/failed/unavailable results; no unsupported-platform claims.

Credential mediation needs a tested, accepted design. Use synthetic credentials only; never inspect or mount real credential stores, SSH agents, host homes or Docker sockets into a worker. Record unresolved exposure as a blocking boundary. Qualification records must bind the runtime/substrate/configuration/toolchain versions and invalidate on relevant change. Test that missing, stale or failed qualification keeps writes disabled. If any mandatory case fails or is unavailable, preserve the denied execution profile, document the smallest remediation/owner decision and stop; do not enable unrestricted fallback.

Use only bounded synthetic qualification work. No product model/provider calls, paid runs, benchmark spending, sealed hold-outs, live implementation, automatic candidate application, merge, deployment or package-registry release. Phase 2D live authorization/resource ceilings remain separate. Phase 2B's launch-intent records are inert contracts; do not interpret execution_allowed=false as a launch grant. Successful qualification permits only its exact profile and later approved execution, not general agent access.

Verify the frozen mandatory cases independently, including failure fixtures, and rerun the complete offline regression suite and fresh artifact checks appropriate to changes. Record exact commands, results, environment, revisions, observed failures and limits. Update README.md, CHANGELOG.md, docs/DEVELOPMENT-PLAN.md and docs/HANDOFF.md; preserve the achievement ledger. Bump the synchronized semantic package version, commit and push the current branch under standing owner authorization. Deliver the Phase 2D prompt and exact input files only if 2C passes; otherwise deliver a precise 2C resumption prompt. Stop at the 2C boundary.
```

## Input files

All paths below are relative to `/Volumes/X10Pro/Crewshal`:

- `AGENTS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/HANDOFF.md`
- `docs/DEVELOPMENT-PLAN.md`
- `docs/DEVELOPMENT.md`
- `docs/ARCHITECTURE.md`
- `docs/decisions/0002-minimal-architecture.md`
- `docs/STATE-AND-GATES.md`
- `docs/PHASE-2C-PROMPT.md`
- `src/crewshal/contracts.py`
- `src/crewshal/gates.py`
- `src/crewshal/durable.py`
- `src/crewshal/state.py`
- `tests/acceptance/test_phase_2a.py`
- `tests/acceptance/test_phase_2b.py`
- `pyproject.toml`
- `requirements-dev.lock`

The synthetic suites create their own fixtures. No database, backup, build output or temporary verification directory from this session is a prerequisite.
