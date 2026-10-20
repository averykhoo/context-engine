---
type: Task
id: CE-34
title: 'G-T5: mutation per criterion as a scheduled or background job'
brief: Un-defer when the §11.2 trigger "the suite is large" is hit; the hand sabotage tables cover it until then
pri: SOMEDAY
state: open
deps: [CE-14]
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-12d
updated: 2026-10-20e
goals: [G-2]
---

Split from CE-14 (2026-10-12d). FRAMEWORK §8.2 G-T5: mutation per criterion, run as a scheduled routine or the one slow background job, keyed on the hash, results in a tracked evidence doc; it mechanises the hand sabotage of P7 (`CLAUDE.md` § Sabotage rule, DEC-11). Not for formal theorems (G-T4 substitutes).

Until it exists, each task keeps a by-hand sabotage table (`tools/sabotage_<task>.py`, the Sabotage probes route). Those tables are the seed: each row is a mutation with the test that must go red.

## Traps

- Fresh bytecode cache per mutation run (PYTHONPYCACHEPREFIX), or a same-length mutation runs the stale .pyc (2026-10-08d).

## Read first

- `docs/framework/FRAMEWORK.md` §8.2 G-T5, §11.2 ("the suite is large")
- `tools/sabotage_ce14.py`

## Log
