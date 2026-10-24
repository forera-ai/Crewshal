# Codex review packet — G1 S3 local readiness document corrections (2026-10-23)

Prepared by the Hermes Crewshal profile for Codex review. This packet changes no tracked file and requests
no commit or push from Hermes. Publication follows Codex acceptance under the standing AGENTS.md ceremony.

## 1. Milestone

Complete the local G1 S3 readiness documents for Codex review: close every finding of
`docs/CODEX-AUDIT-PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` in the driver inventory, and every applicable
finding of `docs/CODEX-AUDIT-PHASE-3B-G1-REVIEW-PACKET-2026-10-23.md` in the saved G1 proposal. Work touched
only those two untracked documents plus this packet and two diff records.

## 2. Base state (verified at session start)

- Branch: `codex/phase1-architecture` → `origin/codex/phase1-architecture`.
- HEAD: `6279a2eb32714530beffab7e6425c3d41fbcfbb5` (re-verified by the S2 archive-gate convention; see §5).
- Package version: 0.27.3. Version was not changed (documentation-only candidate; publication ceremony owns
  any bump decision).
- Git status before this session's edits: 11 untracked planning documents, zero tracked modifications.
  After this session: 14 untracked entries (the same 11 with two edited in place, plus this packet and two
  diff records). No tracked file changed at any point.

## 3. Changed files, digests, hunks

| File | sha256 before | sha256 after | Diff hunks |
| --- | --- | --- | --- |
| `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` | `646eff2c5766f2a2e9524ef2c9d026ecaae146bfa98caa5c48cc63ea8752cb62` | `df549ea4af4e94f533e068ef6d79a563ebfed40266a8da9bb70a0f56e43effeb` | 6 hunks (`@@ -4`, `-24`, `-34`, `-59`, `-70`, `-90`) in `docs/CODEX-DIFF-PHASE-3B-S3-READINESS-INVENTORY-2026-10-23.txt` (110 lines) |
| `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md` | `94d36d98a557a185c4d98c60058aed17ad81902973c884f76e391f29b18072f8` | `3ae1165bebc2c53144ffc9f2ebf9e322e84384431238d347943e1a3ab7da4102` | 8 hunks (`@@ -2`, `-46`, `-192`, `-330`, `-351`, `-361`, `-453`, `-460`) in `docs/CODEX-DIFF-PHASE-3B-S3-READINESS-PROPOSAL-2026-10-23.txt` (148 lines) |

The two `.txt` diff files are new untracked records; they reproduce the before/after bytes exactly. The
"before" copies also stand in `$TMPDIR/g1_s3_readiness_backup/` for this session only.

## 4. What changed and why (audit-finding mapping)

Inventory (`docs/CODEX-AUDIT-PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` findings):

1. Finding 1 (P1, false x86_64 guest claim): cross-cutting binding 2 no longer says "planned VMware x86_64
   guest". It now states the proposal targets Linux `aarch64` (stages S1/S3; option A2 bundle name says
   Ubuntu `arm64`), and keeps each guest's effective architecture and admission state unknown until the S1
   admission observation passes. U-5 stays open. No new unverified claim was added — neither guest's
   architecture is known, so none is asserted.
2. Finding 2 (P2, six wrong references): corrected against live source at HEAD `6279a2e`, each annotated
   "verified this session": protocol constant `scripts/readback_native_full_v3.py:20` (was `:19`);
   `refusal()` starts at line 62 (was 59; range now stated as 62-102); `allowed-grant` at line 179 (was 96);
   `configuration-binding` at line 359 (was 127); profile `CASES` at `scripts/probe_linux_profile.py:22`
   (the nine observed entries all sit on that one line; the old "slice line 40" was wrong); lifecycle
   `CASES` at `scripts/probe_linux_lifecycle.py:54` (old rows said line 37 and line 40). The two references
   the audit left unlisted were also re-verified against live source and corrected where they were off:
   network `executed_subset == ["network-egress"]` confirmed at `scripts/probe_linux_network.py:60`, and
   the v18 startup gate moved from "line 1301" to lines 1303-1304.
3. Finding 2b (case-20 label): row 20 now records execution location and evidence type — `refusal()` builds
   fresh fixtures against the bound product assessor on the aggregating host, and `check_run()` marks
   `qualification-refusal` from that local check at lines 132 and 423; it is explicitly not a guest
   containment observation from the v18 probe.
4. Finding 3 (provisionality): both the map intro and the doc intro now label every case mapping provisional
   until Codex accepts one driver for the case and the chosen guest passes its actual admission gate.
5. A dated correction-log section records all of the above inside the inventory.

Proposal (`docs/CODEX-AUDIT-PHASE-3B-G1-REVIEW-PACKET-2026-10-23.md` findings):

