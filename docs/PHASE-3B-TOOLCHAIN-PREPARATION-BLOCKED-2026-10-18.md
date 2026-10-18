# Phase 3B toolchain preparation amendment draft and blocked boundary

Date: 2026-10-18. Entry revision: `76980c7b8837da63b8c17e0b1fa1535893bfa39e`.
Branch: `codex/phase1-architecture`. Entry worktree: clean. Package version: `0.15.8`.
Status: **draft, incomplete, and not approved for execution**.

## Admission result

The approved Phase 3B batch and unknown subscription quota decision remain in force.
The read-only preparation section of the approved proposal does not authorize installation or retrieval.
The separate Ubuntu guest remains connected to its owner account and disconnected from the network.
Its 16,384 MiB configuration reports 16,728,174,592 guest-visible memory bytes.
That is 451,694,592 bytes below 16 GiB.
RTK and eight selected tools remain absent. Python 3.12.3 differs from selected 3.12.15.
No executable, package, provider identity, native qualification, baseline, or calibration was admitted.
The previous 8 GiB guest remains under owner control and was not changed.

The guest's `/var/log/installer/curtin-install.log` contains `Fetched 393 kB in 1s` and `Fetched 292 MB in 25s`.
These rounded summaries are lower-quality evidence than an exact transfer counter.
They do not bound interrupted transfers, metadata, or other installer traffic.
The known ISO and checksum transfer remains 3,825,518,142 bytes.
The 8 GiB download ledger still has no reliable remaining balance.
The last measured VM bundle and ISO directory allocation totals 9,041,420,288 host bytes.

## Prospective interpretation requiring owner approval

Require at least **17,179,869,184 bytes of guest-visible total RAM** from `free -b`.
Increasing the new guest's configured memory to 17 GiB is one candidate.
Recheck actual guest-visible memory, four online CPUs, and 40 GiB free on `/var/tmp` after that change.
The configured number alone cannot pass admission. Do not change the old guest.

Define the 8 GiB retained-data limit as batch-owned downloaded archives, dependency snapshots, caches, and source copies.
Track the VM bundle and Ubuntu ISO in a separate infrastructure ledger.
Propose a 40 GiB ceiling for their combined host allocation, measured before each retrieval and after each preparation stage.
Keep the 8 GiB transfer limit inclusive of the ISO and its checksum file.
This storage interpretation changes the approved limit's scope and needs explicit owner approval.
Do not delete the VM or historical custody to fit a limit.

The present download ledger is still unreliable. Keep all guest network transfer and host artifact retrieval stopped.
Obtain exact installer transfer evidence or a conservative, independently justified upper bound before any retrieval.
If neither exists, request a new bounded transfer allowance with the unknown prior amount charged in full.
No proposed interpretation silently resets the existing 8 GiB transfer counter.

## Candidate official artifact manifest

This table separates verified source metadata from missing admission fields.
It is **not an installation manifest**. Exact archive bytes, extract sizes, dependencies, and executable hashes remain required.

