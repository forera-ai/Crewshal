# Codex review packet — Phase 3B measurement-record authority guard test (v0.27.3)

Hermes prepared the candidate on 2026-10-23 (Europe/Vienna). Codex reviewed it and corrected the evidence record.

## Milestone and scope

Selected condition (named by the reviewed v0.27.2 packet's next-session prompt): measurement records must not grant execution authority.
The guard already exists at `scripts/phase3b_development_ledger.py:404-412` inside `check_measurements`. This candidate adds one acceptance test that pins its six refusals and proves each guarded clause is load-bearing.
No production source changed. No new rule, adapter, or architecture was added.

## Base revision and working state

- Branch `codex/phase1-architecture`, base HEAD `fb7ec59` (published, reviewed v0.27.2 checkpoint; origin == HEAD at session start).
- Working tree was clean at session start. The candidate is uncommitted: six tracked files modified, plus this new packet file (untracked; part of the commit).
- Package version moves `0.27.2` → `0.27.3` in `pyproject.toml` and `src/crewshal/__init__.py` (synchronized).

## Changed files

1. `tests/acceptance/test_phase3b_development_ledger.py` — one new test method (+21 lines).
2. `pyproject.toml` — version bump.
3. `src/crewshal/__init__.py` — version bump.
4. `README.md` — one new Current-status entry; dated entries unchanged.
5. `CHANGELOG.md` — one new `0.27.3` section.
6. `docs/HANDOFF.md` — one new Current-state record above the preserved v0.27.2 record.
7. `docs/CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-GUARD-2026-10-23.md` — this packet (new file).

## Exact tracked diff (`git diff --no-ext-diff --unified=0` at HEAD `fb7ec59`)

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b97271e..a667563 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -2,0 +3,8 @@
+## 0.27.3 — 2026-10-23
+
+- Add one focused acceptance test that measurement records cannot grant execution authority.
+- Cover six refusals: execution authority, spend authority, verified status, record-kind change, frozen-package rebind, and annotation-method change.
+- Prove each refusal with one single-clause mutation kill against the existing guard.
+- Keep production source unchanged; treat withdrawn commit `4465faf` as historical evidence only.
+- Keep the frozen package, evaluation rows, and all execution flags unchanged.
+
diff --git a/README.md b/README.md
index 0e1d64f..b8ee548 100644
--- a/README.md
+++ b/README.md
@@ -12,0 +13,7 @@ The hypothesis: a human-confirmed model of an unfamiliar repository can reduce m
+**October 23: The Phase 3B measurement-record authority guard test passed Codex review.**
+The focused acceptance test proves `check_measurements` refuses a measurement record that self-declares execution authority, spend authority, verified status, an evidence-inventory kind, a foreign frozen package, or a changed annotation method.
+Each refusal passed one single-clause mutation kill; removing any guarded clause fails its exact claim.
+No production source changed. The [review packet](docs/CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-GUARD-2026-10-23.md) holds the exact diff, results, limits, and review outcome.
+All 192 development rows remain planned. All 576 sealed rows remain unexposed.
+Linux qualification and Phase 3B calibration remain closed.
+
diff --git a/docs/HANDOFF.md b/docs/HANDOFF.md
index 85af797..e077efe 100644
--- a/docs/HANDOFF.md
+++ b/docs/HANDOFF.md
@@ -6,0 +7,16 @@ Last updated: 2026-10-23. This record supplies the next session and the owner wi
+**October 23: The Phase 3B measurement-record authority guard test passed Codex review (v0.27.3).**
+The new acceptance test `test_measurement_records_cannot_grant_authority_or_change_kind` proves `check_measurements` refuses a measurement record that self-declares execution authority, spend authority, verified status, an evidence-inventory kind, a foreign frozen package, or a changed annotation method.
+A valid unverified record still passes the same guard. Each of the six refusals failed its exact claim under one single-clause mutation kill; the guard file returned byte-identical to HEAD (`git diff` clean on `scripts/phase3b_development_ledger.py`).
+No production source changed. The guard at `scripts/phase3b_development_ledger.py:404-412` was already live.
+The added test matches the test in withdrawn commit `4465faf`, which commit `18b7a35` reverted.
+Codex verified the test against the current guard. No approval claim from the withdrawn commit was reused.
+Local results: focused module 20 tests OK; five-module regression set 128 tests OK (baseline 127); Ruff, mypy, frozen checker (`consistent-frozen-source-package`, content sha256 `4bd188deb0…dc892c0` unchanged), and `git diff --check` clean. Linux-specific modules remain deferred per ADR 0009.
+Codex repeated the 128-test regression set, Ruff, mypy, and frozen-package checks.
+Codex also built and installed an offline wheel without pipelines. The fresh installed package reported `0.27.3`.
+The [review packet](CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-GUARD-2026-10-23.md) holds the exact diff, commands, results, limits, and review outcome.
+Hermes made no commit or push. Codex verified the test and corrected the evidence record before publication.
+Changed files: `tests/acceptance/test_phase3b_development_ledger.py`, `pyproject.toml`, `src/crewshal/__init__.py`, `README.md`, `CHANGELOG.md`, `docs/HANDOFF.md`, and the review packet.
+Remaining Phase 3B acceptance needs development corpus runs and a frozen protocol amendment.
+The next session must identify each required owner decision and the ADR 0009 Linux qualification gate before action.
+Current records name no further local source condition; verify that boundary before new implementation.
+
diff --git a/pyproject.toml b/pyproject.toml
index 0adf7cf..18e6354 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7 +7 @@ name = "crewshal"
-version = "0.27.2"
+version = "0.27.3"
diff --git a/src/crewshal/__init__.py b/src/crewshal/__init__.py
index 63ebfe5..595961d 100644
--- a/src/crewshal/__init__.py
+++ b/src/crewshal/__init__.py
@@ -3 +3 @@
-__version__ = "0.27.2"
+__version__ = "0.27.3"
diff --git a/tests/acceptance/test_phase3b_development_ledger.py b/tests/acceptance/test_phase3b_development_ledger.py
index cbde098..fda7ace 100644
--- a/tests/acceptance/test_phase3b_development_ledger.py
+++ b/tests/acceptance/test_phase3b_development_ledger.py
@@ -236,0 +237,21 @@ class Phase3BDevelopmentLedger(unittest.TestCase):
+    def test_measurement_records_cannot_grant_authority_or_change_kind(self):
+        candidate = copy.deepcopy(self.planned)
+        row = candidate["rows"][0]
+        row.update(status="failed", reason="Synthetic refusal.", attempt_ids=["attempt-1"])
+        base = self._measurement(candidate, 0, "attempt-1")
+        ledger.check_measurements(candidate, self._measurement_bundle(candidate, [base]))
+        claims = (
+            ("execution authority", lambda item: item.update(execution_allowed=True)),
+            ("spend authority", lambda item: item.update(spend_authorized=True)),
+            ("verification status", lambda item: item.update(status="verified")),
+            ("record kind", lambda item: item.update(record_kind=ledger.EVIDENCE_KIND)),
+            ("frozen package rebind", lambda item: item.update(package_id="phase3a-99999999-v9")),
+            ("annotation method", lambda item: item.update(annotation_method="self-grading")),
+        )
+        for label, mutate in claims:
+            record = copy.deepcopy(base)
+            mutate(record)
+            bundle = self._measurement_bundle(candidate, [record])
+            with self.subTest(claim=label), self.assertRaisesRegex(ERROR, "authority or kind"):
+                ledger.check_measurements(candidate, bundle)
+
```

This packet file is new and untracked; `git diff` above cannot show it. Its content is this document.

## Acceptance mapping

- Observable acceptance behavior: a valid unverified measurement record passes `check_measurements` unchanged (positive baseline asserted in-test), and each of six self-granting mutations raises `FreezeError` matching "authority or kind" — the guard's message is `measurement claims authority or kind mismatch`.
- Refusal cases (all six, via `subTest(claim=...)`): `execution_allowed=True`, `spend_authorized=True`, `status="verified"`, `record_kind=EVIDENCE_KIND`, `package_id="phase3a-99999999-v9"`, `annotation_method="self-grading"`.
- Guard load-bearing proof (mutation kill, six runs): each run removed exactly one conjunct from the guard clause and re-ran only the new test. All six mutants were killed at their exact claim: `(claim='record kind')`, `(claim='verification status')`, `(claim='execution authority')`, `(claim='spend authority')`, `(claim='frozen package rebind')`, `(claim='annotation method')`. After each run the guard file was rewritten from a byte copy taken before mutation; final `git diff` on `scripts/phase3b_development_ledger.py` is empty and `cmp` against `git show HEAD:...` reported identical.
- Separation preserved: the test asserts refusals of self-declared authority inside records. It grants no execution authority. A passing match report still never authenticates an admitted run; all record kinds in this module stay `not-execution-proof`.

## Graph and coverage evidence (Verify tier)

- Graph project `Volumes-X10Pro-Crewshal`, generation `2026-10-23T09:14:46Z`, status ready.
- `check_index_coverage` for both material paths (`scripts/phase3b_development_ledger.py`, `tests/acceptance/test_phase3b_development_ledger.py`): `no_recorded_issue`, freshness `metadata_match`. Best-effort caveat applies; exact source was read anyway (guard lines 317–628, test helpers lines 500–612).
- The only parse-partial file in the index is `src/crewshal/bootstrap_helper.c` (unrelated to this candidate).

## Withdrawn-commit boundary

Commit `4465faf` introduced the same 21-line test. Commit `18b7a35` reverted it.
Hermes inspected that history and added the same test to the current checkout.
Codex verified the test against the current guard. No approval claim from the withdrawn commit was reused.
The candidate adds new status entries and preserves earlier dated entries.

## Tests and results (macOS 27.2 arm64, CPython 3.12.15 in `.venv`)

Main checks ran from `/Volumes/X10Pro/Crewshal` through RTK with `env -u PYTHONPATH`.
Some mutation and wheel commands called executables directly. Installed-wheel imports ran from `/tmp`.

| Check | Result |
| --- | --- |
| Baseline regression set (`test_phase3b_development_ledger`, `test_phase_3a_freeze`, `test_phase_3a`, `test_phase_2e`, `test_phase_2d_dispatch`) before the edit | Ran 127 tests, OK, exit 0 |
| Focused module after the edit (`tests.acceptance.test_phase3b_development_ledger`) | Ran 20 tests, OK, exit 0 (was 19) |
| Six single-clause mutation kills (one run per conjunct) | all killed, exit 1 each, failure marker names the matching claim; guard restored byte-identical to HEAD |
| Same regression set after the edit and version bump | Ran 128 tests, OK, exit 0 |
| `.venv/bin/ruff check src tests scripts` (after edit) | All checks passed, exit 0 |
| `.venv/bin/ruff format --check tests/acceptance/test_phase3b_development_ledger.py` | 1 file already formatted, exit 0 |
| `.venv/bin/mypy` (pinned target `src/crewshal`) | Success: no issues found in 48 source files, exit 0 |
| `python scripts/check_phase_3a_freeze.py` (before and after the version bump) | `consistent-frozen-source-package`, 23 artifacts, 768 planned units, both execution flags false, content sha256 `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0` unchanged; exit 0 both times |
| `git diff --check` | clean, exit 0 (twice) |
| Offline wheel build: `uv build --wheel --offline --out-dir /tmp/crewshal-q3-review.Y5GFFh` | built `crewshal-0.27.3-py3-none-any.whl`, exit 0 |
| Fresh offline install: `uv pip install --offline --no-deps --target /tmp/crewshal-q3-review.Y5GFFh/installed-final /tmp/crewshal-q3-review.Y5GFFh/crewshal-0.27.3-py3-none-any.whl` | installed `crewshal==0.27.3`, exit 0 |
| Installed import from `/tmp`: `PYTHONPATH=/tmp/crewshal-q3-review.Y5GFFh/installed-final /Volumes/X10Pro/Crewshal/.venv/bin/python -c 'import crewshal, importlib.metadata; print(crewshal.__file__); print(crewshal.__version__); print(importlib.metadata.version("crewshal"))'` | module path `/tmp/crewshal-q3-review.Y5GFFh/installed-final/crewshal/__init__.py`; package and metadata versions `0.27.3`; exit 0 |
| Codex offline build: `uv build --wheel --offline --out-dir /tmp/crewshal-v0273-review.QFy6Y8` | built `crewshal-0.27.3-py3-none-any.whl`, exit 0 without a pipeline |
| Codex fresh install: `uv pip install --offline --no-deps --target /tmp/crewshal-v0273-review.QFy6Y8/installed /tmp/crewshal-v0273-review.QFy6Y8/crewshal-0.27.3-py3-none-any.whl` | installed `crewshal==0.27.3`, exit 0 without a pipeline |
| Codex installed import from `/tmp`: `PYTHONPATH=/tmp/crewshal-v0273-review.QFy6Y8/installed /Volumes/X10Pro/Crewshal/.venv/bin/python -c 'import crewshal, importlib.metadata; print(crewshal.__file__); print(crewshal.__version__); print(importlib.metadata.version("crewshal"))'` | module path inside fresh target; package and metadata versions `0.27.3`; exit 0 |

Hermes piped the wheel build and install output through `tail`. Its recorded exit codes belong to `tail`, not `uv`.
The success messages, installed target, and import support the result. Codex reran build and install without pipelines.
One mutation script stopped on the sixth clause because its search anchor did not match.
Hermes restored the guard before the next command and ran the sixth mutant separately.
The final guard bytes matched HEAD. The packet's six kills include that separate run.

## Deferred checks (not run; recorded as deferred, not passing)

- Linux-specific acceptance modules and Phase 2C/2D platform qualification: deferred per ADR 0009 and the owner's October 18 instruction.
- The full repository test suite beyond the five-module regression set was not run this session; the five-module set is the designated start-prompt set.
- B1 conformance, live runtime qualification, Phase 3B calibration: remain closed until their gates pass.

## Risks, unknowns, and costs

- Pre-existing condition (not introduced here): `ruff format --check src tests scripts` lists 11 unformatted files (`scripts/phase3b_*` Linux-probe artifacts and `tests/acceptance/test_phase3b_capped_archive.py`). They predate base HEAD `fb7ec59`; this candidate changes none of them. The prior packet scoped Ruff format to touched files; this packet does the same, explicitly.
- Unknown: whether any reviewer treats withdrawn commit `4465faf` as evidence. This packet asserts nothing about it beyond "historical, unverified".
- Risk: the test pins six exact field mutations. A future self-granting field added outside the guard's clause list would not be caught by this test; it would need a new guard clause and a new claim row.
- Hermes staged an unrelated `crewshal-dev-session` skill edit for approval (`25d95f6b`) after preparing the packet. The edit was not saved.
- The Crewshal profile prohibits skill edits during a source session. Do not approve that pending edit without a separate review.
- Cost exposure: zero money, zero subscription quota, zero paid-host spending. No evaluation row was executed. All 192 development rows remain planned; all 576 sealed rows remain unexposed.
- The frozen Phase 3A package and private sealed-task custody are unchanged and unexposed (`docs/evaluation/phase-3a-frozen` shows no diff).

## Codex review and publication boundary

Codex reviewed the complete candidate and found no source-code defect. The test checks a valid record and six precise refusals.
Codex corrected the withdrawn-commit lineage and the mutation incident record.
Codex independently reran 128 local tests, Ruff, mypy, and the frozen package check.
Hermes made no commit or push. The delivery revision is the checkpoint commit containing this packet.
Codex must verify the branch push at session closure.

## Next-session prompt (after this checkpoint is published)

"Start a fresh Crewshal session in /Volumes/X10Pro/Crewshal. Read AGENTS.md, docs/HANDOFF.md, and docs/DEVELOPMENT-PLAN.md in that order. Verify a clean published HEAD at v0.27.3. Audit the remaining Phase 3B gates against current records. If a bounded, safe macOS source condition remains, name it and work on one milestone. Otherwise, prepare a read-only decision packet. List each remaining gate, its blocking evidence, and the exact owner decision or qualification it requires. Do not use Linux guests, evaluation rows, sealed rows, or paid services. Stop before commit or push and request Codex review."
