# Phase 3B local claim path checkpoint — 2026-10-21

## Scope and result

This checkpoint extends `scripts/phase3b_development_ledger.py` with declared paths for local JSON sources.
Each populated measurement field names one to eight source references.
Each reference binds one inventory file to one JSON path.
A path contains one to sixteen object keys or array indices.
Keys contain one to 128 characters. Indices range from zero to 1023.
The checker rejects malformed references, duplicate files for one field, and paths outside these bounds.
It does not search other paths for a matching value.

`check-contents` reports the field, inventory file, declared path, status, and detail for each comparison.
An absent path remains `unmatched`. Invalid JSON or a non-JSON file remains `unsupported`.
An exact value remains `matched` only for that declared path and JSON type.
Every result keeps `evidence_verified: false` and `execution_allowed: false`.
Matching bytes do not establish file origin or an admitted run.
The frozen Phase 3A package remains unchanged.

For example, a claim for `outcome` can use `{"file":"run.json","path":["events",0,"state"]}`.
The file name must appear in the same attempt's inventory.
The path applies only to that claim and file.

## Local verification

Environment: local macOS 27.2 arm64, CPython 3.12.15, and the project `.venv`.
Base revision: `c64a8461d2f41ce495793846de7f1c91520b69da` on `codex/phase1-architecture`.
The delivery revision is the commit that contains this record.
Git was clean before changes. All 270 exact starting input files matched their sizes and SHA-256 digests.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 126 local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed after formatting. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-path-wheel-v026` | Built `crewshal-0.26.0-py3-none-any.whl`. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-path-install-v026 /tmp/crewshal-phase3b-path-wheel-v026/crewshal-0.26.0-py3-none-any.whl` | Installed without network access. Isolated import and metadata both reported `0.26.0`. |
| `rtk proxy git diff --check` | No whitespace errors. |

The first format check found one changed test file. Formatting it made the final check pass.
Synthetic fixtures checked two JSON schemas, a nested array path, wrong values, missing paths, and invalid bounds.
They ran no repository task or provider process.
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
Phase 3B still needs admitted development corpus runs with complete accounting and preserved failures.
It also needs a protocol amendment frozen before hold-out exposure.
ADR 0009 defers the consolidated Linux campaign until local source development passes its gates.
Continue with the [next prompt](PHASE-3B-LOCAL-PATH-NEXT-SESSION-2026-10-21.md).
