---
type: Task
id: CE-115
title: Lint flags a HANDOFF rest that cites a closed next item or an answered ASK
brief: HANDOFF.md rest goes stale after banner set/close; lint must catch a closed next or answered ASK
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-23a
updated: 2026-10-23a
status: deprecated
closed: 2026-10-23a
---

Lint flags a HANDOFF rest that cites a closed next item or an answered ASK

What went wrong (adhoc AAR entry 27, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: `banner set` and `session close` leave the rest of HANDOFF.md stale, and lint is blind to it (entry 27). Lint should fail a HANDOFF line that names a closed task as next or an answered ASK as open. Census F18: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F18).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 635c0a7 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
