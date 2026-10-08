# Direct Linux feasibility: admission batch

Date: 2026-10-06. Status: **prepared; replacement topology approval and an owner-accessible existing Linux shell are required before Linux use**. This is the first finite step of [proposed ADR 0003](decisions/0003-direct-linux-qualification.md), not a worker/native qualification profile. No paid host is necessary for this read-only batch. Do not boot or provision a new guest, recover old credentials or assume the earlier test VM is accessible.

## Bound source and exact read-only invocation

Source: [phase-2c-direct-linux-admission-v1.py](qualification/phase-2c-direct-linux-admission-v1.py), SHA-256 `eaf4f37bf1655d9754f1a12421f53673a62558c532ed46fdc0aabebb0b7e936d`.

On the existing approved Linux shell, copy only this public source to the exclusively new path `/tmp/crewshal-direct-linux-admission-v1.py`; refuse an existing file or symlink. The owner supplies shell access directly; no password is stored in the project. Verify copied bytes against the source digest before invocation. Interpreter/timeout paths below must exist; no installation or PATH fallback is implicit.

```sh
/usr/bin/sha256sum /tmp/crewshal-direct-linux-admission-v1.py
/usr/bin/timeout --signal=TERM --kill-after=1s 9s \
  /usr/bin/env -i PATH=/usr/bin:/usr/sbin:/bin:/sbin PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 -I -B /tmp/crewshal-direct-linux-admission-v1.py
```

Use RTK if installed on that Linux shell; RTK absence in the earlier guest was recorded. Host-side transport commands must use RTK. This source performs only reads and prints JSON. It does not execute discovered helpers, start a service/native CLI, create a key/mount/cgroup, consult HOME or a credential store, or contact a network. Its fixed kernel reads are cgroup controller names, supported filesystem names and the current process cgroup. It hashes only six helpers found in fixed system directories. Those byte identities are admission data, not a complete library/kernel/native identity freeze.

Trusted capture must stop after ten seconds total including kill grace and refuse streams above 65536 bytes. Save raw output privately outside the checkout; do not commit local user/cgroup/path metadata verbatim. Only a sanitized observation with byte/source/configuration bindings may become public evidence. Incomplete/oversized output is unavailable. Remove only the newly copied source after recording its digest and verifying the script exited; no service or privileged fixture cleanup is involved.

Preparation is one source file below 8192 bytes, at most 60 seconds for the owner's existing local copy/verification transport. The admission invocation is at most ten seconds, no installation, no paid exposure. The later mechanism experiment remains separately capped at the original two-fixture 600 seconds and is not supplied as safely executable here.

## What this can decide

- Whether the provided shell is Linux and its observed architecture/kernel/Python identity.
- Whether cgroup v2 controller names and the required existing helper bytes are available for a concrete mechanism proposal.
- Whether the next stage can use matching aarch64 binaries locally instead of seeking an amd64/KVM host. Architecture availability is not runtime qualification.

Exit zero means inventory completed only. It does not establish delegated cgroup control, current headroom, a root setup role, syscall compatibility, effective limits, complete identities, broker separation or an admitted native profile. No unavailable value becomes a default. Missing interfaces fail the invocation; missing helpers are explicitly null. No package is installed automatically.

After this inventory, prepare a source-bound mechanism profile on that exact environment: read-only vendor root, exclusive candidate/scratch mounts with independently enforced logical and allocated bounds, whole-worker cgroup, external observer and scoped cleanup. Freeze actual helper/library/kernel/interpreter/source identities before mutation. If the mechanism cannot work within the unchanged limits, report that contradiction and stop. Do not return to SBX documentation research.

## Local verification and next gate

On the observed Darwin arm64 host, the exact source returned **exit 2**, explicit Linux-unavailable status, all execution/native/freeze flags false and no worker operation. This is the expected platform refusal, not a Linux observation. Ruff check/format passed. Existing eleven offline qualification refusal methods passed separately; no new mandatory case was promoted.

The [decision record](qualification/phase-2c-exit-decision-v1.json) maps all twenty original criteria without deleting or weakening any. Owner approval of the topology remains pending. The original SBX and qualification evidence remain immutable. Phase 2C remains incomplete until same-profile mandatory evidence passes twice; Phase 2D stays gated.
