# Next session — supervised S1b planning

Use Codex Sol 6.1 (`gpt-6.1-sol`) as the supervisor.
Start with this message:

```text
Use $crewshal in /Volumes/X10Pro/Crewshal.
Supervise Hermes through the verified CLI route and complete one offline S1b action-proposal milestone.
Read the current project records and the Crewshal skill setup record before dispatch.
Verify the current HEAD, dirty files, skill version, profile, model, context, MCP tools, and runtime budget.

First give Hermes a read-only readiness task. Do not grant implementation authority in that request.
Require a complete AGENTS.md read through its final line, plus the complete RTK instructions.
Require the current HANDOFF state, current plan boundary, ADR 0009, and the relevant S1b records.
Check actual read ranges and errors. A truncated AGENTS read cannot pass.
Require actual graph and Jev access, and a distinct final Git observation.
Inspect the saved events yourself before accepting readiness.
Do not repeat successful probes unless their bindings changed.

The profile currently selects Ornith UD-Q4_K_XL with a 93,696-token context.
Recheck the live server. Do not infer its capacity from the profile or a historical log.
The gateway uses agent.run_budget_seconds; its stream-json route rejects the --run-budget flag.
Never use top-level -z, --yolo, or approval bypass to repair a failed launch.
Keep one worker and finite attempts. Stop if a required tool or runtime binding fails.

After readiness passes, dispatch the task in:
docs/PHASE-3B-G1-S1B-ACTION-NEXT-SESSION-2026-10-24.md
It permits an exact proposal and offline stub tests only.
Do not attach or eject a real image, operate a guest, download, or run Linux tests.
All campaign and evaluation gates remain closed.

Review the exact saved candidate, source citations, failure cases, and command exit statuses independently.
Use bounded corrections. Stop an ineffective route after two attempts without new evidence.
Do not accept a worker-written Codex approval or a completion claim without supporting evidence.
Hermes must stop before commit or push. Codex publishes only an accepted coherent checkpoint.
Update the required records and version, push the current branch, and stop at this milestone boundary.
```

## Exact input files

- `skills/crewshal/SKILL.md`
- `skills/crewshal/references/project-memory.md`
- `skills/crewshal/references/hermes-control.md`
- `skills/crewshal/references/task-packet.md`
- `AGENTS.md`
- `docs/HANDOFF.md`, current state only unless older evidence becomes relevant.
- `docs/DEVELOPMENT-PLAN.md`, current boundary and relevant acceptance sections.
- `docs/ARCHITECTURE.md`, relevant scope and evidence contracts.
- `docs/decisions/0009-local-development-before-consolidated-linux-testing.md`
- `docs/CREWSHAL-SKILL-SETUP-2026-10-25.md`
- `docs/PHASE-3B-G1-S1B-ACTION-NEXT-SESSION-2026-10-24.md`
- `docs/PHASE-3B-G1-OWNER-RESPONSES-DRAFT-2026-10-24.md`
- `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md`, S1b and sections 7 and 12.

Resolve the local RTK, companion skills, and Hermes SOUL paths from the installed skill.
Do not copy profile configuration, credentials, or raw private logs into the repository.
