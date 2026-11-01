# Offline association correction accepted

Date: 2026-11-01. Package checkpoint: `0.27.24`. Crewshal skill: `1.0.0`.
Base: `407744a3090dfe2284c1cfa138b89bd0e1b11025` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Accepted result and scope

The owner approved the [single-correction proposal](CREWSHAL-ASSOCIATION-BRIDGE-CORRECTION-PROPOSAL-2026-11-01.md) with `approved` in the current chat.
Current local `turn_context` metadata identified `gpt-6.1-sol`.
Codex prepared one fresh private copy of the rejected candidate.
Independent review accepted the correction within its offline source scope.
The candidate remains private, unapplied, and unqualified for live operation.
The new correction is consumed. Zero automatic follow-up corrections remain.
All older budgets remain consumed. The separate translator budget remains unused.

Only the three approved candidate paths changed:

1. Studio `routes/inference.py` keeps each request's correlation callback in an immutable cancellation view.
   The view delegates cancellation state to the original event.
   The tracker retains the original event identity for registries and durable registration borrowing.
   Protected passthrough stream failures now retain incomplete evidence and refuse recovery or replay.
2. Studio `core/inference/api_monitor.py` retains the latest observation boundary for each monitor.
   It rejects stale or overlapping intervals and preserves unresolved evidence after a conflict.
3. Private `tests/test_association_bridge.py` selects backend methods without emptying the response wrapper class.
   It supplies the missing timer fixture and exercises actual standard and passthrough stream consumption.
   Nine new tests cover request isolation, shared cancellation, durable borrowing, observation order, closure, and uncertain-submission refusal.

The existing idle-observation test now uses sequential intervals. Its refusal assertions remain unchanged.
All nine original test modules retain their bytes.
All Hermes, native, generated, submission, supervisor, and guard bytes match the rejected base.
The earlier accepted observation-control candidate and the rejected association candidate remain preserved separately.

## Evidence before and after correction

Read-only baseline diagnostics reproduced both confirmed runtime defects before candidate edits.
A later request retained the earlier callback from its shared cancellation event.
The ledger also accepted a release at `[5, 6]` after active observations at `[3, 4]` and `[7, 8]`.

The first read-only fixture preflight exited `1`.
It exposed a missing timer collaborator and a duplicate request argument in the verification scaffold.
Codex preserved those inputs and refined the scaffold before changing candidate source.
The second preflight exited `0` and exercised the actual standard and complete passthrough functions.
It also confirmed that passthrough read failures and timeouts could invoke recovery after headers arrived.
The approved `routes/inference.py` responsibility covers that protected-route refusal.

The complete correction passed 130 guarded tests before candidate freeze.
An initial private Ruff command then reported `E731` in a new fixture callback.
Codex replaced that lambda with an equivalent named function inside the same approved test file.
The correction remained in progress. No failed behavioral case prompted a follow-up correction.
The saved lint input and failed output remain preserved.
Private Ruff then passed, and the complete final candidate passed all 130 tests again.

## Fresh verification

Exact commands, working directories, separate output streams, and exit codes remain in the private evidence directory.

| Check | Exit | Result and limit |
| --- | --- | --- |
| Final guarded suite | `0` | All 130 tests passed: 97 unchanged original cases and 33 association cases. |
| Original association cases | Same passed command | All 24 retained cases passed, including both previously blocked standard-route assertions. |
| Added regression cases | Same passed command | All nine new cases passed. |
| Native focused build and execution | `0`, `0` | Four serializer cases passed with actual native types and unchanged native candidate bytes. |
| Private Ruff | `0` | The correction script and final new fixture module passed. |
| Runtime Ruff comparison | `1`, `1` | Baseline and candidate each retained 55 diagnostics, with zero introduced diagnostics. |
| Deterministic contract generation | Same passed suite | The unchanged generator rendered identical outputs and matched both unchanged candidate artifacts. |
| Three cumulative patch checks | `0` each | Hermes, Studio, and native patches apply to their unchanged installed sources. |
| Syntax, exact scope, hashes, and preservation | `0` | Exactly three owned paths changed. All protected starting and unowned bytes matched. |
| Negative guard | `1`, expected | All 33 selected cases passed. The guard blocked the intended subprocess attempt and refused overall success. |
| Accepted-candidate preservation | `0` | The earlier 97-test candidate, installed source bindings, profile, and SOUL matched. |

