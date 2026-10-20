# Phase 3B separate guest capacity completion

Date: 2026-10-20. Entry revision: `9e790acd96eb7c18ad119e8b5e3003ec40eaf738`.
Environment: local macOS, VMware Fusion, and one isolated Ubuntu 24.04.5 arm64 clone.
The owner selected a separate guest and approved the exact proposal in this Codex chat.
This record covers one clone attempt and one guest capacity check.

## Preflight and custody

The exact 211-file input index passed size and SHA-256 checks before ledger changes.
The destination bundle did not exist. `vmrun list` showed zero running guests.
The source had one `.vmss` and one `.vmem` file. Its configuration specified four CPUs.
The source network and host sharing were disabled.
The source bundle used 21,926,846,464 allocated bytes. The ISO directory used 3,825,520,640 bytes.
Host free space was 143,994,945,536 bytes at the final preflight.
The private source custody manifest recorded 31 files and SHA-256 `a7b1408d10f50aaf44e00c28e8ef71953ae3dc7055e83d1f904d49efc6c89dcf`.

## Commands and results

The approved `vmrun -T fusion clone SOURCE_VMX DESTINATION_VMX full` command ran once without an error.
The exact source, destination, and full command remain in the [approved proposal](PHASE-3B-SEPARATE-GUEST-CAPACITY-PROPOSAL-2026-10-20.md).
The clone was powered off. It did not copy the source suspended state.
The source custody check matched all 31 files after cloning and after guest shutdown.
The clone retained a sparse 64 GiB disk and four CPUs.
Its network adapter and sharing device remained disconnected.
Only the clone changed to 17,408 MiB configured memory.
The clone also disabled the inherited root share mapping and link flags.

`vmrun -T fusion start DESTINATION_VMX gui` ran once.
The owner entered the existing guest password in the VMware console. No password entered this chat or Git.
The console ran these read-only commands: `uname -srm`, `cat /etc/os-release`, `getconf _NPROCESSORS_ONLN`, `free -b`, and `df -B1 /var/tmp`.
The results showed Ubuntu 24.04.5 LTS, Linux 6.8.0-147-generic aarch64, and four online CPUs.
`free -b` showed 17,760,559,104 total memory bytes.
`df -B1 /var/tmp` showed 55,519,887,360 available bytes on the guest root volume.
Both capacity values exceeded the approved minimums.
`vmrun -T fusion stop DESTINATION_VMX soft` shut down the clone.
The final `vmrun list` showed zero running guests.

The first three console input attempts lost or added command characters. Each returned command-not-found.
The correct `uname -srm` command then ran and returned its result.
No package installation, archived tool, repository test, native turn, or evaluation row ran.

## Final limits and unresolved work

The clone used 4,921,806,848 allocated host bytes after shutdown.
The source bundle, ISO directory, and clone used 30,674,173,952 bytes together.
The host had 139,072,647,168 free bytes after shutdown.
These values passed the 32 GiB clone cap, 64 GiB combined cap, and 64 GiB host free floor.
The network adapter stayed disconnected. New network transfer, paid-host cost, and metered API cost were zero.
The attempt took less than the two active hours and four elapsed hours allowed.
The frozen Phase 3A checker passed 23 artifacts and 768 planned units without opening sealed files.

The single ledger closes further clone and guest starts.
Package retrieval, installation, Linux qualification, archived tool execution, native turns, and evaluation remain closed.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The next work must bind exact dependency and campaign limits before another owner decision.
