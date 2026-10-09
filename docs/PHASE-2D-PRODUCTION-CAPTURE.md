# Phase 2D coordinator collection and candidate revision integration

Date: 2026-10-08. Status: **verified offline integration; Phase 2D incomplete**. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, package 0.9.0, uncommitted. Preparation choices remain per project/session. No runtime, validator command, provider/model/Jev, credential store, VMware/SSH or paid host was accessed.

## Observable change

An implementation changes the candidate after launch. The earlier pure seams could normalize output and freeze files, but the durable attempt/run binding could not move from the initial manifest to the resulting manifest without losing launch provenance. The earlier manual SQLite fixture used an already known final digest; it did not demonstrate this revision transition.

[The coordinator integration](../src/crewshal/integration.py) now collects one acknowledged Codex implementation into private SQLite state. It reads the stored run/attempt/task, checks the lease and both expected versions, and verifies the initial manifest and exact allowed-path scope before creating a frozen copy. `scope_digest(paths)` binds sorted exact paths as UTF-8 JSON from `json.dumps({"schema_version": 1, "allowed_paths": sorted(paths)}, sort_keys=True)`. This explicit scope must be retained in the launch binding; no directory expansion or wildcard scope is inferred.

Trusted capture supplies effective runtime identity/configuration, actual process observations and bounded stdout/stderr. Native output supplies only normalized events, claims and reported cumulative usage. Successful collection independently requires a stopped tree, creates a separate frozen copy, computes scope evidence, and changes only the candidate component of the current run/attempt binding. A private `CodexCollection` receipt retains the original launch binding, initial manifest, normalized terminal attempt at that original binding, effective/expected configuration, process observation, resulting binding/manifest and stream digests. Ordered SQLite history also preserves the original intent and acknowledgement. No approval is copied or rewritten. A changed candidate therefore needs an explicit current-binding owner decision before a verified verdict; a launch approval for different bytes remains stale.

Terminal attempt, collection, claims, usage, scope evidence and run transition commit in one SQLite transaction. Streams and receipt bytes are stored using existing private artifact capture. Native failure, stale identity/configuration, timeout or incomplete capture records a refusal and interrupts the run without freezing or retrying. Oversized streams refuse collection before state changes and require explicit supervisor reconciliation; they are not silently truncated or marked complete. Unknown/still-running handles require external inspection. This source seam does not kill or query processes, and its inert lease release is not evidence of cleanup.

[The durable store](../src/crewshal/durable.py) recognizes the additional `collection` record kind without changing SQLite tables or schema version 2. Existing callers/records keep their behavior; older package readers refuse the unknown new kind rather than silently ignoring it. `verdict(..., candidate_root=frozen_root)` is mandatory for collected runs. It checks the stored receipt, corresponding terminal attempt, frozen manifest and private stream/receipt artifacts again before existing evidence rules. Mutation after a successful validator capture refuses the final verdict. Collections without checks remain blocked; worker success prose cannot replace checks. Existing evidence cannot be rebound, and extra attempts cannot hide a retry or acquire the new binding.

## Trust and limits

This is a privileged coordinator API, not a worker-facing import endpoint or an execution approval. The collection operation uses the existing store transaction/artifact primitives inside the package. No new adapter, model/tool loop, gateway, supervisor or public CLI execution command is added. All permission flags remain false. A synthetic fixture owner decision is not real startup/spend authority.

Five seconds, 65536 bytes per stream, 16777216 candidate bytes and existing manifest/inventory limits stay unchanged. Candidate/frozen locations must exclude the entire coordinator state directory. Filesystem copies/artifacts are not SQL transactions: a copy or database failure can leave owned bytes for inspection while SQL state rolls back. Existing paths are never deleted or overwritten to retry. Stable coordinator-owned directories and the trusted-host threat model remain assumptions. Manifest integrity is not a kernel readonly mount, namespace/cgroup observation, credential isolation or storage qualification.

## Fresh acceptance

[18 independent methods](../tests/acceptance/test_phase_2d_integration.py) create their own original dirty/Git files, candidate changes, streams, identities, model/task/scope, private database and captures. They demonstrate changed-candidate rebinding with preserved launch provenance; current approval; missing/failed checks despite forged success text; scope escalation; stale versions/binding/scope/lease; replay; timeout/incomplete stop/malformed output/configuration refusal; stream overflow; restart and artifact tampering; validator and post-validation mutation; required verdict readback; actual SQLite-triggered rollback; failed freeze; state-path exclusion; and multiple-attempt refusal. No prior 2C record or external service is a fixture dependency.

Combined unpublished coverage: **58 Phase 2D methods / 199 complete offline tests**. macOS 27.2 (`26B5101f`) arm64, CPython 3.12.15, hash-locked dependencies. Editable and freshly built installed-wheel suites pass with network denied and an empty inherited environment. Ruff lint/format, strict mypy, offline sdist/wheel build and installed CLI inspection pass. Application imports resolve to external site-packages. See [verification and continuity](qualification/phase-2d-production-capture-verification-v1-20261008.json).

Reproduce source checks:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_integration
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/mypy
```

Fresh external wheel environment/build commands are recorded in the verification artifact. Do not publish the draft 0.9.0 wheel. Discovery loaded 365 previously linked inputs as data. The previous historical ledger differs only in its five intentionally maintained documents; original 2C profiles/sources/observations remain unchanged. Existing unpublished preparation source/tests remain intact. Current `durable.py` is intentionally extended; qualification cannot transfer to changed production source/configuration.

Initial acceptance import failed because the integration module did not exist. Strict typing initially rejected reuse of a digest loop variable with an optional digest; the variable was corrected. Direct review caught checking the database file instead of the entire state directory; source and regression were corrected before final acceptance. These were offline development failures. No live failure or qualification success is inferred.

Codebase-memory Verify used project `Volumes-X10Pro-Crewshal`, initial generation `2026-10-08T13:41:16Z`. Final coverage generation `2026-10-08T13:50:52Z` reports matching metadata/no recorded gap for integration, durable state and new tests. Both-direction depth-one trace is fully paginated (17 callees, one test caller); its `digest` edge incorrectly resolves to JSON-embedded historical source. The actual import from `crewshal.model` and exact source were read instead. Coverage remains best-effort, not completeness. No agents were delegated or paid Jev calls made.

## Remaining Phase 2D boundary

Production launch/supervision through the accepted Linux native/proxy mechanisms remains unimplemented and unqualified. The fixture driver is not a product launcher. Fresh profile/source/configuration/grant bindings, effective Linux controls, scoped provider/credential route, acceptable financial treatment and a separately approved actual native implementation/credential-free check are still missing. Per-project/session choices remain optional preparation data; no global route is requested. This collection cannot create observations or authorization for those missing mechanisms.

Continue Phase 2D only from [the updated prompt and exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md). Do not begin 2E, reuse v18 eligibility for different identities, reconnect to VMware/SSH, start native code or access credentials under this preparation-only prompt. No version bump, commit or push occurs before the complete 2D acceptance gate. Handoff preserves this incomplete boundary.
