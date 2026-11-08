---
type: Task
id: CE-215
title: 'session rollback: the engine operation for rollback and close (FRAMEWORK 6.13), deferred'
brief: Deferred; un-defer on the first by-hand rollback or the owner's ask; compensating ops, never file restore
pri: SOMEDAY
state: open
deps: [CE-18]
goals: [G-7]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Filed by CE-18's builder (session 2026-11-07e, 2026-11-08). The engine operation for FRAMEWORK §6.13 (Rollback and close), DEFERRED by CE-18's build-or-defer decision: the procedure is designed (FRAMEWORK §6.13) and done by hand (`docs/runbooks/procedures.md` § Rollback and close, plugin skill `rollback-and-close`, its git recipe pinned by `tests/test_rollback_recipe.py`). Un-defer: the first rollback done by hand, or the owner asks.

Build sketch (from CE-18's planner; not yet design-reviewed):

- New (not yet in the code): a `session_rollback` operation in `ops.py` -> CLI `session rollback [--run] [--key <closed key>]`, and its `Engine.session_rollback` in `working.py`. Item 1 through `working.py::Engine.derived_digest`'s trailer query plus the op log; item 2's five classes (kept, undone by operation, restored, reverted by hunk, left) as data, printed as the plan; `--run` does items 3 to 6 under the lock in one store batch, the compensating operations called as Engine methods so each logs its own op line, refusing before any write when a path's class is unknown.
- The compensating operation per op name is the list under the runbook section's table; every op name the op log carries needs a row (a test over `ops.py`'s op names, so a new op cannot slip past it).
- `ledger.py::KINDS` gains `rollback`, replacing the `kind: close` entry with its `rolled back:` summary line: G-W6 receipts; staleness counting (`working.py::Engine.staleness` counts closes and pauses after a key: count a rollback too); the `--follows` refusal (a key that is not a `kind: close` entry is refused: decide whether a rollback entry is followable); orient's last-close part.
- G-W7 needs no change: compensating operations log lines, and no record file is restored or deleted.
- Tests: the two-writer fixture of `tests/test_rollback_recipe.py`, through the engine; sabotage each class rule.

## Traps

- Never `git revert`, reset, stash, clean or `checkout <rev> -- <path>`: FRAMEWORK §6.13 says why each breaks other writers.
- A reopen must cite the undone shas, or `hk close --scan` closes the item again on an old `Closes:` trailer (`working.py::Engine._commit_evidence`).
- The rollback commit's title must not lead with a task id (`hk comment` would read it as work on that task).

## Read first

- `docs/framework/FRAMEWORK.md` §6.13; `docs/runbooks/procedures.md` § Rollback and close; `tests/test_rollback_recipe.py`.

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): Deferred by DEC-322 (build-or-defer); the design's calls are DEC-323. Both PROVISIONAL, agent's.
