# Hermes deadline reconciliation: selected service unavailable

Date: 2026-10-28. Package checkpoint: `0.27.12`. Crewshal skill: `1.0.0`.
Base revision: `4af37983b61671ce5ef985d05d0bc93cd98f1cbb` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a1837e-8512-7472-8a6e-07d70abe6bf7`.

## Verdict and acceptance boundary

The same private deadline-control milestone remains **blocked**. No live deadline proof exists.
Read-only reconciliation found no service on the selected loopback route or historical model backend.
The prompt requires dependent work to stop when no matching server exists.
Codex accepts this new evidence and its documentation checkpoint only.
The private runner remains unaccepted. S1b remains closed.

The milestone still requires these acceptance conditions:

1. Reconcile current profile bindings and verify the selected running model server.
2. Verify current submission, receipt, and interruption contracts through exact source.
3. Prove admission mapping and failure cleanup with independent offline fixtures.
4. Assess one recorded, bounded, read-only live diagnostic after offline acceptance.
5. Require matching terminal admission and actual server cancellation or completion evidence.

Condition 1 remains blocked. This continuation did not perform conditions 2 through 5.
The earlier source findings and nine fixture passes remain historical evidence.
No private deadline control, test, runner, plan, or historical baseline changed.

## Verified start and preservation

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
HEAD matched the base above. Initial Git status was empty.
The canonical remote remained `https://github.com/forera-ai/Crewshal.git`.
Both version declarations initially contained `0.27.11`. RTK reported `1.1.0`.
All five installed Crewshal skill files matched the repository copies.
The Hermes skill exposure resolved to `/Users/hamedprooshani/.codex/skills/crewshal`.

Codex read the required companion skills from these files:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`.
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`.
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`.

The graph service responded for both projects. Evidence tier: Verify.
Crewshal coverage generation was `2026-10-28T17:02:18Z`.
All 22 selected existing paths had matching metadata without recorded gaps before publication edits.
Hermes coverage generation remained `2026-09-02T17:14:19Z`; the three control paths remained `not_tracked`.
No current API behavior claim relies on that stale graph. Exact source review remains required after runtime reconciliation.
Best-effort coverage does not prove completeness.
The synthetic Jev check reported probability `0.03`, confidence `0.94`, cost `0`, and latency `251` milliseconds.
It verified a decision path only. Actual total billing remains unknown.

Both historical manifests matched before any new evidence file was written:

- `deadline-20261025/evidence-hashes.json`: all ten entries matched.
- `diagnosis-20261025/prior-artifact-hashes.json`: all 33 entries matched.

The new evidence directory separately binds all 70 existing private files and all 1,349 tracked repository files.
The preservation check includes the old inspectors, manifests, observations, controls, plans, and closure results.
Codex read every private file named by the October 25 continuation and the October 28 binding-stop prompt.
It did not run the old inspector, which writes historical log extracts before its comparison.
It did not run the old closure audit, which can write observation differences into its historical directory.

Original admission sequence 51, generation 1, remains `terminal/completed`.
Original admission sequence 52, generation 2, remains `terminal/interrupted`.
The D1 request has no admission. Its consumed-intent file remains absent.
R1, the refused implementation launch, corrected I1, and failed D1 preflight remain preserved. No count was reset.

## Current profile and selected service

The current profile SHA-256 remains `daf8f597b75b319cd19104753f7b64cda0d66dd0fd9fe44e26c77314554be412`.
The accepted historical baseline remains `aa0b2326acfe4b24494183a79e859a0330501a0bbfdedb6521543ab801ebd1c6`.
All selected fields saved by the diagnosis still match. The SOUL hash also matches.
Fallback providers remain empty. These comparisons do not reconcile the complete profile binding.

The stored R1 effective policy lists only `homeassistant`.
The current profile lists `better-session-appearance` and `homeassistant`.
The current `voice.record_key` also differs from the stored policy.
The stored effective policy is not a complete byte copy of the accepted raw profile.
These observations do not prove the complete cause, timing, or execution effects of the changed profile hash.
No new profile authority or automatic R1 reuse follows from matching selected fields.

The selected route remains `http://127.0.0.1:8888/v1`.
The historical model backend used loopback port `63421` and PID `33814`.

| Read-only observation | Exit or result |
| --- | --- |
| `rtk proxy lsof -nP -iTCP:8888 -sTCP:LISTEN` | Exit 1; stdout and stderr were empty. |
| `rtk proxy lsof -nP -iTCP:63421 -sTCP:LISTEN` | Exit 1; stdout and stderr were empty. |
| `rtk proxy ps -p 33814 -o pid=,lstart=,comm=` | Exit 1; stdout and stderr were empty. |
| `rtk proxy ps -axo pid=,ppid=,lstart=,comm=` | Exit 0; filtered executable paths contained no `llama-server`. |
| Transport-only connection to `127.0.0.1:8888` | `ConnectionRefusedError`, errno `61`, `ECONNREFUSED`. |
| Transport-only connection to `127.0.0.1:63421` | `ConnectionRefusedError`, errno `61`, `ECONNREFUSED`. |

