# Crewshal — Phase 0 predecessor concept audit

Date: 2026-10-01. Consumer: the owner deciding which concepts justify an independent product. Status: decision support; no architecture approval or implementation authorization.

## Scope and evidence

The available internal system was inspected read-only. This report is newly authored and deliberately abstracts away its proprietary implementation, prompts, schemas, rules, names, paths, business logic, history, and operational artifacts. Nothing is being ported. Evidence IDs below refer to an owner-only inspection ledger kept outside this repository; public readers cannot reproduce the private observations from this report. Public prior art is linked in [COMPETITIVE-LANDSCAPE.md](COMPETITIVE-LANDSCAPE.md).

The audit covers every major subsystem: classification and routing; orchestration instructions; agent definitions; authority registry; guards and sandbox configuration; run creation and synchronization; schema and integrity validation; completion gates; contract and consumer analysis; freshness; telemetry, diagnostics and reporting; institutional memory; publication and delivery; failure recovery; tests, evaluations and documentation. Inspection combined graph discovery with direct source reads and targeted checks. The graph omits important extensionless executables, excludes runtime configuration and evidence directories, and has partial test parsing. Those limitations were checked, and material conclusions use source rather than graph absence. The source checkout contains uncommitted changes, so this describes the inspected working tree, not a released version. [E01]

This is a complete **major-concept disposition**, not a line-by-line security certification. Existing Python executable sources were parsed without execution; registry, policy and schema files were parsed as JSON. The legacy test suite, live agent sessions, deployment commands and external services were not executed. Historical observation reports were read, but their raw transcripts and billing records were not independently re-accounted. Accordingly, distinguish source-observed behavior, historically reported failure, and proposed redesign. No assertion here establishes the predecessor's current production reliability. [E01, E09]

## Major-concept disposition

| Concept | Disposition | Why retain it, or what must change | Evidence |
|---|---|---|---|
| Conventional software makes mechanical decisions | KEEP CONCEPT | Exit status, changed paths and contract validity are reproducible; an agent summary cannot substitute for them. | E02, E03 |
| Separate claims, evidence and completion verdicts | KEEP CONCEPT | Prevents a well-formed report from becoming proof that work happened. | E03 |
| Recompute required controls from scope | KEEP CONCEPT | A worker must not reduce assurance by editing its own declared gate list. Retain monotonic controls, with human-authorized policy changes separately recorded. | E02, E03 |
| Risk proportional to consequences | KEEP CONCEPT | Security, persistence and public compatibility deserve different controls from a spelling correction. Every retained signal must have an explanation. | E02 |
| Fixed path patterns and known repository inventory | PROJECT-SPECIFIC — DISCARD | They encode one estate, not discovery of an unfamiliar repository. Names and file counts alone are insufficient risk evidence. | E02, E04 |
| Directory input treated as complete risk knowledge | REDESIGN | The source now explicitly handles certain unscanned directories as unknown. Generalize the lesson: lack of observation cannot establish low risk; reconcile intended scope with the actual diff. | E02 |
| Fixed personas and mandatory role cascades | REMOVE | Capabilities can be selected without maintaining a large organization chart. Separate actors only when independence, authority or evidence requires it. | E05, E09 |
| Human escalation and scoped authority | KEEP CONCEPT | A person must decide consequential tradeoffs. Approvals need scope, identity, time and revision; rejected actions must remain rejected. | E06 |
| Broad authority in the conversational coordinator | REDESIGN | A trusted person and a model sharing a session do not have identical authority. Model coordination must not impersonate the person or bypass evidence ownership. | E04, E06 |
| Tool-hook write checking | PROVIDER-SPECIFIC ADAPTER | Useful early denial and diagnostics, but hook invocation, payload and error semantics belong to a runtime. It is not a portable security boundary. | E04 |
| Shell string parsing as containment | REPLACE WITH STANDARD | Interpreter code, environment, executable resolution and downstream command rewriting defeat complete string-based reasoning. Use an execution boundary and a controlled environment. | E04 |
| Sandbox configuration and activation checks | REDESIGN | Verify effective behavior in a fresh session, including file tools, shell children, network and escape options. Avoid global configuration changes and complex restoration machinery where an isolated environment suffices. | E04, E07 |
| Read scopes, credentials and network | REDESIGN | A write guard does not constrain reads or exfiltration. Grants must cover each authority dimension and all execution channels. | E04 |
| Report ownership and protected control state | KEEP CONCEPT | A reviewer should not change implementation; a worker should not edit another actor's ruling or trusted command records. | E03, E04 |
| Shared mutable working trees | REDESIGN | Baselines cannot reliably attribute concurrent edits. Use isolated workspaces, explicit integration and final revision validation. A Git worktree alone is not a sandbox. | E07, E09 |
| Baselines, freshness and evidence fingerprints | KEEP CONCEPT | Tests and reviews must refer to the tree they judged. Remote freshness is unknown without sufficiently current remote observation. | E03, E07 |
| Agent-authored command evidence | REDESIGN | The gate checks recorded status and owned logs; existence and hashes do not authenticate execution. A trusted runner must capture command, status, environment and tested revision outside worker authority. | E03 |
| Permanent failure stickiness | REDESIGN | Preserve failures in history, but allow a later verified attempt to supersede one after remediation. An unrelated success or disappearing diagnostic cannot clear it. | E03, E09 |
| Pre-existing failures and absent validators | KEEP CONCEPT | Explicit unavailable/waived controls and comparable baselines prevent both false greens and impossible gates. A waiver is not a passing test. | E03 |
| Partial handwritten schema validation | REPLACE WITH STANDARD | Use a maintained validator with a pinned dialect and explicit format enforcement. Cross-artifact business invariants remain separate deterministic checks. | E03, E08 |
| Custom contract parsing and ecosystem scanners | REPLACE WITH STANDARD | Reuse language-aware parsers, API diff tools and dependency metadata. Consumer coverage and scan errors must be visible; text hits alone do not prove complete impact. | E08 |
| Lifecycle telemetry separate from denial controls | KEEP CONCEPT | An unavailable telemetry sink must not change a security decision. No stop event and no recent progress are different observations. | E07 |
| Turn limits as a proxy for execution budgets | REDESIGN | Historical reports associate cap-driven rediscovery with repeated context loading. Use wall-clock deadlines, bounded retries, usage budgets and recoverable checkpoints; tune from measured outcomes. | E07, E09 |
| Main-session prose and late synchronization as run state | REDESIGN | Persist state at transitions and before side effects. A partial implementation remains partial after interruption. | E07, E09 |
| Cross-session memory and compact artifact references | KEEP CONCEPT | Stable facts need not be rediscovered. Cache only facts with provenance, scope, source fingerprints and invalidation; untrusted summaries cannot silently become authority. | E05, E07 |
| Mandatory knowledge-publication role | REMOVE | Durable run evidence and confirmed project facts can be recorded mechanically. Editing institutional narrative is optional work, not every task's completion requirement. | E05, E09 |
| Provider-specific deployment topology and model aliases | PROVIDER-SPECIFIC ADAPTER | Probe availability and actual resolved model. Do not export runtime frontmatter or personal installation topology as a neutral core. | E05, E07 |
| Product-specific release rules and integrations | PROJECT-SPECIFIC — DISCARD | They embody a prior owner's business and release authority. No deployment or automatic merge belongs in the initial hypothesis. | E06, E07 |
| Narrow privileged operations | KEEP CONCEPT | A small validated operation can grant less authority than a general shell. Retain the principle; exclude legacy release operations from v0.1. | E04, E06 |
| Local fixture tests and failure-mode evaluations | KEEP CONCEPT | Deterministic adversarial cases expose false success. Hook unit tests also need actual runtime integration tests before enforcement claims. | E08 |
| Repeated handoffs and remediation-document accumulation | REMOVE | Replace recurring prose ceremony with actionable errors, state records and a short current reference. Keep consequential decisions, not every conversational handover. | E05, E09 |

