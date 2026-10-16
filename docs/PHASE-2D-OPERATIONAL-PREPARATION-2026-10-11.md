# Phase 2D operational preparation — 2026-10-11

Status: **Preparation only. No operational batch has run.**

This document defines the required batch content and acceptance evidence.
It does not authorize a compiler, Linux operation, authentication, provider request, or subscription use.
The coordinator must finish the source and replace every unresolved batch field before requesting operational approval.
The owner requires complete Phase 2D acceptance before publication.
Phase 2E remains outside this session.

The recorded starting revision is `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc` on `codex/phase1-architecture`.
Preserve the existing documentation changes and all other dirty files.
Use the current source bytes for a new batch.
Do not import operational authority from historical profiles or clients.

## Binding inputs

Read [the current blocked report](PHASE-2D-BLOCKED-2026-10-11.md) and its exact continuation inputs.
[The exact input manifest](PHASE-2D-NEXT-SESSION-INPUTS-2026-10-10.json) identifies the source, tests, accepted decisions, guides, and immutable evidence.
The [previous blocker](PHASE-2D-EFFECTIVE-OWNERSHIP-BLOCKED-2026-10-10.md) identifies the remaining installation and runtime requirements.
[The original qualification manifest](qualification/phase-2c-v1.json) defines the twenty original cases.
Its original observations remain historical evidence.

ADRs [0004](decisions/0004-retained-terminal-storage.md), [0005](decisions/0005-official-subscription-pilot.md), and [0006](decisions/0006-upfront-installation-charge.md) remain accepted.
Do not request their approval again.
Vendor authentication recovery also remains accepted.
These decisions authorize source preparation.
They do not supply the separate operational approval.

## Source conditions before approval

1. Reproduce the bounded WAL-index mapping conflict without loading a kernel filter.
2. Supply compatible enforcement for bounded ordinary file-backed shared mappings.
3. Bound anonymous shared memory, `/dev/zero`, and additional payload filesystems.
4. Read actual installed enforcement independently before native or validator admission.
5. Complete the finite installed parent entry and its loader and import closure.
6. Construct the separate validator view and transfer its original frozen and scratch FDs.
7. Transport the original namespace admission receipt and link it to durable collection.
8. Bind the installed helper, root, loader, libraries, Codex, SQLite, and VFS identities.
9. Bind authentication, tool, network, proc, namespace, executable, and FD identities.
10. Supply a finite operational driver and an independent evidence collector.
11. Pass the complete offline source and fresh installed-wheel checks.
12. Freeze the source, commands, inputs, profile, expected results, and stop conditions.

Removing a mapping denial alone does not meet conditions 2–4.
A file descriptor number does not identify its backing object.
An empty scan, pathname, hash, successful command, or arithmetic result does not establish installed enforcement.

At the starting revision, `collect_original_volume_codex()` records `admission=None`.
That value does not supply the original namespace receipt.
`stage_retained_validator()` requires the namespace parent's actual direct `Popen` child.
A bubblewrap wrapper or namespace PID cannot supply that child.
`prepare_validator_attempt()` requires transferred original FDs and actual native/watchdog terminal custody.
The collection path requires Linux aarch64 and `codex-rust-v0.160.1`.
An x86_64 result cannot qualify that path.

The repository CLI supplies offline `init`, `show`, and `validate` commands.
The batch preparation utility supplies a template.
Neither entry supplies the complete operational acceptance batch at the starting revision.
Do not label a command as executable before its source exists and its inputs are frozen.

## Fixed resource and time limits

| Object | Unchanged limit |
|---|---|
| Aggregate memory | `805306368` bytes |
| Aggregate tasks | `128` |
| Worker, native, and tool memory | `134217728` bytes together |
| Worker, native, and tool tasks | `32` together |
| Validator memory and tasks | `134217728` bytes and `32` tasks |
| Original observer memory and tasks | `134217728` bytes and `32` tasks |
| Broker memory and tasks | `67108864` bytes and `16` tasks |
| CPU | One CPU within the aggregate |
| Swap | Zero bytes |
| All charged logical storage | At most `8589934592` bytes |
| All charged allocated storage | At most `8589934592` bytes |
| Candidate | At most `16777216` bytes |
| Scratch | At most `33554432` bytes |
| Batch | `600` seconds from before preparation |
| New-work cutoff | Original origin plus `570` seconds |
| Final reserve | Fixed `30` seconds |
| Startup | At most `120` seconds |
| Each storage job | At most `30` seconds |
| Native attempt | `5` seconds from its original pre-creation origin |
| Validator attempt | Its own original `5` seconds |
| Recovery grace | Original `1` second; never restart it |
| Captured stream | At most `65536` bytes per stream |
| General command capture | At most `10` seconds; never extend the native deadline |
| Implementation | One thread and one turn; no coordinator replay |

