# Codex review packet — Phase 3B read-ledger input-file protection test, v0.27.2

Date: 2026-10-23. Hermes prepared the candidate. Codex reviewed it and corrected the evidence record before publication.

## Milestone and acceptance behavior

Milestone: one focused acceptance condition for the Phase 3B development ledger reader.
Acceptance behavior: `scripts/phase3b_development_ledger.py::read_ledger` parses a regular bounded ledger file unchanged, and refuses four unsafe input classes.
Refusal case (required): a symlinked ledger path must fail with `OSError` and `errno.ELOOP`; its target is never opened.
Second refusal family covered: directory input fails the regular-file check; empty and oversize inputs fail the size bound before parsing.

## Baseline and branch

- Base revision: `18b7a3568427e728ad64cba8c33a7d5b4f4ae20b` (`Revert "test: prove measurement records cannot grant authority (v0.27.2)"`).
- Branch: `codex/phase1-architecture`, tracking `origin/codex/phase1-architecture`.
- Working tree before this session: clean at the base revision.
- Package version before: `0.27.1` in both `pyproject.toml` and `src/crewshal/__init__.py`. After: `0.27.2`, synchronized.

## Served model record

- Served model: `unsloth/Qwen3.8-Flash-Next-GGUF` (llama-server alias).
- Quantization: UD-IQ3_XXS (`Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00003.gguf`).
- Server context: `-c 119296` with `--fit-ctx 119296`. Hermes profile `context_length: 119296`. No mismatch.

## Lineage — why this is a re-presentation

Commit `a2e26ba` (test + packet, base `049cffd`) and commit `4465faf` were pushed and then reverted (`06b40c5`, `18b7a35`).
The earlier packets claimed a Codex APPROVE verdict. That claim was never verified; treat it as untrusted.
Commit `4465faf` also edited the dated October 21 README entry in place, which violates the dated-record rule.
This submission excludes both defects: no dated entry is changed, and no review verdict is claimed here.
The test content itself was called useful in SOUL.md; it is re-presented with one fix already embedded (the explicit `errno.ELOOP` assertion).

## Changed files — tracked changes appear in the diff below

1. `tests/acceptance/test_phase3b_development_ledger.py` — add `import errno`; add `test_read_ledger_refuses_invalid_input_files`.
2. `pyproject.toml` — version `0.27.1` → `0.27.2`.
3. `src/crewshal/__init__.py` — `__version__` `0.27.1` → `0.27.2`.
4. `README.md` — new October 23 reviewed status entry inserted under Current status; October 21 and earlier entries byte-identical.
5. `CHANGELOG.md` — new `## 0.27.2 — 2026-10-23` entry on top; older entries byte-identical.
6. `docs/HANDOFF.md` — rolling header date updated; new October 23 reviewed entry added at the top of Current state; all earlier entries byte-identical.
7. `docs/CODEX-REVIEW-PACKET-PHASE-3B-READ-LEDGER-INPUT-PROTECTION-2026-10-23.md` — this packet; new untracked file, so it cannot appear inside its own diff.

No production source changed. The frozen Phase 3A package is untouched.

