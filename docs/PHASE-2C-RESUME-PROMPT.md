# Phase 2C resumption prompt

Phase 2C remains incomplete. Package 0.8.10 resolves [isolated Docker authentication](ISOLATED-DOCKER-AUTHENTICATION.md). Historical new private account state worked in two fresh denied-network fixtures; current survival is unknown. Exact OCI metadata and deterministic archive are prepared. Supported local template import fails with 500/ENOSPC under conservative storage controls. Complete operational manifest and inner enforcement remain unavailable; all execution/native-start flags stay false.

Prior continuation checkpoint: package 0.8.11 adds [storage control investigation](STORAGE-CONTROL-INVESTIGATION.md). No runtime-compatible control is selected or qualified. Current retained-host connection context was absent from the 2026-10-05 session and requested; no remote operation or new freeze/qualification occurred. That access request is superseded by the cost policy below. Re-establish exact prerequisites only when a necessary approved Linux batch needs them.

Current policy, package 0.8.13: owner confirmed droplet removal on 2026-10-05. No retained-host access is available to assume, and host-only authentication/preparation must not be prerequisites for local development. Do not recover ambient credentials. Complete substantive changes locally; use VMware Ubuntu only when necessary and sufficient. Ask for a concrete droplet batch only when a necessary acceptance check cannot be satisfied locally. This supersedes earlier retention/access requirements; historical qualification evidence stays immutable.

Prior 0.8.14 checkpoint: [storage design and accounting](PHASE-2C-STORAGE-DESIGN.md) and [staged Linux batch](PHASE-2C-STORAGE-BATCH.md) add substantive local diagnostics. Private key/mount/bypass/observer setup and SBX compatibility remain unresolved. Historical resource/credential gates are unchanged.

Current 0.8.15 checkpoint: [two observed Linux storage fixtures](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md) resolve supported private key/mount setup and record 44 independent FD/PID/inode matches, with effective aggregate controls and scoped cleanup. Required native filesystem compatibility, complete runtime identities/layout and guest inner enforcement remain unresolved. Unsupported operations are not passes. The existing test Ubuntu VM is aarch64, was left running and is not an amd64/KVM qualification substrate. No credential is part of these inputs.

Current 0.8.16 checkpoint: [pinned SBX storage requirements](PINNED-SBX-STORAGE-REQUIREMENTS.md) bind fresh release bytes and eleven members, nine public source files, two statements and private replacement/patch limitations. EROFS base zero-write fallback is conditional; continuity copy-range EINVAL has no later plain-copy fallback. No supported cache/disk layout or guest apparent-size enforcement is established. Both new conservative ledgers refuse. No runtime, VM or paid-host operation ran.

Current 0.8.17 checkpoint: [release-era storage contract boundary](PHASE-2C-STORAGE-CONTRACT.md) pins ROOT_SIZE documentation, three Linux XDG roots and creation-command Docker size semantics. A command override is not reflected in settings-get and needs independent disk readback. Seven exact unanswered fields remain in the contract record. The smaller 1 GiB root/512 MiB Docker hypothesis is unvalidated and refuses; its 5,939,237,149-byte known subtotal is not admission. No runtime or host operation occurred.

Prior 0.8.18 checkpoint: [finite exit decision](decisions/0003-direct-linux-qualification.md) concludes the current SBX investigation is NO-GO for this pilot under available evidence. Direct Linux replacement topology is proposed, not approved. [Pinned read-only admission batch](PHASE-2C-DIRECT-LINUX-ADMISSION.md) is prepared; no Linux/native/broker test ran. Original twenty cases, resource ceilings and denial flags are unchanged. The current prompt below supersedes the prior instruction to keep reconstructing private SBX storage contracts. Do not repeat research-only closures or unchanged import attempts.

Prior 0.8.19 checkpoint: [actual direct Linux admission and final kernel fixtures](PHASE-2C-DIRECT-LINUX-ASSESSMENT.md) pass on the owner-accessible aarch64 test guest. ADR 0003 is owner-approved through a separate bound record. Kernel mechanism v5 passes twice with scoped cleanup; all native/broker and complete twenty-case gates remain unavailable. [Pinned native/proxy preparation](PHASE-2C-DIRECT-LINUX-NATIVE-PREREQUISITES.md) is covered by the existing bounded feasibility authority; official matching-platform archives were acquired and verified; isolated version/help passes twice. Actual native sandbox startup refuses under host AppArmor. Fixture-only AppArmor decision remains pending; no profile was loaded. Preserve failures, transport limitations and denial.

