---
type: Task
id: CE-12
title: "Tier-1 housekeeping agents restricted to hk_ tools"
brief: "The allowlist names only hk_ MCP tools: no Edit, Write or Bash. Measure the write budget (Q-K)"
pri: SOMEDAY
state: open
deps: [CE-6]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-09e
closed:
---

A `.claude/agents/housekeeper.md` whose tools are only the `hk_` set, for work that needs
reading: commits into task comments, foreign-commit reconciliation, unrecorded owner words
(reported, never written).

## Log

- 2026-10-09e (claude-code/claude-opus-5-5): Q-K answered (DEC-21, 2026-10-09): no write budget by default; measure writes and token counts per run instead. A configured cap stays optional (G-W10).
