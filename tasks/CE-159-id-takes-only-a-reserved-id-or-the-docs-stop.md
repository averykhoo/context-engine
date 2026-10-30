---
type: Task
id: CE-159
title: --id takes only a reserved id, or the docs stop saying so; one id reserved twice is caught
brief: CE-105 residuals (9e7c1d0); ids never collide today, a series can jump
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

--id takes only an id this session reserved, or the docs stop saying so; two sessions reserving one id is caught.

Source: CE-105's close (9e7c1d0), residuals.
- `record new --id` (and `task new` and `ask new --id`) accepts any never-used id, not only one this session reserved, while the cli.py help and manual-mode § context-engine record new step 1 say it must be reserved; a series can jump, ids never collide (verifier probe: DEC-50 accepted unreserved, next new gave DEC-51).
- No lint catches one id reserved by two sessions, possible only when worktree op logs merge (store.py::Store.reserved_ids keeps the first line).

## Traps

- none yet

## Read first

- store.py::Store.reserved_ids
- ops.py::id_reserve

## Log
