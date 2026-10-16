# Phase 2D charged helper build — source decision

Date: 2026-10-12.
Status: Accepted by the owner on 2026-10-12. Source implementation remains required.

The owner answered: "Approve the charged build source amendment".
This answer permits the source amendment below.
It does not approve compilation or the separate operational batch.

This proposal changes the helper identity binding order.
It preserves the accepted full charge, original observer, three lanes, and every original limit.
It does not reopen ADRs 0004, 0005, or 0006.
It does not authorize compilation or the operational batch.

## Exact source obstruction

The installation constructors require the compiled helper hash before they bind the observer and configuration.
The current optional compiler path writes its output before `reserve_storage_installation()` commits the full charge.
A compiler failure retains the driver and its FDs, but no installation charge exists.
This path cannot establish the required charge order.

The owner requires an original full charge before installation effects.
Treat the new helper build as an installation effect.
Do not use a successful build to excuse an earlier uncharged write.
Do not repeat any consumed syntax attempt or historical client.

## Proposed amendment

Permit one immutable helper build recipe to supply the initial identity for the original full charge.
The recipe must contain these exact inputs:

- The current helper source bytes and hash.
- The compiler, linker, static archives, headers, and required loader identities.
- The complete fixed argument array, empty inherited environment, and sole `TMPDIR` value.
- The existing private compiler volume, backing, loop, mount, inode geometry, and ownership identities.
- The original observer, aggregate, role handles, batch origin, and journal identity.
- Every final dispatch field except the identities derived from the compiled helper bytes.

Commit both original `8589934592`-byte charges before the first compiler output write.
Use the same original observer process and synchronous journal throughout the build and installation.
Retain the original live charge object before any compiler effect.
No parsed recipe, copied journal record, or caller flag can replace that live object.

Compile once in the first original setup role.
Preserve its original memory, task, CPU, swap, startup, job, and batch limits.
Use the existing compiler volume and its unchanged limits:

| Object | Bound |
|---|---:|
| Backing and loop range | `16777216` bytes each |
| Actual ext4 inodes | At most `128` |
| Compiler hard file limit | `1048576` bytes |
| Complete conservative logical compiler term | `167772160` bytes |
| Complete conservative allocated compiler term | `50331648` bytes |
| Compiler job | At most `30` seconds within the original clocks |
| Each captured stream | At most `65536` bytes |

Require the actual compiler exit, positive reaping, setup emptiness, and independently read output bytes.
Retain the compiler volume as readonly after the build.
Retain all original partial handles and the full charge after failure.
Do not refund, retry, release, or reuse them.

Permit exactly one retained derivation receipt after a successful build.
Bind it to the original live charge, observer, recipe, compiler process, and output inode.
Derive only the helper binary hash and the inventory digests that contain that hash.
Derive the corresponding bootstrap policy digest and final configuration digest from those exact bytes.
Verify every other configuration field against the original recipe.
Reject changed, missing, copied, repeated, or unregistered derivation objects.

The observer's original process identity and initial recipe identity remain unchanged.
The final native configuration uses the independently derived installed identities.
Every observer/configuration check must verify their original retained derivation link.
A second observer, charge, journal, configuration choice, or origin remains prohibited.

## Required evidence

Source tests must prove charge-before-write order and failure retention.
They must reject a caller-created receipt and any changed nonderived field.
They must reject repeated compilation, derivation, reservation, or observer attachment.
The complete source and installed-wheel checks remain mandatory.

The separate operational proposal must freeze the final commands and complete recipe inputs.
The owner must approve that proposal before compilation, Linux mutation, authentication, or subscription use.
Both twenty-case fixtures and the actual frozen-candidate live acceptance remain mandatory.
Publication still requires full Phase 2D acceptance.
Phase 2E remains outside this work.

## Decision request

Approve this source amendment to charge the immutable build recipe before compilation and derive installed identities once.
Approval permits source preparation only.
The complete operational batch requires its separate approval.
