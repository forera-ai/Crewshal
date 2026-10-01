# Crewshal — Phase 0 competitive landscape and naming

Research date: 2026-10-01. Consumer: owner deciding whether a new product deserves to exist. Primary documentation and project repositories were searched and opened. Capabilities below are **documented**, not independently executed or security-certified. Maturity describes the inspected product/documentation surface, not reliability. Absence of evidence in this bounded review is not evidence of absence. Pin releases and repeat relevant checks before implementation.

## Conclusion

The proposed broad feature bundle is already crowded. Multi-runtime dispatch, heterogeneous models, isolated working trees, risk routing, resumable execution, independent review and deterministic completion are not defensible novelty claims. In particular, [Orchestrate](https://github.com/bestagentkits/orchestrate) describes almost that bundle already. [Orka](https://github.com/Dusttoo/orka) addresses engineering tickets with isolated implementation and review gates. [GitHub Agentic Workflows](https://github.github.com/gh-aw/reference/faq/) provides an established platform surface for constrained agent jobs and controlled external writes.

The remaining opportunity is a hypothesis: an inspectable, human-confirmed repository model that produces appropriate controls and evidence with less setup, across genuinely different stacks and coding runtimes. No uniqueness or competitive advantage for that combination has been demonstrated. Prefer an integration or contribution to existing execution systems if they can satisfy the evaluation.

## Competitive matrix

| System and primary source | Capability and implementation | Maturity signal | Strength | Limitation / overlap / opportunity |
|---|---|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/headless), [sandbox](https://code.claude.com/docs/en/sandboxing) | Native coding loop; noninteractive execution, structured results, sessions, tools and runtime-specific controls | Official CLI and programmatic documentation | Reuse a working coding environment instead of writing a new agent loop | Runtime-bound controls; explicit configuration loading and credential behavior matter. Opportunity is neutral project adaptation above it |
| [OpenAI Codex](https://learn.chatgpt.com/docs/non-interactive-mode), [SDK](https://learn.chatgpt.com/docs/codex-sdk), [sandbox](https://learn.chatgpt.com/docs/sandboxing) | CLI/SDK execution with event streams, schema-constrained final results and permission/sandbox surfaces | Official supported integration documentation | Execution and usage events can support supervisor-captured evidence | Workspace access is not automatically an arbitrary per-task path boundary. Neutral confirmed policy is still an integration concern |
| [Copilot cloud agent](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent) | Repository tasks produce PRs in GitHub's managed development workflow | Official hosted product documentation | Existing repository/PR integration and human review workflow | Hosted platform and service constraints; not an interchangeable local runtime. Avoid duplicating PR delivery |
| [GitHub Agentic Workflows](https://github.github.com/gh-aw/reference/engines/), [safe outputs](https://github.github.com/gh-aw/reference/safe-outputs-pull-requests/) | Compile Markdown workflows to Actions; selectable engines and restricted outputs | Extensive official references; some individual features explicitly experimental | Read-only agent defaults, protected patch paths, scoped write jobs and infrastructure approval | GitHub/Actions-centric, with configured workflows rather than a verified general adaptive initializer. Strong governance overlap; evaluate integration |
| [Gemini CLI](https://geminicli.com/docs/cli/headless/), [policy engine](https://geminicli.com/docs/reference/policy-engine/) | Headless text/JSON interface and allow/deny/confirmation rules | Official CLI references | Explicit policy decisions and programmatic execution | Tool policy is runtime-specific; cross-provider review is an external workflow. Test rather than assume enforcement equivalence |
| [OpenCode](https://opencode.ai/docs/providers), [SDK](https://opencode.ai/docs/sdk/), [permissions](https://opencode.ai/docs/permissions/) | Multi-provider coding runtime with programmatic server/client and configurable tools/permissions | Maintained public product documentation; versioned permission variants | Provider choice within one runtime and useful permission surfaces | Multiple models in one runtime do not prove multi-runtime portability. Permission rules alone are not OS isolation |
| [OpenHands SDK](https://docs.openhands.dev/sdk), [routing](https://docs.openhands.dev/sdk/guides/llm-routing) | Composable software-agent execution, workspace services and model routing | Public SDK and guides; routing guide explicitly notes active development | Reusable execution foundation with context, security and observability extension points | Replacing other CLI environments with one SDK is a different boundary from coordinating them. Evaluate reuse before inventing execution |
| [Aider repository map](https://aider.chat/docs/repomap.html), [architect mode](https://aider.chat/docs/usage/modes.html) | Compact repository context; separate architect and editor model calls | Public CLI documentation | Direct prior art for context selection and heterogeneous responsibility assignment | Planning/editing split is not independent review; structural context is not a confirmed governance model. Benchmark as a simpler baseline |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupts](https://reference.langchain.com/python/langgraph/types/interrupt) | Stateful orchestration with checkpoints, stores and resumable human interactions | Documented library abstractions | Solves generic state persistence and pause/resume building blocks | Application still owns repository discovery, evidence trust and execution boundaries; do not rebuild generic persistence without need |
| [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework), [HITL](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) | Multi-agent workflows, external requests and checkpoint recovery | Official framework docs and migration guidance from AutoGen / Semantic Kernel | Reusable orchestration and approval interaction | General workflow primitives do not establish project-specific controls; product scope differs from turnkey repository initialization |
| [CrewAI Flows](https://docs.crewai.com/en/concepts/flows) | Stateful flow composition and persistence | Public framework documentation | General workflow construction | Requires application-owned engineering policy, discovery and evidence. A persona collection would add little beyond this category |
| [Orchestrate](https://github.com/bestagentkits/orchestrate) | Skills package with live runtime discovery, risk/capability routing, worktrees, durable events and independent arbitration | Public implementation and contracts; conformance not rerun here | Closest documented overlap with the proposed broad system | Runtime inventory discovery differs from validating a project model. Its documented fresh-context substitution is weaker than a strict cross-provider requirement; test both explicitly |
| [Orka](https://github.com/Dusttoo/orka) | Claude/Codex engineering workflow with durable scheduling, isolated implementation, independent reviews and merge guard | Public reusable harness; conformance not rerun | Direct overlap with bounded multi-runtime engineering | Ticket/release workflow focus. Determine whether neutral repository onboarding can be supplied as an integration |
| [AO](https://github.com/Mats2208/ao) | Separate Claude/Codex/OpenCode worker processes in Git worktrees | Public implementation; conformance not rerun | Prior art for real heterogeneous CLI process coordination | Worktrees establish change isolation, not complete security containment; adaptation/evidence guarantees need behavioral evaluation |
| [eve Software Factory](https://github.com/vercel-labs/eve-software-factory-template) | Four development stations deliver a reviewed draft PR, leaving merge to a person | Public template and deployment instructions | Clear bounded delivery product | Vercel/integration-oriented; already called Foreman. A reviewed PR alone does not prove cross-provider or deterministic policy independence |
| [thruwire/foreman](https://github.com/thruwire/foreman) | Replaceable worker protocol, semantic supervision and deterministic responsibility checks | Public supervisor implementation and test descriptions | Recovery and supervisory separation overlap | Specialized decision-model integration; no verified superiority in adaptive onboarding |
| [ncklrs/foreman](https://github.com/ncklrs/foreman) | Documents model routing, protected paths, sandbox choices, learning and task decomposition | Public implementation; feature claims not rerun | Broad direct product and name collision | README claims must be tested before adopting its guarantees; leaves little room for novelty based on a feature checklist |
| [tuzlu07x/foreman](https://github.com/tuzlu07x/foreman) | Local mediation, risk assessment, audit storage and approvals across agent interfaces | Public implementation; conformance not rerun | Direct governance and runtime-mediation overlap | Risk assessment is not itself deterministic containment. Also a direct name collision |
| [Prooflane](https://prooflane.ai/) | Guided discovery, reviewed assurance plans and evidence-based release decisions for AI systems | Product explicitly describes beta status | Adjacent evidence/decision-plane and adaptive assurance prior art | Targets AI systems rather than general source-code change orchestration; no product benchmark executed. Reject as an alternative name |

## Requested capability comparison

Legend: **D** = explicitly documented; **P** = partial or a narrower related capability; **?** = not established in the reviewed sources; **I** = application integration required. These cells describe the reviewed surface, not universal absence. “Boundary” means deterministic path/tool/output policy; it does not certify prevention across arbitrary processes.

| System | Repo discovery | Adaptive confirmed init | Multiple coding runtimes | Heterogeneous models | Cross-provider independent review | Boundary | Evidence completion | Risk workflow | Cost routing |
|---|---|---|---|---|---|---|---|---|---|
| Claude Code / Codex / Gemini | P | ? | I | P | I | D | P | I | I |
| Copilot cloud agent | P | ? | ? | P | ? | P | P | I | ? |
| GitHub Agentic Workflows | P | ? | D | D | P | D | P | I | P |
| OpenCode | P | ? | I | D | I | D | P | I | P |
| OpenHands | P | ? | I | D | I | P | P | I | P |
| Aider | D | P | I | D | I | P | P | I | P |
| LangGraph / Agent Framework / CrewAI | I | I | I | P | I | I | I | I | I |
| Orchestrate | P (runtime inventory) | ? | D | D | P (independence policy) | D | D | D | D |
| Orka | P | P (bootstrap) | D | P | P | D | D | P | ? |
| AO | P | ? | D | D | P | P | P | ? | ? |
| eve factory | P | P (setup) | ? | P | ? | P | P | P | ? |
| Foreman projects above | P | ? | P | P | P | P | P | P | P |
| Prooflane | D (AI targets) | D (reviewed assurance) | ? | ? | ? | P | D (release decisions) | P | ? |

Grouped rows describe category-level related capabilities; they do not imply that every member provides every cell. The per-system matrix above is the authoritative distinction. For an implementation decision, run the specific selected tool under a pinned version.

## Standards and existing components

[Agent Skills](https://agentskills.io/specification) already defines portable packaging and progressive loading. Its experimental tool field is not a universal enforcement contract. [MCP security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) treats local servers and authorization as explicit trust boundaries; MCP is not an engineering workflow. [ACP](https://agentclientprotocol.com/get-started/introduction) standardizes communication between clients and coding agents, making it relevant to adapter transport.

[OpenRouter](https://openrouter.ai/docs/guides/routing/routers/auto-router) supplies model routing, and [fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks) handle provider failures. Neither establishes a trusted filesystem or a neutral repository policy. Fallback must not silently change privacy constraints, authority or review independence. Avoid treating an OpenAI-compatible endpoint as proof of identical model capabilities.

Use existing Git, CI, parsers, schema validators, sandboxes and provider gateways where appropriate. A small product could compose these around project adaptation; recreating all of them would invalidate the efficiency goal.

## Naming and collision review

**Reject Foreman for public branding.** It collides with the established [Foreman infrastructure project](https://theforeman.org/), [ddollar's Procfile manager](https://github.com/ddollar/foreman), and multiple coding-agent supervisors in the matrix. These are practical product and search-confusion conflicts, independent of any legal trademark ruling.

**Adopt Crewshal**, pronounced like “crucial”, following the owner's decision on 2026-10-01. It connects essential engineering controls with a coordinated crew. Display name: `Crewshal`; future command/package spelling: `crewshal`; canonical repository: [prooshani/Crewshal](https://github.com/prooshani/Crewshal).

The earlier provisional Runwarrant and Taskwarrant recommendations are superseded. The current [naming and repository decision](docs/decisions/0001-name-and-repository.md) records the search scope, observed collisions, registry responses and limitations. Exact-name searches found no direct AI engineering competitor. One older compiler-study repository contains the string; personal/music uses also exist. Seven registry endpoints returned HTTP 404. These results support initial repository use, not comprehensive trademark clearance or guaranteed package/domain reservation. The deliberate resemblance to “crucial” also intersects an established technology brand and remains a similarity risk.

## What is actually differentiated?

Nothing is demonstrably unique yet. The strongest testable product boundary is **confirmed repository adaptation plus portable evidence**, with existing runtimes executing work. The potential advantage is reduced configuration and human remediation, not a new agent metaphor or more roles.

Before architecture selection, compare the same unfamiliar repository against native runtime initialization, Orchestrate/Orka bootstrap, and a minimal scripted two-runtime workflow. If existing software meets the discovery, policy, evidence and efficiency bars with comparable setup, contribute or integrate and abandon a separate orchestrator.
