# Codex review packet — Phase 3B measurement authority guard test

Date: 2026-10-22 (Europe/Vienna). Prepared before publication for Codex supervision and review.

## Milestone

One bounded Phase 3B local source milestone: prove the read-only development ledger refuses a measurement record that claims authority or changes its kind. The guard already existed in production code. This checkpoint adds one acceptance test and proves each refusal path. No production source changed. No Linux action occurred. No spend occurred.

## Base revision and branch

Base revision: `06b40c5` on branch `codex/phase1-architecture`. That commit reverted commit `a2e26ba`, which added read-ledger input-file protection tests without review. The checkout was clean before edits. Verification ran on macOS 27.2 arm64 with the repository `.venv/bin/python` (CPython 3.12).

## Changed files

- `tests/acceptance/test_phase3b_development_ledger.py` — one new test method.
- `README.md` — version line to `0.27.2` and one new current-status paragraph.
- `CHANGELOG.md` — new `0.27.2` entry.
- `docs/HANDOFF.md` — date update and one new current-state entry.
- `pyproject.toml` and `src/crewshal/__init__.py` — version `0.27.1` to `0.27.2`.
- This packet document (new).

## Exact diff of the production-relevant change

The only test-source change:

```diff
--- a/tests/acceptance/test_phase3b_development_ledger.py
+++ b/tests/acceptance/test_phase3b_development_ledger.py
@@ -233,6 +233,27 @@ class Phase3BDevelopmentLedger(unittest.TestCase):
         record["source_refs"]["checks"] = self._source("attempt-1.json", "checks")
         ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))
 
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
     def test_provenance_links_measurements_to_inventory_and_local_bytes(self):
```

## Guard under test

The guard is the `freeze.require` block at `scripts/phase3b_development_ledger.py:404-412`. Each measurement record must keep `record_kind` equal to the measurement kind, keep status `unverified-development-claim`, keep `execution_allowed` false, keep `spend_authorized` false, keep the frozen `package_id`, and keep the frozen `annotation_method`. Any breach raises the shared error with message "measurement claims authority or kind mismatch".

## Acceptance mapping

1. A valid base measurement passes before any escalation is applied. The test calls `check_measurements` on the unmodified record first.
2. Each of six escalation claims is applied to a deep copy and must raise. All six subtests pass: execution authority, spend authority, verification status, record kind change, frozen package rebind, and annotation method change.
3. The guard rejects through the production path only. The test uses `ledger.check_measurements`, the same command interface as prior checkpoints. It adds no new ledger behavior or helper hooks.
4. The frozen Phase 3A package stays byte-identical. The package checker exits zero after the change.

## Refusal cases proved

The six subtests above are the refusal cases. Each proves a distinct field cannot be escalated inside a measurement record: authority flags, status, kind, package binding, and annotation method.

## Commands and results

All commands ran in `/Volumes/X10Pro/Crewshal` on 2026-10-22. Exit codes are as reported.

- `.venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger -v` — Ran 19 tests, OK (exit 0). Baseline before the change was 18 tests, OK.
- `.venv/bin/python scripts/check_phase_3a_freeze.py` — exit 0; frozen package bytes unchanged.
- `.venv/bin/python -m ruff check tests/acceptance/test_phase3b_development_ledger.py` — All checks passed (exit 0).
- `.venv/bin/python -m ruff format --check tests/acceptance/test_phase3b_development_ledger.py` — already formatted (exit 0).
- `.venv/bin/python -m mypy src` — Success: no issues found in 48 source files (exit 0).
- `git diff --check` — clean.
- Version sync confirmed: `pyproject.toml` and `src/crewshal/__init__.py` both report `0.27.2`.

## Limitations and deferred checks

- Linux-specific test modules were not run. They remain deferred, not passing (ADR 0009).
- The full offline suite was not re-run. The change touches one test module, documentation, and the version strings only. No production source file changed.
- `ruff format --check` over all of `src scripts tests` reports pre-existing drift in unrelated Linux probe scripts. This checkpoint changes none of those files.

## Open question for the owner and Codex

Commit `a2e26ba` was reverted by `06b40c5` without a recorded reason beyond "unreviewed". Its read-ledger input-file protection tests were not re-added here. If the revert targeted the test content rather than the process, that work needs a fresh decision.

## Gates kept closed

No execution authority, spend authority, subscription quota use, paid-host action, guest action, merge, deployment, or package release occurred or is implied. All 192 development rows remain planned. All 576 sealed rows remain unexposed. Linux qualification and Phase 3B calibration remain closed.

## Next-session prompt (suggested)

"Continue Crewshal local development from docs/HANDOFF.md. Resolve the open question on the reverted read-ledger tests with Codex, then select one new bounded Phase 3B local source condition from docs/DEVELOPMENT-PLAN.md. Keep all gates closed."

Exact inputs: `AGENTS.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, `docs/CODEX-REVIEW-PACKET-PHASE-3B-MEASUREMENT-AUTHORITY-TEST-2026-10-22.md`, `scripts/phase3b_development_ledger.py`, `tests/acceptance/test_phase3b_development_ledger.py`.
