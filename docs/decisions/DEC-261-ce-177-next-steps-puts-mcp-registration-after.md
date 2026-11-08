---
type: Decision
id: DEC-261
title: 'CE-177: next_steps puts MCP registration after the kit commit and before session start, its command built from sys.executable'
tasks: [CE-177]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:677c7ae07d9734563f636764a005775b649db22ce8822e244591fdc3ad92abe1
---

A build-time call for CE-177, the agent's own, PROVISIONAL until the owner reviews it.

init's `; next:` line (`bootstrap.py::next_steps`) puts MCP registration after the kit commit and before `session start`, with the exact `claude mcp add --scope local context-engine -- "<interpreter>" -m context_engine.mcp` command built from `sys.executable` (`bootstrap.py::mcp_add_command`), quoted as `bootstrap.py::hook_settings` quotes it. init does not run `claude mcp add` itself: that writes outside the repo, which is the owner's call.
