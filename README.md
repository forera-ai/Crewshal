# Crewshal

**Coordinate coding agents. Verify their work.**

Crewshal (pronounced like **crucial**) is an early open-source project exploring repository-aware coordination and verifiable engineering controls for AI-assisted software development.

The hypothesis: a human-confirmed model of an unfamiliar repository can reduce manual workflow setup while supporting consistent boundaries, validation and completion evidence across different coding runtimes.

## Current status

**Phase 0 and Phase 1 complete; Phase 2A is next.** The owner authorized advancing into implementation on 2026-10-02. This repository contains research, naming decisions and a minimal architecture proposal. There is no executable runtime, installable package or working CLI yet. Proposed capabilities and numerical evaluation thresholds are not demonstrated results.

The proposal uses a local Python coordinator with Codex and Claude Code adapters, subject to capability and isolation qualification. Implementation proceeds in bounded sessions. Agent writes require execution qualification; paid evaluation requires a confirmed protocol and spending ceiling.

## Intended workflow

1. Inspect an unfamiliar repository without executing its instructions.
2. Propose project facts, validation commands and engineering boundaries with provenance and uncertainty.
3. Ask the human operator to correct and confirm the project model.
4. Coordinate bounded work through existing coding runtimes.
5. Capture deterministic checks and independent review where required.
6. Support completion with evidence tied to the candidate revision.

This workflow is the proposed experiment, not existing functionality. The owner retains authority over consequential actions. The project will use a clean, independent implementation; proprietary predecessor code, prompts, configurations and artifacts are excluded.

## Development sessions

Work proceeds one phase or major milestone per session. Read the [rolling handoff](docs/HANDOFF.md) for current state and the next-session prompt, and the [development plan](docs/DEVELOPMENT-PLAN.md) for standalone acceptance gates. [AGENTS.md](AGENTS.md) records the persistent session contract. The next session is Phase 2A: passive discovery and human confirmation.

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

Use **Crewshal** as the display name and `crewshal` for future command and package identifiers. Those package names have not been reserved or published.

## Contributing

At this stage, contributions should focus on research corrections, reproducible comparative evidence and evaluation design. Open an issue to discuss architecture or runtime implementation before submitting it. Keep private source, credentials and raw confidential run artifacts out of the repository.

## License

[Apache License 2.0](LICENSE). Copyright 2026 Hamed Prooshani and Crewshal contributors.
