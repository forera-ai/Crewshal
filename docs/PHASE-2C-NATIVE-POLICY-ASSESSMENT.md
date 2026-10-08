# Phase 2C native setup and scoped policy decision

Date: 2026-10-07. Base revision: `dd0c15cadc7bc082843585bd38ea902f8257c592`. Package checkpoint: 0.8.20. Phase 2C remains incomplete. No native payload, agent dispatch, broker positive control or same-profile mandatory case has passed in this batch.

The owner directly approved the fixture-only v2 AppArmor role policy and requested a tiny native workflow followed by full qualification. The [separate authority record](qualification/phase-2c-direct-linux-native-apparmor-approval-v1.json) preserves that message and exact policy digest. The existing test VM was resumed through VMware's supported CLI; authenticated access observed Ubuntu 24.04.5 aarch64 and kernel 7.0.0-38-generic. This does not establish amd64 or KVM equivalence. No new VM, paid host, provider, sign-in or credential-store access occurred.

## Actual bounded observations

Fresh official Codex/proxy archives were verified against the already pinned rust-v0.160.1 digests. The original data preparation passed in 2.974 seconds. The approved policy was loaded in 0.017 seconds; the global unprivileged-userns restriction remained 1. Native/tool workers retained 134217728 memory bytes, zero swap, one CPU, 32 tasks and five seconds; the aggregate retained 805306368 bytes, zero swap, one CPU and 128 tasks. Status streams stayed below 65536 bytes; manifests used the existing SCP file-transfer interface.

Eight successive source-bound trusted tiny-sandbox setup attempts failed before payload. Each failure and its executed source/profile/freeze/bindings remain immutable. They are diagnostic variants, not eight mandatory qualification results.

| Variant | Actual result and correction |
|---|---|
| v2 | Outer bubblewrap cannot mount its tmpfs because the reduced root has no `/tmp`. |
| v3 preparation | Incorrect prior-manifest name refuses before mutation; source preserved. |
| v4 | Bounded `/tmp` alias fixes mounting; outer `setpriv` UID handoff fails. |
| v5 | Moving UID/GID into bubblewrap requires an explicit user namespace. |
| v6 | Codex starts; the pinned sandbox CLI requires `--permission-profile`. |
| v7 | Supported `:workspace` invocation reaches native setup, but the outer UID map makes scratch unwritable. |
| v8 | Direct systemd host UID/GID 65534 fixes ownership; `ProcSubset=pid` hides bubblewrap's required overflow UID metadata. |
| v9 | Keeping readonly proc metadata reaches namespace mapping; AppArmor denies disconnected `/proc/.../uid_map`. |
| v10 | Fixture-local `chroot_relative` changes pathname interpretation without new grants, parses and loads; disconnected UID-map denial persists. |

The [kernel audit](qualification/phase-2c-direct-linux-native-apparmor-audit-v9-v10.txt) supplies the decisive cause. CLI help and release-tag [permission resolution](https://raw.githubusercontent.com/openai/codex/rust-v0.160.1/codex-rs/core/src/config/permissions.rs) support the explicit `:workspace` invocation. Source/actual argv govern the role description; copied-prose and admission-sample limitations are recorded [separately](qualification/phase-2c-direct-linux-native-policy-limitations-v1.json). No complete native identity/configuration freeze is claimed.

## Concrete pending resolver

[Proposal v4](qualification/phase-2c-direct-linux-native-apparmor-proposal-v4.profile) adds `attach_disconnected` only to the trusted exact native bubblewrap setup profile. The payload profile does not receive this flag and retains userns/capability/mount denial and exec inheritance. No access rule, global sysctl or resource limit changes. Parser-only verification exits zero in 0.018 seconds; v4 has never been loaded.

The [official AppArmor manual](https://www.apparmor.net/man/4.0/apparmor.d/) warns that `attach_disconnected` can alias objects and describes it as a policy-development facility. This consequential interpretation change is outside the exact already approved v2 policy. The owner decision was requested directly and remains pending. Syntax success does not prove compatibility or alias containment. Do not infer approval from silence.

The unexecuted [v11 probe](../scripts/probe_direct_linux_native_compatibility_v11.py) and [prospective profile](qualification/phase-2c-direct-linux-native-compatibility-profile-v11.json) use fresh original preparation, without previous generated compatibility manifests. They check a four-byte scratch file, actual payload label, zero capabilities, no-new-privileges, and one-byte memfd/new-userns denial. This is still a trusted capability subset. If approved, load only the fixture policy, bind actual installed sources and loaded policy hashes, freeze fresh controls, then run. Preserve any failure as a new variant. Independently test aliases, deleted-open handles, inherited handles and existing outside canaries before any full-profile qualification claim.

Full 2C still requires constrained official proxy/native transport authority, adversarial descendant and validator separation, real native dispatch using fixed provider-shaped fixtures, and all twenty original cases twice on the same complete frozen profile. Original protocol SHA-256 remains `fed4dde5e3fe459110a5fb0b2d4f6c75b16214c91aa823d3df640a7415e41563`. Agent execution and Phase 2D remain denied.

## Verification and cleanup

`rtk proxy .venv/bin/python -m unittest discover -s tests -v` passes 93 tests in 4.727 seconds. This is an offline package check, not a native qualification. Ruff for product/tests and the new prospective probe/cleanup sources passes; mypy passes for ten product source files. Public readback:

```sh
rtk proxy .venv/bin/python -I -B docs/qualification/phase-2c-direct-linux-native-policy-readback-v1.py
```

The bounded owned cleanup exits zero in 0.086 seconds. Fresh root PID/FD path inspection finds no handles into the owned fixture before or after removal. The [external readback](qualification/phase-2c-direct-linux-native-external-cleanup-v2.json) observes no owned fixture, runtime sources, transient units, aggregate cgroup/unit or loaded profiles; the global restriction remains 1. The existing VM remains running. No exhaustive host inventory or successful native payload is inferred from cleanup. Public records contain no address or authentication material. Exact continuation inputs are in [the resumption prompt](PHASE-2C-RESUME-PROMPT.md).
