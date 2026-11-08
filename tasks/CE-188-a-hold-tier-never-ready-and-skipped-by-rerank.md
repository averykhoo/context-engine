---
type: Task
id: CE-188
title: 'A HOLD tier: never ready, and skipped by rerank'
brief: 'DEC-162: SOMEDAY stands in today and rerank still touches it; shape ruled at build time'
pri: NOW
state: closed
deps: []
goals: [G-1]
source: session 2026-11-06c
created: 2026-11-06
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

A HOLD tier: an engine tier that is never ready and that rerank (CE-99) skips (DEC-162).

Source: DEC-162, adopting docs/evidence/owner-review-advice-2026-11-06b.md § 1 (i). SOMEDAY stands in for it today, and rerank still touches SOMEDAY, so held items keep resurfacing. No decision is needed now; the agent records the shape at build time (cheap to undo).

## Traps

- none yet

## Read first

- docs/evidence/owner-review-advice-2026-11-06b.md § 1

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: a HOLD tier: held tasks are never ready and rerank skips them (verifier PASS)
  residual risk: INV-182, INV-183, INV-184, INV-185, INV-186, INV-187
