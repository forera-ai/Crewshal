# Crewshal project instructions

## Development supervision — owner instruction, 2026-10-25

Load the global `crewshal` skill before project work. The versioned source is [skills/crewshal/SKILL.md](skills/crewshal/SKILL.md).
Use Sol 6.1 for development orchestration. Hermes prepares bounded implementation candidates with the selected local model.
Codex reviews evidence, governs integration, prepares continuation prompts, and publishes accepted checkpoints.
Every worker must load `codebase-memory`, `caveman`, and `jev`, and verify its own required MCP access.
Apply ASD-STE100 over conflicting compression rules. Start each answer with the active Crewshal skill version line.
Verify actual readiness before source delegation. Worker completion claims cannot replace tool evidence or Codex review.
Keep all existing architecture, security, Linux, evaluation, spending, and release gates.
See the [setup record](docs/CREWSHAL-SKILL-SETUP-2026-10-25.md) and [next prompt](docs/CREWSHAL-SUPERVISED-NEXT-SESSION-2026-10-25.md).

## Human communication — owner rule, 2026-10-11

Use [ASD-STE100](https://www.asd-ste100.org/) for all human-readable explanations and decision requests in this project.
Apply this rule to chat replies, progress reports, documentation, handoffs, and approval requests.
Use complete sentences and the active voice. Give each word one meaning.
Keep procedural sentences at 20 words or fewer. Keep descriptive sentences at 25 words or fewer.
Use approved general words and consistent project technical names.
Keep code, commands, paths, identifiers, and exact diagnostic text unchanged.
This rule takes priority over conflicting compression and style skills.
Preserve dated records. Apply this rule to new text and text changed for current work.

## Repository identity — owner update, 2026-10-08

Crewshal is owned and maintained by [forera-ai](https://github.com/forera-ai). The canonical repository is [forera-ai/Crewshal](https://github.com/forera-ai/Crewshal); this checkout uses `origin` at `https://github.com/forera-ai/Crewshal.git` for fetch and push. Use this identity for future repository links and publishing. Earlier `prooshani/Crewshal` references in dated records describe historical ownership and are not current remote instructions. The transfer does not change execution/spend authority. Following the owner’s October 8 copyright correction, the current project notice is `Copyright 2026 forera.ai and contributors.` This supersedes the earlier preservation instruction for the current notice; dated records remain historical.

Read [docs/HANDOFF.md](docs/HANDOFF.md) first, then [docs/DEVELOPMENT-PLAN.md](docs/DEVELOPMENT-PLAN.md) and the accepted architecture/ADRs. These files are persistent project memory. The handoff is authoritative for the active milestone and last verified state; the plan is authoritative for scope and acceptance gates. Do not substitute chat recollection for recorded evidence.

## Session contract — owner declaration, 2026-10-02

- One complete phase or major milestone per session. Name the milestone before work; finish its independently reproducible acceptance checks, then stop at that boundary.
- Deliver a next-session prompt and update the handoff at each completion or blocked boundary. Preserve achievement history; record failures and unknowns explicitly.
- The owner authorized the accepted architecture direction and bounded implementation. Do not repeatedly ask for routine implementation permission. Material architecture changes, paid evaluation budgets, unresolved consequential decisions and releases retain their recorded owner gates.
- Never mark a milestone complete because code exists or a model claims success. Record commands, results, environment, revision and limitations. Earlier milestones may be implementation dependencies; tests must create their own fixtures and must not depend on previous run artifacts or paid services unless explicitly classified as live qualification/evaluation.
- Keep a coherent Git checkpoint for each completed milestone and push the current branch to its remote after every commit, without requesting confirmation. The owner explicitly authorized this publishing workflow on 2026-10-02. Merge, deployment and package releases retain their separate gates. Do not revert unrelated work, force-push or commit credentials/raw confidential artifacts.
- If blocked, make safe independent progress, record the smallest missing decision/capability, and provide a precise continuation prompt. Do not bypass a gate or silently broaden the session.

## Publish and session closure — owner declaration, 2026-10-02

- Before every commit/push, update README.md, CHANGELOG.md and the handoff, and bump the semantic package version according to the change: major for incompatible public changes, minor for compatible functionality, patch for compatible fixes or documentation/process maintenance. Keep pyproject.toml and crewshal.__version__ synchronized. Every new commit includes the version bump, changelog and README update.
- Push the committed current branch to the configured remote. This is standing owner authorization; do not ask again. Preserve branch history and report push failures explicitly. Do not infer merge, deployment or package-registry publication authority.
- At session closure, provide a brief explanation of the next milestone, its initial prompt and the exact files to feed into the next session.
- Once the active milestone's goals and acceptance gates pass, conclude development immediately. The publishing ceremony (README, changelog, handoff, next prompt, version bump, commit and push) ends the session; do not begin the next milestone.

## Local development and deferred Linux tests — owner instruction, 2026-10-18

The owner stopped Linux testing during development. Use the local macOS checkout as the main development environment.
Complete source work with local deterministic fixtures, offline checks, static checks, and installed-package checks where relevant.
Do not run Linux tests or qualification during a development session.
Exclude Linux-specific test modules from local development checks. Record them as deferred, not passing.
Do not boot, inspect, reconfigure, reconnect, or install into either VMware Ubuntu guest during development.
Do not use a droplet or retrieve Linux toolchain artifacts for development preparation.
Preserve existing guests, the ISO, records, charges, and unknown outcomes.
After all planned source work passes local acceptance, prepare one consolidated Linux qualification and test campaign.
Obtain any required approval for changed scope before that campaign acts.
Earlier qualification approvals remain historical records. They do not reopen Linux work during local development.
Keep Linux conformance, Phase 3B calibration, and Phase 3C claims closed until their actual gates pass.
See [ADR 0009](docs/decisions/0009-local-development-before-consolidated-linux-testing.md).

## Linux test cost and host lifecycle — owner declaration, 2026-10-05

This declaration supersedes the 2026-10-02 temporary-host retention rule. The owner intends to remove the current droplet; do not require its retention or assume its continued availability. Do not delete a host on the owner's behalf without an explicit action request. Host-only private authentication state and preparation artifacts may be lost; preserve public evidence and reproducible pinned inputs, never credentials in Git.

Do not run or request VPS tests at every session boundary. Complete a substantial, coherent round of changes first. Use local checks and, when necessary and available, the owner's local VMware Ubuntu installation. Do not assume local VMware supplies KVM/nested virtualization or represents another platform without observing it. Missing target-specific evidence remains unresolved.

Only when a necessary Linux/multiplatform acceptance check cannot be satisfied locally, prepare a concrete test batch explaining why a droplet is necessary, exact commands, resource ceilings, expected duration/cost exposure and cleanup. Ask the owner before any droplet test; the owner will prepare a host if approved. Prior host access or resource-envelope approval does not authorize a new paid-host test batch. Do not provision, resize or purchase infrastructure. Reverify host access, identities and admission only when an approved batch is about to use that host, not automatically every session. Do not commit addresses, passwords or authentication material.

## Engineering boundaries

Clean independent implementation; no copying private Forge code, prompts, schemas, paths or artifacts. Preserve unknown capabilities, provenance and authority separation. Discovery executes no repository instructions. Agent writes stay disabled until execution qualification passes. Original dirty files must remain intact. No paid model calls, benchmark spend, credential-store access, deployment or automatic publication is implied by a test plan.

Use RTK for shell commands when available (`rtk proxy` preserves raw output); this workspace's owner requires RTK. Keep tests focused on observable behavior and security invariants. Build only the active milestone; no speculative orchestration framework, new model tool loop or extra adapters.

## Codebase graph discovery

At session start or compaction, confirm the nearest graph project/generation with list_projects or index_status. Prefer search_graph, trace_path, get_code_snippet, then query_graph/get_architecture for structural discovery. Default to task-directed Verify evidence. After candidate paths are known, check_index_coverage for every evidence path and relevant negative/exhaustive scope. Stale, skipped, partial, excluded or unknown coverage requires targeted source fallback. Non-code text/config searches may use rg directly. Do not claim complete coverage from a clean graph report. Reindex after material updates when needed. Pass explicit graph/coverage evidence to any authorized delegated agent.
