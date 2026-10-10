# Phase 2D: additional frozen batch-timer syntax check

Date: 2026-10-10. Base source checkpoint `758079b9bcf8ad82d5863aaf5f6a096608acb942`, version 0.11.0, branch `codex/phase1-architecture`. Status: prepared; owner approval for this invocation remains pending. Full 2D is incomplete and current source unqualified.

Batch-timer and child-placement implementation changes the helper from the previously approved 8011 bytes. The earlier successful syntax observation cannot establish compatibility of these new bytes. Both earlier invocations are consumed. This proposed check is a separate, explicitly approved additional invocation, with no automatic retry or expanded operation.

## Frozen input and exact operation

Input: `src/crewshal/bootstrap_helper.c`, **13411 bytes**, SHA-256 **`21e8b509e5c25011efd2522a4cfccb0c4e675aa59e147c50c2b32496f0cece2c`**. A new private 0700 directory retains these exact bytes, a one-shot transport client and the private argument arrays. Client: 6421 bytes, SHA-256 `2f94c459587fe9f27316cec7b3bca38261d6ce8901af7f071333332ce54bd58b`. Its only changes from the preserved earlier client are the frozen input digest and length. It retains exclusive attempt/output files, nonblocking bounded capture, strict existing SSH access, 120-second startup, one-second client recovery, 600-second batch and final 30-second reserve. It has not been invoked.

Use the existing exact command-only capability confirmed installed by the owner. The remote argument array is unchanged from the approved successful second command, including its existing unit label. The label still contains the older source prefix; it is a service name, not an input digest or identity/release witness. The new frozen source identity above governs input. Do not inspect/delete an old unit, infer availability from absence, retrieve a password, broaden sudo, remove resources or retry a refusal. A collision or unavailable capability stops this invocation. No resource release or reuse is claimed.

```sh
sudo -n /usr/bin/systemd-run --quiet --wait --pipe --collect \
  --unit=crewshal-2d-syntax-893357d84d18b0d1-b \
  --property=MemoryMax=134217728 --property=MemorySwapMax=0 \
  --property=TasksMax=32 --property=CPUQuota=100% \
  --property=RuntimeMaxSec=30s --property=TimeoutStopSec=1s \
  --property=KillMode=control-group --property=Restart=no \
  --property=NoNewPrivileges=yes --property=CapabilityBoundingSet= \
  --property=WorkingDirectory=/ --property=User=nobody \
  --property=PrivateNetwork=yes --property=ProtectHome=yes \
  -- /usr/bin/env -i PATH=/usr/bin:/bin /usr/bin/cc \
  -pipe -x c -std=gnu11 -Wall -Wextra -Werror -fsyntax-only -
```

Only these public C bytes travel on stdin. One compiler invocation, at most 30 seconds, 128 MiB/32 tasks, zero swap, one CPU and 65536 bytes per stream. No executable is produced or installed. No helper, native, validator, namespace, keyring, mount, loop, storage mutation, login, provider/model or metered service operation is permitted. Requested systemd properties and compiler exit do not establish independent effective containment or a released process/resource tree. Capture failure preserves unknown remote completion and stops without another command.

## Authorization and continuation

Existing Ubuntu access, installed command capability, accepted retained ownership and the subscription decisions remain resolved. The original compiler prohibition and the two consumed exact-input approvals do not authorize compilation of this changed input. This check requires explicit approval of one additional frozen invocation. It does not grant any installation/native/kernel/login/model qualification authority reserved by [ADR 0005](decisions/0005-official-subscription-pilot.md).

Continue safe source work while the question is pending. The [current timer source guide](PHASE-2D-BATCH-TIMER-2026-10-10.md) records implementation, offline evidence, remaining operational placement/terminal uncertainties, capacity/growth/freeze/validator and exact Linux/live gates. A syntax pass clears compiler compatibility only for these bytes. Complete the same effective 2D milestone; no metered fallback, physical cleanup, reuse or 2E.