## Architecture and efficiency critique

**The deterministic machinery is valuable; its current integration is the expensive part.** Gate, authority, synchronization, publication, deployment, telemetry and exception logic have grown around one runtime and one estate. Splitting this into many files would not itself reduce complexity: the real issue is duplicated authority and lifecycle decisions across prompts, registries, tools and prose. An independent implementation should establish one decision owner per invariant, then expose only the relevant result to an agent. [E03–E07]

Source inspection finds substantial repeated instructions across role definitions. Large role bodies, preloaded platform knowledge, repeated discovery, handoff reconstruction and context accumulated in the coordinator plausibly raise overhead. This is an inference about mechanisms, not a token saving estimate. Historical observation reports provide stronger incident evidence of repeated re-entry, incomplete handoffs, clerical gate failures and lengthy review loops. Later source includes fixes for several reported failures; those reports must not be presented as proof that every defect remains today. [E05, E09]

The dedicated cost harness measures deterministic command wall time, including repository fingerprinting and scanning. Its recorded comparison includes unequal repository inventories; those timings cannot establish a speedup. The current measurement code explicitly rejects failed or different-shaped workloads as incomparable. Separate historical reports include agent usage and cache accounting, but they are observations, not randomized comparisons. Cached tokens, new input, output, actual cost, estimated cost and subscription usage must remain distinct. Elapsed time also mixes compute with human waiting. No measured overall efficiency advantage is established. [E09]

Priority remedies are fewer dispatches, one reusable confirmed project model, capability-specific context selection, compact referenced artifacts, incremental invalidation and direct deterministic execution of checks. A separate LLM agent should not be mandatory merely to invoke tests. Cross-provider review should be measured against a fresh-context reviewer using the same provider: different providers may add value, but do not guarantee independent errors.

## Portability and multi-runtime feasibility

The predecessor's neutral concepts are portable; its implementation is not directly portable. Native hooks, identity fields, tool names, frontmatter, skill loading, session paths, model aliases, sandbox semantics and user-scope deployment all require runtime translation. Filesystem case sensitivity, symlinks, process termination, toolchains and host permissions add platform differences. The available implementation and observations do not establish Linux or Windows conformance. [E04, E05, E07]

