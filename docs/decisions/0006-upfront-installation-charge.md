# ADR 0006: Upfront original-owner installation charge

Status: accepted by the owner on 2026-10-10. The owner answered **“Approve upfront charged bootstrap”** to [the exact installation-bootstrap proposal](../PHASE-2D-INSTALLATION-BOOTSTRAP-DECISION-2026-10-10.md). This grants implementation/preparation authority only. The proposal's earlier pending status is dated history; its bytes and verification remain unchanged.

Permit one installation reservation by the same original observer without a preexisting installed-domain record. Commit the full original charge in a distinct synchronous journal record before installation effects. Its initial state is preparing with installation unknown, never available/free. Keep the existing installed-domain contract and installed-to-retained path unchanged.

Bind one original nonserializable live claim to one original reservation. Keep the store, observer, aggregate, roles, handles, configuration and origin strongly bound through constructor refusal and partial creation. Restart, copied records, changed/missing journals and failed work cannot reconstruct this attempt. Failure or observed installation both consume the full charge; no refund, retry, new capacity, release or reuse follows.

Use the original timer and resource envelope. The original origin precedes preparation; the 600-second batch, 570-second cutoff, 120-second startup, 30-second storage jobs and fixed final 30-second reserve remain unchanged. Keep the original five-second native origin, one-second recovery grace and terminal ordering. No second observer or installation allowance is authorized.

Preparation may proceed from the charge. Native/watchdog/validator admission still requires the same live installer's independent readback of actual retained physical-domain/root/journal identities and every applicable growth/control bound. A record, digest, flag, pathname or successful command cannot provide that proof. If it is unavailable, deny admission and retain all handles, charges and unknowns.

Full Phase 2D acceptance remains unchanged except for this installation prerequisite. ADRs 0003–0005 still govern exact changed-profile Linux qualification, retained terminal storage and the separately reviewed official subscription pilot. No compiler, Linux/runtime/host operation, authentication/model exposure, release, reuse or Phase 2E is approved by this decision.

Current implementation and remaining acceptance: [charged bootstrap source boundary](../PHASE-2D-INSTALLATION-BOOTSTRAP-2026-10-10.md).
