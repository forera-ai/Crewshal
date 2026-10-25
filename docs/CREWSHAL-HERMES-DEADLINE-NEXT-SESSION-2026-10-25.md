# Next session: prove an independent Hermes deadline

Use this prompt with Codex Sol 6.1 (`gpt-6.1-sol`):

```text
Use $crewshal in /Volumes/X10Pro/Crewshal.
Complete one runtime deadline-control milestone before further S1b implementation dispatch.
Read the current HANDOFF and the October 25 runtime diagnosis first.
Verify HEAD, dirty files, supervisor identity, runtime bindings, and preserved evidence hashes.

The stored Hermes policy has run_budget_seconds=600 and max_turns=25.
The profile's current default is 45 turns. Resume retains the stored 25-turn policy.
The run budget supplies a turn-local wrap-up notice and selected stale-timeout caps.
The local streaming branch has separate inactivity timing and can continue during active generation.
The prior continuation generated at least 16,770 sampled tokens without a completed tool call or candidate.
Codex interrupted it after 623.226 seconds. No automatic 600-second termination was proved.

Preserve the R1, refused launch, and corrected I1 ledger. Do not reset attempts.
Reuse accepted readiness while its bindings remain unchanged. Do not repeat successful probes without a relevant change.
Do not resume implementation or create the S1b proposal during this milestone.

Prepare a small private supervisory deadline control around the existing supported Hermes session APIs.
Keep it outside Crewshal product source. Do not add a product adapter or general orchestration framework.
Use a monotonic total deadline that continuing chunks and heartbeat activity cannot extend.
Bind cancellation to the exact admitted session and execution generation.
Test it first with deterministic offline fixtures that create no model request.
Prove continued activity cannot extend the deadline, wrong-generation cancellation fails safely,
and a client disconnect cannot masquerade as gateway termination.
Preserve evidence when cancellation or terminal reconciliation fails. Do not retry an uncertain launch blindly.

After those checks pass, assess whether one short read-only live probe is necessary and justified.
Record its prompt, exact argv, session policy, one-worker limit, independent ceiling, and cleanup before launch.
Treat it as a new diagnostic probe, not a reset of I1 or an implementation correction.
Keep the selected model, provider, context, approval controls, and model server unchanged.
Use no metered fallback, credential extraction, or server restart.
Require actual terminal admission and matching server cancellation or completion evidence after the deadline.
Stop after two attempts without new evidence, or after a required tool or runtime binding fails.
Do not start S1b implementation even if the deadline probe passes. That belongs to the following session.

Keep real image actions, guests, downloads, Linux tests, campaign execution, evaluation, and releases closed.
Record commands, results, environment, limitations, and exact next-session inputs.
Publish only an accepted coherent checkpoint under the standing project rules. Stop at that boundary.
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
- This next-session prompt.

Resolve installed companion skills, RTK, and the profile SOUL through the Crewshal skill.
Use the private `diagnosis-20261025/runtime-evidence.json` and `inspect_runtime.py` under the preserved evidence root.
Inspect exact current Hermes source when needed. Its September graph generation was stale during diagnosis.
Keep profile configuration, credential references, full exports, and private logs outside the repository.
The later S1b prompt and campaign documents remain planning inputs. They grant no runtime or host authority here.
