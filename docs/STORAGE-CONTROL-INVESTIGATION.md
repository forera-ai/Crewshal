# Phase 2C storage control investigation

Date: 2026-10-05. Status: **unresolved; current host access is missing from this session**. This is a bounded source investigation and continuation checklist, not an executable profile, operational freeze or qualification result.

Baseline revision: `622f9bb1ac54c5727c9e5dd8b390cc157f505217`, initially clean `codex/phase1-architecture`. The retained host, account state and preparation artifacts must remain. Their current existence, access, available resources and identities have not been reverified. The session requested current connection details; it did not inspect SSH configuration, authentication files, ambient credential stores or prior private chat history to recover them.

## Superseding owner cost policy — 2026-10-05

The owner subsequently revoked mandatory droplet retention and intends to remove it. Earlier retained-host/access requirements below describe the original investigation checkpoint and are superseded by AGENTS.md. Do not require current host access for continued local work. Complete substantive storage/control changes first; use local checks or VMware Ubuntu when necessary and sufficient. Request a concrete droplet batch only if a necessary acceptance check cannot be satisfied locally. No candidate is qualified by this policy change. Host-only account/preparation survival is unknown; re-establish exact prerequisites only on a suitable approved test substrate.

## Established constraint

The authenticated v4 source/profile and freeze status were read directly. Existing independent physical-quota observations accept oversized sparse logical files. The 128 MiB/96-inode/64 MiB-per-file tmpfs layout fails supported template loading with ENOSPC. Neither increasing those bounds without a new aggregate proof nor replacing them with ordinary physical quota resolves the logical requirement. The approved aggregate ceiling remains 8,589,934,592 bytes for each of logical and allocated storage, including preparation, guest disks, private state, logs and fixtures. Every original resource limit and grant remains unchanged.

Docker's current [disk settings](https://docs.docker.com/ai/sandboxes/configuration/settings/) and [disk troubleshooting guidance](https://docs.docker.com/ai/sandboxes/troubleshooting/) describe size configuration. These documents do not establish independent aggregate apparent-size enforcement for the pinned SBX 0.46.0 release or show that its cache fits the approved layout. Historical creation-time 3g/1g values remain unobserved effective settings.

## Bounded candidates, not selected controls

Linux v6.8 [FAT file operations](https://github.com/torvalds/linux/blob/v6.8/fs/fat/file.c) expand files through `fat_cont_expand` and reject hole-punch flags; [buffered writes](https://github.com/torvalds/linux/blob/v6.8/fs/fat/inode.c) use `cont_write_begin`. This suggests a capacity-limited, non-sparse data area as a candidate. It is an inference from source, not proof covering every allocation operation or the installed Ubuntu kernel. SBX/containerd filesystem compatibility, file-size restrictions, permissions, sockets, links, case handling, temporary extraction and guest disk I/O remain unknown. Do not relocate account state to a filesystem that cannot enforce its private modes. No FAT fixture was created.

Linux v6.8 [eCryptfs truncate](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/inode.c) and [write paths](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/read_write.c) fill gaps before extension. This suggests a second candidate for coupling apparent growth to lower allocation. Installed support, mount/key prerequisites, direct I/O, metadata handling, bypass denial, compatibility and performance remain unknown. No key was created, kernel module loaded or mount attempted. No candidate is accepted merely because one source path fills holes.

An immutable prepared cache plus separately bounded writable guest disks is another layout to investigate through supported pinned interfaces. No static path for making the required cache immutable while retaining supported runtime behavior is established. No custom filesystem, gateway, launcher or changed runtime is proposed.

## Required next experiment

1. Obtain current retained-host address/user/authentication context and privately record host-key verification limits. Reverify OS/kernel/KVM HLT twice, available memory/disk, controllers, quota filesystem capability and exact preparation/account prerequisites. Do not repeat login unless its retained state actually fails.
2. Inspect available existing filesystem/tool support read-only. Choose a supported candidate only after checking the pinned runtime's actual filesystem operations. Freeze every diagnostic source/executable/configuration before invocation under the approved discovery exception. No package installation or global configuration change is implied.
3. Define an explicit aggregate ledger before creating storage. Include immutable inputs, backing files, mounted content, guest disks, account copies, transport/observer output and logs; explain accounting layers and avoid hiding duplicated storage or sparse logical capacity. A sampled `du` check is not enforcement. No capacity recommendation is made before this ledger is complete.
4. In two fresh owned fixtures, test actual allocated exhaustion and logical extension through truncate, seek/write, positional writes, mmap, preallocation and any supported copy/reflink operation; cover links, deleted-open files and bypass paths. Capture independent apparent/allocated readback, quota/capacity state, errors and scoped cleanup. Retain failures. A filesystem mechanism must pass compatibility as well as resource oracles.
5. Only after those prerequisites pass, test supported local template load with independently supervised limits. Resolve all-process aggregate placement, descendant migration denial and daemon restart after settings. Inspect actual guest/inner identities through supported trusted discovery. Freeze the complete operational manifest before two inner-enforcement runs; native/broker qualification still follows its own mandatory gates.

## Session evidence and boundary

Caveman ultra was requested; Jev MCP live calls succeeded. Jev advised awaiting current access rather than retrying import or raising limits; this advice does not supply authority or qualification. Codebase-memory Verify used project `Volumes-X10Pro-Crewshal`, generation `2026-10-02T22:00:00Z`. Qualification source/test paths matched graph metadata without recorded gaps; new authenticated profiles/sources were untracked by that generation and received direct-source fallback. Graph cleanliness is best-effort, not completeness.

The network-denied offline command `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .` passed all 78 tests in 5.306 seconds. This is package regression evidence, not fresh storage or runtime qualification. No remote operation, template load, guest startup, inner/native probe or operational freeze occurred. Storage remains unresolved; `execution_allowed` and `native_start_allowed` remain false.

The smallest immediate missing input is current retained-host connection context. Supply it and resume Phase 2C with [the continuation prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md). No unchanged-envelope approval, additional droplet, Phase 2D, merge, deployment or release is requested.
