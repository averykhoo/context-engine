---
type: Task
id: CE-113
title: 'Delegated rulings are not stamped actor: owner; separate owner words from a ruling made on delegation'
brief: A ruling taken on delegation must not be stamped owner or sit inside an owner quote (frozen); add ruled_by
pri: NEXT
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-23f
---

Delegated rulings are not stamped actor: owner; separate owner words from a ruling made on delegation

What went wrong (adhoc AAR entry 24, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: A decision taken on the owner's delegation was stamped `actor: owner` and its text sat inside the owner-quote block, which is frozen, so the agent's reasoning became unamendable owner words (entry 24). Separate the owner's words from the ruling, and record who ruled (`ruled_by`, with the delegating quote). Census F16: NEW, severity high. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F16).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23f (claude-code/claude-opus-5-5): Owner, 2026-10-23f (DEC-72): freeze lifted; work CE-113, then CE-93.
