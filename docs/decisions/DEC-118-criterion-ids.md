---
type: Decision
id: DEC-118
title: Criterion ids
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:c18dbc77ef5cee2453bef14a8d46759256526b557d47e9ad96d6c99f7822dd2f
---

Criterion ids (CE-42): the prefix comes from the rows (AC when there are none); the next id is above every row and every logged `criterion.new`; `--id` is for blocks handed out by hand across worktrees.

A clash after a merge is caught by the duplicate-row check (G-T1, G-T2, G-T6, in guards.py::criteria_rows) and by G-D2 reading `criterion.new` lines (guards.py::ids). Criteria are not a kind, so `id reserve` does not cover them (design review D1).

Code: working.py::Engine._next_criterion, working.py::Engine._free_criterion.
