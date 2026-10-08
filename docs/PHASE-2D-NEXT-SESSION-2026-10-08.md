# Next session: Phase 2D — first runtime and deterministic checks

Phase 2C is complete on the exact v18 local Linux aarch64 profile; package 0.9.0. Start a separate session and name **2D** as its sole milestone. Do not reinterpret qualification as execution permission. No 2D implementation or live model run occurred in the 2C closure.

Read AGENTS.md and RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, ARCHITECTURE.md and accepted ADR 0003 first. Apply Caveman, codebase-memory Verify with freshness/coverage/source fallback, and Jev only within the no-paid-model boundary. Preserve all original and historical source/profile/binding/freeze/observation bytes, failed variants and unknowns.

Implement the bounded first-runtime seam and deterministic offline contracts specified in the plan: recorded/synthetic event streams must reject malformed output, missing identities, stale or forged evidence, quota/refusal, cancellation, timeout and incomplete captures. Coordinator evidence stays separate from worker prose. Preserve original checkout/dirty files and freeze candidates for credential-free validation. Use the existing qualified native runtime seam; no custom gateway or new model/tool loop. Do not start 2E/evaluation.

The 2C test fixture is a qualification harness, not a production launcher. Any actual runtime startup needs the separate recorded owner execution gate; any paid model/provider test needs a concrete reviewable batch, identities, ceilings and explicit spend authorization. Prepare all safe offline work before requesting a missing gate. Do not access credential stores or assume transient guest setup is present: owned roles/helpers/slice were removed and SSH disconnected. Use only local VMware Ubuntu when necessary under current local authorization; no droplet or other paid host. Windows/macOS runtime compatibility is unknown and must remain so without target evidence. Exact profile changes require fresh qualification; never silently transfer v18 eligibility to a different identity.

Finish only 2D, run independently reproducible required checks, update continuity/next prompt and use the standing version/README/changelog/handoff/commit/push ceremony only after its completion gate. If a required live gate is absent, record a precise incomplete boundary without claiming production execution passed.

## Exact inputs

- [AGENTS.md](../AGENTS.md), [README.md](../README.md), [CHANGELOG.md](../CHANGELOG.md)
- [HANDOFF.md](HANDOFF.md), [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md), [DEVELOPMENT.md](DEVELOPMENT.md)
- [ARCHITECTURE.md](ARCHITECTURE.md), [ADR 0002](decisions/0002-minimal-architecture.md), [accepted ADR 0003](decisions/0003-direct-linux-qualification.md)
- [STATE-AND-GATES.md](STATE-AND-GATES.md), [complete 2C assessment](PHASE-2C-COMPLETION-ASSESSMENT.md)
- [All preserved 2C exact inputs](PHASE-2C-ACTIVE-CONTINUATION.md); load every file listed there, including the linked published input set and current additions. Older prompts are historical.
- [qualification.py](../src/crewshal/qualification.py), [model.py](../src/crewshal/model.py), [contracts.py](../src/crewshal/contracts.py), [gates.py](../src/crewshal/gates.py), [durable.py](../src/crewshal/durable.py)
- [offline audit guide](PHASE-2C-OFFLINE-AUDIT.md), [portable audit source](../src/crewshal/qualification_bundle.py), [audit tests](../tests/acceptance/test_phase_2c_bundle.py)
- [v18 profile](qualification/phase-2c-direct-linux-native-full-profile-v18.json), [bindings](qualification/phase-2c-direct-linux-native-full-bindings-v18.json), [freeze](qualification/phase-2c-direct-linux-native-full-freeze-v18.json)
- [v18 full run 1](qualification/phase-2c-direct-linux-native-full-v18-f1.json), [full run 2](qualification/phase-2c-direct-linux-native-full-v18-f2.json), [independent readback](qualification/phase-2c-direct-linux-native-full-readback-v18.json), [false-permission decisions](qualification/phase-2c-direct-linux-native-full-decision-v18.json)
- [Current cleanup](qualification/phase-2c-local-v18-cleanup-complete-20261008.json), [original protocol](qualification/phase-2c-v1.json)

Credentials, addresses and private transport state are not inputs. Original v5 missing raw evidence/cause/final cleanup remain unknown. Never manufacture that history or combine historical subsets into a complete profile.
