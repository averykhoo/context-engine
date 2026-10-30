---
type: Task
id: CE-164
title: 'coverage: housekeeping parts G-D12 does not extract, and a frozen map outranking the board'
brief: CE-141 residuals (c5d96b0)
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

coverage: housekeeping parts the spec names but G-D12 does not extract, and a frozen map outranking the board.

Source: CE-141's close (c5d96b0), residuals.
- N3 only partly closed: the housekeeping script and hk.close named in FRAMEWORK §8.0.2 and §11.1 are not spec items G-D12 extracts, so they show only through §6.11.
- A DEFERRED or PROSE-ONLY row in the newest map (frozen 2026-10-12) outranks the board: G-T4 reads "deferred" though open CE-34 names it, until a new map is written (guards.py::STATUS_RULES says so).

## Traps

- none yet

## Read first

- guards.py::STATUS_RULES
- ops.py::coverage

## Log
