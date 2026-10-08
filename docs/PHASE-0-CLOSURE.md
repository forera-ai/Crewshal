# Phase 0 closure and Phase 1 entry

Date: 2026-10-02. Consumer: owner reviewing the transition from research to architecture.

The owner authorized continuing the remaining Phase 0 work and initializing Phase 1 on 2026-10-02. Research deliverables are complete enough to enter architecture for the narrowed experiment. This records permission to propose a design, not approval of that design or permission to implement it.

| Phase 0 requirement | Evidence and disposition |
|---|---|
| Predecessor concepts, inefficiencies and failure modes | [Audit](../AUDIT.md): retain authority separation and deterministic evidence; redesign adaptation/recovery; discard fixed personas and proprietary material. Private evidence is not publicly reproducible. |
| Current ecosystem and runtime feasibility | [Competitive matrix](../COMPETITIVE-LANDSCAPE.md), refreshed primary runtime documentation and local CLI help; substantial overlap exists. Documentation is not runtime conformance evidence. |
| Name, repository and license | [Accepted decision](decisions/0001-name-and-repository.md): Crewshal, public repository, Apache-2.0. Preliminary collision screening is adequate for this initialization; commercial trademark clearance remains separate. |
| Differentiation and product decision | [Hypothesis](../PRODUCT-HYPOTHESIS.md): MODIFY to confirmed repository adaptation and portable completion evidence; measurable advantage remains unproved. |
| Security concerns | Audit and hypothesis identify untrusted repository content, credentials, external services, writable authority and forged/stale evidence; the [architecture](ARCHITECTURE.md) turns these into proposed boundaries and qualification gates. |
| Objective evaluation strategy | [Evaluation plan](../INITIAL-EVALUATION-PLAN.md): baselines, held-out tasks, quality/overhead measures and adversarial cases. Numbers remain proposals. |

## Remaining decisions and their proper gates

Architecture now proposes Python, a local coordinator, two CLI adapters and explicit capability qualification. These choices require architectural review. Existing execution tools must be behavior-tested before deciding whether to integrate them or implement the small execution seam.

Corpus selection, legal permission to use each repository, frozen task manifests, baseline conformance, numerical thresholds and a spending ceiling belong to evaluation preparation. They are not completed benchmark results and are not prerequisites for drafting architecture. They must be settled before any paid evaluation or exposure of hold-outs. No repository corpus is silently selected from the owner's private projects.

Execution security is still unqualified. Local version/help inspection found Codex CLI 0.156.1 and Claude Code 2.1.278. No model calls, credential inspection, sandbox experiments or benchmark runs were performed during this transition. Installed CLI availability does not demonstrate provider identity, adapter correctness or containment.

Phase 1 produces an architecture proposal and consequential ADR. Phase 2 remains gated by the mission's architectural review requirement. The original four-stack evaluation target remains visible even though the first execution slice is narrower.

## Subsequent owner decision

On 2026-10-02, after receiving the architecture proposal, the owner instructed continuing to the next step and required separate sessions for phases or major portions, testable acceptance criteria and a gradually updated handoff. This accepts the initial architecture direction and authorizes bounded implementation preparation. See the [development plan](DEVELOPMENT-PLAN.md) and [handoff](HANDOFF.md). Execution qualification, paid evaluation and release decisions remain separate gates.
