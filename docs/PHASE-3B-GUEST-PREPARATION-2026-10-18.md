# Phase 3B guest preparation record

Date: 2026-10-18. Entry revision: `90e7aa11c7c6340bb68d7f9bec1084426b0a5163`.
Branch: `codex/phase1-architecture`. Entry worktree: clean.
Environment: macOS 27.2 arm64, VMware Fusion 26.0.0, `vmrun` 1.17.0.25388279.
Delivery revision: the commit containing this record.

## Authority and scope

The owner approved qualification resumption and the exact [Phase 3B limits](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md).
The owner accepted unknown subscription quota debit. These decisions remain in force.
The previous 8 GiB VMware guest remains under the owner's control.
The owner instructed us to leave its state management to them.
`vmrun list` first showed no running guests.
It later showed the previous guest running after Fusion opened, without an explicit Resume selection by the agent.
The owner then took responsibility for that guest. A later list showed only the new guest running.

## New guest preparation

VMware Fusion created a separate Ubuntu 64-bit Arm guest with four virtual CPUs, 16,384 MiB RAM, and a 64 GB sparse NVMe disk.
The guest bundle has `0700` permissions. Its configuration has `0600` permissions.
No shared-folder entry remains in its configuration.
HGFS, clipboard copy, clipboard paste, and drag-and-drop integration are disabled.
The guest uses a separately downloaded Ubuntu Server 24.04.5 arm64 ISO.
The ISO came from the [official Ubuntu release](https://cdimage.ubuntu.com/ubuntu/releases/24.04.5/release/).
Its 3,825,512,448 bytes matched the official SHA-256 value `f12484464c7d4d73e2167e0a7dbda1e669f8fae9bcf778dc0944937034b320cb`.
The private ISO directory has `0700` permissions. The ISO and checksum file have `0600` permissions.

The new guest booted the Ubuntu installer. The disk screen showed one 64.000G VMware virtual NVMe disk.
The guided layout assigns 1.049G to EFI and 62.948G to an ext4 root partition.
The root partition uses the whole remaining disk without LVM.
The installer reached Profile configuration. The owner must enter and submit the new account credentials.
The computer-use credential rule requires this handoff. No guest capacity readback has passed yet.
The account form showed `Password must be set` and `Passwords do not match` after partial owner entry.
The agent did not enter, read, or submit a new credential.

## Commands and results

The following commands ran from `/Volumes/X10Pro/Crewshal`.
`PRIVATE_PLATFORM_ROOT` and `PRIVATE_VMX` name local paths outside Git.

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' list
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' -v
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch
rtk proxy curl --proto '=https' --tlsv1.2 --fail --location --retry 0 --max-time 1800 --output "$PRIVATE_PLATFORM_ROOT/ubuntu-24.04.5-live-server-arm64.iso" 'https://cdimage.ubuntu.com/ubuntu/releases/24.04.5/release/ubuntu-24.04.5-live-server-arm64.iso'
rtk proxy shasum -a 256 "$PRIVATE_PLATFORM_ROOT/ubuntu-24.04.5-live-server-arm64.iso"
rtk proxy chmod 600 "$PRIVATE_PLATFORM_ROOT/ubuntu-24.04.5-live-server-arm64.iso" "$PRIVATE_PLATFORM_ROOT/SHA256SUMS"
rtk proxy stat -f '%N %Sp %z' "$PRIVATE_PLATFORM_ROOT" "$PRIVATE_PLATFORM_ROOT/ubuntu-24.04.5-live-server-arm64.iso" "$PRIVATE_PLATFORM_ROOT/SHA256SUMS"
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' start "$PRIVATE_VMX" gui
rtk proxy df -k /Volumes/X10Pro
```

The frozen checker passed with 23 artifacts and 768 planned units.
The focused offline suite passed 108 tests in 7.961 seconds.
The 126 prior continuation files matched their byte counts and SHA-256 digests.
The prior Git worktree was clean at `90e7aa1`.
`vmrun -v` returned exit 255 with `Invalid argument: -v` and printed version `1.17.0.25388279`.
The host volume reported 166,628,064 KiB available after ISO retrieval.
The official ISO download consumed 3,825,512,448 bytes of the approved 8 GiB transfer limit.
The checksum file consumed another 5,694 bytes.
The approved 8 GiB transfer limit has 4,764,416,450 bytes remaining after these two downloads.

At the publication boundary, the checker again passed with digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The focused suite passed 108 tests in 7.631 seconds.
The new continuation index matched 128 files. Both package version fields reported `0.15.5`.
`rtk proxy git diff --check` passed.

## Open gates and accounting

Guest OS, CPU, RAM, free disk, toolchains, native controls, provider identities, and baseline conformance remain unverified.
The new guest cannot pass capacity admission until the owner completes the account form and the installer finishes.
No development row, coding-runtime submission, evaluation provider request, calibration, or sealed evaluation ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Measured provider billing remains unknown. No evaluation API-equivalent estimate was incurred.
Subscription quota debit for this chat remains unknown. No Jev request entered the approved batch.
No paid host was used. The guest ISO is the only Phase 3B download so far.
Operational admission and Phase 3C remain closed.
