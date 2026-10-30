---
type: Decision
id: DEC-111
title: A kill bar lives in a board item's Kill bar section, and task close --verdict is KILL, PASS or VOID with evidence
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:daf1a3afec2acbea848e08bd14a453f33f31294608c32d7ff4bd76cc946af3a7
---

The agent's call on CE-108, made while building it in session 2026-10-30a: where a kill bar lives and how a close records the verdict against it.

Options:
(a) a body section on the task, `## Kill bar`, written with `task section` before the run, with its op line as the timestamp;
(b) a frontmatter field naming a results-file section;
(c) a new record kind.

Chose (a), with `task close --verdict KILL|PASS|VOID: <evidence>`: KILL (the bar fired), PASS (it did not) and VOID (the run cannot judge it, e.g. the invalid measurement in entry 7). The engine refuses a verdict without a bar, a bar without a verdict, a malformed verdict and a bar under a heading that differs from `## Kill bar` only in case or spacing, and refuses to rewrite a closed item's bar. It does not judge whether the verdict follows from the evidence (the reviewer's call), and it does not check that the bar predates the run, or that it was left alone after the run while the item was open: the op log's `section` lines are the only record of that, and the reviewer reads them. Why: no new kind or config key, it reuses `task section`, and it is cheap to undo.

Built in lane commits a4622c0 and a301376, on main as d9ebc95 and 91fb1e2 (working.py::Engine._against_bar); pinned by AC-126. Cheap to undo.
