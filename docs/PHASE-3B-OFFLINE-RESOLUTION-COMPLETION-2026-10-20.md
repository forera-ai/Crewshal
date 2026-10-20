# Phase 3B offline Ubuntu package resolution completion

Date: 2026-10-20. Entry revision: `b6c9db6` on `codex/phase1-architecture`.
Environment: local macOS, VMware Fusion, and the isolated Ubuntu 24.04.5 arm64 clone.
The owner approved one exact read-only capture in the current Codex chat.

## Preflight and commands

All 217 exact entry inputs matched their sizes and SHA-256 values.
The frozen Phase 3A checker passed 23 artifacts and 768 planned units.
Git was clean. `vmrun list` showed zero running VMs before the start.
The clone had four configured CPUs, 17,408 MiB memory, and disabled network and sharing.
All 31 original guest files matched the private custody manifest before and after the attempt.
The initial clone allocation was 4,977,467,392 bytes.
The initial combined guest and ISO allocation was 30,729,834,496 bytes.
The initial host free space was 139,013,558,272 bytes.

`vmrun -T fusion start DESTINATION_VMX gui` started the clone once.
The owner entered the existing password in the VMware console.
The first visible login attempt failed. The next attempt reached the shell.
No password entered chat or Git.
The console ran the exact setup and read-only commands in the [approved proposal](PHASE-3B-OFFLINE-RESOLUTION-PROPOSAL-2026-10-20.md).
These commands included `set -o pipefail`, capacity checks, `apt-cache policy`, `apt-get -s`, and two `apt-get --print-uris` queries.
The package arguments remained the exact thirty names in that proposal.
The console displayed every simulation and URI-size page during this chat.
The URI-size output omitted source URLs and showed package filenames, byte counts, and APT hashes.

## Results

The guest reported `Linux 6.8.0-147-generic aarch64` and four online CPUs.
It reported 17,760,563,200 total memory bytes and 55,494,590,464 free `/var/tmp` bytes.
The memory floor was 17,179,869,184 bytes. The guest disk floor was 42,949,672,960 bytes.
The offline APT policy command returned a candidate for every named package.
The candidates included `cmake 3.28.3-1build7` and `ninja-build 1.11.1-2`.
The no-action APT simulation returned to the shell without an error.
The URI-size table returned 101 package objects totaling 111,245,650 bytes.
Its largest object was 18,708,214 bytes.
The table's three displayed console pages remain in this chat's tool transcript.
No durable machine-readable copy of the 101 individual rows was produced.
The object count and byte sum bind this offline package-list state only.
APT mirror availability and future candidate drift remain unknown.

`vmrun -T fusion stop DESTINATION_VMX soft` returned exit zero.
The final `vmrun list` showed zero running VMs.
The final clone allocation was 4,990,726,144 bytes.
The combined guest and ISO allocation was 30,743,093,248 bytes.
The host had 138,999,660,544 free bytes.
The clone allocation stayed below 34,359,738,368 bytes.
The combined allocation stayed below 68,719,476,736 bytes.
Host free space stayed above 68,719,476,736 bytes.
The clone still has disabled network and sharing.
All 31 original guest files still match their custody manifest.

No network transfer, package retrieval, installation, archived tool, Linux test, native turn, or evaluation row ran.
Known paid-host and metered API costs were USD 0. Subscription quota debit remains unknown.
The original sixteen archives, both receipts, both extraction images, fixed image, and conservative transfer charges remain unchanged.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The single admission ledger closes this guest start. Later transfer and Linux work need separate exact decisions.