Current 0.8.20 checkpoint: [actual approved-policy setup failures](PHASE-2C-NATIVE-POLICY-ASSESSMENT.md) resolve the original fixture policy decision and isolate AppArmor disconnected `/proc` UID-map denial. Eight trusted setup attempts fail before payload. Scoped v4 setup-only `attach_disconnected` parses successfully but has never been loaded; its documented alias risk needs the directly requested consequential owner decision. Owned profiles, data, runtime files, units and aggregate cgroup were removed; global protection remains enabled. No native payload or complete qualification case passes.

## Initial prompt

```text
Continue Crewshal in /Volumes/X10Pro/Crewshal from 0.8.20, Phase 2C only. Keep caveman ultra, Jev advice and codebase-memory Verify active. Read AGENTS.md, HANDOFF.md, DEVELOPMENT-PLAN.md, ARCHITECTURE.md, ADRs 0002/0003 and PHASE-2C-NATIVE-POLICY-ASSESSMENT.md first. Confirm branch/state and graph generation/coverage. Preserve all historical qualification/source/profile bytes and unrelated dirty work.

ADR 0003 and the fixture-only v2 AppArmor policy are already approved. Do not ask again. Read native-apparmor-approval-v1.json and native-policy-readback-v1.py. Native setup v9/v10 fails before payload: kernel audit identifies a disconnected /proc UID-map path. chroot_relative alone does not fix it. Exact pending resolver is native-apparmor-proposal-v4.json/.profile: attach_disconnected only on trusted copied native bwrap setup, never payload. AppArmor's official manual warns of aliasing; the direct owner answer must authorize this consequential interpretation change before loading it. V4 has only parsed, never loaded. No global sysctl or payload denial may be weakened. If owner rejects it, investigate a supported reduced-root topology instead of bypassing protections.

Existing VMware Ubuntu is aarch64 kernel 7.0.0-38-generic. It was left running; do not infer current availability or recover ambient authentication. Use directly supplied guest authentication only, without persisting it in public files. Local VMware access is authorized; no new VM, paid host, provider, sign-in or credential-store access. Pinned deliberate archive preparation is already authorized; no new download approval is needed. Runtime automatic downloads remain forbidden.

If scoped v4 is approved, create fresh preparation from scripts/probe_direct_linux_native_discovery.py with the exact archives in native-artifacts-v1.json. Install/bind scripts/probe_direct_linux_mechanism_v5.py as its named preparation helper. Then unexecuted native_compatibility_v11.py prepares directly from the fresh original manifest.json: it does NOT need earlier compatibility runs/manifests. Its /var/tmp fixture path must match the exact policy attachment. Create a fresh owned aggregate slice, bind all installed sources/helpers/libraries/kernel/parser/ABI bytes, source/policy configuration and loaded policy hashes. Freeze effective parent controls before the v11 run. Use existing file-transfer APIs for manifest data, bounded 10-second/65536-byte command/status streams.

The supported direct tiny invocation is codex sandbox --permission-profile :workspace -C /scratch -- <literal command>. Native executes as host UID/GID 65534 inside systemd's reduced readonly RootDirectory, ProtectProc=invisible and inaccessible sys/shm. No outer user map or ProcSubset=pid: prior variants break scratch ownership or required readonly overflow UID metadata. Only exact native bwrap may establish tool namespaces; payload exec must enter crewshal-native-tool-v1 and retain userns/capability/mount denial across every exec. V11 checks four-byte scratch success, actual role, zero capabilities, NNP and one-byte memfd/userns refusal. Its success would be a capability subset, not full qualification. Preserve failures using new sources/profiles; never rewrite an executed variant.

Before full qualification, independently test actual alias/deleted-open/inherited-handle behavior and existing excluded canaries. The setup flag is never granted to payload. No unsafe pathname-only or physical-only accounting inference. Candidate/scratch/logical/allocated/inode/backing/deleted-open inventory must include every owned representation. Historical kernel/help/startup subsets cannot compose into a pass. Earlier copied prose and v5 admission-sample limitations are explicit in native-policy-limitations-v1.json and freeze-v5-limitation.json.

Original protocol SHA-256 fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563; all twenty cases, grants, exclusions and empty worker/validator credentials/network remain unchanged. Shared native/tool tree and sequential validator each retain 134217728 memory bytes, zero swap, one CPU, 32 tasks, five seconds. Aggregate retains 805306368 bytes, zero swap, one CPU, 128 tasks. Logical and allocated disk each <=8589934592; candidate <=16777216; scratch <=33554432. Startup <=120 seconds/fixture; two fixtures plus cleanup <=600 seconds, final 30 reserved. Do not add native allowances or silently increase limits.

Prove supported native/proxy transport separation with the pinned existing official Responses proxy and fixed synthetic provider-shaped responses. No custom executor, broker/gateway or new model/tool loop. Native must reach only the permitted authenticated sink; code workers, children, detached grandchildren and validator must not read/replay token, reach proxy/native FDs, substitute headers, cross destinations or follow unauthorized redirects. Use two independently monitored sinks with positive controls. Domain-only injection cannot qualify authority. Native file-edit tools remain inside the outer grant.

Freeze the complete native/broker/configuration/observer profile before hostile cases. Tiny agent startup/work must fit the original shared envelope; every original mandatory case must pass twice on that SAME complete profile. Missing/stale/failed/unavailable/malformed evidence still denies execution. Existing refusal APIs remain unchanged; agent execution and Phase 2D stay gated even after qualification until the separate owner execution decision.

Return concrete GO/NO-GO per capability stage, and ask for the smallest actual blocker resolver promptly. No SBX research-only closure, unchanged import retry or paid-host request merely to explore. At completed or real blocked boundary, remove only owned fixtures/profiles, verify cleanup without weakening global protection, update README/changelog/handoff/plan/this prompt and semantic version, commit and push the current branch under standing authorization. No merge, deployment or registry release.
```

