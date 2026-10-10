---
type: Decision
id: DEC-25
title: If the MCP server is not set up, the agent sets it up, falls back to the CLI, and asks the owner to restart
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-10
session: 2026-10-10d
body_sha: sha256:c0c801b38e3b5ba9ad5e54bdbf25fad5f239d4a1b441259e4a12739e64d3a405
---

Owner, 2026-10-10d (chat, verbatim):

> Actually nvm, let's try to find a better way. How about the Claude agent initializes whatever vars are needed on first run?

> Okay then that should be the instruction written in - if the mcp isn't set up, to set it up but fallback to cli, and ask me to restart