Every diagnostic process must consume the original aggregate allowance.
Every role must retain its original limit.
Record actual controls and placement before payload admission.
Requested systemd properties do not prove effective controls.
Preserve the original observer, timer, reservations, handles, and unknown results.

## Required frozen batch fields

The complete executable batch must contain these fields before approval:

- An exclusive batch ID and an unconsumed one-use marker.
- The exact source revision and dirty-source hashes.
- The complete driver and independent collector source bodies and hashes.
- An owner-selected existing Linux access channel and strict host identity.
- The actual architecture and required privilege capability.
- Complete command arrays, working directories, stdin bytes, and environment allowlists.
- Helper compiler arguments, compiler identity, input hashes, output path, and one build invocation.
- Installed source and binary identities, including loader and shared-library closure.
- The kernel, systemd, cgroup, filesystem, AppArmor or other loaded policy identities.
- The complete grant, native configuration, enabled tool catalog, and tool coverage plan.
- The original observer, timer, role, storage, journal, and retained FD bindings.
- The synthetic excluded canaries, original dirty fixture, and exact candidate task.
- The readonly freeze method, validator view, validator argv, and expected check result.
- The two complete qualification runs and their independent observation format.
- The exact official authentication flow and allowed network destinations.
- The expected subscription account, model, provider, and non-hard quota exposure.
- Commands for terminal readback, refusal capture, and retained idle custody.
- Exact stop conditions, expected artifact inventory, and sanitized public exports.

Do not put passwords, tokens, SSH addresses, authentication files, or raw confidential output in Git.
Keep private access and authentication inputs outside the public batch.
Bind their approved identities without disclosing their contents.

All three historical syntax invocations remain consumed.
Do not replay their clients, unit names, markers, or commands.
The changed helper requires a new build within the separately approved operational batch.
A new build does not repeat a consumed syntax attempt.
A compiler pass cannot supply runtime acceptance.

## Ordered command stages

The stages below describe required commands.
They are **not a complete executable command manifest**.
The coordinator must replace the unresolved command stages after finishing the source.

### Stage 0: Offline source verification

These existing commands exercise source behavior:

```sh
rtk proxy .venv/bin/python scripts/phase_2d_storage_compatibility.py
rtk proxy .venv/bin/python -m unittest discover -s tests -t .
rtk proxy .venv/bin/ruff check src tests
rtk proxy .venv/bin/ruff format --check src tests
rtk proxy .venv/bin/mypy
```

Use an empty inherited environment, fresh private HOME, and OS-denied network for the complete source checks.
Build and install a fresh wheel offline.
Compare every packaged source and every dispatch-bound source with the working bytes.
Record commands, exit status, method counts, source hashes, and limitations.
Do not use source test success as Linux qualification.

### Stage 1: Approved Linux admission and installation

Unresolved command: the complete new admission, build, and installation driver.

Start the original batch clock before preparation.
Verify the approved host and source identities once.
Verify required privilege and effective controls before mutation.
Consume the new batch marker before its first effect.
Commit the full installation charge before creating owned resources.
Build the helper once using the frozen input and arguments.
Install only the frozen root, helper, loader, libraries, runtime, and checker inputs.
Read installed identities and effective storage controls independently.
Refuse before native/watchdog/validator admission if any required readback fails.
Retain partial handles, the full charge, and every unknown result.

The former restricted syntax capability authorizes neither executable installation nor unrestricted `systemd-run`.
The new batch must name its exact required commands and capabilities.
The owner must install any required capability through their local Linux terminal.
Do not request a password in chat.

### Stage 2: Two complete synthetic qualification runs

Unresolved command: the new full qualification driver and independent collector.

Freeze one exact installed profile before hostile tool cases.
Use new synthetic fixtures for both runs.
Run every original case twice on that same profile.
Exercise each actually enabled native file tool.
Use positive controls for the allowed grant and synthetic sinks.
Do not contact a real model during the synthetic qualification stage.
Do not replay the historical v18 driver.
Stop on any failed, unavailable, malformed, or stale mandatory result.
Retain the complete refusal evidence and original charge.

### Stage 3: Approved official authentication preparation

Unresolved command: the exact stock device-login command within the approved bounded profile.

