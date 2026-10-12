---
type: Task
id: CE-16
title: "Coverage map: every FRAMEWORK component, ritual and guard mapped to a task, prose-only, or deferred"
brief: "G7's measure; read-only census of FRAMEWORK.md against the board; files tasks for the gaps"
pri: NEXT
state: open
deps: []
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-08b
updated: 2026-10-12b
closed:
---

The board was scoped to the record engine; the charter is now the whole framework (DEC-10,
G7). Walk FRAMEWORK.md §2 to §11 and map each component, ritual (§6.1 to §6.11, the §5.6
digest) and guard to one of: an existing CE item, a new CE item, deliberately prose-only (a
`CLAUDE.md` rule or a skill, with the reason), or deferred (with the reason). Write the map as
`docs/evidence/framework-coverage-2026-10-08.md` and file the new items.

Known gaps when filed: the rituals beyond session start, close and pause (intake, decision
recording, delegation rounds, promotion, push and CI, the owner digest); the deviation
register, archive and runbooks; stories, criteria and charter tooling.

## Traps

- FRAMEWORK.md is 112 KB: delegate the reading, keep the map (global CLAUDE.md § Delegation).
- Do not add rows past the NEXT cap of 5; new items go to LATER unless they unblock NOW.

## Read first

- `docs/charter.md` (G7)
- `docs/framework/FRAMEWORK.md` §2 (components at a glance), §6, §8, §11

## Log

- 2026-10-12b (claude-code/claude-opus-5-5): Map: docs/evidence/framework-coverage-2026-10-12.md (FROZEN 2026-10-12b), 76 rows (23 components, 14 rituals, 39 guards incl. schema); filed CE-25..CE-30. Date renamed from the body's 2026-10-08 to the census day 2026-10-12. Id coverage checked by a one-off diff against FRAMEWORK.md (sabotaged: dropping the G-W5 row was reported). Deviations from plan: bootstrap §6.9 maps to CE-15 (its brief names it); §6.5 to CE-5; deviation register, law/NFRs and G-T7 DEFERRED on their §11.2 triggers; §6.10 to CE-12.
