---
type: Decision
id: DEC-214
title: 'Duplicate live decision titles are a new intent guard G-I4: not a clause of G-I3 (delegated rulings) or G-W4 (status agreement), so `[guards] off` can drop it alone'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-189]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:9209d3bbd877253babbe3651739ddab8fe76e8301691327bdfecd8fdf188a760
---

Two current decisions sharing a title (DEC-162, CE-189) are failed by a new intent guard, G-I4 (`guards.py::decision_titles`), run from `guards.py::intent` after G-I3, and named in `config.py::LINT_IDS`.

Options: (a) a new guard id; (b) a clause of G-I3 (delegated rulings); (c) a clause of G-W4 (the state key agrees with the derived status).

Chose (a). Neither G-I3's rule nor G-W4's is about titles: DEC-112 put a check in G-W4 because it was G-W4's own rule, and this is not. A separate id lets `[guards] off` drop this check alone, for instance in a repo that imported a log with repeated titles, without losing the delegated-ruling or status checks.

Cost to undo: cheap; fold the function into another guard and drop the id.