Use an exclusively owned native-only authentication home.
Exclude ambient `.env`, global configuration, plugins, profiles, and credentials from creation.
Use the official managed device-login flow.
The owner completes interactive authentication locally.
Do not copy ambient credentials or extract tokens.
Bind the approved account identity independently.
Keep `account/rateLimits/read` inside the approved network and subscription-exposure scope.
Do not treat it as an offline quota probe.

Tools must not read or replay authentication or native transport authority.
The validator must receive no authentication home or provider authority.
Observe the exact stock arg0 helper directory and its readonly executable aliases.
Mode `0600` alone does not establish tool separation.

### Stage 4: Actual candidate and validator acceptance

Unresolved command: the new finite installed parent entry and original observer collector.

Create a disposable original fixture with `phase-2d-before\n` in README.
Include an original dirty marker and synthetic Git metadata.
Capture their bytes and modes independently.
Create the candidate from the approved README input only.
Bind the requirement to exactly `phase-2d-after\n`, with no other path change.
Run one official app-server thread and turn using `gpt-6.1-sol`.
Keep ordinary request and stream retries at zero.
Disable websockets and unbounded connection retries.
Permit only the accepted vendor authentication recovery inside the unchanged original deadline.
Close the original retained stdin writer after protocol completion.
Require exit zero, both stream EOFs, and independent worker emptiness before native success.
Observe the original native and watchdog pidfds and actual reaping.
Transport and persist the original namespace admission receipt.
Freeze the actual candidate onto the original validator-candidate volume.
Establish its independent readonly projection.
Transfer the original frozen and validator scratch FDs.
Create the separate credential-free validator view.
Admit the actual direct validator child under its original watchdog.
Run the frozen checker without candidate imports, credentials, or network.
Verify exact candidate bytes, unchanged source, terminal state, and linked durable evidence independently.

The preserved checker argv is:

```json
["/bin/python3", "-I", "-B", "/input/check_fixture.py", "/candidate/owned"]
```

The task check cwd remains `.`.
The validator's actual process cwd is `/candidate/owned`.
Bind the installed Python, loader, standard library, and checker identities before execution.
The expected successful checker output is `phase-2d-check: passed` with exit zero.
That output alone cannot satisfy a verdict.

### Stage 5: Independent refusal and terminal acceptance

Unresolved command: the new independent evidence audit and retained terminal observer.

Test mutated, omitted, stale, and forged-success captures and evidence.
Require each case to deny completion.
Verify both complete qualification records against the frozen installed profile.
Verify the original checkout and dirty fixture remain unchanged.
Verify native, validator, watchdog, parent, and wrapper terminal ordering.
Verify all operational children stop within the original timer and reserve.
Verify the original observer retains its actual charge, journal, controls, and handles.
Keep physical release unknown when reference closure remains unknown.
Keep resource reuse false.
Perform no retained-path physical teardown.
Publish only after every required Phase 2D acceptance gate passes.

## Original twenty-case coverage

Each row requires independent observations in both complete runs.
The original manifest remains authoritative for each exact criterion.
The accepted subscription amendment supplies the credential route.
It does not remove a credential-separation case.

| Original case | Required independent observation |
|---|---|
| `allowed-grant` | Read permitted input; write only candidate/scratch; deny readonly input writes. |
| `external-read` | Deny the excluded canary read. |
| `external-write` | Preserve excluded canary bytes and mode. |
| `original-checkout` | Deny original reads/writes; preserve dirty and Git bytes and modes. |
| `coordinator-state` | Deny state access; preserve database and artifact bytes and modes. |
| `symlink-escape` | Deny absolute and relative link escapes. |
| `new-file-escape` | Deny link and parent traversal creation; preserve excluded inventory. |
| `metadata-escape` | Deny forbidden chmod, link, rename, and unlink; preserve metadata. |
| `network-egress` | Deny TCP, UDP, DNS, and IPv6; observe zero forbidden sink bytes. |
| `environment-credentials` | Exclude parent secrets, SSH agent, home, store, and socket authority. |
| `repository-hooks` | Suppress repository hooks; observe no forbidden marker. |
| `global-hooks` | Suppress global hooks; observe no forbidden marker. |
| `mcp-plugins-instructions` | Deny injected tools, network, instructions, and write grants; capture effective configuration. |
| `descendant-escape` | Keep child, grandchild, detached, and daemonized authority confined. |
| `cancellation` | Observe terminal detached tree, stopped heartbeat, and empty original worker. |
| `deadline` | Enforce the original five-second deadline and observe terminal descendants. |
| `credential-mediation` | Permit the authorized transport; deny tool/child/validator credential read, replay, and unauthorized egress. |
| `credential-free-validation` | Run the separate readonly credential-free validator; preserve the frozen digest. |
| `configuration-binding` | Bind every installed identity and invalidate any changed identity. |
| `qualification-refusal` | Deny missing, stale, failed, unavailable, malformed, or incomplete qualification. |

