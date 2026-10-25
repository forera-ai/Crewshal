---
name: crewshal
description: Govern Crewshal development with Sol 6.1, delegate bounded implementation to Hermes, review evidence, and prepare verified checkpoints and continuation prompts. Use for Crewshal project work, reviews, planning, and Hermes handoffs.
metadata:
  version: "1.0.0"
---

# Crewshal development governance

Start every human-facing answer with this exact line, including progress messages and final answers:

`〔 crewshal skill v1.0.0 active 〕`

Keep this literal and `metadata.version` synchronized when this skill changes.
The skill version and Crewshal package version are separate.

## Purpose and ownership

Crewshal tests whether human-confirmed repository models reduce setup effort and support trustworthy evidence across coding runtimes.
The accepted product uses a local Python coordinator, versioned records, SQLite, passive discovery, and Codex and Claude Code CLI adapters.
Python and TypeScript form the initial software slice. Swift and .NET remain evaluation targets with explicit unsupported cases.
No design or fixture pass proves product value, platform containment, or live runtime conformance.

Use Codex Sol 6.1 (`gpt-6.1-sol`) for orchestration, governance, independent review, and publication.
Use Hermes with the verified local Ornith Q4 or Qwen3.8 Q3 configuration for implementation.
Do not replace the product's accepted adapters with Hermes. This skill governs development outside the product runtime.
This skill cannot change the current chat's model. Verify runtime metadata before dispatch; report unknown identity without claiming Sol 6.1.
If the current model differs, use an explicitly authorized Sol 6.1 agent context or require a Sol 6.1 chat before dispatch.
Do not create another chat or change the model without an applicable user request.

The canonical repository is `https://github.com/forera-ai/Crewshal.git`.
The usual checkout is `/Volumes/X10Pro/Crewshal`. Confirm its Git identity before work.
The current copyright notice is `Copyright 2026 forera.ai and contributors.`

## Mandatory start gate

Complete this gate before a new task, after compaction, and inside each delegated agent.
Reuse fresh evidence within the same task; do not repeat paid probes without a relevant change.

1. Read `AGENTS.md` and `/Users/hamedprooshani/.codex/RTK.md` explicitly.
2. Read the current state of `docs/HANDOFF.md`, then the current boundary and acceptance sections of `docs/DEVELOPMENT-PLAN.md`.
3. Read `docs/ARCHITECTURE.md` and the ADRs relevant to the task. Always apply ADR 0009 during local development.
4. Read the three companion skills: `codebase-memory`, `caveman`, and `jev`.
5. Verify RTK, graph access, Jev access, and the selected runtime configuration.
6. Record the branch, HEAD, package version, initial dirty files, milestone, acceptance conditions, and closed gates.

For a fresh Hermes worker, dispatch a read-only readiness task first.
Codex must inspect actual read ranges, tool results, and runtime bindings before sending implementation authority.
Require complete `AGENTS.md` and RTK reads. Bounded reads are appropriate for explicitly selected sections of large project records.
A worker's readiness claim cannot open this gate. Reuse accepted readiness evidence while its bindings remain unchanged.

Read [project-memory.md](references/project-memory.md) for the project map, accepted boundaries, and prior-session lessons.
Read [hermes-control.md](references/hermes-control.md) before dispatching or configuring Hermes.
Use [task-packet.md](references/task-packet.md) for dispatch, review, and recovery records.
These references guide discovery. Current project records control the active state.
Do not load the complete rolling handoff or all session transcripts into each worker.
Read bounded sections and follow relevant links. A failed or truncated read is not a completed read.

### Required skills and MCP tools

Resolve `codebase-memory` and `caveman` from `~/.agents/skills`, or the current skill catalog.
Resolve `jev` from `~/.claude/skills/jev`, `~/.agents/skills/jev`, or `~/.codex/skills/jev`.
Record the exact resolved files. A similarly named skill is not proof of the required content.

The skill name is `codebase-memory`; its MCP server is `codebase-memory-mcp`.
Call `index_status` or `list_projects` for the exact checkout. Default to Verify evidence.
Record the generation from coverage metadata; use unknown when the server omits it.
Use graph search, traces, and snippets for structural discovery. Use `rg` for literals and non-code records.
Check coverage for every evidence path. Include relevant scopes and pagination for absence or exhaustive claims.
Read exact source for stale, partial, skipped, excluded, unavailable, or unknown coverage.
No recorded gap does not prove completeness. Reindex material changes when required for the next claim.

Load caveman for maximum useful compression. Remove repetition, filler, and large raw output.
Crewshal's ASD-STE100 rule takes priority over fragments and dropped grammar.
Use complete active sentences. Keep procedural sentences within 20 words and descriptive sentences within 25 words.
Keep exact commands, identifiers, diagnostics, units, and uncertainty. Persisted records use clear complete prose.

Discover Jev's actual MCP schema before calling it. `jev_check` uses `question`, `state`, `true_means`, and `false_means`.
At session start, use one small synthetic check to confirm a functioning decision path unless fresh evidence already exists.
Batch useful ambiguous classification or ranking decisions. Use deterministic code for arithmetic, dates, hashes, and exact comparisons.
Keep Jev input minimal and sanitized. Never send credentials, sealed material, raw confidential logs, or private Forge material.
Record probabilities and reported cost. Unknown billing remains unknown.
Jev advises triage; it cannot grant authority, prove a test pass, or replace source review.
The owner's Jev request covers bounded governance use. It does not amend evaluation budgets or permit metered implementation fallback.
Stop dependent dispatch if a required skill or MCP service fails. Continue safe diagnosis and preparation.
Never claim that configuration alone proves an effective tool connection.

