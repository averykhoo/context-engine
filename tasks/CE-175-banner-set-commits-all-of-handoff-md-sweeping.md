---
type: Task
id: CE-175
title: banner set commits all of HANDOFF.md, sweeping in other sessions' uncommitted edits
brief: Reported by the intervals 2026-11-03a session (CE-11 finish); not yet reproduced first-hand
pri: NOW
state: open
deps: []
goals: [G-6]
source: session 2026-11-03a
created: 2026-11-03
moved: 2026-11-07e
updated: 2026-11-07e
---

banner set commits all of HANDOFF.md, sweeping in other sessions' uncommitted edits.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): Reproduced first-hand 2026-11-08 (session 2026-11-07e, tree at ccc01ec): a temp repo from the tests/test_commit.py helpers under the default `milestones` policy; session A appends a line to HANDOFF.md by hand; session B runs `banner set`, which commits (working.py::_milestone -> store.py::Store._commit -> commit.py::commit) and HEAD:HANDOFF.md carries A's line, tree clean. Real. The 2026-11-07e census line ("banner_set commits nothing") was wrong: banner set is a milestone, and `session close --banner` goes the same way. Fix: a banner-only commit (DEC-292..295, PROVISIONAL).
