---
type: Task
id: CE-154
title: 'doc archive --lines: pointer reds, liveness and the uncommitted check'
brief: CE-96 verifier findings 2 and 3 and the rest (654ea03)
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

doc archive --lines: pointer reds, liveness and the uncommitted check.

Source: CE-96's close (654ea03), residuals (verifier findings 2 and 3, and the rest).
- working.py::Engine._pointer_reds compares G-D3 failures as (path, message), and the message holds a line number, so a pointer already red below a pruned passage is reported as newly red, with wrong advice.
- working.py::Engine._prune checks a change to the liveness G-D4 reads only when the doc declares liveness itself; with liveness from `[guards] liveness_given` alone, a cut can turn a word in passing into a declaration and leave G-D4 red.
- When a doc's frontmatter runs past G-D4's window and has no liveness key, the ARCHIVED line falls outside the window and the archived copy is G-D4 red.
- The uncommitted-changes refusal checks only the doc, not `<stem>-pruned.md` or the README redirect table; a `--lines` range is not re-checked against concurrent edits beyond it.

## Traps

- none yet

## Read first

- working.py::Engine._pointer_reds
- working.py::Engine._prune

## Log
