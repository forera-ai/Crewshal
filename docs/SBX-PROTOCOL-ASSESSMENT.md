# SBX prospective protocol assessment

Date: 2026-10-02. Package 0.7.0. **Phase 2C remains blocked and execution remains denied.** The [resource/configuration protocol](SBX-RESOURCE-CONFIGURATION-PROTOCOL.md) specifies the unchanged worker limits, a separately accounted pending outer allocation, credential-store prerequisites and the exact remaining probes. This is a protocol/refusal checkpoint, not an operational containment or credential qualification.

The later [0.8.0 broker-store assessment](BROKER-ENVIRONMENT-ASSESSMENT.md) demonstrates isolated Linux synthetic store operations in a new separate profile. It does not change this frozen help-only evidence or qualify the operational broker.

## Frozen evidence

Manifest: [SBX protocol v1](qualification/phase-2c-sbx-protocol-v1.json), SHA-256 `976d7ad7b6fe4ef8b2c2dbea981851d03fb2b713942e8dcecab3f6ec24b13f79`. All twenty original cases, grant and limits remain identical to original v1. The manifest binds the protocol document and both source files. It was finalized before the delivered assessor invoked the binary; subsequent relevant changes require a new prospective profile, not an edited observation.

The same official v0.46.0 Darwin archive was prepared again because the earlier temporary extraction was absent. Download size: 133,447,662 bytes; preparation elapsed 12.62 seconds. Archive SHA-256 `1daa077a793bc048ef69acb33cb89d27ce0696efadf44df6466463f2a79d8adc`; CLI SHA-256 `cca2b8379897afa957f6f0fbe98ff45724ddb10e135f1b575232581fdc3caad3`. These match [the previous pinned preparation record](qualification/phase-2c-sbx-preparation.json). Preparation used the recorded official-public 2 GB/30-minute allowance. No template/image/provider download or global installation occurred. Archive digest matching establishes content identity, not an independent signature verification.

Two initial assessor invocations refused the release's symlinked `bin/sbx` before any subprocess. Preserve [first refusal](qualification/phase-2c-sbx-protocol-v1-refused-observed.json) and [repeat refusal](qualification/phase-2c-sbx-protocol-v1-refused-repeat.json). The real, digest-matched app executable was then passed explicitly without changing the protocol or runner. This is a path correction, not removal of the binary-identity refusal.

The [first completed assessment](qualification/phase-2c-sbx-protocol-v1-observed.json) and [fresh-home repeat](qualification/phase-2c-sbx-protocol-v1-repeat.json) each recorded six help/version commands, all exit zero, under empty inherited environment, synthetic HOME/XDG_CONFIG_HOME and macOS network denial. Both record SBX 0.46.0 and a 512 MiB advertised minimum. Both deny direct/nested qualification and operational launch. All twenty operational cases are unavailable in these records. The earlier ad hoc five-command help inspection was preparatory, not a frozen assessment or an operational pass.

No daemon, sandbox, worker, login or secret-store operation occurred. `secret set-custom --help` is help inspection only. Never promote that observation into a broker read/replay test. The source captures only a pinned help binary; its post-collection size cap does not qualify supervision of hostile output.

## Concrete remaining boundaries

Direct SBX worker sizing is incompatible with the observed advertised minimum. The prospective nested option accounts for a 512 MiB/one-CPU outer VM separately while retaining the 128 MiB/one-CPU/32-PID worker. That proposal remains unapproved and untested. The entire native runtime and descendants must be inside an independently enforced inner boundary; the SBX default sudo-capable agent and internal engine access cannot serve as that proof.

macOS's system Keychain is not isolated by changing HOME. Operational broker probes therefore require a disposable separate credential domain or a supported mechanism avoiding the real store. Neither has been supplied/tested. Sentinel masking does not demonstrate caller-specific request authority. Token and sentinel replay, redirects, authenticated descendant requests, independent validator exclusion and native configuration/network probes remain unavailable. The protocol names positive controls and parent/sink oracles so marker absence or a never-reached hook cannot become a pass.

Primary documentation checked on 2026-10-02: [credential storage and injection](https://docs.docker.com/ai/sandboxes/configuration/credentials/), [settings and daemon-start behavior](https://docs.docker.com/ai/sandboxes/configuration/settings/), [isolation and host execution surfaces](https://docs.docker.com/ai/sandboxes/security/isolation/). These describe candidacy and prerequisites, not observed operational behavior. Public Orka/Orchestrate reuse is still conditional; no integration evidence was added.

Seven offline acceptance methods cover incomplete/failed/duplicate/reordered help, operational-command refusal without spawning, original criterion/limit preservation, resource/configuration/source/command drift, unknown binary/manifest refusal, timeout/output refusal and sanitized environment/network wrapper. All 70 package tests and artifact/static checks passed; exact evidence is in [the handoff](HANDOFF.md). These are deterministic refusal tests; no new mandatory operational criterion passed.

Failures retained: an initial test compared the network-denial substring against the argv list instead of its profile argument; corrected and rerun. A manifest preparation command used the global Python without installed Crewshal dependencies and failed; rerun with the project interpreter before final freezing. Neither failure is counted as passing evidence. The symlink refusals remain recorded as refusals.

## Reproduction and continuation

Prepare the exact official archive from the URL/digests in the prior preparation record into a fresh external directory. Verify the archive and real executable digests. Set `crewshal_sbx_binary` to the real executable path, not the release symlink. No earlier temporary directory is required. With a fresh external report path:

```sh
rtk proxy .venv/bin/python -m scripts.assess_sbx_protocol \
  --binary "$crewshal_sbx_binary" \
  --manifest docs/qualification/phase-2c-sbx-protocol-v1.json \
  --manifest-sha256 976d7ad7b6fe4ef8b2c2dbea981851d03fb2b713942e8dcecab3f6ec24b13f79 \
  --output /private/tmp/crewshal-sbx-new-assessment.json
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_protocol
```

The assessor returns 2 even when help inspection succeeds. Missing or changed binaries/protocols cannot authorize a launch. No operational command is exposed. Reports are created exclusively with mode 0600; existing files/symlinks cannot be overwritten.

Next work is **Phase 2C only**: supply/approve the separate broker test environment and explicit outer resource envelope, or select another existing mechanism meeting the frozen worker profile. Fill and freeze operational identities/limits/configuration, run the independent synthetic probes, then seek design acceptance from that concrete evidence. Existing profiles remain separate. No Phase 2D prompt or runtime execution authorization is delivered. Use [the updated resumption prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md).
