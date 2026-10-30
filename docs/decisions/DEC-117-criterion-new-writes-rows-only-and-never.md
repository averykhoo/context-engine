---
type: Decision
id: DEC-117
title: criterion new writes rows only and never guesses the table
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:0406e452689b41bc1eba3dd913ddc53af64f9635d22181bcad6d3e688cdfe479
tasks: [CE-42]
code: [src/context_engine/criteria.py::target]
---

CE-42's `criterion new` writes rows only and never guesses the table.

Options: (a) also write headings and table headers; (b) rows only, refusing without `--under` when the file has several criteria tables. Picked (b): CE-25 says one row only, and where a criterion goes is the writer's choice (design review D4).

Code: criteria.py::target, working.py::Engine.criterion_new.
