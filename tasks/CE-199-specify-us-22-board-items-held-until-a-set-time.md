---
type: Task
id: CE-199
title: 'Specify US-22: board items held until a set time, done only at or after it'
brief: Specify first (criteria under US-22); the build is a separate task
pri: LATER
state: open
deps: []
goals: [G-3]
source: session 2026-11-07d
created: 2026-11-07
moved: 2026-11-07d
updated: 2026-11-07d
---

Specify US-22: how a board item can be held until a set time, and done only at or after it.

Source: US-22 (owner, 2026-11-07d), recorded `unspecified`; this task specifies it (G-T1), then the build is filed separately.

Questions to settle, with a recommendation each (the owner rules on anything not cheap to undo):
- What "scheduled" means here: a board item that is not workable before a time (a not-before field that orient, `task list` and the NOW/NEXT tiers respect), or a Claude Code scheduled run that wakes a session at that time to do it, or both (the field as the record, a scheduled run as an optional trigger).
- Where the time lives (a frontmatter field such as `not_before`, owned by an op like `task set`), its format and time zone, and what lint checks (G-5: a hand edit stays legal).
- What happens when the time passes: orient surfaces it (like "Rerank due"), it is promoted, or a housekeeping row does it (G-3: no judgement in `hk_`).
- How it interacts with the tier caps (NOW exactly one, NEXT at most five) and with CE-34's "scheduled routine" for G-T5.

Output: criteria under US-22 (`criterion new --from US-22`), the story confirmed live, and a build task filed.

## Traps

- none yet

## Read first

- US-22
- tasks/CE-34-g-t5-mutation-per-criterion-as-a-scheduled-or.md
- working.py::Engine.orient (the "Rerank due" part)

## Log
