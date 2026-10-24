# Phase 3B G1 qualification plan — consolidated Linux campaign (read-only, 2026-10-23)

Hermes prepared this document under the Crewshal profile. Revision 3 repairs every finding in
`docs/CODEX-AUDIT-PHASE-3B-CAMPAIGN-REVISION-2026-10-23.md`. The follow-up session of 2026-10-23 closed the
six findings of `docs/CODEX-AUDIT-PHASE-3B-CAMPAIGN-REVISION-3-2026-10-23.md` (section 15). A second
follow-up session of 2026-10-23 applied the audits
`docs/CODEX-AUDIT-PHASE-3B-G1-REVIEW-PACKET-2026-10-23.md` and
`docs/CODEX-AUDIT-PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` (section 16). This document plans one bounded campaign:
the G1 consolidated Linux qualification gate from ADR 0009. It excludes all 192 development corpus rows,
all protocol amendment work, and all sealed evaluation work. Sections 1 and 12 state those boundaries.

Status: planning candidate for Codex review. This revision is **not approval-ready for host action** while
stage S0b transfer ceiling, stage S1b mount identity, stage S2 delivery, stage S3 probe drivers, or stage
S4 conformance bindings remain open. Section 2 names
each open binding and the exact decision that closes it. No host, guest, droplet, evaluation row, sealed
task, credential store, paid service, source file, version, frozen package, or Hermes configuration was
touched in this session.

## 0. What revision 3 changes (Codex audit REVISION findings)

| Audit finding | Revision 3 resolution |
| --- | --- |
| Finding 1 (P1) executable stage commands | Every stage now lists working directory, input identities, commands, expected results, evidence outputs, and stop rules. Guest commands no longer require `rtk`. Stages that cannot have safe concrete commands yet are marked blocked with one named smallest missing binding (section 2). |
| Finding 2 (P1) retrieval request ignores retained archives | The four selected corpus archives are recorded as retained on disk with digests from the readback inventory. No network retrieval is requested for them. A local remount-and-readback verification step (S1b) must confirm availability and digests first. Dependency downloads stay separate and require a finite measured ceiling before any request (section 8). |
| Finding 3 (P1) false withdrawal claims | The correction log (section 13) removes three entries that attributed wording to revision 1 which it never contained. The removals are evidenced against the actual export file. Exact original wording is preserved for the real corrections. |
| Finding 4 (P2) test classification broader than evidence | Section 6 replaces the skip-marker claim with a bounded-group classification from actual effects and fixtures, with reproduction commands and this-session run results. Live Linux probes (S3) stay separate from synthetic fixture tests (S2). |
| Finding 5 (P2) resource rules disagree | No proposed number is used as an effective stop threshold. Stop rules now reference only owner-approved limits. Until the owner records approved floors (decision 2), S1 records observations only and any host action stays blocked (section 7). |
| Finding 6 (P2) unsafe continuation prompt | The original review packet's continuation prompt is marked superseded in place, pointing to one current prompt in `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md`. |

## 1. Scope and boundary

- This plan covers gate G1 only: consolidated Linux qualification under ADR 0009 (owner decision packet
  `docs/OWNER-DECISION-PACKET-PHASE-3B-REMAINING-GATES-2026-10-23.md`, section "Remaining Phase 3B gates").
- The plan does not start any of the 192 development corpus rows. Gate G2 keeps its separate admission and
  budget gate (ADR 0008). Stage S5 states that boundary only.
- Gate G3 (protocol amendment before hold-out exposure) and Phase 3C stay closed. All 576 sealed rows stay
  unexposed.
- The plan completes platform qualification and baseline-conformance preparation for G1. It does not claim
  to complete every deferred Linux test in one campaign; the corpus rows stay behind gate G2.
- ADR 0009 controls: no Linux work during development sessions; this document is the consolidated campaign
  plan that ADR 0009 requires before any such action.

## 2. Stage readiness table

| Stage | Purpose | Status | Smallest missing binding |
| --- | --- | --- | --- |
| S0 | Local preflight and evidence baselining (macOS) | Bound | None. Runs with no approval (read-only); the bound first command creates `evidence/`. Sub-step S0b is blocked: no finite transfer ceiling exists in local records (audit REVISION-3 finding 2). |
| S1 | Host observation and capacity admission (guest) | Commands bound; stage blocked | Owner decision 1 (host selection) and decision 2 (resource floors). Guest identity values stay unknown until an approved observation supplies them. |
| S1b | Retained-archive verification (macOS, no network) | Blocked | The attach action plus its observed disk identifier or device node. `diskutil mount` accepts a disk identifier or device node, not the volume path; no device node exists in any record and the volume is unmounted this session (audit REVISION-3 finding 1). |
| S2 | Deterministic test suite on the guest | Blocked; only the Mac-side checkout-archive command exists, as a checked template (Codex G1 S3-readiness audit finding 3) | Owner decision 5 (transport method), then the guest-side preconditions (`source/` creation before extraction) plus S0b wheel closure and S1 observations. The command binds when the campaign ledger supplies an approved revision. This row does not claim the guest commands are bound (audit REVISION-3 finding 3). |
| S3 | Containment probe requalification (guest) | Blocked; local driver-candidate inventory saved | Per-case probe driver identity: for each of the 20 mandatory cases, the path and sha256 of one driver script plus its argument contract. The local candidate inventory is saved at `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` (candidate paths, digests, argument contracts, provisional case map). No ready runner exists in `src/crewshal/qualification.py`; it is a record contract only (`src/crewshal/qualification.py:10-31`, `assess_qualification`). Binding closes per case only when Codex accepts one driver and the chosen guest passes its actual admission gate. |
| S4 | Baseline conformance B0/B1/B2/P (guest, conditional) | Blocked | Two owner decisions: adopt the B1 manual script with its effective native commands bound in the campaign manifest (admission blocker unchanged), and define how the ten mandatory `baseline-conformance.json` cases run on Linux (the frozen case records carry macOS `sandbox-exec` commands). |
| S5 | Corpus execution boundary | Out of scope | None. Boundary statement only; requests nothing. |

