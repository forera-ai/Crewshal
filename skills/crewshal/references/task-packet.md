# Dispatch, review, and recovery records

Keep each packet short. Link exact source ranges and evidence files instead of copying large documents.
Aim for at most 500 words in routine readiness and review responses. Preserve full evidence in the captured artifacts.

## Dispatch packet

Include these fields before Hermes starts:

1. Name the task ID, milestone, base revision, branch, and original dirty files.
2. State one observable acceptance condition, required refusals, and the stopping boundary.
3. List owned files, permitted scratch locations, prohibited effects, and closed owner gates.
4. List exact input documents and required sections. Separate current records from historical evidence.
5. Record skill versions and paths, RTK status, graph generation, and Jev preflight evidence.
6. Supply graph queries, pagination, symbols, traces, coverage limitations, and exact source fallbacks.
7. Record Hermes profile, SOUL digest, provider, model, quantization, endpoint, and verified context limits.
8. Set the attempt count, turn limit, wall-clock limit, and useful tool-output bounds.
9. List permitted local checks and Linux exclusions. Require exact exit statuses and saved-artifact review.
10. Require a complete candidate packet and a stop before commit, push, profile edits, or further delegation.

Use a fresh Hermes session. Do not resume a conversation whose scope, approval, configuration, or candidate has changed.
For an approved continuation, preserve the attempt ledger and recheck all changed bindings.

## Candidate packet

Record the requirement, actual changed files, full diff identity, and hashes of new files.
Include commands, working directories, exit results, environment, and evidence paths.
Map each acceptance condition and refusal to current evidence.
Keep failed, missing, deferred, and unavailable checks visible.
Record runtime identity, attempts, elapsed time, token usage, and costs only when observed.
Distinguish actual billing, estimates, quota use, and unknown usage.
State that Codex review is pending. A worker cannot issue its own Codex verdict.

## Codex review record

Review the requirement and frozen candidate before using worker explanations.
Inspect every material changed path, its integration effects, and relevant security invariants.
Give actionable findings with file locations, triggering conditions, consequences, and required evidence.
Rerun the checks needed to establish acceptance. Do not repeat broad tests without a new reason.
Use `accepted`, `changes required`, or `blocked`, with explicit evidence and limitations.
Bind acceptance to the exact final candidate. Recheck affected evidence after any correction or integration change.
Only Codex can complete the project's publication ceremony for this workflow.

## Loop recovery

Track attempt ID, failure signature, new evidence, remaining uncertainty, and next decision.
After two attempts without new evidence, stop the route and change the task design.
Examples include providing exact input records, reducing file ownership, or isolating one failing acceptance case.
Do not merely repeat the same prompt with more emphasis.
Keep one implementation attempt and two correction attempts as the default total limit.
If a new bounded route cannot satisfy the same acceptance conditions, record the smallest blocker.
Do not hide failures, enlarge authority, or start the next milestone to escape a blocked result.
