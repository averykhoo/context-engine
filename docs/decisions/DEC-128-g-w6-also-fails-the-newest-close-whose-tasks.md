---
type: Decision
id: DEC-128
title: 'G-W6 also fails the newest close whose tasks: ids are missing from its rows:'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:ee39a6e1265291d05929a2982fb26a88e7c0d62b90bc0e830396a35ba0933823
---

The agent's call on CE-112, made while building it in session 2026-10-30a: whether the named-task check also runs at rest.

Options:
(a) a lint check: G-W6 also fails the newest close whose `tasks:` ids are missing from its `rows:`;
(b) the close's refusal alone.

Chose (a). It is the at-rest twin of the close refusal: it covers a close written by hand (the manual-mode fallback, DEC-20) and a close edited after it was written. The G-W6 definitions in FRAMEWORK's guard list and in manual-mode § lint name it.

Built in lane commits d6aa802 and f6a5dad, on main as bd95ea1 and ba98530; pinned by AC-156 (tests/test_working.py::test_lint_g_w6_fails_a_newest_close_whose_rows_miss_a_named_task). Cheap to undo.