1. Finding 1 (P1, invalid archive command): the S2 block with the `<HEAD>` placeholder is replaced by an
   explicit `set -eu` block that binds `APPROVED_REVISION` to the Codex-approved full hash, proves HEAD
   equals it (`test "$(git rev-parse HEAD)" = "$APPROVED_REVISION"`), archives only that revision with fully
   quoted arguments, and appends archive path, byte count (`wc -c`) and sha256 (`shasum -a 256`) to
   `evidence/g1_delivery_ledger.txt` in the same saved block. The placeholder text now exists only inside
   the section-16 correction log describing the repair.
2. Finding 2 (P2, decision 4): owner decision 4 moved out of the pre-host-action set in section 12 to a new
   "Deferred" note tied to the later admitted gate that first requests native turns. Section 9 and U-9 were
   re-pointed to the same deferral. The numbering gap keeps cross-references to decisions 1, 2, 3 and 5
   stable.
3. Finding 3 (P2, S3 linkage): the section 2 S3 readiness row now cites the saved inventory with its
   candidate paths, digests, argument contracts and provisional case map, and states that binding closes per
   case only on Codex acceptance plus the guest's actual admission gate. S4 stays "Deferred; blocked" — no
   actual baseline runs are planned in G1.
4. Section 16 records both audits' closure inside the proposal; the preservation statement gained a dated
   paragraph for this session.

## 5. Commands and outputs (exact)

All commands ran on macOS at `/Volumes/X10Pro/Crewshal` unless shown otherwise. `rtk proxy` wrapped the git
and read-only source inspections. No command inside any checked shell block executed; no guest, Linux,
droplet, mount, download, live-probe, evaluation-row, sealed-row, credential, or paid action ran.

1. State check: `git rev-parse HEAD`, `git branch --show-current`, `git status --porcelain`,
   `git log --oneline -3`, version import — exit 0; values in §2 (11 untracked, 0 tracked changes).
2. Reference verification reads (live source, HEAD `6279a2e`): `sed`/`grep` over
   `scripts/readback_native_full_v3.py` (lines 17-22, 62-104, 125-135, 175-181, 355-361, 418-426),
   `scripts/probe_linux_profile.py:20-24` + `CASES`, `scripts/probe_linux_lifecycle.py` `CASES`,
   `scripts/probe_linux_network.py` `executed_subset`, `scripts/probe_native_full_v18.py:1299-1306`.
   Exit 0. Findings matched the audit exactly; two extra references (§4 item 2) were corrected beyond it.
3. Static shell checks (`$TMPDIR/g1_s3_readiness_backup/`):
   - `zsh -n saved_archive_block.sh` → exit 0; `bash -n saved_archive_block.sh` → exit 0 (saved block from
     the edited proposal, extracted programmatically from the document).
   - `zsh -n old_archive_block.sh` → exit 1, `parse error near '\n'`; `bash -n old_archive_block.sh` →
     exit 2, `syntax error near unexpected token 'newline'` on the `git archive ... <HEAD>` line (old block
     extracted from the pristine backup copy). This grounds the section-16 claim.
4. No-execution proof: `ls evidence` → `No such file or directory`; `evidence/g1_delivery_ledger.txt` does
   not exist; `git status --porcelain=v1 | wc -l` → 13 before this packet (11 original + 2 diff records), 14
   with the packet.
5. Diff digests: `diff -u` backup vs current produced the two recorded `.txt` diffs (exit 1 = differs);
   `shasum -a 256` values in §3.

## 6. Deferred and omitted checks

- The seven-module local suite was not rerun: this session changed no source, tests, or config; only two
  untracked planning documents. No concrete need arose (session instruction; AGENTS.md focused-testing rule).
- Linux-specific modules stay deferred per ADR 0009. `check_index_coverage` on the touched scripts was not
  requested because every cited line was read directly from live source this session (source fallback, not
  graph reliance).
- No guest architecture probe ran; both guests' effective architectures remain unknown by design.

## 7. Open gates after acceptance

1. Codex acceptance of one driver per case (§4 inventory mappings) — required before any S3 binding.
2. S1 admission observation (architecture, capacity floors, transport identity) — required before guest work.
3. Owner decisions 1, 2, 3, 5 remain unmade; decision 4 now sits at the later admitted native-turn gate.
4. S3 and S4 stay blocked; Linux conformance and Phase 3B calibration stay unclaimed.
5. Publication (version bump, commit, push) belongs to Codex under the AGENTS.md ceremony; Hermes held both.

## 8. Refusal cases honored this session

- No commit, no push, no version bump, no tracked-file edit, no `SOUL.md`/config change.
- No host approval request, no droplet, no guest boot/mount, no download or toolchain retrieval.
- No credential store access, no sealed-task exposure, no evaluation row, no paid service.
- No archive built or transferred; the saved command exists only as text plus static syntax checks.

## 9. Statement of separation

Every number above comes from a command this session ran and recorded. The corrected references are local
source facts at HEAD `6279a2e`. Nothing here authenticates execution origin, guest architecture, admission,
or any Phase 3B calibration claim. A matching digest proves bytes, not authority.
