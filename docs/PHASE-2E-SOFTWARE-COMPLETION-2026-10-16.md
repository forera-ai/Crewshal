# Phase 2E software completion — 2026-10-16

**Phase 2E software complete; platform and live qualification deferred.**

The revised development plan and ADR 0007 govern this checkpoint.
Version 0.15.0 completes the second adapter, independent review, and the planned coordinator software slice.
Operational execution admission remains closed.
Phase 3A implementation has not started.

## Delivered behavior

`ClaudeIdentity`, `ClaudeRequest`, and `normalize_claude` add bounded Claude Code request and stream contracts.
The adapter accepts the tested initialization, assistant, tool-use, tool-result, and terminal event subset.
It rejects malformed, replayed, unsupported, incomplete, failed, or mismatched output.
Runtime tool reports remain claims.
Token and cache counters remain runtime-reported data; measured cost remains unknown.
The adapter starts no process and supplies no launch permission.

`prepare_runtime_attempt` requires a recorded risk plan and uses the existing checked implementation path.
Both adapters use the production candidate capture, SQLite records, validator capture, and verdict rules.
The original first-runtime preparation interface remains available.
Its qualified dispatch retains the original platform and admission checks.
Dispatch binds 44 source files, including both new modules.
Changes to either module invalidate earlier source-bound configurations.

`configure_workflow` records the risk floor and exact allowed paths before implementation.
Ordinary-risk work requires checks and independent review.
High-risk work also requires an explicit human decision for the exact plan.
The current path categories provide a deterministic risk floor; the owner can select a higher risk.
Actual changed paths can raise that floor and block acceptance.
The low-risk path can finish without required model review.

The coordinator captures initial bytes before implementation.
`prepare_review` creates a separate frozen source copy and a bounded before/after diff.
The request contains the same confirmed project model, approved task, check definitions, results, and captured logs.
It excludes implementation claims and conversation.
The required reviewer must have a resolved provider identity that differs from the implementation provider.
A different runtime label or session cannot establish independence.
Missing review remains blocked even when a generic completion waiver exists.

`collect_review` records one terminal judgment, raw capture, claims, usage, and evidence in a SQLite transaction.
It verifies the frozen implementation and reviewer copy before and after capture.
The verdict checks the exact review and check snapshot.
A malformed report, failed process, changed candidate, changed artifact, or stale request cannot produce success.

`resolve_review` records explicit human risk acceptance, remediation, or stopping.
Risk acceptance preserves the disagreement and returns `accepted_with_waiver` when the remaining gates pass.
Stopping preserves findings and interrupts the run.
`start_remediation` creates another candidate copy, task, run, and plan after an explicit human decision.
It preserves prior records and required checks.
The new run requires fresh approval, affected validation, and review.
It cannot accept an earlier scope escape or silently retry an attempt.
The coordinator never merges a candidate automatically.

## Acceptance evidence

The new acceptance module contains 57 methods.
Its separate Python runtime, reviewer, and validator fixtures use actual pipes, candidate files, and SQLite state.
The tests do not replace the coordinator, capture, durable store, or verdict code with mocks.
The fixtures create no descendants and send no provider inference request.

| Software requirement | Fresh observable evidence |
|---|---|
| Both runtime role assignments | Codex implementation with Claude review and the reversed assignment reach actual verdicts. |
| Same confirmed project model | Both assignments use the same stored model in Python and package-based TypeScript fixtures. |
| Provider identity and unavailable review | Matching providers and unknown identity refuse review; absent review and generic waivers remain blocked. |
| Ordinary, high, and low risk | Ordinary review is required; sensitive scope requires planning approval; low-risk work needs no review. |
| Actual scope escalation | An external implementation changes an authentication path; scope and risk gates block acceptance. |
| Review conflict and human decisions | Disagreement blocks; explicit risk acceptance remains waived; stopping preserves findings and prevents retry. |
| Remediation and invalidation | A new candidate and task require new approval, checks, and review; old evidence remains separate. |
| Integrity and record separation | Claims cannot replace checks; source, report, request, and artifact changes cannot produce success. |
| Cancellation, refusal, failure, and restart | Both review roles and the second implementation adapter preserve terminal outcomes without implicit retry. |
| Original preservation and no merge | The complete workflow preserves original source, dirty bytes, and Git metadata. |
| Reproducible package | Complete source and installed suites, static checks, CLI help, and package-source comparison pass. |

