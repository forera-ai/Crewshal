# Phase 2D raw policy continuation — 2026-10-15

Phase 2D remains incomplete.
The owner approved exact v28 through question `call_f303d22c2958456b9e13674bb18ba875`.
Its record SHA-256 is `ad0201333e8292f8371575f9cb0b2d81381dbe0ccb6733ab00b65193f4bde7c5`.

## Actual result and correction

The exact batch ran once and created the twenty-third full charge.
Independent prestart checks verified 227 inputs, both installed units, twenty-two prior journals, and nineteen original journal FD identities.
Observer `30031` passes revision readback and the absent-profile check.
The policy write then fails at frozen `linux_operational.py:1335` with errno `93`.
The matching kernel audit record reports "invalid profile format" for child `30201`.
The retained output starts with a userspace compression header followed by Zstandard data.
The pinned kernel loader expects serialized policy or a Zstandard frame at byte zero.
It does not recognize the userspace header at byte zero.

The [AppArmor 5.0.2 serializer](https://gitlab.com/apparmor/apparmor/-/raw/v5.0.2/parser/parser_interface.c) adds that header to compressed stdout output.
The pinned `parser_main.c` maps `--zstd-compress-level=none` to uncompressed output.
The new recipe requires exactly one instance of that option.
The validator rejects missing, duplicate, or conflicting options.
Other parser arguments, source policy, direct add-only loading, and source-to-binary-to-export checks remain unchanged.
No new loader or decompression path is introduced.
A read-only diagnostic decodes the four retained containers to 37154 bytes of serialized policy.
That result remains below the unchanged one-MiB compilation output ceiling.
No diagnostic executes a compiler, loads policy, or reuses the old output for admission.
Actual new compilation and policy loading remain unverified.

Both original compiler attempts remain consumed.
Observer `30031`, timer `30033`, original handles, objects, outputs, and unknown installation remain retained.
The twenty-third journal SHA-256 is `8e8aa66bb9c2bdae6ff03c4bbb0262a46456b2015d8c67ceadd55fe27b29b268`.
The batch and observer record zero memory-limit events.
Their memory peaks are 118366208 and 94359552 bytes, respectively.
All twenty-three charge snapshots and twenty remaining original journal FD identities pass read-only checks.
Shared OOM counters remain at one event and one kill.
The exact restoration returned forwarding to zero before source changes.
No qualification, device login, or live turn occurred.

## Verification and exact inputs

Two new regression methods produce one failure and one error before correction.
All 69 focused checks pass after correction.
Both fresh source and installed-wheel suites pass 1222 occurrences, including 1206 unique methods and 1065 Phase 2D methods.
Both record zero failures, errors, or skips.
Both deny network access, clear the inherited environment, and use a fresh HOME.
All 47 installed package files match source.
Ruff checks and formatting checks pass for 117 current files; mypy passes for 46 production files.
All 228 archive members and both installed unit derivations pass independent offline checks.
The root contains 348564553 prospective input bytes within its unchanged 469762048-byte ceiling.
The 26583040-byte archive SHA-256 is `c565982627f3db67439d297689bf7c71ff608622224e9d2c7faefdfdc7dad395`.
The private batch SHA-256 is `314865cc42fe02d7b6d5469d4d0538bf051ce5a34578deb06f0d35808d462b4c`.
The configuration SHA-256 is `fe9fca8dc6d55ff3a06242099d6d9931d151d4762703d8b53aa0c959e470f7b8`.
The [exact v29 record](qualification/phase-2d-executable-batch-v29-20261015.json) binds all commands and inputs.
Its SHA-256 is `638cf90f32188dfb024eae2810fe79c547c138a6b41bfcc494bcdb107546b4cd`.

## Exact new exception

Twenty-three charges reserve `197568495616` logical and allocated bytes each, or 184 GiB.
This exception permits one twenty-fourth charge and `206158430208` combined reserved bytes each, or 192 GiB.
It permits one additional C compilation and one additional AppArmor compilation within the original shared 30-second interval.
Twenty-four nominal charges total `19327352832` memory bytes and `3072` tasks.
Keep the approved shared retention parent at 2 GiB.
Each batch remains at 768 MiB, and each observer remains at 128 MiB.
CPU, tasks, swap, all original clocks, and three sequential lanes remain unchanged.
Startup remains 120 seconds, each storage job remains 30 seconds, and the batch remains 600 seconds with its original cleanup reserve.
Preserve all prior charges, remaining original custody, outputs, partial objects, counters, clocks, and unknowns.
The historical loss of observer `24610` and timer `24612` remains accepted under v26.
Reconstruct no lost proof or physical release.
No counter reset, refund, reuse, admission bypass, or further retry is permitted.
Stop on failure, another OOM event, or missing required custody.

Upload and preparation use exclusive `v26` guest paths.
The units are `crewshal-2d-20261015v26.slice` and `crewshal-2d-20261015v26-observer.service`.
Require independent input, custody, and kernel readback before observer start.
Both complete twenty-case qualifications must pass before device login.
Each must cover every enabled native file tool.
The live lane permits genuine stock device login and exactly one subscription implementation turn.
Subscription quota has no hard financial ceiling.
Metered APIs, purchased credits, extra turns, and paid hosts remain excluded.
Require actual frozen candidate validation, complete admission linkage, positive waits, and original idle retention.
Restore forwarding with the exact approved command and preserve the approved 2 GiB parent afterward.

The [approved v28 exception](PHASE-2D-APPARMOR-REVISION-CONTINUATION-2026-10-15.md) excludes any further retry.
This additional attempt requires separate direct owner approval.
No v29 guest operation has started.
Publish only after full Phase 2D acceptance.
Do not start Phase 2E.
