# Proposed Phase 3B APT retry after host storage recovery

Date: 2026-10-20. Status: proposed, not approved.
Entry revision: `901b8ffff00b4f2e67b36515cee05b507aaaaf8a` on `codex/phase1-architecture`.
The [isolated attempt](PHASE-3B-APT-ISOLATION-STORAGE-STOP-2026-10-20.md) stopped before network connection.
The later host readback showed 38,627,844,096 free bytes on `/Volumes/X10Pro`.
The approved 64 GiB floor needs 68,719,476,736 free bytes.
The deficit was 30,091,632,640 bytes at that readback.
The owner must restore space without deleting Crewshal custody artifacts or unrelated files through this proposal.

## Exact requested decision

After the host floor passes, approve one start of only this clone:
`/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Approve one temporary connection of only its network adapter after offline checks and action-time confirmation.
Approve one download-only APT command with the same 30 package names and isolated configuration.
The [earlier approved proposal](PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md) supplies the exact package list and command.
Do not install packages or run archived tools, Linux tests, native turns, or evaluation rows.

## Preconditions and limits

Require a clean worktree, exact input index, zero running guests, and passing frozen Phase 3A checker.
Recheck all 31 original guest file hashes against their private manifest.
Confirm the clone is off with four CPUs, 17,408 MiB memory, disconnected network, and disabled sharing.
Require at least 68,719,476,736 host bytes free before start and before network connection.
Stop immediately if that floor fails. Do not count promised cleanup as free space.
Keep the clone below 34,359,738,368 allocated host bytes.
Keep source guest, ISO directory, and clone together below 68,719,476,736 allocated bytes.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free `/var/tmp` bytes.
Keep the same 101 package objects, 111,245,650 listed bytes, and 18,708,214-byte largest object.
Require no effective `Invoke` or `Hooks` keys with the isolated APT configuration.
Keep guest sharing, clipboard integration, and drag and drop disabled.

Cap new conservative network charge at 167,772,160 bytes, including overhead and stopped partial bodies.
The historical charge remains 10,008,484,533 bytes.
The cumulative conservative ceiling stays 10,176,256,693 bytes.
The network cap is observational; background guest traffic can use the connected adapter.
Record interface counters before and after retrieval. Stop on an overrun and record it as a failure.
Permit at most two active hours and four elapsed hours. Permit zero paid-host and metered API cost.
Retain partial downloads after failure. Do not retry or restart under this decision.

## One attempt

Start the clone once with `vmrun -T fusion start DESTINATION_VMX gui` after the preflight passes.
The owner signs in locally. Keep credentials out of commands, files, and Git.
Repeat the offline guest capacity, isolated APT hook, and exact package-list checks.
Check the host free-space floor again before any network connection.
Ask for action-time confirmation before connecting the clone's adapter in VMware Fusion.
Record receive and transmit counters, then run the earlier proposal's exact download-only command once.
Disconnect the adapter immediately after that command or a stop condition.
Record APT status, network counters, package count, total bytes, largest file, and partial output.
Verify downloaded packages against signed guest APT metadata before any later installation decision.
Soft-stop the clone. Recheck guest custody, host limits, disabled network, and zero running guests.

## Preserved scope

Keep both historical guests, the ISO, all sixteen archives, both receipts, both extraction images, and the fixed image intact.
Do not request an archive body or retry any consumed archive URL.
Keep original URLs, object caps, the 2,232,012,187-byte stage cap, and both receipt histories unchanged.
Keep installation, archived tool execution, Linux qualification, native turns, and evaluation closed.
Keep installed executable hashes, effective commands, providers, and B1 conformance null until observed.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
