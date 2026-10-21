# Phase 3B local development boundary — 2026-10-21

## Decision and scope

The owner stopped guest checks and requested local development only.
ADR 0009 defers Linux tests until a consolidated campaign after source development.
This record closes the approved offline staging attempt without claiming Phase 3B acceptance.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest action.

## Observed result

The approved host transport build completed before this stop.
The transport ISO has 4,396,855,296 bytes and SHA-256 `9c9a85659d67c8954b5f5af84fe9acf5e8794a420614151051a93253fbdd3d55`.
Its `part-12.tar` has 524,001,280 bytes and SHA-256 `71c1c84c7cb48dbe232c1675705d2abf4aec71a2d593cfe02278156764648221`.
Its `part-4.tar` has 3,868,037,120 bytes and SHA-256 `185dc96a8721aee318e94ebd0294faf478de3625bb1844c70f5321315972bca3`.
The transport directory and ISO allocated 8,810,930,176 host bytes at build completion.
This was below the 12,884,901,888-byte host transport cap.

One isolated clone start occurred with network and sharing disconnected.
The guest preflight reported four CPUs, 17,760,563,200 RAM bytes, and 54,870,081,536 free `/var/tmp` bytes.
The guest verified the raw `/dev/sr0` ISO digest.
The CD mounted read-only with `nosuid,nodev,noexec`.
Mac UID 501 blocked ordinary guest reads until the CD was remounted read-only with `uid=1000,gid=1000`.
The destination `/var/tmp/crewshal-phase3b-tools-v1` was absent at the preflight.
The staging command was typed into the console, but the agent did not submit it.
The clone then appeared suspended. The command line may remain in its console.
Do not resume the clone or submit that line under this boundary.

The last host `du -sk` result for the clone was 23,349,716 KiB.
That exceeds the proposed 8,589,934,592-byte growth allowance when compared with the recorded 5,509,558,272-byte baseline.
Suspension can account for the increase, but its exact cause remains unverified.
The private original guest custody manifest was unavailable after the host restart.
Current guest staging state and current original guest hashes remain unverified.
No current guest or VM inspection followed the owner's stop instruction.

## Local verification

Environment: macOS Darwin 27.2.0 arm64, local checkout, Python virtual environment.
Base revision: `69a855015f7df21292376873ef279b0f739c8f42` on `codex/phase1-architecture`.
The following checks ran before the documentation update:

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_toolchain_transport tests.acceptance.test_phase3b_extract_source` | Seven tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_toolchain_transport.py scripts/phase3b_extract_source.py tests/acceptance/test_phase3b_toolchain_transport.py tests/acceptance/test_phase3b_extract_source.py` | All checks passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | 23 frozen artifacts and 768 planned units matched; execution flags remained false. |
| Local size and SHA-256 check of `docs/PHASE-3B-TOOLCHAIN-STAGING-APPROVED-INPUTS-2026-10-20.json` | All 249 files matched. |

No Linux test, archived tool execution, native turn, or evaluation row ran at this boundary.
No new network transfer occurred. Paid host cost and metered API cost were zero.
The historical archive charge remains 10,008,484,533 bytes.
The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.

## Acceptance limit

All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unobserved where the protocol requires observation.
The frozen Phase 3A package and historical custody records remain unchanged.
Phase 3B needs development corpus runs with complete accounting and preserved failures.
It also needs an amended protocol frozen before hold-out exposure.
Those checks depend on later Linux qualification and owner instruction under ADR 0009.
The [next prompt](PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-21.md) keeps this boundary closed.
