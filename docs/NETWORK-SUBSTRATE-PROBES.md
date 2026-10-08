# Synthetic network subset and broker preparation

Date: 2026-10-02. Package 0.6.0. **Phase 2C remains incomplete and denied.** This is a separate synthetic socket profile, not a native Codex/Claude runtime qualification or a combined filesystem/process/network profile. Every execution flag remains false; the credential-design identity remains null.

## Preparation authority and provenance

The owner explicitly approved official public runtime/proxy preparation capped at 2 GB of downloads and 30 minutes, with no paid/provider calls or real credentials. The only new downloads were the official `python:3.12.14-alpine` image and the official SBX archive. Preparation completed within that ceiling; probes and offline regression work are separately classified below. No host credential configuration was read for the image pull: Docker used an empty synthetic HOME/config and the explicit socket.

Pinned Python content identity: `sha256:4c47124a8391cb7a9f571164147d154777cf012a4ece5f86097130d7a4478111`. Registry RepoDigest reported the same identity; unpacked image size was 78,869,135 bytes. Workers use this identity with `--pull=never`, not a mutable tag. The new image differs from the cached Alpine identity of previous profiles, so those results cannot be promoted into this record.

SBX release: [Docker v0.46.0](https://github.com/docker/sbx-releases/releases/tag/v0.46.0), build `991967dc90ce0d9a440cd1df1bdf3e395c5a2693`. Official Darwin archive: 133,447,662 bytes, SHA-256 `1daa077a793bc048ef69acb33cb89d27ce0696efadf44df6466463f2a79d8adc`; this matched the GitHub release asset digest. Extracted CLI SHA-256: `cca2b8379897afa957f6f0fbe98ff45724ddb10e135f1b575232581fdc3caad3`. Digest matching is integrity evidence, not an independent signature verification. This was an external session-local extraction, not a global installation or product dependency. Future sessions can reproduce from the pinned URL/digest; the previous temporary extraction is not required.

Read-only preparation evidence: [SBX record](qualification/phase-2c-sbx-preparation.json). `sbx --help`, `sbx version`, `sbx daemon start --help` and `sbx create --help` all exited zero with empty inherited environment, synthetic HOME/XDG_CONFIG_HOME and macOS network denial. No daemon or sandbox was started; no login, keychain, host credential store, secret import, provider or model call occurred. Help/version availability does not qualify any broker behavior.

## Frozen protocol and retained failures

The original [v1 qualification manifest](qualification/phase-2c-v1.json) remains SHA-256 `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. All twenty original criteria, worker grants and limits are retained verbatim. Each network manifest was frozen before its first launch and pins the runner, client, sink, existing helper and qualification module.

- [Network v1 manifest](qualification/phase-2c-network-v1.json), [failed observation](qualification/phase-2c-network-v1-observed.json) and [frozen runner snapshot](qualification/phase-2c-network-v1-runner.txt): failed before any client because pre-start sink addresses were empty. Cleanup passed; no network denial pass was inferred.
- [Network v2 manifest](qualification/phase-2c-network-v2.json), [failed observation](qualification/phase-2c-network-v2-observed.json) and [frozen runner snapshot](qualification/phase-2c-network-v2-runner.txt): added explicit dual-stack IPAM, but still inspected addresses before start and failed. V2's prospective amendment incorrectly diagnosed v1 as IPv6-only. Inspection evidence shows IPv4 and IPv6 enabled; the diagnosis is superseded, not silently rewritten.
- [Active v3 manifest](qualification/phase-2c-network-v3.json): reads and verifies post-start sink addresses. SHA-256 `82df51dd5acd305602b2cb826bbd56d305e5669c15e0d71c06c9f007bdf36eef`. [First v3 observation](qualification/phase-2c-network-v3-observed.json) and [fresh-fixture repeat](qualification/phase-2c-network-v3-repeat.json) both pass the bounded synthetic subset. Failed records remain failed. No runtime result is upgraded retrospectively.

## Grant, sinks and independent oracle

Each run creates only its own uniquely named/labeled internal dual-stack bridge, two sinks and three clients. Explicit randomly selected IPv4/IPv6 IPAM ranges are used; collision fails without modifying an existing network. No ports are published. Sink/control network access is a qualification-infrastructure grant, never the worker grant. Worker network is `none`; control clients are attached only to the internal fixture bridge.

All containers have the immutable Python image, UID/GID 65532, read-only root, all capabilities dropped, no-new-privileges, private PID/IPC, 32 PIDs, 128 MiB, one CPU and no Docker logging. Only newly created synthetic `/input` (read-only) and per-container `/candidate/owned` (writable) are bound; scratch is a 16 MiB noexec/nosuid/nodev tmpfs. Image defaults plus explicit HOME/bytecode settings form the exact inspected environment. No real checkout, coordinator state, host home, SSH agent or Docker socket is mounted. Engine grants are verified before start; running sink grants are verified again.

Two distinct sinks represent a primary local destination and another nonallowed destination. For each, clients attempt TCP, UDP and a DNS-format UDP query over IPv4 and IPv6: twelve cases per client. TCP/UDP use port 18080; DNS-wire uses synthetic port 15353. DNS messages carry a standard single-question header, an explicit synthetic `.invalid` name and A/IN question. This is an explicit DNS datagram attempt, not a system resolver, DNS-over-HTTPS/TLS or native runtime behavior test.

Connected controls run before and after the network-none worker and must receive exact echoes. Sinks independently append received bytes to coordinator-observed files that the worker cannot access. Parent evidence requires exactly twelve expected receipts before denial, no additional receipts after denial and exactly twenty-four distinct control receipts after the final control. Sink heartbeats must advance across the experiment. Worker outcomes must cover every attempt exactly once, record no connected/sent packet, and agree with an exit-zero nonrunning/non-OOM engine state. Protected source/original/coordinator fixture bytes/modes/link counts must remain unchanged. Cleanup of every owned handle and the owned network must succeed.

Both v3 runs recorded counts 12 before denial, 12 after denial and 24 after final control. All twelve worker attempts were denied. Every client exited zero; protected fixtures were unchanged; all owned containers/network were removed. The detailed records retain exact commands, pre-start/running engine grants, socket errors, payload bytes, sink receipts, kernel/Python versions and terminal states. The two runs use fresh containers, fixtures and networks.

Socket timeout is 0.2 seconds; client deadline is five seconds. Parent polling initiates KILL if that deadline is exceeded. Docker API commands have ten-second limits, so this is not a hard real-time supervision guarantee. Sinks are trusted bounded synthetic infrastructure with a sixty-second maximum loop and fixed packet sizes; cleanup normally ends them much earlier. Existing capture caps apply after collection. Arbitrary hostile output/process supervision is not qualified.

## Limits and remaining decision

Only the `network-egress` criterion passes in this **bounded synthetic** record; the other nineteen criteria are unavailable here. Prior filesystem and lifecycle records remain separate. Native Codex/Claude network and customization behavior, runtime hooks/MCP/plugins/instructions, whole-runtime configuration binding/refusal and accepted credential mediation remain unproved. The offline tests falsify record/oracle claims; they are not fresh containment tests. Public Orchestrate/Orka reuse remains unqualified and unchanged.

[Docker's installation guide](https://docs.docker.com/ai/sandboxes/install/) documents a sign-in prerequisite; this session did not attempt login or observe an operational login refusal. Local `sbx create --help` advertises a 512 MiB minimum sandbox allocation, while the frozen worker allocation is 128 MiB. Whether a separately specified outer VM can contain an inner 128 MiB worker is untested. Do not silently reinterpret the existing limit or launch a larger profile. The next prospective protocol must explicitly distinguish and approve outer preparation/runtime resources and the unchanged worker limits, or select another existing mechanism that meets the frozen profile.

[Docker's credential guide](https://docs.docker.com/ai/sandboxes/configuration/credentials/) describes proxy-managed sentinels and host-side header replacement. That supports candidacy only. Synthetic token read/replay, redirects, provider request authority by arbitrary descendants, local sink egress and separate validator/native configuration tests still need a prospectively frozen operational protocol and an accepted tested design. Hiding a token does not establish request authority. No custom gateway or unrestricted fallback is permitted. Owner acceptance follows concrete synthetic evidence; preparation approval is not design acceptance.

## Reproduction

The runner refuses drift in the manifest, original protocol, image environment and pinned source set before creating resources. From the checkout with the installed package and prepared immutable image, choose a fresh external output:

```sh
rtk proxy .venv/bin/python -m scripts.probe_linux_network \
  --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock \
  --manifest docs/qualification/phase-2c-network-v3.json \
  --manifest-sha256 82df51dd5acd305602b2cb826bbd56d305e5669c15e0d71c06c9f007bdf36eef \
  --output /private/tmp/crewshal-2c-new-network-observation.json
```

Exit 2 intentionally preserves full qualification denial, including when the network subset passes. No previous temporary directory/container/network/CLI extraction is required. If the image is absent, prospectively prepare it under an explicit bounded grant; the runner never pulls it. Continue only Phase 2C with [the updated prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md).
