# Phase 3B S3 containment-driver inventory (local, read-only, 2026-10-23)

Hermes prepared this document under the Crewshal profile. It is the S0 driver-candidate inventory that
proposal stage S3 requires (`docs/PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-PROPOSAL-2026-10-23.md`, section 5,
stage S3; audit REVISION finding 1). It maps all 20 mandatory containment cases at
`src/crewshal/qualification.py:10-31` to existing driver candidates. A candidate driver is not a qualified
Linux result. Every case mapping stays provisional until Codex accepts a driver for that case and the
chosen guest passes its actual admission gate. This session ran no guest action, no live containment case,
and no evaluation row.

Evidence tier: Verify (Tier 2). Graph project `Volumes-X10Pro-Crewshal`, generation
`2026-10-23T18:52:59Z`; `check_index_coverage` reported `no_recorded_issue` for all 14 evidence paths
(best-effort signal; source was read directly for every material claim).

## Candidate driver families and digests (local, this session)

| Family | Driver path | sha256 (this session) | Role |
| --- | --- | --- | --- |
| Native-full | `scripts/probe_native_full_v18.py` | `cd4a4adc7e22b80850c9d2a621356b3051a3decd9bd7938e6f2602aedae2df80` | Guest-side runner of the v18 profile; produces one run record per fixture |
| Native-full | `scripts/readback_native_full_v3.py` | `80628f03b6eae8beb20b86e8564ba880f0025f9efb2213d158dcbf8eb2216097` | Prebound independent aggregator; maps all 20 cases from named record fields into `crewshal.qualification` records |
| Substrate | `scripts/probe_linux_profile.py` | `b53230625b6b8a5ce82f47f696edfd9632588ef3d4d75c36fdf6c798d6e786d9` | 9-case filesystem/credential subset against a Docker host |
| Substrate | `scripts/probe_linux_network.py` | `7636e21bb257cae29397ec639122f67ee6c103ed62cf83f6d5868389126c512a` | network-egress case against a Docker host |
| Substrate | `scripts/probe_linux_lifecycle.py` | `20940da29590f8e263d842a32759d227c3ebb0e6e96c1b394d3d595a7f57c598` | 4-case lifecycle subset against a Docker host |
| Adjacent | `scripts/probe_direct_linux_native_compatibility_v18.py` | `768e6b2be104d1ca8808ece810eeb3c12117f23edfbe0b2df01e4e26801914e2` | Fixture-only native sandbox capability probe; docstring: "never qualification". Not a case driver. |

Bound input identities (local digests equal the values recorded in
`docs/PHASE-2C-COMPLETION-ASSESSMENT.md:10-15`, verified this session): protocol
`docs/qualification/phase-2c-v1.json` `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`
(equals the `PROTOCOL` constant in `scripts/readback_native_full_v3.py:20`, verified this session); profile-v18
`95d3e80835033a2aa6105f22bd69554e59c476f338665e239a6797367f5222df`; bindings-v18
`0bec8dccaa8979706646b25ec4d04bd961588a7279ce5b0ef4ae831aa6552e37`; freeze-v18
`d9236388440548870494b567476e3926a494d1d1695c8e3464047f0e48be01ed`; complete fixture records f1
`97ff552fc0112bcb908934104d31f447313feed47fa556406f9db8af56cd7b0b` and f2
`5becf2a47a0a78943729e295530eb5b054aa8d5a64d2df44f7a77667627c9f6b`.

## Argument contracts (read from source this session)

- `probe_native_full_v18.py`: `mode {prepare|run}`, `--manifest-sha256`, `--fixture {1,2}`. Startup gate at
  lines 1303-1304 (verified this session) refuses unless `euid == 0` and `machine == "aarch64"`. Bases: `/var/tmp/crewshal-native-qualification-v18`,
  systemd slice `crewshalnativediscoveryv1.slice`; runtime helpers load from bound `/run` paths.
- `readback_native_full_v3.py`: `--root --protocol --profile --manifest --freeze --record (repeatable) --output`.
  Bound example at `docs/PHASE-2C-COMPLETION-ASSESSMENT.md:87`.
- Substrate trio (`probe_linux_profile`, `probe_linux_network`, `probe_linux_lifecycle`): identical contract
  `--docker-host unix:///... --manifest --manifest-sha256 --output`. All three invoke the Docker client at
  the hardcoded macOS path `/opt/homebrew/bin/docker` (`scripts/probe_linux_profile.py:88`).

## Local fixture evidence per family (this session)