The complete suites each pass 1,305 test occurrences.
They contain 1,289 unique methods and 16 existing repeated occurrences.
The focused affected suite passes 167 tests.
The Phase 2E and dispatch suite passes 71 tests.
All 49 installed package files match the checkout.
The final suites report no failure, error, or skip.

## Environment and reproduction

The environment is macOS 27.2 arm64 with CPython 3.12.15 and uv 0.9.24.
Pinned dependencies include pydantic 2.12.5, pydantic-core 2.41.5, Ruff 0.14.1, and mypy 1.18.2.
The base revision is `18fa30f5ed28ec78170ee4d73d37378e00017a21` on `codex/phase1-architecture`.
The checkout was clean at session start.
The delivery revision is the commit containing this report and version 0.15.0.
Resolve it with `git log -1 --format=%H -- docs/PHASE-2E-SOFTWARE-COMPLETION-2026-10-16.md`.

Run the focused and static checks from the checkout:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch
rtk proxy .venv/bin/python -m ruff check src tests scripts
rtk proxy .venv/bin/python -m ruff format --check src tests
rtk proxy .venv/bin/python -m mypy src/crewshal
rtk proxy git diff --check
```

[The verification JSON](qualification/phase-2e-software-verification-20261016.json) records exact complete-suite, build, install, and CLI commands.
Use fresh temporary directories and the hash-locked cached dependencies for reproduction.
The complete suites use empty inherited environments, fresh HOME directories, and process-level network denial.
Every test creates its own repository, state, and fixture artifacts.
No historical VM input, credential, or paid service is required.

Graph discovery used Verify evidence for `Volumes-X10Pro-Crewshal`.
The initial coverage generation was `2026-10-16T07:06:58Z`; later coverage used `2026-10-16T07:26:51Z`.
Relevant source and test paths had matching metadata with no recorded gap before inspection.
This signal does not establish complete coverage.
Direct source reads supplied the implementation evidence.
The existing C parser gaps remain outside this change.

## Development failures and limits

The initial second-adapter test failed because its module did not exist.
Regression tests then exposed missing-review waiver acceptance, review before check capture, and missing source diffs.
The corrected production paths pass these cases.
A static check required explicit typing for terminal review data.
The first complete source and installed runs each failed two old source-count assertions.
Their expected count changed from 42 to 44, and they now require both new modules explicitly.
These corrections preserve the existing admission assertions.
The final complete runs pass.

The repository-wide formatter still reports nine historical script differences.
All nine files match their starting hashes.
Source and test formatting passes, as do repository-wide lint and strict source typing.
The session preserved historical script formatting.
The final review found no unresolved correctness issue in this bounded software change.

The [official Claude Code documentation](https://code.claude.com/docs/en/headless) supports noninteractive JSON transport as a design reference.
It does not establish conformance for the pinned adapter version.
No real Claude Code or Codex process ran during this session.
Unsupported stream events fail closed until later conformance work verifies them.
The package-based TypeScript fixtures use independent byte checks; no TypeScript compiler ran.
The path risk rules do not replace human assessment of semantic or unknown critical risk.

Fixture process observations do not prove containment, read-only mount enforcement, cancellation enforcement, or hard deadlines.
Resolved provider identity remains a trusted adapter input that later live qualification must verify.
Platform and live qualification remain deferred requirements for operational use and support claims.
No Linux-specific source or C helper bytes changed.
Historical operational records, charges, custody, and unknown outcomes remain preserved.
The session did not inspect their current physical state.
No VMware, SSH, compiler, qualification batch, credential access, provider inference request, paid model, or paid host operation occurred.
The requested Jev skill required no decision-model call; this milestone authorized no paid model use.
No evaluation, automatic merge, deployment, or package-registry publication occurred.

## Next session

Phase 3A prepares the comparative evaluation package and its unresolved owner decisions.
Use [the next prompt](PHASE-3A-NEXT-SESSION-2026-10-16.md) and [exact input index](PHASE-3A-INPUTS-2026-10-16.json).
Stop this session after the standing version, documentation, commit, and branch-push ceremony.
