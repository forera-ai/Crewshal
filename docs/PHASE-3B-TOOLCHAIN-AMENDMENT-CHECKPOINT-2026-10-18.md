# Phase 3B toolchain amendment checkpoint

Date: 2026-10-18. Entry revision: `7a592dd6d1f47fc98651b44e18edb05feab7c7b7`.
Branch: `codex/phase1-architecture`. Entry worktree: clean. Package version at entry: `0.15.8`.
Status: **blocked preparation amendment; no installation or retrieval authority**.

## Result

The owner authorized continuation of the Phase 3B amendment in this session.
The approved qualification resumption and Phase 3B batch limits remain in force.
The proposed RAM threshold and storage interpretation still require separate owner approval.
The prior installer transfer lacks an exact upper bound in the inspected records.
The artifact manifest still lacks exact archive bytes, extraction bounds, dependencies, and executable hashes.
No guest setting, network connection, tool installation, provider request, calibration, or sealed task changed.

## Transfer and storage ledger

The approved transfer limit is 8,589,934,592 bytes.
The ISO and checksum consumed 3,825,518,142 known bytes.
Their difference is 4,764,416,450 bytes before the installer transfer.
The installer log shows rounded `Fetched 393 kB` and `Fetched 292 MB` summaries.
Those summaries cannot bound retries, metadata, interrupted transfers, or other installer traffic.
Charge the unknown installer amount against the full remaining allowance until exact evidence or a new owner-approved limit exists.
This conservative charge leaves zero bytes available for new retrieval.

The previous simultaneous VM-plus-ISO allocation was 9,041,420,288 host bytes.
It exceeded the approved 8 GiB retained-data ceiling by 451,485,696 bytes if both objects count.
The host now reports 5,144,576 KiB, or 5,268,045,824 bytes, for the new VM bundle alone.
The ISO directory was not remeasured in this session, so no current combined allocation is claimed.
The proposed separate 40 GiB infrastructure ceiling is still an unapproved change of scope.

## Official artifact research

This table adds source metadata to the [earlier draft](PHASE-3B-TOOLCHAIN-PREPARATION-BLOCKED-2026-10-18.md).
It does not admit any artifact for installation.

| Artifact | Verified metadata | Remaining gate |
| --- | --- | --- |
| RTK 0.51.0 Linux arm64 | The [official release assets](https://github.com/rtk-ai/rtk/releases/expanded_assets/v0.51.0) publish SHA-256 `8d6d1aad9e69b42481eda7039507d1f7ee93698f87713cecd873d287c1931632`. | GitHub rounds the size to 4.28 MB. Exact bytes, safe member list, extracted executable hash, and license result remain open. |
| Bun 1.2.2 Linux arm64 | The [official release assets](https://github.com/oven-sh/bun/releases/expanded_assets/bun-v1.2.2) include `bun-linux-aarch64.zip`, `SHASUMS256.txt`, and its signature. | Exact bytes, verified signed checksum contents, safe member list, extracted executable hash, and license result remain open. |
| Swift 6.0.3 Ubuntu 24.04 arm64 | The [official release page](https://www.swift.org/install/linux/ubuntu/24_04/) links the exact tarball and signature. The [tarball instructions](https://www.swift.org/install/linux/tarball/) list direct Ubuntu 24.04 prerequisites. | Exact bytes, verified signature and key, safe member list, extraction size, transitive package set, and license result remain open. |
| .NET SDK 9.0.100 Linux arm64 | The [official release metadata](https://github.com/dotnet/core/blob/main/release-notes/9.0/9.0.0/release.json) publishes the archive URL and SHA-512 `684450e6d1f7c711fffdbf32a2b86a932d17a51f4742bd27a4289e319c5b24f6743553fc7e0ad1c7163e448ed5c40cd1ecf4198b2e681acc4622d8e6193a5cf2`. | Exact bytes, safe member list, extraction size, net8.0 packs, executable hash, and license result remain open. |

The .NET archive URL is `https://download.visualstudio.microsoft.com/download/pr/6f79d99b-dc38-4c44-a549-32329419bb9f/a411ec38fb374e3a4676647b236ba021/dotnet-sdk-9.0.100-linux-arm64.tar.gz`.
The selected `dotnet-1` tasks require `net8.0` and `net9.0` checks.
The [Microsoft release notes](https://github.com/dotnet/core/blob/main/release-notes/9.0/9.0.0/9.0.0.md) say SDK 9.0.100 includes the matching 9.0 runtime.
The net8.0 targeting and runtime dependencies still need exact selection.

The official Swift Ubuntu 24.04 direct prerequisites are `binutils`, `git`, `gnupg2`, `libc6-dev`, `libcurl4-openssl-dev`, `libedit2`, `libgcc-13-dev`, `libncurses-dev`, `libpython3-dev`, `libsqlite3-0`, `libstdc++-13-dev`, `libxml2-dev`, `libz3-dev`, `pkg-config`, `tzdata`, `zip`, `unzip`, and `zlib1g-dev`.
Their exact Ubuntu versions, digests, transfer bytes, and transitive dependencies remain unresolved.
The earlier draft retains the verified CPython and Node.js digests.
It also retains unresolved CMake, Ninja, Codex CLI, Claude Code CLI, and repository dependencies.

## Guest inspection limit

VMware Fusion displayed the existing signed-in Ubuntu console and a disconnected network adapter.
An attempted read-only installer-log query did not produce a reliable new result through the console input path.
A later read-only `ls /var/log/apt` input also produced no reliable result.
No exact transfer counter was observed. No guest file or setting changed.
The console failure is a control limitation, not proof that the logs lack more detail.

## Verification and cost

The host ran these read-only commands on macOS arm64 from the entry revision:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy .venv/bin/python -c 'import hashlib,json,pathlib; p=json.loads(pathlib.Path("docs/PHASE-3B-TOOLCHAIN-PREPARATION-INPUTS-2026-10-18.json").read_text()); bad=[x["path"] for x in p["files"] if (len((b:=pathlib.Path(x["path"]).read_bytes()))!=x["bytes"] or hashlib.sha256(b).hexdigest()!=x["sha256"])]; print(len(p["files"]),"files; mismatches:",bad)'
rtk proxy du -sk "$PRIVATE_VM_BUNDLE"
```

Git was clean. The 135 starting file hashes matched.
The private VM path remains outside Git.
The frozen checker returned 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
These checks do not qualify the guest or run a coding runtime.
No selected runtime turn, evaluation provider request, paid host, or Jev call ran.
Measured billing and API-equivalent evaluation cost have no new observation.
Subscription quota debit for this chat remains unknown.

## Decision and continuation

The reviewable proposed RAM rule requires at least 17,179,869,184 guest-visible total bytes from `free -b`.
Increasing only the new guest to 17 GiB configured memory is a candidate, not a passing readback.
The proposed storage rule assigns batch archives, caches, snapshots, and source copies to the 8 GiB retained-data limit.
It assigns the new VM bundle and Ubuntu ISO to a separate 40 GiB host-allocation ceiling.
The original 8 GiB transfer limit still includes the ISO and unknown installer traffic.
Neither proposed rule has owner approval.

Complete the missing artifact identities and transfer bound before requesting installation approval.
If exact installer accounting cannot be obtained, propose a separately bounded transfer increase and charge the unknown prior balance in full.
Recheck guest memory, CPUs, disk, all selected tools, and all effective controls only after the changed owner decisions pass.
Keep all 192 development rows planned and all 576 sealed rows unexposed.
Keep operational admission, Phase 3B calibration, and Phase 3C closed.
