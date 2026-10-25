# Hermes continuation runtime diagnosis

Date: 2026-10-25. Package checkpoint: `0.27.9`. Crewshal skill: `1.0.0`.
Base revision: `42357d48d839af77199a6fe8eb34a534b5d36fc8` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a17439-55b0-73e3-a3f7-be1631a57e1c`.

## Verdict and acceptance boundary

The read-only runtime diagnosis is complete. The S1b proposal and implementation dispatch remain blocked.
The stored session policy contains a 600-second run budget and a 25-turn limit.
That budget does not establish a hard deadline for a continuing local model stream.
The observed continuation exceeded 600 seconds and ended through Codex's explicit interruption.

The diagnosis required these checks:

1. Verify the supervisor, checkout, preserved attempts, and relevant runtime bindings.
2. Inspect saved argv, events, complete exports, and stored admission policy.
3. Separate stored policy, source behavior, observed inference, and actual termination.
4. Preserve private evidence and prepare an exact continuation prompt.

Codex performed no new worker request, inference request, model change, profile change, or runtime repair.
This checkpoint accepts the diagnosis record only. It cannot accept the absent S1b draft or deadline control.
Changed paths are `README.md`, `CHANGELOG.md`, `docs/HANDOFF.md`, `pyproject.toml`, and `src/crewshal/__init__.py`.
The two new paths are this diagnosis record and `docs/CREWSHAL-HERMES-DEADLINE-NEXT-SESSION-2026-10-25.md`.

## Starting state and reused readiness

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
The branch used the canonical `https://github.com/forera-ai/Crewshal.git` remote.
HEAD matched the base above. Status, staged changes, and unstaged changes were empty before publication edits.
Both package declarations contained `0.27.8` at admission.
RTK reported `1.0.1`.
The five installed Crewshal skill files matched their repository copies.

Codex loaded these companion files:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`

The Crewshal graph generation was `2026-10-25T12:58:18Z`.
The inspected existing project records had matching metadata without recorded gaps at session admission.
This best-effort report does not prove complete indexing.
The synthetic Jev check reported probability `0.98`, confidence `0.96`, `cost_usd: 0`, and latency `357` milliseconds.
Actual total billing remains unknown.

The accepted R1 readiness remains recorded in the [blocked checkpoint](CREWSHAL-S1B-BLOCKED-2026-10-25.md).
Codex reused that evidence. It did not repeat the worker's complete document reads, MCP probes, or approval probes.
It parsed the full saved exports for this diagnosis instead of relying on shortened stream events.

## Runtime bindings

The model server remained PID `33814`, started at local time `13:11:09` on October 25.
Its command still selected Ornith `UD-Q4_K_XL`, port `63421`, one slot, and context `93696`.
The selected Ornith provider metadata also contained context `93696`.
The profile retained pruning at `48000` tokens and compression threshold `70000` tokens.
The SOUL remained present in the saved effective readiness prompt.
Its current SHA-256 was `911c6d5cc08c050429c96e8c8f6bd5f11c000e10a6ab93650b06e7b5631e7177`.
The current profile SHA-256 was `aa0b2326acfe4b24494183a79e859a0330501a0bbfdedb6521543ab801ebd1c6`.
These hashes identify bytes. They do not prove deadline enforcement.

| Field | Current profile | Stored session policy | Meaning |
| --- | --- | --- | --- |
| Model | `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` | Same | The selected model remains unchanged. |
| Provider | `unsloth` | `custom:unsloth` | The stored route contains the normalized custom provider. |
| Endpoint | `http://127.0.0.1:8888/v1` | Same | The configured loopback route remains unchanged. |
| Run budget | `600` seconds | `600` seconds | The stored budget is now directly observed. |
| Turn limit | `45` | `25` | Creation pinned 25 turns; resume retains that limit. |
| Single-query approvals | `deny` | `deny` | No approval mode changed. |
| Fallback providers | Empty | Empty | No fallback provider was added. |
| Nested orchestration | Disabled | Disabled | No child worker was launched. |
| Gateway timeout | `1800` seconds | `1800` seconds | Source treats this value as inactivity time. |
| Gateway warning | `900` seconds | `900` seconds | A warning value is not a total runtime deadline. |

The backup taken before R1 contains a 300-second budget. The current profile and stored R1 policy contain 600 seconds.
That difference matches the prior session's recorded budget preparation. This diagnosis changed none of those files.
The profile's 45 turns and the session's 25 turns are separate values, not a new runtime change.

## Direct stored policy and admission evidence

