# Next-session prompt: resolve the retained extraction decision

Work in `/Volumes/X10Pro/Crewshal` on the current branch.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, and `docs/ARCHITECTURE.md`.
Read ADRs 0001 through 0009 and `docs/evaluation/phase-3a-frozen/README.md`.
Read `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` as the single admission ledger.
Read the retained extraction proposal, member report, source checkpoint, decision proposal, extractor, and synthetic tests.
Verify every file in `docs/PHASE-3B-RETAINED-EXTRACTOR-SOURCE-INPUTS-2026-10-19.json` before using it.
Inspect Git state and preserve later work.

Do not extract retained archives unless the owner separately approves the exact decision proposal.
If approved, repeat all read-only custody, source-hash, quota, and output-root checks before the first write.
Bind the owner answer in the single ledger and run only its one specified extraction command.
Stop on any failure. Keep partial output for read-only review and do not retry or remove it.
Keep installation, archived tool execution, guests, Linux tests, native turns, providers, and evaluation rows closed.
Do not request an archive body or retry any consumed URL.
Preserve the fixed image, both receipts, frozen Phase 3A bytes, charges, and historical custody.

Record commands, results, environment, revision, costs, failures, and limits.
At completion or a blocked boundary, update README, CHANGELOG, handoff, next prompt, and synchronized versions.
Commit and push the current branch under standing owner authorization.

Feed these exact files first: `AGENTS.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, `docs/ARCHITECTURE.md`, ADRs 0001–0009, `docs/evaluation/phase-3a-frozen/README.md`, `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json`, `docs/PHASE-3B-RETAINED-EXTRACTION-PROPOSAL-2026-10-19.md`, `docs/PHASE-3B-RETAINED-ARCHIVE-MEMBERS-2026-10-19.json`, `docs/PHASE-3B-RETAINED-EXTRACTOR-SOURCE-2026-10-19.md`, `docs/PHASE-3B-RETAINED-EXTRACTION-DECISION-2026-10-19.md`, `scripts/phase3b_extract_retained.py`, and `tests/acceptance/test_phase3b_extract_retained.py`.
