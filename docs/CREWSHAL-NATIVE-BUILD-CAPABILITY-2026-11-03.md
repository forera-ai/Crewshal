# Native build capability and restricted-execution boundary

Date: 2026-11-03. Package checkpoint: `0.27.26`. Crewshal skill: `1.0.0`.
Base: `f28689589f12d986afe6cfbbf342ee0d16b8b609` on `codex/phase1-architecture`.
Delivery revision: the commit containing this record.

## Result

CMake `4.3.4` is available in the local `uv` cache and runs successfully outside the proposed restricted policies.
The owner requested local discovery instead of supplying its path.
The discovered executable exceeds the required minimum version `3.18`.
Its SHA-256 is `2269945a888b2ef8a1a6372bff49c59f5b789e3ba3ec355ad576614f4f1801e0`.
Its capabilities include `Unix Makefiles`, which matches the available GNU Make `3.81`.
The executable contains arm64 and x86_64 Mach-O slices.
A private manifest binds 4,041 CMake distribution files, including the required compiler and OpenSSL modules.
AppleClang uses separate language-specific modules; no generic `Compiler/AppleClang.cmake` exists in this distribution.
That filename observation does not indicate a missing language module.

A complete native build remains unperformed and unqualified.
Both proposed restricted CMake version checks fail with exit `134` and reported signal `6`.
Their cause remains unknown. No native configure command or build followed either failure.
The build draft remains unready. This checkpoint requests no build approval.

## Verified dependencies and preserved inputs

Current commands confirm Apple Clang `21.0.0`, macOS SDK `27.2`, and GNU Make `3.81`.
The arm64 OpenSSL `3.5.9` headers and libraries are present.
The native loader returned `OpenSSL 3.5.9 29 Sep 2026` from the selected crypto library.
The selected SSL library depends on the matching crypto library and the system runtime.
The inspected Intel OpenSSL libraries do not supply the proposed arm64 dependency.
No dependency download, installation, link test, TLS handshake, Metal build, or Metal runtime check ran.
The earlier failed `metallib` lookup remains historical evidence.
The inspected embedded-source branch still does not use that separate build path.

Private manifests bind 41,697 SDK entries, 364 compiler-resource entries, and 7,596 TLS entries.
They also bind the selected tool executables, OS build, and 84 arm64e dyld cache files.
These records identify observed bytes. They do not authenticate upstream source provenance or prove loaded model-library identity.

Fresh comparisons found no mismatch in these preserved inputs:

| Input | Fresh result |
| --- | --- |
| November 1 starting private manifest | All 1,291 files match. |
| Accepted correction candidate | All 46 files match. |
| Installed source and support inputs | All 12 installed files and one support file match. |
| Accepted historical private manifest | All 1,110 files match. |
| Native source manifest | All 3,964 regular files match, with the same complete regular-file set under its recorded exclusions. |
| Cached runtime metadata | All 42 entries match sizes and hashes; metadata bytes also match. |
| Candidate, correction diff, and three cumulative patches | All reviewed digests match. |
| Profile, SOUL, and Crewshal skill installation | All selected bindings match. |

The accepted association candidate remains unchanged, unapplied, and unqualified for operation.
The historical 130 guarded tests and four native serializer cases were not rerun.
All source budgets remain consumed. The separate translator budget remains unused.
No fresh server observation was required. The November 1 process arguments remain historical observations.
Current effective context, capacity, request behavior, and loaded library identity remain unverified.

## Synthetic control checks and failure boundary

A synthetic network-only socket probe returned `EPERM` before connecting to loopback port `9`.
This result does not qualify CMake or a model route under the proposed build policy.
A fresh 64 MiB private APFS image returned `ENOSPC` after 63,963,136 written bytes.
Its backing file remained exactly 67,108,864 bytes.
The owned image detached with exit `0`. Cleanup removed only that exact detached image.
Its command records, size, digest, and cleanup result remain private.
These synthetic host-image actions did not inspect or operate a VMware guest.

A private command supervisor passed four synthetic cases:

- It accepted a successful child.
- It rejected a child with exit `7`.
- It stopped an owned child group at a `0.3`-second work deadline, within a separate `2`-second ceiling.
- It stopped excessive output at a scaled `1,024`-byte test ceiling.

All four final group checks observed no remaining owned process group.
These checks do not prove complete native build supervision or containment.

