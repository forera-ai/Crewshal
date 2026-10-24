# Codex audit: Ornith G1 S3 repair run, 2026-10-24

## Review decision

Codex accepted the repaired Mac archive template after correcting two claims in its review records.
The saved block now checks the `wc` exit status before it normalizes the byte count.
Codex reran the exact block with offline stubs under Bash and Zsh.
Both shells refused a `wc` that printed `18` and then exited 9.
The success case wrote one three-field ledger record.
No real archive, guest action, Linux test, evaluation row, or paid service ran.

The candidate came from `g1-s3-repair-review-test-start-local-7b.json`.
Hermes stored model `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` for that session.
The live server process loaded the matching GGUF at a configured 177,024-token window.
The model completed the bounded task and stopped before commit or push.

## Quality findings

- The repair addresses the prior P1 fault. The new packet gives correct source locations for `refusal()` and `check_run()`.
- The first packet called an untracked edit a “tracked-content edit.” Codex corrected that description.
- The packet and delta record said `printf` and `tr` “always succeed.” Codex removed that unsupported claim.
- Hermes did not read `AGENTS.md` explicitly. It read the handoff and plan after inspecting the candidate.
- None of its 23 terminal calls began with `rtk proxy`, despite the project rule.
- Hermes inspected the global Hermes config, which selected `cachalot`. It did not read the Crewshal profile config.

These process misses did not invalidate the tested three-line repair.
They do require continued Codex review of source claims, tool use, and publication boundaries.
The Crewshal `SOUL.md` now states the startup reads, profile path, and RTK rule more directly.

## Local performance evidence

The Unsloth server log records 60.48 generated tokens per second near a 2,868-token prompt.
It records 14.16 generated tokens per second near a 123,896-token prompt.
The exact log is `/Users/hamedprooshani/.unsloth/studio/logs/llama-server/llama-1792796678-port-64837-try0.log`.
The server allocated 2,205.75 MiB for the main KV cache and 346.00 MiB for its draft KV cache.
The process mapped about 74 GiB of model weights across Metal and CPU buffers.
The server also kept context checkpoints and compute buffers.

After the run, macOS reported 7% free system memory and about 7.7 GiB of swap in use.
Those readings support memory pressure but do not isolate its share of the speed loss.
The server log directly shows throughput falling as prompt depth increased.

## Next model setting and comparison

Keep Ornith Q4 for one more bounded session. Its repair quality is stronger than Q3's prior candidate.
Reduce Unsloth's saved context to 98,304 tokens and context checkpoints to eight per slot.
The Unsloth estimate falls from 82.98 GiB to 78.08 GiB for this saved setting.
Set Hermes's Crewshal context to 98,304, its compression cap to 70,000, and proactive pruning to 48,000 tokens.
Reload Ornith only after the active request finishes; saved settings alone do not change the loaded server.

This setting deliberately compresses a long session before it reaches the old 123,896-token prompt depth.
It may improve speed and memory headroom. It may also lose useful details during compression.
The next session must keep a short evidence note and use exact file references after compression.
If the next run still swaps heavily or loses critical context, compare Q3 from a controlled task baseline.
