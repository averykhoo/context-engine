---
type: Question
id: ASK-35
title: Confirm CE-167's design calls on zanzibar's branch (cutover, ids, decisions, cap, HOLD)?
brief: 'Recommend: confirm all five; ids are never reused once merged'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-03b
last_asked: 2026-11-03b
blocks: [CE-167]
---

## Context

The CE-167 builder made these calls on the unmerged branch (cheap to undo until merge; ids are never reused
after it):
1. Full cutover: `tasks/` belongs to the engine; `scripts/task.py` is retired from zanzibar's gate and refuses
   an engine tree (two tools cannot share `tasks/`).
2. Ids: TK<n> becomes TK-<n> with alias TK<n>; the 115 records in other series (ZT-P*, R6-n, P6, SD-1, ...)
   become TK-186..TK-300 by created date, old id as alias. Prefixes DEC/TK/US (the kit's D and S collide with
   zanzibar's D7 and S-1..S-7 labels).
3. Decisions: decision-log.md imported as 9 records, one per section; DEC-7 and DEC-8 have actor owner (their
   headings say "user decision"), the rest unrecorded; all BUILT; spec-deviations.md left unimported.
4. handoff_lint's CLAUDE.md byte cap raised from 32500 to 33500 for the kit block (the file is 32872 B).
5. context.toml gains a HOLD tier and makes pri optional (57 closed records have none).

## Options

- Confirm all five as built.
- Confirm some and name changes (the builder re-runs the import script on a fresh worktree).

## Recommendation

Confirm all five: each was forced by zanzibar's data or caps, conservation is byte-equal, and the cap raise
keeps the ratchet rather than dropping it.
