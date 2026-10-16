# Phase 2D kernel scaffold source review

Date: 2026-10-12.
Status: Source review only. Phase 2D has not passed Linux acceptance.

## Exact reviewed inputs

The recorded host uses Ubuntu 26.04.1, `aarch64`, and kernel release `7.0.0-38-generic`.
Its recorded version signature is `Ubuntu 7.0.0-38.38-generic 7.0.14`.
This record supersedes no dated host observation.
The current operational batch must bind these fresh inputs.

The reviewed package is `linux-source-7.0.0_7.0.0-38.38_all.deb`.
Its SHA256 is `997a13a0c7fd0172a93b0c1ae9a4ffc7d3cbbf91d2fdd91d85334193580687de`.
The actual package member is `./usr/src/linux-source-7.0.0/linux-source-7.0.0.tar.bz2`.
That member contains `195204446` bytes.
Its SHA256 is `1610ed026817da29c6be30c2d9c639287ea472d5b805a1f23e2d576be6be6222`.
Independent local archive readback matched this member to the retained source archive.
All fourteen extracted kernel source files matched their archive bytes and recorded hashes.
These archive reads did not compile or execute kernel source.

| Recorded kernel input | SHA256 |
|---|---|
| Running kernel notes | `df3166d903fc3838eb56969804fe4ce384bb54a9d61880b2294b1ec135091314` |
| Running kernel BTF | `03d25ddfb2b6d716421e6bf19d602725bf8c33ab8e8be0eef3f3346f4d07fe14` |
| Kernel configuration | `c5462b866b5fdb2fe7177a1ae2b2bdff237679cdce2cf14a994c6d5387fdb107` |
| Kernel command line | `2b86c519c1bf7d87e6cfee17c7f3db0da942bc9df16a8971d6c1bbc8d8a1588e` |

The configuration enables `CONFIG_MEMCG`, `CONFIG_SLAB_OBJ_EXT`, `CONFIG_SHMEM`, `CONFIG_TMPFS`, `CONFIG_SLUB`, and `CONFIG_ARM64_4K_PAGES`.
It disables `CONFIG_MEM_ALLOC_PROFILING` and `CONFIG_KASAN`.
It enables `CONFIG_RANDOM_KMALLOC_CACHES`.
The private review data preserves the exact source hashes and recorded geometry.
The source review does not replace actual kernel FD readback.

## Resident inode and accounting facts

`mm/shmem.c:5164` allocates `shmem_inode_info` through `alloc_inode_sb()` and `shmem_inode_cachep`.
`mm/shmem.c:5196` creates that cache with `SLAB_ACCOUNT`.
`fs/inode.c:341` and `fs/inode.c:1185` connect inode creation to the filesystem allocation operation.
`fs/dcache.c:2796` marks each new persistent shmem dentry and retains its reference.
Shmem creation calls that function at `mm/shmem.c:3905` and `mm/shmem.c:4156`.
Thus linked scaffold objects retain their kernel inode allocation.
The inode slab has no swap representation.
Deletion can reduce logical storage, but it grants no charge refund or resource reuse.

`mm/slub.c:773` requests object extensions for an online memory controller and an accounted cache.
`mm/slub.c:792` places the extension array after the cache object slots, with extension alignment.
`mm/slub.c:802` checks whether this array fits within the slab.
`mm/slub.c:2262` initializes extensions directly in that unused space.
`mm/slub.c:3511` performs this initialization before the new slab supplies objects.

The recorded shmem object size is `760` bytes.
Its recorded slab stride is `768` bytes; its recorded order is `2`.
The page size is `4096` bytes.
The retained audit must confirm the actual BTF sizes of `shmem_inode_info` and `slabobj_ext`.
The expected extension size is `8` bytes.

| Slab order | Slab bytes | Object slots | Object and extension bytes |
|---|---:|---:|---:|
| `0` | `4096` | `5` | `3880` |
| `1` | `8192` | `10` | `7760` |
| `2` | `16384` | `21` | `16296` |
| `3` | `32768` | `42` | `32592` |

Every listed order has room for its complete extension array.
This path avoids a separate extension allocation that can fail.
`mm/memcontrol.c:3236` otherwise permits an object after extension allocation failure.
Therefore, `SLAB_ACCOUNT` alone does not prove complete accounting.

The recorded initial cache has `10332` slots.
The logical bound conservatively includes every initial slot, even when an earlier slot lacks accounting metadata.
The original `128 * 262144` exception allowance remains unchanged.
The audit must refuse disabled accounting, changed geometry, or changed kernel exports.