- Substrate trio: `tests/acceptance/test_phase_2c_substrate.py`, `test_phase_2c_network.py`, and
  `test_phase_2c_lifecycle.py` import the drivers directly and patch `docker_capture` with fakes. This
  session ran the seven named Phase 2C acceptance modules: `.venv/bin/python -m unittest
  tests.acceptance.test_phase_2c_{substrate,network,lifecycle,native_readback,native_readback_v2,capture_snapshot,protocol}`
  → `Ran 36 tests ... OK`, exit 0. Offline; no Docker daemon contacted.
- Native-full: no test imports `probe_native_full_v18` or `readback_native_full_v3` (grep over `tests/`).
  Their local evidence is the stored v18 record set under `docs/qualification/` listed above, produced by
  the earlier direct-Linux aarch64 substrate runs. Predecessors are unit-tested:
  `test_phase_2c_native_readback.py` (v1 `check_run`, `load`), `test_phase_2c_native_readback_v2.py`
  (`instruction_evidence`), `test_phase_2c_capture_snapshot.py` (`probe_native_full_v14.capture_observations`).

## Case-to-candidate map (all 20 mandatory cases)

Column N18 = native-full pair above. The guest probe and the local assessor are separate execution roles.
Cases 1–19 come from `probe_native_full_v18.py` on the guest and are checked in
`readback_native_full_v3.check_run` at the named field. Case 20 (`qualification-refusal`) does not come from
the guest probe: it runs in the local readback assessor — `refusal()` performs a fresh local check inside the
aggregator on the aggregating host (row 20). Substrate columns mark the second candidate.
Every mapping below stays provisional: it becomes binding only when Codex accepts one driver for that case
and the chosen guest passes its actual admission gate (section "Cross-cutting missing bindings").

| # | Case | Candidates | readback field / substrate driver | Local fixture evidence | Missing binding (all rows share the cross-cutting set below) |
| --- | --- | --- | --- | --- | --- |
| 1 | allowed-grant | N18 + profile | `checks["allowed-grant"]` (`readback_native_full_v3.py:179`, verified this session; earlier `:96` was wrong) | readback v1 records; substrate unit tests | — |
| 2 | external-read | N18 + profile | `checks["external-read"]` | as row 1 | — |
| 3 | external-write | N18 + profile | `checks["external-write"]` | as row 1 | — |
| 4 | original-checkout | N18 + profile | `checks["original-checkout"]` | as row 1 | — |
| 5 | coordinator-state | N18 + profile | `checks["coordinator-state"]` | as row 1 | — |
| 6 | symlink-escape | N18 + profile | `checks["symlink-escape"]` | as row 1 | — |
| 7 | new-file-escape | N18 + profile | `checks["new-file-escape"]` | as row 1 | — |
| 8 | metadata-escape | N18 + profile | `checks["metadata-escape"]` | as row 1 | — |
| 9 | network-egress | N18 + network | `checks["network-egress"]`; `probe_linux_network.py` (`executed_subset == ["network-egress"]`, line 60, verified this session) | readback v1 records; network unit tests | — |
| 10 | environment-credentials | N18 + profile | `checks["environment-credentials"]`; profile `CASES` at `probe_linux_profile.py:22` (verified this session; the earlier "slice line 40" was wrong — all nine observed entries sit on that one line) | as row 1 | — |
| 11 | repository-hooks | N18 only | `checks["repository-hooks"]` from `hooks` record fields | readback v1 records only; no substrate driver found (grep over `scripts/`) | no second candidate exists |
| 12 | global-hooks | N18 only | `checks["global-hooks"]` | as row 11 | no second candidate exists |
| 13 | mcp-plugins-instructions | N18 only | `checks["mcp-plugins-instructions"]` via `instruction_evidence` | as row 11 | no second candidate exists |
| 14 | credential-mediation | N18 only | `checks["credential-mediation"]` from `provider_auth_observations`/`broker_*` | as row 11 | no second candidate exists |
| 15 | descendant-escape | N18 + lifecycle | `checks["descendant-escape"]`; lifecycle `CASES` at `probe_linux_lifecycle.py:54` (verified this session; earlier "line 37" was wrong) | readback v1 records; lifecycle unit tests | — |
| 16 | cancellation | N18 + lifecycle | `checks["cancellation"]` | as row 15 | — |
| 17 | deadline | N18 + lifecycle | `checks["deadline"]` | as row 15 | — |
| 18 | credential-free-validation | N18 + lifecycle | `checks["credential-free-validation"]`; same lifecycle `CASES` line 54 (earlier "line 40" was wrong) | as row 15 | — |
| 19 | configuration-binding | N18 only | `checks["configuration-binding"] = binding_verified` (`readback_native_full_v3.py:359`, verified this session; earlier "line 127" was wrong) | readback v1 records only | no second candidate exists |
| 20 | qualification-refusal | N18 only | `refusal()` at `readback_native_full_v3.py:62-102` (verified this session; earlier "lines 59–93" was wrong). Execution location and evidence type: a fresh local assessor check — `refusal()` builds fresh fixtures against the bound product assessor on the aggregating host, and `check_run()` marks `qualification-refusal` from that local check at lines 132 and 423. It is not a guest containment observation from the v18 probe. | readback unit tests on v1/v2 predecessors | no second candidate exists |

