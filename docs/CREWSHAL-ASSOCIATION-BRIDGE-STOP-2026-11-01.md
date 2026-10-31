# Offline association bridge: source acceptance failed

Date: 2026-11-01. Package checkpoint: `0.27.23`. Crewshal skill: `1.0.0`.
Base: `6bee0d784b287b2e629c61170d50691c405073b3` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result and authority

The owner approved the [twelve-path offline proposal](CREWSHAL-SERVER-ASSOCIATION-SOURCE-PROPOSAL-2026-10-31.md) with `yes approved` in the current chat.
Current local `turn_context` metadata identified `gpt-6.1-sol`.
Codex prepared a fresh private candidate without applying it.
The implementation attempt and both targeted corrections are consumed.
Codex rejects the candidate for application and live qualification.
This publication accepts the failure record only.
The separate Hermes translator remains unimplemented. Its budget remains unused.

The first script stopped after partial edits because its source match found two upstream constructors.
Correction 1 qualified that edit and completed the private candidate.
Its guarded run passed 117 of 118 tests. One new clock case failed because the candidate accepted a Boolean timestamp.
Correction 2 added strict clock types and incomplete-transport handling.
The final guarded run passed 119 of 121 tests. Two new fixtures stopped before their assertions.
Their AST method filter also emptied `AssociationTextResponse`, which caused `ValueError: empty body on ClassDef`.
No correction remains under this grant. The saved failed fixtures remain unchanged.

## Independent review findings

The final source review confirmed two additional runtime defects through read-only synthetic diagnostics.
Neither diagnostic changed candidate bytes.

1. `routes/inference.py:29984` attaches an association callback to a reused durable cancellation event.
   A later request without that callback retains the earlier request's callback.
   Request correlation can therefore include another request's native observations.
   The correction must separate request-owned correlation from shared cancellation state.
2. `core/inference/api_monitor.py:1210` compares new observations with the first active interval only.
   Active observations at `[3, 4]` and `[7, 8]` incorrectly permit a later-arriving release record at `[5, 6]`.
   The candidate reports server release despite contradictory later activity.
   The correction must retain observation order and reject stale, overlapping, or contradictory intervals.

The fixture filter at `tests/test_association_bridge.py:38` also blocks two required standard-route checks.
Those checks establish no pass for standard generation or its uncertain-submission refusal.
The focused passthrough submission fixture does not qualify the complete passthrough stream-consumption path.
That path needs explicit acceptance evidence before source acceptance.
The [correction proposal](CREWSHAL-ASSOCIATION-BRIDGE-CORRECTION-PROPOSAL-2026-11-01.md) defines a new, unapproved three-path correction.

## Fresh verification

Exact commands, working directories, output streams, and exit codes remain in the private evidence directory.

| Check | Exit | Result and limit |
| --- | --- | --- |
| Unchanged accepted baseline | `0` | All 97 guarded tests passed before candidate comparison. |
| Correction 1 suite | `1` | 118 tests ran; one Boolean clock case failed. |
| Final candidate suite | `1` | 121 tests ran; 119 passed and two new fixtures errored. |
| Original cases within final suite | Same failed command | All 97 original cases passed. The complete command still failed. |
| New cases within final suite | Same failed command | 22 passed and two errored. |
| Native baseline build and execution | `0`, `0` | The actual native slot type confirmed the missing completion field. |
| Native candidate build and execution | `0`, `0` | Four serializer cases passed with actual native types. |
| Deterministic contract generation | `0` | Both renderings matched. The final suite also verified generated candidate bytes. |
| Private Ruff | `0` | The selected preparation scripts and new fixture module passed. |
| Runtime Ruff comparison | `1`, `1` | Baseline and candidate each reported 55 diagnostics, with zero introduced diagnostics. |
| Three cumulative patch checks | `0` each | Hermes, Studio, and native patches apply to their unchanged starting sources. |
| Candidate syntax and preservation | `0` | Starting files, accepted candidate, unowned support, and installed source hashes matched. |
| Negative guard | `1` | The guard blocked the intended subprocess attempt. The command also retained the two fixture errors. |

