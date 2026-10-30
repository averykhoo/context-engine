---
type: Task
id: CE-160
title: criterion new --id refuses a prefix outside the rows' series
brief: CE-42 residual (f85e632); a foreign prefix blocks every later criterion new
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

criterion new --id refuses a prefix outside the rows' series.

Source: CE-42's close (f85e632), residual. working.py::Engine._free_criterion accepts an --id with a prefix outside the rows' series (REQ-1 in an AC file); every later `criterion new` without --id is then refused with '2 id prefixes'.

## Traps

- none yet

## Read first

- working.py::Engine._free_criterion

## Log
