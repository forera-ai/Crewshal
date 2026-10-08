# Phase 2C necessary storage qualification batch

Historical 0.8.14 checkpoint. Current local setup/observations and remaining compatibility gaps are in [the 0.8.15 assessment](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md); use its final bound profile, not unbound historical argv.

Date: 2026-10-05. **Prepared, not executed or authorized for a paid host.** This is a reviewable dependency-ordered command/test specification. The file-operation payload is executable; mount/key/observer and operational profiles are not yet completely bound. Do not mistake this document for the complete operational manifest. See [design and blockers](PHASE-2C-STORAGE-DESIGN.md).

## Stage 0: offline reproduction, no Linux host needed

From the checkout:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_storage
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-storage-refused-layout-v1.json
# Expected exit 2: conservative historical layout exceeds logical ceiling.
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-storage-lab-budget-v1.json
# Exit 0 means arithmetic only; no enforcement or authority.
```

No downloads, credentials, earlier fixtures or paid service is needed. Tests create their own files. Source/budget/test digests are in [the preparation record](qualification/phase-2c-storage-preparation-v1.json).

## Stage 1: read-only disposable Linux admission

Use an owner-supplied local Ubuntu shell if available. No guest boot, package install, existing keyring access or KVM invocation is part of this admission. Commands run with cleared environment, no inherited credentials, ten seconds and 65,536 bytes per stream. Record a freshly created private report externally; sanitize path/user metadata before publishing.

```sh
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C uname -smr
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C cat /etc/os-release
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C cat /proc/filesystems
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C cat /sys/fs/cgroup/cgroup.controllers
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C cat /proc/meminfo
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C df -B1 /srv
rtk proxy env -i PATH=/usr/bin:/usr/sbin:/bin LC_ALL=C sh -c 'command -v python3 mount umount losetup mkfs.ext4 systemd-run systemctl timeout unshare setpriv keyctl ecryptfs-add-passphrase'
```

These are read-only inventories, not effective-controller or KVM tests. Absent eCryptfs in `/proc/filesystems` is not proof of unsupported kernel configuration; inspect the matching kernel configuration/module package as data. No automatic module loading or installation. Refuse unresolved support. Before any binary used for mutation runs, bind exact helper/library/interpreter/stdlib/kernel/module bytes and profile sources; do not reuse old-host hashes blindly. Resolve supported exclusive key setup: the ordinary ecryptfs-add-passphrase tool targets the user keyring, so a new session alone is insufficient. A prospective existing-tool configuration must avoid ambient keys, identify only newly created handles, and revoke only those handles. **No key/mount command is supplied as safe-to-run until that identity/authority gap is closed.**

## Stage 2: two fresh mechanism fixtures, no SBX

The concrete target for each fixture is a new 32 MiB ext4 loop image, encrypted upper mount, and an independent read-only lower observer. The scaled [ledger](qualification/phase-2c-storage-lab-budget-v1.json) charges the loop, lower and upper separately, each at 33,554,432 bytes; two copied files fit only while the actual lower capacity permits them. Reserve 16 MiB for pinned payload/tool inputs and 16 MiB for private bounded output/metadata. Establish the upper logical bound through the tested no-hole mechanism; its reservation is an expectation, not present enforcement. No operational guest or credentials belong in this fixture.

After Stage 1 produces a completely bound supported setup, freeze the exact invocation recipe before use. The existing-helper sequence is: exclusively create the fixture/backing file; format only that file; obtain `losetup --find --show --nooverlap` and verify its BACK-FILE; mount the exact returned loop privately with ext4/nodev/nosuid/noexec; establish a new exclusively owned eCryptfs key and encrypted upper mount; provide only the upper view to the payload. The lower path and loop devices remain inaccessible there. Never format a supplied host block device. Private mount propagation and exact mount/loop/key ownership must be observed. No change to the host's global filesystem or persistent service configuration is allowed.

Use supported systemd cgroup/namespace controls, set before the payload: MemoryMax=805306368, MemorySwapMax=0, CPUQuota=100%, TasksMax=128, NoNewPrivileges=yes, empty payload capabilities, PrivateNetwork=yes, ProtectSystem=strict, ProtectHome=yes, ProtectControlGroups=yes, ProtectKernelTunables=yes; provide only fresh upper writable scope and read-only pinned payload. All fixture setup/observer/helpers and descendants must be in the same bounded aggregate; root mount setup is a trusted separate role and must not remain privileged inside the payload. Do not apply PrivateDevices blindly to required setup loop devices or mistake its denial for a storage result. Reserve cleanup time. No ambient files, keyring, sockets, credentials, SSH agent or host home are mounted.

Each command below is the **payload argv inside those already established controls**, not a host shell containment wrapper. `CREWSHAL_UPPER` denotes that fixture's upper path. It must be bound prospectively; `CREWSHAL_PYTHON` and `CREWSHAL_PAYLOAD` denote digest-verified read-only files. `timeout` is a secondary command deadline; the independent observer enforces the stream caps and whole-fixture deadline and stops the complete cgroup on timeout/overflow. Capture nonzero statuses as observations and continue only when the next case remains safe. Do not use `|| true` to convert denial into success.

```sh
# Repeat each case at 8 MiB (in-capacity) and 40 MiB (over lower capacity).
# A fresh directory per operation; repeat entire fixture with new image/key/mounts.
for crewshal_size in 8388608 41943040; do
  for crewshal_case in truncate seek-write pwrite mmap preallocate copy-range reflink hole-punch hardlink deleted-open metadata; do
    timeout --signal=TERM --kill-after=1s 9s \
      "$CREWSHAL_PYTHON" -I -B "$CREWSHAL_PAYLOAD" \
      --directory "$CREWSHAL_UPPER/$crewshal_case-$crewshal_size" \
      --case "$crewshal_case" --bytes "$crewshal_size" --hold-seconds 2
    # Observer records exit and capped streams; independently samples before cleanup.
    # Remove only this exact new case directory after all FDs close, then next case.
  done
