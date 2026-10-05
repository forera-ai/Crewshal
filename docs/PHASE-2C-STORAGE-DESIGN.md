# Phase 2C storage design and accounting checkpoint

Historical 0.8.14 checkpoint. Current local setup/observations and remaining compatibility gaps are in [the 0.8.15 assessment](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md); use its final bound profile, not unbound historical argv.

Date: 2026-10-05. Base: `d656f4f95c07eee2529e55220ef614863b4132ed`, clean `codex/phase1-architecture`, package 0.8.13. Delivery: 0.8.14. **Blocked: no runtime-compatible storage design is qualified.** This checkpoint adds reproducible accounting and file-operation diagnostics, rather than another unchanged template-load attempt. All historical qualification inputs remain immutable.

## Requirements and accounting layers

The approved logical and allocated aggregate ceilings each remain 8,589,934,592 bytes. They cover public preparation, private state, cache, guest backing disks, filesystem contents, metadata, transport, observer output and logs. Scratch/candidate and all memory/CPU/PID/deadline limits remain unchanged. Physical quota and sampled `du` do not establish a logical ceiling.

Use an object inventory with separate logical and allocated maxima. Count separate files, copied credentials, archives and expanded data separately. For hardlink aliases, identify the same device/inode rather than summing names; keep deleted-open inodes charged until their final FD closes. Sparse backing files still consume their full logical length. Filesystem-internal data and a backing image need explicit representation in the ledger. A guest filesystem can itself hold sparse files, so bounding its virtual disk does not bound the sum of guest apparent sizes. Guest scratch and inner candidate controls must be independently qualified.

The worked ledger deliberately charges upper plaintext, lower ciphertext and any loop image separately. This is a conservative proof strategy, not a newly approved interpretation that reduces the owner's ceiling. Do not silently discount a layer as an alias: establish the exact shared-storage relation and logical accounting convention before proposing such a discount. Physical representations may be charged twice conservatively; neither code nor a fit result proves inventory completeness.

The historical preparation snapshot is 2,053,107,620 logical / 2,053,181,440 allocated bytes. A naive 3 GiB root plus 1 GiB Docker disk, charged once in each eCryptfs view, already yields **10,643,042,212 logical bytes** with that preparation, before logs, backing images or guest contents. It cannot be admitted under this conservative ledger. Those guest disk sizes were historical configuration expectations, not effective observations. This arithmetic rejects that layout; it does not prove every possible supported layout impossible.

An archive-only prospective immutable input set could retain the exact 862,904,320-byte OCI archive and the 244,494,621-byte extracted SBX bundle: **1,107,398,941 logical bytes** before host-specific diagnostics and metadata. Removing redundant downloaded layers and the release tar after independently verifying the surviving artifacts saves space in a new preparation fixture. This is an arithmetic expectation, not observed fresh preparation, runtime compatibility or authority to delete historical private artifacts. Allocated bytes require fresh measurement; do not substitute logical size. Neither a pruned cache nor a read-only cache is currently established as supported by pinned SBX.

`python -m scripts.assess_storage_budget PLAN` computes both dimensions, refuses unknown/negative/boolean counts, duplicate object IDs, changed ceilings and enabled execution flags. Exit 0 means only arithmetic fits; exit 2 means refused. It launches nothing, checks no live quota and grants no execution. [Refused layout](qualification/phase-2c-storage-refused-layout-v1.json) is a reproducible counterexample; [scaled diagnostic budget](qualification/phase-2c-storage-lab-budget-v1.json) is a proposed upper reservation, not enforcement evidence.

## Existing mechanisms and exact unresolved paths

Ordinary XFS/ext4 allocated capacity remains necessary but insufficient because sparse files escape apparent-size bounds. The historical strict file-size/inode/hardlink prototype passes its bounded host cases but its 512 KiB maximum is not a demonstrated native-compatible layout. Increasing inode and file maxima invalidates its previous sum proof. FAT's permission/link/socket and file-size semantics leave full cache/state compatibility unresolved; it is not selected for SBX state. An immutable cache requires a supported static path that has not been established.

**Conditional mechanism to test: existing Linux eCryptfs above a dedicated capacity-limited ext4 filesystem, with its lower path invisible to the diagnostic process.** No custom filesystem, runtime, gateway, adapter or product launcher is introduced. It is selected only for a diagnostic experiment, not operational adoption.

