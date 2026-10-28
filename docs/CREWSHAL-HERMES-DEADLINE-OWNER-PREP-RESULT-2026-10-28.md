# Hermes preparation verified; D2 stopped before submission

Date: 2026-10-28. Package checkpoint: `0.27.13`. Crewshal skill: `1.0.0`.
Base revision: `664677379d3fb164223d5e140c0879ebc5149770` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a183da-4e97-7d70-91a0-bae077e109fb`.

## Verdict and boundary

The same private deadline-control milestone remains **blocked**. S1b remains closed.
Owner preparation now supplies a matching selected model service.
Twenty-four offline fixtures pass, including an independent SQLite admission-mapping fixture.
The new D2 diagnostic stopped after session creation and before prompt submission.
Its stored toolsets did not meet the recorded empty-toolset gate.
The supervisor also checked the orchestration setting in the wrong configuration section.
No live deadline or model-server termination proof exists.
Codex accepts the preparation evidence, bounded fixtures, findings, and this documentation checkpoint only.
The private runner remains unaccepted for live use.

The unchanged acceptance conditions require verified runtime bindings, admission mapping, failure cleanup, and actual live termination evidence.
Preparation and offline control evidence cannot replace the final condition.
The earlier [reconciliation](CREWSHAL-HERMES-DEADLINE-RECONCILIATION-2026-10-28.md) remains a correct historical absence observation.
Codex did not rerun or weaken its expected-absence assertion.

## Start gate and preservation

Trusted local `turn_context` metadata identified this supervisor as `gpt-6.1-sol`.
The checkout started clean at the base above, with both version declarations at `0.27.12`.
The canonical remote remained `https://github.com/forera-ai/Crewshal.git`. RTK reported `1.1.0`.
All five installed Crewshal skill files matched their repository copies.
The Hermes exposure still resolved to the installed Crewshal skill.
Codex read the three required companion skills from the same paths recorded by the prior reconciliation.
The synthetic Jev check returned probability `0.03`, confidence `0.94`, reported cost `0`, and latency `228` milliseconds.
It verified a decision path only. Actual total billing remains unknown.

Graph evidence used the Verify tier.
Crewshal coverage generation was `2026-10-28T17:20:21Z`.
The 23 selected existing repository paths had matching metadata without recorded gaps before publication edits.
Hermes coverage remained stale at `2026-09-02T17:14:19Z`.
Relevant control paths were `not_tracked`; other selected sources had changed metadata.
Codex used current local source for material control findings.
Best-effort graph coverage does not prove completeness.

Both historical manifests matched all 43 entries before new private files were written.
The new starting manifests bind all 78 existing private files and all 1,351 tracked repository files.
The 70 files bound by the earlier reconciliation also retained their hashes.
Old inspectors, observations, manifests, controls, plans, and logs remain unchanged.
New controls and evidence reside in `deadline-20261028-owner-prep` under the preserved private S1b root.
Profile configuration, credential references, raw logs, complete exports, and private controls stay outside Git.

## Current service and profile reconciliation

