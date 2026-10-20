# Phase 3B offline Ubuntu package snapshot completion

Date: 2026-10-20. Entry revision: `93b31fe` on `codex/phase1-architecture`.
Environment: local macOS, VMware Fusion, and the isolated Ubuntu 24.04.5 arm64 clone.
The owner approved exactly one read-only package snapshot in this Codex chat.

## Preflight and commands

The prior 213-file input index matched every size and SHA-256 before the admission commit.
The frozen Phase 3A checker passed 23 public artifacts and 768 planned units.
Git was clean. `vmrun list` showed zero running VMs.
The clone configuration showed four CPUs, 17,408 MiB memory, and disabled network and sharing.
All 31 original guest files matched the private custody manifest.
The initial clone allocation was 4,921,806,848 bytes. Combined allocation was 30,674,173,952 bytes.
The host had 139,071,770,624 free bytes before the start.

`vmrun -T fusion start DESTINATION_VMX gui` started the clone once.
The owner entered the existing guest password in VMware Fusion. No password entered chat or Git.
The console ran each of the eight exact commands in the [approved proposal](PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-PROPOSAL-2026-10-20.md).
The commands were `uname -srm`, `cat /etc/os-release`, `getconf _NPROCESSORS_ONLN`, `free -b`, `df -B1 /var/tmp`, the APT list count, `apt-cache policy`, and `apt-get -s`.
The two APT commands used the proposal's exact package arguments.

## Results and limits

The console showed Linux `6.8.0-147-generic aarch64` and Ubuntu 24.04.5 LTS.
It showed four online CPUs, 17,760,563,200 total memory bytes, and 55,507,247,104 free bytes on `/var/tmp`.
The APT list directory contained 68 entries.
`apt-cache policy` completed and showed candidate versions from the local package lists.
The console did not retain a complete candidate table in the recorded evidence.
`apt-get -s --no-install-recommends install ...` finished at the shell prompt without an error.
The simulation showed `ninja-build` version `1.11.1-2` in its configuration lines.
The full resolved package list and transfer sizes were not captured. They remain unknown.
The [Ubuntu APT manual](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html) defines `-s` as a no-action simulation.

`vmrun -T fusion stop DESTINATION_VMX soft` shut down the clone.
The final `vmrun list` showed zero running VMs.
The clone used 4,977,467,392 allocated host bytes after shutdown.
The source guest, ISO, and clone used 30,729,834,496 bytes together.
The host had 139,016,450,048 free bytes. All three approved host limits passed.
The clone still had disabled network and sharing. All 31 original guest files still matched.
New network transfer, package retrieval, paid-host cost, and metered API cost were zero.
No installation, archived tool, Linux test, native turn, or evaluation row ran.

The missing complete package table prevents an exact transfer and installation decision.
The single ledger closes the used guest start. Any later guest action needs a separate concrete decision.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
