---
type: Task
id: CE-5
title: "Decision records: amend, correct, supersede, why(), generated index, adhoc importer"
brief: "Append-only by body_sha; the import keeps every id; the index is built from frontmatter, never parsed prose"
pri: LATER
state: open
deps: [CE-1, ASK-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-08a
closed:
---

Build step 4 (FRAMEWORK §6.5): the decision kind and its operations, the generated OKF
`docs/decisions/index.md`, G-D10, and an importer for adhoc's single-file `docs/decisions.md`
(33 entries; headings `### D-n -- title *(actor, date)*`; a "Built and rejected" section that
becomes `decision_status: REJECTED`). Test the importer on a copy; the import itself is CE-7.

## Traps

- `decision.correct` waits on the owner (ASK-2).
- This repo's `docs/decisions/` are hand-written fixtures in the target shape, without
  `body_sha`; stamping them is CE-8.

## Read first

- `docs/framework/FRAMEWORK.md` §6.5, §8.3 (G-D6, G-D10)
- adhoc `docs/decisions.md` (52,624 B on 2026-10-08)

## Log
