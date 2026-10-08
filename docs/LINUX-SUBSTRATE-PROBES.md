# Linux substrate probe checkpoint

Date: 2026-10-02. Current package 0.6.0; filesystem evidence below remains the historical 0.4.0 record. See the separate lifecycle resumption at the end. **Phase 2C remains blocked.** The owner supplied running Docker Desktop. Its explicit local socket responds; the earlier default-socket failure is historical, not a claim that Docker is unavailable now.

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

## Lifecycle and validator resumption — 2026-10-02

Package 0.5.0 adds a separate [frozen lifecycle manifest](qualification/phase-2c-lifecycle-v1.json), [first observation](qualification/phase-2c-lifecycle-v1-observed.json), [fresh-fixture repeat](qualification/phase-2c-lifecycle-v1-repeat.json), `scripts/probe_linux_lifecycle.py` and six offline failure/refusal methods. Manifest SHA-256: `930e601021f95e01488f10582feb5adadc4bdd76c566edbd34486d0feb93b2ef`; runner SHA-256: `20940da29590f8e263d842a32759d227c3ebb0e6e96c1b394d3d595a7f57c598`. It also pins the unchanged filesystem helper, qualification module and both payloads. All original twenty criteria, grants and limits are retained. This manifest was frozen before its first probe; no failed observed case was removed or weakened.

The same cached Alpine image and explicit Docker endpoint are used. Each run creates three new, uniquely labeled containers, with engine grants checked before start. The cancellation/deadline payload starts a `setsid` shell whose child survives its immediate parent's exit. Independent `docker top` captures distinct process sessions; the detached grandchild attempts a forbidden read, read-only write and HTTP egress, then emits a heartbeat. Cancellation uses `docker kill --signal=KILL` against only that handle. Deadline supervision requests the same kill five seconds after beginning the start operation. Engine terminal states show exit 137, `Running=false`, `Pid=0` and no OOM; heartbeat sizes stay constant across three post-terminal samples. Every fixture container is removed, and a final label-filtered inventory is empty.

First run: cancellation requested at 0.153965 seconds; deadline at 5.000882 seconds; stopped heartbeat samples `[2, 2, 2]` and `[92, 92, 92]`. Repeat: cancellation at 0.102120 seconds; deadline at 5.000350 seconds. These are recorded monotonic coordinator timings, not a claim of instantaneous engine termination. The frozen deadline oracle allows 0.2 seconds of scheduler delay. Docker calls retain ten-second command timeouts; a stalled engine, hostile output or arbitrary runtime is not qualified by this trusted bounded payload. Heartbeat stability is observed over 0.3 seconds, not an indefinite absence proof.

A separate validator receives a fresh read-only synthetic frozen-candidate copy and its own output/scratch directories; worker outputs and credentials are not mounted. It reads and hashes the candidate, attempts a denied source overwrite and HTTP request, checks absent synthetic/provider/SSH variables and Docker socket, and exits zero. The parent independently verifies expected candidate SHA-256, protected bytes/modes/link counts, effective zero-network/credential grant and engine terminal state. No provider credentials, real source, user home or coordinator state are accessed.

Both runs pass four **bounded synthetic** criteria: descendant-escape, cancellation, deadline and credential-free-validation. The nine-case filesystem/environment profile remains separately recorded. These complementary subsets have different identities and are not merged into a thirteen-case qualified record. The new record marks the other sixteen cases unavailable and has a null credential design, denied decision and `execution_allowed=false`. Full native runtime conformance remains unproved even for these synthetic process observations.

Seven criterion categories still need complete-boundary evidence: network-egress, repository-hooks, global-hooks, mcp-plugins-instructions, credential-mediation, configuration-binding and qualification-refusal. The single denied IPv4 HTTP attempt is supporting evidence; no TCP/UDP/DNS/IPv6 sink protocol or positive sink controls were executed. Offline refusal tests do not qualify an operational runtime gate. No native coding runtime, Git hooks or injected MCP/plugins/instructions were executed.

The public reuse decision is unchanged: neither pinned seam is adopted as a qualified executor. These outer-boundary process observations do not retest Orka's native helper or establish integration/recovery equivalence. No additional private or third-party implementation was copied.

### Credential mediation candidate and smallest blocker

[Docker's credential documentation](https://docs.docker.com/ai/sandboxes/configuration/credentials/) describes an existing host-side HTTP/HTTPS proxy that replaces sandbox sentinel values with credentials when forwarding approved requests; OAuth passthrough reduces that isolation. This is a candidate for a prospective synthetic-only assessment, not an accepted or tested Crewshal design. [The documented isolation layers](https://docs.docker.com/ai/sandboxes/security/isolation/) belong to Docker Sandboxes, a separate environment from the ordinary Alpine containers tested here.

Local read-only availability evidence: `docker sandbox --help` reported `"docker sandbox" is deprecated and has been removed.`; `command -v sbx` found no executable on the session PATH. No installation, image/package download, keychain access, secret import or model/provider run occurred. Preparing that separate boundary requires a bounded resource grant and a prospective protocol: synthetic-token replacement/read/replay/redirect/egress, descendant authority, independent validator and native configuration exclusion. Provider access by arbitrary descendants must be explicitly characterized; hiding the token alone does not establish request authority. The owner must accept the resulting tested design before credential mediation can pass. Do not replace this blocker with a custom gateway.

### Reproduce lifecycle observations

From the checkout, using an installed package and fresh external output path:

```sh
rtk proxy .venv/bin/python -m scripts.probe_linux_lifecycle \
  --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock \
  --manifest docs/qualification/phase-2c-lifecycle-v1.json \
  --manifest-sha256 930e601021f95e01488f10582feb5adadc4bdd76c566edbd34486d0feb93b2ef \
  --output /private/tmp/crewshal-2c-new-lifecycle-observation.json
```

Expected exit 2 preserves denial. Prior temporary containers/directories are not prerequisites. Offline `tests.acceptance.test_phase_2c_lifecycle` exercises terminal/activity/deadline/integrity failures, unsafe-grant refusal before start with cleanup, frozen-source/protocol drift refusal and denied subset identity invalidation. The complete offline suite has 55 methods; final installed-wheel evidence is in HANDOFF.md. Continue only Phase 2C using the updated resumption prompt.

## Network resumption — 2026-10-02

Package 0.6.0 adds a separate [network subset and SBX preparation checkpoint](NETWORK-SUBSTRATE-PROBES.md). Two fresh-fixture runs pass the bounded synthetic network criterion; full native runtime/network conformance and credential mediation remain unproved. The nine filesystem and four lifecycle/validator observations remain separate and are not combined with this result. Earlier statements about missing full sink probes describe their historical checkpoints. Phase 2C remains denied; do not begin 2D.
