---
type: Task
id: CE-120
title: task close asks about residual risk, and register show works on a repo that has no register
brief: task close must prompt for residual risk; the register must exist or be created on first use
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

task close asks about residual risk, and register show works on a repo that has no register

What went wrong (adhoc AAR entry 33, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The residual-risk register was never created; `register show` refuses 'no register' and `task close` never asks for a residual (entry 33). Make close ask (or accept `--residual`) and create the register on first entry. CE-23 (design) is closed; this is the unbuilt part. Census F23: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F23).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
