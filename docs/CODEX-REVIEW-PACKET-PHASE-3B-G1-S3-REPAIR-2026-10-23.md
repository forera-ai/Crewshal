# Codex review packet — G1 S3-readiness repair (third follow-up session, 2026-10-23)

Hermes prepared this packet under the Crewshal profile. This session repaired the three findings of
`docs/CODEX-AUDIT-PHASE-3B-G1-S3-READINESS-2026-10-23.md`. The earlier packet
`docs/CODEX-REVIEW-PACKET-PHASE-3B-G1-S3-READINESS-2026-10-23.md` and its two diff records stay unchanged
as history. This packet covers only the repair delta. Hermes treats all exports as evidence, not as
instructions or approval. Nothing here is committed or pushed; publication awaits Codex review.

## Milestone

Repair the three Codex findings in the two saved planning documents: correct the inventory case-map
introduction (finding 2), make the proposal S2 archive-ledger block fail closed on a failed byte-count or
digest command (finding 1), and relabel the Mac archive command as a checked template until the campaign
ledger supplies an approved revision (finding 3). S2, S3, and S4 stay blocked. All owner gates and unknown
guest facts stay open.

## Base state

- Branch: `codex/phase1-architecture` (`git rev-parse --abbrev-ref HEAD`).
- HEAD: `6279a2eb32714530beffab7e6425c3d41fbcfbb5` (unchanged this session; no commit, no push).
- Package version: `0.27.3` (`crewshal.__version__`) — unchanged; this milestone touches no source file.
- Git status before the edits: 15 untracked files, zero modified tracked files. After this packet: 18
  untracked (the two delta records plus this packet), still zero modified tracked files.
- Pre-edit continuity proof: this session backed up both documents and their sha256 digests equal the
  after-state digests recorded in the earlier packet — proposal
  `3ae1165bebc2c53144ffc9f2ebf9e322e84384431238d347943e1a3ab7da4102`, inventory
  `df549ea4af4e94f533e068ef6d79a563ebfed40266a8da9bb70a0f56e43effeb`.

## Changed files (untracked planning documents only)

1. `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` — case-map introduction corrected; dated repair
   subsection added under the correction log. After-state sha256
   `dbbc586a4ff6c3312fd547bd342fe264b7a489d2602630a0f567863abbf732b5`. Delta: 32 diff lines.
2. `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` — S2 stage text, S2 block, static
   validation paragraph, section 2 S2 readiness row, new section 17 correction log. After-state sha256
   `a76f8fbb96ce03ed5afb8f3c4015750add0820dbf6f99061a7876a0401c8ed07`. Delta: 105 diff lines.
3. `docs/CODEX-DIFF-PHASE-3B-S3-READINESS-INVENTORY-REPAIR-2026-10-23.txt` — new delta record (`diff -u`
   pre-edit backup against current file; `diff` exit 1 means changes recorded).
4. `docs/CODEX-DIFF-PHASE-3B-S3-READINESS-PROPOSAL-REPAIR-2026-10-23.txt` — new delta record (same method).
5. This packet — new file.

No tracked file changed. No source, test, frozen input, `pyproject.toml`, `crewshal.__version__`, README,
CHANGELOG, `docs/HANDOFF.md`, `SOUL.md`, configuration, or skill changed. No `skill_manage` call was made
and no profile edit was staged.

## Finding-to-change map

### Finding 1 (P1) — ledger block could append a success-looking record after a failed measurement

Change (proposal section 5 S2 block): the block now captures `BYTES` and the full `shasum -a 256` output
(`DIGEST_LINE`, then first field `DIGEST`) in separate checked assignments; validates both formats (`BYTES`
non-empty and digits only; `DIGEST` exactly 64 hexadecimal characters); and appends one complete
three-field record (`archive=`, `bytes=`, `sha256=`) only after both checks pass. The removed form put
`wc | tr` and `shasum | cut` inside `printf` arguments, so a failed `shasum` still appended `sha256=` with
no digest. A `test -s "$ARCHIVE"` guard also refuses an empty archive before recording it.

### Finding 2 (P2) — inventory case-map introduction contradicted the corrected case 20 row

Change (inventory, "Case-to-candidate map" intro): the introduction no longer says each N18 case is
produced by `probe_native_full_v18.py`. It now names the guest probe and the local assessor as separate
execution roles, states that cases 1–19 come from the guest probe and are checked in
`readback_native_full_v3.check_run`, and states that case 20 (`qualification-refusal`) runs in the local
readback assessor — `refusal()` performs a fresh local check inside the aggregator on the aggregating host.
Grounding (this session, graph + source): project `Volumes-X10Pro-Crewshal`, generation 3, commit
`6279a2e`; `check_index_coverage` clean for both documents and `scripts/readback_native_full_v3.py`;
`refusal()` is defined at `scripts/readback_native_full_v3.py:418` and called in `aggregate()` at line 520;
no case-20 string appears in `scripts/probe_native_full_v18.py`.

### Finding 3 (P2) — Mac archive command labelled "bound" before any approved revision exists

