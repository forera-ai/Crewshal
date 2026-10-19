# Phase 3B B1 manual operator script

Date: 2026-10-19. Status: source-bound draft. This file grants no execution authority.

This script implements the frozen B1 stage order. It supplies no new executor.
The campaign manifest must bind the effective native commands before an operator uses this script.
The operator must stop if any required field is absent or differs from the admitted campaign.

## Inputs for one B1 row

1. Read one `B1` row from `schedule.json` in frozen order.
2. Bind its task ID to `development-tasks.json` and its source ID to `corpus.json`.
3. Bind the row's implementation and review assignments to `runtime-selections.json`.
4. Verify the source archive and extracted inventory against `source-inventories.json`.
5. Record the exact qualified environment, toolchain, dependency snapshot, policy, scope, and budget identities.
6. Record the admitted native launch commands, executable hashes, configuration hashes, and provider routes.
7. Stop if the implementation and review providers cannot meet the frozen independence rule.

## Manual stage order

1. Start the setup clock before creating the row's private work area.
2. Create one fresh source copy, one private implementation HOME, and one isolated writable cache.
3. Record the unchanged initial candidate digest and each baseline check result.
4. Give the implementer only the frozen requirement, allowed paths, check definitions, and admitted grant.
5. Start one native implementation turn with the admitted effective command. Record its attempt identity before launch.
6. Stop the native process before freezing the resulting candidate. Record its exit and structured result separately.
7. Compare changed paths with the frozen allowed scope. Preserve any violation as a failed result.
8. Freeze the candidate bytes and digest. Give validators a separate copy and no provider credential.
9. Run the frozen checks in their recorded order and working directories. Enforce each 900-second limit.
10. Record each check's command, environment, exit, output digests, and candidate digest.
11. Create a fresh reviewer context with the requirement, frozen candidate, diff, and captured checks only.
12. Give the reviewer no implementation conversation, candidate write access, or validator credential.
13. Start one admitted read-only review turn. Record its provider, model, executable, configuration, exit, and findings.
14. Record a terminal result with unresolved findings and missing evidence visible. Do not convert unknowns to passes.
15. Stop and inspect owned processes, mounts, handles, and files before removing any row-owned scratch.

## Required receipt

Record the schedule row ID, task and source digests, assignment, environment, policy, budget, and all start and stop times.
Record every native attempt, check, review, candidate, scope result, usage category, and cleanup result.
Keep measured billing, API-equivalent estimates, and subscription quota observations separate.
Keep private raw receipts outside Git with `0700` directories and `0600` files.
Do not retry a timeout or uncertain response automatically.

## Current stop

The effective native commands, qualified environment, dependencies, provider identities, and limits remain unbound.
No B1 row may start from this source draft.
