---
type: Task
id: CE-114
title: orient compares HEAD with upstream so a push made outside a session is not lost
brief: A push outside any session is recorded nowhere; orient compares HEAD/upstream and says so
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

orient compares HEAD with upstream so a push made outside a session is not lost

What went wrong (adhoc AAR entry 26, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The first push since the cutover is recorded nowhere (entry 26). Have orient compare HEAD with the upstream ref and flag commits pushed or unpushed that no ledger entry covers. Census F17: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F17).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 8c0c5b8,5409b40 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
