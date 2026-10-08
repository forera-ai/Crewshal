# Repository ownership transfer checkpoint

Date: 2026-10-08. Scope: repository identity and ownership maintenance only.

## Current identity

The owner reported transfer of the existing repository to [forera-ai/Crewshal](https://github.com/forera-ai/Crewshal). The project is owned and maintained by [forera-ai](https://github.com/forera-ai). Local `origin` fetch and push use `https://github.com/forera-ai/Crewshal.git`. GitHub API readback confirms the exact owner/name and default branch `main`.

README clone/ownership instructions, package maintainer/URL metadata, AGENTS.md and the rolling handoff adopt this identity. ADR 0001 keeps its original rename evidence with a dated ownership update. The license and original contributor copyright notices remain intact. Dated historical URLs are evidence of earlier ownership, not current publishing instructions.

Version 0.9.1 is a patch for documentation/metadata maintenance. Base revision: `211538c86b13edf8971b6fc0de7e121d47fc3cf9`. Delivery revision is reproducible with `rtk proxy git log -1 --format=%H -- docs/REPOSITORY-TRANSFER-2026-10-08.md`. The current branch is `codex/phase1-architecture`; publish it to the new `origin` under standing owner authorization, then compare local HEAD with remote branch readback. Merge, deployment and registry release remain separately gated.

## Acceptance and limits

Verified on the existing macOS arm64 checkout using RTK and Python 3.14.8 (`python3`). The existing development virtual environment reports Python 3.12.15:

```sh
rtk proxy gh api repos/forera-ai/Crewshal --jq '{full_name: .full_name, owner: .owner.login, html_url: .html_url, default_branch: .default_branch}'
rtk proxy git remote get-url origin
rtk proxy git remote get-url --push origin
rtk proxy python3 - <<'PY'
from pathlib import Path
import runpy
import tomllib
project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
assert project["version"] == runpy.run_path("src/crewshal/__init__.py")["__version__"] == "0.9.1"
assert project["maintainers"] == [{"name": "forera-ai"}]
assert project["urls"]["Repository"] == "https://github.com/forera-ai/Crewshal"
assert "git clone https://github.com/forera-ai/Crewshal.git" in Path("README.md").read_text()
assert "prooshani/Crewshal" not in Path("README.md").read_text()
print("Ownership and version checks passed")
PY
rtk proxy git diff --cached --check
rtk proxy git ls-remote origin refs/heads/codex/phase1-architecture
```

Identity, metadata/version, staged whitespace and unchanged unrelated-byte checks pass. The session captures 782 tracked/non-ignored files before editing, compares all pre-existing unrelated file hashes afterward, and stages ownership-only transformations of HEAD instead of staging whole dirty files. Existing Phase 2D source, tests, preparation/qualification records and documentation edits remain uncommitted; none are included in this maintenance checkpoint. Their earlier version/source bindings are historical and are not refreshed or transferred by this patch bump. No runtime behavior changes, Linux/VMware checks, model/Jev calls, paid-host tests or live qualification are part of this milestone. The full acceptance suite is not rerun for documentation/metadata maintenance.

## Next session

Resume Phase 2D preparation only in a separate session. The existing local retained-native-admission boundary remains incomplete: envelope/bootstrap, effective storage/role/credential/egress/deadline enforcement, durable admission linkage, fresh exact qualification and separately approved live implementation/check remain missing.

Initial prompt: “Use `forera-ai/Crewshal` and `origin` at `https://github.com/forera-ai/Crewshal.git`. Read the ownership checkpoint, AGENTS.md, HANDOFF.md and DEVELOPMENT-PLAN.md. Resume only the latest local Phase 2D preparation boundary from its continuation and exact input list. Preserve all unrelated dirty work and historical evidence. Respect existing execution/spend gates; do not start Phase 2E. Keep versions/source bindings explicit after the 0.9.1 maintenance checkpoint.”

Feed these exact files from the existing checkout: `AGENTS.md`, `docs/REPOSITORY-TRANSFER-2026-10-08.md`, `docs/HANDOFF.md`, `docs/DEVELOPMENT-PLAN.md`, `docs/ARCHITECTURE.md`, `docs/decisions/0002-minimal-architecture.md`, `docs/decisions/0003-direct-linux-qualification.md`, and the local uncommitted `docs/PHASE-2D-CONTINUATION-2026-10-08.md` with every input it names. A fresh clone does not contain the unpublished Phase 2D continuation or implementation; use the committed `docs/PHASE-2D-NEXT-SESSION-2026-10-08.md` there and do not claim the local unpublished boundary is present.
