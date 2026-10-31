# Proposed single offline association correction

Date: 2026-11-01. Status: unapproved.
Basis: the [failed source checkpoint](CREWSHAL-ASSOCIATION-BRIDGE-STOP-2026-11-01.md).
This proposal grants no authority by itself.

## Requested authority

Permit direct Sol 6.1 preparation of one targeted offline correction.
Permit zero automatic follow-up corrections.
Keep the original implementation attempt and both consumed corrections recorded.
Keep every older budget consumed. Keep the separate translator budget unused.
Copy the rejected candidate into one fresh private directory under the preserved S1b root.
Preserve every rejected candidate, failed fixture, original acceptance input, and historical manifest.

The correction base has candidate manifest SHA-256 `a255a737e81caa02637bdb05074c720f53144677f45add7cc4241bbc9951bc08`.
Verify that manifest and the three patch hashes in the stop record before any candidate edit.
Require current Sol metadata, required skills, actual tools, current source, and preservation checks.

## Exact ownership

Change only these three candidate paths:

1. Studio `routes/inference.py`: separate request-owned correlation from the shared durable cancellation event.
   Preserve the shared event's cancellation, wait, and deadline behavior.
   Prevent callback retention or exchange across sequential and simultaneous requests.
2. Studio `core/inference/api_monitor.py`: retain observation chronology and reject stale, overlapping, or contradictory intervals.
   Preserve separate process, binary, slot, completion, task, active-observation, and release-observation identities.
   A later active observation must prevent an earlier release from satisfying reconciliation.
3. Private `tests/test_association_bridge.py`: correct the class-specific AST selection without weakening assertions.
   Add regression cases for both confirmed runtime findings and exercise the complete protected stream paths.

Keep all Hermes, native, generated, original test, submission, supervisor, and guard bytes unchanged.
Add only private evidence, verification, review, and focused-build fixture files beside the copied candidate.
Stop for an amendment if another runtime path, dependency, authentication change, or unavailable build capability becomes necessary.

## Acceptance and stopping rule

Run all unchanged original cases and all 24 current association cases against the corrected candidate.
Run the new regression cases against fresh deterministic fixtures.
Demonstrate the confirmed callback and chronology defects before claiming that the correction fixes them.
Exercise sequential and concurrent protected requests that share a durable cancellation event.
Exercise a subsequent unprotected request without mutating its cancellation authority.
Exercise the actual standard generation and uncertain-submission refusal paths.
Exercise actual passthrough stream consumption and native identity capture, including uncertain-submission refusal.
Retain every original association refusal, privacy, clock, capacity, partial-write, cancellation, and lifetime acceptance case.
Run native serializer behavior against unchanged native candidate bytes, or verify its unchanged, exact accepted fixture inputs.
Require syntax, private Ruff, baseline-aware runtime Ruff, deterministic generation, patch applicability, hashes, and preservation checks.
Review the complete cumulative candidate independently.
Retain failed commands and distinguish passing cases from a failed complete command.
If a required case fails or remains unavailable, preserve the result and stop without another correction.

## Closed operational gates

Use installed tools and deterministic fixtures only.
Permit zero model requests, zero network calls, zero credential access, and zero service actions during preparation.
Do not download tools, source, dependencies, or models.
Do not apply patches, rebuild installed binaries, change profiles, restart services, or dispatch workers.
Keep the selected model, provider, quantization, context, slot count, profile, and runtime configuration unchanged.
No source acceptance qualifies the loaded native binary or the Hermes worker route.
Require reproducible binary provenance and an exact executable operational plan before any later operational decision.
Keep the original 600-second submission limit, one 15-second cleanup allowance, and independent 630-second ceiling for that later plan.
Require gateway termination, foreground exit, auxiliary owner closure, and associated server release separately.
Never replay an uncertain submission.
Keep product writes, Linux work, evaluation, merge, deployment, and releases closed.

Proposed owner response: `Approve one offline association correction`.
