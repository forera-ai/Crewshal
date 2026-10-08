# 0003 — End the SBX dependency; test a direct Linux qualification profile

Date: 2026-10-06. Status: **proposed owner decision; no replacement execution is authorized by this file**. This addresses the owner's instruction to make effective progress past Phase 2C. It does not mark Phase 2C passed or authorize Phase 2D.

## Decision presented for approval

Retire SBX 0.46.0 from the active Phase 2C pilot route. Preserve its findings and failed observations, but stop spending sessions trying to reconstruct private storage contracts. Test one direct Linux profile using existing bubblewrap, setpriv, systemd/cgroup v2 and kernel filesystem limits, with the native CLI's existing tool sandbox and an existing external credential proxy only if their separation is demonstrable. No nested SBX guest, KVM dependency, Docker-next image conversion, proprietary VMM, new model/tool loop or custom credential gateway.

This is a material change to the currently approved SBX-specific operational topology, despite retaining the original minimal Python architecture and Linux qualification objective. [ADR 0002](0002-minimal-architecture.md) reserves material decisions for the owner. Approval of this proposal authorizes bounded synthetic feasibility tests and preparation of this replacement profile, not agent writes, live provider calls, paid infrastructure or a release.

## Why the current route is NO-GO for this pilot

The [storage contract boundary](../PHASE-2C-STORAGE-CONTRACT.md) establishes seven unanswered private-fork/VMM/layout fields. The historical 3 GiB + 1 GiB upper/lower layout exceeds the approved 8 GiB logical ceiling even before backing and remaining objects. A smaller numerical hypothesis does not establish compatibility or guest apparent-size enforcement. No independent evidence supports choosing it.

There is also an independent credential issue. The original [twenty-case protocol](../qualification/phase-2c-v1.json) and later [operational proposal](../SBX-OPERATIONAL-PROPOSAL.md) require a trusted authenticated request to succeed while code-tool workers, descendants and the validator cannot read/replay its token or exercise its authenticated authority. A host/domain match alone cannot prove caller separation. OpenAI's current [sandbox guidance](https://developers.openai.com/api/docs/guides/agents-api/environments/security) likewise distinguishes keeping secrets outside an environment from trusting a proxy's access boundary. Documentation is comparison evidence; it is not a tested broker for this project.

The observed eCryptfs mechanism also returns EINVAL for copy-range and ENOTSUP for several image-related operations. Encrypting every engine/cache/image representation therefore adds compatibility work without establishing the independently required guest logical bound. This is a project-fit NO-GO under current evidence, not a general claim that SBX is insecure or incapable.

The original Phase 2C selected a qualified Linux container, not a requirement to use SBX. The SBX-specific approval was a later experimental route. Preserve all its historical inputs; do not retrospectively rewrite a denied result into a passed result.

## Concrete replacement boundary

| Role | Authority and proposed existing mechanisms |
|---|---|
| Trusted fixture supervisor and observer | Separate root setup role in an exclusively owned systemd slice; creates only new fixture mounts/cgroups; verifies vendor bytes and independent PID/FD/data/controller readback; never exports privileged handles to code tools. |
| Native CLI transport | Pinned Codex first, followed by separately qualified Claude Code. Read-only copied vendor root, empty synthetic HOME/configuration and only the frozen input/candidate/scratch views. Native requests use an explicit synthetic local endpoint; no ambient credentials, real provider or automatic downloads. |
| Code-tool worker and descendants | Existing native sandbox must place code execution in a nested filesystem/PID/network boundary before it starts; network and credentials stay empty. Broker socket, native transport FDs and parent environment are inaccessible. No unsandboxed fallback, user namespace, engine socket, mount/key API or cgroup migration. All native file-edit tools must also remain inside the outer filesystem grant. |
| External synthetic credential proxy | Existing supported proxy software, separate UID/network/mount scope; synthetic token outside both native and tool filesystems. A channel reachable only by the permitted native transport adds the exact token only for the allowed synthetic destination. Domain-only policy is insufficient. No custom broker implementation is approved. If existing interfaces cannot establish this separation, fail feasibility. |
| Sequential validator | New frozen candidate copy, read-only mount, empty credentials/network and the original limits. No reuse of native transport authority or worker mutable state. |

The native process and all code-tool descendants must share the **original aggregate worker cgroup limit**, not receive independent extra allowances. Native transport is a narrowly trusted request role, not authority to bypass filesystem, deadline, memory or task controls. Any separation assumption must be demonstrated with provider-free native positive controls and adversarial children; synthetic generic helpers alone do not qualify the native CLI.