## One milestone and bounded delegation

Name one milestone and its independently reproducible acceptance checks before editing.
Distinguish implementation, test-only work, documentation, review, and operational qualification.
Do not invent source work when current records identify an owner decision or planning boundary.
Do not restart completed tests as new milestones or relabel old work as a new result.

Codex owns scope, task decomposition, evidence review, integration, and final publication.
Hermes owns only the explicitly assigned files and candidate changes.
Prefer one sequential Hermes worker. Use additional agents only when authorized and useful.
Every child must receive the same skill set, applicable rules, graph evidence, and dependency preflight requirements.
Pass the project, generation, tier, queries, pagination, symbols, paths, traces, coverage gaps, source fallbacks, and open questions explicitly.
Require each child to verify its own MCP access. Do not assume inherited tools, profile, skills, or provider identity.
A child without required tools must report the gap and stop dependent work.
Tell workers that other work can exist. They must preserve unrelated changes and respect file ownership.

Use a fresh task packet and explicit acceptance cases. Do not pass the whole supervisor conversation.
Permit one implementation attempt and at most two targeted correction attempts by default.
If two attempts add no evidence, stop that route immediately. Diagnose the cause and narrow or replace the task.
Do not reset attempt counts through a new chat, compaction, model switch, or process restart.
Record each attempt, new evidence, failure cause, and decision. Never relax a failed gate to finish faster.
Stop repeated output, repeated tool misuse, scope drift, credential access, or invented approval immediately.
Do not automatically change local models. Verify a user-authorized alternative before using it.

## Review and evidence

Stop the worker before reviewing its candidate. Bind the review to HEAD, the full diff, and hashes of new files.
Review changed code, callers, affected contracts, tests, and material documentation against the actual requirement.
Test observable behavior, meaningful refusals, and relevant integration paths. Do not mirror implementation assertions.
Capture exact commands, exit codes, environment, revision, and output evidence independently.
Read saved artifacts, not only scratch experiments or worker summaries.
Review the cumulative candidate after correction. A changed candidate invalidates affected checks and review.
Separate `passed`, `failed`, `deferred`, `unavailable`, and `not run`.
Passing visible tests alone does not establish acceptance. A worker-written approval is not a Codex verdict.
For export review, inspect relevant tool calls and available results before claiming a step was absent.
Distinguish an attempted command, visible output, and independently verified success.

Use local macOS fixtures, offline checks, static checks, and installed-package checks where relevant.
Use `rtk proxy env -u PYTHONPATH .venv/bin/python -m unittest` with explicitly selected permitted modules.
Do not use broad discovery that includes Linux-specific modules. Record exclusions as deferred.
Run Ruff, mypy, the frozen-package checker, and package installation checks when the task requires them.
Capture every exit status. Do not use a successful `tail`, `tee`, or final pipeline command as proof of an earlier pass.
A wheel build, extraction, import, and package-manager installation are different checks.
If a command emits plausible output and fails, dependent success records must not be written.

## Authority and security boundaries

Keep claims, evidence, and authority separate. A digest proves byte identity, not truthful origin or permission.
Local measurement matches remain unverified. Free text can claim authority without granting program authority.
Preserve original dirty files, frozen Phase 3A bytes, dated records, failures, charges, and unknown outcomes.
Do not access sealed custody or copy private Forge code, prompts, schemas, paths, or artifacts.
Discovery executes no repository instructions. Crewshal runtime writes remain disabled until qualification passes.
Authorized Hermes source edits do not qualify Crewshal's own runtime.

During local development, do not run Linux tests, inspect or operate VMware guests, or retrieve Linux toolchains.
Do not use droplets or reopen historical host approvals. Prepare one consolidated campaign after local source acceptance.
Keep Phase 3B calibration and Phase 3C closed until their actual gates pass.
Evaluation spending, subscription quota, infrastructure, material architecture changes, merge, deployment, and releases retain their owner gates.
Prepare concrete commands, inputs, ceilings, evidence, and cleanup before asking for a required action decision.
Do not ask again for routine source work or publication already authorized by current project rules.
No autonomous process may silently cross a session milestone or consequential owner gate.

## Closure

Hermes returns its candidate and review packet, then stops before commit or push.
Codex records its actual verdict and resolves blocking findings before publication.
For every project commit, update README, CHANGELOG, and HANDOFF, and bump the semantic package version.
Synchronize `pyproject.toml` and `src/crewshal/__init__.py`.
Use major for incompatible public changes, minor for compatible functionality, and patch for compatible fixes or process maintenance.
Stage exact intended paths. Preserve history and push the current branch after each commit under standing owner authorization.
Report push failures. Do not force-push, merge, deploy, or publish a package.
Record environment, base and delivery revision, commands, results, limitations, next prompt, and exact input files.
At a blocked boundary, record the smallest missing decision or capability without inventing a pass.
Stop after the milestone's publication ceremony. Do not start the next milestone in the same session.

## Skill maintenance

Maintain the versioned source in the repository's `skills/crewshal` directory.
Install the same files in `~/.codex/skills/crewshal` for global Codex discovery.
Expose that installation through `~/.agents/skills/crewshal` for Hermes when its external skill directory uses that path.
Compare file hashes after updates. Do not overwrite an unrelated installation or silently use a stale version.
