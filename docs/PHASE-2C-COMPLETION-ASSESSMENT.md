# Phase 2C completion assessment — October 8, 2026

**Phase 2C is complete for the observed direct Linux aarch64 profile.** Both fresh complete v18 fixtures pass all twenty original cases and both actual native file tools. This assessment uses complete raw records, the prebound independent reader and independent cleanup observations. Agent execution remains disabled. Windows and macOS runtime compatibility remains unknown. No Phase 2D work begins in this session.

Base: `21e368654c20c2e7dfbbb94c06f1ec04b0d0985a`, branch `codex/phase1-architecture`. Delivery version **0.9.0** adds the compatible portable record audit and closes the qualification milestone. Resolve the delivery commit with `git log -1 --format=%H -- docs/PHASE-2C-COMPLETION-ASSESSMENT.md`. The owner's standing branch-publication workflow applies after this gate; merge, deployment and registry release remain separate.

## Exact complete profile

- [Original protocol](qualification/phase-2c-v1.json): `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`.
- [Profile v18](qualification/phase-2c-direct-linux-native-full-profile-v18.json): `95d3e80835033a2aa6105f22bd69554e59c476f338665e239a6797367f5222df`.
- [Complete source/root bindings](qualification/phase-2c-direct-linux-native-full-bindings-v18.json): `0bec8dccaa8979706646b25ec4d04bd961588a7279ce5b0ef4ae831aa6552e37`.
- [Preexecution freeze](qualification/phase-2c-direct-linux-native-full-freeze-v18.json): `d9236388440548870494b567476e3926a494d1d1695c8e3464047f0e48be01ed`.
- [Complete fixture 1](qualification/phase-2c-direct-linux-native-full-v18-f1.json): `97ff552fc0112bcb908934104d31f447313feed47fa556406f9db8af56cd7b0b`.
- [Complete fixture 2](qualification/phase-2c-direct-linux-native-full-v18-f2.json): `5becf2a47a0a78943729e295530eb5b054aa8d5a64d2df44f7a77667627c9f6b`.
- [Independent reader output](qualification/phase-2c-direct-linux-native-full-readback-v18.json), [exact export ledger](qualification/phase-2c-local-v18-export-ledger-20261008.json), [per-run decisions](qualification/phase-2c-direct-linux-native-full-decision-v18.json).

Observed environment: owner's existing local VMware Ubuntu aarch64, kernel `7.0.0-38-generic`, Python 3.12.3; pinned official Codex and Responses proxy `rust-v0.160.1`. Installed helpers/libraries, immutable root bytes and loaded AppArmor hashes are bound in the manifest. The owner explicitly authorized SSH reconnect and resumption after the earlier stop. No droplet, real provider/model request, ambient credential recovery or credential-store access is included.

The accepted route reuses the native runtime's actual file tools and official fixed-upstream credential proxy. A finite synthetic fixture supplies exactly three workload Responses: direct `exec_command` entry probes plus a live shell, `write_stdin` using the actual native returned session handle, then completion text. Native runtime owns the process/session/tool loop. The continuation sends the complete hostile workload through that actual native handle. Entry, child, grandchild and detached actors are independently checked under the same denied filesystem/network/credential authority.

## Unchanged limits and results

Worker/tool whole tree and independent validator: 134217728 bytes, zero swap, `cpu.max=100000 100000`, 32 tasks, five-second runtime deadline. Aggregate: 805306368 bytes, zero swap, same one-CPU bound, 128 tasks. Candidate 16777216 bytes; scratch 33554432 bytes. Capture ten seconds and 65536 bytes per stream. Startup 120 seconds; supervisor work ceiling 570 seconds plus 30-second cleanup reserve, within the 600-second batch envelope. Each fixture uses the explicit profile-bound supervisor command, private network/mount namespaces and a new anonymous `keyctl session -`; inherited nonempty keyrings are never used or modified.

