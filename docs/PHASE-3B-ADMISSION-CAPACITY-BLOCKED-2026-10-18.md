# Phase 3B admission capacity checkpoint

Date: 2026-10-18. Entry revision: `1bdb65f0ed2b24727d737d547499fd0ad7e7da3d`.
Branch: `codex/phase1-architecture`. Entry worktree: clean.
Environment: macOS 27.2 arm64, CPython 3.12.15, RTK available.
Delivery revision: the commit containing this record. Package version: `0.15.4`.

## Owner authority and result

The owner answered "Yes, resume qualification" to the separate platform and live qualification request.
The owner answered "Approve limits and unknown quota" to the exact [Phase 3B proposal](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md).
The approved batch permits USD 0 metered billing, USD 0 paid hosts, and at most 256 submissions per selected runtime.
It has a USD 200 API-equivalent planning limit, 8 GiB download limit, and 8 GiB retained data limit.
The owner accepted that actual subscription quota debit has no proved hard ceiling.
These approvals do not establish any required qualification observation.

The selected local VMware Ubuntu VM was powered off and configured with 8 GiB RAM and four virtual CPUs.
The proposal requires at least 16 GiB RAM before preparation. The session stopped before VM startup.
The guest's current OS, free disk, toolchains, native controls, provider identities, and baseline conformance remain unobserved.
The smallest missing capability is a new, nonshared Linux arm64 guest with at least 16 GiB RAM.
It must also show four available CPUs, 40 GiB free disk, and enforce the proposed limits.
Do not treat the saved VM state as a fresh environment or change it without a separate explicit instruction.

Phase 3B calibration remains incomplete. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. Operational admission and Phase 3C stay closed.

## Read-only commands and results

The following commands ran from `/Volumes/X10Pro/Crewshal`:

```sh
rtk proxy git status --short --branch
rtk proxy git log -3 --oneline --decorate
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch
rtk proxy .venv/bin/python -c 'import crewshal,platform,sys; print({"version":crewshal.__version__,"python":sys.version.split()[0],"platform":platform.platform(),"machine":platform.machine()})'
rtk proxy '/Applications/VMware Fusion.app/Contents/Public/vmrun' list
rtk proxy sysctl -n hw.memsize
rtk proxy df -B1 /Volumes/X10Pro
rtk proxy df -k /Volumes/X10Pro
```

Before publication edits, Git reported a clean worktree at `1bdb65f`, equal to its remote branch tip.
The frozen checker returned `consistent-frozen-source-package`, 23 artifacts, 768 planned units, and both execution flags false.
The focused suite passed 108 tests in 7.173 seconds.
The environment command reported version `0.15.3`, Python `3.12.15`, macOS `27.2`, and arm64 before the version bump.
The prior exact continuation index matched 124 files with no byte or SHA-256 mismatch.
After publication edits, the checker passed with the same frozen content digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The focused suite passed 108 tests in 7.300 seconds. The new continuation index matched 126 files.
Both package version fields reported `0.15.4`, and `rtk proxy git diff --check` passed.
`vmrun list` reported `Total running VMs: 0`.
The selected VM configuration recorded `memsize = "8192"` and `numvcpus = "4"`.
The VM also has a saved-state reference; it is not evidence of a fresh guest.
The local VM configuration path remains outside Git. Its private path is not a reproducible public input.
The host reported 103079215104 bytes of physical RAM. This does not change the guest's 8 GiB setting.
The macOS `df -B1` command failed with `df: invalid option -- B`.
The successful `df -k` command reported 171480104 KiB available on `/Volumes/X10Pro`.
No command read the guest's current free disk.

The codebase graph project was `Volumes-X10Pro-Crewshal` and its status was ready at generation `2026-10-18T10:43:03Z`.
Coverage reported no recorded issue for the checker, four focused test files, and `src/crewshal/__init__.py`.
This best-effort signal does not prove complete indexing.
It reported partial parsing of `src/crewshal/bootstrap_helper.c` at lines 75, 77, and 89.
No structural claim relied on those ranges.

## Costs and limits

This session made zero evaluation provider requests, coding-runtime turns, credential accesses, dependency preparations, and VM startups.
This count excludes the agent session's own model use, which remains unknown.
Measured billing was not accessed and remains unknown. API-equivalent evaluation cost was not measured.
Subscription quota debit for this chat remains unknown. No Jev request entered the batch.
No paid host was used. No source archive or sealed task content was opened for calibration.

After a qualified guest becomes available, continue under the same approved limits with the [next prompt](PHASE-3B-ADMISSION-CAPACITY-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-ADMISSION-CAPACITY-INPUTS-2026-10-18.json).