## Exact diff (tracked files, `git diff --no-ext-diff --unified=0` at HEAD `18b7a35`)

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 9ad0bdd..b97271e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -2,0 +3,8 @@
+## 0.27.2 — 2026-10-23
+
+- Add one focused acceptance test for Phase 3B `read_ledger` input-file protections.
+- Cover regular-file round-trip parsing plus symlink, directory, empty, and oversize refusals.
+- Assert `errno.ELOOP` for symlink traversal refusal.
+- Re-present the withdrawn v0.27.2 read-ledger test work under a Codex review boundary.
+- Keep the frozen package, evaluation rows, and all execution flags unchanged.
+
diff --git a/README.md b/README.md
index adf80a5..0e1d64f 100644
--- a/README.md
+++ b/README.md
@@ -12,0 +13,7 @@ The hypothesis: a human-confirmed model of an unfamiliar repository can reduce m
+**October 23: The Phase 3B read-ledger input-file protection test passed Codex review.**
+The focused acceptance test proves `read_ledger` refuses symlinked, directory, empty, and oversize input files.
+A regular bounded ledger file parses unchanged; the symlink refusal asserts `errno.ELOOP`.
+The [review packet](docs/CODEX-REVIEW-PACKET-PHASE-3B-READ-LEDGER-INPUT-PROTECTION-2026-10-23.md) holds the exact diff, results, and review outcome.
+All 192 development rows remain planned. All 576 sealed rows remain unexposed.
+Linux qualification and Phase 3B calibration remain closed.
+
diff --git a/docs/HANDOFF.md b/docs/HANDOFF.md
index b7f595a..85af797 100644
--- a/docs/HANDOFF.md
+++ b/docs/HANDOFF.md
@@ -3 +3 @@
-Last updated: 2026-10-21. This record supplies the next session and the owner with project history. [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines the milestone acceptance checks. Preserve the session ledger.
+Last updated: 2026-10-23. This record supplies the next session and the owner with project history. [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines the milestone acceptance checks. Preserve the session ledger.
@@ -6,0 +7,21 @@ Last updated: 2026-10-21. This record supplies the next session and the owner wi
+**October 23: The Phase 3B read-ledger input-file protection test passed Codex review.**
+The focused acceptance test covers `read_ledger` refusals for symlink, directory, empty, and oversize inputs, plus regular-file round-trip parsing.
+The symlink case asserts `errno.ELOOP`.
+This re-presents the withdrawn v0.27.2 read-ledger test work (commits `a2e26ba`, reverted by `06b40c5`) under a fresh review boundary.
+The earlier packet's Codex APPROVE claim was not verified, and commit `4465faf` edited a dated README entry; both defects are excluded here.
+The [review packet](CODEX-REVIEW-PACKET-PHASE-3B-READ-LEDGER-INPUT-PROTECTION-2026-10-23.md) holds the exact diff, tests, results, and review outcome.
+Codex found no code defect. Codex corrected the package-check labels and verified a fresh offline wheel install.
+Changed files: `tests/acceptance/test_phase3b_development_ledger.py`, `pyproject.toml`, `src/crewshal/__init__.py`, `README.md`, `CHANGELOG.md`, `docs/HANDOFF.md`, and the review packet.
+The version is `0.27.2` in the working tree (`pyproject.toml` and `src/crewshal/__init__.py` synchronized). Base revision: `18b7a3568427e728ad64cba8c33a7d5b4f4ae20b` on `codex/phase1-architecture`.
+Verification ran on macOS 27.2 arm64 with CPython 3.12.15. The focused ledger suite passed 19 tests, and the regression set passed 127 tests.
+Ruff check and format, mypy, `git diff --check`, and the frozen package checker passed with both execution flags false.
+An offline wheel build and package-manager install into a fresh isolated target reported `0.27.2`.
+No production behavior changed. The acceptance test changed, and the frozen Phase 3A package is unchanged.
+No Linux test, guest action, native turn, evaluation row, or paid host action ran.
+The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
+The cumulative conservative charge remains 10,125,027,074 bytes.
+All 192 development rows remain planned. All 576 sealed rows remain unexposed.
+Phase 3B acceptance remains open under ADR 0009.
+The next unmet local source condition is the measurement-record authority guard test (withdrawn commit `4465faf`, reverted by `18b7a35`).
+Earlier dated entries remain historical records.
+
diff --git a/pyproject.toml b/pyproject.toml
index fa94c8c..0adf7cf 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7 +7 @@ name = "crewshal"
-version = "0.27.1"
+version = "0.27.2"
diff --git a/src/crewshal/__init__.py b/src/crewshal/__init__.py
index 806f9c5..63ebfe5 100644
--- a/src/crewshal/__init__.py
+++ b/src/crewshal/__init__.py
@@ -3 +3 @@
-__version__ = "0.27.1"
+__version__ = "0.27.2"
diff --git a/tests/acceptance/test_phase3b_development_ledger.py b/tests/acceptance/test_phase3b_development_ledger.py
index 1e41488..cbde098 100644
--- a/tests/acceptance/test_phase3b_development_ledger.py
+++ b/tests/acceptance/test_phase3b_development_ledger.py
@@ -3,0 +4 @@ import copy
+import errno
@@ -485,0 +487,24 @@ class Phase3BDevelopmentLedger(unittest.TestCase):
+    def test_read_ledger_refuses_invalid_input_files(self):
+        with tempfile.TemporaryDirectory() as temporary:
+            base = Path(temporary)
+            regular = base / "ledger.json"
+            regular.write_text(json.dumps(self.planned))
+            self.assertEqual(ledger.read_ledger(regular), self.planned)
+            link = base / "linked.json"
+            link.symlink_to(regular)
+            with self.assertRaises(OSError) as captured:
+                ledger.read_ledger(link)
+            self.assertEqual(captured.exception.errno, errno.ELOOP)
+            directory = base / "directory.json"
+            directory.mkdir()
+            with self.assertRaisesRegex(ERROR, "regular file"):
+                ledger.read_ledger(directory)
+            empty = base / "empty.json"
+            empty.write_bytes(b"")
+            with self.assertRaisesRegex(ERROR, "size bound"):
+                ledger.read_ledger(empty)
+            oversize = base / "oversize.json"
+            oversize.write_bytes(b"0" * (2 * 1024 * 1024 + 1))
+            with self.assertRaisesRegex(ERROR, "size bound"):
+                ledger.read_ledger(oversize)
+
```

## Tests and results (macOS 27.2 arm64, CPython 3.12.15 in `.venv`)

Commands ran from `/Volumes/X10Pro/Crewshal` through RTK. The installed-wheel import ran from `/tmp`.
Python tests and the frozen checker used `env -u PYTHONPATH` to prevent a repository import from masking an install.

| Check | Result |
| --- | --- |
| `python -m unittest tests.acceptance.test_phase3b_development_ledger` | Ran 19 tests, OK, exit 0 (was 18 before) |
| Focused regression set (`test_phase3b_development_ledger`, `test_phase_3a_freeze`, `test_phase_3a`, `test_phase_2e`, `test_phase_2d_dispatch`) | Ran 127 tests, OK, exit 0 (was 126 before) |
| `.venv/bin/ruff check` on both touched Python files | clean, exit 0 |
| `.venv/bin/ruff format --check` on both touched Python files | clean, exit 0 |
| `.venv/bin/mypy src/crewshal` | clean, exit 0 (scripts/ and tests/ are outside the pinned mypy target) |
| `python scripts/check_phase_3a_freeze.py` | `consistent-frozen-source-package`, 23 artifacts, 768 planned units, both execution flags false, content sha256 `4bd188deb0…dc892c0` unchanged; ran once before and once after the version bump, exit 0 both times |
| `git diff --check` | clean, exit 0 (twice) |
| Offline wheel build: `uv build --wheel --offline --out-dir /tmp/crewshal-q3-review.4dRbJ0` | built `crewshal-0.27.2-py3-none-any.whl`, exit 0 |
| Fresh offline install: `uv pip install --offline --no-deps --target /tmp/crewshal-q3-review.4dRbJ0/installed-final /tmp/crewshal-q3-review.4dRbJ0/crewshal-0.27.2-py3-none-any.whl` | installed `crewshal==0.27.2`, exit 0 |
| Installed import from `/tmp`: `PYTHONPATH=/tmp/crewshal-q3-review.4dRbJ0/installed-final /Volumes/X10Pro/Crewshal/.venv/bin/python -c 'import crewshal, importlib.metadata; print(crewshal.__file__); print(crewshal.__version__); print(importlib.metadata.version("crewshal"))'` | module path inside fresh target; package and metadata versions `0.27.2`; exit 0 |

Tool substitution note: `.venv` has no `pip`, and the `build` package is not installed. Hermes first extracted a wheel and checked its contents. Extraction did not establish an install. Codex used `uv` for a fresh package-manager install and verified its import outside the repository.

## Deferred checks (not run; recorded as deferred, not passing)

- Linux-specific acceptance modules and Phase 2C/2D platform qualification: deferred per ADR 0009 and the owner's October 18 instruction.
- The full repository test suite beyond the focused regression set was not run this session; the five-module regression set above is the designated start-prompt set.
- B1 conformance, live runtime qualification, Phase 3B calibration: remain closed until their gates pass.

## Risks, unknowns, and costs

- Risk: `ELOOP` depends on POSIX symlink semantics; the test is macOS/Linux-appropriate and matches how `read_ledger` refuses symlinks via `O_NOFOLLOW`-class behavior observed in prior sessions. Windows behavior is not claimed.
- Unknown: whether any reviewer treats the withdrawn `a2e26ba` APPROVE claim as evidence. This packet asserts nothing about it beyond "unverified".
- Cost exposure: zero money, zero subscription quota, zero paid-host spending. No evaluation row was executed. All 192 development rows remain planned; all 576 sealed rows remain unexposed.
- The frozen Phase 3A package and private sealed-task custody are unchanged and unexposed.

## Codex review and publication boundary

Codex reviewed the complete candidate diff and found no source-code defect. The new test exercises the existing guard and a valid regular file.
Codex corrected two material evidence errors: extraction was labeled an install, and the handoff said no source file changed.
Codex also removed an unsupported build-isolation claim and recorded the command boundaries accurately.
The 127-test regression set, Ruff, mypy, frozen checker, and a fresh offline installed-wheel check passed during Codex review.
Hermes made no commit or push. The delivery revision is the checkpoint commit containing this packet.
Codex must verify the branch push at session closure.

## Next-session prompt (after this checkpoint is published)

"Start a fresh Crewshal development session in /Volumes/X10Pro/Crewshal. Read AGENTS.md, docs/HANDOFF.md, and docs/DEVELOPMENT-PLAN.md in that order. Verify a clean published HEAD and v0.27.2. If review remains pending or the tree is dirty, stop. Work on the next unmet Phase 3B local source condition: measurement records must not grant execution authority. Inspect the current guard and test before editing; do not copy withdrawn commit 4465faf without review. State acceptance behavior and one refusal case. Run offline macOS checks only. Label wheel build, extraction, and installation accurately. Prepare an exact Codex review packet and stop before commit or push."