The positive final run retained no pending owned fixture thread and recorded no denied external-effect attempt.
The negative guard did not execute its blocked subprocess.
Its preloaded denial also triggered the original metadata fixture's empty-denial assertion.
Do not describe that complete negative run as a passing suite.

CMake was unavailable at the checked installed locations.
Apple Clang `21.0.0` built a private focused executable from the complete native translation unit and installed libraries.
The executable used actual `server_slot` and `server_task` types.
Its four cases covered active serialization, previous idle tasks, reused task IDs, and absent tasks.
The sandbox denied network access and live-profile reads during execution.
No installed server binary was rebuilt or changed.
This fixture does not establish reproducible provenance for the loaded server binary.

An initial Ruff command used a missing Hermes-local executable and exited `1`.
The corrected command used the installed Crewshal Ruff executable.
Earlier missing-path searches and a failed result-parser assertion supplied no successful verification claim.
The corrected parser accounted for verbose diagnostics that split two test-status lines.
An initial publication helper read command metadata where it expected a source summary and exited `1`.
Codex recovered the unchanged source summary from saved stdout into a separate evidence file.
All failed outputs and partial implementation bytes remain preserved.

## Candidate and preservation identity

Private evidence resides in `association-bridge-20261031-01a1940c` under the preserved S1b root.
Starting manifests preserve 835 private files and 1,374 tracked repository files.
Twelve installed source hashes remain unchanged.
All 31 accepted observation-control candidate files retain their bytes.
All nine original test modules and the original submission, supervisor, transport fixture, and guarded runner remain unchanged.
The new candidate changes ten of the twelve permitted runtime paths relative to the accepted base.
Its cumulative patches contain nine Hermes paths, four Studio paths, and one native path.
The two unneeded permitted paths retain their accepted bytes.

The final candidate manifest SHA-256 is `a255a737e81caa02637bdb05074c720f53144677f45add7cc4241bbc9951bc08`.
The cumulative Hermes patch SHA-256 is `7f610f21cc3703240b050dbc7f66572c82784a430cb8876db47ba97663dad0ed`.
The Studio patch SHA-256 is `a665bbde4aa68a047dc6e83134257fe5edfe9aaf5120ac679356bae7ec4c1b0f`.
The native patch SHA-256 is `1e0be321aa84f39c722bb9941d51f031b019983040d78fe3c209b9de6d03d3ca`.
These digests identify rejected candidate bytes. They grant no application authority.

The selected process still shows Ornith `UD-Q4_K_XL`, context `93696`, and one slot in its arguments.
Its executable digest matches the preceding feasibility observation.
The profile and SOUL hashes also match their preserved bindings.
These observations do not verify effective loaded context or new request behavior.
No inference, authenticated HTTP observation, worker dispatch, profile edit, application, or service action ran.

## Remaining limits and continuation

Graph discovery used Verify evidence and current-source fallback.
The Crewshal generation was `2026-10-31T21:18:33Z`.
Hermes generation `2026-09-02T17:14:19Z` remains stale.
Coverage reported changed metadata or untracked paths for the relevant Hermes files.
Studio, native source, and the private candidate used bounded direct source inspection.
No result proves exhaustive graph coverage.

Private runtime checks used Darwin `27.2.0`, arm64, and CPython `3.11.14`.
Publication checks record their own environment in the private closure record.
The supervisor synthetic Jev check returned probability `0.98`, confidence `0.96`, reported cost `0`, and latency `479` milliseconds.
Actual total billing remains unknown. This check does not qualify Hermes worker bindings.
Product suites, mypy, wheel builds, and package installation remain not run for this private-runtime failure checkpoint.
Linux tests remain deferred under ADR 0009.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.

Use the [next prompt](CREWSHAL-ASSOCIATION-BRIDGE-NEXT-SESSION-2026-11-01.md) after the new correction decision.
Preserve the accepted 97-test candidate and the rejected association candidate separately.
An eventual offline pass still requires reproducible binary identity and an exact, separately approved operational plan.
