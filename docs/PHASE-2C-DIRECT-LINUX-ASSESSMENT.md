# Direct Linux admission and kernel mechanism observations

Date: 2026-10-06. Base revision: `cefef2e9318eb2d7d9b0382ea63c6e9c7ec0d255`. **The owner approved ADR 0003. Local admission and a credential-free kernel mechanism subset now have actual Linux evidence. Phase 2C is not complete.** No native CLI, credential proxy, real provider, paid host or Phase 2D ran.

## Authority and admission

The [separate authority record](qualification/phase-2c-direct-linux-owner-approval-v1.json) binds the original proposal without changing its historical pending-status bytes. The owner confirmed the existing logged-in VMware guest, then supplied current authentication directly after console input proved unreliable. No credential store was consulted; authentication is excluded from public evidence. SSH supplied reliable transport to the already-running test guest; no VM configuration or host provisioning changed.

The exclusively new, digest-verified [admission source](qualification/phase-2c-direct-linux-admission-v1.py) returned exit zero, empty stderr and inventory-only status. The observed environment is aarch64 Linux `7.0.0-38-generic`, Python 3.12.3. CPU, memory and PIDs controllers and the six required helper bytes are present. The source was removed. The [sanitized inventory](qualification/phase-2c-direct-linux-admission-observed-v1.json) excludes the private login/cgroup identity. A separately authenticated `sudo id` demonstrated the trusted root setup role. Neither observation grants execution.

## Prospective freeze and results

The final [profile v5](qualification/phase-2c-direct-linux-mechanism-profile-v5.json), [installed-byte bindings](qualification/phase-2c-direct-linux-bindings-v5.json) and [invocation freeze](qualification/phase-2c-direct-linux-freeze-v5.json) precede worker launch. There are 1,324 source/helper/library/kernel-image/configuration bindings. The copied vendor/input tree is approximately 46 MB logical / 48 MB allocated. Native identities and a complete operational/module closure are not established by this mechanism manifest.

An exclusively owned systemd aggregate slice independently reads back memory `805306368`, swap `0`, CPU `100000 100000`, PIDs `128`. Preparation and the observer service share that slice, including prepared file-cache charge. The observer moves into its own child cgroup before enabling controllers. Every payload starts in a sibling worker child capped at memory `134217728`, swap `0`, CPU `100000 100000`, PIDs `32`. The worker cannot see writable cgroup interfaces.

The observer uses a private mount namespace. Candidate and scratch are separate new tmpfs mounts: 4 MiB / 8 MiB capacity, 128 / 256 inodes. Hard RLIMIT_FSIZE is 65,536 bytes. Payloads run as UID/GID 65534, empty environment, no capabilities, NoNewPrivileges, read-only copied vendor/input root, isolated PID/network/IPC/UTS namespaces and a source-bound libseccomp filter. Mutable xattrs, device creation, namespace/key/inspection APIs, hardlink aliases and anonymous shared-memory creation are denied; `/dev/shm` is read-only. This deliberately narrow pilot envelope is not a universal native-runtime compatibility claim.

The [unchanged raw v5 observations](qualification/phase-2c-direct-linux-observed-v5.json), SHA-256 `3079b801cf8c6e3e656947660e808805380bc80f7cac69a44ec40a64a72a144f`, contain two fresh fixtures. The service returns exit zero in **10.810 seconds**; fixture durations are **5.354 and 5.353 seconds**, including their mount cleanup.

- Tiny permitted reads/writes succeed; read-only input writes and excluded reads fail. Sparse truncation above 65,536 bytes returns EFBIG. Inode exhaustion occurs after 127 / 255 created files. The final payload also requires hardlink, xattr, anonymous memfd and oversized-symlink attempts to fail and both device/shared-memory roots to be unwritable.
- Independent inventory measures candidate allocation exactly 4,194,304 bytes and scratch exactly 8,388,608 bytes at ENOSPC. Their measured logical totals and inode counts remain below the original 16 MiB / 32 MiB ceilings.
- An independently inspected deleted-open FD has matching reported device/inode/length, zero links, 12 logical / 4,096 allocated bytes and the exact worker cgroup. Closing the killed worker removes that retained allocation.
- A detached setsid descendant is killed at the five-second deadline. Its heartbeat stops; each terminal worker cgroup and each fixture cleanup report `populated 0`. These are kernel/lifecycle examples, not the full original twenty-case native suite.

