---
type: Task
id: CE-103
title: 'Rerank edge cases: goals check on task reopen, lenient Last rerank line, same-session owner records'
brief: From CE-99 verification 2026-10-20e; none blocks use
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-20e
created: 2026-10-20
moved: 2026-10-20e
updated: 2026-10-20f
---

Rerank edge cases: goals check on task reopen, lenient Last rerank line, same-session owner records

From CE-99's verifier (2026-10-20e, .scratch/ce-99/verify.md):

1. working.py::Engine._task_goal_check runs only from new and set; task reopen of a closed task with no goals succeeds and turns G-I1 red. Refuse the reopen, or name task set --set goals=[..] in the remedy.
2. guards.py::last_rerank (LAST_RERANK_RE) reads only a bare line; bold, indented or annotated lines read as missing, so orient says the line is absent when it is malformed.
3. guards.py::newer_than compares session keys strictly: an owner record made in the rerank's own session never counts as newer. Document it or decide.

## Traps

## Read first

## Log

- 2026-10-20f (claude-code/claude-opus-5-5): 2026-10-20f: items 2 and 3 are moot since 393e9e4 (Last rerank is quoted, never a trigger; newer_than removed). Only item 1, the goals check on task reopen, remains.
