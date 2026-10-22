---
type: Task
id: CE-57
title: A guard fails on unmirrored supersedes links, self links and cycles, for stories and decisions
brief: Closes INV-52; both kinds, one check; the ops already write both directions
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

From CE-49's review (2026-10-13c, residual INV-52): `record retire` and `decision supersede` write supersedes and superseded_by both ways, but nothing checks it in the stored files, so a hand edit can leave one side, a self link or a cycle with lint green. Recommendation: one lint check over both kinds, naming the record and the missing side.

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 3a9ee12 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
