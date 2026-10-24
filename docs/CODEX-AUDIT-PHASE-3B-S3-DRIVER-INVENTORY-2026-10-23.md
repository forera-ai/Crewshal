# Codex audit — Phase 3B S3 driver inventory

Date: 2026-10-23. Outcome: changes required before Codex can accept the S3 candidate inventory.

## Scope and verified state

Codex reviewed `prepare-local-s3-containment-driver-inventory-local-3e.json` and the saved inventory.
Hermes created one untracked inventory document. No tracked code changed.
This review covers source claims and campaign commands. It does not qualify a Linux host.
HEAD is `6279a2eb32714530beffab7e6425c3d41fbcfbb5` on `codex/phase1-architecture`.

## Findings

1. **P1 — The inventory states the wrong planned guest architecture.**
   `docs/PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md:92-94` calls the planned VMware guest `x86_64`.
   The G1 proposal requires Linux `aarch64` at S1 and S3.
   Its A2 bundle name also states Ubuntu `arm64`.
   `scripts/probe_native_full_v18.py:1303-1304` requires root and `aarch64`.
   Correct the claim and keep effective guest architecture unverified until admission.
   Do not invent an x86_64 profile decision for this campaign.

2. **P2 — Six source references are wrong.**
   The protocol constant is at `scripts/readback_native_full_v3.py:20`.
   `refusal()` starts at line 62, allowed-grant uses line 179, and configuration-binding uses line 359.
   Profile `CASES` is at `scripts/probe_linux_profile.py:22`.
   Lifecycle `CASES` is at `scripts/probe_linux_lifecycle.py:54`.
   Correct the inventory references before using them as review evidence.

3. **P2 — Case 20 needs a distinct execution label.**
   `readback_native_full_v3.refusal()` creates fresh local assessor fixtures.
   `check_run()` marks qualification-refusal from that local check at lines 132 and 423.
   This is an assessor refusal check, not a guest containment observation from the v18 probe.
   Keep it in the 20-case map, but state its execution location and evidence type.

4. **P1 — The planned milestone remains incomplete.**
   Hermes validated an archive command in scratch but did not update the proposal.
   The saved proposal still contains invalid `git archive ... <HEAD>` syntax at line 200.
   It still lacks an executable size-and-digest ledger write at line 201.
   S3 still lacks the inventory link and candidate table.
   G1 correctly defers S4 actual turns, but owner decision 4 still requests a quota choice before host action.
   G1 plans zero native turns, so that quota choice belongs at the later admitted gate.
   No new Codex review packet records the proposed corrections.
   A scratch command cannot close defects in the saved campaign document.

## Verified progress and limits

The six listed driver digests match the local files. The candidate map covers all 20 case names.
Hermes ran seven named Phase 2C acceptance modules: 36 tests passed with exit code 0.
Those tests use offline fixtures. They provide no G1 Linux result.
The substrate scripts bind `/opt/homebrew/bin/docker`; no Linux guest variant was verified.
No guest, droplet, transfer, live probe, evaluation row, or paid service ran.

## Next boundary

Correct the inventory and saved G1 proposal in one local documentation milestone.
Validate the saved shell block without executing the archive or contacting a guest.
Prepare one review packet with exact changed lines, checks, outcomes, and open gates.
Keep S3 and S4 blocked until their actual admission and qualification checks pass.
