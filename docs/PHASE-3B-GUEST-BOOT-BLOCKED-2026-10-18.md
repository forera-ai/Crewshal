# Phase 3B guest boot and login checkpoint

Date: 2026-10-18. Entry revision: `31b7e8acfa603eff20d35fb22b012f964701765d`.
Branch: `codex/phase1-architecture`. Entry worktree: clean.
Environment: macOS 27.2 arm64, VMware Fusion 26.0.0, Ubuntu Server 24.04.5 arm64 guest.
Delivery revision: the commit containing this record. Package version: `0.15.6`.

## Result and boundary

The owner completed the new Ubuntu account profile without sharing its password.
The installer reached `Installation complete!` and displayed its security-update stage.
The agent disconnected the new guest's VMware network adapter to stop further unmeasured transfer.
The agent disconnected its installation media and selected `Reboot Now`.
The guest requested removal of the installation medium and an Enter key press.
The installation medium was already disconnected. Enter continued the reboot.
The disconnected network caused a boot wait. Ubuntu then reached the `codex-test login:` prompt.
Cloud-init reported completion after the login prompt appeared.
The owner must sign in through VMware Fusion before guest capacity readback can run.
The agent asked the owner to sign in without sending the password.
The owner had not completed that sign-in at this checkpoint.
The Mac later locked, and computer use could not inspect VMware until the owner unlocks it.
The previous 8 GiB VMware guest remains under the owner's control. The agent did not change it.

The new guest's configuration still specifies four virtual CPUs and 16,384 MiB RAM.
It specifies Ubuntu arm64 and disables HGFS, clipboard copy and paste, and drag-and-drop.
The VMware toolbar showed its network, CD/DVD, and sharing devices disconnected.
The installed guest's CPU availability, memory readback, free disk, and resource controls remain unverified.
No toolchain, native control, provider identity, dependency snapshot, B1 script, baseline, or calibration passed admission.
Operational execution remains closed. All 192 development rows remain planned and all 576 sealed rows remain unexposed.

## Commands and results

The following commands ran from `/Volumes/X10Pro/Crewshal`:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy rg -n '^(memsize|numvcpus|guestOS|ethernet0\.present|ethernet0\.connectionType|isolation\.tools\.(copy|paste|dnd|hgfs)\.disable|sharedFolder|sched\.mem)' "$PRIVATE_VMX"
rtk proxy du -sk "$PRIVATE_VM_BUNDLE" "$PRIVATE_PLATFORM_ROOT"
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' list
rtk proxy df -k /Volumes/X10Pro
```

`PRIVATE_VMX`, `PRIVATE_VM_BUNDLE`, and `PRIVATE_PLATFORM_ROOT` are local paths outside Git.
The Git worktree was clean at entry. The frozen checker reported 23 consistent artifacts and 768 planned units.
The VM configuration reported `numvcpus = "4"`, `memsize = "16384"`, and `guestOS = "arm-ubuntu-64"`.
It reported all four guest-sharing disable flags as `TRUE`.
`vmrun list` showed only the new guest running at this check.
The host volume had 162,590,784 KiB available. Guest free disk remains unknown.
The host allocated 5,093,120 KiB for the new VM bundle and 3,736,392 KiB for the ISO directory.
Their combined host allocation was 9,041,420,288 bytes at this check.
This exceeds 8 GiB if the approved retained-data limit includes both infrastructure items.
The proposal does not expressly define that inclusion. Do not retrieve or retain more batch data until accounting is resolved.

## Costs, failures, and unknowns

The official ISO and checksum files consumed 3,825,518,142 known download bytes before this session.
The installer displayed a security-update download stage before the network was disconnected.
Its transferred byte count is unknown. The remaining 8 GiB transfer allowance cannot be verified.
No selected coding-runtime turn, evaluation provider request, or paid host ran in this session.
Measured evaluation billing remains unknown. The evaluation API-equivalent estimate remains unmeasured.
Subscription quota debit for this chat remains unknown. No Jev request entered the approved batch.
No guest capacity or tool check ran because the guest shell was not authenticated.
The network boot wait completed. No installation failure was observed.
Do not claim Phase 3B admission or calibration from this checkpoint.
