---
type: Task
id: CE-154
title: 'doc archive --lines: pointer reds, liveness and the uncommitted check'
brief: CE-96 verifier findings 2 and 3 and the rest (654ea03)
pri: NOW
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07e
updated: 2026-11-07e
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

- 2026-11-06c (claude-code/claude-opus-5-5): Takes over CE-153 (DEC-162): doc archive refuses the engine's own control files, context.toml and the op log (docs/ledger/ops.jsonl), which CE-96 made archivable when it dropped the non-.md refusal (654ea03, verifier finding 1). Same file as this task (working.py::Engine.doc_archive); a one-line refusal.
- 2026-11-06c (claude-code/claude-opus-5-5): Correction (DEC-162): CE-153's one-line refusal of context.toml and the op log moves on to CE-158 at NEXT, since the ruling says to do it now ('merge into CE-154, do now'; 'take CE-153's one-line refusal with them', with CE-156 and CE-158) and CE-154 stays LATER. This task keeps only its --lines findings.
