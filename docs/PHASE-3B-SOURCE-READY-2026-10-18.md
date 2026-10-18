# Phase 3B source-ready boundary

Date: 2026-10-18. Branch: `codex/phase1-architecture`.
Entry revision: `e314651a4f5590f7aea19f678b5e8ad705c83521`. Entry worktree: clean. Entry version: `0.15.11`.
The delivery revision is the commit containing this record. Checkpoint version: `0.15.12`.

## Milestone and result

This session verified the completed Phase 2D, Phase 2E, and Phase 3A source work on macOS.
The accepted plan defines no further core source milestone before Phase 3B admission.
The session changed no production behavior and no frozen Phase 3A package byte.
The source is ready for later consolidated Linux qualification preparation.
This status does not admit a runtime or start Phase 3B calibration.

The existing Phase 2D and Phase 2E tests use the production coordinator, durable store, candidate capture, review, and verdict paths.
They supply deterministic external runtime and validator fixtures.
The 196 selected tests passed from the local checkout.
The same 196 tests passed from a fresh offline wheel installation with network access denied.
The installed package matched all 49 checkout source files and reported version `0.15.12`.
The frozen checker still reports 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
All 146 files in the entry input index matched their recorded sizes and SHA-256 digests.

## Local acceptance

Environment: Darwin 27.2.0 arm64, Python 3.12.15, RTK 0.51.0.
No guest, paid host, Linux test, provider request, or evaluation task ran.
No Jev call ran because the evaluation allowance excludes paid model requests.
Known paid-host and metered API cost was USD 0. Downloaded Linux artifact bytes were zero.
Subscription quota debit for this chat remains unknown.
No selected local check failed. Historical operational failures were not retested.

| Command | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | Entry worktree clean; branch matched `origin/codex/phase1-architecture`. |
| `rtk proxy .venv/bin/python - <<'PY' ... PY` | All 146 entry-index file sizes and SHA-256 digests matched. See the exact command in the prior order record. |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a tests.acceptance.test_phase_2b tests.acceptance.test_phase_2d tests.acceptance.test_phase_2d_core tests.acceptance.test_phase_2d_dispatch tests.acceptance.test_phase_2e tests.acceptance.test_phase_3a tests.acceptance.test_phase_3a_freeze` | Passed 196 tests in 14.139 seconds. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts, 768 planned units, stated digest, and execution disabled. |
| `rtk proxy .venv/bin/ruff check src/crewshal tests/acceptance scripts/check_phase_3a_freeze.py` | Passed. |
| `rtk proxy .venv/bin/ruff format --check src/crewshal tests/acceptance scripts/check_phase_3a_freeze.py` | Passed; 122 files formatted. |
| `rtk proxy .venv/bin/mypy src/crewshal` | Passed; 48 source files. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Users/hamedprooshani/.local/bin/uv build --offline --wheel --out-dir /tmp/crewshal-source-ready-EUowp1/wheel` | Built `crewshal-0.15.12-py3-none-any.whl` offline. |
| `rtk proxy /Users/hamedprooshani/.local/bin/uv venv --offline --python /Volumes/X10Pro/Crewshal/.venv/bin/python /tmp/crewshal-source-ready-EUowp1/installed` | Created a fresh Python 3.12.15 environment. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Users/hamedprooshani/.local/bin/uv pip install --offline --python /tmp/crewshal-source-ready-EUowp1/installed/bin/python --require-hashes -r requirements-dev.lock` | Installed nine locked dependencies offline. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Users/hamedprooshani/.local/bin/uv pip install --offline --no-deps --python /tmp/crewshal-source-ready-EUowp1/installed/bin/python /tmp/crewshal-source-ready-EUowp1/wheel/crewshal-0.15.12-py3-none-any.whl` | Installed the built package offline. |
| `rtk proxy env -i PATH=/tmp/crewshal-source-ready-EUowp1/installed/bin:/usr/bin:/bin HOME=/tmp/crewshal-source-ready-EUowp1/home PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /tmp/crewshal-source-ready-EUowp1/installed/bin/python -m unittest ...` | Passed the same 196 tests in 18.672 seconds. The module list matches the source-suite row. |
| `rtk proxy env -i PATH=/tmp/crewshal-source-ready-EUowp1/installed/bin:/usr/bin:/bin HOME=/tmp/crewshal-source-ready-EUowp1/home PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /tmp/crewshal-source-ready-EUowp1/installed/bin/crewshal --help` | Passed. |
| `rtk proxy /tmp/crewshal-source-ready-EUowp1/installed/bin/python -I - <<'PY' ... PY` | Matched all 49 installed source files and version `0.15.12`. |
| `rtk proxy .venv/bin/python - <<'PY' ... PY` | Verified all 149 next-session indexed file sizes and SHA-256 digests. |
| `rtk proxy .venv/bin/python - <<'PY' ... PY` | Verified local links in six current documents and synchronized version `0.15.12`. |
| `rtk proxy git diff --check` | Passed. |

Linux-specific acceptance modules were deferred. They did not pass in this session.
The deferred scope is `tests.acceptance.test_phase_2c_*` and Linux-specific `tests.acceptance.test_phase_2d_*` outside the selected Mac modules.
The selected Mac modules are `test_phase_2d`, `test_phase_2d_core`, and `test_phase_2d_dispatch`.
Earlier Linux results remain dated records. This session did not reproduce them.

## Campaign boundary

The [consolidated campaign plan](PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-2026-10-18.md) collects the later gates, current inputs, limits, and cleanup.
It remains a plan because exact toolchain, dependency, runtime, and guest admission inputs are unresolved.
The old 8 GiB transfer allowance has zero conservative remaining balance.
The proposed RAM, infrastructure, retained-data, and transfer amendments remain unapproved.
The B1 manual script, safe extraction binding, and effective launch commands remain preparation items.

All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux conformance, native baseline results, and resolved provider identities remain unknown.
Phase 3B calibration and Phase 3C have not started.

Use the [next-session prompt](PHASE-3B-SOURCE-READY-NEXT-SESSION-2026-10-18.md) and its exact input index.
