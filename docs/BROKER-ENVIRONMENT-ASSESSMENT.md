# Disposable SBX credential-store environment

Date: 2026-10-02. Package 0.8.0. Scope: Phase 2C only. **The disposable Linux file-store prerequisite is demonstrated; an operational credential broker and the remaining whole-runtime boundaries are not qualified. Execution remains denied.**

The previous [SBX protocol](SBX-RESOURCE-CONFIGURATION-PROTOCOL.md) remains immutable. This is a new prospective CLI/store profile, not an amendment to its help-only authority or an approval of the pending outer VM. The original twenty cases, empty worker credential/network grant and 128 MiB/one-CPU/32-PID worker limit remain identical in every new manifest.

## Prepared environment and observed store

The official SBX v0.46.0 Linux arm64 archive was downloaded externally and checked against its release asset digest: 72,270,041 bytes, SHA-256 `b20da2e5e2ba7a67151a19821960c657c08d8fa8dcfdf5e9751f284d6e55ffa8`. Its CLI digest is `247f30d8bc7dcce615235024eac43a4ad0d1730a94ff650d52a6e57bad401060`. All extracted file digests are bound in the manifests; no third-party code or binary was added to Crewshal. Matching the release digest establishes identity, not independent signature verification.

An official Ubuntu 24.04 arm64 image was prepared at immutable identity `sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60`. Docker's reported image size is 139,378,930 bytes, not a measured network-transfer total. Archive and image preparation took 15.17 seconds under the previously recorded official-public 2 GB/30-minute preparation allowance. See [preparation record](qualification/phase-2c-broker-preparation.json). No global installation, provider login or real credential operation occurred.

Each preflight created a disposable, unprivileged container with network `none`, a read-only root, user `65532:65532`, all capabilities dropped, no-new-privileges, private IPC, no host PID namespace, no devices, 128 MiB, one CPU and 32 PIDs. The only host bind is the verified official bundle, read-only. Synthetic home/config/runtime directories and the credential store live in a 32 MiB tmpfs. Host homes, original checkout, coordinator state, SSH agents, Docker sockets and credential stores are not mounted. The controller checks the effective engine grant before start and after collection; cleanup removes only its unique fixture handle and checks its absence.

This allocation is a **CLI/store test host**, not the proposed 512 MiB SBX guest or a native worker. Commands have ten-second timeouts and 65,536-byte output checks; fixture lifetime and admission deadline are sixty seconds. Cleanup has separate bounded commands. Output is checked after capture, suitable for the pinned trusted CLI, not qualification of hostile-output supervision.

Two fresh [v3 observations](qualification/phase-2c-broker-environment-v3-observed.json), [repeat](qualification/phase-2c-broker-environment-v3-repeat.json) use the same frozen manifest SHA-256 `27107761f400de9454f855b5ffe319b264dba44b1385aca67d2b4bfe263d9daf` and runner SHA-256 `e8cf5db4867812f6cc76ede35624aaf84b1c4946585f2166c2b34f0511d702a9`. Each records version, custom-secret help, synthetic custom-secret save and a separate CLI listing, all exit zero. The CLI prints the Linux no-keychain fallback notice and lists the synthetic service. The controller independently observes a nonempty `secretpass` backing blob and the `0700` store directory. Backing files were `0644` inside private `0700` directories; do not describe them as `0600`. Plaintext matching did not find the token; this is not a cryptographic or replay-safety claim. No surviving `sbx`/`sandboxd` process is present at the controller's process oracle; that snapshot does not establish that no transient process ever existed. No daemon-start command or sandbox-create/run command was invoked.

The synthetic token is deliberately supplied to this trusted test host. Its CLI arguments and reports contain synthetic values only. This is **not a worker token-hiding test**. No worker or validator is given this store, no provider-shaped service is contacted, and no request is authenticated. All twenty operational results remain unavailable. No execution or broker-design acceptance follows from store success.

## Preserved failures and remaining host requirement

