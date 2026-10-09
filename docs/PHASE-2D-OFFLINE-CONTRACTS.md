# Phase 2D offline runtime and deterministic capture contracts

Date: 2026-10-08. Status: safe offline work implemented; **Phase 2D remains incomplete**. Base revision `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`; working changes are unpublished. Package metadata remains 0.9.0. No live runtime, guest test, provider/model request, credential-store operation or Phase 2E/evaluation ran.

## Implemented seam

[Runtime source](../src/crewshal/runtime.py) builds an inert neutral Codex task request and normalizes one bounded recorded native JSONL turn. It targets the pinned `codex-rust-v0.160.1` vocabulary exercised in 2C: thread/turn lifecycle, command execution, assistant/reasoning text, usage and errors. It does not implement a model/tool loop, gateway, subprocess launcher or qualification-harness wrapper. The existing native runtime continues to own tools and sessions in any future authorized run.

Request preparation revalidates the trusted task/attempt binding, exact runtime/configuration and complete qualification identity. Linux aarch64 is the only candidate runtime target. A changed profile, architecture, platform, version or missing qualification case refuses preparation. Successful preparation still returns `execution_allowed=false`. Parsing qualification records cannot establish their authenticity or owner execution authority.

Terminal normalization requires separately supplied trusted provider/model/configuration identities and process observations: timezone-aware capture times, monotonic elapsed duration, actual exit/termination, both complete streams and an independently stopped tree. Native events receive coordinator attempt/sequence identities. Missing thread/final result, unfinished items, duplicate/reordered lifecycle, conflicting command identity, unknown fields/types, malformed/duplicate-member/nonfinite JSON, partial lines, noninteger usage and stream/event overflows refuse. Runtime process success and a complete native terminal result must agree. Cancellation, timeout, quota, refusal, signal and interruption cannot become completion. Limits remain five seconds and 65536 bytes per stream; at most 1024 events are parsed. Reported usage is cumulative runtime data, not measured billing; missing counters/cost remain unknown.

Command output, native command exits and assistant text become `Claim` records only. Even text saying `execution_allowed=true` or “all tests passed” creates no check evidence. Native error items, including startup warnings represented as error items, conservatively block completion. This policy does not reinterpret the successful 2C qualification record as a failed qualification; qualification and runtime task completion are separate. Unsupported native item variants refuse rather than silently extending the vocabulary. No live conformance of this new consumer is claimed.

## Candidate and validator seam

[Candidate source](../src/crewshal/candidate.py) copies only explicit coordinator-selected source files into a new disposable directory. Selection includes explicitly approved dirty bytes, excludes `.git`, and refuses traversal, path/case aliases, symlinks, hardlinks, special files, special permission bits, existing targets and source/target overlap. Original checkout bytes and Git metadata are never modified. Copies preserve selected file content, executable modes and relative directory modes. File data is bounded to 16777216 bytes and inventory to 2000 entries.

After an independent tree-stop observation, freezing copies the disposable candidate into a separate coordinator-owned directory and checks both copies against a closed manifest. The manifest binds paths, kinds, file sizes, modes and SHA-256 content, including empty directories. Read-atime changes do not invalidate unchanged content; observed size/mode/mtime/ctime/link changes during capture do. Frozen copies are logically immutable through their digest and later integrity checks. These directories are **not** kernel-enforced readonly mounts or sandboxes. File-data bounds do not prove original live logical/allocated/deleted-open storage ceilings; those remain properties of the qualified live substrate. Stable directories and a trusted coordinator/host are assumed; directory replacement races and hostile same-user processes are outside this offline claim.

Validator capture accepts only coordinator-observed command definitions and observations. It requires exact approved argv/cwd/environment/toolchain, current frozen manifest digest, unmodified validator copy, independently stopped validator, complete bounded stdout/stderr and separate credential-free, denied-network authority. These authority observations must come from the eventual trusted supervisor, never worker stdout. Nonzero exit, timeout/cancellation/quota/signal/interruption and refusal produce failed/terminated/unavailable evidence. Missing exit/capture, altered candidate or wrong authority/definition refuses evidence. No command executes in this module.

Scope capture compares initial and frozen coordinator manifests. Added/deleted/content/mode/directory changes outside exact approved paths fail scope; a worker-authored diff is not an input. Existing private SQLite capture rechecks actual supplied log bytes and stored artifacts before persisting a verdict. No database schema, existing qualification/gate contract or public CLI was changed. The CLI still exposes only passive initialization, inspection and validation.

## Fresh acceptance evidence

