---
type: Task
id: CE-55
title: "The engine's task close commit carries Closes: CE-n, and the close's sabotage and receipt lines get a home"
brief: "Since CE-45 the engine commits the close itself; DEC-22's Closes: trailer and the Sabotage: lines must not be lost"
pri: NEXT
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

Found 2026-10-13c closing CE-45: commit.py::message titles every engine commit `engine: <op> <id>` with only a Session: trailer. DEC-22 wants `Closes: CE-n` on the commit that finishes a task, and the sabotage rule (DEC-11) puts `Sabotage:` lines in the commit message; once the engine commits the close itself there is no hand commit to carry either. CE-45 itself was closed through the pre-restart MCP server (old code, no commit) and committed by hand. Recommendation: task close adds `Closes: <id>` to its commit, and takes an optional message body (or the close's msg) for the sabotage and receipt lines; rituals § Clean close and manual-mode say so.
