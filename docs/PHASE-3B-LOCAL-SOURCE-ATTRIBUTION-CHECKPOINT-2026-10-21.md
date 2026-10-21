# Phase 3B local source attribution checkpoint — 2026-10-21

## Scope and result

This checkpoint extends the read-only development measurement checker with field-level `source_refs`.
Each populated observation names one or more files from that attempt's `evidence_refs`.
The requirement covers the date, outcome, reason, observed unit and identity fields, effort, token counts, and usage provenance.
It also covers populated cost fields and nonempty checks, claims, review, and waivers.
Zero measurements need sources. Frozen package identity, schedule values, and fixed accounting rules need no new file link.
The checker rejects missing fields, extra fields, duplicate file names, and file names absent from the attempt.
`check-provenance` also matches those declared files to inventory entries and local bytes.

These links identify declared local files. They do not prove that a file contains the claimed value.
They do not authenticate a file's creator, an execution event, or a platform.
All results keep `evidence_verified: false` and `execution_allowed: false`.
The frozen Phase 3A package remains unchanged.

## Local verification

Environment: macOS Darwin 27.2.0 arm64 and Python 3.12.15 in `.venv`.
Base revision: `b724ab6480c95a921298a1e778e1fa4f97d82a5e` on `codex/phase1-architecture`.
The delivery revision is the commit that contains this record.
Before changes, all 264 files in `docs/PHASE-3B-LOCAL-PROVENANCE-INPUTS-2026-10-21.json` matched their sizes and SHA-256 digests.
Git showed no working-tree changes at the start.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | 122 local tests passed. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | All checks passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_development_ledger.py tests/acceptance/test_phase3b_development_ledger.py` | Both files passed. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | All 23 artifacts and 768 planned units matched. Both execution flags stayed false. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files. |
| `rtk proxy uv build --offline --wheel --out-dir /tmp/crewshal-phase3b-source-wheel` | Built `crewshal-0.24.0-py3-none-any.whl`. |
| `rtk proxy uv pip install --offline --no-deps --target /tmp/crewshal-phase3b-source-install /tmp/crewshal-phase3b-source-wheel/crewshal-0.24.0-py3-none-any.whl` | Installed the wheel without network access. |
| Isolated installed-target import and metadata check | Import and metadata both reported `0.24.0`. |
| `rtk proxy git diff --check` | No whitespace errors. |

Synthetic fixtures rejected unlinked zero values, unlinked cost fields, unlinked check details, missing files, and repeated source names.
They also checked that local file changes still fail the combined provenance check.
No check authenticated the contents or creator of a source file.
No command failed in this checkpoint.

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
Continue with the [next prompt](PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-NEXT-SESSION-2026-10-21.md).