## Exact input files

All paths are relative to `/Volumes/X10Pro/Crewshal`. No previous temporary directory, container, database or clone is a prerequisite.

- `AGENTS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/HANDOFF.md`
- `docs/DEVELOPMENT-PLAN.md`
- `docs/DEVELOPMENT.md`
- `docs/ARCHITECTURE.md`
- `docs/decisions/0002-minimal-architecture.md`
- `docs/STATE-AND-GATES.md`
- `docs/PHASE-2C-PROMPT.md`
- `docs/PHASE-2C-RESUME-PROMPT.md`
- `docs/EXECUTION-QUALIFICATION.md`
- `docs/LINUX-SUBSTRATE-PROBES.md`
- `docs/qualification/phase-2c-v1.json`
- `docs/qualification/phase-2c-observed.json`
- `docs/qualification/phase-2c-substrate-v2.json`
- `docs/qualification/phase-2c-substrate-v2-observed.json`
- `docs/qualification/phase-2c-substrate-v3.json`
- `docs/qualification/phase-2c-substrate-v3-observed.json`
- `docs/qualification/phase-2c-substrate-v4.json`
- `docs/qualification/phase-2c-substrate-v4-observed.json`
- `docs/qualification/phase-2c-substrate-v4-repeat.json`
- `src/crewshal/contracts.py`
- `src/crewshal/gates.py`
- `src/crewshal/durable.py`
- `src/crewshal/state.py`
- `src/crewshal/qualification.py`
- `scripts/qualify_phase_2c.py`
- `scripts/assess_orka_seam.py`
- `scripts/probe_linux_profile.py`
- `tests/acceptance/test_phase_2a.py`
- `tests/acceptance/test_phase_2b.py`
- `tests/acceptance/test_phase_2c.py`
- `tests/acceptance/test_phase_2c_substrate.py`
- `pyproject.toml`
- `requirements-dev.lock`

Additional 0.5.0 inputs:

- `docs/qualification/phase-2c-lifecycle-v1.json`
- `docs/qualification/phase-2c-lifecycle-v1-observed.json`
- `docs/qualification/phase-2c-lifecycle-v1-repeat.json`
- `scripts/probe_linux_lifecycle.py`
- `tests/acceptance/test_phase_2c_lifecycle.py`

Additional 0.6.0 inputs:

- `docs/NETWORK-SUBSTRATE-PROBES.md`
- `docs/qualification/phase-2c-network-v1.json`
- `docs/qualification/phase-2c-network-v1-observed.json`
- `docs/qualification/phase-2c-network-v1-runner.txt`
- `docs/qualification/phase-2c-network-v2.json`
- `docs/qualification/phase-2c-network-v2-observed.json`
- `docs/qualification/phase-2c-network-v2-runner.txt`
- `docs/qualification/phase-2c-network-v3.json`
- `docs/qualification/phase-2c-network-v3-observed.json`
- `docs/qualification/phase-2c-network-v3-repeat.json`
- `docs/qualification/phase-2c-sbx-preparation.json`
- `scripts/probe_linux_network.py`
- `scripts/network_client.py`
- `scripts/network_sink.py`
- `tests/acceptance/test_phase_2c_network.py`