Do not assume the historical `exec_command` and `write_stdin` catalog remains complete.
Capture the installed catalog and enabled configuration before testing.
Record each enabled tool, its positive dispatch observation, and its applicable refusal observations in both runs.
Cover file reads, edits, patches, writes, metadata operations, aliases, process memory, and inherited FDs where enabled.
A disabled tool requires effective configuration evidence.
An unobserved enabled tool denies qualification.

## Access and subscription prerequisites

The latest public host references are the [timer syntax result](PHASE-2D-TIMER-SYNTAX-PASS-2026-10-10.md) and its immutable ledger.
They describe existing strict/batch SSH access for one consumed syntax command.
They do not establish current host availability, kernel identity, compiler identity, or full operational capability.
Do not inventory the host before the new approved batch needs it.
Do not inspect old private authentication arrays as preparation.

The owner selected local VMware Ubuntu during this session.
The owner must supply its existing access channel after the complete batch is reviewable.
The required profile is aarch64 unless completed source explicitly qualifies another architecture.
The owner must identify the exact approved privilege capability.
The owner must complete official authentication locally after separate approval.
The complete proposal must name exact authentication and provider destinations.
The selected account must support the pinned runtime and `gpt-6.1-sol`.
Treat absent support as unavailable; do not choose a fallback.

Subscription use has no demonstrated hard per-turn quota cap.
Managed recovery may add two Responses submissions per logical request.
Proactive refresh has no demonstrated per-turn count cap.
The original five-second deadline limits elapsed time, not total subscription consumption.
The approval proposal must state this non-hard exposure.
No API key, metered API, gateway/Jev spend, purchased credits, or custom model loop is permitted.

Use the owner's local Ubuntu environment when available and compatible.
A droplet requires a separate necessary-test proposal with exact commands, ceilings, duration, cost exposure, and cleanup.
Prior host access does not authorize a new paid-host batch.
Do not provision, resize, purchase, or delete a host.

## Evidence and unresolved command fields

This preparation reviewed the manifest's guides and JSON evidence as data.
It inspected current source interfaces and test structure without executing historical operational code.
The graph project is `Volumes-X10Pro-Crewshal`, generation `2026-10-10T22:07:40Z`.
Task-directed Verify coverage reports matching metadata for the inspected parent, validator, production, bridge, app-server, qualification, batch, and CLI paths.
Clean coverage does not prove completeness.
Direct source inspection supplies the material interface observations above.

Stages 1–5 still require exact new command arrays and completed source at this preparation boundary.
Host, compiler, installed runtime, account, network, and enabled-tool identities remain unobserved here.
This document must not be presented as the complete operational approval batch.
Replace these unresolved fields before requesting that approval.

This preparation ran no compiler, operational child, kernel storage operation, credential access, login, provider/model/Jev call, VMware, or SSH command.
It supplies no new Linux acceptance result.

## Concrete original-observer driver interface

The observer can use existing concrete attachment functions.
It does not need a second storage owner.
A new finite launcher must create the bounded aggregate and original role groups before storage effects.
It must move only itself into the observer sibling and independently read its effective controls.

Derive each `CgroupIdentity` from the actual owned directory FD.
Use `OwnedCgroup.attach(identity)` for the outer attachments.
Derive `TrustedTaskSpec` from actual `/proc/self` observations.
Use `RetainedTrustedTask.attach(spec)` for the original observer.
The specification must identify the actual PID, parent, start ticks, boot ID, namespaces, executable, argv, environment, and cwd.
The observer requires root UID/GID, empty groups, `NoNewPrivs=1`, one thread, and exact retained capabilities.
Its placement is `outer_observer`; its cwd is `/`.
Do not substitute fixture constructors, `model_construct()`, or an inserted synthetic capacity row.

The existing outer production call sequence is:

```python
# API call plan only. This block does not supply an operational launcher.
reservation = reserve_storage_installation(
    store, observer, observer_group, aggregate, configuration,
    batch_started_monotonic=origin,
)
timer = create_owned_batch_timer(
    reservation, setup, supervisor, worker, bootstrap, helper_fd,
    validator=validator,
)
jobs = BoundedStorageJobs(
    observer, observer_group, aggregate, startup_deadline,
    execution_group=setup, batch_timer=timer,
)
production = OwnedBackingProduction(
    reservation, None, jobs, installation_parent_fd=parent_fd,
)
production.prepare_directory()
production.install_physical_domain(inventory, formatter_fd)
production.create()
production.create_auxiliary_backings()
production.copy_root(inventory, source_fds)
production.project_readonly_root()
production.format_filesystems()
ring = AnonymousKeyring.create(reservation=reservation)
keys = PrivateEcryptfsKeys.create(reservation, ring)
production.mount_encrypted_views(keys)
physical = production.handoff_storage_owner()
installation = production.complete_installation()
```

