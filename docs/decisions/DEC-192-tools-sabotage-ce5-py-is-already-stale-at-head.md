---
type: Decision
id: DEC-192
title: tools/sabotage_ce5.py is already stale at HEAD in 5 rows CE-150 does not touch; CE-150 runs its own tools/sabotage_ce150.py
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:7dccb8cd6c35f854f9dfe403e79321258d2a261c5a4d51808c588d1afd2e556c
---

The agent's call on CE-150, made while building it in session 2026-11-07e: `tools/sabotage_ce5.py` is already stale at HEAD.

Five rows of it do not match the source before CE-150: AC-39 `o.set("status", "deprecated")` matches twice; AC-40 `if missing:` matches none; AC-42 `STOP_RE.search`, `back = by_id[t]...` and `if foreign:` match none. The script asserts on the first mismatch. CE-150 updates only the row for the removed `CRITERION_ROW_RE`, and runs its own sabotages through the new `tools/sabotage_ce150.py`. Refreshing the five rows is a follow-on.

Cheap to undo: nothing else changes.
