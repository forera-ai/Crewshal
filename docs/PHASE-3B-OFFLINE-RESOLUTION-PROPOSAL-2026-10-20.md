# Proposed Phase 3B offline package resolution capture

Date: 2026-10-20. Status: Approved for one attempt in the current Codex chat.
The owner replied, “Approve this exact capture.” The single admission ledger records this decision.
Entry revision: `078d6e7` on `codex/phase1-architecture`.
The [first snapshot](PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-COMPLETION-2026-10-20.md) passed a no-action APT simulation.
Its complete candidate table, resolved package list, and transfer sizes were not captured.
This proposal covers one later start of the same isolated clone to capture those facts.
It does not authorize retrieval, installation, archived tool execution, Linux tests, native turns, or evaluation.

## Exact guest and preflight

Use only `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Require a clean Git worktree and zero running VMs before starting.
Verify `docs/PHASE-3B-PRE-RESOLUTION-INPUTS-2026-10-20.json` and the frozen Phase 3A checker.
Check the original guest custody manifest and host allocations before and after use.
Require four configured CPUs, 17,408 MiB memory, and a disconnected network adapter.
Keep guest file sharing, root sharing, clipboard sharing, and drag and drop disabled.
Keep both historical guests, the ISO, and all extraction images unchanged.

Start the clone once with `vmrun -T fusion start DESTINATION_VMX gui`.
The owner enters the existing password in the VMware console.
Run only the following shell setup and read-only commands in that console:

```sh
set -o pipefail
uname -srm
getconf _NPROCESSORS_ONLN
free -b
df -B1 /var/tmp
set -- cmake ninja-build build-essential git binutils gnupg2 libc6-dev libcurl4-openssl-dev libedit2 libgcc-13-dev libncurses-dev libpython3-dev libsqlite3-0 libstdc++-13-dev libxml2-dev libz3-dev pkg-config tzdata zip unzip zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev uuid-dev tk-dev libgdbm-dev
apt-cache policy "$@" | awk '/^[^[:space:]].*:$/{package=$1} /^[[:space:]]*Candidate:/{print package,$2}'
apt-get -s --no-install-recommends install "$@" | grep '^Inst ' | more
apt-get --print-uris --assume-yes --no-install-recommends install "$@" | awk 'NF==4 && $3 ~ /^[0-9]+$/ {print $2,$3,$4}' | more
apt-get --print-uris --assume-yes --no-install-recommends install "$@" | awk 'NF==4 && $3 ~ /^[0-9]+$/ {count++;bytes+=$3; if ($3>max) max=$3} END {print "packages",count,"bytes",bytes,"largest",max}'
```

Capture every page of the candidate, simulation, and URI-size tables in the console.
The URI-size table prints package filenames, lengths, and hashes without the source URLs.
Record exact package counts, total bytes, largest object, versions, and any error.
The [Ubuntu APT manual](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html) defines `-s` as no action.
It states that `--print-uris` prints package URIs instead of fetching files.
Do not run `apt update`, retrieve a package, install a package, or execute an archived tool.
Soft-stop the clone after capture. Do not restart it under this decision.

## Limits and stop rules

Keep clone allocation at or below 34,359,738,368 host bytes.
Keep both guest bundles and the ISO at or below 68,719,476,736 allocated host bytes together.
Keep at least 68,719,476,736 host bytes free at every stop check.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free guest disk bytes.
Permit at most two active hours and four elapsed hours for this attempt.
Allow zero new network transfer, zero package retrieval, and zero paid-host or metered API cost.
Stop on changed source hashes, unsafe sharing, command failure, or a resource limit.
Retain the clone after any failure. Do not repeat the start without another decision.

This attempt can bind the offline Ubuntu candidate set and package size sum.
Repository dependency closure, installation, platform qualification, and evaluation need later exact decisions.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
