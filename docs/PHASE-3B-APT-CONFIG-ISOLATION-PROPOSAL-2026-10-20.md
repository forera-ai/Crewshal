# Proposed Phase 3B package retrieval with isolated APT configuration

Date: 2026-10-20. Status: approved for one exact attempt in the current Codex chat.
Entry revision: `4699791448ae196a025ee5148119714d464d3877` on `codex/phase1-architecture`.
The owner replied, “Approve this exact attempt.” The single admission ledger records this decision.
The [first approved attempt](PHASE-3B-PACKAGE-RETRIEVAL-HOOK-STOP-2026-10-20.md) stopped before network connection.
The guest's default APT configuration contains update, dpkg, and apt frontend hooks.
The first attempt used no package transfer allowance.
This proposal requests one separate clone start and one download-only APT attempt.
It does not request installation, archived tool execution, Linux tests, native turns, or evaluation.

## Requested decision and limits

Approve one start of only `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Approve temporary connection of only this clone's network adapter after offline preflight.
Keep all guest sharing, clipboard integration, and drag and drop disabled.
Approve one download-only APT command with the thirty names from the [first proposal](PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md).
Use no more than 167,772,160 bytes of new conservative network charge.
The 101 listed package bodies total 111,245,650 bytes; reserve 56,526,510 bytes for overhead and stopped partial bodies.
Keep the historical 10,008,484,533-byte charge unchanged.
The cumulative conservative ceiling stays 10,176,256,693 bytes.
The network limit is observational. Guest background traffic can use the connected adapter.
Stop if interface counters exceed the allowance, and record any overrun as a failure.
Keep the 32 GiB clone cap, 64 GiB combined guest-and-ISO cap, and 64 GiB host free floor.
Keep at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free guest disk bytes.
Permit at most two active hours and four elapsed hours. Permit zero paid-host and metered API cost.
Retain partial downloads after a failure. Do not retry or restart under this decision.

## Exact offline preflight

Require a clean Git worktree, zero running guests, and matching exact input index.
Run the frozen Phase 3A checker. Match all 31 original guest files to their private custody manifest.
Verify clone and host storage limits, four CPUs, 17,408 MiB, disconnected network, and disabled sharing.
Start the clone once with `vmrun -T fusion start DESTINATION_VMX gui`.
The owner signs in locally. Keep credentials out of chat commands and Git.
Run `uname -srm`, `getconf _NPROCESSORS_ONLN`, `free -b`, and `df -B1 /var/tmp`.
Set the exact thirty package arguments shown in the first proposal.

APT reads configuration files before command-line overrides, so a late `-o` option cannot prove isolation.
The [Ubuntu APT configuration manual](https://manpages.ubuntu.com/manpages/noble/man5/apt.conf.5.html) defines startup order.
Require two absent paths before creation.
Create an empty `/var/tmp/crewshal-phase3b-empty-aptconf.d` directory with mode `0700`.
Create only `/var/tmp/crewshal-phase3b-apt-nohooks.conf` with these two lines:

```text
Dir::Etc::parts "/var/tmp/crewshal-phase3b-empty-aptconf.d";
Dir::Etc::main "/dev/null";
```

Set `umask 077` before creation. Require the directory to be empty.
Read back the file and require exactly those two lines.
Use these exact creation commands after both absence checks:

```sh
umask 077
mkdir -m 700 /var/tmp/crewshal-phase3b-empty-aptconf.d
printf '%s\n' 'Dir::Etc::parts "/var/tmp/crewshal-phase3b-empty-aptconf.d";' 'Dir::Etc::main "/dev/null";' > /var/tmp/crewshal-phase3b-apt-nohooks.conf
```

Use `APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf` for every later APT command in this attempt.
First run `APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-config dump` and inspect all `Invoke` and `Hooks` keys.
Stop if any executable hook remains or if the configuration query fails.
Then run the exact `apt-get --print-uris` summary with the same startup configuration and package arguments.
Require 101 package objects, 111,245,650 listed bytes, and an 18,708,214-byte largest object.
Stop if any source or package candidate changes, or if either guest floor fails.
Do not run `apt update` or edit the guest's APT configuration files.

## One network and retrieval sequence

After the offline checks pass, connect only the clone's VMware network adapter.
Record the interface name and receive/transmit byte counters before retrieval.
Run once:

```sh
sudo env APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-get -y -d -o Acquire::Retries=0 --no-install-recommends install "$@"
```

The owner enters a sudo password locally if requested.
Disconnect the adapter immediately after the command or on a stop condition.
Record the APT exit status, interface counters, downloaded package count, total bytes, and largest file.
Verify downloaded packages against signed guest APT metadata before later installation.
Soft-stop the clone, then check source custody, host limits, disabled network, and zero running guests.
Stop on command error, unexpected hook, unsafe sharing, changed candidates, missing package, or resource limit.
Do not retry a partial package under this decision.

## Preserved boundaries

Keep both historical guests, the ISO, all sixteen archives, both receipts, extraction images, and fixed image intact.
Do not request an archive body or retry a consumed archive URL.
Preserve the original URLs, object caps, stage cap, and both receipt histories.
Keep installation, archived tool execution, Linux qualification, native turns, and evaluation closed.
Keep executable hashes, effective commands, providers, and B1 conformance null until observed.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
