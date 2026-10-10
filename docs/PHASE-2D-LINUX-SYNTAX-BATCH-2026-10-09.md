# Phase 2D: one bounded Ubuntu helper syntax check

Date: 2026-10-09. Base `8e010b5ca2dd3298268132613f8ad17ff9db07c6`, package 0.10.0. This is a concrete proposed preparation check within the ongoing Phase 2D milestone. It is not an execution profile, installation, native/tool qualification or a model attempt.

The current helper has never been compiled. Offline text assertions cannot show that its Linux namespace, cgroup and descriptor interfaces compile against the owner's installed headers. A single syntax check resolves that prerequisite before further installation or operational qualification is proposed.

## Exact source and action

Input: `src/crewshal/bootstrap_helper.c`, 8011 bytes, SHA-256 `893357d84d18b0d11d3e7a03d044cd39f91fd5f928f233003d04114c1adefd9b`. A separate private 0700 directory contains the frozen input and exact SSH/remote argument arrays. Its private access target is intentionally excluded from Git. Neither its record nor matching hashes authorize execution.

The existing owner-authorized Ubuntu access supplies transport. Send only the frozen public C source on stdin. Require existing strict host-key verification, batch authentication, a ten-second connection timeout and passwordless `sudo -n`. Any failure stops this check; do not retrieve passwords, install a compiler, retry or change host configuration.

The same private directory now contains a complete bounded transport client, `run-syntax-check.py`, 6420 bytes, SHA-256 `fb23cf6080ac9a9a6d318494891933867a389b58e63c7881d36de3ad5d8ddc3b`. It burns an exclusive attempt marker before launch, sends only the frozen input with nonblocking duplex capture, caps each stream at 65536 bytes and uses the fixed 120-second client startup deadline inside the original 600-second/final-thirty-second bounds. On failure it signals only the original SSH client with one second of recovery; it issues no additional SSH or host-cleanup command and records remote completion as unknown. Raw transport output remains private. Two fresh local pipe fixtures with mocked Popen verify full input/EOF, fixed-deadline refusal, one launch and no second attempt. Neither the client nor compiler has run operationally. Syntax success does not claim independent remote containment, release or full 2D acceptance.

Exact remote argument array, rendered as a shell command for review:

```sh
sudo -n /usr/bin/systemd-run --quiet --wait --pipe --collect \
  --unit=crewshal-2d-syntax-893357d84d18b0d1 \
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

Use one compiler invocation, at most 30 seconds, zero swap, one CPU and 32 tasks/128 MiB. These are within the original aggregate 768 MiB/128-task ceiling. Capture at most 65536 bytes per stream. Keep the 120-second startup ceiling and the fixed final 30-second reserve inside 600 seconds; no deadline origin or recovery grace is renewed. The client independently bounds transport and capture. Requested systemd properties do not establish independently observed whole-profile containment.

`-fsyntax-only` produces no helper executable. Invoke no helper/native/validator program, managed login, authentication/quota endpoint, provider/model, keyring, ext4/eCryptfs or loop-device operation. Do not install packages, modify the project checkout or perform physical storage cleanup. Compiler/service failures and unavailable capabilities remain explicit evidence. A successful compiler exit establishes only that this exact C input passes the installed compiler's syntax check. It proves no storage release, reuse, installed identity or Phase 2D acceptance.

## Approval boundary

The original preparation instruction excluded compilers. The current [production guide](PHASE-2D-PRODUCTION-OWNERSHIP-2026-10-09.md#exact-remaining-production-gap) records a separately reviewable operational batch for helper compilation; [ADR 0005](decisions/0005-official-subscription-pilot.md) preserves separate installation/login/native/model gates. Existing Ubuntu access and the two accepted subscription decisions are unchanged. Approval of this concrete syntax check is the remaining authorization for this action only. It does not amend those later gates or authorize metered services.

Continue authorized source work while this question is pending. Full Phase 2D still requires fixed installed physical capacity/journal binding, effective total growth, actual retained views and timer exclusion, installed identities, all twenty original mandatory cases twice/every enabled native file tool, and a separately authorized real candidate/credential-free validator result. Commit/push follows full acceptance only. No Phase 2E.