The positive final suite recorded no denied external-effect attempt and retained no pending owned fixture thread.
The negative guard executed no blocked subprocess.
Its selected test module excludes the separate metadata assertion that rejects intentional denial records.
The guard implementation remains unchanged.

The standard fixture executes the actual generation and transport-wrapper functions with deterministic external collaborators.
The passthrough fixture executes the actual admitted coroutine, upstream class, body iterator, and admission-release helper.
HTTPX supplies synthetic native response bytes without a network connection.
Read errors, timeouts, generic stream errors, and uncertain submissions preserve one physical submission and zero recovery actions.
These checks do not qualify a live application, authentication deployment, native binary, or real provider request.

Apple Clang `21.0.0` built the private native fixture from the complete native translation unit and installed libraries.
The executable used actual `server_slot` and `server_task` types.
The sandbox denied network access and live-profile reads during fixture execution.
No installed server binary was rebuilt or changed.

## Candidate identity and preservation

Private evidence resides in `association-correction-20261101-01a1940c` under the preserved S1b root.
Starting manifests preserve 1,110 private files and 1,377 tracked repository files.
Twelve installed source hashes remain unchanged.
The actual unmodified `ActiveGeneration` source supplied the durable borrowing fixture.
Its current source digest appears in the private support-input manifest.

The candidate manifest SHA-256 is `21c0b433ddf9ca7c32db426d92c09d1ea00b11883ecf37610b4eba9ceb6b8df4`.
The correction diff SHA-256 is `3a5e7f6ef2e27359a9670264cdd6e0cb314d6376bbf6f7c9f068d20cdf885015`.
The unchanged cumulative Hermes patch SHA-256 is `7f610f21cc3703240b050dbc7f66572c82784a430cb8876db47ba97663dad0ed`.
The corrected Studio patch SHA-256 is `d45eb4f335e7b2940f14806e8bcf6c8c8b82d9efd8da71aa44f37fd1a11c4ee1`.
The unchanged native patch SHA-256 is `1e0be321aa84f39c722bb9941d51f031b019983040d78fe3c209b9de6d03d3ca`.
These digests identify offline source artifacts. They grant no application authority.

The profile and SOUL hashes match the preserved bindings.
The read-only closure scan observed no process named `llama-server`.
The scan establishes no cause or transition time for that changed observation.
Current served identity, effective context, slot capacity, and request behavior remain unverified.
No inference, authenticated HTTP observation, worker dispatch, profile edit, application, or service action ran.

## Remaining boundary

Graph work used Verify evidence and current-source fallback for unindexed private and Studio source.
The nearest Crewshal project remained ready, with recorded generation `2026-10-31T21:18:33Z`.
Earlier Hermes generation `2026-09-02T17:14:19Z` remains stale.
No graph result establishes exhaustive code coverage.
The supervisor reused its unchanged functional Jev evidence: probability `0.98`, confidence `0.96`, reported cost `0`, latency `479` milliseconds.
No new Jev request ran. Actual total billing remains unknown.

Private runtime checks used Darwin `27.2.0`, arm64, and CPython `3.11.14`.
Publication checks record their own environment and exact commands in the private closure record.
Product suites, mypy, wheel builds, and package installation remain not run for this private-runtime source checkpoint.
Linux tests remain deferred under ADR 0009.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.

The next milestone must establish binary provenance and prepare the exact operational plan.
Source acceptance alone does not open runtime application or Hermes dispatch.
Use the [next prompt and exact inputs](CREWSHAL-ASSOCIATION-OPERATIONAL-PREP-NEXT-SESSION-2026-11-01.md).