Additional 0.7.0 inputs:

- `docs/SBX-RESOURCE-CONFIGURATION-PROTOCOL.md`
- `docs/SBX-PROTOCOL-ASSESSMENT.md`
- `docs/qualification/phase-2c-sbx-protocol-v1.json`
- `docs/qualification/phase-2c-sbx-protocol-v1-observed.json`
- `docs/qualification/phase-2c-sbx-protocol-v1-repeat.json`
- `docs/qualification/phase-2c-sbx-protocol-v1-refused-observed.json`
- `docs/qualification/phase-2c-sbx-protocol-v1-refused-repeat.json`
- `scripts/assess_sbx_protocol.py`
- `tests/acceptance/test_phase_2c_protocol.py`

Additional 0.8.0 inputs:

- `docs/BROKER-ENVIRONMENT-ASSESSMENT.md`
- `docs/qualification/phase-2c-broker-preparation.json`
- `docs/qualification/phase-2c-broker-environment-v1.json`
- `docs/qualification/phase-2c-broker-environment-v1-runner.txt`
- `docs/qualification/phase-2c-broker-environment-v1-observed.json`
- `docs/qualification/phase-2c-broker-environment-v2.json`
- `docs/qualification/phase-2c-broker-environment-v2-runner.txt`
- `docs/qualification/phase-2c-broker-environment-v2-observed.json`
- `docs/qualification/phase-2c-broker-environment-v3.json`
- `docs/qualification/phase-2c-broker-environment-v3-observed.json`
- `docs/qualification/phase-2c-broker-environment-v3-repeat.json`
- `scripts/probe_broker_environment.py`
- `tests/acceptance/test_phase_2c_broker_environment.py`

Additional 0.8.1 inputs:

- `docs/KVM-HOST-ASSESSMENT.md`
- `docs/qualification/phase-2c-kvm-host-v1.json`
- `docs/qualification/phase-2c-kvm-host-v1-probe.txt`
- `docs/qualification/phase-2c-kvm-host-v1-observed.json`

Additional 0.8.2 inputs:

- `docs/SBX-OPERATIONAL-PROPOSAL.md`
- `docs/qualification/phase-2c-amd64-preparation.json`

Additional 0.8.3 inputs:

- `docs/PHASE-2C-READINESS.md`
- `docs/qualification/phase-2c-readiness-v1.json`

Replacement diagnostic inputs in 0.8.3:

- `docs/REPLACEMENT-HOST-ASSESSMENT.md`
- `docs/qualification/phase-2c-kvm-replacement-v1.json`
- `docs/qualification/phase-2c-kvm-replacement-v1-observed.json`

Second-host and matching Linux help inputs in 0.8.3:

- `docs/AMD64-HOST-PREFLIGHT.md`
- `docs/qualification/phase-2c-kvm-replacement-v2.json`
- `docs/qualification/phase-2c-kvm-replacement-v2-observed.json`
- `docs/qualification/phase-2c-linux-amd64-help-v1.json`
- `docs/qualification/phase-2c-linux-amd64-help-v1-observed.json`
- `docs/qualification/phase-2c-linux-amd64-help-v2.json`
- `docs/qualification/phase-2c-linux-amd64-help-v2-runner.txt`
- `docs/qualification/phase-2c-linux-amd64-help-v2-observed.json`
- `docs/qualification/phase-2c-linux-amd64-cleanup-v1.json`

Additional 0.8.4 authority/freeze inputs:

- `docs/RESOURCE-APPROVAL-AND-FREEZE-STATUS.md`
- `docs/qualification/phase-2c-resource-approval-v1.json`

Additional 0.8.5 current-host and prospective diagnostic inputs:

- `docs/CURRENT-HOST-IDENTITY-PREPARATION.md`
- `docs/DAEMON-CONFIG-DIAGNOSTIC-PROPOSAL.md`
- `docs/qualification/phase-2c-current-help-v1-observed.json`
- `docs/qualification/phase-2c-current-help-v1-runner.txt`
- `docs/qualification/phase-2c-current-help-v1.json`
- `docs/qualification/phase-2c-current-host-toolchain-v1.json`
- `docs/qualification/phase-2c-current-host-v1-observed.json`
- `docs/qualification/phase-2c-current-host-v1-probe.txt`
- `docs/qualification/phase-2c-current-host-v1.json`
- `docs/qualification/phase-2c-current-inventory-v1-observed.json`
- `docs/qualification/phase-2c-current-inventory-v1-probe.txt`
- `docs/qualification/phase-2c-current-inventory-v1.json`
- `docs/qualification/phase-2c-current-preparation-v1-observed.json`
- `docs/qualification/phase-2c-current-preparation-v1-runner.txt`
- `docs/qualification/phase-2c-current-preparation-v1.json`
- `docs/qualification/phase-2c-daemon-config-diagnostic-v1-runner.txt`
- `docs/qualification/phase-2c-daemon-config-diagnostic-v1.json`
- `docs/qualification/phase-2c-template-metadata-v1.json`
- `docs/qualification/phase-2c-template-preparation-v1-observed.json`
- `docs/qualification/phase-2c-template-preparation-v1-runner.txt`
- `docs/qualification/phase-2c-template-preparation-v1.json`

