# Crewshal rolling handoff and project memory

Last updated: 2026-10-23. This record supplies the next session and the owner with project history. [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) defines the milestone acceptance checks. Preserve the session ledger.

## Current state

**October 23: The Phase 3B read-ledger input-file protection test passed Codex review.**
The focused acceptance test covers `read_ledger` refusals for symlink, directory, empty, and oversize inputs, plus regular-file round-trip parsing.
The symlink case asserts `errno.ELOOP`.
This re-presents the withdrawn v0.27.2 read-ledger test work (commits `a2e26ba`, reverted by `06b40c5`) under a fresh review boundary.
The earlier packet's Codex APPROVE claim was not verified, and commit `4465faf` edited a dated README entry; both defects are excluded here.
The [review packet](CODEX-REVIEW-PACKET-PHASE-3B-READ-LEDGER-INPUT-PROTECTION-2026-10-23.md) holds the exact diff, tests, results, and review outcome.
Codex found no code defect. Codex corrected the package-check labels and verified a fresh offline wheel install.
Changed files: `tests/acceptance/test_phase3b_development_ledger.py`, `pyproject.toml`, `src/crewshal/__init__.py`, `README.md`, `CHANGELOG.md`, `docs/HANDOFF.md`, and the review packet.
The version is `0.27.2` in the working tree (`pyproject.toml` and `src/crewshal/__init__.py` synchronized). Base revision: `18b7a3568427e728ad64cba8c33a7d5b4f4ae20b` on `codex/phase1-architecture`.
Verification ran on macOS 27.2 arm64 with CPython 3.12.15. The focused ledger suite passed 19 tests, and the regression set passed 127 tests.
Ruff check and format, mypy, `git diff --check`, and the frozen package checker passed with both execution flags false.
An offline wheel build and package-manager install into a fresh isolated target reported `0.27.2`.
No production behavior changed. The acceptance test changed, and the frozen Phase 3A package is unchanged.
No Linux test, guest action, native turn, evaluation row, or paid host action ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Phase 3B acceptance remains open under ADR 0009.
The next unmet local source condition is the measurement-record authority guard test (withdrawn commit `4465faf`, reverted by `18b7a35`).
Earlier dated entries remain historical records.

**October 21: The local LLM development handoff checkpoint is complete.**
The [handoff](LOCAL-LLM-HANDOFF-2026-10-21.md) gives the local agent the project history and current gates.
The [start prompt](LOCAL-LLM-START-PROMPT-2026-10-21.md) defines one bounded Phase 3B source session.
The [input index](LOCAL-LLM-INPUTS-2026-10-21.json) binds the current transfer files.
The owner will use Codex to supervise and review the local agent's patch before final publication.
This documentation checkpoint changes no runtime behavior or frozen Phase 3A package byte.
Its version is `0.27.1`. The delivery revision is the commit containing this entry.
Base revision: `015e6b2dc0bda6f06628810aaf88038d52b70dbc` on `codex/phase1-architecture`.
The checkout was clean before edits. Verification ran on macOS 27.2 arm64 with CPython 3.12.15.
The 31 transfer file hashes and new document links matched. `git diff --check` passed.
The frozen package checker passed with 23 artifacts, 768 planned units, and false execution flags.
The focused ledger suite passed 18 tests. The offline `0.27.1` wheel built and installed.
An isolated installed import and metadata check both reported `0.27.1`.
No Linux-specific module ran. Linux and live qualification remain deferred.
Phase 3B remains open. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
No Linux test, guest action, native turn, evaluation row, or paid host action ran in this checkpoint.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
Continue with the [local LLM start prompt](LOCAL-LLM-START-PROMPT-2026-10-21.md).
Earlier dated entries remain historical records.

**October 21: The Phase 3B local source review handoff checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-REVIEW-CHECKPOINT-2026-10-21.md) binds local claim results to declared inventory metadata.
Each result includes the file kind, byte count, SHA-256 digest, source path, and comparison status.
Every result requires later admitted source review and keeps `evidence_verified: false`.
The 126 local fixture and related regression tests passed. Ruff, mypy, and the frozen package checker passed.
The offline installed wheel check passed. No Linux test, guest action, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.27.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-REVIEW-NEXT-SESSION-2026-10-21.md).
Check the [exact inputs](PHASE-3B-LOCAL-REVIEW-INPUTS-2026-10-21.json) before source work.
Earlier dated entries remain historical records.

**October 21: The Phase 3B local claim path checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-PATH-CHECKPOINT-2026-10-21.md) covers bounded JSON source paths across different schemas.
Each populated measurement field declares a path for each named inventory file.
Local fixtures, related regressions, Ruff, mypy, and the frozen package checker passed.
An offline installed wheel check passed. No Linux test, guest action, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.26.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-PATH-NEXT-SESSION-2026-10-21.md).
Check the [exact inputs](PHASE-3B-LOCAL-PATH-INPUTS-2026-10-21.json) before source work.
Earlier dated entries remain historical records.

**October 21: The Phase 3B local claim content checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-CONTENT-CHECKPOINT-2026-10-21.md) covers exact comparisons at matching JSON paths.
The checker reports each matched, unmatched, or unsupported file and field without authenticating the event origin.
The 124 local fixture and related regression tests passed. Ruff, mypy, the frozen checker, and an offline installed wheel passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.25.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-CONTENT-NEXT-SESSION-2026-10-21.md).
Check the [exact inputs](PHASE-3B-LOCAL-CONTENT-INPUTS-2026-10-21.json) before source work.
Earlier dated entries remain historical records.

**October 21: The Phase 3B local source attribution checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-CHECKPOINT-2026-10-21.md) covers field-level links from measurement observations to declared files.
The checker requires `source_refs` for populated run observations, identity fields, effort, usage, costs, and reported details.
Local fixture tests, related regressions, Ruff, mypy, the frozen checker, and an offline installed wheel passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.24.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-NEXT-SESSION-2026-10-21.md).
Check the [exact inputs](PHASE-3B-LOCAL-SOURCE-ATTRIBUTION-INPUTS-2026-10-21.json) before source work.
Earlier dated entries remain historical records.

**October 21: The Phase 3B local provenance checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-PROVENANCE-CHECKPOINT-2026-10-21.md) covers measurement links to inventory files.
The new `check-provenance` command checks inventory digests, local bytes, and attempt outcomes.
It cannot authenticate execution or qualify a platform. Every result keeps `evidence_verified: false`.
Local fixture tests, related regressions, Ruff, mypy, the frozen checker, and an offline installed wheel passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.23.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-PROVENANCE-NEXT-SESSION-2026-10-21.md).
Earlier dated entries remain historical records.

**October 21: The Phase 3B local measurement checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-MEASUREMENTS-CHECKPOINT-2026-10-21.md) covers read-only measurement claim checks.
The new `check-measurements` command binds each declared attempt to its frozen schedule row and accounting fields.
It does not authenticate runs, commands, providers, or platform qualification. It always reports `evidence_verified: false`.
Local fixture tests, related regressions, Ruff, the frozen checker, and an offline installed wheel passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.22.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-MEASUREMENTS-NEXT-SESSION-2026-10-21.md).
Earlier dated entries remain historical records.

**October 21: The Phase 3B local evidence inventory checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-EVIDENCE-CHECKPOINT-2026-10-21.md) covers read-only attempt and artifact integrity checks.
The new `check-evidence` command binds declared attempts to schedule rows and checks local file bytes.
It cannot authenticate a run, provider, command, or platform. It always reports `evidence_verified: false`.
Local fixture tests, related regressions, Ruff, the frozen checker, and an offline installed wheel passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The historical archive charge remains 10,008,484,533 bytes. The package charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.21.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-EVIDENCE-NEXT-SESSION-2026-10-21.md).
Earlier dated entries remain historical records.

**October 21: The first Phase 3B local software checkpoint is complete.**
The [checkpoint record](PHASE-3B-LOCAL-LEDGER-CHECKPOINT-2026-10-21.md) covers the new read-only development ledger check.
It matches all 192 planned development rows to the frozen schedule and reports no verified evidence.
The local fixture tests, related acceptance tests, Ruff, and the frozen Phase 3A checker passed.
Mypy on the new script failed because that script and the imported frozen checker lack type annotations; Ruff passed.
No Linux test, guest action, archived tool execution, native turn, or evaluation row ran.
The 10,008,484,533-byte archive charge and 116,542,541-byte package charge remain unchanged.
The cumulative conservative charge remains 10,125,027,074 bytes.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.20.0`. Phase 3B acceptance remains open under ADR 0009.
Continue with the [next prompt](PHASE-3B-LOCAL-LEDGER-NEXT-SESSION-2026-10-21.md).
Earlier dated entries remain historical records.

**October 21: The owner stopped guest checks and requested local development only.**
The [boundary record](PHASE-3B-LOCAL-DEVELOPMENT-BOUNDARY-2026-10-21.md) records the completed host transport and one consumed clone start.
The clone suspended before the staging command was submitted. Do not resume it or submit the pending console line.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes further guest action.
Local synthetic tests, Ruff, the frozen Phase 3A checker, and the 249-file input check passed.
No Linux tests, archived tool execution, native turns, or evaluation rows ran in this boundary.
The historical archive charge is 10,008,484,533 bytes. The package charge is 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. Phase 3B acceptance remains open under ADR 0009.
The checkpoint version is `0.19.2`. Continue with the [next prompt](PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-21.md).
Earlier dated entries remain historical records.

**October 20: One exact offline toolchain staging attempt is approved.**
The owner replied, “Approve this exact attempt,” to the [proposal](PHASE-3B-OFFLINE-TOOLCHAIN-STAGING-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one host transport build and one isolated clone stage.
Recheck all 248 exact inputs, frozen custody, original guest hashes, source outputs, and host limits before the action.
Keep the clone network and sharing disconnected. Archived tool execution and evaluation remain closed.
The attempt has not started. Its result and new host allocation remain unknown.
The cumulative conservative network charge remains 10,125,027,074 bytes.
The checkpoint version is `0.19.1`. Continue this Phase 3B chat with the [next prompt](PHASE-3B-TOOLCHAIN-STAGING-APPROVED-NEXT-SESSION-2026-10-20.md).
Earlier dated entries remain historical records.

**October 20: A bounded offline toolchain staging decision is pending.**
The [proposal](PHASE-3B-OFFLINE-TOOLCHAIN-STAGING-PROPOSAL-2026-10-20.md) binds two pinned source manifests and one isolated clone stage.
The local transport script passed four synthetic tests, Ruff, and mypy. A read-only check matched both retained output trees.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no transport creation or guest action yet.
The clone is off with network and sharing disabled. Archived tool execution, Linux qualification, native turns, and evaluation remain closed.
The historical archive charge is 10,008,484,533 bytes. The package charge is 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. The checkpoint version is `0.19.0`.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-TOOLCHAIN-STAGING-DECISION-NEXT-SESSION-2026-10-20.md) and exact input index.
Earlier dated entries remain historical records.

**October 20: The approved offline Ubuntu package installation completed.**
The [completion record](PHASE-3B-OFFLINE-INSTALLATION-COMPLETION-2026-10-20.md) verifies one resume and one install.
APT returned exit zero. All 101 cached package versions match the installed versions.
The clone is off with network and sharing disabled. All 31 original guest files still match.
Host limits passed, and the [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes further guest action.
The cumulative conservative charge remains 10,125,027,074 bytes.
Archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.19`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-POST-INSTALLATION-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The owner approved one exact offline installation resume.**
The owner replied, “Approve this exact resume,” to the [proposal](PHASE-3B-OFFLINE-INSTALLATION-RESUME-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one saved-state resume and one offline install.
Recheck exact inputs, frozen custody, all 31 source guest hashes, host limits, and the guest package state.
Keep the clone network and sharing disconnected. Stop if the offline simulation changes.
The new network allowance is zero. The cumulative conservative charge remains 10,125,027,074 bytes.
Archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.18`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-OFFLINE-INSTALLATION-RESUME-APPROVED-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The approved offline installation stopped at VMware suspension.**
The [stop record](PHASE-3B-OFFLINE-INSTALLATION-SUSPEND-2026-10-20.md) closes one clone start before installation.
VMware suspended the clone at 16:54:29 local time. The agent did not issue the installation command.
The clone remains suspended with network and sharing disabled. Its package state is unobserved after suspension.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest action.
The [resume proposal](PHASE-3B-OFFLINE-INSTALLATION-RESUME-PROPOSAL-2026-10-20.md) needs a separate owner decision.
The historical 10,008,484,533-byte archive charge and 116,542,541-byte package charge remain intact.
The cumulative conservative charge remains 10,125,027,074 bytes.
Archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.17`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-OFFLINE-INSTALLATION-RESUME-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The owner approved one exact offline Ubuntu package installation.**
The owner replied, “Approve this exact installation,” to the [proposal](PHASE-3B-OFFLINE-PACKAGE-INSTALLATION-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one clone start and one cached-package install.
Recheck the exact inputs, frozen custody, all 31 source guest hashes, and host limits before starting.
Keep the clone network and sharing disconnected. Stop if the offline package simulation changes.
The new network allowance is zero. The cumulative conservative charge remains 10,125,027,074 bytes.
Archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.16`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-OFFLINE-INSTALLATION-APPROVED-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The approved storage-gated package retrieval completed.**
The [completion record](PHASE-3B-APT-STORAGE-RETRY-COMPLETION-2026-10-20.md) records one download-only command and verified cache.
All 101 package names, versions, and SHA-256 hashes matched guest candidate metadata.
The new conservative charge is 116,542,541 bytes. The historical charge remains 10,008,484,533 bytes.
The cumulative conservative charge is 10,125,027,074 bytes.
The clone is off with network and sharing disconnected. The original guest's 31 files still match.
No package was installed. The [offline installation proposal](PHASE-3B-OFFLINE-PACKAGE-INSTALLATION-PROPOSAL-2026-10-20.md) needs an owner decision.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest start or installation.
Archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.15`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-OFFLINE-INSTALLATION-DECISION-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The owner approved one storage-gated APT retry.**
The owner replied, “Approve this exact retry,” to the [exact proposal](PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one clone start and one download-only APT attempt.
The owner reported restored host space. Recheck the 68,719,476,736-byte host floor before start and network connection.
The previous attempt is closed. Keep network and sharing disabled until the offline preflight passes.
The unused conservative transfer allowance remains 167,772,160 bytes. The historical charge remains 10,008,484,533 bytes.
Installation, archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.14`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-APT-STORAGE-RETRY-APPROVED-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The isolated APT attempt stopped at the host storage floor.**
The [stop record](PHASE-3B-APT-ISOLATION-STORAGE-STOP-2026-10-20.md) closes one agent start and one owner reboot.
The isolated APT configuration showed no effective hooks. Both offline package lists matched 101 objects and 111,245,650 bytes.
The host had 41,177,645,056 free bytes before network connection, below the required 68,719,476,736 bytes.
The clone is off. Its network and sharing remain disabled. No download or installation occurred.
All 31 original guest files matched their custody manifest. The frozen Phase 3A checker passed.
The later host readback reached 151,635,742,720 free bytes. Recheck space before any start and network connection.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes the attempt and proposes no automatic retry.
The [exact retry proposal](PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md) needs a separate owner decision.
The historical 10,008,484,533-byte conservative charge remains unchanged. The unused 167,772,160-byte allowance was not charged.
Installation, archived tools, Linux qualification, native turns, and evaluation remain closed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.13`. The delivery revision is the commit containing this entry.
Continue this Phase 3B chat with the [next prompt](PHASE-3B-APT-STORAGE-RETRY-NEXT-SESSION-2026-10-20.md) and its exact input index.
Earlier dated entries remain historical records.

**October 20: The owner approved one isolated APT configuration attempt.**
The owner replied, “Approve this exact attempt,” to the [one-start proposal](PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits only its offline configuration checks and download-only APT attempt.
The clone is off with network and sharing disabled. Start it once after a clean, exact preflight.
Do not connect the adapter if any hook remains or the 101-object package list changes.
The unused conservative transfer allowance is 167,772,160 bytes. The historical charge remains 10,008,484,533 bytes.
The attempt has not started at this checkpoint. Its result and costs remain unknown.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
The checkpoint version is `0.18.12`. The delivery revision is the commit containing this entry.
Continue this Phase 3B session with the [next prompt](PHASE-3B-APT-CONFIG-APPROVED-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-APT-CONFIG-APPROVED-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The approved Ubuntu package retrieval stopped at configured hooks.**
The [completion record](PHASE-3B-PACKAGE-RETRIEVAL-HOOK-STOP-2026-10-20.md) records one clone start, offline checks, and shutdown.
The offline list still had 101 objects and 111,245,650 bytes.
The guest exposed APT and dpkg hooks, so the approved stop rule applied before network connection.
The clone is off. Its network and sharing remain disabled. All 31 original guest files still match.
The final clone allocation was 4,880,777,216 bytes. The host had 139,160,035,328 free bytes.
No package was retrieved or installed. Known new network charge, paid-host cost, and metered API cost were zero.
The historical 10,008,484,533-byte conservative charge remains unchanged.
The proposed 167,772,160-byte allowance was not used. The first attempt is closed.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits no further guest or network action.
The [isolated APT configuration proposal](PHASE-3B-APT-CONFIG-ISOLATION-PROPOSAL-2026-10-20.md) needs a separate owner decision.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.11`. The delivery revision is the commit containing this entry.
Continue Phase 3B with the [next prompt](PHASE-3B-APT-CONFIG-DECISION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-APT-CONFIG-DECISION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The owner approved one bounded Ubuntu package retrieval.**
The owner replied, “Approve this exact retrieval,” to the [one-start proposal](PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits only the proposal's clone start and download-only APT attempt.
Run the exact offline preflight before connecting the network adapter.
Keep sharing disabled. Disconnect the network adapter before shutdown.
The new conservative transfer allowance is 167,772,160 bytes. The historical charge remains 10,008,484,533 bytes.
The attempt has not started at this checkpoint. Its result and costs remain unknown.
Installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
The checkpoint version is `0.18.10`. The delivery revision is the commit containing this entry.
Continue this Phase 3B session with the approved retrieval.
Use the [next prompt](PHASE-3B-PACKAGE-RETRIEVAL-APPROVED-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-PACKAGE-RETRIEVAL-APPROVED-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: A bounded Ubuntu package retrieval decision is pending.**
The [proposal](PHASE-3B-UBUNTU-PACKAGE-RETRIEVAL-PROPOSAL-2026-10-20.md) requests one clone start and download-only APT.
It binds the offline list of 101 objects and 111,245,650 package bytes.
It proposes 167,772,160 bytes of additional conservative network charge, including overhead and stopped partial bodies.
The owner has not approved this new transfer scope at this checkpoint.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) keeps all action flags false.
The clone is off. Its network and sharing remain disabled.
The checkpoint version is `0.18.9`. The delivery revision is the commit containing this entry.
Continue Phase 3B with the owner's decision and the [next prompt](PHASE-3B-PACKAGE-RETRIEVAL-DECISION-NEXT-SESSION-2026-10-20.md).
Use the [exact inputs](PHASE-3B-PACKAGE-RETRIEVAL-DECISION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The approved offline package resolution capture completed.**
The session began at `b6c9db6` with a clean, pushed worktree.
All 217 exact entry inputs matched. The frozen Phase 3A checker passed.
The [completion record](PHASE-3B-OFFLINE-RESOLUTION-COMPLETION-2026-10-20.md) records commands, results, limits, costs, and shutdown.
The isolated Ubuntu clone showed four CPUs, 17,760,563,200 memory bytes, and 55,494,590,464 free guest bytes.
The offline APT list returned 101 package objects totaling 111,245,650 bytes. Its largest object was 18,708,214 bytes.
The clone is off. It uses 4,990,726,144 allocated host bytes. The host has 138,999,660,544 free bytes.
All 31 original guest files matched the private custody manifest. Network and sharing remain disabled.
No package was retrieved or installed. No archived tool, Linux test, native turn, or evaluation row ran.
Known network transfer, paid-host cost, and metered API cost were zero.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes this guest start.
Transfer, installation, Linux qualification, native turns, and evaluation need later exact decisions.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.8`. The delivery revision is the commit containing this entry.
Continue Phase 3B with the [next prompt](PHASE-3B-POST-RESOLUTION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-POST-RESOLUTION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The owner approved one offline package resolution capture.**
The owner replied, “Approve this exact capture,” to the [one-start proposal](PHASE-3B-OFFLINE-RESOLUTION-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one read-only start of the isolated clone.
Run only the proposal's commands after a clean worktree, exact input check, custody check, and host limit check.
The clone must keep network and sharing disabled. The owner must enter the password locally.
The attempt has not started at this checkpoint. Its result and costs remain unknown.
Package retrieval, installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
The checkpoint version is `0.18.7`. The delivery revision is the commit containing this entry.
Continue this Phase 3B session with the approved resolution capture.
Earlier dated entries remain historical records.

**October 20: The one approved offline Ubuntu package snapshot completed.**
The session began at `93b31fe` with a clean, pushed worktree.
The [completion record](PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-COMPLETION-2026-10-20.md) records commands, results, limits, costs, and shutdown.
The guest had four CPUs, 17,760,563,200 memory bytes, and 55,507,247,104 free guest bytes.
Its APT lists held 68 entries. The exact no-action package simulation completed without an error.
The full candidate table and transfer closure were not captured. Do not infer their sizes or completeness.
The clone is off. It uses 4,977,467,392 allocated host bytes. The host has 139,016,450,048 free bytes.
The 31 original guest files matched the private custody manifest. No package or archived tool ran.
Known network transfer, package retrieval, paid-host cost, and metered API cost were zero.
The single ledger closes further guest starts, transfer, installation, Linux qualification, native turns, and evaluation.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The checkpoint version is `0.18.6`. The delivery revision is the commit containing this entry.
Continue Phase 3B with the [next prompt](PHASE-3B-POST-SNAPSHOT-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-POST-SNAPSHOT-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The owner approved one offline Ubuntu package snapshot.**
The owner replied, “Approve this exact snapshot,” to the [one-start proposal](PHASE-3B-OFFLINE-PACKAGE-SNAPSHOT-PROPOSAL-2026-10-20.md).
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) admits one start of the powered-off separate clone.
Run only the proposal's read-only commands after a clean worktree and exact preflight.
The clone must keep its network and sharing disabled. The owner must enter the guest password locally.
The attempt has not started at this checkpoint. Its result and costs remain unknown.
Package retrieval, installation, Linux qualification, archived tools, native turns, and evaluation remain closed.
The checkpoint version is `0.18.5`. The delivery revision is the commit containing this entry.
Continue this same Phase 3B session with the approved snapshot. The prior 213-file index passed before this checkpoint.
Earlier dated entries remain historical records.

**October 20: The approved separate guest capacity attempt passed.**
The session began at `9e790ac` with a clean worktree and a pushed checkpoint.
The [completion record](PHASE-3B-SEPARATE-GUEST-CAPACITY-COMPLETION-2026-10-20.md) records one clone, one start, read-only capacity commands, and shutdown.
The owner selected a separate guest and approved the exact proposal in this Codex chat.
The clone showed Ubuntu 24.04.5 arm64, four CPUs, 17,760,559,104 memory bytes, and 55,519,887,360 free guest bytes.
The final clone allocation was 4,921,806,848 bytes. Combined allocation was 30,674,173,952 bytes.
The host had 139,072,647,168 free bytes. All approved storage limits passed.
Both historical guests remained unchanged. The clone is powered off with its network and sharing disabled.
The single ledger closes further guest starts, package work, Linux qualification, archived tool execution, and evaluation.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Known paid-host and metered API cost was USD 0. New network transfer was zero bytes.
The checkpoint version is `0.18.4`. The delivery revision is the commit containing this entry.
Use the [continuation prompt](PHASE-3B-POST-CLONE-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-POST-CLONE-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: Retained toolchain inventory readback is complete.**
The session began at `57cbae2` with a clean worktree.
The [completion record](PHASE-3B-TOOLCHAIN-READBACK-COMPLETION-2026-10-20.md) records read-only commands, results, costs, and limits.
All 16 archive sizes and hashes matched again. Their compressed bytes total 1,368,218,293.
Both output manifests bind 4,371,619,599 regular content bytes and 40 links.
Static file identification found AArch64 ELF candidates for Bun, Node, Swift, .NET, Codex, and Claude.
Installed executable hashes, effective commands, providers, and B1 conformance remain null.
The guest choice and exact clone approval remain pending. The single ledger admits no guest action.
No archive body request, guest, package install, archived tool, native turn, or evaluation row ran.
Known paid-host and metered API cost was USD 0. New network transfer was zero bytes.
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
The checkpoint version is `0.18.3`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-TOOLCHAIN-READBACK-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-TOOLCHAIN-READBACK-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The post-extraction guest admission review is complete.**
The session began at `aa8f19d` with a clean worktree.
The [review](PHASE-3B-POST-EXTRACTION-ADMISSION-REVIEW-2026-10-20.md) records source constraints, VMware custody, costs, and limits.
The TypeScript lock has 998 integrity entries. Python and .NET still need resolved dependency snapshots.
Swift has no external Swift package dependency. Ubuntu, CMake, and Ninja closures remain unbound.
Both historical VMware guests contain suspended-state files. Neither guest ran or changed in this review.
The Phase 3B VM and ISO use 25,752,367,104 allocated host bytes, above the dated 9,093,566,464-byte readback.
The [separate-guest proposal](PHASE-3B-SEPARATE-GUEST-CAPACITY-PROPOSAL-2026-10-20.md) defines one clone and capacity attempt.
The owner choice and exact approval remain pending. The single ledger keeps all guest flags false.
Both extraction attempts remain complete and closed. The original archives, receipts, charges, and Phase 3A custody remain intact.
Known paid-host and metered API cost was USD 0. No archive body, guest, package install, native turn, or evaluation row ran.
All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Phase 3B calibration and Phase 3C remain closed.
The checkpoint version is `0.18.2`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-GUEST-DECISION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-GUEST-DECISION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The owner-approved four-archive extraction completed in one attempt.**
The session began at `d440ae3eaeafc75c39745c2bf22e8909ba379aa1` with a clean worktree.
All 200 exact entry inputs matched their recorded sizes and SHA-256 values.
The [completion record](PHASE-3B-REMAINING-EXTRACTION-COMPLETION-2026-10-20.md) records commands, readback, costs, and limits.
The owner approved the exact one-image, one-attempt proposal in this Codex chat on October 20.
The output contains four selected IDs, 6,208 verified regular files, and 37 Swift links.
Regular content totals 3,859,951,638 bytes. The manifest SHA-256 is `4075234d7996789333e62cd082b7c408abed38a26d0fd5d3fff2de666f39e79d`.
The new image used 3,891,281,920 allocated bytes. Mounted free space was 2,331,660,288 bytes.
Both receipts, all 16 archives, both output manifests, and frozen Phase 3A checks passed.
The fixed image retained its logical size. Its allocation rose by 2,015,232 bytes for an unknown reason.
The single ledger records one completed attempt and closes further extraction.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No archive body request, guest, Linux test, native turn, provider request, or evaluation row ran.
Guest and VM growth was zero. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Installation, archived tool execution, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.18.1`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-POST-REMAINING-EXTRACTION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-POST-REMAINING-EXTRACTION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.

**October 20: The remaining-archive extractor passed local source acceptance.**
The session began at `e5a73c5c125476182910b938b0571dbe0c8039c9` with a clean worktree.
All 194 exact entry inputs matched their recorded sizes and SHA-256 values.
The [source checkpoint](PHASE-3B-REMAINING-EXTRACTOR-SOURCE-2026-10-20.md) records code, tests, read-only preflight, costs, and limits.
The four archives contain 7,216 members and 3,859,951,638 regular content bytes.
Swift has 37 recorded internal links. The `.NET SDK` has one leading `./` on its members.
Eleven new synthetic tests and 41 related tests passed. Ruff, strict mypy, and frozen Phase 3A checks passed.
Both receipts, all 16 archives, the fixed image, and the prior output manifest passed read-only custody checks.
The [new proposal](PHASE-3B-REMAINING-ARCHIVE-PROPOSAL-2026-10-20.md) binds one 6 GiB image and one extraction attempt.
The single admission ledger keeps new image creation and extraction false pending a separate exact owner decision.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No archive body request, guest, Linux test, native turn, provider request, or evaluation row ran.
Guest and VM growth was zero. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Installation, archived tool execution, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.18.0`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-REMAINING-EXTRACTION-DECISION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-REMAINING-EXTRACTOR-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.


**October 20: The owner-approved retained extraction completed in one attempt.**
The follow-up `0.17.2` checkpoint corrects stale live blockers in the single admission ledger.
The session began at `a3f48ead823ff2fe3a1b04a409753be7e380e849` with a clean worktree.
All 191 exact entry inputs matched their recorded sizes and SHA-256 values.
The owner approved the exact one-attempt decision in this Codex chat on October 19.
The [completion record](PHASE-3B-RETAINED-EXTRACTION-COMPLETION-2026-10-20.md) records the command, readback, costs, and limits.
The output contains twelve selected IDs, 11,019 verified regular files, and three recorded Node links.
The regular content totals 511,667,961 bytes. Final mounted free space exceeded the 536,870,912-byte floor.
Both receipts, all 16 archives, the fixed image, and frozen Phase 3A custody passed read-only checks.
The single admission ledger records one completed attempt and closes further extraction.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No archive body request, guest, Linux test, native turn, provider request, or evaluation row ran.
Guest and VM growth was zero. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Installation, archived tool execution, Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.17.2`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-POST-EXTRACTION-NEXT-SESSION-2026-10-20.md) and [exact inputs](PHASE-3B-POST-EXTRACTION-INPUTS-2026-10-20.json).
Earlier dated entries remain historical records.


**October 19: The bounded retained extractor passed local source acceptance.**
The session began at `2c19bf3ad11b2d3618e0e6eaef3e314ec90f52f1` with a clean worktree.
All 185 exact entry inputs matched their recorded sizes and SHA-256 values.
The [source checkpoint](PHASE-3B-RETAINED-EXTRACTOR-SOURCE-2026-10-19.md) records the extractor, tests, commands, costs, and limits.
The extractor binds twelve archive IDs, 511,667,961 regular content bytes, and a 536,870,912-byte free-space floor.
It binds the `.NET` path rule, three Node links, frozen source inventories, and four excluded archives.
Nineteen new synthetic tests and 22 related tests passed. Ruff, strict mypy, and the frozen Phase 3A checker passed.
Both receipts, all 16 archives, and the fixed image passed read-only custody checks.
The single admission ledger records the source candidate but keeps extraction admission false and its decision null.
The [separate decision proposal](PHASE-3B-RETAINED-EXTRACTION-DECISION-2026-10-19.md) defines one possible attempt.
No retained archive was extracted, installed, or executed. No URL was retried or requested again.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
Guest and VM allocation growth was zero. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.17.0`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-RETAINED-EXTRACTION-DECISION-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-RETAINED-EXTRACTOR-SOURCE-INPUTS-2026-10-19.json) after the owner resolves the separate decision.
Earlier dated entries remain historical records.

**October 19: A bounded retained archive extraction proposal is complete.**
The session began at `9a00dcff8c7505d465b44916a28a87b1333eaa1d` with a clean worktree.
All 182 exact entry inputs matched their recorded sizes and SHA-256 values.
Both receipts matched pinned SHA-256 values and passed read-only SQLite checks.
All 16 retained archive lengths and SHA-256 values matched their recorded values.
The fixed image retained its 3,221,225,472-byte logical size and 1,437,798,400-byte allocation.
The [proposal](PHASE-3B-RETAINED-EXTRACTION-PROPOSAL-2026-10-19.md) selects twelve archives with 511,667,961 regular content bytes.
It excludes four large archives and sets a 536,870,912-byte mounted free-space floor.
It binds `.NET` leading `./` normalization and three exact Node links. Swift remains excluded.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) records the proposal without admitting extraction.
No archive was extracted, installed, or executed. No URL was retried or requested again.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and both receipt histories remain intact.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
Known paid-host and metered API cost was USD 0. Subscription quota debit remains unknown.
No guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.16.3`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-RETAINED-EXTRACTION-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-RETAINED-EXTRACTION-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: Read-only retained archive inspection completed.**
The session began at `00e061ad161063470054c67efa87feaf2273b835` with a clean worktree.
All 178 exact entry inputs matched their recorded sizes and SHA-256 values.
Both receipts matched pinned SHA-256 values and passed read-only SQLite checks.
All 16 retained archives matched recorded lengths and SHA-256 values.
The fixed image retained its 3,221,225,472-byte logical size and 1,437,798,400-byte allocation.
Bounded metadata checks found 19,978 members and 4,371,619,599 regular content bytes.
The `.NET` tarballs contain 5,634 noncanonical `./` paths. Node and Swift contain 40 links.
No path escaped the archive root; no duplicate names, hard links, or special members appeared.
The [inspection record](PHASE-3B-RETAINED-ARCHIVE-INSPECTION-2026-10-19.md) records commands, limits, and each archive bound.
The [member report](PHASE-3B-RETAINED-ARCHIVE-MEMBERS-2026-10-19.json) records every link and exact metadata digests.
No archive was extracted or executed. No URL was retried or requested again.
The prior 8,589,934,592-byte and final 10,008,484,533-byte conservative charges remain intact.
No guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.16.2`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-RETAINED-ARCHIVE-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-RETAINED-ARCHIVE-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: The approved capped archive continuation completed its eight requests.**
The session began at `7d504534e74b1a4f2aea7557025df2c68c0d5cbe` with a clean worktree.
All 175 exact review inputs matched their recorded sizes and SHA-256 values.
The owner separately approved seven digest-bound requests and Swift signature-first verification in this Codex chat.
The new receipt bound manifest SHA-256 `7e2b17bfc9409d01d606ebae3f081dfe5305c10032b9fbd115bd6227a1d78ffc`.
Seven archives matched pinned digests. Swift passed pinned input hashes, key fingerprint, and detached-signature verification.
The new receipt passed SQLite integrity checks and retained eight successful attempts with no incomplete read.
Its SHA-256 is `01df021749e72c6aba7e309e603a815d83d66e7026161fab9c43cb2a8bd9cf37`.
The original receipt remains failed and halted with SHA-256 `9cd1b85273ca68a29d156a35556b7dbf0cc8944da8ec5db3e26c15812c1f93f4`.
No attempted URL was retried. All further body requests are closed.
The prior 8,589,934,592-byte and original 311,183,922-byte conservative charges remain intact.
The final cumulative conservative charge is 10,008,484,533 bytes under the 10,821,946,779-byte cap.
The image, retained archives, source inventories, and original failed `.NET SDK` receipt remain intact.
The [completion record](PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-COMPLETION-2026-10-19.md) records commands, results, costs, failures, and limits.
No archive was extracted or executed. No guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.16.1`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAPPED-ARCHIVE-COMPLETE-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAPPED-ARCHIVE-COMPLETE-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: The halted archive continuation is prepared for a separate owner decision.**
The session began at `901c46fefde60cb099f0cc383baf7bfc7e4051e6` with a clean worktree.
All 170 exact entry inputs matched their recorded sizes and SHA-256 values.
All 175 final continuation inputs matched their recorded sizes and SHA-256 values.
The mounted image and original receipt remain intact. The receipt SHA-256 still matches `9cd1b85273ca68a29d156a35556b7dbf0cc8944da8ec5db3e26c15812c1f93f4`.
It remains failed and halted. The retained SDK remains independently verified data, with no new attempt.
The new [review record](PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-REVIEW-2026-10-19.md) binds the separate transport, receipt, original scope, current ledger, eight IDs, quotas, commands, and stop rules.
The transport SHA-256 is `397c5647f8a74e05039b1e076fe4720b557533ee479aeb5327c78eea9fefbb76`.
Twelve new deterministic continuation tests pass. The original transport and extractor tests also pass.
Ruff, strict mypy, formatting, and the frozen Phase 3A checker pass.
Swift still lacks a trusted full archive digest. The review proposes pinned signature-first verification.
The key and detached signature paths are planned and currently absent. No Swift archive verification is claimed.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) keeps the new owner decision null and body admission false.
The prior 8,589,934,592-byte and current 311,183,922-byte conservative charges remain intact.
The original sixteen URLs, object caps, 2,232,012,187-byte stage cap, and zero guest growth remain unchanged.
No continuation receipt, selected archive body request, guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identity, B1 conformance, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.16.0`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAPPED-ARCHIVE-REVIEW-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAPPED-ARCHIVE-REVIEW-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: The halted archive continuation remains blocked after custody and digest review.**
The session began at `fd5fdf7332224c2d0d47d06ef2e6227a216dbf9b` with a clean worktree.
All 168 continuation inputs matched their recorded size and SHA-256.
The mounted image and original SQLite receipt remain intact. The receipt is halted and records the failed `.NET SDK` attempt.
The retained SDK file independently matched 204,124,866 bytes and its recorded SHA-512.
The receipt binds original script SHA-256 `79c547bcaecdd3ef85a1b4618cbb71b29f8fe28c93f2106380058c36079c14c4`.
The repaired script SHA-256 is `e67c93816da58c242880c631b6f436c75011cf098e317c7a29ca2f1edb104f91`.
Ten local tests, Ruff, strict mypy, and the frozen Phase 3A checker passed.
Official sources supplied Bun and .NET targeting pack checksum inputs. Swift still lacks a trusted full archive digest.
The [single admission ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) retains the original sixteen URLs and caps.
The prior 8,589,934,592-byte charge and the current 311,183,922-byte conservative charge remain intact.
The [continuation boundary](PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-BOUNDARY-2026-10-19.md) specifies a new receipt and transport plan.
That transport does not exist. The original receipt remains closed, and no new archive body request ran.
No guest, Linux test, native turn, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identity, B1 conformance, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.15.18`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAPPED-ARCHIVE-CONTINUATION-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: The owner-approved capped archive stage halted after a transport digest-parser failure.**
The session began at `f11e1b40b63d8b4e33a3b321a421a1293c231598` with a clean worktree.
All 164 continuation inputs matched their recorded size and SHA-256.
The owner approved the exact sixteen-URL stage in this chat.
Four source archives and three tool archives passed their recorded size and trusted digest checks.
The frozen extractor matched all four source inventories.
The `.NET SDK` transfer retained 204,124,866 bytes and independently matched its recorded SHA-512.
The original transport misread hexadecimal SHA-512 as Base64 and recorded a failed attempt.
The receipt remains halted; no further archive body request is admitted under this grant.
The repaired parser passed ten local tests, Ruff, and strict mypy.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Actual archive bodies totaled 260,852,274 bytes. The full reserve makes the conservative new charge 311,183,922 bytes.
The prior 8,589,934,592-byte charge remains intact; cumulative conservative charge is 8,901,118,514 bytes.
The retained local image and receipt remain outside Git. The guest and VM allocations did not change.
The [halted boundary](PHASE-3B-CAPPED-ARCHIVE-HALTED-2026-10-19.md) records commands, results, costs, failures, and limits.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native baselines, provider identity, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.15.17`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAPPED-ARCHIVE-HALTED-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAPPED-ARCHIVE-HALTED-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: A capped archive evidence stage is ready for one owner scope decision.**
The session began at `692eaecd93ddb66d9e9aa918f4c403e26979c88b` with a clean worktree.
All 162 continuation inputs matched their recorded size and SHA-256.
Four npm tarball HEAD responses returned HTTP 200 without compressed byte counts.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now defines a sixteen-URL evidence stage.
The [stage proposal](PHASE-3B-CAPPED-ARCHIVE-STAGE-2026-10-19.md) caps new transfer at 2,232,012,187 bytes.
It caps retained logical data at 3,221,225,472 bytes and permits zero guest or VM allocation growth.
Owner approval and verified transport and storage controls remain mandatory before retrieval.
The full campaign remains blocked by unverified archives, Ubuntu and repository closures, and operational inputs.
No archive body, guest, Linux test, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, native baselines, provider identity, Phase 3B calibration, and Phase 3C remain closed.
The checkpoint version is `0.15.16`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAPPED-ARCHIVE-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAPPED-ARCHIVE-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: Exact campaign batch closure remains blocked after Ubuntu and npm metadata review.**
The session began at `779b2c17c23fa6bc3f6f0b4edd53ea3b10df9a7d` with a clean worktree.
All 159 continuation inputs matched their recorded size and SHA-256.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now records exact official package metadata for CMake and Ninja.
Ten tool package or archive counts and four source archive counts give a 1,118,368,549-byte prospective lower bound.
Four npm tarballs still lack exact compressed counts. Safe archives, extraction bounds, Ubuntu closure, and repository closures remain unbound.
The old transfer allowance has zero conservative remaining balance.
Changed RAM, infrastructure, retained-data, and transfer rules remain unapproved.
No exact transfer, retained-data, or guest-disk upper bound supports a changed-limit request.
No selected source archive, artifact body, guest, Linux test, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identity, native baselines, Phase 3B calibration, and Phase 3C remain closed.
The [latest boundary](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-METADATA-BOUNDARY-2026-10-19.md) records commands, results, costs, failures, and limits.
The checkpoint version is `0.15.15`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-CONTINUATION-2026-10-19.md) and [exact inputs](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-METADATA-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: Exact campaign batch closure remains blocked after read-only metadata checks.**
The session began at `b5259f2505b74c4059ee72940463e18fa357d2a0` with a clean worktree.
All 156 continuation inputs matched their recorded size and SHA-256.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) now binds eight tool archive byte counts and four source archive byte counts.
The prospective archive subtotal is 1,107,938,715 bytes, which is only a lower bound.
Four npm tarballs and CMake/Ninja packages still lack exact byte counts.
Safe archive inventories, extraction bounds, Ubuntu packages, and repository dependency closures remain unbound.
No selected source archive was accessed. Three network-denied synthetic extractor tests passed.
The old transfer allowance has zero conservative remaining balance.
Changed RAM, infrastructure, retained-data, and transfer rules remain unapproved.
No exact transfer, retained-data, or guest-disk upper bound supports a changed-limit request.
No guest, Linux test, artifact body, installation, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux qualification, provider identity, native baselines, Phase 3B calibration, and Phase 3C remain closed.
The [latest boundary](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-BLOCKED-2026-10-19.md) records commands, results, costs, failures, and limits.
The checkpoint version is `0.15.14`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAMPAIGN-BATCH-CLOSURE-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 19: Consolidated Linux campaign admission remains blocked after local binding.**
The session began at `9678937b5f92cc7f9721d441fea7e86ba25a26f7` on `codex/phase1-architecture` with a clean worktree.
All 149 source-ready indexed file hashes matched.
The frozen checker passed with 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The [campaign manifest](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) binds four source archive identities and records unresolved toolchain, dependency, launch, and resource bounds.
The source extractor and B1 manual script have exact source bytes but no archive or native conformance result.
Three network-denied local extractor tests passed with synthetic archives.
The old transfer allowance has zero conservative remaining balance.
The proposed RAM, infrastructure, retained-data, and transfer changes remain unapproved.
No changed-limit approval request was made because the exact batch lacks a transfer and retained-data upper bound.
No guest, Linux test, Linux artifact retrieval, provider request, Jev call, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux conformance, provider identities, native baselines, Phase 3B calibration, and Phase 3C remain closed.
The [boundary record](PHASE-3B-CAMPAIGN-ADMISSION-BOUNDARY-2026-10-19.md) gives commands, results, costs, failures, and limits.
The checkpoint version is `0.15.13`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-CAMPAIGN-ADMISSION-NEXT-SESSION-2026-10-19.md) and [exact inputs](PHASE-3B-CAMPAIGN-ADMISSION-INPUTS-2026-10-19.json).
Earlier dated entries remain historical records.

**October 18: Core source work is ready for consolidated Linux campaign admission.**
The session began at `e314651` on `codex/phase1-architecture` with a clean worktree.
All 146 entry-index file hashes matched.
The selected Mac source suite passed 196 tests through the production coordinator path.
The fresh offline wheel passed the same 196 tests with network access denied.
All 49 installed source files matched the checkout.
The frozen checker retained 23 artifacts, 768 planned units, and digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
Ruff and strict mypy passed. Linux-specific acceptance modules remain deferred.
The accepted plan has no further core source milestone before Phase 3B admission.
The [source-ready record](PHASE-3B-SOURCE-READY-2026-10-18.md) gives local commands, results, costs, failures, and limits.
The [consolidated campaign plan](PHASE-3B-CONSOLIDATED-LINUX-CAMPAIGN-2026-10-18.md) binds known inputs and records unresolved admission work.
The old transfer allowance has zero conservative remaining balance. Proposed limit amendments remain unapproved.
No guest, Linux test, provider request, or evaluation row ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
Linux conformance, native baseline results, and resolved provider identities remain unknown.
Phase 3B calibration and Phase 3C have not started. The checkpoint version is `0.15.12`.
The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-SOURCE-READY-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-SOURCE-READY-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: The owner restored local Mac development before Linux testing.**
The session began at `7dca8e8b134d5304ff6fa2c8952257dce7903cc3` on `codex/phase1-architecture` with a clean worktree.
The owner stopped Linux tests during development and directed local machine development.
[ADR 0009](decisions/0009-local-development-before-consolidated-linux-testing.md) records the active order.
Complete remaining source work with local deterministic checks before one consolidated Linux test campaign.
Do not operate either VMware guest, retrieve Linux artifacts, or run Linux qualification during development.
The previous Phase 3B toolchain prompt is a dated record, not the active next session.
The guest, ISO, transfer ledger, proposed limit amendments, and unknown installer traffic remain unchanged.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
No Linux conformance, provider identity, native baseline, or calibration result was established.
Phase 3B calibration and Phase 3C remain closed.
The [order record](PHASE-3B-LOCAL-DEVELOPMENT-ORDER-2026-10-18.md) supplies commands, results, costs, and limits.
The checkpoint version is `0.15.11`. The delivery revision is the commit containing this entry.
Use the [local development prompt](PHASE-3B-LOCAL-DEVELOPMENT-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-LOCAL-DEVELOPMENT-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B toolchain amendment remains blocked after a second read-only review.**
The session began at `2d627c7f4985801a3b65fe497514e5f226fdf6fd` on `codex/phase1-architecture` with a clean worktree.
All 138 starting public input hashes matched.
The inspected host log and guest console did not establish an exact installer transfer bound.
The guest interface returned `noWindowsAvailable` during further read-only checks.
Charge the prior 8 GiB transfer allowance in full. Its conservative remaining balance is zero.
The [candidate manifest](PHASE-3B-LINUX-ARM64-TOOLCHAIN-MANIFEST-2026-10-18.json) records fourteen artifacts and marks missing admission fields unknown.
The host currently reports 9,093,566,464 allocated bytes for the new VM bundle and ISO directory together.
The proposed 16 GiB guest-visible RAM rule, 40 GiB infrastructure ceiling, and 16 GiB cumulative transfer ceiling need owner approval.
The [current boundary](PHASE-3B-TOOLCHAIN-AMENDMENT-BOUNDARY-2026-10-18.md) gives exact ledgers, results, costs, failures, and limits.
No guest setting, network connection, retrieval, installation, provider request, or calibration changed.
All 192 development rows remain planned. All 576 sealed rows remain unexposed. Operational admission and Phase 3C remain closed.
The checkpoint version is `0.15.10`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-TOOLCHAIN-AMENDMENT-CONTINUATION-2026-10-18.md) and [exact inputs](PHASE-3B-TOOLCHAIN-AMENDMENT-CONTINUATION-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B toolchain amendment remains blocked after official artifact review.**
The session began at `7a592dd6d1f47fc98651b44e18edb05feab7c7b7` on `codex/phase1-architecture` with a clean worktree.
The frozen checker passed with 23 artifacts, 768 planned units, and content digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
All 135 starting file hashes matched.
The known ISO and checksum consumed 3,825,518,142 bytes of the approved 8 GiB transfer limit.
The installer's rounded fetch summaries do not bound its exact transfer.
Charging the unknown prior amount against the full remaining balance leaves zero bytes for new retrieval.
The host reported 5,268,045,824 allocated bytes for the new VM bundle alone.
Official RTK and .NET digests, Bun checksum-manifest availability, and Swift direct dependencies are now recorded.
Exact archive sizes, extraction bounds, transitive dependencies, and executable hashes remain missing.
The proposed guest-visible RAM threshold and separate infrastructure ledger still require owner approval.
The guest network remains disconnected. No setting, installation, provider request, or calibration changed.
No Jev call ran. All 192 development rows remain planned, and all 576 sealed rows remain unexposed.
Operational admission and Phase 3C remain closed.
The source checkpoint version is `0.15.9`. The delivery revision is the commit containing this entry.
Use the [checkpoint](PHASE-3B-TOOLCHAIN-AMENDMENT-CHECKPOINT-2026-10-18.md), [next prompt](PHASE-3B-TOOLCHAIN-AMENDMENT-NEXT-SESSION-2026-10-18.md), and [exact inputs](PHASE-3B-TOOLCHAIN-AMENDMENT-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B toolchain preparation amendment remains incomplete.**
The session began at `76980c7b8837da63b8c17e0b1fa1535893bfa39e` on `codex/phase1-architecture` with a clean worktree.
The frozen checker again passed with 23 artifacts, 768 planned units, and content digest `4bd188deb0089a79d018ed13b2fd2467927a53efc4d3d4e323f8cf43bdc892c0`.
The separate Ubuntu guest remains disconnected. Installer logs show rounded `Fetched 393 kB` and `Fetched 292 MB` summaries.
These summaries do not provide an exact upper bound for the installer transfer.
The guest's 16,728,174,592 visible memory bytes remain below 16 GiB. Selected tools remain absent or different.
The [blocked amendment draft](PHASE-3B-TOOLCHAIN-PREPARATION-BLOCKED-2026-10-18.md) proposes an exact visible-memory threshold and separate VM-plus-ISO ledger.
The proposed storage interpretation needs owner approval. Artifact digests, byte counts, dependency sets, and commands remain incomplete.
No guest settings, network connection, tool installation, provider request, or calibration changed.
The prior qualification and batch-limit approvals remain in force. No Jev paid call ran.
All 192 development rows remain planned. All 576 sealed rows remain unexposed. Operational admission and Phase 3C remain closed.
The source checkpoint version is `0.15.8`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-TOOLCHAIN-PREPARATION-NEXT-SESSION-2026-10-18.md) and [exact input index](PHASE-3B-TOOLCHAIN-PREPARATION-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B guest readback blocks operational admission.**
The session began at `c421624` on `codex/phase1-architecture` with a clean worktree.
The owner unlocked the Mac and signed in to the separate Ubuntu guest without sharing the password.
The guest reported Ubuntu 24.04.5, Linux arm64, four online CPUs, and 55,538,384,896 bytes free on `/var/tmp`.
The 16 GiB VM configuration yielded 16,728,174,592 guest-visible memory bytes.
RTK, Node.js, Bun, Swift, .NET, CMake, Ninja, Codex CLI, and Claude Code CLI were absent.
Installed Python 3.12.3 differs from the selected 3.12.15.
The approved proposal says to stop on an absent or different selected tool.
The [readback record](PHASE-3B-GUEST-CAPACITY-READBACK-BLOCKED-2026-10-18.md) gives exact commands, results, costs, and limits.
The guest network remains disconnected. No installation, dependency retrieval, provider request, or calibration ran.
The previous 8 GiB guest remains under owner control. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. Operational admission and Phase 3C stay closed.
The source checkpoint version is `0.15.7`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-GUEST-CAPACITY-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-GUEST-CAPACITY-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Separate Phase 3B guest installed; login and accounting block readback.**
The session began at `31b7e8a` on `codex/phase1-architecture` with a clean worktree.
The owner completed the new Ubuntu account profile without sharing the password.
The installer completed, and the guest reached its login prompt after reboot.
The guest network and installation media are disconnected in VMware Fusion.
The owner must sign in before the guest's capacity and control checks can run.
The Mac locked during this checkpoint. The owner must unlock it before VMware inspection resumes.
The installer's security-update transfer is unknown. Further retrieval remains stopped.
The VM bundle and ISO directory together occupy 9,041,420,288 host bytes.
That amount exceeds 8 GiB if both items fall under the approved retained-data limit.
The [boot record](PHASE-3B-GUEST-BOOT-BLOCKED-2026-10-18.md) gives commands, results, limits, and unknowns.
No coding-runtime turn or evaluation provider request ran. All 192 development rows remain planned.
All 576 sealed rows remain unexposed. Operational admission and Phase 3C stay closed.
The source checkpoint version is `0.15.6`. The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-GUEST-BOOT-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-GUEST-BOOT-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Separate Phase 3B guest awaits owner account entry.**
The session began at `90e7aa1` on `codex/phase1-architecture` with a clean worktree.
The approved Phase 3B limits and qualification authority remain in force.
The owner took responsibility for the previous 8 GiB VMware guest.
A separate, nonshared Ubuntu arm64 guest has four virtual CPUs, 16 GiB RAM, and a 64 GB disk.
Its official Ubuntu Server 24.04.5 arm64 ISO matched the published SHA-256 digest.
The installer selected a 62.948 GB ext4 root layout and reached Profile configuration.
The owner must enter and submit the new account credentials under the computer-use handoff rule.
Guest free disk, toolchains, native controls, provider identities, dependencies, baselines, and calibration remain unverified.
The [guest record](PHASE-3B-GUEST-PREPARATION-2026-10-18.md) gives exact commands, results, costs, failures, and limits.
No development row or coding-runtime submission ran. All 576 sealed rows remain unexposed.
Operational admission and Phase 3C stay closed. The source checkpoint version is `0.15.5`.
The delivery revision is the commit containing this entry.
Use the [next prompt](PHASE-3B-GUEST-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-GUEST-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B limits approved; local guest capacity blocks preparation.**
The session began at `1bdb65f` on `codex/phase1-architecture` with a clean worktree.
The owner separately answered "Yes, resume qualification" and "Approve limits and unknown quota" against the exact proposal.
The approved Phase 3B batch has USD 0 metered billing, USD 0 paid hosts, and 256 turns per runtime.
It has a USD 200 API-equivalent planning limit and 8 GiB download and retention limits.
Actual subscription quota debit remains unknown and was explicitly accepted. No hard quota ceiling was proved.
The selected local VMware Ubuntu VM was powered off and configured with 8 GiB RAM.
The approved proposal requires 16 GiB before preparation. No guest startup or qualification occurred.
The frozen package checker passed with 23 artifacts and 768 planned units.
All 124 files in the previous continuation index matched byte counts and SHA-256 digests.
The focused offline suite passed 108 tests on macOS 27.2 arm64 with Python 3.12.15.
The [capacity record](PHASE-3B-ADMISSION-CAPACITY-BLOCKED-2026-10-18.md) gives exact commands, results, costs, and limits.
No dependency preparation, credential access, native runtime turn, provider inference, calibration, or sealed exposure occurred.
Phase 3B calibration remains incomplete. Operational admission and Phase 3C stay closed.
The source checkpoint version is `0.15.4`; the delivery revision is the commit containing this entry.
Use [the next prompt](PHASE-3B-ADMISSION-CAPACITY-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-ADMISSION-CAPACITY-INPUTS-2026-10-18.json).
Earlier dated entries remain historical records.

**October 18: Phase 3B admission proposal published; calibration remains closed.**
The session began at `9deb7d476615c4f3016acedd0e0c0160ffab08b6` on `codex/phase1-architecture`.
The worktree was clean at entry. All 120 files in the Phase 3B starting index matched their byte counts and SHA-256 digests.
The read-only frozen-package checker passed with 23 artifacts and 768 planned units.
The focused offline suite passed 108 tests. These checks did not run a coding runtime or provider.
The [verification record](PHASE-3B-ADMISSION-VERIFICATION-2026-10-18.md) lists exact commands, environment, results, costs, and limits.
The [Phase 3B admission proposal](PHASE-3B-ADMISSION-PROPOSAL-2026-10-18.md) names the four development repositories, twelve tasks, 192 rows, commands, dependencies, limits, and cleanup.
The proposal requests USD 0 metered billing, USD 0 paid hosts, at most 256 turns per selected runtime, and a USD 200 API-equivalent planning limit.
Actual service quota debit remains unknown. No hard provider quota control has been proved.
The owner has not approved the proposal or explicitly resumed platform and live qualification.
No dependency preparation, credential access, native runtime turn, calibration, sealed task exposure, or paid operation occurred.
Phase 3B calibration remains incomplete. Operational admission stays closed.
The source checkpoint version is `0.15.3`; the delivery revision is the commit containing this entry.
Use [the continuation prompt](PHASE-3B-ADMISSION-NEXT-SESSION-2026-10-18.md) and [exact inputs](PHASE-3B-ADMISSION-INPUTS-2026-10-18.json).
Stop before Phase 3C or sealed evaluation. Earlier dated entries remain historical records.

**October 18: Phase 3A complete; the source evaluation package is frozen.**
The owner approved agent annotation, delegated bounded selections, and selected zero evaluation spending.
The package retains twelve pinned repositories, all four stacks, independent annotations, and attributed adjudication.
It fixes 24 development tasks and 24 sealed task commitments under separate custody.
B0, B1, B2, P, both role assignments, thresholds, accounting, and 768 planned units are fixed.
Accepted ADR 0008 separates package acceptance from deferred native and platform qualification.
Operational admission stays closed. Phase 3B execution requires separate approval and qualified controls.
No calibration or sealed evaluation ran. Earlier dated entries remain historical records.
The source checkpoint version is `0.15.2` on `codex/phase1-architecture`.
The delivery revision is the commit containing this entry and the completion report.
Use [the completion report](PHASE-3A-COMPLETION-2026-10-18.md) and [verification record](qualification/phase-3a-freeze-verification-20261018.json).
Continue with [the Phase 3B prompt](PHASE-3B-NEXT-SESSION-2026-10-18.md) and [exact input index](PHASE-3B-INPUTS-2026-10-18.json).
Complete publication, then stop before Phase 3B work.

**October 16: Phase 3A preparation checkpoint; freeze blocked.**
The proposed package records 12 pinned public corpus candidates and preserves all four stacks.
It defines B0, B1, B2, P, both role assignments, task contracts, independent annotation, protocol proposals, and separate usage categories.
Fourteen fresh offline tests check package integrity and refusal behavior through existing interfaces.
Owner decisions, independent annotations, sealed task commitments, exact live identities, baseline conformance, and spending approval remain missing.
Operational execution admission remains closed. Phase 3A remains incomplete, and Phase 3B has not started.
Use [the package](evaluation/phase-3a/README.md), [owner decisions](PHASE-3A-OWNER-DECISIONS-2026-10-16.md), and [continuation prompt](PHASE-3A-CONTINUATION-2026-10-16.md).
See [the preparation report](PHASE-3A-PREPARATION-2026-10-16.md) for verification and limitations.
Earlier dated status entries remain historical records.

The source checkpoint version is 0.15.1 on `codex/phase1-architecture`.
The delivery revision is the commit containing this entry and the Phase 3A preparation report.
Continue this same milestone with [the exact input index](PHASE-3A-CONTINUATION-INPUTS-2026-10-16.json).
Stop after the standing branch publication ceremony.

**October 16: Phase 2E software complete; platform and live qualification deferred.**
Both runtime role assignments pass deterministic external fixtures through the production coordinator.
The second adapter uses existing candidate capture, SQLite state, checks, evidence, and verdict rules.
Required review enforces resolved provider independence and the same confirmed project model.
Risk gates preserve planning approval, actual scope escalation, human conflict decisions, and fresh remediation evidence.
Source and installed-wheel suites each pass 1,305 test occurrences, including 57 Phase 2E methods.
All 49 packaged source files match the checkout.
Operational execution admission remains closed.
See [the completion report](PHASE-2E-SOFTWARE-COMPLETION-2026-10-16.md) and [verification](qualification/phase-2e-software-verification-20261016.json).
Phase 3A prepares the comparative evaluation package in a separate session.
Use [its prompt](PHASE-3A-NEXT-SESSION-2026-10-16.md) and [exact input files](PHASE-3A-INPUTS-2026-10-16.json).
No Phase 3A implementation or evaluation occurred.
Earlier dated status entries remain historical records.

The source checkpoint version is 0.15.0 on `codex/phase1-architecture`.
The delivery revision is the commit containing this entry and the Phase 2E completion report.
Stop after the standing branch publication ceremony.

**October 16: Phase 2D software complete; platform and live qualification deferred.**
The coordinator workflow passes fresh deterministic external runtime and validator fixtures.
Checked request preparation verifies the confirmed model, task, approval, configuration, scope, and initial candidate.
Atomic validator capture resolves approved definitions and checks the frozen candidate before and after persistence.
Existing collection, normalization, claims, evidence, verdict, and recovery code remain the production path.
Both complete source and fresh installed-wheel suites pass 1,248 occurrences, including 26 new core tests.
The suite contains 1,232 unique methods and 16 existing repeated occurrences.
All 47 packaged source files match; lint, strict typing, source formatting, and CLI help pass.
Nine historical script format differences remain byte-identical to session start.
[The completion report](PHASE-2D-SOFTWARE-COMPLETION-2026-10-16.md) and [verification record](qualification/phase-2d-software-verification-20261016.json) supply exact evidence and limitations.
The source checkpoint version is 0.14.0 on `codex/phase1-architecture`.
Its delivery revision is the commit containing this entry and the completion report.
Operational execution admission remains closed; platform and live qualification remain deferred.
No Linux implementation bytes changed during this session.
No platform operation, credential access, provider call, paid host, merge, deployment, or registry publication occurred.
Phase 2E implementation has not started.
Use [the Phase 2E prompt](PHASE-2E-NEXT-SESSION-2026-10-16.md) and [exact input index](PHASE-2E-INPUTS-2026-10-16.json) next.
Stop after the standing branch publication ceremony.
Earlier dated status entries remain historical records.

**October 15: Phase 2D is active and unblocked for core software development.**
The owner instructed continued development under the plan and explicitly unblocked Phase 2D.
[Accepted ADR 0007](decisions/0007-core-development-before-platform-qualification.md) separates software acceptance from deferred platform and live qualification.
The active milestone completes the first-runtime integration and platform-independent coordinator workflow through existing interfaces.
Exercise actual production code with deterministic external runtime and validator fixtures.
[The revised plan](DEVELOPMENT-PLAN.md) defines the observable software acceptance conditions.
[The current next-session prompt](PHASE-2D-CORE-NEXT-SESSION-2026-10-15.md) directs implementation and verification.
[The input index](PHASE-2D-CORE-INPUTS-2026-10-15.json) lists exact starting files and preparation hashes.

Do not resume Linux adapter development, VMware or SSH operations, compiler attempts, or the exception sequence.
The unused v29 approval remains inactive.
Keep operational execution admission closed and preserve all existing evidence and custody.
Platform and live qualification remain deferred requirements for operational use and support claims.
Their missing evidence does not block the revised Phase 2D software checkpoint or subsequent source development.
After software acceptance, update the required publication files, commit, push the current branch, and stop before Phase 2E.
Use the completion status "Phase 2D software complete; platform and live qualification deferred" only after the software checks pass.

No production code, operational gate, or historical result changed for this prompt preparation.
The preceding source and installed suites each passed 1222 occurrences; these remain dated baseline results.
Base revision remains `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc` on `codex/phase1-architecture`.
The dirty candidate remains unreleased `0.13.0`.
Earlier entries that defer the whole milestone are superseded by this instruction.

**October 15: The owner stopped Linux work and moved core completion before platform adaptation.**
Stop the repeated Linux exception sequence and all further Linux adapter development.
The owner approved v29, then gave this newer change of direction before any v29 operation started.
Do not execute the unused v29 approval without a later explicit instruction to resume.
[The direction record](CORE-COMPLETION-DIRECTION-2026-10-15.md) governs the revised work order.
[The current prompt](CORE-COMPLETION-NEXT-SESSION-2026-10-15.md) starts bounded core completion work.
The next milestone uses existing interfaces and deterministic fixtures to complete the platform-independent coordinator workflow.
Linux, macOS, and Windows qualification follow core completion.
Operational execution admission remains closed.
Phase 2D remains incomplete and deferred; no supported-platform or live acceptance claim follows.

The v29 approval file and consumed-operation markers do not exist.
No v29 upload, preparation, compiler, observer, authentication, or live turn started.
Forwarding remains zero from the last exact restoration.
The shared retention parent remains at its approved 2 GiB limit.
Preserve the twenty-three recorded charges, remaining original custody, private artifacts, and all historical unknowns.
This direction authorizes no VM shutdown or retained-object removal.
Both latest offline suites pass 1222 occurrences; no source changed for this direction record.
No commit, push, release, deployment, or Phase 2E implementation occurred.
Earlier continuation and approval statements below are dated history.

**October 15: Revision readback passes; the kernel rejects the userspace policy compression header.**
The owner approved exact v28, and it ran once.
Observer `30031` passes revision readback and the absent-profile check.
The policy write returns errno `93`; the kernel reports "invalid profile format" for child `30201`.
The retained stdout output contains four userspace compression containers.
The pinned parser emits raw serialized policy when its compression level is `none`.
The new recipe requires exactly one `--zstd-compress-level=none` and rejects missing, duplicate, or conflicting options.
Direct add-only loading and exact source-to-binary-to-export checks remain unchanged.
A read-only diagnostic decodes the historical containers to 37154 bytes, below the existing one-MiB output ceiling.
No diagnostic executes a compiler, loads policy, or reuses old output for admission.
All 69 focused checks and both fresh 1222-test suites pass.
All 47 installed package files match source.
Actual new compilation and policy loading remain unverified.
[The exact v29 proposal](PHASE-2D-RAW-POLICY-CONTINUATION-2026-10-15.md) requires separate approval for another attempt.
[The exact record](qualification/phase-2d-executable-batch-v29-20261015.json) binds all commands and inputs.
[The current prompt](PHASE-2D-RAW-POLICY-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Twenty-three full charges remain retained under 184 GiB combined logical and allocated reservations each.
All twenty-three charge snapshots and twenty remaining original journal FD identities pass read-only checks.
Keep the approved shared retention parent at 2 GiB.
Individual batches keep 768 MiB, and observers keep 128 MiB.
The latest batch and observer record zero memory-limit events.
Shared OOM counters retain their accepted historical values.
The historical loss of observer `24610` and timer `24612` remains accepted under v26.
Reconstruct no lost proof or physical release.
Forwarding is zero after the exact restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No v29 guest operation, commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.

**October 15: Policy opening passes; the AppArmor revision interface requires its existing event reader.**
The owner approved exact v27, and it ran once.
Observer `29199` passes policy opening, then its child reports `BlockingIOError` at frozen `admission.py:157`.
The failure precedes policy loading.
A fresh read-only probe returns revision `269`, then `EAGAIN`.
The existing AppArmor reader handles this interface correctly on the actual VM.
All four operational revision sites now use that existing reader.
The generic proc reader remains unchanged, and revision comparisons remain required.
All 41 focused checks and both fresh 1220-test suites pass.
All 47 installed package files match source.
Actual policy loading remains unverified.
[The exact v28 proposal](PHASE-2D-APPARMOR-REVISION-CONTINUATION-2026-10-15.md) requires separate approval for another attempt.
[The exact record](qualification/phase-2d-executable-batch-v28-20261015.json) binds all commands and inputs.
[The current prompt](PHASE-2D-APPARMOR-REVISION-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Twenty-two full charges remain retained under 176 GiB combined logical and allocated reservations each.
All twenty-two charge snapshots and nineteen remaining original journal FD identities pass read-only checks.
Keep the approved shared retention parent at 2 GiB.
Individual batches keep 768 MiB, and observers keep 128 MiB.
The latest batch and observer record zero memory-limit events.
Shared OOM counters retain their accepted historical values.
The historical loss of observer `24610` and timer `24612` remains accepted under v26.
Reconstruct no lost proof or physical release.
Forwarding is zero after the exact restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No v28 guest operation, commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.

**October 15: Fixture preparation returns; policy opening loses the retained mount context.**
The owner approved exact v26, and it ran once.
Observer `28259` passes storage-owner readback and returns from fixture preparation before policy opening.
The policy opener then raises `FileNotFoundError` at frozen `linux_operational.py:585`.
Read-only retained-frame inspection identifies `readonly-root` as the missing path component.
The original projected root FD contains the expected policy bytes, but its mount path is absent in the observer namespace.
The correction walks each canonical policy component relative to the retained projected-root FD.
No-follow flags, root ownership, outside-write refusal, inventory verification, and original deadlines remain required.
All eleven focused checks and both fresh 1218-test suites pass.
All 47 installed package files match source.
Actual policy loading remains unverified.
[The exact v27 proposal](PHASE-2D-RETAINED-POLICY-CONTINUATION-2026-10-15.md) requires separate approval for another attempt.
[The exact record](qualification/phase-2d-executable-batch-v27-20261015.json) binds every command and input.
[The current prompt](PHASE-2D-RETAINED-POLICY-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Twenty-one full charges remain retained under 168 GiB combined logical and allocated reservations each.
All twenty-one charge snapshots and eighteen remaining original journal FD identities pass read-only checks.
The shared retention parent now has its approved persistent 2 GiB memory limit.
Individual batches keep 768 MiB, and observers keep 128 MiB.
The new batch and observer record zero memory-limit events.
Shared OOM counters retain their accepted historical values; no additional OOM event occurred.
The historical loss of observer `24610` and timer `24612` remains accepted under v26.
Reconstruct no lost proof or physical release.
All prior charges, remaining original custody, outputs, counters, clocks, and unknowns remain retained or historically recorded.
Forwarding is zero after the exact restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No v27 guest operation, commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.

**October 15: Storage-owner readback passes; fixture startup expires, and shared retention records an OOM custody loss.**
The owner approved exact v25, and it ran once.
Observer PID `27007` passes initial storage-owner readback.
Fixture preparation then expires at its original shared creation deadline, 32.460042 seconds after the startup journal entry.
Retained production and active-job deadlines both equal `102042.736105428` monotonic seconds.
The correction uses the original 120-second startup cutoff and preserves each original 30-second job clock.
Both FD handoff helpers keep the original active-job deadline without renewal.
A separate corrected join requires all forty fixture handoffs, including fifteen formatter handles and twenty-five file handles.
All 227 focused checks and both fresh 1216-test suites pass.
Actual completed fixture preparation remains unverified.

The shared 768 MiB parent now records one OOM kill.
Original v22 observer `24610` and timer `24612` no longer exist; their old batch records the kill.
Their full charge, journal, unknown objects, and historical loss remain retained.
All twenty journal snapshots and seventeen remaining current original journal FD identities pass read-only checks.
No lost proof, physical release, or refund is reconstructed.
[The exact v26 proposal](PHASE-2D-STARTUP-RETENTION-CONTINUATION-2026-10-15.md) requires explicit acceptance of that loss and a 2 GiB shared retention parent.
Individual batches keep 768 MiB, and observers keep 128 MiB.
The proposed higher parent limit remains after the batch to preserve remaining retention.
CPU, task, swap, per-job, and overall batch limits retain their original values.
[The exact record](qualification/phase-2d-executable-batch-v26-20261015.json) binds every command, input, resource exception, and custody requirement.
[The current prompt](PHASE-2D-STARTUP-RETENTION-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Twenty charges remain retained under 160 GiB combined logical and allocated reservations each.
No v26 operation or shared memory-limit change has started.
Forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: The original child diagnostic identifies missing lane-name geometry mapping.**
The owner approved exact v24, and it ran once.
The original report identifies `ValueError` at frozen `linux_storage.py:1141`.
The reader looks up full lane-prefixed names in a geometry table with unprefixed roles.
The correction uses the producer's existing exact mapping only for geometry lookup.
Full backing and loop names, identities, magic, size, and inode ceilings remain required.
All fifteen actual retained superblocks pass those unchanged checks through the corrected pure mapping.
All 218 focused checks and both fresh 1207-test suites pass.
Actual successful storage-owner readback remains unverified.
[The exact v25 proposal](PHASE-2D-LANE-GEOMETRY-CONTINUATION-2026-10-15.md) requires separate approval.
[The exact record](qualification/phase-2d-executable-batch-v25-20261015.json) binds all commands and inputs.
[The current prompt](PHASE-2D-LANE-GEOMETRY-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Nineteen full charges remain retained under 152 GiB combined logical and allocated reservations each.
Observer PID `26265` retains its original journal, compiler proofs, loops, copied root, and encrypted views.
Read-only checks verify all nineteen charges and seventeen current original journal FD identities.
The observer retains effective domain direct I/O and records zero memory-limit events.
All earlier original custody, counters, clocks, and unknowns remain retained or historically recorded.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Initial storage-owner readback still fails; bounded child failure reporting is prepared.**
The owner approved exact v23, and it ran once.
The original domain loop retains direct I/O and 4096-byte logical blocks.
The observer records zero memory-limit events and a 94113792-byte memory peak.
Initial storage-owner readback still returns unknown child readback after the preceding FD correction.
The remaining internal child cause is unknown.
The new source reports bounded source coordinates and errno without exception messages, local values, or full paths.
The parent strictly validates the failure data and keeps execution refused.
All 215 focused checks and both fresh 1204-test suites pass.
Actual successful storage-owner readback remains unverified.
[The exact v24 diagnostic proposal](PHASE-2D-CHILD-FAILURE-CONTINUATION-2026-10-15.md) requires separate approval.
[The exact record](qualification/phase-2d-executable-batch-v24-20261015.json) binds all commands and inputs.
[The current prompt](PHASE-2D-CHILD-FAILURE-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Eighteen full charges remain retained under 144 GiB combined logical and allocated reservations each.
Observer PID `25399` retains its original journal, compiler proofs, loops, copied root, and encrypted views.
Read-only checks verify all eighteen charge snapshots and sixteen current original journal FD identities.
All earlier original custody, counters, clocks, and unknowns remain retained or historically recorded.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Physical-domain direct I/O passes; initial storage-owner readback exposes a child proof lifetime error.**
The owner approved exact v22, and it ran once.
The domain loop reports direct-I/O flag `16` and 4096-byte logical blocks.
The observer records zero memory-limit events and a 93712384-byte memory peak.
The original path reaches storage-owner handoff after root projection, formatting, and encrypted-view setup.
The first storage-owner readback returns unknown child readback.
Retained parent frames identify that readback path.
Frozen source closes compiler proof FDs before child namespace entry invokes full parent derivation verification.
A fresh closed-FD regression reproduces `EBADF`; the original internal child exception remains unavailable.
The correction retains full parent verification before admission and checks child custody during namespace entry.
All 187 focused checks and both fresh 1197-test suites pass.
Actual successful storage-owner readback remains unverified.
[The exact v23 proposal](PHASE-2D-CHILD-CUSTODY-CONTINUATION-2026-10-15.md) requires separate approval.
[The exact record](qualification/phase-2d-executable-batch-v23-20261015.json) binds all commands and inputs.
[The current prompt](PHASE-2D-CHILD-CUSTODY-NEXT-SESSION-2026-10-15.md) supplies continuation files.

Seventeen full charges remain retained under 136 GiB of combined logical and allocated reservations each.
Observer PID `24610`, its original journal, compiler proofs, loops, copied root, and encrypted views remain retained.
Read-only checks verify all seventeen original charge snapshots and fifteen current original journal FD identities.
Original common-parent refusal counters remain retained; no counter is reset.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Copied-file cache advice works; the physical-domain backing cache still reaches the observer limit.**
The owner approved exact v21, and it ran once.
Final verification again refused original memory-limit history.
Read-only cache inspection reports zero cached bytes across all 910 copied root files.
The 1 GiB physical-domain image retains 127778816 cached bytes.
The observer again reaches 128 MiB and records 861 memory-limit events.
All original refusal history remains retained.
The correction requires direct I/O and verified 4096-byte blocks for the physical-domain loop only.
Original loop custody precedes controls, and positive complete kernel readback precedes formatting.
Later domain proofs require the effective direct-I/O flag.
All 121 focused checks and both fresh 1191-test suites pass.
Actual effective direct I/O remains unverified.
[The exact v22 proposal](PHASE-2D-DOMAIN-DIRECT-IO-CONTINUATION-2026-10-15.md) awaits separate approval.
[The current record](qualification/phase-2d-executable-batch-v22-20261015.json) binds its exact commands and inputs.
[The current prompt](PHASE-2D-DOMAIN-DIRECT-IO-NEXT-SESSION-2026-10-15.md) supplies the continuation files.

Sixteen full charges remain retained under the accepted 128 GiB combined reservation.
Observer PID `21410`, its journal, compiler proofs, copied root, and buffered backing image remain retained.
No old loop is reconfigured, detached, cleared, or reused.
All earlier original custody and unknown results remain retained or historically recorded.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Root copying passes; final resource readback refuses observer file-cache pressure.**
The owner approved exact v20, and it ran once.
Snapshot preparation passed, and all 1163 copied root entries have expected modes with no missing or extra paths.
Final production verification refused because the observer reached its 128 MiB memory ceiling.
The retained snapshot records 50196480 anonymous bytes, 74772480 file-cache bytes, and 834 observer memory-limit events.
The shared parent also retains refusal history; no original counter is reset.
The cache helper skipped all completed files at or below 4 MiB.
The correction advises completed small files and aligns final tails to actual kernel page size.
It changes no memory ceiling, clock, original FD custody, or mandatory resource-refusal check.
All seven focused checks and both fresh 1186-test suites pass.
Actual successful cache reclamation remains unverified.
[The exact v21 proposal](PHASE-2D-SMALL-CACHE-CONTINUATION-2026-10-15.md) awaits separate owner approval.
[The exact record](qualification/phase-2d-executable-batch-v21-20261015.json) binds its commands and inputs.
[The current prompt](PHASE-2D-SMALL-CACHE-NEXT-SESSION-2026-10-15.md) supplies the continuation files.

Fifteen full charges remain retained under the accepted 120 GiB combined reservation.
Observer PID `20701`, its journal, compiler proofs, and original root FDs `2437` and `2439` remain retained.
All earlier original custody and unknown results remain retained or historically recorded.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Owner preparation encounters an original exclusive journal lock before creating a new charge.**
The owner approved exact v19.
Upload and preparation each ran once; preparation refused with `sqlite3.OperationalError: database is locked`.
Original observer PID `19621` holds the exclusive lock.
No new input directory, storage directory, unit, observer, charge, or compiler was created.
The uploaded v19 archive remains retained, and the preparation attempt remains consumed.
The correction reads bounded hash-verified journal snapshots in private memory without changing original locks.
Three fresh checks pass; the exact helper also verifies all fourteen actual journals and preserves the original lock.
Production source and acceptance files remain unchanged, so both passing 1182-test results remain current.
[The exact v20 proposal](PHASE-2D-JOURNAL-SNAPSHOT-CONTINUATION-2026-10-15.md) awaits separate approval.
[The current record](qualification/phase-2d-executable-batch-v20-20261015.json) binds its exact replacement commands and inputs.
[The current prompt](PHASE-2D-JOURNAL-SNAPSHOT-NEXT-SESSION-2026-10-15.md) supplies the continuation files.

Fourteen full charges remain retained under the accepted 112 GiB combined reservation.
The proposed fifteenth charge and 120 GiB ceiling remain unchanged because v19 created no charge.
Original observer PID `19621`, its exclusive lock, journal, compiler proofs, and partial root remain retained.
All older original custody remains retained or historically recorded.
IPv4 forwarding is zero after the approved restoration.
No qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Physical-domain preparation passes; root copying rejects filesystem metadata allocation.**
The owner approved exact v18, and it ran once.
Both compilers, sealing, lane binding, physical-domain preparation, and primary and auxiliary backing creation passed.
Root copying returned an unknown child readback.
The retained first file, `/bin/bash`, matches its exact expected bytes.
Its actual allocation exceeds rounded data bytes by one 4096-byte filesystem metadata block.
The child suppresses internal exception text; read-only partial-file data and exact frozen source establish the accounting condition.
The copier now sums actual file allocation within the unchanged 448 MiB root ceiling.
It retains the existing directory allowance, exact bytes, identity, ownership, size, and exclusive creation checks.
All 64 focused checks and both fresh 1182-test suites pass.
[The exact v19 proposal](PHASE-2D-COPY-ACCOUNTING-CONTINUATION-2026-10-15.md) awaits separate owner approval.
[The exact record](qualification/phase-2d-executable-batch-v19-20261015.json) binds its scripts, commands, units, limits, and hashes.
[The current prompt](PHASE-2D-COPY-ACCOUNTING-NEXT-SESSION-2026-10-15.md) supplies the continuation inputs.

Fourteen full charges remain retained under the accepted 112 GiB combined reservation.
Observer PID `19621` retains its journal, compiler proofs, and partial root under original FD `2439`.
All earlier original objects remain retained or historically recorded.
IPv4 forwarding is zero after the exact approved restoration.
No qualification, device login, or live turn occurred.
Physical closure remains unknown; actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: Directory preparation passes; the frozen root lacks its required formatter entry.**
The owner approved exact v17, and it ran once.
Both compilers, sealing, final lane binding, polling, and both installation-directory FD handoffs passed.
Physical-domain preparation refused at frozen `linux_production.py:736` because `/usr/sbin/mkfs.ext4` is absent from the root inventory.
The preliminary inventory-digest diagnosis was incorrect; the exact line identifies the missing formatter entry.
The new root entry uses the original `/usr/sbin/mke2fs` bytes and source path.
New offline and precharge checks reject missing or different formatter bindings.
All production formatter hash, inode, custody, and read-only checks remain unchanged.
All 47 focused checks and both fresh 1180-test suites pass.
[The exact new proposal](PHASE-2D-FORMATTER-INPUT-CONTINUATION-2026-10-15.md) and [v18 record](qualification/phase-2d-executable-batch-v18-20261015.json) await separate approval.
[The current prompt](PHASE-2D-FORMATTER-INPUT-NEXT-SESSION-2026-10-15.md) supplies the exact continuation inputs.
[The execution ledger](qualification/phase-2d-execution-progress-v2-20261015.json) records the consumed v17 attempt.

Thirteen full charges remain retained under the accepted 104 GiB combined reservation.
Observer PID `15078`, both compiler proofs, and its journal remain retained.
All earlier original custody and partial objects remain retained or historically recorded.
IPv4 forwarding is zero after the exact approved restoration.
No qualification, device login, or live turn occurred.
Physical closure remains unknown; actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.


**October 15: High-descriptor polling passes; the retained compiler check conflicts with later setup work.**
The owner approved exact v16.
[The current execution record](qualification/phase-2d-execution-progress-v2-20261015.json) preserves commands, approvals, results, and earlier history.
Both compilers, full compiler-volume sealing, final lane binding, and high-descriptor child admission passed.
The child created the installation root and began its first FD handoff.
The retained compiler proof then refused because the shared setup role contained that admitted storage child.
The source now checks build-role emptiness immediately before sealing.
Later compiler readback retains immutable-output proofs and original role controls.
Actor admission checks remain unchanged.

All 26 focused checks and both fresh 1177-test suites pass.
[The exact lifecycle batch](PHASE-2D-ROLE-CONTINUATION-2026-10-15.md) awaits separate operational approval.
The [v17 record](qualification/phase-2d-executable-batch-v17-20261015.json) binds the complete current proposal.
The original child PID `14490` remains a zombie under observer PID `14430` and pidfd `1476`.
The preceding child PID `13791` and its original pidfd also remain retained.
Do not signal, reap, resume, or replace these children or pidfds.
The empty partial installation root remains present; do not remove or reuse it.

Twelve full charges remain retained under the accepted 96 GiB combined reservation.
IPv4 forwarding is zero after the exact approved restoration.
No policy installation, qualification, device login, or live turn occurred.
Physical closure remains unknown.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The private recovery directory and local custody index remain outside Git.
The earlier approval-pending statements below describe dated history.

**October 15: Final lane binding passes; high descriptor numbers block the next storage job.**
The owner approved exact v15 on October 15.
[The current execution record](qualification/phase-2d-execution-progress-v2-20261015.json) preserves commands, approvals, results, and earlier history.
All ten prior journal hashes and eight original journal FD identities matched before new preparation.
Both compilers, full compiler-volume sealing, and final lane binding passed.
The parent then refused the installation-directory child because `select()` cannot handle its high FD numbers.
The original pipe FD is `1475`, and the original child pidfd is `1476`.
The original child PID `13791` remains a retained zombie under observer PID `13731`.
Do not signal, reap, resume, or replace this child or its pidfd.

The source now uses a shared polling path for high descriptor numbers at all 75 observer readiness sites.
It preserves original descriptor custody, controls, clocks, and fixed child source bytes.
Four real high-descriptor regression checks and both fresh 1174-test suites pass.
[The exact polling batch](PHASE-2D-POLL-CONTINUATION-2026-10-15.md) awaits separate operational approval.
The [v16 record](qualification/phase-2d-executable-batch-v16-20261015.json) binds the complete current proposal.
The private recovery directory and local custody index remain outside Git.

Eleven full charges remain retained under the accepted 88 GiB combined reservation.
IPv4 forwarding is zero after the exact approved restoration.
No policy installation, qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier approval-pending statements below describe dated history.

**October 14: Compiler sealing passes; final lane verification exposes a cycle.**
The owner approved exact v10, v11, v12, v13, and v14 exceptions during this session.
[The execution record](qualification/phase-2d-execution-progress-v1-20261014.json) preserves their commands, approvals, results, and limitations.
All 276 public bundle entries matched before new source changes.
All twelve dated private paths were missing.
The owner authorized access recovery from project memory; SSH and password-free sudo work.
Offline preparation recovered the exact v10 private archive and plan from retained guest inputs.
The private recovery directory remains outside Git.

Both actual compilers and the full compiler-volume read-only remount now pass.
The v14 final lane binding then exposed a timer, lane, reservation, and build derivation verification cycle.
The original traceback confirms this cycle.
The source now separates internal lane role-handle checks from full reservation verification.
All original custody and control checks remain required.
All 47 focused checks and both fresh 1170-test suites pass.
[The exact cycle correction batch](PHASE-2D-RECURSION-CONTINUATION-2026-10-14.md) awaits separate operational approval.
The [v15 record](qualification/phase-2d-executable-batch-v15-20261014.json) binds the complete current proposal and final unit hashes.

Ten full charges remain retained under the accepted 80 GiB combined reservation.
All operational attempts remain consumed; original processes, timers, clocks, handles, and unknowns remain retained or historically recorded.
IPv4 forwarding is zero after each exact approved restoration.
No policy installation, qualification, device login, or live turn occurred.
Actual Phase 2D acceptance remains incomplete at unreleased candidate 0.13.0.
No commit, push, release, or Phase 2E work occurred.
The earlier decline statements below describe dated history; the exact new approvals supersede that operational decline only.

**October 14: Next-session package prepared at the owner's request.**
[The new prompt](PHASE-2D-NEXT-SESSION-2026-10-14.md) and [current exact manifest](PHASE-2D-NEXT-SESSION-INPUTS-2026-10-14.json) include the updated handoff.
The public bundle is `phase2d-next-session-2026-10-14.zip` in the existing local Crewshal artifact directory.
The separate October 13 local custody index remains outside the public bundle.
This preparation grants no operational approval and changes no source, package version, or acceptance result.
The next milestone remains actual Phase 2D acceptance under exact owner authority.

**October 14: Local continuation inputs verified; Phase 2D remains incomplete.**
[The resumption report](PHASE-2D-RESUMPTION-2026-10-14.md) supplies the exact boundary and continuation prompt.
[Fresh local evidence](qualification/phase-2d-local-preflight-v1-20261014.json) records matching hashes for all 267 initial repository inputs and the complete 272-file bundle.
Both v10 owner scripts, unit hashes, private archive, and private batch plan match their exact records.
All 117 production and test files in each recorded suite still match.
The 1161-test source and wheel results remain historical; unchanged complete suites were not repeated.
Task-directed source inspection supplies no actual installed or live acceptance evidence.
The October 13 operational decline remains in force.
The owner has received a question about reopening that decision; no answer was available when this record was written.
No VM operation, compiler, charge, observer, timer, login, provider call, or Linux installation occurred.
Original source and dirty work remain intact; only the handoff and new local records change.
The candidate remains unreleased version 0.13.0 at base revision `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc`.
No commit, push, release, or Phase 2E work occurred.
Actual installation, both complete Linux qualifications, and live candidate validation require exact separate operational approval.
Preserve the dated October 13 manifest and ZIP; their handoff hash describes the preceding handoff.

**October 13: The owner declined the additional Phase 2D batch.**
The exact v10 reservation and additional compiler exception remain unauthorized.
[The decision record](qualification/phase-2d-v10-declined-v1-20261013.json) binds the unchanged v10 batch hash and fresh retained-custody readback.
No v10 operational command ran, and no sixth charge was created.
The five prior full charges retain the approved 40 GiB combined reservation allowance each.
All five journal hashes, three current journal FD identities, and the consumed compiler pidfd remain unchanged.
IPv4 forwarding is zero. The v10 guest paths remain absent.
Both complete source and fresh-wheel suites pass 1161 tests, but actual Phase 2D acceptance remains incomplete.
The candidate remains unreleased version 0.13.0.
No publication or Phase 2E work occurred.
Do not execute the declined batch or request the same decision again without new owner instructions.
The dated records below preserve the preceding work and approval history.


**October 11: Phase 2D remains blocked at version 0.12.0.** The owner requested completion or an explicit list of causes. [The current report](PHASE-2D-BLOCKED-2026-10-11.md) records four causes, the required capability, and exact continuation inputs. [Fresh verification](qualification/phase-2d-blocked-verification-v1-20261011.json) records 77 focused and 863 complete passing source tests. These include 722 Phase 2D tests. Network access was denied for the complete suite and compatibility check. The inherited environment was empty; HOME was fresh. The source filter still denies bounded WAL mappings on both supported ABIs. Installation admission remains closed. The installed parent, validator view, admission linkage, and exact Linux/live acceptance remain incomplete. No accepted owner decision needs another answer.

The base revision is `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc` on `codex/phase1-architecture`. Production source, tests, and dated evidence remain unchanged. AGENTS.md now records the owner's permanent ASD-STE100 rule. New human communication must obey that rule, including future session prompts and approval requests. No operational batch, paid call, credential access, version change, commit, push, or Phase 2E work occurred. Publication remains conditional on full Phase 2D acceptance. Continue with the new report's exact prompt and input list. The earlier current-state paragraphs are dated records.

**Owner-authorized 0.12.0 blocked source checkpoint, October 10.** The owner instructed “publish and prepare next session's prompt and files.” [Checkpoint and publication verification](PHASE-2D-EFFECTIVE-OWNERSHIP-CHECKPOINT-2026-10-10.md), [next-session prompt and exact input manifest](PHASE-2D-NEXT-SESSION-2026-10-10.md) now govern continuation. Resolve the delivery revision from the commit containing this checkpoint; the current branch is `codex/phase1-architecture`, canonical remote `forera-ai/Crewshal`. This explicitly supersedes the earlier requirement to wait for full Phase 2D acceptance before publishing this checkpoint only. All current uncommitted implementation/evidence is included without reverting original dirty work. Phase 2D remains blocked/incomplete and source unqualified; installation admission stays closed on the recorded stock-runtime growth-policy incompatibility. Accepted decisions, original controls/charges/handles/unknowns and all three consumed compiler attempts remain unchanged. Publication authorizes no compiler/Linux/kernel/credential/login/model/VMware/SSH action, release/reuse, merge/deployment/registry release or Phase 2E. Earlier revision/version/publication statuses below are dated history.

**October 10: effective ownership preparation verified offline; stock-runtime growth-policy incompatibility blocks acceptance.** [Latest blocker, exact capability and continuation](PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md), [new immutable verification](qualification/phase-2d-effective-ownership-verification-v1-20261010.json). All 863 unique methods / 722 Phase 2D pass in denied-network source/fresh-wheel checks, with 31 packaged and 26 dispatch-bound source identities matching. Retained physical/journal/root, freeze/bridge/validator preparation is added; source is unqualified and actual installed finite parent/validator view/admission linkage remain unfinished. Pinned app-server mandatory SQLite WAL uses shared file mapping that the current shmem filter denies. Compatible actual anonymous/dev-zero/additional-namespace-filesystem enforcement is missing; installation admission explicitly refuses and retains full charge/unknown. Accepted ADR 0006 and prior ownership/subscription/authentication decisions stay resolved. Original deadlines/controls/handles and all three consumed syntax invocations remain intact. No compiler/Linux/kernel/credential/login/model/VMware/SSH operation occurred. Base remains pushed 758079b / 0.11.0; dirty changes are preserved, no version/commit/push before full Phase 2D acceptance, no 2E. All preceding statuses below are dated history.

**October 10: upfront bootstrap approved; charge and finite preparation source verified.** [Current boundary and exact continuation](PHASE-2D-INSTALLATION-BOOTSTRAP-2026-10-10.md), [accepted ADR 0006](decisions/0006-upfront-installation-charge.md), [immutable verification](qualification/phase-2d-installation-bootstrap-verification-v2-20261010.json). The owner answered “Approve upfront charged bootstrap”; do not reask that architecture decision. Distinct full synchronous charge, one original claim/reservation, unknown-result consumption and bounded root/backing-directory custody are implemented. Complete source verification passes **699 methods / 558 Phase 2D**; installed-wheel/static/package results are recorded in the ledger. Effective physical-domain/root/journal combined-growth installation remains missing, so the new charge path deliberately refuses native/watchdog/validator admission even with matching observed data. This is not completion of its effective installation gate or full 2D. Continue the physical capacity/growth producer, original-volume readonly freeze/credential-free validator, installed identities and exact Linux/live qualification within the existing accepted scope. No new owner policy incompatibility has been established. Original controls/charges/handles/unknowns remain; all three syntax invocations are consumed. Pushed base stays 758079b / 0.11.0; subsequent source is uncommitted. No operational runtime/host/login/model, release/reuse or 2E authority follows. All older pending/current-status paragraphs below are dated history.

**October 10: growth source verified; installation-bootstrap owner decision pending.** [Current boundary, exact continuation and complete inputs](PHASE-2D-GROWTH-BOUNDARY-2026-10-10.md), [immutable verification](qualification/phase-2d-growth-verification-v1-20261010.json), [exact owner proposal](PHASE-2D-INSTALLATION-BOOTSTRAP-DECISION-2026-10-10.md). Pushed base remains 758079b9bcf8ad82d5863aaf5f6a096608acb942 / 0.11.0; subsequent source remains uncommitted. Source adds inherited 131072-byte soft/hard payload file limits and actual ext4 inode/directory readback. Complete source verification is 681 / 540 Phase 2D methods; three fresh regressions reproduce twelve failures in a fresh byte-verified published baseline. This does not establish full combined growth or installed/runtime eligibility. The current installed-first claim and creation reservation/timer prerequisites obstruct in-place installation bootstrap. One material proposal permits an upfront fully charged same-original-observer installation reservation with actual installation proof before native/validator admission. It is pending, unapproved and unimplemented; no synthetic initializer or physical-capacity claim is substituted. Preserve all original controls/charges/handles/unknowns and existing installed-first refusal. Finish the actual capacity/growth, original frozen-volume/credential-free validator, installed identities and exact Linux/live gates after the decision. The changed C syntax pass is recorded below; all three invocations are consumed. No broader host/runtime/login/model, release/reuse or 2E authority. All older pending/current-status statements below are dated history.

**October 10: approved additional timer syntax check passed; continued idle-retention source verified.** [Latest result, exact remaining work and inputs](PHASE-2D-TIMER-SYNTAX-PASS-2026-10-10.md), [immutable verification](qualification/phase-2d-timer-syntax-pass-verification-v1-20261010.json). Pushed base remains `758079b9bcf8ad82d5863aaf5f6a096608acb942`, package 0.11.0; continued source remains uncommitted. The exact approved 13411 C bytes pass syntax-only compilation: complete input/transport, exit 0, empty streams, 0.36629341600928456 seconds. Three approved syntax invocations are consumed; no further compiler or broader operational action is authorized. Effect-free original idle custody now checks retained helper/lifeline, actual pidfd exit/reap, stopped roles, original jobs/wrapper and sole original observer after the fixed batch; live admission still refuses expiry and the original cutoff. All **674 complete / 533 Phase 2D offline methods** pass in source and installed wheel, plus static/build/28-byte-source comparisons. This is process/accounting source, not full storage-owner/attempt acceptance or runtime qualification. Effective installed capacity/growth, original frozen-volume/credential-free validator, installed identities and exact Linux/live acceptance remain unfinished. Continue the same consolidated milestone. No pending owner policy decision is established; no retry, release/reuse, metered fallback or 2E. All pending-status statements below are dated history.

**Continued timer/child-placement source, October 10: pushed base `758079b9bcf8ad82d5863aaf5f6a096608acb942`, package 0.11.0; subsequent changes uncommitted.** [Current implementation, unresolved mechanics and exact continuation](PHASE-2D-BATCH-TIMER-2026-10-10.md), [immutable offline verification](qualification/phase-2d-batch-timer-verification-v1-20261010.json). Namespace launch leaves the original retaining observer outside stopped roles. An original-observer timer pins the unchanged 570-second cutoff/600-second batch without another recovery wait or allowance; creation children independently prove actual setup placement before admission. Storage-owner readback binds the original job, timer and execution role. Three regression methods fail the independently byte-verified published wheel and pass current source. **528 Phase 2D / 669 complete offline tests** pass in source and freshly installed wheel; lint/format 66, strict types 27, offline build and 28 packaged / 23 dispatch-bound byte checks pass. Effects remain explicitly synthetic. The changed helper is **13411 bytes / `21e8b509e5c25011efd2522a4cfccb0c4e675aa59e147c50c2b32496f0cece2c`**, uncompiled. [One additional exact frozen syntax invocation](PHASE-2D-BATCH-TIMER-SYNTAX-2026-10-10.md) has been requested; approval is pending. Its private client/attempt remain uninvoked. Both prior attempts are consumed and do not cover these bytes.

**Full effective Phase 2D remains incomplete and source unqualified.** Child birth/self-placement can leave an unknown operational child outside stopped roles; the helper's independently observed terminal transition is unfinished. Installed capacity/journal/growth, actual original frozen-volume/credential-free validator, installed identities and exact changed-profile Linux/live acceptance also remain unfinished. No new policy incompatibility or owner decision beyond the pending exact compiler invocation is established. Keep all actual/partial handles and full original charges, no admission after cutoff, no storage release/reuse or deadline/grace renewal. Continue the same consolidated milestone using the current guide's exact input chain; do not reask resolved retention/subscription/Ubuntu decisions or begin 2E. Publication of the preceding checkpoint is verified and complete; the historical uncommitted 0.10.0/0.9.2 and conditional publication statements below are dated history, not the current revision or authority.

**Owner-authorized 0.11.0 source checkpoint, October 10.** The owner instructed “commit + push the works and continue to complete the 2D.” [Checkpoint, explicit publication exception and exact continuation](PHASE-2D-CHECKPOINT-2026-10-10.md) and [publication verification](qualification/phase-2d-publication-verification-v2-20261010.json) govern current delivery. Resolve the delivery revision from its containing commit. This instruction supersedes the older conditional publication statements for this checkpoint; full Phase 2D remains incomplete and source unqualified. Existing source verification is 649 complete / 508 Phase 2D tests; both syntax attempts are consumed and the explicitly approved additional check passed. Continue the same consolidated milestone after push: effective installed capacity/growth, actual readonly frozen-volume/credential-free validator, original-observer batch timer and installed identities, followed by concrete separately approved exact Linux/live qualification. No execution, spend, physical release, reuse, merge, deployment, registry release or 2E authority follows from publication. Original controls/charges/unknowns and immutable evidence remain intact.

**Latest October 10 continuation: the owner confirmed the exact capability installed and approved one additional check; that bounded Ubuntu syntax check passed.** [Current result, source corrections, exact remaining work and continuation](PHASE-2D-SYNTAX-PASS-2026-10-10.md), [immutable verification](qualification/phase-2d-syntax-pass-verification-v1-20261010.json). Frozen helper source remains 8011 bytes / `893357d84d18b0d11d3e7a03d044cd39f91fd5f928f233003d04114c1adefd9b`; exit 0, complete transport and empty streams. Both approved attempts are consumed and private markers/output remain retained. Compiler syntax compatibility is resolved only for these bytes; no further compiler/host action, installation, helper/native, login or model operation is implied. Source now checks retained native exit/reap and original controls, binds Linux/subscription collection to the original watchdog/live-parent handoff, reads terminal state before and after copy, retains repopulation failures and fixes auth/validator mount target creation. The admitted wrapper forwards the original lifetime; legacy envelope-free collection remains offline data only. **Full effective 2D is still incomplete:** installed physical capacity/journal/growth, actual original-volume readonly freeze and credential-free validator, original-observer terminal timer, installed identities and exact Linux/live qualification remain open. No new owner policy decision is established. Preserve accepted decisions, original controls, full charges/unknowns and immutable history. Base 8e010b5 / version 0.10.0 remain uncommitted; commit/push follows full acceptance, no 2E. The older refusal and unanswered-capability statements below are dated history.

Continue the same consolidated milestone using the linked guide's exact inputs/prompt. Do not replay either consumed syntax client, reask resolved approvals, treat this source round as 2D completion or infer a publication exception.

Latest verification: **508 Phase 2D / 649 complete tests**, editable and fresh installed wheel with denied network/empty environment/fresh HOME; focused 227, Ruff lint/format 64, strict mypy 27, offline build/fresh install and 28 packaged / 23 dispatch-bound byte comparisons pass. Three regressions independently fail the preserved preceding wheel and pass final source; an exact predecessor patch permits fresh offline reproduction. No additional runtime/native/kernel or host check was performed after the approved syntax invocation.

Owner follow-up, October 10: selected “Arrange narrowly scoped sudo.” [Exact owner-terminal instructions, locally parsed command-only snippet and separately proposed one additional check](PHASE-2D-SYNTAX-CAPABILITY-2026-10-10.md) are prepared. This selection does not establish installed capability or approve the extra invocation. No second SSH/compiler call or host authorization change occurred. Wait for both explicit installation confirmation and one-additional-attempt approval; preserve the first consumed marker and its immutable refusal evidence. No old deadline or general no-retry policy is silently reset.

- **Current consolidated Phase 2D boundary, October 10: approved syntax refusal and retained candidate-root correction; base `8e010b5`, version 0.10.0, uncommitted.** [Exact result/continuation and inputs](PHASE-2D-SYNTAX-RESULT-2026-10-10.md), [new immutable evidence](qualification/phase-2d-syntax-result-verification-v1-20261010.json). The owner approved the frozen syntax batch. One SSH transport sent all 8011 public C bytes; sudo -n refused with the exact password-required diagnostic before compilation. The exclusive attempt is consumed; no retry, password retrieval, sudoers change, further SSH/probe, installation or broader execution occurred. Compiler compatibility remains unknown. The required capability is noninteractive authorization for the exact reviewed command or an equivalent independently bounded owner-operated check; capability alone does not grant another attempt. No resolved Ubuntu/subscription/retention decision is reopened. Safe independent source work fixes regular-directory root replacement: preparation and freeze now pin one original FD throughout and refuse changed root identity. Both old-source subcases demonstrably fail; **499 Phase 2D / 640 complete offline tests** pass. Current static/build/package checks and exact source identities are in the new verification. Full 2D remains incomplete: actual installed capacity/journal/growth, stopped-worker readonly frozen view and credential-free validator, original-observer terminal timer, installed identities and exact Linux/live qualification are still unfinished. All unknowns/full charges and original controls remain retained. No version bump, commit/push or 2E; publication follows complete acceptance. Earlier pending-approval/no-SSH/no-compiler-attempt statements below are dated history.

Next work remains the same full Phase 2D mechanics. Preserve the failed private compiler marker/output and immutable October 9 ledgers; do not rerun the consumed client or silently bypass sudo/control limits. Use the new exact prompt/input chain. Prepare further operational work only as a concrete reviewable batch with its required authority.

- **Current consolidated Phase 2D source boundary, October 9: owned filesystem/root/view production and capture corrections; base `8e010b5`, version 0.10.0, uncommitted.** [Current exact continuation and inputs](PHASE-2D-OWNED-VIEWS-2026-10-09.md), [fresh immutable verification](qualification/phase-2d-owned-views-verification-v1-20261009.json). Source adds retained private anonymous key payloads, fixed-FD ext4 formatting, copied readonly root, fixed native-auth/validator backings and ext4/eCryptfs mount custody. Namespace setup executes the helper through the actual readonly-root FD; inherited namespace/cgroup C checks remain uncompiled. Effect-free readback keeps a fixed terminal bound without renewing creation or physical teardown. Candidate FD traversal refuses a reproduced ancestor-symlink race and leaf mutation before capture. **498 Phase 2D / 639 complete offline tests**, denied-network editable/fresh wheel, lint/format 64 files, strict types 27 modules, offline build and 28 packaged / 23 dispatch-bound sources pass. **Full 2D remains incomplete:** installed physical capacity/journal binding and total growth, actual stopped-worker freeze/readonly validator view and credential-free validator startup, original-observer terminal timer, installed loader/import/authentication/tool identities and exact Linux/live qualification remain unfinished. No policy incompatibility/new owner decision is established. [One frozen syntax-only Ubuntu compiler batch](PHASE-2D-LINUX-SYNTAX-BATCH-2026-10-09.md) has been asked and awaits an answer; its bounded private transport client is prepared and passes two fresh mocked pipe fixtures, but no actual compiler/SSH/runtime action ran. Keep accepted retention/subscription decisions and original limits unchanged; unknowns remain retained/fully charged. Continue the same full milestone, with no metered fallback, cleanup/reuse or 2E. Commit/push is conditional on full acceptance and has not run. All earlier bullets are dated history.

Next implementation remains fixed installed physical capacity/journal/growth, actual frozen candidate/validator and original-observer timer. The syntax-only pending action resolves compiler compatibility only and grants no authority for installation, login, model or full qualification. Do not substitute another source-test pass for full acceptance.

- **Current consolidated Phase 2D boundary, October 9: irreversible capacity and partial production custody; base `8e010b5`, version 0.10.0, uncommitted.** [Current guide, exact continuation and inputs](PHASE-2D-PRODUCTION-OWNERSHIP-2026-10-09.md), [fresh verification](qualification/phase-2d-production-ownership-verification-v1-20261009.json). Full synchronous journal claims deny restart/reconstruction/reuse, bind the original live reservation before creation and retain full charges on refusal. Actual-FD handoff precedes partial namespace/backing/loop mutation, uses independently pinned child proc/pidfd identity and moves blocking loop readback into the bounded child. Subscription profile/cwd/authentication projection now agrees across envelope, setup, parent/watchdog, C helper and native admission. **442 Phase 2D / 583 complete offline tests**, focused 86, lint/format 67 files, strict types 27 modules, offline build and fresh denied-network installed-wheel/source checks pass; 28 packaged / 23 dispatch-bound sources. **Full 2D is still incomplete:** fixed installed physical pool/journal binding, effective combined growth, ext4/private-key/eCryptfs/root/auth/view production, original-observer timer exclusion, installed identities and exact Linux/live qualification remain missing. Source supplies no operational readiness. No new owner decision is identified; complete missing mechanics without reopening accepted policies. Idle original retention can survive the batch only with all operational jobs stopped, original charges/ceilings retained and no further allocation. No compiler, operational fork/Popen/kernel, credentials/login/provider/model/Jev or target-host action occurred; no metered fallback or 2E. The user's commit/push instruction is conditional on full acceptance, so no commit/push/version bump occurs at this partial boundary. Prior bullets and evidence are dated history.

Next implementation step: establish the smallest fixed installed capacity/root producer and actual retained source views, rather than another policy proposal or placeholder qualification command. Use only the current guide's exact continuation and complete historical input chain. Do not reconstruct installation or ownership from the synthetic journal fixtures.

- **Current consolidated Phase 2D boundary, October 9: official subscription source; base `8e010b5`, version 0.10.0, uncommitted.** The owner approved the official subscription route and then “Approve only vendor authentication recovery.” [Accepted ADR 0005](decisions/0005-official-subscription-pilot.md), [current source/continuation](PHASE-2D-SUBSCRIPTION-AUTH-BOUNDARY-2026-10-09.md) and [fresh verification](qualification/phase-2d-subscription-auth-boundary-verification-v1-20261009.json) govern. Six fixed requests, full startup readback, independent account identity, retained unbuffered stdin, bounded nonblocking duplex capture and raw RPC normalization are implemented; ordinary retries remain zero, HTTP is forced and default unbounded reconnects are disabled. Protocol completion never supplies exit/EOF/tree-stop, project verdict, release or reuse. Stock helper placement required exact auth/config masks rather than a blanket home mask; all actual helper aliases/views and fresh home exclusion of `.env` remain qualification gates. **Phase 2D remains incomplete:** effective from-creation/persistent ownership and total storage controls, installed parent/root/helper/library identities, exact changed-profile Linux qualification and one separately authorized real candidate/validator batch remain missing. No compiler, operational fork/Popen, real Linux controls, credentials/login, provider/model or target-host action occurred in this round. All original limits/origins/grace/reserve and retained charges/unknowns stay fixed. Both subscription decisions are resolved; do not ask them, retention, loop ordering, billing or Ubuntu access again. No metered API/custom model loop/2E; publication remains gated.

Final verification for the current subscription-source boundary: **395 Phase 2D / 536 complete tests**, focused 104, lint/format 64 files and strict types 26 modules; offline build, fresh installed-wheel complete suite and all 27 packaged-source comparisons pass (22 dispatch-bound sources). This is source verification only; operational qualification and Phase 2D acceptance remain incomplete.

- **Current consolidated Phase 2D boundary, October 9, after accepted retained-terminal storage; base `8e010b5`, package 0.10.0, uncommitted.** The owner approved the retention clause and instructed bounded ownership. [Accepted ADR 0004](decisions/0004-retained-terminal-storage.md) resolves the former physical-release requirement decision; earlier pending statements below are dated history. [Current source and exact continuation/inputs](PHASE-2D-RETAINED-OWNERSHIP-2026-10-09.md), [verification](qualification/phase-2d-retained-ownership-verification-v1-20261009.json). Source retains the full original reservation, original observer/aggregate, partial owners and every storage handle. It provides effect-free one-shot terminal readback, rejects missing handles/rebinding/new references/repopulation and enforces the original absolute cleanup bound without restarting recovery grace. Retained reservations have no release authority. Setup's observer-limit incompatibility is corrected to 134217728 bytes/32 tasks. **Effective from-creation producer, persistent owner/capacity handoff, combined total storage-growth enforcement, installed parent/root/helper/library and exact changed-profile Linux/live qualification remain unproved. Phase 2D is incomplete.** No real compiler/fork/Popen/kernel/login/model operation ran in this round. The exact pinned API-key-only proxy is incompatible with a demonstrated subscription login/lifecycle; [one concrete official Codex app-server pilot amendment](PHASE-2D-SUBSCRIPTION-ROUTE-DECISION-2026-10-09.md) awaits the owner. Do not reask retention, loop-close ordering, Ubuntu access or subscription-only billing. Preserve all original limits/origins/grace/reserve, unknowns, full charges and immutable evidence; no metered API/custom gateway/model loop/2E. Finish offline verification and stop at this precise architecture/capability boundary; publication remains gated by complete acceptance or explicit checkpoint exception.

- **Current consolidated Phase 2D completion boundary, October 9; checkpoint `8e010b5ca2dd3298268132613f8ad17ff9db07c6`, package 0.10.0, work uncommitted.** The owner requested full 2D completion and confirmed loop-device FD closure within loop detach, existing local Ubuntu use and subscription-only models. Existing SSH access is restored; read-only Ubuntu 24.04.5 / `7.0.0-38-generic` aarch64 admission observes cgroup v2 and eCryptfs support. Codex/Claude are absent from PATH. No model, installation, compiler or storage/cgroup mutation occurred. Review rejected and removed a direct observer-side loop close because final close can itself block outside the bounded job. Final source preserves the ENXIO correction and retained loop FDs; the approved ordering requires a bounded sole holder from creation plus independent completion. A new regression fails the discarded candidate and passes final source. **334 Phase 2D / 475 complete offline tests**, focused 74, static/build and fresh-wheel/source checks pass. [Confirmed decisions, exact remaining incompatibility, proposed requirement amendment, all completion gates and next prompt/inputs](PHASE-2D-COMPLETION-DECISION-2026-10-09.md); [verification](qualification/phase-2d-owner-decisions-verification-v1-20261009.json). Positive physical release remains mandatory unless the owner explicitly accepts the proposed retained-terminal outcome. This decision is pending; no release/reuse/2D completion follows from approval or source tests. From-creation ownership, actual installed parent/root/helper/library/effective controls, observer/aggregate accounting, fresh exact Linux/native qualification and a concrete separately approved subscription live batch remain required. Preserve original ceilings, admission/terminal ordering, five-second origin, one-second grace and fixed 30-second/600-second reserve. Do not reask the three resolved decisions or repeat unchanged tests. Subscription quota percentages are shared observations; no metered API/credit/reset/Jev fallback. Historical blocker/checkpoint/evidence bytes stay intact. Publication remains gated; no 2E. Stop at this recorded requirement boundary.

- **Current 2D boundary: effective retained storage closure blocked, October 9, after checkpoint `8e010b5ca2dd3298268132613f8ad17ff9db07c6`; package 0.10.0, new work uncommitted.** [Exact incompatibility, smallest owner decision and next prompt/inputs](PHASE-2D-STORAGE-CLOSURE-BLOCKER-2026-10-09.md), [new verification](qualification/phase-2d-storage-closure-verification-v1-20261009.json). Loop GET_STATUS64 ENXIO can describe rundown with a still-retained backing reference; source now raises unknown instead of reporting disappearance. Three regression cases failed on checkpoint source; 73 focused / 474 complete offline tests (333 Phase 2D), static checks, offline build and fresh-wheel source checks pass. Upstream Linux v7.0 commit-bound source exposes the last-loop-close ordering conflict; it does not establish Ubuntu/current-kernel identity. Current setup-to-owner handoff has no complete effective from-creation reference confinement. The first consequential decision is whether to permit final loop-device FD closure inside the loop-detach stage with independent identity/non-rebinding/completion readback; it is necessary but insufficient for closure. Unknowns and remaining handles stay retained/charged, reuse stays false, no retries or changed controls. Historical bytes/0.10.0 publication checkpoint remain intact. The checkpoint exception does not extend to this boundary: the resumed exact prompt requires offline and approved live 2D acceptance before further publication. No compiler, runtime child, real kernel/credential/provider/model/Jev, VMware/SSH or target-host operation occurred; no 2E. Do not begin another milestone before the precise decision.

- **Owner-authorized source publication checkpoint, October 9; package 0.10.0.** The owner explicitly requested commit + push of the verified Phase 2D source and the next-session prompt. [This checkpoint](PHASE-2D-SOURCE-CHECKPOINT-2026-10-09.md) supersedes the earlier 0.9.2 publication stop for this delivery only. Compatible source functionality receives a synchronized minor version bump. The complete pending 2D source/dependencies/tests/guides form one reproducible checkpoint; 473 offline tests (332 Phase 2D), static/build and installed-wheel/source checks pass. Effective reference closure and all operational Linux/live gates remain blocked or unverified. No execution/spend/host operation, merge/deployment/registry release or 2E is authorized. Earlier 0.9.2/uncommitted/no-publication statements remain dated history. Resolve the delivery revision from the commit containing the checkpoint guide. Next session uses only its **0.10.0 prompt and exact required inputs** for effective retained reference closure.

- **Latest active 2D boundary: retained Linux storage-owner source; effective reference closure blocked, October 9.** [Guide and exact next prompt/inputs](PHASE-2D-LINUX-STORAGE-OWNER.md), [source](../src/crewshal/linux_storage.py), [44 fresh storage methods](../tests/acceptance/test_phase_2d_storage.py), two teardown deadline methods and [verification/continuity](qualification/phase-2d-linux-storage-owner-verification-v1-20261009.json) add pinned namespace/mount/private-keyring/loop/backing readback and fixed absolute cleanup operation source. Positive aliases and deleted-open/mapped references prevent cleanup. **Empty proc scans remain unknown**: effective closure of taskless namespaces, asynchronous/socket-passed/kernel references, delayed/additional loops and concurrent mutation is missing. Concrete source cannot admit actual physical teardown or authorize reuse. **332 Phase 2D / 473 complete offline tests**, focused 72, static checks, offline build and fresh-wheel comparison of all 26 packaged sources pass. Twenty-one dispatch-bound sources invalidate prior prospective configurations. No fork, compiler, Popen, namespace/key/mount/loop/cgroup action, credentials, spend, VMware/SSH or host operation occurred. Original ceilings, terminal/admission ordering, five-second origin, one-second grace and 30-second/600-second reserve remain unchanged. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, maintenance version **0.9.2**, uncommitted. Next scope is only effective retained reference closure and trusted storage-owner handoff, or its exact incompatibility/smallest owner decision. Actual parent/root/helper/library/FD installation, effective controls, observer/aggregate handoff, exact Linux qualification and separate live acceptance remain missing. Stop at this source/blocking boundary; no publication or 2E. Earlier bullets retain historical achievements.

- **Latest active 2D boundary: physical teardown ordering and trusted parent inventory binding source, October 9.** [Guide/exact next prompt and inputs](PHASE-2D-OWNED-TEARDOWN.md), [inventory](../src/crewshal/linux_inventory.py), [teardown](../src/crewshal/linux_teardown.py), [20 inventory methods](../tests/acceptance/test_phase_2d_inventory.py), [26 teardown methods](../tests/acceptance/test_phase_2d_teardown.py) and [verification/continuity](qualification/phase-2d-owned-teardown-verification-v1-20261009.json) add exact retained root/entry/helper-library binding and one-shot owned physical release ordering after fresh terminal watchdog/parent/wrapper and empty-role observations. Unknown/partial failures retain remaining handles; backing FDs close before unlink, role removal precedes final FD closure, observer/aggregate remain retained and every reuse result stays false. Original stopped native admission, five-second origin, one-second grace and ceilings stay unchanged. **286 Phase 2D / 427 complete offline tests**, focused 204, lint/format (59 files), mypy (24 modules), offline build/fresh-wheel and 25 packaged-source comparisons are recorded. Twenty bound sources invalidate prior configurations. **Production remains incomplete:** concrete retained Linux storage-owner readback/bounded operations, actual parent entry/import bootstrap and installed root/helper/library/FD identity, effective controls, Linux inheritance/pre-instruction checkpoint, fresh exact qualification and separate project/session live gate are missing. `PhysicalOwner` is a protocol; kernel effects and process exits in tests are synthetic, C remains uncompiled. No startup, credentials, model/provider/Jev spend, VMware/SSH or host operation occurred. 803 prior/current local inputs were read/hash-snapshotted as data; unrelated dirty/historical bytes stay intact. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, maintenance version **0.9.2**, uncommitted. Stop at this source boundary; no publishing before complete 2D acceptance or 2E. Earlier bullets remain historical.


- **Latest active 2D boundary: owned setup and terminal process lifetime source, October 9.** [Guide and exact next prompt/inputs](PHASE-2D-OWNED-SETUP.md), [source](../src/crewshal/linux_setup.py), [35 fresh methods](../tests/acceptance/test_phase_2d_setup.py) and [verification/continuity](qualification/phase-2d-owned-setup-verification-v1-20261009.json) add sealed retained controls, bounded observer/setup/supervisor/worker siblings under the original aggregate, namespace-local parent attachment, owned fixed-FD watchdog creation before worker creation and local/external terminal process observations. Worker emptiness precedes external supervisor/setup stops; failed/unknown handles remain retained and every reuse result stays false. Original native admission, five-second origin, one-second grace and ceilings remain unchanged. **240 Phase 2D / 381 complete offline tests** pass editable and fresh installed wheel under denied network/empty environment; lint/format (55 files), mypy (22 modules), build and 23 packaged-source comparisons pass. Eighteen bound sources invalidate prior configurations. **Production bootstrap remains incomplete**: owned physical mount/key/backing teardown and release ordering, qualified parent entry/root/helper/library identities, actual effective controls and Linux inheritance/pre-instruction checkpoint, fresh exact qualification and separate project/session live gate are missing. Kernel/Popen/sealing/migration/timer effects are synthetic; C is uncompiled. No startup, credentials, spend or host operation occurred. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, version **0.9.2**, uncommitted. Keep all effects disabled; no publication before complete 2D acceptance or 2E. Earlier bullets remain historical.

- **Latest active 2D boundary: parent/watchdog bridge source, October 9.** [Guide and exact next prompt/inputs](PHASE-2D-PARENT-WATCHDOG.md), [source](../src/crewshal/linux_parent.py), [23 fresh methods](../tests/acceptance/test_phase_2d_parent.py) and [verification/continuity](qualification/phase-2d-parent-watchdog-verification-v1-20261009.json) add retained namespace-parent/watchdog readback, initial traced attachment, effective timer/FD/owned kill observation before direct helper Popen creation, and one-shot inherited worker placement. Native admission remains unchanged; the trusted parent temporarily shares the original worker ceiling, returns to its bounded supervisor sibling before the exec-stop handoff, and retains refusal resources without restarting the one-second recovery grace. **205 Phase 2D / 346 complete offline tests** pass editable and fresh installed wheel under denied network/empty environment; static/build and 22 packaged-source comparisons pass. Seventeen current source files invalidate older configurations. **Production bootstrap remains incomplete**: owned namespace/watchdog setup, wrapper/init placement and terminal resource lifetime, helper/libc compilation/identity, actual effective containment and Linux pre-instruction checkpoint, fresh exact qualification and separate project/session live gate are missing. Kernel/Popen/migration/ptrace/timer effects are synthetic; no startup or host operation occurred. Readiness text, source or digests supply no authority. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, version **0.9.2**, uncommitted. Keep startup, credentials, spend, VMware/SSH and host operations disabled; no publication before complete 2D acceptance or 2E. Earlier bullets retain history.

- **Latest active 2D boundary: owned bootstrap helper/handoff source, October 9.** [Guide and exact next prompt/inputs](PHASE-2D-OWNED-BOOTSTRAP.md), [Python controller](../src/crewshal/linux_bootstrap.py), [packaged C source](../src/crewshal/bootstrap_helper.c), [25 fresh methods](../tests/acceptance/test_phase_2d_bootstrap.py) and [verification/continuity](qualification/phase-2d-owned-bootstrap-verification-v1-20261009.json) prepare a same-PID helper/native exec-event, real SIGSTOP delivery and detach handoff ending at unchanged stopped admission. Separate watchdog source arms the original absolute five-second timer before readiness; original origin persists through handoff/admission and owned refusal recovery has one-second grace. **182 Phase 2D / 323 complete offline tests** pass editable and fresh installed wheel under denied network/empty environment; static checks/build and 21 packaged source comparisons pass. Sixteen current source files invalidate prior configurations. **Production bootstrap remains incomplete**: the qualified namespace-resident direct-Popen parent, initial traced-proc attachment, compiled helper/watchdog/FD/role/timer identity and readiness-before-worker readback, effective controls, exact qualification and separate live gate are missing. All kernel/child/timer effects are synthetic; no C compilation or Linux/helper/startup operation occurred. Source and acknowledgements supply no readiness/authority. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, version **0.9.2**, uncommitted. Keep startup, credentials, spend, VMware/SSH and host operations disabled until the concrete project/session gate. No publication before complete offline and approved live 2D acceptance; no 2E. Earlier bullets remain historical.

- **Latest active 2D boundary: passive Linux envelope/bootstrap preparation, October 8.** [Guide and exact next prompt/inputs](PHASE-2D-LINUX-ENVELOPE.md), [source](../src/crewshal/linux_envelope.py), [18 fresh methods](../tests/acceptance/test_phase_2d_envelope.py) and [verification/continuity](qualification/phase-2d-linux-envelope-verification-v1-20261008.json) compile and audit per-session role/mount/argv, original systemd/controller ceilings, storage reservations and unchanged stopped-native checkpoint requirements. Prospective binding digests persist through dispatch/admission; fourteen current source files invalidate earlier configurations. **157 Phase 2D / 298 complete offline tests** pass editable and fresh installed wheel under denied network/empty environment; static checks/build/source equality pass. No child/helper/kernel setup or startup occurs. **Production bootstrap/effective controls remain missing**: current source cannot establish the retained native Popen/executable/PID/start/parent/boot/pidfd, `T`/zero-tracer, stdio-only and exact worker population before native code, independently arm the five-second deadline or recover owned admission refusals. All digests/flags remain preparation data, never enforcement or authority. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`, maintenance version **0.9.2**, uncommitted. Continue only the smallest owned compatible bootstrap source and preserved exact inputs; keep startup, credentials, spend, VMware/SSH and host operations disabled until the separate concrete batch gate. No publication until complete offline and approved live 2D acceptance; no 2E. Earlier current-state bullets retain historical achievements.

- **Latest active 2D boundary: durable retained admission/collection, October 8.** [Guide](PHASE-2D-ADMISSION-COLLECTION.md), [15 fresh tests](../tests/acceptance/test_phase_2d_admission_collection.py) and [verification/continuity](qualification/phase-2d-admission-collection-verification-v1-20261008.json) join admission, bounded supervisor capture and private terminal/scope state in one SQLite transaction. Receipt/spec/clock snapshots, private artifact links and final durable readback refuse mutation, missing/detached links, stale state and replay. Reopen and real SQL rollback pass. **139 Phase 2D / 280 complete offline tests** pass editable and fresh installed wheel under denied network/empty environment. Linux/proc/child effects remain synthetic; no startup or Linux attachment occurs. Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`; maintenance version **0.9.2**, implementation uncommitted. Canonical repository remains `forera-ai/Crewshal`, copyright `forera.ai and contributors`. Changed admission/supervisor/durable bytes invalidate prior thirteen-source prospective configurations. Production envelope/bootstrap, effective role/storage/credential/egress/hard-deadline/financial controls, fresh exact qualification and separately approved actual implementation/check remain missing. [Current continuation and exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) govern resumption. Publication waits for complete 2D acceptance; no 2E. Earlier bullets retain historical achievement evidence.

- **Copyright maintenance complete, October 8; package 0.9.2.** The owner explicitly requested `forera.ai and contributors`. README and LICENSE now state `Copyright 2026 forera.ai and contributors.`; AGENTS.md records this notice. Apache-2.0 terms and unrelated pending Phase 2D work remain intact. See the copyright maintenance closure below for base/delivery, checks and next prompt. Repository identity remains `forera-ai/Crewshal`.

- **Repository ownership maintenance complete, October 8; package 0.9.1.** Canonical repository: [forera-ai/Crewshal](https://github.com/forera-ai/Crewshal), owned and maintained by [forera-ai](https://github.com/forera-ai). Local `origin` fetch/push is `https://github.com/forera-ai/Crewshal.git`. GitHub API identity and remote branch readback match. Only ownership documentation/metadata and the synchronized patch version are included in this checkpoint; pre-existing unpublished Phase 2D changes remain local and retain their acceptance gates. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`; delivery is the commit adding [the transfer record](REPOSITORY-TRANSFER-2026-10-08.md). That record gives exact checks, limitations and next-session inputs. This maintenance boundary does not supersede the latest local Phase 2D continuation below. Historical repository URLs/version statements describe their original checkpoints.

- **Latest active 2D boundary: retained native admission source, October 8.** [Admission guide](PHASE-2D-NATIVE-ADMISSION.md) adds bounded read-only checks for an already created stopped native child: pinned proc/pidfd/PID/start/parent identity, native privilege/configuration/executable/namespace and pipe readback, actual worker/aggregate ancestry and original controls. Retained resources connect to supervisor capture. Twenty-eight fresh methods bring unpublished coverage to **124 Phase 2D / 265 complete offline tests**, passing editable and installed wheel with denied network, empty inherited environment and fresh HOME. [Verification/continuity](qualification/phase-2d-native-admission-verification-v1-20261008.json) records commands/results/failures and byte continuity. Proc/kernel/child effects are synthetic; no Linux attachment or process startup occurred. Dispatch binds thirteen source files, invalidating prior prospective configurations. Envelope/bootstrap, effective storage/role/credential/egress/hard deadline enforcement, durable admission linkage, fresh exact qualification and approved live implementation/check remain missing. Preparation-only per-project/session scope persists. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, version 0.9.0, uncommitted; no startup, credentials/provider/model/Jev, VMware/SSH, publication or 2E. [Current continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) govern resumption; previous bullets remain history.

- **Latest active 2D boundary: bounded supervisor capture source, October 8.** [Supervisor guide](PHASE-2D-SUPERVISOR-SOURCE.md) adds capture of an already admitted child through real bounded pipes and independently read pinned cgroup descriptors, with owned subtree stop, conservative incomplete/failed-stop refusal and private receipt linkage. The existing collection body and new supervision/scope records share one SQLite transaction; no general nested-transaction feature is added. Twenty-four fresh fixture methods bring unpublished coverage to **96 Phase 2D / 237 complete offline tests**. [Verification/continuity](qualification/phase-2d-supervisor-verification-v1-20261008.json) records final editable/installed-wheel checks, failures, environment and source integrity. Child/clock/kernel-stop effects are synthetic; Linux attachment and hard enforcement remain unobserved. Dispatch now binds twelve source files, so earlier prospective configurations invalidate. Production admission/launcher/envelope, actual ownership/role/credential/financial enforcement, fresh exact qualification and separately approved real implementation/check remain missing. [Current next prompt/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) govern resumption. Preparation-only per-project/session scope persists. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, version 0.9.0, uncommitted; no startup, credential/provider/model/Jev, VMware/SSH, publication or 2E. Historical/other dirty bytes remain intact; intentional source updates are supervisor, dispatch, collection and durable integration. Prior bullets remain history.

- **Latest active 2D boundary: source-bound native/proxy dispatch preparation, October 8.** [Preparation source join](PHASE-2D-DISPATCH-PREPARATION.md) now compiles literal pinned-native/proxy argv, separate task stdin, intended environment and original ceilings, bound to eleven current coordinator source files, exact batch, task/check and launch context. Complete preparation reads back the independently retained batch and refuses stale/missing qualification, changed choices/source/settings, terminal attempts and expanded fixture scope. Fourteen fresh methods bring unpublished coverage to **72 Phase 2D / 213 complete offline tests**, passing editable and freshly installed wheel under denied network/empty environment; lint/format/strict typing/offline build pass. [Verification/continuity](qualification/phase-2d-dispatch-preparation-verification-v1-20261008.json) and [current continuation/input set](PHASE-2D-CONTINUATION-2026-10-08.md) govern resumption. This is inert data, not a Linux envelope, launcher, supervisor observation or execution/spend gate. Those capabilities and exact live qualification/implementation/check remain missing. Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, version 0.9.0, uncommitted. Earlier source/artifact/dirty bytes are preserved; only maintained documents change. No live operation or publication occurred. Previous bullets/next-session sections are historical.

- **Latest active 2D boundary: production capture/revision integration, October 8.** [Coordinator collection](PHASE-2D-PRODUCTION-CAPTURE.md) now persists stopped Codex terminal/capture/claim/usage/scope data in one SQLite transaction and binds changed frozen candidate bytes without losing launch provenance or copying old approvals. Final verdict requires independent current candidate/capture readback; stale state, replay, mutation, false completion and SQL failure refuse. Eighteen independent fresh methods bring unpublished coverage to **58 Phase 2D / 199 complete offline tests**, passing editable and freshly installed wheel with denied network/empty environment; lint/format/strict typing/build pass. [Verification/continuity](qualification/phase-2d-production-capture-verification-v1-20261008.json) and [updated next prompt/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) govern resumption. Production launcher/supervisor, exact changed-profile qualification and separately approved live implementation/check remain missing. Preparation-only per-project/session choices remain controlling. Base stays `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, version 0.9.0, uncommitted. Original 2C and earlier dirty preparation bytes are preserved except intentional maintained documents and the current durable integration. No startup/provider/model/Jev, credential access, VMware/SSH, version bump, commit/push or 2E occurred. Earlier bullets remain historical.

- **Latest active 2D boundary: per-project/session preparation selection, October 8.** Owner clarified **“just do the preparation with ability to select on each project/session”.** [Selection/readback](PHASE-2D-SESSION-SELECTION.md) now accepts explicit model and optional route/billing/credential choices without ambient/default inheritance into a selected context. Bounded readback refuses different contexts, mutated files/references/declarations, unknown entries, links and candidate mode changes. Seven fresh methods bring unpublished 2D coverage to **40 / 181 complete offline tests**, passing editable and installed wheel with denied network/empty environment; lint/format/strict typing pass. [Exact example](qualification/phase-2d-session-selection-v1-20261008.json), [verification/continuity](qualification/phase-2d-session-selection-verification-v1-20261008.json) and [current continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) govern next work. Live route/billing/credential decisions are deferred to each project/session; no global answer is needed now. Production dispatch/profile and separately approved live acceptance remain pending. Base stays `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, package 0.9.0, changes uncommitted. Original 2C and previous preparation records remain intact. No native/provider/model/Jev, VMware/SSH, credential-store, version, commit/push or 2E operation occurred. Previous bullets remain historical checkpoints.

- **Latest active 2D boundary: batch preparation only, October 8 resumption.** Owner selected **Sol6.1**, then explicitly clarified **“Batch preparation only.”** [Concrete preparation](PHASE-2D-BATCH-PREPARATION.md) preserves eleven exact fixture/check/template artifacts, eight original historical references and false startup/spend/qualification flags. Official documentation maps the label to `gpt-6.1-sol`; pinned CLI/account access is unobserved. Seven additional fresh methods bring unpublished 2D coverage to **33 / 174 complete offline tests**, passing both editable and installed wheel under denied network/empty environment. Build/lint/format/typing pass. Version stays 0.9.0; no live native/provider, credentials, VMware/SSH, commit/push or 2E. Production envelope/qualification and live execution/spend gate remain missing. [Preparation record](qualification/phase-2d-batch-preparation-v1-20261008.json), [verification/continuity](qualification/phase-2d-batch-preparation-verification-v1-20261008.json) and [current exact continuation](PHASE-2D-CONTINUATION-2026-10-08.md) govern next work; earlier entries remain historical.

- **Active milestone: Phase 2D incomplete, October 8 offline boundary.** Base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`; version remains **0.9.0**. Unpublished work adds inert pinned-Codex request/event normalization, disposable candidate/freeze/scope manifests and trusted validator capture with existing SQLite integrity. All **26 fresh 2D methods / 167 complete offline tests** pass on macOS under denied network, both editable and freshly built installed wheel; lint/format/strict typing pass. No product launcher, guest/runtime/model/provider operation, credential-store access, version bump, commit/push or 2E. Production dispatch remains unimplemented/unqualified and the required owner-approved live implementation/credential-free check gate is absent. See [offline contracts and evidence](PHASE-2D-OFFLINE-CONTRACTS.md), [concrete missing execution/spend gates](PHASE-2D-EXECUTION-GATE.md), [current continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md) and [continuity](qualification/phase-2d-offline-continuity-20261008.json). This bullet governs active work; all previous milestones and unknowns below remain historical evidence.

- **Current: Phase 2C complete; version 0.9.0.** One fresh v18 Linux aarch64 native/proxy profile passes all twenty original cases independently twice and exercises both actual native file tools. Original protocol, limits, grants and historical bytes are preserved. See [completion assessment](PHASE-2C-COMPLETION-ASSESSMENT.md), [independent readback](qualification/phase-2c-direct-linux-native-full-readback-v18.json) and [false-permission decisions](qualification/phase-2c-direct-linux-native-full-decision-v18.json). Current cleanup is independently verified, 60 source files/configurations preserved outside `/run`, roles/slice/helpers removed, prepared roots retained, SSH disconnected and VM left running. Lost v5 cause/original cleanup remain unknown. Windows/macOS runtime compatibility remains unknown. Offline suite: 141 passed. No paid call or Phase 2D work. Next: [separately gated 2D prompt and exact inputs](PHASE-2D-NEXT-SESSION-2026-10-08.md). Earlier bullets below describe historical checkpoints; they do not override this state.


- **Latest owner update, October 8, after the offline checkpoint:** the owner restarted the existing VMware Ubuntu installation, requested SSH retry and explicitly answered “Reconnect and resume 2C checks.” The earlier test stop is superseded for this local continuation only. SSH and sudo succeed; aarch64/kernel 7.0.0-38-generic were reobserved. No droplet, paid operation or production execution is authorized; standing milestone publication applies only after verified completion. See [the credential-free authority record](qualification/phase-2c-local-resumption-approval-20261008.json). The offline-only prompt below is historical; this current local authorization controls. Phase 2C remains incomplete and unpublished.

- **Historical owner stop, October 8, subsequently superseded by explicit local resumption:** stop VMware and Linux tests; continue source development for all platforms including Linux. Local offline checks on macOS only. Do not reconnect for tests, inventories, cleanup or authentication; do not substitute another Linux environment. New explicit owner instruction is required to change that restriction. [Current prompt and exact inputs](PHASE-2C-OFFLINE-NEXT-SESSION-2026-10-08.md) supersede earlier continuation directions.
- **Latest unpublished state:** fresh full v4 fails global instruction exclusion. Fresh v5 reaches the independent validator then refuses cgroup control readback; raw evidence failed to transfer after SSH timeout. Final v5 cleanup and remaining prepared roots/helpers are unknown. Portable two-run bundle audit now passes 26 fresh macOS fixture methods within the 119-test offline suite, including policy/directory alias and nonfinite JSON refusal; it always reports runtime verification and execution permission false. Original twenty-case same-profile qualification remains incomplete. Package stays **0.8.20**, base `21e3686`; no commit/push/Phase 2D.

- Repository: `forera-ai/Crewshal`, owned and maintained by `forera-ai`; display name Crewshal, pronounced like crucial; Apache-2.0. Earlier repository ownership is historical.
- Phases 0, 1, 2A and 2B complete. The initial architecture direction remains accepted. Package version: **0.8.20**. **Active milestone: blocked 2C; next session resumes 2C.**
- Accepted direction: local Python coordinator, versioned models, SQLite state, Codex/Claude Code adapters, independent provider review where required, trusted revision-bound evidence and qualified isolation. Phase 2A delivers passive discovery, explicit correction/confirmation and private external JSON model storage. Phase 2B adds private SQLite records/events, compare-and-update versions, explicit migration, inert launch-intent reconciliation, captured artifact integrity and deterministic evidence/waiver/usage rules. No runtime launcher exists; every verdict keeps execution disabled. Phase 2C added closed qualification/refusal records and frozen synthetic Linux probes. Nine bounded filesystem/environment cases and four separate lifecycle/validator cases passed twice. Complementary subsets are not a combined qualified profile; a separate twelve-attempt synthetic network subset also passed twice. Full native-runtime/network boundaries remain unproved. The 0.7.0 checkpoint freezes the SBX resource/configuration protocol and records two help-only assessments; direct sizing conflicts with the 128 MiB worker ceiling, nested enforcement and isolated credential-store operations remain unavailable. The 0.8.0 checkpoint demonstrates a disposable Linux SBX synthetic file store twice in separate unprivileged Ubuntu containers, without macOS Keychain or login. The store domain prerequisite is observed, but those inspected fixtures lack a KVM device/sysfs entry; a supported operational host, approved outer envelope and caller/request authority remain unavailable. No new mandatory whole-runtime operational criterion passed. Full qualification stays denied and credential mediation remains unresolved.
- Latest 0.8.1 checkpoint: an owner-supplied temporary Ubuntu 24.04.5 x86_64 VPS demonstrates KVM API 12, VM/vCPU creation and two actual trusted 1 MiB HLT executions. The host capability prerequisite is observed on that host; SBX operational configuration and all whole-runtime boundaries remain unqualified. No remote file/package, broker or native runtime was created; final process/FD inspection found no remaining VM/vCPU handles and SSH disconnected. The owner intends to delete the host. Do not assume continuing access or reuse its credentials; reverify any replacement. See [the exact host evidence](KVM-HOST-ASSESSMENT.md).
- Latest 0.8.2 preparation checkpoint: official Linux amd64 SBX bundle downloaded, extracted and digest-matched locally. No bundled code was executed. The [concrete operational proposal](SBX-OPERATIONAL-PROPOSAL.md) specifies a pending 512 MiB guest inside a 768 MiB aggregate host envelope, one CPU, 8 GiB fixture disk and 600-second total experiment, preserving original inner worker limits. Current host SSH access and owner resource approval were requested but are not supplied in this session at closure. Missing identities/enforcement remain blocking even after approval.
- Latest 0.8.3 host/help checkpoint: the previous VPS was deleted. The first replacement passes HLT twice but fails memory admission; a second owner-supplied temporary Ubuntu x86_64 host now passes HLT twice and sampled memory/disk headroom. Exact amd64 SBX bytes are reverified and source-bound Linux version/help succeeds twice. See [first refusal](REPLACEMENT-HOST-ASSESSMENT.md), [current preflight](AMD64-HOST-PREFLIGHT.md), [inner checklist](PHASE-2C-READINESS.md) and [non-executable readiness snapshot](qualification/phase-2c-readiness-v1.json). Owned diagnostic files/services were removed; no daemon/store/native/provider operation ran. Resource approval remains unanswered; quota/aggregate/inner controls, operational identities and trusted dispatch remain unresolved. No new whole-runtime case passes.
- Latest 0.8.4 checkpoint: the owner directly approved the unchanged operational resource envelope. See [approval and freeze status](RESOURCE-APPROVAL-AND-FREEZE-STATUS.md) and [digest-bound authority record](qualification/phase-2c-resource-approval-v1.json). Current SSH alias/user/authentication was requested but not supplied. No remote connection or operational/inner/native test ran. Operational identities and controls remain unresolved; approval clears only resource authority. Historical pending-approval documents remain immutable.
- Latest 0.8.5 checkpoint: newly supplied host passes two frozen HLT runs and sampled admission; exact SBX and Codex template bytes are prepared and verified without template/native execution. See [current evidence](CURRENT-HOST-IDENTITY-PREPARATION.md). Full operational configuration/freeze and inner enforcement remain blocked. A [bounded daemon/settings diagnostic](DAEMON-CONFIG-DIAGNOSTIC-PROPOSAL.md) awaits an explicit owner exception and has not run. Keep the current droplet until all required host work is finished; verified preparation artifacts remain there. No further droplet is requested.
- Latest 0.8.6 checkpoint: owner selected continuation on the supplied droplet; the exact bounded daemon/settings diagnostic runs twice in fresh private systemd fixtures. Both exit zero with identical settings, effective host-service controller/namespace samples and empty final owned-unit/process/KVM inventories. See [the assessment](DAEMON-CONFIG-DIAGNOSTIC-ASSESSMENT.md). Full operational identities, inner controls and caller/request authority remain unavailable; no inner/native probe ran. The diagnostic decision is resolved for that exact scope. Keep the current droplet and artifacts; no further droplet or unchanged-envelope approval is needed.
- Latest 0.8.7 checkpoint: [private configuration and host quota controls](CONTROL-RESOLUTION-ASSESSMENT.md) are recorded. Settings reproduce twice. Physical quota accepts oversized sparse logical files; a combined file-size/inode quota/hardlink-denial host prototype passes in two fresh fixtures. Native compatibility and inner placement remain unqualified. A [bounded infrastructure-discovery ordering proposal](PHASE-2C-INFRASTRUCTURE-DISCOVERY-DECISION.md) awaits the owner decision; no guest runs under it. Full manifest/inner/caller authority remain unavailable. Keep the droplet and preparation artifacts.
- Latest 0.8.8 checkpoint: bounded discovery ordering approved in a separate digest-bound record. [Actual discovery admission](GUEST-DISCOVERY-ASSESSMENT.md) preserves initial device-policy denial; corrected fresh services observe aggregate limits and HLT passes twice each. Both mountless create attempts refuse Docker authentication. Login is excluded and no SBX guest runs. Full freeze/inner/native gates remain unavailable. Keep the droplet/artifacts; next capability is separately authorized isolated Docker authentication or supported unauthenticated dispatch, not new resource/discovery approval.
- Latest 0.8.10 checkpoint: [isolated Docker authentication](ISOLATED-DOCKER-AUTHENTICATION.md) succeeds, retained private state authenticates two fresh denied-network listings, and exact OCI metadata/archive are prepared. Supported template load fails repeatedly with bounded ENOSPC diagnostics. Resolve runtime-compatible independent logical/allocated fixture storage; full freeze/inner/native remain unavailable. Keep host/account/artifacts; do not request another login or droplet.
- Latest 0.8.11 checkpoint: [bounded storage investigation](STORAGE-CONTROL-INVESTIGATION.md) records unqualified existing-filesystem/layout candidates and independent compatibility/exhaustion requirements. Current retained-host connection details are absent from this chat and were requested. No fresh remote operation, complete freeze or qualification run occurred; all prior authentication/import observations remain immutable. Keep the host/account/preparation.
- Latest 0.8.14 local storage checkpoint: [design/accounting](PHASE-2C-STORAGE-DESIGN.md) and [staged Linux batch](PHASE-2C-STORAGE-BATCH.md) deliver conservative layer arithmetic and bounded synthetic file-operation diagnostics, with twelve new offline methods (90 total). A naive encrypted upper/lower historical disk layout exceeds the logical ceiling. eCryptfs remains a conditional mechanism experiment; supported private key setup, bypass/independent observer evidence and pinned SBX compatibility are unresolved. Two macOS fixtures retain unavailable optional operations; initial xattr-API failure and correction are recorded. Fusion reports zero running VMs; no guest access/start, Linux key/mount, SBX or paid-host test occurred. Local disposable Ubuntu shell access was requested but not supplied at closure. No routine VPS/access or unchanged-envelope approval request is required. All execution/native flags stay false.
- Latest 0.8.15 local Linux checkpoint: [two fresh eCryptfs fixtures](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md) deliver 44 independently matched FD/PID/inode observations. Supported exclusively new keys/mounts, effective aggregate controls, small regular growth, oversized ENOSPC and scoped cleanup are observed. Unsupported preallocation/copy/reflink/hole operations remain compatibility gaps; full pinned-runtime/guest/inner/native/broker qualification stays denied. The owner confirmed a test-only Ubuntu guest and supplied authentication directly; it reports Ubuntu 24.04.5 aarch64/kernel 7.0.0-38-generic, not amd64 equivalence. Existing Fusion guest was started and left running; keyutils installed, no SSH service, credentials in Git, SBX or paid host. All owned runtime/preparation/report artifacts removed; raw public evidence and failed profiles preserved. Offline suite: 93 tests. Next milestone resolves actual pinned runtime filesystem/cache/disk requirements and a supported admissible layout.
- Latest 0.8.16 requirements checkpoint: [pinned storage research](PINNED-SBX-STORAGE-REQUIREMENTS.md) verifies fresh SBX archive/all eleven members as data, binds nine public source files and two release statements, and identifies dirty/private containerd/diskfs/engine replacements plus declared private EROFS patches. Operation-specific fallbacks remain conditional; selected engine/VMM paths and a supported admissible layout are unresolved. Pruned hypothetical 3g+1g upper/lower ledger totals 9697333533 logical bytes and refuses. Unknown inventory also refuses. No SBX/runtime, VM access or paid host ran; full 2C/inner/native qualification remains denied. Next scope is the exact storage contract/layout, not another unchanged import or routine host request.
- Current owner policy, 2026-10-05: owner confirmed droplet removal after revoking retention. No routine per-session VPS tests/access requests. Complete substantive changes first; use local checks/VMware Ubuntu where sufficient. Request approval for a droplet batch only if a necessary acceptance check cannot be satisfied locally. Host-only private account/preparation must not be assumed available; do not recover ambient credentials. See AGENTS.md.
- Owner declaration: each phase or major portion gets a separate session, tracked achievements, independent acceptance checks, updated handoff and next-session prompt. AGENTS.md makes this persistent for future sessions.
- Boundaries: clean independent work; preserve private-source confidentiality; no paid runs, agent writes, evaluation or publication without their applicable gates. Four-stack evaluation remains later work.
- Current local branch: `codex/phase1-architecture`. Initial published main revision: `04d6f68e1914285fc660606348cd0a5616d1152f`. The owner subsequently authorized automatic remote branch pushes at every commit; follow the publishing ceremony in AGENTS.md. Package-registry releases and merges remain separately gated.
- Local checkout is named Crewshal. The desktop project's saved path still reported the old Foreman directory during preparation. Open the actual Crewshal checkout when starting the next session; do not create another repo or overwrite a checkout to compensate.

- Latest 0.8.17 checkpoint: [release-era storage contract boundary](PHASE-2C-STORAGE-CONTRACT.md) resolves documented ROOT_SIZE, XDG roots and Docker creation-override/readback distinction. Seven exact private-fork/VMM/layout/enforcement fields remain unanswered. Smaller disk arithmetic refuses; no supported layout selected, runtime/VM/host/vendor operation or new qualification pass. See the contract record and exact continuation inputs.

- Latest 0.8.18 checkpoint: current SBX pilot route receives a bounded NO-GO; [direct Linux replacement topology](decisions/0003-direct-linux-qualification.md) is proposed for owner decision. Twenty cases are preserved and mapped; [read-only admission batch](PHASE-2C-DIRECT-LINUX-ADMISSION.md) is prepared. No replacement Linux/native/broker observation occurred; qualification and agent execution remain denied.

- Latest 0.8.19 checkpoint: ADR 0003 is directly owner-approved in a separate bound record. Actual owner-accessible aarch64 Linux admission and two fresh final kernel mechanism fixtures pass; source/helper/library/kernel bindings, failed variants, independent storage/FD/controller/lifecycle readback and external cleanup are preserved. See [assessment](PHASE-2C-DIRECT-LINUX-ASSESSMENT.md). Official matching-platform native/proxy bytes are deliberately prepared and bound; isolated version/help passes twice. Actual sandbox startup refuses under Ubuntu AppArmor before payload. A fixture-only role-policy proposal parses without loading and awaits the requested owner host-policy decision; native/tool separation, native compatibility and all twenty mandatory same-profile cases remain unavailable. This does not qualify execution. Existing Linux remains running; no authentication is part of public inputs.

- Latest 0.8.20 checkpoint: the fixture-only v2 policy is directly approved and was loaded under unchanged limits. Eight trusted setup attempts preserve actual failures; direct systemd UID/GID 65534 reaches native namespace mapping, which AppArmor denies as a disconnected proc path. A fixture-local chroot-relative correction also refuses. Setup-only v4 `attach_disconnected` parses but has never been loaded; its documented alias risk needs the directly requested owner decision. All owned profiles/data/services/cgroup were removed; global userns restriction remains 1. No native payload, broker or mandatory same-profile case passed. See [the concrete blocker and scoped proposal](PHASE-2C-NATIVE-POLICY-ASSESSMENT.md).

- Working continuation, 2026-10-08 (unpublished): scoped v7 policy resolves native startup; tiny native v8 and official proxy v3/v6 have two-run subset evidence, with supervised SIGTERM recorded honestly. Full v1/v2 failed readonly-cwd preparation; full v3 reached the payload but failed ENOSPC and exposed a synthetic instruction marker. Full v4 preparation/freeze passed, but its workload never ran. All twenty original same-profile cases, sequential validator and lifecycle stages remain incomplete. Read [the current assessment](PHASE-2C-NATIVE-CONFORMANCE-ASSESSMENT.md), [exact working inputs](PHASE-2C-ACTIVE-CONTINUATION.md) and [October 8 next-session prompt](PHASE-2C-NEXT-SESSION-2026-10-08.md) before resuming. This session's guest roots/copies were removed; inherited preparation, aggregate slice, scoped v7 policy and the running VM remain. Original 577 files were hash-unchanged before continuity edits; focused refusal suite passed 11 tests. **Latest owner publication gate: only after verified 2C completion.** Version stays 0.8.20, no commit or push.

## Start-of-session procedure

1. Open the Crewshal checkout. Read AGENTS.md, this document, DEVELOPMENT-PLAN.md and the relevant architecture/ADRs. Check branch, HEAD, status and graph freshness; preserve unrelated dirty work.
2. Name one active milestone and its prerequisites. Verify the prior checkpoint and acceptance evidence instead of assuming completion from chat.
3. Implement, test and deliver only that scope. Update this handoff and the plan, checkpoint the work, provide the next standalone session prompt and stop at the boundary.

## Current next-session prompt — consolidated Phase 2D completion

Use [the accepted bootstrap source boundary and exact inputs/prompt](PHASE-2D-INSTALLATION-BOOTSTRAP-2026-10-10.md#exact-continuation). The owner approved upfront same-original-observer charging in ADR 0006; charge/unknown-result and finite directory custody source is verified, but effective physical-domain/root/journal combined-growth installation is still missing and its payload gate deliberately stays closed. Do not reask this or prior retention/subscription/authentication/Ubuntu decisions. Current base is pushed 758079b / 0.11.0 with subsequent uncommitted source. Complete the effective installation/growth producer, original-volume readonly freeze/credential-free validator and installed identities before preparing concrete separately authorized exact Linux/live acceptance. Keep original observer/timer/charges/handles/unknowns/ceilings/origins/grace/reserve; all three syntax attempts are consumed. Full 2D stays incomplete/unqualified. Publish the version/README/changelog/handoff/commit and push after full acceptance; no release/reuse or 2E.

## Historical next-session prompt — Phase 2D effective retained storage reference closure, 0.10.0

The source checkpoint's exact prompt/input chain remains immutable history. Current owner scope and accepted ADR 0004 are above; do not treat the earlier closure-only scope or unanswered retention decision as current.

## Historical next-session prompt — Phase 2D effective retained storage reference closure, 0.9.2

Resume **2D preparation only** from [the retained storage-owner guide's exact prompt and complete inputs](PHASE-2D-LINUX-STORAGE-OWNER.md#next-boundary-exact-prompt-and-inputs). Address only the effective retained reference-closure mechanism and trusted storage-owner handoff through accepted namespace/private anonymous keyring/ext4/eCryptfs/owned loops. Empty proc scans, path absence, exit codes, PID text and caller flags cannot authorize release. Include taskless namespaces, deleted-open/mapped/socket-passed/asynchronous kernel holders, additional/delayed loops and concurrent mutation; keep unknowns and handles retained. If accepted mechanisms cannot supply closure within original controls, record the exact incompatibility and smallest consequential owner decision. Preserve all original limits, terminal/admission ordering and deadlines; source remains unqualified. Invoke no compiler, fork, Popen, kernel operation, credentials, spend, VMware/SSH or host activity. Parent installation/effective controls/observer handoff/exact qualification of twenty-one sources and separate live acceptance remain mandatory. Preserve version 0.9.2 and dirty/historical bytes. Record reproducible offline evidence, update handoff and stop; publish only after complete 2D acceptance, no 2E.

## Historical next-session prompt — Phase 2D owned physical-resource teardown and parent binding

Resume **2D preparation only** from [the owned setup guide's exact prompt and complete input set](PHASE-2D-OWNED-SETUP.md#next-boundary-exact-prompt-and-inputs). Preserve forera-ai/Crewshal, copyright forera.ai and contributors, maintenance version 0.9.2, per-project/session choices and dirty/historical bytes. Implement only owned physical-resource teardown source and trusted namespace-parent program/inventory binding: retained mount/key/backing and FD/cgroup release order after independently observed terminal watchdog/parent/wrapper and empty target groups. Do not authorize reuse from process emptiness, PID text or prospective hashes, or while the watchdog survives. Preserve bounded observer/setup/supervisor/worker siblings under original aggregate, unchanged native admission, original five-second origin and one-second grace. Current startup/kernel/compiler source must not be invoked. Exact helper/root/library identities, effective controls, Linux checkpoint/inheritance qualification of all eighteen sources and a separate concrete project/session live batch gate remain mandatory. Keep startup, credentials, spend, VMware/SSH and host operations disabled. Record independent offline evidence, update handoff and stop at the next verified or blocked source boundary; publication waits for complete 2D acceptance, no 2E.

## Historical next-session prompt — Phase 2D owned setup and terminal lifetime source

Resume **2D preparation only** from [the parent/watchdog bridge guide's exact prompt and complete input set](PHASE-2D-PARENT-WATCHDOG.md#next-boundary-exact-prompt-and-inputs). Preserve forera-ai/Crewshal, copyright forera.ai and contributors, maintenance version 0.9.2, explicit per-project/session choices and all original/dirty/historical bytes. Implement only owned namespace/watchdog setup and terminal resource lifetime source through accepted mechanisms: retained controls for the namespace parent, bounded wrapper/init placement, fixed-FD watchdog creation before worker creation and observed terminal cleanup without retry/reset/reuse while the watchdog survives. Do not invoke the current Popen/migration/ptrace source on the host. The inheritance topology, compiled helpers/effective controls and pre-instruction Linux checkpoint still require fresh exact qualification of all seventeen bound files. Preserve unchanged native admission, original five-second origin and one-second recovery grace. Startup, credentials, spend, VMware/SSH and host operations remain disabled until a separately recorded concrete project/session batch gate. Record independent offline evidence, update handoff and stop at the next verified or blocked source boundary; publication waits for complete 2D acceptance, no 2E.

## Historical next-session prompt — Phase 2D dispatch preparation boundary

Resume **2D only** from this handoff and [the current standalone prompt/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md). Preserve preparation-only scope, explicit per-project/session choices, all original ceilings, historical records and dirty bytes. Read [dispatch preparation](PHASE-2D-DISPATCH-PREPARATION.md), source/tests/verification, prior collection/preparation source/evidence and accepted architecture. Build only bounded Linux supervisor source through the accepted native/proxy mechanisms, supplying trusted stopped capture to `collect_codex_attempt`; do not replay/wrap the 2C fixture driver or construct observations. Bind any prospective configuration to the exact batch/task/check/launch/source digest and freshly qualify that profile; v18 eligibility cannot transfer. Keep runtime/validator startup, credentials, provider/model/Jev spend, VMware/SSH and host operations disabled until concrete project/session identities and the separately recorded execution/spend batch gate exist. Do not request a global route or treat prepared argv as authority. Record independent evidence and the smallest remaining capability/gate; update handoff and stop at the next verified or blocked boundary. Publish only after complete offline and approved live 2D acceptance; no 2E.

## Achievement ledger

### Phase 0 / initial repository — 2026-10-01

Delivered AUDIT.md, COMPETITIVE-LANDSCAPE.md, PRODUCT-HYPOTHESIS.md, INITIAL-EVALUATION-PLAN.md, naming ADR, README, Apache-2.0 and repository initialization. Public initial checkpoint: `04d6f68e1914285fc660606348cd0a5616d1152f`. Name collision screening was bounded, not legal clearance. Proprietary predecessor evidence is owner-only, not publicly reproducible. No product performance/security benchmark passed or was claimed.

### Phase 1 / architecture and session workflow — 2026-10-02

Delivered Phase 0 closure, architecture, consequential ADR, updated status documents, persistent AGENTS.md, development plan and this rolling handoff. Owner authorized continuing after presentation and required separate sessions. The architecture covers the mission's domain/discovery/adapters/capabilities/workflow/policy/evidence/risk/routing/security/state/observability areas.

Evidence: local Codex/Claude CLI version/help inspection, current primary documentation and source review supported feasibility only. Documentation verification: an inline Python checker passed for all 12 Markdown files (local links, balanced fences, whitespace, milestone IDs and architecture topic coverage); `rtk proxy git diff --check` and `rtk proxy git diff --cached --check` passed. The initial topic check found that the domain heading lacked an explicit label; the heading was clarified and the checker rerun successfully. There are no executable runtime tests at this milestone; isolation, credential treatment, runtime contracts and comparative advantage remain unproved. No model calls, paid benchmarks, container probes or private credential inspection were performed. Local Git delivery revision is recorded by the milestone commit containing this entry; resolve it with `git log -1 --format=%H -- docs/HANDOFF.md` at this checkpoint rather than embedding a self-referential hash here.

### Phase 2A / Python foundation and passive initialization — 2026-10-02

Completed this milestone only. Base revision: `fa588e2d01e324399d01b1846fcea2dc26016631` on `codex/phase1-architecture`; checkout was clean. Delivery revision is the local milestone commit containing this entry; resolve it with `git log -1 --format=%H -- docs/HANDOFF.md` at this checkpoint. No push, PR, merge or release occurred.

Artifacts: installable `pyproject.toml`/src-layout `crewshal` package; closed schema-version-1 Pydantic contracts; bounded TOML/JSON discovery; explicit interactive and digest-bound decision replay; provenance-preserving correction/invalidation; private external model state and explicit non-overwriting exports; `tests.acceptance.test_phase_2a`; hash-locked `requirements-dev.lock`; [development/setup guide](DEVELOPMENT.md); updated README and milestone plan. Builds produced ignored `dist/crewshal-0.1.0.tar.gz` and `dist/crewshal-0.1.0-py3-none-any.whl`, not published artifacts.

Acceptance evidence, all confirmed:

1. Python/Hatch commands and TypeScript package/workspace fixtures produce literal candidates, relative manifest-key source locations and independently checked SHA-256 digests. Workspace facts depend on both root/member inputs.
2. Observed, strong/weak inference, unknown and pending/confirmed/rejected states stay separate. Empty/malformed inputs, absent commands/members and conflicting lockfiles remain visible unresolved data. Unknown confirmation without correction is refused.
3. Malicious instruction/setup/script fixtures never execute, even after a command candidate is explicitly confirmed. Symlink escape, private-file, file-count, per-file-size, aggregate-byte and nesting exclusions are visible.
4. Scripted interactive input corrects/rejects/confirms facts, preserves source provenance and inspects stored validated models. Noninteractive defaults stay pending; replay requires explicit local decisions bound to the current model. EOF, stale/malformed batches and unknown IDs refuse materialization.
5. Changed member manifests invalidate member/root-dependent workspace facts while unrelated root check confirmations survive. Unrelated file changes preserve decisions. Removed inputs revoke active facts; source mutation during interaction refuses save. Unsupported versions (including boolean coercion), extra fields, malformed JSON and unbound confirmations are refused.
6. Synthetic original/uncommitted file bytes remain identical after ordinary initialization; state is outside the repository with directory/file modes 0700/0600. State symlinks, repository-local state, path-escaping exports and overwriting existing files are refused. Explicit exports have no private root/state metadata and never become approvals.
7. Fresh built-wheel installation exposes help and actual console-entry-point initialization. Acceptance and full offline suites create all their own fixtures, with empty inherited environment, temporary home and OS-level network denial. No previous model/state artifacts or provider credentials are needed.

Exact verification and environment:

- Observed host: macOS 27.2, build 26B5091g, arm64. Interpreter: CPython 3.12.14 (`/opt/homebrew/opt/python@3.12/bin/python3.12`). uv 0.9.24; RTK 0.50.0. Direct runtime dependency Pydantic 2.12.5; Pydantic Core 2.41.5. Development dependencies mypy 1.18.2 and Ruff 0.14.1; build backend setuptools 80.9.0. All development/runtime transitive versions/hashes are recorded in requirements-dev.lock.
- Setup: `rtk proxy uv venv --python python3.12 .venv`; `rtk proxy uv pip install --python .venv/bin/python -e '.[dev]'`; `rtk proxy uv pip compile pyproject.toml --extra dev --generate-hashes --output-file requirements-dev.lock`. Package/dependency preparation used the package index; test execution did not.
- `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a`: passed during development; final artifact verification runs the expanded 12-case module below. No test count is inferred from earlier runs.
- `rtk proxy .venv/bin/ruff check src tests`: passed. `rtk proxy .venv/bin/ruff format --check src tests`: passed (9 files). `rtk proxy .venv/bin/mypy`: passed, strict, 6 source files. Repeated against the fresh verification environment.
- `rtk proxy uv build --offline`: built sdist and wheel successfully, using the cached pinned backend.
- Fresh verification directory: `/private/tmp/crewshal-2a-verify.EYFzX8`. `rtk proxy uv venv --python python3.12 "$crewshal_verify_dir/fresh"`; `rtk proxy uv pip install --offline --require-hashes --python "$crewshal_verify_dir/fresh/bin/python" -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python "$crewshal_verify_dir/fresh/bin/python" dist/crewshal-0.1.0-py3-none-any.whl`: passed after dependency-cache preparation. Application imports resolved to external site-packages, not editable src. Temporary directory is optional evidence, not a prerequisite for rerunning fixtures.
- With `crewshal_verify_dir` set to that external directory and its home created: `rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' "$crewshal_verify_dir/fresh/bin/python" -m unittest tests.acceptance.test_phase_2a`: **12 tests passed**. Same wrapper with `-m unittest discover -s tests -t .`: **12 tests passed**. Installed `crewshal --help`: passed; console `crewshal init` is exercised by the acceptance module.
- Markdown local links/fences/whitespace and required current/next-milestone markers checked; `rtk proxy git diff --check` and staged diff check passed before commit. See [development guide](DEVELOPMENT.md) for reproducible setup and network-denial wrapper.
- Jev CLI live availability and a bounded offline-verification decision were checked successfully (decision probability 0.9). Jev was assistant workflow support explicitly requested by the owner, not product/runtime execution. Product tests call no model.
- Codebase-memory CLI was available throughout. Verify-tier startup graph generation was `2026-10-01T23:46:50Z`; refreshed after implementation. Structural search, both-direction CLI trace, exact source snippets and coverage checks informed inspection. Relevant production paths had no recorded gaps; changed test ranges were read directly and the final tree reindexed. Excluded metadata/caches are not runtime evidence; graph cleanliness is not completeness proof.

Failures retained and resolved: the first acceptance test failed because no package existed; subsequent schema refusal exposed Pydantic accepting `true` as literal version 1, fixed by an exact integer validator; one newly added test initially had a misplaced test-body tail (`NameError`), corrected before reruns. The first fresh offline hash-locked install lacked cached wheel archives, so it failed; dependency preparation populated the cache and a new environment then installed fully offline. The first staged whitespace check found a surplus blank line at the end of pyproject.toml; it was normalized and the staged check rerun. None of these failed attempts is counted as acceptance success.

Limitations: verified only on the recorded macOS/Python combination, not Linux/Windows or other Python versions. Discovery supports the documented bounded formats; YAML and other Python build systems remain visibly unsupported. Fingerprints are file-granular; discovery is not an atomic snapshot against adversarial concurrent mutation. Source digests do not prove truth. Exports retain literal repository values/human corrections and must be inspected before sharing; they carry no execution authority. Current JSON storage is atomic model replacement only, with no two-writer conflict detection, migrations, launch reconciliation or trusted evidence persistence. The network-denied test wrapper does not qualify worker execution. No execution adapter, provider SDK, benchmark, container probe, runtime credential-store inspection, hold-out exposure or private predecessor source was used. Agent writes remain disabled; 2C qualification and later owner gates are unchanged.

### Phase 2A / publishing closure — 2026-10-02

The owner added standing publishing rules after the implementation checkpoint: push after every commit without another confirmation; include a semantic version bump, README and changelog updates in each new commit; update handoff and provide next-session prompt/input files; end development when the milestone is complete. Persisted these rules in AGENTS.md and README.md and introduced CHANGELOG.md. This closure bumps 0.1.0 to **0.1.1** for compatible documentation/process maintenance; no Phase 2B development is included.

Base: `849b7fcc2b6f23894a5caf2de73ac435fd59b637`. Delivery: the commit containing this closure entry, resolved with `git log -1 --format=%H -- docs/HANDOFF.md`. Push the current `codex/phase1-architecture` branch to `origin` (`https://github.com/prooshani/Crewshal.git`) under the owner's authorization; verify the remote branch matches the delivery revision and report the outcome at closure. Earlier no-publication statements in the achievement ledger describe their original checkpoints.

Verification passed: `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a` and `rtk proxy .venv/bin/python -m unittest discover -s tests -t .` (12 cases each); Ruff lint/format and strict mypy (commands above); `rtk proxy uv build --offline --quiet`; offline installation of the 0.1.1 wheel into the external verification environment; installed metadata and crewshal.__version__ both equal 0.1.1; installed CLI help; full 12-case suite against that wheel under the same empty-environment/network-denial wrapper above. Markdown local links/fences/whitespace, synchronized pyproject version, and staged/unstaged Git whitespace checks passed before commit. No failed check remained at this closure. Current artifact filenames use 0.1.1.

Next milestone: 2B, durable coordinator state and deterministic trusted-evidence gates. Feed AGENTS.md, README.md, CHANGELOG.md, docs/HANDOFF.md, docs/DEVELOPMENT-PLAN.md, docs/DEVELOPMENT.md, docs/ARCHITECTURE.md and docs/decisions/0002-minimal-architecture.md to the next session. Its full initial prompt follows below.

### Phase 2B / durable state and deterministic evidence gates — 2026-10-02

Completed this milestone only. Base: `781c215dba5b0d137334d75f2374a569c23b3ed1`, clean `codex/phase1-architecture` checkout, tracking `origin/codex/phase1-architecture`. Delivery is the milestone commit containing this entry; resolve it with `git log -1 --format=%H -- docs/HANDOFF.md`. Version **0.2.0** is a minor bump for compatible coordinator functionality, with explicit legacy-state migration. Push the current branch to `origin` and verify the remote revision at closure; no merge or package-registry release is authorized by this entry.

Artifacts: `src/crewshal/contracts.py`, `durable.py`, `gates.py`; updated model-store/CLI facade and Phase 2A storage assertions; `tests.acceptance.test_phase_2b` (21 cases); [state/gate guide](STATE-AND-GATES.md); [standalone Phase 2C prompt and exact inputs](PHASE-2C-PROMPT.md). Dependency pins/hashes are unchanged. Ignored build artifacts are `dist/crewshal-0.2.0.tar.gz` and `dist/crewshal-0.2.0-py3-none-any.whl`.

Acceptance confirmed:

1. Unknown/malformed record/database versions and boolean/coerced record versions are refused. Supported database schema-1-to-2 migration requires an explicit option, creates a private consistent backup before change, preserves ordered history and rolls back on malformed payloads. Schema 1 is a specified synthetic upgrade format, not a historically released database.
2. Explicit Phase 2A JSON import preserves complete provenance, corrections/confirmations and original backup bytes. Reinitialization still invalidates changed sources. Informational repository exports have no import/approval authority.
3. Records and ordered events commit together; synthetic exception and hard process exit before commit leave neither a partial version nor a partial event. Interleaved independent writers detect stale expected versions and preserve the winning decision. A run lease blocks a second coordinator and blind takeover.
4. Outstanding intents and acknowledged handles become interrupted on explicit restart reconciliation. Handles stay available for inspection, repeated reconciliation does nothing, and no side effect is replayed. A terminal attempt with an unfinished leased run also requires inspection. There is no process launcher, adoption or kill implementation.
5. Approvals/evidence/waivers bind exact model/task/policy/scope/candidate digests. Each changed binding invalidates its use. Worker prose/exports, unknown attempts and mismatched capture ownership cannot establish evidence authority. Capture requires actual private artifact/log bytes; missing/mutated bytes refuse verdict persistence.
6. Check definitions, process exit, runtime result, capture times, logs and terminal states must agree. Failed, skipped, unavailable, terminated, incomplete and contradictory checks cannot verify. Scope violations cannot be waived by a completion waiver. Review requires matching role and known provider/model identities; missing identity or the same provider cannot establish independence.
7. Explicit owner/gate/residual-risk waivers produce accepted-with-waiver while preserving original failed/missing status. Successful verdict, terminal run state and lease release are atomic. Every verdict has `execution_allowed=false`.
8. Identical usage replay produces no extra event; conflicting identities/sequences or decreasing known cumulative counters are refused. Totals use the latest cumulative snapshot per attempt. Missing usage/cost stays unknown; measured cost, estimates and subscription quota remain separate.

Exact verification and environment:

- Host: macOS 27.2 build 26B5091g, arm64; CPython 3.12.14 at `/opt/homebrew/opt/python@3.12/bin/python3.12`; SQLite 3.53.4; uv 0.9.24; RTK 0.50.0. Pydantic 2.12.5/Core 2.41.5; mypy 1.18.2; Ruff 0.14.1; setuptools backend 80.9.0. All transitive dependency versions/hashes remain in requirements-dev.lock.
- Prerequisite: `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2a`: 12 passed. `rtk proxy uv build --offline --quiet`; fresh `/private/tmp/crewshal-2b-baseline` venv with offline hash-locked dependencies and the 0.1.1 wheel; installed CLI help and installed-wheel Phase 2A suite: passed, 12 cases. The editable environment's old 0.1.0 metadata was observed; reinstalling the final editable package synchronized it to 0.2.0. The prerequisite wheel had correct 0.1.1 metadata.
- Final editable checks: `rtk proxy uv pip install --offline --no-deps --python .venv/bin/python -e .`; `rtk proxy .venv/bin/ruff check src tests`; `rtk proxy .venv/bin/ruff format --check src tests` (13 files); `rtk proxy .venv/bin/mypy` (strict, 9 source files); `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2b` (21 cases); `rtk proxy .venv/bin/python -m unittest discover -s tests -t .` (33 cases); `rtk proxy uv build --offline --quiet`: all passed.
- Fresh final verification directory: `/private/tmp/crewshal-2b-verify.DfQP8S`. `rtk proxy uv venv --python python3.12 "$crewshal_verify_dir/fresh"`; `rtk proxy uv pip install --offline --require-hashes --python "$crewshal_verify_dir/fresh/bin/python" -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python "$crewshal_verify_dir/fresh/bin/python" dist/crewshal-0.2.0-py3-none-any.whl`: passed. Import resolved to external site-packages; installed metadata and crewshal.__version__ both asserted equal to 0.2.0.
- With `crewshal_verify_dir` set to that directory and its `home` created, used `rtk proxy env -i PATH="$crewshal_verify_dir/fresh/bin:/usr/bin:/bin" HOME="$crewshal_verify_dir/home" PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'` followed by installed `crewshal --help`, then installed Python `-m unittest tests.acceptance.test_phase_2a` (12), `-m unittest tests.acceptance.test_phase_2b` (21) and `-m unittest discover -s tests -t .` (33): all passed. The fresh tests use no editable application imports, credentials or prior fixtures. The wrapper does not qualify worker containment.
- Skills remained available: Jev live doctor succeeded (probability 0.97); bounded completion-evidence check returned 0.73 and was advisory only. No product model call occurred. Codebase-memory ran its own MCP tools through the installed CLI because direct MCP tools were not exposed in this chat. Startup Verify generation was `2026-10-02T06:46:29Z`; task-directed structural search, both-direction main trace, exact ModelStore snippet and path coverage informed inspection. An initial CLI array flag was interpreted as one literal path; raw structured arguments corrected it, and all four paths showed matching metadata/no recorded gap. Source fallback read the relevant exact files. Final full refresh generation was `2026-10-02T07:17:07Z` (362 nodes/1,260 edges), with zero skipped/partial/unindexed source files. Final search and both-direction evaluate trace matched the durable verdict call; all eight evidence paths had matching metadata/no recorded gaps. The src scope reported only excluded generated __pycache__; its directory was inspected and contained .pyc files. This does not prove graph completeness. The final tree was refreshed again after the ledger update.

- Final documentation check: inline Python verified all 16 Markdown files for local links, balanced fences and whitespace; every listed Phase 2C input exists; pyproject/runtime/installed versions match 0.2.0 and current/next markers match 2B/2C. `rtk proxy git diff --check` and `rtk proxy git diff --cached --check` passed before commit.

Observed failures retained and resolved: initial strict typing rejected nullable aggregation and the optional check-definition map (three errors), corrected before reruns; the first integrated Phase 2A run refused macOS `/var` parent aliases (11 failures), resolved by canonicalizing parent aliases while retaining directory/file symlink refusal and repository exclusion; obsolete JSON-internal assertions were updated to inspect durable payloads. Two unused test imports failed Ruff, removed. Final reinstall emitted uv's cross-filesystem clone warning and completed using copies. No required check remains failed.

Limitations: only this macOS/Python combination is verified. Trusted local operator/coordinator calls supply real task/policy/scope/candidate digests, identities and observations; no remote authentication or protection against same-user tampering is claimed. Pure evaluate requires a trusted snapshot; product callers use durable verdict resolution, never worker exports. No real candidate freeze, provider identity resolution, launcher, adapter, isolation profile, credential mediation or retention service exists. Capture interruption may leave unreferenced private artifacts, which cannot satisfy gates. Reconciliation is deliberately conservative and has no exactly-once execution claim. Unknown billing cannot enforce a hard spending ceiling. No target command, container, provider product model, benchmark, hold-out or private predecessor artifact was used. Agent writes remain disabled; 2C/2D and later owner gates are unchanged.


### Phase 2C / reuse assessment and denied qualification checkpoint — 2026-10-02

**Blocked, not complete.** Base: `faf2d7d12613c8e96ef3da8a2cd7f861ed740c8d`, clean `codex/phase1-architecture` tracking its origin branch. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Version **0.3.0** is a compatible functionality bump for qualification identity/refusal records, not a claim that Phase 2C passed. Follow the standing push authorization; no merge, deployment or registry release.

Artifacts: [frozen protocol](qualification/phase-2c-v1.json), [denied observation](qualification/phase-2c-observed.json), [qualification/reuse assessment](EXECUTION-QUALIFICATION.md), `src/crewshal/qualification.py`, trusted preflight and public-helper assessment utilities, 11-case `tests.acceptance.test_phase_2c`, updated README/changelog/plan/development guide and [precise resumption prompt/input list](PHASE-2C-RESUME-PROMPT.md). No runtime adapter, model/tool loop, malicious-worker runner or process supervisor exists.

Evidence and disposition:

1. Reproduced Phase 2B prerequisite from a newly built 0.2.0 wheel: Phase 2A 12, Phase 2B 21 and complete 33 cases passed, along with Ruff, strict mypy and installed CLI. Fresh baseline environment `/private/tmp/crewshal-2c-baseline-20261002` used offline hash-locked installation; tests had empty inherited environment, synthetic HOME and OS-level network denial. No previous temporary fixture was needed.
2. Froze 20 mandatory criteria/grants before the initial bounded substrate preflight, manifest SHA-256 `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. The initial inline preflight and delivered repeatable utility both queried only `unix:///var/run/docker.sock`, with empty environment/synthetic HOME/Docker config and 10-second command timeouts. Docker client 29.8.1 build 4a63305d74 was present; server version exited 1 with `connect: no such file or directory`. This proves only that explicit endpoint was unavailable. No user Docker context/alternative engine was inspected. Worker launches: 0; containment probes: 0; all 20 whole-boundary cases unavailable; profile denied.
3. Public Orchestrate revision `1846530cf4383c4592d739601f3c9870e83d9a13` (MIT) was assessed through its tracked-file inventory and plugin contracts. No executable implementation of the requested seam exists in that pinned plugin snapshot; harness-dispatched behavior could not be tested without a coding runtime. No documentation claim was counted as containment.
4. Public Orka revision `9e366915fc6cd6ede5aa47ac7a3b418a32ff528b` (MIT) passed its actual 20-case synthetic execution-backend conformance suite with network denied. Independent pure native-helper probes replaced the provider credential but **failed** exclusion of another synthetic secret, SSH_AUTH_SOCK and injected hook settings (utility exit 2). Hook values were only inspected, never executed. No real credential, Claude/provider launch or public implementation copy occurred. Receipts/fencing are useful seams but the fake backend and helper behavior do not qualify a real isolated executor. Reuse as-is rejected; fitting reuse remains conditional on an outer boundary and Crewshal authority/recovery mapping.
5. Eleven offline acceptance methods prove missing/stale/failed/unavailable/malformed qualification refusal, all identity-field invalidation, exact case coverage, duplicate/extra/missing case rejection, unresolved credential/substrate refusal, immutable false execution authority, frozen manifest refusal before output, and command absence/failure/output handling. Every mandatory failed/unavailable fixture is exercised. All-passing synthetic fixtures produce only later-authorization eligibility; they never enable writes. Qualification APIs are trusted coordinator inputs; no worker import, SQLite persistence or product launch path is added.

Exact commands and verification:

- Host: macOS 27.2 build 26B5091g, arm64, Darwin 27.2.0; CPython 3.12.14, SQLite 3.53.4; uv 0.9.24; RTK 0.50.0. Dependency pins/hashes unchanged: Pydantic 2.12.5/Core 2.41.5, Ruff 0.14.1, mypy 1.18.2 and setuptools backend 80.9.0. No Linux/image/runtime/broker qualification identity is available.
- Build/setup: `rtk proxy uv build --offline --quiet`; `rtk proxy uv venv --python python3.12 /private/tmp/crewshal-2c-baseline-20261002`; `rtk proxy uv pip install --offline --require-hashes --python /private/tmp/crewshal-2c-baseline-20261002/bin/python -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python /private/tmp/crewshal-2c-baseline-20261002/bin/python dist/crewshal-0.2.0-py3-none-any.whl`: passed. Baseline static commands used that environment's Ruff/mypy against src/tests.
- Final editable setup: `rtk proxy uv pip install --offline --no-deps --python .venv/bin/python -e .`: passed, synchronized 0.3.0 metadata, cross-filesystem copy fallback warning only. `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c`: 11 passed. Fresh final build and hash-locked installation repeated the preceding setup using `/private/tmp/crewshal-2c-verify-20261002` and `dist/crewshal-0.3.0-py3-none-any.whl`: passed.
- Final network-denied wrapper: `rtk proxy env -i PATH=/private/tmp/crewshal-2c-verify-20261002/bin:/usr/bin:/bin HOME=/private/tmp/crewshal-2c-verify-home-20261002 PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'`, followed by the fresh installed Python and `-m unittest tests.acceptance.test_phase_2a` (12 passed), `tests.acceptance.test_phase_2b` (21 passed), `tests.acceptance.test_phase_2c` (11 passed), or `-m unittest discover -s tests -t .` (44 passed). Installed `crewshal --help` passed. Python asserted `crewshal.__version__ == importlib.metadata.version("crewshal") == "0.3.0"` and imports from external site-packages. No editable application imports, provider credentials or previous fixtures were required.
- Static checks: `rtk proxy /private/tmp/crewshal-2c-verify-20261002/bin/ruff check src tests scripts`; `ruff format --check src tests scripts` (17 files); `mypy` (strict, 10 source files): passed. Existing and new tests were read separately from production behavior; no containment success is inferred from fixture records.
- Preflight: `rtk proxy .venv/bin/python scripts/qualify_phase_2c.py --manifest docs/qualification/phase-2c-v1.json --output /private/tmp/crewshal-2c-final-preflight-20261002.json`: expected denied exit 2. Its reviewed secret-free output is the committed observed record. Linux/image/runtime and credential design remain null, invalidating any eligibility. No image pull or socket mount.
- Public clones used `rtk proxy env -i PATH=/usr/bin:/bin:/opt/homebrew/bin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null git -c core.hooksPath=/dev/null clone --depth 1` with each public HTTPS repository URL and a new external directory. Resolve/check the pinned commits before assessment. The original network-denied baseline wrapper followed by its Python and `/private/tmp/crewshal-2c-orka-20261002/tests/execution_backend_test.py`: 20 passed. Same wrapper followed by Python `scripts/assess_orka_seam.py --source /private/tmp/crewshal-2c-orka-20261002`: expected exit 2; one provider replacement check true, three exclusion checks false. The helper source SHA-256 is recorded in EXECUTION-QUALIFICATION.md. These clones are optional assessment inputs, not package-test prerequisites.
- Jev live doctor passed and advisory choice returned `denied` for the observed unavailable mandatory boundary. Jev served the explicitly requested assistant workflow, not a product model/provider call or qualification authority.
- Codebase-memory's own CLI remained operational. Verify-tier startup generation `2026-10-02T07:17:07Z` had matching metadata/no recorded gaps for six Crewshal evidence paths. Both-direction evaluate trace found the durable verdict caller; exact snippet and full prerequisite source were read. Public snapshot graph generations were `2026-10-02T11:22:10Z`; Orka execution-backend/native-helper paths had matching metadata/no recorded gaps. Orka's partial SQL and unrelated shell ranges were outside the bounded assessment and no claims relied on them. Orchestrate's plugin scope had no recorded gap; exact tracked inventory/source supplemented the negative executable-seam claim. An initial partially qualified trace name failed; the exact graph-qualified name resolved. Graph cleanliness is best-effort, not completeness. The final Crewshal tree was reindexed and changed source/tests/scripts checked with coverage and direct source fallback as needed.
- Local Markdown links/fences/whitespace, exact resumption inputs, synchronized package versions and frozen record/protocol integrity were checked. Git unstaged/staged whitespace checks passed before commit. Final build includes the updated README and new module. No required offline regression remains failed.

Limits and next scope: no Linux execution, hostile payload, network sink, descendant kill, validation boundary or credential mediation was qualified. The preflight utility refuses even with an available daemon because the actual worker runner/broker is still missing. It caps persisted captured output after private temporary capture and is restricted to trusted health commands. Records are not signatures, launch grants or defenses against a compromised coordinator/same-user process. Original project code/dirty state was not exercised by a worker. No private Forge source, host secret store, model product call, paid run, hold-out, application, merge, deployment or registry release occurred. Public-helper failures and unavailable mandatory cases are retained. Resume 2C only after an explicit available Linux endpoint/image and accepted synthetic-tested credential design; implement the frozen payload runner then. Do not begin 2D.

### Phase 2C / bounded Linux substrate resumption — 2026-10-02

**Blocked, not complete.** Base: `5284428472eeb123d134bec9883bd18033259760`, clean `codex/phase1-architecture` checkout. Version **0.4.0** adds compatible synthetic Linux qualification tooling, not execution authority. Delivery is the commit containing this entry, resolved with `git log -1 --format=%H -- docs/HANDOFF.md`; push the current branch under standing owner authorization and verify remote equality. No merge, deployment or registry release.

The owner supplied running Docker Desktop. Narrow explicit socket checks found `unix:///Users/hamedprooshani/.docker/run/docker.sock` responding; the historical `/var/run/docker.sock` failure remains recorded. No Docker credential/context store was inspected. Observed Desktop 4.93.0 (240920), engine/client 29.8.1, API 1.56, arm64 Linux kernel 7.0.14-linuxkit, containerd v2.3.5, runc 1.5.1 and BusyBox v1.37.0. The cached Alpine image is `sha256:5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11`. Host and locked Python dependency versions remain those recorded above. No image/package download, private source, real credential, product model call or existing user-container mutation occurred.

Artifacts: [Linux report](LINUX-SUBSTRATE-PROBES.md), frozen v2/v3/v4 manifests and retained observations in docs/qualification, `scripts/probe_linux_profile.py`, five offline methods in `tests.acceptance.test_phase_2c_substrate`, explicit Unix endpoint support and compact engine identity in the preflight utility, synchronized package/docs and [resumption prompt with exact inputs](PHASE-2C-RESUME-PROMPT.md). The helper executes only a frozen trusted synthetic shell payload; it is not a product launcher, adapter or arbitrary-process supervisor.

Evidence and retained limitations:

1. Each prospective manifest retained all twenty v1 criteria and grants. Active v4 manifest SHA-256 is `6f4c5a568f89ad16fa6b5754247938bb816ae6c8cb71fd2b12746f95b0af4db1`; frozen runner SHA-256 is `b53230625b6b8a5ce82f47f696edfd9632588ef3d4d75c36fdf6c798d6e786d9`. Engine inspection verifies the exact image, read-only root, UID/GID 65532, dropped capabilities, no-new-privileges, network none, private PID/IPC, 32 PIDs, 128 MiB, one CPU, disabled logging, synthetic input/output binds and 16 MiB scratch tmpfs before start. Pulls are forbidden. Synthetic inherited secret/agent markers are not forwarded; host homes, sockets and real source/state are not mounted.
2. Two final v4 runs used separate fresh fixtures and containers. Nine bounded cases passed: allowed grant, external read/write, original-checkout and coordinator-state exclusion, symlink escape, new-file escape, metadata escape and credential/environment inheritance. Protected parent bytes, modes and hardlink counts were unchanged; approved output contents and terminal exit were independently checked. Actual absolute and relative symlink targets were exercised. Each normally exited container was removed. A separate labeled-container inventory returned empty after all four historical/final runs; no existing container was removed.
3. Eleven mandatory cases remain unavailable: network egress attempts, repository/global hooks, MCP/plugins/instructions, detached descendants, cancellation, deadline, accepted credential mediation, separate credential-free validation, whole-runtime configuration binding and qualification refusal. Engine network-none inspection is not a traffic-sink test. Ordinary cleanup is not cancellation/deadline evidence. The runtime was BusyBox shell, not Codex or Claude. Credential design remains null; all decisions remain denied and `execution_allowed=false`.
4. Retained v2 failure: a read-only cross-mount `mv` created a permitted owned copy before failing unlink; the parent oracle wrongly rejected that allowed output. V3 corrected this oracle and preserved input integrity, but subsequent source review found its nominal relative symlink used an absolute target. V4 prospectively added real relative target/parent variants and ran twice. Historical v2/v3 records remain visible and cannot qualify the active v4 configuration.
5. Offline tests validate frozen hashes/criteria, captured result limits, rejection of weakened grants, detection of protected bytes/modes/link/new-file mutations and manifest-drift refusal before container creation. They inspect static observations and failure fixtures; they are not additional live qualification. The trusted helper caps output after capture and uses ten-second Docker command timeouts; arbitrary hostile-output supervision remains unimplemented.

Verification and reproducibility:

- Reproduced the prior 0.3.0 installed-wheel 44-case suite and static checks before resuming. Built 0.4.0 with `rtk proxy uv build --offline --quiet`. Created `/private/tmp/crewshal-2c-linux-verify-20261002` using `rtk proxy uv venv --python python3.12`, installed requirements-dev.lock offline with `--require-hashes`, then installed `dist/crewshal-0.4.0-py3-none-any.whl` offline with `--no-deps`. Cross-filesystem editable-install copy fallback completed successfully.
- Empty inherited environment, synthetic HOME and macOS network-denial wrapper: `rtk proxy env -i PATH=/private/tmp/crewshal-2c-linux-verify-20261002/bin:/usr/bin:/bin HOME=/private/tmp/crewshal-2c-linux-verify-home-20261002 PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'`, followed by that installed Python. Phase 2A 12, Phase 2B 21, Phase 2C 11 and substrate 5 tests passed; complete `-m unittest discover -s tests -t .` passed **49**. Installed CLI help passed; runtime and distribution metadata both asserted 0.4.0, importing external site-packages. Fixtures require no prior temporary artifact.
- `rtk proxy .venv/bin/ruff check src tests scripts`, `ruff format --check src tests scripts` (19 files) and strict `mypy` (10 source files): passed. Final documentation links/fences/whitespace, exact next-session inputs, synchronized versions, frozen source/manifest hashes and Git staged/unstaged whitespace checks passed.
- Actual v4 invocation: `rtk proxy .venv/bin/python scripts/probe_linux_profile.py --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock --manifest docs/qualification/phase-2c-substrate-v4.json --manifest-sha256 6f4c5a568f89ad16fa6b5754247938bb816ae6c8cb71fd2b12746f95b0af4db1 --output /private/tmp/crewshal-2c-substrate-v4-observed.json`; repeated with a new `phase-2c-substrate-v4-repeat.json` output. Both intentionally exit 2 because the complete mandatory boundary remains denied. Exact normalized commands, effective engine inspections, terminal states and owned inventories are in the committed observations. The v1 preflight with the explicit socket now sees the daemon but still refuses; it does not run the separate subset helper.
- Caveman ultra, Jev and codebase-memory remained operational. Jev advisory disposition was denied; it did not grant product authority. Verify-tier graph refresh generation `2026-10-02T12:09:12Z` had 798 nodes/2,194 edges, zero skipped/partial source files. Four changed evidence paths had matching metadata/no recorded gaps. Structural search, both-direction verify_grant trace and exact source snippet informed inspection. The graph falsely associated dictionary `.get` with CoordinatorStore.get; direct source confirmed plain dictionary access, so no claim relies on that edge. Clean graph metadata is not completeness proof.

Next scope remains 2C: prospectively pin the provider-free network/process/native-runtime probe toolchain, independently exercise the remaining boundaries, and synthetic-test an existing credential mediation mechanism for owner acceptance. Do not build a custom gateway/model loop, weaken criteria, grant general agent writes or begin 2D. Mandatory unavailable/failed cases preserve denial. The precise continuation inputs are in PHASE-2C-RESUME-PROMPT.md.

### Phase 2C / bounded lifecycle and validator resumption — 2026-10-02

**Blocked, not complete.** Base: `1723740006abaaa122237648922ec27a9ddce141`, clean `codex/phase1-architecture`. Package **0.5.0** adds compatible synthetic qualification tooling, not execution authority. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push the current branch under standing owner authorization; no merge, deployment or registry release.

Artifacts: the prospectively frozen lifecycle v1 manifest, two normalized observations, `scripts/probe_linux_lifecycle.py`, six methods in `tests.acceptance.test_phase_2c_lifecycle`, updated [Linux evidence](LINUX-SUBSTRATE-PROBES.md) and [exact resumption prompt/inputs](PHASE-2C-RESUME-PROMPT.md). All twenty original mandatory criteria, grants and limits remain unchanged. The original v1 and v2/v3/v4 filesystem records and failures remain intact.

Evidence:

1. The frozen lifecycle manifest/source/payload/helper/qualification-module identities were checked before creation. Manifest SHA-256 `930e601021f95e01488f10582feb5adadc4bdd76c566edbd34486d0feb93b2ef`; runner SHA-256 `20940da29590f8e263d842a32759d227c3ebb0e6e96c1b394d3d595a7f57c598`. Both actual runs used new directories and three unique containers. Exact grants were independently inspected before start; pulls were forbidden. Only cached public Alpine and fresh synthetic source/output/scratch were used.
2. Detached setsid grandchildren retained denied synthetic read/write/network authority and no parent synthetic credential/SSH variable. Engine process tables independently showed separate sessions. Coordinator cancellation and five-second deadline kill requests produced terminal exit 137, `Running=false`, `Pid=0`, no OOM and stable post-terminal heartbeats. Deadline requests occurred at 5.000882 and 5.000350 seconds; the frozen oracle allows 0.2 seconds scheduler tolerance. API completion latency is not an instantaneous five-second-kill guarantee. All six fixture containers were removed; final label-filtered inventory was empty.
3. Separate validators used fresh read-only candidate copies, no worker output or credential mounts, network none and their own scratch/output. The validator read/hash succeeded, forbidden overwrite/HTTP attempts failed, expected parent candidate digest and bytes/modes/link counts survived, and engine terminal exit was zero. These four bounded synthetic criteria passed twice; the new record marks its other sixteen cases unavailable. Earlier nine-case records are separate identities, not upgraded or merged. Every decision remains denied and execution_allowed=false; credential design is null.
4. Seven categories lack whole-boundary evidence: full network-egress, repository-hooks, global-hooks, mcp-plugins-instructions, credential-mediation, configuration-binding and qualification-refusal. Native coding runtime conformance is also unproved for the observed synthetic process cases. IPv4 HTTP denial is not TCP/UDP/DNS/IPv6 sink evidence. No model/tool loop, runtime adapter, arbitrary hostile-output supervisor or gateway was added. The pinned Orchestrate/Orka as-is reuse rejection remains unchanged; these probes do not establish actual seam integration/recovery.
5. Existing Docker Sandboxes credential injection is a documentation-supported candidate only. `docker sandbox --help` reported it removed; `command -v sbx` found no executable on this PATH. No broker installation, credential-store access, secret import, image/package download or product/provider call occurred. A bounded preparation grant and complete synthetic-token/request-authority evidence plus owner design acceptance remain prerequisites. The optional preparation question received no answer during this checkpoint, so no preparation grant was assumed.

Verification:

- Host remains macOS 27.2 build 26B5091g arm64; CPython 3.12.14, uv 0.9.24, RTK 0.50.0. Same immutable Alpine identity and engine 29.8.1 as the earlier checkpoint; locked dependency versions/hashes unchanged.
- Baseline `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: 49 passed before new code. New module: six passed. Final editable complete suite: 55 passed. `rtk proxy .venv/bin/ruff check src tests scripts`, `ruff format --check src tests scripts` (21 files), strict `mypy` (10 source files): passed.
- Actual probe: `rtk proxy .venv/bin/python -m scripts.probe_linux_lifecycle --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock --manifest docs/qualification/phase-2c-lifecycle-v1.json --manifest-sha256 930e601021f95e01488f10582feb5adadc4bdd76c566edbd34486d0feb93b2ef --output /private/tmp/crewshal-2c-lifecycle-v1-observed.json`; repeated with `/private/tmp/crewshal-2c-lifecycle-v1-repeat.json`. Both intentionally exit 2 while reporting subset success and full denial. The committed sanitized observations retain exact commands, effective grants, terminal states, process tables, protected comparisons and output manifests.
- Fresh final artifact: `rtk proxy uv build --offline --quiet`. External verification root `/private/var/folders/4p/xh823rjd32x53hbm_zvcjnqh0000gn/T/crewshal-2c-lifecycle-verify-spn3p7zb`. `rtk proxy uv venv --python python3.12 ROOT/fresh`; `rtk proxy uv pip install --offline --require-hashes --python ROOT/fresh/bin/python -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python ROOT/fresh/bin/python dist/crewshal-0.5.0-py3-none-any.whl`: passed.
- With ROOT substituted above, empty inherited environment `PATH=ROOT/fresh/bin:/usr/bin:/bin HOME=ROOT/home PYTHONDONTWRITEBYTECODE=1`, wrapper `rtk proxy /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' ROOT/fresh/bin/python -m unittest MODULE`: modules tests.acceptance.test_phase_2a (12), test_phase_2b (21), test_phase_2c (11), test_phase_2c_substrate (5), test_phase_2c_lifecycle (6) passed. Same wrapper with `-m unittest discover -s tests -t .`: 55 passed. Installed `crewshal --help` passed; runtime/distribution versions asserted 0.5.0 and application imports resolved to external site-packages. No previous runtime/container/database artifacts are prerequisites.
- Jev live doctor passed (probability 0.98); advisory choice selected cached synthetic probes rather than unqualified runtime execution. Jev is owner-requested assistant support, not product execution or authority. Codebase-memory CLI was operational throughout; native MCP tool bindings were unavailable, so its supported local CLI was used. Verify-tier startup generation `2026-10-02T12:09:12Z` had matching metadata/no recorded gaps for probe_linux_profile.py, qualification.py and test_phase_2c_substrate.py. Both-direction assess_qualification trace and exact verify_grant snippet informed source inspection. An initial CLI array flag was interpreted as a literal path; raw structured JSON corrected coverage. Graph cleanliness is best-effort, not completeness; exact sources were read and final changes reindexed. Final generation `2026-10-02T12:42:19Z` has 1,002 nodes/2,588 edges; the four relevant source/test paths have matching metadata and no recorded gaps.
- Frozen protocol/source identities, local Markdown links/fences/whitespace, exact next-session inputs, synchronized versions and Git whitespace were checked before commit. No required offline test failed. Initial default-shell execution failed because the desktop cwd still named absent Foreman; using explicit /bin/bash in the actual Crewshal checkout resolved it without creating or overwriting a repo.

Next scope: resume Phase 2C only. Prepare/pin the full provider-free network/native-runtime toolchain and existing credential mediation mechanism under the recorded resource/design gates; freeze protocols before probes, preserve failed/unavailable results and independently verify complete boundaries. No Phase 2D prompt is delivered.

### Phase 2C / synthetic network subset and SBX preparation — 2026-10-02

This session resumed only Phase 2C. Base revision `feffe762c4ee30ae71b37eecd900f878d2abc763`, branch `codex/phase1-architecture`; checkout was clean. Package checkpoint is 0.6.0. Delivery revision is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Full 2C remains denied; no 2D prompt, native runtime adapter, live implementation, credential access, application, merge, deployment or registry release occurred.

Achievements and retained limits:

1. Reproduced baseline full editable suite (55 passed) and original five acceptance modules (55 passed) against a fresh installed 0.5.0 wheel with empty inherited environment, synthetic HOME and OS network denial. Original v1 protocol and prior substrate/lifecycle source identities remain unchanged.
2. The owner explicitly approved official public preparation capped at 2 GB of downloads and 30 minutes, synthetic only, no paid/provider calls or real credentials. Prepared official Python 3.12.14 Alpine image, immutable identity `sha256:4c47124a8391cb7a9f571164147d154777cf012a4ece5f86097130d7a4478111`, unpacked size 78,869,135 bytes. Pulled with empty synthetic Docker config/HOME using the explicit socket. No worker performs a pull. Prepared official SBX v0.46.0 Darwin archive (133,447,662 bytes), release asset digest `1daa077a793bc048ef69acb33cb89d27ce0696efadf44df6466463f2a79d8adc`; verified exact digest before extraction. Preparation stayed within the approved bounds. No third-party implementation was copied into Crewshal; the archive is external preparation evidence, not a product dependency.
3. Added separate frozen synthetic network client/sink/runner. Two distinct local sinks exercise twelve TCP/UDP/DNS-wire IPv4/IPv6 worker attempts. Connected positive controls before/after receive exact packets; independent sink files and advancing heartbeats establish that zero additional packets arrived during denial. Effective grants, terminal states, protected fixture inventories and scoped cleanup are checked by the parent. All worker allocations retain original 128 MiB/32 PIDs/one CPU and network-none authority; sink/control authority is separate internal-only fixture infrastructure. The DNS query uses synthetic port 15353; system resolver, DoH/DoT and native coding runtime conformance remain unproved.
4. Initial network v1/v2 runs conservatively failed before clients because addresses were read before engine start. V2's tentative IPv6-only diagnosis was incorrect; effective network inspection showed both families enabled. V3 inspects/verifies running sink addresses. Both failed reports/manifests and exact runner source snapshots remain recorded; no failed case was removed or promoted. Active v3 manifest SHA-256 `82df51dd5acd305602b2cb826bbd56d305e5669c15e0d71c06c9f007bdf36eef`; runner SHA-256 `7636e21bb257cae29397ec639122f67ee6c103ed62cf83f6d5868389126c512a`. Both fresh-fixture v3 runs pass: sink counts 12 before denial, 12 after denial, 24 after final control; all twelve worker attempts denied, all three clients exit zero, protected fixtures unchanged, owned handles/network removed. Records retain exact commands and observations in [network evidence](NETWORK-SUBSTRATE-PROBES.md). The nineteen other mandatory categories remain unavailable in this record; prior profiles remain separate. Configuration/credential designs are not qualified by combining subset observations.
5. SBX v0.46.0 build `991967dc90ce0d9a440cd1df1bdf3e395c5a2693` help/version inspection passed with synthetic HOME/XDG_CONFIG_HOME and macOS network denial. No daemon, sandbox, login, host credential store or secret import was used. `sbx create --help` advertises minimum sandbox memory 512 MiB; outer VM versus inner 128 MiB worker resource mapping remains untested and must be defined prospectively. Docker documentation describes sign-in and host-side proxy-managed sentinels, not observed operational refusal or tested request authority. The existing candidate still lacks synthetic read/replay/redirect/egress, descendant authority, independent validator and native configuration evidence plus owner acceptance. Do not implement a custom proxy or enlarge the worker grant as a fallback.
6. Added eight independent offline falsification/refusal methods: controls missing, incomplete/sent attempts, unexpected/missing sink receipts, terminal/integrity/cleanup failures, widened grants refusing before start, frozen criteria/source drift, independently checked DNS wire format and denied/stale qualification identities. These are record/oracle regressions, not new Linux containment runs. Prior pinned public reuse decisions remain unchanged; no Orka/Orchestrate native integration or recovery pass was claimed.

Exact verification and environment:

- Host macOS 27.2 arm64, CPython 3.12.14; locked requirements unchanged. Explicit Docker endpoint `unix:///Users/hamedprooshani/.docker/run/docker.sock`; engine/client 29.8.1, kernel 7.0.14-linuxkit. New synthetic client records Python/kernel identity directly. Jev MCP live checks and batched routing worked; final advisory probability that full 2C qualified was 0.04. Jev is owner-requested assistant workflow support, not product qualification or authority.
- Initial `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: 55 passed. New `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_network`: eight passed. `rtk proxy .venv/bin/ruff check src tests scripts`, `ruff format --check src tests scripts` (25 files), strict `mypy` (10 source files): passed.
- `rtk proxy .venv/bin/python -m scripts.probe_linux_network --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock --manifest docs/qualification/phase-2c-network-v3.json --manifest-sha256 82df51dd5acd305602b2cb826bbd56d305e5669c15e0d71c06c9f007bdf36eef --output /private/tmp/crewshal-network-v3-observed.json`; repeat output `/private/tmp/crewshal-network-v3-repeat.json`. Both intentionally exit 2 while reporting subset pass/full denial. Earlier v1/v2 also exit 2, reporting subset failure. Final label-filtered container/network inventories were empty.
- Baseline external installed 0.5.0 artifact root `/private/tmp/crewshal-2c-baseline.IbGYoR`; original five acceptance modules: 55 passed under empty-environment/synthetic-home macOS `(version 1)(allow default)(deny network*)` wrapper; CLI help passed. No prior artifact was needed to recreate fixtures.
- Final `rtk proxy uv build --offline --quiet`: passed for synchronized 0.6.0 sdist/wheel. Fresh final verification root `/private/tmp/crewshal-2c-network-verify.yIZ7v6`: `uv venv --python python3.12 ROOT/fresh`; `uv pip install --offline --require-hashes --python ROOT/fresh/bin/python -r requirements-dev.lock`; `uv pip install --offline --no-deps --python ROOT/fresh/bin/python dist/crewshal-0.6.0-py3-none-any.whl`: all passed. Application imports resolve to external site-packages; runtime/distribution versions asserted 0.6.0.
- With ROOT substituted, `rtk proxy env -i PATH=ROOT/fresh/bin:/usr/bin:/bin HOME=ROOT/home PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' ROOT/fresh/bin/python -m unittest tests.acceptance.test_phase_2a tests.acceptance.test_phase_2b tests.acceptance.test_phase_2c tests.acceptance.test_phase_2c_substrate tests.acceptance.test_phase_2c_lifecycle tests.acceptance.test_phase_2c_network`: 63 passed (12/21/11/5/6/8). Same wrapper with `-m unittest discover -s tests -t .`: 63 passed. Installed console help passed under empty environment/synthetic HOME/network denial; initialization is exercised by the acceptance suite.
- Codebase-memory MCP Verify-tier startup project `Volumes-X10Pro-Crewshal` was ready, generation `2026-10-02T12:42:19Z`. Exact grant snippet and both-direction trace informed helper reuse. New untracked paths initially required source fallback; exact source was read/written and reindexed. Generation `2026-10-02T13:30:10Z` has 2,167 nodes/4,216 edges and matching metadata/no recorded gaps for network runner/client/sink, existing helper/qualification module and acceptance module. Search/trace pagination completed for the bounded scope. Generic `get` edges are resolver suggestions, not independent call proof; material checks use exact source. Clean coverage is best-effort, not completeness. Final generation `2026-10-02T13:39:42Z` has 2,180 nodes/4,229 edges; final network paths, qualification module, version source and acceptance module again have matching metadata/no recorded gaps.
- Original/frozen protocol/source hashes, retained source snapshots, six-module documentation commands, exact next-session inputs, synchronized versions, local Markdown links/fences/whitespace and Git diff/staged whitespace checked before commit. Sanitized network observations contain only synthetic fixture/configuration/packet data. No required offline test failed.

Smallest resumption scope: Phase 2C only. Prospectively define and approve isolated outer/inner SBX resource/configuration and documented login prerequisites, or select another existing tested mechanism meeting the frozen worker boundaries. Then run full synthetic credential request-authority and native runtime customization/network cases before design acceptance. Full whole-runtime binding/refusal and public seam integration remain unproved. Preparation approval is not credential-design or live execution approval. Use [the exact updated prompt and inputs](PHASE-2C-RESUME-PROMPT.md); no 2D prompt is delivered.

### Phase 2C / prospective SBX resource/configuration checkpoint — 2026-10-02

Outcome: **partial protocol/refusal checkpoint; 2C remains blocked**. Base revision `a4aea5051fd164edcc578b9ff1b3cf1c7479cda6` on `codex/phase1-architecture`, initially clean. Version **0.7.0**. Delivery revision is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push the current branch under standing AGENTS.md authorization. No merge, deployment, registry release or Phase 2D prompt.

Delivered:

- [Prospective resource/configuration protocol](SBX-RESOURCE-CONFIGURATION-PROTOCOL.md), [assessment report](SBX-PROTOCOL-ASSESSMENT.md), pinned help-only assessor and seven offline refusal methods. Every original criterion/grant/limit remains unchanged. A pending 512 MiB/one-CPU outer proposal is distinct from the unchanged 128 MiB/one-CPU/32-PID entire native worker. Direct mapping conflicts with the advertised minimum; nested enforcement has no operational evidence.
- Manifest SHA-256 `976d7ad7b6fe4ef8b2c2dbea981851d03fb2b713942e8dcecab3f6ec24b13f79` binds the resource/configuration document, assessor/helper and pinned official binary. Prior substrate/lifecycle/network manifests and observations remain intact and separate. Every operational criterion in the new record is unavailable; no whole-runtime case was upgraded.
- Official SBX v0.46.0 archive re-prepared because the earlier external extraction was absent. 133,447,662 bytes, 12.62 seconds; archive/binary match earlier recorded SHA-256 identities. Preparation stayed within the recorded 2 GB/30-minute official-public allowance. No global installation, new container image/template download, native worker, provider or paid product call.
- First two assessor attempts refused the release's `bin/sbx` symlink before subprocesses; both refusal reports are preserved. Two fresh-home assessments using the explicitly resolved digest-matched executable subsequently completed all six help/version commands with exits zero and returned 2/full denial. No daemon, login, settings operation, secret-store operation or worker launch occurred. Ad hoc preparatory help inspection is separate from these frozen assessments.
- Configuration protocol excludes host lifecycle/dynamic credential commands, host MCP, SSH forwarding, skills and inherited configuration. Synthetic HOME cannot isolate macOS Keychain; a separate disposable broker credential domain or supported no-store mechanism is a prerequisite. Token masking is not request authorization. Remaining native hook/plugin/network, descendant/sentinel replay/redirect, validator and whole-runtime binding/refusal oracles are explicit. The public reuse decision remains conditional and unchanged.

Verification and environment:

- Baseline `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: **63 passed**. Baseline Ruff lint/format and strict mypy passed. New `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_protocol`: **7 passed** after correcting one test's argv-substring assertion. An initial manifest preparation command used global Python without installed Crewshal and failed; rerun with project interpreter before final freezing. Both failures are recorded, not counted as passes.
- Host macOS 27.2 arm64; CPython 3.12.14 and locked dependency file unchanged. Final `rtk proxy .venv/bin/ruff check src tests scripts`, `rtk proxy .venv/bin/ruff format --check src tests scripts` (**27 files**), `rtk proxy .venv/bin/mypy` (**10 source files**): passed. `rtk proxy uv build --offline --quiet`: passed; built synchronized 0.7.0 wheel/sdist.
- Fresh artifact verification root `/private/var/folders/4p/xh823rjd32x53hbm_zvcjnqh0000gn/T/crewshal-2c-protocol-verify-e0v4qq2i`. `rtk proxy uv venv --python python3.12 ROOT/fresh`; `rtk proxy uv pip install --offline --require-hashes --python ROOT/fresh/bin/python -r requirements-dev.lock`; `rtk proxy uv pip install --offline --no-deps --python ROOT/fresh/bin/python dist/crewshal-0.7.0-py3-none-any.whl`: passed. Imports resolve to external site-packages; distribution/runtime versions asserted 0.7.0. No earlier build/environment/state artifact was required to create test fixtures.
- Empty-environment/temporary-home/network-denial wrapper: `rtk proxy env -i PATH=ROOT/fresh/bin:/usr/bin:/bin HOME=ROOT/home PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' ROOT/fresh/bin/python -m unittest tests.acceptance.test_phase_2a tests.acceptance.test_phase_2b tests.acceptance.test_phase_2c tests.acceptance.test_phase_2c_substrate tests.acceptance.test_phase_2c_lifecycle tests.acceptance.test_phase_2c_network tests.acceptance.test_phase_2c_protocol`: **70 passed**. Same wrapper with `-m unittest discover -s tests -t .`: **70 passed**. Installed console help passed under the same denied-network/synthetic-home environment.
- Assessor command: `rtk proxy .venv/bin/python -m scripts.assess_sbx_protocol --binary REAL_PINNED_EXECUTABLE --manifest docs/qualification/phase-2c-sbx-protocol-v1.json --manifest-sha256 976d7ad7b6fe4ef8b2c2dbea981851d03fb2b713942e8dcecab3f6ec24b13f79 --output FRESH_EXTERNAL_PATH`. Successful first/repeat external paths were `/private/tmp/crewshal-sbx-protocol-v1-resolved-observed.json` and `/private/tmp/crewshal-sbx-protocol-v1-resolved-repeat.json`. Both intentionally exit 2. Sanitized committed reports retain arguments, stdout/stderr, host and pinned identities; no real secret or user configuration data.
- Jev live availability passed; completion evidence decision probability **0.03** for full native/broker qualification. Advisory assistant support only, never execution authority. Caveman ultra and graph-first access stayed active. Native MCP tools were unavailable in this desktop turn; local MCP CLI provided graph access throughout. Startup project `Volumes-X10Pro-Crewshal`, generation `2026-10-02T13:39:42Z`; Verify-tier searches, exact snippets, both-direction traces and complete relevant pages informed inspection. A first array-flag coverage invocation treated its JSON list as a string; corrected with structured CLI JSON. Actual evidence paths had matching metadata/no recorded issues. Final source reindex generation `2026-10-02T14:30:17Z`: 2,342 nodes/4,606 edges, matching evidence-path metadata. Excluded bytecode/cache metadata does not establish runtime coverage; broad resolver-suggestion edges are not call evidence. Exact newly written source was inspected. Best-effort coverage is not proof of completeness.
- Local Markdown links/fences/whitespace, synchronized versions, frozen source/parent hashes, exact next-session inputs and Git staged/unstaged whitespace checked before commit. Package tests establish refusal behavior on this host, not new Linux/native containment.

Smallest continuation: **Phase 2C only**. Choose/provide an approved disposable broker credential domain and explicit separately bounded outer resources, or select another existing fitting mechanism. Freeze missing operational template/image/runtime/configuration/disk/deadline identities and prove inner resource enforcement before native startup. Then qualify the exact native/broker profile with independent local synthetic sink/hook controls; design acceptance follows that evidence. Nothing permits using the ordinary macOS Keychain, increasing the worker ceiling, a custom gateway, actual provider calls or an unrestricted fallback. Use [the updated exact prompt/inputs](PHASE-2C-RESUME-PROMPT.md). No 2D prompt is delivered.

### Phase 2C / disposable Linux broker-store environment — 2026-10-02

Outcome: **partial environment checkpoint; 2C remains blocked**. Base `cbc53b0c712281284538ccfc475bda6faf5d1aa5`, clean `codex/phase1-architecture`. Package **0.8.0** adds a compatible preflight utility and eight acceptance methods. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push the current branch under standing AGENTS.md authority; merge/deployment/registry release remain gated.

Achievements and exact limits:

1. Owner-requested caveman ultra communication, Jev decision support and codebase-memory access were checked before project work. Jev live CLI decision returned 0.92 on a synthetic environment-blocker question; final full-credential-qualification advisory returned 0.04. MCP graph/Jev tools were not exposed in this session; their local CLI paths worked. Codebase graph project `Volumes-X10Pro-Crewshal` was ready at generation `2026-10-02T14:30:17Z`; exact source/coverage checks covered the existing assessment, Linux/preflight and qualification files. Six paths had metadata-match/no-recorded-issue signals; the scripts scope excluded only generated `__pycache__`. An initial flag-array invocation treated the list as a literal path; corrected typed JSON input produced the actual coverage evidence. Traces contained ambiguous library/document targets; material claims used exact source. The stale Foreman cwd failed; explicit `/bin/sh` and the existing Crewshal checkout resolved execution without creating another checkout.
2. Reproduced all 70 baseline tests. Prepared the official SBX v0.46.0 Linux arm64 archive and Ubuntu 24.04 image under the recorded official-public preparation bounds, without global installation or real-store access. Exact archive/binary/full-bundle/image identities, sizes and preparation elapsed time are in [the assessment](BROKER-ENVIRONMENT-ASSESSMENT.md) and [preparation record](qualification/phase-2c-broker-preparation.json). Dependency lock unchanged; no third-party implementation or binaries committed.
3. Froze separate v1/v2/v3 CLI/store manifests before their respective invocations. V1 successful synthetic save/list did not satisfy the failed Docker-cp tmpfs oracle. V2's plaintext-token requirement and log-path/process-name inference were incorrect. Both observations and exact source snapshots remain preserved; neither becomes a pass. V3 independently observes nonempty backing storage/private directory plus the successful CLI fallback notice and service listing, and labels actual process names. Its two fresh-fixture observations agree. Store files are 0644 within 0700 directories; no plaintext match is a bounded observation, not cryptographic/replay proof.
4. Each live preflight used only an inspected unprivileged, network-none, read-only-root Ubuntu CLI/store test host: 128 MiB, one CPU, 32 PIDs, one read-only verified bundle mount and 32 MiB synthetic tmpfs. No host credential directory, home, SSH agent, source checkout, coordinator state or engine socket was mounted. Before/after engine grants and unique-handle removal were checked. This host is not an outer SBX VM or native worker; no 512 MiB outer allocation was used. Both v3 hosts report Ubuntu 24.04.5/kernel 7.0.14-linuxkit and no KVM device/sysfs entry. No explicit daemon-start, local-sandbox create/run, login, worker, validator or provider request occurred. No surviving daemon is observed at collection; no claim about all transient processes.
5. All twenty mandatory whole-runtime results remain unavailable in this profile. Credential request/replay/redirect/descendant/validator controls, native hooks/MCP/configuration, native network/resolver/proxy controls and inner enforcement remain unavailable. Original worker grants/limits and every earlier frozen source/document/profile are unchanged. No runtime integration, custom gateway, product model/tool loop or execution grant was added.
6. Eight offline methods cover successful-store authority separation, failed/incomplete/reordered oracles and cleanup, failed command/fallback absence, manifest/grant/configuration/source drift, unknown bundle/remote endpoint, effective resource/privilege/device/mount/environment drift, preserved observations and report/symlink overwrite refusal. One initial invocation failed because the repeat observation had not yet been copied; after copying the committed sanitized fixture, all eight passed. Test fixtures use no prior temporary directories, credentials, Docker, SBX or paid service.

Verification commands and results:

- `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: baseline **70 passed**. `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c_broker_environment`: final **8 passed**. One invocation naming all eight acceptance modules: **78 passed**.
- `rtk proxy .venv/bin/ruff check src tests scripts`, `rtk proxy .venv/bin/ruff format --check src tests scripts` (29 files), strict `rtk proxy .venv/bin/mypy` (10 package files): passed. `rtk proxy uv build --offline`: built 0.8.0 sdist/wheel; repeated after README metadata changed.
- Live command: `rtk proxy .venv/bin/python -m scripts.probe_broker_environment --bundle "$crewshal_sbx_bundle" --manifest docs/qualification/phase-2c-broker-environment-v3.json --manifest-sha256 27107761f400de9454f855b5ffe319b264dba44b1385aca67d2b4bfe263d9daf --docker-host unix:///Users/hamedprooshani/.docker/run/docker.sock --output /private/tmp/crewshal-broker-environment-v3-observed.json`; repeat used `/private/tmp/crewshal-broker-environment-v3-repeat.json`. Both exit **2**, record store observation true and full denial. All v1/v2/v3 fixture handles were removed. Existing containers were untouched.
- Fresh external wheel verification root `/private/var/folders/4p/xh823rjd32x53hbm_zvcjnqh0000gn/T/crewshal-2c-broker-wheel-uards4_g`. `uv venv --python python3.12` passed. Initial `uv pip install --offline --require-hashes -r requirements-dev.lock` failed because annotated-types was absent from cache. Prepared all nine hash-locked dependencies from explicit `https://pypi.org/simple` with synthetic HOME/empty inherited environment and a separate cache; the subsequent offline hash-locked invocation audited the installed dependencies successfully. `uv pip install --offline --no-deps dist/crewshal-0.8.0-py3-none-any.whl` installed the fresh wheel. Imports resolve to that environment's site-packages. CLI help, all eight named acceptance modules and full discovery suite each pass under empty inherited environment, synthetic HOME and `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'`; **78 tests** in each suite. These package checks do not perform live broker/worker qualification.
- Host macOS 27.2 arm64, CPython 3.12.14; Docker Desktop 4.93.0, engine/client 29.8.1, Linux 7.0.14-linuxkit. Original protocol and pinned source identities, Markdown links/fences/whitespace, exact continuation inputs and Git whitespace checked before commit. Reindexed material new source before closure: generation `2026-10-02T16:40:02Z`, 3,350 nodes/5,890 edges; new runner and acceptance paths have metadata-match/no-recorded-issue coverage signals, with the best-effort caveat.

Smallest continuation: supply a disposable Ubuntu 24.04+ host with demonstrably working KVM or a separate macOS credential domain; approve the concrete outer memory/CPU/disk/deadline envelope and freeze operational identities/configuration. The current disposable Linux store demonstrates store isolation but cannot supply a local SBX VM. The owner input was requested during this session; no host or outer-VM approval was inferred from elapsed time. Prepare provider-free authenticated request and native-hook positive controls, then run the full synthetic boundary suite twice before design acceptance. If no suitable existing mechanism is available, retain denial. See [the precise continuation and input files](PHASE-2C-RESUME-PROMPT.md); no 2D prompt.

### Phase 2C / temporary KVM host capability — 2026-10-02

Outcome: **host capability checkpoint complete; full 2C remains blocked**. Base `121d6ece8d83b2eeb66c9ef36e400b28b3967ea1`, clean `codex/phase1-architecture`. Package **0.8.1** is documentation/evidence maintenance plus synchronized version metadata; no product behavior or runtime launcher changed. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Commit and current-branch push follow standing owner authorization; no merge or registry release.

The owner supplied temporary DigitalOcean SSH access and explicitly authorized tests before deletion. Initial shell inspection and preliminary Python KVM API/VM/vCPU creation succeeded. A new prospective protocol and exact trusted source were then frozen locally before two full HLT invocations. Each fresh Python process allocated 1,048,576 guest bytes, ran one x86 HLT instruction under a five-second signal alarm, returned API 12/exit reason 5 and closed its owned mappings/descriptors. A supplementary non-KVM-group UID/GID 65534 device-open attempt was denied; that control was not prospectively frozen and is labeled accordingly. Administrative root hardware access is not non-root worker qualification.

Host: Ubuntu 24.04.5 LTS, x86_64, Linux 6.8.0-142-generic; 961 MiB reported RAM, zero swap, approximately 22 GiB root disk free. Device root:kvm mode 0660, vmx CPU flag and kvm_intel/kvm/irqbypass modules observed. Protocol/source/sanitized observations and exact reproduction steps are in [KVM-HOST-ASSESSMENT.md](KVM-HOST-ASSESSMENT.md). No host address, password or real secret is committed. SSH used a dedicated first-use known-hosts file without an independently supplied console fingerprint; this limitation is recorded.

Cleanup: the independent final administrative `/proc/PID/fd` inventory found no KVM VM/vCPU handle; named SBX/sandboxd/QEMU process inventory was empty. No remote file, package, user/settings change, persistent VM, SBX binary, daemon, template, broker, native worker or provider operation was created by the session. SSH disconnected. These are final observations, not proof about every transient process. The owner may delete the Droplet; deletion is not performed or assumed. Future hosts require new evidence.

Verification: `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.360 seconds, local existing macOS/CPython development environment. `rtk proxy uv build --offline`: **0.8.1 sdist/wheel built**. No new fresh-wheel installation or denied-network wrapper was run for this documentation-only checkpoint; earlier installed-wheel evidence remains historical. JSON records, frozen probe SHA-256, synchronized versions, local Markdown links/fences/whitespace and Git whitespace were checked before commit. No new behavioral test was added. Caveman ultra persisted; native MCP Jev availability/decision check passed (0.02 for complete broker/native qualification, advisory only). Graph Verify startup status was ready, generation 2026-10-02T16:40:02Z; targeted version-symbol discovery and evidence-path coverage showed no recorded issues, with HANDOFF metadata changed and directly read. Graph coverage remains best-effort, not completeness proof. Final full reindex generation 2026-10-02T19:56:03Z: 3,408 nodes/5,956 edges. New assessment/JSON/version paths have metadata-match/no-recorded-issue signals; the plain-text probe snapshot is not tracked by graph source coverage and was read directly.

Smallest continuation: **Phase 2C only**. Supply/reverify a temporary KVM-capable Ubuntu host (the observed 1 GiB host sufficed for diagnostics only); prepare and freeze architecture-matching x86_64 SBX artifacts, disposable broker state, exact configuration and concrete outer/inner resource bounds before operational launch. Prior arm64 bundles cannot be reused on x86_64. Qualify inner enforcement, provider-free caller/request controls and actual native hooks/network with independently monitored positive controls; retain denial on any unavailable criterion. No full native/broker probe ran here. Use [the updated prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md); no 2D prompt.

### Phase 2C / operational preparation and pending resource decision — 2026-10-02

Outcome: **preparation checkpoint; operational qualification remains blocked**. Base `5f31bad0fe56a2aa80bfc7ba0c0c69bc721eb03d`, clean `codex/phase1-architecture`. Package **0.8.2** changes documentation/evidence and synchronized version metadata only. Delivery is the commit containing this entry, resolved with `git log -1 --format=%H -- docs/HANDOFF.md`; push the current branch under standing AGENTS.md authority. No release or Phase 2D work.

Live native MCP Jev and codebase-memory were available before project work. Jev startup check responded; final operational-readiness and full-qualification questions each returned 0.02, advisory only. Caveman ultra remains active for communication; persisted documents use normal prose. Verify-tier graph startup was ready; coverage generation `2026-10-02T19:58:04Z` matched seven initial evidence paths. Exact Darwin help-assessor source and its depth-one both-direction trace were inspected: it rejects non-Darwin hosts and cannot qualify this Linux profile. Trace suggestions resolving library names to document symbols are not material call evidence. New proposal/preparation/version paths had matching metadata and no recorded issues at generation `2026-10-02T20:06:34Z`; graph coverage is best-effort, not completeness proof. Final path coverage retained matching metadata except the just-updated HANDOFF.md, which was read directly; no structural claim relies on that stale document metadata.

Safe independent progress: checked current official release metadata and Docker credential/isolation documentation. Downloaded the official v0.46.0 Linux amd64 static archive into a new external directory, with a prospective local preparation plan containing expected URL/digest/size and 2 GB/30-minute bounds. Exact 82,815,215-byte archive SHA-256 matches GitHub's release API. Python data-filter extraction checked an expanded-size ceiling; every extracted regular file is recorded in [the sanitized preparation record](qualification/phase-2c-amd64-preparation.json). Elapsed preparation 11.19 seconds. External working root: `/var/folders/4p/xh823rjd32x53hbm_zvcjnqh0000gn/T/crewshal-sbx-amd64-7fliy5i3`. No previous temporary directory is required for reproduction. Published digest matching is not independent signature verification. No bundled executable/installation script was run; no template/image/native runtime, daemon, broker operation, remote connection or provider request occurred.

The [reviewable resource proposal](SBX-OPERATIONAL-PROPOSAL.md) supplies explicit memory/CPU/PID/disk/scratch/startup/total limits and cleanup/refusal requirements. It is not a frozen executable protocol: template/image/native runtime/toolchain/configuration, supported trusted dispatch and inner enforcement are still unresolved. The earlier 961 MiB total RAM observation does not establish proposed available-memory headroom. The owner was asked for current SSH alias/user/authentication mechanism and concrete resource approval; both remain pending. No silence is treated as consent, and no old shared password or credential store was accessed. Every original frozen manifest/grant is unchanged; execution remains denied.

Verification: `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.408 seconds, existing local macOS/CPython development environment. No new behavioral test is appropriate for preparation/documentation only. `rtk proxy uv build --offline --quiet`: **0.8.2 wheel/sdist built**. Inline project-interpreter validation passed for synchronized versions, preparation JSON, actual archive/extracted file digests/sizes/modes, unchanged original v1/SBX protocol v1/broker v3 manifest hashes and local Markdown links/fences/whitespace. `rtk proxy git diff --check` passed. No fresh installed-wheel, static-analysis or denied-network test rerun was performed for this documentation-only checkpoint; earlier results remain historical. No live operational or native acceptance run occurred; no whole-runtime criterion passed. No failure was promoted into a pass.

Smallest continuation: provide current disposable KVM-host access and decide the explicit proposal. Reverify hardware and resources; refuse insufficient headroom instead of silently resizing. Resolve every remaining identity/configuration/command and freeze a new operational manifest before creation; qualify inner enforcement before native startup, then run all twenty cases with provider-free positive controls twice. Next session remains Phase 2C only. Feed AGENTS.md, README.md, CHANGELOG.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2C-RESUME-PROMPT.md, KVM-HOST-ASSESSMENT.md, SBX-OPERATIONAL-PROPOSAL.md, qualification/phase-2c-amd64-preparation.json and every exact historical input listed by the resumption prompt. No Phase 2D prompt.

### Phase 2C / replacement hardware, Linux help and inner readiness — 2026-10-02

Outcome: **current hardware/headroom/help prerequisites pass; operational qualification remains blocked**. Base `f56e97a87d9cfb4db258ca7cec72198355af96ea`, initially clean `codex/phase1-architecture`. Package **0.8.3** changes documentation/evidence/process plus synchronized version metadata; no product runtime behavior changes. Delivery is the commit containing this entry, resolved with `git log -1 --format=%H -- docs/HANDOFF.md`. Push follows standing AGENTS.md authorization; no merge, deployment or registry release.

The owner requested host revalidation, missing-identity freeze and inner enforcement qualification. Caveman ultra instructions, live native MCP Jev and codebase-memory were checked before project work. Jev responds; final advisory probabilities are 0.89 for reached hardware/sampled-headroom prerequisites, 0.04 for full qualification and 0.08 for independently qualified inner enforcement. These are decision aids, not authorization or evidence replacement. Verify-tier graph project `Volumes-X10Pro-Crewshal` was ready; generation `2026-10-02T20:09:35Z` matched eleven initial evidence paths with no recorded issue. Exact `scripts.assess_sbx_protocol.run_assessment` source and depth-one both-direction trace were inspected with no pagination remaining: it rejects non-Darwin hosts, so it cannot be relabeled as Linux operational qualification. Low-confidence document-symbol trace edges are not material evidence. At generation `2026-10-02T21:00:11Z`, the initial twelve new/changed paths matched metadata with no recorded issue. Final generation `2026-10-02T21:14:30Z` (metadata recorded `2026-10-02T21:15:54Z`) matches twenty changed/new evidence and metadata paths with no recorded issue; the additional plain-text v2 runner is not tracked by graph source coverage and is read/hash-checked directly. The final handoff edit is also read directly. Coverage is best-effort, not completeness proof.

The owner confirmed deletion of the previous VPS and supplied a first replacement. A prospective replacement manifest binds the original trusted HLT protocol/source before two fresh Python invocations, each source-verified locally/remotely. API 12/exit reason 5 pass. Memory admission fails twice: 535,486,464 and 675,692,544 bytes versus required 939,524,096 (896 MiB). Total RAM is 1,008,185,344 bytes, zero swap; disk headroom passes. Exact first-host [assessment](REPLACEMENT-HOST-ASSESSMENT.md), [manifest](qualification/phase-2c-kvm-replacement-v1.json) and [observations](qualification/phase-2c-kvm-replacement-v1-observed.json) remain preserved. No cache clearing, service stop, swap, resize or operational fallback manufactured headroom; that host was left untouched after diagnostics.

The owner then supplied a second new temporary VPS. It reports Ubuntu 24.04.5, x86_64/kernel 6.8.0-142-generic, KVM device mode 0660/device 10:232 and ext4 root. A second prospective manifest precedes two fresh HLT passes. Both replacement profiles allocate 1,048,576 bytes per process with five-second alarm, ten-second command bound and 25-second trusted aggregate wrapper; process-owned handles close. On the second host, total memory is 2,063,577,088 bytes, zero swap; available memory 1,720,717,312 then 1,757,585,408 bytes and disk free 48,877,850,624 then 48,877,821,952 bytes satisfy sampled headroom. Root cgroup v2 controllers are available, but effective quota/aggregate/inner limits are unverified. Displayed root mount options have no quota option. Docker/SBX/setquota were absent in inspected PATH; no exhaustive filesystem absence claim. See [current host/help preflight](AMD64-HOST-PREFLIGHT.md), [second manifest](qualification/phase-2c-kvm-replacement-v2.json) and [second observations](qualification/phase-2c-kvm-replacement-v2-observed.json).

The matching official archive and every extracted regular file were reverified locally. An initial check omitted the actual `bundle/` extraction prefix and failed; correction then verified every identity. No new download was needed. The 82,815,215-byte archive was copied into an exclusively created second-host diagnostic directory, reverified remotely, safely extracted and checked file-by-file. No installer or global PATH installation occurred. Linux help v1 freezes identity/argv/environment/requested service properties, and six help/version commands exit zero, but its inline preparation/capture wrapper was not prospectively source-bound. Preserve that limitation in v1 observations; it is preparatory only. New v2 binds the exact runner text before two final six-command sequences. Every final command exits zero within the output cap under a fresh systemd service/private synthetic directories. Requested UID/GID 65534, network/tmp/system/home/proc restrictions, no-new-privileges, empty capabilities, 128 MiB/zero swap/one CPU/32 tasks/ten-second lifetime and successful systemd summaries are not independently observed native inner enforcement. No operational case is promoted. All profile/source/outputs are exact continuation inputs. Capture's post-collection cap is limited to trusted help output.

Observed SBX is v0.46.0/revision `991967dc90ce0d9a440cd1df1bdf3e395c5a2693`. Help confirms 512 MiB minimum, default auto CPU/always pull/read-only skills, user-selectable local exec, domain placeholder behavior and daemon-starting non-help settings. No daemon-start, settings read/write, store/login, sandbox-create/run, native worker, validator or provider request occurred. Current passwords were entered interactively; no address/password/private key is committed. Each host used a dedicated first-use SSH key then pinned later connections, without independent console fingerprints. No packages/accounts/host settings were changed or paid host provisioned by the agent. Only owned second-host diagnostic files were removed. Final independent snapshots show the diagnostic path absent, empty owned help-unit listing, no KVM VM/vCPU handle, no named SBX/QEMU process and no unreadable process entry. Final memory 1,755,480,064 bytes and disk free 48,877,772,800 bytes still meet sampled headroom. Supplementary inventory source is not prospectively digest-bound; no exhaustive transient-process or whole-runtime cleanup claim. SSH exited zero and disconnected. Owner controls host deletion; neither replacement deletion is performed or inferred.

Safe delivery also includes the independently observed inner placement/privilege, memory/swap, CPU, task, cancellation/deadline, scratch/disk and validator/cleanup requirements. The final non-executable readiness snapshot binds original inputs plus separate host/help/cleanup records and preserves the exact original grant/limits/twenty cases. It is finalized from preparation, not a pre-probe or executable operational manifest. Resource envelope approval was explicitly requested for the second host and remains unanswered. Effective quota/aggregate/inner controls, template/inner-image/native-runtime/toolchain/configuration identities, dynamic-download behavior, supported trusted dispatch, exact operational observers/commands and cleanup handles remain unresolved. No missing identity is invented. Current primary Docker/kernel documentation informs requirements only. Every historical frozen source/manifest stays unchanged and execution remains denied.

Verification in the existing local Darwin arm64/CPython 3.12.14 environment: `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.329 seconds, before documentation/version edits. `rtk proxy uv build --offline --quiet`: **0.8.3 wheel/sdist built**, repeated after final README changes. Inline project-interpreter checks cover synchronized wheel/package versions, all readiness/host/help/source/output bindings, immutable original v1/help/store identities/grants, hardware/headroom arithmetic, local Markdown links/fences/whitespace, exact continuation paths and absence of supplied addresses/passwords in public additions. `rtk proxy git diff --check` passes. No new behavioral test is appropriate for documentation/evidence maintenance. No fresh installed-wheel, static-analysis, denied-network or live native check ran; earlier results stay historical. No failure/unavailable observation was promoted.

Smallest continuation: obtain the exact envelope decision, reverify current second-host access/headroom and resolve operational quotas/identities/configuration/commands. Freeze a separate fully bound operational manifest before creation, qualify inner enforcement before native startup, then run all twenty provider-free native cases twice. No paid provisioning, resizing, relaxed worker limit or custom gateway is implied. Feed AGENTS.md, README.md, CHANGELOG.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2C-RESUME-PROMPT.md, PHASE-2C-READINESS.md, AMD64-HOST-PREFLIGHT.md and every exact original/first/second-host/help/source/cleanup/readiness input listed in the resumption prompt. Next milestone remains Phase 2C; no 2D prompt.

### Phase 2C resource approval and blocked operational freeze — 2026-10-02

Outcome: **resource envelope approved; complete operational identity freeze and inner enforcement unavailable**. Base `149c290e419249a446e2e67805d878b02e194525`, initially clean `codex/phase1-architecture`. Package **0.8.4** changes documentation/authority recording and synchronized version metadata only. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push follows standing AGENTS.md authorization; no merge, deployment or registry release.

The owner explicitly instructed approval of the linked envelope before operational identity freeze and inner qualification. Recorded that authority in [a separate approval record](qualification/phase-2c-resource-approval-v1.json), SHA-256 `872c244d2a28488a1379cb5e61f56567a2aa86cf3a2d954e019f06bd40105df1`, bound to the unchanged proposal, readiness snapshot and original v1 protocol. All approved ceilings and admission conditions are explicit. [Freeze status](RESOURCE-APPROVAL-AND-FREEZE-STATUS.md) separates known historical artifact identities from unresolved operational bindings. Historical proposal/readiness files and all twenty original cases/grants remain unchanged. Their pending-resource statements are historical, not a new approval requirement.

Current SSH alias/user and approved authentication mechanism were requested early in this session but not supplied at closure. No old password, credential store or inferred host connection was used. No remote connection, archive download/extraction, settings/store operation, daemon, VM, operational fixture, worker, validator or provider-shaped request ran. No operational manifest is claimed frozen; no inner or whole-runtime criterion is promoted. The smallest missing input is current authorized disposable host access. Complete artifact/configuration identities, aggregate/quota enforcement, supported dispatch and inner controls still require subsequent evidence after access. Resource approval grants no qualification, limit increase, paid provisioning, real credentials or Phase 2D authority.

Workflow availability verified before milestone work: RTK 0.50.0; Jev MCP live (successful initial literal check); codebase-memory project `Volumes-X10Pro-Crewshal` ready, Verify tier, initial coverage generation `2026-10-02T21:18:10Z`. Task-directed qualification search, exact `assess_qualification` snippet and both-direction depth-one trace confirmed unresolved identities/mandatory failures preserve denial. Relevant evidence paths have no recorded coverage gaps; best-effort coverage is not completeness proof. New documents are indexed at generation `2026-10-02T21:25:38Z`. Jev advisory batch returns resource approval 0.93 and support for an inner-qualified claim 0.04; direct owner instruction and concrete evidence govern, not probabilities. Product tests call no model. Current primary Docker settings/isolation documentation was reviewed as preparation only; a failed templates-page fetch supplies no evidence. No pinned-release command or runtime identity was inferred from current web text.

Verification on Darwin 27.2.0 arm64, CPython 3.12.14:

- `rtk proxy .venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.389 seconds before version/documentation edits.
- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.231 seconds after edits. No product/provider network. This uses the existing local environment, not a fresh installed wheel or Linux inner enforcement.
- `rtk proxy uv build --offline --quiet`: **0.8.4 wheel/sdist built**. Inline project-interpreter checks verify wheel metadata/package version, twenty historical readiness bindings, three approval bindings, false execution/native-start/freeze flags, original case count and unchanged historical tracked qualification inputs. Markdown local links, fences, whitespace and exact continuation paths checked; Git staged/unstaged whitespace checks passed before commit.

No new behavioral test was added for documentation/process maintenance. No fresh installed-wheel/static-analysis or live native qualification ran. Prior failures remain historical; all missing operational evidence stays unavailable. An initial console summary mistakenly said 21 historical bindings; the final check counts and verifies exactly 20. No persisted evidence used the mistaken count.

Next milestone remains Phase 2C operational qualification: provide current authorized host access; reverify admission/KVM/help with fresh prospective sources; resolve every binding; freeze the complete operational manifest; qualify inner controls twice before native startup. Then satisfy remaining native/provider-free whole-runtime gates. Feed AGENTS.md, README.md, CHANGELOG.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2C-RESUME-PROMPT.md, RESOURCE-APPROVAL-AND-FREEZE-STATUS.md, qualification/phase-2c-resource-approval-v1.json and every exact historical input listed in the continuation prompt. Do not request unchanged envelope approval again; no 2D prompt.

### Phase 2C current-host identity preparation and diagnostic decision — 2026-10-03

Outcome: **new host and candidate artifact identities verified; complete operational freeze/inner enforcement blocked**. This continues the 2026-10-02 session across local midnight. Base `72f9132a7f4f04a9cd7a23749cbb3511944955a6`, initially clean `codex/phase1-architecture`. Package **0.8.5** changes evidence/protocol/continuation documents, owner host-retention instructions and synchronized version metadata; no product execution behavior changes. Delivery is the commit containing this entry, resolved with `git log -1 --format=%H -- docs/HANDOFF.md`. Push follows standing authorization; no merge/deployment/registry release.

The owner reported deleting the earlier droplet after premature deletion guidance, supplied a new host and explicitly forbade deletion guidance until all required host work finishes and no further droplet is needed. Persisted that contract in AGENTS.md. Current root/password authentication succeeded; the address/password are absent from public evidence. First-use host key pinned privately, with no independent fingerprint verification. Do not repeat unchanged resource approval or request another host while the supplied host remains suitable. Preserve the droplet at this blocked/session boundary.

[Current preparation report](CURRENT-HOST-IDENTITY-PREPARATION.md) links exact prospective host/source/observations, fresh SBX preparation/help, public candidate-template metadata/layer preparation and final inventory. Two trusted one-MiB KVM HLT runs pass; sampled memory/disk admission passes; cgroup controller presence is observed, not enforced qualification. Exact SBX archive and every regular-file identity match. Twenty-four help/version invocations succeed in fresh systemd services. Codex candidate immutable manifest `sha256:4478aac4b542421404a5a5c860164f88c42c201e8730c1f3174c8d749f781703` and all layer/diff IDs match; selected entries identify Codex 0.149.1 and its native executable. No layer code ran or template was loaded. Combined download bytes 945,674,853, within the recorded two-GB preparation allowance. Host/toolchain and layer observations remain bounded, not full effective runtime bindings.

The full freeze gate still blocks operational creation: effective daemon/download/disk/configuration, supported dispatch and intended inner controls remain unresolved. Static binary strings cannot establish these. Settings help says reads may start the daemon; current Docker documentation describes model-service startup/download. Prepared a concrete source/identity-bound network-denied ten-second trusted daemon/settings diagnostic within the approved aggregate envelope, with independent namespace/controller/cleanup sampling. Requested a narrow owner exception through the async question; no answer arrived at closure. **The proposed diagnostic is not executed.** No settings/store/login, daemon, VM, worker, validator, provider/model call, host package/global setting or operational fixture creation ran. Every execution/native-start flag remains false. Original grants/criteria/historical profiles are unchanged; no inner/whole-runtime pass is claimed. A future approved diagnostic must reverify participating source/binaries and current admission before invocation, and must preserve restriction failures rather than relax them.

Final prospectively bound inventory finds no owned help/daemon unit, SBX process, KVM handle or unreadable process entry. Verified preparation files are deliberately retained: logical 1,190,184,184 bytes, allocated 1,190,252,544. Final available memory 1,708,994,560 bytes; disk free 47,687,544,832. Retaining artifacts supports continuation; fresh reproduction does not require an old directory. SSH exited zero and disconnected. Host deletion is not cleanup evidence or an authorized session closure step.

Verification and limitations:

- RTK shell proxy and existing CPython 3.12.14/macOS arm64 environment used. Jev MCP remains live; advisory check that host/help alone establishes inner enforcement returns probability 0.06 (not an authority or sole gate). Product tests call no model. Codebase-memory project remains ready; Verify-tier coverage generation for new evidence is `2026-10-02T21:58:45Z`. JSON/Markdown paths have no recorded gaps; `.txt` probe sources are not structurally tracked and were read/compiled directly. Final coverage generation `2026-10-02T22:00:00Z` reports changed or not-tracked metadata for eighteen edited/new paths; direct source reads, syntax/binding checks and documentation verification were used for those paths. Best-effort coverage supplies no completeness proof.
- Remote wrappers verify prospectively committed source digests in memory before trusted execution. Host HLT/diagnostic wrapper: `timeout 30s python3` with the bound host source and two ten-second subprocesses. Artifact preparation: `timeout 180s python3` with the pinned preparation source (7.305 seconds observed). Help: `timeout 180s python3` with twelve allowlisted argument lists twice. Template layers: `timeout 930s python3` with the 900-second source bound (58.047 seconds observed). Final read-only inventory: `timeout 10s python3` with its frozen source. Exact sources and parameters are committed; these wrappers use administrative SSH only, with no real credentials supplied to probe processes. Shell output capture of trusted diagnostics is post-collection, not hostile-output qualification.
- Inline project-interpreter checks verify all twenty unchanged historical readiness bindings, prospective source hashes/syntax, two host and two twelve-command help sequences, headroom arithmetic, template manifest/layer/diff-ID agreement, false execution flags, synchronized package/wheel versions, local Markdown links/fences/whitespace and all exact continuation files. Git staged/unstaged whitespace checks pass before commit.
- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 passed**, 4.387 seconds. Existing environment, not a fresh installed wheel or Linux inner qualification. `rtk proxy uv build --offline --quiet`: **0.8.5 wheel/sdist built**. No new product behavioral tests or fresh installed-wheel/static-analysis/native checks.
- Preserved limitations: current help's copied unused historical path/cleanup fields are not used by its executed source; `model --help` prints top-level help, not a supported model subcommand. Unbound static environment scanning produces concatenated Go strings; broader regex scanning timed out after ten seconds, followed by bounded context lookup. Those inspections supply no configuration or negative/qualification claim. OCI selected entries do not reconstruct the entire effective overlay. First-use host-key trust and unsigned sanitized local transcriptions limit provenance.

Next milestone remains Phase 2C. The smallest input is the proposed bounded daemon diagnostic decision, not a new droplet or resource-envelope reapproval. With explicit approval, reverify and run only that prospective diagnostic; then resolve effective settings/download/disk/dispatch/inner identities, freeze full operational protocol and qualify exact inner controls twice before native startup. Feed AGENTS.md, README.md, CHANGELOG.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2C-RESUME-PROMPT.md, CURRENT-HOST-IDENTITY-PREPARATION.md, DAEMON-CONFIG-DIAGNOSTIC-PROPOSAL.md and every listed original/current-host/template/prospective diagnostic source/profile/observation input. Keep the current droplet. No Phase 2D prompt.

### Phase 2C bounded daemon/settings diagnostic closure — 2026-10-03

Base revision: `0534d2e8fb9f033b1bc8ac93f4ef1b0bd13d15e6`, branch `codex/phase1-architecture`, initially clean except this session's new companion authority record. Package **0.8.6** is documentation/evidence maintenance only. The owner selected continued probes on the existing droplet. The exact authorized v1 daemon/settings source was invoked twice through a SHA-256-checked stdin payload under `timeout 30s python3`. It verifies its pinned tool/library/SBX bytes and uses `systemd-run --pipe --wait --collect` with the recorded private network/devices/tmp, synthetic state, 256 MiB memory, one CPU, 128 tasks, zero swap and ten-second limit.

Both invocations exit zero with identical settings, eight independent effective service samples each and empty final owned-unit/process/KVM inventories. Times: 3.553 and 3.192 seconds. The effective default Docker data volume is 10g; no logical disk fitting the approved aggregate has yet been observed. Full inner controls and caller/request authority are unavailable. The missing prospective mkdir identity, incomplete transitive/standard-library bindings, sampled-shell scope and post-capture output bound remain explicit limitations, not silently repaired historical evidence. See [the complete assessment and exact observations](DAEMON-CONFIG-DIAGNOSTIC-ASSESSMENT.md). No original profile or grant changed. No VM, template load, native worker/validator, store/login/provider request or Phase 2D work ran.

Independent final read-only confirmation found the owned service/cgroup absent and preparation archive retained. SSH exited zero. Keep the host and verified artifacts; host deletion is not fixture cleanup and is not authorized at this blocked boundary.

Verification on macOS 27.2 arm64 / CPython 3.12.14:

- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 tests pass**, 5.269 seconds. Tests use their own fixtures and no paid provider service; these remain package refusal/behavior tests, not inner qualification.
- `rtk proxy uv build --offline`: sdist and wheel for 0.8.6 built successfully with cached pinned backend. No package release or fresh-wheel-install qualification is claimed.
- An independent local checker verified authority/profile/source hashes, Python source syntax, JSON settings equality, observed exit/output/cleanup outcomes and execution-denial flags. Changed Markdown links/fences/whitespace, JSON parsing and Git diff whitespace checks pass before checkpointing. No new product tests were added for this evidence-only change.
- Jev's live decision screening returned 0.03 probability that these host diagnostics establish complete inner enforcement; direct evidence independently denies that claim. Codebase-memory reports ready with no recorded parse/skipped gaps, but its coverage generation remains `2026-10-02T22:00:00Z` and operated files are changed/untracked. Exact source/doc/JSON reads supply fallback evidence; no graph completeness claim is made.

Commit and push this coherent checkpoint under the standing owner authorization; delivery revision is the commit containing this entry. Resolve it with `git log -1 --format=%H -- docs/HANDOFF.md`. Next session resumes 2C on the same retained host, resolves supported trusted inner dispatch/controls and remaining identities, freezes the complete prospective manifest, then runs inner oracles twice. The exact bounded diagnostic decision and unchanged resource approval are resolved; do not ask again. A new gateway or changed credential design remains a material architecture gate. Use [the prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md); no 2D prompt is supplied.

### Phase 2C private configuration and host quota controls — 2026-10-03

Base revision `37b6826a36e7d7eb6e453206894cf26c9a6b3254`, branch `codex/phase1-architecture`, initially clean. Package **0.8.7** is documentation/evidence maintenance with no public runtime API change. The owner instructed control resolution, complete freeze and qualification twice on the same retained droplet. [The assessment](CONTROL-RESOLUTION-ASSESSMENT.md) links every prospective source/profile and captured result. Host: Ubuntu 24.04.5 x86_64, kernel 6.8.0-142-generic, existing root/password access with first-use pinned SSH key and no independent fingerprint verification. No package/global configuration change, VM/image load, native worker/validator, login, provider call or credential-store access occurred.

Configuration source SHA-256 `47e6be9fbf05a03befd229163ca8b242029129d0d3dd1ec02043959c77c8c34d` now includes prospective mkdir identity. Two invocations (4.278/4.305 seconds, exit zero) restart the private daemon and reproduce forwarding false, skills off, Docker default 1g, diagnostics consent no, empty kit sources and experimental features false. Creation-time 3g/1g environment does not establish effective guest disks. Scoped services, owned PIDs and KVM handles are absent afterward. Host-service settings are not guest/inner qualification.

XFS quota v1 fails its cleanup observer's empty-output JSON parser; no structured quota result is promoted. Separate read-only checks confirm loop/mount absence before exact owned-root removal. V2 fixes parsing prospectively, but its strict EDQUOT oracle fails on project-quota ENOSPC. Primary upstream Linux v6.8 source informs v3 before execution. V3 reaches exact 32/16 MiB allocated limits with independent reports and over 400 MiB free, but accepts 64 MiB sparse logical files with zero allocation in both fresh fixtures. Physical quota alone fails logical-byte enforcement.

A separate combined prototype (source SHA-256 `61cf44f20aa3bebbbc704e65e18c29cf745a2214e91e76e3cb9c66e3afe4cd03`) installs 512 KiB hard RLIMIT_FSIZE, 64/32 inode quotas and link/linkat seccomp denial before privilege drop. Initial client capture truncation is retained as no-pass evidence. A complete unchanged-source invocation (1.188 seconds) produces two fresh fixtures: all four bounded regular-file tests deny hard-limit increase, oversized truncate, hardlinks and inode exhaustion. Outside counts/sums agree: scratch 33,030,144 bytes each; candidate 15,728,640/16,252,928 bytes. Native compatibility, metadata, full runtime policy, placement and descendant inheritance remain unproved. Python standard-library/OS identities and trusted observer post-capture output limits are diagnostic limitations; no complete operational identity or inner pass is claimed.

Final read-only inventory finds no owned configuration/quota/logical root, mount or service. Preparation artifacts remain; available memory 1,732,120,576 bytes and disk free 47,643,914,240 bytes. SSH exits zero. Keep the host at this boundary.

The original pre-creation gate requires effective guest/inner facts not statically established. A concrete [trusted infrastructure-discovery ordering amendment](PHASE-2C-INFRASTRUCTURE-DISCOVERY-DECISION.md) is prepared and requested through the async question; no answer is recorded at this checkpoint. It permits only prospectively pinned trusted guest inspection under unchanged independently enforced bounds, no agent/login/provider access. No VM invocation occurs under the unanswered proposal. Complete freeze must still precede inner/native tests. If an answer arrives in the continuing chat, record it separately and do not ask again. No changed envelope or new droplet is requested.

Verification:

- Source hashes, embedded Python compilation, structured observation assertions, Markdown links/fences, whitespace, secret exclusion and historical-profile byte equality are checked directly. New graph paths are untracked and existing metadata changed at generation `2026-10-02T22:00:00Z`; Verify coverage is best-effort, not completeness proof. Local checker schema/section-name mistakes are corrected without changing frozen sources or historical observations.
- Jev is live; advisory support for whole-runtime qualification is 0.07, confidence 0.86. Concrete missing controls independently preserve denial.
- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 tests pass in 4.067 seconds**, macOS 27.2 arm64/CPython 3.12.14.
- `rtk proxy uv build --offline`: sdist/wheel 0.8.7 build successfully; no release or fresh-wheel-install qualification is claimed.

Next milestone remains 2C. Resolve the exact ordering proposal on the same retained host, establish prospective aggregate bounds, inspect supported effective guest/inner identities if authorized, freeze the complete operational manifest, then qualify inner enforcement twice before native/broker cases. Use [the continuation prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md); no 2D prompt. Commit/push under standing authorization; delivery revision is the commit containing this entry, obtainable with `git log -1 --format=%H -- docs/HANDOFF.md`.

### Phase 2C approved discovery and authentication refusal — 2026-10-03

Base revision `aeb5cdeae5dc9eec05f38c95e2268114aad05fc6`, branch `codex/phase1-architecture`, initially clean. Package **0.8.8** is evidence/process maintenance. Direct owner approval is recorded separately against discovery proposal SHA-256 `46aa89646ebf5a3d51d2af425cb3f43b36833c68d1adec4708da040a685b69cb`; the original proposal and all historical profiles remain byte-identical. No repeated resource/discovery decision is needed. Same retained Ubuntu 24.04.5 x86_64/kernel 6.8.0-142-generic host, private pinned first-use SSH key without independent fingerprint verification. Connection material is absent from public evidence.

[Assessment](GUEST-DISCOVERY-ASSESSMENT.md) links every prospective source/profile/transport and result. V1 source `a95c381cf3ded49856b11d2306c9ab93ebc4e91f0e3a7516994f45b1f2340f97`, transport `0d42ec4d5e23b5897283d0ad2e7b7fd1622e3480f834d581c5adb07d6fc3e776`: two device-open EPERM admissions, before daemon/create. V2 source `c28de9c0122ef02fd70807608335611a5e2ba389252d84ec62f8697fa72aab31`, transport `691257ecdb62b274fd99e42a780e33182ec1f914c0041f5d6e906ace9a68f0a9`: prospective KVM/TUN DeviceAllow correction; original aggregate memory 805,306,368, CPU 100000/100000, tasks 128 and swap zero observed before SBX commands. Service-private tmpfs 128 MiB/96 inodes and hard 64 MiB per-file limit yield a conservative 6 GiB mutable regular-file upper bound plus 1,190,184,184 prepared bytes. This conservative shape may reject template/guest writes and is not an operational layout. ProtectControlGroups/ProtectKernelTunables are not explicitly set and descendant-migration denial is not observed; controller readback is not cgroup escape qualification. Python standard-library manifest (627 files) and every bundle/helper/library identity are checked. Service observer is inside aggregate; SSH/systemd transport and supplementary observer are outside, so full all-host-process accounting remains unproved.

V2 total 9.006 seconds, two fresh services, two HLT executions per service pass. Settings updates/readback succeed, but forwarding requires restart and this admission source does not restart; preserve limitation. Actual mountless `create shell` with exact template digest, pull never, skills off, 512m and one CPU returns exit one/401 Unauthorized before runtime lookup succeeds in both fixtures. Subsequent private list also refuses authentication and supplies no runtime inventory. No template/image load, SBX guest, inner command, native attachment, login, existing session import, provider/model call, package/global host change or custom gateway occurs. Fresh synthetic authentication absence is not whole credential-domain qualification. The approved exception explicitly requires stopping when sign-in is required; complete operational freeze stays false and inner run count is zero.

Owned-unit listings/KVM handles are empty after both variants. Final supplementary inventory additionally finds no named SBX process, unreadable process entry or host synthetic path. Preparation remains; memory available 1,709,228,032 bytes, free disk 47,641,702,400 bytes. SSH exits zero. Keep the host at this blocked boundary. Supplementary final inventory is not prospectively source-bound; systemd peak summary/RSS disagreement does not establish peak/stress qualification. Two systemd documentation fetches return HTTP 403 and supply no source evidence; device behavior is established by the recorded runs.

Verification: RTK required throughout; Caveman ultra, Jev and codebase-memory available. Jev direct-authorization advisory probability 0.78/confidence 0.56; direct owner statement governs. Graph Verify project ready, generation `2026-10-02T22:00:00Z`; new/stale paths receive exact-source fallback. Hash/compile/JSON/observation, local-link/fence, whitespace/secret and historical immutability checks are performed. Network-denied command `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 tests pass in 4.679 seconds**, macOS 27.2 arm64/CPython 3.12.14. `rtk proxy uv build --offline` builds sdist/wheel 0.8.8 successfully; no release or installed-wheel qualification claimed.

Next milestone remains 2C: resolve a separately authorized isolated Docker-account authentication/network/credential-domain path or an officially supported unauthenticated path; then source-bind and inspect guest state, complete freeze and qualify exact inner enforcement twice before native/broker criteria. Do not re-request resolved resource/discovery authority or retry unchanged no-session create. [Continuation prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md) are updated. Commit/push under standing authorization; delivery revision is the commit containing this entry, obtainable with `git log -1 --format=%H -- docs/HANDOFF.md`. No Phase 2D prompt.

### Phase 2C frozen-source whitespace correction — 2026-10-03

The final 0.8.8 `git diff --cached --check` returned exit 2 for a final blank line in each of the four frozen discovery runner/transport files. The command sequence incorrectly continued to commit/push `a5ea687c7ec336a9df7fbd9467864ede111e83b4` after that failure. No source/observation bytes or security verdict are changed. Version **0.8.9** adds exact-path `.gitattributes` entries permitting final blank lines for those four already-executed artifacts while retaining normal whitespace checking elsewhere. Hash bindings and historical profile equality are rechecked; the staged whitespace check and offline 0.8.9 build pass. No new host probe occurs. Preserve this failed check and corrective commit; no force push or history rewrite. The supported Docker authentication prerequisite and all operational/inner/native denials remain unchanged. Use the same [continuation inputs](PHASE-2C-RESUME-PROMPT.md).

### Phase 2C isolated authentication and authenticated import refusal — 2026-10-03

Base revision `539a0ff17a493151496b7a5e1ce802230c20fe37`, branch `codex/phase1-architecture`, initially clean. Version **0.8.10** records evidence/process maintenance. The owner explicitly requested isolated Docker authentication; separate authority supersedes only this login prerequisite, leaving original resource/discovery proposals immutable. [Assessment and exact sources](ISOLATED-DOCKER-AUTHENTICATION.md) preserve all observations, failures and limitations.

Device v1 expires at 585.090 seconds; owner requests a fresh code. V2 JSON-as-Python profile fails before ready/login. Corrected v3 device login exits zero after 116.561 seconds; kernel readback verifies 256 MiB memory, zero swap, one CPU, 32 tasks and attached ingress/egress BPF filters before login. Exclusively owned private state remains on the same Ubuntu 24.04.5 x86_64/kernel 6.8.0-142-generic host. No ambient store/provider login is accessed. New state and private diagnostic copies are protected by private directories; file fallback, shared UID and shared CDN address limitations remain disclosed. Host SSH key is first-use pinned without independent fingerprint verification. No credentials or device codes enter public evidence.

Exact manifest/config bytes match original digests. All 16 layers are checked before deterministic archive preparation: 862904320 logical bytes, SHA-256 `26b27211f7244b76ba2556db29b76a2b1c9c9ba9efe7c192f9afed4bba8b47c0`, elapsed 9.540 seconds. Two placeholder transport-hash assertions fail before execution and are corrected; original JSON reserialization is not lossless. Preparation is outside the operational aggregate, and elapsed assertion is not an external hard deadline.

Authenticated discovery v1 reproduces two private-directory permission failures. Prospective v2 root-owned copy of only new authorized state resolves this: both fresh listings exit zero, without prior 401; template import returns exit one/500 twice. V3 debug output reaches 65536 bytes and truncated-summary JSON fails; incomplete capture is retained as no-pass evidence. V4 bounded diagnostics reproduce containerd ENOSPC in two fresh fixtures, 20.191 seconds total. Post-stop tmpfs readback has 237568 allocated bytes and 23 free of 96 inodes; exact transient exhaustion cause is not proved. Original aggregate memory 805306368, swap zero, one CPU and 128 tasks are observed; HLT passes twice in each fresh fixture. ProtectControlGroups/ProtectKernelTunables are explicit. No create follows failed template import, so no guest, complete manifest, inner/native attachment or provider/model call exists. Inner run count remains zero. Conservative file/inode shape is not runtime compatible; full logical/allocated accounting, descendant escape and daemon restart limitations remain.

Supplementary final inventory finds no running owned units or KVM VM/vCPU handles; failed auth v2 unit is inactive. Private original sign-in, protected copies, raw diagnostics, archive and host remain. Available memory 1695133696, free disk 46763958272 bytes. No deletion recommendation. Next capability is runtime-compatible independent logical/allocated storage within unchanged envelope, not repeated authentication authority or a replacement host.

Verification: RTK throughout; Caveman ultra, Jev and graph Verify available. Graph project ready with stale/untracked new paths; exact source/hash/embedded-profile/compile/JSON fallback supplies evidence, not graph completeness. Original tracked qualification inputs remain byte-identical. Network-denied offline suite: **78 tests pass in 4.678 seconds**, macOS 27.2 arm64/CPython 3.12.14. Offline 0.8.10 sdist/wheel build and whitespace/secret/local-link checks are recorded at publishing. No installed-wheel or package-registry release is claimed.

Next milestone remains Phase 2C: resolve supported bounded cache/guest storage, freeze complete effective operational identities, qualify inner enforcement twice, then original native/broker criteria. Use [continuation prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md). All execution/native permissions remain false. Commit/push under standing authorization; delivery revision is the commit containing this entry, obtainable with `git log -1 --format=%H -- docs/HANDOFF.md`. No Phase 2D prompt.

### Phase 2C storage investigation and access prerequisite — 2026-10-05

**Blocked, not complete.** Base revision `622f9bb1ac54c5727c9e5dd8b390cc157f505217`; clean `codex/phase1-architecture` at startup. Version **0.8.11** records documentation/process maintenance, not storage resolution. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push the current branch under standing authorization; no merge, deployment or registry release.

[Storage investigation](STORAGE-CONTROL-INVESTIGATION.md) distinguishes primary-source candidates from observed controls. FAT/eCryptfs and immutable-cache layouts are not selected, available or runtime-compatible by evidence. All original ceilings/grants remain unchanged. Current host address/user/authentication context is absent from this session; the owner was asked for it. No ambient credential-store, SSH configuration or prior private history recovery was attempted. No remote operation, template load, guest creation, operational freeze, inner/native probe or new whole-runtime pass occurred. Host survival/access and retained account/preparation are unverified current facts; keep them, do not request deletion or another droplet.

Caveman ultra, Jev MCP live calls and codebase-memory Verify were available. Jev chose awaiting current access (probability 1/confidence 1) over unchanged import, limit increases or historical qualification. Advisory output does not grant authority. Graph project `Volumes-X10Pro-Crewshal` generation `2026-10-02T22:00:00Z` was ready; qualification/test paths matched metadata without recorded gaps. Authenticated discovery v4 profile/source were untracked by this generation and were read directly. Both-direction qualification trace and exact source were inspected; no completeness claim.

Verification: `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **78 tests pass in 5.306 seconds**. Offline package regression does not qualify storage/runtime. `rtk proxy uv build --offline` built the 0.8.11 sdist/wheel successfully; no installed-wheel or registry release is claimed. Version synchronization, Markdown links/fences and all 201 continuation input paths passed checks; 145 tracked historical qualification files are byte-identical to HEAD, including the original v1 manifest digest. `rtk proxy git diff --check` passed. Historical qualification artifacts remain unchanged; all execution/native-start flags stay false.

Publishing environment: macOS 27.2 arm64, CPython 3.12.14. Final graph coverage generation `2026-10-05T10:40:58Z` matched changed paths except the just-updated handoff; its exact diff/source supplied fallback. No recorded gap is a best-effort signal, not completeness.

Smallest immediate missing input: current retained-host connection context, with host-key fingerprint if available. Next milestone remains 2C: reverify host/preparation/account, independently resolve supported aggregate logical/allocated storage, then complete freeze and qualify twice. Use [the continuation prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md), including the new investigation. No repeated resource/discovery/login approval or Phase 2D prompt.

### Phase 2C Linux test cost and host policy correction — 2026-10-05

Base `c67959c8847074b53cbfeb661720747430134d4c`; version **0.8.12**, documentation/process maintenance only. The owner explicitly revoked required droplet retention and intends to remove the current host. Deletion was not observed or performed by this session. Host-only private authentication/preparation may be lost; historical public observations remain immutable and do not require a live host to read.

AGENTS.md now prohibits routine VPS tests at each session and requires a substantial round of changes before considering a necessary paid-host test batch. Local tests and the owner's VMware Ubuntu may be used when sufficient/available. Observe actual local capabilities; do not claim VMware equivalence or KVM support without evidence. Ask the owner to prepare a droplet only when a necessary test cannot be satisfied locally, with a concrete bounded test batch. Existing ceilings remain unchanged; any new paid-host batch requires approval. No host connection request is a prerequisite to the next development session.

Updated README/changelog/plan/continuation and investigation policy note. No product behavior changed; no remote operation, new offline test, VM inspection, runtime qualification, freeze or Phase 2D work occurred. Version/link/fence/input/historical-integrity and Git whitespace checks validate this documentation change; no runtime suite is needed for this policy edit. All execution/native flags remain false. The prior 78-test result belongs to the preceding checkpoint, not a fresh run here. Delivery is the commit containing this entry, pushed under standing authorization.

Next scope remains 2C storage/control resolution and a reviewable test batch after substantive progress. Feed AGENTS.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2C-RESUME-PROMPT.md and its exact input list. Initial prompt: continue 2C locally under the revised cost policy; resolve supported storage controls, assess VMware Ubuntu only if necessary, and request droplet tests only when a necessary acceptance check cannot be satisfied locally. Preserve unknowns and unchanged limits; no 2D.

### Next-session preparation and confirmed droplet removal — 2026-10-05

Base `86ec4643dce68077cb2080edd5996a785a73cadd`; version **0.8.13**, documentation/process maintenance. The owner replied “done” after announcing droplet removal; removal is now owner-confirmed, not independently inspected. Host-only account/preparation availability must not be assumed. No private state was recovered or exported, no remote action or runtime test occurred, and no qualification gate changed.

Prepared a standalone local-first Phase 2C prompt in PHASE-2C-RESUME-PROMPT.md, retaining its 201 exact input files and all original limits. Next session must make substantive storage/control progress before considering any necessary Linux batch. Local VMware Ubuntu is an optional test substrate to assess only if needed; a droplet batch requires a concrete necessity explanation and owner approval. Version/link/fence/input/historical-integrity and Git whitespace checks validate this documentation-only change. Delivery is the commit containing this entry, pushed under standing authorization. No 2D work.

### Phase 2C local storage design and diagnostic preparation — 2026-10-05

**Blocked, not complete.** Base `d656f4f95c07eee2529e55220ef614863b4132ed`; clean `codex/phase1-architecture` at startup. Version **0.8.14** is diagnostic/process maintenance; product runtime behavior and qualification gates do not change. Delivery is the commit containing this entry, resolvable with `git log -1 --format=%H -- docs/HANDOFF.md`. Push under standing authorization; no merge/deployment/registry release.

Delivered [storage design/accounting](PHASE-2C-STORAGE-DESIGN.md), [reviewable dependency-ordered Linux batch](PHASE-2C-STORAGE-BATCH.md), offline accounting checker, synthetic file-operation payload, two budget fixtures, source preparation bindings and a sanitized local observation. Separate upper/lower/backing/guest logical views and deleted-open inodes require explicit inventory. The naive historical encrypted disk layout totals 10,643,042,212 logical bytes before omitted items and is refused. New archive+bundle preparation could be 1,107,398,941 logical bytes before diagnostics; actual allocation and compatibility remain unknown. No accounting convention or resource ceiling was silently changed. Fit arithmetic is not enforcement or completeness.

Pinned Linux v6.8 research paths suggest eCryptfs fills growth holes; installed-kernel behavior and exact SBX I/O compatibility are unobserved. Standard ecryptfs-add-passphrase targets the user keyring, so a private session alone does not isolate its access. Supported exclusively new key setup, lower/FD/key/mount/cgroup bypass denial, independent observer/supervision, effective guest sizing and supported cache placement remain precise blocking capabilities. No key/module/package/mount, Linux worker, template import, VM/inner/native/provider operation or new paid-host test ran. Host: Darwin arm64; installed Fusion `vmrun list` exited zero with zero running VMs, which proves neither guest absence nor KVM capability. Owner-supplied local Ubuntu access was asked for asynchronously and not supplied at this closure. No droplet was requested or provisioned; prior host removal/credential loss remains accepted.

Failure retained: first six-method diagnostic test run failed with `AttributeError: module 'os' has no attribute 'setxattr'`; prospective API-availability check now records ENOSYS. Eleven diagnostic cases ran in each of two fresh macOS fixtures; preallocation/copy-range/reflink/hole-punch/xattr cases preserve unavailable errors. These trusted local facts are not independent Linux enforcement or native compatibility. Record/source bindings are preparation, not a retrospectively frozen Linux qualification profile.

Verification before final source integration: 89 network-denied tests passed in 5.299 seconds; lint/format/types passed. A bounded-reader CLI check then added one meaningful method; twelve focused storage methods passed in 0.090 seconds. Final integrated checks and publishing evidence are recorded below. Test environment: macOS 27.2 arm64, CPython 3.12.14. No installed-wheel or registry-release claim.

Graph Verify: project `Volumes-X10Pro-Crewshal`, generation `2026-10-05T10:50:48Z`, ready. Exact qualification gate source and both call directions were inspected; relevant one-hop trace had no pagination. Candidate coverage matched old paths; authenticated v4 text source was not tracked and was read directly. New diagnostic files receive direct source/compile/tests and final coverage checks; no graph completeness claim. Jev advised diagnostic preparation (probability/confidence 1, reported cost zero), not qualification or infrastructure spend; advisory output grants no authority. Caveman ultra remains active.

Final integration: `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .` passed **90 tests in 5.515 seconds**. `rtk proxy .venv/bin/ruff check src tests scripts` and `rtk proxy .venv/bin/ruff format --check src tests scripts` passed (32 files formatted); `rtk proxy .venv/bin/mypy` passed (10 product source files). `rtk proxy uv build --offline` built the 0.8.14 sdist/wheel. No installed-wheel or platform qualification is claimed. Final version/source/input/link/history/whitespace checks follow the publishing ceremony; failed earlier checks stay recorded.

Publishing checks: synchronized 0.8.14 versions, all 210 unique continuation input files, eight source bindings, eight changed/new Markdown files' local links/fences, three diagnostic/test compile checks and the unchanged original protocol digest passed. All 145 historical tracked qualification files remain byte-identical to HEAD; Git whitespace passed. Final graph coverage generation `2026-10-05T11:15:41Z` matched all changed paths without recorded gaps. The probe trace heuristically mapped some standard-library calls to unrelated JSON/durable symbols; exact source supplied fallback, and those graph edges are not asserted as real dependencies. No completeness claim. The subsequently updated handoff is validated directly.

Smallest continuation: authorized disposable local Linux shell for mechanism admission, then supported exclusively new key/mount setup and independent bypass/FD/lower observation. Bind exact tools/source/profile before Linux invocation; qualify fresh mechanism fixtures twice before considering an exact amd64/KVM SBX compatibility batch. Operational batch remains non-executable; no claim that a missing manifest is complete. Use [updated initial prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md), including every 0.8.14 storage input. Retain all original 20 cases/limits/grants and false execution/native flags. No 2D.

## Open gates and risks

- 2A and 2B passed their offline gates. 2C is blocked: Docker is connected; nine filesystem/environment cases, four separate synthetic lifecycle/validator cases and a separate twelve-attempt synthetic network subset passed twice. Full network/native configuration, whole-runtime binding/refusal and accepted credential mediation remain unresolved. See [the current Linux checkpoint](LINUX-SUBSTRATE-PROBES.md) and [historical reuse assessment](EXECUTION-QUALIFICATION.md). No runtime adapter or live implementation should be added early.
- 2C must qualify the complete execution boundary and decide reuse from behavior evidence. Credential mediation is unresolved; a Docker executable is not evidence of containment.
- 2D/2E need explicit bounded live-run authority and resource ceilings. Missing provider identity blocks strict independence.
- 3A needs legal corpus selection, baseline conformance, frozen criteria and spending approval. Numerical thresholds remain proposals.
- Swift/.NET execution support is not delivered. Hold-outs stay sealed. Release/product expansion remain owner decisions.

## Next-session prompt — Phase 2C

Continue Phase 2C from 0.8.20. Read [the current initial prompt and exact input files](PHASE-2C-RESUME-PROMPT.md). The fixture-only v2 decision is resolved; do not ask again. Obtain the direct answer to the scoped v4 setup-only `attach_disconnected` question before loading it. After approval, recreate fresh pinned data, run the explicit tiny payload oracle, then complete broker/native separation and all twenty original cases twice on one complete frozen profile. Historical subsets do not compose. No SBX storage research, changed limits, paid provider, custom executor/gateway or Phase 2D.

### Phase 2C / local Linux storage observation milestone — 2026-10-05

Base `c30c8eb270520d6fc5296f1864d0d1ee3a26e411`, clean branch `codex/phase1-architecture`, package 0.8.14. Delivery 0.8.15; resolve delivery revision through the commit containing this entry. [Assessment](PHASE-2C-LOCAL-STORAGE-ASSESSMENT.md), [prospective profile](PHASE-2C-LOCAL-STORAGE-PROFILE.md), final v6 profile/bindings/observation and separate failures record the bounded milestone. Two fixtures: 47.298/47.495 seconds, 44 observations, maximum command 2.174 seconds, aggregate memory peak 105021440 bytes. All final independent FD/device/inode/length/allocation/link/PID matches pass. Raw output SHA-256 `9ed71c46226508d5a8aa7fff663f03aba54c06c95a5d47f916d7736ef1aeaaa3`; 435812 bytes. No full runtime qualification is inferred.

Verification: `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **93 passed, 5.656s**. `rtk proxy .venv/bin/ruff check src tests scripts`, format check and mypy pass; mypy covers 10 product source files. `rtk proxy .venv/bin/python docs/qualification/phase-2c-local-storage-readback-v1.py` verifies 44 recorded matches; `rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-local-storage-budget-v2.json` returns arithmetic-only totals 654311424 in each dimension and denial. `rtk proxy uv build --offline` built the 0.8.15 sdist/wheel. Final validation confirms 246 unique existing continuation inputs, 149 previously tracked qualification files byte-identical, all six source/archive/manifest bindings matched, synchronized version, local links/fences and clean diff whitespace. Ruff format covers 36 source/test/script files. Publishing uses the standing commit/push authorization; delivery revision is the milestone commit. No fresh installed-wheel claim.

Failures/unknowns are preserved in the assessment and immutable v1–v5 refusal/source/profile records. Unsupported operations, kernel-module/full operational identity, privileged chown, full escape coverage, deleted-open lower-capacity sampling and global-sync diagnostic behavior remain explicit limits. No provider, model product call, SBX, inner/native probe or paid infrastructure ran. Jev live workflow decisions returned cost zero; it is owner-requested assistant support, not product qualification. Codebase-memory Verify graph/trace/snippet/coverage was used throughout; generation 2026-10-05T15:59:52Z reported current metadata/no recorded gaps for the new sources/tests/profile. Earlier heuristic trace edges misresolved standard-library names into evidence/product symbols; exact source was used. Clean graph metadata is not completeness proof.

External cleanup observes cgroup populated zero, no owned host mount/loop, removed fixture/inputs/slice file and sixty known new report paths; failed transient units reset. The final client exited and its bridge was removed. Test VM remains running, keyutils retained, no credential saved in project files. Future sessions must not assume access or recover ambient authentication. Preserve all earlier qualification bytes. Next session follows [the updated initial prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md) for pinned runtime storage compatibility/admission only; no Phase 2D.

### Phase 2C pinned storage requirements / blocked layout — 2026-10-05

Base `d163c4752fcbfddd35f01b695831208a18db90ad`, initially clean `codex/phase1-architecture`, package 0.8.15. Delivery 0.8.16 is the milestone commit containing this entry. [Requirements](PINNED-SBX-STORAGE-REQUIREMENTS.md) and [research](qualification/phase-2c-sbx-storage-research-v1.json) bind fresh release data, eleven exact bundle members, nine public source files and two release statements. ELF/Go metadata identifies dirty source and private containerd/diskfs replacements; declared private EROFS patches and anonymous source-access 404 results are preserved. No authentication, installer, bundled executable, daemon, template, VM access, provider, paid host or original qualification case ran.

Source findings are conditional: the provenance EROFS base has zero-pwrite fallback for ordinary-file failed punching, but private patches are unavailable. Continuity's initial seek fallback handles EINVAL; its later copy-range fallback does not. bbolt database lock/read-map/growth/durability and actual engine/cache/VMM paths remain unobserved. Upstream containerd is comparison only, not the private replacement. Positive symbols/literals cannot establish selected paths, supported cache splitting or effective root disk sizes. No supported admissible layout is selected. Pruned requested 3g+1g upper/lower hypothesis totals 9697333533 logical bytes before other representations, exceeding the original ceiling by 1107398941. Both new ledgers refuse; guest apparent sparse-file enforcement remains independent. Original limits/digests/twenty criteria and all execution/native/freeze denial flags remain unchanged.

Exact fresh checks:

- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: 93 passed in 5.495 seconds, Darwin arm64. No new product test methods or runtime implementation.
- Same empty-environment/network-denied wrapper with `docs/qualification/phase-2c-sbx-storage-readback-v1.py`: passed eleven source/statement bindings, subjects and fork distinction. Optional `--archive` against the fresh digest-verified release passed all eleven member digests, Go identity/build metadata and recorded positive literals/symbols. No extraction/execution by the checker. The previous downloaded data-only copies were removed after verification.
- `rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-sbx-storage-pruned-refused-v1.json` and the same command with `phase-2c-sbx-storage-inventory-v1.json`: each expected exit 2/arithmetic_refused; overflow and unknown counts remain visible.
- Five isolated temporary evidence-copy checks refused execution-flag tampering, changed source bytes, escaping binding paths, substituted private-fork metadata and substituted archive bytes. Each exited 1 with the intended refusal reason and no stdout. Temporary copies were removed. Results and checker digest are in [verification](qualification/phase-2c-sbx-storage-verification-v1.json); these are research checker tests, not containment passes.
- `rtk proxy .venv/bin/ruff check src tests scripts docs/qualification/phase-2c-sbx-storage-readback-v1.py`: passed. `ruff format --check` on the same scope: 37 files already formatted. `rtk proxy .venv/bin/mypy`: passed ten product files. `rtk proxy uv build --offline`: built 0.8.16 sdist/wheel; no fresh installed-wheel execution is claimed.
- All 180 previously tracked qualification files were byte-identical to base HEAD. Final version/link/fence/input/whitespace checks validate 269 unique existing continuation inputs. External research inputs are removed; no VM/host resources were created or modified.

Skills live: Caveman ultra persisted, Jev chose source-first and then blocked-contract conclusions (confidence 1, reported cost 0); neither supplied authority. Codebase-memory Verify startup generation 2026-10-05T16:29:02Z and final relevant-path coverage generation 2026-10-05T16:55:39Z matched metadata/no recorded issues. Budget search/snippet/both-direction trace informed use; the heuristic trace misattributed dict.get to CoordinatorStore.get, so exact source governed. External public research inputs were initially outside the repository index and received exact file/URL/hash checks. Clean coverage is best-effort, not complete engine-source coverage.

Stop at this blocked boundary. Smallest missing capability: exact private-fork/VMM storage contract plus supported admissible layout and independent guest apparent-size enforcement. No paid-host batch is yet runnable; do not request routine access or repeat ENOSPC. [Next initial prompt and 269 exact inputs](PHASE-2C-RESUME-PROMPT.md) preserve the original state and narrowly resume that gap. Standing authorization publishes this checkpoint by commit and current-branch push; no merge/deployment/registry release or Phase 2D.

Publishing includes unchanged upstream MIT/Apache source licenses and EROFS licensing description alongside the archived public files; these are research evidence, not adopted product code. License source URLs/digests are separately recorded.

### Phase 2C release-era storage contract / exact blocked boundary — 2026-10-05

**Blocked, not complete.** Base `9ebcc49f268ce9febe66b6a7a50600acd372f46a`; initially clean `codex/phase1-architecture`, package 0.8.16. Delivery 0.8.17 is the commit containing this entry, resolvable with `git log -1 --format=%H -- docs/HANDOFF.md`. This is research/process maintenance; no product behavior changes. Standing authorization publishes only the current branch checkpoint, not merge/deployment/registry release.

[Contract boundary](PHASE-2C-STORAGE-CONTRACT.md) and its record pin public Docker documentation revision `7211da11e648595ef32f7d0c3d91fb86571b3907`, selected by anonymous API as latest main commit before the pinned release publication. Three complete source hashes, exact line ranges and archived excerpt hashes reproduce fresh public readback without previous temporary state. Chronology is not vendor version-conformance evidence. Documentation resolves ROOT_SIZE as a configuration interface and identifies Linux state/cache/config roots. Per-command Docker size does not change settings-get, so historical settings cannot prove its effective disk. No private engine object map, minimum root size, EROFS route or VMM I/O contract is inferred.

The new smaller-layout screen separately charges hypothetical upper/lower/backing images with an unvalidated 1 GiB root and documented 512 MiB Docker minimum, alongside pruned preparation. Known logical subtotal 5,939,237,149 bytes; remaining 2,650,697,443 is unreserved, not available/complete headroom. Allocation and seven other representation groups remain unknown; expected accounting exit 2/arithmetic_refused. An optimistic root maximum of 1,957,307,638 bytes ignores those unknowns and is only a necessary screening bound. No supported admissible layout is selected; guest sparse apparent-size enforcement remains independent. Seven explicit unanswered contract fields define the smallest continuation. No vendor message was sent.

No bundled executable, installer, daemon, image import, VM access, keys, mounts, credentials, provider/model product call or paid host ran. All original limits/grants/twenty cases, protocol digests, historical evidence and execution/native/freeze denial flags remain unchanged. Existing local VM access was neither assumed nor requested. No paid batch is yet runnable. The optional request for version-matching vendor documentation was unanswered at closure; credentials were not requested. Do not repeat source-only closures or unchanged ENOSPC without new contract evidence.

Skills: Caveman ultra persists. Jev live availability passed; it selected documentation pinning (confidence 1) and advised that evidence does not establish layout (true probability 0.04, confidence 0.92); reported costs zero, advisory only. Codebase-memory Verify project `Volumes-X10Pro-Crewshal` ready; coverage generation `2026-10-05T17:02:32Z`, metadata matched for accounting/research paths, no recorded gaps. Search, exact accounting snippet and both-direction one-hop trace were read with no pagination. The heuristic dict.get edge incorrectly points to CoordinatorStore.get; direct source governs, and that edge is not an asserted dependency. Documentation/text inputs receive exact direct byte checks; no graph completeness claim.

Verification and publishing results follow below. Next milestone still needs exact version-matching contract/layout evidence and independent guest logical enforcement; then a complete peak ledger and supported supervised commands before any necessary matching-platform batch. Feed all [275 exact continuation inputs](PHASE-2C-RESUME-PROMPT.md), including the six new files. Initial prompt: continue Phase 2C from 0.8.17, answer the seven contract fields with version-matching evidence, select a supported admissible layout only after complete independent admission, retain unchanged limits and denied execution; no routine host test or Phase 2D.

Fresh acceptance: `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .` passed **93 tests in 5.466 seconds** on Darwin arm64/CPython 3.12.14. No new test methods or runtime qualification are claimed. `rtk proxy .venv/bin/ruff check src tests scripts docs/qualification/phase-2c-sbx-storage-readback-v1.py` and matching `ruff format --check` passed (37 formatted files); `rtk proxy .venv/bin/mypy` passed ten product source files. `rtk proxy uv build --offline` built the 0.8.17 sdist/wheel; no fresh installed-wheel test or package publication.

The exact offline excerpt command in PHASE-2C-STORAGE-CONTRACT.md passed. Fresh anonymous pinned raw-document reads with 262,144-byte/20-second bounds matched all three complete-source hashes and every archived inclusive range. Four isolated temporary evidence-copy variants (substituted excerpt, escaping path, true execution flag, invented contract answer) each returned exit 1/AssertionError with no stdout; all temporary directories were automatically removed. The previous SBX source/statement checker passed eleven bindings; the new smaller ledger returned expected exit 2/arithmetic_refused with known subtotal 5,939,237,149 and all unknown reasons visible. These verify archived research/refusal only.

Final direct checks passed: synchronized 0.8.17 versions, all 275 unique existing input files, local links/fences in six changed Markdown files, and all **201 previously tracked qualification files byte-identical to base HEAD**. Git diff whitespace passed. No test failed during this session; unresolved runtime/contract fields are unavailable, not failed containment tests. Final graph coverage and staged/publish checks are recorded at closure. No external host resources or public raw research staging directories were created; downloaded documentation was held in memory and only attributed excerpts were saved.

Final graph coverage generation `2026-10-05T17:23:11Z` (recorded 17:25:11Z) reported no recorded issues for all thirteen changed/new paths. README/handoff metadata changed since indexing; the three new text excerpts were not yet tracked by graph metadata. All five received direct source/byte inspection, and no freshness/completeness claim relies on those graph entries. Other paths matched metadata. The subsequently appended handoff remains directly validated. Staged whitespace and final input/version/history/link checks precede the commit; push outcome is reported in the session response after actual remote verification.

### Phase 2C finite exit decision / pending topology review — 2026-10-06

**Phase 2C is not complete. Current SBX pilot investigation is NO-GO under available evidence.** Base `0d36a52e499e4f734e62b64047c015f5d97b761f`, initially clean `codex/phase1-architecture`, package 0.8.17. Delivery 0.8.18 is the commit containing this entry, resolved through `git log -1 --format=%H -- docs/HANDOFF.md`. The owner asked to continue and get past 2C effectively after the explanation of repeated storage research. That authorizes concrete feasibility work, not inventing successful probes or silently removing retained material-topology gates.

[Proposed ADR 0003](decisions/0003-direct-linux-qualification.md) ends further unchanged SBX documentation/import trials for this pilot and presents a direct Linux topology using existing isolation/control tools, explicit native transport versus code-tool authority and only an existing supported external proxy if separation is provable. The proposal removes nested SBX/KVM/private image conversion dependencies; it retains the original entire-native-worker 128 MiB/five-second envelope and all twenty cases. It is an owner-reviewable proposal, not a selected qualified replacement. Material topology approval was requested asynchronously with the concrete file and ADR 0002's owner-review clause; no response had arrived at this checkpoint. No replacement Linux mutation or native startup is authorized by these proposed artifacts. No custom executor/gateway, new model loop or provider call was built.

The exact [read-only local admission batch](PHASE-2C-DIRECT-LINUX-ADMISSION.md) pins a 2061-byte source, SHA-256 `eaf4f37bf1655d9754f1a12421f53673a62558c532ed46fdc0aabebb0b7e936d`, exclusively new copy path, exact Python/timeout invocation, ten-second/65536-byte capture requirements and scoped source cleanup. It reads fixed public kernel interfaces and hashes six system helpers without executing them. No installation, guest boot, credential recovery or paid host is required or authorized. Local Linux access is not assumed. Darwin arm64 has no bwrap/systemd-run in PATH; presence of Docker/Codex/Claude/Fusion paths is inventory, not execution or qualification.

The decision record preserves each original criterion text, grant and limit exactly and maps all twenty to replacement observation scopes. Every replacement result remains unavailable with null evidence; owner approval is null; execution/native/freeze, Phase 2C completion and Phase 2D flags are false. Original protocol SHA-256 remains `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. Product qualification source remains byte-identical. A chronological release/source description cannot resolve caller-specific authenticated authority; the proposal makes broker separation an independent finite GO/NO-GO, with no domain-only substitute.

Actual checks: `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -I -B docs/qualification/phase-2c-direct-linux-admission-v1.py` returned expected **exit 2**, explicit Darwin/Linux-unavailable result and all denial flags. No Linux branch, helper execution, mount/key/cgroup mutation or worker ran. Initial `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2c` passed eleven refusal methods in 0.248 seconds; the fresh empty-environment/network-denied wrapper above with `-m unittest tests.acceptance.test_phase_2c` passed **11 methods in 0.222 seconds**. No new methods or whole-runtime pass is claimed; the prior complete 93-case suite is historical, not rerun for this maintenance proposal.

`rtk proxy .venv/bin/ruff check src tests scripts docs/qualification/phase-2c-direct-linux-admission-v1.py` and corresponding `ruff format --check` passed (37 files). `rtk proxy .venv/bin/mypy` passed ten product source files. `rtk proxy uv build --offline --quiet` exited zero for 0.8.18; artifact metadata is checked directly at publication. No installed-wheel, Linux, broker, native or live-provider check is claimed. First combined integrity check accidentally used system python3 and failed with `ModuleNotFoundError: No module named 'crewshal'`; the same check under .venv passed. That preparation failure remains recorded; it did not alter qualification inputs or become a product bug.

Direct validation passed original case order/text/count, grant/limits, all false gates, pending approval, nine source bindings, synchronized version, Markdown links/fences, **279 unique existing continuation inputs** and all **206 previous tracked qualification files byte-identical to base HEAD**. No private credentials or raw administrative outputs were saved. No external host/VM resource was created or modified.

Skills remain available: Caveman ultra; Jev chose finite feasibility over bypass/repeated research (confidence 1, reported cost zero), then advised the proposed topology does not grant higher limits or retire native tests. Advisory judgments grant no authority. Code-work guided scope and verification. Codebase-memory Verify project ready; relevant-path coverage generation `2026-10-06T06:17:44Z` matched metadata without recorded gaps. Original qualification and new admission source were discovered/read through graph with both-direction one-hop traces and no pagination. New admission trace heuristically misresolved hashlib.sha256/Path to unrelated recorded JSON fields and a caller to product __main__; exact source supplies fallback and those edges are not asserted as real dependencies. No graph completeness claim. Final changed-path coverage/whitespace/publish checks follow.

Next milestone: approve or reject the concrete topology, then run the exact existing-local-Linux admission and prepare one source-bound mechanism fixture under unchanged limits. If approval/access/mechanism or existing broker/native separation is unavailable, name that exact gate and stop; do not reopen SBX research or create another source-only milestone. Feed [current prompt and all 279 inputs](PHASE-2C-RESUME-PROMPT.md). Initial prompt: continue 2C from 0.8.18; resolve proposed ADR 0003's owner decision, then exact local admission and finite mechanism/broker/native GO/NO-GO stages. Full same-profile twenty-case qualification still precedes any 2D/live execution authority. Standing authorization publishes this pending-decision checkpoint without merge/deployment/registry release.

Final changed-path graph coverage generation `2026-10-06T06:19:26Z` (recorded 06:22:15Z) reported no recorded gaps for eleven changed/new paths; handoff and decision-record metadata changed since indexing. Both receive direct source/JSON/binding checks, including this appended handoff. Other paths matched metadata. Clean coverage is best-effort, not complete source/caller evidence. Final staged whitespace, archive-version/input/history/source-binding/link checks precede commit; actual push outcome is reported after remote branch verification.

### Phase 2C direct Linux admission and kernel mechanism — 2026-10-06

Version 0.8.19 records direct owner approval of ADR 0003, reliable owner-authenticated local SSH admission and two fresh final credential-free kernel fixtures. Final v5 service exit zero in 10.810 seconds; fixture times 5.354/5.353 seconds. Independent deleted-open identity, 4 MiB/8 MiB allocated exhaustion, hard 64 KiB lengths, 128/256 inode limits, alias/anonymous-memory exclusions, five-second detached deadline and empty cgroup/mount cleanup are observed. All failed profiles remain separate. Isolated native/proxy version/help discovery v4 passes all eight commands in two fresh services. Earlier observer/interface failures remain separate. Trusted tiny native sandbox compatibility v1 fails before payload under Ubuntu AppArmor net_admin/setpcap denial; no complete native dispatch or proxy mediation test passes. Artifact manifests were transported over SSH stdout above the diagnostic stream ceiling; preserve that limitation and use an existing file-transfer interface in subsequent batches. This mechanism subset cannot be promoted or copied blindly onto a native parent that needs namespace setup. The next capability is native/tool separation and startup under unchanged limits. A concrete fixture-only AppArmor role policy and next tiny-workflow probe are prepared, syntax-checked without kernel loading, and await the directly requested owner host-policy decision; no global restriction was changed. Deliberate pinned fixture preparation is covered by existing authority; the initial acquisition question was too broad and its unanswered preference creates no additional gate. See [concrete prerequisites](PHASE-2C-DIRECT-LINUX-NATIVE-PREREQUISITES.md). Phase 2C, agent execution and Phase 2D remain denied.

Checkpoint verification: Darwin arm64/CPython 3.12.14, network-denied empty-environment `python -m unittest discover -s tests -t .`: **93 tests passed in 3.978 seconds**. Both public direct Linux mechanism/native readbacks pass under the same network denial. Ruff check passes; format check passes for 49 files; mypy passes for ten product source files. `uv build --offline` builds the 0.8.19 sdist/wheel; wheel metadata and embedded version agree. Editable metadata was refreshed from stale 0.5.0 to 0.8.19 offline; no installed-wheel execution is claimed. All 208 previously tracked qualification files and the original ADR 0003 proposal remain byte-identical to base `cefef2e`; original protocol digest/criteria stay unchanged. Approval/profile/freeze/observed bindings, 344 unique exact existing continuation inputs, local links/fences and sensitive-literal checks pass. Privileged SSH exited zero; the native control-master exit request succeeded but the master returned 255, so clean-zero master termination is not claimed. Owned Linux/native data, source/runtime files, aggregate cgroup, mounts and host private transport/vendor preparation were removed; the existing VM remains running. No temporary AppArmor profile was loaded, and the global userns restriction still reads 1. Cleanup proves owned cgroup/mount absence, not exhaustive host PID inventory. No credentials are saved in project inputs. Delivery revision is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Push is required under standing authorization; no merge, deployment or registry release.


Next milestone remains Phase 2C. The smallest current resolver is the pending owner choice on the fixture-only AppArmor role-policy test; it changes an existing host protection policy and has not been assumed from silence. Feed [the complete initial prompt and 344 exact files](PHASE-2C-RESUME-PROMPT.md), especially the native prerequisite assessment, v4 discovery profile/freeze/bindings/observed, native compatibility v1 failure, both proposed AppArmor policies and the unexecuted compatibility v2 source/proposal. Initial prompt: continue 2C from 0.8.19, apply the direct owner policy decision if supplied, run a newly source-bound tiny native workflow under unchanged limits, then prove broker/native boundaries and all twenty same-profile cases twice; no SBX research, new executor, paid provider or Phase 2D. Syntax/help/subset passes do not complete 2C.

Final task-directed graph coverage generation `2026-10-06T11:26:30Z` reports no recorded gaps for nine current native/status evidence paths. Assessment, handoff, plan and README metadata changed and receive direct changed-source/link/binding fallback; the other paths match metadata. This is best-effort coverage, not completeness.

### Phase 2C native setup and scoped policy resolver — 2026-10-07

Base `dd0c15cadc7bc082843585bd38ea902f8257c592`; delivery is the commit containing this entry. Active phase remains 2C. The owner directly approved the fixture-only policy; fresh pinned archives and data preparation were used. Eight bounded trusted tiny-sandbox setup attempts, plus one preparation refusal, preserve exact executed sources, profiles, bindings, freezes and observations. Corrections reach actual native UID mapping under host UID/GID 65534. Kernel audit identifies AppArmor disconnected proc-path denial; chroot-relative policy also fails. No native payload or full mandatory case passes. See [assessment](PHASE-2C-NATIVE-POLICY-ASSESSMENT.md), immutable audit and public policy readback.

The smallest pending resolver is proposal v4: `attach_disconnected` only on the exact trusted native bubblewrap setup role, never payload. Official AppArmor documentation warns about aliasing; the direct owner decision was requested and remains pending. Parser-only verification passes; v4 was not loaded. The original v2 approval is not reopened. Unexecuted v11 prepares from fresh original data and has explicit tiny-file, role, zero-capability, no-new-privileges and denial oracles. It must not depend on earlier generated diagnostic manifests.

Verification: macOS arm64/CPython 3.12.14; `rtk proxy .venv/bin/python -m unittest discover -s tests -v` passes 93 tests in 4.727 seconds. Ruff product/tests and new prospective sources pass; mypy passes for ten product files. Public policy readback passes and records only refusals. Executed source/profile bytes stay immutable; copied prose and one stale admission sample are disclosed separately, so no complete freeze is asserted. Original qualification/API authority and all twenty criteria remain unchanged. All public inputs exclude addresses and authentication.

Owned Linux cleanup passes in 0.086 seconds. Independent post-cleanup readback finds no owned fixture, source artifacts, units, aggregate cgroup/unit or profiles; global restriction stays 1. No exhaustive host PID inventory is claimed. SSH sessions exit zero; existing VM remains running. No paid host, provider, credential-store operation, new VM, package-registry release, merge or Phase 2D. Resume only after the consequential v4 decision, with the exact prompt/files; then tiny workflow and complete qualification. Version/README/changelog/handoff are synchronized before the standing-authorized branch commit/push.

Final checkpoint checks: public policy readback passes after formatting; Ruff check passes and format check covers 24 maintained files (executed diagnostic snapshots are immutable). A focused installed CLI/provenance test passes in 0.216 seconds after version synchronization. `uv build --offline` builds the 0.8.20 wheel/sdist and both embedded/metadata versions match. The first editable refresh with `--no-build-isolation` failed because setuptools is not installed in the development environment; `uv pip install --offline --no-deps -e .` succeeds using the declared cached build isolation. No dependency/schema change or installed-wheel execution is claimed. All 261 qualification files already tracked at base `dd0c15c`, ADR 0003 and the product qualification module remain byte-identical. The continuation has 402 unique existing inputs; links/fences and host-owned private vendor/transport cleanup pass. Task-directed graph generation `2026-10-07T09:26:21Z` records no gaps for eight current paths, with matching metadata; this is best-effort evidence, not completeness. Later documentation edits were checked directly. Commit/push follows standing authorization; delivery revision resolves with `git log -1 --format=%H -- docs/HANDOFF.md`.

### Phase 2C / native complete-profile continuation — 2026-10-08, unpublished

Preserved all historical evidence, including native/proxy subset passes and failed/prepared variants. Fresh full v3 preparation and freeze passed; its first actual native workload failed buffered ENOSPC handling, and both provider requests included a synthetic instruction marker. Full v4 correction was freshly prepared and frozen; no workload ran. Exact public inputs and hashes are in [the next-session record](PHASE-2C-NEXT-SESSION-2026-10-08.md). Original protocol, grant and limits remain unchanged; all execution flags stay false. This is an incomplete boundary, not a completed milestone.

Focused offline acceptance: 11 tests passed in 0.206 seconds; Ruff passed new sources. The full 93-test suite was not rerun. Scoped guest cleanup verified no active v3/v4 units, owned mounts/loops or populated owned cgroups and removed only this session's new fixture/copy/upload paths. Existing diagnostics and v7 policy were retained, the VM remains running and SSH closed. No paid host/provider/model, new VM, credentials in Git, commit, push or release. Resume 2C only; publish after independently verified completion under the owner's latest explicit gate.

### Phase 2C / resumed v4/v5 failures, owner test stop and portable audit — 2026-10-08, unpublished

Sole milestone: 2C. Base `21e3686` on `codex/phase1-architecture`, package 0.8.20. Original dirty files and every historical executed/prepared diagnostic remained intact. Initial exact-input loading read/parsed 580 files (17588919 bytes); baseline hashes covered 595 files. This is byte/parse continuity, not independent runtime qualification. Preserve prior tiny native v8 and proxy v3/v6 two-run passes and all failures; no complementary subset counts as completion.

Before the later owner stop instruction, the authorized existing VMware Ubuntu aarch64 guest was accessed using directly owner-supplied prior authentication outside Git. No credential-store search, paid host/provider/model or new VM. Kernel `7.0.0-38-generic`, fixture AppArmor v7 and unchanged aggregate controls were read back. Pinned native/proxy archives were freshly hash-checked and each profile rebuilt from originals. Private transport material and addresses are excluded from public inputs. Jev skill was read but no paid/live model call was made under the existing boundary.

Fresh v4 preparation succeeded (service 6.348 s), reproduced manifest `71bc6e55de5d628a757cb3b593d12da10da22864e395dfb0c92ea3c370220bfc`, and actual freeze/stale-manifest refusal passed. Its first workload failed `RuntimeError: untrusted instructions inherited into native provider request` in 1.837 s (driver 3.188 s). Both provider requests contained the synthetic global instruction marker; repository marker was excluded. Unbuffered payload exited zero; deleted-open candidate was independently observed at 1048576 logical / 1056768 allocated bytes, one link-zero FD. Candidate sampled peak logical 5795919 / allocated 11177984; scratch 25700776 / 26562560. These sampled observations do not close every storage case. Fixture cleanup reports four unmounts, two loop detachments, empty anonymous keyring and absent fixture-owned files. Prepared root and copied helpers/upload were not removed. New v4 binding/freeze/failed observation files are available locally in the active input list.

New v5 source/profile and payload v4/boundary v2/freeze v3 were finalized and formatted before preparation, then frozen immutable. Added readonly empty masks for global instruction files, parent/child read-write-unlink oracles preserving hostile backing bytes, and readable root permission for the separate validator UID. Fresh preparation succeeded (4.667 s); console reported manifest `7b2eb308ba050369413cec4bd64daccca99cdcd23aa5710c8d6d6a2f75d25cc0` and freeze/stale-manifest refusal. First fixture console reported `tiny_workflow_passed=true` then `BoundaryFailure: boundary cgroup limits differ from frozen limits`, 1.979 s (driver 3.371 s). Driver exited zero because errors are recorded, not because qualification passed. Validator controls/raw details remain unavailable; cause is unresolved. No second run. See the explicitly [console-only incomplete record](qualification/phase-2c-direct-linux-native-full-v5-console-incomplete.json); it is not an observed qualification record or independently verified freeze.

Guest operations used new units under the inherited aggregate slice with memory 805306368, swap zero, CPU 100%, tasks 128, runtime 120 s, stop timeout 1 s, control-group kill, private network/mount namespaces and anonymous key session. Worker/validator controls stayed 134217728 bytes, zero swap, one CPU, 32 tasks, five seconds. Exact helper prepare/freeze/run argv and sources are preserved in the profile/source set. Initial sudo transport could not forward stdin and was stopped; subsequent direct PTY worked. v5 artifact copy then lost SSH responsiveness: scp exit 255, broken pipe; SSH exit 255, operation timeout/broken pipe. Complete v5 manifest, freeze and observation were not transferred. Do not fabricate their files.

The owner then instructed: “totally stop VMware's and linux's tests. continue development for all platform including Linux but you should not test the linux part like you did before.” Linux/VMware activity stopped and the failing SSH session was terminated. No subsequent guest connection, inventory, test or cleanup occurred. Final v5 cleanup is **unknown**; `/var/tmp/crewshal-native-qualification-v4`, `/var/tmp/crewshal-native-qualification-v5`, new `/run` helper copies and `/tmp/crewshal-full-resume-20261008` may remain. VM current status is unknown; no VM stop/delete action was requested or performed. Earlier scoped cleanup does not establish these final artifacts absent.

Subsequent authorized development: [portable bundle audit](PHASE-2C-OFFLINE-AUDIT.md), read-only source/helper and 21 fresh synthetic fixture methods. It independently applies the unchanged assessor to two complete records, exact original protocol/grant/limits/cases, one profile/current identity and all source bindings. Refuses complementary subsets, duplicate IDs/bytes, changed/missing/null/conflicting inputs, boolean substitutions, malformed/duplicate JSON, path aliases/escapes/symlinks, forged flags and byte overflows. Does not run any source, certify record authenticity or attest runtime containment. `runtime_verified` and `execution_allowed` always false. Source development is portable in intent; actual Linux/Windows behavior remains untested.

Final local checks on macOS 27.2 arm64 / CPython 3.12.15, existing pinned dependencies:

```sh
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/mypy
```

Full suite **114 tests passed in 4.531 s** under empty inherited environment and OS-level network denial. Ruff lint and strict mypy passed (11 source files). Initial 15-method bundle suite/full 108 tests passed; expanded 18 methods passed; final binding review exposed null digests, conflicting bindings and Python boolean/numeric equality, corrected with fresh regression cases before final 114-test run. Existing qualification assessor and runtime execution flags were not changed. Graph Verify coverage generation `2026-10-08T08:53:38Z` reported no recorded issues for audit, assessor, script and tests; direct source was read, and graph cleanliness is not completeness proof.

Current milestone remains **incomplete and blocked for runtime qualification**. User stopped Linux testing; offline checks do not replace two complete independently verified original twenty-case runs on one fresh profile. No version bump, commit, push, deployment, package release or Phase 2D. At this boundary use [the current offline continuation prompt](PHASE-2C-OFFLINE-CONTINUATION-2026-10-08.md) and every exact file in the updated [active input list](PHASE-2C-ACTIVE-CONTINUATION.md). Continue concrete portable 2C source work and local macOS offline checks only; preserve all unknowns and failed/prepared source bytes.

Final preservation/documentation checks: 590 of 595 baseline files remained byte-identical; only README, changelog, handoff, development plan and active continuation were intentionally edited. Every historical diagnostic source/profile/evidence file is unchanged. v5 profile SHA-256 remains `2f6b4198901820cf69ccef4eaae1ce192561cb5ef4a05a50885156cbb91d7a41`; all nine referenced source/policy bindings match. Original protocol and both package version declarations remain unchanged. Seven current Markdown files passed local-link/fence/whitespace checks; Git diff whitespace passed. Ruff format check passed (25 files). Audit CLI missing-directory smoke check returned expected exit 2 with denied status, false runtime verification and false execution permission. v4 failed observation resume1 SHA-256: `8440e595c8085585798e0740db9358787f3ba95637569c14617ff1a4830b7dbd`; explicitly incomplete v5 console record: `2c858d2bd4597e8d934d0570f644c27994398f9a0d12fba66407eb10c4a988ff`. These hashes are continuity references, not complete qualification evidence.

### Phase 2C / portable audit path and JSON corrections — 2026-10-08, unpublished

Sole milestone: 2C. Published base remains `21e368654c20c2e7dfbbb94c06f1ec04b0d0985a` on `codex/phase1-architecture`; package remains 0.8.20. The owner stop/publication restrictions remain controlling. No VMware connection, inventory, cleanup, start/stop, Linux test, Docker/VPS substitution, provider/model call or credential-store operation occurred. Runtime qualification remains blocked, not completed.

Loaded/read and syntactically parsed 594 exact public inputs (18124899 bytes), including the backtick paths in the published input set and Markdown-linked working additions. This is byte/parse continuity, not independent verification of their runtime claims. Saved a local non-Git SHA-256 baseline for 609 tracked/nonignored working files before edits. All 526 historical qualification/source files remain byte-identical. Original dirty work is retained. Only the portable audit, its fresh tests and continuity documents changed; one new next-session prompt was added. Original protocol hash and assessor/model contracts remain unchanged. The immutable v5 profile still hashes to `2f6b4198901820cf69ccef4eaae1ce192561cb5ef4a05a50885156cbb91d7a41`; all nine source/policy bindings match. No missing v5 raw records were manufactured and final guest cleanup remains unknown.

Fresh public-API regressions reproduced seven incorrect acceptances: three policy aliases normalized before validation, directory case aliases, and NaN/positive/negative Infinity. The same four-method run preserved valid nested profile/policy acceptance. The correction validates policy paths before resolution, checks all declared directory prefixes for case aliases, and refuses nonfinite JSON constants and floating-point exponent overflow. Five added fixture methods exercise refusal and valid finite/literal-string/nested controls. No runtime launcher, gateway, adapter, model/tool loop or execution authority was added. Both audit authority flags remain false; unchanged original assessor still checks each complete twenty-case record independently.

Local environment: macOS 27.2 arm64 / CPython 3.12.15, existing pinned development dependencies. Commands and outcomes:

```sh
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .
rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest tests.acceptance.test_phase_2c_bundle
rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py
rtk proxy .venv/bin/mypy
rtk proxy git diff --check
```

Full suite: **119 tests passed in 5.394 seconds**, exit zero, under empty inherited environment and OS-level network denial. Initial mypy then failed because a new loop reused the later source-binding variable name; renamed that local variable only. Final focused suite passed **26 tests in 0.196 seconds**, and strict mypy passed all 11 source files. Lint and formatting checks passed; 25 maintained files. No installed-wheel/build or Linux/Windows runtime compatibility claim. Synthetic fixtures are not a fresh real complete runtime profile or two qualifying executions; all original limits remain requirements.

Graph Verify project `Volumes-X10Pro-Crewshal` was ready at session start. Initial relevant-path coverage generation `2026-10-08T09:00:04Z` matched metadata without recorded issues for audit, assessor, model, entry point and tests; graph search/snippet and both-direction one-hop trace had no pagination. The trace heuristically attributed local `require` to an unrelated historical JSON field and `dict.get` to CoordinatorStore; direct source supplied fallback, and those are not asserted dependencies. Final changed-path coverage request failed with `Transport closed`; no refreshed generation or clean final graph claim. Changed source and documents received direct read/parse/path/hash checks instead. Graph coverage is best effort, never proof of completeness. Caveman and codebase-memory instructions applied; Jev instructions read with no paid call. Code-work guided the bounded regression/fix sequence.

Incomplete boundary: no version bump, commit, push, merge, deployment, registry publication or Phase 2D. Next milestone remains 2C source continuation under the existing test stop. The unresolved completion gate still needs two independently verified complete original twenty-case runs on one fresh unchanged profile; offline consistency cannot supply that evidence. No new guest action is requested or authorized. Feed [the updated initial prompt and exact files](PHASE-2C-OFFLINE-NEXT-SESSION-2026-10-08.md), [the active complete input list](PHASE-2C-ACTIVE-CONTINUATION.md), handoff, plan, accepted architecture/ADR 0003, audit guide, README/changelog/AGENTS and unchanged assessor/model before selecting further concrete portable source work. Stop at the 2C boundary and retain the publication gate.


### Phase 2C complete native/proxy profile and portable audit — 2026-10-08

**Complete on the observed direct Linux aarch64 profile; execution permission remains false.** Base `21e368654c20c2e7dfbbb94c06f1ec04b0d0985a`, branch `codex/phase1-architecture`, version **0.9.0**. Delivery is the commit containing this entry; resolve with `git log -1 --format=%H -- docs/HANDOFF.md`. Stop at 2C after the standing branch-publishing ceremony. No 2D code or live model evaluation is included.

The owner explicitly superseded the earlier test stop with “Reconnect and resume 2C checks,” and restricted the run to the existing local VMware Ubuntu installation. SSH/sudo succeeded; no droplet, paid model/provider, credential-store access or credentials in public evidence. Read [the full assessment](PHASE-2C-COMPLETION-ASSESSMENT.md) and [all exact input additions](PHASE-2C-ACTIVE-CONTINUATION.md).

Two independently complete fresh v18 runs, one frozen profile/configuration, pass all twenty unchanged original cases. Native exec_command performs direct denied-boundary probes and opens a real PTY; native write_stdin uses its actual returned handle for the complete hostile workload. Actual native command completion and the independent four-byte artifact are observed. Worker times 2.481/2.245 seconds; readonly validator 0.122/0.144 seconds; cancellation 0.230/0.271 seconds; five-second actual deadline plus original one-second stop grace terminates within 5.098/5.050 seconds. Source/root/toolchain/config/grant/policy/protocol bindings, controls, logical/allocated/deleted-open storage, actor/descendant authority, synthetic proxy mediation, hook positive/negative controls, global instructions, tool catalog and terminal cleanup are checked independently. Both native file tools are actually exercised. Reader v3 was frozen before execution; each readback run independently creates 56 denied assessor decisions and three malformed-record refusals. Trusted per-run records are qualified_for_later_authorization with false execution permission. Portable audit/runtime-verification flags stay false.

Preserved v3/v4/v5 and every later failed/prepared source/record. v5 recovery yielded actual surviving binding bytes and an empty observation file; original cause/raw freeze/final cleanup remain unknown. v6 primary failure was masked by cleanup; v7 prepared only; v8 timed out; v9/v11/v13 harness passes did not resolve complete evidence; v10 hook control failed; v12 captured empty setup defaults; v14 final review found actual write_stdin missing; v15 actual file-tool/tiny pass later failed ENODEV at deadline with exact object/cause unknown. v16/v17 invocation omissions respectively lacked private keyring/network wrappers and refused before native startup; both are preserved. v18 binds the complete supervisor argv explicitly. Observer v6 exceptions require independently dead/removed processes or absent/empty cgroups, and neither successful run needed that exception. No claim resolves v5/v15 unknown causes.

Current outside-driver cleanup finds empty owned services/cgroups, no owned loops/mounts and absent v8–v18 fixture roots. Sixty exact source/configuration files were preserved outside `/run`; all prepared roots and failed v6 files retained; exact owned roles/helpers/slice removed. Global user namespace protection stays 1, SSH disconnected, VM left running. [Current final cleanup](qualification/phase-2c-local-v18-cleanup-complete-20261008.json) does not claim historical v5 cleanup. [Original byte-preservation ledger](qualification/phase-2c-original-byte-preservation-20261008.json) checks 609 baseline files, with 599 byte-identical and ten explicit maintained document/audit/test/version exceptions; every historical executed full-profile source digest still matches.

Final verification on macOS 27.2 arm64, CPython 3.12.15:

- `rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py` plus all new native/readback/observer sources: passed. `ruff format --check` on the maintained scope and new sources: 39 files already formatted. Strict `rtk proxy .venv/bin/mypy`: passed, 11 source files. Prepared/executed historical source bytes were never reformatted.
- `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .`: **141 passed in 4.861 seconds** after the synchronized 0.9.0 version update. The earlier 114/119/137/141 results remain historical checkpoints.
- `rtk proxy uv build --offline --quiet`: passed. `rtk proxy uv pip install --offline --no-deps --python .venv/bin/python -e .`: synchronized editable metadata to 0.9.0; cross-filesystem clone warning fell back to copies.
- Fresh `/private/tmp/crewshal-2c-final-wheel-20261008`: `rtk proxy uv venv --python .venv/bin/python /private/tmp/crewshal-2c-final-wheel-20261008`; offline hash-locked development dependencies; offline 0.9.0 wheel installation. Installed package import resolves exclusively to this external site-packages; runtime/metadata versions both 0.9.0. Installed CLI help passes with network denied. Complete **141 tests pass in 8.055 seconds** through this installed interpreter under empty environment and OS network denial. Tests create fresh fixtures; qualification helper sources are the pinned repository files, and product modules are installed wheel bytes.
- The public-record reader command in the assessment reruns after the version update: all_twenty_twice_observed=true; runtime_verified=false, execution_allowed=false. All original full-profile source digests/protocol bytes match; no subset assembly or missing-record fabrication.
- Codebase-memory Verify initially provided targeted current-generation snippets/traces/coverage. Later MCP transport closed; final index_status/check_index_coverage failed with Transport closed, so current source claims use exact file fallback. No exhaustive graph coverage claimed. Caveman and RTK remained active; Jev made no paid call.

Publication uses the standing owner authorization only after this gate. Git credential helpers/askpass are disabled for the push because credential-store access remains forbidden. Any authentication failure must be reported explicitly; do not recover credentials or force-push. No merge, deployment or registry release. Next session: [2D prompt and exact files](PHASE-2D-NEXT-SESSION-2026-10-08.md), plus every preserved input in the active index. Windows/macOS runtime compatibility stays unknown.


## Session ledger — 2026-10-08, Phase 2D incomplete offline boundary

- **Milestone and revision:** 2D only; base/current HEAD `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, package **0.9.0**. Initial working tree clean. Working changes stay uncommitted/unpublished because the user requires the complete 2D gate before the version/README/changelog/handoff/commit/push ceremony. No delivery commit is claimed.
- **Changes:** new `src/crewshal/runtime.py`, `src/crewshal/candidate.py` and `tests/acceptance/test_phase_2d.py`; maintained README/changelog/development/plan/handoff status; new offline contract, execution preparation, current prompt and continuity ledger. No original source, profile, binding, freeze, observation, protocol, dependency lock, database schema or package version changed. The original 749 tracked-file baseline and 359 loaded linked-input hashes are recorded in the new continuity ledger. Historical 2C qualification remains complete only for exact v18 Linux aarch64; no identity transfer.
- **Offline acceptance:** 26 independently created 2D methods test malformed/unknown/duplicate/nonfinite/incomplete event refusal; missing/stale runtime/config/provider/model identities; exit/terminal agreement; cancellation, five-second deadline, quota/refusal, interruption and stream bounds; cumulative reported usage with unknown cost; inert preparation with false permission; original dirty/Git preservation; path/hardlink/symlink/special-file/mode/size refusal; candidate mutation; exact validator command/authority; scope and private SQLite capture/verdict integrity. Native command events and prose become claims only. A synthetic verified verdict still grants no execution. No fixture needs previous artifacts or a live service.
- **Focused command:** `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d` — **26 passed in 0.053s**, exit 0. Initial expected import failure proved the new seam absent. Development fixture failures exposed case-insensitive alias assumptions, lack of a store context manager and the existing required validating transition; corrected fixtures then passed. Atime-only read changes have a separate regression. No live failure was relabelled.
- **Final editable complete suite:** `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .` — **167 passed in 5.164s**, exit 0. Earlier 165-test run passed in 5.068s; two additional focused regressions and the final package rebuild supersede it.
- **Final static commands:** `rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py`; `rtk proxy .venv/bin/ruff format --check src tests scripts/audit_phase_2c_bundle.py`; `rtk proxy .venv/bin/mypy` — all exit 0, **34 files formatted / 13 source files typed**. Historical executed scripts remain untouched and are not reformatted.
- **Build/install:** `rtk proxy uv build --offline --out-dir <fresh-external-directory>/final-dist` built wheel/sdist; `rtk proxy uv venv --python python3.12 <fresh-external-directory>/fresh`; `rtk proxy uv pip install --python <fresh-external-directory>/fresh/bin/python --offline --require-hashes -r requirements-dev.lock`; `rtk proxy uv pip install --python <fresh-external-directory>/fresh/bin/python --offline --no-deps --reinstall <fresh-external-directory>/final-dist/crewshal-0.9.0-py3-none-any.whl` — all exit 0. Draft metadata retains 0.9.0, not a release. The initial and final build directories are separate; no historical wheel is overwritten.
- **Final installed-wheel suite:** `rtk proxy env -i PATH=/usr/bin:/bin HOME=<fresh-external-directory>/home PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' <fresh-external-directory>/fresh/bin/python -m unittest discover -s tests -t .` — **167 passed in 5.592s**, exit 0. Import inspection resolved package/runtime/candidate to external `site-packages`, not editable `src`; installed CLI help succeeds and still offers only `init`, `show`, `validate`. The preceding installed 165-test result (8.146s) predates the atime correction and final rebuild; it is not the final source evidence. Exact reusable commands are in PHASE-2D-OFFLINE-CONTRACTS.md.
- **Environment:** macOS 27.2 build `26B5101f`, arm64, CPython 3.12.15, Pydantic 2.12.5, uv 0.9.24, Ruff 0.14.1, mypy 1.18.2, hash-locked dependencies. Empty inherited environment and denied network cover test execution. No Linux/Windows test or macOS runtime qualification is claimed.
- **Discovery/skills:** codebase-memory Verify confirmed project/generation, relevant snippets/traces and path coverage. Initial generation `2026-10-08T09:40:18Z`; updated coverage `2026-10-08T12:55:33Z` matched candidate/tests but flagged subsequently edited runtime metadata. Direct source fallback covers that edit and a misresolved graph `digest` edge. Final generation `2026-10-08T13:03:36Z` reports matching metadata/no recorded gap for all three new source/test paths; no exhaustive completeness claim. Caveman chat, RTK shell and the code-work skill were applied. Jev was read but no paid Jev/provider/model call was requested.
- **Unrun/unknown:** product supervision/dispatch and recorded execution authority are absent. No production process, live provider/model, SSH/VM operation, broker credential, hosted test, merge, deployment, release or 2E/evaluation ran. Qualification fixtures are not product launchers. Existing guest roles/helpers/slice were removed; no transient setup was assumed. A changed effective profile/upstream/source needs fresh qualification. Original v5 raw cause/final cleanup and Windows/macOS runtime compatibility remain unknown. Offline manifests/copies are not kernel containment or live storage enforcement.
- **Smallest next input and scope:** choose exact live provider/model and approved egress/credential treatment plus provider-enforced financial ceiling or explicitly acceptable non-hard billing/quota exposure. Then prepare a fully source-bound one-attempt batch through the accepted native boundary for recorded owner execution/spend approval; preserve the five-second/128 MiB and all original ceilings. Complete production integration and actual candidate/check/refusal evidence within **2D**, then perform the standing completion-only publishing ceremony and stop. Until those gates pass, resume [the exact current 2D prompt](PHASE-2D-CONTINUATION-2026-10-08.md), not 2E. Required files are listed there, including every prior 2C exact input.


## Session ledger — 2026-10-08, Phase 2D preparation-only resumption

- **Authority and outcome:** resumed 2D only on current/base HEAD `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, package 0.9.0. The owner answered “Sol6.1 / approved”, then “Batch preparation only.” Record that later clarification as controlling scope, not a runtime or spend gate. No native process/model/provider request, credential-store operation, SSH/VM test, commit/push, 2E or evaluation occurred.
- **Concrete work:** `runtime_batch.py` and `scripts/prepare_phase_2d_batch.py` create a new private external bundle of exact synthetic README/original-marker/metadata/candidate bytes, neutral task, initial manifest, standalone byte-check source, unchanged limits and non-launchable native/validator template. No 2C driver code is imported/wrapped/executed. Eleven artifact bodies/digests and eight unchanged historical references are preserved in `phase-2d-batch-preparation-v1-20261008.json`; its SHA-256 is `b08afc86a6146acce8c4947874b833f699d65495eac7bc3c7f2ebe4ed1ae6bd1`. Namespace/role/helper/provider/credential/financial/qualification/execution/spend fields remain explicitly unresolved. The original 749 tracked-file baseline changed only the five maintained documents; all original 2C bytes and earlier 2D runtime/candidate/test source hashes remain unchanged.
- **Focused checks:** `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_batch` — **7 passed in 0.352s**, exit 0. Fresh fixtures demonstrate reference/output refusal, byte continuity/private modes, declared Python nonexecution, inert utility output and original/false/missing README rejection plus exact expected-byte acceptance by the standalone CPython check. This is a local synthetic helper smoke, not a Linux validator/native runtime test. Mypy initially refused the Literal URL default; it was corrected and strict typing passed. Generated artifact bytes did not change.
- **Final editable suite:** `rtk proxy env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Volumes/X10Pro/Crewshal/.venv/bin/python -m unittest discover -s tests -t .` — **174 passed in 5.194s**, exit 0.
- **Static/build:** `rtk proxy .venv/bin/ruff check src tests scripts/audit_phase_2c_bundle.py scripts/prepare_phase_2d_batch.py`; matching `ruff format --check`; `rtk proxy .venv/bin/mypy` — all exit 0, **37 formatted files / 14 typed source files**. `rtk proxy uv build --offline --out-dir <fresh-external-preparation-directory>/dist` builds draft 0.9.0 wheel/sdist. Fresh external uv environment, offline hash-locked dependency installation and offline `--no-deps` wheel installation all pass. No historical dist artifact or source/profile is overwritten.
- **Installed wheel:** run the complete suite with the new external interpreter under `env -i`, temporary HOME and the same denied-network sandbox — **174 passed in 8.789s**, exit 0. Import inspection resolves `runtime_batch.py` to external site-packages, with bytes matching current source. Installed CLI help passes; passive `init/show/validate` interface remains unchanged. Wheel/source/artifact hashes and checks are in `phase-2d-batch-preparation-verification-v1-20261008.json`. Environment remains macOS 27.2 arm64/CPython 3.12.15 with the existing hash lock. No target runtime portability is inferred.
- **Evidence/skills:** reloaded 359 historical linked inputs as data. Codebase-memory Verify confirmed the nearest project; original relevant source coverage matched generation `2026-10-08T13:06:50Z`, new preparation paths matched `2026-10-08T13:15:30Z`. No exhaustive graph claim. Exact source inspection supports behavior. RTK/Caveman/code-work continue; OpenAI Docs verified current model ID from the actually opened official HTML page after a Markdown fetch error. Auth docs were comparison data only. No paid Jev/model call or credential action was requested.
- **Boundary and next prompt:** the preparation-only request is handled; the **2D milestone remains incomplete**. Do not re-ask the selected model or preparation-only scope. Resolve pinned native/account availability, owner-selected provider/egress/credential/billing exposure, source-bound production supervision and fresh exact profile qualification before requesting/using a separate live execution/spend gate. Preserve original limits and historical unknowns. Feed [current continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md), [preparation guide](PHASE-2D-BATCH-PREPARATION.md), both new preparation records, generator/utility/tests and every earlier required input. Version/commit/push ceremony awaits full 2D completion; 2E stays closed.


## Session ledger — 2026-10-08 Phase 2D project/session preparation boundary

- **Milestone/outcome:** 2D remains incomplete; the newly requested preparation selection is implemented. The owner answered “just do the preparation with ability to select on each project/session”. No global provider/route/billing/credential choice is required now. Those choices belong to each relevant later project/session. This answer supplied no live execution or spending authority.
- **Revision/environment:** base `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, current branch `codex/phase1-architecture`, version 0.9.0. No delivery commit/push. Observed macOS 27.2 build `26B5101f`, arm64, CPython 3.12.15, pinned Pydantic 2.12.5, Ruff 0.14.1 and mypy 1.18.2. Offline cached build/install uses requirements-dev.lock; this is source/package verification, not macOS/Linux native runtime qualification.
- **Changes:** `PreparationSelection` and optional utility `--selection FILE` bind one explicit project/session/model with optional requested provider/destination/billing/credential labels. Explicit selections have no ambient or previous-bundle inheritance. Legacy Sol6.1 preparation remains readable. `audit_runtime_batch` reads data against a separately retained coordinator expectation and exact selection; different contexts, changed declarations/artifacts/references, extra/missing entries, symlinks/hardlinks and candidate mode/content changes refuse. All authority/qualification flags stay false. Runtime adapter count, CLI execution surface, original limits and historical qualification records remain unchanged.
- **Fresh checks:** `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_selection tests.acceptance.test_phase_2d_batch` passes **14 tests in 0.640s**. Complete editable suite under `env -i` and macOS `sandbox-exec` denying network passes **181 in 5.669s**; a new external installed-wheel environment passes **181 in 5.097s** under the same denial/empty-environment conditions. This comprises 40 current 2D methods and 141 earlier methods. Installed `runtime_batch.py` bytes exactly match working source, imports resolve to external site-packages and `crewshal --help` exposes only passive init/show/validate. Offline build/hash-locked dependency installation succeeds. Ruff check/format passes (38 files); strict mypy passes (14 source files); `git diff --check` passes. Tests create their own fixtures and do not rely on the stored example or previous paid/live artifacts.
- **Evidence:** [selection/schema/reproduction guide](PHASE-2D-SESSION-SELECTION.md), [eleven-artifact/eight-reference bound example and successful offline readback](qualification/phase-2d-session-selection-v1-20261008.json), [verification, exact commands, source hashes, failed checks and continuity](qualification/phase-2d-session-selection-verification-v1-20261008.json). Bound example SHA-256: `ade780071f57be32759a0c38ef518faf1119a065b6a5f219854d9b261d166a6a`. Preparation labels are explicit descriptive context labels, not authenticated Git/thread identities. Live fields remain unresolved.
- **Failures/coverage:** initial test import failed because `PreparationSelection` did not yet exist. Initial mypy rejected a widened model-source constant; its explicit Literal annotation fixed the failure. A documentation patch context mismatch was corrected with exact bounded replacement; no historical source was executed. Codebase-memory Verify covered relevant paths at initial generation `2026-10-08T13:22:57Z` and final matching generation `2026-10-08T13:37:41Z`; signals are best-effort. Misresolved JSON/builtin graph edges were replaced with exact source inspection, and overly broad discovery was narrowed to fully paginated exact-file queries. No completeness claim is made.
- **Continuity:** 359 historical linked inputs loaded as data (17878511 current bytes); only the five already-maintained status documents differ from their earlier recorded fingerprints at session start. Initial baseline contains 763 files. This session intentionally changes nine existing paths; every other initial file remains identical, including all 528 paths with phase-2c/phase_2c names and all other original historical artifacts. Previous 2D runtime/candidate/tests and v1 preparation/verification/continuity records remain byte-identical. Uncommitted work stays preserved. The execution-gate prose now matches the existing bound four-argument validator template; executable identity remains pending.
- **Unresolved/not run:** no product launcher/production authority integration, new exact production qualification, native/provider/model/Jev call, credential-store access, VMware/SSH operation or approved live implementation/readonly validator acceptance. No version bump, commit/push, 2E or evaluation. Readback proves data/context consistency, not authenticity, live containment or financial enforcement. Stable trusted directories are assumed; hostile same-user/directory replacement races remain outside this offline claim. Windows/macOS native compatibility and original lost v5 cause/final cleanup remain unknown.
- **Next milestone/prompt:** continue **2D**, not 2E. Feed HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2D-SESSION-SELECTION.md, PHASE-2D-CONTINUATION-2026-10-08.md and all exact source/evidence/architecture inputs listed there. Initial prompt: “Resume 2D from the project/session preparation boundary. Preserve explicit per-session choices and preparation-only scope; do not infer live authority from selection/readback or require a global route. Complete only authorized preparation/production integration, prospectively bind and qualify any changed profile, and obtain a separate exact execution/spend gate before live startup. Preserve original limits, dirty work and historical bytes; record fresh evidence, update handoff and stop at the boundary.”


## Session ledger — 2026-10-08 Phase 2D production collection/revision integration

- **Revision/outcome:** base/delivery revision remains `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, version 0.9.0, uncommitted. [Coordinator integration](PHASE-2D-PRODUCTION-CAPTURE.md) adds a private collection receipt and one transactional terminal/freeze/scope/claim/usage operation. It preserves launch history, binds changed frozen bytes, leaves earlier approvals stale and requires actual manifest/capture readback at verdict. SQL rollback preserves database state; owned filesystem residues remain for inspection. Preparation-only project/session choices and all original limits remain intact.
- **Acceptance:** 18 independent new methods; 58 total Phase 2D / 199 complete offline methods. Focused unittest, complete editable/installed-wheel discovery under `env -i` and macOS network denial, Ruff lint/format, strict mypy, offline sdist/wheel build, fresh external hash-locked offline installation, external site-packages inspection and installed CLI help pass. Environment: macOS 27.2 (`26B5101f`) arm64 / CPython 3.12.15. [Verification/continuity](qualification/phase-2d-production-capture-verification-v1-20261008.json) records exact commands, results, hashes and preserved bytes. Initial missing-module and typing failures, state-directory review correction and documentation patch context failure remain explicit offline development history.
- **Evidence/continuity:** 365 linked inputs read as data, totaling 17938358 bytes; only five maintained documents differed from the earlier input ledger. The initial working tree had 766 fingerprinted files and unpublished 2D work. Current changes intentionally extend durable.py and maintained documents; new integration/test/guide/verification files are added. All other initial bytes, historical 2C artifacts and earlier preparation source/tests/records are preserved. Graph Verify uses the matching final generation documented in the verification artifact, with direct source replacing one misresolved historical digest edge. RTK wraps commands. Caveman governs chat only; no paid Jev or delegated agent operation occurred.
- **Incomplete/not run:** production Linux supervisor/launcher, exact changed-profile qualification and separately authorized actual implementation/credential-free check. No live native/provider/model/Jev, credentials, VMware/SSH, paid host, version bump, commit/push or 2E. No source-only result supplies runtime qualification or authorization. Original lost v5 cause/final cleanup and Windows/macOS native support remain unknown.
- **Next milestone/prompt:** continue 2D only using [updated initial prompt and exact files](PHASE-2D-CONTINUATION-2026-10-08.md), production-capture guide/source/durable state/fresh tests/verification plus all prior architecture and historical inputs. Build bounded accepted native/proxy dispatch source, then bind and independently qualify the exact profile and obtain the concrete project/session execution/spend gate before startup. No global route answer is required. Publication remains gated on complete offline and approved live 2D acceptance.


## Session ledger — 2026-10-08 Phase 2D source-bound dispatch preparation

- **Milestone/outcome:** 2D remains incomplete. Only the bounded native/proxy dispatch-preparation join is implemented and independently verified offline. Source compiles explicit CLI settings and separate task stdin; it connects audited per-project/session preparation to exact task/check/launch/source configuration and the existing qualification/request refusal seam. It creates no envelope, process, supervisor observation, authenticated authority, live account access or approval. Per-session choices and preparation-only scope remain controlling.
- **Revision/environment:** base/delivery revision remains `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, version 0.9.0, uncommitted. Observed macOS 27.2 (`26B5101f`) arm64, CPython 3.12.15, Pydantic 2.12.5, Ruff 0.14.1 and mypy 1.18.2 with the existing hash lock. No Linux/Windows/macOS runtime support is inferred from these package tests.
- **Changes/trust:** [dispatch source/guide](PHASE-2D-DISPATCH-PREPARATION.md) binds eleven current coordinator source files, exact batch/context/task/check/launch binding, literal pinned Codex/proxy argv, intended replacement environment, validator argv and original limits. Missing choices remain unresolved during compilation. Complete preparation requires exact independent readback and fresh configuration-matching qualification, but remains false execution/spend data. The token input is an inert separate-broker-stdin declaration. No fixture driver is imported, wrapped or run; no model/tool loop, custom gateway, new adapter or CLI execution command is added. Task, check environment/toolchain, policy, candidate, route/model, source and batch changes invalidate the prospective digest.
- **Fresh acceptance:** `rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_dispatch` passes **14 in 0.196s**. Full editable suite under `env -i`/temporary HOME/macOS network denial passes **213 in 8.205s**; fresh installed-wheel suite under the same restrictions passes **213 in 10.741s**. Combined 2D coverage is 72 methods plus 141 prior methods. Ruff lint/format passes (42 files); strict mypy passes (16 source files). Offline sdist/wheel build and fresh external hash-locked dependency/wheel installation pass. All eleven installed bound source files match working bytes, imports resolve to external site-packages, and installed CLI help remains passive `init/show/validate`. Exact commands/hashes/results are in [verification/continuity](qualification/phase-2d-dispatch-preparation-verification-v1-20261008.json).
- **Failures/evidence:** initial focused import failed with `ModuleNotFoundError: No module named 'crewshal.dispatch'` before implementation. Two non-code literal searches guessed nonexistent historical filenames; exact graph discovery/recorded help corrected them without executing code. No later lint, typing or acceptance failure occurred. Pinned recorded help documents `-`/stdin; historical source documents native flags and the official fixed-upstream proxy interface, not current live availability. Graph Verify starts from generation `2026-10-08T13:57:51Z`; matching updated coverage and both-direction depth-one trace are recorded in the verification artifact. Misresolved historical digest/file-method and `dict.get` edges were replaced with exact source, not treated as actual calls. Signals remain best-effort. No agents or paid Jev calls were used.
- **Continuity:** initial baseline has 770 fingerprinted tracked/nonignored files; 376 linked/current exact inputs totaling 18408665 bytes were loaded as data. Differences from the previous session's loaded fingerprints already existed at this session's start in seven maintained/current paths. This session modifies only seven existing documentation paths and adds dispatch source/test/guide/verification. All initial source/test/artifact bytes, historical 2C records and prior dirty preparation bytes remain identical. Documentation preserves previous achievement/session history. Generated build/cache files are excluded from tracked continuity.
- **Incomplete/not run:** production Linux envelope/supervisor, effective credential and financial enforcement, exact changed-profile qualification and separately approved actual native implementation/credential-free validator acceptance. No native/validator/provider/model/Jev startup, credential-store, VMware/SSH, host operation, paid infrastructure, version bump, commit/push, 2E or evaluation. Attempt ceilings are declared preparation values, not observed enforcement. Source hashes bind bytes, not effective settings, authorization or authenticity. Stable trusted coordinator directories remain assumed; hostile same-user replacement races are outside this offline claim. Original lost v5 cause/final cleanup and Windows/macOS native qualification remain unknown.
- **Next milestone/prompt:** continue 2D only. Feed this handoff, DEVELOPMENT-PLAN.md, PHASE-2D-DISPATCH-PREPARATION.md, new dispatch source/test/verification, prior collection/preparation source/evidence and every exact input in [the updated continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Initial prompt: “Resume 2D from source-bound dispatch preparation. Preserve preparation-only scope, per-project/session choices, original ceilings and historical/dirty bytes. Build bounded Linux supervisor source through accepted native/proxy mechanisms; prospectively bind/freshly qualify the exact configuration and separately obtain the concrete execution/spend batch gate before startup. Use trusted stopped capture with collect_codex_attempt, never the fixture driver or forged observations. Update evidence/handoff and stop at the next verified or blocked boundary; no publication until full 2D acceptance and no 2E.”

## Session ledger — 2026-10-08 Phase 2D retained native admission source

- **Milestone/outcome:** 2D remains incomplete. This session delivers only bounded read-only admission source and its retained-handle capture join. It checks an already created stopped native child; no envelope or process is created/resumed. No receipt grants execution, spend or qualification. Preparation-only choices remain controlling.
- **Revision/environment:** base/delivery revision remains `211538c86b13edf8971b6fc0de7e121d47fc3cf9`, branch `codex/phase1-architecture`, version 0.9.0, uncommitted. Observed macOS 27.2 (`26B5101f`) arm64, CPython 3.12.15, Pydantic 2.12.5, Ruff 0.14.1, mypy 1.18.2 with unchanged hash lock. No runtime platform equivalence is inferred.
- **Changes/trust:** [admission source/guide](PHASE-2D-NATIVE-ADMISSION.md) retains proc/pidfd and stopped PID/start/parent identity; checks exact native role, source-bound argv/initial environment, executable, namespace and stdio identities; verifies actual aggregate ancestry and unchanged controls/elapsed limits. Existing bounded capture receives retained resources with pipe/source readback. Thirteen bound package sources invalidate older configurations. Internal constructors, setup identities and child/clock are trusted seams; parsed data is never kernel proof. Receipt persistence and qualified bootstrap are still missing.
- **Fresh acceptance:** focused admission passes **28 in 0.652s**. Final full editable suite with fresh HOME/empty environment/network denial passes **265 in 9.031s**. Fresh installed wheel under the same restrictions passes **265 in 12.663s**. Combined 2D coverage is 124 methods plus 141 prior methods. Ruff lint/format passes (46 files); strict mypy passes (18 package files). Offline sdist/wheel build, external hash-locked dependencies and wheel install pass. All eighteen installed source bytes match, including thirteen dispatch inputs. CLI remains passive `init/show/validate`. Exact commands/hashes/results are in [verification](qualification/phase-2d-native-admission-verification-v1-20261008.json).
- **Failures/evidence:** initial import exposed the absent admission module. Initial tests exposed different macOS pipe-end identities and full-stat comparison rejecting read-induced atime changes; fixture semantics and material identity comparison were corrected. A temporary lambda caused Ruff E731/type errors and was replaced with a typed function. An unmatched patch context applied no changes. Final required checks pass. Caveman evidence review is unavailable: no callable MCP tools and CLI missing (exit 1); no cloud context/cost conclusion is inferred. Jev is loaded but paid calls remain disabled. No subagents used. Graph Verify starts from generation `2026-10-08T15:41:08Z`; final matching source coverage and exact snippets/both-direction traces are in the verification artifact. Source confirms the heuristic capture edge; coverage remains best-effort.
- **Continuity:** baseline hashes 778 tracked/nonignored initial files and reads 588 local linked inputs as data. Only six maintained documentation paths and current uncommitted dispatch source are intentionally updated; new admission source/tests/guide/verification are added. Historical 2C, prior source/tests/artifacts and all other dirty bytes remain identical. No previous ledger achievement is removed. Generated ignored build/cache files are excluded.
- **Incomplete/not run:** Linux admission/attachment, process creation/resume, envelope/bootstrap, hard enforcement/storage/role/credential/egress/financial authority, durable admission linkage, exact fresh qualification and separately approved actual implementation/credential-free check. Proc/child/kernel effects are synthetic. Initial environment/argv readback is not ongoing configuration proof; namespace equality is not privacy proof; a stopped checkpoint cannot prove no earlier native code. Trusted directory/setup ownership remains assumed; no hostile same-user race defense. No native/validator/provider/model/Jev, credentials, VMware/SSH, paid host, version bump, commit/push, 2E or evaluation. Lost v5 cause/final cleanup and Windows/macOS runtime support remain unknown.
- **Next milestone/prompt:** continue 2D only. Feed HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2D-NATIVE-ADMISSION.md, admission source/test/verification, dispatch/supervisor and every exact prior input in [the updated continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Initial prompt: “Resume 2D only from HANDOFF.md and the retained-native-admission source boundary. Read the four linked admission files, dispatch/supervisor source and all exact prior inputs. Preserve preparation-only scope, per-project/session choices, original limits and historical/other dirty bytes. Implement missing Linux envelope/bootstrap source through accepted systemd/cgroup, bubblewrap/setpriv, native sandbox and official proxy mechanisms. Independently establish stopped native PID/start/parent/boot, pipe and aggregate identities, storage/role/FD/credential/egress enforcement and hard deadline; bind admission persistence to supervised collection. Thirteen current source hashes invalidate old dispatch configurations. No fixture replay, custom gateway/model loop, direct host execution, manufactured observations or old eligibility transfer. Keep startup, credentials, model/provider/Jev spend, VMware/SSH and host operations disabled until a concrete project/session batch has its separate recorded gate. No global route decision or routine VPS test. Record fresh offline evidence and smallest remaining capability/gate, update handoff and stop at the next verified or blocked boundary. Publish only after complete offline and approved live 2D acceptance; no 2E.”

## Copyright maintenance closure — 2026-10-08

- **Scope and authority:** the owner explicitly requested “change the copyright to forera.ai and contributers.” The displayed notice uses the standard spelling: `Copyright 2026 forera.ai and contributors.` This supersedes the earlier preservation instruction for the current notice; the October 8 repository-transfer record remains historical.
- **Delivery:** README notice replaced, project notice prepended to LICENSE, and AGENTS.md updated for future sessions. The Apache-2.0 license body remains byte-identical. Version is synchronized at 0.9.2 for this documentation maintenance checkpoint. Base `35c34fa8afa5876eb9f61191338f8f41935e2b65`; delivery is the commit containing this closure entry (`rtk proxy git log -1 --format=%H -- LICENSE`). Push the current `codex/phase1-architecture` branch to `origin` at `https://github.com/forera-ai/Crewshal.git` under standing authorization and compare local HEAD with remote readback.
- **Acceptance:** on macOS arm64, Python 3.14.8 and development Python 3.12.15, copyright/version assertions and staged whitespace checks pass. All 783 pre-existing tracked/non-ignored files were hashed before editing; only exact authorized transformations change. Only seven maintenance files are staged from HEAD; unrelated Phase 2D work remains uncommitted. LICENSE after removing the prepended notice is byte-identical to the base revision. No runtime code, live qualification, model/Jev or paid-host check ran; the full acceptance suite was not rerun for notice/version maintenance.

Reproduce notice/version checks from the checkout:

```sh
rtk proxy .venv/bin/python - <<'PY'
from pathlib import Path
import runpy
import tomllib
notice = "Copyright 2026 forera.ai and contributors."
assert notice in Path("README.md").read_text()
assert Path("LICENSE").read_text().startswith(notice + "\n\n")
project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
assert project["version"] == runpy.run_path("src/crewshal/__init__.py")["__version__"] == "0.9.2"
print("Copyright and version checks passed")
PY
rtk proxy git diff --cached --check
rtk proxy git ls-remote origin refs/heads/codex/phase1-architecture
```

**Next milestone:** resume only Phase 2D preparation from the existing local retained-native-admission boundary. Initial prompt: “Read AGENTS.md, HANDOFF.md, DEVELOPMENT-PLAN.md and the local PHASE-2D-CONTINUATION-2026-10-08.md with every exact input it names. Use forera-ai/Crewshal, copyright forera.ai and contributors, and maintenance version 0.9.2. Preserve pending dirty work and original gates; finish the next bounded Phase 2D preparation milestone, with no Phase 2E or unapproved live execution/spend.” Exact next-session file set is preserved in [the repository-transfer checkpoint](REPOSITORY-TRANSFER-2026-10-08.md#next-session); its 0.9.1 wording is historical and this 0.9.2 notice update controls current metadata.

## Phase 2D durable admission/collection preparation boundary — 2026-10-08

- **Milestone/authority:** one bounded Phase 2D preparation boundary, resumed from the copyright closure prompt at line 824. Preparation-only per-project/session choices, original grants/ceilings and false execution/spend/qualification flags persist. The missing durable admission linkage is now implemented offline; no Linux envelope or live startup is inferred.
- **Base/delivery:** `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, `codex/phase1-architecture`, version 0.9.2. This source boundary is uncommitted. Only complete offline and separately approved live Phase 2D acceptance authorizes its version/commit/push ceremony. The prior maintenance commits already use forera-ai/Crewshal; this session does not amend them.
- **Changed behavior:** retained receipt/spec/clock snapshot and digest checks; `collect_admitted_codex`; one private registered admission record, supervision/scope links, SQLite atomic collection and final semantic/artifact readback. Existing supervisor callers remain independent and supply no admission proof. No generic nested transaction, launcher, tool loop, gateway, CLI endpoint or table-schema change is added. Fifteen independent methods create fresh real pipes/files/SQLite with synthetic process/proc/kernel effects.
- **Fresh acceptance:** focused admission/supervisor/integration suite 85 passed in 3.134s; complete editable 280 passed in 9.674s; fresh installed wheel 280 passed in 10.391s. Full runs deny network, replace inherited environment and use fresh HOME. Ruff lint passes, formatting checks 47 files, strict mypy checks 18 package files. Offline build and fresh hash-locked install pass; all eighteen installed package files and thirteen bound source files match working bytes. CLI remains init/show/validate; installed version is 0.9.2. Exact commands/results/source/build/continuity hashes are in [verification](qualification/phase-2d-admission-collection-verification-v1-20261008.json); independently reproducible checks are in [the guide](PHASE-2D-ADMISSION-COLLECTION.md). macOS arm64/Python 3.12.15; system Python 3.14.8 only reads preparation/continuity data.
- **Failures retained:** missing new entry point reproduced before implementation; initial registry import cycle through runtime-batch/durable resolved with runtime-local dispatch imports. Two patch context/validation failures changed no files. One fixture selected validator instead of scope evidence; exact scope ID corrected the test. These are development failures, not Linux/live qualification evidence.
- **Continuity:** read/hash 783 initial tracked/non-ignored files and 593 local linked inputs as data. Only admission/supervisor/durable source and six maintained documentation paths are intentionally changed; new source test, guide and verification are added. Prior tests, every historical qualification/preparation artifact and unrelated dirty bytes remain identical. No earlier ledger achievement is removed. Ignored build/cache files are excluded. Receipt clock fields invalidate prior unpublished snapshots; no prior configuration or qualification eligibility transfers.
- **Incomplete/not run:** Linux envelope/bootstrap and stopped-checkpoint compatibility, effective mount/storage/deleted-open/role/FD/credential/egress controls, independent hard deadline/owned admission-failure recovery, financial treatment, exact fresh qualification and separately approved actual implementation plus credential-free check. Snapshot identity and consistent SQLite linkage supply no authority or ongoing configuration proof. Artifact files/frozen copies are outside SQLite rollback; retained freeze targets refuse reuse. Trusted host/coordinator/directory ownership remains assumed; administrator/same-user hostile rewriting of all state is outside this evidence. No native/validator/provider/model/Jev, credentials, VMware/SSH, paid host, version bump, commit/push, 2E or evaluation. Lost v5 cause/original cleanup and Windows/macOS runtime qualification remain unknown.
- **Next milestone/prompt:** continue 2D preparation only. Feed this handoff, DEVELOPMENT-PLAN.md, PHASE-2D-ADMISSION-COLLECTION.md, admission/supervisor/durable source, new test/verification and every exact prior input in [the updated continuation](PHASE-2D-CONTINUATION-2026-10-08.md). Initial prompt: “Resume 2D from durable admission/collection linkage. Preserve forera-ai/Crewshal, copyright forera.ai and contributors, maintenance version 0.9.2, preparation-only per-project/session scope, original ceilings and historical/unrelated dirty bytes. Implement missing bounded Linux envelope/bootstrap source through accepted systemd/cgroup, bubblewrap/setpriv, native sandbox and official proxy mechanisms. Establish stopped PID/start/parent/boot and pipe ownership, effective storage/role/FD/credential/egress controls, independent hard deadline and owned refusal recovery before using collect_admitted_codex. No fixture replay, custom gateway/model loop, direct host execution, fabricated observations or old eligibility transfer. Keep startup, credentials, spend, VMware/SSH and host operations disabled until a concrete project/session batch has its separately recorded gate. Record fresh offline evidence and stop at the next verified or blocked boundary; publish only after complete offline and approved live 2D acceptance. No 2E.”

## Phase 2D Linux envelope/bootstrap preparation boundary — 2026-10-08

- **Milestone/outcome:** one bounded preparation milestone. Passive Linux envelope source/readback is independently verified; production bootstrap and Phase 2D remain incomplete. Per-project/session choices, original grants/ceilings and separate live authority gates persist. Source is clean independent coordinator preparation, not a fixture-driver wrapper or execution path.
- **Base/environment:** `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, `codex/phase1-architecture`, maintenance version 0.9.2, uncommitted. macOS 27.2 arm64, CPython 3.12.15, Pydantic 2.12.5, Ruff 0.14.1, mypy 1.18.2 and unchanged hash lock. Repository remains forera-ai/Crewshal, copyright forera.ai and contributors.
- **Changes:** LinuxEnvelopeBindings bind prospective inventory/policy/credential/financial digests to the full selection context and dispatch identity. Exact plan readback refuses changed source, controls, mounts, role argv, task/check/context and missing gates. Native, official proxy and independent validator fragments preserve bounded views and roles; systemd/controller requirements preserve original deadlines/resources. All owned storage representations reserve 1358954496 bytes without asserting enforcement. Existing admission's native Popen, executable/configuration, `T`/zero-tracer, stdio-only and exact worker/aggregate requirements stay intact. Fourteen source hashes invalidate earlier configurations. Eighteen new methods; one prior source-count assertion changes only 13 to 14.
- **Acceptance:** focused envelope/dispatch/admission/collection 75 passed in 1.958s. Full editable 298 passed in 14.209s; fresh installed wheel 298 passed in 11.593s. Both full runs deny network, replace inherited environment and use fresh HOME. Lint passes; formatting checks 49 files; strict mypy checks 19 package files. Offline sdist/wheel build, external hash-locked install, passive init/show/validate help and all nineteen installed source identities pass, including fourteen dispatch inputs. [Verification](qualification/phase-2d-linux-envelope-verification-v1-20261008.json) records exact commands/results, artifacts, source/input hashes and continuity.
- **Development failures:** missing module reproduced before implementation; new fixture initially omitted required Task.checks; existing test hard-coded thirteen sources; typing rejected an untyped literal-list default. These were corrected and final required checks pass. Initial linked-input scanner treated prose as a filename and was restricted to candidate paths; no repository mutation occurred. One guessed ADR filename did not exist; actual accepted ADR 0002 was read. Initial graph file-pattern search returned insufficient results; scoped exact searches and complete direct source resolved it. No Linux/live failure or paid Jev call occurred.
- **Graph/continuity:** Verify evidence starts with current Crewshal project and coverage generation 2026-10-08T20:03:56Z; final graph generation 2026-10-08T21:25:41Z matches source metadata with no recorded source gap. Complete relevant searches and both-direction depth-one traces are retained; heuristic import edges were confirmed in exact source. Ignored bytecode is excluded, and graph signals remain best-effort. Initial hashes cover 786 tracked/nonignored files; 788 linked/current inputs are loaded as data. Only admission/dispatch source, one existing admission assertion and maintained current documentation change. New envelope source/test/guide/verification are added. Historical qualification/preparation artifacts and all unrelated dirty bytes remain identical; session history is preserved. Ignored build/cache outputs are outside initial-byte preservation.
- **Incomplete/not run:** an owned production bootstrap compatible with the exact pre-native checkpoint; independent five-second deadline origin/enforcement; bounded owned admission-failure recovery; effective keyring/loop/mount/storage/role/FD/credential/egress controls; financial enforcement or explicit bounded exposure; new exact qualification and separately approved implementation plus credential-free validator acceptance. Systemd/bwrap handles, ordinary post-start SIGSTOP and ptrace stops are not presumed compatible. Prospective hashes supply no observations/readiness. No native/proxy/validator/helper/kernel startup, credentials, provider/model/Jev spend, VMware/SSH, paid-host operation, version bump, commit/push, 2E or evaluation. Lost v5 cause/original cleanup and Windows/macOS runtime qualification remain unknown.
- **Next milestone/prompt:** continue Phase 2D preparation with the smallest owned Linux bootstrap compatible with the existing admission contract, original independent deadline and owned refusal recovery. Feed AGENTS.md/RTK.md, this handoff, DEVELOPMENT-PLAN.md, PHASE-2D-LINUX-ENVELOPE.md, new source/test/verification, current dispatch/admission/supervisor/durable and updated admission test, plus every prior exact input in PHASE-2D-CONTINUATION-2026-10-08.md. The guide contains the full initial prompt. Startup/spend/host operations remain separately gated; publication waits for complete offline and approved live 2D acceptance. Stop at that next verified or blocked boundary; no 2E.


## Phase 2D owned bootstrap helper/handoff source boundary — 2026-10-09

On unchanged base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, [owned source preparation](PHASE-2D-OWNED-BOOTSTRAP.md) adds a packaged uncompiled Linux helper, exec-event-to-verified-SIGSTOP-delivery handoff, unchanged native admission, separate original-deadline watchdog source and bounded owned refusal recovery. No launcher or native release is supplied; no observed Linux checkpoint or hard enforcement is claimed. Twenty-five new methods bring coverage to 182 Phase 2D / 323 complete offline tests. Focused affected suite: 100 in 2.123s. Complete editable: 323 in 10.483s; fresh installed wheel: 323 in 16.894s, both with empty environment/fresh HOME/network denial. Ruff lint/format and strict typing pass; offline build/install and 21 packaged source-byte comparisons pass. Both helper/controller files are bound among sixteen current dispatch sources.

Initial module absence was reproduced. Preserve the recorded readonly-fixture, duplicate-test-collection, lint/type and dereferenced-venv command failures; final corrected checks pass. Original admission implementation and unrelated dirty/historical bytes remain intact. Production namespace-resident direct-Popen/initial traced-proc attachment, compiled helper/watchdog identity and timer/role/FD/ordering readback, effective storage/credential/egress/financial controls, fresh exact qualification and separately approved implementation/check remain missing. Source/acknowledgement inputs and synthetic drivers are not capabilities or authority. Package stays 0.9.2; no version bump, commit/push, paid model/provider/Jev call, real helper/child/native/validator startup, credentials, VMware/SSH, host controls or 2E. Lost v5 cause/original cleanup and other-platform runtime support stay unknown.

Next session remains 2D: implement only the smallest compatible parent/namespace/traced-attachment and watchdog-readback bridge, preserving unchanged admission, original deadline/recovery and all prior controls/gates. Feed the guide, its two source files, new tests, verification, package-data metadata, dispatch/admission and **every prior exact input** from the envelope/continuation. [Exact initial prompt and file list](PHASE-2D-OWNED-BOOTSTRAP.md#next-boundary-exact-prompt-and-inputs) govern resumption. Stop at that next independently verified or blocked boundary; publish only after complete offline and approved live 2D acceptance.

### Phase 2D parent/watchdog bridge source — 2026-10-09, unpublished

The owner requested the owned-bootstrap guide's exact next milestone. Delivered only its preparation source boundary: retained namespace parent/watchdog identities, original effective timer/FD/kill readback, readiness before one-shot direct-Popen inherited placement, initial traced attachment and retained owned refusal resources. Twenty-three fresh methods, 123 focused and 346 complete editable/fresh-wheel offline tests pass, with denied network/empty environment and static/build/source checks. Seventeen bound sources require new qualification. No live Linux/helper/startup or spending operation, version bump, commit/push or 2E occurred. Original dirty/historical bytes remain intact except the explicitly enumerated milestone source/test/docs edits in verification. The guide records all development failures and limitations.

Next source milestone: owned namespace/watchdog setup and terminal resource lifetime through accepted mechanisms. Use [the exact prompt and complete input list](PHASE-2D-PARENT-WATCHDOG.md#next-boundary-exact-prompt-and-inputs), including every earlier historical input as data. Prepare the bounded wrapper/init/control-FD and watchdog creation/cleanup route; never invoke the current parent Popen/kernel effects, transfer historical eligibility or relax original admission/limits. Effective containment, exact helper/Linux qualification and the separate concrete project/session live gate remain mandatory. Stop at the next verified or blocked source boundary; publication waits for complete 2D acceptance.

### Phase 2D owned setup and terminal process lifetime source — 2026-10-09, unpublished

Completed this source boundary only. [Guide](PHASE-2D-OWNED-SETUP.md), [source](../src/crewshal/linux_setup.py), [35 methods](../tests/acceptance/test_phase_2d_setup.py) and [verification](qualification/phase-2d-owned-setup-verification-v1-20261009.json) deliver retained sealed controls, fixed-FD C source normalization, bounded observer/setup inheritance, namespace-local attachment and direct watchdog creation before unchanged stopped admission. Local/external terminal source observes owned worker emptiness and watchdog exit/reaping without restarting grace; resource-limit refusal does not remove cleanup ownership. Every resource-reuse result remains false pending physical cleanup. Original controls/admission remain unchanged. 240 Phase 2D / 381 complete tests, 158 focused tests, editable/fresh-wheel network-denied execution, static checks and 23 source comparisons pass; eighteen files bind dispatch. Current source invalidates older exact configurations. All constructor/kernel effects are synthetic and C remains uncompiled. Failures and preserved historical/dirty bytes are recorded. Base/branch/version remain `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, `codex/phase1-architecture`, 0.9.2; no commit/push, effects, credentials, paid calls or 2E.

Next source milestone: owned physical-resource teardown and trusted parent entry/inventory binding through accepted mechanisms, retaining unknown cleanup. Use [the exact next prompt and full inputs](PHASE-2D-OWNED-SETUP.md#next-boundary-exact-prompt-and-inputs), including every prior input as data. Qualified root/helper/library installation, effective role/storage/FD/credential/egress/financial/deadline controls, Linux inheritance and pre-instruction checkpoint, fresh exact qualification and separate concrete project/session live gate remain mandatory. Stop at the next verified or blocked boundary; publication waits for complete 2D acceptance.

## Physical teardown ordering and trusted parent inventory source closure — 2026-10-09

The owner resumed the exact next boundary from PHASE-2D-OWNED-SETUP.md with caveman, codebase-memory and Jev skills. Explicit no-spend scope controlled; no Jev model was called. This session implemented only retained inventory binding/readback and physical release ordering, with synthetic kernel seams. Forty-six new tests, fresh editable/installed-wheel checks, static checks and package byte equality are recorded in the immutable new verification. Development failures are retained there; no historical qualification/guide is rewritten, no old eligibility transfers and no milestone is promoted to live acceptance.

Next smallest milestone: concrete retained Linux storage-owner readback and bounded teardown operations through the accepted private anonymous keyring/ext4/eCryptfs/owned-loop mechanisms. Actual parent/root installation/import/loader proof and observer/aggregate final handoff remain separate gaps. Feed AGENTS.md, RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, PHASE-2D-OWNED-TEARDOWN.md, linux_inventory.py, linux_teardown.py, both new acceptance modules, the new verification, current setup/envelope/dispatch source/tests, package metadata and every exact prior input linked from PHASE-2D-OWNED-SETUP.md. Use the new guide's verbatim initial prompt. Keep all startup, kernel effects, credentials, paid calls, VMware/SSH and host operations disabled; no direct-host argv, custom gateway/model loop, global route choice, routine VPS test or 2E. Version/commit/push remain excluded until complete offline and approved live 2D acceptance. No new owner decision is required for ordinary bounded source work; a concrete mechanism/ceiling incompatibility requires the smallest precise decision.

### Phase 2D retained Linux storage-owner source — 2026-10-09, unpublished blocking boundary

The owner's exact prior prompt requested concrete retained Linux storage-owner readback and bounded teardown source. Added linux_storage.py, 44 current fresh methods, two teardown deadline methods and a new guide/verification. Exact kernel rows and pinned FDs bind mount namespace/mount IDs, private anonymous ring provenance and revocation errno, loop UAPI/backing inode, relative leaf identity and positive deleted-open/mapped/alias references. Narrow child job source checks existing observer/aggregate controls before fork, retains pidfd/reaping, uses one fixed original cleanup deadline and refuses retries/unknown children. No invocation of that source occurred.

A concrete limitation blocks physical release: proc enumeration cannot prove closure of taskless namespaces, socket-passed/asynchronous kernel references, delayed/additional loops and concurrent mutation. Empty observations remain None; no caller readiness flag can authorize cleanup. This source cannot pass actual physical-resource admission until an effective retained closure mechanism and trusted setup handoff exist. Job transport tests also do not qualify fork inheritance, libc/interpreter identity, blocking admission reads or whole-observer deadline enforcement. All remaining installed-parent/effective-control/Linux/live gates remain open.

Fresh evidence: 473 complete tests (332 Phase 2D), focused owner/teardown 72, Ruff lint/format 61 Python files, strict mypy 25 package modules, offline sdist/wheel build and byte equality for 26 packaged sources. Complete editable and fresh-wheel suites use denied network, empty inherited environments and fresh HOME. Exact commands, development failures, original-input continuity and source digests are in [the verification](qualification/phase-2d-linux-storage-owner-verification-v1-20261009.json). Base `7ae02cfc64ce71b8f443af4073eb4814b588eb4f`, branch `codex/phase1-architecture`; original dirty/historical bytes outside the recorded intentional edits are preserved. Version 0.9.2 remains unchanged, no commit/push/release. Next session receives [the precise closure prompt and complete input chain](PHASE-2D-LINUX-STORAGE-OWNER.md#next-boundary-exact-prompt-and-inputs). No next milestone begins here; no startup/kernel/compiler/credential/provider/Jev/host operation, routine VPS test or 2E.

### Phase 2D source publication checkpoint — 2026-10-09

The owner expressly authorized commit/push after the verified retained storage-owner source boundary. Publish the complete verified pending 2D dependency set as version 0.10.0, preserving prior guide/verification bytes and all runtime authority separation. [The checkpoint](PHASE-2D-SOURCE-CHECKPOINT-2026-10-09.md) records the superseding prompt, exact inputs and [fresh publication evidence](qualification/phase-2d-source-checkpoint-verification-v1-20261009.json). Delivery is the commit containing that guide; push success/readback is reported in the publishing turn. Effective reference closure remains the only next source milestone; no next milestone starts during publication. Git commit/push is authorized, while all execution, qualification, paid/live, release and 2E gates remain unchanged.

### Phase 2D effective retained storage closure — 2026-10-09, corrected source and blocked decision

Resumed from `8e010b5ca2dd3298268132613f8ad17ff9db07c6`, branch `codex/phase1-architecture`, synchronized version 0.10.0. The complete prior chain was read as data and snapshotted: 821 inputs, including six ignored generated metadata files; historical guides/drivers/qualifications remain unchanged. Codebase-memory Verify used fresh project/generation, targeted searches/snippets/both-direction traces and exact coverage, with direct source checks for material claims and heuristic-edge limitations. Requested Jev made no paid call.

The narrow correction changes only concrete loop ENXIO readback and its acceptance expectations: unknown final release retains backing/handles rather than returning an absent loop. Three focused cases demonstrably failed on baseline source; final focused owner/teardown suite passes 73, complete editable/fresh-wheel suite passes 474 (333 Phase 2D), Ruff lint/format passes 61 files, strict mypy passes 25 package modules, offline sdist/wheel and all 26 packaged-source comparisons pass. The new ledger retains initial formatting failure and its correction, commands/environment/digests, source references and limits. Twenty-one bound sources remain, with changed storage bytes invalidating every earlier prospective configuration.

The inspected upstream v7.0 loop route, resolved to commit `028ef9c96e96197026887c0f092424679298aae8`, performs backing teardown on final loop close and permits ENXIO during rundown. Current owner loop FDs survive that transition; no actual final-close/release-completion readback is implemented. This is a concrete source compatibility conflict, not target-kernel qualification. Taskless namespaces, deleted-open/mapped/socket-passed/asynchronous kernel references, additional/delayed loop attachments and concurrent mutation also prevent retrospective global closure from current scans/FD transfer. The architecture trusts the operator host; no malicious-host threat is added.

Smallest owner decision: whether final closure of every owned loop-device open-file reference may occur inside the loop-detach stage, before backing release, with independent retained identity/non-rebinding/completion evidence. That decision alone cannot resolve effective from-creation reference confinement or the trusted setup handoff. No architecture, kernel/policy, order or ceiling amendment is implemented here. Unknown resources remain retained/charged; source remains unqualified and all reuse is false. Actual installed parent/root/helper/library/FD identity, observer/aggregate final handoff, exact Linux qualification and separate live acceptance remain unresolved. No next milestone begins.

Follow [the new exact continuation prompt and files](PHASE-2D-STORAGE-CLOSURE-BLOCKER-2026-10-09.md#next-session-exact-inputs-and-initial-prompt) and [reproducible verification](qualification/phase-2d-storage-closure-verification-v1-20261009.json). Version remains 0.10.0; no commit/push because the resumed checkpoint prompt explicitly requires complete offline and approved live 2D acceptance. Earlier checkpoint-only publication authorization remains historical. No compiler, fork/Popen/helper/native/namespace/key/mount/loop/cgroup action, credentials/spend, VMware/SSH, target-host operation, release or 2E occurred.

### Phase 2D approved subscription interface and finite source — 2026-10-09

The owner approved the official subscription route for implementation/preparation and separately permitted only stock vendor authentication recovery inside the unchanged attempt. Pinned source exposed auth recovery independent of retry settings, a default unbounded reconnect feature, lossy legacy sandbox readback, stock helper placement under private HOME and CLI literal-dot parsing. Record those facts and their corrections; immutable proposals/evidence remain dated history. Implement six finite requests and complete startup projection/origin refusal, unique account linkage, fixed candidate cwd, exact thread/turn/item lifecycle, retained stdin provenance and bounded writes/raw capture. A protocol event cannot grant authority or replace independent terminal evidence. Ten transport and additional protocol/integration methods cover the identified failure paths. Final exact counts/commands, fresh offline/wheel/build/static checks, source identities, development failures and review limits are in the new verification. No actual Linux/runtime/login/provider/model operation occurred.

Continue the same consolidated 2D milestone with [the exact next prompt and complete inputs](PHASE-2D-SUBSCRIPTION-AUTH-BOUNDARY-2026-10-09.md#evidence-and-continuation). Finish the actual from-creation producer, persistent charged ownership and total growth controls; establish installed identities and independently observe native/tool/helper filesystem, PID/proc, FD, network and credential exclusion under the original limits; prepare exact qualification/live artifacts before the separate final operational/login/quota gate. No resolved decision is reopened. Source verification does not complete 2D, authorize reuse or permit publication; version stays 0.10.0 and current branch remains uncommitted. No 2E.

### Phase 2D irreversible capacity and partial creation custody — 2026-10-09

Integrated the three source branches locally after subscription subagents exhausted their allowance; no paid fallback. Added complete-journal synchronous capacity CAS, exact minted-token identity, one reservation per original live claim and refusal without refund. Fresh concurrent SQLite claimants commit exactly one charged reservation. Missing/replaced/reset journals or copied token data refuse; a record is denial data and cannot establish installed pool availability. Corrected subscription cwd/profile/authentication projection and C helper selection without compiling it.

Partial production now retains actual FDs before acknowledging subsequent mutation. The bounded job pins child pidfd/proc before effects; reservation readback permits exactly that original producer child, rejects extra/migrated/rebound tasks and keeps normal sole-observer checks. Busy loop attachment has no retry or cleanup; potentially blocking loop readback is confined to a separate bounded child. Review corrected the initial nonexistent capacity property, own-child rejection, parent ioctl, Linux-only socket flag typing/fixtures, original job identity and creation deadline. Early test/format failures are recorded rather than treated as qualification.

Fresh integrated final evidence: 583 complete tests (442 Phase 2D), focused 86, Ruff 67 files, strict mypy 27 modules, offline source/wheel build and fresh denied-network installed suite; all 28 packaged sources match and 23 inputs bind dispatch. [The current source slice and unfinished mechanics](PHASE-2D-PRODUCTION-OWNERSHIP-2026-10-09.md) and [reproducible verification](qualification/phase-2d-production-ownership-verification-v1-20261009.json) preserve the complete prior chain. No actual operational source or historical driver was invoked. Fixed physical pool/journal/root/growth and installed-view/credential/native qualification remain absent; no new policy decision is requested. Phase 2D remains incomplete, version 0.10.0 and branch uncommitted. Honor the owner's condition to commit/push after full acceptance, not after a partial source check. No next milestone starts.

### Phase 2D owned filesystem/view source — 2026-10-09, uncommitted

Continued the same full completion request, preserving every accepted decision and prior immutable ledger. Delivered only source mechanics, corrected a deterministic ancestor-symlink capture race and retained independent readback bounds. Final current evidence is 639 complete / 498 Phase 2D tests on editable and fresh installed wheel, with denied network and empty inherited environment, offline build, static checks and byte equality. The current guide records all missing implementation/qualification and development failures. A concrete syntax-only compiler approval is pending; no operational action, version bump, commit/push or 2E occurred. Use its exact continuation/input chain rather than historical source-only counts or synthetic installation records.

### Phase 2D approved syntax refusal and retained-root capture — 2026-10-10

Executed the owner's exact single approved syntax transport after checking frozen source/client and private argument arrays. SSH transport completed, but noninteractive sudo refused before compiler invocation. Recorded sanitized diagnostic/result only, retaining private access/output and consumed marker. No retry, credential retrieval or host configuration change. Independent source regression reproduced regular-directory root replacement in preparation and freeze; one retained root FD plus identity checks now refuses both. This does not prove worker cessation, atomic snapshot, readonly projection, release or phase completion. Current verification/continuation is linked above. Version/branch remain uncommitted at 0.10.0; all substantive effective Linux/live 2D gates remain open and no next milestone starts.

## Effective Phase 2D blocked boundary — 2026-10-10

Continued the same consolidated milestone from 758079b / 0.11.0 and preserved dirty source. The [PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md](PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md) guide records prepared source, exact source-derived MAP_SHARED/WAL incompatibility, smallest missing compatible enforcement capability, remaining installed entry/view/admission identities, exact offline reproduction and next-session prompt/input chain. Final denied-network source/fresh-wheel and static results are recorded in its immutable verification; actual Linux/runtime/storage closure remains unknown. Full Phase 2D acceptance and its required twenty-case twice/native-tool/live-validator gates did not pass. Installation admission remains closed; no new owner decision is inferred, no accepted decision reopened, no further syntax or operational batch invoked. Publication remains conditional on full acceptance.

## Owner-authorized blocked checkpoint publication — 2026-10-10

The owner explicitly requested publication and next-session materials after the 863 / 722 Phase 2D blocked boundary. Version 0.12.0 publishes the preserved source/evidence checkpoint; use the containing commit as the delivery revision, with push independently verified against the canonical current branch. The checkpoint, publication ledger and next-session prompt/input manifest retain the exact incomplete gates and closed installation admission. Continue compatible effective storage enforcement and the missing installed original-parent/validator/admission chain before preparing separately approved Linux/live qualification. No acceptance, operational or release authority is inferred from publication; no Phase 2E work follows session closure.

## Phase 2D blocked verification and communication rule — 2026-10-11

The owner requested full Phase 2D completion or a list of blocking causes. The session verified the current refusal and supplied that list. [The report](PHASE-2D-BLOCKED-2026-10-11.md) records the storage conflict, missing compatible enforcement, incomplete installed execution chain, and absent Linux/live acceptance. [Fresh evidence](qualification/phase-2d-blocked-verification-v1-20261011.json) records exact commands, source hashes, graph limits, and environment. All 77 focused and 863 complete source tests pass, including 722 Phase 2D tests. The complete suite and compatibility check deny network access and use an empty inherited environment with a fresh HOME. The source result does not qualify installed Linux behavior.

Base revision remains `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc`, branch `codex/phase1-architecture`, version 0.12.0. AGENTS.md records the owner's permanent ASD-STE100 rule. Production source, tests, and historical records remain intact. No operational batch, credential access, paid call, commit, push, or Phase 2E work occurred. Continue the same Phase 2D milestone from the report's exact prompt and input list. The next required capability is compatible installed storage enforcement with independent readback. Accepted decisions require no repeat approval. Publication remains conditional on full Phase 2D acceptance.

## Phase 2D source progress and bootstrap decision — 2026-10-12

Phase 2D has not passed acceptance.
SSH and root access work on the owner's local VMware Ubuntu installation.
The owner accepted the three lanes and charged helper build source amendments.
Those decisions remain accepted.

Source now includes compatible storage readback, installed identities, the finite parent, validator views, and admission linkage.
It also includes original qualification process transport, the finite synthetic TLS broker, fixture seeding, and observer evidence collection.
These source changes remain unqualified on Linux.

[Fresh source evidence](qualification/phase-2d-source-progress-v1-20261012.json) records 1,079 passing method occurrences.
These represent 1,063 unique methods, including 922 Phase 2D methods.
The complete suite denied network access and used an empty inherited environment with a fresh HOME.
Source hashes remained unchanged during the suite.
Ruff checks pass; mypy passes for 41 source files.
The original batch tests remain intact; new observer tests use a separate module.
A fresh installed wheel still requires verification.

The [bootstrap source proposal](PHASE-2D-BOOTSTRAP-CLOSURE-DECISION-2026-10-12.md) records two additional source obstructions.
The existing build receipt cannot derive the required new compiled policy and its audit identities.
The current C batch timer also starts after helper compilation.
The observer service deadline does not independently stop the sibling compiler role.
The proposed amendment supplies one original timer before building and extends one charged build receipt.
This new source decision is pending.
No accepted decision requires another answer.

The complete executable operational entry and immutable input closure remain unfinished.
The separate operational approval has not been requested.
Both twenty-case Linux runs and actual frozen-candidate live acceptance remain required.
No new compiler, Linux mutation, authentication, subscription request, publication, or Phase 2E work occurred.
The base revision, branch, and version remain unchanged.

Continue Phase 2D from the original blocked report and its exact continuation inputs.
Also supply the accepted three-lane and charged build decisions, bootstrap proposal, operational preparation, and fresh source evidence.
Resolve the new source decision, then complete the source and freeze the exact operational batch.
Request operational approval only after the complete batch is reviewable.
Preserve all original limits, handles, charges, clocks, unknown results, and dirty files.
Publish only after full Phase 2D acceptance, then stop.

## Phase 2D active continuation — 2026-10-13

Phase 2D has not passed acceptance.
The owner accepted the bootstrap source amendment on October 12.
All earlier accepted decisions remain accepted.
Version 0.13.0 now identifies the unreleased candidate before its exact runtime inputs are frozen.
The branch and base revision remain unchanged.
No commit or push has occurred.

The current source includes the original early timer, charged compiler volume, helper and policy build receipt, and finite batch entry.
It also includes stock device login, exact kernel profile directory readback, and original idle retention.
The original observer holds its FDs after the batch ends.
The independent timer preserves the original 570-second cutoff and 600-second end.
No further active work starts during idle retention.
All original limits and charges remain unchanged.

A fresh denied-network suite passed 1,142 occurrences and 1,126 unique methods before the latest input corrections.
It included 956 Phase 2D methods.
Source hashes remained unchanged during that run.
The latest directory and streaming-cache checks pass; final combined source and fresh-wheel verification remain required.
The first two packaging attempts failed because the build backend was unavailable or not extracted.
An extracted pinned setuptools 80.9.0 backend produced a wheel without network access.
These packaging attempts were not C compiler attempts.

Read-only VM evidence identifies Ubuntu 26.04.1, aarch64, explicit Python 3.12.3, GCC 15.2.0, and AppArmor parser 5.0.2.
The kernel signature is Ubuntu 7.0.0-38.38-generic 7.0.14.
The exact kernel source review supports the unchanged scaffold formulas.
Short symlink targets use separate kernel objects and create no file-data extents.
Private source and runtime input data remain outside Git.
No new C compilation, Linux mutation, authentication, provider request, or Phase 2E work has occurred.

The complete immutable batch and separate operational approval remain pending.
The VM needs a readonly Crewshal and Pydantic input capability.
Its writable shared folder does not establish that capability.
Complete the exact input package, source and wheel checks, and operational commands before requesting operational approval.
Then run both twenty-case Linux qualifications and the actual frozen-candidate live acceptance.
Publish only after full acceptance, then stop.

### Phase 2D complete operational proposal — 2026-10-13

The complete source and private executable batch are now prepared.
[The operational proposal](PHASE-2D-OPERATIONAL-BATCH-2026-10-13.md) identifies exact commands, immutable inputs, clocks, exposure, decisions, and stop conditions.
[The current batch record](qualification/phase-2d-executable-batch-v3-20261013.json) supplies frozen hashes and complete owner script and unit bodies.
Earlier preparation records remain intact and supply no execution authority.
Both source and fresh-wheel suites pass 1,150 occurrences and 1,134 unique methods, including 993 Phase 2D methods.
The suites deny network access, use an empty inherited environment, and preserve source hashes during execution.
All 47 package files match; Ruff checks and mypy pass.
The qualification probe now requires compatible shared-file mapping, denied shared-memory routes, and denied native authentication file access.
The original twenty cases, limits, charges, observer, clocks, and handles remain unchanged.

The source now supplies exact owner input capability preparation and private disk binds without changing original installation paths.
No new C compilation, Linux mutation, login, subscription turn, commit, push, or Phase 2E work has occurred.
The separate operational approval remains required by the owner's original task.
After that approval, execute only the exact current batch and complete both Linux qualifications and actual live acceptance.
Record each actual result and preserve unknown custody after any refusal.
Publish only after full Phase 2D acceptance, then stop.


## Phase 2D actual batch continuation — October 13, 2026

Phase 2D remains incomplete. No Phase 2E work has started.
The owner approved the v3 operational batch, the v5 refusal-before-charge exception, and the v6 two-charge exception.
The first upload refused a Python-generated locale before any upload or installation.
The corrected entry removes that value only after empty kernel environment readback.
The first observer then refused the tab-separated UID and GID identity check before charge.
The corrected numeric field parser passes actual independent readback.
The v5 observer consumed its full charge and marker, then refused mismatched setup role limits before either compiler.
The corrected constructor restores the original setup and supervisor limits.
The v6 observer consumed a second full charge, then refused a legitimate empty timer runtime file before its timer process.
The corrected runtime check preserves exact bytes, protections, readonly mounts, and deadlines for empty files.
A new runtime inventory also pins fourteen actual bytecode files.

The VM then restarted. Fresh kernel readback confirms lost original observer processes and FD custody.
Both full charge journals remain byte-identical, retained, and unknown.
No compiler, installed backing, AppArmor profile, qualification, login, or live turn has started.
IPv4 forwarding is zero.
Both latest complete suites pass 1156 occurrences and 1140 unique methods, including 999 unique Phase 2D methods.
All 47 wheel files match current source; static checks pass.
The candidate remains unreleased 0.13.0. No commit or push has occurred.

[The complete current proposal](PHASE-2D-RUNTIME-CONTINUATION-2026-10-13.md) and [exact v7 record](qualification/phase-2d-executable-batch-v7-20261013.json) define the next operational gate.
They require explicit approval for a 24 GiB combined reserved test allowance and continuation with lost old custody recorded as unknown.
Actual common kernel limits remain 805306368 bytes, 128 tasks, one CPU, and zero swap.
Each new original batch retains the original 8 GiB logical and allocated limits.
The old records supply no live ownership, eligibility, physical closure, refund, or reusable resource.
Do not repeat accepted decisions or consumed compiler attempts.
Publish only after full actual Phase 2D acceptance, then stop.


## Phase 2D mapping continuation gate — October 13, 2026

The owner approved the v7 24 GiB combined reservation exception and continuation after lost older custody.
The v7 observer and timer remain retained at PIDs 5553 and 5555.
The original timer reached its initial trace stop, then mapping lookup returned errno 2.
The parser used padded `maps` addresses for unpadded `map_files` names.
The corrected parser preserves numeric ranges and all original identity checks.
All 33 actual mapped ranges and 11 actual mapped file readbacks pass independently.
Both complete suites pass 1158 occurrences and 1142 unique methods, including 1001 unique Phase 2D methods.
All 47 wheel package files match current source; static checks pass.

No C or AppArmor compiler has started.
No installed backing, loaded policy, qualification, login, or live turn has started.
All three full charges remain retained with unknown results.
The first two original process owners remain lost after the guest restart.
The current observer, stopped timer, original FDs, groups, journal, marker, clock, and unknown result remain retained.
IPv4 forwarding is zero.

[The complete mapping proposal](PHASE-2D-MAPPING-CONTINUATION-2026-10-13.md) and [exact v8 batch](qualification/phase-2d-executable-batch-v8-20261013.json) define the pending operational gate.
The requested exception adds one new full charge and increases combined reserved storage from 24 GiB to 32 GiB each.
Actual common kernel memory, task, CPU, and swap limits remain unchanged.
Do not infer approval from the earlier v7 exception.
Do not reset old clocks, close unknown original handles, refund charges, or repeat consumed compiler attempts.
Phase 2D remains incomplete. The candidate remains unreleased 0.13.0.
No commit, push, or Phase 2E work has occurred.

### Exact continuation inputs and prompt

Feed AGENTS.md, RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, and all accepted architecture decisions.
Also feed the original October 11 blocker and its exact continuation inputs.
Feed the three accepted source amendments, the current mapping proposal, and the exact v8 batch record.
Preserve every v3 through v7 operational record as dated evidence.
The private v16 immutable archive, batch plan, controller, and actual readbacks remain outside Git.
The pending human decision must bind the exact v8 record hash before execution.

Continue Phase 2D on the current dirty branch from revision 87ed7e6f6c766c7ff2df245ad05569558a9ca3bc.
Preserve all original documentation, dirty work, charges, handles, clocks, and unknown results.
Use ASD-STE100 for every explanation and decision request.
Consume only an explicit approval of the exact v8 reservation exception and operational batch.
Do not repeat accepted decisions or consumed compiler attempts.
Then perform its exact input preparation, independent readback, original timer, sole unconsumed build, and actual acceptance sequence.
Pass all twenty original Linux cases twice and cover every enabled native file tool.
Complete actual frozen-candidate acceptance and independent credential-free validation.
Publish only after full Phase 2D acceptance under the explicitly amended authority, then stop.
Record any exact missing capability with fresh evidence. Do not begin Phase 2E.

## October 13: v8 execution and exact private file continuation

The owner approved the exact v8 mapping exception and batch through question `call_LHhNyof7DFyXRzGaPJXZGb2a`.
The approval binds record SHA-256 `deeb0c5b318b7fbcde53dcd451021049c5592908b658c7b465082cc50fd23c43`.
The approved upload, owner preparation, forwarding change, and observer start each ran once.
Independent readback verified all 226 inputs, both unit hashes, unchanged prior journals, and the common and new kernel limits.

The observer has PID 6476 and retains original timer PID 6478.
It recorded a fourth full charge and created its original 16 MiB compiler volume.
The volume remains empty.
Its helper build admission refused the Ubuntu env inode with 116 hard links before compiler process creation.
The admission remains consumed; neither compiler started.
The observer retains every partial handle, full charge, original clock, and unknown result.
The fourth journal SHA-256 is `ebcd9bd415699d422390a13670c85a0f9479168a9da1d1b89d9681016d8a20a5`.
Its configuration SHA-256 is `94c0af7a0a9bc133f4648919a0cc96e5f3400861b56de0a8918e88c1f2ef38d0`.
The original observer PID 5553 and stopped timer PID 5555 also remain retained.
IPv4 forwarding is zero after the approved restoration command.

Independent inspection covered 1180 prospective file paths.
The env inode is the only existing input that fails the protected regular file and single-link checks.
Three absent paths identify outputs that require the new charged build.
The exact private copy preserves executable bytes, its root inventory entry, and every production single-link check.
The new owner unit supplies that copy through a private read-only bind.
All 227 immutable archive members pass local size and hash checks.
Both new owner scripts pass parsing and Ruff checks.
The two 1158-test suite results remain current because all production and test source hashes remain unchanged.

The [private file continuation](PHASE-2D-SINGLE-LINK-CONTINUATION-2026-10-13.md) and [v9 record](qualification/phase-2d-executable-batch-v9-20261013.json) define the new pending gate.
The exception requests one new original batch and increases combined reserved storage from 32 GiB to 40 GiB each.
It expressly permits one new build admission without resuming the consumed v8 admission.
Actual common kernel memory, task, CPU, and swap limits remain unchanged.
The exact input member bound increases to 33554432 bytes within the existing transfer hard file limit.
Every previous charge, clock, timer, handle, unknown result, and accepted loss of older custody remains recorded.
The pending request supplies no authority until the owner answers.
Phase 2D remains incomplete at unreleased candidate version 0.13.0.
No commit, push, or Phase 2E work has occurred.

### Exact continuation inputs and prompt

Feed AGENTS.md, RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, and the accepted architecture decisions.
Also feed the original October 11 blocker and its exact continuation inputs.
Feed the three accepted source amendments, all dated operational continuations, the private file proposal, and the exact v9 record.
Preserve every v3 through v8 batch record as dated evidence.
The private v17 archive, plan, controller, and actual readbacks remain outside Git.

Continue Phase 2D on the dirty branch from revision 87ed7e6f6c766c7ff2df245ad05569558a9ca3bc.
Preserve all original documentation, dirty work, charges, clocks, timers, handles, and unknown results.
Use ASD-STE100 for every explanation and decision request.
Consume only an explicit approval of the exact v9 exception and batch.
Do not repeat accepted decisions or resume consumed build admissions.
Perform the exact input preparation, independent readback, original timer, new charged build, and actual acceptance sequence.
Pass all twenty original Linux cases twice and cover every enabled native file tool.
Complete actual frozen-candidate acceptance and independent credential-free validation.
Publish only after full Phase 2D acceptance under the explicitly amended authority, then stop.
Record any exact missing capability with fresh evidence. Do not begin Phase 2E.

## October 13: v9 execution and exact build mapping continuation

The owner approved the exact v9 exception and batch through question `call_87a36c14771e48a8ba9fee3e721322fd`.
The approval binds record SHA-256 `58c4ac0819555ba85d9f20a3f5ad2b3f5d490811c6d7070b8326f134897bea71`.
The approved upload, preparation, forwarding change, and observer start each ran once.
All 227 inputs, both units, the private env identity, prior journal hashes, and original kernel limits passed independent readback.

Observer PID 7157 recorded the fifth full charge and retains timer PID 7159.
C compiler PID 7168 reached its original executable trace stop.
The separate build mapping reader used the padded maps address and refused with errno 2 before detachment.
The failure path stopped its original setup group.
The compiler remains a zombie with its original pidfd and proc FD retained by the observer.
All three output files contain zero bytes.
The compiler attempt remains consumed; no AppArmor compiler started.
No policy installation, qualification, authentication, or live turn occurred.
The original timers, backing, mount, groups, handles, clocks, full charges, and unknown results remain retained.
The fifth journal SHA-256 is `737d4446eeeb79f63b710f2e418d2148d0a7b962f1556b0abcb1c61f877c10f7`.
Its configuration SHA-256 is `2e2afaf143b8e98d88dada60d1bec20197a52d8b7f0122193d641cf8455a2716`.
Fresh readback confirms all five prior journal hashes and all three current journal FD identities.
It also confirms the original consumed compiler pidfd.
IPv4 forwarding is zero after approved restoration.

The build reader now uses the existing shared strict numeric parser.
Three new regression tests cover padded addresses, overlapping numeric ranges, and retained FDs after a writable mapping refusal.
The focused 18-test suite passes.
Independent current-reader execution passes all 33 retained kernel ranges and exact frozen read-only hashes without another compiler execution.
Both complete source and fresh-wheel suites pass 1161 tests with denied network access, an empty inherited environment, and fresh HOME directories.
There are no skips, failures, or errors.
All 47 wheel package files equal current source.
Ruff and mypy pass for the changed scope and production source.
Nine older script format differences remain unchanged.
The first local wheel build lacked setuptools; the successful build used the exact cached setuptools 80.9.0 wheel.
Neither local wheel command executes a Linux C or AppArmor compiler.

The [build mapping continuation](PHASE-2D-BUILD-MAPPING-CONTINUATION-2026-10-13.md) and [v10 record](qualification/phase-2d-executable-batch-v10-20261013.json) define the pending gate.
The exception requests one new batch, one additional C compiler process, and 48 GiB combined reserved storage each.
It does not resume, reset, or reuse any consumed compiler or installation.
All original actual common and per-batch limits remain unchanged.
The private v18 archive, plan, controller, and fresh actual readbacks remain outside Git.
The complete proposal and record supply exact source, owner scripts, units, commands, and inputs before approval.
Phase 2D remains incomplete at unreleased candidate version 0.13.0.
No commit, push, or Phase 2E work occurred.

### Exact continuation inputs and prompt

Feed AGENTS.md, RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, and the accepted architecture decisions.
Also feed the original October 11 blocker and its exact continuation inputs.
Feed the three accepted source amendments, all dated operational continuations, the build mapping proposal, and the exact v10 record.
Preserve every v3 through v9 operational record as dated evidence.

Continue Phase 2D on the dirty branch from revision 87ed7e6f6c766c7ff2df245ad05569558a9ca3bc.
Preserve all original documentation, dirty work, charges, clocks, timers, handles, and unknown results.
Use ASD-STE100 for every explanation and decision request.
Consume only an explicit approval of the exact v10 reservation, additional compiler exception, and operational batch.
Do not repeat accepted decisions or resume consumed compilers or build admissions.
Perform the exact input preparation, independent readback, original timer, newly authorized build, and actual acceptance sequence.
Pass all twenty original Linux cases twice and cover every enabled native file tool.
Complete actual frozen-candidate acceptance and independent credential-free validation.
Publish only after full Phase 2D acceptance under the explicitly amended authority, then stop.
Record any exact missing capability with fresh evidence. Do not begin Phase 2E.

## October 13: owner decline and retained boundary

The owner answered “Decline the additional batch” to question `call_13eba8afbe454491a9e81b2fe7348450`.
The decision binds v10 record SHA-256 `c3c09e7b4ab8205fe53024ae2718d45e7f279166053a5a0d17c673a063151b2b`.
The exact [decision and fresh readback](qualification/phase-2d-v10-declined-v1-20261013.json) preserve this boundary.
The private decision file records a refusal of operational authority.
No v10 approval file or consumed operational marker exists.
The new guest archive, input directory, storage directory, and observer unit remain absent.
No additional compiler, original observer, timer, charge, login, or live turn started.
Read-only inspection confirms all five prior journal hashes, three current journal FD identities, and the consumed compiler pidfd.
IPv4 forwarding remains zero.
Every original charge and unknown result remains unchanged.
No original handle was closed or original process restarted.
No clock, timer, compiler flag, marker, or installation was reset.

The exact missing authority is the declined 48 GiB reservation and additional C compiler exception.
The source correction remains prepared and verified by both complete 1161-test suites.
The twenty original Linux cases, live frozen-candidate acceptance, and credential-free validation remain incomplete.
The existing 40 GiB allowance permits no additional full charge.
Do not infer approval from the original completion request or the preceding accepted exceptions.
The owner must supply new instructions before any further operational batch.
Do not request the same declined batch again without such instructions.
Phase 2D remains incomplete at unreleased candidate version 0.13.0.
No commit, push, release, or Phase 2E work occurred.

### Exact next-session inputs and prompt

Feed AGENTS.md, RTK.md, HANDOFF.md, DEVELOPMENT-PLAN.md, and the accepted architecture decisions.
Feed the original October 11 blocker and its exact continuation inputs.
Feed all three accepted source amendments and every dated operational continuation.
Feed the build mapping continuation, immutable v10 record, and v10 decline record.
Preserve all earlier batch records and private original custody data.
The private v18 source inputs and all prior consumed markers remain available outside Git.

Read the owner decline record before further Phase 2D work.
Preserve the current dirty branch, source correction, documentation, charges, clocks, timers, handles, and unknown results.
Use ASD-STE100 for every explanation and decision request.
Do not run the declined v10 batch, repeat consumed compiler attempts, or request the same approval again.
Wait for new owner instructions that define any further permitted operational scope.
Phase 2D remains the active milestone; Phase 2E must not start.
If later authorized, complete independently reproducible Linux and live acceptance before publication.
Publish only after full Phase 2D acceptance, then stop.

## October 13: next-session context prepared

The owner requested a next-session prompt and its required files after declining v10.
[The new prompt](PHASE-2D-NEXT-SESSION-2026-10-13.md) preserves that decline and the Phase 2D boundary.
[The exact input manifest](PHASE-2D-NEXT-SESSION-INPUTS-2026-10-13.json) lists current source, tests, accepted decisions, instructions, and dated evidence.
The accompanying public context ZIP supplies those files for a new local session.
The ZIP excludes private capabilities, authentication, keys, retained VM storage, and operational archives.
The prompt grants no further operational authority and does not request the same declined approval again.
Existing dirty source and dated records remain intact.
No additional test, compiler, VM action, charge, provider call, commit, push, or Phase 2E work occurred during context preparation.


## Phase 2D software completion — October 16, 2026

Milestone: Phase 2D software complete; platform and live qualification deferred.
Base revision: `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc`.
Branch: `codex/phase1-architecture`. Version: `0.14.0`.
Delivery revision: the commit containing this ledger entry and the completion report.

This session added checked first-runtime intent preparation and atomic validator capture through existing interfaces.
Separate deterministic external fixtures exercised actual candidate capture, normalization, SQLite state, claims, evidence, verdicts, and recovery.
The workflow preserved original files, dirty bytes, and Git metadata.
Stale approvals, stale definitions, malformed output, forged success, candidate mutation, and failed or missing checks cannot pass.
Cancellation, timeout, refusal, interruption, and restart preserve explicit outcomes without an automatic retry.
The session preserved all earlier Phase 2D source, dated evidence, charges, custody, and unknown results.
It changed only core integration, request validation, new core tests, versions, and publication files.

The final core module passed 26 tests.
The complete source suite passed 1,248 occurrences in 42.034 seconds.
The complete installed-wheel suite passed 1,248 occurrences in 47.172 seconds.
Both suites used fresh HOME directories, empty inherited environments, and network denial.
All 47 installed source files matched the checkout.
Ruff lint, source and test formatting, strict mypy, CLI help, and diff checks passed.
The full formatter check retained nine unchanged historical script differences.
The observed environment was macOS 27.2 arm64, CPython 3.12.15, and uv 0.9.24.

Initial development checks exposed nested transactions, a retained fixture trigger, and an unused import.
The implementation and fixture corrections passed the final complete suites.
The development venv lacks pip; offline packaging used uv and cached pinned dependencies.
[The report](PHASE-2D-SOFTWARE-COMPLETION-2026-10-16.md) records acceptance mapping, exact limitations, and delivery revision lookup.
[The verification JSON](qualification/phase-2d-software-verification-20261016.json) records commands, results, environment, hashes, and preserved-byte checks.

Fixture supervision observations do not qualify platform containment or hard deadline enforcement.
Operational admission remains closed.
No Linux development, VMware, SSH, compiler, qualification batch, exception proposal, credentials, real runtime, model call, or paid host occurred.
No Phase 2E implementation, merge, deployment, or package publication occurred.
Standing instructions authorize this coherent branch commit and push.
Phase 2E software is next; its prompt and exact files are linked in the current state.


## Phase 2E software completion — October 16, 2026

Milestone: Phase 2E software complete; platform and live qualification deferred.
Base revision: `18fa30f5ed28ec78170ee4d73d37378e00017a21`.
Branch: `codex/phase1-architecture`. Version: `0.15.0`.
Delivery revision: the commit containing this ledger entry and the completion report.

The second adapter uses the existing production coordinator, candidate capture, SQLite store, normalization, evidence, and verdict path.
Both role assignments use the same confirmed Python or package-based TypeScript project model.
The reviewer receives a separate frozen copy, actual source diff, task, project model, and captured checks.
The request excludes implementation claims and conversation.
Resolved provider identity must differ when independent review is required.
A different session or runtime label cannot establish independence.
Required review remains blocked when no independent capture exists, including when a generic completion waiver exists.

The risk plan enforces ordinary-risk review and separate high-risk planning approval.
Actual scope escalation remains blocked.
Low-risk work can finish without mandatory review.
Human conflict decisions retain the review, explicit risk acceptance, stopping, and remediation separately.
Authorized remediation creates another candidate and task.
It preserves required checks and requires fresh owner approval, affected checks, and review.
It cannot accept an earlier scope escape or remove required checks.
Claims, captured evidence, decisions, and verdicts remain separate records.
Cancellation, timeout, refusal, malformed output, failure, and restart cannot silently retry work.
The fixtures preserve original files, dirty bytes, and Git metadata.
The coordinator never merges a candidate automatically.

The new module passes 57 tests.
The focused affected suite passes 167 tests.
The Phase 2E and dispatch suite passes 71 tests.
Both complete suites pass 1,305 occurrences, with 1,289 unique methods and 16 existing repeated occurrences.
All 49 installed package files match the source.
Lint, source and test formatting, strict typing, CLI help, and diff checks pass.
The nine historical script format differences match their starting bytes.
The environment is macOS 27.2 arm64 with CPython 3.12.15, uv 0.9.24, and the pinned development dependencies.
[The verification record](qualification/phase-2e-software-verification-20261016.json) supplies exact commands, results, environment, hashes, and limitations.

Development tests reproduced missing-review waiver acceptance, review before check capture, and missing before/after diff data.
The corrected production paths pass their regression tests.
The first complete source and installed runs each failed two old assertions after source binding increased from 42 to 44 files.
The corrected tests require both new modules and preserve the existing admission checks.
A static check also required an explicit type for review termination data.
The final checks pass.
[The completion report](PHASE-2E-SOFTWARE-COMPLETION-2026-10-16.md) maps acceptance conditions and records these failures.

Platform containment, hard deadlines, real provider identity, and live runtime behavior remain unqualified.
The strict Claude stream subset refuses unsupported event types.
Fixture process observations supply no platform proof or execution permission.
Core source changes invalidate older source-bound configurations.
No Linux-specific implementation or C helper bytes changed.
The session made no VMware, SSH, compiler, qualification-batch, credential, provider-inference, paid-model, or paid-host operation.
Historical records, retained charges, custody, and unknown outcomes remain preserved.
The session did not inspect their current physical state.
No Phase 3A implementation, evaluation, merge, deployment, or registry publication occurred.

Next milestone: Phase 3A prepares the frozen comparative evaluation package and unresolved owner decisions.
Feed [the next prompt](PHASE-3A-NEXT-SESSION-2026-10-16.md) and every file in [the exact input index](PHASE-3A-INPUTS-2026-10-16.json).
Complete the standing branch commit and push, then end this session.

## Phase 3A preparation checkpoint — October 16, 2026

Milestone: prepare the comparative evaluation package. Freeze remains blocked; Phase 3A is incomplete.
Base revision: `ae4c6beb2ef2083292863be02cbd6f4ea374478b`.
Branch: `codex/phase1-architecture`. Version: `0.15.1`.
Delivery revision: the commit containing this entry and the Phase 3A preparation report.
The checkout was clean, and every exact starting input hash matched.

The proposed package contains seven manifests, a guide, and a content index.
It records 12 public candidate revisions, root-license digests, source access, observed development prerequisites, and unresolved annotations.
Each stack retains two development candidates and one proposed hold-out.
Four independent synthetic fixtures supplement the real corpus; they do not replace it.
Six task categories and 24 empty sealed-task commitments preserve the planned hold-out shape.
No hold-out source, manifest, test, or task content was inspected.
Only public revision metadata and root licenses were read for hold-out candidates.

B0, B1, B2, and P preserve both role assignments and explicit identity fields.
Live identities, selected baselines, configuration digests, and platform conformance remain unavailable.
The protocol records threshold proposals, ordering seeds, cache treatment, blinded review, failure accounting, and separate usage categories.
The fully crossed planning shapes contain 192 development runs and 576 sealed runs, before optional ablations.
No numerical budget, quota exposure, evaluation execution, or protocol freeze is approved.
[Six concrete owner decisions](PHASE-3A-OWNER-DECISIONS-2026-10-16.md) state the missing choices and evidence.

The new acceptance module passes 14 tests through existing interfaces.
The focused package, Phase 2E, and dispatch command passes 85 tests:
`rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_3a tests.acceptance.test_phase_2e tests.acceptance.test_phase_2d_dispatch`.
Source and fresh installed-wheel suites each pass 1,319 occurrences, with 1,303 unique methods and 16 existing repeats.
Both suites use empty inherited environments, fresh HOME directories, and process-level network denial.
All 49 installed package source files match. Offline build, install, CLI help, lint, source/test formatting, typing, and diff checks pass.
The final data-only review changes pass 14 focused checks in both source and installed environments.
The first package check exposed one incorrect fixture label and two missing synthetic qualification IDs.
Fixture corrections pass without changing production behavior.
The nine historical script format differences retain their starting bytes.

The environment is macOS 27.2 arm64, CPython 3.12.15, uv 0.9.24, and the pinned development dependencies.
[The preparation report](PHASE-3A-PREPARATION-2026-10-16.md) maps delivered preparation and remaining gates.
[The verification record](qualification/phase-3a-preparation-verification-20261016.json) supplies exact commands, exits, output hashes, package identity, and limitations.
The initial evaluation plan, operational code, Linux source, C helper, historical records, charges, custody, and unknown outcomes remain preserved.
Only the synchronized package version changes inside production source.
The session did not inspect current physical custody or access credentials or private artifacts.
No Linux development, VMware, SSH, compiler attempt, real coding runtime, provider inference, paid model, or paid host operation occurred.
No calibration, sealed evaluation, infrastructure provisioning, merge, deployment, or registry publication occurred.
Operational execution admission remains closed under ADR 0007.

Continue this same Phase 3A milestone with [the continuation prompt](PHASE-3A-CONTINUATION-2026-10-16.md).
Feed every file in [the exact continuation index](PHASE-3A-CONTINUATION-INPUTS-2026-10-16.json).
The smallest missing decision assigns independent corpus engineers, adjudication, and sealed-task custody.
Owner decisions cannot replace missing independent task or baseline and platform conformance evidence.
Complete the standing branch commit and push, then stop before Phase 3B.

## Phase 3A complete — October 18, 2026

Milestone: freeze the comparative source evaluation package under accepted ADR 0008.
Base revision: `e3457ee0218d1a16d16f1a4a07f363f99454c65f`. Branch: `codex/phase1-architecture`. Version: `0.15.2`.
The delivery revision is the commit containing this entry, completion report, and exact next input index.
The starting checkout was clean. All 1,095 starting tracked files were inventoried.

The owner explicitly approved agent annotation, bounded source-package selections, and zero evaluation spending.
Two independent agent contexts completed source annotations before reading each other's records.
The separate custodian prepared and verified 24 sealed tasks without exposing contents to development authors or the parent.
The package retains twelve pinned public sources and all four stacks.
Development adjudication records 120 field decisions across eight repositories and 822 verified citations.
Both source inventory serializations reproduce their digests for all 2,264 development entries.
Independent task review verified 128 source and scope citations.
Private adjudication binds eight original records, 60 field decisions, and 688 evidence references.
The sealed task artifacts contain 272 files and 245,463 bytes. The private integrity manifest binds 763 entries.
The public index binds 23 artifacts and exposes no sealed requirements, paths, or oracle code.
Private custody uses `private-store:phase3a-20261016/sealed/v1`; Git does not back it up.
Files use `0600`; directories use `0700`. Retention requires an explicit later disposal decision.

B0, B1, pinned Orka B2, and P preserve both role assignments.
Selected CLI distributions, requested providers/models, configurations, and toolchains are fixed.
Future actual candidates, project models, executables, effective settings, and resolved identities remain explicit admission observations.
The protocol fixes thresholds, scoring, cache treatment, blinding, repetitions, ordering, paired analysis, and failure accounting.
All 192 development and 576 sealed planned units remain represented.
The primary model overhead metric estimates API-equivalent cost. Actual billing, subscription quota, and unknown usage remain separate.
Twenty fresh deterministic Orka source tests pass; historical native exclusion failures remain failed.
Native execution, dependency resolution, provider behavior, and platform conformance remain unavailable.
Agent reference annotations establish neither human ground truth nor cross-provider independence.
Swift and .NET discovery support remain unavailable. No unsupported unit disappears from planned coverage.
The original initial evaluation plan, proposed package, and prior completion records remain unchanged.

All 23 new package checks pass. The focused package, Phase 2E, and dispatch command passes 108 tests.
Source and fresh installed-wheel suites each pass 1,342 occurrences: 1,326 unique methods and sixteen inherited repeats.
All 49 installed source files match. Offline build, hash-locked install, CLI help, lint, formatting, strict typing, and diff checks pass.
Both complete suites use empty inherited environments, fresh HOME paths, and process-level network denial.
Nine historical script format differences remain byte-identical.
Eight independent review findings were corrected and verified. Initial fixture errors remain recorded in verification.
[The completion report](PHASE-3A-COMPLETION-2026-10-18.md) and [verification record](qualification/phase-3a-freeze-verification-20261018.json) supply exact evidence and limitations.

Only the synchronized version changed inside production source. All other starting source and historical files remain intact.
All 28 Linux and C source files match their starting bytes. Historical physical custody was not inspected.
No credential, private predecessor, VM, SSH, compiler, coding-runtime, evaluation inference, or paid-host operation occurred.
No calibration, sealed evaluation, infrastructure provisioning, merge, deployment, or registry publication occurred.
Operational admission remains closed under ADRs 0007 and 0008.
The approved evaluation allowance remains zero money, zero quota, and zero paid-host spending.
Agent-session subscription usage was not measured and remains unknown.

Next milestone: Phase 3B development calibration and prospective protocol corrections.
Its execution requires separate owner spending approval and an explicit instruction to resume required qualification.
Use [the Phase 3B prompt](PHASE-3B-NEXT-SESSION-2026-10-18.md) and [exact input index](PHASE-3B-INPUTS-2026-10-18.json).
Do not reopen Phase 3A because later execution gates remain closed.
Complete the standing commit and push, then stop before Phase 3B work.
