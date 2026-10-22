---
type: Task
id: CE-59
title: Multi-record writes are ordered so a retry completes them
brief: Store.update writes records one by one; decision supersede can stop half-written today
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-2]
status: deprecated
closed: 2026-10-23a
---

From CE-49's review (2026-10-13c): Store.update's multi-record writes are not atomic. record retire orders its writes (the successor's idempotent link first) so a retry finishes the job; decision supersede and any other multi-record op do not. Recommendation: audit every op that writes two or more records, order each so a retry completes it, and test the second write failing, as tests/test_retire.py does.

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 484e39d (sweep 2026-10-23a; verified by an independent agent, gate green on main)
