---
type: Task
id: CE-104
title: orient shows when each open session last did anything, not only when it opened
brief: 'A dead session must not look live in orient: show last activity per open stub'
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-22b
updated: 2026-10-22b
status: deprecated
closed: 2026-10-22b
---

orient shows when each open session last did anything, not only when it opened

What went wrong (adhoc AAR entry 1, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: orient lists other open sessions with only an `opened` time, so a dead session looks as live as a working one. Show last activity (newest ledger/op/commit line carrying that session key). DEC-29 mentions a last-seen window but nothing is built. Census F1: NEW; relates to CE-6 (stale stubs) and DEC-29. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F1).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-22b (claude-code/claude-opus-5-5): closed: done in 70e3450
