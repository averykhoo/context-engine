---
type: Task
id: CE-101
title: Wire foreign_commits into orient or start-of-session housekeeping
brief: CE-65 built ledger.py::foreign_commits; nothing calls it yet
pri: LATER
state: open
deps: []
source: session 2026-10-20b
created: 2026-10-20
moved: 2026-10-20b
updated: 2026-10-20e
goals: [G-3]
---

From CE-65 (5775bf5): ledger.py::foreign_commits gives each session its range of foreign commits from the start heads, but only the tests and the by-hand recipe in procedures § Reconciling foreign commits use it. Wire it into orient (a 'foreign commits to reconcile' section) or the start-of-session housekeeping, so a session sees its range without running git by hand. Known gap (FRAMEWORK §6.10): a session that dies before reconciling leaves its range unreconciled; an orient section could also list the ranges of abandoned sessions.
