---
type: Decision
id: DEC-240
title: CE-186 drops only sabotage_ce55's reindex row; its nine other stale rows are filed
actor: claude-code/claude-sonnet-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:466b1a53d1663fa58f2ad989e651b93236a3db599ddd3a1f5b2e30d09b21249c
---

CE-186 drops only the dead `reindex` row of tools/sabotage_ce55.py (the method is gone). Its nine other stale rows point at code that moved, and their guards still exist, so they are neither fixed here (a table rewrite) nor dropped (that loses the record of nine live guards): they go to a new LATER task.
