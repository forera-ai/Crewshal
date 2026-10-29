# Offline S1b proposal: rejected candidate and auxiliary termination gap

Date: 2026-10-29. Package checkpoint: `0.27.15`. Crewshal skill: `1.0.0`.
Base revision: `16d4019aef2bfee4e4632eb3a6570bdb198da119` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.
Supervisor chat: `01a187b8-4f50-7971-ad7c-132ebc25940f`.

## Verdict and boundary

The offline S1b proposal milestone remains **blocked**.
Codex rejected the saved I3 candidate after syntax, identity, and independent stub checks failed.
The exact candidate remains private. No attach-action draft enters this public checkpoint.
Codex accepts this blocked process record only.
This checkpoint does not accept the proposal or qualify the implementation runner.

The implementation budget is exhausted: I1 plus corrections I2 and I3.
No count was reset. No additional implementation request is permitted under that budget.
The next session must diagnose auxiliary cancellation through read-only evidence.
Any later implementation attempt needs an explicit new bounded budget.

## Start gate and preservation

Trusted local `turn_context` metadata identified the supervisor as `gpt-6.1-sol`.
The checkout started clean at the base revision. Both package declarations contained `0.27.14`.
The remote remained `https://github.com/forera-ai/Crewshal.git`.
RTK reported `1.1.0` at `/opt/homebrew/bin/rtk`.
All five installed Crewshal skill files matched their repository copies.
The Hermes exposure resolved to the same global installation.
Codex loaded these companion skills:

- `/Users/hamedprooshani/.agents/skills/codebase-memory/SKILL.md`.
- `/Users/hamedprooshani/.agents/skills/caveman/SKILL.md`.
- `/Users/hamedprooshani/.codex/skills/jev/SKILL.md`.

The synthetic Jev check returned probability `0.98`, confidence `0.96`, and reported cost `0`.
Its reported latency was `240` milliseconds. Actual total billing remains unknown.
Crewshal graph coverage used Verify evidence at generation `2026-10-29T12:51:18Z`.
Fourteen selected repository paths had matching metadata without recorded gaps.
That best-effort result does not prove completeness.
Hermes graph generation `2026-09-02T17:14:19Z` remained stale for relevant control paths.
Current source controlled the policy, resume, submission, and interruption findings.

All historical manifest sets matched before private control work.
Their entry counts were `33`, `10`, `78`, `111`, and `37`.
The new starting manifest preserved `149` existing private files.
Original records, failed attempts, policies, inspectors, controls, and observations remain unchanged.

## Runtime and reused readiness

Read-only observations found current model PID `37533`, under parent PID `44430`.
The selected backend used port `63340`; the existing route retained port `8888`.
Arguments and matching load evidence selected cached Ornith `UD-Q4_K_XL`, context `93696`, and one slot.
Transport checks sent zero application bytes.
No service start, restart, model substitution, download, credential extraction, or profile edit ran.
Hermes source remained clean at `bf0203a794a07aac3ff764972ab9087baa4e4f4e`.
The saved diagnosis source hashes matched.

The raw-profile hash matched the October 28 observation.
It still differed from the older October 25 baseline. Full raw-profile history remains unknown.
The SOUL, selected settings, fallback settings, installed skills, and MCP bindings remained unchanged.
The seven checked R1 input documents retained their bytes.
Codex reused R1 readiness for the same existing worker.
No successful worker, approval, or MCP probe was repeated.

The actual stored implementation policy retained source `oneshot`, platform `cli`, 25 turns, and budget `600`.
Its effective tools matched R1. This was not D3's empty ACP diagnostic policy.
Single-query approvals remained `deny`. Nested orchestration remained disabled. Fallback providers remained empty.
The continuation used `finite=True` and `unattended=False`.
The runner bound multiplexer epoch `12` and profile authority epoch `11` separately.
It created no new session and submitted each correction once.

## Private controls and attempts

The new resume wrapper reused the accepted deadline lifecycle outside product source.
It checked the existing session, prior generation, idle state, and exact stored policy before submission.
The total deadline remained `600` seconds, with `15` seconds for cleanup and a separate `630`-second client ceiling.
Twenty-three offline fixtures passed, including four tests of the actual runner.
They covered identity drift, lost acknowledgements, policy refusal, admission mapping, and bounded cleanup.
An initial run exposed an unclosed evidence file before admission.
Codex added its close callback and preserved the initial warning.
The corrected run passed 23 tests in `0.218` seconds.
The existing SQLite warning remains preserved. No runtime update ran.

| Attempt | New observation | Decision |
| --- | --- | --- |
| I2, first correction | Two terminal calls repeated bare `cd`; the first also used bare `echo` and shell chains. | Stop the exact generation for repeated command misuse. |
| I3, final correction | One file-tool call saved a 39,288-byte draft. The runtime then entered compaction. | Stop before candidate review; reject the saved candidate after failed checks. |

I2 used admission sequence `55`, generation `3`.
Codex requested its interruption after `333.422974` seconds.
Its foreground process exited 0 after `334.060257` seconds, with gateway outcome `terminal/interrupted`.
Server task `809` received cancellation and released its slot.
The checkout remained clean after I2. It produced no candidate.

