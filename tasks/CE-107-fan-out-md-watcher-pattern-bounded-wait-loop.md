---
type: Task
id: CE-107
title: 'fan-out.md watcher pattern: bounded-wait loop, confirm twice before declaring done'
brief: A haiku watcher must loop with a bounded wait and confirm a finish twice before it reports
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

fan-out.md watcher pattern: bounded-wait loop, confirm twice before declaring done

What went wrong (adhoc AAR entry 6 and 11, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: Both haiku babysitters returned within moments instead of watching (entry 6); the looped version worked but one false alarm cost a sonnet turn (entry 11). Write a Watchers section in fan-out.md: bounded-wait loop, confirm the terminal state twice, never return on first poll. Census F5: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F5).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
