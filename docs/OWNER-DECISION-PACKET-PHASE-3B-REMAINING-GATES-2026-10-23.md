# Owner decision packet — Phase 3B remaining gates (read-only, 2026-10-23)

Hermes prepared this packet under the Crewshal profile. Codex reviewed and corrected its evidence record.
No source file, version, or Git record changed. This packet is the only new file.
The owner reviews any proposed campaign before host action.

## Session verification

- Branch `codex/phase1-architecture`, HEAD `6279a2e` ("test: verify Phase 3B measurement authority guard (v0.27.3)"). `origin` equals HEAD. Working tree was clean at session start and stayed clean until this packet was written.
- Package version `0.27.3` in `pyproject.toml` (line 7) and `src/crewshal/__init__.py` (line 3), synchronized.
- The expected checkpoint matched: the Codex-reviewed v0.27.3 measurement-authority guard test is committed and published. The packet `docs/CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-GUARD-2026-10-23.md` records that Codex reviewed the candidate and corrected the evidence record. No review or publication is pending.
- Served model `unsloth/Qwen3.8-Flash-Next-GGUF`, provider custom (local GGUF). The exact quantization and server context were unavailable. Hermes could not compare the server window with its pinned window.
- Host: macOS 27.2 arm64. `.venv` CPython 3.12.15. `rtk` 1.0.1 at `/opt/homebrew/bin/rtk`.

## Records read (exact ranges)

1. `AGENTS.md` — lines 1–67 (full file).
2. `/Users/hamedprooshani/.codex/RTK.md` — lines 1–32 (full file).
3. `docs/HANDOFF.md` — lines 5–124 (Current state, including the v0.27.3 and v0.27.2 records and the Oct 21 boundary entries).
4. `docs/DEVELOPMENT-PLAN.md` — lines 1–73 (all eight dated Phase 3B local boundary sections) and lines 554–629 (milestone map, including the Phase 3B row at line 566).
5. `docs/CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-GUARD-2026-10-23.md` — lines 1–40 and 140–156 (scope, changed files, commands, results).
6. `docs/decisions/0009-local-development-before-consolidated-linux-testing.md` — lines 1, 23, 26, 39–40 (consolidated-campaign condition and parked amendments).

## Reported checks and Codex verification at HEAD

| Check | Command | Result |
| --- | --- | --- |
| Five-module regression set | `rtk proxy env -u PYTHONPATH .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch` | Codex ran this command directly: 128 tests passed, exit 0. Hermes reported the same count, but its `tail` pipeline hid the Python exit code. |
| Broad discovery incident | Hermes ran `env -u PYTHONPATH .venv/bin/python -m unittest discover -s tests -t . 2>&1 | tail -3` | The output showed 1418 tests and `OK`. The pipeline hid Python's exit code. It did not exclude Linux-specific modules, contrary to ADR 0009. Do not use this run as local acceptance evidence. |
| Ruff | `rtk proxy .venv/bin/ruff check src tests scripts` | Codex ran this command directly: all checks passed, exit 0. |
| mypy | `rtk proxy .venv/bin/mypy src/crewshal` | Codex ran this command directly: no issues in 48 source files, exit 0. Hermes's earlier `tail` pipeline hid mypy's exit code. |
| Frozen checker | `.venv/bin/python scripts/check_phase_3a_freeze.py` | `consistent-frozen-source-package`, 23 artifacts, 768 planned units, both execution flags false, content sha256 `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0` (unchanged), exit 0 |
| Whitespace | `git diff --check` | clean, exit 0 |

Deferred, not passing claims: Linux platform conformance, Phase 3B calibration, and real-runtime qualification remain closed under ADR 0009.
Hermes ran broad discovery without excluding Linux-specific modules. That run did not authorize Linux qualification or touch a guest.
Installed-wheel checks were not run in this session. The v0.27.3 review packet records the earlier installed-wheel check.

## Codebase graph evidence

- Project `Volumes-X10Pro-Crewshal`, branch `codex/phase1-architecture`, generation `2026-10-23T09:44:23Z`.
- `check_index_coverage` for `scripts/phase3b_development_ledger.py` and `tests/acceptance/test_phase3b_development_ledger.py`: status `no_recorded_issue`, freshness `metadata_match`, recording `complete`. Best-effort signal only; exact source was also read.

## Boundary audit — reviewed local source paths

