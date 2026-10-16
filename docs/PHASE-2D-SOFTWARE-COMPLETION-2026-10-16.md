# Phase 2D software completion — 2026-10-16

**Phase 2D software complete; platform and live qualification deferred.**

ADR 0007 and the revised development plan define this software checkpoint.
This session completed the existing coordinator workflow with deterministic external fixtures.
Operational execution admission remains closed.
No Phase 2E implementation occurred.

## Delivered behavior

`prepare_codex_attempt` checks the stored confirmed project, current owner approval, task, configuration, scope, and initial candidate.
It commits one implementation intent and returns the existing inert `CodexRequest` contract.
It refuses existing attempts instead of retrying them.
`prepare_codex_contract` shares request validation with the existing qualified dispatch path.
The qualified path retains its platform and qualification checks.
Neither function launches a runtime or grants execution authority.

The external runtime fixture receives that request and changes the disposable candidate.
The existing collection path normalizes captured output and freezes the stopped candidate.
It records initial and final identities, claims, usage, scope evidence, and durable state.
The original repository files, dirty file, and Git metadata remain unchanged.

`capture_collected_check` resolves the approved check from the stored task.
It verifies the collection artifacts and exact frozen candidate before capture.
It records external validator results and the validating transition in one transaction.
It checks the candidate again before commit and refuses duplicate check capture.
The existing verdict code requires current candidate approval and all required evidence.
Worker success text remains an untrusted claim.

The checkpoint also includes the existing unpublished Phase 2D source and dated records.
This session changed no Linux implementation bytes.
It preserved all starting files outside the named core and publication files.
The prior operational failures, retained charges, custody, and unknown results remain historical evidence.

## Acceptance evidence

The new module contains 26 behavior tests.
It uses separate Python runtime and validator fixtures with real pipes, temporary files, and SQLite state.
It does not mock the coordinator or insert final success evidence.
Fixtures create no descendants and contain no provider calls.
Process supervision observations remain fixture inputs at the external boundary.
These observations do not prove platform containment, cancellation enforcement, or hard deadlines.

| Plan condition | Fresh evidence |
|---|---|
| Confirmed model and approved task | The request path accepts explicit decisions and refuses missing approval or stale inputs. |
| Changed candidate through production integration | A separate runtime fixture consumes the request; actual collection captures its changed candidate. |
| Original preservation and candidate identities | The complete workflow checks original bytes, dirty files, Git metadata, and changed candidate digests. |
| Independent exact validation | A separate validator checks frozen bytes; capture resolves and verifies the stored check definition. |
| Current decisions, scope, and required evidence | Actual verdicts block missing checks, stale approval, and changes outside scope. |
| Forgery and integrity refusal | Forged text, malformed output, artifact changes, candidate changes, and failed checks cannot pass. |
| Cancellation, timeout, refusal, and restart | Runtime and validator outcomes remain explicit; recovery preserves state and refuses retry. |
| Fresh durable fixtures | Every case creates new repository files, external fixtures, state, and artifacts. |
| Complete software checks | Source and installed suites each pass 1,248 occurrences; static, package, and CLI checks pass. |

The complete suite contains 1,232 unique methods and 16 existing repeated occurrences.
It includes 1,107 Phase 2D occurrences.
The new core tests account for 26 occurrences.
No suite reported a skip, failure, or error in the final runs.

## Environment and commands

The observed environment was macOS 27.2 arm64 with CPython 3.12.15 and uv 0.9.24.
Pinned dependencies included pydantic 2.12.5, pydantic-core 2.41.5, Ruff 0.14.1, and mypy 1.18.2.
The base revision was `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc` on `codex/phase1-architecture`.
The source contained preserved unpublished work at session start.
The delivery revision is the commit containing this report and version 0.14.0.
Use `git log -1 --format=%H -- docs/PHASE-2D-SOFTWARE-COMPLETION-2026-10-16.md` to resolve that revision.
The verification JSON records source hashes and exact final commands.

The focused affected suite passed 121 tests before six additional core cases were added.
The final standalone core run passed all 26 tests.
The source suite passed 1,248 tests in 42.034 seconds.
The installed suite passed 1,248 tests in 47.172 seconds.
Both complete suites used empty inherited environments, fresh HOME directories, and process-level network denial.
The installed environment used cached hash-locked dependencies and a fresh offline wheel.
All 47 installed package source files matched the checkout byte for byte.

Run these checks from the checkout:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_core
rtk proxy .venv/bin/python -m ruff check src tests scripts
rtk proxy .venv/bin/python -m ruff format --check src tests
rtk proxy .venv/bin/python -m mypy src/crewshal
rtk proxy git diff --check
```

Use the complete denied-network commands in the verification JSON for source and installed acceptance.
Build and dependency preparation require the pinned packages in the local cache.
Tests create their own fixtures and require no historical platform artifacts.

## Failures and limits

The first new test run exposed nested transactions in the initial implementation.
The correction uses the store's existing transaction primitives.
A later rollback test left its deliberate SQL trigger installed.
The test now removes that fixture trigger before reopening the strictly checked database.
The first lint run also found one unused test import; it was removed.
The development environment has no pip module; offline packaging used uv.
An initial 0.13.0 wheel build checked cached build availability before the final version update.
Only the final 0.14.0 wheel supplied installed acceptance evidence.

The complete formatter command reports nine existing script format differences.
All nine scripts match their session-start hashes.
Source and test formatting passes; repository-wide lint and strict source typing pass.
No unrelated historical script was reformatted.

Graph discovery used Verify evidence for `Volumes-X10Pro-Crewshal`.
The initial generation was `2026-10-15T19:30:19Z`; later coverage used `2026-10-16T07:00:02Z`.
Relevant core paths had matching metadata with no recorded issue.
This signal does not prove complete coverage.
The recorded C parser gaps remain outside this core change.
Direct source reads supplied the material implementation evidence.
The final core diff review found no unresolved correctness issue.

No Linux development, VMware operation, SSH operation, compiler, qualification batch, or exception proposal occurred.
No credential access, real coding runtime, provider request, paid host, merge, deployment, or registry publication occurred.
Platform and live qualification remain deferred.
Fixture outcomes do not change historical results or operational permission.

## Next session

Phase 2E adds the second runtime, independent review, and the planned software vertical slice.
Use [the next prompt](PHASE-2E-NEXT-SESSION-2026-10-16.md) and [exact input index](PHASE-2E-INPUTS-2026-10-16.json).
Stop this session after the coherent branch commit and push.