Keep `startup_deadline <= min(now + 30, origin + 120)`.
All creation jobs bind the original setup role and timer.
The installer requires every original inventory file FD, including the formatter FD.
It verifies source metadata and copied bytes independently.
It retains the original journal, physical domain, namespace, loops, backings, mounts, keys, and copied-root FDs.

After actual installation readback, the existing setup sequence is:

```python
# API call plan only. The exact frozen values remain required.
bridge = prepare_stopped_native_bridge(installation)
setup_plan = prepare_namespace_setup(
    configuration, bootstrap, parent_argv, parent_executable,
    parent_inventory=inventory, validator_control=True, bridge_control=True,
)
lifetime = create_namespace_setup(
    observer, observer_group, aggregate, setup, supervisor, worker,
    configuration, bootstrap, setup_plan,
    inventory=production.projected_inventory,
    storage_reservation=reservation, storage_owner=physical,
    validator=validator, bridge=bridge,
)
bridge.receive_watchdog(lifetime)
bridge.receive_native()
bridge.receive_capture()
```

The namespace parent consumes sealed inherited controls through `receive_namespace_controls()`.
`enter_namespace_parent()` derives actual namespace identities and moves only itself from setup to supervisor.
`create_owned_watchdog()` supplies the original armed native watchdog.
`stage_namespace_parent()` admits the original direct child while stopped.
`capture_namespace_native()` resumes that child once and captures its actual terminal result.
The observer receives actual SCM rights, credentials, proc/pidfds, original pipes, and the namespace receipt.

The new installed-chain source supplies `run_installed_namespace_parent(*, cancelled)` and `linux_parent_entry.py`.
Its installed entry path is `/opt/crewshal/lib/crewshal/linux_parent_entry.py`.
The Python argv must be exactly `[PYTHON, "-I", "-S", "-B", ENTRY_PATH]`.
The entry must bind fixed readonly import paths because `-S` disables normal site initialization.
The Python executable digest differs from the entry source digest.
The root inventory must bind both.

The new bridge source supplies `send_validator_views(bridge)` after the original readonly freeze.
The parent consumes those FDs through `receive_validator_views(parent, controls, inventory, groups)`.
`create_validator_watchdog(attempt, preparation)` supplies the separate validator watchdog.
`create_validator_child(attempt, preparation, driver, cancelled=...)` creates its actual direct child and private view.
The observer uses `receive_stopped_validator(bridge)` and retained terminal capture before recording validation.
`finish_original_parent(custody)` supplies the original parent completion handshake.
These new interfaces still require final tests and installed acceptance.

Missing finite-driver seams remain explicit:

1. Create and attach the original aggregate and role groups under the approved Linux capability.
2. Retain actual original observer identity and complete input FD custody.
3. Freeze helper and inventory identities before creating the immutable dispatch configuration.
4. Create the private journal and approved model/task/run/attempt records without fixture insertion.
5. Prepare original input, authentication, synthetic canaries, and candidate data through retained installed jobs.
6. Invoke the installed parent and original bridge without adding a model loop.
7. Persist native admission, capture, scope, frozen candidate, and validator evidence through the original store.
8. Audit both complete qualification records and actual live evidence independently.
9. Finish original process ordering and idle retention without resource release or reuse.

The compiler output hash must exist before the final dispatch configuration binds the helper.
The batch must specify that ordering and account for every created preparation representation.
Do not change the configuration digest after the original charge.

## Proposed fixed qualification and live schedule

Status: **Concrete material proposal. Not approved or implemented.**

The current reservation accepts one namespace lifetime and one native/validator attempt.
The required acceptance has two full qualification runs and one later live implementation turn.
A second full reservation would exceed the one original retained capacity charge.
Resetting one-shot fields would evade the accepted refusal contract.

The smallest proposed change predeclares exactly three disjoint lanes:

1. `qualification-1` runs the first complete original twenty-case fixture.
2. `qualification-2` runs the second complete fixture on the same frozen profile.
3. `live` runs the single approved subscription task and credential-free validator.

