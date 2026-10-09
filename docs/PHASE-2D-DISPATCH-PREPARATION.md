# Phase 2D source-bound native/proxy dispatch preparation

Date: 2026-10-08. Status: **verified offline preparation; Phase 2D incomplete**. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, package 0.9.0, uncommitted. The owner's preparation-only, per-project/session scope remains controlling.

## Observable change

The existing batch template contains a native command tail but does not translate its security settings into concrete CLI arguments or bind the resulting command to the task, source and qualification. [The new coordinator module](../src/crewshal/dispatch.py) prepares those exact data without executing them. It imports no qualification driver and adds no CLI command, model/tool loop, proxy implementation or subprocess launcher.

`prepare_dispatch_configuration(selection, preparation_digest=..., task=..., binding=...)` compiles literal argv for pinned Codex 0.160.1 and the official matching-platform Responses proxy. Codex reads the requirement from separate stdin using final `-`; task text is never a command option or shell expression. Explicit `-c` values disable retries, hooks/plugins/skills, extra agents, login shell, web search and telemetry, using the pinned interfaces retained in the qualification inputs. The internal provider name is `crewshal`, with the prospective native transport at `http://127.0.0.1:8080/v1`. The selected provider/model remains in the separate attempt/selection identity; the proxy's upstream URL comes only from the explicit HTTPS destination. This does not observe provider availability or approve egress.

Configuration data includes the exact batch digest, task/check definitions digest, complete model/task/policy/scope/candidate launch binding, eleven current coordinator source hashes, native environment, validator argv and the original resource ceilings. Missing route choices remain missing; the compiler does not inspect ambient configuration, accounts or credentials. It returns false execution, spend and qualification flags. A selection-only configuration is useful unresolved preparation but cannot pass the complete dispatch preparation join.

`record_digest(configuration)` is the prospective configuration identity. A subsequent exact qualification must bind that digest along with the actual root, helpers/libraries, kernel, policies, grants, observer and broker design. Any changed task/check environment/toolchain, launch binding, selection, package source or batch changes the digest. Original v18 eligibility cannot transfer. Compiling data and parsing a qualification record prove neither authenticity nor effective controls.

`prepare_codex_dispatch(...)` first uses `audit_runtime_batch` against the independently retained coordinator expectation, then recompiles current source/configuration for exact equality. It requires explicit per-session provider/destination/billing/credential-treatment choices, the exact initial manifest, only README scope, the prepared requirement and one exact validator argv/cwd with no review. It delegates qualification/runtime/attempt validation to the existing `prepare_codex_request` seam and retains the exact qualification-record digest. Even success returns an inert `CodexDispatch` with false execution/spend authority. No live choices are required globally or requested by this session.

The native argv/environment and proxy argv describe separate roles. The proxy token input is only the declaration `separate_broker_stdin`; no secret, path, descriptor or credential is read or materialized. No kernel envelope is constructed. Running these argv directly on a host would bypass required containment. A future qualified supervisor must establish separate UIDs, namespaces, PID/FD views, credential channel, AppArmor/network/storage controls and cgroup placement, then capture actual readback. The prepared environment must replace inherited environment, not merge with it.

## Independent offline evidence

[Fourteen fresh tests](../tests/acceptance/test_phase_2d_dispatch.py) create their own references, batch, task/check, initial candidate, context and synthetic qualification. No historical observation or account is a fixture. They verify literal native/proxy argv and separate stdin without process/network calls; original limits and disabled feature settings; valid unresolved-choice refusal; project/session/model/route/billing isolation; altered argv/environment/stdin/source/authority refusal; absent/partial/failed/stale/platform-mismatched qualification; task/check/policy/snapshot invalidation; artifact/reference/candidate mutation; terminal/acknowledged attempt refusal; literal option-injection handling; current source change refusal; and refusal of an expanded fixture task/scope even with a fresh synthetic qualification. Synthetic qualification is test data, not a real profile pass. Attempt ceilings remain declarations, not observed budget enforcement.

Focused check: 14 passed in 0.196s. Full source suite: **213 passed in 8.205s**. Fresh installed wheel: **213 passed in 10.741s**. This is **72 Phase 2D methods** plus the original 141 methods. Both full runs use an empty inherited environment, temporary HOME and macOS sandbox network denial. Ruff lint/format passes (42 files); strict mypy passes (16 source files). Offline sdist/wheel build and fresh hash-locked dependency/wheel installation pass; all eleven installed bound source files exactly match the working source. Installed CLI still exposes only `init`, `show`, `validate`.

Reproduce:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_dispatch
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/mypy
```

[Verification/continuity](qualification/phase-2d-dispatch-preparation-verification-v1-20261008.json) records exact external build/install commands, hashes, environment, graph evidence and byte continuity. The initial focused import failed because `crewshal.dispatch` did not exist. No failed live run is inferred. Codebase-memory Verify reports matching source metadata with no recorded gap; graph edges misresolving `dict.get`/historical digest helpers were replaced with exact source. Coverage is best-effort. RTK wraps commands; Caveman affects chat only; Jev guidance was read but no paid call occurred.

## Incomplete boundary and next step

This session completes only the dispatch-preparation source join. Production Linux launch/supervision, independently observed credential and financial enforcement, fresh exact-profile qualification and separately approved actual implementation/credential-free validator acceptance remain missing. Original five-second/128 MiB ceilings, all twenty qualification cases, lost v5 cause/original cleanup and Windows/macOS runtime unknowns remain unchanged. No runtime, validator launch, credentials, provider/model/Jev, VMware/SSH, paid host, version bump, commit/push or 2E occurred.

Continue 2D only using [HANDOFF.md](HANDOFF.md), [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md), [current continuation and complete input set](PHASE-2D-CONTINUATION-2026-10-08.md), this guide, new source/tests/verification and prior collection source/evidence. Supply the missing supervisor source through accepted mechanisms; do not manufacture its observations or owner authority. Startup remains disabled until the exact project/session identity and separately recorded execution/spend batch gate exist. Publication awaits the full 2D gate.
