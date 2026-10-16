# Phase 2D executable batch input contract

Date: 2026-10-12.
Status: Source preparation. The separate operational batch has not been approved.

The finite entry is `crewshal.linux_batch_entry`.
The entry preserves one original observer, charge, journal, timer, and three-lane schedule.
It does not reconstruct custody from parsed records or success flags.

## Exact entry command

The approved observer unit must use this exact command:

```sh
/usr/bin/env -i /usr/bin/python3.12 -I -S -B /run/crewshal-phase2d-input-v1/observer-entry.py /run/crewshal-phase2d-input-v1/batch.json
```

Generate `observer-entry.py` with `observer_entry_source()`.
The entry requires Python 3.12 and an empty inherited environment.
It imports only the fixed readonly runtime at `/run/crewshal-phase2d-input-v1/lib`.
That directory must have root ownership and mode `0555`.
The plan must have root ownership, mode `0400`, and an actual readonly mount.
The plan has an `8388608`-byte bound.

The owner must prepare the original bounded observer and aggregate before this command starts.
The driver derives its original clock from the kernel process birth time.
The driver charges the original installation before it creates the exclusive attempt marker.
It creates the marker before any lane, timer, or build effect.
Failure preserves the marker, original charge, process handles, and partial outputs.
The entry supplies no automatic retry or resource refund.

## Offline assembly

Use `assemble_frozen_batch()` after the source is complete and stable.
This function reads current package source as data.
It does not inspect Linux state, create files, authenticate, or execute a process.
Supply these exact records:

| Input | Required content |
|---|---|
| `installation` | Complete `FrozenInstallationInputs`, original paths, root inventory, build recipe, and early timer runtime. |
| `networks` | Three `LaneNetworkPlan` records, exact public stock endpoints, tool hashes, and `original_two_lane_tls_v1`. |
| `tls` | Exact certificate, private key, zstd hash, two fixed listeners, peers, and stock bootstrap replies. |
| `qualification` | Actual target host, kernel, architecture, runtime, image, toolchain, grant, harness, and credential design identities. |
| `project` | The exact reviewed `ProjectModel`. |
| `task` | The fixed requirement and independent validator check. |
| `policy_sha256` | The exact reviewed policy record digest. |
| `run_id`, `attempt_id` | New identifiers for the sole live implementation attempt. |
| `decisions` | Literal owner decision text for the proposed implementation and conditional frozen approval. |
| TLS paths | The certificate, private key, and zstd paths in the immutable root inventory. |
| `one_use_parent` | A private root-owned directory with mode `0700`. |
| `lease_token` | A new local lease value. This value is not a provider credential. |

The task must use `REQUIREMENT`, one check, and the original `README.md` scope.
Compute the check toolchain with `validator_toolchain_digest(inventory, validator_argv)`.
Use `digest(b"")` for its empty validator environment.
Keep `review_required=False` and `independent_provider=False` for this acceptance task.
These flags do not remove the independent credential-free validator.

The builder computes the initial binding from the supplied project, task, policy, scope, and exact initial manifest.
It binds the current source, immutable inventory, network plan, build recipe, and bootstrap policy.
It prepares one implementation decision and one conditional frozen decision.
These proposed decision records require the separate operational batch approval before use.

The conditional frozen decision permits only the following actual result:

| Property | Exact value |
|---|---|
| Path | `README.md` |
| Kind | `file` |
| Mode | `0644` |
| Bytes | `AFTER` from `crewshal.runtime_batch` |
| Extra paths | None |

The entry applies that supplied decision only after the actual frozen binding matches every field.
It does not generate a new owner decision from a model result.

## Required Linux preparation inputs

Record actual bytes and identities for every input below.
Do not substitute test fixtures, historical run handles, or observed records from another host.

- The pinned official native archive and its executable, sandbox, and bundled bubblewrap bytes.
- Python 3.12, its loader, standard library, extension libraries, and the installed Crewshal wheel.
- Pydantic and its actual extension and runtime dependencies.
- Every current `SOURCE_FILES` entry under `/opt/crewshal/lib/crewshal/`.
- The exact isolated parent entry and its fixed argument array.
- `mkfs.ext4`, `ip`, `nft`, their loaders, and their complete reviewed library closures.
- The C compiler, linker, static archives, headers, and actual runtime closure.
- The original compiler volume, backing, loop, ext4 geometry, ownership, and inode identities.
- The AppArmor parser, include files, ABI files, package record, policy source, and audit template.
- The actual target kernel package record, source files, configuration, BTF, notes, and shared-memory inode cache interfaces.
- The fixed readonly fixture files, including `/input/check_fixture.py` with exact `CHECK_SOURCE` bytes.
- The synthetic qualification certificate and private key, and the actual zstd library.
- The exact stock HTTPS hostname and public endpoint inventory.
- The owner-prepared cgroup parent, aggregate, observer role, and controller settings.

The builder does not collect these inputs.
The complete operational proposal must specify their preparation commands and independent readback.
It must specify any required forwarding change and its exact restoration command.
It must include the installation of absent AppArmor profile names and their independent installed readback.
It must preserve unknown cleanup results and retain resources after refusal.

## Qualification manifest convention

`current_qualification_manifest()` binds the unchanged original protocol digest and all twenty mandatory case names.
It also binds the current qualification probe source and `FrozenQualificationFixture` schema.
This digest does not depend on compiled helper or policy output bytes.

The original protocol digest remains:

```text
fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563
```

The legacy portable bundle auditor requires that original protocol digest directly in its `manifest` field.
The Phase 2D records use the new source manifest convention.
Do not present them to the legacy auditor as records with its earlier manifest convention.

The live qualification projection retains both original terminal qualification collectors and their exact records.
It preserves the common profile and changes only the declared lane configuration identity.
A parsed qualification, copied record, or caller readiness flag cannot replace those owners.

## Authentication and stop conditions

Use `FrozenAuthenticationPlan` with `stock_device_login_v1`.
Bind its source digest and account reference to the same frozen common configuration.
Use the owner's supplied email and Plus plan metadata in the private account profile.
Keep the account ID unknown until actual native readback supplies a value.
Do not read ambient credential stores or copy an authentication file into the live home.

The entry performs one stock device login through `authenticate_original_live()`.
It uses the original live setup role and the original clocks.
The owner must be ready to complete the device login within the remaining original startup interval.
Authentication failure consumes the attempt and preserves its original handles.

Both complete twenty-case qualification lanes must finish before the live lane starts.
The actual tool catalog must match the frozen enabled file tool set.
The live lane requires actual native completion, original frozen custody, and the independent credential-free validator.
Any incomplete or unknown result prevents acceptance.
The entry stops after the three original terminal lane results and the verified live verdict.
It does not publish, release resources, start Phase 2E, or change an original limit.
