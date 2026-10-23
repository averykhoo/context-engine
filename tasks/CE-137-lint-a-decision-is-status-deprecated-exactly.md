---
type: Task
id: CE-137
title: 'Lint: a decision is status: deprecated exactly when it is SUPERSEDED'
brief: a hand-set deprecated on a current decision passes lint and hides it from the doc guards and G-I3
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-23f
---

FRAMEWORK §9.3.1: a decision is `status: deprecated` exactly when it is SUPERSEDED. Its "Not checked:" sentence says no guard compares the two keys, so a hand-set `status: deprecated` on a current decision passes lint, and the doc guards and G-I3 (`guards.py::delegated_rulings`, which treats a deprecated decision as history) skip it. G-W4 does this for board items and G-I2 for stories. Filed by CE-93's fix round.

Build the check (its G-id, or a clause of an existing one), sabotage it (DEC-11), then drop the "Not checked:" sentence from §9.3.1.

## Traps

- An imported decision that was superseded before import: check what `decision.import` writes for it before the guard goes red on real records.

## Read first

- `docs/framework/FRAMEWORK.md` §9.3.1; `guards.py::delegated_rulings`

## Log
