# Offline development and project initialization

Phases 2A and 2B deliver passive discovery, human decisions, durable SQLite coordinator state and deterministic trusted-evidence contracts. There is no runtime launcher, check executor or execution grant. Confirmation records describe a project; they cannot authorize agent writes or command execution. See [state, migration and gates](STATE-AND-GATES.md).

## Reproducible setup

Use Python 3.12 or newer and uv. The recorded qualification environment is macOS arm64 with Python 3.12.14; other operating systems and Python versions are not yet verified. The package currently uses POSIX no-follow file opens and user/mode checks. Do not infer Windows support from the wheel's packaging tag.

From a fresh checkout:

```sh
rtk proxy uv venv --python python3.12 .venv
rtk proxy uv pip install --python .venv/bin/python --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python .venv/bin/python --no-deps -e .
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_substrate
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_lifecycle
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_network
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_protocol
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_broker_environment
rtk proxy .venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts
rtk proxy .venv/bin/ruff format --check src tests scripts
rtk proxy .venv/bin/mypy
rtk proxy uv build --offline
```

Dependency preparation may use the package index; tests need no network, provider credentials or earlier artifacts. The hash-locked file pins all development/runtime dependencies; the isolated build backend is separately pinned in pyproject.toml. `uv build --offline` needs its pinned build dependency already cached, as with the preceding editable installation. To prepare another machine for disconnected installation, first obtain its required wheels and build dependency. An empty cache is not an offline install source.

For artifact verification, create a second external environment, install requirements-dev.lock with `--offline --require-hashes`, then install `dist/crewshal-0.8.0-py3-none-any.whl` with `--offline --no-deps`. Run all eight acceptance modules and the complete unittest suite with that interpreter from the checkout. Tests live in the checkout; application imports must resolve to the external environment's site-packages, not src. Tests create all repository/state/interaction/database/artifact fixtures themselves.

On the verified macOS host, tests additionally passed under the following process-level network denial with an empty inherited environment and a temporary HOME. This test wrapper does not qualify a future worker execution environment:

```sh
# Substitute fresh environment and temporary home paths; create the home first.
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2a
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2b
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest discover -s tests -t .
```

## Initialization

```sh
rtk proxy .venv/bin/crewshal --help
rtk proxy .venv/bin/crewshal init /path/to/repository --state-dir /private/coordinator-state
rtk proxy .venv/bin/crewshal init /path/to/repository --state-dir /private/coordinator-state --interactive
rtk proxy .venv/bin/crewshal show /path/to/repository --state-dir /private/coordinator-state
```

Default initialization proposes facts and stores them as pending. It never prompts or confirms implicitly. `--interactive` explicitly reads `confirm`, `reject`, `correct <literal value>` or `skip` for pending facts, then separately asks for confirmation after correction. Blank answers skip. Unknown values require correction before confirmation. EOF or invalid answers refuse materialization. Prompts go to stderr, the validated JSON model to stdout. No command candidate is executed, including after confirmation.

Alternatively replay an explicit, operator-selected decision file with `--decisions FILE`. First obtain the current model digest with `crewshal show REPOSITORY --state-dir STATE --digest`. The decision file uses this format:

```json
{
  "schema_version": 1,
  "model_digest": "replace with the 64-character digest returned by show --digest",
  "decisions": [
    {"fact_id": "package.json:check:test", "action": "correct", "value": "vitest run", "reason": "Human correction"},
    {"fact_id": "package.json:check:test", "action": "confirm", "reason": "Human confirmation"}
  ]
}
```

Stale batches, unknown IDs, unsupported versions and malformed records are refused. This is explicit local operator input, not cryptographic authentication or a worker approval channel. Exported models cannot be imported as approvals. `show` displays stored state without refreshing it; rerun `init` to rediscover and invalidate changed dependencies. `validate FILE` checks the closed model contract, not authority or truth.

