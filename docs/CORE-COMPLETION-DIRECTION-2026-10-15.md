# Core completion before platform qualification — 2026-10-15

## Latest clarification — Phase 2D software development is active

The owner subsequently instructed: "unblock phase 2D and continue with the plan and focus ONLY on developing based on plan."
Phase 2D is active and unblocked for the core software milestone under [accepted ADR 0007](decisions/0007-core-development-before-platform-qualification.md).
Only platform adaptation and live qualification are deferred.
[The current prompt](PHASE-2D-CORE-NEXT-SESSION-2026-10-15.md) replaces the earlier general continuation.
Earlier references below to deferring all of Phase 2D describe the preceding work-order record.


## Owner direction

The owner asked to stop the repeated Linux exception batches and finish the code before platform adaptation.
This direction supersedes the previous instruction to continue Linux Phase 2D attempts in this session.
The owner approved exact v29 immediately before this direction, but no v29 operation started.
Do not use that unused approval to resume Linux work automatically.

## Current evidence

Phase 2D remains incomplete.
The sequence through v28 concerns the Linux execution and isolation integration.
Observed failures include FD custody, mount namespace paths, AppArmor revision reads, and compiled policy format.
These findings do not establish a VMware version defect.
Both latest offline suites pass 1222 occurrences with zero failures, errors, or skips.
These tests do not establish actual runtime qualification or successful live implementation.
Twenty-three full charges and their retained evidence remain recorded.
The last exact restoration returned forwarding to zero.
The shared retention parent remains at its approved 2 GiB limit.
Keep existing private access material and custody records local.
This direction authorizes no host shutdown, retained-object deletion, or reconstruction of lost proof.

## Revised work order

Stop Linux adapter development, operational batches, compiler attempts, qualification runs, and further exception proposals.
Defer Linux, macOS, and Windows platform qualification until the core workflow is complete.
Preserve the Linux implementation and dated evidence for later work.
Keep operational execution admission closed while platform qualification is deferred.
Do not mark Phase 2D complete or claim supported execution platforms.

Finish the platform-independent coordinator workflow first.
Use the accepted architecture, current source, and existing contracts to identify the remaining core gaps.
Exercise project confirmation, task dispatch, candidate capture, deterministic validation, evidence recording, and failure recovery as one complete workflow.
Use deterministic runtime and validator fixtures for this core acceptance check.
Keep source completion evidence separate from live runtime and containment evidence.
Reuse existing interfaces and avoid a replacement isolation framework or new platform adapter.
The next session must state a bounded core milestone and its observable acceptance criteria before implementation.
Its handoff must identify remaining platform work explicitly.

No code was changed for this direction record.
No v29 operation, authentication, model call, commit, push, release, or deployment occurred.
