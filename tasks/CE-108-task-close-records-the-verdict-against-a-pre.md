---
type: Task
id: CE-108
title: task close records the verdict against a pre-registered kill bar
brief: A kill bar written before a run must link to the task; close records its verdict (e.g. --verdict)
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

task close records the verdict against a pre-registered kill bar

What went wrong (adhoc AAR entry 7, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: A pre-registered kill bar written by an agent was not linked to the task and needed a coordinator check before the verdict (entry 7). Consider `task close --verdict` and a section that holds the bar so close compares them. Census F6: NEW, low. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F6).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in d9ebc95 (review fixes 91fb1e2; lane a4622c0, a301376), cite in 208a0a8: `## Kill bar` section plus task close --verdict KILL|PASS|VOID: <evidence>; the close refuses a verdict without a bar, a bar without a verdict, and a bar under a heading that differs only in case or spacing, and records the verdict in the Log, reply and commit; a closed item's bar is not rewritten; AC-126 tested; DEC-111
  residual risk: INV-85