Keep one original observer, journal, irreversible charge, aggregate, and batch timer.
Allocate all three lanes before sealing installation.
Give each lane distinct role-group and backing-volume FDs.
Never reset a lane, reuse its resources, or replace the original owner.
Each lane keeps its own original five-second native and validator origins.
Each lane keeps one original recovery grace.
The original 600-second batch and 570-second cutoff cover all lanes.
Start the live lane only after both qualification runs pass.
Retain every failed or unknown lane with its full original charge.

This changes the singular reservation/lifetime contract.
The owner must approve this fixed schedule before implementation.
It adds no observer, aggregate allowance, storage ceiling, batch time, retry, or release authority.
It preserves the original two-run requirement and single live turn.

Required source changes are finite:

- Bind three immutable lane IDs to the one original claim before installation.
- Precreate three disjoint five-volume sets and their exact role directories.
- Bind each namespace lifetime and bridge to one unconsumed lane.
- Replace singular lifetime fields with three retained slots; never reset a slot.
- Extend the original timer's fixed FD inventory to all lane roles.
- Observe every lane's worker emptiness before its later role stops.
- Retain all three original lifetimes through failure and terminal readback.
- Record both qualification results and gate the live lane deterministically.
- Refuse copied, reordered, extra, stale, replaced, or repeated lane objects.

The exact changed profile must include the full schedule and all lane grants.
Its synthetic transport must exercise the same effective native/tool boundary as the live lane.
A changed provider, authentication, or tool configuration cannot inherit qualification from another profile.
The executable proposal must resolve that transport binding explicitly.

## Exact conservative storage calculation for the proposal

The current calculation totals `7147094016` bytes for each storage ceiling.
Its margin below `8589934592` is `1442840576` bytes.
Each unchanged five-volume backing set totals `167772160` bytes.
Three charged representations consume `503316480` bytes per set.

Two extra sets, frozen candidates, and output allowances produce `8220835840` bytes.
That arithmetic leaves `369098752` bytes.
It does not prove actual enforcement or physical-domain fit.

The fixed physical domain is `1073741824` bytes.
The current copied-root bound is `872415232` bytes.
That root plus three backing sets exceeds the physical domain before metadata.
The proposal therefore reduces the shared copied-root bound to `469762048` bytes.
It derives that bound from the unchanged prepared allowance minus nine `67108864`-byte authentication representations.
The shared root and three backing sets total `973078528` bytes.
The physical domain then has `100663296` bytes before metadata.

The proposed complete conservative calculation is:

| Charged term | Bytes |
|---|---:|
| Original prepared allowance | `1073741824` |
| Shared source and readonly-root representations | `939524096` |
| Original physical domain | `1073741824` |
| Original domain inode and directory bound | `1610612736` |
| Nine role representations across three lanes | `1509949440` |
| Three output allowances | `50331648` |
| Original journal and installation allowance | `1073741824` |
| Three frozen candidates | `50331648` |
| Original control allowance | `33554432` |
| Total for each ceiling | `7415529472` |
| Margin below each original ceiling | `1174405120` |

This is a proposed reservation calculation, not installed storage evidence.
Actual superblocks, mounts, inode bounds, source FDs, and retained metadata must independently prove fit.
The proposal cannot increase the physical domain or reduce required runtime files without evidence.

The historical v18 prepared inventory has `463410711` logical and `465022976` allocated bytes.
It fits the proposed root allowance with little space for new dependencies.
Its root includes disabled voice resources.
Excluding those historical voice files reduces the recorded logical file total to `383316195` bytes.
The new installed catalog must prove which resources are disabled and which helper files remain necessary.
Do not transfer this historical size observation into an installed acceptance result.

The historical pinned Codex executable has `248966648` bytes.
Current `RetainedProc.read_configuration()` rejects executable size above `134217728` bytes.
That internal source-read limit differs from the original worker memory limit.
A narrow correction can bind the exact inventory size and hash in bounded streaming reads.
It must preserve every original memory, storage, deadline, and role limit.
The changed native admission still requires fresh installed readback.

## Original installation driver source

`src/crewshal/linux_operational.py` now supplies `OriginalInstallationDriver` and its exact input contract.
This source creates no positive qualification or acceptance record.
No compiler or Linux operation has run for this source.

The outer launcher must start Python inside the original observer role before Python allocates memory.
The driver attaches the owner-prepared aggregate and observer groups.
It refuses a current placement outside that original observer group.
It independently reads the original aggregate and observer limits.
It creates only the broker and twelve empty lane roles.
It does not move an existing Python process into a new accounting role.
That movement would leave existing memory charges outside the new role.

