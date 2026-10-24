# Crewshal next session: G1 decision readiness

Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal` with the Crewshal profile.
Use `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` at a 98,304-token server context.
Record the Hermes model, profile context, served model, and actual server context before work.
Stop if an observed model or context differs from this prompt.

Read `AGENTS.md` and `/Users/hamedprooshani/.codex/RTK.md` first, in separate reads.
Then read the current state in `docs/HANDOFF.md` and current Phase 3B plan sections, in that order.
Use `rtk proxy` for every terminal command. Do not substitute injected rules for these file reads.
Verify the published revision, branch, version, and Git status before any other document read.

Name one milestone: decide whether the accepted G1 campaign proposal is ready for an owner decision.
Read `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md`,
`docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md`,
`docs/OWNER-DECISION-PACKET-PHASE-3B-REMAINING-GATES-2026-10-23.md`, and ADR 0009.
Check the G1 S0–S4 gates, exact owner choices, finite limits, and unknown guest facts.
Use exact sections and source lines. Do not repeat whole documents in chat.

Produce one concise, read-only decision-readiness packet for Codex.
Separate decisions needed before host action from later development-run and protocol decisions.
Name any factual contradiction and its exact location.
If no contradiction exists, state that the proposal awaits the owner's exact decision.
Do not make a new proposal or source change without a specific verified defect.
Keep every execution and spending gate closed.

Do not boot, inspect, or change a guest. Do not use a droplet or run Linux tests.
Do not run evaluation rows, access credentials or sealed tasks, or spend money.
Do not edit Hermes settings, memory, or skills. Do not call `skill_manage`.
Do not commit or push. Stop for Codex review with exact checks, limits, and one next-session prompt.
