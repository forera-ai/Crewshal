# Phase 3B operational admission proposal v1

Date: 2026-10-18. Status: proposed; no execution authority.
Base revision: `9deb7d476615c4f3016acedd0e0c0160ffab08b6`.
Frozen source package: `phase3a-20261016-v1` at version `0.15.2`.

This proposal covers development calibration only. It does not amend the frozen package or authorize a run.
The owner approved zero evaluation money, zero subscription quota, and zero paid-host spending.
Phase 3A completion did not qualify a runtime, platform, baseline, or dependency environment.
The exact public starting index matched all 120 recorded files on this date.
The read-only checker reported 23 consistent artifacts and 768 planned units.
The focused offline suite passed 108 tests. Neither check ran a coding runtime.
The [verification record](PHASE-3B-ADMISSION-VERIFICATION-2026-10-18.md) gives the exact commands and results.

## Requested decision and batch

Request explicit resumption of platform and live qualification on the owner's existing local VMware Ubuntu installation.
Request a separate Phase 3B batch with these limits:

| Exposure | Proposed limit | Enforcement and limit |
| --- | --- | --- |
| Metered API billing | USD 0 | Do not supply API keys or enable metered fallback. Stop on any billed operation. |
| Paid hosts | USD 0 | Use the existing local VMware installation only. No droplet operation enters this batch. |
| Official subscription submissions | 256 Codex turns and 256 Claude Code turns, including qualification, implementation, review, and remediation | Count submissions before launch. Disable automatic coordinator retries. This limits submissions, not service quota debit. |
| API-equivalent estimate | USD 200 for the batch | Use the frozen rate formula. Stop when the next known estimate would exceed this planning limit. Unknown counters remain unknown. |
| Service subscription quota debit | Unknown | Neither selected CLI supplies a verified hard quota ceiling in the frozen package. The owner must accept this unknown exposure explicitly. |
| Data transfer and dependency retrieval | 8 GiB downloaded, 8 GiB retained | Record source and package digests. Admit each destination before retrieval. No package hook executes during retrieval. |

These are proposed limits, not observations or current approval.
The USD 200 estimate is not measured billing. A missing usage category cannot be entered as zero.
Stop further turns if unknown usage prevents a reliable check against the planning limit.
If the owner requires a hard provider quota ceiling, this batch cannot start until that control is proved.
No Jev request enters this batch. Jev is a paid model service, and the current allowance is zero.

## Frozen development units

Use exactly four selected development repositories and twelve tasks.
Use two repetitions, four conditions, and both role assignments for each task.
The frozen schedule has 192 development rows. Keep the 576 sealed rows planned and unexposed.
Do not use the other four development repositories for calibration runs.

| ID | Public repository and revision | Archive SHA-256 | Tasks |
| --- | --- | --- | --- |
| `python-1` | `pallets/click` `934813e4d421071a1b3db3973c02fe2721359a6e` | `edfa6cf117bbbe46f6690266a40389b08b12cbf87fad8664d349ebd6eea811a1` | `python-1-documentation`, `python-1-behavior`, `python-1-compatibility` |
| `typescript-2` | `honojs/hono` `5e1f54caf99cc158b0d20dc02ed44d0a4a596842` | `4754f74b4defcbaa9b8748406fcd3e974b756abf7824e8a1a4304ec9665e6ced` | `typescript-2-documentation`, `typescript-2-behavior`, `typescript-2-compatibility` |
| `swift-1` | `apple/swift-argument-parser` `41982a3656a71c768319979febd796c6fd111d5c` | `45c952a441611e17d8c30de26c4a6b40eec483c07900d9faad2501539aa5c900` | `swift-1-documentation`, `swift-1-behavior`, `swift-1-compatibility` |
| `dotnet-1` | `serilog/serilog` `0e316b7cb072ee660b97976098b1bbdb20ac6da0` | `71a77a7c2eb4d1ffa1572c97c9050c673e16f24cdac19d5039ad79cad06a26dd` | `dotnet-1-documentation`, `dotnet-1-behavior`, `dotnet-1-compatibility` |

