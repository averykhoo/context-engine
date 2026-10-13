---
type: Task
id: CE-62
title: The MCP stdio test checks main's code when the gate runs in a worktree
brief: A worktree gate must test the worktree; pass the child an env carrying PYTHONPATH
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

Hit by CE-49 and noted by CE-33 (2026-10-13c): tests/test_mcp.py::test_python_dash_m_context_engine_mcp_serves_over_stdio starts the server through the MCP client, whose default environment drops PYTHONPATH, so in a worktree (gated with PYTHONPATH=<wt>/src) the child imports the main tree's editable install and fails on any new tool. Recommendation: pass env with PYTHONPATH to the stdio child; gate.md and fan-out.md's worktree note can then drop the caveat.
