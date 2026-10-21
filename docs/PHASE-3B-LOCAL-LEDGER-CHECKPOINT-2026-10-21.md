# Phase 3B local development ledger checkpoint — 2026-10-21

## Scope and result

This checkpoint adds `scripts/phase3b_development_ledger.py` and five local fixture tests.
The script checks the frozen Phase 3A package before it reads the development schedule.
Its `init` command prints one planned ledger entry for each of the 192 development rows.
Its `check` command rejects missing, repeated, changed, or reordered schedule entries.
It also rejects added execution authority, missing reasons, and repeated attempt IDs.
It reports status counts but does not authenticate attempts or verify run evidence.
The script reads the public sealed schedule only to confirm its 576-row count.
It does not read private sealed task content or change frozen Phase 3A bytes.

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `3a8ccfff33f36e5f071c1a07fb42e374800307d0` on `codex/phase1-architecture`.
The exact input index matched all 252 files before source changes.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger` | Five tests passed. |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 113 tests passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | 23 frozen artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/mypy scripts/phase3b_development_ledger.py` | Failed with 165 errors. The new script and imported frozen checker lack type annotations. Ruff supplies this script's static acceptance check. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| `rtk proxy .venv/bin/python -m scripts.phase3b_development_ledger init > /tmp/crewshal-phase3b-development-ledger-20261021.json` | Wrote a synthetic planned ledger outside the repository. |
| `rtk proxy .venv/bin/python -m scripts.phase3b_development_ledger check /tmp/crewshal-phase3b-development-ledger-20261021.json` | Reported 192 planned rows, 576 sealed rows, and `evidence_verified: false`. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-local-wheel` | Built `crewshal-0.20.0-py3-none-any.whl` without network access. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-local-install /tmp/crewshal-phase3b-local-wheel/crewshal-0.20.0-py3-none-any.whl` | Installed the wheel into a temporary target. Its metadata and imported version both reported `0.20.0`. |

The virtual environment has no `pip` module, so the first wheel command failed.
The offline `uv` build and temporary installation passed instead.

These commands used local files only. They made no network or provider request.
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
The single admission ledger closes that staging attempt and admits no restart or stage.
Phase 3B still needs development corpus runs with complete accounting and preserved failures.
It also needs an amended protocol frozen before hold-out exposure.
ADR 0009 defers the consolidated Linux campaign until source development passes local checks.
Do not treat this coverage ledger as execution authority or run evidence.
