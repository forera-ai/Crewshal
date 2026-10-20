# Proposed Phase 3B offline package snapshot

Date: 2026-10-20. Status: Approved for one attempt in the current Codex chat.
The owner replied, “Approve this exact snapshot.” The single admission ledger records this decision.
Entry revision: `3f74a47` on `codex/phase1-architecture`.
The [capacity completion](PHASE-3B-SEPARATE-GUEST-CAPACITY-COMPLETION-2026-10-20.md) verified the separate clone and shut it down.
This proposal covers one later start of that clone for read-only Ubuntu package metadata.
It does not authorize package retrieval, installation, archived tool execution, Linux tests, native turns, or evaluation rows.

## Exact guest and checks

Use only `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Keep both historical guests and all extraction images unchanged.
Before starting, require zero running VMs and a clean Git worktree.
Repeat the frozen Phase 3A checker and verify the exact input index.
Check the clone configuration before and after use.
Require four CPUs, 17,408 MiB configured memory, and a disconnected network adapter.
Keep root sharing, guest file sharing, clipboard sharing, and drag and drop disabled.
Check source custody hashes and host allocations before and after use.

Start the clone once with `vmrun -T fusion start DESTINATION_VMX gui`.
The owner enters the existing guest password in the VMware console.
Run only these read-only guest commands in the logged-in console:

```sh
uname -srm
cat /etc/os-release
getconf _NPROCESSORS_ONLN
free -b
df -B1 /var/tmp
ls -1 /var/lib/apt/lists | wc -l
apt-cache policy cmake ninja-build build-essential git binutils gnupg2 libc6-dev libcurl4-openssl-dev libedit2 libgcc-13-dev libncurses-dev libpython3-dev libsqlite3-0 libstdc++-13-dev libxml2-dev libz3-dev pkg-config tzdata zip unzip zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev uuid-dev tk-dev libgdbm-dev
apt-get -s --no-install-recommends install cmake ninja-build build-essential git binutils gnupg2 libc6-dev libcurl4-openssl-dev libedit2 libgcc-13-dev libncurses-dev libpython3-dev libsqlite3-0 libstdc++-13-dev libxml2-dev libz3-dev pkg-config tzdata zip unzip zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev uuid-dev tk-dev libgdbm-dev
```

Capture the package candidates, versions, simulation result, and any error.
The [Ubuntu APT manual](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html) defines `-s` as a no-action simulation.
Do not run `apt update`, `apt install`, a package hook, or an archived executable.
Soft-stop the clone after capture. Do not restart it under this decision.

## Limits and stop rules

Keep the clone at or below 34,359,738,368 allocated host bytes.
Keep both guest bundles and the ISO directory at or below 68,719,476,736 allocated host bytes together.
Keep at least 68,719,476,736 host bytes free at every stop check.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free guest disk bytes.
Permit at most two active hours and four elapsed hours for this attempt.
Allow zero new network transfer, zero package retrieval, and zero paid-host or metered API cost.
Stop on a changed source hash, unsafe sharing, failed package simulation, or resource limit.
Retain the clone after any failure. Do not repeat the start without another decision.

This metadata attempt cannot establish the full dependency closure by itself.
It can identify the guest's offline Ubuntu package candidates and missing metadata.
The later campaign needs a separate exact transfer, installation, qualification, and evaluation decision.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
