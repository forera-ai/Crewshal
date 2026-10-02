# Phase 2C resumption prompt

Phase 2C is incomplete. The 0.3.0 checkpoint records a denied profile, public-seam assessment, frozen synthetic protocol and offline refusal tests. No containment case passed.

## Initial prompt

```text
Continue Crewshal in /Volumes/X10Pro/Crewshal. Resume Phase 2C only; do not start 2D. Read AGENTS.md, HANDOFF.md, DEVELOPMENT-PLAN.md, EXECUTION-QUALIFICATION.md and the original PHASE-2C-PROMPT.md. Use the actual Crewshal checkout. Verify HEAD/status, graph generation/coverage and reproduce the three acceptance modules, complete offline suite, static checks and fresh wheel/CLI checks with requirements-dev.lock.

Preserve the achievement ledger and unrelated work. Protocol docs/qualification/phase-2c-v1.json is frozen at SHA-256 fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563. The observed record is denied: Docker client 29.8.1 was present, but unix:///var/run/docker.sock was unavailable. No other engine/context was examined; no image, Linux execution or credential broker was qualified.

First establish an explicitly approved available Linux engine endpoint and immutable image/toolchain. Record the missing owner/environment decision if these remain unavailable; do not start/install a VM or inspect credential stores to guess a substitute. Obtain an accepted credential mediation design and test it only with synthetic secrets. No worker may mount host homes, SSH agents, credential stores, coordinator state, original checkout or Docker sockets.

scripts/qualify_phase_2c.py is only a preflight/denial utility: even an available daemon does not run malicious worker probes. Implement a bounded no-model synthetic probe runner only after these prerequisites. Freeze its commands/payloads/limits before probes; preserve all v1 mandatory cases. Any prospective protocol amendment needs a reason/new digest and invalidates old observations. Qualify exact read/write/scratch/network grants, effective hook/MCP/plugin/instruction exclusion, credential inheritance/mediation, independent credential-free validation and detached descendant/cancel/deadline behavior. Parent-side fixture and sink checks must independently verify outcomes. Missing/failed/unavailable cases remain denied; no unrestricted fallback.

Public Orchestrate revision 1846530cf4383c4592d739601f3c9870e83d9a13 provided skill contracts without an executable seam to test in that plugin snapshot. Orka revision 9e366915fc6cd6ede5aa47ac7a3b418a32ff528b passed 20 fake-backend tests, but actual native helper probes retained synthetic ambient secret/SSH_AUTH_SOCK and hook settings. Reassess fitting public seams behind the candidate outer boundary. Record exact revision/license and limits; neither fake tests nor documentation prove containment. No private Forge inputs or new adapter/model/tool loop.

Qualification record APIs are trusted-coordinator inputs only; all execution_allowed values remain false. Bind every relevant runtime/substrate/configuration/toolchain/harness/protocol/design identity and test stale/missing/failing refusal. No live implementation, paid product/provider calls, benchmark spending, hold-outs, application, merge, deployment or registry release.

Record pass/fail/unavailable separately. If a mandatory probe fails or is unavailable, retain denial, identify the smallest remediation and stop at the blocked 2C boundary. Otherwise independently rerun mandatory cases and offline/fresh-artifact verification. Update README, CHANGELOG, plan and handoff; synchronize semantic version, commit and push the current branch under AGENTS.md authorization. Deliver a 2D prompt only if every 2C gate passes. Otherwise update this precise 2C resumption prompt and exact inputs.
```

## Exact input files

All paths are relative to `/Volumes/X10Pro/Crewshal`. No previous temporary directory, container, database or clone is a prerequisite.

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
- `docs/PHASE-2C-RESUME-PROMPT.md`
- `docs/EXECUTION-QUALIFICATION.md`
- `docs/qualification/phase-2c-v1.json`
- `docs/qualification/phase-2c-observed.json`
- `src/crewshal/contracts.py`
- `src/crewshal/gates.py`
- `src/crewshal/durable.py`
- `src/crewshal/state.py`
- `src/crewshal/qualification.py`
- `scripts/qualify_phase_2c.py`
- `scripts/assess_orka_seam.py`
- `tests/acceptance/test_phase_2a.py`
- `tests/acceptance/test_phase_2b.py`
- `tests/acceptance/test_phase_2c.py`
- `pyproject.toml`
- `requirements-dev.lock`