State defaults to `$XDG_STATE_HOME/crewshal` or `~/.local/state/crewshal`. It must resolve outside the discovered repository, belong to the coordinator user and have mode 0700. The SQLite database and capture files use mode 0600; symlink state directories/records are rejected. Writes atomically compare the loaded version and append an ordered event. Conflicting writers must reload and reconsider their decisions. Existing external JSON state requires explicit `init --migrate-state` or `show --migrate-state`; the original remains unchanged as a backup. Unsupported database versions are refused. See [the durable-state guide](STATE-AND-GATES.md) for supported database migration and inert crash reconciliation. A trusted local host/user is assumed; this does not defend against same-user malicious processes.

Initialization does not modify the discovered repository. `--export RELATIVE_FILE` explicitly creates a new model file there; parents must exist, path escapes/symlinks and existing files are refused. Exports contain relative source paths and no coordinator state path or repository root metadata. Literal repository values and human corrections remain visible; inspect them before sharing. Exported files are informational copies and never replace external state. An export and a state write are separate operations; an export may remain if state saving subsequently fails.

## Supported discovery and limits

- `pyproject.toml`: Python stack, `[project].name`, manifest directory; literal `[tool.hatch.envs.default.scripts]` string values become command candidates. Pytest configuration is a strong tool inference, not a synthesized executable command or proof of installation. Python entry-point declarations are not test commands.
- `package.json`: JavaScript/TypeScript family, name, manifest directory and literal script values. A TypeScript devDependency is a strong tool inference. All scripts are proposed candidates; the operator chooses/rejects which are checks. No package manager wrapper or implicit test command is invented.
- `workspaces` arrays and `workspaces.packages`: bounded member manifests matched using Python pathlib relative patterns. Root/member source fingerprints both bind member boundaries. Missing members and conflicting manager lockfiles remain unknown. pnpm workspace YAML, CI YAML, requirements/setup/tox files are visibly unsupported and never executed.
- `AGENTS.md` and `CLAUDE.md`: bounded input fingerprints and an untrusted-data notice only. Their instructions do not create commands or authority.
- Observed, strong inference, weak inference, unknown and human decision status are distinct. `.github` is a weak sensitive-path suggestion; data egress starts unknown. No provider/network policy is inferred from these records.
- SHA-256 source fingerprints are file-granular, with repository-relative paths and manifest-key locations. Changes to a source invalidate its dependent confirmations/corrections; unrelated files preserve them. Removed facts lose active approval and produce removal notices. Inputs are checked again before saving decisions. This is not an atomic repository snapshot or protection against adversarial concurrent filesystem mutation.
- Defaults: 2,000 directory entries, 256 KiB per supported input, 2 MiB total supported-input bytes, depth 12 and a 5-second cooperative inventory deadline. Count, size, depth, unreadable/malformed inputs, unsupported formats and exclusions are visible notices. Parsing is bounded by input sizes, not a separate hard process deadline. CLI exposes `--max-files`, `--max-file-bytes`, `--max-total-bytes` and `--max-depth`; all must be positive.
- All symlinks, special files, known private/generated/vendor trees and `.env*` paths are excluded. This is a bounded supported-format scan, not comprehensive secret detection or execution isolation. No hooks, imports from the target, dependency installation, models, containers or target scripts run during discovery.

See [the handoff](HANDOFF.md) for recorded evidence and the next milestone.

## Phase 2C blocked preflight

Package 0.8.0 includes qualification records/refusal fixtures and a partial synthetic Linux substrate harness; no product runtime launcher or completed execution qualification. See [execution qualification](EXECUTION-QUALIFICATION.md). Reproduce the preflight with a fresh, nonexistent external report path:

```sh
rtk proxy .venv/bin/python scripts/qualify_phase_2c.py \
  --manifest docs/qualification/phase-2c-v1.json \
  --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock \
  --output /private/tmp/crewshal-2c-new-observation.json
```

Exit 2 means denied; the utility never grants execution. It uses an empty synthetic HOME/Docker configuration and only the explicit local endpoint. It does not inspect host credential stores or start a container. Its fixed manifest digest refuses retrospective changes. This preflight alone leaves all worker cases unavailable. The separate active v4 utility demonstrates nine bounded cases; eleven whole-boundary cases and accepted synthetic-tested credential mediation remain unavailable. Fresh Linux execution is not demonstrated by the macOS network-denied package tests.

