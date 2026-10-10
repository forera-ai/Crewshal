# Phase 2D: exact noninteractive syntax capability and one additional proposal

Date: 2026-10-10. The owner selected **“Arrange narrowly scoped sudo”** after the [first approved syntax attempt was refused](PHASE-2D-SYNTAX-RESULT-2026-10-10.md). That selection permits preparing the precise capability instructions. It does not show that Ubuntu authorization has been installed and does not authorize another compiler invocation. The consumed original marker/output and immutable result remain retained.

## Owner action in the Ubuntu terminal

Open only this dedicated entry:

```sh
sudo visudo -f /etc/sudoers.d/crewshal-2d-syntax
```

Enter any authentication locally in Ubuntu; do not send passwords to the agent. Paste the complete contents of [the exact sudoers snippet](qualification/crewshal-2d-syntax-sudoers-20261010.txt), replacing only `your_linux_username` with the existing Ubuntu login name. Save through visudo. The entry specifies one command and its full fixed arguments, with no wildcards. It does not grant unrestricted systemd-run or unrestricted sudo. The application still runs the compiler as `nobody` with an empty environment and the original fixed limits.

The snippet was parsed locally with `/usr/sbin/visudo -cf` and returned `parsed OK`; this is an offline syntax check, not evidence of Ubuntu installation, policy inclusion or effective authorization. Sudoers requires command arguments to match and requires escaping its punctuation; those escapes are already included in the snippet. [Official sudoers manual](https://www.sudo.ws/docs/man/1.9.14/sudoers.man.pdf).

The owner supplies the actual Ubuntu authorization. The agent has made no sudoers/configuration changes, further SSH probe or compiler invocation. After the separately approved check, the owner may remove this dedicated entry through visudo; the agent will not modify unrelated authorization.

## Proposed one additional bounded attempt

This is an explicit proposal for **one additional syntax-only invocation after the failed privilege prerequisite**, not an automatic retry and not an extension of the failed batch's deadline. A separate private review directory contains frozen source/client/access arrays, no attempt marker and no credentials in Git. Both source/client byte identities remain the same as the first approved proposal. The only remote argument change is the dedicated next unit name `crewshal-2d-syntax-893357d84d18b0d1-b`, exactly as restricted by the snippet.

Input: bootstrap_helper.c, 8011 bytes, SHA-256 `893357d84d18b0d11d3e7a03d044cd39f91fd5f928f233003d04114c1adefd9b`. Client: 6420 bytes, SHA-256 `fb23cf6080ac9a9a6d318494891933867a389b58e63c7881d36de3ad5d8ddc3b`. Sudoers snippet SHA-256: `b9dcd7781e4bebef239da26ff800765c75aa70d47b1bd1f806cccc1857980dd8` before local username substitution. Existing strict host-key/batch SSH and ten-second connect timeout remain fixed. Do not retrieve keys/passwords or retry a transport/compiler refusal.

Exact remote command:

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

One compiler invocation, at most thirty seconds, 128 MiB/32 tasks, zero swap and one CPU. Client capture stays at 65536 bytes per stream and its fixed 120-second startup bound lies within its explicitly separate 600-second preparation batch with the final thirty-second reserve intact. This does not restart a native five-second origin, failed-batch deadline or runtime recovery grace. Requested systemd properties do not prove independently observed whole-profile containment. No binary output/installation, helper/native/validator execution, storage/key/loop operation, login/provider/model call, metered spend or host cleanup is included. Any failure consumes this additional attempt and stops without retry.

## Required answer and continuation

The agent must receive both confirmation that the exact capability is installed and explicit approval of **one additional syntax-only attempt** before using the new private client. The owner's capability preference alone supplies neither fact. This precise extra invocation is the necessary exception to the failed first proposal's one-shot/no-retry stop; it is not permission for routine retries or broader runtime work. Do not rerun or delete the consumed first client/marker.

Full 2D remains incomplete. Continue the exact source/capacity/validator/timer/identity and Linux/live gates in the result guide. Keep every accepted decision, original ceiling/origin/grace/reserve, retained charge/unknown and publication gate. Compiler success alone never completes 2D or grants release/reuse. Commit/push follows full acceptance; no 2E.
