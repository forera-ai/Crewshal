# Phase 2D retained admission and durable supervised collection

Date: 2026-10-08. Status: **offline preparation boundary verified; Phase 2D incomplete**. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, maintenance version 0.9.2. Implementation remains uncommitted. Repository: `forera-ai/Crewshal`; copyright: forera.ai and contributors.

## Observable behavior

[Admission source](../src/crewshal/admission.py) now exposes `collect_admitted_codex` for trusted coordinator callers holding an `AdmittedNative`. It binds the retained child, worker, exact dispatch, pipes and original clocks to the existing [supervised collection](../src/crewshal/supervisor.py). It starts or releases no child, reads no credentials and adds no CLI endpoint or execution authority. The lower-level supervisor entry point remains available for its existing independent fixtures; it does not prove native admission.

The native receipt snapshots its specification rather than sharing mutable retained-proc state. It records aware launch time and finite nonnegative monotonic origin. Its retained digest and original clocks are checked before capture; spec, configuration, pipes and aggregate readback must still agree. A changed receipt during capture refuses collection. These checks preserve an observed snapshot; they do not prove Linux bootstrap compatibility, absence of earlier execution, ongoing process configuration or effective role/storage/credential/egress enforcement.

`NativeAdmissionRecord` binds that receipt to run, attempt, handle and dispatch, with execution/spend/qualification flags fixed false. Admission insertion, bounded capture, terminal collection, claims/usage, candidate binding, supervision receipt and scope linkage share one SQLite transaction. The supervision receipt references the admission digest; successful scope evidence references both private artifacts. Failure at admission or supervision insertion rolls back records and events. Artifact files and frozen copies are not transactional; a leftover freeze target refuses reuse. No automatic retry, release or process recovery is added.

[Durable verdict readback](../src/crewshal/durable.py) requires the recorded admission and supervision links to agree with collection, PID, original worker identity, original start time, handle, dispatch and log digests. Both artifacts must remain intact and linked to scope evidence. Missing, detached, changed or ambiguous linkage refuses a final verdict. Actual SQLite reopen and artifact mutation are exercised offline. This is consistency under a trusted coordinator/host, not authenticated owner authority or defense against an administrator rewriting all state.

The SQLite table schema is unchanged; the closed registry adds one record kind. Admission receipts gain required clock fields and earlier unpublished snapshots are not promoted. All thirteen dispatch-bound source identities remain current-source-bound: admission, supervision and durable changes invalidate prior prospective configurations. Existing qualification/grants do not transfer. Package version remains the published maintenance version 0.9.2 because complete Phase 2D acceptance/publication is still gated.

## Fresh independent evidence

[Fifteen new acceptance methods](../tests/acceptance/test_phase_2d_admission_collection.py) create their own candidate copies, separate real pipes, private SQLite state and synthetic proc/controller fixtures. They import fixture builders, not observations from previous runs. No native process, validator, Linux attachment, signal, credential, model/provider/Jev or host operation occurs. Child, proc, clock and kernel effects remain explicitly synthetic; descriptor IO, hashes, files, transactions and restart readback are real.

Cases exercise exact durable links/private modes/reopen; original dirty-file preservation; altered admission artifact; missing admission row; detached supervision/scope references; real SQL refusal before capture and after collection with complete event rollback; stale versions/lease/handle before capture; changed dispatch; mutable receipt and launch clock; retained-proc spec mutation without aliasing the receipt; pipe substitution and relaxed aggregate; receipt mutation during capture; nonzero native exit; missing EOF; terminal replay; and false authority/unknown-field refusal.

Focused admission/supervisor/collection suite: **85 passed in 3.134s**. Complete editable suite: **280 passed in 9.674s** with denied network, replaced inherited environment and fresh HOME. Fresh installed wheel: **280 passed in 10.391s** under the same constraints. New coverage is **139 Phase 2D methods** plus the original 141. Ruff lint passes; formatting checks 47 files; strict mypy checks 18 package files. Offline build, fresh hash-locked dependency/wheel installation and passive CLI help pass. All eighteen installed package source files match working bytes, including all thirteen dispatch-bound sources; installed version is 0.9.2.

Reproduce from the existing checkout:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_admission_collection tests.acceptance.test_phase_2d_admission tests.acceptance.test_phase_2d_supervisor tests.acceptance.test_phase_2d_integration
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py
rtk proxy .venv/bin/mypy
```

[Verification and continuity](qualification/phase-2d-admission-collection-verification-v1-20261008.json) records exact commands, environment, build/source/input hashes, failures and byte continuity. Initial entry-point absence was reproduced. Adding the registry initially exposed an import cycle through dispatch/runtime-batch/durable; dispatch imports now occur only where needed at runtime. Two failed patch validations changed no files. One new test selected validator evidence instead of scope evidence; exact scope-ID lookup corrected the fixture. All final checks pass. No live failure or Linux qualification is inferred.

## Next boundary and exact inputs

Stop here. Resume only Phase 2D preparation with [HANDOFF.md](HANDOFF.md), [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md), [the updated continuation and its complete exact input list](PHASE-2D-CONTINUATION-2026-10-08.md), this guide, admission/supervisor/durable source, the new test and verification artifact. Prior input records, accepted architecture/ADRs and historical 2C evidence remain mandatory and unchanged.

Next initial prompt: “Resume 2D preparation from durable admission/collection linkage. Read the current guide, source, test and verification plus every prior exact input. Preserve forera-ai/Crewshal, forera.ai and contributors, maintenance version 0.9.2, per-project/session choices, original ceilings and unrelated dirty bytes. Implement only missing bounded Linux envelope/bootstrap source using accepted systemd/cgroup, bubblewrap/setpriv, native sandbox and official proxy mechanisms. Establish stopped PID/start/parent/boot and pipe ownership, storage/role/FD/credential/egress controls, independent hard deadline and owned refusal recovery before using collect_admitted_codex. Do not replay fixtures, build a gateway/model loop, execute prepared argv directly on the host or transfer old eligibility. Keep startup, credentials, spend, VMware/SSH and host operations disabled until an exact project/session batch has a separately recorded gate. Record fresh offline evidence and stop at the next verified or blocked boundary; publication requires complete offline and approved live 2D acceptance. No 2E.”

Production envelope/bootstrap, stopped-checkpoint compatibility, hard deadline and effective storage/role/credential/egress/financial enforcement remain unobserved. Fresh exact-profile qualification and separately approved actual implementation/credential-free validation remain missing. Linux/Windows/macOS runtime support beyond the historical qualified profile and lost v5 cause/original cleanup remain unknown. No version bump, commit/push or Phase 2E occurs at this incomplete boundary.
