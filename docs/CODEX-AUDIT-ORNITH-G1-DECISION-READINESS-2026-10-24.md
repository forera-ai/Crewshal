# Codex audit: Ornith G1 decision-readiness run, 2026-10-24

## Result

Codex reviewed `execute-next-test-prompt.md-instructions-local-ed.json` and the saved decision-readiness packet.
The session used `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` at a served 98,304-token context.
It produced one read-only packet and stopped before commit or push.
It did not act on a guest, run Linux tests, use a droplet, or spend money.

The packet's main conclusion is sound: proposal section 12 is ready for an owner decision.
That conclusion does not approve host action.
The owner must bind the named choices before the relevant stage acts.
Codex corrected the packet before acceptance.

## Corrections

1. The packet called option A1 an `x86_64` guest. The proposal keeps both guest architectures unknown.
   The S1 admission check requires Linux `aarch64` before dependent work.
2. The packet omitted two S4 owner choices. B1 commands and ten Linux baseline cases remain unbound.
3. The packet cited proposal section 4 and the owner decision packet for numbered choices.
   Only proposal section 12 numbers decisions 1, 2, 3, and 5.
4. The packet placed audit references at proposal lines 254–264. Those lines describe S2 and S3.
   The proposal does not name the later Ornith audit.
5. The packet used U-13 for retained archive bytes. U-13 names the missing wheel-closure ceiling.
   Proposal sections 3 and 8 record the retained archive bytes.
6. The packet called its direct source reads Tier 2 graph evidence. Hermes made no graph call.
   Codex's graph service returned `Transport closed`, so Codex checked the exact source directly.

Hermes did not read `AGENTS.md` explicitly. It read the development plan after other campaign documents.
Only one of six terminal calls contained `rtk proxy`; it did not prefix the whole terminal command with it.
One git history query was blocked by a Hermes deny rule. The packet now records that limitation.

## Local performance

The Unsloth log is `/Users/hamedprooshani/.unsloth/studio/logs/llama-server/llama-1792802172-port-53593-try0.log`.
It confirms `n_ctx = 98304` and eight context checkpoints.
Thirteen completed generation calls had a median speed of 27.33 tokens per second.
The deepest completed prompt used 68,762 tokens and generated at 26.21 tokens per second.
The next completed prompt used 1,986 tokens after a Hermes context summary.
No completed prompt exceeded 70,000 tokens in this run.

These results show that the 98,304-token setting kept this session below the prior 123,896-token prompt depth.
They do not isolate the effect of context size from task length, compression, cache reuse, or other apps.

## Model choice

Use Ornith Q4 at 98,304 tokens for bounded Crewshal source work with Codex review.
Its prior repair handled a failed command with plausible partial output that Q3 missed.
This run kept the requested execution boundary and produced a usable decision packet.
Its source and process errors prevent unsupervised acceptance or publication.
Keep Q3 as a faster fallback for drafting when Ornith's speed is the limiting factor.
