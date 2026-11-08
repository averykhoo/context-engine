---
type: Decision
id: DEC-285
title: 'coverage: a G-id with no lint guard reads built when the guards.py::ENFORCED table names the operation that enforces it and its tested criterion (G-W8 session_close AC-11, G-W10 hk_run AC-177); a test pins that every home resolves'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:d726c4d2477a01051d68bd8c8b946ae032f1202451f413b4c12dd85a850c1baf
---

The agent's call on CE-164 (session 2026-11-07e): a G-id no lint guard reports reads built in `context-engine coverage` when `guards.py::ENFORCED` names the operation that enforces it at write time and the tested criterion that pins it: G-W8 by `working.py::Engine.session_close` (AC-11), G-W10 by `working.py::Engine.hk_run` (AC-177). The note reads "<home> enforces it (<criterion>)".

Before this, `_item_status` called a G-id built only when it was in `config.LINT_IDS`, so G-W10 read deferred (the frozen 2026-10-12 map's row, written when only one hk operation existed) and G-W8 read done, though both are built.

A test (`tests/test_coverage_status.py`) pins that every ENFORCED home resolves to a real symbol, that its G-id is not a lint id, and that its criterion is tested, so the table cannot name code that is gone.

Rejected: built inferred from criteria text (AC-177 never names G-W10) or from closed board items (a passing mention would read as built).

Cheap to undo: one table and one clause.