Additional 0.8.6 diagnostic authority and observations:

- `docs/DAEMON-CONFIG-DIAGNOSTIC-ASSESSMENT.md`
- `docs/qualification/phase-2c-daemon-config-authorization-v1.json`
- `docs/qualification/phase-2c-daemon-config-diagnostic-v1-observed.json`
- `docs/qualification/phase-2c-daemon-config-diagnostic-v1-repeat.json`

Additional 0.8.7 inputs:

- `docs/CONTROL-RESOLUTION-ASSESSMENT.md`
- `docs/PHASE-2C-INFRASTRUCTURE-DISCOVERY-DECISION.md`
- `docs/qualification/phase-2c-config-controls-v1-observed.json`
- `docs/qualification/phase-2c-config-controls-v1-repeat.json`
- `docs/qualification/phase-2c-config-controls-v1-runner.txt`
- `docs/qualification/phase-2c-config-controls-v1.json`
- `docs/qualification/phase-2c-quota-prerequisite-v1-observed.json`
- `docs/qualification/phase-2c-quota-prerequisite-v1-runner.txt`
- `docs/qualification/phase-2c-quota-prerequisite-v1.json`
- `docs/qualification/phase-2c-quota-prerequisite-v2-observed.json`
- `docs/qualification/phase-2c-quota-prerequisite-v2-runner.txt`
- `docs/qualification/phase-2c-quota-prerequisite-v2.json`
- `docs/qualification/phase-2c-quota-prerequisite-v3-observed.json`
- `docs/qualification/phase-2c-quota-prerequisite-v3-runner.txt`
- `docs/qualification/phase-2c-quota-prerequisite-v3.json`
- `docs/qualification/phase-2c-logical-quota-v1-capture-limited.json`
- `docs/qualification/phase-2c-logical-quota-v1-observed.json`
- `docs/qualification/phase-2c-logical-quota-v1-runner.txt`
- `docs/qualification/phase-2c-logical-quota-v1.json`

Additional 0.8.8 inputs:

- `docs/GUEST-DISCOVERY-ASSESSMENT.md`
- `docs/qualification/phase-2c-discovery-admission-v1-observed.json`
- `docs/qualification/phase-2c-discovery-admission-v1-runner.txt`
- `docs/qualification/phase-2c-discovery-admission-v1-transport.txt`
- `docs/qualification/phase-2c-discovery-admission-v1.json`
- `docs/qualification/phase-2c-discovery-admission-v2-observed.json`
- `docs/qualification/phase-2c-discovery-admission-v2-runner.txt`
- `docs/qualification/phase-2c-discovery-admission-v2-transport.txt`
- `docs/qualification/phase-2c-discovery-admission-v2.json`
- `docs/qualification/phase-2c-discovery-authorization-v1.json`
- `docs/qualification/phase-2c-discovery-final-inventory-v1.json`
- `docs/qualification/phase-2c-discovery-freeze-status-v1.json`

Additional 0.8.9 maintenance input:

- `.gitattributes` (exact-path whitespace treatment preserves executed source bytes; no qualification change)

Additional 0.8.10 inputs:

