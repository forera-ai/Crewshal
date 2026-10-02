# Changelog

Versions follow semantic versioning. Remote branch publication is distinct from a package-registry release; no registry release has occurred.

## 0.2.0 — 2026-10-02

- Complete Phase 2B: private SQLite coordinator records, atomic ordered events, optimistic version conflicts, run leases and inert launch-intent reconciliation without replay.
- Add explicit legacy JSON import preserving human decisions and the original file; refuse unsupported database schemas and support schema-1-to-2 migration with a private backup and transactional rollback.
- Add closed task/run/attempt, approval, claim, capture, waiver, verdict and cumulative usage contracts. Keep worker claims and informational exports outside completion authority.
- Bind gates to exact model/task/policy/scope/candidate digests, verify captured artifact bytes, distinguish nonpassing check states and require known independent provider identities where configured.
- Preserve failed/missing gate status when an owner waiver names its gate and residual risk. Deduplicate cumulative usage by attempt/event identity; retain unknown measured cost and separate estimates/quota.
- Verify 21 new Phase 2B cases and all 12 Phase 2A cases; document migration, trusted API boundaries and the standalone Phase 2C prompt. No launcher or execution qualification is delivered.

## 0.1.1 — 2026-10-02

- Persist the owner's automatic branch-push authorization and required version/README/changelog/handoff ceremony.
- Require concise next-session prompts with explicit input files and stop development at the completed milestone boundary.
- Synchronize package metadata and runtime version. Phase 2A behavior and its acceptance scope are unchanged.

## 0.1.0 — 2026-10-02

- Deliver Phase 2A's installable Python package and CLI for bounded passive Python/TypeScript manifest discovery.
- Add typed versioned project contracts, explicit human correction/confirmation, provenance and narrow invalidation.
- Keep coordinator state outside repositories; require explicit non-overwriting informational exports.
- Add 12 synthetic acceptance cases, pinned dependencies, offline artifact verification and development documentation.
- Runtime execution, trusted evidence gates and evaluation remain future milestones.