The first proposed sandbox policy denied unspecified operations.
The second allowed ordinary operations while retaining file-data, write, and network restrictions.
Both CMake version commands exited `134`; RTK reported termination by signal `6`.
No output establishes whether a read rule, loader requirement, network rule, or another condition caused either failure.
Both policy variants and failed results remain preserved.
The route stopped after those two unsuccessful variants.
A bounded diagnosis must establish the cause before another effective policy can be accepted.
Do not remove independent network denial or required TLS features to obtain a pass.

## Build draft and next acceptance conditions

Private evidence resides in `native-build-capability-20261103-01a1a0f4` under the preserved S1b root.
`DRAFT-PROPOSAL-NOT-READY.md` contains the exact private paths, executable entry point, and proposed arguments.
`bounded_run.py` and `native_build_steps.py` are unaccepted preparation drafts. Do not execute their build path.
Their syntax and synthetic checks cannot replace complete control review.

The draft proposes a fresh source copy and two separate output directories inside a fixed 7 GiB image.
It binds the unchanged accepted native patch and preserves installed files and accepted candidates.
It proposes two sequential complete server builds, each with at most two parallel jobs.
Its independent `1,800`-second total includes cleanup; work stops at `1,770` seconds.
A `64 MiB` command log and `1 MiB` detach diagnostic leave margin below the `8 GiB` new-file ceiling.
Preparation observed more than `100 GiB` free. Future execution must recheck storage admission.
These remain proposed limits, not build authority or established full-build enforcement.

The draft disables UI retrieval, UI builds, Connect, optional TLS retrieval, LLGuidance, and ccache.
It retains required TLS, Metal, CPU, Accelerate BLAS, RPC, and subprocess support.
It requests disconnected dependency handling and separate sandbox network denial.
It records file-api replies, generated inputs, compile commands, dependency identities, runtime manifests, rpaths, and repeat-build differences.
A complete build must precede independent bundle review and any operational plan that relies on the new native field.

The smallest missing capability is accepted restricted CMake execution with verified file, network, deadline, storage, and cleanup controls.
Resolve that failure with harmless tool queries and synthetic fixtures. Do not run native configuration or compilation as a diagnostic.
Then complete the exact private-build proposal and review all saved commands before requesting a separate owner decision.
No build approval can grant application, service actions, model requests, or live-proof authority.

Later operational planning retains the prior exact-route requirements and four separate lifetime outcomes.
It requires prior active association, exact prompt bytes, policy, session, admission, generation, and auxiliary attempt.
Keep one submission, `600` seconds, one `15`-second cleanup allowance, and an independent `630`-second ceiling.
Never replay an uncertain submission.
Only accepted exact-route control can open one sequential Hermes read-only readiness task.
Only accepted readiness can open the preserved four-file translator task.

## Evidence limits and publication

Trusted current `turn_context` metadata identifies `gpt-6.1-sol`.
The initial checkout was clean, with synchronized version `0.27.25` and canonical `origin`.
RTK reports `1.1.0`. All required skills loaded from their recorded installed paths.
The synthetic Jev check returned probability `0.99`, confidence `0.98`, reported cost `0`, and latency `208` milliseconds.
Actual total billing remains unknown.
Initial Crewshal coverage reported generation `2026-10-31T21:18:33Z`.
Publication coverage reported refreshed generation `2026-11-03T10:44:41Z` with matching metadata for the seven intended paths.
Coverage flagged changed or untracked record metadata; current file reads supplied those facts.
No graph result establishes complete source coverage.

The search covered selected installation roots, development environments, and local tool caches.
One application-directory traversal encountered a permission denial.
Spotlight results included directory names, which were not treated as executable evidence.
No search establishes exhaustive host coverage.
An early private record reported the missing tool before the final cache search completed.
The current private verification record corrects that interim result and preserves the discovered path.

Publication checks passed the whitespace check, all 23 frozen Phase 3A artifacts, synchronized version/import, links, exact scope, and preservation.
The scope check retained 1,376 unchanged tracked files outside the seven intended paths.
The private closure record contains exact commands, outputs, environment, and diff identities.
Product tests, Ruff, mypy, wheel builds, package installation, native configuration, and native builds remain not run for this documentation boundary.
Linux tests and qualification remain deferred under ADR 0009.
No candidate edit, installed-source edit, model-service action, model request, authenticated route, credential extraction, or worker dispatch ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Product writes, guests, campaigns, evaluation, merge, deployment, and releases remain closed.
Use the [next prompt and exact inputs](CREWSHAL-NATIVE-BUILD-CONTROL-NEXT-SESSION-2026-11-03.md).