The exact task requirements, allowed paths, acceptance cases, check `argv`, working directories, and 900-second check limits are in `development-tasks.json`.
Do not translate those commands without a prospective campaign amendment.
The complete ordered rows are in `schedule.json` with seed `310016` and algorithm `sha256-sort-v1`.
Preserve B0, B1, B2, P and both `A-implements` and `B-implements` assignments.
B0 has no reviewer. B1 requires fresh review. B2 review applies only when supported.
P uses the same confirmed model for both assignments and requires review under its recorded risk policy.

## Required inputs and proposed preparation commands

Run these commands only after the owner approves the exact preparation scope.
Run them inside a new, owner-controlled, nonshared local Ubuntu environment.
The commands shown here do not authorize package installation, login, inference, or task execution.

```sh
rtk proxy uname -srm
rtk proxy cat /etc/os-release
rtk proxy getconf _NPROCESSORS_ONLN
rtk proxy free -b
rtk proxy df -B1 /var/tmp
rtk proxy sh -c 'command -v rtk'
rtk proxy sh -c 'command -v python3'
rtk proxy sh -c 'command -v node'
rtk proxy sh -c 'command -v bun'
rtk proxy sh -c 'command -v swift'
rtk proxy sh -c 'command -v dotnet'
rtk proxy sh -c 'command -v cmake'
rtk proxy sh -c 'command -v ninja'
rtk proxy sh -c 'command -v codex'
rtk proxy sh -c 'command -v claude'
```

Stop if the guest is not Linux arm64, or if any selected tool is absent or different.
Require at least four available CPUs, 16 GiB RAM, and 40 GiB free disk before preparation.
Cap concurrent task units at one. Cap the preparation tree at four CPUs, 12 GiB RAM, and 24 GiB disk.
Cap each coding-runtime batch at the unchanged qualified native limits, including its 600-second deadline and 768 MiB charge.
Cap each separate validator at four CPUs, 8 GiB RAM, 8 GiB disk, and its frozen 900-second check deadline.
Stop if the local guest cannot enforce these limits. Do not substitute host-side timeout for the qualified native timer.
The 12 GiB preparation limit is a proposed new control. It does not enlarge any historical native limit.

The source archive URLs and exact archive sizes are recorded in `corpus.json`.
Use a private `0700` batch root under `/var/tmp/crewshal-phase3b-v1` after admission.
Download only the four selected public archives from their recorded `archive_url` values.
Use this exact retrieval pattern for each selected repository ID after binding `ARCHIVE_URL` and `ARCHIVE_SHA256` from `corpus.json`:

```sh
rtk proxy curl --proto '=https' --tlsv1.2 --fail --location --retry 0 --max-time 120 --output "$BATCH_ROOT/archives/$REPOSITORY_ID.tar.gz" "$ARCHIVE_URL"
rtk proxy sha256sum "$BATCH_ROOT/archives/$REPOSITORY_ID.tar.gz"
```

Compare each digest and byte count with `corpus.json` before extraction.
Bind and verify a safe extraction command before extraction.
Reject symbolic links and paths that escape the owned root. Compare the extracted file inventory with `source-inventories.json`.
Create a fresh source copy for every scheduled row. Keep source archives and dependency snapshots read-only.
Keep writable caches, runtime HOME directories, source copies, and reviewer contexts separate for each run.

Freeze the following exact selected toolchains before checks: CPython `3.12.15`; Node.js `22.14.0`; Bun `1.2.2`; Swift `6.0.3`; and .NET SDK `9.0.100` for `dotnet-1`.
Bind the actual executable digests, platform SDK, target frameworks, CMake, Ninja, and resolved package versions.
Use the selected Codex CLI `0.160.1` and Claude Code CLI `2.1.278` only after their exact Linux arm64 distribution integrity and executable digests match.
Use requested models `gpt-6.1-sol` and `claude-sonnet-5-5` at high reasoning effort.
Use fresh contexts, no inherited global configuration, hooks, plugins, MCP servers, fallback models, or coordinator retries.
The selected constraints are not effective configuration observations. Bind effective configuration before each turn.

