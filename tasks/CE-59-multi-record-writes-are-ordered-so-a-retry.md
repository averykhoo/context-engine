---
type: Task
id: CE-59
title: Multi-record writes are ordered so a retry completes them
brief: Store.update writes records one by one; decision supersede can stop half-written today
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-20e
goals: [G-2]
---

From CE-49's review (2026-10-13c): Store.update's multi-record writes are not atomic. record retire orders its writes (the successor's idempotent link first) so a retry finishes the job; decision supersede and any other multi-record op do not. Recommendation: audit every op that writes two or more records, order each so a retry completes it, and test the second write failing, as tests/test_retire.py does.
