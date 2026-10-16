# Phase 2D physical-domain direct-I/O continuation — 2026-10-15

Phase 2D remains incomplete.
The owner approved exact v21 through question `call_bc66a65f46274e4c81da6b973757b554`.
The approved record SHA-256 is `0629f34bd651d8c374f578f14ed9647048d9e7bf6be1f57b7bb6e116fe41ca61`.

## Actual v21 result

Upload, preparation, forwarding enable, and observer start each ran once.
Independent readback verified 227 inputs, both final units, fifteen prior journals, and thirteen original journal FD identities.
Observer PID `21410` created the sixteenth full charge.
Root copying reached the same final resource gate at frozen `admission.py:458`:

```text
aggregate has resource-refusal history
```

The observer again reached its 128 MiB memory limit and records 861 memory-limit events.
The snapshot records zero OOM events and OOM kills.
The common parent retains 3779 memory-limit events, including 2084 local events.
No counter was reset.
The exact restoration returned forwarding to zero before source changes.
Both compiler attempts and the operational attempt remain consumed.
The sixteenth journal SHA-256 is `60a50e20eb1242227224a1dc3ae1c4c2b2f8384658adf6b0c9f1d1d3fe26c747`.
No qualification, device login, or live turn occurred.
Physical closure remains unknown.

Read-only `cachestat` inspection now separates the two cache layers.
All 910 copied root files have zero cached data bytes at the measured snapshot.
The 1 GiB physical-domain backing image retains 127778816 cached bytes and 61440 dirty bytes.
It has no active writeback in that snapshot.
The earlier small-file correction therefore does not address the buffered backing image.
The first diagnostic used an empty range and could not measure whole files.
The corrected diagnostic uses each actual file size; both local records remain preserved.
No cache diagnostic writes, evicts pages, or changes original loop settings.

## Source correction and verification

The change applies only to the physical-domain loop.
Original loop FD custody and the existing attach sequence precede every new control.
The child requests a 4096-byte logical block size, then direct-I/O mode.
It requires actual `BLKSSZGET` readback of 4096 and exact `LOOP_GET_STATUS64` readback with flag `16` before formatting.
Later physical-domain proofs also require that exact direct-I/O flag.
A refused or ineffective request stops the batch; buffered fallback is not accepted.
Compiler and role loops keep their existing settings.
All original backing identities, offsets, sizes, namespace controls, clocks, and resource checks remain required.
No old loop is reconfigured, detached, cleared, or reused.
No original counter is reset.

Linux exposes separate block-size and direct-I/O controls. See the [Linux loop manual](https://man7.org/linux/man-pages/man4/loop.4.html).
The installed UAPI confirms both ioctl values and direct-I/O flag `16`.
Read-only `statx` reports 4-byte memory alignment and 512-byte offset alignment for the retained backing file.
The proposed 4096-byte blocks satisfy those reported alignments.
Actual effective direct I/O remains unverified until the exact approved batch observes it.

Five fresh regressions produce four failures and one error before correction.
All 121 focused production and installation checks pass after correction.
They require custody before controls, reject ignored mode requests, reject wrong block size, and preserve loops after kernel refusal.
They also require direct I/O only for the physical domain.
Both complete source and fresh installed-wheel suites pass 1191 test occurrences.
Each contains 1175 unique methods, including 1034 Phase 2D methods.
Both record zero failures, errors, or skips.
Both deny network access, clear the inherited environment, and use a fresh HOME.
All 47 installed package files match source.
Ruff checks and formatting checks pass for 117 files; mypy passes for 46 production files.
The offline wheel uses cached setuptools `80.9.0`.
No local verification command executes a Linux C or AppArmor compiler.

All 227 prospective inputs match their exact sizes, modes, and hashes.
The prospective root contains 348559405 input bytes within its original allowance.
The archive contains 26583040 bytes.
Its SHA-256 is `4a5ebc105cd6fc3ea8c6f0bec0f96a97b951b92ee392c05e4ea1093a61a14296`.
The private batch SHA-256 is `f5a315625eadf04bf0cd5b4fc8a0258a8342866c08186ca6071d1e5b70f360d1`.
The configuration SHA-256 is `36027e3093fa723cfc43a7c1cf1f7a0fe088f8ad43c63390bfead7d4454a639e`.
The [v22 record](qualification/phase-2d-executable-batch-v22-20261015.json) binds exact scripts, commands, units, limits, and hashes.
Its SHA-256 is `9473b455ddbd02253e07b6f1b2b2a789ebd2b05d96c98741a25a7ebc31039d0c`.

## Exact new exception

Sixteen charges reserve `137438953472` logical and allocated bytes each, or 128 GiB.
This exception permits one seventeenth charge and `146028888064` combined reserved bytes each, or 136 GiB.
It permits one additional C compilation and one additional AppArmor compilation.
Both builds share one original 30-second interval.
The observer receives one original 600-second clock and 120-second startup interval.
Actual common limits remain 768 MiB memory, 128 tasks, one CPU, and zero swap.
The observer limit remains 128 MiB.
Each batch retains its original `8589934592`-byte logical and allocated ceilings.
Seventeen nominal charges total `13690208256` memory bytes and `2176` tasks.
All sixteen earlier charges, outputs, consumed attempts, original custody, clocks, timers, counters, partial objects, and unknowns remain retained or historically recorded.
The failed v19 archive also remains retained.
This exception permits no refund, release, reuse, counter reset, or further retry.
It bypasses no existing admission check.

Upload and preparation use exclusive `v19` guest paths.
The units are `crewshal-2d-20261015v19.slice` and `crewshal-2d-20261015v19-observer.service`.
Require independent input and kernel readback before observer start.
Both complete twenty-case qualifications must pass before device login.
Each must cover every enabled native file tool.
The live lane permits genuine stock device login and exactly one subscription implementation turn.
Subscription quota has no hard financial ceiling.
Metered APIs, purchased credits, extra turns, and new paid hosts remain excluded.
Require the actual frozen candidate, credential-free validator, complete admission linkage, positive waits, and original idle retention.
Restore forwarding with the exact approved command.
Stop on any failed, missing, incomplete, or stale mandatory result.

The [approved v21 exception](PHASE-2D-SMALL-CACHE-CONTINUATION-2026-10-15.md) excludes another attempt after failure.
This proposal requires separate direct owner approval.
Publish only after full Phase 2D acceptance.
Do not start Phase 2E.
