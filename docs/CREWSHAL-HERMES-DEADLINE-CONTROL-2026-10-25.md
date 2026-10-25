# Private Hermes deadline control: blocked live proof

Date: 2026-10-25. Package checkpoint: `0.27.10`. Crewshal skill: `1.0.0`.
Base revision: `2897c5abbe91b5b5beef1f602de32df0226b8c8f` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a17444-1dd1-7bf3-a85f-32579c5d9cdb`.

## Verdict and scope

The runtime deadline-control milestone remains **blocked**. Nine offline fixtures pass, but no live deadline proof exists.
Codex accepts this process record and the bounded offline evidence. It does not accept the live probe runner.
The private control remains outside Crewshal product source. No product adapter or orchestration framework was added.
No new Hermes session or model request ran. S1b implementation and its action proposal remain closed.

The acceptance conditions were:

1. Verify the checkout, supervisor, preserved evidence, and unchanged runtime bindings.
2. Prepare an immutable monotonic deadline around supported Hermes session controls.
3. Test continuing activity, wrong generations, disconnects, cancellation failure, and terminal reconciliation without inference.
4. Assess one bounded live diagnostic after offline checks pass.
5. Require actual admission, matching terminal evidence, and matching server cancellation or completion for live acceptance.

Conditions 1 through 3 passed within their stated fixture limits.
Condition 4 produced a recorded plan and a failed preflight. Condition 5 remains **not run**.
Codex applied the owner's stopping rule to the failed admission preflight. It stopped the live route before launch.

## Admission and preserved state

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
The checkout started clean at the base above. The remote remained `https://github.com/forera-ai/Crewshal.git`.
Both version declarations initially contained `0.27.9`.
All 1,345 tracked files retained their starting hashes before publication edits.
RTK reported `1.0.1`. All five installed Crewshal skill files matched their repository copies.
The Hermes skill exposure resolved to the global Codex installation.

