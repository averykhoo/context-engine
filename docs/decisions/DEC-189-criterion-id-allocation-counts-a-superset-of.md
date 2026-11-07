---
type: Decision
id: DEC-189
title: "Criterion id allocation counts a superset of lint's rows: every id-led row of any table outside fenced code"
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:bbe79134aceb08e67c2dc896f43a1af86145776932d1e9028ef4c1be4a682973
---

The agent's call on CE-150, made while building it in session 2026-11-07e: how criterion ids are allocated once `decision link` reads criteria as lint does.

Options:
(a) allocate from `guards.py::criteria_rows` exactly (only the rows lint reads);
(b) allocate from every id-led body row of every table outside fenced code (`guards.py::table_blocks` with `guards.py::ROW_ID_RE`), plus the logged `criterion.new` ids.

Chose (b): `Engine._criterion_ids` counts a superset of lint's rows, so the id of a row lint cannot read (a table with no `status` or source column) is never handed out again (P3). Counting too many only skips a number; counting too few could reuse an id. `decision link` and `why` accept only the ids `criteria_rows` reads.

Cheap to undo: one set comprehension and one test.
