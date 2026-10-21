---
type: Task
id: CE-123
title: A guards receipt without a gate pass count is refused
brief: A close receipt must carry the gate pass count; refuse a guards receipt that omits it
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

A guards receipt without a gate pass count is refused

What went wrong (adhoc AAR entry 36, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The newest close's receipt had no gate pass count, so the test baseline is unknown (entry 36). Refuse (or lint) a guards receipt that has no gate line. Census F26: NEW, low. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F26).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