I3 restricted the task to file tools and the single draft.
It retained the same tested control path, with different artifact labels and request identity.
No further correction remained after dispatch.
One `write_file` call saved the complete draft. Worker tests remained not run under that packet.
I3 used admission sequence `56`, generation `4`.
The foreground process exited 0 after `456.715376` seconds, with gateway outcome `terminal/interrupted`.
That process result did not establish model termination.

## Auxiliary request exceeded the ceiling

After the file write, the runtime started auxiliary compaction request `14181`.
The gateway became terminal while that request continued generating.
At `635.708800` seconds from I3's monotonic start, the server still reported generation for that task.
This exceeded both the `600`-second deadline and its `15`-second cleanup allowance.
The separate client process had already exited.

A later reconciliation captured task `14181` releasing its slot and subsequent idle entries.
No cancellation line for that task appeared in the retained interval.
Codex observed the final reconciliation at `819.679392` seconds from the I3 start.
That observation time is not the exact server release time.
Supervisor and server log clocks were not independently synchronized.
Task association uses the bounded request interval, selected route, one slot, and gateway compaction events.
The server log supplies no direct admission identifier.

The runner is **not accepted** for termination across this auxiliary path.
Later slot release does not repair the failed ceiling.
D3's earlier bounded prompt-processing acceptance remains historical and unchanged.
No broader cancellation or runtime-conformance claim follows from D3 or the new fixtures.
Final usage and actual billing remain unknown.

## Candidate review and failed checks

The complete rejected draft has SHA-256:
`f06318c540ed8ecbca092e59f140d49dea921cadef89173352741bd6cef6208c`.
Its preserved name is `s1b-20261029/I3/candidate.md` under the existing private evidence root.
The two exact Python blocks remain preserved separately with their hashes.
The original worker-owned draft was removed from the checkout after byte-preserving archival.

Codex found these blocking defects:

- The test block has an unclosed `try` statement. Compilation fails at test line `386`.
- The `python-1` digest differs from the frozen public corpus value in the table and action.
- The identity check accepts a whole-device self-reference without selecting a mounted partition.
- The action skips cleanup after a verification failure, despite marking the identity trusted.
- The harness leaves filesystem predicates and the real recorded mount path unisolated.
- Its content generator falsely assumes generated bytes match a prescribed existing SHA-256.
- The draft attributes plist keys to help output that supplies no such schema evidence.

The action block passed syntax parsing. The test block failed with:
`SyntaxError: expected 'except' or 'finally' block`.
The first extraction command exited 1. It wrote no success record for the failed test block.
The later exact saved unittest command also exited 1 at import. Zero action cases ran.
It ran inside a fresh temporary directory that was removed afterward:

```sh
rtk proxy env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest -v test_s1b_action
```

Two independent diagnostic fixtures then exercised the unchanged saved action with fully synthetic effects.
They isolated blob verdicts and injected every external command.
One reproduced acceptance without a mounted partition. The other reproduced missing cleanup after verification failure.
Both failed. Their command exited 1; temporary evidence directories were removed.
No real image, device, mount, or blob was accessed.
These failures are not passing S1b refusal checks.

## Closure and next scope

Private evidence resides in `s1b-20261029` under the preserved S1b evidence root.
It includes start-gate evidence, manifests, task packets, controls, exports, logs, failed checks, review, and closure results.
Full policies, credential references, raw logs, and complete exports remain outside Git.
The whitespace, frozen-package, version, link, scope, and preservation checks passed with exit 0.
The verifier confirmed 1,350 unchanged tracked files and all 149 starting private files.
It also confirmed all 37 preserved I2 files and the exact rejected candidate hash.
The frozen digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Both frozen execution flags remained false. The exact commands were:

```sh
rtk proxy git diff --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal,platform,sys; print("version",crewshal.__version__); print("environment",platform.system(),platform.release(),platform.machine(),sys.version.split()[0])'
```

The private `verify_closure.py` command also exited 0 through the same repository interpreter and RTK proxy.
Its absolute argv, environment, and results remain in the private closure record.
The final staged whitespace check and complete publication diff require Codex review before commit.

Repository checks use local Darwin `27.2.0`, arm64, and CPython `3.12.16`.
Private control fixtures use CPython `3.11.14` on the same host.
Product suites, Ruff, mypy, wheel builds, and installed-package checks remain **not run** for this process checkpoint.
Linux-specific checks remain **deferred** under ADR 0009.

Use the [continuation prompt](CREWSHAL-S1B-BLOCKED-NEXT-SESSION-2026-10-29.md) for read-only auxiliary-cancellation diagnosis.
Do not replay I2 or I3, reset attempts, or silently start another worker.
The exact archive attach action remains unapproved. The selected floors still require a reviewed proposal amendment.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Historical archive and package charges remain `10,008,484,533` and `116,542,541` bytes.
Their conservative total remains `10,125,027,074` bytes.
Image actions, guests, downloads, Linux tests, campaigns, evaluation, merge, deployment, and releases remain closed.
