# Proposed Phase 3B Ubuntu package retrieval

Date: 2026-10-20. Status: approved for one exact attempt in the current Codex chat.
Entry revision: `2b6c939` on `codex/phase1-architecture`.
The owner replied, “Approve this exact retrieval.” The single admission ledger records this decision.
The [offline resolution capture](PHASE-3B-OFFLINE-RESOLUTION-COMPLETION-2026-10-20.md) found 101 package objects.
Their listed sizes total 111,245,650 bytes. The largest object is 18,708,214 bytes.
The current transfer balance is zero under the single admission ledger.
This proposal requests one separate download attempt in the isolated Ubuntu clone.
It does not request installation, archived tool execution, Linux tests, native turns, or evaluation.

## Requested owner decision

Approve one clone start and one APT download-only attempt for the thirty named packages below.
Approve temporary connection of the clone's network adapter after offline preflight.
Keep guest sharing, clipboard sharing, and drag and drop disabled.
Disconnect the adapter before the clone shuts down.
Add at most 167,772,160 bytes of conservative network charge for this attempt.
Keep the prior 10,008,484,533-byte conservative charge unchanged.
The resulting cumulative conservative ceiling is 10,176,256,693 bytes.
The listed APT bodies use 111,245,650 bytes of the new allowance.
Reserve 56,526,510 bytes for protocol overhead and any stopped partial body.
No original archive URL or consumed redirect is eligible for retry.

This proposal does not prove a hard network byte control.
The adapter can carry background guest traffic while connected.
Stop if guest network counters exceed the new 167,772,160-byte allowance.
Record any observed overrun as a failure, not as authorized extra transfer.
The owner should approve this observational limit only if that risk is acceptable.

## Exact guest and preflight

Use only `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Require a clean Git worktree and zero running VMs before starting.
Verify the exact input index and frozen Phase 3A checker.
Check all 31 original guest files against their private custody manifest.
Require four configured CPUs, 17,408 MiB memory, and disconnected network and sharing before the start.
Keep clone allocation at or below 34,359,738,368 host bytes.
Keep both guest bundles and the ISO at or below 68,719,476,736 allocated host bytes together.
Keep at least 68,719,476,736 host bytes free at every stop check.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free guest disk bytes.
The owner enters the existing password in the VMware console. No credential enters chat or Git.

Start the clone once with `vmrun -T fusion start DESTINATION_VMX gui`.
Run these offline commands before connecting the network:

```sh
set -o pipefail
uname -srm
getconf _NPROCESSORS_ONLN
free -b
df -B1 /var/tmp
set -- cmake ninja-build build-essential git binutils gnupg2 libc6-dev libcurl4-openssl-dev libedit2 libgcc-13-dev libncurses-dev libpython3-dev libsqlite3-0 libstdc++-13-dev libxml2-dev libz3-dev pkg-config tzdata zip unzip zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev uuid-dev tk-dev libgdbm-dev
apt-get --print-uris --assume-yes --no-install-recommends install "$@" | awk 'NF==4 && $3 ~ /^[0-9]+$/ {count++;bytes+=$3; if ($3>max) max=$3} END {print "packages",count,"bytes",bytes,"largest",max}'
apt-config dump | grep -E '(^APT::Update::Post-Invoke|^DPkg::(Pre|Post)-Invoke|^APT::Get::(Pre|Post)-Invoke)' || true
```

Stop before network connection unless the summary remains 101 objects, 111,245,650 bytes, and 18,708,214 largest bytes.
Stop if an APT or dpkg hook is configured or any resource floor fails.
The command above checks the common APT hook names. Treat an incomplete check as unknown and stop.
Do not run `apt update` or change the configured package sources.

After preflight, connect only the clone's VMware network adapter.
Record the guest interface receive and transmit counters before retrieval.
Run this one download-only command:

```sh
sudo apt-get -y -d -o Acquire::Retries=0 --no-install-recommends install "$@"
```

The owner enters a `sudo` password locally if the console requests one.
No package install, unpack, or configuration command is admitted.
After the command, disconnect the network adapter immediately.
Record the guest network counters, APT exit, package cache count, total file bytes, and largest file.
Verify each downloaded package against the guest's signed APT package metadata before later installation.
Do not infer package authenticity from the displayed MD5 alone.
Soft-stop the clone after readback. Do not restart it under this decision.

## Time, cost, and stop rules

Permit at most two active hours and four elapsed hours for this attempt.
Permit zero paid-host and zero metered API cost.
Permit zero native turns and zero evaluation rows.
Stop on changed candidates, missing packages, unsafe sharing, command error, custody drift, or resource limit.
Retain the clone and partial downloaded packages after a failure.
Do not retry a partial package or start the clone again without another decision.
Keep both historical guests, the ISO, archives, receipts, extraction images, fixed image, and frozen Phase 3A bytes unchanged.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