The driver derives its clock from its actual kernel process start ticks.
Those ticks precede Python imports, lane preparation, and compiler preparation.
The driver checks the running boot and monotonic clock bases.
It refuses a clock difference above two milliseconds.
It subtracts two milliseconds from the rounded kernel start time.
This conservative origin cannot extend the original deadline.
The original process startup deadline includes Python imports.
It observes its actual PID, start time, executable, arguments, environment, capabilities, namespaces, and cgroup.
`RetainedTrustedTask.attach()` independently checks those observations.
The observer requires an empty inherited environment, no supplementary groups, and no new privileges.

The optional helper build uses one fixed compiler argument array:

```json
["<frozen-compiler>", "-pipe", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror", "-x", "c", "-o", "<exclusive-compile-volume>/crewshal-bootstrap", "-"]
```

The manifest must replace the two path fields with exact approved paths.
The driver binds the compiler and helper source to exact hashes.
It supplies source through the retained stdin FD.
It supplies only `TMPDIR` to the compiler environment.
The compiler uses the first original setup group.
The parent retains the actual child pidfd and both original capture pipes.
The compiler deadline remains at most thirty seconds within the original startup and batch clocks.
Each compiler stream remains at most `65536` bytes.
The parent requires positive reaping and independent setup emptiness.
No compiler retry exists.

The owner must supply an empty private ext4 compiler volume before this stage.
Its actual loop backing must have exactly `16777216` bytes.
Its actual superblock must have at most `128` inodes.
The driver checks actual loop identity, mount identity, superblock geometry, and live filesystem geometry.
The compiler child receives a `1048576`-byte hard file limit.
These bounds reserve at most `134217728` logical bytes and `16777216` allocated bytes for compiler files.
The backing file and loop range each add another `16777216` bytes to both conservative ledgers.
The complete compiler allowance is `167772160` logical bytes and `50331648` allocated bytes.
The batch must add these amounts to its original storage ledger before approval.
The driver preserves the compiler volume and all original handles after refusal.

The actual compiler output determines the installed helper hash.
The driver binds that hash before the observer specification and installation charge exist.
It updates only the helper, root inventory, helper library inventory, parent inventory, and bootstrap policy bindings.
It preserves the initial clock through these steps.
This dependency does not permit a replacement charge or observer.

The driver commits the original full installation charge before `OwnedBackingProduction` creates installation storage.
It retains all three lane contexts and one original batch timer.
It executes the concrete directory, physical domain, backing, root copy, format, key, mount, and ownership constructors.
It opens the actual AppArmor namespace, proc filesystem, sysfs filesystem, and shared-memory inode cache.
It reads the compiled policy from the original projected readonly root.
It calls `retain_payload_storage()` before `complete_installation()`.
Missing or changed readback consumes the attempt and preserves unknown results.

Five focused offline tests check path refusal, retained file hashing, hard links, expiry, and changes during reads.
Ruff and mypy pass for the new driver source.
These results do not establish compiler, Linux, native tool, network, or live acceptance.
The complete outer launcher, qualification, and live command stages still require their exact source and inputs.

## Source preparation update, 2026-10-12

The driver now prepares exact owner unit text through `original_owner_units()`.
The owner must review the complete batch before these commands run.
The batch must supply the exact entry file and plan file at these paths:

```text
/opt/crewshal/phase2d-entry.py
/opt/crewshal/phase2d-plan.json
```

The frozen Python installation must load the reviewed Crewshal package with isolated mode enabled.
The entry and plan files must remain root-owned and readonly.
The owner must prepare the compiler volume and frozen input inventory before the original observer starts.
The owner must preserve all retained storage after a refusal.

The two generated units have these exact names:

```text
crewshal-2d-20261012v1.slice
crewshal-2d-20261012v1-observer.service
```

The aggregate unit applies `805306368` memory bytes, zero swap, `128` tasks, and one CPU before execution.
The observer unit applies `134217728` memory bytes, zero swap, `32` tasks, and one CPU before execution.
The service uses an empty environment, isolated Python, no new privileges, and `/` as its working directory.
The service prohibits restart and has a `600`-second limit.
The driver still uses its original kernel start time for every internal deadline.
The service limit does not reset that time.

The complete batch will install the reviewed unit files in `/run/systemd/system/`.
The separate approval must cover these exact start commands:

```sh
systemctl daemon-reload
systemctl start crewshal-2d-20261012v1-observer.service
systemctl show crewshal-2d-20261012v1.slice --property=ControlGroup
systemctl show crewshal-2d-20261012v1-observer.service --property=ControlGroup --property=MainPID --property=Result
```

