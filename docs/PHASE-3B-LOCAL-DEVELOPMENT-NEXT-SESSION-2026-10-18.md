# Next-session prompt — local development before Linux tests

Work in `/Volumes/X10Pro/Crewshal` on the current branch.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, and `docs/ARCHITECTURE.md`.
Read accepted `docs/decisions/0001` through `0009` and `docs/evaluation/phase-3a-frozen/README.md`.
Read the [current order record](PHASE-3B-LOCAL-DEVELOPMENT-ORDER-2026-10-18.md) and verify every file in the [exact input index](PHASE-3B-LOCAL-DEVELOPMENT-INPUTS-2026-10-18.json).
Inspect Git state and preserve later work.

The owner stopped Linux tests during development.
Use the local macOS checkout as the main development environment.
Do not run Linux tests, enter either VMware guest, use a droplet, or retrieve Linux toolchain artifacts.
Do not change guest settings, network state, storage, or historical custody.
Do not resume the earlier Phase 3B Linux toolchain prompt during development.
The earlier qualification and batch approvals remain dated records. They do not reopen Linux work now.

Identify the next coherent source development milestone from the accepted plan and current code.
Complete only that milestone with local deterministic fixtures and relevant offline checks.
Exclude Linux-specific test modules and record them as deferred.
Use the actual production path for acceptance tests. Preserve frozen Phase 3A package bytes.
Keep platform behavior, provider identities, dependencies, and native baseline results unknown until observed later.
If no source work remains, record a source-ready boundary without claiming Linux qualification or calibration.

After all planned source development passes local acceptance, prepare one consolidated Linux qualification and test campaign.
Do not run that campaign in this development session.
Keep all 192 development rows planned and all 576 sealed rows unexposed until their separate gates pass.
Do not claim Phase 3B calibration or begin Phase 3C.

At completion or a blocked boundary, record commands, results, environment, revision, costs, failures, and limits.
Update README, CHANGELOG, handoff, next prompt, and synchronized semantic versions.
Commit and push the current branch under standing owner authorization.
