# Phase 2C portable record audit

The owner stopped VMware/Linux tests earlier on October 8, 2026, then explicitly authorized “Reconnect and resume 2C checks” on the existing local VMware Ubuntu installation. The resumed v18 profile passes its separate complete runtime qualification gate; see [the assessment](PHASE-2C-COMPLETION-ASSESSMENT.md). The offline stop prompts remain historical inputs.

This portable audit checks record consistency; every result keeps `runtime_verified=false` and `execution_allowed=false`. Hashes establish byte continuity. They do not authenticate observations, attest host controls or independently qualify a runtime. Platform identity strings are data; accepting a Linux or Windows identity is not a platform test. No launcher, provider call or executable qualification seam is added. Complete v18 runtime evidence is checked separately by its prebound independent reader; the audit's protocol-manifest identity convention is not substituted for v18's actual runtime manifest.

## Usage

With the existing editable development installation:

```sh
rtk proxy .venv/bin/python scripts/audit_phase_2c_bundle.py /path/to/bundle
```

Exit zero means `consistent_records`; exit two means `denied`. The script reads files and prints JSON. It never launches declared sources or writes to the bundle. Use a stable directory supplied by a trusted coordinator. The reader rejects observed symlinks and checks identity during each read, but it is not an atomic directory snapshot or a confinement boundary against concurrent parent-directory replacement. Do not use it to inspect an actively attacker-controlled filesystem.

## Bundle schema

The directory contains `bundle.json` with exactly the following fields:

```json
{
  "schema_version": 1,
  "protocol": {"path": "protocol.json", "sha256": "<64 lowercase hexadecimal characters>"},
  "profile": {"path": "profile.json", "sha256": "<64 lowercase hexadecimal characters>"},
  "current_identity": "<QualificationIdentity object supplied by a trusted coordinator>",
  "runs": [
    {"path": "run-1.json", "sha256": "<64 lowercase hexadecimal characters>"},
    {"path": "run-2.json", "sha256": "<64 lowercase hexadecimal characters>"}
  ],
  "artifacts": [
    {"path": "scripts/source.py", "sha256": "<64 lowercase hexadecimal characters>"}
  ],
  "execution_allowed": false
}
```

This is a schema illustration with placeholders, not an executable passing fixture. `current_identity` uses the unchanged [QualificationIdentity contract](../src/crewshal/qualification.py). Each run uses the unchanged Qualification contract: schema version, distinct ID, the exact current identity, all twenty distinct mandatory results with status `passed` and nonempty observations, and explicit false execution permission. Missing runtime/image/substrate/credential-design identity refuses under the existing assessor.

`protocol.json` must be the exact [original protocol](qualification/phase-2c-v1.json), SHA-256 `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. The profile preserves `original_protocol_sha256`, `original_grant`, `original_limits`, ordered `mandatory_cases`, and both false execution/native-start flags. Current identity configuration equals profile SHA-256; manifest equals original protocol SHA-256. Other identity facts remain assertions supplied by the trusted caller.

The profile binds `source`, `fixture_source`, `payload_source` and their `_sha256` fields; `policy` and `policy_sha256`; and `additional_sources`, an object mapping paths to digests. Policy paths are relative to the profile directory. Other source paths are relative to the bundle root. Every required source must appear in `artifacts` with the exact same digest. Additional artifact entries are also checked. Historical diagnostic observations require a trusted conversion into the Qualification contract; this utility does not infer or manufacture results from raw logs.

Artifact names are normalized relative ASCII paths. Absolute paths, traversal, symlinks, Windows device names, trailing dots/spaces and case aliases refuse. Case checks cover directory prefixes as well as whole file names; `Sources/first.txt` and `sources/second.txt` cannot share a bundle. Policy names must satisfy the same path contract before resolution relative to the profile, so `./policy.txt`, repeated slashes and trailing slash/dot aliases refuse. Consistently named shared directories and nested profile/policy directories remain supported.

At most 128 source artifacts, one MiB per file and eight MiB total are accepted. Duplicate JSON members, NaN/Infinity, exponents outside finite float range, conflicting/missing/null bindings, numeric/boolean substitutions in the original contract, duplicate run IDs/bytes and changed inputs refuse. Literal strings containing `NaN` or `Infinity` remain ordinary data. Each run passes the original assessor independently. Complementary subsets cannot combine into success.

## Local verification

Fresh fixtures exercise consistent records without execution; all twenty omission/failure/unavailability variants; profile/identity mutations; conflicting/null sources; forged flags/schema; duplicate runs/JSON; path, byte and symlink refusal; unchanged file bytes; and declared source code that never executes. Additional regressions cover policy aliases, directory case aliases, nested profile/policy success, nonfinite JSON and exponent overflow. Source: [qualification_bundle.py](../src/crewshal/qualification_bundle.py); entry point: [audit_phase_2c_bundle.py](../scripts/audit_phase_2c_bundle.py); fixtures: [test_phase_2c_bundle.py](../tests/acceptance/test_phase_2c_bundle.py).

On macOS 27.2 arm64, CPython 3.12.15:

```sh
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/mypy
```

Latest full suite: **141 tests passed in 5.252 seconds**, including 26 bundle methods and fresh independent readback/controller/capture/native-continuation regressions. The preceding 114/119-test results remain in the handoff ledger. Lint and strict typing pass. Only the separate complete Linux profile satisfies Phase 2C; these offline fixtures never grant runtime qualification or execution permission. Windows and macOS runtime compatibility remain unknown.
