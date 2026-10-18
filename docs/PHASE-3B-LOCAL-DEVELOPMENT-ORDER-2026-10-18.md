# Local development order before consolidated Linux tests

Date: 2026-10-18. Entry revision: `7dca8e8b134d5304ff6fa2c8952257dce7903cc3`.
Branch: `codex/phase1-architecture`. Entry worktree: clean. Entry version: `0.15.10`.
Milestone: record the owner's development order and replace the active next-session prompt.

## Owner instruction and result

The owner stopped Linux tests during development.
The owner directed development to use the local machine as its main ground.
The owner placed Linux checks after all planned source steps pass local verification.
[ADR 0009](decisions/0009-local-development-before-consolidated-linux-testing.md) records this accepted order.
The active [next-session prompt](PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-18.md) now directs local macOS source development.
It excludes Linux-specific test modules and requires their deferred status in local acceptance records.
The earlier Linux toolchain prompt remains a dated record and is no longer the active continuation.

The current Ubuntu guest, previous guest, ISO, artifact manifest, transfer ledger, and unknown installer count remain unchanged.
The proposed RAM, infrastructure, retained-data, and transfer amendments remain unapproved and parked.
Do not request those amendments during local source development.
The original Phase 3B spending approval remains a dated record.
It does not reopen Linux work during this development period.

Phase 2D and Phase 2E software remain complete with deferred platform qualification.
The Phase 3A source package remains frozen.
No Linux conformance, provider identity, native baseline, or calibration result follows from this order change.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Phase 3B calibration and Phase 3C remain closed.

## Verification, costs, and limits

This checkpoint changes policy documents, the active prompt, and synchronized version metadata.
It runs no Linux test, VMware operation, artifact retrieval, provider request, or coding-runtime turn.
No paid host or Jev call ran. No new evaluation billing observation exists.
Subscription quota debit for this chat remains unknown.

The host reported Darwin 27.2.0 arm64, Python 3.12.15, and RTK 0.51.0.
The starting branch matched `origin/codex/phase1-architecture` and had no worktree changes.
The frozen package checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The new continuation index records exact public file bytes and SHA-256 digests.
The two package version fields report `0.15.11`.

Commands and results for this local checkpoint:

| Command | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | Entry branch matched its remote; the entry worktree was clean. |
| `rtk proxy git rev-parse HEAD` | Entry revision was `7dca8e8b134d5304ff6fa2c8952257dce7903cc3`. |
| `rtk proxy uname -srm` | `Darwin 27.2.0 arm64`. |
| `rtk proxy .venv/bin/python --version` | `Python 3.12.15`. |
| `rtk proxy rtk --version` | `rtk 0.51.0`. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts, 768 planned units, stated digest, and no execution. |
| `rtk proxy .venv/bin/python -c 'import crewshal; print(crewshal.__version__)'` | `0.15.11`. |
| `rtk proxy git diff --check` | Passed. |

The file-index verification checked 146 public paths, lengths, and SHA-256 digests; all matched.
It used this local command:

```sh
rtk proxy .venv/bin/python - <<'PY'
import hashlib
import json
from pathlib import Path
index = json.loads(Path('docs/PHASE-3B-LOCAL-DEVELOPMENT-INPUTS-2026-10-18.json').read_text())
for row in index['files']:
    data = Path(row['path']).read_bytes()
    assert len(data) == row['bytes'], row['path']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
print(f"verified {len(index['files'])} indexed files")
PY
```

The full suite was not run because this checkpoint changes documentation and version metadata only.
Linux-specific test modules remain deferred under the owner's instruction.
No Linux test failure was hidden or converted into a pass.

## Continuation

Use the [local development prompt](PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-18.md) and its [exact input index](PHASE-3B-LOCAL-DEVELOPMENT-INPUTS-2026-10-18.json).
Choose one coherent source milestone under the accepted plan.
Verify it on the local Mac with deterministic checks.
Prepare one consolidated Linux campaign only after all planned source development passes local acceptance.
