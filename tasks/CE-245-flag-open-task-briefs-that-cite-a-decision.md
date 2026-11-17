---
type: Task
id: CE-245
title: Flag open task briefs that cite a decision superseded or amended since
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

Flag open task briefs that cite a decision superseded or amended since.

adhoc-microphone-array (AD-112 item 20): a decision changed several task briefs and nothing flagged the stale ones; they were found by eye. docs/evidence/engine-feedback-2026-11-17.md, F20. The nearest prior work is CE-115 (HANDOFF only, closed); guards.py::supersede_links checks only link symmetry.

## Traps

- A warning, not a refusal, unless the owner rules otherwise: an amended decision does not always change a brief.
- Read only open board items: a closed task's brief is history.

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F20
- guards.py::supersede_links; CE-115

## Log
