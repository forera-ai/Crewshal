# Restricted CMake diagnosis and build-control rejection

Date: 2026-11-03. Package checkpoint: `0.27.27`. Crewshal skill: `1.0.0`.
Base: `7596b4523409dc9a4d8623671418587530237c28` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result

Harmless queries isolated two restrictions behind the earlier CMake failure.
A read exception for the root directory itself removed the loader abort.
CMake then reported `Current working directory cannot be established.`
The same policy passed CMake version and capabilities queries from an allowed working directory.
The exception uses `(literal "/")`. It does not permit reads of all root descendants.
Network denial and the existing write restrictions remained in place.
Codex preserved both historical failed policies and did not replay their unchanged commands.

This result accepts the bounded diagnosis only.
It does not qualify the complete build policy or either saved runner.
Independent synthetic fixtures exposed two supervisor defects.
A separate harmless query showed that the proposed make path still fails under the restricted policy.
No complete private-build proposal is ready for owner approval.

## Diagnosis evidence

Both historical CMake crash reports contain `SIGABRT` and loader frames through `ignition_halt`, `boot_boot`, and `dyld4::CacheFinder`.
These frames directed the root-directory hypothesis.
They do not identify every internal loader operation.
The single read-rule change removed the abort, while the allowed working directory removed the later CMake error.
These observations establish the tested remedy without claiming a complete operating-system diagnosis.

| Query or fixture | Exit | Result |
| --- | --- | --- |
| CMake version with only the root-directory exception | `1` | The loader abort disappeared. CMake rejected the original working directory. |
| CMake version from an allowed directory | `0` | CMake reported `4.3.4`. |
| CMake capabilities from that directory | `0` | The capabilities response included the expected generator. |
| Exact compiler version under the fixture policy | `0` | Apple Clang reported `21.0.0`. |
| Proposed `/usr/bin/make --version` under that policy | `71` | The Xcode shim requested a denied cache path and a denied framework read. |
| Explicit TCP and file-policy fixture | `0` | Allowed reads and writes passed. External synthetic reads, writes, symlink access, and TCP connections returned `EPERM`. |

The make diagnostic names `DVTSystemPrerequisites.framework` under Xcode's `Contents/SharedFrameworks` directory.
The saved policy permits `Contents/Developer`, which does not include that directory.
The shim also attempted an `xcrun_db` file outside the owned temporary directory.
These are observed requirements of the failed query, not permission to broaden access.
The next preparation must bind supported exact tools or justify each necessary narrow dependency.
It must retain independent network denial and required TLS.

One synthetic preflight never launched because its sanitized PATH omitted RTK.
The corrected command used the verified absolute RTK path.
The system Python shim then failed through Xcode with exit `71`.
The first Perl fixture passed with a protocol-lookup warning.
A refinement using an unavailable Perl constant failed before its fixture executed.
The final fixture used explicit TCP protocol number `6` and passed without diagnostics.
All failed inputs and results remain preserved. None supplies passing evidence.

## Saved runner review

Codex read both complete saved scripts before executing any synthetic review fixture.
The original `bounded_run.py` digest remains `e6c8d3d73c849b1562889c73eb42c9f41ccc15a05f5a5066cc0be87f0bb2fdf3`.
The original `native_build_steps.py` digest remains `c23a2847365702b4ad2f0b6b2f320a1a5a3a057101ccdaa221d98c3407a086a6`.
The fixture loaded the exact supervisor function without invoking either script's build entry point.

1. The supervisor accepted success before a detached finite child completed.
   The leader exited `0`, and the original process group disappeared.
   The supervisor returned `accepted: true` before the child wrote its synthetic marker.
   The child wrote that marker after acceptance and then exited.
   A later exact-PID check confirmed that the owned fixture child was gone.
   Process-group disappearance therefore cannot establish complete descendant termination.
2. The supervisor killed valid finite work after both output streams closed.
   The child needed approximately `0.25` seconds and had a `1`-second work budget.
   The supervisor killed it after approximately `0.020` seconds, with exit `-9`.
   The same child completed with exit `0` outside that supervisor.
   Pipe EOF and process completion require separate handling.
