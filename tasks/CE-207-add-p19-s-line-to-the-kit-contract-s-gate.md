---
type: Task
id: CE-207
title: Add P19's line to the kit contract's Gate section at the next contract version bump (CE-194)
brief: 'Wait for a version bump: changing it now turns G-D0 red in every adopting repo'
pri: LATER
state: open
deps: []
goals: [G-3, G-7]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Add P19's line to the kit contract's Gate section at the next contract version bump (CE-194).

FRAMEWORK §1 P19 (CE-194, US-20) makes a green gate the whole release decision. The kit contract does not say so, and changing `src/context_engine/kit/contract.md` now, without a version bump, turns G-D0 red in every adopting repo (CE-132's 0.6 bump is done). Add the line at the next contract version bump, in both `src/context_engine/kit/contract.md` and `docs/framework/contract.md`, byte-equal.

Suggested line, for the contract's Gate section: "A green gate is the whole release decision (FRAMEWORK P19): a check only a human runs is a board item to automate, never an accepted residual."

## Traps

- Not before a contract version bump: G-D0 compares an adopting repo's contract with the installed kit's.

## Read first

- docs/framework/FRAMEWORK.md (§1 P19)
- src/context_engine/kit/contract.md (§ Gate)

## Log