Session: `local-9874572c1e54092333526ee56990bc614cd0e98ffe4c64a9592573aa84978e83`.
Codex opened the profile's `state.db` with SQLite `mode=ro`.
It selected only this session's creation receipt and admission rows.
It inspected `state_meta` key `gateway.local_policy.v1:<session-id>`.
The receipt's `policy.config_json.agent` contains `run_budget_seconds: 600` and `max_turns: 25`.
The stored request selects the four required skills, provider, model, and Crewshal directory.
It contains no `follow_profile_config` selection or adopted-follow marker.

The stored policy therefore resolves to 600 seconds through the inspected budget getter.
No live agent-memory dump was available after termination. Source wiring cannot replace that missing observation.
The supported resume check compares supplied flags with the stored launch request.
It does not replace the session budget with the profile's later defaults.

| Admission | Generation | Status | Outcome |
| --- | ---: | --- | --- |
| Sequence 51 | 1 | `terminal` | `completed` |
| Sequence 52 | 2 | `terminal` | `interrupted` |

The first refused implementation launch created no additional admission.
Both original admissions remained terminal during this diagnosis.
No credential reference was resolved. No credential store, key file, or process environment was extracted.

## Source findings and limits

The installed Hermes checkout was clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
The relevant source hashes are saved privately with the diagnosis.
The Hermes graph generation was `2026-09-02T17:14:19Z`, which was stale for these paths.
Two graph snippets returned obsolete line ranges. Codex rejected those snippets as current evidence.
Coverage marked relevant files `metadata_changed` or `not_tracked`.
Codex used exact local source and literal searches for the runtime findings below.
Coverage scope pagination completed for `agent` and `gateway`; excluded caches and unrelated assets remained outside the diagnosis.
No graph reindex or runtime restart ran.

Paths below are relative to the installed Hermes checkout:

| Source | Inspected behavior |
| --- | --- |
| `hermes_state_local.py:7-75` | The creation transaction stores the policy receipt separately from transcript exports. |
| `gateway/session_policy.py:128-248,320-336` | The budget getter reads the stored policy configuration. |
| `hermes_cli/gateway_chat.py:297-321` | Resume refuses changed creation flags. |
| `gateway/session_execution.py:178-188` | Agent construction receives the policy budget. This is wiring evidence only. |
| `agent/agent_init.py:324-332,706-713,1402-1405` | A positive budget becomes a float; configuration supplies a constructor fallback. |
| `agent/turn_context.py:657-661` | Each conversation turn starts its own budget clock. |
| `agent/conversation_loop.py:75-80,124-156` | At 80 percent, the helper appends one instruction to an eligible tool result. |
| `agent/turn_iteration_prep.py:183-186` and `agent/tool_executor.py:200-209` | Iteration and tool-result boundaries call the notice helper. |
| `agent/chat_completion_helpers.py:634-646,678-700,3882-3894` | Local streams use separate stale timing; the local branch returns before the cloud run-budget cap. |
| `agent/chat_completion_helpers.py:2858-2878` | Received chunks and prompt progress refresh request liveness. |
| `agent/chat_completion_stream_monitor.py:85-142` | The monitor checks stale time and interruption; heartbeats also refresh gateway activity. |
| `gateway/run_turn.py:1479-1541` and `gateway/run.py:2731-2763` | The gateway watchdog measures inactivity, not total elapsed time. |
| `gateway/run_watchers.py:232-249` | The session stall watcher only notifies. |

For 600 seconds, the notice threshold is 480 seconds.
The notice asks the model to finish. It does not interrupt an active request at that threshold.
It also requires an eligible tool-result tail. The blocked continuation completed no new tool call.
The source resets the clock per conversation turn; it does not impose a cumulative session deadline.

The local stale default is 900 seconds without an explicit configuration or environment override.
That timer measures silence since a chunk, not total request duration.
Continuing generation can refresh it repeatedly. A stale kill can also enter request retry handling.
Neither the stale default nor the 1800-second inactivity setting establishes a 600-second total deadline.
Historical process environment overrides remain unknown. The diagnosis does not claim an observed 900-second enforced cutoff.
The separate nonstreaming local path also returns infinite stale patience when it uses implicit defaults (`run_agent.py:563-588`).
That source finding describes another path. The interrupted continuation used streaming.

## Observed inference and actual termination

Saved argv confirms the refused launch requested 45 turns, then the corrected launch requested 25 turns.
The refused launch exited 2 after `1.066` seconds and reported zero tokens.
The corrected launch produced only its initialization event and interrupted result in the saved CLI stream.
Its runner exited 130 after `623.226` seconds.
The result reported `622306` milliseconds and `Operation interrupted: waiting for model response (622.1s elapsed).`