See [Linux substrate probes](LINUX-SUBSTRATE-PROBES.md) for the active v4 hash-bound invocation, nine passed subset cases and eleven unavailable whole-boundary cases. Offline fixture/record checks need no Docker; real substrate probes need the explicit engine endpoint and pinned cached image. The older v1 preflight remains a denial utility, even with a responding daemon. Neither result grants agent writes.

## Phase 2C lifecycle resumption

The separate [lifecycle checkpoint](LINUX-SUBSTRATE-PROBES.md#lifecycle-and-validator-resumption--2026-10-02) adds four synthetic-only observations and six offline refusal/failure methods. It does not promote the earlier nine-case record or qualify a native coding runtime. Use `python -m scripts.probe_linux_lifecycle` from the checkout with the frozen manifest and fresh output path documented there. Both subset utilities intentionally return 2 while full qualification is denied. No downloads or installation are required for the cached Alpine observations.

## Phase 2C network resumption

The separate [network checkpoint](NETWORK-SUBSTRATE-PROBES.md) records two fresh-fixture runs of twelve denied socket attempts with bracketing independent sink controls. Use `python -m scripts.probe_linux_network` with the frozen v3 manifest/hash and a fresh external output path. The prepared immutable Python image is required; the runner uses `--pull=never`. The eight offline network acceptance methods need neither Docker nor SBX and use committed sanitized record fixtures plus newly created temporary refusal fixtures. These are record/oracle regressions, not fresh network qualification. Full qualification remains denied.

## Phase 2C prospective SBX protocol

The [resource/configuration protocol](SBX-RESOURCE-CONFIGURATION-PROTOCOL.md) and [help-only assessment](SBX-PROTOCOL-ASSESSMENT.md) preserve the worker ceiling and define the remaining operational oracles. The pinned utility exposes no daemon, login, secret-store or worker operation. Its seven offline acceptance methods need neither SBX nor Docker; the real help assessment needs the exact external Darwin binary and intentionally returns 2. Full qualification remains denied. No previous temporary extraction is required.

## Phase 2C disposable broker-store preflight

The [broker environment assessment](BROKER-ENVIRONMENT-ASSESSMENT.md) documents preparation and the frozen v3 invocation. Two separate Ubuntu fixtures demonstrate synthetic secret save/list and independently observed private backing storage. This avoids the real macOS store but does not qualify an operational broker, native runtime or authenticated request. The observed Linux host has no KVM device/sysfs entry. The utility uses a pinned external official bundle, `--pull=never`, no network or host-secret mounts, exact effective grant checks and unique-handle cleanup. It always exits 2; all twenty whole-runtime results remain unavailable. Eight offline methods need no Docker, SBX, credentials or previous temporary directory. Historical v1/v2 oracle failures and source snapshots remain recorded.


## Phase 2D unpublished offline contracts

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d` for the 26 fresh contract methods. Full offline suite now contains 167 tests in the unpublished working tree. [The source/verification guide](PHASE-2D-OFFLINE-CONTRACTS.md) documents native event refusal, candidate integrity, independent validator observations and fresh installed-wheel checks. No runtime/check launcher or CLI execution command exists. 2D remains incomplete until its separately approved live gate passes; see [execution preparation](PHASE-2D-EXECUTION-GATE.md) and [continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Version remains 0.9.0; do not publish the draft verification wheel.


The [Sol6.1 preparation guide](PHASE-2D-BATCH-PREPARATION.md) documents the offline utility and exact bundle. Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_batch` for its seven fresh methods. Combined unpublished 2D coverage is 33 methods / 174 complete tests. “Batch preparation only” supplies no native startup or spend authority.

## Phase 2D preparation selection

Use explicit `--selection FILE` with the offline preparation utility to bind model and optional route/billing/credential choices to each project/session. Read back against an independently retained coordinator record before reuse; a different context refuses. This selects data, not account access or execution authority. See [the exact schema, commands and verification](PHASE-2D-SESSION-SELECTION.md).

## Phase 2D coordinator capture integration

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_integration` for 18 fresh coordinator/SQLite cases. Combined unpublished coverage is 58 Phase 2D methods / 199 complete offline tests. `collect_codex_attempt` consumes independently retained initial snapshot/scope and trusted effective identity/process captures, then persists a changed frozen candidate without losing its launch binding. Changed candidates invalidate earlier candidate approvals. Collected runs require `CoordinatorStore.verdict(..., candidate_root=frozen_root)` to recheck bytes and private captures. Missing/failed checks and worker success text cannot complete a run. See [source, trust boundaries and verification](PHASE-2D-PRODUCTION-CAPTURE.md). No native or validator launcher exists; Phase 2D remains incomplete.


## Phase 2D source-bound dispatch preparation

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_dispatch` for 14 independent inert preparation/refusal cases. Combined unpublished coverage is 72 Phase 2D methods / 213 complete offline tests. `prepare_dispatch_configuration` compiles pinned native/proxy argv and separate task stdin, binding the exact batch/task/check/context and current package source. `prepare_codex_dispatch` audits data and requires exact qualification through the existing request seam; it still cannot launch or grant execution/spend authority. Missing route choices remain per-session preparation data. See [the source and reproduction guide](PHASE-2D-DISPATCH-PREPARATION.md) and [current continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Linux supervision and approved live acceptance remain unavailable; package stays 0.9.0.


## Phase 2D bounded supervisor source

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_supervisor tests.acceptance.test_phase_2d_integration` for 24 new supervision cases and the existing 18 collection cases. Combined unpublished coverage is 96 Phase 2D / 237 complete offline tests. Tests create actual separate pipes, controller-file fixtures, candidate copies and SQLite state; child/clock/kernel-stop effects are explicitly synthetic. `collect_supervised_codex` joins independent bounded capture/readback to the existing collection body in one transaction and links its private receipt to scope artifact integrity. The Linux attachment source and exact hard enforcement remain unqualified. No process or envelope is created; no CLI launcher is added. See [source behavior, commands and limitations](PHASE-2D-SUPERVISOR-SOURCE.md), [verification](qualification/phase-2d-supervisor-verification-v1-20261008.json) and [current continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Startup, credentials, spend and publication remain gated; package stays 0.9.0.

## Phase 2D retained native admission source

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_admission` for 28 new admission/refusal methods. Combined unpublished coverage is 124 Phase 2D / 265 complete offline tests. `admit_native_process` checks a retained stopped child, pinned proc/pidfd and cgroup identities, native role/configuration/executable/namespace, separate stdio and original controls. `AdmittedNative.capture` hands retained resources to the existing bounded capture seam. No process is created or resumed. Fixture proc/kernel/child effects are explicitly synthetic; source is unqualified on Linux. See [guide](PHASE-2D-NATIVE-ADMISSION.md), [verification](qualification/phase-2d-native-admission-verification-v1-20261008.json) and [continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Envelope/bootstrap, hard controls, admission persistence, exact qualification and approved live gate remain missing; version stays 0.9.0.

## Phase 2D durable admission/collection source — offline only

`collect_admitted_codex` accepts trusted retained admission, checks exact dispatch/handle/pipe/clock bindings and delegates capture through the existing supervisor. Admission, terminal collection, supervision and scope records commit atomically. Private artifacts remain outside worker authority; filesystem artifacts/frozen copies are not transactional, and a retained freeze target refuses retry. Final readback requires intact admission/supervision links and original observed identities. Lower-level capture remains a trusted seam, not proof of admission or a launcher.

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_admission_collection`. Fifteen fresh cases plus the previous suite produce 280 offline tests. Child/proc/kernel effects are synthetic; real pipes, files and SQLite rollback/reopen are exercised. See [the guide and complete commands](PHASE-2D-ADMISSION-COLLECTION.md) and [current exact continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Changed source requires fresh prospective bindings/qualification. Version stays 0.9.2; no startup, spend, host test or publication occurs before the remaining production envelope and full live 2D gate.

## Phase 2D passive Linux envelope preparation

[The envelope guide](PHASE-2D-LINUX-ENVELOPE.md) documents pure per-session Linux role/mount/argv and original controller/systemd/storage requirements, prospective source/policy bindings, unchanged bootstrap requirements and exact continuation inputs. `prepare_linux_envelope` and `audit_linux_envelope` supply no launch or effective readback. Missing bootstrap, deadline/recovery and containment/credential/financial enforcement remain explicit with false execution/spend/qualification flags. Dispatch binds fourteen current package files; old profile eligibility does not transfer.

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_envelope tests.acceptance.test_phase_2d_dispatch tests.acceptance.test_phase_2d_admission_collection tests.acceptance.test_phase_2d_admission
```

Focused suite: 75 passed in 1.958s. Complete suite: 298 passed editable in 14.209s and fresh installed wheel in 11.593s under empty environment, fresh HOME and denied network. Ruff lint/format (49 files), strict mypy (19 package files), offline build/hash-locked installation, passive help and nineteen-file installed-source equality pass. See [exact commands and continuity](qualification/phase-2d-linux-envelope-verification-v1-20261008.json). Package remains 0.9.2; production bootstrap, Linux qualification and separately approved live 2D acceptance remain unavailable. No startup, credentials, paid calls, VMware/SSH, host control operations, version/commit/push or 2E.


## Phase 2D owned bootstrap source, offline only

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_bootstrap` for 25 fresh helper/handoff/deadline/refusal methods. [The source guide](PHASE-2D-OWNED-BOOTSTRAP.md) explains the exec-event to signal-delivery handoff, unchanged admission, original watchdog origin and owned recovery, and records the exact next prompt/inputs. The C helper is packaged as source data only; no compiler invocation or process startup occurs. Parent/namespace placement, initial traced-proc attachment, effective watchdog/role/FD/containment readback and Linux qualification remain missing. A readiness acknowledgement is trusted seam data, not hard enforcement or authority.

Complete suite: 323 passed editable in 10.483s and fresh installed wheel in 16.894s, with fresh HOME, empty environment and denied network. Focused affected suite: 100 passed in 2.123s. Ruff lint/format (51 Python files), strict mypy (20 modules), offline build/hash-locked install, passive help and 21 packaged source-file comparisons pass; sixteen files bind dispatch. Full commands, development failures and byte continuity are in [verification](qualification/phase-2d-owned-bootstrap-verification-v1-20261009.json). Use the venv interpreter path without resolving its symlink; resolving it selects the global interpreter and loses venv imports. Preparation/readiness/qualification/execution/spend flags stay false; no version/commit/push, host activity, paid calls or 2E at this incomplete 2D boundary.

## Phase 2D parent/watchdog bridge, offline only

[Guide and exact continuation](PHASE-2D-PARENT-WATCHDOG.md) documents the one-shot namespace-parent source route and its unqualified inheritance/migration candidate. [Source](../src/crewshal/linux_parent.py) independently reads retained trusted tasks, watchdog timer/FD/owned kill identities and original deadline before creating a direct helper child through the accepted setpriv mechanism. Dedicated initial traced attachment does not weaken RetainedProc.attach or native admission. The source retains unknown/failed recovery and forbids resource reuse; real setup, terminal lifecycle and exact Linux qualification remain missing.

Twenty-three fresh methods make 205 Phase 2D / 346 complete offline tests. The focused affected suite passes 123; complete editable and fresh installed-wheel suites pass with fresh HOME, empty environment and denied network. Ruff lint/format, mypy (21 modules), offline build/hash-locked installation, passive CLI help and 22 packaged-source comparisons pass. Seventeen files bind dispatch. Exact commands, timing, environment, source/input/build hashes and development failures are in [verification](qualification/phase-2d-parent-watchdog-verification-v1-20261009.json). No C compilation, real process/kernel operation, credential access, paid calls, host activity, version/commit/push or 2E occurs.

## Phase 2D owned setup and terminal lifetime, offline only

Run `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_setup` for 35 fresh methods. [The setup guide](PHASE-2D-OWNED-SETUP.md) documents sealed retained controls, fixed-FD C source normalization, bounded observer/setup placement, namespace-local identity, owned watchdog creation before worker creation, unchanged stopped admission and local/external one-grace terminal observations. Constructors and Linux effects are synthetic; real temporary files/pipes are exercised. Every physical-resource reuse result stays false. Owned storage teardown, trusted entry/root/helper/library inventory, actual effective controls, exact Linux qualification and separately approved live acceptance remain missing.

Complete suite: 381 passed editable and fresh installed wheel with fresh HOME, empty environment and denied network. Focused affected suite: 158 passed. Ruff lint/format (55 Python files), strict mypy (22 modules), offline build/hash-locked install, passive CLI help and 23 packaged source comparisons pass; eighteen files bind dispatch. Commands, environment, timing, input/source/build hashes, preserved-byte continuity and development failures are in [verification](qualification/phase-2d-owned-setup-verification-v1-20261009.json). Use a new external venv/HOME and the literal venv interpreter path, without resolving its symlink. No C compilation, real runtime/kernel effect, credentials, paid calls, host operation, version/commit/push or 2E occurs.

## Phase 2D owned physical ordering and trusted parent inventory, offline only

[Guide and exact continuation](PHASE-2D-OWNED-TEARDOWN.md), [inventory source](../src/crewshal/linux_inventory.py), [teardown source](../src/crewshal/linux_teardown.py) and [verification](qualification/phase-2d-owned-teardown-verification-v1-20261009.json) define the latest preparation boundary. Run the two new modules plus the affected setup/parent/bootstrap/envelope/dispatch/admission suites. Forty-six new methods yield 427 complete / 286 Phase 2D offline tests, with 204 focused methods. Ruff covers 59 Python files; strict mypy covers 24 modules. A fresh wheel compares all 25 package source files and twenty dispatch bindings under empty environment/denied network. Retain literal venv interpreter paths.

Physical effects are synthetic trusted-owner observations, not Linux teardown proof. No concrete `PhysicalOwner` adapter or installed trusted parent entry/import/loader closure exists. Bound parent preparation requires exact inventory and retained root readback; unbound historical seams remain unqualified. Watchdog survival, unknown holders/key revocation, partial releases, substituted descriptors, inode replacement, replay and exhausted original batch cannot produce reusable resources. The observer and aggregate remain retained even on synthetic success. Keep all effects/spend/host operations disabled; no version bump, commit/push or 2E before complete 2D acceptance. Use the guide's exact next prompt and every prior input.

## Retained Linux storage-owner source — October 9

[The storage-owner guide](PHASE-2D-LINUX-STORAGE-OWNER.md) and [verification](qualification/phase-2d-linux-storage-owner-verification-v1-20261009.json) record concrete retained mount/keyring/loop/backing readback and fixed-deadline observer-child operation source. Readback detects actual descriptor/row identity changes and positive deleted-open/mapped/alias holders. An empty proc scan remains unknown because it omits kernel references and taskless namespaces; operational physical release is blocked, not inferred from a protocol, exit code or absence of paths. No readiness flag or historical qualification can supply closure.

The 44 new storage methods and two teardown methods use fresh current fixtures; all syscall/namespace/fork/child effects are synthetic. Complete editable/fresh-wheel suites have 473 tests, including 332 Phase 2D methods. Ruff covers 61 Python files, mypy 25 modules, and 26 packaged sources are compared byte-for-byte. Twenty-one sources bind dispatch. Follow exact denied-network/empty-environment and fresh-proof commands in the ledger; do not reuse previous environments. No compiler, startup, credentials, model/provider/Jev spend or host operations are authorized. Keep version 0.9.2/uncommitted status and stop at effective-reference-closure refusal; actual installation, controls, Linux qualification and separately approved live acceptance remain missing.

## Source publication checkpoint — 0.10.0

The owner expressly authorized branch commit/push on October 9. [The checkpoint](PHASE-2D-SOURCE-CHECKPOINT-2026-10-09.md) and [publication verification](qualification/phase-2d-source-checkpoint-verification-v1-20261009.json) supersede the old 0.9.2 source-publication stop for this delivery. The compatible functionality uses a minor version bump. Earlier guides and verification bytes remain historical; current source remains unqualified, effective reference closure remains blocked, and execution/host/spend/live/release/2E gates do not change. Use the checkpoint's exact 0.10.0 continuation.
