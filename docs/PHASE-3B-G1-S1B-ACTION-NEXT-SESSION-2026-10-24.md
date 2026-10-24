# Next session — G1 S1b action proposal

Start a fresh Crewshal session in `/Volumes/X10Pro/Crewshal`.

Milestone: prepare one exact S1b archive verification action for Codex review.
This is planning and offline validation only. Do not attach or mount the image.

Read `AGENTS.md` and `/Users/hamedprooshani/.codex/RTK.md` first.
Then read the current state in `docs/HANDOFF.md`, the current Phase 3B gate in
`docs/DEVELOPMENT-PLAN.md`, and ADR 0009. Read the G1 response record and the
campaign proposal's S1b, section 7, and section 12. Use targeted reads.

Treat the four responses in the export as decision evidence. Decision 3 gives
`20000000000` bytes but gives no exact archive-image attach approval. The
selected floors need a reviewed proposal amendment before a stage uses them.
Keep every campaign stage closed.

Create one draft at
`docs/PHASE-3B-G1-S1B-ATTACH-ACTION-DRAFT-2026-10-24.md`.
Write the exact proposed image path, command, expected result, stop rules,
device capture, blob checks, evidence output, and cleanup. Copy the four blob
sizes and SHA-256 values from proposal lines 180–184. Do not invent a disk
identifier, image-level digest, mount result, or current guest fact.

Use local command help to check syntax. Make a failed attach, missing device,
wrong mount, missing blob, size mismatch, hash mismatch, and failed eject
produce a nonzero result. Eject only the device returned by this attach.
Preserve a failure result during cleanup. Do not hide failures in a pipeline.
Do not use a fixed mount path as proof of the attached device's identity.

Run syntax checks and offline tests with stub commands only. Keep temporary
test files under a new `$TMPDIR` directory and remove that directory after
the tests. Never invoke the real attach or eject command during a test.
Record each command, exit code, and tested refusal. Do not run Linux tests.

Show the exact diff and a concise Codex review packet. Do not commit or push.
Do not request owner approval. Stop for Codex review before any host action.
