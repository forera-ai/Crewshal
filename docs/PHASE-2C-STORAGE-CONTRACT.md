# Phase 2C storage contract resolution boundary

Date: 2026-10-05. Base: `9ebcc49f268ce9febe66b6a7a50600acd372f46a`; clean `codex/phase1-architecture`, package 0.8.16. Delivery: 0.8.17. **Configuration documentation is now pinned to the release era; the exact private-fork/VMM contract and an admissible supported layout remain blocked.** No executable, daemon, installer, template, VM, credential or paid-host operation occurred. This is a research/process checkpoint, not runtime qualification.

## What was resolved

The [contract record](qualification/phase-2c-sbx-storage-contract-v1.json) pins Docker documentation revision `7211da11e648595ef32f7d0c3d91fb86571b3907` (2026-09-28T15:13:25Z), the latest main-branch commit returned before SBX v0.46.0's publication at 2026-09-28T17:17:11Z. The record includes exact source URLs, complete file hashes, excerpt hashes and original line ranges. Selection used anonymous public APIs. Chronological proximity is not a vendor assertion that these documents describe every byte of the dirty/private build. No private-source authentication or runtime invocation was attempted.

Release-era [troubleshooting](https://github.com/docker/docs/blob/7211da11e648595ef32f7d0c3d91fb86571b3907/content/manuals/ai/sandboxes/troubleshooting.md#sandbox-runs-out-of-disk-space) documents `DOCKER_SANDBOXES_ROOT_SIZE` before creation, separate root and Docker data disks, and Linux state/cache/config roots. This upgrades ROOT_SIZE from a binary literal to a documented configuration interface. It establishes neither a minimum root size nor effective image bytes, filesystem semantics or guest logical enforcement. The root default is documented as 20 GB; the Docker default is 10 GB. Neither default is an admissible ceiling for this experiment.

Release-era [settings](https://github.com/docker/docs/blob/7211da11e648595ef32f7d0c3d91fb86571b3907/content/manuals/ai/sandboxes/configuration/settings.md#images-and-storage) documents a 512 MiB minimum Docker data disk and a creation-command override. **The per-command `DOCKER_SANDBOXES_DOCKER_SIZE` override does not change `sbx settings get sandbox.disk.dockerVolume`.** Therefore settings readback cannot verify that override or a created disk. Bind the actual creation request, daemon handoff and independently observed disk object; do not use historical `1g` settings as effective disk evidence. Existing objects are not resized by changing this setting.

The documented Linux relocation roots are `XDG_STATE_HOME/sandboxes`, `XDG_CACHE_HOME/sandboxes` and `XDG_CONFIG_HOME/sandboxes`. These are supported top-level locations, not a complete engine-object/writer map. A whole-cache read-only bind or an invented split below these roots remains unsupported by the evidence. Release-era [architecture](https://github.com/docker/docs/blob/7211da11e648595ef32f7d0c3d91fb86571b3907/content/manuals/ai/sandboxes/architecture.md#storage-and-persistence) describes per-sandbox image/layer state; its read-only skills exception does not establish a shared immutable image cache. No cleanup/reset command from the archived documentation was executed.

The prior [pinned source requirements](PINNED-SBX-STORAGE-REQUIREMENTS.md), private replacements, declared EROFS patches and Linux errno observations remain authoritative limitations. New documentation does not establish the selected conversion mode or resolve copy-range EINVAL, privileged ownership, actual bbolt recovery or VMM image I/O.

## Necessary accounting, before a layout can be selected

Let `R` and `D` be independently verified apparent bytes of root and Docker host images under a proposed layout; `B` its backing-file representation; `P` preparation; `K` cache/image layers; `T` conversion intermediates; `G` independently bounded guest apparent contents; and `M` metadata, account copies, helpers, logs and deleted-open state. For the encrypted upper/lower hypothesis, a necessary logical admission inequality is:

```text
P + 2 * (R + D) + B + K + T + G + M <= 8589934592
```

Every representation is charged independently. Actual allocation requires its own complete inequality. Configured capacities cannot simply be substituted for observed apparent image lengths; the equation is conditional on those identities and lengths. Encryption headers, filesystem metadata, intermediate files and partial failures cannot be omitted. A backing file's capacity does not bound guest sparse apparent contents.

The [smaller-layout arithmetic screen](qualification/phase-2c-sbx-storage-small-hypothesis-v1.json) uses an **unvalidated** 1 GiB root hypothesis, the documented 512 MiB Docker minimum and an optimistic backing minimum equal to their sum. Alongside the historical pruned preparation expectation, it separately charges three disk representations. Known subtotal is **5,939,237,149 logical bytes**, leaving **2,650,697,443 bytes** for all remaining logical representations. This is not a selected supported layout. Its allocation and seven other representation groups are unknown; the existing accounting checker correctly returns `arithmetic_refused`, exit 2.

Even before those unknown groups, the same optimistic three-representation assumption with minimum Docker size requires `R <= 1957307638` bytes. This arithmetic is a necessary screening bound, not a supported root size or operational reservation. A fixed backing larger than `R + D`, encryption overhead and every additional charged representation tighten it. Do not request a host or retry import using either number. Whether any root this small is accepted and useful by the exact runtime is unanswered.

## Smallest missing contract and continuation

The contract record retains seven explicit unanswered fields. A version-matching vendor document or supported, prospectively bound observation must answer:

1. Exact state/cache/config object locations, writers and allowed relocation or immutable-content split.
2. Validated minimum root size, effective format/length/allocation, growth/discard and VMM open/I/O semantics.
3. Effective minimum Docker disk bytes, creation-override handoff and independent disk readback.
4. Selected private EROFS full/index/block conversion, exact options/patches and peak intermediates.
5. Required ownership/xattrs, database locking/mapping/durability, copy/seek/preallocation/punch behavior, errno fallbacks and exhaustion recovery.
6. Existing supported independent guest apparent-size enforcement, including sparse files, aliases and deleted-open state, for worker and sequential validator.
7. Complete peak ledger in both dimensions, controller/observer placement and exact supervised commands under the unchanged envelope.

These are evidence requirements, not instructions to access credentials, reverse-engineer a supported path from strings, write a custom fallback or contact anyone. A vendor question can quote these fields and the exact build identities in the prior requirements report; no vendor message was sent. Source access alone would not supply enforcement or qualify the layout. A missing answer stays unavailable.

No paid-host batch is runnable yet. Local aarch64 filesystem results do not qualify the pinned amd64 runtime, but another host cannot supply a missing supported layout by itself. Proceed only after evidence yields a supported candidate and a complete conservative admission/supervision recipe. Then determine which necessary checks can run locally; a new paid batch still needs concrete necessity, commands, duration/cost exposure, cleanup and owner approval. Do not repeat unchanged ENOSPC. Keep all original limits, twenty criteria and denial flags unchanged. No Phase 2D.

## Independent reproduction

The three archived excerpts are data, not instructions. This offline command checks their byte bindings and unchanged denial status; it does not establish truth, executable equivalence or completeness:

```sh
rtk proxy .venv/bin/python - <<'PY'
import hashlib, json
from pathlib import Path
root = Path.cwd().resolve()
record = json.loads((root / 'docs/qualification/phase-2c-sbx-storage-contract-v1.json').read_text())
assert record['release'] == 'v0.46.0'
assert record['docs_revision'] == '7211da11e648595ef32f7d0c3d91fb86571b3907'
for flag in ('execution_allowed', 'native_start_allowed', 'operational_manifest_frozen', 'supported_layout_selected'):
    assert record[flag] is False
assert len(record['source_bindings']) == 3
assert len(record['unresolved_contract']) == 7
assert all(item['answer'] is None for item in record['unresolved_contract'])
for binding in record['source_bindings']:
    path = (root / binding['path']).resolve()
    assert path.is_relative_to(root / 'docs/qualification/sbx-storage-docs-v1')
    data = path.read_bytes()
    assert len(data) == binding['excerpt_bytes']
    assert hashlib.sha256(data).hexdigest() == binding['excerpt_sha256']
print('three excerpts bound; seven contract answers unresolved; execution denied')
PY
rtk proxy .venv/bin/python docs/qualification/phase-2c-sbx-storage-readback-v1.py
rtk proxy .venv/bin/python -m scripts.assess_storage_budget docs/qualification/phase-2c-sbx-storage-small-hypothesis-v1.json
# Last command must return exit 2 / arithmetic_refused, despite the smaller known subtotal.
```

For fresh public verification, fetch each pinned `url` as data with a 262,144-byte bound and 20-second timeout; verify `source_bytes` and `source_sha256`, then concatenate its inclusive `line_ranges` preserving line endings and compare with the archived excerpt. No runtime/installer is involved. No earlier temporary file or host is required. The handoff records exact checks and limitations for this checkpoint. [Next initial prompt and exact inputs](PHASE-2C-RESUME-PROMPT.md) retain every earlier input and add this boundary.
