# 0007 — Complete core development before platform qualification

Date: 2026-10-15. Status: accepted through the owner's direct instructions in this session.

## Context

The owner stopped Linux development and requested core completion before platform adaptation.
The owner then instructed: "unblock phase 2D and continue with the plan and focus ONLY on developing based on plan."
This instruction resolves the development order without another approval request.
The earlier Phase 2D gate combined software development, Linux isolation qualification, and live implementation acceptance.
Repeated operational failures prevented completion of the software milestone.
The historical Linux and live results remain incomplete.

## Decision

Phase 2D is active and unblocked for core software development.
Its current deliverable is the first runtime integration and deterministic coordinator workflow in the accepted architecture.
Complete the production code through existing interfaces and verify it with deterministic external runtime and validator fixtures.
Exercise the actual coordinator, candidate handling, durable store, normalization, evidence, and verdict rules.
Do not replace the implementation under test with mocks or manually assembled success records.

Move platform adaptation, containment qualification, and live conformance to a separate deferred work item.
That work follows core software development and precedes dependent live evaluation or platform support claims.
The deferred work does not block Phase 2D software acceptance or subsequent source development under the plan.
Phase 2E software development follows completed Phase 2D software acceptance in a separate session.
Paid evaluation and release retain their existing owner gates.

Preserve the local Python coordinator, typed contracts, SQLite state, CLI adapter direction, and separation of claims from evidence.
Reuse existing interfaces and components.
If a core path requires Linux effects, isolate only those effects behind the existing adapter boundary.
Keep the Linux backend's operational admission checks intact.
Do not add an unrestricted execution fallback, new isolation framework, model SDK, or model tool loop.

## Phase 2D software acceptance

1. A fresh confirmed project and approved task enter the existing first-runtime contract through the coordinator.
2. A deterministic external runtime fixture produces a changed candidate through the actual production integration path.
3. The coordinator preserves the original checkout and records the initial and resulting candidate identities.
4. A separate validator fixture supplies captured results tied to the exact frozen candidate and approved check definitions.
5. The actual evidence and verdict rules require valid checks, current decisions, and permitted scope before software workflow success.
6. Forged claims, stale bindings, candidate mutation, failed checks, malformed output, and missing evidence cannot produce success.
7. Cancellation, timeout, refusal, and interrupted recovery retain explicit outcomes and cannot silently retry work.
8. Fresh durable state and fixtures reproduce the workflow without historical VM objects or private access material.
9. Relevant regressions, the complete offline suite, static checks, and fresh installed-package checks pass.

Tests must use deterministic fixtures only at external boundaries.
They must exercise observable production behavior rather than repeat implementation assertions.
Record the environment, revision, commands, results, and remaining limitations.
Passing software acceptance permits the status "Phase 2D software complete; platform and live qualification deferred."
It does not establish a qualified execution platform or authorize production agent writes.

## Operational state and history

No further Linux adapter development, VMware or SSH operations, compiler attempts, or exception proposals belong to the active milestone.
The unused v29 approval does not resume Linux work.
Keep operational execution admission closed while qualification is deferred.
Preserve all existing source, dated evidence, private artifacts, charges, custody, and unknowns.
This decision authorizes no host shutdown, object deletion, credential access, model call, or platform support claim.
Earlier ADRs and qualification requirements remain applicable to later operational work where this decision does not change their order.

## Completion and publication

Finish one software milestone per session and stop at its accepted boundary.
After revised Phase 2D software acceptance, apply the standing version, README, changelog, handoff, commit, and branch-push rules.
Deferred Linux qualification does not block that software checkpoint.
Describe the published checkpoint as software with deferred operational qualification.
Do not merge, deploy, publish a package, or begin Phase 2E in the same session.
