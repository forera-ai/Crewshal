# Consolidated Linux qualification and test campaign plan

Date: 2026-10-18. Status: prepared for later admission review; no execution authority.
This plan follows [ADR 0009](decisions/0009-local-development-before-consolidated-linux-testing.md).
It does not restart Linux work during source development.

## Scope and fixed inputs

Run one later campaign for exact platform qualification, native runtime conformance, baseline checks, and Phase 3B development calibration.
Use the frozen `phase3a-20261016-v1` package without changing its bytes.
The package index binds 23 artifacts and 768 planned units.
The selected calibration schedule contains 192 development rows across twelve tasks and four repositories.
The 576 sealed rows remain unexposed and outside this campaign.
Use the four selected source revisions, archives, task checks, schedule, roles, and condition contracts in the [admission proposal](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md).
Use the production Crewshal interfaces for condition P.
Keep unsupported Swift and .NET paths visible in the planned denominator.

This campaign has four sequential stages:

1. Resolve admission limits and bind exact toolchain, source, dependency, guest, and runtime identities.
2. Qualify the exact Linux platform, credential separation, native tools, validator, and all applicable containment cases.
3. Run actual baseline conformance for each enabled B0, B1, and B2 comparison channel.
4. Run only admitted development rows in frozen order. Record failures and any prospective protocol correction before sealed exposure.

Stop when a required earlier stage fails or remains unknown.
No stage inherits a pass from an earlier platform or different profile.

## Commands and admission

Before any guest action, verify current checkout and frozen inputs on the Mac:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
```

After the owner reopens Linux work and approves any changed scope, use the read-only guest admission commands in the [Phase 3B proposal](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md#required-inputs-and-proposed-preparation-commands).
Stop on a missing or different selected tool, less than four CPUs, insufficient guest-visible RAM, or less than 40 GiB free disk.
Bind actual command paths, executable hashes, configuration bytes, operating-system identity, and supported resource controls before installation or runtime use.
Run no retrieval until the transfer ledger permits it.

The proposal contains the exact selected task `argv`, working directories, prerequisites, and 900-second check limits.
Do not rewrite those commands or broaden their test selectors.
The proposal's archive retrieval pattern needs bound URLs, digests, byte counts, and an approved transfer balance before use.
Prepare and verify a safe extraction command and inventory comparison before extracting an archive.
Bind the B1 manual script bytes and operator steps before B1 conformance.
Bind effective launch commands before native or Crewshal turns.
These commands and bindings are preparation requirements, not current passes.

## Resource and cost limits

The owner approved the earlier proposal's historical batch limits. ADR 0009 now stops Linux work until a later campaign is admitted.
Do not interpret the dated approval as current execution authority.

| Resource | Recorded limit or state |
| --- | --- |
| Paid host and metered API | USD 0 each. |
| Subscription turns | At most 256 Codex and 256 Claude Code submissions, including qualification and remediation. |
| API-equivalent estimate | USD 200 planning ceiling. Stop if unknown usage prevents a reliable next-turn check. |
| Subscription quota debit | Unknown; the prior owner approval accepted this uncertainty for the dated proposal. Rebind it for the later campaign. |
| Download and retained data | Original 8 GiB limits. The old download allowance has zero conservative remaining balance. |
| Guest preparation | One task unit at a time; four CPUs, 12 GiB RAM, and 24 GiB disk for preparation. |
| Native batch | Unchanged qualified limits, including 600 seconds and the 768 MiB aggregate charge. |
| Separate validator | Four CPUs, 8 GiB RAM, 8 GiB disk, and 900 seconds per frozen check. |
| Time | Eight active preparation hours; 24 elapsed preparation hours; 90 minutes per task unit; 14 days after the first qualified turn. |

The [toolchain amendment boundary](PHASE-3B-TOOLCHAIN-AMENDMENT-BOUNDARY-2026-10-18.md) retains the exact known transfer and storage ledger.
The guest and ISO directories had 9,093,566,464 allocated host bytes at the last recorded readback.
The guest reported 16,728,174,592 visible memory bytes, below 16 GiB.
The known ISO and checksum consumed 3,825,518,142 transfer bytes.
The installer transfer has no exact upper bound; charge it against the full remaining allowance.
Its proposed 16 GiB guest-visible RAM rule, 40 GiB VM-plus-ISO ceiling, and 16 GiB cumulative transfer ceiling lack owner approval.
Do not use those proposed values as current allowances.
The installed guest's selected tools, dependency closure, package rights, provider identities, and executable hashes remain unknown.
No droplet or new infrastructure enters this campaign without a separately approved exact batch.

## Evidence and cleanup

Record each stage's exact command, environment, input digest, exit, output digest, duration, charge, and failure.
Keep measured billing, API-equivalent estimates, service quota observations, and unknown usage separate.
Use one fresh source copy and isolated writable cache per scheduled row.
Store private receipts under an owned `0700` batch root with `0600` files.
Keep credentials, private paths, and raw provider logs outside Git.

After capture, stop and inspect owned processes, mounts, and file handles.
Remove only verified batch-owned source copies, caches, and dependency scratch.
Retain unresolved resources and charge their full reservations.
Preserve both historical guests, the ISO, old records, and sealed custody.
Retain private raw evidence until an owner disposal decision.

The next preparation session must finish exact input binding and seek approval for changed limits before any Linux action.
This plan does not qualify a platform, authorize a provider turn, or start calibration.
