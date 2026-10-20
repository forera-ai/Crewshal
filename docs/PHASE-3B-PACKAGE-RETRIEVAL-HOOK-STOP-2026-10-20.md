# Phase 3B Ubuntu package retrieval stopped at APT hooks

Date: 2026-10-20. Entry revision: `4699791448ae196a025ee5148119714d464d3877`.
Branch: `codex/phase1-architecture`. Environment: macOS 27.2 arm64, VMware Fusion, Ubuntu 24.04.5 arm64.
The owner approved the [one-attempt proposal](PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md).
This record closes that attempt. The guest never connected to a network.

## Preflight and commands

Before the start, all 224 indexed inputs matched their recorded sizes and SHA-256 values.
Git was clean. `vmrun list` showed zero running guests.
The frozen Phase 3A checker passed 23 artifacts and 768 planned units.
All 31 original guest files matched the private custody manifest.
The clone had four CPUs, 17,408 MiB configured memory, and disabled network and sharing.
The host storage limits passed before the start.

`vmrun -T fusion start DESTINATION_VMX gui` started the clone once.
The owner signed in locally. No credential entered a command, project file, or Git.
The Ubuntu console ran `free -b`, `df -B1 /var/tmp`, `getconf _NPROCESSORS_ONLN`, and `uname -srm`.
The first two console entries lost initial characters. Their failed commands are visible in the chat transcript.
The valid `getconf` and `uname` entries then returned four CPUs and `Linux 6.8.0-147-generic aarch64`.
The guest reported 17,760,563,200 total memory bytes and 55,481,946,112 free `/var/tmp` bytes.
Both values exceeded the proposal's guest floors.

The console set the proposal's exact thirty package arguments.
`apt-get --print-uris --assume-yes --no-install-recommends install "$@"` ran offline through the proposal's AWK summary.
It returned 101 package objects, 111,245,650 listed bytes, and an 18,708,214-byte largest object.
These values matched the approved preflight.
`apt-config dump | grep -Ei '(invoke|hook|script)' || true` then exposed configured hooks.
They include `APT::Update::Pre-Invoke`, `APT::Update::Post-Invoke-Success`, `DPkg::Post-Invoke`, and `binary::apt::AptCli::Hooks::Install`.
The output also included unrelated `Description` keys because the broad grep matched `script`.
The proposal required a stop if any APT or dpkg hook was configured.
The adapter stayed disconnected. No download command ran.

`vmrun -T fusion stop DESTINATION_VMX soft` returned exit zero.
The final `vmrun list` showed zero running guests.

## Final readback and limits

The clone used 4,880,777,216 allocated host bytes after shutdown.
The source guest, ISO directory, and clone used 30,581,501,952 allocated bytes together.
The host had 139,160,035,328 free bytes.
These values passed the 32 GiB clone cap, 64 GiB combined cap, and 64 GiB host free floor.
The clone VMX still specifies four CPUs, 17,408 MiB, and disconnected network and sharing.
All 31 original guest files still match their custody manifest.
The frozen Phase 3A checker again passed 23 artifacts and 768 planned units.

This attempt used less than two active hours and four elapsed hours.
Known new network transfer, package retrieval, paid-host cost, and metered API cost were zero.
Subscription quota debit remains unknown. No package was installed or executed.
No Linux test, native turn, or evaluation row ran.
The prior 10,008,484,533-byte conservative charge remains unchanged.
The proposed 167,772,160-byte new allowance was not used.
All sixteen archives, both receipts, both extraction images, the fixed image, and frozen Phase 3A bytes remain unchanged.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The single admission ledger closes this guest start and network permission.

## Continuation

The [revised proposal](PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md) requests a separate decision.
It requires an isolated APT configuration and another offline preflight before any network connection.
No original archive URL or consumed redirect is eligible for retry.
