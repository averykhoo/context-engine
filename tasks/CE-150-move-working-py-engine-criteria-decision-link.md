---
type: Task
id: CE-150
title: Move working.py::Engine._criteria (decision link) onto guards.py::criteria_rows
brief: It reads CRITERION_ROW_RE over raw text, counting ids in fenced code and non-criteria tables (CE-42 review D5)
pri: LATER
state: open
deps: [CE-42]
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

Move working.py::Engine._criteria (decision link) onto guards.py::criteria_rows.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): Declined in CE-42 because CE-41 cites working.py::Engine._criteria and tools/sabotage_ce5.py mutates it; both move with it. Same root (CE-25's one-parser row M): working.py::Engine.criterion_ids/_next_criterion use CRITERION_ROW_RE, which misses an indented '  | AC-5 |' row guards.py::criteria_rows reads, so the next id can fall below it (CE-42 verifier nit; the read-back still refuses a real duplicate).
- 2026-10-30a (claude-code/claude-opus-5-5): Correction to the line above: the method is working.py::Engine._criterion_ids (read by Engine._next_criterion), not Engine.criterion_ids.
