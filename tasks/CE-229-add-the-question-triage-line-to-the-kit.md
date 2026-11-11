---
type: Task
id: CE-229
title: Add the question triage line to the kit contract's Who decides rule at the next contract version bump (CE-217)
brief: 'Wait for a version bump: changing it now turns G-D0 red in every adopting repo'
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-11a
created: 2026-11-11
moved: 2026-11-11a
updated: 2026-11-11a
---

Add the question triage line to the kit contract's Who decides rule at the next contract version bump (CE-217).

FRAMEWORK §5.3 (CE-217, US-24, DEC-325) now triages a question before it reaches the owner: derivable from the owner's recorded intent, decided as a PROVISIONAL agent decision with the arbiter's second opinion; cheap to undo, decided anyway; the rest asked. The kit contract's Who decides rule does not say so, and changing `src/context_engine/kit/contract.md` now, without a version bump, turns G-D0 red in every adopting repo: G-D0 compares an adopting repo's contract with the installed kit's (DEC-310 is the precedent, CE-207 its sibling). Add the line at the next contract version bump.

Suggested line, for the contract's Who decides rule: "Before raising a question, decide it as a PROVISIONAL agent decision if it follows from the goals or the owner's decisions (with the arbiter's opinion, `ask decide` for one already open), or if it is cheap to undo; what remains goes to the owner with context and a recommendation."

Add it in both `src/context_engine/kit/contract.md` and `docs/framework/contract.md`, byte-equal.

## Traps

- Not before a contract version bump.

## Read first

- docs/framework/FRAMEWORK.md (§5.3, Triage before raising)
- src/context_engine/kit/contract.md (§ Rules, Who decides)

## Log
