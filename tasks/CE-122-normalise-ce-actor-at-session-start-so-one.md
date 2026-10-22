---
type: Task
id: CE-122
title: Normalise CE_ACTOR at session start so one agent has one spelling
brief: CE_ACTOR is free text and one agent signed under several names; normalise or refuse at session start
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

Normalise CE_ACTOR at session start so one agent has one spelling

What went wrong (adhoc AAR entry 35, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: CE_ACTOR is free text, so the same agent signed under several spellings across a trial (entry 35). Normalise to `<harness>/<model>` at session start, or warn on a spelling that differs from the session's first. Census F25: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F25).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in cb24085 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
