---
type: Decision
id: DEC-203
title: "CE-155: stale_after is refused at write time by record new, task set and decision set, as G-D4's twin: the three writers that take caller fields refuse an empty, non-instant or already-passed stale_after (guards.instant + Engine.now) before any byte; off with G-D4 like the G-I1/G-I2/G-I3 twins; criteria cells and register lines have no engine writer and stay lint's alone"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:bf792db9dd0bda50e1efd44e7ee1abe85f74504e2785fb645f1a5cfe42e8f822
---

The three engine writers that take caller-given frontmatter, `record new`, `task set` and `decision set` (working.py::Engine.record_new, Engine.set, Engine.decision_set, each with `--set`), refuse a `stale_after` that is empty (coerced to None, which would be written as `stale_after: null`), not an absolute instant by guards.py::instant, or already passed by Engine.now, before any byte is written. The check lives in working.py::Engine._stale_after_check, beside the other write-time twins (`_story_checks`, `_born_checks`), and is called after each writer's coerce line.

Why: CE-136's residual. Before this, `record new --set stale_after=2026-10-01` wrote, and only lint G-D4 and the gate went red afterwards. The stop reads the same rule as G-D4's freshness half (guards.py::stale), so, like the G-I1, G-I2 and G-I3 twins, it is off when `[guards] off` names G-D4; it is not an operation-ownership stop like CE-149 and CE-151, which hold whatever `[guards] off` says.

Out of scope: criteria cells and register lines have no engine writer that sets `stale_after` (criterion new and criterion set take none; the register has no writer), and `decision import` takes no `--set` fields, so lint stays their only check. Rejected: a check in Store.set or Store.new (Store has no clock and carries mechanical and import writes), a new `instant` type in coerce (a kit schema change, and coerce has no clock), and sharing guards.stale's inner check (it would reword lint's pinned messages).