No case lacks a candidate. No command was invented here: cases 11–14, 19 and 20 have exactly one candidate
family each, and the substrate trio covers only its declared CASES subsets.

## Cross-cutting missing bindings (why every row stays a candidate)

1. Codex has not accepted this candidate set; stage S3 requires review before any command binds.
2. Platform gate conflict: `probe_native_full_v18.py` refuses to start unless the host reports `aarch64`
   as root (startup gate at lines 1303-1304). The G1 proposal targets Linux `aarch64` at stages S1 and S3,
   and its option A2 bundle name states Ubuntu `arm64`. No observation has confirmed either VMware guest's
   effective architecture, so the guest's effective architecture and admission state stay unknown until the
   S1 admission observation passes. U-5 stays open; no candidate is verified runnable on any G1 guest before
   that observation and Codex acceptance. The earlier "planned VMware x86_64 guest" wording was false and is
   removed (Codex audit finding 1); no x86_64 profile decision is invented for this campaign.
3. The substrate trio binds the macOS Docker client path `/opt/homebrew/bin/docker` and a `unix:///` host:
   verified against the Phase 2C substrate only. No Linux-guest-side equivalent driver exists in the repo.
4. Every driver needs fresh admitted manifest/profile/freeze identities (`--manifest-sha256`, bound profile).
   The v18 input digests above are historical bindings, not G1 bindings.
5. Guest transport stays unbound (proposal decision 5); no file reached any guest in this session.

## Correction log — Codex S3-driver-inventory audit, 2026-10-23

This session applied every finding of
`docs/CODEX-AUDIT-PHASE-3B-S3-DRIVER-INVENTORY-2026-10-23.md`:

1. Finding 1 (P1): the false "planned VMware x86_64 guest" claim is removed from cross-cutting binding 2.
   The proposal targets Linux `aarch64`; each guest's effective architecture and admission state stay
   unknown until the S1 admission observation passes.
2. Finding 2 (P2): the six source references are corrected against live source at HEAD
   `6279a2eb32714530beffab7e6425c3d41fbcfbb5` — protocol constant `readback_native_full_v3.py:20`;
   `refusal()` starts at line 62; `allowed-grant` at line 179; `configuration-binding` at line 359; profile
   `CASES` at `probe_linux_profile.py:22`; lifecycle `CASES` at `probe_linux_lifecycle.py:54`. The network
   `executed_subset` marker re-verified at `probe_linux_network.py:60`, and the v18 startup gate at lines
   1303-1304 (earlier text said 1301).
3. Finding 3 (P2): row 20 now states the execution location and evidence type — a fresh local assessor
   check performed by the readback aggregator, not a guest containment observation from the v18 probe.
4. The case-to-candidate map intro now labels every mapping provisional until Codex accepts one driver per
   case and the chosen guest passes its actual admission gate.

### Repair of the G1 S3-readiness re-audit (third follow-up session, 2026-10-23)

Codex audit `docs/CODEX-AUDIT-PHASE-3B-G1-S3-READINESS-2026-10-23.md` found that the map introduction still
contradicted the corrected case 20 row (its finding 2). Repaired: the introduction no longer says every N18
case comes from the guest v18 probe. It now names the guest probe and the local assessor as separate
execution roles, states that cases 1–19 come from the guest probe, and states that case 20 runs in the local
readback assessor (`refusal()` inside `readback_native_full_v3.py`), not the guest probe. No other row,
digest, or binding statement changed.

## Statement of separation

The stored v18 records prove earlier direct-Linux aarch64 behaviour. They do not qualify the planned G1
guest and are not G1 rows. This inventory creates planning knowledge only; agent writes stay disabled and
S3 stays blocked until bindings 1–5 close and Codex accepts the chosen drivers.
