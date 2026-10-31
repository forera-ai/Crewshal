# Supported server-task association feasibility

Date: 2026-10-31. Package checkpoint: `0.27.22`. Crewshal skill: `1.0.0`.
Base: `057c447e138cd03750a8244bee459491c3601d48` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result

Read-only feasibility work did not establish a supported association for the selected auxiliary route.
The current contracts expose separate identities without a verified connection between them.
The new findings change the failure boundary. They do not qualify worker control.
The translator remains unimplemented, and its attempt budget remains unused.

The [bounded source proposal](CREWSHAL-SERVER-ASSOCIATION-SOURCE-PROPOSAL-2026-10-31.md) specifies a possible extension and its limits.
That proposal remains unapproved and unimplemented.
No exact operational plan is ready. No operational approval is requested for a placeholder runner.

## New source findings

The selected provider uses Unsloth Studio, rather than Hermes's separate managed llama.cpp runtime.
Hermes's `get_prefill_progress` returns only a processed-token count.
Its source describes failures, idle state, and decoding as indistinguishable absent prefill observations.
Its model-status route also starts a loading-progress watcher and can adopt legacy model files.
Codex did not invoke these functions during feasibility work.
Neither inspected projection supplies the required auxiliary request identity.

Studio implements owner-only `GET /slots` forwarding through its existing authentication boundary.
Its forwarding code supplies the engine authentication internally.
This is a supported route in inspected source, rather than an invented endpoint.
Codex did not extract credentials or invoke this authenticated route.
The earlier unauthenticated HTTP 401 results remain historical.
An authenticated slot read alone would not establish the missing association.

Studio returns `X-Unsloth-Monitor-ID` for monitored responses.
Its inspected monitor record contains request status, usage, and monotonic timing fields.
It contains no native server-task identity or retained native-completion association.
The standard GGUF stream creates its own completion ID before it consumes the native generator.
The passthrough stream can retain native IDs, so completion-ID provenance depends on the actual route.
A Studio completion ID must not be treated as a native completion ID without route evidence.

The available native source emits `id_task` in slot records.
Its slot serializer retains the current or previous task, so `id_task` alone does not prove current activity.
The inspected serializer does not emit the native `oaicompat_cmpl_id` beside that task identity.
Native completion IDs and native task IDs therefore cannot be joined through this inspected slot contract.
The source-to-loaded-binary relationship remains unverified. Source inspection does not establish actual binary behavior.

Studio's inspected `_LlamaUpstream` also permits one transport recovery and retargeting operation.
This finding concerns that code path. It does not establish that the selected auxiliary request used it.
A later protected-route contract must address such recovery explicitly and preserve uncertain submissions without replay.

## Current bindings and preservation

Current local `turn_context` metadata identifies the supervisor as `gpt-6.1-sol`.
The checkout started clean. Both version declarations contained `0.27.21`.
The canonical remote matches `https://github.com/forera-ai/Crewshal.git`.
RTK reports `1.1.0`. All four repository skill files match their installed counterparts.
The three companion skills loaded from the paths required by the Crewshal skill.

The current selected server process and port differ from the historical observations.
Its observed arguments retain Ornith `UD-Q4_K_XL`, context `93696`, and one slot.
This is process-argument evidence. It does not independently establish the loaded context or request behavior.
Codex performed no service action and did not change the selected provider, profile, or model.

The accepted candidate's preservation checker exited 0.
It verified 618 preserved private files, 31 candidate files, 12 installed source hashes, and 22 unchanged support files.
It also verified the profile, SOUL, cumulative patch applicability, and recorded 97-test acceptance inputs.
The 97-test result remains the earlier guarded run. This session did not rerun that suite.
The cumulative patch SHA-256 remains `b0ab63564e43011f9973c0ff13999ee569572dbfc7ad1d3ae12bd211d7d8b03c`.
The candidate manifest SHA-256 remains `0ff31bcd6ed9c52cc77a1d9cf78152625c7a66e8792310bd56eec534ee35f66d`.
The earlier source attempt and both corrections remain consumed.

The synthetic Jev check returned probability `0.98`, confidence `0.96`, reported cost `0`, and latency `455` milliseconds.
It confirms one supervisor decision path only. Actual total billing remains unknown.
It does not qualify new Hermes bindings or replace worker readiness.

## Evidence and limitations

Private evidence resides in `server-association-20261031-01a193ca` under the preserved S1b root.
`capture_feasibility.py` records exact source ranges, full source hashes, selected process fields, and individual command exits.
`feasibility.json` records the source limitations and current process observation.
The source capture covers fourteen files. It excludes credential stores and raw profile contents.
Starting manifests preserve the private root and tracked repository files before publication edits.

Graph work used Verify evidence and relevant one-hop calls in both directions.
Hermes generation `2026-09-02T17:14:19Z` remains stale.
The graph snippet returned `source not available`; current source reads supplied the evidence.
Coverage reported changed metadata, untracked files, and one missing historical route file.
The current caller resides in `agent/chat_completion_local.py`.
The listed graph projects contain no Studio or native source project. Those sources used direct inspection.
No graph result establishes complete code coverage or absence of another supported mechanism.
The conclusion is bounded: no usable association was established through the inspected current contracts.

Early exploration included missing-path errors, a missing `psutil` import, and an unavailable native Git identity.
The corrected process observation used the installed Hermes interpreter with `psutil`.
The native tree has no Git metadata. Its file hashes preserve the inspected source identity instead.
Truncated exploratory output supplied no complete-read or test-pass claim.
The private review record retains these limitations.

Private source evidence used Darwin `27.2.0`, arm64, and CPython `3.11.14`.
Publication checks record their own environment and exact results in the private closure record.
Product suites, Ruff, mypy, wheel builds, and installation checks are not required for this documentation checkpoint.
They remain not run. Linux checks remain deferred under ADR 0009.
No worker, local inference, authenticated HTTP observation, candidate application, profile edit, or restart ran.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.

Use the [next prompt](CREWSHAL-SERVER-ASSOCIATION-NEXT-SESSION-2026-10-31.md) after the exact source-scope decision.
