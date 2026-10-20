# Proposed Phase 3B offline package installation

Date: 2026-10-20. Status: proposed; no installation is admitted.
Entry revision: `bb86c0ad5deca0c63d31fea3b8a9eb93a66a77a1` on `codex/phase1-architecture`.
The [retrieval record](PHASE-3B-APT-STORAGE-RETRY-COMPLETION-2026-10-20.md) verifies 101 cached Ubuntu packages.
All 101 names, versions, and SHA-256 hashes matched guest APT candidate metadata.
The clone is off with its network adapter and sharing disconnected.

## Exact owner decision requested

Approve one start of `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Approve one offline APT installation of the 101 cached objects for the thirty requested package names below.
The command may execute Ubuntu package maintainer scripts as root and change this separate clone.
Allow no network connection, package retrieval, archived tool execution, Linux tests, native turns, or evaluation.
Stop after the installation result and custody checks. Do not retry or restart under this decision.

```sh
set -- cmake ninja-build build-essential git binutils gnupg2 libc6-dev libcurl4-openssl-dev libedit2 libgcc-13-dev libncurses-dev libpython3-dev libsqlite3-0 libstdc++-13-dev libxml2-dev libz3-dev pkg-config tzdata zip unzip zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev uuid-dev tk-dev libgdbm-dev
sudo env APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-get -y --no-download -o Acquire::Retries=0 --no-install-recommends install "$@"
```

## Exact preflight and limits

Require a clean worktree, matching exact input index, passing frozen Phase 3A checker, and zero running guests.
Match all 31 original guest files to their private custody manifest.
Require four configured CPUs, 17,408 MiB memory, disconnected network, and disabled guest sharing.
Require at least 68,719,476,736 host bytes free before start and at shutdown.
Keep clone allocation below 34,359,738,368 bytes.
Keep source guest, ISO, and clone allocation together below 68,719,476,736 bytes.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free `/var/tmp` bytes.
Limit this attempt to two active hours and four elapsed hours.
Permit zero new network charge, paid-host cost, metered API cost, native turns, and evaluation rows.

Start this clone once with `vmrun -T fusion start DESTINATION_VMX gui`.
Require the owner to sign in locally. Keep credentials out of commands, files, and Git.
Read back the network, sharing, memory, CPU, guest disk, and cache state before installation.
Require the isolated APT configuration to retain exactly its two recorded lines and empty parts directory.
Require no effective APT or dpkg executable hooks under `APT_CONFIG`.
Require exactly 101 cached packages, 111,245,650 bytes, and zero partial cache entries.
Verify all 101 cached package hashes against the signed guest APT candidate metadata again.
Run an offline `apt-get -s --no-download --no-install-recommends install "$@"` with the same `APT_CONFIG`.
Require exactly the approved 101 package objects, unchanged candidates, and no additional download or removal.
Stop before installation if any check differs or if any resource floor fails.

## One installation and closure

Run the exact installation command once with the network adapter disconnected.
Record APT exit status, installed package versions, actual package count, guest free bytes, clone allocation, and command output.
Record package maintainer-script errors and preserve partial installed state after failure.
Soft-stop the clone, then check network isolation, zero running guests, host limits, and all 31 source guest hashes.
This decision closes after one command, including a partial or failed result.

Preserve both historical guests, ISO, sixteen archives, receipts, extraction images, fixed image, and frozen Phase 3A bytes.
Keep the historical 10,008,484,533-byte archive charge and new 116,542,541-byte package charge intact.
The cumulative conservative charge remains 10,125,027,074 bytes.
Keep executable hashes, effective commands, providers, and B1 conformance null until observed.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
