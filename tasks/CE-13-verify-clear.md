---
type: Task
id: CE-13
title: "Check what /clear does to the MCP server, in an interactive session"
brief: "Not testable headless; the design does not depend on it"
pri: SOMEDAY
state: closed
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-12c
updated: 2026-10-12c
closed: 2026-10-12c
status: deprecated
---

Open an interactive Claude Code session in a temp copy of `spike/project/` (as
`spike/run_probes.sh` does), call `ping`, run `/clear`, call `ping` again, and compare the pids.
Record the result in `spike/FINDINGS.md` row 5.

## Log

- 2026-10-12c (claude-code/claude-opus-5-5): closed: Closed: the reasoned answer is spike/FINDINGS.md row 5 and the design does not depend on the live pid-compare run; owner approved the 2026-10-12c prioritisation ("Sure okay"). Reopen to run it in an interactive session.
