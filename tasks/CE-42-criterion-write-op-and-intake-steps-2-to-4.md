---
type: Task
id: CE-42
title: Criterion write op and intake steps 2 to 4 tooling
brief: Rewrites or appends one row under the lock; setting tested refuses unless G-T2 finds a claim
pri: LATER
state: open
deps: [CE-25]
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
---

Split from CE-25 by DEC-33 (owner, 2026-10-13b): the write-op half. CE-25's design review covers it: see its rows on the criterion write op (byte-identical outside the row, under the store lock, an op-log line; tested refuses unless G-T2 finds a claim) and intake steps 2 to 4. Criteria stay rows of docs/criteria.md (DEC-33). Needs review: [write-op, shipped] and its own design review before promote.
