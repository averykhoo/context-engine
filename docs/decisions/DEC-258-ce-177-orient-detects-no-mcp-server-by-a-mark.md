---
type: Decision
id: DEC-258
title: "CE-177: orient detects no MCP server by a mark the server writes on its first tool call, not by reading Claude Code's config"
tasks: [CE-177]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:c938ac3d0bc52bdfa293228331f6f252b08b1f82c543883c88fa482c146bead3
---

A build-time call for CE-177, the agent's own, PROVISIONAL until the owner reviews it.

Orient detects "no MCP server" (DEC-155) by a mark file the MCP server writes on its first tool call, `<lockfile dir>/mcp-seen` (by default `.context/mcp-seen`), not by reading Claude Code's config (`~/.claude.json` projects, `.mcp.json`, plugin settings). Reading that config works only for Claude Code, needs Windows path keys normalised, moves with `CLAUDE_CONFIG_DIR`, makes every hook run read a large file outside the repo, and needs a fake home in tests. The mark covers the local, `.mcp.json` and plugin routes alike, since all of them run `context_engine.mcp`. Flagging by channel (CLI caller against MCP caller) was rejected too: the hook's orient is always a CLI run with no key, so every session would be flagged.
