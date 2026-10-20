# Proposed Phase 3B offline toolchain staging

Date: 2026-10-20. Status: proposed; no host bundle or guest action is admitted.
Entry revision: `f1104ce` on `codex/phase1-architecture`.
The [installation completion](PHASE-3B-OFFLINE-INSTALLATION-COMPLETION-2026-10-20.md) closes its earlier guest action.
This proposal needs a separate owner decision before creating a transport or starting the clone.

## Exact decision requested

Approve one offline transport build from the two verified extraction output roots.
Approve one start of the separate Phase 3B clone and one toolchain staging command.
The command may copy verified regular files and create the 40 recorded links in this clone.
It will not execute an archived tool, install another package, connect a network adapter, or run a test.
Permit zero new network transfer, paid-host cost, metered API cost, native turns, or evaluation rows.
Retain partial transport or guest output after a failure. Do not retry under this decision.

## Exact source and transport

The two pinned output manifests have SHA-256 values `13e41f6e8156afd0e4284af200a1ac99f89b46aae7fbfd8f012933d5b56b4529` and `4075234d7996789333e62cd082b7c408abed38a26d0fd5d3fff2de666f39e79d`.
Together they bind 17,227 regular files, 4,371,619,599 content bytes, 2,768 output directories, and 40 links.
A read-only local check matched both full output trees. Their 20,035 paths had zero case aliases.
The longest path had 173 characters. No retained archive body is requested.

The source is [the transport script](../scripts/phase3b_toolchain_transport.py), SHA-256 `d489a1fc3b68a9b6cada003d9a40d03af8b534f66bbec08d7cec8160daddb1eb`.
It validates output manifests, paths, aliases, source hashes, tar members, and link targets.
It writes two tar files with private file modes. It refuses replacement and retains partial output after failure.
Its guest stage verifies the tar SHA-256 values before writing and again verifies every regular file.
It checks the guest free-space floor before each content block and after each write.
It creates links only after writing regular files and checks that resolved links remain inside the output root.
The four local synthetic tests passed. Ruff lint, format, and mypy passed.
A small UDF image fixture mounted read-only and returned its expected file bytes.
No large transport image exists yet.

Use only these new host paths:

```text
/Volumes/X10Pro/Crewshal-Phase3B-Toolchain-Transport-20261020/
/Volumes/X10Pro/Crewshal-Phase3B-Toolchain-Transport-20261020.iso
```

The first path must not exist before `pack` starts. The ISO path must not exist before `makehybrid` starts.
The `pack` command writes `part-12.tar`, `part-4.tar`, both pinned manifests, the script, and `bundle.json`.
The second command makes a UDF image from that directory:

```sh
rtk proxy .venv/bin/python scripts/phase3b_toolchain_transport.py pack /Volumes/X10Pro/Crewshal-Phase3B-Toolchain-Transport-20261020
rtk proxy .venv/bin/python scripts/phase3b_toolchain_transport.py iso /Volumes/X10Pro/Crewshal-Phase3B-Toolchain-Transport-20261020 /Volumes/X10Pro/Crewshal-Phase3B-Toolchain-Transport-20261020.iso
```

Verify both tar digests, the bundle, the script, and the mounted read-only ISO before guest use.
Stop if both tar files together exceed 5,368,709,120 bytes or the ISO exceeds 6,442,450,944 bytes.
The script applies an ISO file-size limit before it starts `hdiutil`.
Cap all new transport directory and ISO host allocation together at 12,884,901,888 bytes.
Require at least 68,719,476,736 free host bytes before and after each write stage.
Do not remove a partial transport automatically.

## Guest limits and action

Require a clean worktree, exact input-index match, and passing frozen Phase 3A checker.
Require all 31 original guest files to match their private custody manifest before and after.
Require the clone off, four configured CPUs, 17,408 MiB memory, network disconnected, and sharing disabled.
Require at least 17,179,869,184 guest-visible memory bytes and 42,949,672,960 free `/var/tmp` bytes.
The last installed clone readback had 54,882,734,080 free `/var/tmp` bytes.
Keep its allocation below 34,359,738,368 bytes and its new growth below 8,589,934,592 bytes.
Keep the original guest, original ISO, clone, and new transport ISO together below 68,719,476,736 allocated bytes.
Keep the host free-space floor at 68,719,476,736 bytes through shutdown.
Limit this attempt to two active hours and four elapsed hours.

While the clone is off, save its CD configuration and point only `sata0:1` at the verified transport ISO.
Set only this CD drive to start connected. Keep `ethernet0.startConnected = "FALSE"`.
Start the clone once. Require the owner to sign in locally.
Confirm the guest still has no network link and no sharing before staging.
Observe the UDF CD device identity. Stop if it differs from the verified ISO.
Mount only that CD read-only with `nosuid,nodev,noexec`.
Run one staging command as the ordinary guest user:

```sh
python3 /mnt/crewshal-phase3b-transport/phase3b_toolchain_transport.py stage /mnt/crewshal-phase3b-transport /var/tmp/crewshal-phase3b-tools-v1
```

Require the destination to be absent before the command.
The stage writes at most 4,371,619,599 regular content bytes and retains at least 42,949,672,960 free guest bytes.
The stage uses private `0700` directories and `0600` regular files. It does not set executable bits.
Record the command status, output inventory, guest space, clone allocation, and errors.
Unmount the CD, soft-stop the clone, and restore its original disconnected Ubuntu ISO CD configuration.
Then verify zero running guests, host limits, network isolation, and original guest custody.

Stop on any changed source hash, missing UDF support, changed device identity, space failure, or staging error.
Do not start, resume, or retry again under this decision.
Keep both historical guests, the original ISO, sixteen archives, receipts, extraction images, fixed image, and frozen Phase 3A bytes unchanged.
The historical archive charge remains 10,008,484,533 bytes.
The package charge remains 116,542,541 bytes. The cumulative conservative charge remains 10,125,027,074 bytes.
Installed executable hashes, effective commands, providers, and B1 conformance remain unknown until observed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