The pinned `python-1` constraints are `requirements/build.txt`, `dev.txt`, `docs.txt`, `tests.txt`, `tests37.txt`, and `typing.txt` under `requirements/`.
The pinned `typescript-2` root lock is `bun.lock`; the five benchmark locks remain source inputs.
The selected `swift-1` and `dotnet-1` sources have no recognized lockfile in the frozen inventory.
Resolve their dependencies in a separately admitted preparation operation. Freeze exact package IDs, versions, hashes, license results, and a read-only snapshot.
Do not run package install hooks or open network access inside a validator.
If resolution changes selected inputs, create a prospective campaign version before dependent checks.

## Qualification and command binding

First qualify the exact local platform with synthetic inputs and all applicable original containment cases.
Test external reads and writes, symlink escapes, native file tools, shell descendants, network egress, credential inheritance, hooks, plugins, MCP injection, cancellation, timeout, and restart.
Use synthetic credentials only. Test an independent credential-free validator.
Keep the historical failed Orka native exclusions failed until a new exact observation passes.
Do not treat the prior Orka fake-backend tests as native conformance.
For each enabled condition, run actual baseline conformance with the same pinned source, task, budget, check definitions, and qualified environment.
Record failed, blocked, unsupported, interrupted, and unknown cases in the denominator.
No failed or unavailable comparison becomes a passing baseline.

The frozen task checks supply exact `argv` arrays. Invoke each array without shell rewriting.
Run each baseline check on the unchanged pinned source before task execution.
Record the command, working directory, exit, stdout/stderr digests, environment, toolchain, and baseline candidate identity.
The selected checks include Python, Bun, Node.js, Swift, CMake, Ninja, and .NET commands.
The exact task commands appear below and in the frozen task contracts.
The Node regression check uses the local Vitest module and only `runtime-tests/node/base64url-strict.test.ts`.
Its network remains denied. Do not select `runtime-tests/node/index.test.ts`.
The exact commands and prerequisites for each task remain authoritative in `development-tasks.json`.

The selected task check commands are listed below. Run them from each fresh source copy.
Each check has the frozen 900-second limit. Run checks only after their recorded prerequisites pass.

```text
python-1-documentation:
  rtk proxy git diff --check
  rtk proxy tox run -e docs
  rtk proxy python -m pytest tests/test_types.py
python-1-behavior:
  rtk proxy python -m pytest tests/test_types.py
  rtk proxy tox run -e typing
python-1-compatibility:
  rtk proxy python -m pytest tests/test_types.py
  rtk proxy tox run -e typing
  rtk proxy tox run -e docs
typescript-2-documentation:
  rtk proxy git diff --check
  rtk proxy bun x vitest --run src/utils/encode.test.ts
typescript-2-behavior:
  rtk proxy bun x vitest --run src/utils/encode.test.ts
  rtk proxy bun x tsc --noEmit
  rtk proxy bun run lint
typescript-2-compatibility:
  rtk proxy bun x vitest --run src/utils/encode.test.ts
  rtk proxy bun x tsc --noEmit
  rtk proxy bun run build
  rtk proxy node ./node_modules/vitest/vitest.mjs run --config ./runtime-tests/node/vitest.config.ts runtime-tests/node/base64url-strict.test.ts
swift-1-documentation:
  rtk proxy git diff --check
  rtk proxy swift test
swift-1-behavior:
  rtk proxy swift test --filter ArgumentListConversionTests
  rtk proxy swift test --filter ArgumentParserUnitTests
swift-1-compatibility:
  rtk proxy swift test --filter NonEmptyArgumentTests
  rtk proxy swift build
  rtk proxy cmake -S . -B task-cmake -G Ninja
  rtk proxy cmake --build task-cmake
dotnet-1-documentation:
  rtk proxy git diff --check
  rtk proxy dotnet test test/Serilog.Tests/Serilog.Tests.csproj --framework net8.0 --configuration Release --filter 'FullyQualifiedName~MessageTemplateParserTests'
dotnet-1-behavior:
  rtk proxy dotnet test test/Serilog.Tests/Serilog.Tests.csproj --framework net8.0 --configuration Release --filter 'FullyQualifiedName~LogEventLevelExtensionsTests'
  rtk proxy dotnet test test/Serilog.ApprovalTests/Serilog.ApprovalTests.csproj --framework net9.0 --configuration Release --filter 'FullyQualifiedName~Serilog'
dotnet-1-compatibility:
  rtk proxy dotnet test test/Serilog.Tests/Serilog.Tests.csproj --framework net8.0 --configuration Release --filter 'FullyQualifiedName~LogEventLevelParserTests'
  rtk proxy dotnet build src/Serilog/Serilog.csproj --configuration Release --framework netstandard2.0
  rtk proxy dotnet test test/Serilog.ApprovalTests/Serilog.ApprovalTests.csproj --framework net9.0 --configuration Release --filter 'FullyQualifiedName~Serilog'
```

