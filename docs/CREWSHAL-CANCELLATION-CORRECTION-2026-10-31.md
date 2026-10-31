# Offline auxiliary cancellation correction

Date: 2026-10-31. Package checkpoint: `0.27.20`. Crewshal skill: `1.0.0`.
Base: `5ee638397c9ddecdcc14af3e6245e2cc740685d2` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Verdict and authority

The owner approved one direct Sol 6.1 offline correction after the read-only diagnosis.
The approved private proposal has SHA-256 `22224e830141602483f64ce906d2d655ab6c025d96d8e59d646b5bf97c558d20`.
The grant permits zero automatic follow-up corrections.
Current local turn metadata identified `gpt-6.1-sol`.
The repository started clean at the base revision with package version `0.27.19`.

Codex accepts the corrected candidate within its tested offline scope.
The full guarded suite exited 0: all 76 tests passed.
It recorded zero denied external-effect attempts and zero pending owned fixture threads.
The one new correction is consumed. No further correction remains under this grant.
The earlier repair budget, I1/I2/I3, and the context task's implementation plus two corrections remain exhausted.
The [previous rejection](CREWSHAL-TRANSPORT-CONTEXT-STOP-2026-10-31.md) remains unchanged historical evidence.

Installed Hermes source, profile, SOUL, dependencies, and historical runners remain unchanged.
The candidate was not applied or activated. No live gateway observation, worker, model request, restart, or inference ran.
Offline acceptance does not establish server release, live auxiliary cancellation, or readiness of a worker control route.

## Diagnosis before correction

The new fixture exercised the exact unchanged selected consumer through installed OpenAI, HTTPX, and HTTPCore code.
Synthetic network backends supplied HTTP bytes. No provider connection ran.
Controlled barriers ordered inner-read completion and request-owned task cancellation.
The fixture retained an unrelated active request and recorded operation identity, task state, monotonic times, and owner-thread closure.

The baseline ran three diagnostic tests. Two failed at the intended behavior assertion; pending-read cancellation passed.
The completed-inner trace showed `wait_for` returning with cancellation count `1` and the persistent stop set.
The consumer then fed another chunk and started another provider read.
The terminal-inner trace showed `StopAsyncIteration` after cancellation, followed by result construction after the persistent stop.
The pending-inner trace propagated `CancelledError` and closed its owned resources.
The isolated diagnostic recorded no denied effects or pending owned threads.

These new observations establish the source-level mechanism through a controlled SDK execution.
They do not reconstruct the historical failed request. Its exact failure sequence remains unproven.
The deterministic fixture bounds the baseline after the extra read rather than leaving its stream active.
Its diagnostic wrapper preserves the installed `wait_for` implementation and records the controlled scheduling boundary.

## Exact correction

The runtime correction changes only these two existing private candidate files:

- `agent/auxiliary_client.py` passes the persistent stop event into its selected protected request consumer.
- `agent/auxiliary_stream_watchdog.py` carries that same event through the request-owned transport contract.

The consumer checks the event before dispatch, before each read, after awaited results, and at stream end.
It checks again after stream closure and before result construction.
The transport checks the event after owned client closure and before returning its result.
Cancellation cannot disappear merely because the inner result completed at the same time.
The original protected wrapper retains responsibility for terminal-state selection and cleanup reconciliation.

All three gateway candidate files retain their previous bytes.
The protected wrapper, ordinary unprotected behavior, identity rules, admission contract, and commit fence remain unchanged.
All 71 original tests, the private submission control, and the private supervisor retain their bytes.
Three cancellation regression tests and two metadata tests were added.
The original request deadline, concurrency cleanup allowance of `0.2` seconds, and separate client ceiling remain unchanged.
No proxy, shared-client close, server kill, new product adapter, or alternate runtime route was added.

The cumulative runtime patch has SHA-256 `284cd55e118573debc8ddf1be3e5037f6b5e730eeadf89f44d4e90fa29779537`.
The candidate manifest has SHA-256 `df6c6cd86106ac6f6316a4d0f038123f9871e946f07ef9255befd03e597fb2c6`.
These identities bind the isolated candidate. They grant no application or operational authority.

## Metadata isolation and strict guard

The fixture now supplies synthetic data at `platform.uname_result.processor`.
That property bypasses the top-level `platform.processor` function.
After that change, the first diagnostic exposed a second metadata subprocess path through `platform.architecture`.
Its blocked attempts remain recorded. No blocked subprocess executed.
The fixture now supplies synthetic architecture metadata at that observed boundary as well.
The cold-cache SDK test requires actual property lookup and valid synthetic platform headers.
It does not hide the problem behind cached `Unknown` metadata.

