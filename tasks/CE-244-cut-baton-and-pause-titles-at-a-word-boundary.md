---
type: Task
id: CE-244
title: Cut baton and pause titles at a word boundary; the brief refusal says what to cut; the cap remedy names task promote
pri: LATER
state: open
deps: []
goals: [G-3]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

Refusal remedies and cut titles: baton and pause titles cut at a word boundary, the brief refusal names the cut, the cap remedy names `task promote`.

docs/evidence/engine-feedback-2026-11-17.md, F17 and F29 (adhoc AD-112 items 17 and 29):
1. working.py::Engine.baton_add and the pause title cut at `[:100]`, mid-word: cut at a word boundary with an ellipsis (the expired-baton task title in working.py::Engine._hk_expire likewise, F25's cut).
2. The `--brief` refusal gives only the length: say what to cut, or by how much.
3. working.py::Engine._cap_check's remedy says `promote <id> LATER`, which is no command: say `task promote <id> LATER`.

## Traps

- One string fix and two cuts: small, do them together; sabotage each (DEC-11).
- The housekeeping title cut stays mechanical (DEC-68): no judgement about what to keep.

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F17, F25, F29
- working.py::Engine.baton_add, working.py::Engine._cap_check, working.py::Engine._hk_expire

## Log
