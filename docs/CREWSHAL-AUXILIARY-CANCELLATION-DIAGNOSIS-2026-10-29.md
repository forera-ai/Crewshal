# Auxiliary cancellation: diagnosis and bounded repair proposal

Date: 2026-10-29. Package checkpoint: `0.27.16`. Crewshal skill: `1.0.0`.
Base revision: `37b2d72777a3efbd049e63f0a91b9f649b9cb5ae` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a187e3-5537-7ba2-b373-834e195675fe`.

## Verdict and scope

Codex accepts the read-only diagnosis milestone.
Current source explains a cancellation gap between the protected auxiliary-call owner and its provider thread.
The private supervisor also accepts terminal admission status before it establishes auxiliary termination.
The proposed repair and offline cases below remain unimplemented and unqualified.
No new model request, worker creation, worker resume, diagnostic prompt, or historical runner execution occurred.

The [S1b rejection](CREWSHAL-S1B-BLOCKED-2026-10-29.md) remains unchanged.
I1, I2, and I3 exhausted the implementation budget. No count was reset.
[D3 acceptance](CREWSHAL-HERMES-DEADLINE-ACCEPTANCE-2026-10-28.md) still covers its recorded prompt-processing case only.
This checkpoint changes process records and synchronized package versions only.

## Start gate and preservation

Trusted local `turn_context.model` identified the supervisor as `gpt-6.1-sol`.
The checkout started clean at the base revision. Both package declarations contained `0.27.15`.
The remote remained `https://github.com/forera-ai/Crewshal.git`.
RTK reported `1.1.0`. All five installed Crewshal files matched their repository copies.
The Hermes skill exposure resolved to the same global installation.
Codex loaded the required `codebase-memory`, `caveman`, and `jev` skills from their previously recorded paths.
The synthetic Jev check returned probability `0.97`, confidence `0.94`, reported cost `0`, and latency `320` milliseconds.
Actual total billing remains unknown. Jev supplied no acceptance or execution authority.

Eight preserved manifest sets matched before diagnosis.
Their entry counts were `33`, `10`, `78`, `111`, `37`, `149`, `37`, and `83`.
The new starting manifests captured 233 existing private files and 1,357 tracked repository files.
The rejected 39,288-byte candidate retained this SHA-256:
`f06318c540ed8ecbca092e59f140d49dea921cadef89173352741bd6cef6208c`.
Its compilation, digest, identity, cleanup, and filesystem-isolation defects remain recorded failures.
Codex neither repaired nor executed the saved harness.

Graph discovery used Verify evidence and completed both pages of the selected one-hop compaction trace.
Crewshal coverage generation was `2026-10-29T13:31:17Z`.
The 11 selected repository paths had matching metadata without recorded gaps.
Hermes generation `2026-09-02T17:14:19Z` remained stale.
Its 15 selected paths had changed metadata or were untracked.
One graph snippet returned unavailable source and obsolete locations.
Codex used exact current source for material findings and saved its hashes and read ranges privately.
Graph relationships supplied orientation only. No recorded coverage gap does not prove completeness.

## Current read-only observation

Hermes source remained clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
All source hashes from the earlier diagnosis matched.
The raw profile, SOUL, selected settings, and stored I3 policy retained their hashes.
The older raw-profile history remains unknown. Fallback providers remained empty.

The existing route retained port `8888`, parent PID `44430`, and model PID `37533` at backend port `63340`.
Process arguments and matching load evidence selected Ornith `UD-Q4_K_XL`, context `93696`, and one slot.
Listener observations matched those processes.
Gateway discovery reported the existing ready instance.
The only observation RPC was `runtime.describe`; it verified multiplexer epoch `12` and profile authority epoch `11` separately.
No service-start or ensure path ran.

SQLite observation used `mode=ro` and `PRAGMA query_only=ON`.
The original worker retained these admissions:

| Sequence | Generation | Status | Outcome |
| --- | ---: | --- | --- |
| 51 | 1 | `terminal` | `completed` |
| 52 | 2 | `terminal` | `interrupted` |
| 55 | 3 | `terminal` | `interrupted` |
| 56 | 4 | `terminal` | `interrupted` |

The database reported zero queued or started admissions at observation.
The current server-log tail reported idle slots.
These are bounded observations. They do not prove cancellation of the earlier auxiliary task.
A new agent-log suffix contained connection records and no additional compaction outcome.
No successful worker, approval, or MCP connection probe was repeated.

## Ownership and cancellation path

Paths in this section are relative to the inspected Hermes source checkout.
The private source record binds each range to its complete file hash.

| Lifetime | Owner and current source | What termination establishes |
| --- | --- | --- |
| Admission | `gateway/session_controls.py:827-830` selects interruption; `gateway/session_authority.py:865-895` checks the generation and requests a hard stop. | Terminal status describes the admitted turn. It does not describe every provider request. |
| Foreground client | The private `run_implementation.py` waits for `diagnostic_control.py`; `outer.py` limits that client process. | Client exit establishes that the foreground supervisor returned. The existing gateway remains a separate process. |
| Compaction owner | `agent/compression_facade.py:226-324` publishes a commit fence; `agent/conversation_compression.py:2949-3005` supplies cancellation to the summary call. | The fence prevents a cancelled summary from committing session changes. |
| Provider thread | `agent/auxiliary_client.py:446-505` creates `hermes-protected-aux-provider` as a daemon. | The owner can raise `AuxiliaryExplicitCancellation` while the provider callback remains active. |
| Chat stream | `agent/auxiliary_client.py:7095-7170` creates and consumes the stream; `agent/auxiliary_stream_watchdog.py:171-192` drives its iterator. | Transport closure requires the provider consumer to unwind and close its own stream. |
| Model-server task | The selected model server owns task `14181` and its slot. | Its release record establishes slot release within the retained server interval. |

The hard stop reached the agent.
`agent/interrupt_control.py:163-265` sets the hard-cancel event and cancels pending commit admission.
The retained I3 agent log records `Interrupt requested (hard): explicit stop requested`.
It then records aborted compaction with `failure_class="explicit_interrupt"` and an interrupted turn.
Thus, the evidence does not support a missing gateway stop as the primary explanation.

`ContextCompressor._call_summary_llm` enters nested interrupt protection at `agent/context_compressor.py:3828-3831`.
That nested scope retains the cancellation source installed by `_run_summary_dispatch`.
`_relay_sync_completion`, at `agent/auxiliary_client.py:2630-2663`, runs the provider callback through the protected-call wrapper.
The wrapper captures the cancellation source, hooks, and host compression deadline before it starts the provider thread.
Its owner polls cancellation every `0.02` seconds and raises without joining that thread or closing its stream.
This behavior is explicit in the current implementation.

The chat-stream accumulator checks elapsed time and the host compression deadline at `agent/auxiliary_client.py:7197-7210`.
It does not consult the captured hard-cancel decision there.
The chat watchdog observes silence and shuts down an attempt-owned socket when its progress timer expires.
It does not connect hard cancellation to that socket in the inspected consumer path.
Continuous generation can therefore keep the silence timer active after the protected-call owner returns.
The normal `finally` closes the stream only when that consumer unwinds.
The Codex Responses guard has different cancellation handling; it does not qualify this local chat-completions path.

The compression deadline also differs from the external task deadline.
`agent/conversation_compression_deadline.py:25-82` derives compression limits and permits prompt-reading extensions.
`CompressionCommitFence.cancel_before_commit`, at `agent/conversation_compression.py:558-565`, cancels commit admission without replacing its deadline.
Neither mechanism binds every provider lifetime to the private runner's original monotonic deadline.
Increasing a profile timeout or waiting for natural completion cannot repair this contract.