## Cached short symlinks and the 147-byte bound

The earlier phrase “inline symlink” is incorrect for this kernel source.
`mm/shmem.c:4133` calls `kmemdup(symname, len, GFP_KERNEL)`.
`include/linux/fs.h:951` stores the returned pointer in `inode->i_link`.
The target bytes reside in a separate kernel object.
They do not reside inside `shmem_inode_info`.

`mm/shmem.c:92` defines `BOGO_DIRENT_SIZE` as `20`.
`mm/shmem.c:98` defines `SHORT_SYMLINK_LEN` as `128`, including the terminating zero.
The short target therefore contains at most `127` logical bytes.
One parent entry adds `20` logical bytes.
The resulting upper bound remains `147` logical bytes per inode.
An empty regular file contributes at most its parent entry.
A directory contributes `40` initial logical bytes and its parent entry.
Its child entries are assigned to the child inodes.
The reviewed routes must create no additional hardlink entries or long symlink targets.

The unchanged conditional logical formula is:

```text
10332 * 147 + ceil((805306368 + 128 * 262144) * 147 / 760)
= 163772143 bytes
```

This is a conditional source bound.
It requires the original aggregate, live kernel geometry, and qualified trusted scaffold routes.

## Filesystem allocated extents and separate kernel objects

The existing allocated ledger counts filesystem extents through `st_blocks * 512` and conservative original filesystem allowances.
`mm/shmem.c:3087` initializes `i_blocks` to zero.
The cached short-link branch does not allocate a file-data folio.
It therefore creates no allocated filesystem data extent.
The allocated-extent formula remains unchanged.
The complete recorded allocated ledger remains `8271167488` bytes, below the original `8589934592`-byte ceiling.

A conservative count permits `1114097` inode slots.
At most `128` requested link-object bytes per slot gives `142604416` bytes.
This number describes requested kernel object bytes.
It does not bound whole shared slabs or global kernel RAM.
The recorded normal kmalloc caches have no enabled debug padding, and their orders are zero.
Random kmalloc caches and unrelated clients can affect slab occupancy.
Do not treat a whole foreign slab as an owned file extent.
Do not claim that the original memory controller charges these `GFP_KERNEL` link objects.
Keep the original exception allowance intact.

## Reviewed trusted scaffold routes

The reviewed stock Codex `bwrap.rs` creates filesystem arguments from the fixed filesystem policy.
Its production argument builder has no `--symlink` or arbitrary `--file` operation.
`bwrap.rs:1254` supplies its empty read-mask file through `/dev/null` and `--ro-bind-data`.
That input produces zero file-data bytes.
`bwrap.rs:1266` creates empty readonly directory masks.
The other tmpfs arguments create roots or readonly masks for the selected policy.

`bubblewrap.c:1386` creates empty device bind targets.
`utils.c:480` writes content only when its content argument is present.
`utils.c:504` creates a missing bind target with a null content argument.
`bubblewrap.c:1391` creates the fixed standard-stream symlinks.
Its other device symlink targets are `/proc/self/fd`, `/proc/kcore`, and `pts/ptmx`.
The maximum target length on these reviewed routes is `15` bytes.
This is below the required `127`-byte target ceiling.

Bubblewrap also implements general file-data and symlink options.
Their existence does not establish permission to use them in the frozen profile.
The actual selected native arguments and source-to-binary provenance must exclude unreviewed routes.
All native, sandbox, and bubblewrap executable identities remain required installed inputs.

The proposed tool and validator profiles deny user namespace creation, capabilities, mounts, unmounts, and `pivot_root`.
Their write rules permit only the original bounded views and `/dev/null`.
The helper filter rejects `memfd_create`, `shmget`, `shmat`, `memfd_secret`, and shared anonymous `mmap` routes.
Ordinary file-backed WAL mappings remain permitted by that filter source.
The policy must deny every actual zero-device alias and exclude inherited descriptor escape routes.
These source rules cannot prove their installed operation.

## Acceptance limits

The source facts support the original conditional logical and allocated-extent formulas.
The corrected source uses “cached short symlink” and preserves every numerical limit.
Actual policy compilation, loaded policy readback, stacked transitions, and device aliases remain unqualified.
Actual kernel FD readback must confirm the source audit before payload admission.
Both original twenty-case Linux runs and the live frozen-candidate acceptance remain required.
No compiler, Linux mutation, authentication, provider request, or live acceptance followed from this source review.