- `docs/ISOLATED-DOCKER-AUTHENTICATION.md`
- `docs/qualification/phase-2c-auth-help-v1-observed.json`
- `docs/qualification/phase-2c-auth-help-v1.json`
- `docs/qualification/phase-2c-authenticated-discovery-v1-observed.json`
- `docs/qualification/phase-2c-authenticated-discovery-v1.json`
- `docs/qualification/phase-2c-authenticated-discovery-v2-observed.json`
- `docs/qualification/phase-2c-authenticated-discovery-v2.json`
- `docs/qualification/phase-2c-authenticated-discovery-v3-observed.json`
- `docs/qualification/phase-2c-authenticated-discovery-v3.json`
- `docs/qualification/phase-2c-authenticated-discovery-v4-observed.json`
- `docs/qualification/phase-2c-authenticated-discovery-v4.json`
- `docs/qualification/phase-2c-authenticated-freeze-status-v1.json`
- `docs/qualification/phase-2c-isolated-auth-authorization-v1.json`
- `docs/qualification/phase-2c-isolated-auth-final-inventory-v1.json`
- `docs/qualification/phase-2c-isolated-auth-v1-init-observed.json`
- `docs/qualification/phase-2c-isolated-auth-v1-observed.json`
- `docs/qualification/phase-2c-isolated-auth-v1.json`
- `docs/qualification/phase-2c-isolated-auth-v2-observed.json`
- `docs/qualification/phase-2c-isolated-auth-v2.json`
- `docs/qualification/phase-2c-isolated-auth-v3-init-observed.json`
- `docs/qualification/phase-2c-isolated-auth-v3-observed.json`
- `docs/qualification/phase-2c-isolated-auth-v3.json`
- `docs/qualification/phase-2c-oci-archive-v1-observed.json`
- `docs/qualification/phase-2c-oci-archive-v1.json`
- `docs/qualification/phase-2c-oci-metadata-v1-observed.json`
- `docs/qualification/phase-2c-oci-metadata-v1.json`
- `docs/qualification/phase-2c-auth-help-v1-runner.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v1-runner.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v1-transport.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v2-runner.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v2-transport.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v3-runner.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v3-transport.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v4-runner.txt`
- `docs/qualification/phase-2c-authenticated-discovery-v4-transport.txt`
- `docs/qualification/phase-2c-isolated-auth-v1-runner.txt`
- `docs/qualification/phase-2c-isolated-auth-v1-transport.txt`
- `docs/qualification/phase-2c-isolated-auth-v2-runner.txt`
- `docs/qualification/phase-2c-isolated-auth-v2-transport.txt`
- `docs/qualification/phase-2c-isolated-auth-v3-runner.txt`
- `docs/qualification/phase-2c-isolated-auth-v3-transport.txt`
- `docs/qualification/phase-2c-oci-archive-v1-runner.txt`
- `docs/qualification/phase-2c-oci-metadata-v1-runner.txt`

Additional 0.8.11 input:

- `docs/STORAGE-CONTROL-INVESTIGATION.md`

Additional 0.8.14 storage design/diagnostic inputs:

- `docs/PHASE-2C-STORAGE-DESIGN.md`
- `docs/PHASE-2C-STORAGE-BATCH.md`
- `docs/qualification/phase-2c-storage-preparation-v1.json`
- `docs/qualification/phase-2c-storage-refused-layout-v1.json`
- `docs/qualification/phase-2c-storage-lab-budget-v1.json`
- `docs/qualification/phase-2c-storage-local-observed-v1.json`
- `scripts/assess_storage_budget.py`
- `scripts/probe_storage_operations.py`
- `tests/acceptance/test_phase_2c_storage.py`

Additional 0.8.15 local Linux storage inputs:

- `docs/PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md`
- `docs/PHASE-2C-LOCAL-STORAGE-PROFILE.md`
- `docs/qualification/phase-2c-local-storage-bindings-v1.json`
- `docs/qualification/phase-2c-local-storage-bindings-v2.json`
- `docs/qualification/phase-2c-local-storage-bindings-v3.json`
- `docs/qualification/phase-2c-local-storage-bindings-v4.json`
- `docs/qualification/phase-2c-local-storage-bindings-v5.json`
- `docs/qualification/phase-2c-local-storage-bindings-v6.json`
- `docs/qualification/phase-2c-local-storage-boundary-v1.py`
- `docs/qualification/phase-2c-local-storage-budget-v2.json`
- `docs/qualification/phase-2c-local-storage-external-cleanup-v1.json`
- `docs/qualification/phase-2c-local-storage-observed-v6.json`
- `docs/qualification/phase-2c-local-storage-observer-v1.py`
- `docs/qualification/phase-2c-local-storage-observer-v2.py`
- `docs/qualification/phase-2c-local-storage-observer-v3.py`
- `docs/qualification/phase-2c-local-storage-observer-v4.py`
- `docs/qualification/phase-2c-local-storage-observer-v5.py`
- `docs/qualification/phase-2c-local-storage-preparation-v1.json`
- `docs/qualification/phase-2c-local-storage-prepare-v1.py`
- `docs/qualification/phase-2c-local-storage-prepare-v2.py`
- `docs/qualification/phase-2c-local-storage-profile-v1.json`
- `docs/qualification/phase-2c-local-storage-profile-v2.json`
- `docs/qualification/phase-2c-local-storage-profile-v3.json`
- `docs/qualification/phase-2c-local-storage-profile-v4.json`
- `docs/qualification/phase-2c-local-storage-profile-v5.json`
- `docs/qualification/phase-2c-local-storage-profile-v6.json`
- `docs/qualification/phase-2c-local-storage-readback-v1.py`
- `docs/qualification/phase-2c-local-storage-refusal-v1.json`
- `docs/qualification/phase-2c-local-storage-refusal-v2.json`
- `docs/qualification/phase-2c-local-storage-refusal-v3.json`
- `docs/qualification/phase-2c-local-storage-refusal-v4.json`
- `docs/qualification/phase-2c-local-storage-refusal-v5.json`
- `docs/qualification/phase-2c-local-storage-summary-v1.json`
- `scripts/observe_linux_storage.py`
- `scripts/prepare_linux_storage.py`
- `scripts/probe_storage_boundary.py`
- `tests/acceptance/test_phase_2c_storage_observer.py`