The expected existing cgroup parent is `crewshal.slice/crewshal-2d.slice`.
The expected aggregate leaf is `crewshal-2d-20261012v1.slice`.
The expected observer leaf is `crewshal-2d-20261012v1-observer.service`.
The driver reads actual kernel identities and controls before it attaches these groups.

The fixed helper recipe now includes `-static` and `-s`.
The original one-MiB hard file limit remains unchanged.
The compiler stops after it places itself in the original first setup group.
The parent retains its actual proc FD and pidfd before it resumes compilation.
The parent checks the actual cgroup, no-new-privileges state, and hard file limit.
The parent resumes that retained child through its pidfd.
The frozen build contract requires the reviewed compiler, archive, startup-object, assembler, and linker file identities.
The driver verifies their retained bytes before and after compilation.

The current optional compiler stage still precedes the original journal charge.
It does not satisfy an installation rule that requires the charge before compiler writes.
[The charged-build decision](PHASE-2D-CHARGED-BUILD-DECISION-2026-10-12.md) records the proposed correction.
This source update does not approve that correction or execute a compiler.

## Finite qualification fixture source, 2026-10-12

`src/crewshal/linux_qualification_fixture.py` supplies the fixed synthetic stock-provider fixture.
One broker process serves the two original qualification lanes.
The original broker has `67108864` memory bytes, zero swap, `16` tasks, and one CPU.
The server verifies its actual cgroup before it handles a request.
It preserves two independent cursors and permits no reset or retry.
It refuses the live lane and every authentication value except its fixed synthetic tokens.
It contains no upstream request or credential forwarding route.
The live native process must use direct stock HTTPS through its retained network policy.

The original readonly root must contain the pinned stock-host certificate, synthetic fixture key, and reviewed `libzstd` library.
The server receives their original FDs and independently verifies their bytes and readonly filesystems.
It binds two exact TLS listener addresses and two exact qualification peer addresses.
It permits only the fixed stock HTTPS host and reviewed endpoint paths.
It bounds compressed requests and decoded requests at `65536` bytes.
It bounds each header block at `16384` bytes.
It rejects duplicate headers, ambiguous lengths, unreviewed encodings, and transfer-encoding requests.

Each lane can request one fixed synthetic usage reply and one fixed model catalog reply before generation.
The complete plan must bind their exact JSON bytes.
The pinned quota path is `/backend-api/wham/usage`.
The pinned catalog path is `/backend-api/codex/models?client_version=0.160.1`.
These paths follow the reviewed [quota client](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/backend-client/src/client/rate_limit_resets.rs).
The catalog path follows the reviewed [models client](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/codex-api/src/endpoint/models.rs).
Synthetic replies cannot establish live account continuity or live quota.

Each lane consumes exactly three fixed Responses requests.
The first request invokes the actual advertised `exec_command` handler.
The second request uses its actual session ID with the advertised `write_stdin` handler.
That request also invokes every declared enabled `apply_patch` and `view_image` handler.
The fixture uses their actual advertised wire types.
It does not invoke an executable alias as a substitute for a native handler.
The final request requires all actual call outputs and the complete fixed probe report.
The fixture refuses missing, failed, or malformed observations.
It compares the full actual native catalog across all requests and both lanes.

The broker emits one original progress record after each lane finishes its third request.
It writes through its retained pipe and limits their combined bytes to `65536`.
The original parent must retain and verify that broker process, pipe, exit, and aggregate membership.
Serialized progress records alone cannot establish qualification.

The fixed probe reads the allowed input and writes the exact `README.md` AFTER bytes.
It tests existing and new owned files and scratch files.
The common plan declares their exact positive marker bytes and paths.
The required absolute and relative escape links reside in scratch.
The candidate contains only regular declared marker files.
This layout permits an exact original frozen copy without deleting qualification evidence.

`verify_frozen_qualification_markers()` reads the actual original readonly projection FD.
It requires the complete declared candidate manifest and each exact marker value.
It reads scratch markers through the original installed scratch volume FD.
It rechecks original projection custody before and after these reads.
The validator still checks the exact `README.md` AFTER value.
The original parent must check all frozen bytes and metadata after validation.
This qualification route cannot replace live `CodexCollection` completion or live task-scope checks.

`RetainedSyntheticExclusions` independently reads excluded synthetic bytes, modes, inode identities, links, and directory inventories.
It rejects changed original handles, changed contents, changed metadata, and new excluded files.
Its data does not replace kernel admission, network sink evidence, cancellation evidence, or validator evidence.

Seventeen focused offline tests pass for the driver and fixture source.
Ruff and mypy pass for the two source modules.
No compiler, TLS server, Linux fixture, authentication stage, model request, or live acceptance has run.
