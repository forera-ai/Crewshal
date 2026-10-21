# Phase 3B local claim content checkpoint — 2026-10-21

## Scope and result

The read-only `check-contents` command compares each declared claim with its matching path in a local JSON object.
It first checks the coverage ledger, evidence inventory, file sizes, SHA-256 digests, and measurement links.
The command reads each compared file through a directory descriptor without following symbolic links.
Each file is limited to its declared size, which cannot exceed 8 MiB.
It checks the digest again before comparing a value.
JSON keys must be unique. JSON must use valid finite values.
The comparison requires the same JSON type and exact value.
It reports `matched`, `unmatched`, or `unsupported` for each field and declared source file.
An absent JSON path remains `unmatched`. Non-JSON files and invalid JSON remain `unsupported`.
These results do not establish who created the file or whether an admitted event occurred.
Every result keeps `evidence_verified: false` and `execution_allowed: false`.
The frozen Phase 3A package remains unchanged.

Run the command with four local inputs:

```sh
rtk proxy .venv/bin/python scripts/phase3b_development_ledger.py check-contents LEDGER INVENTORY MEASUREMENTS ARTIFACT_DIR
```

The command compares a claim only at its own dotted JSON path.
For example, `effort.context_bytes` reads `{"effort":{"context_bytes":0}}` from a declared JSON file.
It never searches for a value at another path.

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `22cf7d71dfa6ec309915d2fe20f11f102a515f10` on `codex/phase1-architecture`.
The delivery revision is the commit that contains this record.
Before changes, all 267 files in `docs/PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-INPUTS-2026-10-21.json` matched their sizes and SHA-256 digests.
Git showed no working-tree changes at the start.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 124 local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-content-wheel-v025` | Built `crewshal-0.25.0-py3-none-any.whl`. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-content-install-v025 /tmp/crewshal-phase3b-content-wheel-v025/crewshal-0.25.0-py3-none-any.whl` | Installed the wheel without network access. |
| Isolated installed-target import and metadata check | Import and metadata both reported `0.25.0`. |
| `rtk proxy git diff --check` | No whitespace errors. |

Synthetic fixtures covered exact nested values, mismatched values, missing paths, unsupported text, duplicate JSON keys, and numeric type differences.
A changed file failed the inventory digest check before content comparison.
No check authenticated a file's creator or an execution event.
An initial focused test expected a digest error after changing file size. The size check correctly failed first.
The fixture then changed bytes without changing file size. The final test passed.
An initial Ruff format check found two unformatted files. Ruff formatted both files before the final pass.
An early offline wheel build used version `0.24.0` before the version bump. The final installed wheel reports `0.25.0`.

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
Continue with the [next prompt](PHASE-3B-LOCAL-CONTENT-NEXT-SESSION-2026-10-21.md).
