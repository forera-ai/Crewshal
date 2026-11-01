# Native binary provenance and build capability boundary

Date: 2026-11-01. Package checkpoint: `0.27.25`. Crewshal skill: `1.0.0`.
Base: `3aaf79afe9f007d8467cb6344784bb12a29c5173` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result

Read-only preparation established the cached runtime's byte identity and its split-library build layout.
It did not establish a reproducible native build or qualify the accepted association candidate for operation.
CMake is unavailable on PATH and at the seven checked installation locations.
The smallest missing capability is an installed CMake executable, version `3.18` or newer, for read-only verification.
No tool installation, download, native build, runtime application, or service action is approved by this record.

The pasted October 31 continuation predates the [accepted November 1 correction](CREWSHAL-ASSOCIATION-CORRECTION-2026-11-01.md).
The current handoff supplied the controlling [read-only preparation milestone](CREWSHAL-ASSOCIATION-OPERATIONAL-PREP-NEXT-SESSION-2026-11-01.md).
This session preserved the accepted candidate and all consumed source budgets.
The separate translator budget remains unused.

## Cached native identity

All 42 entries in `UNSLOTH_PREBUILT_INFO.json` match their recorded sizes and SHA-256 values.
The installed launcher is a `33472`-byte arm64 Mach-O executable.
Its SHA-256 is `b1f37cf8624593d07b520414181591637bac2778ed6d7919ce870291a1ac8e19`.
The server implementation library's SHA-256 is `dc37a3c0b0fefe1457d10c29349a8318c0680bfdc7338a694c40a6b31dd1627a`.
`otool -L` shows that the launcher depends on this implementation library and the llama, mtmd, and ggml libraries.

The cached metadata declares release `b11985-mix-c116c32` and source commit `6f4cc4d72556554a7c137de536e2fbd93fd7f907`.
Its source archive digest is `24e2248972bba218156875d38aaba1d39099af689b6ff598a616d6f917714624`.
Its binary archive digest is `09c4d4b17f92a55f8f3bf5cbf3b9c427a64ddf074d43a921db6dacc038d48077`.
These values are cached vendor declarations. This session did not authenticate or reconstruct either archive.
The source tree has no Git metadata, CMake cache, or generated Makefile or Ninja build graph in its `build` directory.
Its `cmake/build-info.cmake` declares build `11985` and abbreviated commit `6f4cc4d72`.
Matching declarations do not prove a source-to-binary relationship.

A fresh manifest records 3,964 regular native files outside `build` and `.git`; it excludes symlinks.
Its SHA-256 is `ec3fc42113554091512fc60499e1759180fe7f9aa72fd4dd8bdd7e9f273250b4`.
It identifies inspected local bytes, not a verified upstream revision or a complete future build-input closure.

The accepted native patch changes the slot serializer in `tools/server/server-context.cpp`.
The supported CMake target compiles that source into `server-context`, then links it into `llama-server-impl`.
Therefore, an operational binary identity must bind the implementation libraries and their resolution, alongside the launcher.
The accepted candidate's `_association_engine_identity` hashes the executable only.
A later observer must supply the additional bundle and process-lifetime evidence without claiming that launcher identity proves loaded library identity.
This session inspected no live memory mappings and changed no candidate source.

## Local build capability

Apple Clang `21.0.0` and macOS SDK `27.2` are available.
`make` is available. CMake and Ninja were absent from PATH.
The seven additional CMake checks covered the standard app, Homebrew, local, profile, Studio, and project locations.
This bounded search does not prove that no other installation exists.
The top-level CMake file requires `3.14`; the server's UI asset script requires `3.18`.
The legacy Makefile refuses builds because CMake replaced that build system.

`xcrun --sdk macosx --find metal` exited `0`.
The corresponding `metallib` lookup exited `72`; its failed output remains preserved.
The inspected `GGML_METAL_EMBED_LIBRARY=ON` branch embeds shader source through assembly.
It does not use the separate `metallib` build branch.
This source finding does not prove that a complete Metal build or runtime will pass.

The UI target permits prebuilt asset downloads by default.
A later offline build must disable `LLAMA_USE_PREBUILT_UI`, `LLAMA_BUILD_UI`, and `LLAMA_CONNECT` explicitly.
It must also disable optional BoringSSL, LibreSSL, and LLGuidance retrieval and deny network access independently.
Keep TLS and the selected Metal backend requirements explicit. Do not remove required features to bypass a missing dependency.
Installed TLS dependency availability remains unverified.

## Current process and supported controls

A fresh exact-name process scan found a `llama-server` process using the inspected cached executable path.
Its observed arguments specify Ornith `UD-Q4_K_XL`, context `93696`, and one slot.
The profile selects provider `unsloth` and the recorded Ornith model, with configured context `93696`.
The profile's run budget remains `600` seconds. Its fallback provider list remains empty.
Process arguments and configuration do not establish effective loaded context, capacity, or successful request behavior.
The earlier absence observation remains historical. This scan establishes no cause for the transition.
No authenticated HTTP observation, socket connection, model request, or worker ran.

