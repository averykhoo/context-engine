---
type: Decision
id: DEC-197
title: hk comment on a record that is not a board kind is refused as '<id> is a <kind>, not a task', via membership in [working] board, not [working] task
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:168dcca3df6db20a4fea2c956349ec59f42380424f9c0e618574b50b7e6bc519
---

`hk comment <id> --commit <sha>` on a record whose kind is not a board kind (a decision, a story) is refused as "<id> is a <kind>, not a task: housekeeping comments only on tasks", checked in working.py::Engine._comment_problem by membership in `[working] board` (Engine._board()), after the owner-question check and before the open-state check. Before this, such a record has no `state` and was refused as "<id> is closed", which is false. Rejected: comparing against `[working] task`, which breaks a repo that sets board kinds without naming `task`; and changing Engine.hk_comment's remedy table, whose fallback "comment only on an open task" already fits. CE-170.
