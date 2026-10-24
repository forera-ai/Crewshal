# Phase 3B G1 decision-readiness packet (read-only, 2026-10-24)

Hermes prepared this packet under the Crewshal profile. It answers one question: is the accepted G1
consolidated Linux campaign proposal ready for an owner decision? This packet makes no proposal, no source
change, and no host action. It keeps every execution and spending gate closed. It ran no guest action, no
Linux test, and no evaluation row.

Hermes checked the cited source lines directly at HEAD. It did not query the codebase graph or check index
coverage. Codex repeated the material source checks after its graph service returned `Transport closed`.

## Served runtime and session state (verified first)

- Hermes model: `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL`.
- Profile context (`config.yaml`): 98,304 tokens.
- Served model: `unsloth/Ornith-1.5-122B-GGUF:UD-Q4_K_XL` (`chat_completions` mode, base_url `127.0.0.1:8888/v1`).
- Actual server context (catalog `context_length`): 98,304.
- Prompt expectation: 98,304. Match. No mismatch observed. Proceeded.
- Branch: `codex/phase1-architecture` @ `a618079`, in sync with `origin/codex/phase1-architecture`.
- Working tree: clean. Version: 0.27.4 (`pyproject.toml`, `crewshal.__version__`).

## Verdict

The proposal is ready for an owner decision. It awaits the owner's exact decision on four pre-host-action
choices. It presents exact, bounded owner choices, finite limits with no unknown-ceiling network allowance,
documented unknown guest facts, and correctly blocked mutating stages. Material source references verify at
HEAD. One non-blocking provenance note requires Codex awareness (named below).

## Decisions required before host action (owner, four)

These match decisions 1, 2, 3, and 5 in proposal section 12. They are owner gates, not development-run
or protocol decisions. The earlier owner decision packet names the G1 approval gate without this numbering.

1. Select G1 host. Options: A1 consolidated VMware guest, A2 offload VMware guest, or droplet B. Both guest
   architectures remain unobserved. The chosen guest must pass the S1 Linux aarch64 admission check.
2. Approve or decline CPU/RAM/disk floors. The proposed values in section 7 are not effective limits.
   No approved disk floor exists. An unapproved choice keeps mutating stages blocked.
3. Fix a finite byte ceiling for guest wheel closure and approve the exact archive-image attach action.
   Stage S0b cannot run without the ceiling. Stage S1b cannot run without the exact attach action and a
   bound disk identifier or device node.
4. Select source delivery transport (decision 5). This binds stage S2. The proposal groups it with the other
   three as pre-host-action; strictly it is required before S2, while host selection (1), floors (2), and the
   wheel-closure ceiling plus attach (3) are required before the earliest host actions (S0b and S1).

## Later decisions (not owner pre-host gates)

These stay open and do not block the owner decision. They are development-run, Codex, or protocol gates.

- Decision 4 (quota acceptance): deferred by the owner to a later gate (proposal section 6).
- S3 driver acceptance: Codex must accept the candidate driver set before any containment case binds
  (S3 driver inventory, "Cross-cutting missing bindings" 1).
- S4 conformance: the owner must adopt the B1 manual script with effective native commands bound in the
  campaign manifest. The owner must also define the Linux run for ten mandatory baseline cases. Both
  choices remain open. They do not authorize actual baseline turns in G1.
- S1 admission observation: each guest's effective architecture and arch-boot state are unconfirmed before
  S3. The v18 probe refuses to start unless the host reports `aarch64` as root
  (`scripts/probe_native_full_v18.py:1303-1304`, verified at HEAD). No guest architecture is confirmed yet.
- Phase 3B acceptance: development corpus runs and a frozen protocol amendment remain required
  (`docs/DEVELOPMENT-PLAN.md` milestone map, row 3B, line 566). These are separate from the host campaign.
- U-1 through U-13 remain documented unknowns (proposal section 11).

## Factual note for Codex (non-blocking)

Location: `docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md`, section 17 "Preservation
statement", lines 546, 549, 552, and 561.

Claim: the proposal and its review packets are "untracked planning candidates" / "untracked planning
documents", and "this session changed no tracked file".

Live state: those documents are now TRACKED and committed at HEAD `a618079`
("docs: accept G1 S3 planning repair and Ornith audit"). `git ls-files --error-unmatch` confirms each is
tracked; the working tree is clean.

Assessment: the statements were true in the 2026-10-23 sessions that wrote revision 3, and the documents
were committed afterward. This is stale provenance, not a gate defect. It does not change any owner choice,
finite limit, unknown guest fact, or stage gate. Codex should note it before relying on the phrase "changed
no tracked file" in the current tree.

## Verified evidence (read at HEAD a618079)

- Mandatory case set: 20 cases at `src/crewshal/qualification.py:10-31`. Matches the S3 inventory 20-case map.
- v18 startup gate: `scripts/probe_native_full_v18.py:1303-1304` refuses unless `geteuid() == 0` and
  `uname().machine == "aarch64"`.
- Readback assessor: `PROTOCOL` constant at `scripts/readback_native_full_v3.py:20`; `refusal()` at line 62;
  `allowed-grant` check at line 179; `configuration-binding` check at line 359.
- Substrate drivers: profile `CASES` at `scripts/probe_linux_profile.py:22`; network `executed_subset` marker
  at `scripts/probe_linux_network.py:60`; lifecycle `CASES` at `scripts/probe_linux_lifecycle.py:54`; macOS
  Docker client path at `scripts/probe_linux_profile.py:88`.
- Finite-limit check: proposal section 5 stage S0b requires a stated ceiling before any wheel request;
  corpus archives have known retained byte records (proposal sections 3 and 8). Current disk availability
  remains unknown until S1b. Proposal section 11 U-13 names the missing wheel-closure ceiling. No decision opens
  an unknown-ceiling network allowance.
- Owner-choice check: proposal section 12 lists decisions 1, 2, 3, and 5. The owner decision packet records
  the general G1 approval gate. It does not number these choices.

## Deferred and closed (preserved)

- No Linux test, guest boot, droplet use, credential access, sealed-task access, or spend occurred.
- The consumed guest staging attempt remains closed (handoff current state).
- VMware guests, the ISO, archives, receipts, charges, and unknown outcomes are preserved.
- Phase 3B calibration and G1 qualification stay closed until their actual gates pass under ADR 0009.

## Checks run and limitations

- Run: model/context match; `git` branch, HEAD, version, and clean-tree status; direct source reads at the
  cited lines; `git ls-files --error-unmatch` tracking check on the planning documents.
- Not run: any guest, Linux, droplet, or evaluation command (deferred by ADR 0009 and this session's gates).
- Limitations: Hermes did not read `AGENTS.md` explicitly. It did not use `rtk proxy` for each terminal
  command. Its git history range query was blocked by deny rule `*git * commit*`. Codex verified the
  planning documents' commit separately. Direct source reads support the cited lines; no graph coverage
  result supports a Tier 2 graph claim.

## Next-session prompt (one)

"Read `/Volumes/X10Pro/Crewshal/docs/PHASE-3B-G1-DECISION-READINESS-2026-10-24.md` and the current G1 proposal
section 12. If the owner has given exact answers for decisions 1, 2, 3, and 5, record them in a new dated
document. Prepare a read-only S0b command batch only after the owner approves a finite wheel-closure ceiling.
If the owner keeps resource floors unapproved, keep every mutating stage blocked. If a decision remains open,
record the smallest missing choice and stop. Do not boot a guest, use a droplet, run Linux tests, or spend money."