| Tool | Official source and Linux arm64 artifact | Digest and archive bytes | Candidate install action after all gates pass |
| --- | --- | --- | --- |
| RTK | [RTK releases](https://github.com/rtk-ai/rtk/releases); candidate `v0.51.0`, `rtk-aarch64-unknown-linux-gnu.tar.gz` | SHA-256 and exact bytes unresolved. The host has RTK 0.51.0; that does not bind guest bytes. | Verify the signed or published checksum. Extract into the owned tool root. Run `rtk --version` and `rtk proxy true`. |
| CPython 3.12.15 | [Python source release](https://www.python.org/downloads/release/python-31215/); `Python-3.12.15.tar.xz` | SHA-256 `c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a`; 20,829,824 bytes. Python publishes source only for this release. | Pin compiler and library packages first. Extract safely, configure for an owned prefix, build with at most four jobs, and run `make altinstall`. |
| Node.js 22.14.0 | [Node.js archive](https://nodejs.org/download/release/v22.14.0/); `node-v22.14.0-linux-arm64.tar.xz` | [Official SHA-256](https://nodejs.org/download/release/v22.14.0/SHASUMS256.txt): `08bfbf538bad0e8cbb0269f0173cca28d705874a67a22f60b57d99dc99e30050`. Exact bytes unresolved. | Verify checksum and byte count. Extract safely into the owned tool root. Check `node --version`. |
| Bun 1.2.2 | [Bun release assets](https://github.com/oven-sh/bun/releases/expanded_assets/bun-v1.2.2); `bun-linux-aarch64.zip` | Official checksum manifest and exact bytes remain unresolved. Release page rounds its size to 34.5 MB. | Verify signed checksum and byte count. Extract into the owned tool root. Check `bun --version`. |
| Swift 6.0.3 | [Swift Linux instructions](https://www.swift.org/install/linux/tarball/); `swift-6.0.3-RELEASE-ubuntu24.04-aarch64.tar.gz` and `.sig` | SHA-256 and exact bytes unresolved. Verify the Swift release signature and key. | Pin all [Ubuntu 24.04 dependencies](https://www.swift.org/install/linux/tarball/) first. Verify signature, extract safely, and check `swift --version`. |
| .NET SDK 9.0.100 | [Microsoft .NET 9 downloads](https://dotnet.microsoft.com/en-us/download/dotnet/9.0); Linux Arm64 SDK archive and the required net8.0 runtime or targeting packs | Exact artifact URL, digest, bytes, and required packs remain unresolved. | Pin all artifacts. Extract into the owned tool root. Set `DOTNET_ROOT` inside the batch and check `dotnet --info`. |
| CMake and Ninja | Official Ubuntu 24.04 arm64 packages or pinned upstream releases | Exact versions, package digests, bytes, and transitive packages remain unresolved. | Install only from a frozen package set or verified archives. Check versions and executable digests. |
| Codex CLI 0.160.1 | Frozen npm `@openai/codex` wrapper and `@openai/codex@0.160.1-linux-arm64` native tarballs | Frozen registry integrity strings are in `runtime-selections.json`. Exact archive bytes and extracted executable SHA-256 remain unresolved. | Verify both frozen npm integrity values and byte counts. Extract without install scripts. Bind the native executable and effective configuration. |
| Claude Code CLI 2.1.278 | Frozen npm `@anthropic-ai/claude-code` wrapper and `@anthropic-ai/claude-code-linux-arm64@2.1.278` native tarballs | Frozen registry integrity strings are in `runtime-selections.json`. Exact archive bytes and extracted executable SHA-256 remain unresolved. | Verify both frozen npm integrity values and byte counts. Extract without install scripts. Bind the native executable and effective configuration. |

The exact CPython source digest and byte count come from its official release and directory pages.
Node.js publishes the selected digest in its official checksum list.
The frozen runtime selection records npm integrity values, not future installed executable hashes.
No unverified value in this table may be treated as a passing artifact identity.

## Proposed install command shape and limits

The following commands describe the proposed operation. **Do not run them under the existing approval.**
Replace each placeholder with a frozen, reviewed manifest value before requesting installation approval.
An archive with an unresolved digest, byte count, extraction inventory, or license result remains blocked.
RTK is absent in the guest, so only its verified bootstrap may use raw commands.

```sh
install -d -m 0700 /var/tmp/crewshal-phase3b-v1/tools
curl --proto '=https' --tlsv1.2 --fail --location --retry 0 --max-time 120 --output "$OWNED_RTK_ARCHIVE" "$PINNED_RTK_URL"
test "$(wc -c < "$OWNED_RTK_ARCHIVE")" -eq "$PINNED_RTK_ARCHIVE_BYTES"
sha256sum "$OWNED_RTK_ARCHIVE"
test "$OBSERVED_RTK_SHA256" = "$PINNED_RTK_SHA256"
rtk --version
rtk proxy curl --proto '=https' --tlsv1.2 --fail --location --retry 0 --max-time 120 --output "$OWNED_DOWNLOAD" "$PINNED_OFFICIAL_URL"
rtk proxy test "$(wc -c < "$OWNED_DOWNLOAD")" -eq "$PINNED_ARCHIVE_BYTES"
rtk proxy sha256sum "$OWNED_DOWNLOAD"
rtk proxy test "$OBSERVED_SHA256" = "$PINNED_SHA256"
```

The RTK archive extraction step requires its own safe, exact member manifest before `rtk --version` can run.
These command shapes omit that unresolved step and cannot be executed as a script.
The real install command must also verify signature or npm SHA-512 integrity where the vendor supplies it.
Validate archive members before extraction. Reject absolute paths, parent traversal, links, special files, and duplicate paths.
Do not run remote install scripts or package hooks. Do not use `sudo apt install` without a pinned package manifest.
Keep download, extraction, build, and executable locations under a private owned root.
Measure downloaded bytes, retained bytes, VM allocation, CPU, RAM, and disk before and after each artifact.
Stop before a prospective action exceeds any approved ceiling or cannot be measured.

Retain one task unit at a time. Keep preparation within four CPUs, 12 GiB RAM, and 24 GiB guest disk.
Keep the original native 600-second and 768 MiB limits and the validator's four CPUs, 8 GiB RAM, 8 GiB disk, and 900 seconds.
Keep the eight-hour active and 24-hour wall preparation limits from the approved proposal.
Do not reconnect the guest while the transfer ledger or manifest remains incomplete.

After a qualified batch, remove only batch-owned source copies, writable caches, and temporary extraction files.
First verify that no child process, mount, or file handle retains them.
Retain unknown resources and charge their full reservation. Keep the VM, ISO, raw receipts, and historical custody pending a later disposal decision.

## Smallest remaining work

1. Resolve the exact installer transfer bound without new downloads.
2. Fill every unresolved artifact digest, exact byte count, extraction size, dependency set, and install command.
3. Prepare an exact prospective ledger under both the 8 GiB download and retained-data limits.
4. Obtain owner approval for guest-visible memory, storage interpretation, and any changed ceiling.
5. Only then change the new guest, retrieve tools, and qualify the exact platform.

The existing qualification and batch-limit approvals need no repeat request.
No Jev call ran because Jev is a paid model service outside the approved evaluation batch.
Measured billing and API-equivalent cost have no new evaluation observation. Subscription quota debit for this chat remains unknown.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Phase 3B calibration and Phase 3C remain closed.

## Exact checks and limits at this boundary

The host reported Darwin 27.2.0 arm64, Python 3.12.15, and RTK 0.51.0.
The host is the local macOS checkout. It is not the qualified Linux guest.
The following host commands were read-only:

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy uname -srm
rtk proxy .venv/bin/python --version
rtk --version
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
```

Git was clean at entry. The checker returned 23 artifacts, 768 planned units, and content digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The guest console used `ls /var/log/installer` and `grep Fetched /var/log/installer/curtin-install.log`.
One attempted `ls -l` input lost several characters and failed with `ls: invalid option -- '/'`.
Another input lost the hyphen in `grep -E`; the shell ran `grep E` and returned irrelevant lines.
The corrected `grep Fetched` returned the two rounded summaries quoted above.
No guest command changed files or connected the network.

No selected coding-runtime submission or paid host ran.
Measured evaluation billing remains unknown. No new API-equivalent estimate was measured.
The guest ISO and checksum are the only known Phase 3B host retrievals.
The installer transfer remains unknown, and the earlier VM-plus-ISO allocation remains the last measured value.

The publication checks used these commands:

```sh
rtk proxy git diff --check
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy .venv/bin/python -c 'import crewshal; print(crewshal.__version__)'
```

The diff check passed. The checker retained the same 23 artifacts, 768 planned units, and content digest.
`pyproject.toml` and `crewshal.__version__` both report `0.15.8`.
The new public continuation index contains 135 paths. This command checked each byte count and SHA-256:

```sh
rtk proxy .venv/bin/python - <<'PY'
import hashlib
import json
from pathlib import Path
p = json.loads(Path('docs/PHASE-3B-TOOLCHAIN-PREPARATION-INPUTS-2026-10-18.json').read_text())
assert len(p['files']) == 135
for item in p['files']:
    data = Path(item['path']).read_bytes()
    assert len(data) == item['bytes']
    assert hashlib.sha256(data).hexdigest() == item['sha256']
print('135 public input hashes match')
PY
```

It passed. The index marks operational admission and calibration false, and it excludes private and sealed contents.
No test suite ran because this checkpoint changes documentation and synchronized version metadata only.