The private lifecycle returns immediately on terminal admission in three branches of `diagnostic_control.py`.
The runner then saves bounded log extracts and exits.
Its outer process ceiling ceases to supervise once that client exits.
The old fixtures model admission reconciliation but contain no independent auxiliary transport or server lifetime.
Their historical passes therefore do not test this gap.

## Historical observation and limits

| I3 observation | Preserved result |
| --- | --- |
| Original limits | Total `600` seconds; cleanup `15` seconds; separate client ceiling `630` seconds. |
| Foreground process | Exit 0 after `456.715376` seconds, with terminal/interrupted admission. |
| Later supervisor observation | Task `14181` still generated at `635.708800` seconds from the original monotonic start. |
| Final reconciliation | Captured release and idle capacity at an observation time of `819.679392` seconds. |
| Cancellation record | No cancellation line for task `14181` appeared in the retained server interval. |

The final observation time is not the server release time.
The two clocks were not independently synchronized.
The server log contains no direct admission identifier.
Association uses the bounded request interval, selected route, one slot, and retained compaction events.
No live thread or socket instrumentation identified the specific provider thread during I3.
Current source explains the observed gap; that attribution remains an inference from source and retained observations.
The exact cause of eventual server release remains unknown.
No new cancellation proof ran in this milestone.

## Bounded repair proposal — not implemented

The repair needs both request termination and independent supervision of termination.
A private wrapper that only waits longer can detect failure but cannot supply the missing transport operation.

1. Keep new supervisor controls in a new private directory. Preserve every historical control and observation.
2. Record gateway terminal status, client exit, auxiliary transport closure, and server release as separate facts.
3. Retain supervision after terminal admission or foreground exit until owned transport termination is reconciled.
4. Keep the original `T0 + 600` deadline. Progress and prompt reading must not extend it.
5. For an early explicit stop, cap cleanup at `min(stop_at, T0 + 600) + 15`.
6. Preserve the independent client ceiling. Its expiry must record unresolved termination, never success.
7. Bind cancellation to the gateway instance, profile epoch, session, admission, generation, and individual auxiliary attempt.
8. Provide an attempt-owned cancellation operation before dispatch, during response creation, and during blocked stream reads.
9. Use request-owned transport shutdown and owner-thread closure. Preserve shared clients and unrelated requests.
10. Prevent late cleanup from closing a socket that a later request has acquired.
11. Preserve commit fencing. Cancellation must prohibit retries, fallback requests, and late transcript mutation.
12. Refuse inference when the exact transport cannot supply these controls. Record unresolved effects without replay.

The candidate runtime scope is the protected auxiliary-call wrapper, chat-stream watchdog, and their focused tests.
Those paths reside outside Crewshal product source.
Private lifecycle, runner, and outer-observer changes form a separate candidate with new hashes.
The proposal permits no new product adapter, provider proxy, orchestration framework, global client shutdown, or server kill.
An established stream socket alone cannot cover a blocked response-creation call.
The repair must demonstrate that earlier boundary or refuse before inference.

The inspected gateway interrupt seam supplies no auxiliary attempt transport handle to this private control.
The owner must supply that capability or authorize the narrow external runtime repair through a separately accepted source route.
Any source attempt also requires an explicit new bounded implementation budget and accepted control readiness.
The exhausted I1/I2/I3 budget supplies neither.
The current unaccepted runner must not supervise a repair worker as though cancellation were qualified.

## Offline acceptance cases — planned, not run

Use fake clocks, synthetic streams, and temporary databases and files.
Block provider access and real socket, image, mount, guest, and subprocess effects in each fixture.
Test the exact candidate call path rather than a replacement implementation.

