# Phase 2C replacement-host and inner-enforcement readiness

Date: 2026-10-02. Package 0.8.3. Status: **blocked; operational approval and identities/enforcement unresolved**. The previous VPS was deleted. The first replacement failed memory headroom; a second replacement now passes trusted KVM HLT twice and sampled memory/disk headroom. Its matching Linux SBX version/help commands also succeed twice in a source-bound diagnostic profile. See [current host/help evidence](AMD64-HOST-PREFLIGHT.md). No operational or inner qualification follows. Resource approval remains unresolved. This document is a preparation checklist, not a frozen executable protocol, a qualification result or permission to start native code.

## Current identity boundary

The [readiness snapshot](qualification/phase-2c-readiness-v1.json) binds the existing amd64 preparation record and original qualification inputs by SHA-256. It preserves the original grant and limits. It distinguishes previously recorded artifact identities from unresolved operational identities; no unresolved value is replaced by a default. It is not consumed by an executor and cannot grant execution.

Previously recorded identities cover the official SBX 0.46.0 amd64 archive and every extracted regular file, including the CLI, shim, library, kernel and rootfs. These bytes were prepared earlier; this session reverified the existing archive and every file, copied verified bytes for help-only inspection and removed the remote diagnostic directory. No fresh download was needed. Reproduction must prepare fresh pinned bytes and does not require the old temporary directory. A new host must receive freshly verified copies. The arm64 Ubuntu store-test image is not an amd64 operational template.

Current second-host OS/kernel/KVM, sampled headroom and matching CLI/help identities are recorded separately; they are not a full operational environment binding. Still unresolved: approved envelope; quota filesystem and effective host cgroup; daemon launch and dynamic-download behavior; template and inner image digests; native runtime and toolchain bytes; effective configuration; supported trusted provider-free dispatch; worker/validator launch and deadline mechanism; exact observer sources, commands and cleanup handles. An archive digest does not supply these identities. The existing Darwin help assessor rejects non-Darwin hosts and must not be relabeled as a Linux operational harness.

## Replacement-host input

Supply a disposable Ubuntu 24.04+ x86_64 host with working KVM, current SSH alias/address, user and authentication method. Use current authorized access, not the deleted host's password. Record independent host-key verification or its absence privately. Do not commit an address, password, private key or raw administrative output.

Before further SBX operations, reverify OS/kernel/architecture, KVM permissions, actual execution and available headroom on the current authorized host. Reproduce the [frozen trusted 1 MiB HLT protocol](qualification/phase-2c-kvm-host-v1.json) twice with its exact [source](qualification/phase-2c-kvm-host-v1-probe.txt). Inspect final process/FD cleanup independently. Hardware access is not worker qualification.

The [resource proposal](SBX-OPERATIONAL-PROPOSAL.md) requires at least 896 MiB available memory, 10 GiB free disk, functioning cgroup v2 controllers and a quota-capable dedicated fixture filesystem. Total RAM alone does not establish headroom. Its 768 MiB aggregate, 512 MiB guest, 8 GiB fixture disk, startup and total deadlines still require owner approval. Refuse insufficient resources; do not resize, buy a replacement, enable swap, map host devices into the existing Docker fixtures or change worker limits implicitly.

## Operational freeze gate

The second host now has a separate source-bound credential-free Linux help-only profile. Any changed binary/source/environment needs a new prospective profile before invocation. It may inspect prospective version/help commands only. Settings commands may start infrastructure; do not use them as help-only observations. Pin exact supported commands from the tested release, not current web documentation alone.

Resolve each unresolved snapshot item with an immutable identity, exact configuration and independent observation source. Before creation, freeze a separate operational manifest binding all original twenty cases, grants, both resource layers, all artifacts/configuration/source hashes, exact commands, fresh fixture paths, two sink identities and unique owned cleanup handles. No native startup is allowed while any item is unresolved. Historical manifests and their bound sources stay unchanged.

