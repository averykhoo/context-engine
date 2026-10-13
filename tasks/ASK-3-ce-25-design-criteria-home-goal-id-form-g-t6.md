---
type: Question
id: ASK-3
title: 'CE-25 design: criteria home, goal id form, G-T6 actor, G-T1 landing red, split'
brief: Five design calls CE-25's review left to the owner; each has a recommendation
pri: NEXT
state: open
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-13a
updated: 2026-10-13a
last_asked: 2026-10-13a
blocks: [CE-25]
---

Raised in chat 2026-10-13a from CE-25's design review (commit 2c7b951). The session's recommendation follows each question.

1. **Where criteria live:** rows of `docs/criteria.md`, or a criterion record kind? Recommended: rows (lighter, hand-editable). A record kind adds `record-kind` to CE-25's triggers and redoes the review.
2. **Goal id form:** `docs/charter.md` and every story use `G1`; rituals.md § Intake step 2 and § Bootstrap step 3 say `G-n`. Recommended: keep `G<n>`, fix both runbook copies.
3. **G-T6 actor match:** `docs/criteria.md` has no actor column. Add one, or amend FRAMEWORK §8.2 so a criterion's actor is its source's and G-T6 checks only that references resolve? Recommended: the actor comes from the source.
4. **G-T1 lands red:** US-10, US-12 and US-13 are live with no criterion. Draft planned criteria for them, or mark them `unspecified` with a board task (needs a new op for a story's frontmatter)? Recommended: draft planned criteria.
5. **Split CE-25?** (a) the five guards (G-I1, G-I2, G-T1, G-T2, G-T6; the §11.1 minimum-set ones among them), (b) the criterion write op and intake steps. Recommended: split; (a) first, which drops the `write-op` trigger from it.
