---
type: Task
id: CE-155
title: Refuse a bad or expired stale_after at write time
brief: CE-136 residual (a7f128b); today only lint and the gate go red afterwards
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

Refuse a bad or expired stale_after at write time.

Source: CE-136's close (a7f128b), residual. `record new --set stale_after=2026-10-01` writes; only lint and the gate go red afterwards.

## Traps

- none yet

## Read first

- guards.py::stale

## Log
