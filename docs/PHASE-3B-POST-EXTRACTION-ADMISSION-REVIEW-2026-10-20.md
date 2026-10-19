# Phase 3B admission review after retained extraction

Date: 2026-10-20. Status: Read-only review complete; guest decision pending.
Entry revision: `aa8f19d` on `codex/phase1-architecture`.
The two approved extraction batches are complete. Their further attempt flags are closed in the single admission ledger.
This review does not admit guest work, installation, package retrieval, archived tool execution, native turns, or evaluation rows.
The [retained inventory readback](PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json) binds all sixteen archives to both output manifests.
Its 4,371,619,599 regular content bytes match the sum of the two extracted batches.
It records 40 links: three Node links and 37 Swift links.
Installed executable hashes, effective commands, and providers remain null.
The local `file` check identified AArch64 ELF candidates for Bun, Node, Swift, .NET, Codex, and Claude.
It did not launch them or establish Linux runtime conformance.

## Local source metadata

The four selected sources remain in the first extracted output.
The Python source has six pinned requirement files. They contain 54 development, 26 documentation, four test, five typing, three build, and nine Python 3.7 entries.
The selected Python `tox` environments use the documentation and typing files. The base test environment uses the test file.
The TypeScript root `bun.lock` has 998 package entries with integrity values and 24 root development dependency declarations.
It does not record compressed archive byte counts for those packages.
The Swift `Package.swift` declares no external Swift package dependency.
The .NET source fixes SDK `9.0.100`. The selected project files declare direct package references.
The actual .NET transitive package set, byte counts, hashes, and rights remain unbound.
The Ubuntu arm64 package closure, including CMake and Ninja, remains unbound.
The [Ubuntu CMake package page](https://packages.ubuntu.com/noble/arm64/cmake) lists twelve direct dependencies for `3.28.3-1build7`.
The [Ubuntu Ninja package page](https://packages.ubuntu.com/noble/arm64/devel/ninja-build) lists two direct dependencies for `1.11.1-2`.
These pages do not identify the packages already installed in a selected guest or freeze its full dependency closure.
No package resolver, installer, or tool from the retained archives ran during this review.
The retained Codex wrapper names `bin/codex.js` and a Linux arm64 optional package.
The retained Claude wrapper names `bin/claude.exe` and a Linux arm64 optional package.
Its `package.json` declares a postinstall hook. The extracted `bin/claude.exe` is a refusal placeholder.
No hook ran. The actual installed command and executable identity still require an admitted installation and Linux readback.

| Local source input | SHA-256 |
| --- | --- |
| Python `requirements/build.txt` | `d3ef91ebee54f317182134b191061325ad72eed5be7a2484d1f9de7205c5a293` |
| Python `requirements/dev.txt` | `edb0efa850ff4a2cb07121a972462dc02f4a439146dfb6d50e990c1c610f6640` |
| Python `requirements/docs.txt` | `9734b3d503f345f7d03eb7c923fb0baafbd574780fd070992aad87da21ed3ccc` |
| Python `requirements/tests.txt` | `5bac9588b5dda6960373aa11fe3c4ca9da734edf178169ceef18579702ee5c2f` |
| Python `requirements/tests37.txt` | `d87080293ce5a12245249089ed75b794a9ad1276b7d8491a13724ad307763a82` |
| Python `requirements/typing.txt` | `afa23e2cb2e7cec61928565cb9b0481ce410b1cf7067b0df727d0e80eaa8f07f` |
| TypeScript `bun.lock` | `2bcdfebb22fd9487a8f3344c4aa6b99baa073a372a460d74f8b5c44d10fbd298` |
| Swift `Package.swift` | `5c0ea7f615b82bfb850c64f66224124a7041e1d0004406543cd24c8ab526d84e` |
| .NET `global.json` | `ef3c65250475d812c838f1da34d65a7bae8b1a8d2ea1d375cc6644b898f47d41` |

## Host and guest custody

The host has 103,079,215,104 bytes of physical memory.
`vmrun list` reported zero running VMs. Both historical VMware bundles contain suspended-state files.
The first guest's `.vmss` and `.vmem` files date to October 18. The Phase 3B guest's files date to October 19.
The Phase 3B VM configuration records four CPUs and `memsize = "16384"` MiB.
Its last recorded guest-visible memory was 16,728,174,592 bytes, below the proposed 17,179,869,184-byte floor.
The current Phase 3B VM bundle uses 21,926,846,464 allocated host bytes.
Its 17,179,869,184-byte `.vmem` file accounts for most of that allocation.
The ISO directory uses 3,825,520,640 allocated host bytes.
Their current combined allocation is 25,752,367,104 bytes.
The earlier 9,093,566,464-byte combined allocation is historical. The cause and timing of the difference remain unknown.
No guest file, setting, disk, snapshot, or suspended state changed during this review.
The owner must choose whether to preserve both suspended guests and use a separate campaign guest.
An exact guest and resource proposal must follow that choice before any guest action.
One possible separate guest would reuse the existing ISO, four CPUs, 17 GiB configured RAM, and a sparse 64 GiB disk.
The alternate path would resume the suspended Phase 3B guest before an orderly shutdown and memory change.
Neither path is admitted. The suspended state makes these paths materially different custody decisions.
The [separate-guest capacity proposal](PHASE-3B-SEPARATE-GUEST-CAPACITY-PROPOSAL-2026-10-20.md) defines one bounded clone candidate.
The owner has not selected or approved that candidate.

## Remaining admission gates

The cumulative conservative transfer charge is 10,008,484,533 bytes.
The earlier 8,589,934,592-byte allowance has no conservative balance.
No new transfer ceiling, retained-data ceiling, or infrastructure rule is approved.
The two output images have 9,663,676,416 total logical bytes.
Their measured host allocations total 5,822,615,552 bytes after extraction.
Any new retained-data rule must state whether it counts these images and their contents.
The original sixteen URLs, object caps, stage cap, receipts, and charges remain fixed.

The frozen Phase 3A package still has 192 planned development rows and 576 sealed rows.
No executable identity, effective launch, provider identity, B1 conformance, native baseline, or calibration result is observed.
The frozen package requires two independent human quality graders before Phase 3C.
The old owner approval covered a dated proposal. ADR 0009 requires a new consolidated campaign decision for changed scope.
No Phase 3C acceptance claim can follow from the two extraction results alone.