| Case | Required observable result |
| --- | --- |
| Cancellation before dispatch | The provider receives zero requests. The attempt cannot later start. |
| Cancellation during response creation | The owned request aborts within cleanup, or admission refuses the unavailable capability before inference. |
| Generated-token stream continues | Hard cancellation closes the owned request despite continued token progress. |
| Iterator blocks between chunks | Cancellation wakes the blocked consumer and completes owner-thread closure within cleanup. |
| Terminal admission precedes provider exit | The supervisor remains active. It cannot report accepted termination from the terminal row alone. |
| Foreground client exits first | The independent observer retains the original deadline and records the auxiliary outcome. |
| Tokens, prompt progress, and compaction restart | None changes the external absolute deadline or creates another cleanup allowance. |
| Cancellation races completion | One terminal decision wins. The original cause and evidence remain stable. |
| Late timer and reused connection | Retired cleanup cannot close a successor's transport. |
| Another request shares the client | Cancellation leaves the other request and shared client usable. |
| Lost acknowledgement or observation failure | The supervisor preserves identity and unknown effects. It never replays the submission. |
| Wrong instance, epoch, admission, or generation | Cancellation refuses without affecting another request. |
| Cancellation during commit | The existing commit contract remains explicit. An overrun cannot become a passing deadline result. |
| Retry or fallback after hard stop | The provider receives no additional request. Late summary results cannot mutate the transcript. |
| Server release is absent or ambiguous | Termination remains unresolved at cleanup expiry. Earlier idle entries cannot satisfy release. |
| Evidence output partly writes then fails | The check fails, preserves the primary failure, and writes no success or acceptance record. |

A later live proof requires a separate reviewed admission after offline acceptance and current binding verification.
It must exercise auxiliary generation and reconcile the same owned request through server release.
This proposal grants no live admission and does not repeat D3.

## Evidence, checks, and next boundary

New private evidence resides in `aux-cancellation-20261029` under the preserved S1b root.
It contains the starting manifests, start gate, read-only observer, runtime result, new log suffixes, source ranges, and graph coverage.
It also contains historical lifetime summaries, closure results, and checkpoint hashes.
Full policies, credential references, raw logs, and complete exports remain outside Git.

The read-only observation command exited 0 under the installed Hermes interpreter:

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 /Users/hamedprooshani/.hermes/hermes-agent/.venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/aux-cancellation-20261029/observe_readonly.py
```

Its private record retains every process and listener command and exit status.
Publication checks use local Darwin `27.2.0`, arm64, and CPython `3.12.16`.
The observer uses CPython `3.11.14` on that host.
The exact closure commands and results reside in `closure-results.json`:

```sh
rtk proxy git diff --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python /Users/hamedprooshani/.hermes/backups/crewshal-s1b-20261025-e9n5_nu3/aux-cancellation-20261029/verify_closure.py
```

The closure verifier checks versions, links, scope, source identities, and preservation.
The whitespace, frozen-package, closure, and local import checks passed with exit 0.
The verifier confirmed 1,352 unchanged tracked files, all 233 starting private files, and 12 current source hashes.
It checked 843 local links and preserved every byte of the earlier README, changelog, and handoff records.
The frozen digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Both frozen execution flags remained false. The local import reported version `0.27.16`.
A later staged check exposed a verifier error: its version-diff assertion inspected unstaged changes after staging.
That command exited 1. Codex preserved the failure and changed the verifier to compare against the fixed base revision.
The corrected verifier passed with exit 0. No acceptance record was written by the failed command.
Product suites, Ruff, mypy, wheel builds, and installed-package checks remain not run for this process-only change.
All proposed repair cases remain planned. Linux-specific checks remain deferred under ADR 0009.
Use the [next prompt](CREWSHAL-AUXILIARY-CANCELLATION-NEXT-SESSION-2026-10-29.md) only with its stated decision and capability gates.

The exact archive-image attach action remains unapproved. The selected floors still need a reviewed proposal amendment.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain `10,008,484,533` and `116,542,541` bytes, totaling `10,125,027,074` bytes.
Image actions, guests, downloads, Linux tests, campaigns, evaluation, merge, deployment, and releases remain closed.