The current-state record names no further local source condition and requires verification before new implementation.
Hermes found no new condition in the paths and records below. This is a bounded finding, not an exhaustive codebase claim.

1. Hermes read `scripts/phase3b_development_ledger.py` (860 lines). It found six CLI commands: `init`, `check`, `check-evidence`, `check-measurements`, `check-provenance`, and `check-contents`. It inspected the authority guard at lines 404–412 and `read_ledger` at lines 773–784.
2. Content search for `TODO`, `FIXME`, `NotImplemented`, and "not yet implemented" in the ledger script and `src/crewshal/`: no matches.
3. The ledger acceptance module has 20 tests. Their names and reviewed bodies cover the selected authority, evidence, provenance, content, path, and input-file conditions.
4. The newest Phase 3B boundary and milestone map require development corpus runs and a frozen protocol amendment (plan lines 9, 17, 566).
5. The withdrawn commit `4465faf` condition was met by the published v0.27.3 test. No record names another unmet local condition.

## Remaining Phase 3B gates, missing evidence, and owner decisions

| # | Gate (plan line 566) | Missing evidence | Exact owner decision needed | Proposed next action |
| --- | --- | --- | --- | --- |
| G1 | Prerequisite: consolidated Linux qualification (ADR 0009; milestone map line 566) | No admitted qualification for the next campaign. Guests remain closed during development. The prior clone's staging attempt was not submitted. | No decision is required to draft the campaign. Before any host action, approve its exact host, scope, limits, and changed terms. | Prepare the campaign now. Bind inputs, commands, resource ceilings, transfer and storage ledgers, duration, cost exposure, and cleanup. Do not act on a host. |
| G2 | Development corpus runs with complete accounting (192 rows) | All 192 development rows remain planned. Actual runtime identities, admission, and campaign budget remain unresolved. The approved allowance is zero money, zero subscription quota, and zero paid-host spending. | Before any development run, approve a concrete budget and operational admission under ADR 0008. Resolve provider, model, runtime, and quota identities. Do not substitute a local model for frozen campaign identities without an approved amendment. | Prepare an execution proposal after the qualification plan. Keep all rows planned until separate approval and admission pass. |
| G3 | Failures preserved; amended protocol frozen before hold-outs | No development outcomes exist to support a specific amendment. All 576 sealed rows remain unexposed. | No sequencing decision is needed now. Review and approve any concrete protocol amendment after admitted development evidence exists and before hold-out exposure. | Preserve sealed custody. Draft a versioned amendment only when outcomes justify it. |
| G4 | Phase 3B calibration; then Phase 3C gate | Calibration needs admitted corpus runs on a qualified platform (G1+G2). | None new. Existing gates stand. | Keep Phase 3B and 3C closed until their recorded acceptance checks pass. |

## Preservation statement

This session used no Linux guest, no droplet, no evaluation row, no sealed row, no credential store, and no paid service.
Its broad test discovery failed the local test-selection rule. No tracked file, version, or Git record changed.
This packet is the only new file. It remains untracked for owner review. No commit or push occurred.

## Codex quality audit

No code changed, so there is no code diff to review. Codex reviewed this decision packet and corrected its evidence claims.
Codex verified the focused 128-test set, Ruff, mypy, and the frozen checker with direct commands.
The broad discovery run is excluded from acceptance evidence. Its pipeline hid the Python exit code and did not exclude Linux-specific modules.
ADR 0009 permits campaign preparation now. Owner approval is required before the campaign acts or its scope changes.
The gate table now requests decisions only when a concrete campaign, budget, or protocol amendment is ready.

## Continuation prompt (for the next session)

> Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal`. Read `AGENTS.md`, `/Users/hamedprooshani/.codex/RTK.md`, the current state in `docs/HANDOFF.md`, and the Phase 3B gates in `docs/DEVELOPMENT-PLAN.md`. Verify HEAD `6279a2e` or its accepted successor. Read this reviewed decision packet and ADR 0009. Prepare one concrete consolidated Linux qualification campaign document. Bind pinned inputs, exact commands, host options, resource ceilings, transfer and storage ledgers, expected duration, cost exposure, stop rules, and cleanup. Identify each remaining unknown and the exact owner approval needed before any host action. Do not run Linux-specific tests, use guests or a droplet, execute evaluation rows, access sealed tasks or credentials, or spend money. Make no source or version change. Stop with a Codex review packet before commit or push.
