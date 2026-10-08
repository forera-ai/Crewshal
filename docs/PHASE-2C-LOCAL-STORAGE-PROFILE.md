# Local synthetic storage profile

Date: 2026-10-05. This profile is prospective diagnostic work, not the operational manifest. The owner identified the local Ubuntu installation as test-only and supplied authentication directly. No credential is stored in the checkout or evidence. No paid host, SSH service, native runtime, custom filesystem or product launcher is used.

## Observed admission and supported key setup

The guest reports Ubuntu 24.04.5, aarch64, kernel `7.0.0-38-generic` (`7.0.0-38.38~24.04.4`). `CONFIG_ECRYPT_FS=y`, `CONFIG_KEYS=y`, `CONFIG_ENCRYPTED_KEYS=y`; eCryptfs is already in `/proc/filesystems`. Root access works through existing VMware guest operations and the owner-supplied password. RTK is absent inside the guest; host commands use RTK. No ambient keyring or credential store is read.

The official [kernel encrypted-key interface](https://www.kernel.org/doc/html/latest/security/keys/ecryptfs.html) supports the `ecryptfs` authentication-token format. The diagnostic uses installed `keyutils=1.6.3-3build1` from Ubuntu noble/main, verified as `/usr/bin/keyctl` SHA-256 `3cfa42ed0f9f37dd8bb126093511a10218179abe640aa17bbcff315b16cafde9`. Each fixture starts through `keyctl session -`, creating a separate anonymous session keyring. Only that newly owned ring is listed; an empty ring is a prerequisite. A fresh random 32-byte master is piped into `keyctl padd user NAME @s`; a new encrypted token is created through `keyctl add encrypted SIGNATURE 'new ecryptfs user:NAME 64' @s`. Neither master nor encrypted blob is printed. Only returned new handles are described, revoked and unlinked. Ordinary ecryptfs-add-passphrase and ambient `@u` access are excluded.

Mounting uses `mount -i` directly with encrypted token signature, AES, 32-byte key, `ecryptfs_mount_auth_tok_only`, nodev/nosuid/noexec. No plaintext passthrough, xattr metadata, encrypted view or imported lower files. This is an experiment with installed kernel bytes, not a claim that upstream source exactly matches Ubuntu's build. The kernel image SHA-256 is `c5f1e915ecf0303df41c4ec7ce2fc150bf5c50bc940dfb63701996c5bbd069fb`.

## Bound recipe and roles

Source bindings before any fixture:

| Source | SHA-256 |
|---|---|
| scripts/prepare_linux_storage.py | `cd29eaf9048c8c6416628f8e7128865d8c9b98d3fd18bd251b6b14dbb6c81445` |
| scripts/observe_linux_storage.py | `5f8804cf8b25d03714d2564483c1f4d0554d59cbde6e46829cd2d298484f86cd` |
| scripts/probe_storage_boundary.py | `2aaefb14aafaeefbefe848cce98c584e05d0e4b36c96eb7cadc35da91f3bb7de` |
| scripts/probe_storage_operations.py | `b5072ac70ee5eceb40f885a7c045dc420548cff8e4432977eb80fb25d83b49a0` |

`prepare_linux_storage.py` exclusively creates a private input tree, copies vendor Python/stdlib/dependent libraries and the exact diagnostic sources, and records SHA-256 for originals, copies, participating installed helpers/libraries, kernel and configuration. It refuses copied inputs above 256 MiB. The copied payload root contains only those vendor dependencies, payloads and empty standard mount points. No home, credential files, sockets or network state are imported. Preparation precedes the experiment and is reported separately.

An exclusively named runtime systemd slice holds the observer, mount/key helpers and sequential payload services. Effective `memory.max=805306368`, `memory.swap.max=0`, `cpu.max=100000 100000`, `pids.max=128` are required. The observer service receives private mount/network namespaces and remains the trusted root setup/readback role. Its source rechecks all bindings before mutation. It creates only new 32 MiB regular backing files, formats those files, obtains `losetup --find --show --nooverlap`, and checks exact BACK-FILE before mounting or detaching. Host block devices are never formatted. Mount propagation/readback is recorded.

The final diagnostic profile uses already installed bubblewrap 0.9.0 directly from the observer's private mount namespace. Earlier systemd service binding attempts flattened `/proc` magic references to an unmounted tmpfs directory; their readback/refusals remain immutable. No host-global mount workaround is used. Bubblewrap binds the copied vendor root read-only and the actual encrypted upper at `/work`, supplies private PID/network/IPC/UTS and mount namespaces, minimal devices/proc, empty environment, a new terminal session and die-with-parent behavior. The installed setpriv helper inside the copied root drops all real/effective/saved identities to 65534, clears groups and all capabilities, and sets NoNewPrivileges. Only its temporary SETUID/SETGID/SETPCAP capability needs are retained until that trusted drop.

An exact existing libseccomp API-generated BPF filter denies keyring, mount, setns, unshare, clone3, ptrace, process-memory, BPF and perf operations with EPERM; masked clone rules deny all namespace creation flags. BPF bytes are read-only synthetic inputs, recorded by digest, and passed only to the existing bubblewrap `--seccomp` interface. No product launcher or custom runtime is introduced. The observer enforces ten seconds and 65,536 bytes per stream, kills the owned wrapper group on timeout, and requires observed owned PIDs absent before cleanup. Bubblewrap's private PID namespace dies with its reaper. All helpers and descendants inherit the already verified aggregate slice; each observed worker cgroup is recorded. RLIMIT_FSIZE must remain unlimited.

Before growth cases, the bound boundary payload attempts lower, observer FD, loop, key, user/mount namespace, setns and cgroup access. It records effective identity/capabilities/seccomp and checks same-identity chown, rename and a Unix socket. These limited denials do not prove absence of every engine/runtime escape or privileged chown compatibility.

The observer runs all eleven operations at 8 MiB and 40 MiB per fixture. Root observation reads the actual payload PID's regular-file FDs during its two-second hold, including unlinked-open state, and records upper/lower device/inode/length/allocation plus free lower capacity. It waits for stopped payload state before exact case cleanup. Unsupported operations remain compatibility gaps. Partial failed growth remains evidence. Two fixtures get separate new backing images, mounts, anonymous rings and keys. No fixture consumes previous-run outputs.

The complete experiment is capped at 600 seconds including cleanup; new work stops before the final 30-second reserve. Driver RuntimeMaxSec=570s and TimeoutStopSec=30s enforce that reserve. Startup is at most 120 seconds per fixture. The arithmetic ledger charges loop, lower and upper independently at 32 MiB each, reserves 256 MiB for copied vendor inputs and another 256 MiB for source/helper representations, plus 16 MiB for private diagnostic output/metadata. All remain far below each original 8 GiB ceiling; upper no-hole behavior is still an unproved premise until observed. An output file is capped independently at 16 MiB before publication. No SBX cache or guest disk belongs in this ledger.

Cleanup unmounts upper then lower without lazy unmount, verifies/detaches only the owned loop, revokes/unlinks only returned new keys, and removes only new files after handles close. External readback checks no owned services/processes/loops/mounts remain, then removes only the owned runtime unit/slice and private preparation artifacts. Host package installation remains recorded; the guest is not deleted or automatically shut down.

## Qualification boundary

Fixture observations can support only this scaled installed mechanism and limited payload boundary. Pinned amd64 SBX compatibility, cache/disk layout, guest apparent-size enforcement, actual image operations, all broker/native criteria and the full operational manifest remain unresolved. `execution_allowed=false`, `native_start_allowed=false`, `operational_manifest_frozen=false`. Stop at this milestone; no Phase 2D.
