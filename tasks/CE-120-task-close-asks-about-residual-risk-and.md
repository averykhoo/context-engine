---
type: Task
id: CE-120
title: task close asks about residual risk, and register show works on a repo that has no register
brief: task close must prompt for residual risk; the register must exist or be created on first use
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

task close asks about residual risk, and register show works on a repo that has no register

What went wrong (adhoc AAR entry 33, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The residual-risk register was never created; `register show` refuses 'no register' and `task close` never asks for a residual (entry 33). Make close ask (or accept `--residual`) and create the register on first entry. CE-23 (design) is closed; this is the unbuilt part. Census F23: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F23).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 750aff7 (review fixes 8fe039d; lane 1a89d74, 73da625), cite in 208a0a8: task close --residual (none, or one-line risk lines filed as INV-n, register created on first use); `none` refused when the design review lists residuals; the Log names every INV id filed and those already in the register; a reply nudge when nothing is stated; register show reads a missing register as empty; AC-127 tested; DEC-108, DEC-109, DEC-110
  residual risk: none
