# Draft G1 owner-response record — 2026-10-24

Status: DRAFT for Codex review. This document records the owner choices in one
decision-intake export. It grants no host, guest, Linux, evaluation, or spending
authority. No campaign stage ran or was submitted to run while this draft was
prepared. The draft preparation changed no existing tracked file, proposal,
version, or frozen input.

## Source of the owner choices

This draft reads one export as evidence of owner choices only.

- File: `/Users/hamedprooshani/Downloads/prepare-g1-owner-decision-intake-local-57.json`
- `exported_at`: `2026-10-24T12:24:02.905Z`
- `session_id`: `local-57db0bbd53bb502f7bd8c7ad621ca9bfcebea28076485fe049fb8faceb18c097`
- `title`: `Prepare G1 owner decision intake`
- `outcome`: `submitted`
- The four decisions appear in `messages[31].content` as one JSON object with a
  `responses` array and an `outcome` value.

The export is evidence of choices. It is not authority to execute a stage.

## The four decisions, verbatim

Each `user_response` value below is copied exactly from the export.

1. Decision 1 (section 12, host): `A1 — consolidated VMware guest`
2. Decision 2 (section 12, floors in section 7): `Approve the proposed section 7 floors as effective limits`
3. Decision 3 (section 12, ceiling and attach): `20000000000`
4. Decision 5 (section 12, transport for S2): `Private path`

The export offered no `choices_offered` list for Decision 3. It offered free
text. The owner entered one integer, `20000000000`, and no other text.

## Distinction 1 — A1 selected; guest architecture and capacity stay unobserved

Decision 1 selected `A1 — consolidated VMware guest`. This records a host
selection. It does not observe the guest.

- The guest power state, Ubuntu release, effective CPU, RAM, and disk stay
  unobserved. The proposal lists these as U-2.
- The effective guest architecture stays unobserved. A prior false x86_64 guest
  claim was withdrawn in the proposal correction log (section 16). The proposal
  keeps guest architecture and admission state unknown.
- The recorded 8 GiB capacity stop stands until Decision 2 and one observation
  replace it (proposal U-2, section 11).

A host selection is not a guest observation. Guest work stays closed under ADR
0009 during local development.

## Distinction 2 — Section 7 floors: selected in the export; still labeled proposed in the proposal

Decision 2 selected `Approve the proposed section 7 floors as effective limits`.
The export records the owner's choice on the CPU, RAM, and disk floors named
in proposal Decision 2. It does not identify a separate choice on every time
ceiling or the concurrent-unit limit in section 7.

The current proposal still labels every section 7 row `Proposed, not approved`
(proposal lines 331-334). This draft does not change the proposal. Until a
reviewed proposal edit records the approval, the two records differ:

- Export: the owner selected approval of the named CPU, RAM, and disk floors.
- Proposal (lines 331-334): the floors remain `Proposed, not approved`.

The section 7 rule states that no table value gates a stage, and the effective
capacity stop is the floor the owner records in Decision 2 (proposal lines
336-339). This export supplies evidence of the choice. The proposal text has
not been changed to show it. A later reviewed proposal amendment must reconcile
the label and exact floor values before any stage relies on them.

The section 7 table is copied for context. Its time and concurrency values do
not become approved through this draft:

| Unit | vCPU | RAM | Disk | Wall ceiling | Proposal label |
| --- | ---: | ---: | ---: | ---: | --- |
| Preparation tree (per host) | 4 | 12 GiB | 24 GiB working | 8 h active / 24 h wall | Proposed, not approved |
| One task unit, native runtime | native ceiling | 768 MiB attempt ceiling | shared working tree | 600 s deadline | Proposed, not approved |
| One validator run | 4 | 8 GiB | 8 GiB | 900 s | Proposed, not approved |
| Concurrent execution units | 1 | — | — | batch 14 days | Proposed, not approved |

## Distinction 3 — A byte ceiling was supplied; attach approval was not

Decision 3 asked for two things: one finite byte ceiling for the guest wheel
closure, and approval of the exact archive-image attach action (proposal section
12, Decision 3, lines 409).

The export supplied only the byte ceiling: `20000000000` bytes (20,000,000,000
bytes). It supplied no attach approval and no device text.

- The supplied value names a finite byte ceiling for the guest wheel closure
  (proposal U-13, section 11). It does not approve the archive-image attach.
- The attach action still lacks an approved exact identity. The proposal records
  no disk identifier or device node (U-12, section 11).