3. Static review did not establish an independent total ceiling.
   The same supervisor performs pipe handling, process waits, detach capture, file traversal, and final evidence writes.
   Detach uses `capture_output` before truncating its saved diagnostic.
   No separate watchdog bounds every stage through final evidence capture and cleanup.
   The claimed `1,800`-second total therefore remains unverified.

The fixture command exited `0` because it captured the defects successfully.
That exit does not turn either defective behavior into a control pass.
The historical four successful supervisor fixtures remain valid only for their original bounded cases.
No full-scale storage, output, cleanup, or process-lifetime enforcement claim follows.
The old runners remain unchanged, unaccepted drafts.

## Preservation and environment

Trusted current `turn_context` metadata identifies `gpt-6.1-sol` in the exact checkout.
The branch started clean at the recorded base, with synchronized version `0.27.26` and canonical `origin`.
RTK reports `1.1.0`. The required installed skills loaded and matched their preserved hashes.
The synthetic Jev check returned probability `0.98`, confidence `0.96`, reported cost `0`, and latency `289` milliseconds.
Actual total billing remains unknown.
Graph Verify evidence used generation `2026-11-03T10:46:35Z`.
Exact saved-source reads supplied evidence for the unindexed private controls.
Publication coverage reported generation `2026-11-03T13:54:00Z`, with matching metadata for all `23` selected paths.
Graph coverage remains a best-effort signal, not proof of completeness.

Fresh comparisons found no mismatch in these inputs:

- All `1,488` starting private files match, including historical failures and both runner drafts.
- All `46` accepted candidate files, `12` installed source files, and one support source match.
- All `3,964` native regular files match, with the same complete regular-file set under the recorded exclusions.
- All `42` cached runtime entries, `16` selected tools, and `4,041` CMake distribution files match.
- All `41,697` SDK entries, `364` compiler-resource entries, `7,596` TLS entries, and `84` system-runtime entries match.
- The profile, SOUL, companion skills, and versioned and installed Crewshal skill files match.

Storage observation recorded `117,499,355,136` free bytes.
That observation does not establish future admission or aggregate storage enforcement.
Codex performed no image creation, attachment, detachment, or removal during this diagnosis.
The earlier `64 MiB` storage probe remains historical evidence.

Private evidence resides in `native-build-diagnosis-20261103-01a1a1a5` under the preserved S1b root.
It contains exact query commands, policies, crash reports, fixture source, results, manifests, and the Codex review.
`codex-review.json` accepts diagnosis documentation and rejects build readiness.
The closure record binds publication commands, revision, environment, scope, and preservation results.

Publication checks passed these commands with exit `0`:

- `rtk proxy git diff --check`.
- `rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py`.
- The saved version/import command, which confirmed synchronized version `0.27.27` from the current checkout.

The freeze checker confirmed all `23` artifacts and retained false execution gates.
Scope checks preserved `1,378` tracked files outside the seven intended publication paths.
Link checks, historical-record comparisons, and all `1,488` starting private-file comparisons passed.
The private publication record retains exact commands, output streams, exit statuses, and file hashes.

## Remaining acceptance and closed gates

The next milestone must prepare fresh private controls and verify their complete observable behavior.
It must preserve the old drafts and all accepted candidate bytes.
Required checks include detached descendants, closed pipes, failure exits, deadlines, bounded output, evidence failures, storage exhaustion, and owned cleanup.
The exact effective tool paths and policy must pass harmless queries before any build decision request.
Keep at most two parallel jobs, `1,800` seconds total including cleanup, and at most `8 GiB` new files.
Only accepted complete controls can support the executable private-build proposal and a separate owner build decision.
This checkpoint requests no build approval.

No native configuration, compiler probe, compilation, compiled runtime, candidate edit, service action, model request, or Hermes dispatch ran.
Codex did not rerun the historical `130` guarded tests or four native serializer cases.
All source budgets remain consumed. The separate translator budget remains unused.
Current model readiness and loaded library identity remain unverified.
Product tests, Ruff, mypy, wheel builds, and package installation remain not run for this documentation checkpoint.
Linux checks remain deferred under ADR 0009.
All `192` development rows remain planned. All `576` sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.
Use the [control-preparation prompt and exact inputs](CREWSHAL-NATIVE-BUILD-CONTROL-REPAIR-NEXT-SESSION-2026-11-03.md).
