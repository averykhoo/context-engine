---
type: Task
id: CE-106
title: Document that workflows cannot express dependencies across runs; sequencing is the coordinator's
brief: State in fan-out.md that cross-run dependencies are sequenced by the coordinator, not a workflow
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

Document that workflows cannot express dependencies across runs; sequencing is the coordinator's

What went wrong (adhoc AAR entry 5, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: AD-13's fresh render needed an earlier workflow's output, and workflows cannot express a dependency across runs. Add a note to docs/runbooks/fan-out.md (and the kit copy) saying the coordinator sequences runs and passes outputs by file. Census F4: NEW, doc only. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F4).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
