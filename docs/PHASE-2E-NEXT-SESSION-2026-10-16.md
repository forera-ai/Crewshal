# Next-session prompt — Phase 2E software

Work in `/Volumes/X10Pro/Crewshal`.
Complete Phase 2E software under the revised development plan.
Stop after its acceptance checks and required branch publication.

## Read first

Read `AGENTS.md` and its RTK instructions.
Read `docs/HANDOFF.md`, starting with the current state and latest session entry.
Read `docs/DEVELOPMENT-PLAN.md` and `docs/ARCHITECTURE.md`.
Read the accepted architecture decisions, especially ADR 0007.
Read `docs/PHASE-2D-SOFTWARE-COMPLETION-2026-10-16.md` and its verification record.
Use `docs/PHASE-2E-INPUTS-2026-10-16.json` for exact starting files.
Inspect the current Git state and preserve later changes.

## Implement Phase 2E only

Add the second runtime through the existing adapter contracts.
Complete independent review and the planned vertical slice through production coordinator code.
Use deterministic external runtime and reviewer fixtures.
Do not replace the coordinator, durable store, capture, or verdict code with mocks.

Verify both runtime role assignments against the same confirmed project model.
Verify resolved provider identity and block required review when independence is unavailable.
A separate session does not establish provider independence.
Verify ordinary-risk review, high-risk planning approval, and the low-risk path without required review.
Verify actual scope escalation, review disagreement, and explicit human conflict handling.
Verify that remediation creates a new candidate and invalidates affected checks and review.
Preserve claims, captured evidence, decisions, and verdicts as separate records.
Verify cancellation, refusal, restart, and failure without an implicit retry.
Never merge the candidate automatically.

Reuse the current Python coordinator, typed records, SQLite store, and CLI adapter direction.
Use graph discovery and coverage checks before structural source searches.
Use narrow behavior-based tests and fresh repositories, state, and artifacts.
Run focused checks, the complete offline suite, static checks, and fresh installed-wheel checks.
Record commands, results, environment, revision, and limitations.

## Boundaries

Platform adaptation and live conformance remain separate deferred work under ADR 0007.
Keep operational execution admission closed.
Do not resume Linux development, VMware, SSH, qualification batches, or exception proposals.
Do not access credentials, private VM inputs, or retained custody data.
Do not run a real coding runtime, provider request, paid model, or paid host.
Do not add a provider SDK, model tool loop, workflow framework, or extra runtime.
Preserve historical results, retained charges, original custody, and unknown outcomes.
Fixture success supplies no platform qualification or execution authority.
Phase 3 evaluation and releases retain their owner gates.

## Closure

Finish every Phase 2E software acceptance condition before claiming completion.
Use ASD-STE100 for new human-readable text and RTK for shell commands.
Update README, CHANGELOG, handoff, next-session prompt, and synchronized semantic package versions.
Commit and push the coherent current branch under standing publication instructions.
Stop before Phase 3A implementation, live evaluation, merging, deployment, or package publication.
Provide the next milestone prompt and exact input files.
