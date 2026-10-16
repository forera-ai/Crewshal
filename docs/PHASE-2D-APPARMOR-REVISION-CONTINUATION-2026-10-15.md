# Phase 2D AppArmor revision continuation — 2026-10-15

Phase 2D remains incomplete.
The owner approved exact v27 through question `call_f68783ab804d4dadb1787fa44c41d81f`.
Its record SHA-256 is `1b427675e9e78da5390316f9f234d308cd304654d33cfcd0d284ae90cf8c5914`.

## Actual v27 result

The exact batch ran once and created the twenty-second full charge.
Independent prestart checks verified 227 inputs, both installed units, twenty-one prior journals, and eighteen original journal FD identities.
Observer `29199` passes the corrected policy-open step.
Its bounded policy-load child then reports `BlockingIOError`, errno `11`, at frozen `admission.py:157`.
The failure occurs during the first AppArmor namespace revision read, before policy loading.
A fresh read-only probe returns `269\n`, then `EAGAIN` on its second read.
The [Linux 7.0 source](https://github.com/torvalds/linux/blob/v7.0/security/apparmor/apparmorfs.c#L584) specifies this event-interface behavior.
It does not provide ordinary end-of-file behavior after the current revision.
The generic proc reader therefore refuses while waiting for end-of-file.

The project already has a bounded AppArmor reader for this interface.
Its exact source returns revision `269` in a separate read-only VM check.
The correction uses `RetainedAppArmorExport._revision` at all four operational revision sites.
That reader checks AppArmorfs, handles `EAGAIN` after nonempty data, and validates the revision syntax.
The generic proc reader remains unchanged.
Before-and-after revision comparisons remain required.
No diagnostic command loads policy or executes a compiler.

Both original compiler attempts remain consumed.
Observer `29199`, timer `29201`, original handles, objects, outputs, and unknown installation remain retained.
The twenty-second journal SHA-256 is `bb950808571b86b3b030b4c8d344353784745f0894554d95536c5ac7b7c059e9`.
The new batch and observer record zero memory-limit events.
Their memory peaks are 121405440 and 93913088 bytes, respectively.
All twenty-two charge snapshots and nineteen remaining original journal FD identities pass read-only checks.
Shared OOM counters remain at one event and one kill.
The exact restoration returned forwarding to zero before source changes.
No qualification, device login, or live turn occurred.

## Verification

Two new regression methods produce two errors before correction.
They exercise revision reads during policy loading and installed-role discovery.
All 41 focused checks pass after correction.
Both fresh source and installed-wheel suites pass 1220 occurrences, including 1204 unique methods and 1063 Phase 2D methods.
Both record zero failures, errors, or skips.
Both deny network access, clear the inherited environment, and use a fresh HOME.
All 47 installed package files match source.
Ruff checks and formatting checks pass for 117 current files; mypy passes for 46 production files.
Actual policy loading remains unverified.

All 228 archive members and both installed unit derivations pass independent offline checks.
The root contains 348564437 prospective input bytes within its unchanged 469762048-byte ceiling.
The 26583040-byte archive SHA-256 is `61a12c8393e7d3a9721f836c01d19068cc7e83ab08b6669b6c859939f181febb`.
The private batch SHA-256 is `0012dd93141c7998ae38ea6dcdb9cc11e016bb590178e2c2cd217bc71f0585b4`.
The configuration SHA-256 is `e8b9315c08d35cdf2927840af7a42fd0cb09fca89771b38eefc1154efeb0ed9d`.
The [exact v28 record](qualification/phase-2d-executable-batch-v28-20261015.json) binds all commands and inputs.
Its SHA-256 is `ad0201333e8292f8371575f9cb0b2d81381dbe0ccb6733ab00b65193f4bde7c5`.

## Exact new exception

Twenty-two charges reserve `188978561024` logical and allocated bytes each, or 176 GiB.
This exception permits one twenty-third charge and `197568495616` combined reserved bytes each, or 184 GiB.
It permits one additional C compilation and one additional AppArmor compilation within the original shared 30-second interval.
Twenty-three nominal charges total `18522046464` memory bytes and `2944` tasks.
Keep the approved shared retention parent at 2 GiB.
Each batch remains at 768 MiB, and each observer remains at 128 MiB.
CPU, tasks, swap, all original clocks, and three sequential lanes remain unchanged.
Startup remains 120 seconds, each storage job remains 30 seconds, and the batch remains 600 seconds with its original cleanup reserve.
Preserve all prior charges, remaining original custody, outputs, partial objects, counters, clocks, and unknowns.
The historical loss of observer `24610` and timer `24612` remains accepted under v26.
Reconstruct no lost proof or physical release.
No counter reset, refund, reuse, admission bypass, or further retry is permitted.
Stop on failure, another OOM event, or missing required custody.

Upload and preparation use exclusive `v25` guest paths.
The units are `crewshal-2d-20261015v25.slice` and `crewshal-2d-20261015v25-observer.service`.
Require independent input, custody, and kernel readback before observer start.
Both complete twenty-case qualifications must pass before device login.
Each must cover every enabled native file tool.
The live lane permits genuine stock device login and exactly one subscription implementation turn.
Subscription quota has no hard financial ceiling.
Metered APIs, purchased credits, extra turns, and paid hosts remain excluded.
Require actual frozen candidate validation, complete admission linkage, positive waits, and original idle retention.
Restore forwarding with the exact approved command and preserve the approved 2 GiB parent afterward.

The [approved v27 exception](PHASE-2D-RETAINED-POLICY-CONTINUATION-2026-10-15.md) states, "No counter reset, refund, reuse, admission bypass, or further retry is permitted."
This additional attempt requires separate direct owner approval.
No v28 guest operation has started.
Publish only after full Phase 2D acceptance.
Do not start Phase 2E.
