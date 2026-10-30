---
type: Task
id: CE-149
title: record new refuses a decision created with --set status or --set decision_status=SUPERSEDED
brief: Refuse at write time, before any byte, as stories already refuse their twin; G-W4 stays the at-rest check
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

record new refuses a decision created with --set status or --set decision_status=SUPERSEDED

From CE-137's review (session 2026-10-30a): working.py::Engine.record_new accepts `record new decision --set status=deprecated` and `--set decision_status=SUPERSEDED`. The record is created and stamped, and G-W4 (working.py::Engine._decision_status_failures, DEC-112) then goes red. Add a write-time refusal, as stories already have for their twin, naming `decision supersede` in its remedy.

## Traps

## Read first

## Log
