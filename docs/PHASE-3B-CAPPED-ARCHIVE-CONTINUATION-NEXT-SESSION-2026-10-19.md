# Next-session prompt — make the halted archive continuation reviewable

Work in `/Volumes/X10Pro/Crewshal` on the current branch.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, and `docs/ARCHITECTURE.md`.
Read accepted ADRs 0001 through 0009 and `docs/evaluation/phase-3a-frozen/README.md`.
Verify every file in `docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-INPUTS-2026-10-19.json` before using it.
Inspect Git state and preserve later work.

Continue only exact archive continuation preparation.
Use `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` as the single admission ledger.
Read `docs/PHASE-3B-CAPPED-ARCHIVE-STAGE-2026-10-19.md`, `docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-2026-10-19.md`, and `docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-BOUNDARY-2026-10-19.md`.
Preserve the mounted image, all retained archives, and the original failed SQLite receipt.
Do not publish signed redirect URLs from the receipt.
Do not request any selected archive body or retry any attempted URL.

Resolve a trusted full Swift archive digest before its body request.
If no digest exists, prepare an exact signature-first amendment with the pinned Swift key and detached signature.
Do not treat the signature packet as a verified archive.
Implement a separate continuation transport and `continuation.sqlite3` receipt under the recorded plan.
Keep `receipt.sqlite3` read-only and failed. Reject all eight attempted IDs before any network request.
Bind the original receipt SHA-256, original scope, current manifest, new script hash, and eight unattempted IDs.
Pass local deterministic tests for redirects, errors, crash reservations, changed receipts, digest checks, and quota stops.

Keep all sixteen original URLs, per-object caps, 2,232,012,187-byte stage cap, and zero guest growth unchanged.
Keep the prior 8,589,934,592-byte charge and current 311,183,922-byte conservative charge intact.
Keep CMake, Ninja, dependency packages, guests, Linux tests, native turns, and evaluation rows outside this work.
Keep unobserved executable hashes, effective commands, providers, and B1 conformance null.
Preserve frozen Phase 3A bytes and historical custody.
Keep all 192 development rows planned and all 576 sealed rows unexposed.

Seek a separate owner decision only after the exact continuation transport, receipt, trusted inputs, quota, commands, and stop rules are reviewable.
No earlier approval authorizes transfer after the halt.
Record commands, results, environment, revision, costs, failures, and limits.
At completion or a blocked boundary, update README, CHANGELOG, handoff, next prompt, and synchronized versions.
Commit and push the current branch under standing owner authorization.
