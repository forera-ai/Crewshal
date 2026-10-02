# Temporary Ubuntu KVM host capability

Date: 2026-10-02. Package 0.8.1. Scope: **Phase 2C host capability checkpoint only**. The owner supplied a temporary DigitalOcean VPS and authorized testing before deletion. No host address or authentication secret is retained in these public records. Full execution qualification remains denied.

## Observed capability

SSH inspection observed Ubuntu 24.04.5 LTS, x86_64, kernel `6.8.0-142-generic`, 961 MiB reported RAM, zero swap and approximately 22 GiB free on the root filesystem. CPU flag `vmx`, modules `kvm_intel`/`kvm`/`irqbypass`, `/dev/kvm` character device 10:232 with mode 0660 and root:kvm ownership, and its sysfs entry were present. Initial API/VM/vCPU creation checks passed before the full HLT protocol was frozen; these are preliminary evidence, not the two prospective runs.

The [prospective protocol](qualification/phase-2c-kvm-host-v1.json) binds the [exact source](qualification/phase-2c-kvm-host-v1-probe.txt), SHA-256 `cfce2653fe58d2a53c7ebc5a541b3067737c2e788ac662183a014807b30b4a2f`, five-second alarm, 1,048,576-byte guest memory and expected KVM exit reason 5. Each invocation creates a new anonymous memory mapping, VM and vCPU. The only guest instruction is x86 HLT at physical address 4096; no guest OS, filesystem, network interface or external image is supplied.

Two separate invocations returned KVM API version 12 and exit reason 5, with every process-owned mapping/descriptor closed. This demonstrates actual hardware-assisted guest execution, beyond device/module presence. See [sanitized observations](qualification/phase-2c-kvm-host-v1-observed.json).

A supplementary child cleared supplementary groups, dropped to UID/GID 65534 and attempted read/write open of `/dev/kvm`. PermissionError was observed and the child exited zero. This control was not frozen prospectively and is not promoted into the HLT protocol. The successful probes ran as the administrative root account; no non-root worker profile has been qualified.

## Reproduction and cleanup

On a newly supplied disposable Ubuntu x86_64 host with Python 3 and KVM, inspect OS/kernel, CPU flag, device permissions and available resources first. Copy the exact probe text to a temporary file; verify its SHA-256 before execution. As an authorized KVM-capable account, run `timeout 10s python3 PROBE_FILE` twice as separate processes. Expect API 12, exit reason 5 and `kvm_run_hlt: pass`; any exception, signal, timeout or disagreement is a failure. This is a trusted hardware diagnostic, not an untrusted worker launcher.

Actual remote invocations used the frozen source supplied through base64 to Python's `compile`/`exec`, without creating any remote file. The source's five-second alarm bounded guest execution. Host inspection and supplementary checks used only existing shell/Python commands; no remote package was installed or account/settings changed.

After both runs and the supplementary control, an independent administrative scan of all readable `/proc/PID/fd` links found no remaining `kvm-vm` or `kvm-vcpu` handles. A process-name inventory found no `sbx`, `sandboxd` or `qemu-system` process. These are final snapshots, not claims about every transient process. SSH disconnected successfully. No remote file, installed package, daemon, guest image or persistent VM was created by this session. The owner may delete the Droplet after receiving the final handover; deletion itself is not performed or assumed here.

SSH accepted a first-use host key into a dedicated temporary known-hosts file. No independent console fingerprint was supplied, so host authentication has that explicit limitation. Public evidence is a sanitized transcription of tool outputs, not a signed remote attestation.

## Remaining Phase 2C gate

This host clears the observed KVM capability prerequisite. It does not establish operational SBX startup, credential-store isolation, caller/request authority, native hooks/MCP/configuration, inner resource enforcement, network boundaries or a separate validator. No SBX binary, daemon, template or native coding runtime was installed or launched; no model, provider, login or authenticated request occurred. All existing worker limits, frozen profiles and denial decisions remain unchanged.

The 1 GiB host proved sufficient for these diagnostics only. The proposed 512 MiB outer SBX guest and its memory/CPU/disk/scratch/startup/total bounds still require a concrete operational protocol. A compatible x86_64 SBX bundle must be prepared and pinned; previous arm64 identities cannot be reused. The temporary host is slated for deletion, so replacement access and fresh capability/configuration checks are necessary next session. Continue with [the updated prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md); no Phase 2D work is authorized.
