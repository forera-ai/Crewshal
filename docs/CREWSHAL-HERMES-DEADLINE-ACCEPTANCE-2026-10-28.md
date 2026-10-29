# Private deadline control: bounded D3 acceptance

Observations: 2026-10-28. Publication: 2026-10-29. Package checkpoint: `0.27.14`. Crewshal skill: `1.0.0`.
Base revision: `3bdb459f42290cd07f98c2c9df540d4ede115ac7` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a183f3-c8f9-7a22-9435-29052655dffd`.

## Verdict and stopping boundary

Codex accepts the private deadline-control milestone within the observed D3 scope.
Twenty-one offline fixtures passed. One live diagnostic passed stored-policy verification and reached `terminal/interrupted` after the independent deadline.
The matching model-server log records task cancellation, slot release, and idle capacity.
S1b remains unstarted in this session. Its offline action proposal belongs to the next session.
No product adapter, general orchestration framework, or product behavior changed.

This result establishes one supervised cancellation during prompt processing.
It does not prove automatic enforcement of the stored 600-second budget.
It does not establish live cancellation during generated-token streaming or general runtime conformance.
Offline fixtures establish the immutable deadline under continuing synthetic activity.
The earlier generation overrun, supervisor defects, and failed attempts remain historical evidence.

## Start gate and preservation

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
The checkout started clean at the base above. Both package declarations contained `0.27.13`.
The canonical remote remained `https://github.com/forera-ai/Crewshal.git`. RTK reported `1.1.0`.
All five installed Crewshal skill files matched the repository copies.
The Hermes skill exposure still resolved to that installation.
Codex loaded these companion skills:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`.
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`.
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`.

The synthetic Jev check returned probability `0.97`, confidence `0.94`, reported cost `0`, and latency `250` milliseconds.
That result verifies a decision path only. Actual total billing remains unknown.
Graph evidence used the Verify tier. The private graph record retains exact coverage responses.
Hermes generation `2026-09-02T17:14:19Z` was stale; relevant paths were untracked or had changed metadata.
Codex used current source for the policy, toolset, approval, submission, receipt, and interruption contracts.
The exploratory graph trace was partial and did not support exhaustive claims.
Best-effort graph coverage does not prove completeness.

Both historical manifests matched all 43 entries before private control edits.
All 78 entries in the owner-preparation starting manifest also matched.
The new starting manifests bind 111 existing private files and 1,353 tracked repository files.
All those files retained their hashes before publication edits.
Historical inspectors, observations, controls, manifests, logs, and failed runners remain unchanged.

Read-only observations verified the same selected route, process, context, capacity, and matching load log.
The service used parent PID `44430`, model PID `47505`, and the existing loopback route.
The cached Ornith `UD-Q4_K_XL` model retained context `93696` and one slot.
Hermes source remained clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
The raw-profile hash matched the prior October 28 observation. The older October 25 baseline remains intact.
Selected fields and SOUL matched. Fallback providers remained empty. Full raw-profile history remains unknown.
The multiplexer epoch remained `12`; the profile authority epoch remained `11`. They have separate scopes.
Codex repeated no worker, approval, or MCP connection probe.

## Effective tools and corrected private control

Current `build_policy` calls `_resolve_toolsets`, which calls `_get_platform_tools`.
That resolver adds configured MCP servers and default-enabled plugin toolsets.
An empty requested list therefore reproduced D2's three effective toolsets.
The supported `no_mcp` sentinel suppresses default MCP servers. Alone, it leaves `homeassistant` enabled on the CLI surface.
The existing profile already lists `homeassistant` in `known_plugin_toolsets.acp`.
A new `source=acp` session with `toolsets=["no_mcp"]` therefore supplies a supported per-session selection.
No profile edit was needed. Codex did not select safe mode, ignore user configuration, or bypass project rules.
Single-query approvals remained `deny`; the ACP edit policy remained `ask`.
The selected provider, model, endpoint, stored budget, and server remained unchanged.
The ACP surface differs from the historical CLI implementation surface. This diagnostic does not requalify that implementation surface.

The independent policy fixture uses actual stored D2 policy structure and current resolver code.
Its plugin projection contains observed gateway metadata. A false credential-presence fixture prevents credential discovery.
Those offline inputs cannot prove live tool suppression.
D3 independently checked its actual stored policy before submitting any prompt.
That check confirmed an empty effective toolset, the correct `delegation.orchestrator_enabled` field, and retained controls.

The new private lifecycle retains the acknowledged session identity before post-creation validation.
A failed validation records that identity and permits no prompt submission or cancellation.
The lifecycle starts its monotonic deadline before creation and never extends it for activity.
It permits one submission and targets only the verified admission and generation during cleanup.
Lost acknowledgements, failed lookups, disconnects, failed cancellation, and absent terminal evidence preserve unknown outcomes.

The final offline command ran from `deadline-20261028-tool-gate` under the preserved private S1b root:

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python -m unittest -v test_effective_policy test_diagnostic_control
```

