# Phase 2D operational batch — 2026-10-13

Status: Prepared for separate operational approval. Phase 2D has not passed acceptance.

This proposal uses the existing local VMware Ubuntu installation and the accepted SSH access channel.
It requires no paid host, infrastructure purchase, package release, or Phase 2E work.
The original task requires separate approval for this complete operational batch.
The three source amendments remain accepted.

## Exact reviewed inputs

[The complete batch record](qualification/phase-2d-executable-batch-v3-20261013.json) contains the source hashes, command arrays, owner script bodies, and exact unit bodies.
It supersedes the earlier preparation record without consuming that record's inputs.
The private batch contains the owner's supplied account metadata and synthetic TLS key.
Those private bytes remain outside Git.

| Input | Exact identity |
|---|---|
| Branch | `codex/phase1-architecture` |
| Base revision | `87ed7e6f6c766c7ff2df245ad05569558a9ca3bc` |
| Unreleased candidate | `0.13.0` |
| Private batch SHA-256 | `b73d02ab625217f18c38225d9487cf685ede7311f1f16c661c1c5a70bd0edeb4` |
| Common configuration SHA-256 | `142694cea4496a8f3de05155047c4828ae8b239c3e58c34e896ff103dbcce914` |
| Input archive bytes | `15923200` |
| Input archive SHA-256 | `9997d9ec0a2e8140b17b3d5faf719911b6b846553c6a7971417524e8c27cd1f2` |
| Input manifest SHA-256 | `81bffc52756278235f067c23bb52edaa5d2bf00d3b7be7cd07e5c0077652500b` |
| Wheel SHA-256 | `70c744b2cda0de01bf316b3d740d577a7e772d5daf93bfd2c57d940d739ec85b` |
| Copied root entries | `1162` |
| Prospective root input bytes | `348349855` |
| Accepted copied root ceiling | `469762048` bytes |

The root inventory binds actual VM runtime files and the official pinned native release.
Every recorded ELF dependency has an exact file or direct alias in that inventory.
The compiler recipe binds actual headers, static archives, compiler programs, runtime libraries, parser features, and ABI bytes.
The initial helper and policy entries identify uncompiled inputs.
The sole registered build receipt derives their installed identities after actual compilation and readback.
No initial placeholder is presented as an installed binary.

The actual VM reports Ubuntu 26.04.1, aarch64, four CPUs, and `7573400` KiB of total memory.
The kernel signature is `Ubuntu 7.0.0-38.38-generic 7.0.14`.
The batch uses explicit Python 3.12.3, GCC 15.2.0, AppArmor parser 5.0.2, and systemd 259.5.
Fresh readback confirms ext4, eCryptfs, loop control, cgroup controllers, and AppArmor policy export support.
The four declared AppArmor profile names are absent.
IPv4 forwarding is currently zero.
The operational entry must verify these inputs again before use.

## Completed source verification

Both complete suites pass `1150` method occurrences and `1134` unique methods.
Each suite includes `993` unique Phase 2D methods.
The `16` repeated occurrences come from imported test classes.
Both suites deny network access and use an empty inherited environment with a fresh HOME.
Source bytes remain unchanged during both suites.
All `47` installed package files match current source bytes.
Ruff checks pass; mypy passes for `46` source files.

The first wheel suite failed because a storage test mock replaced unrelated symlink reads.
The corrected mock applies only to its controlled proc FD paths.
All affected checks and both complete suites then pass.
These results prove source and package behavior only.
They do not prove Linux installation, tool enforcement, authentication, or live acceptance.

## Owner input capability preparation

The owner input stage supplies the immutable capabilities required before the original observer starts.
It does not build the helper, load policy, create installation volumes, authenticate, or start a model turn.
The exact scripts use exclusive new paths and retain partial inputs after failure.

1. Verify the frozen local source, scripts, archive, private plan, and existing SSH host identity.
2. Send the exact archive to [the fixed upload entry](../scripts/phase_2d_owner_input_upload.py).
3. Run [the fixed owner capability entry](../scripts/phase_2d_owner_capabilities.py) with its exact source on stdin.
4. Verify the prepared input files, installed unit bytes, aggregate controls, and forwarding value.
5. Set IPv4 forwarding from zero to one with the exact command in the batch record.
6. Start `crewshal-2d-20261012v1-observer.service` once.

The input stage uses `/var/lib/crewshal-phase2d-input-v1` for immutable source data.
It uses `/var/lib/crewshal-phase2d-storage-v1` for the private disk backing directory.
The observer unit binds the disk directory at `/run` in its private mount namespace.
This preserves every original installation path and avoids a tmpfs copy of the large native executable.
The unit binds the source capability readonly at `/run/crewshal-phase2d-input-v1`.
It supplies the existing verified native and bubblewrap bytes through readonly binds.
It also supplies pinned bubblewrap at `/usr/bin/bwrap` inside that private namespace.
These binds do not replace host executable files.
The batch does not alter the VM's writable shared folder.

