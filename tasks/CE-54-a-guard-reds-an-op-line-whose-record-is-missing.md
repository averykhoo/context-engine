---
type: Task
id: CE-54
title: A guard fails an op line whose record is missing from the stored files
brief: 'Closes INV-44: a by-hand commit can commit an op line without the file it names, and G-W7 cannot see it'
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-20e
goals: [G-2]
---

From CE-45's review (2026-10-13c, residual INV-44): the engine always commits an op line with the files it names, but a by-hand commit can commit ops.jsonl alone, and G-W7 reads moved against the op log without checking that each line's record exists in the stored files. Recommendation: a lint guard that names each op line whose path is absent from the tree, with the by-hand step from manual-mode § Commit the write as the remedy.
