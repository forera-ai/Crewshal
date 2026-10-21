# Phase 3B local provenance checkpoint — 2026-10-21

## Scope and result

This checkpoint extends `scripts/phase3b_development_ledger.py` with a read-only `check-provenance` command.
Each local measurement record now declares `evidence_refs` for its attempt.
Each reference repeats an inventory file name, kind, byte count, and SHA-256 digest.
The measurement bundle also declares the canonical SHA-256 digest of the inventory.
The checker validates the coverage ledger, frozen schedule, inventory, measurement claims, local file bytes, and cross-record links.
It rejects changed inventory content, changed artifact bytes, missing references, and conflicting attempt outcomes.

Run the combined checker from the repository root with existing local files:

```sh
rtk proxy .venv/bin/python -m scripts.phase3b_development_ledger check-provenance LEDGER.json INVENTORY.json MEASUREMENTS.json ARTIFACT_DIRECTORY
```

The `check-measurements` command checks reference syntax but cannot compare references with inventory files.
Use `check-provenance` for the combined local check.
Its `provenance_links_checked: true` result means the declared links match local bytes.
It does not authenticate who created a file or whether an admitted run occurred.
It never changes `evidence_verified: false` or `execution_allowed: false`.
The frozen Phase 3A package remains unchanged.

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `1333e7f9f02ec2751c13bdc70ed940cec5def224` on `codex/phase1-architecture`.
The delivery revision is the commit that contains this record.
Before changes, all 262 files in `docs/PHASE-3B-LOCAL-MEASUREMENTS-INPUTS-2026-10-21.json` matched their sizes and SHA-256 digests.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 121 tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed after formatting. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Execution flags stayed false. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| Local `check-provenance` CLI smoke with a planned ledger and empty bundles | Reported 192 planned rows, zero attempts, and `evidence_verified: false`. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-provenance-wheel` | Built `crewshal-0.23.0-py3-none-any.whl` without network access. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-provenance-install /tmp/crewshal-phase3b-provenance-wheel/crewshal-0.23.0-py3-none-any.whl` | Installed into a temporary target. Import and metadata reported `0.23.0`. |

The first wheel metadata inspection used an unsupported `distribution(path=...)` argument and failed.
The corrected `distributions(path=...)` inspection passed.
Synthetic fixtures covered changed inventory digests, changed file bytes, changed file references, and conflicting attempt outcomes.
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
Local file integrity cannot establish event origin, command execution, or platform qualification.
Phase 3B still needs admitted development corpus runs with complete accounting and preserved failures.
It also needs a protocol amendment frozen before hold-out exposure.
ADR 0009 defers the consolidated Linux campaign until local source development passes its gates.
Continue with the [next prompt](PHASE-3B-LOCAL-PROVENANCE-NEXT-SESSION-2026-10-21.md).