Separate CLI processes are feasible: [Claude Code](https://code.claude.com/docs/en/headless), [Codex](https://learn.chatgpt.com/docs/non-interactive-mode), [Gemini CLI](https://geminicli.com/docs/cli/headless/) and [OpenCode's SDK](https://opencode.ai/docs/sdk/) expose programmatic execution. This establishes interface feasibility, not reliable adapter behavior. The adapter must detect unsupported controls and refuse an incompatible policy instead of pretending that similarly named permissions are equivalent.

| Mechanism | Useful property | Cost or limit | Phase 0 recommendation |
|---|---|---|---|
| CLI subprocess plus structured events | Reuses an existing coding loop; separate sessions | Startup, authentication, version drift, process-tree cleanup, ambiguous interruptions | Preferred first experiment, with externally enforced authority |
| Runtime SDK or app server | Rich events, lifecycle and approvals | Runtime-specific versions and lifecycle semantics | Use when it demonstrably improves a selected adapter |
| Direct provider API / OpenRouter | Explicit model and usage control | Requires an agent/tool loop; an inference gateway is not a coding runtime | Defer a new implementation loop; consider later narrow analysis jobs |
| Agent Client Protocol | Common client/agent interaction contract | Implementation support and enforcement still differ | Evaluate existing [ACP](https://agentclientprotocol.com/get-started/introduction) adapters before inventing a transport |
| MCP | Standard access to tools/resources | Server trust, credentials, permissions and lifecycle still need host controls | Optional integration; not the workflow or authority model |
| Filesystem artifacts / mailbox | Durable, inspectable, easy references | Identity, locking, atomic writes, replay and ownership must be solved | Exchange trusted references, not executable instructions |
| Runtime-native subagents | Low integration effort within one environment | Does not by itself prove runtime neutrality or independent authority | Optional adapter capability |
| Worktrees plus sandbox/process isolation | Separates changes and limits access | Toolchain setup, integration conflicts, platform gaps | Test the distinction between change isolation and security containment |

The smallest feasible execution experiment is one bounded implementation process, deterministic validation, and one fresh review process using a different runtime/provider when required. Swapping implementer and reviewer must reuse the same confirmed project model. No generic distributed agent bus is justified yet.

## Preliminary security analysis

Assets: source, user changes, secrets, approvals, control policy, trusted evidence, provider accounts and external publication authority. Treat repository content, instruction files, dependency scripts, model responses, tool output, MCP servers and generated patches as untrusted inputs. Trust the owner-facing approval channel and an execution supervisor only to the extent their isolation is tested.

| Attack or failure | Required boundary for an experiment | Residual limitation |
|---|---|---|
| Repository instruction or tool-output injection | Discovery reads data without executing configuration; only the owner can promote proposed policy to confirmed policy | A model can still misunderstand benign or malicious content |
| Malicious build/test/dependency scripts | Validate inside an isolated environment, with bounded resources and explicit network grants | A passing test does not prove scripts or dependencies safe |
| Shell injection or executable shadowing | Structured arguments, controlled environment and executable resolution; no shell assembly from untrusted strings | Native coding runtimes may generate shell programs; the outer sandbox must constrain them |
| Secrets exposure | No broad credential inheritance; narrow provider credential handling/proxy; isolate validation from runtime authentication | Provider-bound request data and encoded leaks require separate data-egress decisions |
| Worker forges evidence or approval | Trusted runner records command evidence; approval identity and policy remain outside worker-writable state | Hashes detect changed bytes, not honesty of the original producer |
| Boundary escape via symlink, hard link, case alias, child process or MCP | Behavior tests across every enabled tool channel; deny unsupported enforcement combinations | Hooks and worktrees alone are insufficient |
| Stale review or concurrent edits | Review and command evidence bind to the same immutable candidate; integration triggers revalidation | External dependencies and services can change independently |
| Lost response after a privileged side effect | Persist intent, use operation identity, reconcile external state before retry | Exactly-once external effects cannot be assumed |
| Timeout, quota exhaustion or excessive spend | Explicit terminal failure, bounded retries, cost/deadline caps and retained partial state | Some providers report delayed or estimated usage |
| Control-plane self-modification | Control state mounted separately and protected; approval required for revised authority | A compromised supervisor defeats its own controls |

These are design requirements, not a claim of implemented protection. [MCP security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) describes additional server and authorization threats. Native sandbox documentation must be verified against pinned installed versions. Broad autonomous execution remains out of scope.

## Decision

Retain evidence-backed verdicts, risk proportionality, explicit unknowns, revision binding, scoped authority, lifecycle observation and reusable confirmed knowledge. Delete fixed personas, mandatory memory publication, repeated prose ceremony and all estate-specific assumptions. Replace custom parsers and incomplete validators with standards. Redesign execution, evidence provenance, recovery and context selection from scratch.

The preceding lessons justify an evaluation, not a new general orchestration runtime. See the narrowed hypothesis and stop conditions in [PRODUCT-HYPOTHESIS.md](PRODUCT-HYPOTHESIS.md).
