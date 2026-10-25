# Next session: complete the same Hermes deadline-control milestone

Use this prompt with Codex Sol 6.1 (`gpt-6.1-sol`):

```text
Use $crewshal in /Volumes/X10Pro/Crewshal.
Continue the existing private deadline-control milestone. Do not start S1b implementation.
Read current HANDOFF, the runtime diagnosis, and the blocked deadline-control record first.
Verify supervisor identity, HEAD, original dirty files, preserved hashes, and unchanged runtime bindings.
Reuse accepted R1 readiness while its bindings remain unchanged. Do not repeat successful worker or approval probes.
Preserve R1, the refused implementation launch, corrected I1, and failed D1 preflight. Do not reset counts.

Nine private offline fixtures passed. No live diagnostic session or request ran.
The D1 preflight incorrectly expected database column input_id in session_admissions.
The database stores request_id. Current source maps RPC input_id to Submission.request_id.
This was a supervisor query defect, not evidence of a Hermes regression.
Do not launch the preserved probe.py unchanged.

First inspect exact current source for the supported submission, receipt, and interrupt APIs.
Verify admission mapping with an independent temporary SQLite fixture.
Review failure cleanup after possible submission acceptance, lost acknowledgement, failed lookup, and disconnect.
Preserve unknown outcomes. Never replay an uncertain launch or cancel a different session or generation.
Keep the control outside Crewshal product source. Do not add an adapter or general orchestration framework.
Use the original monotonic total deadline. Continuing chunks and heartbeat activity must not extend it.
Test cancellation failure and missing terminal reconciliation without any model request.

After offline checks pass, reassess one short read-only live diagnostic.
Record a revised prompt, exact argv, session policy, one-worker limit, independent ceiling, and cleanup before launch.
Keep the selected provider, model, context, approval controls, and model server unchanged.
Use no metered fallback, credential extraction, profile change, or server restart.
Treat any live diagnostic as a new diagnostic admission, never an I1 correction or ledger reset.
Require actual terminal admission and matching server cancellation or completion evidence after the deadline.
A client disconnect, interrupt acknowledgement, or fixture pass cannot establish live termination.
Stop after two attempts without new evidence, or after a required tool or runtime binding fails.
Do not start S1b even if the deadline proof passes. That belongs to a following session.

Keep image actions, guests, downloads, Linux tests, campaign execution, evaluation, and releases closed.
Record exact commands, exits, environment, revision, limitations, and next inputs.
Publish only an accepted coherent checkpoint under standing project rules. Stop at that boundary.
```

## Exact input files

- `AGENTS.md` and `/Users/hamedprooshani/.codex/RTK.md`.
- `skills/crewshal/SKILL.md`.
- `skills/crewshal/references/project-memory.md`.
- `skills/crewshal/references/hermes-control.md`.
- `skills/crewshal/references/task-packet.md`.
- `docs/HANDOFF.md`, current state only.
- `docs/DEVELOPMENT-PLAN.md`, current Phase 3B boundary and evidence contracts.
- `docs/ARCHITECTURE.md`, scope, runtime, cancellation, and evidence contracts.
- `docs/decisions/0009-local-development-before-consolidated-linux-testing.md`.
- `docs/CREWSHAL-HERMES-RUNTIME-DIAGNOSIS-2026-10-25.md`.
- `docs/CREWSHAL-S1B-BLOCKED-2026-10-25.md`.
- `docs/CREWSHAL-SKILL-SETUP-2026-10-25.md`.
- `docs/CREWSHAL-HERMES-DEADLINE-NEXT-SESSION-2026-10-25.md`, the original milestone prompt.
- `docs/CREWSHAL-HERMES-DEADLINE-CONTROL-2026-10-25.md`.
- This continuation prompt.

Resolve installed companion skills, RTK, and the profile SOUL through the Crewshal skill.
The preserved private root is `/Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3`.
Read `diagnosis-20261025/runtime-evidence.json` and `diagnosis-20261025/inspect_runtime.py` there.
Verify every entry in `deadline-20261025/evidence-hashes.json` before changing private control files.
Read these exact private files:

- `deadline-20261025/deadline_control.py`.
- `deadline-20261025/test_deadline_control.py`.
- `deadline-20261025/probe.py`, an unaccepted runner with the recorded SQL defect.
- `deadline-20261025/probe-plan.json`, a historical plan that was never launched.
- `deadline-20261025/D1-preflight-failure.json`.
- `deadline-20261025/offline-tests.result.json` and `deadline-20261025/offline-tests.stderr`.
- `deadline-20261025/session-evidence.json` and `deadline-20261025/closure-results.json`.

Inspect exact current Hermes source when needed. Its September graph generation was stale during this session.
Keep profile configuration, credential references, full exports, and private logs outside the repository.
Later S1b and campaign documents remain planning inputs. They grant no runtime or host authority here.
