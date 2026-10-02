# Crewshal project instructions

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

## Temporary host retention — owner declaration, 2026-10-02

The owner deleted the earlier droplet after premature deletion guidance and supplied another host. Keep the current disposable host until all required host work is actually finished and no further droplet is needed for that work. Do not recommend or request droplet deletion at an intermediate preparation, blocked, publishing or session boundary. Scoped removal of owned experimental resources is separate from deleting the host. Future sessions must reverify current access and host state without inferring deletion or survival. Do not commit connection addresses, passwords or authentication material.

## Engineering boundaries

Clean independent implementation; no copying private Forge code, prompts, schemas, paths or artifacts. Preserve unknown capabilities, provenance and authority separation. Discovery executes no repository instructions. Agent writes stay disabled until execution qualification passes. Original dirty files must remain intact. No paid model calls, benchmark spend, credential-store access, deployment or automatic publication is implied by a test plan.

Use RTK for shell commands when available (`rtk proxy` preserves raw output); this workspace's owner requires RTK. Keep tests focused on observable behavior and security invariants. Build only the active milestone; no speculative orchestration framework, new model tool loop or extra adapters.

## Codebase graph discovery

At session start or compaction, confirm the nearest graph project/generation with list_projects or index_status. Prefer search_graph, trace_path, get_code_snippet, then query_graph/get_architecture for structural discovery. Default to task-directed Verify evidence. After candidate paths are known, check_index_coverage for every evidence path and relevant negative/exhaustive scope. Stale, skipped, partial, excluded or unknown coverage requires targeted source fallback. Non-code text/config searches may use rg directly. Do not claim complete coverage from a clean graph report. Reindex after material updates when needed. Pass explicit graph/coverage evidence to any authorized delegated agent.
