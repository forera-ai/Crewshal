# Phase 3B retained toolchain readback completion

Date: 2026-10-20. Entry revision: `57cbae2` on `codex/phase1-architecture`.
Environment: macOS 27.2, build `26B5112a`, Python 3.12.15, local retained images.
Status: Read-only inventory complete. Installation and execution remain closed.

The [inventory](PHASE-3B-RETAINED-TOOLCHAIN-READBACK-2026-10-20.json) binds all 16 retained archive IDs.
It records 1,368,218,293 compressed bytes and 4,371,619,599 regular content bytes.
The member report records 40 links: three Node links and 37 Swift links.
Each archive ID binds its pinned compressed size, SHA-256, member metadata digest, and extracted output root.
Each output root binds one of the two independently verified output manifest digests.

The read-only Python check hashed all 16 retained `.blob` files again.
All lengths and SHA-256 values matched. Every bound output root existed.
The inventory left all installed executable hashes, effective commands, and providers null.
`rtk proxy file` identified AArch64 ELF candidates for Bun, Node, Swift, .NET, Codex, and Claude.
This static file check did not establish that any candidate can run in the selected Linux guest.
The frozen Phase 3A checker passed with 23 artifacts and 768 planned units.
No guest, package resolver, installer, archived tool, native turn, provider, or evaluation row ran.

Known paid-host and metered API cost was USD 0. New network transfer was zero bytes.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte charge and final 10,008,484,533-byte cumulative charge remain intact.
The two extraction attempts remain closed. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. B1 conformance and Phase 3B calibration remain unknown.
The [separate-guest proposal](PHASE-3B-SEPARATE-GUEST-CAPACITY-PROPOSAL-2026-10-20.md) still needs an owner decision.
