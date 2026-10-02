# Phase 2B: durable state and deterministic gates

Version 0.2.0 delivers offline coordinator contracts. No code in this milestone launches a runtime, executes a discovered command, adopts a process or qualifies containment. Every verdict has `execution_allowed=false`. Phase 2C remains mandatory before agent writes.

## Storage and migration

The public `init`/`show` facade resolves the repository and excludes repository-local state. Its private external directory contains `coordinator.sqlite3`, ordered transactional records/events and, after evidence capture, content-addressed private files in `artifacts/`. Directories use 0700; databases, backups and artifacts use 0600. The directory/database/artifact itself cannot be a symlink; file hardlinks, other owners and group/world permissions are refused. Parent aliases are canonicalized before repository exclusion, including macOS `/var` and `/tmp`.

SQLite uses explicit `BEGIN IMMEDIATE`, full synchronization, an application identity and database schema version 2. Record contracts independently use schema version 1. Unsupported versions, unexpected tables/columns/types/keys/triggers, inconsistent event histories and malformed records are refused. Each transaction compares the expected record version, writes the next version and appends its event atomically. Conflicts require a reload and reconsideration; no automatic last-writer overwrite occurs. A private run lease permits only one active run; stale ownership requires explicit recovery, not silent takeover.

New installations write only SQLite. To import an existing Phase 2A external JSON model:

```sh
rtk proxy .venv/bin/crewshal show /path/to/repository --state-dir /private/coordinator-state --migrate-state
```

Import reads only the expected legacy file for that repository in the selected private external directory, validates its project ID and closed schema, and stores the complete model/history in a transaction. The original JSON remains byte-for-byte unchanged as its backup. An existing SQLite model takes precedence thereafter. `init --migrate-state` also supports this explicit operation. Rediscovery continues to use Phase 2A's source-dependent invalidation; migration itself never synthesizes confirmation.

Database schema 1 is a defined supported fixture/upgrade format, not a previously released database. It has the same records/events/lease tables except for `records.payload_digest`. Explicit migration creates a consistent SQLite backup named `schema-1-*.sqlite3.bak` under the write lock, validates all contracts/history, adds/backfills payload digests and commits version 2. Errors roll back the database; the private backup remains available. Migration is refused without `--migrate-state`; no downgrade or arbitrary schema guessing exists. Restore/inspect backups only while the coordinator is closed. Neither a JSON export nor a database copied into a worker repository is an approval input.

## Trusted API boundary

`contracts.py` contains closed Pydantic records; `durable.py` owns persistence and trusted capture; `gates.py` evaluates a trusted snapshot without I/O. These are coordinator APIs, not worker tools. No CLI imports approval/evidence/verdict exports. The trusted operator/coordinator supplies task, policy, scope and candidate digests and resolved provider identities; this phase does not capture a real candidate or resolve a real provider. A digest binds content and never proves its truth.

`create_task`, `create_run` and `save_project` preserve typed state. `owner_approval` and `owner_waiver` represent explicit local operator actions. They are not remote authentication or cryptographic signatures. `record_claim` stores worker prose separately. Parsing a claim, export or even a syntactically valid evidence record creates no trusted record.

`capture` requires the active lease, a known bound attempt and the actual stdout/stderr/artifact bytes. It checks referenced SHA-256 values and stores bounded content-addressed files outside the repository. `verdict` loads authoritative records itself and rechecks those stored bytes before applying the pure rules. Missing/mutated artifacts refuse verdict persistence. A failed database write may leave an unreferenced capture file; that file cannot satisfy any gate by itself. Retention/garbage collection is deferred.

The operator and local host/user remain trusted. Private modes and digests do not defend against malicious same-user processes, administrators or concurrent adversarial filesystem replacement. The execution boundary and exclusion of coordinator state from worker mounts must be qualified in 2C. Do not expose these coordinator APIs to workers.

## Gates, lifecycle and recovery

Bindings include exact model, task, policy, scope and candidate digests. The stored task digest covers its requirement, required check definitions and review rules. Approval, attempts, evidence and waivers must bind the same current context. Changed models or any binding digest invalidate their use. Check definitions bind argv, relative working directory, sanitized environment identity and toolchain identity; this milestone never runs the argv.

Verification requires a frozen/validating candidate, explicit approval, consistent completed implementation attempts, exact passing check definitions, passing scope evidence and passing review when required. Process exit and runtime result must both indicate completion. Passing command evidence requires zero exit, timezone-aware capture times, stdout/stderr digests and no termination or blocking finding. Passed, failed, skipped, unavailable and terminated remain distinct. Multiple records for one required gate are contradictory; remediation requires a new bound candidate/run, not hiding older failure evidence. Missing or mismatched provider/model identity cannot establish independent review; provider IDs are canonical lowercase identifiers supplied by the trusted caller.

A waiver identifies its owner, current binding, gate and residual risk. Only check/review requirements can be waived. Integrity, approval, lifecycle and scope cannot be waived by these completion records. Accepted waivers produce `accepted_with_waiver`; original failed/missing gate status remains visible and is never relabeled passed. Pure gates ignore claims. Only the durable `verdict` operation can atomically persist a successful verdict, complete the run and release its lease.

`launch_intent` records an inert future attempt before any hypothetical external side effect; `record_attempt` binds a subsequent synthetic handle/terminal observation. These methods do not grant launch permission or perform execution. On restart `reconcile_launches` marks every outstanding intent/handle interrupted, preserves handles for inspection, interrupts an unfinished leased run and releases its stale lease transactionally. Repeated reconciliation does nothing. Even a terminal attempt without a committed run verdict requires inspection. No handle is queried, adopted, killed or replayed. Future qualified supervision must supply those observations; there is no exactly-once execution claim.

## Usage and verification

Usage events are cumulative snapshots. Replay of an identical record adds no event; conflicting attempt/event or sequence identities are refused. Aggregation uses the latest sequence for each attempt rather than summing cumulative snapshots, rejects decreases in known counters and leaves missing counters/cost unknown. Input, cached input, cache writes, output, reasoning, measured cost in micro-USD, estimated cost in micro-USD and subscription quota remain separate. A missing attempt report makes the relevant total unknown. No hard spending ceiling or provider billing enforcement is claimed.

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b
rtk proxy .venv/bin/python -m unittest discover -s tests -t .
```

The 21 independent Phase 2B cases use temporary databases, artifacts, synthetic handles and crash subprocesses. They need no network, credential, container, adapter or earlier generated artifact. The complete suite retains 12 Phase 2A observable-behavior cases; assertions that depended on JSON internals now inspect durable payloads. See [DEVELOPMENT.md](DEVELOPMENT.md) and [HANDOFF.md](HANDOFF.md) for the installed-wheel checks and exact environment. These are offline contract tests, not containment qualification or live runtime evidence.