The exact observer command is:

```sh
/usr/bin/env -i /usr/bin/python3.12 -I -S -B /run/crewshal-phase2d-input-v1/observer-entry.py /run/crewshal-phase2d-input-v1/batch.json
```

## Original installation and acceptance sequence

The original observer obtains its clock from its kernel process birth time.
It records the full original charge before it creates the exclusive attempt marker.
It retains the original observer, journal, groups, handles, and unknown results.
It creates the sole independent timer before either compiler.

1. Create the original compiler volume under the existing charge.
2. Run one C compilation and one AppArmor compilation within the same original 30-second build interval.
3. Verify actual successful waits, empty setup, readonly compiler storage, and the three original output FDs.
4. Derive only the accepted installed identities through the sole registered receipt.
5. Load only the absent declared AppArmor profiles and retain their actual kernel directory IDs.
6. Verify policy exports, kernel geometry, root files, original volumes, and installed process identities independently.
7. Run all twenty original qualification cases in `qualification-1`.
8. Run all twenty original qualification cases in `qualification-2`.
9. Require actual coverage for `exec_command`, `write_stdin`, and `apply_patch` in both lanes.
10. Refuse any additional enabled file tool until the frozen qualification covers it.
11. Complete one stock device login for the owner's supplied account.
12. Run one live thread and one turn only after both original qualifications pass.
13. Capture the actual frozen candidate through original custody.
14. Apply the supplied conditional owner decision only to its exact expected binding.
15. Run the independent credential-free validator through its original private view and original FDs.
16. Verify the actual verdict, durable admission linkage, positive waits, and original terminal ownership.
17. Verify original idle retention at the original 600-second end.

The fixed probe now requires ordinary shared-file mapping to succeed.
It also requires private anonymous mapping to succeed.
It requires anonymous shared mapping, `/dev/zero` access, and `memfd_create` to fail.
The original worker and detached descendant must both supply these observations.
Both qualification lanes must also prove denied tool access to the private native authentication and configuration files.
These probes add no new qualification case, owner, retry, or timer.
The twenty original case names remain unchanged.

## Unchanged ceilings and clocks

| Object | Original limit |
|---|---|
| Aggregate | `805306368` bytes, `128` tasks, one CPU, zero swap |
| Worker, native, and tools together | `134217728` bytes and `32` tasks |
| Validator | `134217728` bytes and `32` tasks |
| Observer | `134217728` bytes and `32` tasks |
| Broker | `67108864` bytes and `16` tasks |
| Logical and allocated storage | `8589934592` bytes each |
| Candidate | `16777216` bytes |
| Scratch | `33554432` bytes |
| Batch end | Original origin plus `600` seconds |
| New-work cutoff | Original origin plus `570` seconds |
| Final reserve | Fixed `30` seconds |
| Startup | Original `120` seconds |
| Each storage job | Original `30` seconds |
| Native attempt | Original `5` seconds from pre-creation origin |
| Validator attempt | Its original `5` seconds |
| Recovery grace | Original `1` second |
| Captured stream | `65536` bytes |

Input transfer has its own fixed 30-second owner capability bound.
It does not extend or replace an installation clock.
Active installation starts only in the original bounded observer.
Expected exposure includes one Plus subscription turn.
The accepted subscription design supplies no hard financial ceiling.
The batch creates no paid-host exposure or API-key request.
The original observer remains idle after terminal verification and retains all original handles.

## Decisions included in the operational approval

The approval permits the exact owner capability preparation and original installation sequence above.
It permits one stock device login and one live implementation turn after both qualifications pass.
It also accepts these two supplied fixture decisions:

- Approve the exact bounded implementation of the original fixed README task.
- Approve only a frozen `README.md` file with mode `0644` and exact `AFTER` bytes from `crewshal.runtime_batch`.

The frozen candidate must contain no extra path.
The second decision applies only after the actual frozen binding matches the supplied expected binding.
The approval supplies no replay, retry, resource refund, release, merge, deployment, or Phase 2E authority.
All accepted source decisions remain accepted.
The owner must be ready to complete device login within the remaining original startup interval.

## Stop conditions and retention

Any missing input, changed identity, failed readback, unknown result, limit event, or incomplete case prevents acceptance.
Any compiler refusal consumes the sole build attempt.
Any authentication or live refusal consumes that original attempt.
The observer reports the failure type, source location, and available OS error number without exporting secret values.
It retains the original owner, partial handles, full charge, and unknown results.
The batch does not close unknown original handles or start a replacement observer.

Restore IPv4 forwarding to its original zero value with the exact recorded restoration command.
Do not delete policy, network, storage, markers, journals, or retained process custody automatically.
Physical closure remains unknown unless its original owner supplies independent evidence.
Do not infer a resource refund from a timeout, empty scan, closed stream, or process exit.

Publish the current branch only after every actual Phase 2D acceptance gate passes.
Then complete the required documentation, version, commit, push, and next-session prompt.
Stop at the Phase 2D boundary.