Additional 0.8.16 pinned storage requirements inputs:

- `docs/PINNED-SBX-STORAGE-REQUIREMENTS.md`
- `docs/qualification/phase-2c-sbx-storage-research-v1.json`
- `docs/qualification/phase-2c-sbx-storage-provenance-v1.json`
- `docs/qualification/phase-2c-sbx-storage-sbom-v1.json`
- `docs/qualification/phase-2c-sbx-storage-pruned-refused-v1.json`
- `docs/qualification/phase-2c-sbx-storage-inventory-v1.json`
- `docs/qualification/phase-2c-sbx-storage-readback-v1.py`
- `docs/qualification/sbx-storage-source-v1/bbolt-db.go.txt`
- `docs/qualification/sbx-storage-source-v1/bbolt-unix.go.txt`
- `docs/qualification/sbx-storage-source-v1/containerd-erofs-mount.go.txt`
- `docs/qualification/sbx-storage-source-v1/containerd-erofs.go.txt`
- `docs/qualification/sbx-storage-source-v1/containerd-store.go.txt`
- `docs/qualification/sbx-storage-source-v1/containerd-writer.go.txt`
- `docs/qualification/sbx-storage-source-v1/continuity-copy-linux.go.txt`
- `docs/qualification/sbx-storage-source-v1/continuity-copy.go.txt`
- `docs/qualification/sbx-storage-source-v1/erofs-io.c.txt`
- `docs/qualification/phase-2c-sbx-storage-verification-v1.json`
- `docs/qualification/sbx-storage-source-v1/LICENSE-bbolt-MIT.txt`
- `docs/qualification/sbx-storage-source-v1/LICENSE-containerd-Apache-2.0.txt`
- `docs/qualification/sbx-storage-source-v1/LICENSE-erofs-MIT.txt`
- `docs/qualification/sbx-storage-source-v1/COPYING-erofs.txt`
- `docs/qualification/sbx-storage-source-v1/README.md`

Additional 0.8.17 inputs:

- `docs/PHASE-2C-STORAGE-CONTRACT.md`
- `docs/qualification/phase-2c-sbx-storage-contract-v1.json`
- `docs/qualification/phase-2c-sbx-storage-small-hypothesis-v1.json`
- `docs/qualification/sbx-storage-docs-v1/troubleshooting.excerpt.txt`
- `docs/qualification/sbx-storage-docs-v1/architecture.excerpt.txt`
- `docs/qualification/sbx-storage-docs-v1/configuration-settings.excerpt.txt`

Additional 0.8.18 finite exit decision inputs:

- `docs/decisions/0003-direct-linux-qualification.md`
- `docs/PHASE-2C-DIRECT-LINUX-ADMISSION.md`
- `docs/qualification/phase-2c-exit-decision-v1.json`
- `docs/qualification/phase-2c-direct-linux-admission-v1.py`

Additional 0.8.19 direct Linux observation inputs:

- `docs/PHASE-2C-DIRECT-LINUX-ASSESSMENT.md`
- `docs/PHASE-2C-DIRECT-LINUX-NATIVE-PREREQUISITES.md`
- `docs/qualification/phase-2c-direct-linux-admission-observed-v1.json`
- `docs/qualification/phase-2c-direct-linux-bindings-v1.json`
- `docs/qualification/phase-2c-direct-linux-bindings-v2.json`
- `docs/qualification/phase-2c-direct-linux-bindings-v3.json`
- `docs/qualification/phase-2c-direct-linux-bindings-v4.json`
- `docs/qualification/phase-2c-direct-linux-bindings-v5.json`
- `docs/qualification/phase-2c-direct-linux-external-cleanup-v1.json`
- `docs/qualification/phase-2c-direct-linux-freeze-v1.json`
- `docs/qualification/phase-2c-direct-linux-freeze-v2.json`
- `docs/qualification/phase-2c-direct-linux-freeze-v3.json`
- `docs/qualification/phase-2c-direct-linux-freeze-v4.json`
- `docs/qualification/phase-2c-direct-linux-freeze-v5.json`
- `docs/qualification/phase-2c-direct-linux-mechanism-profile-v1.json`
- `docs/qualification/phase-2c-direct-linux-mechanism-profile-v2.json`
- `docs/qualification/phase-2c-direct-linux-mechanism-profile-v3.json`
- `docs/qualification/phase-2c-direct-linux-mechanism-profile-v4.json`
- `docs/qualification/phase-2c-direct-linux-mechanism-profile-v5.json`
- `docs/qualification/phase-2c-direct-linux-observed-v1.json`
- `docs/qualification/phase-2c-direct-linux-observed-v2.json`
- `docs/qualification/phase-2c-direct-linux-observed-v3.json`
- `docs/qualification/phase-2c-direct-linux-observed-v4.json`
- `docs/qualification/phase-2c-direct-linux-observed-v5.json`
- `docs/qualification/phase-2c-direct-linux-owner-approval-v1.json`
- `docs/qualification/phase-2c-direct-linux-readback-v1.py`
- `scripts/probe_direct_linux_mechanism.py`
- `scripts/probe_direct_linux_mechanism_v2.py`
- `scripts/probe_direct_linux_mechanism_v3.py`
- `scripts/probe_direct_linux_mechanism_v4.py`
- `scripts/probe_direct_linux_mechanism_v5.py`

Additional 0.8.19 native discovery, failed startup and proposed resolver inputs:

- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v1.profile`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v2.profile`
- `docs/qualification/phase-2c-direct-linux-native-artifacts-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-proposal-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-bindings-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-bindings-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-bindings-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-bindings-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-freeze-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-freeze-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-freeze-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-freeze-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-observed-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-observed-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-observed-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-observed-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-profile-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-profile-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-profile-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-discovery-profile-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-external-cleanup-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-observation-integrity-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-readback-v1.py`
- `scripts/probe_direct_linux_native_compatibility_v1.py`
- `scripts/probe_direct_linux_native_compatibility_v2.py`
- `scripts/probe_direct_linux_native_discovery.py`
- `scripts/probe_direct_linux_native_discovery_v2.py`
- `scripts/probe_direct_linux_native_discovery_v3.py`
- `scripts/probe_direct_linux_native_discovery_v4.py`

Additional 0.8.20 native policy/actual failure inputs:

- `docs/PHASE-2C-NATIVE-POLICY-ASSESSMENT.md`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-approval-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-audit-v9-v10.txt`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-parser-observed-v3-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v3.profile`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-apparmor-proposal-v4.profile`
- `docs/qualification/phase-2c-direct-linux-native-cleanup-observed-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-cleanup-profile-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v10.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v5.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v6.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v7.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v8.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-bindings-v9.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v10.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v5-limitation.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v5.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v6.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v7.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v8.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-freeze-v9.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v10.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v5.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v6.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v7.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v8.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-observed-v9.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-preparation-refused-v3.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v10.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v11.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v4.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v5.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v6.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v7.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v8.json`
- `docs/qualification/phase-2c-direct-linux-native-compatibility-profile-v9.json`
- `docs/qualification/phase-2c-direct-linux-native-external-cleanup-v2.json`
- `docs/qualification/phase-2c-direct-linux-native-policy-limitations-v1.json`
- `docs/qualification/phase-2c-direct-linux-native-policy-readback-v1.py`
- `scripts/cleanup_direct_linux_native_v2.py`
- `scripts/probe_direct_linux_native_compatibility_v10.py`
- `scripts/probe_direct_linux_native_compatibility_v11.py`
- `scripts/probe_direct_linux_native_compatibility_v3.py`
- `scripts/probe_direct_linux_native_compatibility_v4.py`
- `scripts/probe_direct_linux_native_compatibility_v5.py`
- `scripts/probe_direct_linux_native_compatibility_v6.py`
- `scripts/probe_direct_linux_native_compatibility_v7.py`
- `scripts/probe_direct_linux_native_compatibility_v8.py`
- `scripts/probe_direct_linux_native_compatibility_v9.py`