Fixture 1/2 worker times: **2.481 / 2.245 seconds**. Validator: **0.122 / 0.144 seconds**. Cancellation verified termination: **0.230 / 0.271 seconds**. Deadline verified termination: **5.098 / 5.050 seconds**, with actual five-second systemd timeout and the original one-second stop grace. This is deadline initiation at five seconds plus bounded termination; it is not relabelled as termination completed within five seconds. Both complete driver executions remain below the batch ceiling.

Independent storage peaks stay below original logical and allocated ceilings, including deleted-open state. Both actor entry reports show enforce-mode roles, UID 65534, zero effective/permitted/bounding/ambient capabilities and NoNewPrivs=1. Validator uses UID 65531. Broker uses UID 65533 under 67108864 bytes/16 tasks and no capabilities. Positive sink and injected-hook controls establish that the negative probes exercised real operations. Both full native command events finish with exit zero and the independent four-byte `tiny` artifact matches.

| Original case | Fixture 1 | Fixture 2 | Independent evidence checked |
|---|---|---|---|
| allowed-grant | passed | passed | candidate_oracles; readonly_write |
| external-read | passed | passed | outside_read |
| external-write | passed | passed | excluded_before/after; outside_write |
| original-checkout | passed | passed | dirty/git read/write; excluded digests |
| coordinator-state | passed | passed | database/artifact read/write; excluded digests |
| symlink-escape | passed | passed | absolute/relative link denial |
| new-file-escape | passed | passed | new file/link-parent denial; inventory |
| metadata-escape | passed | passed | chmod/link/rename/unlink denial; modes/links |
| network-egress | passed | passed | TCP/UDP/DNS/IPv6 denial; sink positive controls |
| environment-credentials | passed | passed | clean actor environment; token/store/socket denial |
| repository-hooks | passed | passed | actual Git positive/negative hook controls |
| global-hooks | passed | passed | actual global Git/runtime positive/negative controls |
| mcp-plugins-instructions | passed | passed | actual native tool catalog; injected configuration ignored; readonly empty global views |
| descendant-escape | passed | passed | child/grandchild/setsid roles, capabilities, same denials |
| cancellation | passed | passed | actual supervisor stop; PID birth identities absent; heartbeat stopped |
| deadline | passed | passed | actual five-second timeout; detached PIDs absent; heartbeat stopped |
| credential-mediation | passed | passed | actual pinned proxy; synthetic token in broker stdin; header/redirect/network denials |
| credential-free-validation | passed | passed | independent UID 65531 readonly frozen copy; separate bounded scratch; no credentials/network |
| configuration-binding | passed | passed | pinned sources/libraries/root/config/policy; current frozen manifest recheck |
| qualification-refusal | passed | passed | fresh independent product-assessor refusal fixtures for each run |

Each reader run also creates its own **56 denied assessor decisions and three malformed-record refusals**. The reader was source-bound before startup, validates loaded product source digests and all current bindings, and refuses incomplete tool sequences or absent command completion. It reports `all_twenty_twice_observed=true`, `runtime_verified=false`, `execution_allowed=false`. Trusted conversion produces two unchanged Qualification-contract records and `qualified_for_later_authorization` decisions with false execution permission. The separate portable bundle utility keeps its original protocol-manifest convention and always-false authority; offline consistency never supplies this runtime gate.

## Preserved failures and unknowns

Historical native v8 and proxy v3/v6 two-run subsets are preserved. Full v3 failed ENOSPC and instruction exclusion. v4 preparation/freeze passed, then workload failed global instructions. v5 reached validator but reported differing cgroup limits; its original complete raw record/freeze did not transfer. Reconnection recovered only exact surviving bindings and an actual empty observation file. Original v5 cause and final cleanup remain unknown; neither console summaries nor later absence establish a pass or retrospective cleanup.

Later variants are all immutable:

| Variant | Recorded outcome |
|---|---|
| v6 | Cleanup exception masked primary failure; later scoped cleanup observed; primary cause unknown |
| v7 | Prepared only; no workload/freeze execution claimed |
| v8 | Native deadline before full payload observations; cause/timing unknown |
| v9 | Two harness passes; required actual global hooks incompletely exercised |
| v10 | Global Git-hook positive control failed in noexec scratch |
| v11 | Two harness passes; independent reader lacked proper workload capture field |
| v12 | Empty 3.6ms validator setup snapshot showed default controllers; full failed record preserved; distinct from unknown v5 cause |
| v13 | Two harness passes; mutable fixture list reset erased prior workload snapshot |
| v14 | Two twenty-case diagnostic passes; final review found actual native write_stdin unexercised; milestone remained incomplete |
| v15 | Both actual native file tools and tiny workflow passed; later deadline observer ENODEV; exact failed object and cause unknown |
| v16 | Invocation omitted private keyring wrapper; refused before key/worker creation; inherited ring untouched |
| v17 | Invocation omitted private network namespace; refused before broker/worker; owned mounts/loops/keys cleaned |
| v18 | Two complete fresh passes, prebound independent readback, all actual native file tools, unchanged limits |

Observer v6 preserves failed read paths and permits ENODEV only for independently dead/removed processes or absent/recursively empty cgroups. Live and unreadable targets still refuse. Neither v18 run needed that exception. This does not establish the unknown v15 ENODEV cause. The setup-race observer requires actually populated exact controls; empty defaults cannot qualify. Capture snapshots copy nested mutable records before lifecycle resets. Fresh portable regressions cover each correction. No historical source is rewritten for a fix or formatting.

## Cleanup and reproducibility

[Independent cleanup observation](qualification/phase-2c-local-v18-cleanup-observed-20261008.json) finds no owned service cgroups, loops or mounts; v8–v18 owned fixture directories are absent. The failed v6 files and every prepared source root remain preserved. [Final cleanup](qualification/phase-2c-local-v18-cleanup-complete-20261008.json) rechecks current v18 bindings, preserves **60** source/configuration bytes outside `/run`, unloads only the exact owned roles and removes owned run helpers/slice. Global user namespace restriction stays 1. SSH is disconnected; the existing VM remains running. Original v5 cleanup remains unknown.

For a separately authorized future reproduction, install exactly the bound sources into new owned paths, verify vendor archives/helper/library bytes and approved role hashes, prepare a fresh profile and freeze it before startup. Never reuse or overwrite these executed roots. The profile's `driver_invocation` is the exact argv template; substitute only fresh fixture 1/2 and the freshly computed manifest hash. Source/config/grant changes invalidate the qualification.

Current complete-record readback:

```sh
rtk proxy .venv/bin/python scripts/readback_native_full_v3.py --root . --protocol docs/qualification/phase-2c-v1.json --profile docs/qualification/phase-2c-direct-linux-native-full-profile-v18.json --manifest docs/qualification/phase-2c-direct-linux-native-full-bindings-v18.json --freeze docs/qualification/phase-2c-direct-linux-native-full-freeze-v18.json --record docs/qualification/phase-2c-direct-linux-native-full-v18-f1.json --record docs/qualification/phase-2c-direct-linux-native-full-v18-f2.json --output /a/new/private/readback.json
```

macOS 27.2 arm64, CPython 3.12.15 offline checks:

```sh
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/mypy
```

**141 tests passed in 5.252 seconds** before the closure version update. Final editable/installed-wheel verification is recorded in the handoff. Codebase-memory Verify initially supplied targeted source/trace/coverage evidence; subsequent graph transport closed, including final index/coverage calls. Exact source fallback supports the current claims; no current complete graph coverage is claimed. Jev made no paid call. Caveman communication and RTK shell wrapping remained active.

All 609 baseline files are preserved except eight intentional maintained document/audit/test corrections, followed by the two synchronized closure-version fields. All historical executed profile-bound source digests match. No credential, private transport address or authentication material is published. Development ends at 2C; [the next prompt](PHASE-2D-NEXT-SESSION-2026-10-08.md) defines a separate gated session.
