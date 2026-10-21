---
type: Task
id: CE-119
title: 'Refuse literal DEC-<NEW> placeholders in committed records: id reserve op or lint'
brief: A committed record must not hold a literal DEC-<NEW> placeholder; reserve ids or lint it
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

Refuse literal DEC-<NEW> placeholders in committed records: id reserve op or lint

What went wrong (adhoc AAR entry 32, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: Agents drafted records with a literal `DEC-<NEW>` placeholder and only a review caught it before commit (entry 32). Lint any `<NEW>` id placeholder in tracked records and/or offer an id-reserve op (shared with F2's design). Census F22: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F22).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log