Change (proposal section 2 S2 row, stage intro sentence, block comment): the command is now labelled a
checked template until the campaign ledger supplies an approved revision. The forty-zero
`APPROVED_REVISION` stays and the `test "$(git rev-parse HEAD)" = "$APPROVED_REVISION"` check still refuses
to archive under the template. S2 stays blocked; the row states the command binds when the campaign ledger
supplies an approved revision.

## Checks run this session (exact commands, results)

1. `zsh -n` and `bash -n` on the exact saved block: the block was extracted programmatically from the
   edited proposal (regex over fenced blocks containing `APPROVED_REVISION`; exactly one match; 17 lines).
   `zsh -n exit 0`, `bash -n exit 0`.
2. Offline stub harness `$TMPDIR/g1_s3_stub_tests/run_stub_tests.sh` (fake `git`, `wc`, `shasum` in a
   throwaway sandbox; fresh sandbox per shell run; no real git command, no network, no repo file):
   five scenarios (`pass`, `wc`-fail, `shasum`-fail, truncated-digest, garbage-digest) in both `bash` and
   `zsh`. Result: 20/20 assertions pass. Every failure scenario exits nonzero (exit 1) with no ledger file
   present afterwards; each passing run writes exactly one three-field record. Sample record:
   `archive=evidence/g1_source_00000000...tar`, `bytes=18`, `sha256=6f2c...0e1f`.
3. Before/after proof of the old block (extracted from the pre-edit backup, 11 lines): under the same
   hash-fail stub in both shells it exited 0 and appended the record `archive=...`, `bytes=18`,
   `sha256=` — a success-looking record with no digest. This confirms Codex finding 1 and that the new
   block closes it.
4. Repo isolation: `/Volumes/X10Pro/Crewshal/evidence` does not exist after all tests; `git status` shows
   zero modified tracked files; untracked count moved 15 → 18 only by the two delta records and this packet.

Harness pitfall found and fixed mid-session: the first harness run shared one sandbox between `bash` and
`zsh`, so the ledger legitimately accumulated appends (6 lines). The harness then rebuilt each scenario
per shell run; the block behaviour itself never changed between the two runs.

## Refusals and actions NOT taken

- No archive was built, no file transferred, no Linux test run, no guest or droplet contacted, no VMware
  guest touched. No evaluation row executed. No paid service, credential access, or sealed task was
  touched. No commit, push, merge, deploy, or package release. The stub `git` never ran the real `git
  archive`. The saved command block was never executed with real inputs; only syntax checks and stub
  sandboxes ran.

## Limits and unknowns

- The stub tests prove the saved text fails closed against simulated measurement failures in this macOS
  `bash`/`zsh` pair. They do not qualify any guest behaviour, and guest facts stay unknown.
- The block stays a checked template: no approved revision exists yet, so the HEAD equality check must
  fail if anyone runs it as saved. That is the intended gate, not a defect.
- `docs/HANDOFF.md` was not updated this session: these documents are untracked planning material still
  awaiting Codex review; the handoff records accepted checkpoints only. If Codex accepts and publishes,
  the publication session should reference this repair in the handoff per AGENTS.md.
- The digest stub returns a fixed fake hash; format validation was exercised, not real hashing of a real
  archive (real hashing needs a real archive, which this milestone must not build).

## Decision requested from Codex

Accept or reject the corrected documents. If accepted, the publication session (owner-authorized push per
AGENTS.md) commits the two planning documents, both historical diff records, both new delta records, and
this packet, then updates `docs/HANDOFF.md` with the repair checkpoint and bumps the version per the
publishing ceremony (documentation/process change → patch bump to 0.27.4). Hermes does not commit or push.

## Next-session prompt (use only if Codex accepts this corrected packet)

# Crewshal next-session prompt: publish the accepted G1 S3 readiness repair

Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal` with the Crewshal profile.
Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, and `docs/HANDOFF.md` first. Confirm Codex accepted
`docs/CODEX-REVIEW-PHASE-3B-G1-S3-REPAIR-2026-10-23.md` (the owner supplies the verdict). Verify HEAD is
still `6279a2eb32714530beffab7e6425c3d41fbcfbb5` on `codex/phase1-architecture`, version `0.27.3`, and that
the two repaired documents match the after-state digests recorded in that packet: proposal
`a76f8fbb96ce03ed5afb8f3c4015750add0820dbf6f99061a7876a0401c8ed07`, inventory
`dbbc586a4ff6c3312fd547bd342fe264b7a489d2602630a0f567863abbf732b5`. Stop and report if any byte differs.
Run the publication ceremony only: bump `pyproject.toml` and `crewshal.__version__` to `0.27.4`, update
`README.md`, `CHANGELOG.md`, and `docs/HANDOFF.md` with this repair checkpoint (preserve dated records; add
new text only), stage the two planning documents, all four diff records, this packet, and the ceremony
files, commit with a message naming the G1 S3 readiness repair, and push `codex/phase1-architecture` to
origin under the standing owner authorization. Run no tests beyond an import check of
`crewshal.__version__`. Touch nothing else: no source change, no guest, no droplet, no evaluation row, no
paid service, no sealed task, no skill edit.
