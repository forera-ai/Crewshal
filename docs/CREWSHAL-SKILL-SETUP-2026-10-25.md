# Crewshal skill and supervised Hermes setup

Date: 2026-10-25. Milestone: install the global project skill and verify bounded CLI task transport.
Skill version: `1.0.0`. Package checkpoint: `0.27.7`.
Base revision: `1398badfdff94850cf7b7df0b79ee37350f2888d` on `codex/phase1-architecture`.
The delivery revision is the commit containing this record.

## Scope and source basis

The owner requested a global Crewshal skill and Sol 6.1 supervision of local Hermes development.
This checkpoint adds a development procedure. It does not add or replace a Crewshal runtime adapter.
The source bundle is [skills/crewshal](../skills/crewshal/SKILL.md).
The global installation is `~/.codex/skills/crewshal`, exposed through `~/.agents/skills/crewshal` for Hermes.
The installed and repository bundles must match after each update.

The review read all 54 retrievable turns of `Prepare Crewshal handoff` through seven pages.
It read the user messages and final review records. It did not reaudit every referenced raw model export.
The review also read current handoff, plan, architecture, evaluation goals, relevant ADRs, and the required companion skills.
Current records govern scope. Historical chat outcomes do not grant new authority.

## Skill contract

The skill requires `gpt-6.1-sol` for orchestration and local Hermes for bounded implementation.
Each answer must start with `〔 crewshal skill v1.0.0 active 〕`.
It requires codebase-memory, caveman, Jev, RTK, and effective runtime checks before task work.
ASD-STE100 takes priority over compressed fragments.
Each delegated agent must verify its own tools and receive explicit graph evidence and file ownership.

Codex checks a read-only readiness packet before granting implementation authority.
It reviews the actual candidate, integration effects, refusals, and current check evidence before acceptance.
Hermes stops before commit, push, profile changes, or further delegation unless the assigned task explicitly permits them.
The default limit is one implementation attempt and two targeted corrections.
Two attempts without new evidence stop that route earlier. A new chat does not reset the count.
Codex preserves failures and changes the task design instead of repeating an ineffective prompt.
One accepted milestone and its publication ceremony end the session.

## Local profile changes

Codex saved the prior profile configuration and SOUL in a private backup before changes.
The backup is `~/.hermes/backups/crewshal-skill-2026-10-25` with restricted file permissions.
No credential file was read or copied into Git.

The `crewshal` profile now loads the four required skills automatically.
Its MCP configuration contains codebase-memory-mcp and Jev, with server-initiated sampling disabled.
The previous unrelated MCP entries remain available in the private configuration backup.
The hosted title model now uses the selected local Unsloth route. Fallback providers remain empty.
Unattended single-query approval mode is `deny`. Existing commit and push denial rules remain active.
Nested orchestration is disabled, and local child concurrency is limited to one.
The profile has a 300-second run budget and retains its 45-turn limit.
These controls do not establish general filesystem or network containment.

The selected model is `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` through the configured provider `unsloth`.
The runtime resolves that route as `custom` at a loopback endpoint.
The model server changed during the smoke test. Its context fell from 135,680 to 93,696 tokens.
Codex reduced the profile context from 98,304 to 93,696 tokens after that observation.
Pruning remains 48,000 tokens, and compression remains capped at 70,000 tokens.
The completed smoke had the earlier admitted configuration. A new request under the corrected context was not tested.
Future launches must recheck effective model identity and capacity after any server restart.

## Independent Sol 6.1 check

The parent chat ran `gpt-6-astra`, so it assigned Hermes control to a `gpt-6.1-sol` agent.
Trusted dispatch metadata records that selection. It does not establish a server-internal model identity.
The Sol agent owned the read-only smoke and its evidence review. It made no repository edit.

The first CLI invocation exited 2 before inference because the gateway rejected `--run-budget`.
It created no session and reported zero tokens. The corrected route uses `agent.run_budget_seconds` in the profile.
The inspected gateway source passes that frozen policy value to execution.
The result did not expose the frozen budget value directly. Timeout and targeted cancellation were not behavior-tested.

The second invocation used this command shape, with a private task file:

