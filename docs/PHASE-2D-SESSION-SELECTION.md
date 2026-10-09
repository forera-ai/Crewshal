# Phase 2D preparation selection per project and session

Date: 2026-10-08. Status: preparation implemented and verified offline; **Phase 2D remains incomplete**. Package remains 0.9.0 and changes are uncommitted. The owner clarified: “just do the preparation with ability to select on each project/session”. This preserves preparation-only scope and defers live choices to each project/session.

## Explicit choices

The existing [preparation utility](../scripts/prepare_phase_2d_batch.py) accepts `--selection FILE`. Each file identifies one project/session and chooses a model for the pinned Codex template. Optional provider, HTTPS destination, billing mode and credential treatment are requested choices, not availability, approved egress, credentials or enforcement. No ambient settings, account, credential store or previous bundle supplies defaults to an explicit selection.

Example coordinator-owned selection file, saved outside the checkout:

```json
{
  "schema_version": 1,
  "project": "Crewshal",
  "session": "2026-10-08-preparation",
  "model": "gpt-6.1-sol",
  "provider": null,
  "destination": null,
  "billing_mode": "unresolved",
  "credential_treatment": "unresolved"
}
```

Use a new file/bundle for another project or session. Change `model` there rather than changing a global setting. Other models have no documentation/availability claim. Runtime remains pinned Codex 0.160.1; selection does not add another adapter. Billing labels are `unresolved`, `api_metered` and `subscription_quota`; credential labels are `unresolved` and `external_scoped_channel`. No secret, credential path or authentication field is accepted. Destinations reject URL user information, query strings, fragments and non-HTTPS schemes. Do not put secrets in labels or URL paths; this is not a general secret detector.

Omitting `--selection` retains the historical Sol6.1 preparation default without a project/session claim. Readback requires an explicit bundle's exact selection and refuses reuse in another context. A legacy bundle cannot be silently adopted into an explicit context. Neither path grants authority.

## Reproduce preparation and readback

Create the external `selection.json` above and `references.json` from [the earlier guide](PHASE-2D-BATCH-PREPARATION.md). From the recorded development environment:

```sh
rtk proxy .venv/bin/python -m scripts.prepare_phase_2d_batch \
  --reference-root "$PWD" \
  --references "$crewshal_prepare_dir/references.json" \
  --selection "$crewshal_prepare_dir/selection.json" \
  --output "$crewshal_prepare_dir/bundle"
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_selection
```

`prepare_runtime_batch(..., selection=selection)` returns a `BatchPreparation`. Retain that expectation in coordinator-owned state **outside the bundle**. `audit_runtime_batch(reference_root, output, expected, selection=selection)` compares current data with the independently retained record. Reading the bundle's `batch.json` as its own expectation does not establish independent integrity.

Readback validates the closed JSON declaration, every artifact/reference hash, exact inventory, missing/unexpected entries, symlinks/hardlinks, candidate modes/content and initial manifest binding. Different project/session/model/route/billing/credential choices refuse. Result: `prepared_data_matches`; execution, spend and qualification remain false. This is not a task verdict, live qualification or authenticity check. Stable trusted coordinator directories are assumed; hostile directory replacement races and same-user adversaries remain outside this offline claim.

[The bound example](qualification/phase-2d-session-selection-v1-20261008.json) preserves eleven artifact bodies, the explicit unresolved selection and eight unchanged historical references. Original v1 preparation/evidence remains intact. The exact check template is `[/bin/python3, -I, -B, /input/check_fixture.py, /candidate/owned]`; executable/library identity remains unbound. The audit executes neither this script nor the native tail. Original five-second/128 MiB ceilings and all other limits remain unchanged.

## Verification and continuation

Seven fresh tests prove context isolation, CLI selection, legacy compatibility, altered history/artifact/declaration refusal, unknown entry/link/mode refusal and malformed selection refusal without importing declared code. With existing tests: **40 Phase 2D methods / 181 complete offline tests**. [Fresh verification](qualification/phase-2d-session-selection-verification-v1-20261008.json) records editable/installed-wheel results, static checks, source hashes and byte continuity. Initial import failed before the API existed; typing initially rejected a widened model-source constant, corrected to its exact Literal type. These are local failures, not live failures.

Continue **2D** under preparation-only scope. Resolve live choices when the relevant project/session needs them; then bind production dispatch, qualify the exact profile and separately record execution/spend authorization. Do not ask again for a global route or this session's resolved scope. Production/live acceptance remains unavailable. No runtime startup, provider/model/Jev call, VMware/SSH operation, credential-store access, version bump, commit/push, 2E or evaluation occurred. Read [handoff](HANDOFF.md), [execution gate](PHASE-2D-EXECUTION-GATE.md) and [continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md).
