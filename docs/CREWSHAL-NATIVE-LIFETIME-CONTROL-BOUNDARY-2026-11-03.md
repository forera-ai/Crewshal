# Native tool binding and descendant ownership boundary

Date: 2026-11-03. Package checkpoint: `0.27.28`. Crewshal skill: `1.0.0`.
Base: `5a5845084b53535884680650e12beaea1afae40f` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result

Preparation resolved the proposed make query failure through an exact installed executable.
It also tested and rejected kqueue automatic descendant tracking as a replacement lifetime mechanism.
Complete private build-control preparation remains incomplete.
No replacement supervisor or executable build proposal is ready for owner approval.
This checkpoint records new tool and ownership evidence. It does not repeat the resolved CMake loader diagnosis.

## Exact tool queries

The direct Xcode make executable reported GNU Make `3.81` under a fresh restricted query policy.
Its SHA-256 is `ba5dd576c636ab1ed626f790be00c0aa71ea73befdaae478a8ac10577134a95c`.
The exact Xcode otool resolved through its installed `llvm-otool` symlink.
Its SHA-256 is `bb522e392b7834c29ff579ba8c9259293229163e0fd28b7c64d323d7a858f9d4`.
The dependency query names `/usr/lib/libxcselect.dylib` and `/usr/lib/libSystem.B.dylib`.
These results avoid the earlier system shim without adding a SharedFrameworks or external cache exception.
Exact installed paths, symlink targets, sizes, commands, environments, and outputs remain private.

The first query wrapper inherited a `32,768`-byte file limit around RTK and its child.
That wrapper returned `-25` despite plausible make output. Codex retained the failure and did not accept the version claim.
A targeted revision placed the file limit below RTK, around the sandboxed query process.
It retained the same policy structure and changed only owned query paths.
This result supports the changed limit placement. It does not identify the exact write that caused the earlier signal.

| Query or fixture | Exit | Observed result |
| --- | --- | --- |
| Direct make version | `0` | GNU Make `3.81`; no stderr. |
| Direct make dependency inspection | `0` | Two system dependencies; no stderr. |
| CMake version | `0` | CMake `4.3.4`; no stderr. |
| CMake capabilities | `0` | Expected `Unix Makefiles` generator; no stderr. |
| Fresh policy fixture | `0` | Allowed reads and writes passed; external reads, writes, symlink access, and TCP returned `EPERM`. |

The policy retains `(literal "/")`, independent network denial, and writes confined to owned locations and `/dev/null`.
It adds no broad home, credential, SharedFrameworks, or temporary-directory access.
The query streams have individual `32,768`-byte file limits.
Those per-file limits do not establish aggregate storage enforcement or complete descendant control.
Harmless query acceptance does not qualify native configuration, linking, Metal, or every build subprocess.

## Kernel lifetime route

The installed SDK header `sys/event.h`, lines `355–362`, marks three process flags unsupported since macOS 10.5.
Those flags are `NOTE_TRACK`, `NOTE_TRACKERR`, and `NOTE_CHILD`.
The inspected header SHA-256 is `435ed8fe99ae70c19404c3da14be6e2d217686ac256aed3b5df721b353dbb350`.
Exact-source inspection supplied this evidence because the SDK lies outside the Crewshal graph.

A fresh fixture paused its leader before forking, which permitted registration before the synthetic child existed.
The child changed session, closed its streams, completed finite work, wrote a synthetic marker, and exited.
The fixture sent no signal and addressed no unrelated process.

1. Ordinary `NOTE_FORK` and `NOTE_EXIT` registration reported the leader's fork and exit.
   It produced no detached-child exit event. A parent notification did not establish complete child ownership.
2. Adding `NOTE_TRACK` returned an event with `EV_ERROR` and data `45`, which maps to `ENOTSUP`.
   The Python registration call raised no exception. The returned error event still refused registration.
   No child filter was established. This unsupported route stopped.

Both leaders exited `0`. Both finite children wrote their markers and were absent at exact-PID closure checks.
The capture command exited `0` because it recorded both outcomes.
That fixture exit does not establish a passing ownership control.
The fixture itself is not an independent total-deadline supervisor.

The first independent review extraction matched `udata` instead of `data` and failed an assertion.
No successful review record followed that failed extraction.
The corrected extraction used exact field boundaries and confirmed `EV_ERROR` and `ENOTSUP`.
The failed review preflight and unchanged fixture output remain preserved.

This evidence rejects one proposed kernel route only.
Other supported host mechanisms remain unassessed. No claim of universal host-capability absence follows.
Polling ancestry or accepting leader exit cannot replace complete owned-descendant evidence.

