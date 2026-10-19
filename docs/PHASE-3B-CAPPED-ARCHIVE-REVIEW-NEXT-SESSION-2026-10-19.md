# Next-session prompt — decide the halted archive continuation

Work in `/Volumes/X10Pro/Crewshal` on the current branch.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, and `docs/ARCHITECTURE.md`.
Read accepted ADRs 0001 through 0009 and `docs/evaluation/phase-3a-frozen/README.md`.
Verify every file in `docs/PHASE-3B-CAPPED-ARCHIVE-REVIEW-INPUTS-2026-10-19.json` before using it.
Inspect Git state and preserve later work.

Use `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` as the single admission ledger.
Read `docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-REVIEW-2026-10-19.md` and the historical stage, halt, and continuation records.
Keep the mounted image, retained archives, and original failed SQLite receipt intact.
Do not publish signed redirect URLs from the original receipt.
The original approval does not authorize another body request.

Seek the owner's separate decision on the exact seven digest-bound requests, new receipt, and new elapsed origin.
Ask separately whether the owner approves Swift signature-first verification under the pinned key and detached signature.
Do not request Swift's archive body until the two local signature inputs pass their hashes and the key fingerprint check.
Do not treat the signature packet as a verified archive.
If approval is absent, keep `owner_decision` null and `body_requests_admitted` false.

After explicit approval, recheck the script hash, manifest, original receipt hash, eight retained files, quota, and commands.
Create `continuation.sqlite3` only through the reviewed `prepare` command.
Request each admitted unattempted ID at most once. Stop after any failure or uncertain read.
Never retry an attempted URL or change the sixteen selected URLs, object caps, or 2,232,012,187-byte stage cap.
Keep the 8,589,934,592-byte prior charge and 311,183,922-byte current conservative charge intact.
Keep guest and VM growth at zero.

Keep CMake, Ninja, dependency packages, guests, Linux tests, native turns, and evaluation rows outside this stage.
Keep executable hashes, effective commands, providers, and B1 conformance null until observed.
Preserve frozen Phase 3A bytes and historical custody.
Keep all 192 development rows planned and all 576 sealed rows unexposed.

Record commands, results, environment, revision, costs, failures, and limits.
At completion or a blocked boundary, update README, CHANGELOG, handoff, next prompt, and synchronized versions.
Commit and push the current branch under standing owner authorization.
