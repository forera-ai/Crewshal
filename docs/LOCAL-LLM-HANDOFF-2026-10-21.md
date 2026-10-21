# Crewshal handoff for local LLM development

Date: 2026-10-21. Scope: the next local source development session and Codex review.
This document summarizes current records. The linked records remain authoritative for their detailed evidence and decisions.
Read [HANDOFF.md](HANDOFF.md) first and [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) second.

## 1. Project and objective

Crewshal is an open-source experiment owned by [forera-ai](https://github.com/forera-ai/Crewshal).
The package and command name are `crewshal`. The name has one final `l`.
The project tests repository-aware coordination of coding runtimes and verifiable completion evidence.
Its first scope uses a local Python coordinator, passive discovery, SQLite state, and Codex and Claude Code CLI adapters.
The user confirms the project model and task authority. The coordinator separates runtime claims from captured evidence and verdicts.
The initial software scope supports Python and TypeScript project models.
Swift and .NET remain in the evaluation plan with unsupported capabilities recorded.
The [accepted architecture](ARCHITECTURE.md), [ADR 0002](decisions/0002-minimal-architecture.md), and [initial evaluation plan](../INITIAL-EVALUATION-PLAN.md) define the product direction.

## 2. Exact starting state

The clean starting branch is `codex/phase1-architecture` at `015e6b2dc0bda6f06628810aaf88038d52b70dbc`.
That revision contains package version `0.27.0` in `pyproject.toml` and `src/crewshal/__init__.py`.
The canonical remote is `https://github.com/forera-ai/Crewshal.git`.
This handoff checkpoint will advance the revision and patch version. Check Git before using the stated starting revision.
Never reset, revert, or overwrite later work because this document names an older revision.
The last software checkpoint is [Phase 3B local source review](PHASE-3B-LOCAL-REVIEW-CHECKPOINT-2026-10-21.md).
Its 126 focused local tests, Ruff, mypy, frozen package check, and offline installed wheel check passed.
These results apply to that checkpoint and its recorded environment. Rerun relevant checks after source changes.

## 3. Completed work and current phase

Phase 0 defined evidence, audit, and the initial evaluation proposal. Phase 1 accepted the minimal architecture.
Phase 2A delivered installable passive discovery and a confirmed project model.
Phase 2B delivered durable state, policy gates, and evidence contracts.
Phase 2C completed one bounded aarch64 Linux qualification profile with two complete runs.
That historical profile does not qualify changed runtimes, guests, configurations, or other platforms.
Phase 2D completed the first runtime software workflow with deterministic external fixtures.
Phase 2E completed the second adapter, independent review rules, and both role assignments in local software tests.
Their platform containment and live runtime behavior remain deferred under [ADR 0007](decisions/0007-core-development-before-platform-qualification.md).
Phase 3A froze the comparative source package under [ADR 0008](decisions/0008-agent-annotation-and-phase-3a-freeze.md).
Read its [package guide](evaluation/phase-3a-frozen/README.md) and [completion report](PHASE-3A-COMPLETION-2026-10-18.md).
The package binds 23 public artifacts and 768 planned units. Its bytes must remain unchanged.
Phase 3B is open. Phase 3C sealed evaluation and Phase 4 release remain future gates.

The current Phase 3B source chain is a read-only development ledger and local evidence checks.
It binds 192 planned development rows to the frozen schedule.
It checks attempt inventories, measurement claims, field-level file references, declared JSON paths, and exact local values.
The latest result includes inventory kind, byte count, SHA-256, field, file, path, status, and detail.
The implementation is [phase3b_development_ledger.py](../scripts/phase3b_development_ledger.py).
Its focused tests are [test_phase3b_development_ledger.py](../tests/acceptance/test_phase3b_development_ledger.py).
Local matches show byte and value consistency only. They do not authenticate an admitted run or file origin.
Every result keeps `admitted_source_review_required: true`, `evidence_verified: false`, and `execution_allowed: false`.
Missing paths, unsupported formats, and unequal values remain visible.

## 4. Acceptance gates and authority

[DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines each milestone and its independent acceptance checks.
Phase 3B needs admitted development corpus runs with complete accounting and preserved failures.
It also needs a protocol amendment frozen before any sealed task exposure.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The approved evaluation allowance remains zero money, zero subscription quota, and zero paid-host spending.
No local fixture result changes that allowance or authorizes a coding-runtime evaluation turn.
Actual provider identity, executable hashes, effective commands, B1 conformance, and platform behavior require later observation.
Keep unknown observations unknown. Do not convert missing usage to zero or a local match to verified evidence.
Do not expose private sealed tasks, their checks, hidden requirements, or the blinded condition map.
Private custody is outside Git at `private-store:phase3a-20261016/sealed/v1`.
Do not inspect or copy private custody during local source work.

[ADR 0009](decisions/0009-local-development-before-consolidated-linux-testing.md) controls the development order.
Use local macOS deterministic fixtures, offline checks, static checks, and installed-package checks where relevant.
Exclude Linux-specific test modules. Record each exclusion as deferred.
Do not boot, resume, inspect, reconfigure, reconnect, or install into either VMware Ubuntu guest.
Do not use a droplet or retrieve Linux toolchain artifacts for development preparation.
After planned source work passes locally, prepare one consolidated Linux qualification and test campaign.
The [campaign plan](PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-2026-10-18.md) is preparation, not current admission.
Any changed scope and spending require the recorded owner gates before that campaign acts.

The [local development boundary](PHASE-3B-LOCAL-DEVELOPMENT-BOUNDARY-2026-10-21.md) closed the guest staging attempt.
The host transport ISO exists. One isolated clone started and then appeared suspended.
The staging command was typed but not submitted. Its console line and guest state remain unknown.
Do not press Return on that line. Do not reuse the consumed [admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json).
Preserve both guests, ISO, archives, receipts, extraction images, records, charges, and unknown outcomes.
The historical archive charge is 10,008,484,533 bytes.
The package charge is 116,542,541 bytes. The cumulative conservative charge is 10,125,027,074 bytes.
No new transfer or cost follows from this handoff.

Discovery executes no repository instructions. Agent writes remain disabled until execution qualification passes.
Protect original dirty files, Git metadata, credentials, and raw private artifacts.
Do not copy private Forge code, prompts, schemas, paths, or artifacts.
Do not add a new model tool loop, orchestration framework, or adapter outside the active milestone.
Merge, deployment, and package-registry release remain separate owner gates.

## 5. Repository map and evidence entry points

The architecture document defines the conceptual contracts and threat model.
`src/crewshal/discovery.py` and `src/crewshal/model.py` support passive project modeling.
`src/crewshal/contracts.py`, `state.py`, `durable.py`, `gates.py`, and `candidate.py` support records and evidence rules.
`src/crewshal/integration.py`, `review.py`, `runtime.py`, `claude.py`, and `cli.py` support the software workflow.
The `src/crewshal/linux_*.py` files and `bootstrap_helper.c` belong to deferred platform work.
Use graph discovery and source reads before changing those paths. The graph is advisory and needs coverage checks.
`scripts/check_phase_3a_freeze.py` checks frozen public package consistency without executing tasks.
`scripts/phase3b_development_ledger.py` checks local Phase 3B declarations without granting execution authority.
`docs/evaluation/phase-3a-frozen/` contains the frozen public package.
`tests/acceptance/` contains focused offline fixtures and separate Linux-specific modules.

The prior [exact input index](PHASE-3B-LOCAL-REVIEW-INPUTS-2026-10-21.json) records 273 files at its stated entry revision.
It is a historical starting-input record. Later commits can change indexed files without corrupting that record.
Use this handoff's [input index](LOCAL-LLM-INPUTS-2026-10-21.json) for current transfer checks.
Confirm each file's current hash before relying on it. Report any mismatch and inspect the actual Git change.
Do not restore an older file merely to satisfy a historical hash.

## 6. Next local development session

Use [the start prompt](LOCAL-LLM-START-PROMPT-2026-10-21.md) as the local LLM's first instruction.
Start one bounded Phase 3B local source milestone. Do not start a new product phase in that session.
First inspect the current ledger and its tests for the next missing source review requirement.
Write a short change proposal with one observable acceptance condition and one refusal case.
Keep the change within the existing read-only ledger unless evidence shows another layer owns it.
Do not design an admission bypass or label any local artifact as authenticated execution.
Implement the smallest accepted source change and independent local fixtures.
Run focused tests, relevant regressions, Ruff, mypy, the frozen package checker, and an offline wheel check when relevant.
Record commands, exit results, environment, revision, failures, and deferred checks.
If no safe local requirement remains, record that finding and prepare the consolidated campaign for later owner review.
Do not run that campaign during source development.

The local LLM prepares the patch and a review packet for Codex before final publication.
The packet names scope, changed files, accepted checks, failed checks, risks, unresolved gates, and the exact diff.
Codex reviews the patch and tests against this handoff and the authoritative records.
Resolve review findings before the milestone closes.
This review step does not waive any project acceptance or owner gate.

## 7. Publication and next boundary

Use ASD-STE100 for new human-readable project text. Use complete active sentences and consistent terms.
Keep procedural sentences at 20 words or fewer. Keep descriptive sentences at 25 words or fewer.
Use `rtk` for shell commands; use `rtk proxy` when raw output matters.
Keep historical records intact and append new dated evidence instead of changing old results.
At a completed or blocked boundary, update `README.md`, `CHANGELOG.md`, and `docs/HANDOFF.md`.
Bump the package version by SemVer and synchronize `pyproject.toml` with `crewshal.__version__`.
Write the next prompt and exact input list. Check links, whitespace, version values, and Git status.
Commit a coherent checkpoint and push the current branch under standing owner authorization.
Do not force-push, merge, deploy, or publish a package.
Stop after the milestone and its publication ceremony.

If a required gate fails, preserve the failure and keep the phase open.
Give the next agent the smallest missing decision or capability and an exact continuation prompt.
The local LLM must present its review packet before publication, so Codex can act as supervisor and reviewer.

## 8. Handoff checkpoint verification

This documentation checkpoint ran on macOS 27.2 arm64 with CPython 3.12.15.
The base revision was `015e6b2dc0bda6f06628810aaf88038d52b70dbc` on `codex/phase1-architecture`.
The 31 transfer files matched their sizes and SHA-256 digests after the final handoff edit.
The new handoff links resolved. `git diff --check` reported no whitespace error.
The frozen package checker reported 23 consistent artifacts and 768 planned units.
It kept both execution flags false. The focused ledger suite passed 18 tests.
An offline wheel build and target install succeeded for `crewshal-0.27.1-py3-none-any.whl`.
An isolated installed import and package metadata check both reported `0.27.1`.
No Linux-specific test module ran. Linux and live qualification remain deferred.
No guest, archived tool, native coding, evaluation, paid host, or metered API action ran.
