# Phase 2C resource approval and operational freeze status

Date: 2026-10-02. Package 0.8.4. Status: **resource envelope approved; operational freeze and inner qualification blocked**.

The owner directly instructed this session to approve the linked [resource envelope](SBX-OPERATIONAL-PROPOSAL.md), then freeze operational identities and qualify inner enforcement. This is explicit authorization for the unchanged envelope. The [separate approval record](qualification/phase-2c-resource-approval-v1.json) binds the exact proposal, historical readiness snapshot and original protocol by SHA-256. It records the owner's instruction and all ceilings. It is a local session transcription, not a cryptographic attestation or an execution grant. The proposal and historical readiness documents remain byte-for-byte unchanged; their pending-approval statements describe the earlier checkpoint and are superseded only on resource authority by this record.

Approved bounds: 768 MiB aggregate host memory, one CPU, 128 host PIDs, zero swap; one 512 MiB/one-vCPU guest included in that aggregate; 8 GiB aggregate logical and allocated fixture disk; 128 MiB guest scratch; 32 MiB inner scratch; 16 MiB candidate; 120 seconds startup per fresh fixture; 600 seconds for both fixtures including cleanup, with the final 30 seconds reserved. Individual commands retain ten seconds and 65,536 bytes per stream. Worker and separate sequential validator retain 128 MiB, one CPU, 32 PIDs, zero swap and a five-second deadline. Empty worker network/credential grants and all twenty criteria remain unchanged. Resource approval permits no automatic limit increase, host purchase/resize or swap enablement.

## Operational identity freeze

No executable operational manifest has been frozen. Current SSH alias/user and approved authentication mechanism were requested this session; no current access was supplied at this checkpoint. No connection or remote operation was attempted. Historical host access and temporary paths cannot be reused as authority. The earlier second-host diagnostics remain historical, time-specific observations.

The known official SBX 0.46.0 Linux amd64 archive and all extracted regular-file identities remain in [the preparation record](qualification/phase-2c-amd64-preparation.json). This session verified the committed historical readiness bindings against current repository bytes; it did not reverify external archive bytes, reproduce extraction or execute any bundled program. Recorded bytes do not supply a template, inner image or native runtime identity.

The following bindings remain unresolved. Resolve them from the authorized current host and exact pinned release; record failures or unavailable mechanisms explicitly.

- Current host OS/kernel/architecture, twice-reproduced trusted KVM HLT, current headroom, credential-domain isolation and final diagnostic cleanup.
- Dedicated quota filesystem and effective aggregate cgroup controls, including logical disk accounting and all infrastructure descendants.
- Exact daemon launch, libraries/VMM/kernel/rootfs, environment/state paths and dynamic-download behavior.
- Immutable architecture-matching template, worker image, separate validator image, native runtime and complete toolchain identities.
- Exact effective hooks, MCP, plugins, instructions, shared skills, SSH, clipboard, proxy/resolver, network and download configuration.
- Supported trusted provider-free local dispatch, two independent sinks, worker/validator placement and cancellation/deadline commands.
- Prospectively bound observer/payload sources, sampling thresholds, output supervision, fresh paths and uniquely owned cleanup handles.

Current [Docker settings documentation](https://docs.docker.com/ai/sandboxes/configuration/settings/) describes daemon-starting settings operations and a default 10g Docker volume. This reinforces the existing requirement to resolve explicit disk configuration before creation under the approved 8 GiB aggregate. Current [Docker isolation documentation](https://docs.docker.com/ai/sandboxes/security/isolation/) describes sudo-capable default agents and a separate in-VM engine. Neither document establishes the required inner limits, and neither was treated as a pinned-release command/configuration identity. Public documentation review is preparation only; no settings or daemon command ran.

## Inner enforcement and next action

Inner enforcement is **not run**, not failed or passed. No worker, validator, broker request, daemon, VM or operational fixture was created. Every `execution_allowed` and `native_start_allowed` remains false. Offline tests verify recorded refusal behavior, not current Linux enforcement.

Supply current authorized disposable host access first. Reverify at least 939,524,096 available memory bytes, 10 GiB free disk, cgroup v2 and quota capability. Reproduce trusted KVM/help diagnostics with fresh prospective bindings. Resolve every identity above, freeze a separate complete operational manifest, then qualify the synthetic inner subset from [the existing acceptance checklist](PHASE-2C-READINESS.md) twice in fresh fixtures before native startup. Preserve all prior profiles and failures. Passing inner controls alone would still leave native/provider-free whole-runtime gates. No Phase 2D work is authorized.

Use [the continuation prompt and exact input files](PHASE-2C-RESUME-PROMPT.md). Resource approval need not be requested again while the proposal digest and ceilings remain unchanged. Changed bounds require a new owner decision.
