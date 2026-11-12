---
type: Task
id: CE-234
title: Report a record or criterion the op log never shows created (muse's hand-made CE-231/232, AC-208)
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-12b
created: 2026-11-13
moved: 2026-11-12b
updated: 2026-11-12b
---

Lint passes a record the op log never shows created.

**Why:** muse (an agent without the engine) wrote CE-231, CE-232 and AC-208 by hand in bc9f1c3
and 63db00b: no `new` or `criterion.new` op lines, AC-208 straight to `tested`, both tasks left
`state: open` under a hand-written "closed" log line. `context-engine lint` stayed clean
(2026-11-12b). Housekeeping caught the commits as foreign only because they lacked a `Session:`
trailer; a hand-made record inside an agent commit would pass unseen.

**What:** decide whether lint (or `hk run start`) should report a board item, record or criterion
row whose id no op line creates, and a task log line saying "closed" on an open item; the by-hand
path (manual-mode) must stay legal, so the remedy may be an op that adopts a hand-written record
rather than a refusal.

## Traps

## Read first

- ledger entry 2026-11-12c (the foreign commits)

## Log
