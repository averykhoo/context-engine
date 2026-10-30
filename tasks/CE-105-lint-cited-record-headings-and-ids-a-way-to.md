---
type: Task
id: CE-105
title: Lint cited record headings and ids; a way to reserve ids before a batch of linked tasks
brief: 'Cross-refs in records must resolve: lint missing headings, and let a batch cite ids it has reserved'
pri: NOW
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
---

Lint cited record headings and ids; a way to reserve ids before a batch of linked tasks

What went wrong (adhoc AAR entry 2 and 31, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: Records cited headings that do not exist (entry 2) and a batch of linked tasks cited each other's ids before the ids were assigned (entry 31). Lint cited section headings of other records, and offer `task new` in batch or an id-reserve op so a linked batch can cite ids that exist. Census F2: NEW. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F2).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): Lint half landed 20b9c03 (G-D3 record_refs). Id-reserve / batch task new op not built: needs kit runbook steps, held by the kit freeze until the adhoc re-pin commits.
