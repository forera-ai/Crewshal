# Next-session prompt — finish Phase 2D core software

Work in `/Volumes/X10Pro/Crewshal`.
Complete Phase 2D software development under the revised plan, then stop at that milestone.
Phase 2D is active and unblocked for development.
The owner deferred platform adaptation and live qualification until core development is complete.
Do not return to the Linux exception sequence.

## Read first

1. `AGENTS.md` and its referenced RTK instructions.
2. `docs/HANDOFF.md`, starting with the latest current-state entry.
3. `docs/DEVELOPMENT-PLAN.md`, including its revised Phase 2D acceptance section.
4. `docs/decisions/0007-core-development-before-platform-qualification.md`.
5. `docs/ARCHITECTURE.md` and `docs/decisions/0002-minimal-architecture.md`.
6. `docs/PHASE-2D-CORE-INPUTS-2026-10-15.json` for exact starting files and their preparation hashes.

The latest owner instruction and accepted ADR 0007 supersede historical requirements to complete Linux qualification before source development.
Do not ask again for routine implementation permission or this work-order decision.

## Implement the planned software

Use graph discovery and coverage checks to inspect the existing core and first-runtime integration.
Start with `runtime.py`, `dispatch.py`, `app_server.py`, `candidate.py`, `integration.py`, `durable.py`, and `gates.py`.
Read their relevant tests and follow actual dependencies when needed.
These are starting points, not an exhaustive dependency map.
State the concrete missing behavior briefly, then implement it.
Do not spend the session producing another proposal or documentation-only continuation.
If an acceptance condition already passes, retain its evidence and work on the remaining conditions.
Do not invent features to enlarge the milestone.

Complete one coherent workflow through the actual production coordinator:

- Accept a confirmed project model and approved task through the existing first-runtime contract.
- Capture deterministic runtime events and a changed disposable candidate.
- Freeze the candidate and preserve the original checkout and dirty files.
- Capture separate validator results for the exact candidate and approved check definitions.
- Persist candidate identities, claims, evidence, and state transitions through the actual durable store.
- Compute the verdict through the existing rules with current decisions and valid scope.
- Handle failure, cancellation, timeout, refusal, and restart without false success or an implicit retry.

Use deterministic fixtures for external runtime and validator effects.
Exercise the real integration, storage, capture, and verdict code.
Do not mock the coordinator under test or create success by inserting handcrafted final evidence.
Keep worker claims separate from coordinator evidence.
Test forged success text, malformed events, stale bindings, candidate mutation, failed checks, missing evidence, and interrupted recovery.
Use fresh repositories, state, artifacts, and fixtures.

Reuse the existing architecture and interfaces.
Where necessary, isolate Linux effects at the existing adapter boundary while preserving its operational refusal checks.
Do not build another sandbox, framework, provider SDK, tool loop, or second-runtime adapter.
Phase 2E remains the next software milestone after this session.

## Development boundaries

Focus only on software required by the revised Phase 2D plan.
Do not develop or test Linux, VMware, AppArmor, cgroups, loop devices, mounts, or platform qualification.
Do not access SSH, credentials, private VM inputs, or the private custody index.
Do not run v29, another exception batch, a real coding runtime, a model call, or a paid host.
Existing source and evidence remain preserved; no host shutdown or retained-object cleanup is authorized.
Keep operational execution admission closed.
Fixture success must not set platform qualification or real execution permission to true.
Do not mark unknown historical results as passed.

Use RTK for shell commands and ASD-STE100 for human-readable text.
Preserve all unrelated dirty work.
Use narrow changes and behavior-based regression tests.
Run focused checks during implementation, then the complete offline suite and relevant static checks.
Build and verify a fresh installed wheel without network access or private service dependencies.
Do not repeatedly run unchanged checks without a new reason.

## Starting evidence and completion

Prepared base revision: `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc`.
Prepared branch: `codex/phase1-architecture`.
The dirty candidate is unreleased `0.13.0`.
Confirm the current Git state before editing and preserve changes made since prompt preparation.
The preceding source and installed suites each passed 1222 test occurrences before this documentation update.
That result is a baseline, not fresh verification of the next implementation.

Finish every revised Phase 2D software acceptance condition before declaring software completion.
Report actual commands, results, environment, revision, and limitations.
Use the status "Phase 2D software complete; platform and live qualification deferred" only when the software checks pass.
Update README, CHANGELOG, handoff, next-session prompt, and synchronized package versions under the standing publication rules.
Commit and push the coherent software milestone to the current branch without another routine permission request.
Do not publish unrelated work, credentials, private artifacts, or raw confidential logs.
Stop after publication and provide the Phase 2E software prompt and exact input files.
Do not merge, deploy, publish a package, run live evaluation, or start Phase 2E in this session.
