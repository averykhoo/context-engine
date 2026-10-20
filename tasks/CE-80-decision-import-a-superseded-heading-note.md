---
type: Task
id: CE-80
title: 'decision import: a SUPERSEDED heading note cannot be undone after import'
brief: Import turns 'SUPERSEDED by D-n' into status+link; decision set refuses SUPERSEDED and no op removes a link
pri: LATER
state: open
deps: []
source: session 2026-10-14d
created: 2026-10-14
moved: 2026-10-14d
updated: 2026-10-20e
goals: [G-6]
---

Seen in the adhoc trial (CE-7, 2026-10-14d): adhoc's D-27 note read "SUPERSEDED by D-29 for the gate backend; the permissive rule stands", but the owner wanted BUILT with D-29 narrowing it (DEC-28). After import nothing could change it: `working.py::decision_set` refuses a SUPERSEDED status and no operation removes an id link. The fix used was to reword the source note to "narrowed by D-29" before importing (adhoc DEC-68). Options: an import flag that overrides a note's relation (`--as D-27=relaxes`), or make the dry run's table flag every note-derived SUPERSEDED for review before the real import.

## Traps

- none yet

## Read first

- `src/context_engine/decisions.py::plan_import`; adhoc's DEC-68

## Log
