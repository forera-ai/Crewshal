# Hermes control from Codex

Use this workflow for foreground supervision within the current Codex session.
It does not install a background service, schedule future work, or add a product runtime adapter.
The owner authorized Codex to dispatch development tasks to Hermes and review their results.
Keep one milestone per session and preserve every consequential owner gate.

## Configuration and preflight

The profile is `crewshal` at `~/.hermes/profiles/crewshal`.
Read its `SOUL.md` and inspect only needed nonsecret configuration fields.
Do not read `.env`, authentication databases, credential pools, or private keys.
Do not print entire configuration files. They can contain secrets.
Use the installed CLI's help to confirm current flags before launch.

Verify these conditions:

- The coordinator model is `gpt-6.1-sol` in trusted runtime metadata.
- The selected Hermes provider points to the intended loopback endpoint.
- The served model and quantization match the selected Ornith Q4 or Qwen3.8 Q3 configuration.
- The Hermes context does not exceed the observed server context.
- `crewshal`, `codebase-memory`, `caveman`, and `jev` resolve and load.
- Graph and Jev MCP connections work in this profile, not only in Codex.
- The SOUL requires Codex review and forbids worker publication and profile mutation.
- Hosted fallback providers are absent. Auxiliary requests use the selected local provider.
- Commit and push denial probes pass through the actual Hermes approval evaluator.
- Unattended approvals deny requests that require an unanswered decision.
- The effective gateway configuration binds `agent.run_budget_seconds` to the task's finite budget.

The initial Ornith setting uses model `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` through provider `unsloth`.
The profile context is 93,696 tokens, with pruning at 48,000 and compression capped at 70,000.
The first server observation was 135,680 tokens. A later server restart reduced the observed context to 93,696 tokens.
Codex reduced the profile from 98,304 tokens to match. Recheck the current process before each launch.
The previously tested Qwen3.8 Q3 setup used 119,296 tokens. Its exact served identity must be checked before selection.
These are historical settings, not current server observations. Do not reload or retune the server automatically.
Use local server logs and a matching live process when authenticated metadata is unavailable.
Distinguish configured values, current process arguments, load logs, and effective request observations.
An HTTP 401 is a missing observation, not permission to extract a credential.

Test MCP connections with these commands:

```sh
rtk proxy hermes -p crewshal mcp test codebase-memory-mcp
rtk proxy hermes -p crewshal mcp test jev
rtk proxy hermes -p crewshal approvals test --json -- rtk proxy git commit -m probe
rtk proxy hermes -p crewshal approvals test --json -- rtk proxy git push origin probe
```

The approval probes never execute Git. An exit code of 3 means denial in the inspected CLI.
Also verify that ordinary Git status remains allowed.
These rules constrain shell approval paths. They do not establish a complete filesystem or network sandbox.
Do not test a denied publication by trying another API, shell encoding, or tool.

## Dispatch and collection

Start with a read-only readiness task. Do not include implementation authority in that first request.
Codex checks actual reads, tool calls, runtime identity, and the returned packet before dispatching source work.
The initial smoke connected correctly but falsely claimed complete reads after a truncated `AGENTS.md` read.
Require a complete instruction read and explicit final Git observation. Do not infer either from the worker's prose.
Reuse accepted readiness evidence within the same unchanged task context to avoid repeated full reads.

Write the bounded prompt to a private task file. Use `--query-file` so shell substitutions cannot execute prompt text.
Capture output in a new private directory outside the repository. Preserve failed attempts.
Use explicit provider and model flags, the intended profile, and the actual repository working directory.
Load the four skills explicitly unless the effective profile already loads them.
Prefer the installed `hermes chat` interface. Do not use top-level `-z`, `--yolo`, or `--accept-hooks`.
Do not suppress project rules or user configuration to make a blocked call work.
The top-level `-z` help advertises approval bypass. Do not assume another mode shares its behavior.
Before unattended use, verify `approvals.single_query_mode: deny` and the actual launch path.

The gateway rejects the advertised `--run-budget` flag. Set and verify `agent.run_budget_seconds` in the owned profile instead.
The initial bounded preflight uses 300 seconds. Choose a suitable finite limit before each later task.
Use this command shape after verifying that configuration:

```sh
rtk proxy hermes -p crewshal chat \
  --query-file /absolute/private/task.md \
  --provider unsloth \
  --model unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL \
  --in /Volumes/X10Pro/Crewshal \
  --skills crewshal,codebase-memory,caveman,jev \
  --max-turns 45 --format stream-json
```

Replace the task path with an existing reviewed file. Use smaller limits for preflight tasks.
Do not dispatch product work until a bounded connection smoke test confirms the effective route and result collection.
Inspect structured events, session identity, exit status, and the actual filesystem diff.
Do not equate a zero process exit with task acceptance or assume every stream is valid JSONL.
If this interface fails, inspect its current local help and source once before choosing a supported alternative.
Do not cycle through unrelated modes, restart the model, or weaken approval controls.

Keep Codex available for intervention. Check progress without flooding the context with token streams.
Stop the identified run on repetition, scope violations, timeout, or refusal.
A gateway run can survive a client disconnect. Use supported session cancellation and verify its terminal state.
Verify termination before reviewing the candidate. Never kill an unrelated Hermes Desktop session or model server.
An interrupted process can leave effects. Inspect the owned files before retrying.
If CLI control remains unavailable, provide a prepared Desktop prompt and exact export requirements.
Label that route manual. Do not claim autonomous integration passed.

## Worker and child controls

Hermes must report its role as implementer. Sol 6.1 remains the supervisor.
Disable nested orchestration by default. Use one local worker to avoid competing memory-heavy model requests.
Any explicitly assigned child needs the same skills, graph and Jev tools, scope, context, and publication boundary.
`inherit_mcp_toolsets` is configuration only; the child must prove that its tools work.
Do not allow a child to approve its own work or create another coordinator hierarchy.
Keep profile changes owned by Codex and separate from ordinary source tasks.

## Integration and publication

Capture initial Git status and preserve any original dirty files.
When the primary checkout is shared, prevent concurrent workers from editing overlapping files.
Use an isolated candidate when useful, but never describe a worktree as a security sandbox.
Codex reviews the exact final diff and performs current acceptance checks before integration or publication.
A candidate identity change requires fresh affected evidence.
Publish only the coherent accepted checkpoint, then stop at the milestone boundary.
