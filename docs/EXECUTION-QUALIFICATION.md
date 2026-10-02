# Phase 2C qualification checkpoint

Date: 2026-10-02. Outcome: **blocked, denied profile**. Package 0.3.0 adds compatible qualification record/refusal APIs and bounded assessment utilities; it does not complete Phase 2C. No worker was launched, no containment case passed, and Phase 2D is not authorized.

## Frozen protocol and evidence

[Protocol v1](qualification/phase-2c-v1.json) was frozen before the first substrate preflight. Its SHA-256 is `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. The first bounded preflight used an inline Python command with the same explicit endpoint, empty environment, synthetic HOME and ten-second command timeout. The delivered repeatable preflight utility was then rerun. No malicious worker payload was run before or after this preflight.

The protocol defines 20 mandatory cases, exact intended grants and synthetic criteria. The [observed record](qualification/phase-2c-observed.json) contains the exact version/health commands, exits, stdout/stderr digests, OS and identity bindings. Every substrate case is **unavailable**, including whole-boundary configuration/refusal cases. Offline refusal fixtures are separate evidence; they do not upgrade a substrate case.

The intended worker may read `/input` and `/candidate/owned`, write only `/candidate/owned`, and use `/scratch`. Network and credentials are empty grants. Original checkout, coordinator state, host home, credential stores, SSH agent and Docker socket are excluded. Limits are 5 seconds for worker deadline, 10 seconds per probe, 65,536 captured output bytes, 32 PIDs, 128 MiB and one CPU. No image pull is implicit. These are frozen requirements, not enforced worker controls in this checkpoint.

The selected target remains a separately qualified Linux container. On macOS 27.2 build 26B5091g, arm64, Docker client 29.8.1 build 4a63305d74 was present. The coordinator queried only `unix:///var/run/docker.sock` using an empty synthetic Docker configuration. Server version failed with exit 1: `connect: no such file or directory`. No user context, alternative daemon, credential store or host home was inspected. Availability elsewhere is unknown. No Linux kernel, engine version, image digest or runtime configuration was qualified.

`scripts/qualify_phase_2c.py` is a preflight/denial harness only. It performs no worker/container launch, image pull or mount. Even if a daemon is available, the current utility records worker probes and accepted credential mediation as unavailable and exits 2. The malicious-payload runner, actual kill-tree supervision, effective runtime configuration capture and credential broker tests still need implementation after prerequisites are available. Temporary capture files are private; the persisted record is capped per output stream after capture. This utility is not intended to supervise arbitrary untrusted commands.

## Reuse assessment

The public repositories were cloned without inherited Git configuration or hooks, outside Crewshal. They are assessment inputs, not installed plugins, product dependencies or implementation sources. No third-party implementation was copied. Their MIT licenses require notices if code is reused later.

| Candidate and pinned revision | Behavior evidence | Concrete fit/gap and decision |
| --- | --- | --- |
| [Orchestrate, 1846530cf4383c4592d739601f3c9870e83d9a13](https://github.com/bestagentkits/orchestrate/tree/1846530cf4383c4592d739601f3c9870e83d9a13) | Tracked-file inventory and plugin scope inspected. This snapshot supplies Markdown skill/reference/runtime contracts, not an executable implementation of the requested start/observe/cancel boundary. A no-model executable seam test is unavailable. | Its documented lifecycle/observations are useful comparison criteria. Harness-dependent dispatch, worktrees and written policy cannot establish Crewshal containment, digest-bound grants, trusted capture or restart behavior. Do not adopt it as a qualified executor. |
| [Orka, 9e366915fc6cd6ede5aa47ac7a3b418a32ff528b](https://github.com/Dusttoo/orka/tree/9e366915fc6cd6ede5aa47ac7a3b418a32ff528b) | Its actual public execution-backend suite passed 20 synthetic tests with network denied. Additional pure native-helper probes replaced the provider key but retained another synthetic secret, SSH_AUTH_SOCK and injected hook settings. No Claude/provider or hook execution occurred. | Lifecycle negotiation, receipts and fencing are useful seams. The fake backend is not containment. Crewshal needs its own model/task/policy/scope/candidate binding, trusted evidence authority and durable recovery mapping. Helpers alone do not exclude ambient credentials/configuration. Do not adopt as-is; reassess behind a qualified outer boundary. |

The Orka helper source SHA-256 was `c8fe004a0a901d9c23ad8b822e91cabe7b0326e197421db1cfb96a95f28296b8`. See [the pinned helper](https://github.com/Dusttoo/orka/blob/9e366915fc6cd6ede5aa47ac7a3b418a32ff528b/scripts/native_gateway.py) and [backend implementation](https://github.com/Dusttoo/orka/blob/9e366915fc6cd6ede5aa47ac7a3b418a32ff528b/scripts/execution_backend.py). The helper probe is reproducible with `scripts/assess_orka_seam.py`; exit 2 preserves the three failed exclusion criteria. This is a bounded incompatibility observation, not a general security verdict about Orka. Production launch/cancellation and restart across a real isolated worker remain untested.

No new adapter, model/tool loop or custom process supervisor was added. Minimal new code only validates qualification records and performs trusted health/helper assessments. Reuse selection remains conditional until actual execution evidence is available.

## Record and authority boundary

`crewshal.qualification` supplies closed schema-1 records. Identity includes host OS/kernel/architecture, substrate/version/image, runtime, toolchain, configuration, exact grant, harness, protocol and credential-design digests. The preflight binds both its own source and the qualification module plus Python/package/dependency/client identity. Null image/runtime/design fields visibly deny qualification. Changing any identity field invalidates a previous record.

The trusted coordinator must supply current identity and actual observations. Missing records, each failed/unavailable case, missing/extra/duplicate cases and unresolved identity deny. Unsupported/boolean versions, unknown fields and an attempted `execution_allowed=true` are refused. An all-passing **synthetic fixture** only yields `qualified_for_later_authorization`; execution remains false. Nothing imports worker records as trusted authority, persists these records through SQLite or launches a worker. Existing Phase 2B verdicts remain incapable of granting execution. Schema validation and hashes are not signatures or defenses against a compromised trusted coordinator.

Eleven offline acceptance methods cover these failures and prospective identity invalidation. All 44 package tests, static checks and installed-wheel/CLI verification passed; exact commands are in [HANDOFF.md](HANDOFF.md). These results establish refusal behavior on the recorded macOS/Python host, not Linux containment or credential mediation.

## Smallest resumption conditions

1. Provide/approve an explicit local Linux engine endpoint and a pinned available image/toolchain for synthetic-only qualification. Do not infer another Docker context or start/install a VM silently.
2. Specify and accept a credential mediation design with no real secrets or host stores. Prove it with synthetic token replay/read/egress and separate credential-free validation cases. A broker token exposed to arbitrary descendants remains a blocking design issue.
3. Implement the bounded no-model worker probe runner for the frozen protocol. Capture exact configuration/grants/commands, independently verify parent-side fixture bytes/modes and local sink traffic, and test detached descendants, cancellation and deadlines.
4. Reassess pinned public seams from that evidence. Any failed/unavailable mandatory case keeps the profile denied. Amend the protocol prospectively with reasons and invalidate old results; never remove a failed case after observing it.

Resume only Phase 2C with [the resumption prompt](PHASE-2C-RESUME-PROMPT.md). No Phase 2D prompt is delivered.
