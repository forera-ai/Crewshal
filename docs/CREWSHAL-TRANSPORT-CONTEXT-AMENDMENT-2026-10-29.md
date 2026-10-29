# Proposed scope amendment: trusted auxiliary execution context

Date: 2026-10-29. Status: prepared for an owner decision; not implementation authority.
This amendment follows the [selected transport feasibility stop](CREWSHAL-TRANSPORT-FEASIBILITY-2026-10-29.md).

## Requested change

Extend the approved isolated transport task to three additional Hermes source files and one new private submission control.
Keep the approved direct Sol 6.1 exception and unused budget of one implementation attempt and two corrections.
Do not reset the previous repair budget or I1, I2, and I3.
The amendment supplies no activation, restart, model request, or live diagnostic authority.

## Exact candidate ownership

| Path | Permitted change |
| --- | --- |
| `gateway/session_controls.py` | Add a versioned optional `auxiliary_control_v1` input to the local submit seam. Require verified operator authority and reject unsupported fields or callers. |
| `gateway/session_authority.py` | Validate and retain that input in the admitted payload. Bind it to server identity, policy limits, and existing admission fingerprint and replay rules. |
| `gateway/session_ingress.py` | Publish the validated control and claimed server identity for the exact executing admission. Reset the context on every exit. |
| `agent/auxiliary_client.py` | Read the trusted context, mint a distinct physical auxiliary attempt, and prepare the selected transport call. Retain the previously approved relay and progress scope. |
| `agent/auxiliary_stream_watchdog.py` | Hold the immutable binding and deadline contract and the proposed request-owned asynchronous transport. Preserve refusal and closure semantics. |

Prepare all runtime edits in a new private candidate tree. Do not modify installed Hermes source.
Prepare the new private submission control from reviewed requirements. Preserve every historical runner unchanged.
Its only admitted execution uses offline synthetic RPC and transport fixtures.
Do not run it against a live gateway or model service.

Keep `gateway/run_turn_runner.py`, `gateway/session_runtime_workers.py`, SDK files, database schema, dependencies, and profile unchanged.
Current storage fingerprints the full JSON payload. Verify compatibility and replay behavior without changing that storage implementation.
Verify existing context propagation across executor and compression threads.
If that propagation needs another source edit, stop and identify the exact additional path.
Managed-worker and other runtime paths remain unsupported for this control unless separately admitted.

## Binding and deadline contract

The new private control must capture its monotonic start before submission effects.
The optional record must contain a version, expected instance and profile epoch, original start, fixed deadline, cleanup allowance, and client ceiling.
Keep multiplexer identity and epoch in a separate observation binding. Never substitute them for profile authority values.
Bind monotonic values to the same local clock domain and current runtime instance. Reject an unverified clock domain.
Reject nonfinite values, future starts, expired deadlines, inconsistent limits, and unsupported versions before inference.
Clamp permitted exposure to the existing approved policy. Caller data cannot create execution or spending authority.
No progress event may replace the original start or extend the fixed deadline.

Use current server values for the seven-field operation identity:

- Obtain the instance and profile epoch from the admitted authority and verify their exact runtime meaning.
- Obtain the canonical session, admission, and generation from the claimed row and reference.
- Use the admitted row's `request_id` for the request field.
- Generate a fresh auxiliary-attempt identity for each physical provider attempt.

The client cannot select an admission, generation, or auxiliary-attempt identity through prompt text.
Verify the authority instance against the routed runtime observation before relying on that mapping.
On restart, instance or epoch mismatch must refuse the stored control. Do not recalculate its deadline or replay inference.
Absent control must retain the existing candidate's refusal for protected inference.
Unprotected ordinary calls must retain their existing behavior.

## Acceptance and stopping boundary

Prove that an unauthorized caller cannot install or spoof the control.
Prove exact replay consistency and rejection of changed control bytes for an existing request.
Test wrong instance, each wrong epoch, wrong admission, stale generation, unsupported version, and invalid time values.
Test queue delay, cancellation before dispatch, context propagation, scope reset, concurrent admissions, and restart refusal.
Demonstrate that prompt-reading progress cannot extend the admitted deadline.
Use actual selected SDK code with controlled transport fixtures for response creation, continuing generation, and blocked reads.
Preserve shared clients, concurrent requests, reuse fences, owner closure, and commit fencing.
Rerun the complete 16-case diagnosis matrix against exact loaded candidate files.
Apply the original proposal's external-effect guard, immutable candidate review, attempt limits, and Ruff limitations.

Stop if the installed libraries cannot meet the transport contract within these paths.
Do not substitute a provider proxy, shared-client close, server kill, new product adapter, or another runtime route.
Do not add live observation translation to this source task.
Record exact checks and remaining limitations. Publish only a newly accepted coherent checkpoint, then stop.

The next separate milestone may prepare executable live observation, application, gateway action, rollback, prompt, and limits.
That later preparation and any operational admission retain their recorded gates.