B1 requires a minimal manual script that implements its frozen process contract.
Bind the script bytes, exact command, inputs, and operator steps before its first conformance run.
No such script is present in the frozen package. B1 stays blocked until that preparation passes.
B2 uses Orka revision `9e366915fc6cd6ede5aa47ac7a3b418a32ff528b` without Crewshal wrapping.
Orka's native exclusion failures and unsupported control differences stay visible.
P uses the production Crewshal interfaces at the frozen behavioral source hashes unless a prospective amendment records a change.

Before each turn, bind source, task, initial candidate, applicable confirmed model, policy, scope, checks, runtime, provider, and model.
Also bind executable, effective configuration, command, environment, toolchain, and platform qualification.
Record the resulting candidate only after capture. Do not invent future digests.
Use the frozen schedule order, two repetitions, cache rules, thresholds, and failure accounting.
Stop on a failed boundary, false completion, unavailable mandatory control, or exhausted approved limit.
No blocked or no-op row can count as a saving over completed work.

## Deadlines, evidence, and cleanup

Limit preparation to 8 hours of active operation and 24 hours of elapsed wall time.
Limit one task unit to 90 minutes, including checks, review, and approved remediation.
Limit the whole batch to 14 days after its first qualified turn.
Keep the original 600-second native limit and each frozen 900-second check limit within these outer limits.
Any incomplete unit keeps its actual terminal status and partial usage.
No automatic retry follows a timeout or lost side-effect response.

Store raw receipts under the owned batch root with `0700` directories and `0600` files.
Keep raw provider logs, authenticated state, and private paths outside Git.
Publish only sanitized evidence with digests after reviewing license and privacy limits.
Record measured billing, API-equivalent estimates, service quota telemetry, and unknown usage in separate fields.
Record active setup, corrections, human remediation, machine time, cache categories, and every attempt.
Keep agent reference annotations distinct from human ground truth.

After capture, remove only batch-owned source copies, writable caches, and dependency scratch.
Verify that no child process, mount, or file handle still owns them before removal.
Retain unresolved resources and charge their full reservations. Do not delete historical custody or the VM.
Keep public source receipts and reproducible pinned inputs. Retain private raw evidence until a later owner disposal decision.

## Admission result today

This proposal is not an executable admission manifest. Current host, toolchain, dependency, runtime, provider, and baseline observations remain unavailable.
Safe extraction, the minimal B1 script, and exact effective launch commands still require source preparation and qualification.
The current guest capacity and quota enforcement are unknown.
An approved proposal cannot convert these missing observations into passes.
The smallest owner decisions are explicit qualification resumption and acceptance of the proposed batch limits, including unknown service quota debit.
If either decision is absent, retain all 192 development rows as planned and start no operational operation.
Phase 3B calibration remains incomplete. Phase 3C and sealed contents stay closed.

## October 18 owner approval and capacity stop

The owner answered "Yes, resume qualification" to the separate platform and live qualification request.
The owner answered "Approve limits and unknown quota" to the exact Phase 3B limit request.
These answers approve this batch's limits. They do not supply platform, toolchain, runtime, provider, dependency, or baseline observations.
The selected powered-off local VMware Ubuntu VM has 8 GiB configured RAM.
This proposal requires 16 GiB before preparation. The session stopped before VM startup.
The [capacity record](PHASE-3B-ADMISSION-CAPACITY-BLOCKED-2026-10-18.md) gives the exact checks and continuation.
