# Selected transport integration: feasibility stop

Date: 2026-10-29. Package checkpoint: `0.27.18`. Crewshal skill: `1.0.0`.
Base: `61070f783522e59417eea8ef33618bb198d9d31c` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result and authority

The owner approved the private transport proposal and direct Sol 6.1 preparation.
The grant permits one implementation attempt and at most two targeted corrections.
It restricts candidate runtime edits to `agent/auxiliary_client.py` and `agent/auxiliary_stream_watchdog.py`.
It requires identification of the complete gateway identity and original supervisor deadline before editing.
The proposal explicitly requires a stop if those inputs need gateway changes.

That feasibility gate failed before implementation.
The inspected selected path does not deliver the required identity and original deadline to the auxiliary seam.
The [proposed amendment](CREWSHAL-TRANSPORT-CONTEXT-AMENDMENT-2026-10-29.md) identifies the additional source boundary.
No runtime candidate changed. No implementation attempt or correction was consumed.
The new budget retains one implementation attempt and two corrections, subject to the scope decision.
The previous repair budget remains consumed. I1, I2, and I3 remain exhausted.
Codex accepts this bounded source diagnosis and stop record. Transport integration remains blocked.

## Start gate and preservation

Trusted current turn metadata identifies `gpt-6.1-sol`.
The checkout started clean at the base revision, with package version `0.27.17`.
The remote remains `https://github.com/forera-ai/Crewshal.git`.
Codex read the current instructions, handoff, approved private proposal, and applicable source.
The unchanged architecture, plan, ADR 0009, Crewshal references, and companion-skill reads remain available from the preceding preparation.
The companion paths resolve through `~/.agents/skills/codebase-memory`, `~/.agents/skills/caveman`, and `~/.codex/skills/jev`.
RTK reports `1.1.0`. No new Jev or other model request followed approval.

Nine historical manifest sets match their saved files.
The repair checkpoint matches 79 entries. Its eight candidate artifacts match their saved hashes.
The twelve installed Hermes source hashes match.
The approved proposal and its evidence match their saved manifest.
New starting manifests preserve 341 private files and 1,362 tracked repository files.
Installed profile and SOUL hashes matched during the preceding preparation. No binding-changing operation followed.
No current service readiness or live admission is claimed.

## Current source evidence

These paths refer to the inspected Hermes checkout.
Private source captures retain exact ranges and complete file hashes.

| Boundary | Current source | Finding |
| --- | --- | --- |
| Original timer | Preserved I3 `diagnostic_control.py:19-29` and its submit call | The private control calculates the original monotonic deadline locally. Its submission sends session, input, text, finite, and unattended fields. |
| RPC input | `gateway/session_controls.py:751-770` | The submit method rejects unrecognized fields. It accepts no original supervisor deadline or auxiliary control record. |
| Admission payload | `gateway/session_authority.py:653-699` | A second whitelist constructs the admitted payload. Additional control data needs an authorized contract change here. |
| Execution binding | `gateway/session_ingress.py:226-296` | The claimed row and authority hold authoritative admission data. The inspected execution scopes publish author, viewer, API, and result context. |
| Auxiliary identity | `agent/auxiliary_client.py:2555-2575` | The relay creates task, auxiliary request, attempt count, route, and response metadata. This record does not contain the complete required gateway binding. |
| Summary dispatch | `agent/conversation_compression.py:2949-3005` | The summary receives cancellation and a compression-fence deadline. It does not receive the original private supervisor deadline through these arguments. |
| Deadline semantics | `agent/conversation_compression_deadline.py:69-82` | The published compression deadline is callable and can move during prompt reading. It cannot replace the fixed original supervisor deadline. |

Gateway source identifies the profile authority instance, epoch, canonical session, admission, request, and generation.
Those source values are suitable proposed inputs. This record does not claim their propagation or runtime qualification.
Multiplexer and profile authority epochs must remain separate.
An auxiliary UUID, compressor generation, reconstructed timestamp, or caller text cannot replace the missing binding.

Graph work used Verify evidence.
Hermes generation `2026-09-02T17:14:19Z` remains stale.
Relevant queries returned no nodes for newer gateway and summary symbols.
Coverage reports changed or untracked source metadata. Codex therefore read current source for every material finding.
Empty stale queries establish no absence. No recorded coverage gap proves completeness.

## Reproducible checks and limits

Private evidence resides in `aux-transport-integration-20261029-01a1883d` under the preserved S1b root.
Resolve that root from the [owner-preparation prompt](CREWSHAL-HERMES-DEADLINE-OWNER-PREP-NEXT-SESSION-2026-10-28.md).
The directory contains starting manifests, the approved scope identity, graph evidence, source ranges, and an independent source audit.
It also contains exact command results, publication checks, review, and closure manifests when publication completes.
No private source capture, policy, credential reference, or raw log belongs in Git.

The source audit ran through RTK with `PYTHONPATH` removed and bytecode writes disabled.
It used the Crewshal Python environment and exited 0.
It verified preservation, source hashes, historical submit arguments, and the selected method's field whitelist.
The exact extracted current submit method refused `auxiliary_control_v1` with `invalid_params` in a synthetic fixture.
That fixture executed the refusal branch without importing Hermes, accessing its database, or submitting a request.
It does not exercise the complete RPC stack or a provider transport.

The installed-library transport feasibility check remains not run because its prerequisite gate failed.
The 39 historical offline transport-contract tests were not rerun or relabeled as a new result.
No source candidate, SDK integration test, worker, activation, restart, or live proof ran.
Configured Hermes Ruff remains historically unavailable with the installed checker.
Its isolated comparison retains 19 baseline diagnostics and exit 1; those results remain historical.
Product suites, product mypy, wheel builds, and installed-package checks are not required for this documentation checkpoint.
Linux-specific checks remain deferred under ADR 0009.

The preceding preparation mistakenly ran one synthetic Jev probe despite the model-request restriction.
Its reported cost was `$0`; actual billing remains unknown. No model request followed this task's approval.
The private preparation record preserves that deviation.

## Closure

Whitespace, frozen-package, synchronized-version, local-import, scope, link, and preservation checks passed with exit 0.
The closure verifier confirmed 1,357 unchanged tracked files, all 341 starting private files, eight candidate artifacts, and twelve installed source hashes.
It verified matching profile hashes and preserved every byte of the earlier README, changelog, and handoff sections.
Checks used Darwin `27.2.0`, arm64, and CPython `3.12.16`.
The frozen digest remains `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Both frozen execution flags remain false.
Private records retain exact commands, exits, environment, scope, history, versions, and frozen-package identity.
The [next prompt](CREWSHAL-TRANSPORT-CONTEXT-NEXT-SESSION-2026-10-29.md) requires the source-scope decision before implementation.
It carries the unused budget forward without resetting any historical attempt.
This is new evidence about the approved feasibility boundary, not a repetition of the earlier missing-transport checkpoint.

Activation, model requests, restarts, profile changes, downloads, image actions, and guests remain closed.
Linux tests, campaigns, evaluation, merge, deployment, and releases remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The prior D3 acceptance, I3 overrun, unknown release cause, and clock limitations remain unchanged.
