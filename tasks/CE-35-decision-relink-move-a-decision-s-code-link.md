---
type: Task
id: CE-35
title: "Decision relink: move a decision's code link when the code moves"
brief: 'logged like link, re-checks existence; code: is never hand-edited'
pri: NEXT
state: open
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
review: [write-op, shipped]
---

Filed by CE-14-fix (session 2026-10-12d). G-T3 (src/context_engine/guards.py::decision_code) fails a current decision whose `code:` link no longer resolves. `decision link` only adds; no operation removes or replaces a link, and `code` is written by an operation, so it is not hand-edited: today the only remedy is restoring the code. Add one (e.g. `decision link --replace <old>`), its runbook section, and point the G-T3 remedy and INV-15 at it.

## Design review

affects: the owner, whose decisions name the code that carries them out; the next session, which reads why() and `decision find --links-to` answers from `code:` links; a plain-git human relinking by hand from manual-mode.md; every deployed repo, which gets the operation and the kit runbook copy
- eliminated: a decision's `code:` link is hand-edited to follow moved code, because no operation rewrites it (`decision relink` writes it under the lock, logs `relink` with session and actor, and regenerates the index in the same write)
- reduced: a relink writes a link that does not resolve, so G-T3 stays red or why() answers from nothing | rung: reduce | control: Engine.relink checks the new link with Engine._code_exists, the check `decision link` uses (file case-exact, every dotted part of the symbol); G-T3 at rest; sabotaged
- reduced: `relink` silently adds a link when the old one is not there, or moves an id link (`tasks`, `relaxes`, ...), leaving a `relaxes` without its `narrowed_by` backlink | rung: reduce | control: Engine.relink refuses an old link that is not in `code:`, naming the field when it is an id link (ids never move: they are never reused and records are never deleted); sabotaged
- reduced: a superseded decision's links are rewritten, though they are history that G-T3 deliberately skips | rung: reduce | control: Engine.relink refuses a decision with `status: deprecated` (SUPERSEDED), checked under the lock; sabotaged
- reduced: the code a decision names is deleted with no successor, and G-T3 is red with no remedy but a hand edit | rung: reduce | control: the G-T3 remedy (guards.py::decision_code) names `decision relink` when the code moved and `decision supersede` when the behaviour is gone; manual-mode § decision relink says the same
- residual: an agent relinks a decision to code that resolves but does not carry the decision out (a different symbol, or a file the behaviour never moved to), so why() answers wrongly | rung: individual | why: whether code carries out a decision is a reading judgement no operation can make; the op log `relink` line names session and actor, and the commit diff shows old and new side by side | control: manual-mode.md § decision relink: relink only to where the same behaviour now lives, in the commit that moves it
F: goes stale if a link field other than `code:` gains targets that move (it would need its own relink with its backlink), or if G-T3's resolution rule changes (relink reuses Engine._code_exists, so it follows `decision link`); INV-15's control names this operation
A: by hand, manual-mode.md § decision relink: replace the one entry in `code:` in place, check the new target as for `decision link`, log one `relink` line, regenerate the index
M: one Engine.relink over Store.update (lock, validation, op log, reindex already there) and Engine._code_exists shared with Engine.link; one ops.decision_relink wired to the CLI and MCP by OPS
E: mirrors `decision link` (same positional id and target, same one-line return, one op-log line); one runbook section beside § decision link, one row in the op-log table, one clause in FRAMEWORK §6.5's operations list and §8.0.2's operations list

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): built: `decision relink <id> <old> <new>` (working.py::Engine.relink, ops.py::decision_relink; op-log op `relink`): moves one `code:` link in place, the new one checked as `decision link` checks it; refuses id links, superseded decisions, an old link it does not have. G-T3 remedy and INV-15 point at it; manual-mode § decision relink; FRAMEWORK §6.5, §8.0.2, §8.2; AC-54. Shape: a separate verb, not `decision link --replace` (link stays add-only). Awaiting review.
