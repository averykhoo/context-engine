---
type: Task
id: CE-3
title: "MCP server over the CLI operations; dogfood it on this repo"
brief: "One implementation per operation: each MCP tool calls the CLI's function; writes return one line"
pri: NOW
state: closed
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-10c
updated: 2026-10-10c
closed: 2026-10-10c
status: deprecated
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
- 2026-10-10c (claude-code/claude-opus-5-5): Built: ops.OPS (one function per op, called by cli.run and the server), context_engine.mcp, .mcp.json via ${CE_PYTHON}, .claude/settings.json; mcp pin fixed to >=2.3,<3. Sabotage table tools/sabotage_ce3.py: 11 rows, all red. Dogfood VERIFIED headless (claude -p haiku): routes answered through .mcp.json; control with CE_PYTHON unset: tool unavailable.
- 2026-10-10c (claude-code/claude-opus-5-5): SessionStart hook measured: orient over MCP is 5195 bytes on this repo (2026-10-10, cap 6000). Not added: session_start must come first anyway and orient then marks own batons; revisit if sessions skip orient. Dots: MCP SDK 2.3 allows them (TOOL_NAME_REGEX); Claude's side still UNVERIFIED, moot under DEC-15.
- 2026-10-10c (claude-code/claude-opus-5-5): closed: MCP server built and dogfooded; AC-18, AC-19 tested (sabotaged red)
