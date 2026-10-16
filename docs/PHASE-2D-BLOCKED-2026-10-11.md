# Phase 2D blocked report — 2026-10-11

Phase 2D remains blocked. The current source cannot pass the required installation check. Offline tests pass; Linux and live acceptance remain incomplete.

Base revision: `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc`. Branch: `codex/phase1-architecture`. Package version: `0.12.0`. The initial checkout was clean. Production source and tests remain unchanged.

The owner requested completion or an explicit list of causes. This session supplies the list with fresh evidence. It does not claim that a compatible solution is impossible.

## Causes

1. **The current filter conflicts with SQLite WAL.** The source filter denies `MAP_SHARED`, including a bounded ordinary WAL-index file. The offline driver confirms this result for x86_64 and aarch64. [Pinned Codex source](https://github.com/openai/codex/blob/d27764b82f7118f674371e6d6e76271d9d606edb/codex-rs/state/src/sqlite.rs#L285) selects WAL. [SQLite 3.51.3 source](https://github.com/sqlite/sqlite/blob/version-3.51.3/src/os_unix.c#L4914) uses `MAP_SHARED` for its ordinary WAL-index file. A denied mapping returns `SQLITE_IOERR_SHMMAP`. The installed runtime result remains unknown.
2. **Compatible storage enforcement is missing.** The filter checks mapping flags; it does not identify the backing object of the supplied FD. Removing the shared-mapping denial alone cannot prove bounds for anonymous shared memory, `/dev/zero`, and additional payload filesystems. [`EffectiveInstallation.require_effective_payload_growth()`](../src/crewshal/linux_production.py#L1826) therefore refuses admission and retains the full charge. [`CoordinatorStore._retain_observed_installation()`](../src/crewshal/durable.py#L948) cannot record observed installation through that refusal. Independent installed readback must establish compatible enforcement before startup.
3. **The installed execution chain is incomplete.** The [previous exact report](PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md#smallest-missing-capability-and-acceptance) records the missing finite parent entry, validator private view, and original admission linkage. The affected source bytes remain unchanged. Actual helper, root, loader, libraries, Codex, SQLite, authentication, tools, FDs, network, and proc identities still need qualification. Synthetic fixture success cannot supply these identities.
4. **The required Linux and live acceptance tests have not passed.** The changed profile must pass all twenty original cases twice. It must also cover every enabled native file tool. Live acceptance requires an actual readonly frozen candidate, a separate credential-free validator, and independent terminal evidence. The [current continuation](PHASE-2D-NEXT-SESSION-2026-10-10.md) requires separate approval of the exact operational batch. The incomplete implementation prevents preparation of that complete batch. All three compiler attempts remain consumed.

## Required next capability

Supply compatible installed storage enforcement and independent readback. Permit bounded ordinary WAL mappings. Bound anonymous shared memory, `/dev/zero`, and additional payload filesystems under the original logical and allocated limits.

Keep each storage total at or below `8589934592` bytes. Keep the original observer, timer, charges, handles, and unknown results. Preserve every original role limit, deadline, grace period, and terminal check. Do not authorize reuse from an empty scan, a pathname, a hash, or a successful command.

No accepted owner decision needs another answer. ADRs [0004](decisions/0004-retained-terminal-storage.md), [0005](decisions/0005-official-subscription-pilot.md), and [0006](decisions/0006-upfront-installation-charge.md) remain accepted. Ordinary bounded source work can continue. A material architecture change requires its own concrete proposal. Prepare the complete implementation before requesting operational approval.

## Fresh evidence and limits

The [verification record](qualification/phase-2d-blocked-verification-v1-20261011.json) contains commands, results, source hashes, environment, and graph limits.

The driver evaluates source instructions with hypothetical FDs. It does not open a WAL-index file or load a kernel filter.

- The compatibility driver reports `compatible=false` for both supported ABIs. Its exit status is zero because it produced the report.
- The focused bootstrap and installation suite passes 77 tests.
- The complete source suite passes 863 unique tests, including 722 Phase 2D tests. No test fails or skips.
- The complete suite and compatibility check use OS-denied network access, an empty inherited environment, and a fresh HOME.
- The host is macOS arm64 with Python 3.12.15. These checks do not qualify Linux effects.

The graph project is `Volumes-X10Pro-Crewshal`. Its generation is `2026-10-10T21:57:30Z`. Task-directed Verify checks found matching metadata for the evidence paths. The C helper has a recorded parse gap at line 78. Direct source inspection covered that line and the full filter. Two caller edges are heuristic; direct source inspection confirmed both calls. Clean coverage does not prove completeness.

This session ran no operational helper, compiler, Linux storage action, login, provider call, Jev call, VMware operation, or SSH operation. The previous installed-wheel and static results remain historical evidence. This session did not repeat them because production source and tests did not change.

AGENTS.md now records ASD-STE100 for human communication. Dated records remain intact. Version 0.12.0 remains unchanged. No commit or push occurred because the current continuation requires full Phase 2D acceptance before publication. No Phase 2E work occurred.

## Exact continuation inputs

Read these files in order:

1. [AGENTS.md](../AGENTS.md) and `/Users/hamedprooshani/.codex/RTK.md`.
2. [HANDOFF.md](HANDOFF.md), [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md), and [ARCHITECTURE.md](ARCHITECTURE.md).
3. This report and its [verification record](qualification/phase-2d-blocked-verification-v1-20261011.json).
4. [The previous prompt](PHASE-2D-NEXT-SESSION-2026-10-10.md) and its [exact input manifest](PHASE-2D-NEXT-SESSION-INPUTS-2026-10-10.json).
5. [The previous blocker](PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md) and its [immutable verification](qualification/phase-2d-effective-ownership-verification-v1-20261010.json).
6. Every source, test, accepted ADR, and historical evidence file listed in that manifest.

Use this initial prompt:

```text
Continue Phase 2D in /Volumes/X10Pro/Crewshal from revision
87ed7e6f6c766c7ff2df245ad05569558a9ca3bc on codex/phase1-architecture.
Preserve the current documentation changes and all other dirty files.
Use ASD-STE100 for every human explanation and decision request.
Read PHASE-2D-BLOCKED-2026-10-11.md and its exact continuation inputs.
Reproduce the shared-mapping conflict before changing the installation check.
Supply compatible installed storage enforcement with independent readback.
Finish the finite parent entry, validator private view, admission linkage, and installed identities.
Preserve the original limits, observer, timer, charges, handles, and unknown results.
Keep all accepted decisions closed. Do not repeat consumed compiler attempts.
Prepare complete source and a concrete operational batch before requesting its separate approval.
Pass all twenty original Linux cases twice and cover every enabled native file tool.
Complete the actual frozen-candidate and credential-free-validator live acceptance.
Publish only after full Phase 2D acceptance, then stop.
If blocked, record the exact missing capability with fresh evidence.
Do not begin Phase 2E.
```
