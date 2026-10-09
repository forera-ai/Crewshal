# Phase 2D Sol6.1 batch preparation — October 8, 2026

Status: **prepared offline; not executable or qualified**. Phase 2D remains incomplete and 2E stays closed. Package remains 0.9.0; working changes are uncommitted. The owner selected “Sol6.1 / approved”, then clarified **“Batch preparation only.”** That clarification controls scope: no native runtime startup, provider/model request, credential-store access, billing/quota spending, VMware/SSH operation or publication is authorized by this preparation.

## Reviewable result

[Preserved preparation record](qualification/phase-2d-batch-preparation-v1-20261008.json), SHA-256 `b08afc86a6146acce8c4947874b833f699d65495eac7bc3c7f2ebe4ed1ae6bd1`, contains the owner scope, a closed preparation manifest, all eleven generated artifact bodies as UTF-8 data and their SHA-256 values. It also pins eight unchanged historical v18/protocol/cleanup references and the three new producer/test sources. Those references prove continuity only; they do not qualify the new model/upstream/dispatch identity. Nothing in this record is imported as execution authority.

The generated bundle contains:

- Original `README.md` with exact bytes `phase-2d-before\n`, a separate uncommitted marker and clearly synthetic original Git metadata. Its live Git identity remains unresolved. The disposable candidate includes only README; no Git metadata, original marker, home or coordinator state is part of its intended worker grant.
- Neutral documentation-only requirement: change README to exactly `phase-2d-after\n`, with no other path change. Initial candidate manifest and original integrity hashes are captured; the expected output is separately bound.
- Exact standalone `check_fixture.py` source that checks candidate README bytes without importing candidate code. Proposed readonly-validator argv is `[/bin/python3, -I, -B, /input/check_fixture.py, /candidate/owned]`, cwd `.`. Linux executable/library identity and approved command/environment/toolchain digests still need fresh binding. The check script is data until separately approved validator execution.
- Original worker/validator, aggregate, candidate/scratch, stream/startup/capture/batch/cleanup ceilings, one implementation attempt and zero automatic retries. No additional financial ceiling is invented or inferred.
- A dispatch **template**, including pinned native CLI tail, neutral task stdin, check argv, disabled inherited customization requirements, validator UID/read-only/credential/network requirements and the existing mechanism names. Production envelope argv, loaded roles/helpers, observed namespace PID/birth, exact provider destination, credential channel, billing/quota enforcement, effective configuration, fresh qualification and execution/spend records are explicitly `null`. This template cannot launch a process.

OpenAI's official model page identifies GPT-6.1 Sol as `gpt-6.1-sol`, supports Responses tool calling and lists `low`, `medium`, `high`, `xhigh`, `max` reasoning settings. This supports the documented mapping of the owner's label; it does **not** prove pinned Codex 0.160.1/account availability, select a provider route, authorize egress or establish billing mode. No reasoning override or auth fallback is chosen. [Official model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)

The model-page Markdown fetch returned an internal error; the actual HTML page was opened and its relevant model section read instead. Current authentication documentation was also read as comparison evidence; no login/cache/store operation or credential-copy instruction was executed. It does not qualify the pinned boundary or provide a selected credential treatment. [Official Codex authentication documentation](https://learn.chatgpt.com/docs/auth)

## Reproduce preparation safely

[Source](../src/crewshal/runtime_batch.py) and [offline utility](../scripts/prepare_phase_2d_batch.py) read bounded coordinator-selected historical references, verify their bytes before writing, and create a fresh private external bundle. They invoke no runtime, shell, network, model, dependency preparation or credential API. Exit zero means preparation data was written, not execution or qualification. Existing outputs, reference mutations/misses/aliases/symlinks and output/source overlap refuse. Failed copies remain available for inspection; caller-owned directories are never deleted.

From the recorded development environment:

```sh
crewshal_prepare_dir=$(rtk proxy mktemp -d /private/tmp/crewshal-2d-preparation.XXXXXX)
rtk proxy .venv/bin/python -c 'import json,sys; from pathlib import Path; record=json.loads(Path("docs/qualification/phase-2d-batch-preparation-v1-20261008.json").read_text()); Path(sys.argv[1]).write_text(json.dumps(record["bundle"]["historical_references"], indent=2)+"\n")' "$crewshal_prepare_dir/references.json"
rtk proxy .venv/bin/python -m scripts.prepare_phase_2d_batch --reference-root "$PWD" --references "$crewshal_prepare_dir/references.json" --output "$crewshal_prepare_dir/bundle"
rtk proxy .venv/bin/python -m unittest tests.acceptance.test_phase_2d_batch
```

Do not start the native tail, materialize privileged Linux roles or request model output from this bundle. The owner authorized preparation only. The new producer is independent of the 2C qualification driver and does not wrap, import or execute its code.

## Fresh verification and remaining boundary

[Seven fresh tests](../tests/acceptance/test_phase_2d_batch.py) create their own reference files, repositories and outputs. They verify all generated artifact hashes/private modes, original/candidate isolation, fixed ceilings/unresolved authority, changed/missing/duplicate/symlink reference refusal, existing/overlapping output refusal, inert declared Python, utility success/refusal, and the standalone synthetic byte check. The check smoke uses CPython on fresh local fixture bytes and proves rejection of original/missing/false-completion content plus acceptance of exact expected bytes. It does not demonstrate a Linux readonly validator, native runtime or provider access.

Complete editable suite: **174 passed in 5.194s** under macOS denied network and empty inherited environment. Lint/format pass; strict mypy covers 14 source files. Final installed-wheel suite: **174 passed in 8.789s**, with current producer bytes resolving to external site-packages. [Verification/continuity record](qualification/phase-2d-batch-preparation-verification-v1-20261008.json) and the handoff retain exact evidence. Earlier 167-test evidence remains historical. Initial static typing rejected a Literal constant default; the default was corrected without changing generated fixture bytes. No native/paid failure is hidden by that source correction.

Codebase-memory Verify confirmed the project at resumption and relevant original source coverage at generation `2026-10-08T13:06:50Z`. New producer/utility/test coverage matched generation `2026-10-08T13:15:30Z`; coverage is best-effort, not completeness. Exact source inspection supplies the material behavior. RTK, Caveman and code-work remain applied; OpenAI Docs supplies the read-only model mapping. No paid Jev call is requested.

Next work remains **2D**: resolve owner-selected billing/quota/credential/egress treatment, complete and prospectively bind production supervision through existing mechanisms, qualify the changed exact profile, then present a concrete execution/spend batch for separate recorded owner approval. The selected model and preparation-only scope are resolved; do not ask those same questions again. The five-second deadline and other original limits stay unchanged. No paid host, new runtime/model/tool loop, custom gateway, credential-store recovery, 2E or evaluation. See [execution gate](PHASE-2D-EXECUTION-GATE.md) and [continuation/exact inputs](PHASE-2D-CONTINUATION-2026-10-08.md).
