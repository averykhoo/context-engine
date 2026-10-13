---
type: Task
id: CE-57
title: A guard reds unmirrored supersedes links, self links and cycles, for stories and decisions
brief: Closes INV-52; both kinds, one check; the ops already write both directions
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

From CE-49's review (2026-10-13c, residual INV-52): `record retire` and `decision supersede` write supersedes and superseded_by both ways, but nothing at rest checks it, so a hand edit can leave one side, a self link or a cycle with lint green. Recommendation: one lint check over both kinds, naming the record and the missing side.
