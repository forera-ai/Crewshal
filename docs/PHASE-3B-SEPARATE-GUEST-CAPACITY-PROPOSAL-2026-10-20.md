# Proposed Phase 3B separate-guest capacity attempt

Date: 2026-10-20. Status: Draft. No guest action is admitted.
This proposal uses the separate-guest planning assumption while the owner choice remains pending.
It would preserve both historical VMware bundles and their suspended states.
It covers one full clone attempt of the Phase 3B guest and one capacity check on the clone.
It does not admit package retrieval, installation, archived tool execution, Linux qualification tests, native turns, or evaluation rows.

## Exact source and destination

Source bundle: `/Volumes/X10Pro/Internal-Offload-2026-09-15/Moved/Virtual Machines.localized/Crewshal Phase 3B Ubuntu arm64.vmwarevm`.
Source VMX: `Crewshal Phase 3B Ubuntu arm64.vmx` inside that bundle.
Destination bundle: `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm`.
Destination VMX: `Crewshal Phase 3B Consolidated.vmx` inside that bundle.
The destination must be absent before the clone. The source must have zero running processes.
Do not modify or remove either historical guest, ISO, receipt, archive, or extraction image.

The current source VM has four CPUs, 16,384 MiB configured memory, and one suspended-state file.
Its bundle uses 21,926,846,464 allocated host bytes. The ISO directory uses 3,825,520,640 bytes.
Their current combined allocation is 25,752,367,104 bytes.
The host had 143,998,521,344 free bytes after extraction.
The selected ISO matched 3,825,512,448 bytes and SHA-256 `f12484464c7d4d73e2167e0a7dbda1e669f8fae9bcf778dc0944937034b320cb`.
The clone must retain a sparse 64 GiB guest disk and four CPUs.

## Proposed attempt and limits

Permit one `vmrun -T fusion clone SOURCE_VMX DESTINATION_VMX full` attempt.
The exact proposed clone command is:

```sh
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' -T fusion clone '/Volumes/X10Pro/Internal-Offload-2026-09-15/Moved/Virtual Machines.localized/Crewshal Phase 3B Ubuntu arm64.vmwarevm/Crewshal Phase 3B Ubuntu arm64.vmx' '/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx' full
```

Before that command, verify the destination absence, source suspension, source file hashes, and current host space.
After it, compare source file hashes again and inspect the clone's network and sharing settings before any start.
Cap the new bundle at 34,359,738,368 allocated host bytes.
Cap the source bundle, ISO directory, and new bundle together at 68,719,476,736 allocated host bytes.
Keep at least 68,719,476,736 host bytes free at each stop check.
Permit no new network transfer during this attempt. Keep the clone's network disconnected before its first start.
Do not enable shared folders, clipboard sharing, drag and drop, or host file mounts.
Permit one clone resume solely to shut it down in an orderly way if the copied VM is suspended.
After shutdown, set only the clone to 17,408 MiB configured memory.
Permit one later clone start and read-only capacity commands: `uname -srm`, `cat /etc/os-release`, `getconf _NPROCESSORS_ONLN`, `free -b`, and `df -B1 /var/tmp`.
Require Linux arm64, at least four CPUs, at least 17,179,869,184 guest-visible memory bytes, and at least 42,949,672,960 free guest disk bytes.
Allow at most two active hours and four elapsed hours. Keep paid-host and metered API cost at USD 0.
Stop on failed clone, unsafe sharing, unavailable console access, missing capacity, or exceeded host bounds.
Retain a partial clone after failure. Do not retry, rename, or delete it without a new decision.

## Review and remaining gates

The owner must explicitly approve this changed guest and VM scope before any clone or start.
This decision would replace the earlier zero guest and VM growth rule only for the bounded clone attempt.
It would not approve the wider Phase 3B campaign or change transfer and retained-data ceilings.
The actual clone behavior with a suspended source is unverified. A refusal would end this attempt.
Exact package snapshots, installed tool identities, provider commands, and baseline conformance still need later admission.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
