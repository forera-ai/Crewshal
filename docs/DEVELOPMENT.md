# Offline development and project initialization

Phases 2A and 2B deliver passive discovery, human decisions, durable SQLite coordinator state and deterministic trusted-evidence contracts. There is no runtime launcher, check executor or execution grant. Confirmation records describe a project; they cannot authorize agent writes or command execution. See [state, migration and gates](STATE-AND-GATES.md).

## Reproducible setup

Use Python 3.12 or newer and uv. The recorded qualification environment is macOS arm64 with Python 3.12.14; other operating systems and Python versions are not yet verified. The package currently uses POSIX no-follow file opens and user/mode checks. Do not infer Windows support from the wheel's packaging tag.

From a fresh checkout:

```sh
rtk proxy uv venv --python python3.12 .venv
rtk proxy uv pip install --python .venv/bin/python --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python .venv/bin/python --no-deps -e .
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b
rtk proxy .venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests
rtk proxy .venv/bin/ruff format --check src tests
rtk proxy .venv/bin/mypy
rtk proxy uv build --offline
```

Dependency preparation may use the package index; tests need no network, provider credentials or earlier artifacts. The hash-locked file pins all development/runtime dependencies; the isolated build backend is separately pinned in pyproject.toml. `uv build --offline` needs its pinned build dependency already cached, as with the preceding editable installation. To prepare another machine for disconnected installation, first obtain its required wheels and build dependency. An empty cache is not an offline install source.

For artifact verification, create a second external environment, install requirements-dev.lock with `--offline --require-hashes`, then install `dist/crewshal-0.2.0-py3-none-any.whl` with `--offline --no-deps`. Run both acceptance modules and the complete unittest suite with that interpreter from the checkout. Tests live in the checkout; application imports must resolve to the external environment's site-packages, not src. Tests create all repository/state/interaction/database/artifact fixtures themselves.

On the verified macOS host, tests additionally passed under the following process-level network denial with an empty inherited environment and a temporary HOME. This test wrapper does not qualify a future worker execution environment:

```sh
# Substitute fresh environment and temporary home paths; create the home first.
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2a
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2b
rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" \
  HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$crewshal_verify_dir/fresh/bin/python" -m unittest discover -s tests -t .
```

## Initialization

```sh
rtk proxy .venv/bin/crewshal --help
rtk proxy .venv/bin/crewshal init /path/to/repository --state-dir /private/coordinator-state
rtk proxy .venv/bin/crewshal init /path/to/repository --state-dir /private/coordinator-state --interactive
rtk proxy .venv/bin/crewshal show /path/to/repository --state-dir /private/coordinator-state
```

Default initialization proposes facts and stores them as pending. It never prompts or confirms implicitly. `--interactive` explicitly reads `confirm`, `reject`, `correct <literal value>` or `skip` for pending facts, then separately asks for confirmation after correction. Blank answers skip. Unknown values require correction before confirmation. EOF or invalid answers refuse materialization. Prompts go to stderr, the validated JSON model to stdout. No command candidate is executed, including after confirmation.

Alternatively replay an explicit, operator-selected decision file with `--decisions FILE`. First obtain the current model digest with `crewshal show REPOSITORY --state-dir STATE --digest`. The decision file uses this format:

```json
{
  "schema_version": 1,
  "model_digest": "replace with the 64-character digest returned by show --digest",
  "decisions": [
    {"fact_id": "package.json:check:test", "action": "correct", "value": "vitest run", "reason": "Human correction"},
    {"fact_id": "package.json:check:test", "action": "confirm", "reason": "Human confirmation"}
  ]
}
```

Stale batches, unknown IDs, unsupported versions and malformed records are refused. This is explicit local operator input, not cryptographic authentication or a worker approval channel. Exported models cannot be imported as approvals. `show` displays stored state without refreshing it; rerun `init` to rediscover and invalidate changed dependencies. `validate FILE` checks the closed model contract, not authority or truth.

State defaults to `$XDG_STATE_HOME/crewshal` or `~/.local/state/crewshal`. It must resolve outside the discovered repository, belong to the coordinator user and have mode 0700. The SQLite database and capture files use mode 0600; symlink state directories/records are rejected. Writes atomically compare the loaded version and append an ordered event. Conflicting writers must reload and reconsider their decisions. Existing external JSON state requires explicit `init --migrate-state` or `show --migrate-state`; the original remains unchanged as a backup. Unsupported database versions are refused. See [the durable-state guide](STATE-AND-GATES.md) for supported database migration and inert crash reconciliation. A trusted local host/user is assumed; this does not defend against same-user malicious processes.

Initialization does not modify the discovered repository. `--export RELATIVE_FILE` explicitly creates a new model file there; parents must exist, path escapes/symlinks and existing files are refused. Exports contain relative source paths and no coordinator state path or repository root metadata. Literal repository values and human corrections remain visible; inspect them before sharing. Exported files are informational copies and never replace external state. An export and a state write are separate operations; an export may remain if state saving subsequently fails.

## Supported discovery and limits

- `pyproject.toml`: Python stack, `[project].name`, manifest directory; literal `[tool.hatch.envs.default.scripts]` string values become command candidates. Pytest configuration is a strong tool inference, not a synthesized executable command or proof of installation. Python entry-point declarations are not test commands.
- `package.json`: JavaScript/TypeScript family, name, manifest directory and literal script values. A TypeScript devDependency is a strong tool inference. All scripts are proposed candidates; the operator chooses/rejects which are checks. No package manager wrapper or implicit test command is invented.
- `workspaces` arrays and `workspaces.packages`: bounded member manifests matched using Python pathlib relative patterns. Root/member source fingerprints both bind member boundaries. Missing members and conflicting manager lockfiles remain unknown. pnpm workspace YAML, CI YAML, requirements/setup/tox files are visibly unsupported and never executed.
- `AGENTS.md` and `CLAUDE.md`: bounded input fingerprints and an untrusted-data notice only. Their instructions do not create commands or authority.
- Observed, strong inference, weak inference, unknown and human decision status are distinct. `.github` is a weak sensitive-path suggestion; data egress starts unknown. No provider/network policy is inferred from these records.
- SHA-256 source fingerprints are file-granular, with repository-relative paths and manifest-key locations. Changes to a source invalidate its dependent confirmations/corrections; unrelated files preserve them. Removed facts lose active approval and produce removal notices. Inputs are checked again before saving decisions. This is not an atomic repository snapshot or protection against adversarial concurrent filesystem mutation.
- Defaults: 2,000 directory entries, 256 KiB per supported input, 2 MiB total supported-input bytes, depth 12 and a 5-second cooperative inventory deadline. Count, size, depth, unreadable/malformed inputs, unsupported formats and exclusions are visible notices. Parsing is bounded by input sizes, not a separate hard process deadline. CLI exposes `--max-files`, `--max-file-bytes`, `--max-total-bytes` and `--max-depth`; all must be positive.
- All symlinks, special files, known private/generated/vendor trees and `.env*` paths are excluded. This is a bounded supported-format scan, not comprehensive secret detection or execution isolation. No hooks, imports from the target, dependency installation, models, containers or target scripts run during discovery.

See [the handoff](HANDOFF.md) for recorded evidence and the next milestone.
