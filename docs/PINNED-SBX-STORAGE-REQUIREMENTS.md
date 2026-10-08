# Pinned SBX storage requirements and blocked layout

Date: 2026-10-05. Base revision: `d163c4752fcbfddd35f01b695831208a18db90ad`, clean `codex/phase1-architecture`, package 0.8.15. Delivery: 0.8.16. **Bounded source research delivered; a supported admissible runtime layout remains unresolved.** No SBX executable, daemon, installer, template, provider, paid host or native worker ran in this session. The existing local VM was not accessed. Phase 2C remains blocked.

The [research record](qualification/phase-2c-sbx-storage-research-v1.json) binds nine public source files, two release statements, declared Go dependencies, selected binary symbols and failed anonymous source lookups. These are research inputs, not a frozen operational manifest or new qualification passes. The [previous Linux observations](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md) remain immutable.

## Exact executable identity and source limits

The official [0.46.0 release](https://github.com/docker/sbx-releases/releases/tag/v0.46.0) archive was freshly downloaded as data: 82,815,215 bytes, SHA-256 `edd86e2f21559e190723fd884c3a1dced161a555afdff85c5921ed45e7d6d56e`. All eleven regular bundle members matched the historical digest/size manifest. Nothing from the archive was executed; file bytes were copied to an exclusively created external research directory without preserving executable mode. That directory is not a replay prerequisite.

The pinned sbx binary has SHA-256 `530f1d5b8ec662946e33c46a454fc17381790b6c5f13d0922d050a82e57d75a2`. Its inline Go build information declares `go1.27.0`, main module `github.com/docker/sandboxes v0.46.0+dirty`, revision `991967dc90ce0d9a440cd1df1bdf3e395c5a2693`, and `vcs.modified=true`. A revision alone therefore cannot reproduce its exact source. The package license identifies proprietary software. The public release repository is not the engine implementation.

Material declared dependencies:

| Declared component | Version / replacement | What this establishes |
|---|---|---|
| containerd/v2 | v2.3.5 replaced by docker-next-containerd/v2 v2.3.5-internal.2 | Upstream v2.3.5 is comparison source, not exact executable source |
| docker-next | v0.43.1 | Engine identity metadata; private implementation unavailable anonymously |
| go-diskfs | v1.8.0 replaced by docker-next-go-diskfs d801cc851604 | Upstream disk helpers cannot be assumed equivalent |
| continuity | v0.5.0 | Identifies a public dependency; selected copy routes remain unknown |
| bbolt | v1.5.0 | Identifies public metadata-store dependency; effective options remain unknown |
| go-erofs | v0.3.1 | Identifies a public image library; no selected conversion path is proved |

The [release provenance](qualification/phase-2c-sbx-storage-provenance-v1.json) declares EROFS base source commit `b96836c051cbdbc0e21f0f8e8396bd239b56c4a5`, Docker-next v0.43.1 and Sailor v0.136.0. The bundled third-party notice explicitly points to private Docker-next EROFS patches. The base source is **not the complete bundled mkfs.erofs source**. The supplied [SBOM](qualification/phase-2c-sbx-storage-sbom-v1.json) lists a document-root package rather than a complete transitive inventory. Both statements bind the archive subject, but signatures were not verified; they are publisher assertions, not independently reproduced builds.

Anonymous module-proxy requests for the three private replacements/engine returned HTTP 404. Anonymous GitHub lookups for the EROFS patches, Sailor tag and Sandboxes tag also returned 404. No authentication, credential lookup or private-source access was attempted. These are access failures, not proof that source does not exist. Public source files were independently matched against their raw upstream URLs and archived with copyright/license headers intact as `.txt` research inputs. No upstream code was adopted into Crewshal implementation.

## Operations and exact fallback distinctions

| Storage role | Source evidence | Existing observation / unresolved gate |
|---|---|---|
| Content ingest and commit | Upstream containerd local writer writes, syncs, closes, changes modes and renames content; resume can truncate to zero | Regular writes/rename/private modes observed; actual fork, directory sync, locking and successful import untested |
| Metadata database | bbolt Unix paths use advisory flock, read-only shared mmap/madvise, positional writes, and default writable truncate/sync growth | Prior writable mmap probe does not test database locking, read-map/remap, durable transactions or exhaustion recovery |
| Full EROFS conversion | Upstream comparison invokes `mkfs.erofs --tar=f --aufs --quiet -Enoinline_data` | Selected private-fork invocation/options and actual output remain unknown |
| Indexed EROFS conversion | Upstream comparison `--tar=i` keeps a temporary tar and appends tar data to an index image | Must charge compressed input, temporary uncompressed tar, output data and metadata at peak coexistence; cannot assume this path is selected |
| Hole punching / zeroing | Provenance base EROFS ordinary-file I/O tries hole punching, then falls back to zero pwrite when it fails | ENOTSUP is not by itself fatal for that base path; private patches/build options and fresh bundled behavior still unverified |
| Preallocation / reflink | Library and VMM binary signals are insufficient to determine a mandatory operation or complete fallback | Keep prior ENOTSUP results unavailable; neither universal requirement nor compatibility inferred |
| File copying | Continuity has distinct seek and copy-range errno branches | Initial SEEK_DATA EINVAL/ENOTSUP/EOPNOTSUPP uses plain copy; later copy_file_range fallback accepts EXDEV/ENOSYS/EOPNOTSUPP, **not EINVAL** |
| Ownership and image metadata | Upstream archive/copy paths preserve owners, modes, links, xattrs and times; some paths create special files | Same-identity chown/socket and user xattr are only partial evidence; privileged ownership/security attributes and actual tar semantics remain unknown |
| Guest writable images | Upstream EROFS block mode offers ext4-image transforms and truncate-based preparation | Private replacement includes additional options; selected mode, formats, effective sizes and VMM I/O/discard behavior unobserved |

The byte-bound [continuity copy source](qualification/sbx-storage-source-v1/continuity-copy-linux.go.txt) exposes the errno distinction. The earlier eCryptfs copy-range EINVAL would propagate **if** this route is selected after a successful SEEK_DATA. SEEK_DATA/Hole routing itself was not observed, and no exact runtime call-chain is claimed. Presence of a dependency does not prove this path is used. Do not add a custom fallback or silently patch the vendor runtime.

The pinned [EROFS base I/O source](qualification/sbx-storage-source-v1/erofs-io.c.txt), lines 170–216, supplies zero-write fallback plus ftruncate. This reduces one source-level concern but does not turn unsupported punching into a passed operation. Direct bundled mkfs execution and independent output/data/allocation readback are still necessary. The archive notice's private patches keep exact-source conformance unavailable.

ELF function-name data includes containerd EROFS conversion/snapshotter, local content writer, bbolt grow and Docker-next block-volume symbols. It also includes `WithRwlOptions` and `WithNoSync` variants not supplied by the inspected upstream snapshotter file. These positive signals reinforce the fork distinction; symbols are not execution traces, syscall contracts or proof of completeness. Engine/VMM source, selected cache layout, direct-I/O/preallocation/discard semantics and recovery remain unresolved.

## Supported paths, sizes and accounting

Historical pinned settings observations establish `sandbox.disk.dockerVolume=1g` as an effective configuration value, not a created disk. The pinned description states a 512 MiB minimum, creation-only effect and a per-sandbox DOCKER_SANDBOXES_DOCKER_SIZE override. Current [official settings guidance](https://docs.docker.com/ai/sandboxes/configuration/settings/) agrees on creation-time disk settings and daemon environment inheritance; it does not prove this pinned runtime's resulting disk bytes. Stop/restart/readback and fresh disk inspection remain required.

Historical XDG relocation supplied private writable config/cache/runtime roots. XDG_CACHE_HOME, DOCKER_SANDBOXES_ROOT_SIZE and DOCKER_SANDBOXES_DOCKER_SIZE literals are present in freshly verified binary data. The ROOT_SIZE literal plus the earlier requested `3g` value does **not** establish a supported effective root size, selected writable-layer mode or complete path inventory. No root setting is invented.

No supported immutable **entire cache** layout is established. Upstream comparison code mutates ingest directories, content commits and metadata. Immutable input archives or committed image data are distinct from making all cache/database state read-only. The bounded settings/docs/source inspection provides no pinned compatible split-cache interface; its absence from this inspection is not a universal absence claim. A bind mount chosen solely from strings or manually relocated private engine files is not an accepted layout.

The [pruned counterexample](qualification/phase-2c-sbx-storage-pruned-refused-v1.json) charges the prior archive-plus-bundle logical expectation of 1,107,398,941 bytes and hypothetical requested 3 GiB + 1 GiB disks in both upper and lower representations. Total **9,697,333,533 logical bytes**, exceeding 8,589,934,592 by **1,107,398,941 bytes**, before backing files, cache, guest contents, temporary conversion, metadata or output. Requested sizes are not effective observations. This is a lower-bound refusal for that hypothesis, not an actual runtime inventory. Pruning prior inputs does not rescue that layout.

The [unresolved inventory](qualification/phase-2c-sbx-storage-inventory-v1.json) explicitly retains unknown counts for every required runtime representation. Compressed cache, conversion intermediates, EROFS data/metadata, host images, encrypted lower state, fixture backing, guest apparent contents, scratch/candidate, deleted-open FDs and outputs are independently charged. A successful source fallback can increase allocated storage; no silent compression/reflink/alias discount is allowed. Hardlinks retain inode identity. EROFS indexing may retain several representations simultaneously; no estimate is substituted for peak measurement.

An encrypted host image that fills holes does not prevent a guest ext4 filesystem from creating sparse apparent files. Host allocated capacity and configured virtual disk capacity therefore cannot qualify aggregate **guest apparent-size** enforcement. This independent gate remains mandatory for both worker and validator. Neither a smaller Docker setting nor sampled du output resolves it.

## Reproduction and next boundary

Offline, using only committed public evidence:

```sh
rtk proxy .venv/bin/python docs/qualification/phase-2c-sbx-storage-readback-v1.py
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-sbx-storage-pruned-refused-v1.json
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-sbx-storage-inventory-v1.json
```

The first command validates eleven source/statement byte bindings, archive subjects and the private replacement while retaining all denial flags. Both budget commands must return **exit 2 / arithmetic_refused**: one for overflow plus unknown allocation, the other for unknown inventory. This proves recorded arithmetic/refusal only. No runtime/storage operation is performed.

For independent static reproduction, download the exact release archive as data into a new external directory, verify its published digest, then pass `--archive /absolute/path/to/DockerSandboxes-linux-amd64.tar.gz` to the readback command. It checks all eleven member digests, Go identity, fork marker, recorded positive literals/symbols without extracting or executing programs. Reject substituted archives. The corresponding release provenance/SBOM URLs and hashes, and every public source URL/hash, are in the research record. No old temporary directory is required. Do not run install.sh.

**Smallest blocker:** the exact private-fork/VMM storage contract and a supported layout with independently enforceable host and guest logical/allocated ceilings. Resolve this through version-matching public/vendor documentation, source availability or a prospectively bound narrow trusted compatibility diagnostic under the recorded discovery authority. Do not substitute upstream containerd or unpatched EROFS for the exact bundle. Do not claim that unavailable source requires credentials or broaden access to private repositories.

A necessary diagnostic must identify the actual supported cache/config/runtime paths and selected conversion/root-image mode; freeze installed helper/kernel/module bytes and exact invocation; prove an admissible peak ledger and ownership/observer placement before import or guest creation. Then, on the matching platform, observe real template conversion and disk creation twice with exact errno, copy/seek routing, ownership, database locks/transactions, VMM image access, independent FD/data/allocation/cgroup readback and scoped cleanup. Inner/native operations remain separately gated. No unchanged ENOSPC retry.

This session prepares requirements and refusal evidence only. A concrete paid-host batch is **not yet runnable** because supported layout/admission and exact observation/setup bindings are missing. No paid batch, host access or unchanged resource decision is requested at this boundary. Use local source/ledger work first; arm64 helper diagnostics cannot establish amd64/KVM runtime qualification. Only after the layout and commands are concrete and a necessary check cannot run locally may a new paid batch be presented for owner approval with unchanged ceilings, preparation/experiment durations, cost exposure and cleanup. Do not provision or use prior paid-host authority.

All original memory/CPU/PID/swap/deadline/stream/disk limits, proposal/protocol digests and twenty criteria remain unchanged. `execution_allowed=false`, `native_start_allowed=false`, `operational_manifest_frozen=false`. Stop at this blocked boundary; [next initial prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md) resume only the missing compatibility/layout contract, not Phase 2D.

## Checkpoint checks

The empty-environment/network-denied offline package suite passed 93 tests in 5.495 seconds. Ruff check/format passed (37 files including the new research checker); mypy passed ten product files. Offline build produced the 0.8.16 sdist/wheel; no fresh installed-wheel run is claimed. Readback passed offline and against fresh pinned archive data. Five isolated evidence-copy mutations refused with the expected reasons; the [verification record](qualification/phase-2c-sbx-storage-verification-v1.json) includes the reproduction recipe, checker digest and results. All 180 previous qualification files remain byte-identical to base HEAD. No runtime compatibility criterion is promoted. The exclusively owned external research directory and its 1,778 data files were removed after verification; it measured 337,967,339 logical / 344,174,592 allocated bytes. No VM or host lifecycle action occurred. Final version/link/fence/input/whitespace checks accompany commit and push under standing authorization.
