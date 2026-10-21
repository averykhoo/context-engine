---
type: Task
id: CE-114
title: orient compares HEAD with upstream so a push made outside a session is not lost
brief: A push outside any session is recorded nowhere; orient compares HEAD/upstream and says so
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

orient compares HEAD with upstream so a push made outside a session is not lost

What went wrong (adhoc AAR entry 26, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The first push since the cutover is recorded nowhere (entry 26). Have orient compare HEAD with the upstream ref and flag commits pushed or unpushed that no ledger entry covers. Census F17: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F17).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