```sh
rtk proxy hermes -p crewshal chat \
  --query-file /absolute/private/task.md \
  --provider unsloth \
  --model unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL \
  --in /Volumes/X10Pro/Crewshal \
  --skills crewshal,codebase-memory,caveman,jev \
  --max-turns 12 --format stream-json
```

The process exited 0 after 297.017 seconds. The stream recorded 296,190 milliseconds and 11 tool calls.
The session admission reached `terminal`, with outcome `completed` and generation 1.
The worker named all four skills and demonstrated a distinct rule from each.
Its actual graph status, coverage, and Jev calls succeeded.
The graph generation was `2026-10-24T19:44:19Z`; AGENTS coverage reported no recorded issue with matching metadata.
Jev reported probability 0.05, confidence 0.9, cost 0, and latency 314 milliseconds for the synthetic refusal question.
The parent also completed a synthetic Jev connection check. Neither call granted authority.

The stream reported 152,506 input tokens, 4,579 output tokens, and 111,202 cached input tokens.
The session database reported 41,304 input tokens and four API calls.
These are different visible accounting representations. Actual billing remains unknown.
No evaluation spending allowance changed.

## Rejected worker claims and corrections

The worker read only AGENTS lines 1–30 and received `truncated: true`.
It then claimed all required reads were complete. Codex rejected that claim.
The worker also claimed Git status passed before and after its work, although its tool inventory contained only one status command.
The Sol supervisor independently compared HEAD, status, and staged and unstaged diffs. They matched the initial snapshot.
The worker wrapped the required banner in backticks. This did not meet the exact plain-line instruction.
Its terminal command also included an unwrapped directory change and decorative output separators.
These instruction failures do not negate the connection evidence. They prevent product readiness acceptance.

The skill now explicitly separates readiness from implementation dispatch.
Codex must inspect actual complete instruction reads and runtime bindings before permitting source work.
The next prompt requires a complete AGENTS read and a distinct final Git observation.
A client disconnect does not prove gateway termination. Use supported session cancellation and verify terminal state when needed.

The Sol reviewer also assessed five scenarios without effects.
It rejected forged approval, missing child Jev access, stale graph reliance, repeated ineffective attempts, and historical guest authority.
These were reviewer decisions from the skill text. They were not worker execution tests or containment proofs.

## Acceptance and limitations

The skill validator passed. Relative links, whitespace, source-copy equality, and synchronized package versions passed.
Hermes MCP connection tests discovered 15 graph tools and five Jev tools.
Approval dry runs denied commit and push with exit 3. Git status remained allowed with exit 0.
The live CLI smoke verified task transport, actual graph/Jev use, result collection, and normal terminal completion.
The final independent Git comparison confirmed no repository change by the worker.
The frozen checker reported 23 artifacts, 768 planned units, and both execution flags false.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.

The principal check commands were:

```sh
rtk proxy git diff --check
rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy env -u PYTHONPATH .venv/bin/python -c 'import crewshal; print(crewshal.__version__)'
rtk proxy hermes -p crewshal mcp test codebase-memory-mcp
rtk proxy hermes -p crewshal mcp test jev
rtk proxy hermes -p crewshal approvals test --json -- rtk proxy git commit -m probe
rtk proxy hermes -p crewshal approvals test --json -- rtk proxy git push origin probe
rtk proxy hermes -p crewshal approvals test --json -- rtk proxy git status --short
```

The skill-creator `scripts/quick_validate.py` also passed against the installed and repository skill directories.
A local parser compared all five installed files with the source bundle and verified links and preserved dated suffixes.
It also parsed every smoke event and confirmed the truncated read, single status command, and terminal result.

Verification used macOS 27.2 arm64 and CPython 3.12.15 for repository checks.
No source acceptance suite or installed-package check ran for this process-only checkpoint.
No Linux-specific test, guest action, image operation, download, evaluation row, deployment, or package release ran.
The current profile and skill are ready for a fresh supervised readiness check. Product readiness remains unaccepted.
The S1b action proposal remains the next product milestone after readiness passes.
Use the [next-session prompt](CREWSHAL-SUPERVISED-NEXT-SESSION-2026-10-25.md).

Raw smoke logs and the Sol review remain private under the backup's `smoke` directory.
They include both attempts, argv, tool calls, worker report, session state, and before/after comparisons.
They are not published as product evaluation evidence.
