# Hermes deadline continuation: runtime binding stop

Date: 2026-10-28. Package checkpoint: `0.27.11`. Crewshal skill: `1.0.0`.
Base revision: `166019cb9ceac16e5203397a410b0b9e4207e089` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a1836e-2ce8-77c1-884c-0f6e2390dfc4`.

## Verdict and stopping boundary

The existing private deadline-control milestone remains **blocked**. No live deadline proof exists.
The continuation explicitly requires a stop after a required runtime binding fails.
The preserved inspector failed before private control edits or a diagnostic launch.
Codex accepts this blocked-state record only. The private runner remains unaccepted for live use.
No new Hermes session, model request, implementation attempt, worker probe, or approval probe ran.
S1b implementation remains closed.

The remaining milestone acceptance conditions are unchanged:

1. Verify current runtime bindings and the preserved evidence.
2. Verify supported submission, receipt, and interruption contracts with exact current source.
3. Prove admission mapping and failure cleanup with independent offline fixtures.
4. Assess one short read-only diagnostic with a recorded policy, deadline, ceiling, and cleanup.
5. Require matching terminal admission and server cancellation or completion evidence.

Condition 1 failed for runtime bindings. Evidence preservation passed.
The source review is partial. Conditions 3 through 5 remain **not run** during this continuation.
The nine earlier fixture passes remain historical evidence. They do not establish current live termination.

## Start evidence

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
HEAD matched the base above. Git status and both diffs were initially empty.
The remote remained `https://github.com/forera-ai/Crewshal.git`.
Both package declarations initially contained `0.27.10`. RTK reported `1.1.0`.
The five installed Crewshal skill files matched their repository copies.
The Hermes skill exposure resolved to `/Users/hamedprooshani/.codex/skills/crewshal`.
Codex read the required companion files from these paths:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`.
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`.
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`.

The graph service responded for both projects. Evidence tier: Verify.
Crewshal coverage generation was `2026-10-25T18:30:46Z`; selected existing records had matching metadata without recorded gaps.
Hermes generation remained `2026-09-02T17:14:19Z`.
Graph search returned zero matching control symbols; coverage marked the three control paths `not_tracked`.
Exact source supplied the limited control findings below. Best-effort coverage does not prove completeness.
A bounded synthetic Jev check returned probability `0.05`, confidence `0.9`, reported cost `0`, and latency `208` milliseconds.
The check advised no runtime decision. Actual total billing remains unknown.

## Failed runtime gate

This preserved command exited 1:

```sh
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/diagnosis-20261025/inspect_runtime.py
```

Its final diagnostic was `AssertionError: Diagnosis bindings changed.`
Codex did not replace its saved baseline or weaken its comparison.

| Binding | Observation |
| --- | --- |
| Profile SHA-256 | Expected `aa0b2326acfe4b24494183a79e859a0330501a0bbfdedb6521543ab801ebd1c6`; observed `daf8f597b75b319cd19104753f7b64cda0d66dd0fd9fe44e26c77314554be412`. |
| Selected nonsecret configuration fields | All fields saved by the diagnosis still matched. Fallback providers remained empty. |
| SOUL | Its saved hash still matched. |
| Hermes source | HEAD remained `bf0203a794a07aac3ff764972ab9087baa4e4f4e`; status was clean; all 15 saved source hashes matched. |
| Preserved probe bindings | All matched except the profile hash. |
| Original model-server process | `rtk proxy ps -p 33814 -o pid=,lstart=,command=` exited 1 with empty output. |

The current enabled plugins are `better-session-appearance` and `homeassistant`.
The preserved pre-R1 configuration lists only `homeassistant`.
That snapshot predates accepted readiness. It is not the complete accepted-profile snapshot.
The observed plugin difference does not establish the complete cause or timing of the profile hash change.
Codex did not inspect or select a replacement server. Its identity, context, capacity, and cancellation behavior remain unknown.
No profile edit, model switch, credential extraction, server restart, or metered fallback ran.
R1 remains accepted historical evidence. Current bindings do not permit its automatic reuse.

## Preserved attempts and limited source review

All ten entries in `deadline-20261025/evidence-hashes.json` matched before any new private evidence file was written.
All 33 entries in `diagnosis-20261025/prior-artifact-hashes.json` also matched.
The original admissions remain sequence 51, generation 1, `terminal/completed`, and sequence 52, generation 2, `terminal/interrupted`.
The preserved D1 request has no admission. Its consumed-intent file remains absent.
R1, the refused implementation launch, corrected I1, and failed D1 preflight remain unchanged.
No attempt or correction count was reset.

Codex read every private input named by the continuation. It did not launch or modify the old runner.
Direct source confirms these limited facts:

- `gateway/session_controls.py:749` maps RPC `input_id` into `Submission.request_id`.
- `gateway/session_authority.py:406` exposes stored `request_id` as a pending receipt's `input_id`.
- `gateway/session_authority.py:865` checks the generation before interruption effects.
- `hermes_cli/gateway_client.py:190` preserves unknown execution outcome after disconnect.

The runner still queries nonexistent database column `input_id`.
After possible submission acceptance, a failed admission lookup prevents entry into `supervise`.
The outer exception handler saves a failure. Its finalizer cancels the collector and captures server-log bytes.
That finalizer does not interrupt and reconcile the possibly accepted execution.
A lost creation acknowledgement can also leave the local session ID unknown.
These findings require independent mapping and cleanup fixtures before any launch.
This continuation performed no repair or new fixture run after the failed binding gate.

## Closure evidence and next inputs

Private evidence resides under `deadline-20261028-binding-stop` within the preserved S1b evidence root.
The directory uses mode `0700`; evidence files use mode `0600`.
`audit_bindings.py` reads selected configuration and SQLite data without connecting to a gateway or model.
`binding-evidence.json` stores the sanitized observations, exact subprocess argv, exits, source comparisons, and preserved admission states.
`initial-tracked-hashes.json` binds all 1,347 tracked files before publication edits.
Raw logs, profile configuration, credential references, and complete exports remain outside Git.

The local publication checks are recorded in the private `closure-results.json`.
They cover preserved artifacts, unrelated tracked bytes, historical document suffixes, links, versions, whitespace, and the frozen package.
The exact closure commands are:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-binding-stop/audit_bindings.py
rtk proxy python3 /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-binding-stop/verify_closure.py
```