It exited 0: 21 tests passed in `0.265` seconds.
Six new fixtures cover effective policy and creation identity. Fifteen adapted regression fixtures cover lifecycle and SQLite mapping.
The first run exited 1 because the new fixture supplied an in-memory tuple instead of stored JSON's list.
The corrected fixture serializes through JSON. The failed run remains recorded.
The fixtures also retained the runtime's SQLite warning and expected `no_mcp` warning. No update or installation ran.
All new private Python sources passed syntax parsing before D3.

## D3 plan and independent reconciliation

`D3-plan.json` recorded the prompt, exact argv, policy, bindings, one-worker limit, and cleanup before launch.
The prompt requested a synthetic integer sequence without tools, edits, delegation, configuration changes, or approvals.
The runner used the verified existing gateway directly. It could not ensure or restart a gateway.
It selected the four required skills, 25 turns, stored budget `600`, `finite=True`, and `unattended=False`.
The total deadline was 30 seconds. Cleanup had 15 seconds. The independent process ceiling was 55 seconds.
The exact launch command was:

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/deadline-20261028-tool-gate/run_d3.py
```

| Observation | Result |
| --- | --- |
| Actual stored effective toolsets | Empty, verified before submission. |
| Prompt submissions | One. No replay occurred. |
| Admission | Sequence `54`, generation `1`, `terminal/interrupted`. |
| Interruption request | `30.006967` seconds after the original monotonic start. |
| Terminal observation | `30.233026` seconds after that start. |
| Foreground process | Exit 0 after `30.370292` seconds. |
| Server task | The bounded log interval contains one task, `282`. |
| Server cancellation | `cancel task, id_task = 282`. |
| Server release | The same task stopped processing; the slot became idle. |
| Release delay | `3.246341` seconds between the server cancellation and release log entries. |
| Tool calls | Zero in the retained session counters and observed turn. |

The first server extract ended before its cancellation entries arrived.
Codex preserved that extract and captured a later reconciliation suffix without replacing it.
The later read observed release after the client had exited.
Server task association uses the sole request in the bounded interval, selected route, and one-slot configuration.
The server log contains no direct admission identifier. Codex did not independently synchronize the two log clocks.
The release delay is a server-log interval, separate from supervisor monotonic timing.

The model was still processing prompt tokens when interruption occurred.
Its last preserved processing count was 6,144 prompt tokens. That count is not generated output or final usage.
The agent log reports one API call and zero tool turns.
The session database's API and token counters remain zero after interruption.
Those zero counters do not mean no request occurred or establish zero usage. Final usage and actual billing remain unknown.

The independent `verify_live.py` command exited 0.
It checked actual SQLite admission identity, preserved R1 and I1 outcomes, D2's empty session, policy bindings, and saved server evidence.
The new `D3-review.json` binds Codex's verdict to the exact private candidate and evidence.
R1, the refused launch, corrected I1, D1, and D2 remain preserved. No count was reset.
No additional diagnostic, implementation continuation, session deletion, or unrelated cancellation ran.

## Publication checks and next boundary

Private records, complete policies, credential references, source captures, and raw logs remain outside Git.
The evidence directory is `deadline-20261028-tool-gate` under the preserved private S1b root.
Its closure record retains exact argv, exits, environment, publication diff identity, and preservation results.
The publication checks are:

```sh
rtk proxy git diff --check
rtk proxy git diff --cached --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
```

All four commands exited 0. The private live verifier and publication verifier also exited 0.
The frozen checker retained digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0` and both execution flags false.
Codex reviewed the complete seven-file publication diff and accepted this bounded process checkpoint.
Repository checks used Darwin `27.2.0`, arm64, and CPython `3.12.16`.
Private runtime fixtures used CPython `3.11.14` on the same host.
Product suites, Ruff, mypy, wheel builds, and installed-package checks remain **not run** for this process checkpoint.
Linux-specific checks remain **deferred** under ADR 0009.

Use the [next-session prompt](CREWSHAL-S1B-AFTER-DEADLINE-NEXT-SESSION-2026-10-28.md) for the offline S1b action proposal.
That session must verify current bindings and its implementation-specific deadline plan before source dispatch.
It must preserve the original attempt ledger and review any candidate independently.
This session stops after publication. No image action, guest action, download, Linux test, evaluation, deployment, or release ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical charges remain 10,008,484,533 archive bytes and 116,542,541 package bytes; their total remains 10,125,027,074 bytes.
