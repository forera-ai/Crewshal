# Phase 3B guest capacity readback checkpoint

Date: 2026-10-18. Entry revision: `c421624961bed1f218bb4ca6c27b76032d316ed6`.
Branch: `codex/phase1-architecture`. Entry worktree: clean.
Environment: macOS 27.2 arm64, VMware Fusion 26.0.0, Ubuntu Server 24.04.5 arm64 guest.
Delivery revision: the commit containing this record. Package version: `0.15.7`.

## Result and stop gate

The owner unlocked the Mac and signed in to the separate Ubuntu guest without sharing the password.
The VMware toolbar showed its network, CD/DVD, and sharing devices disconnected.
The guest reported Linux `6.8.0-147-generic` on `aarch64` and Ubuntu 24.04.5 LTS.
It reported four online CPUs and 55,538,384,896 bytes available on `/var/tmp`.
The VM configuration still specifies 16,384 MiB RAM.
The guest reported 16,728,174,592 bytes of total memory, below 16 GiB by 451,694,592 bytes.
The approved proposal does not distinguish configured RAM from guest-visible total memory.
Treat the strict guest-visible capacity gate as unresolved until the new VM has sufficient readback.

`rtk` was absent inside the guest. Python was present at 3.12.3, below selected 3.12.15.
Node.js, Bun, Swift, .NET, CMake, Ninja, Codex CLI, and Claude Code CLI were absent.
The approved proposal says to stop when any selected tool is absent or different.
It also states that its preparation commands do not authorize package installation.
No tool was installed. No guest network transfer, dependency retrieval, native qualification, provider login, baseline, or calibration ran.
The guest remains powered on with its network adapter disconnected.
The previous 8 GiB VMware guest remains under owner control. The agent did not change it.

## Exact guest commands and results

RTK was absent in the guest, so the agent used raw commands for read-only admission checks.
VMware console input omitted initial characters twice. The agent recorded both failed commands.

```text
ue -srm                         -> ue: command not found
nam -srm                        -> Command 'nam' not found
uname -srm                      -> Linux 6.8.0-147-generic aarch64
getconf _NPROCESSORS_ONLN       -> 4
free -b                         -> Mem total 16728174592; available 16291524608; Swap total 4294963200
df -B1 /var/tmp                 -> /dev/nvme0n1p2; size 66205626368; used 7270957056; available 55538384896; 12% used
command -v rtk                  -> no path
cat /etc/os-release             -> Ubuntu 24.04.5 LTS; VERSION_ID=24.04; ID=ubuntu
command -v python3              -> /usr/bin/python3
command -v node                 -> no path
command -v bun                  -> no path
command -v swift                -> no path
command -v dotnet               -> no path
command -v cmake                -> no path
command -v ninja                -> no path
command -v codex                -> no path
command -v claude               -> no path
python3 --version               -> Python 3.12.3
```

The commands used the owner's authenticated guest console. No password entered the agent context.
The proposal's `rtk proxy` command form could not run because `rtk` was absent.
The host-side commands below verified repository state and the frozen source package:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
```

The host Git worktree was clean at entry. The checker reported 23 consistent artifacts and 768 planned units.
Its content digest remained `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.

## Costs, failures, and continuation

No selected coding-runtime turn or evaluation provider request ran during this checkpoint.
Measured evaluation billing remains unknown. No evaluation API-equivalent cost was measured.
Subscription quota debit for this chat remains unknown. No Jev request entered the approved batch.
The guest network stayed disconnected, so this checkpoint made no guest download.
The earlier installer security-update transfer remains unknown.
The ISO directory and VM bundle occupied 9,041,420,288 host bytes at the prior checkpoint.
That exceeds 8 GiB if the approved retained-data limit includes both infrastructure items.
Do not retrieve more batch data until transfer and retention accounting is bounded.

The next step requires a conforming guest and the exact selected executables.
Supply them outside this batch or approve a prospective preparation amendment with pinned sources, digests, and costs.
That amendment must also settle the RAM readback and retention interpretation before dependent operations.
The existing approval for qualification and batch limits remains in force. Do not request it again.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Operational admission, Phase 3B calibration, and Phase 3C remain closed.
