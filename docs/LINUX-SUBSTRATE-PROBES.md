# Linux substrate probe checkpoint

Date: 2026-10-02. Version 0.4.0. **Phase 2C remains blocked.** The owner supplied running Docker Desktop. Its explicit local socket responds; the earlier default-socket failure is historical, not a claim that Docker is unavailable now.

## Actual environment and grant

Observed Docker Desktop 4.93.0 (240920), client/engine 29.8.1, API 1.56, arm64 Linux kernel 7.0.14-linuxkit, containerd v2.3.5, runc 1.5.1. Cached public Alpine content identity: `sha256:5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11`; BusyBox v1.37.0. No image, package or model was downloaded, and no existing user container was changed.

The fixture uses `--pull=never`, read-only image root, UID/GID 65532, all capabilities dropped, no-new-privileges, private PID/IPC namespaces, network none, 32 PIDs, 128 MiB, one CPU and disabled Docker logging. Only fresh synthetic input (read-only) and owned output (read/write) directories are bound. Scratch is a 16 MiB noexec/nosuid/nodev tmpfs. Image OS files remain readable as baseline runtime resources. No original checkout, coordinator state, host home, SSH agent or Docker socket is mounted. Parent credential markers are synthetic and are not forwarded.

Engine inspection is checked before starting the worker. The coordinator independently compares excluded fixture bytes, modes and hardlink counts, approved output contents, effective mounts/environment and cleanup. A failed cross-mount `mv` may leave an allowed copy in the owned directory; the protected input must remain unchanged. This is allowed by the write grant and is not an escape.

Docker documents [container controls](https://docs.docker.com/reference/cli/docker/container/run/) and [network none](https://docs.docker.com/engine/network/drivers/none/). Those descriptions explain the selected options; only the recorded experiments support the bounded observations below.

## Frozen versions and retained failures

Every manifest retains all 20 original mandatory criteria and the original grants. No case was removed after observing a failure.

- [v2 manifest](qualification/phase-2c-substrate-v2.json) and [denied observation](qualification/phase-2c-substrate-v2-observed.json): the shell exited zero and protected fixtures were unchanged, but the parent oracle incorrectly rejected the permitted `moved.txt` copy. All subset results were conservatively failed. The failure remains recorded.
- [v3 manifest](qualification/phase-2c-substrate-v3.json) and [observation](qualification/phase-2c-substrate-v3-observed.json): corrected the oracle and recorded the owned tree. Source review then found that a symlink named relative used an absolute target; its relative-variant coverage was incomplete.
- [v4 active manifest](qualification/phase-2c-substrate-v4.json): adds actual relative excluded-target reads/writes and relative read-only parent new-file attempts. SHA-256: `6f4c5a568f89ad16fa6b5754247938bb816ae6c8cb71fd2b12746f95b0af4db1`. Frozen runner SHA-256: `b53230625b6b8a5ce82f47f696edfd9632588ef3d4d75c36fdf6c798d6e786d9`. The [first final observation](qualification/phase-2c-substrate-v4-observed.json) and [fresh-fixture repeat](qualification/phase-2c-substrate-v4-repeat.json) agree on identity and results; both removed their fixture container.

The final worker observed denied reads/writes to synthetic external/original/coordinator paths; denied absolute and relative symlink escapes, new-file parent escapes and read-only metadata mutations; allowed source reads and owned/scratch writes; and no inherited synthetic provider secret, SSH agent or Docker socket. Protected host fixture bytes/modes/link counts stayed unchanged. The final repeat uses a separate container and freshly created directories, not old state.

## Results and limits

Nine cases passed their bounded filesystem/environment criteria: allowed grant, external read, external write, original-checkout exclusion, coordinator-state exclusion, symlink escape, new-file escape, metadata escape and credential/environment inheritance.

Eleven mandatory cases remain **unavailable**: network egress attempts, repository/global hooks, MCP/plugins/instructions, detached descendants, cancellation, deadline, accepted credential mediation, separate credential-free validation, whole-runtime configuration binding and whole-runtime qualification refusal. Network-none configuration was inspected, but TCP/UDP/DNS/IPv6/data-sink attempts were not run. No cancellation/deadline claim follows from removing a normally exited shell. The shell is a synthetic payload, not a Codex/Claude runtime; no customization behavior or model path was exercised.

Both qualification decisions remain denied, with `execution_allowed=false` and credential design null. Five new offline methods inspect the captured terminal/grant/result data, reject weakened engine grants, detect parent-side mutations and refuse manifest drift before creation. They are record/failure checks, not fresh containment qualification. The complete package suite now has 49 tests. Existing Phase 2B authority remains unchanged.

The utility is limited to its frozen trusted payload. It uses ten-second Docker command limits and caps captured output after collection; it is not arbitrary untrusted-output/process supervision. Its stable configuration identity normalizes fixture names/paths, while exact observations retain normalized argv and engine inspection. The full configuration-binding case stays unavailable; coordinator/runtime/credential designs still need their own complete identities.

## Reproduce and continue

Use the current installed package and fresh external output path. The worker helper is in the checkout, not a product CLI command:

```sh
rtk proxy .venv/bin/python scripts/probe_linux_profile.py \
  --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock \
  --manifest docs/qualification/phase-2c-substrate-v4.json \
  --manifest-sha256 6f4c5a568f89ad16fa6b5754247938bb816ae6c8cb71fd2b12746f95b0af4db1 \
  --output /private/tmp/crewshal-2c-new-substrate-observation.json
```

Exit 2 is intentional: the subset can pass while full Phase 2C remains denied. The active v4 manifest refuses source/image drift; the explicit full manifest hash prevents retrospective editing. Old manifests/observations are historical and must not be relabeled as current qualification.

Next work remains Phase 2C: prospectively prepare/pin a provider-free Linux probe/runtime toolchain; exercise network sinks, detached processes, cancellation/deadline, native customization exclusion and separate validation; select and synthetic-test an existing credential mediation mechanism for owner acceptance. Keep real credentials, private source and model calls out. Do not implement a custom gateway or new model/tool loop to bypass this missing boundary. Architectural changes or dependency/image preparation grants remain explicit. Any failed/unavailable mandatory boundary preserves denial. Use [the updated resumption prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md).
