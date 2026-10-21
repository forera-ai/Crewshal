# Phase 3B local source review handoff checkpoint — 2026-10-21

## Scope and result

This checkpoint extends the read-only `check-contents` result for each declared claim source.
Each result now includes the inventory file kind, byte count, and SHA-256 digest.
It retains the attempt ID, field, file name, declared JSON path, status, and detail.
Every result sets `admitted_source_review_required: true`.
The result keeps `evidence_verified: false` and `execution_allowed: false`.

These fields let a later reviewer locate the exact declared file and value path.
The inventory digest binds local bytes, but it does not identify the file's creator.
A matching value does not prove that an admitted event produced the file.
Missing paths remain `unmatched`. Invalid JSON and non-JSON files remain `unsupported`.
Wrong values remain `unmatched`. The checker does not search another path for a match.
No result can establish event origin without admitted run evidence.
The frozen Phase 3A package remains unchanged.

## Local verification

Environment: macOS Darwin 27.2.0 arm64, CPython 3.12.15, and the project `.venv`.
Base revision: `279e07485d3bdf6355c7199d8b8a333f16101eb9` on `codex/phase1-architecture`.
The delivery revision is the commit containing this record.
Git was clean before changes. All 273 exact starting input files matched their sizes and SHA-256 digests.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 126 local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-review-wheel-v027` | Built `crewshal-0.27.0-py3-none-any.whl`. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-review-install-v027 /tmp/crewshal-phase3b-review-wheel-v027/crewshal-0.27.0-py3-none-any.whl` | Installed without network access. |
| Isolated installed-target import and metadata check | Both versions reported `0.27.0` from the installed target. |
| `rtk proxy git diff --check` | No whitespace errors. |

Synthetic fixtures covered matched, unmatched, and unsupported sources with their inventory metadata.
They also kept admitted review required for matching sources.
No local check failed in this checkpoint.
No Linux-specific test module ran. Linux qualification and native conformance remain deferred.
No guest action, archived tool execution, native turn, or evaluation row ran.
No new network transfer occurred. Paid host and metered API costs were zero.
No Jev model call occurred under the zero-spending evaluation allowance.
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
Continue with the [next prompt](PHASE-3B-LOCAL-REVIEW-NEXT-SESSION-2026-10-21.md).
