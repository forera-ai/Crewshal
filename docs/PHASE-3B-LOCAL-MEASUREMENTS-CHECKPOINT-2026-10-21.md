# Phase 3B local measurement checkpoint — 2026-10-21

## Scope and result

This checkpoint adds a read-only `check-measurements` command to `scripts/phase3b_development_ledger.py`.
The command checks one measurement claim for each declared development attempt.
It binds attempt IDs, schedule fields, outcomes, and reasons to the frozen Phase 3A package and coverage ledger.
It rejects incomplete token counters marked as known usage.
It requires separate provenance for measured cost, estimated cost, and subscription quota amounts.
It preserves the frozen usage deduplication and cumulative snapshot rules.
It rejects a baseline claim to a Crewshal project model and a B0 reviewer claim.

The command checks structure and consistency only. It does not authenticate an execution event.
It does not validate the contents of check, review, claim, or waiver details.
It does not bind measurement records to files in the evidence inventory yet.
Every result reports `evidence_verified: false` and `execution_allowed: false`.

The bundle has `schema_version`, `record_kind`, `package_content_sha256`, `ledger_sha256`, and `records`.
Each record uses the frozen `measurement-template.json` fields.
Set its `record_kind` to `phase3b-development-measurement-claims-not-execution-proof`.
Set its `status` to `unverified-development-claim` and keep both authority flags false.
Fill `unit` from the matching frozen schedule row and declare one outcome and reason per attempt.
Use `null` for unavailable observations and keep `unknown_usage: true` when counters are incomplete.

Run the checker from the repository root:

```sh
rtk proxy .venv/bin/python -m scripts.phase3b_development_ledger check-measurements LEDGER.json MEASUREMENTS.json
```

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `c01fe030735e005c165a4554c949db02e417d90` on `codex/phase1-architecture`.
All 260 files in `docs/PHASE-3B-LOCAL-EVIDENCE-INPUTS-2026-10-21.json` matched their sizes and SHA-256 digests before changes.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 119 tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| Local `check-measurements` CLI smoke with a planned ledger and empty bundle | Reported 192 planned rows, zero measurement attempts, and `evidence_verified: false`. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-measurement-wheel` | Built `crewshal-0.22.0-py3-none-any.whl` without network access. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-measurement-install /tmp/crewshal-phase3b-measurement-wheel/crewshal-0.22.0-py3-none-any.whl` | Installed into a temporary target. Metadata and import both reported `0.22.0`. |

The first metadata inspection used `crewshal-0.22.0` as a distribution name and failed.
The corrected inspection used the installed target path and passed.
The new tests use synthetic records. They cover missing attempts, changed schedule fields, false final outcomes, and incomplete usage.
They also check that a zero measured cost still needs billing evidence.

No Linux-specific test module ran. Linux qualification and native conformance remain deferred.
No guest action, archived tool execution, native turn, or evaluation row ran.
No new network transfer occurred. Paid host and metered API costs were zero.
The historical archive charge remains 10,008,484,533 bytes.
The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.

## Remaining gates

All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown until observed.
The staging command was not submitted before the clone suspended. Its console line and guest state remain unknown.
The single admission ledger closes the staging attempt and admits no restart or stage.
Phase 3B needs admitted development corpus runs with complete accounting and preserved failures.
It also needs an amended protocol frozen before hold-out exposure.
ADR 0009 defers the consolidated Linux campaign until local source development passes its gates.
Continue with the [next prompt](PHASE-3B-LOCAL-MEASUREMENTS-NEXT-SESSION-2026-10-21.md).
