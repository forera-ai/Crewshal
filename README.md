# Crewshal

**Coordinate coding agents. Verify their work.**

Crewshal (pronounced like **crucial**) is an early open-source project exploring repository-aware coordination and verifiable engineering controls for AI-assisted software development.

The hypothesis: a human-confirmed model of an unfamiliar repository can reduce manual workflow setup while supporting consistent boundaries, validation and completion evidence across different coding runtimes.

## Current status

Local package version: **0.8.5**. See [CHANGELOG.md](CHANGELOG.md) for version history.

**Phases 0, 1, 2A and 2B complete; Phase 2C is blocked.** The Python package delivers passive discovery, explicit human decisions, private SQLite state with transactional version checks, supported migration with backup, inert launch-intent recovery contracts and deterministic gates over coordinator-captured evidence. The offline suite has 78 synthetic cases. Docker Desktop is connected; nine bounded filesystem/environment cases and four separate lifecycle/validator cases passed twice. These complementary subsets are not a combined qualified runtime. A separate synthetic network subset passed twice with IPv4/IPv6 TCP, UDP and DNS-wire attempts plus independent positive sink controls. Native runtime network/configuration and credential mediation remain unproved. The frozen [SBX resource/configuration protocol](docs/SBX-RESOURCE-CONFIGURATION-PROTOCOL.md) preserves 128 MiB worker limits, records the 512 MiB outer proposal and refuses operational launch until credential-store isolation and inner enforcement are demonstrated. Two help-only assessments pass. A new [disposable Linux credential-store preflight](docs/BROKER-ENVIRONMENT-ASSESSMENT.md) passes twice with synthetic secrets only, demonstrating file-store isolation from macOS Keychain. Its Docker Desktop fixtures have no observed KVM device/sysfs entry; a later [temporary VPS capability check](docs/KVM-HOST-ASSESSMENT.md) demonstrates KVM VM/vCPU creation and actual trusted HLT execution twice on Ubuntu x86_64. Operational SBX host configuration, inner enforcement and request authority remain unqualified. The [operational proposal](docs/SBX-OPERATIONAL-PROPOSAL.md) now pins the official x86_64 bundle and presents explicit outer/inner ceilings. The owner confirmed that the temporary VPS was deleted. A new [readiness checklist and bound identity snapshot](docs/PHASE-2C-READINESS.md) records replacement-host requirements, unresolved operational identities and independent inner-enforcement acceptance checks. The [first replacement](docs/REPLACEMENT-HOST-ASSESSMENT.md) fails available-memory admission. A [second replacement host and Linux help preflight](docs/AMD64-HOST-PREFLIGHT.md) passes KVM twice, sampled memory/disk headroom and source-bound SBX version/help twice. The exact resource envelope is now approved; operational identities and effective quotas/inner controls remain unresolved; no daemon or native runtime was started. No new whole-runtime operational criterion passes. See [protocol evidence and remaining gate](docs/SBX-PROTOCOL-ASSESSMENT.md). See [network evidence and preparation limits](docs/NETWORK-SUBSTRATE-PROBES.md). See [Linux substrate evidence](docs/LINUX-SUBSTRATE-PROBES.md). Public Orka helper probes retained synthetic ambient credentials and hook settings. Runtime execution, agent writes and comparative evaluation remain gated. See [qualification evidence and resumption conditions](docs/EXECUTION-QUALIFICATION.md). Numerical evaluation thresholds are not demonstrated results.

The proposal uses a local Python coordinator with Codex and Claude Code adapters, subject to capability and isolation qualification. Implementation proceeds in bounded sessions. Agent writes require execution qualification; paid evaluation requires a confirmed protocol and spending ceiling.

## Intended workflow

1. Inspect an unfamiliar repository without executing its instructions.
2. Propose project facts, validation commands and engineering boundaries with provenance and uncertainty.
3. Ask the human operator to correct and confirm the project model.
4. Coordinate bounded work through existing coding runtimes.
5. Capture deterministic checks and independent review where required.
6. Support completion with evidence tied to the candidate revision.

