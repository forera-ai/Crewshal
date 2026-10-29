# Offline auxiliary cancellation repair

Date: 2026-10-29. Package checkpoint: `0.27.17`. Crewshal skill: `1.0.0`.
Base revision: `04d208d502006ab9b37f6d2a4b0a09debd652ca2` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a187ef-bc1f-74e2-a639-ff9b56bcc0c9`.

## Verdict and authority

Codex accepts the isolated offline source candidate and private supervisor controls within the tested scope.
The owner authorized direct preparation by a verified Sol 6.1 context for this milestone.
Trusted local `turn_context.model` identified this context as `gpt-6.1-sol`.
No Hermes worker or model request ran.
The temporary implementation exception does not change the global Crewshal skill.

One implementation attempt and two targeted corrections consumed the new repair budget.
I1, I2, and I3 remain exhausted and unchanged.
The candidate remains isolated. Installed Hermes source, services, profile, and SOUL remain unchanged.
The rejected I3 draft retains its recorded digest and defects.
This checkpoint contains project records and synchronized versions only.

**The selected default provider path remains unavailable for protected inference.**
Its existing relay callback supplies no prepared request-owned operation.
The candidate refuses that callback before provider dispatch.
Positive cancellation tests use synthetic owned operations. They do not qualify an installed provider transport.
The [activation proposal](CREWSHAL-AUXILIARY-CANCELLATION-ACTIVATION-PROPOSAL-2026-10-29.md) therefore remains unapproved and not ready for a live auxiliary proof.

## Start gate and preservation

The checkout started clean at the base revision. Both package declarations contained `0.27.16`.
The remote remained `https://github.com/forera-ai/Crewshal.git`.
All five installed Crewshal files matched their repository copies.
Codex read `codebase-memory`, `caveman`, and `jev` from their established paths.
The owner closed model requests. Codex therefore preserved historical Jev evidence without repeating its synthetic model call.
Current tool exposure supplied the Jev schema. No fresh Jev functional result is claimed.
Historical Jev probability remained `0.97`, with reported cost `0`. Actual total billing remains unknown.

Nine historical manifest sets matched, including the auxiliary-diagnosis checkpoint.
New starting manifests captured existing private files and all 1,359 tracked repository files.
Twelve current Hermes source hashes matched the earlier diagnosis.
Hermes remained clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
Read-only observation verified unchanged profile, SOUL, stored I3 policy, selected model, context `93696`, and one slot.
The gateway retained multiplexer epoch `12` and profile authority epoch `11` separately.
The database reported zero active admissions. The bounded server tail reported idle slots.
Only `runtime.describe` ran through the observation RPC surface.

Graph discovery used Verify evidence.
Crewshal coverage generation was `2026-10-29T13:51:55Z` before publication changes.
Hermes generation `2026-09-02T17:14:19Z` remained stale.
Its snippet returned unrelated current lines. Codex used exact current source and hashes for material claims.
Private candidates were not indexed. No coverage report proves completeness.

## Candidate behavior and ownership

The private candidate changes two Hermes files:

- `agent/auxiliary_client.py` changes only `_run_protected_sync_provider_call`.
- `agent/auxiliary_stream_watchdog.py` adds the prepared-operation contract and terminal failure signals.

No existing provider adapter, gateway file, commit fence, or ordinary stream watchdog changes.
The existing relay `create` argument carries a prepared callback without a new adapter.
Unprotected callbacks retain their calling-thread path.

Protected callbacks require a cancellation source and one prepared request-owned operation.
The operation binds seven identity fields, an absolute deadline, and one cleanup allowance.
It must own cancellation during response creation and blocked reads before dispatch becomes eligible.
An ordinary SDK callback or a capability flag cannot satisfy this contract.
Construction alone does not qualify the supplied transport functions.

The owner rechecks cancellation and deadline before invocation.
Cancellation sets an attempt-local stop signal and invokes only the owned abort operation.
The provider owner closes its resources. Retirement and abort use one transport fence.
Late cleanup cannot abort a retired connection after reuse.
Cancelled attempts cannot restart when a reusable host event clears.
Deadline, refusal, and unresolved signals bypass ordinary retry and fallback exception handlers.
Failed or overdue closure remains unresolved. Local closure does not prove server release.

