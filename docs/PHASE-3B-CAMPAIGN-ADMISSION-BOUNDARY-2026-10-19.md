# Phase 3B campaign admission boundary

Date: 2026-10-19. Branch: `codex/phase1-architecture`.
Entry revision: `9678937b5f92cc7f9721d441fea7e86ba25a26f7`. Entry worktree: clean.
Status: blocked exact admission. Phase 3B calibration has not started.

## Result

The [campaign manifest](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records known inputs, missing bounds, and pending owner decisions.
All 149 files in the starting index matched their byte counts and SHA-256 digests.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
No frozen Phase 3A byte changed.

The manifest binds four selected source archive URLs, sizes, digests, file counts, expanded content sizes, and inventory digests.
The four archives total 2,777,282 download bytes.
The [source extractor](../scripts/phase3b_extract_source.py) binds a candidate safe extraction command to those frozen records.
It rejects links, special members, extra files, duplicate files, and unsafe paths.
It checks each extracted file and the final canonical inventory.
Local syntax, frozen inventory serialization, and three network-denied synthetic extraction tests passed.
The tests accepted an exact archive and refused a symbolic link and an extra file.
No selected archive was extracted in this session.

The [B1 manual operator script](PHASE-3B-B1-MANUAL-SCRIPT-2026-10-19.md) binds the frozen stage order and receipt fields.
Its native launch commands remain unbound. No B1 conformance or row ran.
The current Crewshal dispatch source supplies prospective Codex configuration only.
It does not supply an observed effective launch or a Claude Code launch command.
The Crewshal graph was ready at generation `2026-10-18T17:59:41Z`.
Coverage checks reported no recorded issue for `src/crewshal/dispatch.py` and `src/crewshal/claude.py`.
That signal does not prove complete source coverage or effective Linux behavior.

The fourteen-artifact toolchain candidate still lacks thirteen exact archive sizes.
It lacks safe member inventories, extraction bounds, executable hashes, license results, and dependency closure.
The four selected repositories retain their frozen constraints and lockfile digests.
No exact installed dependency set, download bound, retained-data bound, or read-only snapshot exists.
The local records cannot establish those values without additional admitted inputs.

## Limits and decision boundary

The original transfer ceiling is 8,589,934,592 bytes.
The ISO and checksum account for 3,825,518,142 known bytes.
The installer transfer remains unbounded. Charge its unknown amount against the remaining 4,764,416,450 bytes.
The conservative transfer balance is zero bytes.
The known prospective archive subtotal is 23,607,106 bytes, including CPython and four selected source archives.
Other artifact, package, signature, and metadata transfer bounds remain unknown.

The last host allocation for the VM and ISO is 9,093,566,464 bytes.
The last guest readback gave 16,728,174,592 visible memory bytes and 55,538,384,896 free bytes on `/var/tmp`.
No current readback or future growth bound was obtained.
The proposed 16 GiB visible-memory rule, 40 GiB infrastructure ceiling, retained-data interpretation, and 16 GiB transfer ceiling remain unapproved.
The manifest records each proposed decision without treating it as an allowance.
The exact batch lacks a transfer and retained-data upper bound. No changed-limit approval request is ripe.
The campaign manifest records the proposed time and process ceilings, but no Linux control readback exists.

The standing plan sets paid-host and metered API limits at USD 0.
The dated Phase 3B proposal sets 256 submissions per runtime and a USD 200 API-equivalent planning ceiling.
Its unknown service quota debit needs a current campaign decision.
Earlier batch approvals do not reopen Linux work under ADR 0009.

## Local checks and limits

Environment: Darwin 27.2.0 arm64, Python 3.12.15, RTK 0.51.0.
No guest, Linux test, Linux artifact retrieval, provider request, evaluation row, or Jev call ran.
Known paid-host, metered API, and Linux download cost for this session was USD 0 and zero bytes.
Subscription quota debit for this chat remains unknown.

| Command | Result |
| --- | --- |
| `rtk proxy git status --short --branch` | Entry branch matched `origin/codex/phase1-architecture`; worktree was clean. |
| `rtk proxy git rev-parse HEAD` | Returned the entry revision above. |
| The exact index check in the block below | All 149 starting file sizes and SHA-256 digests matched. |
| `rtk proxy .venv/bin/python scripts/check_phase_3a_freeze.py` | Passed; 23 artifacts, 768 planned units, and the stated digest. |
| `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' .venv/bin/python -m unittest tests.acceptance.test_phase3b_extract_source` | Passed three tests. |
| `rtk proxy .venv/bin/ruff check scripts/phase3b_extract_source.py tests/acceptance/test_phase3b_extract_source.py` | Passed. |
| `rtk proxy .venv/bin/ruff format --check scripts/phase3b_extract_source.py tests/acceptance/test_phase3b_extract_source.py` | Initial test-file check failed. Both files passed after formatting. |
| The exact index check in the block below | All 156 continuation file hashes matched. |
| `rtk proxy git diff --check` | Passed. |

Run this read-only check for either named input index:

```sh
rtk proxy .venv/bin/python - docs/PHASE-3B-CAMPAIGN-ADMISSION-INPUTS-2026-10-19.json <<'PY'
import hashlib
import json
from pathlib import Path
import sys

index = json.loads(Path(sys.argv[1]).read_text())
failures = []
for row in index["files"]:
    path = Path(row["path"])
    if not path.is_file():
        failures.append((row["path"], "missing"))
        continue
    data = path.read_bytes()
    if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
        failures.append((row["path"], "mismatch"))
print("files", len(index["files"]), "failures", failures)
raise SystemExit(bool(failures))
PY
```

At the entry revision, replace the index argument with `docs/PHASE-3B-SOURCE-READY-INPUTS-2026-10-18.json`.

The extractor has no real-archive result. The B1 script has no native conformance result.
The extractor may refuse a selected archive that contains a link. Such a refusal must stay blocked.
Linux-specific acceptance modules remain deferred. Earlier Linux failures were not retested.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux conformance, provider identities, native baselines, Phase 3B calibration, and Phase 3C acceptance remain unknown or closed.

Use the [next prompt](PHASE-3B-CAMPAIGN-ADMISSION-NEXT-SESSION-2026-10-19.md) and its exact input index.
