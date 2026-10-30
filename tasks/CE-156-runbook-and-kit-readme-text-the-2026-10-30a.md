---
type: Task
id: CE-156
title: Runbook and kit README text the 2026-10-30a builds left stale
brief: 'Both runbooks are kit copies kept byte-equal: fix each line in both'
pri: NEXT
state: open
deps: []
goals: [G-7]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

Runbook and kit README text the 2026-10-30a builds left stale.

Source: residuals in the close commits named per line; both runbooks are kit copies, kept byte-equal by the gate, so each fix lands twice.
- procedures.md § Clean close step 4 still tells every close to state `--residual none`; on an item whose design review lists residuals that `none` is now refused (CE-120, 2bd0583).
- procedures.md § Bootstrap row 4 shows a bare `context-engine ask new`, which is now always refused (CE-44, 3371106).
- procedures.md § Push and CI describes the CI watcher as one agent that waits for the runs, with no pointer to fan-out.md § Watchers (CE-107, 8c30e8a).
- manual-mode.md opens the G-D4 bullet with "(only when `[guards]` lists `liveness` or `history` paths)", though the freshness half runs whatever those lists hold (CE-136, a7f128b).
- manual-mode.md § context-engine orient does not list the "Charter unconfirmed: ask the owner" part, CE-121's templates part or CE-114's upstream part (CE-136, a7f128b).
- manual-mode.md § criterion set step 2 says a changed cell becomes ` <value> `; for the last cell of a row with no closing pipe criteria.py::rewrite writes ` <value>` (CE-42, f85e632).
- manual-mode.md § context-engine coverage says built is "a G-id lint reports (§ lint lists them)", but § lint never names G-D6 (in config.LINT_IDS), so a by-hand run marks G-D6 done instead of built (CE-141, c5d96b0).
- The kit README's "33 to 36 seconds" carries no date or Claude Code version (evidence: docs/evidence/plugin-design-2026-10-14.md, 2.1.280) (CE-85, 75b3748).

## Traps

- none yet

## Read first

- docs/runbooks/procedures.md
- docs/runbooks/manual-mode.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): rerank: G-4/G-7, exit criterion 1 (DEC-20 by-hand fallback): eight stale runbook lines, kit copies only, no contract touch.
