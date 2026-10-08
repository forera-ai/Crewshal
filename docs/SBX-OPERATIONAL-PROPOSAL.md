# Phase 2C operational SBX proposal

Date: 2026-10-02. Status: **pending owner resource decision and current host access**. This document is a reviewable preparation checkpoint, not a frozen executable protocol or an execution grant. Every `execution_allowed` remains false. The twenty original criteria and earlier prospective manifests remain unchanged.

## Prepared architecture-matching artifacts

The official Docker SBX v0.46.0 Linux amd64 static archive was downloaded and extracted locally, without running any bundled program or installation script. Its 82,815,215 bytes match the SHA-256 published by the GitHub release API: `edd86e2f21559e190723fd884c3a1dced161a555afdff85c5921ed45e7d6d56e`. Preparation took 11.19 seconds, within the previously recorded 2 GB/30-minute preparation allowance. Extraction used Python's `data` filter and checked an expanded-size ceiling. No image or template was downloaded.

The [preparation record](qualification/phase-2c-amd64-preparation.json) records every extracted regular file, size, mode and digest. CLI SHA-256: `530f1d5b8ec662946e33c46a454fc17381790b6c5f13d0922d050a82e57d75a2`. Bundled x86_64 guest kernel SHA-256: `ee7877107ca754b22ef37e455293ff05edc87fac2a204d9630621ba3f3440916`; rootfs SHA-256: `ca4412572eb0be56f1e66524ea7124fe615d739bda0ce11b55a87e60bf9d4831`. Matching a published digest establishes identity; no independent signature/provenance verification was performed. These identities do not qualify a native runtime.

Reproduce from the exact `url`, `expected_sha256` and `expected_bytes` in the record into a new external directory. Verify before extraction; reject absolute/escaping paths, links escaping the extraction root, special files and excessive expanded sizes. Never run `install.sh`. Earlier temporary directories are not prerequisites. The arm64 bundle and Darwin help assessor cannot be substituted for this architecture.

## Concrete resource decision

The following ceilings are proposed, not approved or measured. Exceeding a ceiling stops the experiment; it does not authorize resizing the host or raising a worker limit.

| Layer | Proposed ceiling |
|---|---|
| Aggregate host experiment processes | 768 MiB (805,306,368 bytes), one CPU, 128 host PIDs, zero swap; includes daemon, VMM/guest allocation, sinks and monitors |
| One SBX guest | 512 MiB (536,870,912 bytes), one vCPU; its allocation is included in the host aggregate, not added twice |
| Entire inner native worker and descendants | Original 128 MiB (134,217,728 bytes), one CPU, 32 PIDs, zero swap, five-second deadline |
| Separate validator | Same original memory/CPU/PID/deadline ceilings; sequential with worker; zero credentials and network |
| Aggregate fixture disk | 8 GiB (8,589,934,592 bytes), including bundle copies, images, guest disks, state, logs and fixtures; enforce allocated and logical bounds |
| Guest transient scratch | 128 MiB (134,217,728 bytes), included in guest memory/disk accounting |
| Inner scratch | 32 MiB (33,554,432 bytes), included in the worker ceiling; approved synthetic writable candidate maximum 16 MiB |
| Startup | 120 seconds per fresh fixture |
| Full two-fixture operational experiment | 600 seconds including cleanup; reserve final 30 seconds for cleanup |
| Individual captured command | Original ten-second probe limit and 65,536 bytes per stream; startup is separately supervised infrastructure |

Before creation, independently verify at least 896 MiB available host memory (aggregate ceiling plus 128 MiB OS headroom), at least 10 GiB free disk, working cgroup v2 controls and a quota-capable dedicated fixture filesystem. The prior 961 MiB total-RAM observation does not establish this available-memory condition. If the temporary host cannot meet it, record unavailable; do not allocate a paid replacement or enable swap implicitly. Host diagnostics alone do not consume this proposed operational grant.

Only trusted infrastructure may execute outside the inner worker. A supervisor outside that boundary must enforce the worker deadline and remove its entire cgroup, including detached descendants. Capture effective cgroup files, engine inspection and process membership before/after each invocation. Prove denial of sudo/root escalation, engine sockets, writable cgroups and parent namespace access before starting native code. If existing supported SBX mechanisms cannot establish the mapping, stop without building a custom gateway or runtime launcher.

## Freeze-before-start sequence

1. Obtain current SSH alias/user and an approved authentication mechanism. Do not reuse the prior shared password or infer that its host survives. Reverify OS, architecture, KVM HLT twice, resources and final diagnostic cleanup. Record host-key verification limits privately; do not commit address or authentication material.
2. Freeze a new diagnostic/help-only manifest and exact source before running the matching binary. Use a credential-free account, synthetic state/home and empty environment; inspect only prospective version/help commands. Do not run settings, daemon, secret or create commands during this step. Preserve failures and terminal outcomes.
3. Resolve and pin every daemon/VMM/library/kernel/rootfs/template/image/native runtime/toolchain identity, exact commands, configuration files and effective setting names. Pin daemon behavior that could trigger downloads, including the local model runtime. The prepared bundle supplies only some identities; template/image/runtime/configuration remain unavailable. Inspect supported configuration without consulting a real user store.
4. Prepare an enforceable aggregate host cgroup and quota filesystem, isolated synthetic broker state, two independently monitored local sinks and unique owned cleanup handles. Bind all paths, identities, source hashes, grants, authority separations and outputs in a new prospective operational manifest. No null identity or default becomes an approval.
5. After the concrete envelope is approved and the manifest is fully bound, qualify trusted infrastructure and inner enforcement first. Refuse native startup on drift, missing evidence or unavailable controls. Only then exercise all original cases with provider-free native positive controls and fresh fixtures twice. Preserve every failure and earlier result separately.
6. Remove only owned fixture resources. Independently inspect cgroups, process/FD inventories, owned disks/state, daemon and VM handles; no unscoped reset or unrelated resource deletion. Failure to establish cleanup remains failure, not success inferred from SSH disconnection.

## Credential and native gates

Docker's [credential documentation](https://docs.docker.com/ai/sandboxes/configuration/credentials/) describes host-side injection selected by service/domain and a headless Linux file-store fallback. Its [isolation documentation](https://docs.docker.com/ai/sandboxes/security/isolation/) describes sudo-capable agents and an in-VM engine. These are capability descriptions, not evidence of Crewshal's inner limits or caller-specific authenticated-request authority. Current documentation may differ from the pinned release; prospective behavior tests govern.

The permitted trusted provider-shaped request must reach one local sink with the exact synthetic header. Worker, child, detached grandchild and separate validator must fail unauthorized authenticated requests, token/sentinel replay, header replacement, cross-destination use and redirect forwarding at both monitored sinks. Network-empty worker grants remain unchanged. A supported mechanism must supply the separate trusted dispatch path; domain masking alone is insufficient. If that path or a provider-free native hook/tool positive control is unavailable, record unavailable and retain denial. No actual provider, login, custom credential gateway, model loop, adapter or Phase 2D work is authorized.

The next milestone remains **Phase 2C operational qualification**. Supply host access and decide this envelope, then complete and freeze operational identities before creation. No mandatory whole-runtime criterion passed during preparation.