## Acceptance mapping

| Required condition | Status at this boundary |
| --- | --- |
| Preserve old drafts, accepted candidates, installed sources, and historical inputs | Passed for all recorded starting files and selected external bindings. |
| Resolve the make shim query failure without broad new access | Passed for exact version and dependency queries only. |
| Verify restricted queries and synthetic policy refusals | Passed for the fresh query policy and listed fixtures. |
| Establish complete owned-descendant lifetime | Failed for the tested kqueue route; no accepted replacement exists. |
| Separate pipe EOF from completion in replacement controls | Not run. No complete replacement supervisor was prepared. |
| Independent `1,800`-second ceiling through cleanup and evidence | Not run for replacement controls; no scaled or full-scale pass is claimed. |
| Aggregate `8 GiB` new-file accounting and enforcement | Not run for replacement controls. Per-file query limits do not satisfy it. |
| Bounded build diagnostics, admission, evidence-write failure, and owned cleanup | Not run for replacement controls. |
| Exact executable private-build proposal | Unready. No build decision is requested. |

Complete descendant ownership is the smallest unresolved prerequisite for replacement control selection.
The next session must establish a supported mechanism and its permitted scope before constructing a full supervisor.
It must retain two parallel jobs, `1,800` seconds total including cleanup and evidence, and at most `8 GiB` new files.
All remaining controls require observable success and refusal cases against their exact saved implementation.
Short scaled tests cannot establish an unobserved full-scale pass.
No image was created, attached, detached, inspected, or removed during this preparation.
Future cleanup must preserve unresolved attachment and termination outcomes.

## Preservation, environment, and review

Trusted current `turn_context` metadata identifies `gpt-6.1-sol` in this checkout.
The checkout started clean with synchronized version `0.27.27` and canonical `origin`.
RTK reports `1.1.0`. Required companion skills loaded from their recorded installed paths.
The Jev preflight returned probability `0.99`, confidence `0.98`, reported cost `0`, and latency `229` milliseconds.
Actual total billing remains unknown.
Graph Verify evidence used generation `2026-11-03T13:54:00Z`.
Private controls lie outside that project and used exact-source fallback.
Graph coverage remains a best-effort signal, not proof of completeness.

Fresh preservation checks found no mismatch in these records:

- All `1,552` starting private files, including both unchanged runner drafts and historical failures.
- All `46` accepted candidate files, `12` installed source files, and one support source.
- All `3,964` native regular files under the recorded exclusions, with the same complete regular-file set.
- All `42` cached runtime entries and `16` previously selected tool files.
- All `4,041` CMake files, `41,697` SDK entries, `364` compiler-resource entries, and `7,596` TLS entries.
- All `84` system-runtime entries and the recorded profile, SOUL, companion skills, and Crewshal skill installations.

The storage observation recorded `117,267,988,480` free bytes. It supplies no future admission or hard-limit proof.
Private evidence resides in `native-control-preparation-20261103-01a1a1fb` under the preserved S1b root.
The two previous preparation directories remain unchanged.
The private catalogue records complete file reads and hashes for their `64` diagnosis files and `74` capability files.
Both complete saved runner sources were reviewed without executing their build entry points.
`codex-review.json` accepts this changed preparation boundary and rejects complete build-control readiness.
Publication and closure records contain exact commands, exit statuses, file identities, environment, scope, and delivery revision.

Publication checks passed `rtk proxy git diff --check` and the explicit frozen Phase 3A checker with exit `0`.
The checker confirmed all `23` artifacts and retained false execution gates.
The saved version/import command exited `0` and confirmed synchronized version `0.27.28` from the current checkout.
Local links, historical text, exact seven-file scope, private syntax, and all starting private-file comparisons passed.
Scope verification preserved `1,380` tracked files outside the intended publication paths.
Publication graph coverage reported generation `2026-11-03T15:24:49Z`, with matching metadata for all `21` selected paths.
Product suites, Ruff, mypy, wheel builds, and package installation remain not run for this documentation boundary.
Linux checks remain deferred under ADR 0009.

## Closed gates

No native configuration, compiler probe, compilation, compiled runtime, installed-file edit, or accepted-candidate edit ran.
No image action, model-service action, authenticated route, credential extraction, model request, or Hermes dispatch ran.
All source budgets remain consumed. The separate translator budget remains unused.
The historical `130` guarded tests and four native cases were not rerun.
Current model readiness and loaded library identity remain unverified.
All `192` development rows remain planned. All `576` sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.
Use the [next prompt and exact inputs](CREWSHAL-NATIVE-LIFETIME-CONTROL-NEXT-SESSION-2026-11-03.md).
