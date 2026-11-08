---
type: Task
id: CE-12
title: "Tier-1 housekeeping agents restricted to hk_ tools"
brief: "The allowlist names only hk_ MCP tools: no Edit, Write or Bash. Measure the write budget (Q-K)"
pri: NOW
state: closed
deps: [CE-6]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-11-07e
updated: 2026-11-07e
closed: 2026-11-07e
goals: [G-3]
status: deprecated
---

A `.claude/agents/housekeeper.md` whose tools are only the `hk_` set, for work that needs
reading: commits into task comments, foreign-commit reconciliation, unrecorded owner words
(reported, never written).

## Log

- 2026-10-09e (claude-code/claude-opus-5-5): Q-K answered (DEC-21, 2026-10-09): no write budget by default; measure writes and token counts per run instead. A configured cap stays optional (G-W10).
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: Tier-1 housekeeping agent restricted to hk_ tools; hk comment --scan lists tier-1 title mentions
  residual risk: INV-232, INV-233, INV-234, INV-235, INV-236
