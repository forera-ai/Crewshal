# Crewshal — Phase 0 product hypothesis and owner decision

Date: 2026-10-01. Consumer: owner deciding whether to authorize Phase 1. Accepted product name: Crewshal, pronounced like “crucial”. The owner authorized naming and repository initialization on 2026-10-01; Phase 1 architecture remains unapproved. This document proposes a boundary; it does not choose architecture, configuration syntax, language or dependencies.

## Recommendation: MODIFY

Do not build a new general agentic engineering runtime from the original feature list. Existing tools already document much of that list, including risk/capability routing, heterogeneous CLI workers, isolated changes, independent review and deterministic gates. [Orchestrate](https://github.com/bestagentkits/orchestrate), [Orka](https://github.com/Dusttoo/orka) and [GitHub Agentic Workflows](https://github.github.com/gh-aw/reference/faq/) make the overlap particularly concrete.

Authorize, if desired, architecture for a **small repository-adaptation and evidence experiment**. Its value must come from reducing the manual work required to configure appropriate controls in unfamiliar repositories. Reuse existing execution machinery where it satisfies tested boundaries. If the experiment adds no measurable advantage over a native workflow plus a short script, abandon the independent product.

## A–J owner brief

| Requested decision | Finding / recommendation |
|---|---|
| A. What is valuable | Deterministic completion, explicit unknowns, project-aware risk, scoped authority, revision-bound evidence, lifecycle observation and reusable confirmed facts |
| B. What to delete | Fixed persona organization, mandatory knowledge publication, repeated narrative handoffs, incidental complexity and all proprietary/estate-specific material |
| C. What to redesign | Discovery, effective permissions, trusted evidence capture, recovery, review identity, budgets and context selection |
| D. What existing software solves | Coding loops; CLI/SDK execution; multi-runtime dispatch; model routing; sandbox building blocks; resumable workflows; CI checks; skill packaging; substantial engineering governance |
| E. What remains differentiated | An unproven combination: inspectable confirmed project adaptation that reduces setup while producing consistent controls and evidence across stacks and runtimes |
| F. Product boundary | Local, single-repository confirmed discovery → bounded task → existing runtime → deterministic checks → independent review where required → inspectable completion record |
| G. Name | Adopt Crewshal; retire the Foreman working name. Bounded collision screening supports initial repository use; comprehensive trademark clearance remains uncompleted. See [naming decision](docs/decisions/0001-name-and-repository.md) |
| H. Minimal v0.1 hypothesis | A reusable confirmed project model materially reduces setup and repeated context work while preserving quality and enforcement when implementation/review runtimes are swapped |
| I. Evaluation | Predefined held-out repositories, simpler and competing baselines, blinded quality review, adversarial failures and complete token/cost/time accounting |
| J. Decision | MODIFY now; GO only after approval and evidence; ABANDON the separate product if existing tools meet the bars or the overhead exceeds the benefit |

Detailed rationale: [audit](AUDIT.md), [competitive and naming research](COMPETITIVE-LANDSCAPE.md), [evaluation plan](INITIAL-EVALUATION-PLAN.md).

## Proposed minimal v0.1 hypothesis

For explicitly supported project structures in unfamiliar Git repositories, a discovery process can propose stack, package boundaries, validation commands and risk locations with source provenance and explicit uncertainty. A human can correct and confirm that proposal with less setup effort than the baselines. The confirmed model can then govern a small task through two independent coding runtimes without hand-translating the model, while producing trustworthy revision-bound evidence at acceptable overhead.

This is falsifiable. It fails if discovery invents actionable facts, correction work erases setup savings, security depends on worker obedience, runtime swapping needs project-specific edits, or completion/quality and overhead regress against the baselines.

## Proposed experiment boundary

| Include enough to test | Defer until demonstrated need |
|---|---|
| Read-only discovery of a bounded set of common manifests, instructions and CI definitions | Universal architectural understanding, semantic indexing of every language |
| Fact provenance and observed / inferred / unknown / confirmed distinctions | Opaque risk scores or automatic promotion of inference to authority |
| Review, correction and explicit confirmation before model materialization | Silent generation of large configurations |
| Explained risk floor based on confirmed project facts plus intended and actual changed paths | Automatic consequential architecture or migration decisions |
| One bounded worker; one review session for the ordinary/high-risk experiment | A fixed multi-agent organization or parallel implementation DAG |
| Two genuine coding runtimes, with distinct provider identity for strict independence tests | Five shallow adapters or a new inference/tool loop |
| Trusted deterministic execution and evidence capture | Model-authored proof that commands ran |
| Persisted run transitions and recoverable interruption state | Distributed scheduling, queues, background autonomy |
| Isolated candidate changes and tested filesystem/network grants | Automatic merge, publication, deployment or credential operations |
| Explicit context and usage accounting; narrow invalidation of confirmed facts | Proprietary memory ecosystem or assumed cost savings |

Suggested first runtime pair: Claude Code and Codex, because their [programmatic](https://code.claude.com/docs/en/headless) [interfaces](https://learn.chatgpt.com/docs/non-interactive-mode) support a concrete feasibility experiment. This is a proposed test pair, not a core dependency or a final adapter choice. Reverse the implementation/review assignment during evaluation. Gemini/OpenCode remain researched candidates, not implementation commitments.

Supported stacks must be stated explicitly. A reasonable first discovery benchmark spans Python, TypeScript, Swift and .NET; execution support may initially be narrower where native toolchains or sandbox guarantees are unavailable. Unsupported combinations must be reported and counted, not demonstrated away.

## Capability model to evaluate

Maintain separate observations for runtime identity/version, provider identity, resolved model, structured events/results, resumability, cancellation/process-tree termination, file-tool restrictions, shell restrictions, network/credential isolation, human approval, context capacity and usage reporting. Each observation should have a status such as documented, behavior-tested, unsupported or unknown, plus its verification conditions.

Routing should first filter by required capabilities, privacy and authority. Cost/latency preferences can choose among eligible routes. Unknown capability is not permission to proceed, and an unavailable independent reviewer is a blocked requirement. Do not silently substitute a weaker provider or policy. A provider change must preserve the owner's data-egress decision.

Skills are a packaging mechanism; adapters translate them only where supported. No universal skill permission semantics should be assumed. [Agent Skills](https://agentskills.io/specification) expressly leaves support for experimental tool declarations dependent on implementations.

## Security and evidence requirements for architecture review

The confirmed model and policy, human decisions, trusted command records and verdict logic must be outside worker mutation authority. Reviewers see requirements, relevant source, diff and command evidence, without the implementer's conversational reasoning. Reviews must name the exact candidate revision and actual reviewer runtime/provider; a different session alone does not satisfy a cross-provider requirement.

Completion must make passing, failing, skipped, unavailable and waived checks distinguishable. Human acceptance of residual risk does not retroactively turn a failed test into a pass. The final integration tree must be checked again if it differs from the reviewed candidate.

Discovery does not execute repository instructions, hooks or dependency scripts. Validation executes repository-controlled code only after the relevant execution authority has been confirmed, inside tested isolation. Threat modeling and adverse-boundary tests precede enabling agent writes. User credentials and unrestricted global runtime configuration are not prerequisites for the product.

## What would change the decision?

GO to broader development only if the preregistered evaluation shows reduced configuration effort, portable control behavior, adequate quality and acceptable overhead. Prefer integration if a competitor supplies the needed execution and only discovery/evidence translation is missing. Abandon a separate product if those advantages disappear under fair baselines or require excessive ceremony.

The immediate owner decision is whether to authorize **Phase 1 architecture for this narrowed experiment**, revise its boundary, or stop. Naming and publication of the initial research repository were separately authorized on 2026-10-01. Approval for architecture does not authorize runtime implementation, benchmark spend or broader autonomous execution. Phase 1 must stop for architectural review, as the mission requires.
