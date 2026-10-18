# Phase 3B toolchain amendment boundary

Date: 2026-10-18. Entry revision: `2d627c7f4985801a3b65fe497514e5f226fdf6fd`.
Branch: `codex/phase1-architecture`. Entry worktree: clean. Entry version: `0.15.9`.
Status: **blocked preparation amendment**. Phase 3B calibration has not started.

## Results and failures

All 138 public files in the [starting input index](PHASE-3B-TOOLCHAIN-AMENDMENT-INPUTS-2026-10-18.json) matched their byte counts and SHA-256 digests.
The graph index reported a ready Crewshal project. No structural source claim was needed for this documentation checkpoint.
The host VMware log search found no exact installer transfer counter in the targeted lines.
The guest console still displayed only rounded `Fetched 393 kB` and `Fetched 292 MB` summaries.
A read-only `ls /var/log/apt` attempt produced no reliable guest result.
The VMware computer-use interface then returned `noWindowsAvailable` on two attempts.
These control failures do not prove that no exact counter exists inside the guest.
No exact prior installer transfer bound was established.

The [candidate manifest](PHASE-3B-LINUX-ARM64-TOOLCHAIN-MANIFEST-2026-10-18.json) records fourteen artifacts.
It binds official URLs and published digests where verified.
The .NET `net8.0` requirement now names runtime 8.0.11 and targeting pack 8.0.11 as candidates.
The pinned [Serilog test project](https://raw.githubusercontent.com/serilog/serilog/0e316b7cb072ee660b97976098b1bbdb20ac6da0/test/Serilog.Tests/Serilog.Tests.csproj) targets `net8.0` and `net9.0` and declares exact direct NuGet versions.
The [Serilog source project](https://raw.githubusercontent.com/serilog/serilog/0e316b7cb072ee660b97976098b1bbdb20ac6da0/src/Serilog/Serilog.csproj) also targets `netstandard2.0`.
The [approval test project](https://raw.githubusercontent.com/serilog/serilog/0e316b7cb072ee660b97976098b1bbdb20ac6da0/test/Serilog.ApprovalTests/Serilog.ApprovalTests.csproj) targets `net9.0`.
No NuGet restore ran. Its transitive package set, hashes, bytes, and rights remain unknown.

The manifest still lacks exact bytes for thirteen artifacts.
It lacks all safe extraction inventories, extraction bounds, installed executable hashes, and license results.
The exact Ubuntu arm64 package closure remains unknown.
The direct Swift package names are recorded from the [official tarball instructions](https://www.swift.org/install/linux/tarball/).
No rounded vendor size was converted into an exact byte count.
No artifact was retrieved, unpacked, installed, or executed.

## Exact ledgers and proposed ceilings

The approved transfer ceiling is **8,589,934,592 bytes**.
The ISO and checksum consumed **3,825,518,142 known bytes**.
Their arithmetic difference is **4,764,416,450 bytes** before installer traffic.
Charge unknown prior installer traffic against that entire difference.
The conservative remaining balance is **zero bytes**.
The proposed cumulative ceiling is **17,179,869,184 bytes (16 GiB)**.
If approved, charge the prior phase at the full original **8,589,934,592 bytes**.
That leaves exactly **8,589,934,592 bytes (8 GiB)** for later transfer.
This is a ceiling proposal, not a forecast or retrieval grant.
It includes the existing ISO, checksum, and installer traffic.
It does not erase the unknown installer count or permit unmeasured transfer.

The four selected development archives have frozen exact sizes totaling **2,777,282 bytes**.
The CPython source archive adds **20,829,824 bytes**.
Their known prospective subtotal is **23,607,106 bytes**.
Every other tool archive, package, signature, and metadata transfer remains unpriced.
The prospective total is `23,607,106 + unknown artifact and dependency bytes`.
Its upper bound remains unknown, so the transfer ledger cannot admit retrieval.

The host reports **5,268,045,824 allocated bytes** for the new VM bundle.
It reports **3,825,520,640 allocated bytes** for the ISO directory.
Their current combined allocation is **9,093,566,464 bytes**.
This exceeds the current 8 GiB retained-data limit by **503,631,872 bytes** if both objects count.
The proposed separate infrastructure ceiling is **42,949,672,960 bytes (40 GiB)**.
Its current headroom is **33,856,106,496 bytes**, before future VM growth.
The proposed 8 GiB retained-data ledger covers batch-owned archives, dependency snapshots, caches, and source copies.
Its current exact balance is unknown because those objects were not fully inventoried.
Do not count the proposed infrastructure separation as approved.

The last guest readback reported **55,538,384,896 bytes** free on `/var/tmp`.
The future guest-disk charge for tool extraction, packages, builds, snapshots, and source copies is unknown.
The 24 GiB preparation disk ceiling therefore has no prospective admission result.
The frozen guest disk remains a 64 GB virtual disk; that configured size is not host allocation.
No VM setting or disk object changed in this session.

## Owner decision and sequence

The exact proposed RAM rule requires `free -b` to report at least **17,179,869,184 guest-visible total bytes**.
The last readback was **16,728,174,592 bytes**, short by **451,694,592 bytes**.
A 17 GiB VM configuration is only a candidate. Admission requires a passing guest readback.
The proposed separate VM-plus-ISO ceiling is **40 GiB**.
The proposed cumulative transfer ceiling is **16 GiB**, with the prior 8 GiB charged in full.
The 8 GiB retained-data limit would apply only to batch-owned archives, caches, snapshots, and source copies.
These changed rules need explicit owner approval before any new VM change or ledger use.
The earlier qualification resumption and original Phase 3B limits remain approved.

After approval, the artifact, package, transfer, retained-data, guest-disk, and infrastructure ledgers must all become exact.
Then recheck the new guest's memory, four CPUs, free disk, and disconnected network state.
Only after all admission gates pass may work follow this order: platform qualification, provider identities, dependencies, B1, baselines, calibration.
The previous guest remains unchanged.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Phase 3C remains closed.

## Commands, environment, and cost

The host reported Darwin 27.2.0 arm64, Python 3.12.15, and RTK 0.51.0.
The guest was the separate Ubuntu 24.04.5 arm64 VM.
The host ran these read-only checks from the repository root:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python -c 'import hashlib,json,pathlib; p=json.loads(pathlib.Path("docs/PHASE-3B-TOOLCHAIN-AMENDMENT-INPUTS-2026-10-18.json").read_text()); failures=[]; [(failures.append({"path":x["path"],"expected_bytes":x["bytes"],"actual_bytes":len(b),"expected_sha256":x["sha256"],"actual_sha256":hashlib.sha256(b).hexdigest()}) if len(b)!=x["bytes"] or hashlib.sha256(b).hexdigest()!=x["sha256"] else None) for x in p["files"] for b in [pathlib.Path(x["path"]).read_bytes()]]; print(json.dumps({"count":len(p["files"]),"failures":failures},indent=2))'
rtk proxy rg -n -i 'received|transferred|download|bytes|network' '/Volumes/X10Pro/Internal-Offload-2026-09-15/Moved/Virtual Machines.localized/Crewshal Phase 3B Ubuntu arm64.vmwarevm' -g 'vmware*.log' -m 20
rtk proxy du -sk '/Volumes/X10Pro/Internal-Offload-2026-09-15/Moved/Virtual Machines.localized/Crewshal Phase 3B Ubuntu arm64.vmwarevm' '/Volumes/X10Pro/Crewshal-phase3b-platform-20261018'
rtk proxy .venv/bin/python -m json.tool docs/PHASE-3B-LINUX-ARM64-TOOLCHAIN-MANIFEST-2026-10-18.json
```

The input hash check returned 138 files and no failures.
The VM log search returned VMware event and heartbeat lines, with no exact installer byte counter.
The allocation command returned 5,144,576 KiB and 3,735,860 KiB.
The manifest JSON syntax check passed.
The guest network adapter and installation media remained disconnected in VMware Fusion.
No paid host, evaluation provider request, coding-runtime turn, or Jev call ran.
No new measured evaluation billing or API-equivalent cost exists.
Subscription quota debit for this chat remains unknown.

The frozen checker still reported 23 artifacts, 768 planned units, and content digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The new continuation index verified 142 public files with no hash mismatch.
`rtk proxy git diff --check` passed.
Both version fields reported `0.15.10`.
The graph coverage check reported no recorded issue for the version file and frozen checker at generation `2026-10-18T17:20:02Z`.
That best-effort result is not proof of complete graph coverage.
No test suite ran because this checkpoint changes documentation and synchronized version metadata only.

The next session must use the [continuation prompt](PHASE-3B-TOOLCHAIN-AMENDMENT-CONTINUATION-2026-10-18.md) and its exact public input index.