## 3. Inputs and identities (local, verified this session)

| Input | Identity | Verification state |
| --- | --- | --- |
| Checkout revision | `6279a2eb32714530beffab7e6425c3d41fbcfbb5`, branch `codex/phase1-architecture` | Bound (S0 re-verifies; campaign binds the approved revision). |
| Frozen package | content sha256 `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`, 23 artifacts | Bound (checker passed at HEAD per owner decision packet line 32; S0 re-runs it). |
| Admission manifest | `docs/PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json` | Read-only inspected. Eight blockers, including "no effective native command observed" and the B1 draft block. |
| B1 manual script | `docs/PHASE-3B-B1-MANUAL-SCRIPT-2026-10-19.md`, sha256 `c031a045af15436462fa3100c14f32bc06005db5b651d8d8282dadaf1e02e1e7` (verified this session) | Source-bound draft. Grants no execution authority. |
| Frozen condition P | `docs/evaluation/phase-3a-frozen/conditions.json`, contract `phase3a-p-v1`, contract sha256 `c90cf576e4b55042566614ca978625d411fd9804d8072e150c9cc9ea048b9f91`, package version 0.15.2 (verified this session) | Bound reference. No new P contract is proposed. |
| Baseline conformance record | `docs/evaluation/phase-3a-frozen/baseline-conformance.json`: `mandatory_actual_cases` is a list of ten case-id strings (ids listed in section 5 S4). The value `native_execution: "unavailable"` belongs to the two candidate records, not to the case entries. The file records exactly one macOS `sandbox-exec` conformance command (`candidates[].fresh_source_conformance.command`), not one per case (verified against the file this session) | Bound reference. That single command is a macOS conformance fact and binds no per-case Linux run; Linux adaptation is an open S4 binding (audit REVISION-3 finding 4). |
| Containment case list | 20 mandatory case names pinned in `src/crewshal/qualification.py:10-31` | Bound list. Driver identity unbound (section 2, S3). |
| Retained toolchain readback | `docs/PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json`: 16 archives, compressed total 1,368,218,293 bytes, content upper bound 4,371,619,599 bytes | Bound ledger. On-disk availability unknown: volume `/Volumes/CrewshalPhase3BArchiveStage` is unmounted (S1b verifies). |
| Selected corpus archives | `docs/evaluation/phase-3a-frozen/corpus.json` pins each `archive_sha256`; the four archive byte counts come from `docs/PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json` (`archive_bytes`: python-1 343,014; typescript-2 1,580,238; swift-1 655,699; dotnet-1 198,331; sum 2,777,282, also recorded in the admission manifest). Digests compared pairwise this session: all four match. `corpus.json` does carry byte values at `repositories[i].source_identity.archive_bytes`; verified this session to equal the readback values (audit REVISION-3 finding 5). Pinned record values do not attest to current on-disk availability | Record values bound; on-disk availability stays closed until the S1b hash. All four also appear in the retained readback with identical per-archive digests (section 8). |
| Python runtime dependency | `pyproject.toml`: `requires-python >=3.12`; sole runtime dependency `pydantic==2.12.5` | S0b blocked: no finite transfer ceiling exists in local records; zero transfer allowance preserved (audit REVISION-3 finding 2) |

## 4. Host options and capacity facts (unchanged from revision 2)

| Option | Identity | Verified state | Unknowns |
| --- | --- | --- | --- |
| A1 — consolidated VMware guest | `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm` | Bundle path exists. Never opened this session. | Power state, Ubuntu release, effective CPU/RAM/disk, guest Python version. |
| A2 — offload VMware guest | `/Volumes/X10Pro/Internal-Offload-2026-09-15/Moved/Virtual Machines.localized/Crewshal Phase 3B Ubuntu arm64.vmwarevm` | Bundle path exists. Never opened this session. | Same as A1. |
| B — owner-prepared droplet | None selected, none provisioned | Excluded from the default G1 scope. | Price, region, transfer cost — all unknown. Any droplet variant needs its own finite cost exposure before approval. |

The previously selected VM reported 8 GiB RAM against a 16 GiB requirement. That recorded capacity stop
stands until the owner approves different floors (decision 2) and an observation confirms them.

## 5. Campaign stages, bound commands, and stop rules

Conventions for every stage:

- "Mac-side" commands run in `/Volumes/X10Pro/Crewshal` through `rtk proxy`. RTK is the owner's macOS
  Codex CLI wrapper (`/opt/homebrew/bin/rtk`). It stays on the Mac only.
- Guest-side commands are plain POSIX shell. They must not require `rtk`; it is not installed in any guest,
  and revision 2 wrongly prefixed guest commands with it (audit REVISION finding 1).
- Guest working root: `/srv/crewshal-batch/<batch-id>/`, batch-owned. Source extracts to
  `/srv/crewshal-batch/<batch-id>/source`. The venv lives at `/srv/crewshal-batch/<batch-id>/venv`.
- Evidence outputs are files under `evidence/` in the batch root, each with sha256 recorded on the Mac side
  after transfer.
- A failed check is preserved as evidence. Do not retry a failure to manufacture a pass.

### Stage S0 — local preflight (macOS, read-only, no approval needed)

Working directory: `/Volumes/X10Pro/Crewshal`. Input identities: section 3. Commands:

```
mkdir -p evidence                                    # binds the output dir; its files stay untracked
git rev-parse HEAD                                   # expect the approved revision or its successor
.venv/bin/python scripts/check_phase_3a_freeze.py    # expect exit 0, content sha256 unchanged
env -u PYTHONPATH .venv/bin/python -m unittest \
  tests.acceptance.test_phase3b_development_ledger \
  tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a \
  tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch \
  > "$TMPDIR/g1_s0_regression.log" 2>&1              # expect exit 0; never accept a piped-away exit code
shasum -a 256 scripts/native_full_boundary_v*.py \
  scripts/native_credential_negative_v*.py \
  scripts/native_fixed_response_fixture_v*.py \
  scripts/native_authenticated_response_fixture_v*.py \
  > evidence/g1_driver_candidates.txt                # evidence for the S3 driver selection decision
```

Expected results: revision match; checker exit 0 with unchanged digest; regression exit 0 with recorded test
count; driver-candidate inventory with one sha256 per line. Evidence outputs: `g1_s0_regression.log`,
`g1_driver_candidates.txt`. Stop rule: any mismatch stops the campaign before any host contact.

Sub-step S0b — guest wheel closure (BLOCKED; audit REVISION-3 finding 2): a network download must have a
finite ceiling fixed before any request. A `pip download` run measures its own output only after the
transfer completes, so it cannot establish its own ceiling, and a general go-ahead binds neither maximum
response bytes nor dependency closure size. No local record fixes a byte ceiling for the `pydantic==2.12.5`
manylinux_2_28_aarch64 wheel closure: this session grepped every file under `docs/` and found no such
figure. The locally installed macOS build (7,600 KiB across four `site-packages` directories, measured with
`du -sk`) is reference data for a different platform's artifacts, not a ceiling. S0b therefore stays blocked
and the zero transfer allowance is preserved. No download command is given. The binding closes when the
owner fixes a finite byte ceiling from a derivation this document can cite, or admits a metadata-only
lookup that yields one; only then may a future session bind an exact download command.

### Stage S1 — host observation and capacity admission (chosen guest, read-only)

Blocked until owner decision 1 selects the host. Working directory: operator login shell on the chosen
guest. Commands (plain POSIX):

```
uname -s; uname -m; uname -r                 # expect Linux aarch64 for option A
cat /etc/os-release                          # record exact Ubuntu release
nproc                                        # record CPU count
free -b                                      # record RAM bytes
df -k /srv                                   # record free disk KiB (create /srv path only with owner go-ahead)
command -v git tar sha256sum python3         # record paths; record python3 --version
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'   # expect exit 0
```

Expected results: a complete observation ledger `g1_s1_host.json` with every value above. Evidence outputs:
the ledger plus raw command transcripts. Stop rules: not Linux aarch64 → stop and report. Missing any
listed tool → stop and report. Python older than 3.12 → stop and report; do not install anything without an
owner decision. Resource values are recorded, not thresholded: the effective capacity stop uses only floors
the owner approved in decision 2. If no floors are approved, S1 produces observations and the campaign stays
blocked before any mutating stage (audit REVISION finding 5).

### Stage S1b — retained-archive verification (macOS, no network) — BLOCKED

Working directory: Mac side. Purpose: confirm the retained archives that revision 2 wrongly proposed to
download again (audit REVISION finding 2), with zero network transfer.

Bound identities (verified this session):

- Image: `/Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg` — the fixed RAW image behind volume
  `/Volumes/CrewshalPhase3BArchiveStage`; logical size 3,221,225,472 bytes
  (`docs/PHASE-3B-CAPPED-ARCHIVE-HALTED-2026-10-19.md:20-21,68-69`). Present on disk this session (`ls`).
- The sparseimage `/Volumes/X10Pro/Crewshal-Phase3B-Remaining-Stage-20261020.sparseimage` holds only the
  four Remaining-stage archives (claude-native, codex-native, dotnet-sdk, swift); none of the four selected
  corpus archives lives there (`docs/PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json` output roots).
- Archive paths: `/Volumes/CrewshalPhase3BArchiveStage/archives/<id>.blob` for id in {python-1,
  typescript-2, swift-1, dotnet-1}. The stage scripts write `<root>/archives/<id>.blob`
  (`scripts/phase3b_capped_archive.py:225,299`); the recorded example is `archives/dotnet-sdk.blob`
  (`docs/PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-BOUNDARY-2026-10-19.md:117`). The four `.tar.zst` names that
  revision 3 of this section hashed appear in no record and are removed (audit REVISION-3 finding 1).

Blocked, with the smallest missing binding named: `diskutil mount` requires a disk identifier or device
node, not a volume path. No disk identifier or device node is recorded in any repository document, and the
volume was unmounted when this session listed `/Volumes/`. This proposal therefore gives no mount command;
inventing one is forbidden. The binding closes when the owner approves the exact attach action for the image
path above and the observed disk identifier or device node is recorded in the campaign ledger. Mounting
stays an owner-only exact action until that approval exists.

Read-only verification steps once attached (no writes to the image): for each of the four ids, `stat` the
blob byte length against the expected value, then `shasum -a 256` against the digest recorded in the
readback JSON (verified identical to `corpus.json` this session): python-1
`edfa6cf117bbbe46f6690266a40389b08b12cbf87fad8664d349ebd6eea811a1` (343,014 bytes), typescript-2
`4754f74b4defcbaa9b8748406fcd3e974b756abf7824e8a1a4304ec9665e6ced` (1,580,238 bytes), swift-1
`45c952a441611e17d8c30de26c4a6b40eec483c07900d9faad2501539aa5c900` (655,699 bytes), dotnet-1
`71a77a7c2eb4d1ffa1572c97c9050c673e16f24cdac19d5039ad79cad06a26dd` (198,331 bytes). Expected results: four
matching lengths and digests; total 2,777,282 archive bytes available with zero network transfer. Evidence
output: `g1_s1b_archive_verification.txt`. Stop rules: attach fails or is refused → record and stop this
stage; the four archives stay "availability unknown". A length or digest mismatch → stop and preserve both
records. Only after a mismatch or unavailable result may any later document request re-retrieval, and only
with the finite ceiling of 2,777,282 bytes plus these four digests.