The reviewed [Linux v6.8 truncate path](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/inode.c#L689) fills extensions using [ecryptfs_write](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/read_write.c#L86). Buffered writes in [mmap.c](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/mmap.c#L273) fill intervening pages. These paths suggest coupling apparent growth to lower allocation; this is an inference for encrypted regular files, not a universal proof for an installed kernel. [file.c](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/file.c#L403) supplies no fallocate callback and filters forwarded ioctls, leaving preallocation, reflink, hole-punch and direct-I/O behavior to test. mmap modification after growth, short writes, metadata failure and partial exhaustion also require independent readback. Source expectations are not passes.

Disable plaintext passthrough, encrypted-view and xattr-metadata modes; [main.c](https://github.com/torvalds/linux/blob/v6.8/fs/ecryptfs/main.c#L145) exposes these separate options. No imported encrypted file or lower FD is admissible. Prove lower-path, `/proc` FD, mount, namespace and keyring bypass denial for the actual service identity. Read lower state from a distinct trusted observer. Ordinary metadata compatibility must include private modes, ownership, rename, xattrs, hardlinks, symlinks, Unix sockets and the actual runtime's image operations. A generic file probe cannot establish all of these.

The standard upstream [ecryptfs-utils key management](https://github.com/dustinkirkland/ecryptfs-utils/blob/master/src/libecryptfs/key_management.c) searches/adds keys in `KEY_SPEC_USER_KEYRING`. Merely making a new session keyring does not redirect that tool's hard-coded user-keyring access. No ambient user/root keyring enumeration or imported login key is authorized. A supported setup with exclusively new key state, exact participating tool/library/kernel identities and scoped key cleanup must be resolved before mounting. No key was created, module loaded, package installed or mount attempted here. This concrete setup gap prevents an executable eCryptfs qualification profile today.

Reviewed v6.8 source identities, fetched as data without execution:

| File | SHA-256 |
|---|---|
| inode.c | `914c491992770207c141464d307d088d46a018780adb1b53b2427efb2e4d202c` |
| read_write.c | `a1c81a86e172b631b3599da497bda84a8bfb1cbcb9a23211f5a9ed6c531daf7d` |
| mmap.c | `a3586bab3943878cddc528c492dac1284b7b998a26691bec7c66ee3fbb1c3d7a` |
| file.c | `ed29689441ceb2240494ce6acb0511f7cf2847f0ede5ac4be2022ffcc9e09aad` |
| main.c | `182cefa78fbbfdf08bcc2a186b3b549711afd63199c80fd17aa0c2e7e5d0045e` |

These are research-source bindings, not installed-kernel identity. The upstream ecryptfs-utils page is unpinned supporting evidence for a setup risk, never an executable identity. Rebind the exact installed package/source before use.

## Delivered diagnostic and acceptance scope

[probe_storage_operations.py](../scripts/probe_storage_operations.py) creates one new owned directory and executes a single bounded synthetic file operation. It refuses existing paths and unknown cases/sizes. Cases cover truncate, seek/write, pwrite, mmap, preallocation, copy-range, reflink, hole punching, hardlinks, deleted-open files and a partial metadata check. It records completed/error/errno and FD state, including partial growth after failure. All operations remain at most 64 MiB per file; copied source/target are separately charged. The caller supplies an external ten-second deadline, capped streams, actual controllers, mount isolation and cleanup. There are no network, credential, SBX, subprocess or mounting operations in the payload.

The optional zero-to-two-second FD observation window is not supervision or evidence that an observer sampled it. Independent sampling must match PID/device/inode and operation state, especially deleted-open files. A missed observation remains unavailable. Trusted parent directories are required; leaf exclusivity is not containment against a concurrently hostile parent. Fixtures are deliberately retained for readback; the utility does not recursively delete caller paths. An unsupported operation returning ENOSYS/EOPNOTSUPP is unavailable compatibility, not a passed exhaustion oracle.

The twelve fresh offline acceptance methods verify file data/size, preserved existing/symlink targets, invalid input refusal, deleted-open charging, hardlink identity, optional-operation errors, independent accounting dimensions and refusal at unknown/overflow/duplicate/permission boundaries. The first six-case run failed because this macOS Python exposes no xattr API; the prospective fix now records ENOSYS. Preserve that failure. Package tests cannot qualify a Linux filesystem or pinned native runtime.

## Local substrate and next gate

Observed host: Darwin arm64. VMware Fusion is installed; `vmrun list` reported **zero running VMs**. No guest was started or authenticated. This does not prove that no configured guest exists or that any guest lacks KVM. Broadcom's [supported nested-hypervisor statement](https://knowledge.broadcom.com/external/article?articleNumber=313547) and [Fusion platform description](https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion) do not establish amd64/KVM equivalence on this observed arm64 host. An available local arm64 Ubuntu guest can test filesystem primitives but cannot qualify the exact amd64 SBX bundle merely by passing them.

The [necessary staged batch](PHASE-2C-STORAGE-BATCH.md) separates mechanism tests from pinned runtime compatibility and complete operational/inner/native qualification. No paid host is needed for arithmetic/offline checks. Local disposable Linux access was requested; none was supplied at this checkpoint. No droplet was requested or provisioned. The operational portion remains non-executable until supported private key setup, effective disk sizes/accounting, aggregate placement, independent observer/supervision and all executable identities are bound. **Smallest next capability:** an authorized disposable Linux shell for read-only mechanism admission and supported private key setup, followed by two independently observed storage fixtures. Missing key/bypass/runtime evidence retains denial even after access exists. No retained-host access, repeated resource/discovery approval or Phase 2D.
