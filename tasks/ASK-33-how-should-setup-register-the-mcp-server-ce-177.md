---
type: Question
id: ASK-33
title: How should setup register the MCP server (CE-177)?
brief: 'Recommend: next_steps names claude mcp add as required; orient flags a missing server'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-03b
last_asked: 2026-11-03b
blocks: [CE-177]
---

## Context

audio-workspace's feedback item 1 (setup also registers the MCP server) is not done at engine pin 309641b:
`bootstrap.py::next_steps` calls registration optional and init writes no MCP config (CE-177). Registering
writes ~/.claude.json, outside the repo, so CE-167 did not do it for zanzibar.

## Options

- `next_steps` names `claude mcp add --scope local ...` as a required step, and orient flags a session that has
  no MCP server.
- init writes a committed `.mcp.json` pointing at the repo-relative engine env (needs a per-OS form).
- Make the plugin route (CE-77) the default.

## Recommendation

The first: it is a small change, and it keeps machine paths out of committed files.
