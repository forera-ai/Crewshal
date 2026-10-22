# Codex review packet — Phase 3B read-ledger input-file protection tests — 2026-10-22

## Milestone

Name: Phase 3B read-ledger input-file protection test coverage.

Scope: `tests/acceptance/test_phase3b_development_ledger.py` only. No source file changed.

Requirement: `read_ledger` is the parsing entry point for every ledger, inventory, and
measurement check. No prior test exercised its input-file protections. This milestone
adds one focused acceptance test that proves those protections.

## Base state

- Base revision: `049cffd18c520f7f8460ec0889ff19ef579b3156`
- Branch: `codex/phase1-architecture`
- Base version: `0.27.1` (`pyproject.toml` and `src/crewshal/__init__.py` synchronized)
- Git status before change: clean

## Changed files

- `tests/acceptance/test_phase3b_development_ledger.py` — 25 insertions, 0 deletions
  (one import and one test; the Codex finding on `ELOOP` is applied).

Exact diff:

```diff
diff --git a/tests/acceptance/test_phase3b_development_ledger.py b/tests/acceptance/test_phase3b_development_ledger.py
--- a/tests/acceptance/test_phase3b_development_ledger.py
+++ b/tests/acceptance/test_phase3b_development_ledger.py
@@ -1,6 +1,7 @@
 """Local checks for Phase 3B development coverage, with no task execution."""

 import copy
+import errno
 import hashlib
 import json
 from pathlib import Path
@@ -483,6 +484,30 @@ class Phase3BDevelopmentLedger(unittest.TestCase):
         with self.assertRaisesRegex(ERROR, "source refs invalid"):
             ledger.check_measurements(candidate, self._measurement_bundle(candidate, [record]))

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
     @staticmethod
     def _source(name, field):
         return [{"file": name, "path": field.split(".")}]
```

No other file changed. No source file changed. The frozen Phase 3A package is unchanged.

## Acceptance mapping

| Test case | Requirement | Result |
| --- | --- | --- |
| Regular ledger file | `read_ledger` parses a full valid ledger and returns the decoded object unchanged | pass |
| Symlinked ledger path | `O_NOFOLLOW` refuses symlink traversal at `os.open` | pass (`OSError`, `errno.ELOOP`) |
| Directory path | `S_ISREG` refuses non-regular files | pass (`"ledger must be a regular file"`) |
| Empty file | size bound refuses zero-length input | pass (`"ledger exceeds size bound"`) |
| Oversize file (2 MiB + 1) | size bound refuses input above 2 MiB | pass (`"ledger exceeds size bound"`) |

## Commands and results

Environment: macOS Darwin 27.2.0 arm64, CPython 3.12.15, project `.venv`, base revision `049cffd`.

| Command | Result |
| --- | --- |
| `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase3b_development_ledger -v` | 19 tests passed (18 previous + 1 new), exit 0. |
| `rtk proxy .venv/bin/ruff check tests/acceptance/test_phase3b_development_ledger.py` | All checks passed, exit 0. |
| `rtk proxy .venv/bin/ruff format --check tests/acceptance/test_phase3b_development_ledger.py` | 1 file already formatted, exit 0. |
| `rtk proxy .venv/bin/mypy src/crewshal` | No issues in 48 source files, exit 0. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | 23 artifacts and 768 planned units consistent; `content_sha256` unchanged; both execution flags false. |

## Refusal cases

- Symlinked ledger path: refused with `OSError` from `O_NOFOLLOW`.
- Directory path: refused with `FreezeError` message `ledger must be a regular file`.
- Empty file: refused with `FreezeError` message `ledger exceeds size bound`.
- Oversize file: refused with `FreezeError` message `ledger exceeds size bound`.

## Deferred checks and limits

- No Linux-specific test module ran. Linux qualification and native conformance remain deferred per ADR 0009.
- No guest action, archived tool execution, native turn, or evaluation row ran.
- No new network transfer occurred. Paid host and metered API costs were zero.
- The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes. The cumulative conservative charge remains 10,125,027,074 bytes.
- All 192 development rows remain planned. All 576 sealed rows remain unexposed.
- Executable hashes, effective commands, providers, and B1 conformance remain unknown until observed.
- A passing local test does not prove event origin. Every result stays unverified until admitted run evidence can establish its source.

## Risks and unknowns

- Resolved: the symlink refusal raises `OSError` from `O_NOFOLLOW` at `os.open`.
  Codex review (2026-10-22, verdict APPROVE) confirmed the behavior and suggested
  asserting the error code. The test now asserts `errno.ELOOP` for the symlink case
  and passes with the full suite (19 tests).
- No other unknowns were observed.

## Publication boundary

Codex reviewed this packet on 2026-10-22. The review matched the diff to the packet,
confirmed coverage of all five refusal cases, and returned verdict APPROVE with one
low nonblocking finding (assert `ELOOP`). That finding is applied. Publication steps
(version bump to `0.27.2`, README, CHANGELOG, handoff updates, commit, and push)
proceed under standing owner authorization.
