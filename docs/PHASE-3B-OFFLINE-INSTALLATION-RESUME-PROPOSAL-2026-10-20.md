# Proposed Phase 3B offline installation resume

Date: 2026-10-20. Status: proposed; no resume or installation is admitted.
The [stop record](PHASE-3B-OFFLINE-INSTALLATION-SUSPEND-2026-10-20.md) closes the approved start.
VMware suspended the separate clone before the agent issued an installation command.
The existing approval bars a restart. This proposal requests one new, exact decision.

## Exact owner decision requested

Approve one resume of the saved state in `/Volumes/X10Pro/Crewshal-Phase3B-Consolidated-20261020.vmwarevm/Crewshal Phase 3B Consolidated.vmx`.
Approve one offline APT installation, only after every original preflight passes again.
The command may run Ubuntu package maintainer scripts as root and change only this separate clone.
The agent may finish the existing guest sign-in using the owner-provided credentials.
Keep credentials out of commands, files, Git, and reports.
Keep the clone network adapter and sharing disconnected.
Allow zero network transfer, package retrieval, archived tool execution, Linux tests, native turns, or evaluation.
Stop after one installation command or any failed preflight. Do not retry or resume again under this decision.

## Bounds and checks

Require a clean worktree, matching exact input index, and passing frozen Phase 3A checker.
Require all 31 original guest files to match the private custody manifest.
Require four configured CPUs, 17,408 MiB memory, disconnected network, and disabled guest sharing.
Require at least 68,719,476,736 host bytes free before resume and at shutdown.
Keep clone allocation below 34,359,738,368 bytes.
Keep source guest, ISO, and clone allocation together below 68,719,476,736 bytes.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free `/var/tmp` bytes.
Limit the resumed attempt to two active hours and four elapsed hours.

After resume, read back the original proposal's isolated APT configuration and empty parts directory.
Require no effective APT or dpkg executable hooks under `APT_CONFIG`.
Require exactly 101 cached packages, 111,245,650 bytes, and zero partial cache entries.
Match all cached hashes to guest APT candidate metadata.
Run the original offline simulation with `--no-download` and the same `APT_CONFIG`.
Require the same 101 package objects, candidates, and no removal or download.
Stop if any check or resource floor differs.

Run the original proposal's exact installation command once with the adapter disconnected.
Record command output, exit status, installed versions, package count, storage, and errors.
Preserve any partial state after failure. Soft-stop the clone if possible.
Then check zero running guests, network isolation, host limits, and all 31 source hashes.

Preserve historical guests, ISO, sixteen archives, receipts, extraction images, fixed image, and frozen Phase 3A bytes.
Keep the 10,008,484,533-byte historical archive charge and 116,542,541-byte package charge intact.
The cumulative conservative charge remains 10,125,027,074 bytes.
Keep executable hashes, effective commands, providers, and B1 conformance null until observed.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