All six final closure commands exited 0.
The source import reported `0.27.11` on Darwin `27.2.0`, arm64, with CPython `3.12.16`.
The frozen checker reported 23 artifacts, 768 planned units, and both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The binding audit verified the blocked observation. Its exit 0 does not make the failed runtime gate pass.
The closure verifier checked all seven intended paths and preserved historical bytes.
An earlier closure run stopped with exit 1 because the audit compared Python tuples with saved JSON arrays.
A diagnostic rerun isolated that type mismatch. Codex normalized comparison types without replacing the saved observations.
The corrected audit exited 0. The initial failed closure results and diagnostic difference remain private.
Codex reviewed the complete seven-file publication diff and accepted this blocked documentation checkpoint.

Product suites, private fixtures, Ruff, mypy, wheel builds, and installed-package checks remain **not run** for this documentation checkpoint.
Linux-specific checks remain **deferred** under ADR 0009.
Actual billing remains unknown. No Crewshal evaluation or spending authority changed.

The [next prompt](CREWSHAL-HERMES-DEADLINE-RESUME-2026-10-28.md) continues this same milestone after runtime reconciliation.
The smallest missing capability is a verified running selected server with a reconciled profile binding.
The remaining runner mapping and cleanup work follows that gate. Neither approval nor publication can replace termination evidence.
All image actions, guests, downloads, Linux tests, campaign execution, calibration, evaluation, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain 10,008,484,533 and 116,542,541 bytes.
Their conservative total remains 10,125,027,074 bytes.
