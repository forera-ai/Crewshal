# Local Linux storage observation milestone

Date: 2026-10-05. Base revision: `c30c8eb270520d6fc5296f1864d0d1ee3a26e411`, clean `codex/phase1-architecture`, package 0.8.14. Delivery: 0.8.15. **Two fresh synthetic Linux fixtures observed; Phase 2C remains blocked.** No pinned SBX, operational guest, provider, inner/native test, paid host or Phase 2D ran.

## Substrate, authority and exact profile

The owner identified the local Ubuntu installation as test-only and supplied authentication directly. The initially shut-down existing Fusion VM was started without VM configuration changes. It reports Ubuntu 24.04.5 aarch64, Linux `7.0.0-38-generic`; this differs from its display name. Filesystem admission does not supply an amd64/KVM equivalence claim. Existing VMware tools supplied authenticated guest operations; no SSH service, ambient credential recovery or credential store was used. Authentication remained in the temporary client process and was not written to repository/evidence files. RTK was absent in the guest; all host shell commands used RTK.

`CONFIG_ECRYPT_FS`, `CONFIG_KEYS` and `CONFIG_ENCRYPTED_KEYS` are built in. The official [encrypted eCryptfs key interface](https://www.kernel.org/doc/html/latest/security/keys/ecryptfs.html) supplied the existing supported mechanism: separate new anonymous session rings, new random master/token handles, direct `mount -i`, and exact-handle revocation/unlink. Only each newly created ring and its returned handles were inspected. No ambient `@u` ring was enumerated or imported. Pinned Ubuntu `keyutils=1.6.3-3build1` was installed; existing bubblewrap 0.9.0, setpriv and libseccomp supplied the final synthetic payload boundary. These are diagnostic tools, not a Crewshal product/runtime launcher.

The [prospective recipe](PHASE-2C-LOCAL-STORAGE-PROFILE.md), [final profile](qualification/phase-2c-local-storage-profile-v6.json) and [1,342 original/copied vendor/source/kernel bindings](qualification/phase-2c-local-storage-bindings-v6.json) bind the final invocation. The aggregate slice independently read back memory 805,306,368 bytes, swap zero, CPU `100000 100000`, PIDs 128. All sampled payload descendants remained under that exact slice. Peak aggregate memory was 105,021,440 bytes. The copied final vendor tree measured 45,834,159 logical / 47,284,224 allocated bytes. Four then-retained preparation trees plus their directory/manifest bytes totaled 183,668,187 logical bytes, within the prospective 256 MiB copied-input reservation. The [conservative ledger](qualification/phase-2c-local-storage-budget-v2.json) reserves 654,311,424 bytes in each dimension; it is arithmetic, not full inventory/enforcement proof. Original 8 GiB ceilings are unchanged.

The final observer runs in a distinct mount namespace and makes its propagation private before creating fixtures. Each fixture uses a new 32 MiB regular ext4 backing file, verified returned loop, encrypted upper, new session ring and keys. Bubblewrap inherits this actual private mounted view and binds it directly at `/work`. Readback confirms eCryptfs rather than an unmounted directory. A copied vendor root is read-only; PID/network/IPC/UTS/mount namespaces, minimal devices/proc, empty environment, setpriv UID/GID 65534, zero capabilities/NoNewPrivileges, and exact libseccomp filter restrict the payload. No lower path, loop, observer FD, key API, new user/mount namespace, setns or writable cgroup path was available in either boundary observation. These eight tested denials per fixture are a bounded subset, not every native/engine escape.

## Independent results

The [unchanged raw observation](qualification/phase-2c-local-storage-observed-v6.json) is 435,812 bytes, SHA-256 `9ed71c46226508d5a8aa7fff663f03aba54c06c95a5d47f916d7736ef1aeaaa3`. Fixtures took **47.298 and 47.495 seconds**, including their cleanup. Maximum observed operation command duration was 2.174 seconds. Both fixtures produced the same outcomes across eleven operations at 8 MiB and 40 MiB: **44 observations**. No missing/unsupported result is counted as successful exhaustion.

| Operation | 8 MiB | 40 MiB |
|---|---|---|
| truncate, seek/write, pwrite, mmap | completed; exact logical length and allocated lower content | ENOSPC; partial lower content retained in evidence |
| hardlink | completed; aliases share an inode, link count 2 | ENOSPC during growth |
| deleted-open | completed; independently sampled link count 0 and retained allocation | ENOSPC during write, before unlink |
| preallocate | ENOTSUP | ENOTSUP |
| copy-range | EINVAL | source growth fails ENOSPC before copy |
| reflink | ENOTSUP | source growth fails ENOSPC before clone |
| hole-punch | ENOTSUP | write fails ENOSPC before punching |
| metadata | mode, rename, symlink and xattr completed | same metadata-only behavior; does not allocate 40 MiB |

Independent root FD samples match the payload's reported device, inode, logical length, allocation and links in all 44 cases. Host PID/namespace-PID mapping matches the reported payload PID. Independent byte readback is retained; hardlink aliases and inline symlink metadata are distinct. Successful 8 MiB regular growth allocates 8,396,800 lower bytes, including encryption overhead. Oversized sequential writes retain at most 26,521,600 upper logical bytes in these observations. Failed truncation/offset growth may leave upper length zero while retaining lower allocation; the failed file and lower state are inspected before deletion.

Same-identity chown, rename and Unix socket binding also work. Privileged chown and actual containerd/EROFS/VMM cache/image operations were not tested. In particular, unavailable preallocation/copy/reflink/hole operations remain material compatibility questions until the pinned runtime's real requirements and supported fallbacks are known. Scaled growth observations do not prove a universal apparent-size bound, a supported runtime layout or guest inner enforcement.

Reproduce the published readback locally, without a Linux host or prior temporary files:

```sh
rtk proxy .venv/bin/python docs/qualification/phase-2c-local-storage-readback-v1.py
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-local-storage-budget-v2.json
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_storage_observer
```

The readback verifies recorded observations only; a fresh Linux experiment needs fresh admission, matching installed bindings, exclusive paths and the exact recipe. It is not safely replayed against an arbitrary host. No new run depends on these old loops, directories, keys or reports.

## Cleanup, failures and limitations

Both fixtures stop their observed payload PIDs, empty each exact case, unmount upper then lower without lazy unmount, verify/detach the owned loop, revoke/unlink only new keys, observe each new ring empty and remove the owned backing/fixture tree. External cgroup readback reports `populated 0`; no owned host mount or loop remained. Private preparations, input transport, runtime slice file and sixty known new report paths were removed. Failed transient units were reset after their evidence was preserved. [External cleanup](qualification/phase-2c-local-storage-external-cleanup-v1.json) records the exact final state. The authenticated client ended and its secret-free local bridge was removed. The existing test VM is left running; installed keyutils remains. The VM was not deleted. Do not assume future availability or retain/recover authentication from project files.

All failed variants remain separate: initial preparation rejected ldd on a shell script; profile v1 expected the wrong empty-ring text; v2 encountered `/run` noexec; v3's systemd `/proc/PID/root` source produced the wrong view; v4 had an observer forwarding NameError; v5's O_PATH source was also flattened to tmpfs. Profile v6 used the installed bubblewrap inherited namespace and produced both full observations. Prior sources, profiles, bindings and refusal records are retained. The initial preparation source was reconstructed and matched its original SHA-256 exactly. An initial local readback assertion incorrectly applied a regular-file allocation rule to inline symlinks; the oracle was corrected to regular files without changing evidence. Long PTY input and VMware's early shell-variable expansion also refused external housekeeping; corrected short Python requests produced the final external readback. Those faulty status requests are not evidence of unit shutdown.

Explicit remaining limitations: installed kernel image/configuration are bound, but all kernel-module bytes/paths and complete operational/native identities are not frozen. Lower free capacity was not separately sampled during the deleted-open hold; independent upper FD allocation was sampled. The trusted diagnostic calls global sync between cases on this test host; this is not an adopted production policy. Only the listed boundary attempts, scales and metadata were exercised. Original twenty native/broker cases, worker/validator enforcement, exact request authority and full guest apparent-size accounting remain unavailable.

The milestone's setup and two observations are delivered. **Stop development at this boundary.** Next milestone: establish the pinned runtime's actual filesystem operation/cache/disk requirements and a supported layout that fits both independent ceilings, then prepare only the necessary matching-platform qualification batch. Local aarch64 observations cannot execute the exact amd64 bundle. Do source/ledger work first; request a new paid-host batch only if a necessary check cannot run locally and the concrete commands/limits/cost/cleanup are ready. No premature template import, native run, complete-manifest claim or Phase 2D.

## Checkpoint verification

The fresh network-denied empty-environment offline suite passed **93 tests in 5.656 seconds** on Darwin arm64. Ruff check and format passed for src/tests/scripts (36 formatted files); mypy passed for ten product source files. `rtk proxy uv build --offline` built the 0.8.15 sdist/wheel; no fresh installed-wheel execution is claimed. Published readback and arithmetic commands above pass while retaining execution denial. Final input/history checks confirm 246 unique existing continuation files, all six profile/source/archive/manifest bindings, synchronized version, local links/fences and 149 previously tracked qualification files byte-identical. Final Git whitespace checks pass. The milestone commit supplies the delivery revision; current branch is pushed under standing authorization, without merge/deployment/registry release.