### Stage S2 — deterministic test suite on the chosen guest

Blocked; the stage readiness row does not claim bound guest commands (audit REVISION-3 finding 3). Only
the Mac-side checkout-archive command below exists, and only as a checked template until the campaign ledger
supplies an approved revision (Codex G1 S3-readiness audit finding 3). Source delivery contract: the Mac side creates one
clean archive of the approved revision, records its byte count and sha256 in `evidence/g1_delivery_ledger.txt`,
then transfers it by the owner-selected private transport (decision 5); the transfer command stays unbound
until decision 5 names the method. Checked-template Mac-side commands (working directory
`/Volumes/X10Pro/Crewshal`). Until the campaign ledger supplies an approved revision, this sequence is a
checked template, not a bound command: `APPROVED_REVISION` stays forty zeroes and the HEAD equality check
refuses to archive under it (Codex G1 S3-readiness audit finding 3). The earlier `<HEAD>` placeholder text
failed `zsh -n` with `parse error near '>'` and failed `bash -n`; it is replaced by an explicit, quoted
variable form (Codex G1 review-packet audit finding 1). When Codex accepts a revision in the campaign
ledger, the session replaces the forty-zero placeholder with that full commit hash. The command sequence
archives exactly HEAD only after proving HEAD equals that approved revision; no floating ref is archived.
It captures the byte count and the full digest output in separate checked assignments, validates both
formats, and writes one complete ledger record only after both checks pass (Codex G1 S3-readiness audit
finding 1):

```
set -eu
APPROVED_REVISION="0000000000000000000000000000000000000000"   # checked template: the campaign ledger binds the Codex-approved full hash here
test "$(git rev-parse HEAD)" = "$APPROVED_REVISION"            # archive exactly HEAD, and only the approved revision
mkdir -p evidence
ARCHIVE="evidence/g1_source_${APPROVED_REVISION}.tar"          # output stays untracked
git archive --format=tar -o "$ARCHIVE" "$APPROVED_REVISION"
test -s "$ARCHIVE"                                             # refuse an empty archive before recording it
BYTES_RAW="$(wc -c < "$ARCHIVE")" || exit 1                    # capture the byte count alone; a failed wc aborts before any record
BYTES="$(printf '%s' "$BYTES_RAW" | tr -d ' ')"                # strip surrounding whitespace from the captured count
DIGEST_LINE="$(shasum -a 256 "$ARCHIVE")" || exit 1            # capture the full digest output; a failed digest command aborts before any record
DIGEST="${DIGEST_LINE%% *}"                                    # the first whitespace-delimited field is the digest
test -n "$BYTES" || exit 1                                     # fail closed when the byte count is missing
case "$BYTES" in *[!0-9]*) exit 1 ;; esac                      # byte count must be digits only
test "${#DIGEST}" -eq 64 || exit 1                             # digest must be exactly 64 characters
case "$DIGEST" in *[!0-9a-f]*) exit 1 ;; esac                  # digest must be hexadecimal only
{                                                                              # one complete record, written only after both checks pass
  printf 'archive=%s\nbytes=%s\nsha256=%s\n' "$ARCHIVE" "$BYTES" "$DIGEST"
} >> evidence/g1_delivery_ledger.txt                                           # byte count and digest recorded before transfer
```

Static validation (this session): the saved block passes `zsh -n` and `bash -n` with exit 0; the old
placeholder block failed both. Offline stub tests ran this session in `$TMPDIR/g1_s3_stub_tests` only, with
fake `git`, `wc` and `shasum` commands and no real archive: a failing byte-count command, a failing hash
command, and a truncated-digest hash command each made the block exit nonzero before any append, so no
ledger record exists afterwards; passing stubs wrote exactly one three-field record. The real sequence was
never run: this document milestone builds and transfers nothing, `evidence/` stays absent in the checkout,
and the ledger file did not get created.

The guest commands below are a draft contract, not bound: they run only after decision 5 binds the arrival
path and S0b/S1 outputs exist, and they must create `source/` before extraction. Draft contract (guest,
plain), working directory after delivery `/srv/crewshal-batch/<batch-id>/`, source root
`/srv/crewshal-batch/<batch-id>/source`:

```
cd /srv/crewshal-batch/<batch-id>
mkdir -p source evidence wheels                   # create every target dir before extraction (finding 3)
sha256sum source.tar                                # must match g1_delivery_ledger.txt before extracting
tar -xf source.tar -C source
python3 -m venv venv
venv/bin/python -m pip install --no-index --find-links wheels/ pydantic==2.12.5
cd source
env -u PYTHONPATH ../venv/bin/python -m unittest discover -s tests/acceptance -p 'test_*.py' \
  > ../evidence/g1_s2_suite.log 2>&1                # expect exit 0; record the module and test counts
```

Expected results: digest match; discovery reports the bounded module count from section 6; suite exit 0 or
a preserved failure. Evidence outputs: delivery ledger, `g1_s2_suite.log`, group results per section 6.
Stop rules: digest mismatch → stop before extraction. Any test failure → preserve output, report, no retry.
On Linux aarch64 this stage is the deferred Linux execution of these modules; its result does not qualify
containment or conformance (those are S3/S4). Discovery here is scoped to `tests/acceptance` on the guest by
design; it must never replace the named-module regression set used for local acceptance.

