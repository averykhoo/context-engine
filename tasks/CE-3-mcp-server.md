---
type: Task
id: CE-3
title: "MCP server over the CLI operations; dogfood it on this repo"
brief: "One implementation per operation: each MCP tool calls the CLI's function; writes return one line"
pri: NOW
state: open
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08f
updated: 2026-10-09f
closed:
---

Build step 3: a thin `MCPServer` wrapper (SDK 2.x, stdio), `python -m context_engine.mcp`,
plus this repo's own `.mcp.json` and `.claude/settings.json` so sessions here use it. Claims
AC-18 and AC-19 (AC-20 arrives with the `hk_` set in CE-6).

## Traps

- SDK 2.x: `from mcp.server.mcpserver import MCPServer`; `FastMCP` is gone (DEC-8).
- Name the interpreter in `.mcp.json` through `${VAR}` (verified to expand), and document the
  value for the owner's machine; pre-approve with `enabledMcpjsonServers`.
- The server's cwd is the repo root (verified). A `/clear` probably does not restart it
  (UNVERIFIED, CE-13), so sessions begin with an explicit `session.start`.
- A SessionStart hook can inject `orient()`'s output (verified); decide after measuring its size.

## Read first

- `docs/framework/FRAMEWORK.md` §8.0.2
- `spike/FINDINGS.md`, `spike/probe_server.py`, `spike/project/`

## Log

- 2026-10-09a (claude-code/claude-opus-5-5): DEC-15 (owner): server name in .mcp.json is context-engine (agents see mcp__context-engine__<tool>); tool names use underscores (session_start, task_close, hk_close), not FRAMEWORK §8.0.2's dotted names. Check first that Claude tool names really refuse dots (UNVERIFIED).
- 2026-10-09f (claude-code/claude-opus-5-5): pyproject.toml pins mcp>=1.2, but DEC-8 and FRAMEWORK §8.0.2 target SDK 2.x (MCPServer); fix the pin when building the server (audit finding B8, 2026-10-09).
