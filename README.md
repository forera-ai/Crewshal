# Crewshal

**Coordinate coding agents. Verify their work.**

Crewshal (pronounced like **crucial**) is an early open-source project exploring repository-aware coordination and verifiable engineering controls for AI-assisted software development.

The hypothesis: a human-confirmed model of an unfamiliar repository can reduce manual workflow setup while supporting consistent boundaries, validation and completion evidence across different coding runtimes.

## Current status

**Phases 0, 1 and 2A complete; Phase 2B is next.** An installable Python package now exposes passive manifest discovery, explicit human correction/confirmation, versioned validated models and external coordinator state. Synthetic offline acceptance tests cover its bounded behavior. Runtime execution, agent writes, trusted evidence gates and comparative evaluation remain future work. Numerical evaluation thresholds are not demonstrated results.

The proposal uses a local Python coordinator with Codex and Claude Code adapters, subject to capability and isolation qualification. Implementation proceeds in bounded sessions. Agent writes require execution qualification; paid evaluation requires a confirmed protocol and spending ceiling.

## Intended workflow

1. Inspect an unfamiliar repository without executing its instructions.
2. Propose project facts, validation commands and engineering boundaries with provenance and uncertainty.
3. Ask the human operator to correct and confirm the project model.
4. Coordinate bounded work through existing coding runtimes.
5. Capture deterministic checks and independent review where required.
6. Support completion with evidence tied to the candidate revision.

Steps 1–3 are implemented for the bounded Python/TypeScript formats documented in [the development guide](docs/DEVELOPMENT.md). Steps 4–6 remain proposed. The owner retains authority over consequential actions. Implementation is clean and independent; proprietary predecessor code, prompts, configurations and artifacts are excluded.

## Development sessions

Work proceeds one phase or major milestone per session. Read the [rolling handoff](docs/HANDOFF.md) for current state and the next-session prompt, and the [development plan](docs/DEVELOPMENT-PLAN.md) for standalone acceptance gates. [AGENTS.md](AGENTS.md) records the persistent session contract. The next session is Phase 2B: durable state, pure gates and trusted evidence contracts.

## Try passive initialization

Python 3.12+ is required; macOS arm64/Python 3.12.14 is the verified environment. From this checkout:

```sh
rtk proxy uv venv --python python3.12 .venv
rtk proxy uv pip install --python .venv/bin/python --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python .venv/bin/python --no-deps -e .
rtk proxy .venv/bin/crewshal --help
rtk proxy .venv/bin/crewshal init /path/to/repository --interactive
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a
```

Without `--interactive` or an explicit decision batch, facts remain pending. No discovered command runs. State stays outside the target repository; exports require `--export` and never become execution approvals. See [setup, limits and verification](docs/DEVELOPMENT.md).

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
