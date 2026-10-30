---
type: Task
id: CE-107
title: 'fan-out.md watcher pattern: bounded-wait loop, confirm twice before declaring done'
brief: A haiku watcher must loop with a bounded wait and confirm a finish twice before it reports
pri: LATER
state: closed
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

fan-out.md watcher pattern: bounded-wait loop, confirm twice before declaring done

What went wrong (adhoc AAR entry 6 and 11, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: Both haiku babysitters returned within moments instead of watching (entry 6); the looped version worked but one false alarm cost a sonnet turn (entry 11). Write a Watchers section in fan-out.md: bounded-wait loop, confirm the terminal state twice, never return on first poll. Census F5: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F5).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 55c47ec and 189c1cd: fan-out.md Watchers: never return on the first poll, one bounded wait per watcher, confirm a terminal state twice a minute apart, loop in deterministic code; Fan-out route cap raised to 110 lines (DEC-86).