### Stage S3 — containment probe requalification (guest) — BLOCKED

Input identities: the 20 mandatory case names at `src/crewshal/qualification.py:10-31`, matching the
"Platform qualification cases" list in `docs/PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md`. The failed Orka
case stays failed. The v18 profile must be requalified on Linux aarch64 (U-5). Every null
`installed_executable_sha256` in the readback becomes an observed value or stays unknown (U-6).

No command is safe to bind yet. `src/crewshal/qualification.py` is a record contract; it executes nothing.
Smallest missing binding: for each case, the path plus sha256 of one driver script and its argument
contract, chosen from the S0 driver-candidate inventory or built in a separate source milestone, then
reviewed by Codex. Until that table exists, S3 has no launch command and the campaign cannot claim probe
coverage (audit REVISION finding 1). Stop rule when bound: any failed hard control closes agent-file-write
eligibility for that host until fixed and retested; agent writes stay disabled until this stage passes.

### Stage S4 — baseline conformance B0/B1/B2/P (guest, conditional) — BLOCKED

Input identities are bound: the four conditions in `conditions.json` (condition P: contract
`phase3a-p-v1`, sha256 `c90cf576…`, package 0.15.2); the ten mandatory actual cases in
`baseline-conformance.json`: same-input-task-checks-budgets, fresh-workspace-and-context,
exact-resolved-identities, provider-independent-read-only-review, trusted-check-and-terminal-capture,
scope-and-approval-refusal, failed-and-unavailable-check-accounting, cancel-timeout-restart-no-replay,
honest-usage-and-cache-accounting, setup-and-configuration-effort. The B1 draft script is cited above with
its sha256. No new P contract is proposed.

No command is safe to bind yet. Smallest missing bindings: (1) the owner decision that adopts the B1 draft
with its effective native commands bound in the campaign manifest — the admission manifest blocker "no
effective native command observed" stands; (2) a Linux runner definition for the ten mandatory cases — the
frozen file records exactly one macOS `sandbox-exec` conformance command
(`candidates[].fresh_source_conformance.command`), not one per case, so no frozen command binds a Linux run
(audit REVISION-3 finding 4). G1 includes no actual baseline turns: running the ten cases sits behind a later
gate. Until both bindings exist, S4 requests nothing and runs nothing.

### Stage S5 — corpus execution (out of scope; boundary statement)

The 192 development rows do not start in this campaign. They require a separate budget and admission
decision (gate G2). This proposal requests nothing for S5.

## 6. Test module classification (replaces the revision 2 skip-marker claim)

Revision 2 claimed all acceptance modules were platform independent because no skip markers exist. That was
broader than its evidence (audit REVISION finding 4). This section classifies from actual effects and
fixtures. Reproduction commands (Mac side, read-only):

```
ls tests/acceptance/test_*.py | wc -l                                        # 79 test modules (+ __init__.py)
grep -lE 'crewshal\.linux_' tests/acceptance/test_*.py | wc -l               # 38
grep -lE "patch\(['\"]crewshal\.linux_" tests/acceptance/test_*.py           # 15, listed below
grep -lE 'platform\.system|platform\.machine|uname|sys\.platform' tests/acceptance/test_*.py   # 7, listed below
grep -lE 'subprocess\.(run|Popen|check)|os\.fork|\bexecv' tests/acceptance/test_*.py | wc -l   # 27
```

Bounded groups for S2 reporting (groups overlap; a module may belong to several):

| Group | Definition (from source effects) | Count | Meaning on the guest |
| --- | --- | --- | --- |
| G-a | Modules that import or reference `crewshal.linux_*` and drive them with synthetic fixtures. 15 of them patch `crewshal.linux_*` internals directly: attempt_marker, bootstrap, bootstrap_build_closure, bridge, charged_build, file_cache, fixture_inputs, freeze, installed_chain, network, operational, parent, policy_directories, storage, validator (all `test_phase_2d_*`). | 38 | These simulate Linux semantics through mocks. They run on the guest as fixture tests; their pass does not prove real Linux behavior. |
| G-b | Modules that reference platform values (`platform.system`, `platform.machine`, `uname`, `sys.platform`): test_phase_2d_admission, bootstrap, bootstrap_build_closure, file_cache, installed_chain, network, supervisor. These patch Linux platform values and kernel-interface shapes in fixtures. | 7 | On the guest the real values become observable; record any fixture-versus-host divergence as evidence. |
| G-c | Modules that launch real subprocesses (git, python, shell helpers). Their behavior depends on the observed host tool identities from S1. | 27 | Run as-is; failures against real host tools are findings, not flakes. |
| G-d | The three Phase 2C native readback/continuation fixture modules (`test_phase_2c_native_*`, 12 tests). Re-verified this session on macOS: exit 0 (log `$TMPDIR/rev3_fixture_run.log`). | 3 modules / 12 tests | Fixture tests. Their macOS pass is kept separate from any Linux claim. |

Classification limits: these counts come from the four grep commands above; they are effect-shape proxies,
not proof of behavior for each of the 79 modules. No module was executed on Linux (none could be). Live
Linux probes stay exclusively in S3 and never merge into this suite's verdict.

## 7. Resource ceilings (proposed values; effective stops use approved limits only)

| Unit | vCPU | RAM | Disk | Wall ceiling | Approval status |
| --- | ---: | ---: | ---: | ---: | --- |
| Preparation tree (per host) | 4 | 12 GiB | 24 GiB working | 8 h active / 24 h wall | Proposed, not approved |
| One task unit, native runtime | native ceiling | 768 MiB attempt ceiling | shared working tree | 600 s deadline | Proposed, not approved |
| One validator run | 4 | 8 GiB | 8 GiB | 900 s | Proposed, not approved |
| Concurrent execution units | 1 | — | — | batch 14 days | Proposed, not approved |

