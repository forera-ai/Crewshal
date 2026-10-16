# Phase 2D bootstrap closure — source decision

Date: 2026-10-12.
Status: Accepted by the owner on 2026-10-12. Source implementation remains required.

The owner answered: "Approve source amendment".
This answer permits the source amendment below.
It does not approve compilation or the separate operational batch.

Phase 2D has not passed acceptance.
The accepted three lanes and charged helper build remain accepted.
This proposal requires a new source decision.
It does not request operational approval.

## Current source obstruction

The current installation needs the compiled AppArmor policy hash before it can freeze the root inventory.
The current storage audit also needs the exact parser and source-to-binary provenance.
No reviewed compatible policy binary has been supplied.

The accepted build receipt permits only helper identities and the inventory digests that contain them.
It cannot derive a new policy binary or its audit record.
Compiling that policy before the original full charge would violate the accepted charge order.

The current driver calls `_compile_helper()` before `create_owned_batch_timer()`.
The current timer needs the compiled helper.
`RuntimeMaxSec=600` limits the observer service.
It does not establish an independent deadline for the sibling setup role during compilation.
Compiler failure recovery through the observer does not close this gap.

The complete executable observer entry also remains unfinished.
These source gaps prevent a complete operational proposal.

## Proposed source amendment

Keep one original observer, journal, full charge, aggregate, and batch timer.
Keep all original limits, handles, unknown results, and refusal rules.
Keep the accepted three lanes and their original clocks.

Commit the original full charge before creating the lane groups or producing build outputs.
Retain the exact original role FDs as each group is created.

Create the sole original batch timer before either build process starts.
Use fixed isolated Python source with an empty inherited environment.
Pin its source, interpreter, loader, libraries, process, and timer FDs before release.
Require readonly runtime images and independent process readback.
Place it in the original observer role under the original limits.
Give it only the predeclared original operational group FDs.
Use `CLOCK_MONOTONIC` and absolute kernel timer deadlines from the original batch origin.
Stop new work at origin plus 570 seconds.
Keep the original 600-second end and fixed 30-second final reserve.
Do not create the later C batch timer.
Do not replace the original Python timer, reset its clocks, or add another timer process.
Keep the C native and validator watchdogs unchanged.

Extend the immutable build recipe to include the AppArmor policy and its audit template.
Freeze the exact parser, loader, libraries, ABI data, include files, arguments, and environment.
Permit one C compilation and one policy compilation.
Run them in sequence within one original 30-second build interval.
Do not restart that interval for the policy process.
Use the first original setup role and its unchanged controls.

Keep the original compiler storage limits:

| Object | Unchanged bound |
|---|---:|
| Backing and loop range | `16777216` bytes |
| Actual ext4 inodes | At most `128` |
| Hard file size | `1048576` bytes |
| Conservative logical term | `167772160` bytes |
| Conservative allocated term | `50331648` bytes |
| Each captured stream | `65536` bytes |

Permit only the helper, policy binary, and derived audit record as build outputs.
Pin each output FD before its first write.
Read the actual output bytes independently after positive reaping and setup emptiness.
Remount the original compiler volume readonly after both builds.
Retain every partial output, process handle, and original charge after failure.
Do not refund, retry, release, or reuse them.

Extend the single registered derivation receipt.
Bind both processes and all three output inodes to the original recipe and charge.
Derive only the helper hash, policy hash, and audit fields that contain the policy hash.
Derive the corresponding root, parent, storage audit, bootstrap, and final configuration digests.
Verify every other field against the initial frozen recipe.
Keep the initial observer and charge identities unchanged.
Require the same registered receipt for every final configuration check.
Reject missing, changed, copied, repeated, or unregistered receipts.

The build must not load or replace AppArmor policy.
The separately approved installation must load only the frozen absent profile names.
Actual installed readback remains mandatory before payload admission.

## Source and operational gates

Prove charge-before-effect order and timer-before-build order with source tests.
Prove that failure retains original handles and charges.
Reject changed clocks, nonderived fields, extra outputs, replacement owners, and repeated builds.
Verify the complete source and a fresh installed wheel.

Then finish and freeze the complete executable operational batch.
That batch must include every exact input, command, authority, deadline, and stop condition.
Request its separate approval only after this preparation is complete.
Do not repeat the three consumed compiler attempts.

Both original twenty-case Linux runs remain mandatory.
Cover every enabled native file tool on the exact installed profile.
Complete actual frozen-candidate and credential-free-validator live acceptance.
Publish only after full Phase 2D acceptance.
Do not begin Phase 2E.

## Decision

Accept this source amendment to close the policy build and timer order gaps.
Acceptance permits source work only.
Compilation, Linux mutation, authentication, and subscription use still require separate operational approval.
