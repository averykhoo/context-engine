---
type: Task
id: CE-117
title: 'sabotage.md Traps: never sabotage a file a running job imports'
brief: Sabotage runs must not edit a file a running job imports; add the trap to sabotage.md
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

sabotage.md Traps: never sabotage a file a running job imports

What went wrong (adhoc AAR entry 29, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: A sabotage run edited a file that a running job then imported, corrupting the job (entry 29). Add a Traps entry to docs/runbooks/sabotage.md (and the kit copy): sabotage in a copy or when nothing running imports the file; check for running jobs first. Census F20: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F20).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