Read-only source inspection identified Studio's existing custom-directory selection and owned process lifecycle methods.
The selector recognizes root and `build/bin` executable layouts and honors existing environment overrides.
The selected path can be stored through `set_custom_llama_cpp_path`; this changes settings and remains outside this session's authority.
`_start_llama_process`, `unload_model`, and `_kill_process` have operational effects and were not invoked.
The in-app updater can retrieve and replace bundles. It is not an offline inspection command.
No exact activation or restart command is submitted for approval at this boundary.

## Required next capability and later build scope

First obtain an absolute path to an already installed CMake executable, version `3.18` or newer.
Verify its version, digest, bundled modules, and compatibility through read-only commands.
No permission to install or retrieve CMake follows from that request.

Then prepare a separate, exact private-build proposal with these inputs and limits:

- Bind the current native source manifest and the unchanged accepted native patch.
- Copy source into a fresh private directory. Keep installed source and all accepted candidate bytes unchanged.
- Own two private build output directories for repeat-build comparison and retain their logs.
- Use the verified CMake executable, installed Apple compiler, SDK, and an explicit generator.
- Record every required library, generated input, backend option, and UI asset decision before execution.
- Propose at most two parallel build jobs, an `1800`-second total ceiling, and an `8 GiB` new-file ceiling.
- Verify enforcement and current storage capacity before asking for the build decision.
- Permit no downloads, credentials, model loads, inference, installed-file replacement, or service actions.
- Retain failed outputs. Cleanup must affect only newly owned scratch after evidence capture.

These proposed build limits are not approved or enforced by this preparation record.
The build proposal must contain executable commands after the missing tool and dependencies are verified.
Do not substitute another focused fixture for a complete native build.
Keep any install-prefix, runtime selection, application, rollback, and live proof decisions separate.

Only a later ready operational plan can request application or live qualification.
It must include the real executable observer, supported process controls, shared-profile effects, rollback, and exact submission bytes.
Keep one submission, at most `600` seconds, one `15`-second cleanup allowance, and an independent `630`-second ceiling.
Require prior matching active association and four separate outcomes: gateway termination, foreground exit, owner closure, and server release.
Preserve unknown results and never replay an uncertain submission.

## Evidence and limitations

Private evidence resides in `association-operational-prep-20261101-01a198c7` under the preserved S1b root.
`audit_preparation.py` records individual commands, exits, source ranges, manifests, and selected process fields.
The audit exited `0` using Darwin `27.2.0`, arm64, and CPython `3.11.14`.
It preserves 1,291 starting private files and records 1,379 starting tracked repository files.
The accepted candidate's 46 files, 12 installed sources, one support source, and 1,110 historical private files match their manifests.
Candidate, correction diff, and all three cumulative patch digests match the accepted review.
The historical 130-test and four-case native results remain historical. This session did not rerun them.

Trusted current `turn_context` metadata identified `gpt-6.1-sol`.
RTK reports `1.1.0`. The versioned Crewshal skill files match their installed counterparts.
The required companion skills loaded from their recorded installed paths.
The synthetic Jev call returned probability `0.98`, confidence `0.96`, reported cost `0`, and latency `335` milliseconds.
Actual total billing remains unknown.

Actual MCP calls confirmed the Crewshal graph project and generation `2026-10-31T21:18:33Z`.
Graph tools were accessed through their configured stdio service because this chat exposed no direct graph tool.
Coverage flagged changed handoff metadata and untracked recent records; exact current reads supplied the evidence.
The project listing contained no matching Studio or native project. Those sources used exact source fallback.
No graph result establishes exhaustive coverage.
Truncated exploratory reads, missing-path searches, and the system interpreter's missing `yaml` supplied no passing evidence.
The successful audit used the installed Hermes interpreter. It did not launch Hermes inference.

Publication verification passed these checks:

| Check | Result |
| --- | --- |
| `rtk proxy git diff --check` | Exit `0`. |
| `rtk proxy env -u PYTHONPATH .venv/bin/python scripts/check_phase_3a_freeze.py` | Exit `0`; all 23 frozen artifacts remain consistent. |
| Version and import | Exit `0`; version `0.27.25` imports from the current checkout under CPython `3.12.16`. |
| Scope, links, preservation, and historical status entries | Passed against the starting manifests and exact intended paths. |

The private closure record retains complete commands, outputs, and final diff identities.
Product suites, Ruff, mypy, wheel builds, and package installation remain not run for this documentation checkpoint.
Linux checks remain deferred under ADR 0009.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.
Use the [next prompt and exact inputs](CREWSHAL-NATIVE-BUILD-CAPABILITY-NEXT-SESSION-2026-11-01.md).