The strict network, datagram, subprocess, credential, and live-profile guards remain active.
A separate negative guard command deliberately attempted a subprocess through the guard and caught its exception.
Its two ordinary tests passed, but the runner still exited 1 because it recorded that attempted effect.
This expected refusal proves that catching the exception cannot turn an external-effect attempt into acceptance.
The acceptance suite contains no such deliberate attempt and exited 0.

## Checks and evidence

| Check | Result |
| --- | --- |
| Initial diagnosis preservation | Nineteen historical manifest sets matched before the approved correction. |
| Starting snapshots | Preserved 513 existing private files and 1,367 tracked repository files. |
| Controlled unchanged consumer | Three tests ran; two intended failures established post-stop work. |
| Corrected focused cancellation cases | Three tests passed, with no post-stop read, chunk feed, or result construction. |
| Cold SDK metadata | Two tests passed; no denied attempt occurred. |
| Complete guarded acceptance | All 76 tests passed; exit 0; zero pending owned threads and denied effects. |
| Negative external-effect guard | Expected exit 1 after a caught blocked attempt; no subprocess executed. |
| Candidate syntax | All five runtime files compiled in memory without bytecode writes. |
| Cumulative patch applicability | `git apply --check` exited 0. The patch was not applied. |
| Private Ruff | Exit 0 for controls, runner, transport, and all tests. |
| Isolated runtime Ruff | Baseline and candidate each exited 1 with 19 diagnostics; zero introduced diagnostics. |
| Configured Hermes Ruff | Unavailable: the unchanged `ruff.toml` selector `PLR1708` caused exit 2. |
| Product tests, mypy, wheel, installation | Not run for this private runtime evidence checkpoint. |
| Linux checks | Deferred under ADR 0009; not run. |

Checks used Darwin `27.2.0`, arm64, Hermes CPython `3.11.14`, OpenAI `2.24.0`, HTTPX `0.28.1`, and HTTPCore `1.0.9`.
Publication checks use Crewshal CPython `3.12.16` where applicable.
Each captured command records its argv, working directory, exit, input hashes, and unchanged-input result.
The corrected deterministic cases completed owned wire closure within two milliseconds in the full acceptance run.
That local observation does not establish live timing guarantees.

Private evidence resides in `aux-correction-20261031-01a1938d` under the preserved S1b root.
Resolve that root from the [owner-preparation prompt](CREWSHAL-HERMES-DEADLINE-OWNER-PREP-NEXT-SESSION-2026-10-28.md).
The adjacent `aux-context-diagnosis-20261031-01a1938d` retains the approved proposal and preceding read-only review.
Raw candidate source, traces, exact commands, failures, and hashes remain outside Git.
Historical candidates and all failure records remain preserved.

Graph work used Verify evidence. Stale Hermes generation `2026-09-02T17:14:19Z` required current-source fallback.
The preceding source captures and coverage findings remain applicable to unchanged installed source.
Private candidates were reviewed directly. No recorded coverage gap proves completeness.
No new Jev probe ran. Historical reported cost and unknown actual billing remain historical.

## Next milestone and closed gates

The owner requested concrete local-model work in the next session.
The [next prompt](CREWSHAL-LOCAL-MODEL-OBSERVATION-NEXT-SESSION-2026-10-31.md) assigns an offline observation translator and deterministic fixture suite to Hermes.
It specifies owned files, acceptance cases, bounded attempts, and a stop before publication.
It requires accepted control readiness for the exact worker route before dispatch.
This offline correction alone cannot supply that operational readiness.
No worker is dispatched by this checkpoint or by writing that prompt.

Activation, application, gateway actions, live proof, profile changes, credentials, downloads, image actions, and guests remain closed.
Linux tests, campaigns, evaluation, merge, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The prior D3 acceptance, I3 overrun, unknown server-release cause, and clock limitations remain unchanged.

## Publication evidence

Whitespace, frozen-package, local-import, synchronized-version, scope, link, and preservation checks passed with exit 0.
Closure verified 1,362 unchanged tracked files, all 513 starting private files, seventeen candidate artifacts, and twelve installed source hashes.
It also verified unchanged gateway candidates, original tests, private controls, profile, SOUL, and historical document bytes.
The frozen digest remains `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Both frozen execution flags remain false.
The first whitespace command ran from the private evidence directory and exited 129 because that directory has no Git repository.
The corrected command supplied the explicit Crewshal checkout with `git -C` and exited 0.
The staged check then found one added blank line at the new record's end and exited 2.
That line was removed. The corrected staged check passed without changing candidate bytes.
All command records remain preserved. No acceptance claim relied on a failed whitespace command.
