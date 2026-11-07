---
type: Task
id: CE-191
title: "A louder close when NOW is empty: session close warns with G-W5's line and remedy, never refuses"
brief: 'DEC-162: a warning, not a refusal; an everything-is-done close stays legal'
pri: NOW
state: open
deps: []
goals: [G-2]
source: session 2026-11-06c
created: 2026-11-06
moved: 2026-11-07d
updated: 2026-11-07d
---

A louder close when NOW is empty: session close warns, it does not refuse (DEC-162).

Source: DEC-162, adopting docs/evidence/owner-review-advice-2026-11-06b.md § 1 (ii). When NOW is empty at close, the close prints G-W5's red line and its remedy (`task promote <id>`) in the digest. A refusal would block a legitimate "everything is done" close, so it is a warning.

## Traps

- A warning, not a refusal (DEC-162).

## Read first

- docs/evidence/owner-review-advice-2026-11-06b.md § 1

## Log
