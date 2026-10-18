# Next-session prompt — Phase 3B admission capacity

Work in `/Volumes/X10Pro/Crewshal`.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, the current handoff, the development plan, the architecture, and accepted ADRs 0001 through 0008.
Read the frozen Phase 3A package README and verify it with its read-only checker.
Read the [capacity record](PHASE-3B-ADMISSION-CAPACITY-BLOCKED-2026-10-18.md), [approved proposal](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md), and [exact inputs](PHASE-3B-ADMISSION-CAPACITY-INPUTS-2026-10-18.json).
Inspect Git state and preserve later work.

The owner already approved two separate decisions: resume platform and live qualification, and accept the exact Phase 3B limits with unknown subscription quota debit.
Do not request these decisions again unless a proposed limit or scope changes.
The selected powered-off VMware Ubuntu VM had 8 GiB configured RAM, below the 16 GiB minimum.
Do not resume its saved state or change it without an explicit instruction that preserves prior work.
First establish a new, owner-controlled, nonshared Linux arm64 guest with at least four CPUs, 16 GiB RAM, and 40 GiB free disk.
Stop if the guest or its controls cannot meet the approved proposal.

After capacity admission, follow the proposal's sequence for toolchains, native qualification, provider identities, dependency snapshots, B1 script, baseline conformance, and calibration.
Version changed selections or protocols before dependent runs.
Use only four selected development repositories and twelve tasks.
Retain all 192 development rows, four conditions, both role assignments, failures, and unknowns.
Keep all 576 sealed rows unexposed. Do not inspect sealed contents or private held-out annotations.
Keep measured billing, API-equivalent estimates, subscription quota, and unknown usage separate.

At the next completed or blocked boundary, record exact commands, results, environment, revision, costs, failures, and limits.
Update README, CHANGELOG, handoff, next prompt, and synchronized semantic versions.
Commit and push the current branch under the standing owner instruction.
Do not claim completed calibration or begin Phase 3C without its acceptance gates.
