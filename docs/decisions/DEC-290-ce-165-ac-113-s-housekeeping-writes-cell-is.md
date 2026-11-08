---
type: Decision
id: DEC-290
title: "CE-165: AC-113's housekeeping Writes cell is pinned to only through hk_ operations with an optional each logged as mechanical, any other clause red"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:99f6a4515431d0c5759e40aeadf205aeb42e6b58afaf5928b621e288eef1b3b6
---

The agent's call on CE-165 (session 2026-11-07e): AC-113's housekeeping Writes cell is pinned in tests/test_roster.py to exactly "only through `hk_` operations", with an optional ", each logged as mechanical" (the FRAMEWORK §6.6 row's text today).

Any other trailing clause is red, including one that widens the role ("..., and by hand where they fall short"). So a reword of that FRAMEWORK §6.6 cell changes the test with it, on purpose.

Rejected: exact equality (no stronger here, and the optional clause keeps the cell's minimal form legal); a deny-list of widening words ("and", "or", "by hand", "except": open-ended).

Cheap to undo: one regex in one test.