The complete readiness export contains 37 message records. The interrupted export contains 39.
Only user message `4884` and interruption placeholder `4885` follow the completed readiness transcript.
Neither contains a new tool call. The proposed S1b draft remains absent.
The export's placeholder is not a model deliverable.

The matching model-server log records task `10047` with a 61,502-token prompt and a 93,696-token slot.
Prompt processing took approximately 4.31 seconds for 1,457 new tokens after cache reuse.
Generation continued throughout the wait. The last pre-cancellation sample reports `n_gen = 16770` at approximately `27.36 t/s`.
The log then records `cancel task, id_task = 10047`, slot release, and all slots idle.
This establishes active server generation. It does not establish useful reasoning, completed output, or a correct candidate.
The generation sample is not final usage accounting or a billing record.

The agent log records one API call in the continuation and `interrupted_during_api_call` after explicit stop.
Thus, a long active request explains the absence of completed tool work without proving a hung server.
The observed failure is the missing deliverable and missing independently enforced total deadline.
The cancellation path worked in this single observation. Natural budget termination remains unproved.

## Preserved attempts and private evidence

The prior finite ledger remains unchanged:

| Attempt | Preserved result |
| --- | --- |
| R1 | Accepted readiness; exit 0 after 470.739 seconds. |
| Implementation launch 1 | Resume-policy refusal before inference; exit 2. |
| Corrected implementation I1 | No candidate or tool call; explicit interruption; exit 130 after 623.226 seconds. |

This diagnosis adds zero worker attempts and zero local model requests.
No correction count or prior failure was reset.
The original 33 evidence files remain byte-identical to the diagnosis manifest.
Private evidence remains under `/Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3`.
The new `diagnosis-20261025` directory contains the inspector, selected policy evidence, source hashes, and bounded log extracts.
It also contains `prior-artifact-hashes.json`, which preserves the original evidence identities.
No raw private log, profile configuration, or complete export enters this repository.

The reproducible diagnosis command is:

```sh
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/diagnosis-20261025/inspect_runtime.py
```

It exited 0 and verified budget 600, limit 25, terminal admissions, and preserved artifact hashes.
Repeated execution compares the same selected bindings with the saved evidence.
The first comparison rerun exited 1 because Python admission tuples differed from persisted JSON arrays.
Codex normalized the comparison to JSON types. The corrected rerun exited 0 without changing the saved runtime evidence.
Some exploratory searches named absent source files and exited 2. They established no pass.
Exact source discovery resolved those paths. No required runtime service or approval control failed during this diagnosis.

## Publication checks and next boundary

No product source suite, Ruff, mypy, wheel build, or installed-package check is required for this diagnosis-only checkpoint.
Those checks remain **not run**. Linux-specific modules remain **deferred**, not passing.
The frozen-package check, source version import, evidence-preservation check, documentation checks, and whitespace check are required.

Codex ran these commands against the publication tree:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
rtk proxy /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/diagnosis-20261025/inspect_runtime.py
rtk proxy python3 /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/diagnosis-20261025/verify_closure.py
```

All six final commands exited 0.
The source import reported `0.27.9` on Darwin `27.2.0`, arm64, with CPython `3.12.15`.
The frozen checker reported 23 artifacts and 768 planned units, with both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The closure verifier checked seven intended paths, synchronized versions, preserved historical suffixes, local links, and the absent S1b candidate.
The runtime inspector confirmed unchanged selected bindings, terminal admissions, and all 33 original artifact hashes.
Codex reviewed the complete seven-file publication diff. The final review result was `NO FINDINGS`.
Codex accepted this coherent diagnosis checkpoint. The acceptance grants no implementation dispatch or runtime qualification.

The next milestone must establish an independent total deadline before another implementation request.
It must first use deterministic offline fixtures to prove interruption and terminal reconciliation despite continuing activity.
Any later live proof must remain read-only, use one bounded worker, preserve this ledger, and verify actual termination.
Changing a configuration value, adding a timer in source, or observing a client exit alone cannot pass that gate.
The [continuation prompt](CREWSHAL-HERMES-DEADLINE-NEXT-SESSION-2026-10-25.md) defines that bounded work.

All real image actions, guests, downloads, Linux tests, campaign execution, evaluation, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain 10,008,484,533 and 116,542,541 bytes.
Their conservative total remains 10,125,027,074 bytes.
