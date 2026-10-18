# Phase 3B admission proposal verification

Date: 2026-10-18. Entry revision: `9deb7d476615c4f3016acedd0e0c0160ffab08b6`.
Branch: `codex/phase1-architecture`. Entry worktree: clean.
Environment: macOS 27.2 arm64, CPython 3.12.15, RTK 0.51.0.
All commands ran in `/Volumes/X10Pro/Crewshal`.

## Exact read-only commands and results

```sh
rtk proxy git status --short --branch
rtk proxy git rev-parse HEAD
rtk proxy .venv/bin/python -c 'import json,hashlib,pathlib; root=pathlib.Path.cwd(); index=json.loads((root/"docs/PHASE-3B-INPUTS-2026-10-18.json").read_text()); mismatches=[]; checked=0;
for item in index["files"]:
 path=root/item["path"]; data=path.read_bytes(); checked+=1
 if len(data)!=item["bytes"] or hashlib.sha256(data).hexdigest()!=item["sha256"]: mismatches.append(item["path"])
print({"checked":checked,"mismatches":mismatches,"package":index.get("frozen_package"),"keys":list(index)})'
rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_3a_freeze tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch
rtk proxy .venv/bin/python -c 'import json,pathlib,collections; x=json.loads(pathlib.Path("docs/evaluation/phase-3a-frozen/schedule.json").read_text()); print(dict(collections.Counter(r["split"] for r in x["rows"])))'
rtk proxy .venv/bin/python -c 'import crewshal,platform,sys; print({"version":crewshal.__version__,"python":sys.version.split()[0],"platform":platform.platform(),"machine":platform.machine()})'
rtk proxy rtk --version
rtk proxy git diff --check
```

The input index checked 120 files with no mismatch before this session changed publication files.
The package checker reported 23 artifacts, 768 planned units, and closed execution gates.
The focused suite passed 108 tests. The schedule contains 192 development and 576 sealed rows.
The synchronized package version is 0.15.3 after the documentation checkpoint.
The final package checker, focused suite, and `git diff --check` returned exit code 0 after the edits.

The graph project was `Volumes-X10Pro-Crewshal`, with generation `2026-10-18T10:10:50Z`.
The checker and focused test paths had no recorded coverage gap. This signal does not prove complete indexing.
No graph claim was used to replace direct package or source verification.

## Operational result and limits

The current approved evaluation allowance remains USD 0, zero subscription quota, and zero paid-host spending.
This session made zero evaluation provider requests, coding-runtime turns, credential accesses, dependency preparations, and VM operations.
This count covers evaluation operations in this session. It does not measure the agent session's own model or subscription use.
No evaluation operation could add a new bill in this session. Billing records were not accessed, so measured billing remains unknown.
API-equivalent evaluation cost is not measured.
Subscription quota debit for this chat is unknown. No price estimate converts it to billed money.
Platform, runtime, baseline, dependency, and B1 script qualification remain unavailable.
The admission proposal is the only Phase 3B deliverable. Calibration acceptance did not run.