| Binding | Read-only evidence |
| --- | --- |
| Selected route | PID `44430` listens on `127.0.0.1:8888`. |
| Model backend | Its child PID `47505` listens on `127.0.0.1:59988`. |
| Model | Process arguments and the matching load log select cached Ornith `UD-Q4_K_XL`. |
| Context | Process arguments, load log, and selected profile metadata specify `93696` tokens. |
| Capacity | Process arguments and the load log specify one slot. |
| Route association | The current parent startup log links port `8888` to the matching port-`59988` model log. |
| Transport | Both one-second loopback connections succeeded and sent zero application bytes. |
| Hermes source | Clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`; all 15 saved diagnosis source hashes matched. |
| Gateway | Credential-free discovery found the existing ready owner with the expected source revision. |

The owner-prepared process replaces the historical PID and backend port. Neither historical identity was required for reuse.
The matching load log is `llama-1793213221-port-59988-try0.log`.
No server start, restart, model selection, download, credential extraction, or profile edit ran in this session.

The profile hash remains `daf8f597b75b319cd19104753f7b64cda0d66dd0fd9fe44e26c77314554be412`.
It matches the earlier October 28 observation, not the October 25 raw-profile baseline.
All saved selected diagnosis fields and the SOUL hash matched. Fallback providers remained empty.

Static review found these relevant differences from the stored effective R1 policy:

- The added `better-session-appearance` Python entry point returns without registering behavior.
- Its complete desktop JavaScript adds session colors and idle glyphs through the desktop SDK.
- `voice.record_key` selects `ctrl+b`; current source uses it for the interactive recording shortcut.
- The 45-turn profile default and stored 25-turn limit reflect the preserved creation override.
- Current source normalizes provider spelling and removes secret fields from stored policies.

The plugin review executed neither plugin entry point.
These presentation changes do not expand authority for the planned RPC diagnostic.
Their source review does not qualify general plugin containment or reconstruct historical raw-profile bytes.
The full raw-profile change history remains unknown. The old baseline remains intact.
Codex reused R1 only for unchanged instruction and MCP evidence. It repeated no worker or approval probe.

The gateway multiplexer reports epoch `12`; the Crewshal profile authority reports epoch `11`.
Current source gives these values different scopes. D2 bound both identities separately.
Their difference does not establish a runtime failure.

## Private offline control and source findings

The independent fixture uses a temporary `SessionDB` and current submission and admission functions.
It proves RPC `input_id` becomes `Submission.request_id` and persists in SQLite column `request_id`.
It verifies exact session and request matching. The table has no `input_id` column.

The new private control permits one creation call and one prompt submission.
It starts one monotonic total deadline before creation. Activity cannot extend that deadline.
It reconciles a lost submission acknowledgement through the owned admission without replay.
It can use an acknowledged receipt when a database lookup fails.
Cleanup uses an already verified identity before a hung read can consume the cleanup interval.
It handles queued cancellation and a queued-to-started race with exact admission and generation checks.
Unknown identity, failed cancellation, disconnect, or absent terminal evidence remains explicit.
It never cancels a successor generation or infers termination from an acknowledgement.
The runner permits one control-only reconnection to the same existing gateway. It cannot ensure or restart a gateway.

Source review found that the old runner's `unattended=True` requests automatic approval behavior.
The revised submission uses `finite=True` and `unattended=False` to retain single-query approval controls.
The old `probe.py` remains unchanged and was never launched.

The final offline command ran from the new private directory:

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python -m unittest -v test_diagnostic_control test_deadline_control
```

It exited 0: 24 tests passed in `0.309` seconds.
Fifteen new fixtures and nine preserved fixture copies supplied that result.
The tests created no service connection or model request.
SQLite reported its existing WAL-reset warning and selected DELETE journal mode for the temporary database.
No runtime update or installation ran. The warning is preserved in the private result.
All saved private Python files passed syntax parsing before D2.
Offline acceptance covers tested control behavior. It does not accept every live runner precheck.

## D2 plan, failure, and reconciliation