The new private `supervisor_control.py` observes one existing attempt without submitting it.
It retains supervision after terminal admission and foreground exit.
It records gateway state, client exit, auxiliary closure, and matching server release separately.
Its default limits preserve `600` seconds, `15` seconds of cleanup, and the separate `630`-second client ceiling.
An early stop shortens cleanup. Activity cannot extend the original limits.
Lost acknowledgements never permit replay.
The controller requires prior server-task association before release can satisfy reconciliation.
Failed evidence output cannot publish an acceptance record.
No live gateway or server observation adapter was added.

## Offline evidence and review

New evidence resides in `aux-repair-20261029` under the preserved S1b root.
The root remains defined in the [owner-preparation prompt](CREWSHAL-HERMES-DEADLINE-OWNER-PREP-NEXT-SESSION-2026-10-28.md).
All controls, source copies, patches, raw observations, and test artifacts remain private.

The initial fixture import failed because the external-effect guard blocked version-discovery subprocesses.
The corrected fixture supplies a synthetic version and an empty plugin directory.
The baseline then reproduced unsupported provider dispatch: one test failed and one passed.
The first candidate passed 30 tests. Review required additional refusal, terminal-state, and evidence-failure controls.
Correction 1 passed 37 tests. Review then required cancellation-consumption and dispatch-boundary checks.
Correction 2 and final verification passed 39 tests.
The fixture guard denies network connection, datagram send, subprocess, credential-file, and live-profile access.
The runner verifies both loaded candidate paths and waits for owned fixture threads to finish.

The final command exited 0:

```sh
rtk proxy env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/aux-repair-20261029/offline_runner.py
```

Private `codex-review.json` maps all 16 diagnosis cases to exact passing test names.
The cases cover pre-dispatch refusal, blocked creation, continuous generation, blocked reads, independent lifetimes, and immutable limits.
They also cover completion races, connection reuse, concurrent requests, identity refusal, commit fencing, absent release, and partial evidence failures.
Existing commit-fence tests execute the unchanged current class.
These are bounded offline results, not live conformance.

Syntax and compilation checks passed without writing bytecode.
Ruff passed for the private controls, tests, and watchdog candidate.
The configured Hermes router check exited 2 because the installed checker does not recognize `PLR1708`.
An isolated comparison retained the same 19 baseline router diagnostics; both isolated commands exited 1.
No new router diagnostic appeared. The configured Hermes check remains unavailable, not passing.
The read-only patch applicability check exited 0.
The exact commands and exits reside in `verification-results.json` and the preserved failure record.
Checks used Darwin `27.2.0`, arm64, and CPython `3.11.14`.
Publication checks use the Crewshal CPython `3.12.16` environment.

Codex reviewed the complete cumulative patch, existing relay callers, commit contracts, saved tests, and actual results.
No separate reviewer model ran under the model-request restriction.
The frozen runtime patch SHA-256 is `7d47820263b5bd27847d13bf7e4cc835f6e24d7b521e7b63aeffeae0c428aec5`.
`candidate-hashes.json` binds all eight candidate artifacts.

## Closure and next boundary

Whitespace, frozen-package, synchronized-version, local-import, link, scope, and preservation checks passed with exit 0.
Product suites, product mypy, wheel builds, and installed-package checks remain not run for this process checkpoint.
Linux-specific checks remain deferred under ADR 0009.
The [next prompt](CREWSHAL-AUXILIARY-CANCELLATION-REPAIR-NEXT-SESSION-2026-10-29.md) preserves the remaining transport and activation gates.

The default transport still needs an actual request-owned operation before positive live proof becomes eligible.
Neither this candidate nor the owner's offline authority admits activation, restart, or model inference.
S1b, image actions, guests, downloads, Linux tests, campaigns, evaluation, merge, deployment, and releases remain closed.
The exact image attach action remains unapproved. Selected floors still need the reviewed proposal amendment.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
D3 retains its original bounded acceptance. I3's release cause and unsynchronized-clock limitation remain unchanged.
