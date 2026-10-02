# Replacement Ubuntu host assessment

Date: 2026-10-02. Package 0.8.3. Scope: **Phase 2C trusted host diagnostics only**. The owner confirmed deletion of the previous VPS, then supplied current access to a new temporary VPS. The replacement was accessed with the newly supplied password, entered interactively; no password, address or private key is retained in these public files. No host was purchased or resized by this session.

## Current evidence

The replacement reports Ubuntu 24.04.5 LTS, x86_64 and kernel `6.8.0-142-generic`. `/dev/kvm` and its sysfs entry are present; device mode is 0660, owner/group root:kvm and device 10:232. Root filesystem is ext4. cgroup v2 exposes `cpuset cpu io memory hugetlb pids rdma misc`, with `cpu memory pids` in root subtree control. Controller availability does not establish effective aggregate or inner limits. Root mount options show no quota option; a dedicated quota-capable fixture filesystem and enforced quotas were not demonstrated.

The [replacement manifest](qualification/phase-2c-kvm-replacement-v1.json) was frozen before two separate Python HLT invocations. It binds the original trusted [protocol](qualification/phase-2c-kvm-host-v1.json) and [exact source](qualification/phase-2c-kvm-host-v1-probe.txt). The source digest was checked locally and remotely before execution. Both invocations return KVM API 12, exit reason 5, a passing trusted HLT result and closed process-owned handles. Each allocates 1,048,576 guest bytes with a five-second alarm and ten-second outer command limit. A 25-second trusted wrapper covers the two fresh subprocesses. No guest OS, image, filesystem or network is supplied.

See [sanitized observations](qualification/phase-2c-kvm-replacement-v1-observed.json). Successful administrative root diagnostics establish hardware access on this replacement only. They do not qualify a native worker or SBX runtime.

## Resource refusal

The existing [operational proposal](SBX-OPERATIONAL-PROPOSAL.md) requires 939,524,096 available bytes (896 MiB). Both observed samples fail this admission condition:

| Measurement | Available memory | Result |
|---|---:|---|
| Initial diagnostic | 535,486,464 bytes (510.68 MiB) | Below required headroom |
| Independent final diagnostic | 675,692,544 bytes (644.39 MiB) | Below required headroom |

Total memory is 1,008,185,344 bytes; swap is zero. Root disk free is 22,861,336,576 bytes initially and 22,849,523,712 bytes finally, above the proposed 10 GiB free-space requirement. Disk headroom does not establish the separate fixture quota requirement. Memory headroom changes over time; these are observations, not a capacity guarantee.

**Operational creation is refused.** The envelope is still proposed, not approved; even approval alone would not clear the observed memory failure. No services were stopped, caches dropped, swap enabled, packages installed, accounts/settings changed or quotas created to manufacture headroom. No SBX bundle was copied to the host. Native runtime/template/configuration identities and inner enforcement remain unresolved. The session requested either a host satisfying the existing proposal or an explicit decision to prepare a revised proposal; no choice is inferred from silence.

## Cleanup and limits

An independent final administrative `/proc/PID/fd` scan found no KVM VM/vCPU handles and no unreadable process entries. A separate process-name inventory found no `sbx`, `sandboxd` or named QEMU process. These are final snapshots, not evidence about every transient process. The supplementary inventory source was not prospectively pinned by digest; it is not promoted into the two HLT criteria. All SSH commands exited successfully and disconnected. No remote file, daemon, persistent VM, broker, worker, validator or provider operation was created by this session. Existing host services and unrelated resources were untouched.

SSH used a dedicated first-use known-hosts file and pinned that accepted key on subsequent connections. No independent console fingerprint was supplied; host authentication has that limitation. Public results are sanitized transcriptions, not signed attestations. This session's reproduction requires current authorized access; no earlier temporary directory or password is a prerequisite. The owner controls the temporary VPS lifecycle; deletion was not performed or assumed for the replacement.

## Reproduction and next gate

With current authorized access, inspect OS, architecture, KVM permissions, `/proc/meminfo`, disk space, cgroup controllers and quota capability. Verify the manifest/protocol/source digests before executing the exact HLT source twice, as fresh `timeout 10s python3` processes. Expect API 12 and exit reason 5; retain exceptions, timeouts and disagreement. Then independently inspect KVM handles, named infrastructure processes and resource headroom. The source can be supplied through a verified base64 argument to Python `compile`/`exec` without a remote file, as this session did. These are trusted hardware diagnostics only.

Next milestone remains **Phase 2C**: resolve the host resource refusal and owner envelope decision. Then resolve operational identities, freeze exact supported configuration/commands and qualify the [inner enforcement requirements](PHASE-2C-READINESS.md) before native startup. Every original grant, manifest and twenty whole-runtime criteria remain unchanged. No mandatory whole-runtime result passes and execution remains denied. Use [the next-session prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md); no Phase 2D work.