V1 saved/listed the secret but its controller `docker cp` oracle could not find the tmpfs directory. Preserve [manifest](qualification/phase-2c-broker-environment-v1.json), [source snapshot](qualification/phase-2c-broker-environment-v1-runner.txt) and [observation](qualification/phase-2c-broker-environment-v1-observed.json); store observation stays false. V2 observed backing files, but incorrectly required a plaintext token and mistakenly treated a `sandboxd` log path as a process name. Preserve [manifest](qualification/phase-2c-broker-environment-v2.json), [source snapshot](qualification/phase-2c-broker-environment-v2-runner.txt) and [observation](qualification/phase-2c-broker-environment-v2-observed.json). Neither failed oracle is promoted. V3 was frozen before running with a blob/directory/CLI agreement oracle and explicitly labeled process names.

Both v3 fixtures report Ubuntu 24.04.5 LTS, kernel `7.0.14-linuxkit`, no `/dev/kvm` character device and no `/sys/class/misc/kvm` entry. This establishes absence in these inspected fixtures, not an exhaustive claim about all host virtualization capabilities. Docker's [installation prerequisites](https://docs.docker.com/ai/sandboxes/install/) require working KVM for local Linux sandboxes and nested virtualization when Linux runs inside a VM. Consequently the demonstrated container is usable for store preflight, not a supported operational local-SBX host. No privileged container, KVM device mapping, host OS change or cloud fallback was attempted.

Docker documents [Linux file fallback and domain-based placeholder injection](https://docs.docker.com/ai/sandboxes/configuration/credentials/) and [daemon-starting settings commands](https://docs.docker.com/ai/sandboxes/configuration/settings/). These explain prerequisites, not tested request authority. In particular, domain-scoped placeholder replacement does not itself demonstrate caller-specific restrictions. The fresh CLI help also describes placeholder substitution by target host. Authenticated child/grandchild requests, direct token/sentinel replay, header replacement, redirects, second-sink egress and independent validator exclusion remain untested. Native hooks, MCP/plugins/instructions, system resolver/proxy behavior, inner resource enforcement and whole-runtime identity/refusal remain untested. Existing historical subsets remain separate.

## Reproduce and continue

Prepare the exact official Linux archive, verify its digest, safely extract into a fresh external directory and verify every bundle digest from the v3 manifest. Prepare the pinned official image separately; the probe always uses `--pull=never`. With `crewshal_sbx_bundle` set to the real extracted `docker-sbx` directory and a fresh external report path:

```sh
rtk proxy .venv/bin/python -m scripts.probe_broker_environment \
  --bundle "$crewshal_sbx_bundle" \
  --manifest docs/qualification/phase-2c-broker-environment-v3.json \
  --manifest-sha256 27107761f400de9454f855b5ffe319b264dba44b1385aca67d2b4bfe263d9daf \
  --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock \
  --output /private/tmp/crewshal-broker-new-observation.json
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_broker_environment
```

Exit 2 always preserves denial. Existing reports and dangling symlinks refuse before fixture creation. Eight offline methods cover authority separation, failed/missing/reordered oracles and cleanup, manifest/grant/configuration/source drift, unknown bundles/remote endpoints, effective privilege/mount/device/resource drift, preserved failures and exclusive reports. These are deterministic regressions over fresh synthetic inputs and committed sanitized observations, not fresh broker qualification. One initial offline invocation preceded copying the repeat fixture and failed with a missing file; the fixture was added and all eight methods rerun successfully.

Next supply a disposable Ubuntu 24.04+ host with demonstrably working KVM, or a separate macOS OS credential domain. The 512 MiB/one-CPU outer guest allocation remains pending. Freeze disk/scratch/startup/total limits, daemon/template/native-runtime identities and all effective configuration before any operational launch. Prove supported provider-free local dispatch and caller/request authority before accepting a design. If these prerequisites cannot be supplied, select another existing mechanism prospectively; do not implement a custom gateway or weaken the worker grant. Phase 2C remains blocked; Phase 2D is not authorized. Use [the continuation prompt](PHASE-2C-RESUME-PROMPT.md).