`D2-plan.json` records the revised prompt, exact argv, hashes, policy, one-worker limit, and cleanup before execution.
The plan selected the verified provider, model, context, server, four skills, and 25-turn limit.
Its independent total deadline was 30 seconds, with 15 seconds for cleanup and a separate 55-second process ceiling.
It requested `toolsets=[]` and retained approval mode `deny`.
The outer command was:

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-owner-prep/run_d2.py
```

The process exited 0 after `0.498` seconds. Its result was `uncertain/creation_outcome_unknown`, not success.
The gateway created one session. The supervisor's stored-policy precheck then raised `AssertionError`.
No prompt submission followed that assertion.

The saved policy exposed two failed assumptions:

1. The runner checked `agent.orchestrator_enabled`. The actual setting is `delegation.orchestrator_enabled`, which remained false.
2. The empty requested toolset list resolved to `codebase-memory-mcp`, `homeassistant`, and `jev`.

The first assertion short-circuited before evaluating the toolset comparison.
Direct stored-policy inspection independently establishes the second failed gate.
The runner did not prove disabled tools. Its passing lifecycle fixtures did not test this effective-policy resolution.
Current `_resolve_toolsets` calls `_get_platform_tools`, which also folds in enabled plugin and MCP toolsets.
This source behavior explains the observation. The record establishes no Hermes regression.
The failed policy precheck prevented prompt submission. Its orchestration assertion failed before the empty-toolset comparison ran.

The initial control result lost the known session identity when validation failed inside the creation wrapper.
`D2-created.json` retained that identity. Independent SQLite reconciliation recovered the exact empty session.
It remained at generation `0`, with no admissions, messages, tool calls, API calls, or tokens.
The captured server-log suffix contained zero bytes. No model task or cancellation was observed.
The session and consumed D2 intent remain preserved. No session deletion, cancellation, or replay ran.

A later read-only reconciliation query incorrectly selected nonexistent column `runtime_state` and exited 1.
Codex inspected `PRAGMA table_info(sessions)` and corrected only that observation query.
The successful reconciliation uses actual columns and records the failed query separately.
This supervisor query error did not create an admission or change the failed D2 result.

| Attempt | Preserved state |
| --- | --- |
| R1 | Original generation 1 remains `terminal/completed`. |
| Refused implementation launch | Preserved refusal; no additional admission. |
| Corrected I1 | Original generation 2 remains `terminal/interrupted`. |
| D1 | Historical schema preflight failed; no session, admission, or consumed intent. |
| D2 | One empty session and consumed intent; failed policy precheck; zero prompt submissions or model requests. |

No attempt count was reset. No second D2 creation or submission ran.
Codex stopped the route after the failed tool binding.
The post-D2 verdict supersedes the earlier offline permission to attempt this diagnostic.
No live deadline acceptance follows from process exit, fixtures, empty-session reconciliation, or publication.

## Closure and next inputs

Private files preserve the preparation observation, offline results, plan, effective policy, control result, reconciliation, and post-D2 review.
The private `closure-results.json` records exact publication argv, exits, outputs, environment, and preservation checks.
The whitespace checks, frozen checker, version import, and private closure verifier all exited 0.
The verifier checked seven intended paths, 1,346 unchanged tracked files, historical suffixes, links, and synchronized versions.
It also verified all 78 starting private files, all 43 historical manifest entries, and D2's empty session.
The frozen checker reported 23 artifacts, 768 planned units, and both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The exact closure commands were:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
rtk proxy python3 /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-owner-prep/verify_closure.py
```

Codex reviewed the complete seven-file publication diff and accepted this new blocked process checkpoint.
That verdict does not accept the private runner or establish live termination.
Repository checks use local Darwin `27.2.0`, arm64, with CPython `3.12.16`.
Private runtime checks use CPython `3.11.14` on the same host.
Product suites, Ruff, mypy, wheel builds, and installed-package checks remain **not run** for this process checkpoint.
Linux checks remain **deferred** under ADR 0009.

The [next prompt](CREWSHAL-HERMES-DEADLINE-TOOL-GATE-NEXT-SESSION-2026-10-28.md) continues the same milestone.
It first requires an offline effective-policy fixture and a supported way to suppress diagnostic tools.
It must also correct the orchestration field and preserve known creation identity when a post-creation check fails.
It must not replay D2 or run either preserved probe unchanged.
Any required profile decision needs exact bindings, effects, limits, and cleanup before an owner request.
The current prompt grants no profile edit or server operation.

All image actions, guests, downloads, Linux tests, campaigns, evaluation, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical charges remain 10,008,484,533 archive bytes and 116,542,541 package bytes.
Their conservative total remains 10,125,027,074 bytes.
