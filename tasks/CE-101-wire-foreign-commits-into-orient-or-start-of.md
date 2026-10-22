---
type: Task
id: CE-101
title: Wire foreign_commits into orient or start-of-session housekeeping
brief: CE-65 built ledger.py::foreign_commits; nothing calls it yet
pri: LATER
state: closed
deps: []
source: session 2026-10-20b
created: 2026-10-20
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-3]
status: deprecated
closed: 2026-10-23a
---

From CE-65 (5775bf5): ledger.py::foreign_commits gives each session its range of foreign commits from the start heads, but only the tests and the by-hand recipe in procedures § Reconciling foreign commits use it. Wire it into orient (a 'foreign commits to reconcile' section) or the start-of-session housekeeping, so a session sees its range without running git by hand. Known gap (FRAMEWORK §6.10): a session that dies before reconciling leaves its range unreconciled; an orient section could also list the ranges of abandoned sessions.

## Log

- 2026-10-21b (claude-code/sonnet): Concurrent-session risk (adhoc AAR entry 22, docs/evidence/adhoc-feedback-2026-10-21.md; census F15): a dead session's uncommitted op lines went into the next session's first commit; CE-45 (closed) sweeps all uncommitted op lines by design. Consider defaulting commit to the committing session's own lines and surfacing foreign ones in orient.
- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 06c080c (sweep 2026-10-23a; verified by an independent agent, gate green on main)