Rule (audit REVISION finding 5): no value in this table gates a stage. The effective capacity stop at S1 is
the floor set the owner records in decision 2. If that decision is absent, mutating stages stay blocked and
S1 reports observations only. ADR 0009 lines 39-40 keep these amendments parked; the approved zero metered
billing and zero paid-host limits remain unchanged until separate owner decisions replace them.

## 8. Transfer and storage ledger (corrected against retained archives)

| Item | Identity | Bytes | Direction | State |
| --- | --- | ---: | --- | --- |
| Source delivery | `git archive` of the approved revision; exact size recorded in `g1_delivery_ledger.txt` before transfer | unknown until built | Mac → guest, private transport (decision 5) | Finite once built; digest-verified before extraction |
| Guest wheel closure | `pydantic==2.12.5` aarch64 wheel closure | no finite ceiling derivable from local records (audit REVISION-3 finding 2) | would be local fetch + Mac → guest | Blocked. Zero transfer allowance preserved; the owner must fix a finite ceiling before any request |
| Selected corpus archives (4) | python-1, typescript-2, swift-1, dotnet-1 with digests in section 5 S1b | 2,777,282 total (known) | already retained on `/Volumes/CrewshalPhase3BArchiveStage` | **No network retrieval requested.** Availability verified by S1b; re-retrieval only after an S1b failure, with the finite ceiling and digests stated in S1b |
| Frozen package | content sha256 `4bd188deb0…`, inside the source archive | 0 extra | none | Bound |
| Ubuntu system packages (apt closure) | unresolved | unknown | would need guest network | Not requested. Any future request must state a finite ceiling first; this proposal asks for no unknown-ceiling network allowance |

Revision 2 had proposed a new network allowance to retrieve the four archives above. The retained readback
inventory (`docs/PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json`) records all four with identical
digests, so that request is withdrawn in revision 3 and replaced by the local S1b verification. The
cumulative conservative transfer charge remains 10,125,027,074 bytes (unchanged historical record).

## 9. Duration and cost exposure

- Per-stage wall ceilings are the proposed values in section 7. They are not approvals.
- Option A (VMware): no metered service; energy and owner time only. G1 requests no new network transfer:
  S0b stays blocked until the owner fixes a finite byte ceiling (audit REVISION-3 finding 2).
- Actual baseline turns: G1 includes none. The ten `mandatory_actual_cases` do not run in G1; S4 work in G1
  is binding preparation only, and S4 stays blocked until its runner and limits are bound (audit REVISION-3
  finding 4).
- Option B (droplet): excluded from the default scope. If the owner selects it, that variant returns with a
  stated price, time ceiling, and cost exposure before any approval (unchanged October 5 rule).
- Subscription quota: this plan runs no native runtime turns. The manifest records
  `subscription_quota_debit: "unknown; requires later owner acceptance"` at line 593 and per-runtime turn
  limits of 256/256 (`resource_ledgers.subscription_turn_limits`). Accepting a possible debit is moved to
  the later admitted gate that first requests native turns (section 12, audit finding 2); no quota decision
  and no quota submission are requested before host action in G1.

## 10. Cleanup authority (unchanged from revision 2)

The batch-owned root `/srv/crewshal-batch/<batch-id>/` and its `evidence/` contents are retained until the
owner accepts the campaign report. After acceptance, cleanup means: stop related processes only; remove the
batch paths above; preserve the read-only staging roots and all retained archives. No path outside the batch
root is removed by this campaign. Evidence retention follows ADR 0004 ownership rules.

## 11. Unknowns (renumbered)

- U-1: guest selection (decision 1).
- U-2: guest power state, Ubuntu release, effective CPU/RAM/disk; the recorded 8 GiB capacity stop stands
  until decision 2 and an observation replace it.
- U-3: transport method for source delivery (decision 5); delivery byte count unknown until built.
- U-4: guest tool identities and versions (`git`, `tar`, `sha256sum`, `python3` ≥3.12) — S1 observes them.
- U-5: Linux aarch64 requalification of the v18 profile (S3, blocked on driver bindings).
- U-6: installed executable digests for retained toolchains (null in readback; become observed or stay unknown).
- U-7: B1 effective native commands and the P-run definition on Linux (S4 blockers).
- U-8: Ubuntu package closure bytes (unrequested; needs a finite ceiling first).
- U-9: subscription quota debit (deferred to the later admitted gate that requests native turns; no G1
  submission planned, no acceptance requested before host action).
- U-10: retained-archive availability (volume unmounted; S1b verifies without network).
- U-11: per-case containment probe drivers (S3 blocker; S0 inventory feeds the choice).
- U-12: archive-volume attach identity — no disk identifier or device node is recorded in any document, and
  the volume is unmounted this session (S1b blocker, audit REVISION-3 finding 1).
- U-13: a finite byte ceiling for the `pydantic==2.12.5` aarch64 wheel closure — absent from every local
  record (S0b blocker, audit REVISION-3 finding 2).

## 12. Owner decisions required before any host action

Four decisions gate a host action. The earlier decision 4 (quota acceptance) left this pre-host-action set
in this session (Codex G1 review-packet audit finding 2); its text stays below in the deferred note, and the
numbering keeps a gap so cross-references to decisions 1, 2, 3 and 5 stay stable.

