---
type: Decision
id: DEC-15
title: 'One name, context-engine: the CLI command and the MCP server; tools use underscores'
actor: owner
decision_status: PROVISIONAL
tags: '[naming, mcp, cli]'
decided: 2026-10-09
session: 2026-10-09a
body_sha: sha256:244bb017f30548a2da4b4b1230d4484d9075d4f3f687ca56043c13bffe1da212
---

Owner, in order, after the agent suggested renaming the `ce` command (to `ctx`) and noted that
agents will mostly see the MCP server name (CE-3):

- *"It's going to be an mcp in the future?"*
- *"Then maybe call it context-engine? Or use underscores"*
- *"Just use the long name since it's less likely to collide with things"*

So, with the agent's split between hyphens and underscores, which the owner did not object to:

1. **The CLI command is `context-engine`**, with no short alias. `ce` is retired as a command
   name. Records written before this decision keep the word `ce`, since they are append-only.
2. **The MCP server name in `.mcp.json` is `context-engine`**, so agents see
   `mcp__context-engine__<tool>`.
3. **MCP tool names use underscores** (`session_start`, `task_close`, `hk_close`), not the
   dotted names in FRAMEWORK §8.0.2. As far as the agent knows, Claude tool names allow only
   letters, digits, `_` and `-` (UNVERIFIED; CE-3 checks it).
4. **The Python package stays `context_engine`**, because Python names cannot contain hyphens.