done
```

The loop is an argv enumeration, not an executable fixture driver: independent observation, per-case cleanup and exit handling must be bound in a prospective host-specific profile before execution. Without cleanup between cases, the first operation changes later capacity and invalidates the oracle. Original per-command maximum remains ten seconds including kill grace, output 65,536 bytes per stream. Limit startup to 120 seconds per fixture; total two fixtures including cleanup at most 600 seconds, stop new work by second 570, reserve final 30 for scoped cleanup. Worst-case 44 operations at ten seconds leave 160 seconds for setup/observation/cleanup; if measured setup cannot fit, refuse rather than increase bounds. Expected successful mechanism batch: roughly 2–8 minutes; hard cap ten minutes. No cost is incurred on a supplied local guest. A paid host would expose provider hourly/minimum billing until the owner removes it; no price or automatic shutdown promise is made.

Independent oracles required in **each** fresh fixture:

- Successful small growth has matching upper FD/inode length and data plus lower allocation, fsync and capacity readback; deny/assert partial over-capacity growth never exceeds the reserved bound. Observe ENOSPC/EDQUOT, not EFBIG from an accidentally inherited small per-file limit. Check actual hard RLIMIT_FSIZE before each operation. A timed-out syscall is unavailable, not quota success.
- Logical extension through truncate, seek/write, pwrite, mmap, copy-range and supported clone cannot create a sparse escape. Inspect partial files after failed growth, not only the return code. Upper/lower inode lists and backing bytes agree with the ledger. No compression, reflink-sharing or imported lower file silently invalidates allocated-to-logical inference.
- Preallocation, hole-punch and reflink may legitimately be unsupported. Record that incompatibility; do not score it as a passed exhaustion test. Pinned SBX's actual corresponding operations must succeed if it requires them.
- Hardlinks share an inode; distinguish alias counting from a new copied inode. Deleted-open FDs remain charged when directory scans see nothing. Independent FD samples during the two-second window must match PID/device/inode/size; a missed sample is unavailable. Repeat observer sampling/readback for writes and post-stop state.
- Private modes, ownership, rename, xattrs, links, Unix sockets and actual cache/image operations must work. The provided metadata case is partial: it does not exercise chown, sockets or containerd. Add prospectively bound standard-tool commands for those required semantics once exact installed tools are known.
- Payload attempts to access the lower path/observer `/proc` FDs, loop devices, keys, mounts/namespaces and writable cgroups must fail. Place prospective trusted bypass payloads under the exact intended identity, with no CAP_SYS_ADMIN, mount/user-namespace/cgroup migration or engine escape. Until exact bypass sources are frozen and observed, mechanism qualification remains incomplete.
- Stop the owned aggregate, inspect final PIDs/FDs and mounted upper/lower views, unmount upper then lower, verify/detach only the exact owned loop, revoke only newly owned keys, then remove exact owned files. Never lazy-unmount a busy fixture or delete files before establishing ownership/handle closure. Missing cleanup evidence fails the fixture.

## Stage 3: runtime compatibility and operational qualification

**Not executable in this checkpoint.** Stage 2 does not show that SBX accepts encrypted cache/disks. Before a Linux amd64/KVM runtime batch is requested, resolve the supported SBX cache path, effective disk sizes, actual containerd/EROFS/VMM operations and aggregate ledger (including guest apparent-size enforcement). Bind the isolated key/mount/bypass setup, all-process placement, daemon stop/restart after settings, command/stream supervision and independent observer sources. Recreate digest-verified public preparation only when needed; record actual allocated bytes. Fresh explicitly authorized isolated Docker state may need recreation after deleted-host loss, without ambient credential import. No login/provider call is part of Stage 2.

The necessary compatibility argv is the supported pinned `sbx template load VERIFIED_ARCHIVE`, then settings restart/readback and `sbx create shell --pull never --skills off --memory 512m --cpus 1 --template VERIFIED_LOCAL_TAG` in one mountless, externally network-denied trusted fixture. Resolve the exact names/paths/disk settings first; do not launch from these symbolic argv. Archive/native identities and actual successful import are prerequisites. Refuse dynamic unpinned code/downloads. Before guest creation, independently prove the ledger and effective aggregate placement. Current expected disk sizes cannot be substituted for readback.

Use local amd64/KVM Linux only if actually observed. This Mac's arm64/Fusion installation and zero-running-VM observation do not supply it. Only after substantive local work and when a necessary pinned-runtime check cannot be satisfied locally, present the owner a new paid-host batch with exact bound commands, the unchanged envelope, ten-minute experiment/cleanup cap, preparation duration/bytes separately specified, pricing exposure and scoped cleanup. Do not provision or use a droplet without approval. Stage 2 should use local Linux when possible and does not itself require KVM.

Freeze the complete operational manifest after approved trusted discovery and **before** two fresh synthetic inner-enforcement runs; then apply [PHASE-2C-READINESS.md](PHASE-2C-READINESS.md) and all twenty original native/broker criteria twice. Every original worker/validator limit and empty grant remains unchanged. No missing phase can be filled by this plan, source research, arithmetic, generic primitives or historical complementary passes. Current status remains `execution_allowed=false`, `native_start_allowed=false`, `operational_manifest_frozen=false`. Resume 2C only.
