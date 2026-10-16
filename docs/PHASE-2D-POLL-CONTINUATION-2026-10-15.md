# Phase 2D high-descriptor wait continuation — 2026-10-15

Phase 2D remains incomplete.
The owner approved exact v15 through question `call_e9cf5e010b04402dbef0c64c59999fe8` on October 15.
The approval binds record SHA-256 `71d41d82dd99a8f0541e54eff7c6878d8362199e544d4b52e404d29f7e9ce5a8`.

## Actual v15 result

All ten prior journal hashes and eight original journal FD identities matched before new preparation.
The old consumed compiler pidfds remained unchanged.
The new guest paths were absent, and IPv4 forwarding was zero.
Actual common memory use was `344190976` bytes within the unchanged `805306368`-byte ceiling.
The exact upload, preparation, forwarding change, and observer start each ran once.
Independent prestart readback verified all 227 inputs, both final units, prior journals, original custody, and common controls.

Observer PID `13731` created the eleventh full charge.
Both original compilers passed, and the full compiler-volume read-only remount passed.
The original final lanes bound without the earlier verification cycle.
The batch then reached installation-directory preparation.
Its storage job forked child PID `13791`.
The parent refused before it could admit that child.

The retained diagnostic is:

```text
filedescriptor out of range in select()
```

Bounded read-only inspection recovered the original `ValueError` frames and their local FD values.
The original pipe read FD is `1475`, and the child pidfd is `1476`.
The observer retained 1476 descriptors when inspected.
The first failure occurred at `linux_storage.py:514` during placement acknowledgement polling.
The same limitation caused another failure at line `582` during terminal cleanup polling.
The source sent its original pidfd SIGKILL before that second failure.
The child remains a zombie under the original parent and retained pidfd.
No later diagnostic operation signalled or reaped it.

The [Python documentation](https://docs.python.org/3/library/select.html) describes the polling interfaces.
The [Python issue record](https://bugs.python.org/issue31610) identifies the `select()` descriptor-number ceiling of 1024.
This ceiling differs from the approved `4096` open-file limit.
The original custody requirements keep the observer's descriptors open.
Closing or renumbering original descriptors would change that custody.

The eleventh journal SHA-256 is `917ba2832e26af663221aa37bad8895221a30cf274ccdba89c48ad46148052c6`.
Its original charge remains retained with installation `unknown`.
Its configuration SHA-256 is `9ab21657ab4d4af75af305d076689ea5f0f53736e51112d4870990df1b245abe`.
Both compiler attempts remain consumed.
All eleven charges, original processes, outputs, and unknown results remain retained or historically recorded.
Physical closure remains unknown.
No policy installation, qualification, device login, or live turn occurred.
The exact approved restoration command returned IPv4 forwarding to zero.

## Source correction and verification

A shared readiness function now uses `poll()` when any descriptor number is at least 1024.
Low descriptors retain the existing `select()` behavior.
All 75 observer readiness call sites use this function.
Source AST inspection verifies those call sites across the production Python files.
The helper preserves original objects, list order, duplicates, read and write readiness, and EOF readiness.
It refuses invalid descriptors and negative or nonfinite supplied timeouts.
Its polling path creates no additional FD.
It does not close, duplicate, or renumber any supplied descriptor.
Callers retain their original deadline checks.
All common controls, clocks, file limits, and ownership checks remain unchanged.
The fixed-descriptor child source constants remain unchanged.

Four real high-descriptor regression checks produce five errors before the correction.
All four checks pass after the correction.
They exercise pipe readiness, socket object identity, duplicate inputs, EOF, closed-handle refusal, and finite timeout validation.
The first targeted migration suite also exposed two obsolete multiline mock targets.
Their corrected targets now replace the shared readiness call.
Both complete source and fresh installed-wheel suites pass 1174 test occurrences.
Each suite contains 1158 unique methods, including 1017 Phase 2D methods.
Both suites record zero failures, errors, or skips.
Both deny network access, start with an empty inherited environment, and use a fresh HOME directory.
All 47 installed package files match current source.
Ruff checks and formatting checks pass for all production and acceptance Python files and both new owner scripts.
Mypy passes for all 46 production Python files.
The wheel build uses cached setuptools `80.9.0` with network access denied.
No local verification command executes a Linux C or AppArmor compiler.

All 227 prospective manifest entries match their exact sizes, modes, and hashes.
The prospective root contains `348357464` input bytes within its original allowance.
The archive contains `26583040` bytes.
Its SHA-256 is `f697fe838fa6ba8bd9664041296269b735abe5aa7b2261a298ed27d471d625ff`.
The private batch SHA-256 is `5ebcdae5ddd50fbc4f89c4fa142fca9e35995f0ecbd5b907d77c7b4cae07397a`.
The configuration SHA-256 is `7a626a821d12baa067136a0facc6d02a591ce0a7a9b27cd07ec4a98fd65f9ab9`.
The [v16 record](qualification/phase-2d-executable-batch-v16-20261015.json) supplies the complete scripts, commands, limits, and hashes.
It records both archive unit hashes and final installed unit hashes.

## Exact new exception

Eleven charges reserve `94489280512` logical and allocated bytes each, or 88 GiB.
The new exception permits one twelfth charge and `103079215104` combined reserved bytes each, or 96 GiB.
It permits one additional C compiler process and one additional AppArmor compiler process.
It does not reuse any earlier output or reset a consumed attempt.
Both new builds share one original 30-second interval.
The new observer receives one original 600-second clock and 120-second startup interval.

Actual common limits remain `805306368` memory bytes, `128` tasks, one CPU, and zero swap.
Each new batch retains both original `8589934592`-byte storage ceilings.
The twelve nominal charges total `9663676416` memory bytes and `1536` tasks.
All previous charges, clocks, timers, handles, consumed attempts, and unknown results remain retained or historically recorded.
The exception permits no refund, release, reuse, or further retry.
Do not signal, reap, resume, or replace the original child PID `13791` or its pidfd `1476`.

The exact upload and preparation use exclusive `v13` guest paths.
The new units are `crewshal-2d-20261015v13.slice` and `crewshal-2d-20261015v13-observer.service`.
Independent input and kernel readback must precede observer start.
Both complete twenty-case qualifications must pass before the live lane.
Both qualifications must cover every enabled native file tool.
The live lane permits stock device login and exactly one subscription implementation turn.
Subscription quota has no hard financial ceiling.
Metered APIs, purchased credits, extra turns, and new paid hosts remain excluded.
The actual frozen candidate and independent credential-free validator must pass their original gates.
Complete admission linkage, positive waits, and original idle retention.
Restore IPv4 forwarding with the exact approved restoration command.
Stop on any failed, missing, incomplete, or stale mandatory result.

This proposal grants no operational approval.
Publish only after full Phase 2D acceptance.
Do not start Phase 2E.
