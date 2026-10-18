# Next-session prompt — Phase 3B toolchain preparation amendment

Work in `/Volumes/X10Pro/Crewshal`.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, and `docs/ARCHITECTURE.md`.
Read accepted `docs/decisions/0001` through `0008`.
Read `docs/PHASE-3B-TOOLCHAIN-PREPARATION-BLOCKED-2026-10-18.md`, `docs/PHASE-3B-GUEST-CAPACITY-READBACK-BLOCKED-2026-10-18.md`, and `docs/PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md`.
Read `docs/PHASE-3B-TOOLCHAIN-PREPARATION-INPUTS-2026-10-18.json` and every file it names.
Read the frozen `docs/evaluation/phase-3a-frozen/README.md`.
Read `docs/evaluation/phase-3a-frozen/runtime-selections.json` and run `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py`.
Inspect Git state and preserve later work.

The owner already approved qualification resumption and the exact Phase 3B limits with unknown subscription quota debit.
Do not ask for those decisions again unless scope or limits change.
The preparation amendment is incomplete and has no execution approval.
The new guest remains disconnected. The old 8 GiB guest remains under owner control.
Do not install, download, change VM settings, or run a coding runtime under the current amendment draft.

First obtain a reliable upper bound for the installer's prior transfer without new downloads.
Use read-only installer records and keep rounded `Fetched` summaries distinct from exact network transfer.
Complete the official Linux arm64 artifact manifest with exact URLs, versions, digests, archive bytes, extraction bounds, dependencies, install commands, and cleanup.
Keep the selected CPython, Node.js, Bun, Swift, .NET, Codex CLI, and Claude Code CLI versions fixed.
Pin RTK, CMake, Ninja, and all prerequisite packages prospectively.
Do not replace an unknown artifact size or executable digest with a guess.

Prepare a reviewable owner decision for a 16 GiB guest-visible RAM threshold and the proposed infrastructure ledger.
The draft proposes 17,179,869,184 guest-visible bytes and a separate 40 GiB VM-plus-ISO allocation ceiling.
The 8 GiB download limit still includes the ISO and installer traffic.
The 8 GiB retained-data limit would cover batch assets separately only if the owner approves this change.
Do not change either interpretation or perform dependent work before that approval.

After the new gates pass, follow the approved proposal's order: native qualification, provider identities, dependencies, B1, baselines, then calibration.
Version changed selections before dependent runs.
Keep four selected development repositories, twelve tasks, all 192 planned development rows, and every failure or unknown.
Keep all 576 sealed rows unexposed. Do not inspect private held-out annotations.
Keep measured billing, API-equivalent estimates, subscription quota, and unknown usage separate.

At the next completed or blocked boundary, record commands, results, environment, revision, costs, failures, and limits.
Update README, CHANGELOG, handoff, next prompt, and synchronized semantic versions.
Commit and push the current branch under standing owner authorization.
Do not claim Phase 3B calibration or begin Phase 3C without their gates.