So Decision 3 is half supplied. The ceiling exists. The attach approval does not.

## S0b — no command enforces the byte ceiling

Stage S0b would obtain the guest wheel closure. The proposal describes a local
fetch and Mac-to-guest transfer (section 8, line 346). It gives no download
command and keeps S0b blocked (section 5, lines 119-128).

This draft states: S0b has no command that enforces the byte ceiling. The export
supplies a ceiling value, but the proposal still gives no S0b command. A ceiling
value is not a command. No S0b stage can run on this evidence.

## Distinction 4 — Quota decision deferred to its later gate

The export asked four questions: Decisions 1, 2, 3, and 5. It did not ask the
quota decision. The proposal moved the quota decision out of the pre-host-action
set to the later admitted gate that first requests native turns (proposal section
12, deferred note, lines 412-415; U-9).

This draft records: the quota decision stays deferred. G1 plans zero native
runtime turns and zero actual baseline runs. No quota choice is supplied here, and
none is requested before host action.

## Distinction 5 — Private-path transport selected; no S2 path or command is bound

Decision 5 selected `Private path` for the S2 source delivery transport (proposal
section 12, Decision 5, line 410). This records a transport choice.

It does not bind an S2 path or command. The proposal keeps the guest-side delivery
commands as an unbound draft contract (proposal section 15, finding 3). The Mac
archive command is a checked template, not a bound command, until the campaign
ledger supplies an approved revision (proposal sections 16 and 17). This draft
supplies no S2 path and no S2 command. S2 stays blocked.

## S1b — no exact attach approval or observed device

Stage S1b verifies the four retained corpus archive blobs from a local archive
image (proposal section 5, lines 153-172). The proposal states that no disk
identifier or device node is recorded anywhere, that `diskutil mount` requires
one, and that S1b is blocked with no mount command given (proposal section 15,
finding 1; U-12).

This draft states: S1b has no exact attach approval and no observed device.
Decision 3 supplied only a wheel-closure byte ceiling. It supplied no attach
approval. The proposal reports that the volume was unmounted in its own session
(U-10). This draft did not inspect current mount state. Mounting stays an
owner-only exact action. S1b stays blocked.

## The four corpus archive identities

These four identities come from proposal lines 180-184. Their bytes and SHA-256
values are copied exactly. These are corpus archive blobs, not the guest wheel
closure. The supplied byte ceiling in Decision 3 applies to the guest wheel
closure, not to these blobs.

| # | Corpus ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| 1 | `python-1` | `343,014` | `edfa6cf117bbbe46f6690266a40389b08b12cbf87fad8664d349ebd6eea811a1` |
| 2 | `typescript-2` | `1,580,238` | `4754f74b4defcbaa9b8748406fcd3e974b756abf7824e8a1a4304ec9665e6ced` |
| 3 | `swift-1` | `655,699` | `45c952a441611e17d8c30de26c4a6b40eec483c07900d9faad2501539aa5c900` |
| 4 | `dotnet-1` | `198,331` | `71a77a7c2eb4d1ffa1572c97c9050c673e16f24cdac19d5039ad79cad06a26dd` |

Byte total check: 343,014 + 1,580,238 + 655,699 + 198,331 = `2,777,282`. This
matches the proposal total (section 8, line 347; section 13, line 442).

This draft invents no image-level digest and gives no executable attach command.
On-disk availability of these blobs stays closed until S1b observes it.

## What stays closed

These actions stay closed after the four decisions in this export:

- Guest work. A1 is selected, but ADR 0009 keeps guest boot, inspection, and
  installation closed during local development. No guest command runs.
- Image attachment. S1b has no attach approval and no observed device. No mount
  command is bound.
- Downloads. S0b has no command and no network retrieval is requested. No
  unknown-ceiling network allowance opens. The zero transfer allowance is kept.
- Evaluation. No evaluation row runs. No corpus run, sealed-row exposure, Phase
  3C, deployment, or package release is authorized.
- Spending. The approved zero metered billing and zero paid-host limits stay
  unchanged (ADR 0009, lines 39-40). No droplet variant was selected.

## Authority boundary

This draft records owner choices from one export. Its preparation changed no
proposal text, existing tracked file, version, or frozen input. It ran no stage.
It grants no host, guest, Linux, evaluation, or spending authority. Codex reviews
this draft before any owner decision request and before any proposal amendment.