Steps 1–3 are implemented for the bounded Python/TypeScript formats documented in [the development guide](docs/DEVELOPMENT.md). [Durable state and evidence rules](docs/STATE-AND-GATES.md) support the contracts for steps 4–6; those steps still have no runtime launcher or check executor. The owner retains authority over consequential actions. Implementation is clean and independent; proprietary predecessor code, prompts, configurations and artifacts are excluded.

The owner has [approved the exact operational resource envelope](docs/RESOURCE-APPROVAL-AND-FREEZE-STATUS.md). A [new current host and immutable candidate artifacts](docs/CURRENT-HOST-IDENTITY-PREPARATION.md) are verified. Full operational configuration/freeze and inner enforcement remain unqualified. A [bounded network-denied daemon diagnostic](docs/DAEMON-CONFIG-DIAGNOSTIC-PROPOSAL.md) awaits an explicit owner decision. Keep the current droplet until all required host work finishes. Historical proposal/readiness documents remain immutable.

## Development sessions

Work proceeds one phase or major milestone per session. Read the [rolling handoff](docs/HANDOFF.md) for current state and the next-session prompt, and the [development plan](docs/DEVELOPMENT-PLAN.md) for standalone acceptance gates. [AGENTS.md](AGENTS.md) records the persistent session contract. The next session resumes Phase 2C: supply current authorized host access, freeze operational identities and qualify inner enforcement before native runtime and credential mediation checks. Use [the resumption prompt and exact inputs](docs/PHASE-2C-RESUME-PROMPT.md).

Each completed milestone ends with version, README, changelog and handoff updates, followed by a commit and remote branch push. See [the standing publishing rules](AGENTS.md). Development stops at the milestone boundary.

## Try passive initialization

Python 3.12+ is required; macOS arm64/Python 3.12.14 is the verified environment. From this checkout:

```sh
rtk proxy uv venv --python python3.12 .venv
rtk proxy uv pip install --python .venv/bin/python --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python .venv/bin/python --no-deps -e .
rtk proxy .venv/bin/crewshal --help
rtk proxy .venv/bin/crewshal init /path/to/repository --interactive
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_substrate
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_lifecycle
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_network
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_protocol
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_broker_environment
```

Without `--interactive` or an explicit decision batch, facts remain pending. No discovered command runs. State stays outside the target repository; exports require `--export` and never become execution approvals. See [setup, limits and verification](docs/DEVELOPMENT.md).

Existing Phase 2A JSON state requires explicit `--migrate-state` on `init` or `show`; the original private JSON remains unchanged as a backup. New writes use SQLite. Unknown database/record versions are refused. No verdict or qualification record grants execution; Phase 2C remains the write gate.

## Research and decisions

- [Product hypothesis and owner brief](PRODUCT-HYPOTHESIS.md)
- [Competitive landscape and naming](COMPETITIVE-LANDSCAPE.md)
- [Predecessor concept audit](AUDIT.md)
- [Initial evaluation plan](INITIAL-EVALUATION-PLAN.md)
- [Phase 0 closure and remaining gates](docs/PHASE-0-CLOSURE.md)
- [Accepted minimal architecture](docs/ARCHITECTURE.md)
- [Accepted architecture decision](docs/decisions/0002-minimal-architecture.md)
- [Accepted name and repository initialization](docs/decisions/0001-name-and-repository.md)

The current recommendation is to narrow the product to confirmed repository adaptation and portable evidence, and evaluate it against simpler workflows and existing tools before broader development.

## Get the repository

```sh
git clone https://github.com/prooshani/Crewshal.git
cd Crewshal
```

Use **Crewshal** as the display name and `crewshal` for local command and package identifiers. The package has not been published or its index name reserved.

## Contributing

Contributions should follow the active milestone and its acceptance gates. Open an issue to discuss architecture or runtime changes before submitting them. Keep private source, credentials and raw confidential run artifacts out of the repository.

## License

[Apache License 2.0](LICENSE). Copyright 2026 Hamed Prooshani and Crewshal contributors.
