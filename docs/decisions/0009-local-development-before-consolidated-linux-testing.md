# 0009 — Local development before consolidated Linux testing

Date: 2026-10-18. Status: accepted through the owner's direct instruction in this chat.

## Context

ADR 0007 separated core software completion from platform qualification.
Phase 2D and Phase 2E software passed local deterministic acceptance on macOS.
Phase 3A froze the source evaluation package under ADR 0008.
Later Phase 3B preparation moved into a separate Ubuntu guest before all intended development was complete.
The owner has now stopped Linux testing during development.

## Decision

Use the owner's local macOS checkout as the main development environment.
Complete remaining source work with local deterministic fixtures, offline checks, static checks, and installed-package checks where relevant.
Do not run Linux tests or Linux qualification during development sessions.
Exclude Linux-specific test modules from local checks and record each omission as deferred.
Do not boot, inspect, reconfigure, reconnect, or install into either VMware Ubuntu guest during those sessions.
Do not use a droplet or retrieve Linux toolchain artifacts for development preparation.
Preserve the existing guests, ISO, records, charges, and unknown outcomes without changing them.

After all planned source development passes its local acceptance gates, prepare one consolidated Linux qualification and test campaign.
The campaign must bind its current inputs, commands, resource limits, transfer and storage ledgers, expected duration, and cleanup.
Seek any required owner decisions for changed scope before that campaign acts.
The earlier qualification approval and Phase 3B limits remain dated records.
They do not reopen Linux work during this local development period.

Local macOS checks establish only the behavior they test.
Local source acceptance must name every deferred Linux check without treating it as a pass.
They do not establish Linux containment, native runtime conformance, provider identity, baseline results, or Phase 3B calibration.
Keep all 192 development rows planned and all 576 sealed rows unexposed until their separate gates pass.
Do not start Phase 3C or claim supported Linux execution from local checks.

## Scope of this amendment

This decision changes development order and the active next-session instructions.
It does not alter frozen Phase 3A package bytes, historical evidence, or unresolved operational limits.
The proposed RAM, infrastructure, retained-data, and transfer amendments remain unapproved and parked.
The approved zero metered billing and zero paid-host limits remain unchanged.