Current Docker documentation describes a sudo-capable default agent with access to an in-VM engine. That arrangement does not establish Crewshal's inner boundary. See [Docker isolation](https://docs.docker.com/ai/sandboxes/security/isolation/). Current [settings documentation](https://docs.docker.com/ai/sandboxes/configuration/settings/) also advertises a default Docker-volume size of 10g, which cannot be silently accepted inside an 8 GiB aggregate fixture budget. Resolve and test explicit supported disk settings for the pinned release before creation; sparse allocation alone does not establish the logical bound.

## Inner-enforcement acceptance before native startup

Use existing supported engine/supervision mechanisms. This checklist adds no custom gateway, launcher or model/tool loop. First exercise bounded synthetic payloads inside the exact intended inner image. The independent trusted observer stays outside the worker. Every payload/source, threshold, sampling interval and command must be frozen before invocation; the rows below are requirements, not executed commands or passes.

| Boundary | Required independent evidence |
|---|---|
| Placement and authority | Engine inspection plus kernel membership show the native entry point will start inside the worker boundary. Parent, child and detached grandchild remain there. No untrusted code runs before placement. Non-root identity, dropped capabilities, no-new-privileges and namespace/mount inspection agree. Attempts to use sudo, an engine socket, writable cgroups, parent namespaces or cgroup migration fail. |
| Memory and swap | Effective inner `memory.max` is 134,217,728 and `memory.swap.max` is 0. Bounded allocation stress reaches the control; observer captures memory events, terminal state and descendant cleanup. Do not disable the OOM killer. Capture corresponding aggregate host limits separately. |
| CPU | Effective `cpu.max` quota/period equals one CPU or is stricter. Bounded multi-process load reaches the controller; observer captures `cpu.stat` throttling and membership. A one-vCPU guest or CLI flag alone is insufficient. |
| Tasks | Effective `pids.max` is 32. A bounded task-creation payload reaches the limit; observer captures `pids.events`, membership and terminal state. The kernel controller counts tasks, including threads; do not reinterpret 32 as an extra allowance per process. |
| Deadline and cancellation | Supervisor outside the worker initiates termination at the five-second deadline. Independently timed heartbeat, recursive process membership, terminal outcome and `cgroup.events` establish descendant termination. Cancellation is tested separately. Killing only the initial PID or observing SSH disconnection is insufficient. Freeze a bounded cleanup interval and retain any late termination as failure. |
| Scratch, candidate and disk | Enforced 32 MiB inner scratch and 16 MiB candidate maximum are reached with bounded writes. Observer checks quota errors, bytes/modes and absence of writes outside the grant. Guest scratch is at most 128 MiB. Logical and allocated fixture disk remain within the approved 8 GiB aggregate, including images and logs. |
| Validator and repeatability | A separate sequential validator has the same original resource ceilings, no credentials/network, and an independently frozen candidate copy. Repeat in a second fresh fixture. Inspect owned process/cgroup/VM/disk/state removal; preserve failures and contradictory observations. |

Controller semantics are described by [Linux cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html); engine resource options by [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/). These support the prospective checks, not their enforcement on the diagnosed replacement host. Pin observed host/guest kernels and engines when applying them.

Passing this synthetic inner subset would still not qualify native hooks, MCP/plugins/instructions, native network/resolver/proxy behavior or credential mediation. A separate supported trusted request must reach a local sink with the exact synthetic header; worker/descendant/validator replay and unauthorized requests must fail at both sinks. Domain-based injection alone is not caller-specific authority. All twenty whole-runtime cases require native provider-free positive controls and two fresh runs. Any unavailable path retains denial.

## Continuation

Resume Phase 2C only. Resolve the resource decision; then reverify current second-host access, adequate headroom and hardware, resolve operational identities, freeze exact commands and qualify inner enforcement before native startup. Do not begin Phase 2D. Use [the updated prompt and exact input files](PHASE-2C-RESUME-PROMPT.md), adding this document and its readiness snapshot. No earlier temporary directory or deleted host is a prerequisite.
