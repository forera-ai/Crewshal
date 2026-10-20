# Phase 3B isolated APT attempt stopped at host storage floor

Date: 2026-10-20. Entry revision: `901b8ffff00b4f2e67b36515cee05b507aaaaf8a`.
Branch: `codex/phase1-architecture`. Host: macOS 27.2 arm64 with VMware Fusion.
Guest: Ubuntu 24.04.5 arm64, Linux `6.8.0-147-generic`, four CPUs.
The owner approved the [exact isolated APT proposal](PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md).
This record closes that attempt. The clone is off, and its network adapter remains disconnected.

## Commands and results

The worktree was clean at entry revision. The approved input index and frozen Phase 3A checker passed.
The checker verified 23 artifacts and 768 planned units.
The private custody manifest matched all 31 original guest files before and after the attempt.
Its SHA-256 was `a7b1408d10f50aaf44e00c28e8ef71953ae3dc7055e83d1f904d49efc6c89dcf`.
The source guest, ISO, both historical guests, archives, receipts, and extraction images were not changed by this attempt.

`vmrun -T fusion list` showed zero running guests before the start.
The clone VMX specified four CPUs, 17,408 MiB memory, and disabled network and sharing.
`vmrun -T fusion start DESTINATION_VMX gui` started only the separate clone once.
The owner signed in locally. No credential entered a command, project file, or Git.

The guest commands included `uname -srm`, `getconf _NPROCESSORS_ONLN`, `free -b`, and `df -B1 /var/tmp`.
They returned four CPUs, 17,760,563,200 memory bytes, and more than 55,000,000,000 free guest disk bytes.
The isolated APT file held only the approved two `Dir::Etc` lines.
Its empty configuration directory remained empty.
`APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-config dump` showed no `Invoke` or `Hooks` keys.
The exact 30 package arguments produced 101 objects, 111,245,650 listed bytes, and an 18,708,214-byte largest object.
The guest interface `enp2s0` stayed down with zero receive and transmit bytes.

The owner then rebooted the clone and signed in again. The owner did not authorize a network toggle through that reply.
The repeated offline checks returned the same 101 objects, 111,245,650 bytes, and 18,708,214-byte largest object.
The isolated APT configuration still showed no effective `Invoke` or `Hooks` keys.
The guest reported 55,456,399,360 free `/var/tmp` bytes after reboot.

Before network connection, `df -Pk /Volumes/X10Pro` showed 40,212,544 KiB free.
This equals 41,177,645,056 bytes.
The approved floor was 68,719,476,736 bytes. The stop rule applied.
No adapter connection or download command ran.
`vmrun -T fusion stop DESTINATION_VMX soft` returned exit zero.
The final `vmrun -T fusion list` showed zero running guests.
The clone used 4,885,889,024 allocated host bytes after shutdown.
At shutdown, `df -Pk /Volumes/X10Pro` showed 40,212,412 KiB, or 41,177,509,888 free bytes.
A later check showed 37,722,504 KiB, or 38,627,844,096 free bytes.
The available space changed during this work. Its cause is not established.

## Costs, limits, and continuation

Known new network transfer, package retrieval, paid-host cost, and metered API cost were zero.
Subscription quota debit remains unknown. The prior conservative charge remains 10,008,484,533 bytes.
The unused 167,772,160-byte allowance did not become a charge.
No package was installed. No archived tool, Linux test, native turn, or evaluation row ran.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes this attempt.
The [retry proposal](PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md) requires restored host space and a separate exact decision.
