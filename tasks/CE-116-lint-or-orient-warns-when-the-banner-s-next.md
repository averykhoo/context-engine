---
type: Task
id: CE-116
title: Lint or orient warns when the banner's next task depends on a SOMEDAY task
brief: Banner 'next' that is blocked by a SOMEDAY dependency must be flagged, not silent
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-23a
updated: 2026-10-23a
status: deprecated
closed: 2026-10-23a
---

Lint or orient warns when the banner's next task depends on a SOMEDAY task

What went wrong (adhoc AAR entry 28, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The owner's next task was blocked on a parked (SOMEDAY) task and nothing flagged it (entry 28). Add a warning in orient or a lint check for a banner next whose deps include a SOMEDAY or closed-unsatisfied item. Census F19: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F19).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in c6aeebd (sweep 2026-10-23a; verified by an independent agent, gate green on main)
