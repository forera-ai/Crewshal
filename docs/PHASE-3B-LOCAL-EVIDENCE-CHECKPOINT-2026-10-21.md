# Phase 3B local evidence inventory checkpoint — 2026-10-21

## Scope and result

This checkpoint extends `scripts/phase3b_development_ledger.py` with a read-only `check-evidence` command.
It checks one inventory entry for each attempt ID declared in the development ledger.
Each entry must match its schedule row and condition digest.
The last declared attempt must match the ledger outcome and reason.
The command checks every declared artifact size and SHA-256 digest through a directory file descriptor.
It refuses missing attempts, changed bytes, repeated names, symbolic links, and path escapes.
Each attempt needs a nonempty `run` artifact.

The inventory format has `schema_version`, `record_kind`, `package_content_sha256`, `ledger_sha256`, and `attempts`.
The ledger digest uses canonical JSON with sorted keys and compact separators.
Each attempt has `attempt_id`, `schedule_row_id`, `condition_sha256`, `outcome`, `reason`, and `files`.
Each file has `name`, `kind`, `bytes`, and `sha256`.
Artifact names are single basenames. Each file must contain 1 through 8,388,608 bytes.

Run the checker from the repository root with an existing ledger and inventory:

```sh
rtk proxy .venv/bin/python -m scripts.phase3b_development_ledger check-evidence LEDGER.json INVENTORY.json ARTIFACT_DIRECTORY
```

The checker verifies declared file integrity only. A digest does not prove that a run occurred.
It does not verify commands, provider identity, platform qualification, checks, review judgments, or admission.
It always reports `evidence_verified: false` and `execution_allowed: false`.
Do not use its output to mark a development row verified.

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `d67358c` on `codex/phase1-architecture`.
Before changes, all 257 files in `docs/PHASE-3B-LOCAL-LEDGER-INPUTS-2026-10-21.json` matched their recorded sizes and SHA-256 digests.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 116 tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Execution flags stayed false. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| Local `check-evidence` CLI smoke with a planned ledger and empty inventory | Reported 192 planned rows, zero attempts, and `evidence_verified: false`. |
| Offline wheel build and temporary installation | The installed package metadata and imported version reported `0.21.0`. |

The fixture tests cover changed bytes, missing attempts, a false final outcome, path escape, and symbolic links.
They use local synthetic artifacts and run no repository task or provider process.
The checker has no source of authenticated run provenance.

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
Phase 3B needs admitted development corpus runs with complete accounting and preserved failures.
It also needs an amended protocol frozen before hold-out exposure.
ADR 0009 defers the consolidated Linux campaign until local source development passes its gates.