[26 Phase 2D tests](../tests/acceptance/test_phase_2d.py) create their own synthetic streams, repositories, original dirty/Git bytes, candidate copies, manifests, identities, qualifications, private databases and capture artifacts. They require no old observation file, provider, VM, SSH or qualification fixture. One offline integration exercises intent/acknowledgement/terminal persistence, claims without evidence, forged capture rejection, validator/scope capture, mutated durable artifact refusal and a synthetic verified verdict that still has false execution permission.

Environment: macOS 27.2 (`26B5101f`) arm64, CPython 3.12.15, Pydantic 2.12.5, uv 0.9.24, Ruff 0.14.1, mypy 1.18.2, hash-locked development dependencies. This is macOS **offline source/package verification**, not macOS runtime compatibility evidence. Linux/Windows runtime behavior of the new code remains unobserved.

Reproduce from the documented development environment:

```sh
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' "$PWD/.venv/bin/python" -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/mypy
```

Final acceptance counts and installed-wheel evidence are recorded in [the handoff](HANDOFF.md). For fresh package verification, use a new external directory; the draft build retains version 0.9.0 because publication is gated:

```sh
crewshal_verify_dir=$(rtk proxy mktemp -d /private/tmp/crewshal-2d-verify.XXXXXX)
rtk proxy mkdir "$crewshal_verify_dir/home"
rtk proxy uv build --offline --out-dir "$crewshal_verify_dir/dist"
rtk proxy uv venv --python python3.12 "$crewshal_verify_dir/fresh"
rtk proxy uv pip install --python "$crewshal_verify_dir/fresh/bin/python" --offline --require-hashes -r requirements-dev.lock
rtk proxy uv pip install --python "$crewshal_verify_dir/fresh/bin/python" --offline --no-deps "$crewshal_verify_dir/dist/crewshal-0.9.0-py3-none-any.whl"
rtk proxy env -i PATH=/usr/bin:/bin HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' "$crewshal_verify_dir/fresh/bin/python" -m unittest discover -s tests -t .
rtk proxy "$crewshal_verify_dir/fresh/bin/python" -c 'import crewshal, crewshal.runtime, crewshal.candidate; print(crewshal.__file__); print(crewshal.runtime.__file__)'
rtk proxy "$crewshal_verify_dir/fresh/bin/crewshal" --help
```

Offline cache preparation is documented in [DEVELOPMENT.md](DEVELOPMENT.md); an empty cache cannot satisfy disconnected installation. Build artifacts stay outside the checkout and are neither published nor qualified live inputs.

Initial test execution failed with the expected missing `crewshal.runtime` module before implementation. Development also exposed a case-insensitive-filesystem test assumption and incorrect use of the existing store context/transition contract; fixtures were corrected. All failures were local/offline. No failed live run is hidden by these corrections.

## Continuity and remaining boundary

The session loaded 359 local files linked by the 2C active/published continuation and the exact 2D input prompt, totaling 17859892 bytes, as data. The initial working tree was clean. All 749 original tracked files were fingerprinted before changes; only maintained continuity/status documents are intentionally updated. [Input and source continuity](qualification/phase-2d-offline-continuity-20261008.json) records the bound inputs, base revision and new source hashes. Every original source/profile/binding/freeze/observation/protocol remains byte-identical, including failed variants and v5 unknowns.

Codebase-memory Verify selected project `Volumes-X10Pro-Crewshal`, initial generation `2026-10-08T09:40:18Z`. Relevant original files had matching coverage metadata; scope exclusions covered generated bytecode only. One graph call misresolved `digest` to a JSON-embedded source; exact source was used instead. The updated graph generation was `2026-10-08T12:55:33Z`; new candidate/test paths matched, while the subsequently edited runtime path required direct source fallback. Final generation `2026-10-08T13:03:36Z` reports matching metadata/no recorded gap for all three new source/test paths. No exhaustive graph claim is made. RTK wraps shell commands. Caveman controls chat style only. Jev was read but no paid Jev/provider/model call was requested.

The production dispatch/supervision/authority integration is still unimplemented and unqualified. The 2C fixture driver is not a production launcher. Its removed roles/helpers/slice and disconnected SSH cannot be assumed present. Runtime/provider/model/destination or source/configuration changes require a fresh exact qualification; v18 eligibility cannot transfer. The independently approved live task run, actual credential-free check and false-completion/mutation refusals remain **not run**. See [the concrete preparation and missing gates](PHASE-2D-EXECUTION-GATE.md) and [next-session prompt](PHASE-2D-CONTINUATION-2026-10-08.md). No version bump, commit or push occurs before the complete 2D gate. Do not begin 2E.