Codex loaded these companion skills:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`.
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`.
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`.

The Crewshal graph generation was `2026-10-25T18:09:12Z`. The evidence tier was Verify.
Coverage reported matching metadata for most selected records. The diagnosis record required direct source fallback.
The Hermes generation remained `2026-09-02T17:14:19Z`.
Its relevant control paths were not tracked by that stale generation. Exact current source supplied the evidence.
Best-effort coverage does not prove completeness. No stale graph snippet supplied a current control claim.
The synthetic Jev check reported probability `0.97`, confidence `0.94`, cost `0`, and latency `251` milliseconds.
Actual total billing remains unknown. This check granted no authority.

The preserved runtime inspector exited 0 at admission.
It confirmed the original 33 artifact hashes, selected profile and SOUL hashes, stored policy, and original terminal admissions.
The profile retained 45 default turns. The original session retained 25 turns and `run_budget_seconds=600`.
The server remained PID `33814`, with Ornith Q4, one slot, and context `93696`.
Provider, model, context, approval controls, fallback settings, and model-server configuration did not change.
Codex reused accepted R1 readiness. It did not repeat successful worker, MCP, or approval probes.

| Preserved attempt | State |
| --- | --- |
| R1 | Accepted readiness; generation 1 remains `terminal/completed`. |
| Refused implementation launch | Exit 2 before inference; no additional admission. |
| Corrected I1 | Generation 2 remains `terminal/interrupted`; no candidate. |
| D1 | New diagnostic plan; schema preflight failed; no session or model request. |

No previous attempt or correction count was reset.

## Private control and offline evidence

Private evidence resides under:
`/Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261025`.
The parent directory has mode `0700`. Evidence files use mode `0600`.
Profile configuration, credential references, exports, and raw logs remain outside this repository.

`deadline_control.py` calculates one deadline from the original monotonic start and finite duration.
Chunks, heartbeat activity, receipt polls, and transport errors cannot replace that deadline.
It submits one `session.interrupt` request with the exact session and admitted execution generation.
It requires the exact admission receipt before reporting terminal state.
An interrupt acknowledgement alone cannot establish termination.
Cancellation and terminal reconciliation share a fixed cleanup allowance.
Failed cancellation or missing terminal evidence preserves an explicit `uncertain` result. The control cannot launch or resubmit work.

The nine fixtures verify:

- Continuing synthetic chunks and heartbeats cannot extend the deadline.
- A wrong-generation request fails without a cancellation retry.
- The actual Hermes authority refuses a wrong generation before cancellation effects.
- A disconnected viewer cannot establish terminal state.
- The actual gateway client reports a closed synthetic socket as an unknown outcome.
- A cancellation failure preserves evidence that survives JSON storage.
- An interrupt acknowledgement without terminal reconciliation remains uncertain.
- An observed terminal completion needs no cancellation.
- A hung receipt wait cannot prevent the deadline from requesting interruption.

These fixtures create no gateway connection or model request.
They establish bounded control behavior, not live gateway or model-server termination.
The real-clock hung-read fixture passed with a 0.2-second observation tolerance. It does not prove real-time scheduling guarantees.

The final saved command ran from the private directory:

```sh
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python -m unittest -v test_deadline_control
```

It exited 0: nine tests passed in `0.113` seconds.
`offline-tests.result.json`, `offline-tests.stdout`, and `offline-tests.stderr` preserve that result.
Earlier development runs passed eight tests, then nine after the hung-read case was added.
All private Python files also passed syntax parsing.

| Private file | SHA-256 |
| --- | --- |
| `deadline_control.py` | `e29564cf30b1f57299d77eb395845a02c0119d783ab604699d790340bf9409f0` |
| `test_deadline_control.py` | `48ef895d9e939322f97d3d6d83a613531857db736a888ffdff6e9b0b1380c1ae` |
| `probe.py` | `6ce5214cb6e925ab9f264d8448f7e808cca6b9bc28e727774106de99fe8bdcb1` |

`evidence-hashes.json` binds ten private evidence files. A digest proves bytes, not authority or truthful origin.

## D1 preflight failure and stopping decision

Offline fixtures cannot prove that gateway cancellation reaches the selected model server.
Codex therefore prepared one read-only D1 plan in `probe-plan.json` before any possible launch.
It records the exact prompt, argv, request identities, session policy, bindings, ceiling, cleanup, and one-worker limit.
The planned command was:

```sh
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261025/probe.py
```

This command was **not run**.
The prompt requests an integer sequence without tools, file edits, implementation, configuration changes, or delegation.
The new session would select the existing provider, model, four skills, and Crewshal directory, with 25 turns.
Its stored run budget would remain 600 seconds.
The independent total deadline was 30 seconds. Terminal collection had a separate 15-second cleanup allowance.
No metered fallback, credential extraction, server restart, or implementation continuation was planned.

The preflight opened `state.db` read-only and inspected `PRAGMA table_info(session_admissions)`.
It incorrectly required `input_id`, `target_session_id`, `admission_id`, and `generation` as database columns.
The assertion exited 1 before any gateway connection or model submission.
The table contains `request_id`; it does not contain `input_id`.
`D1-preflight-failure.json` preserves the actual columns, failed assumption, and stopping decision.
`D1-preflight-command.json` preserves the exact failed argv and diagnostic, copied from the executed tool record without another attempt.
The planned runner also uses that incorrect SQL column. It remains unaccepted and must not be launched unchanged.

This defect came from Codex's unverified query assumption. It does not prove a Hermes runtime regression or changed binding.
Current source supplies the likely repair:

- `gateway/session_controls.py:749-770` maps RPC `input_id` into a `Submission.request_id`.
- `gateway/session_authority.py:406` projects stored `request_id` as a pending receipt's public `input_id`.
- `gateway/session_authority.py:865-892` checks the execution generation before interrupt effects.
- `hermes_cli/gateway_client.py:190-210` reports disconnection without claiming terminal execution.

The next session must test the mapping against an independent offline SQLite fixture before another live assessment.
It must also review cleanup when submission acknowledgement or admission lookup fails after possible acceptance.
A simple SQL substitution alone cannot prove safe recovery.
No `D1-consumed.json` exists. No diagnostic session, admission, stream, or server-cancellation evidence exists.
There was one failed diagnostic preflight and zero live diagnostic attempts.
Two exploratory searches also exited 2 because they named absent source files. They established no pass.

## Closure and next boundary

Checks ran on Darwin `27.2.0`, arm64.
Private runtime fixtures used CPython `3.11.14`. Repository checks used CPython `3.12.15`.
The record-generation interpreter was CPython `3.15.0`.
No product behavior changed. Product source suites, Ruff, mypy, wheel builds, and installed-package checks remain **not run**.
Linux-specific modules remain **deferred** under ADR 0009.

The final publication commands were:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/diagnosis-20261025/inspect_runtime.py
rtk proxy python3 /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261025/verify_closure.py
```

All six commands exited 0. The source import reported `0.27.10`.
The frozen checker reported 23 artifacts and 768 planned units, with both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The closure verifier checked intended paths, preserved historical bytes, links, versions, private hashes, and the absent S1b candidate.
The runtime inspector confirmed unchanged original admissions, selected bindings, and all 33 original evidence hashes.
The private `closure-results.json` preserves exact argv, exits, output, and elapsed times.
Codex reviewed the complete seven-file publication diff and accepted this blocked process checkpoint.
The private live runner remains unaccepted. Its known defect and missing recovery evidence remain explicit.

Only README, CHANGELOG, HANDOFF, synchronized versions, this record, and its continuation prompt enter the checkpoint.
The delivery commit records this blocked boundary. Publication cannot qualify the private live runner or accept S1b work.
Use the [continuation prompt](CREWSHAL-HERMES-DEADLINE-CONTINUATION-2026-10-25.md) to complete this same deadline-control milestone.
The smallest remaining work is verified admission mapping and failure cleanup before one independently bounded live diagnostic.
No owner approval can replace that missing evidence.

All image actions, guests, downloads, Linux tests, campaign execution, calibration, evaluation, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain 10,008,484,533 and 116,542,541 bytes.
Their conservative total remains 10,125,027,074 bytes.