| # | Decision | Effect when recorded |
| --- | --- | --- |
| 1 | Select the G1 host: option A1, option A2, or a separately-priced droplet variant (option B returns with its own cost exposure first). | Unblocks S1 command execution. |
| 2 | Record approved CPU/RAM/disk floors for the campaign, or explicitly keep them unapproved. | Makes S1 capacity stops effective; if unapproved, mutating stages stay blocked. Parked proposals in section 7 are never applied implicitly. |
| 3 | Fix a finite byte ceiling for the guest wheel closure before any S0b request (audit REVISION-3 finding 2), and approve the exact archive-image attach action whose observed disk identifier or device node is then recorded in the campaign ledger (finding 1). | Unblocks S0b and S1b only after both identities exist; opens no unknown-ceiling network allowance. |
| 5 | Select the source delivery transport (private path, owner-performed copy, or other private method). | Unblocks S2 delivery; byte count and digest are recorded before transfer regardless of method. |

Deferred (not requested before any host action): accept or defer the possible subscription quota debit
(manifest line 593; per-runtime turn limits 256/256). G1 plans zero native runtime turns and zero actual
baseline runs, so this decision moves to the later admitted gate that first requests native turns; that
gate must state each turn's exact purpose and a bounded count before approval. U-9 stays open until then.

No decision in this list opens a network allowance with an unknown ceiling. No decision here authorizes G2
corpus rows, sealed exposure, Phase 3C, deployment, or package release.

## 13. Correction log — revision 1 to revision 2 (corrected per audit REVISION finding 3)

Evidence source for this section: the actual export file
`/Users/hamedprooshani/Downloads/prepare-consolidated-linux-campaign-plan-local-24.json` (83 messages; the
revision-1 document text is the `write_file` call in message 72, and its one in-session ledger patch is
message 76). Grep results against that extracted text are quoted below.

Genuine corrections kept (exact original wording from revision 1):

1. B1 claim withdrawn. Revision 1 §S4 said: "Blocked on two owner decisions from the decision-packet line:
   no B1 manual script exists in the repository, and condition P lacks a defined contract." It also said at
   U-7: "B1 manual script (absent) and condition P contract (undefined)." Both records exist: the source-bound
   draft (`c031a045…`) and the frozen P contract `phase3a-p-v1`.
2. Fabricated manifest key withdrawn. Revision 1 §7 cited "`development.proposed_quota_submission_ceiling`"
   as a quota cap. The manifest has no such key; it records `subscription_quota_debit` (line 593) and
   `subscription_turn_limits` 256/256 instead.
3. Retained-bytes sum corrected in place. Revision 1 first wrote "1,459,270,803 observed sum" for the 16
   retained archives and patched it during its own session to "1,368,218,293 computed sum". The readback
   JSON confirms 1,368,218,293.
4. Corpus transfer row replaced by measured bytes. Revision 1 §6 said: "Corpus archives | The 12 `corpus.json`
   repository entries pinned by `archive_sha256`. Byte counts are not pinned. | unknown until download;
   proposed ceiling 12 GiB total". The four selected archives have exact pinned byte counts at
   `repositories[i].source_identity.archive_bytes` in `corpus.json` (sum 2,777,282; audit REVISION-3 finding
   5), and the retained readback records them as retained; on-disk availability stays closed until S1b.
5. Six-module exclusion withdrawn as source-resolved. Revision 1 §S2 listed six modules under the comment
   "# the six modules recorded as Linux-specific under ADR 0009". Section 6 classifies by actual effects
   instead.

Entries removed from this log (audit REVISION finding 3 — revision 1 never made these claims, so no
withdrawal was possible):

- "96,154,107,538 retained bytes" — absent from the revision-1 text (grep found no match in the extracted
  message-72 content). The figure first appeared inside revision 2's own correction log.
- "up to four elapsed days" — absent from the revision-1 text. Revision 1's only duration values were the
  per-unit ceilings ("8 h active / 24 h wall", "600 s deadline", "900 s", "batch 14 days"), which revision 2
  and this revision keep as proposed values.
- "no baseline conformance record exists" — absent from the revision-1 text. Revision 1 cited
  `docs/evaluation/phase-3a-frozen/baseline-conformance.json` in §S4 ("Four-condition matrix per …"). Only
  the B1 half of that correction-log entry was real.

## 14. Correction log — revision 2 to revision 3 (this session)

1. Removed every false withdrawal claim from sections 1 and 8 above and marked the affected entries in both
   review packets (audit REVISION finding 3).
2. Replaced the four-archive retrieval request with retained-digest verification S1b; kept dependency
   closure separate behind the finite measured ceiling rule (finding 2).
3. Bound working directories, input identities, expected results, evidence outputs, and stop rules for every
   stage; removed `rtk` from all guest commands; marked S3 and S4 blocked with one named smallest missing
   binding each instead of deferred placeholders (finding 1).
4. Replaced the skip-marker classification with section 6's bounded-group classification from actual effects,
   reproduction commands, and this-session fixture re-runs (finding 4).
5. Removed all parked-number stop thresholds; stops now reference owner-approved limits only, and absent
   approvals keep mutating stages blocked (finding 5).
6. Marked the original review packet's continuation prompt superseded in place; one current prompt lives in
   `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md` (finding 6). That packet did
   not exist at the time of writing; the follow-up session of 2026-10-23 created it.

## 15. Correction log — audit REVISION-3 closure (follow-up session, 2026-10-23)

1. S1b corrected (finding 1): the four `.tar.zst` names matched no record and are removed. Bound identities:
   image `/Volumes/X10Pro/Crewshal-Phase3B-Archive-Stage-20261019.dmg`, volume
   `/Volumes/CrewshalPhase3BArchiveStage`, archive paths `<volume>/archives/<id>.blob` per
   `scripts/phase3b_capped_archive.py:225,299`. No disk identifier or device node is recorded anywhere and
   `diskutil mount` requires one, so S1b is marked blocked and no mount command is given. Mounting stays an
   owner-only exact action.
