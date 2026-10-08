# Crewshal

**Coordinate coding agents. Verify their work.**

Crewshal (pronounced like **crucial**) is an early open-source project exploring repository-aware coordination and verifiable engineering controls for AI-assisted software development.

The hypothesis: a human-confirmed model of an unfamiliar repository can reduce manual workflow setup while supporting consistent boundaries, validation and completion evidence across different coding runtimes.

## Current status

Local package version: **0.9.0**. See [CHANGELOG.md](CHANGELOG.md) for version history.

**Phases 0, 1, 2A, 2B and 2C complete.** Passive discovery, confirmed project models, private SQLite state, recovery contracts and deterministic evidence gates are implemented. The local offline suite has **141 tests**, verified on macOS with network denied.

The accepted direct Linux qualification route passes all **20 original cases twice on one complete v18 profile**, using the pinned native Codex runtime, official Responses proxy and synthetic local provider fixture. Both actual native file tools, `exec_command` and `write_stdin`, are exercised. Original grants and resource limits remain unchanged. The independent reader checks full records, source/configuration bindings, containment, credential mediation, validator isolation, cancellation and deadlines. See [the complete assessment and reproduction commands](docs/PHASE-2C-COMPLETION-ASSESSMENT.md).

Qualification applies to the observed local Linux aarch64 profile. Windows and macOS runtime compatibility remains unverified. Historical native/proxy subsets, failures and prepared variants remain intact; they do not combine into this pass. The lost v5 cause and original cleanup remain unknown. Current continuation cleanup is independently observed; the VM remains running and SSH is disconnected.

The [portable record audit](docs/PHASE-2C-OFFLINE-AUDIT.md) adds bounded offline consistency checks and refuses altered, incomplete or malformed bundles. Every audit and qualification decision retains false execution permission; the audit also always returns false runtime verification. No runtime launcher, production agent write, paid model call, deployment or registry release is included. Phase 2D needs its separate execution authorization.

The proposal uses a local Python coordinator with Codex and Claude Code adapters, subject to capability and isolation qualification. Implementation proceeds in bounded sessions. Agent writes require execution qualification; paid evaluation requires a confirmed protocol and spending ceiling.

## Intended workflow

1. Inspect an unfamiliar repository without executing its instructions.
2. Propose project facts, validation commands and engineering boundaries with provenance and uncertainty.
3. Ask the human operator to correct and confirm the project model.
4. Coordinate bounded work through existing coding runtimes.
5. Capture deterministic checks and independent review where required.
6. Support completion with evidence tied to the candidate revision.

Steps 1–3 are implemented for the bounded Python/TypeScript formats documented in [the development guide](docs/DEVELOPMENT.md). [Durable state and evidence rules](docs/STATE-AND-GATES.md) support the contracts for steps 4–6; those steps still have no runtime launcher or check executor. The owner retains authority over consequential actions. Implementation is clean and independent; proprietary predecessor code, prompts, configurations and artifacts are excluded.

Historical SBX investigation: the owner [approved the exact operational resource envelope](docs/RESOURCE-APPROVAL-AND-FREEZE-STATUS.md). A [new current host and immutable candidate artifacts](docs/CURRENT-HOST-IDENTITY-PREPARATION.md) are verified. Package **0.8.8** records [approved bounded discovery and actual supported-create refusal](docs/GUEST-DISCOVERY-ASSESSMENT.md). Prospective aggregate/controller/device bounds are observed in fresh private services; KVM HLT passes twice per service after an initial device-policy failure. Both mountless SBX create attempts return `401 Unauthorized` requiring Docker sign-in. Login is excluded by the approved discovery scope, so no SBX guest, complete operational freeze or inner qualification is delivered. Historical discovery/resource approval is resolved; current host retention is superseded by the 2026-10-05 cost policy. Historical profiles remain immutable. Version 0.8.10 preserves exact executed-source trailing bytes through narrowly scoped whitespace attributes; no host rerun or qualification change.

## Development sessions

Work proceeds one phase or major milestone per session. Read the [rolling handoff](docs/HANDOFF.md), [development plan](docs/DEVELOPMENT-PLAN.md), [next Phase 2D prompt and exact inputs](docs/PHASE-2D-NEXT-SESSION-2026-10-08.md), and [preserved Phase 2C input index](docs/PHASE-2C-ACTIVE-CONTINUATION.md). [AGENTS.md](AGENTS.md) records the persistent session contract. The owner's October 8 local VMware resumption superseded the earlier test stop. That qualification batch is complete; this session stops at 2C.

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

Existing Phase 2A JSON state requires explicit `--migrate-state` on `init` or `show`; the original private JSON remains unchanged as a backup. New writes use SQLite. Unknown database/record versions are refused. No verdict or qualification record grants execution; production runtime startup and agent writes require separate authorization in Phase 2D.

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