Each connection used a one-second timeout and sent no application bytes.
No gateway RPC, HTTP generation request, or model request ran.
No selected running server was available during these observations.
The served model, current context, capacity, and cancellation behavior therefore remain unavailable.
Historical model settings cannot establish a current server identity.

Hermes source remained clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
All 15 saved diagnosis source hashes matched. The preserved plan bindings matched except the profile hash.
No server start, restart, model selection, profile edit, credential extraction, or fallback ran.

## Exact owner preparation and later decision boundary

The owner must prepare the existing selected local service before dependent work resumes.
This session did not perform or authorize that preparation on the owner's behalf.

1. Use the existing Unsloth Studio controls for the selected local service.
2. Load the existing cached `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` model.
3. Retain the recorded 93,696-token context and one-slot configuration.
4. Keep the existing selected loopback route at `http://127.0.0.1:8888/v1`.
5. Leave the Hermes profile, provider, approval controls, skills, and fallback settings unchanged.
6. Preserve the resulting process identity and matching model-load log for read-only verification.
7. Stop if preparation requires a download, model substitution, credential extraction, or changed runtime settings.

The historical backend port can identify the earlier process only. Do not force a new backend to reuse that port.
A new PID or backend port requires fresh process, route, model, context, capacity, and log evidence.
The owner need not supply a password, API key, or complete configuration export.
No model request or readiness probe is part of this preparation.

A running service alone cannot reconcile the changed profile.
After preparation, inspect the added plugin and other relevant differences without executing them.
Prepare any required owner decision with exact changed bindings, execution effects, permitted action, limits, and cleanup.
Do not request acceptance of an unexplained hash change or overwrite the old baseline.
Do not repeat successful worker or approval probes without a relevant changed binding.

After both runtime prerequisites pass, follow the October 25 continuation for the remaining private controls.
The old `probe.py` still queries nonexistent database column `input_id`.
Its possible-acceptance cleanup remains unaccepted. Never launch it unchanged or replay an uncertain launch.
Independent SQLite mapping fixtures and lost-acknowledgement cleanup evidence remain required before another live assessment.

## Private evidence and publication checks

Private evidence resides under `deadline-20261028-reconciliation` within the preserved S1b root.
The directory uses mode `0700`; its files use mode `0600`.
`audit_reconciliation.py` records selected comparisons, exact subprocess argv, exits, transport results, and preserved admissions.
It makes no gateway or model request. Its exit 0 verifies the blocked observation, not runtime readiness.
`binding-evidence.json` preserves the first observation without replacing either historical baseline.
`initial-private-hashes.json` and `initial-tracked-hashes.json` bind the starting bytes.
`graph-evidence.json` preserves the coverage responses.
Profile configuration, credential references, complete exports, and raw logs remain outside Git.

The private `closure-results.json` records exact publication commands, working directories, exits, and outputs.
The required commands are:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-reconciliation/audit_reconciliation.py
rtk proxy python3 /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-reconciliation/verify_closure.py
```

All six commands exited 0.
The source import reported `0.27.12` on Darwin `27.2.0`, arm64, with CPython `3.12.16`.
The frozen checker reported 23 artifacts, 768 planned units, and both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The closure verifier checked seven intended paths, preserved historical suffixes, links, versions, and 1,344 unchanged tracked files.
It also verified all 70 historical private files, all 43 manifest entries, private permissions, and absent D1 consumption.
Codex reviewed the complete seven-file publication diff and accepted this blocked documentation checkpoint.
The acceptance does not pass the runtime gate or qualify the private runner.
The audit environment is Darwin `27.2.0`, arm64, with CPython `3.11.14`.
Repository checks use the local macOS virtual environment.
Product suites, private fixtures, Ruff, mypy, wheel builds, and installed-package checks remain **not run**.
Linux-specific checks remain **deferred** under ADR 0009.
No new Hermes session, request, worker probe, approval probe, or live diagnostic ran.

The [next prompt](CREWSHAL-HERMES-DEADLINE-OWNER-PREP-NEXT-SESSION-2026-10-28.md) continues this same milestone after owner preparation.
All image actions, guests, downloads, Linux tests, campaigns, calibration, evaluation, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain 10,008,484,533 and 116,542,541 bytes.
Their conservative total remains 10,125,027,074 bytes.