The [Claude sandbox documentation](https://code.claude.com/docs/en/sandboxing) explicitly concerns the Bash tool; that is why an outer filesystem boundary must cover native file tools and all other process activity. Current docs cannot establish exact behavior of the pinned installed CLI. Native capability/version/configuration must be pinned and separately observed. If the 128 MiB/five-second native worker envelope is incompatible, record NO-GO and return that concrete contradiction to the owner; do not increase it automatically.

## Remove unnecessary storage complexity without weakening ceilings

Use a digest-bound read-only copied vendor root and inputs. Mutable candidate and scratch use separate exclusively owned kernel mounts. No writable guest block image exists in this proposed profile, so guest sparse files inside a second filesystem are not introduced. Do not count the host OS or unrelated installed files as a created experimental representation, and do not omit any copied input, output, mount, backing or deleted-open object actually owned by the fixture. The inventory convention remains explicit and independently checked.

First test a deliberately narrow combination of kernel tmpfs capacity/inode bounds and hard RLIMIT_FSIZE. Physical tmpfs size alone does **not** bound sparse apparent files. The logical oracle must cover inode cardinality, per-file length, directory/symlink metadata, aliases and deleted-open FDs; a sum over existing pathnames alone is insufficient. Choose stricter per-file/inode bounds only after showing that the actual intended tiny pilot workflow works under them. No numerical settings are silently declared universal or compatible in this proposal. Existing quota alternatives may be compared only if this first mechanism fails; do not launch another open-ended filesystem investigation.

All original grant exclusions and twenty criteria remain unchanged. Worker/native process tree and sequential validator each retain 134217728 memory bytes, zero swap, one CPU, 32 tasks and five seconds; commands ten seconds/65536 bytes per stream. Aggregate diagnostic processes retain 805306368 memory bytes, one CPU, 128 tasks, zero swap; disk logical and allocated each 8589934592 bytes. Candidate remains at most 16777216, scratch 33554432. No new guest is created, and the former SBX guest ceiling is not repurposed as extra native memory. Startup remains at most 120 seconds per fixture; two fixtures and cleanup at most 600 seconds, with final 30 reserved. If any required accounting or controller cannot be enforced, stop before hostile/native execution.

## Finite acceptance sequence and stop rules

1. **Admission and mechanism:** use an owner-accessible existing disposable local Linux environment. Read-only identity/controller/helper admission first; pin every actual source/helper/library/kernel before mutation. Reuse no credentials or old fixture artifacts. Test candidate/scratch logical and allocated bounds, deleted-open charging, containment, cgroup placement, deadline and cleanup twice with fresh synthetic fixtures. Observe the actual architecture; aarch64 is acceptable only for a matching aarch64 runtime profile. No amd64/KVM claim.
2. **Credential separation:** before adopting any proxy, prove one exact synthetic token reaches only the permitted sink through a permitted transport; direct worker/child/detached-grandchild/validator access, token read/replay, header substitution, cross-destination and redirects fail at both sinks. Positive controls verify sinks. Freeze exact proxy config/identity/channel placement. An inability to exercise actor separation is a terminal NO-GO, not a reason to build a custom gateway.
3. **Native conformance:** freeze complete native profile after trusted discovery and before hostile native/tool cases. Replay fixed provider-shaped synthetic responses only to exercise native dispatch and malicious tools/hooks/configuration. No real model request or new model loop. Demonstrate startup and deterministic fixture work within original limits. Test every original criterion on the same complete profile twice; complementary historical subsets do not compose into a pass.
4. **Closure:** only all mandatory independent passes yield qualification for later authorization. Execution remains false until the separate owner execution gate. Preserve failures, scope cleanup and publish the coherent checkpoint. Phase 2D/live spending remains separately authorized.

Each step has one concrete GO/NO-GO output. Do not restart public-source/SBX documentation research when it fails. The mechanism/broker/native batch must be concretely source-bound on the observed substrate before it runs; this ADR is not that executable manifest. Do not request a paid host merely to explore. A necessary paid-host batch requires exact commands, necessity, duration/cost exposure, unchanged ceilings and owner approval under [AGENTS.md](../../AGENTS.md).

## Alternatives and rollback

- Continue SBX: rejected for the pilot under current evidence; reconsider only with new version-matching contract and enforceable layout evidence, not another unchanged import retry.
- Domain-only proxy, exposed credentials or larger unapproved limits: rejected because they do not meet the accepted boundary.
- Mark 2C complete and build adapters: rejected; qualification/refusal code must remain unchanged and deny missing evidence.
- Custom executor/gateway or a third coding runtime: outside this approval request.

Rollback is simple: retain the denied original protocol and archived SBX findings; remove only newly owned replacement fixtures. No existing product schema, qualification decision or runtime execution grant changes through this proposal.

## Owner decision sought

Approve retiring SBX from the pilot path and the bounded direct Linux feasibility sequence above, including the explicit native-transport/code-tool separation? This retains all twenty tests and resource ceilings. It authorizes no paid host, credential recovery, real provider call, agent write or Phase 2D. If approved, separately obtain owner-supplied access to an existing test Linux shell only when the concrete admission batch is ready.