2. S0b corrected (finding 2): the download-first-then-measure order is removed. No finite ceiling exists in
   local records; S0b is blocked and the zero transfer allowance is preserved.
3. S0 binds `evidence/` creation as its first command (finding 3). S2 gives exact Mac-side commands with
   bound paths, keeps the guest commands as an unbound draft contract that creates `source/` before
   extraction, and the section 2 row no longer says the guest commands are bound.
4. The baseline description is corrected against the frozen file (finding 4): ten case-id strings;
   `native_execution: "unavailable"` belongs to candidate records; one macOS `sandbox-exec` conformance
   command total. G1 states it includes zero actual baseline turns; S4 stays blocked.
5. The corpus byte claim is corrected (finding 5): `corpus.json` carries
   `repositories[i].source_identity.archive_bytes`; sections 3 and 13 now agree, and record values stay
   separate from on-disk availability.
6. The missing review packet was created:
   `docs/CODEX-REVIEW-PACKET-PHASE-3B-CAMPAIGN-PROPOSAL-REVISION-3-2026-10-23.md`. Both older packets are
   marked historical in place, and their banners state that the revision-3 packet was created by this
   follow-up session (finding 6).

## 16. Correction log — G1 review-packet and S3-inventory audits (second follow-up session, 2026-10-23)

Findings of `docs/CODEX-AUDIT-PHASE-3B-G1-REVIEW-PACKET-2026-10-23.md` (this document):

1. Finding 1 (P1): the S2 Mac-side archive command no longer contains the `<HEAD>` placeholder that failed
   `zsh -n`. The saved block uses an explicit quoted `APPROVED_REVISION` variable, proves HEAD equals it
   before archiving, and appends the archive path, byte count and sha256 to
   `evidence/g1_delivery_ledger.txt`. Static checks: the saved block passes `zsh -n` and `bash -n` (exit 0);
   the removed placeholder block failed both. The block was not executed; no archive was built or transferred.
2. Finding 2 (P2): owner decision 4 (quota acceptance) moved out of the pre-host-action set in section 12 to
   the later admitted gate that first requests native turns, consistent with G1's zero actual baseline and
   zero native turns. U-9 stays open until that gate; no quota choice is requested before host action.
3. Finding 3 (P2): S3 readiness now links the saved local driver-candidate inventory
   (`docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md`) with its candidate paths, digests, argument
   contracts and provisional case map. S3 stays blocked; no guest command is bound.

Findings of `docs/CODEX-AUDIT-PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md` (closed in the paired inventory
document, recorded here for one-packet review): the false x86_64 guest claim is removed with the effective
guest architecture and admission state kept unknown; the six wrong source references are corrected against
live source; case 20 `qualification-refusal` is labelled a fresh local assessor check, not a guest probe
observation; every case mapping is labelled provisional until Codex accepts a driver and the guest passes
its actual gate.

## 17. Correction log — G1 S3-readiness re-audit closure (third follow-up session, 2026-10-23)

Findings of `docs/CODEX-AUDIT-PHASE-3B-G1-S3-READINESS-2026-10-23.md` (this document):

1. Finding 1 (P1): the S2 ledger block no longer puts `shasum | cut` inside `printf`. It now captures the
   byte count (`BYTES`) and the full digest output (`DIGEST_LINE`, then its first field `DIGEST`) in
   separate checked assignments, validates both formats (byte count digits only; digest exactly 64
   hexadecimal characters), and appends one complete three-field record only after both checks pass. The
   removed form could append `sha256=` with no digest after a failed `shasum` because the inner pipeline hid
   the failure from `set -eu`. Static checks: the saved block passes `zsh -n` and `bash -n` (exit 0).
   Offline stub tests (`$TMPDIR/g1_s3_stub_tests`, fake `git`/`wc`/`shasum`, no real archive): a failing
   byte-count command, a failing hash command, and a truncated-digest hash command each stop the block with
   nonzero exit before any append, leaving no complete ledger record; passing stubs write exactly one
   three-field record. The block was not executed with real inputs; no archive was built or transferred.
2. Finding 2 (P2): closed in the paired inventory document, recorded here for one-packet review: the
   case-map introduction now names the guest probe and the local assessor as separate execution roles, and
   states that case 20 (`qualification-refusal`) runs in the local readback assessor, not the guest probe.
3. Finding 3 (P2): the section 2 S2 row and the stage text no longer call the Mac archive command bound.
   They label it a checked template until the campaign ledger supplies an approved revision. The
   forty-zero `APPROVED_REVISION` stays, and the HEAD equality check still refuses to archive under this
   template. S2 stays blocked and the command was not run.

## Preservation statement

The revision-3 session and this follow-up session changed no tracked file. It ran no Linux-specific test, guest action, droplet action, toolchain
retrieval, evaluation row, sealed-row exposure, credential access, or paid service. It ran no broad local
test discovery; the named-module regression rule stays in force. The documents it touched are the proposal
(rewrite to revision 3) and annotations to its two review packets, all untracked planning candidates. Codex
reviews before any owner decision request. Nothing in this document authorizes execution.

The second follow-up session of 2026-10-23 (this section's author) changed exactly two untracked planning
documents: this proposal (section 16, the S2 archive block, the S3 readiness row, sections 9 and 12) and
the paired `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md`. It ran no guest, Linux, droplet, mount,
download, live-probe, evaluation-row, sealed-row, credential, or paid action. Its only executions were
static `zsh -n`/`bash -n` syntax checks on saved shell blocks (no command in any checked block ran), targeted
`sed`/`grep` source reads for reference verification, and two read-only line probes of
`scripts/phase3b_capped_archive.py`. It changed no tracked file, version, frozen input, or Hermes
configuration, and it built and transferred no archive. Codex reviews before any owner decision request.
