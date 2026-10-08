# 0002 — Local adaptation and evidence experiment

Date: 2026-10-02. Status: **accepted as initial direction** on 2026-10-02 through the owner's instruction to continue to the next step; execution qualification and evaluation-spend gates remain. Consumer: architecture reviewer and implementer.

## Context

Existing coding runtimes and orchestration tools already cover much of the original product vision. Crewshal must test confirmed repository adaptation and portable evidence with minimal new machinery. Runtime security and cost behavior are not established by documentation.

## Decision

Use a single local Python coordinator with typed versioned records, a SQLite state store, private artifact files and two CLI adapters (Codex and Claude Code). Propose Python 3.12 or newer: its standard library covers TOML/JSON parsing, subprocess supervision and SQLite. A maintained schema validator and safe YAML parser may be added when their respective supported formats need them; select/pin these during approved implementation rather than write permissive custom validators. No model SDK is required for CLI execution.

Core modules own discovery, domain/policy/verdict rules, state/evidence and execution supervision; adapters translate runtime-specific interfaces. Start with passive Python/TypeScript discovery and a qualified Linux execution profile. Use separate immutable candidate copies and coordinator-owned evidence, explicit grants and independent review where required. Read-only host discovery and write-capable execution have different support matrices.

Before building execution machinery, behavior-test the existing Orchestrate/Orka seams against the required contracts. Prefer integration when they fit. The decision does not mandate wrapping an unsuitable tool or recreating its whole workflow.

## Alternatives and tradeoffs

TypeScript is a credible alternative with strong event-stream tooling; Python is proposed because discovery and local transactional persistence require fewer platform packages. Python's runtime typing and process handling still require validation and integration tests. Go adds compile-time guarantees and a distributable binary but is not necessary to test the hypothesis at this stage.

A provider SDK/tool loop duplicates existing runtime functionality. A general workflow framework adds scheduling/persistence concepts beyond a single worker and reviewer. Worktrees simplify Git operations but share metadata and supply no containment. Containers provide an execution substrate whose filesystem/network/credential behavior still must be qualified; Linux-only execution narrows initial portability.

SQLite avoids operating a database service but requires explicit transactions, schema migrations and recovery logic. Two CLI adapters incur version/event drift; conformance evidence must be invalidated when relevant versions/configuration change. Unknown mandatory capability blocks execution. Credential mediation may force reuse of external isolation tooling or postponement of writes.

## Approval and reconsideration

Proceed in bounded sessions under the accepted scope, Python choice, runtime pair and qualified-execution requirement. Material changes to those decisions require owner review. Reconsider a standalone executor if an existing seam satisfies the controls. Reconsider the product if comparative evaluation does not show useful setup savings with adequate quality and acceptable overhead. Four-stack sealed evaluation remains a later gate, not a claim that the first two-stack slice supports every target.