Hardlinks are explicitly denied because aliases could grow directory metadata without consuming a new inode. Anonymous shared memory and writable `/dev/shm` are excluded from the storage grant. The inode/per-file accounting argument therefore does not silently omit those representations. Native compatibility with these restrictions remains a separate required test. Excluded-read attempts in this subset address absent paths in the reduced view; they do not replace the original independently existing excluded-canary fixtures. Memory/task exhaustion, complete namespace/syscall adversaries and an independent validator were not exercised by this subset.

## Failures and cleanup

All failed sources, profiles, bindings and observations remain separate. V1 refuses the unavailable legacy aarch64 `mknod` filter before payload launch; v2 retains `mknodat` but bubblewrap cannot enter a worker-owned 0700 mount during root setup. V3 uses traversable mount roots and its bounds payload exits zero, but immediate kernel cgroup-event sampling is still populated. V4 polls terminal state within the original deadline/grace and passes twice. V5 adds the alias/anonymous-storage restrictions and passes twice. A transfer wrapper substitution error, failed console typing, a heredoc/PTY authentication attempt and an accidentally literal placeholder hash check are preparation failures, not successful probes.

The [external cleanup](qualification/phase-2c-direct-linux-external-cleanup-v1.json) independently records no owned base tree, preparation path, supervisor mount or aggregate cgroup after each batch. Existing Linux stays running. `reset-failed` reports already-unloaded units because `--collect` had removed them; that command is not recorded as an additional successful cleanup.

The 179,823-byte binding manifests were transported as artifact data using SSH `cat`, rather than a bounded diagnostic stdout capture. This is a transport limitation: these transfers must not be represented as commands obeying the 65,536-byte stream ceiling. Subsequent batches must use an existing file-transfer interface with bounded status streams. Worker output uses streaming bounds; this limitation prevents promoting the whole invocation profile to qualification. Freeze v1–v4 retains the initial shared-slice admission sample; those copied `memory.current` values are not fresh per-version measurements. V5 samples the recreated parent slice independently.

## Reproduction and remaining gate

Fresh-checkout public readback, with no Linux host, credentials or earlier temporary files:

```sh
rtk proxy .venv/bin/python -I -B docs/qualification/phase-2c-direct-linux-readback-v1.py
```

This verifies recorded evidence and unchanged original protocol bytes only. A fresh Linux experiment must create new paths, freshly bind the matching installed bytes, enforce the recorded systemd invocation and collect independent cleanup. Never run against someone else's existing directories.

The next prerequisite is [explicitly bounded native/proxy artifact preparation](PHASE-2C-DIRECT-LINUX-NATIVE-PREREQUISITES.md). The initial acquisition-gate interpretation was corrected: deliberate pinned fixture preparation is covered by existing owner authority; runtime automatic downloads remain forbidden. The kernel payload profile is not a native-parent profile: the pinned Codex sandbox requires namespace setup, which this payload filter intentionally forbids. A supported complete native/tool authority boundary must therefore be designed and demonstrated before hostile native cases. Do not simply remove the filter and compose old subset results. All twenty original mandatory same-profile cases, caller-separated credential mediation, native startup under 128 MiB/five seconds and independent validator behavior remain required twice. Execution and Phase 2D stay denied.


Subsequent [native preparation and actual startup evidence](PHASE-2C-DIRECT-LINUX-NATIVE-PREREQUISITES.md) binds official package/proxy bytes and records eight isolated version/help successes in two fixtures. Actual sandbox startup refuses under the guest's AppArmor policy before the literal payload. A concrete fixture-only role-policy proposal parses without kernel loading; the requested owner decision is pending. All native/broker/full-profile gates remain denied. The separate [native cleanup](qualification/phase-2c-direct-linux-native-external-cleanup-v1.json) removes newly owned preparation/cgroups/mounts and leaves global protection enabled and the VM running; it does not claim an exhaustive host PID scan.
