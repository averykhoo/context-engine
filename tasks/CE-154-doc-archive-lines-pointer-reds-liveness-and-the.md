---
type: Task
id: CE-154
title: 'doc archive --lines: pointer reds, liveness and the uncommitted check'
brief: CE-96 verifier findings 2 and 3 and the rest (654ea03)
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
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
- 2026-11-07e (claude-code/claude-opus-5-5): Built in 9aba4d5 (DEC-224..228, PROVISIONAL): pointer reds as a multiset without line numbers, a prune never changes the doc's own declaration, a long frontmatter gets liveness: FROZEN, the table and archive file refuse a hand edit, and a file changed mid-run refuses the archive. Not closed (the builder does not close).
- 2026-11-07e (claude-code/claude-opus-5-5): Residual: a prune can drop an ACTIVE-PLAN doc's named board item out of G-D4's window (G-D4 red); doc archive --lines does not check it.
- 2026-11-07e (claude-code/claude-opus-5-5): Residual: a small TOCTOU window remains between doc archive's re-check (DEC-228) and its first write.
- 2026-11-07e (claude-code/claude-opus-5-5): Residual: a hand edit on top of an engine-written, still uncommitted redirect table or archive file passes DEC-227's check, since op lines carry no content hash.
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: doc archive --lines: pointer reds as a multiset, prune never changes the doc's own declaration, long frontmatter gets liveness FROZEN, table and archive file refuse hand edits, mid-run change refuses (9aba4d5, d08161d)
  residual risk: INV-164, INV-165, INV-166, INV-167, INV-168, INV-169
