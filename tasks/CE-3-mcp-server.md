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
updated: 2026-10-12b
closed: 2026-10-10c
status: deprecated
review: [long-lived]
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
- 2026-10-12b (claude-code/claude-opus-5-5): retroactive design review written by CE-23 (session 2026-10-12b); its residuals copied into src/context_engine/REGISTER.md by hand (manual-mode.md § task close) as INV-1 to INV-3

## Design review

affects: every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- eliminated: a crashed server leaves the repo lock held | rung: eliminate | control: the lock is an OS byte-range lock, released when its holder dies (lock.py)
- eliminated: the MCP tools and the CLI drift apart | rung: eliminate | control: one function per operation in ops.OPS, called by both (AC-18)
- reduced: a read floods the session's context | rung: reduce | control: every read is capped at read_max_bytes and says where the rest is (AC-19)
- reduced: two servers in one checkout lose each other's write | rung: reduce | control: every write takes the OS lock and re-reads inside it (AC-9)
- residual: a long-lived server keeps running old engine code after the engine changes, and it may outlive `/clear` | rung: individual | why: Claude Code owns the server process, and the engine cannot restart itself inside a session | control: CLAUDE.md asks the owner to restart Claude Code after setting up or changing the server (DEC-25); CE-13 checks what `/clear` does
- residual: a write is logged under the wrong actor or session, because the server remembers the first `session_start` and a subagent that passes no `actor` inherits the parent's | rung: individual | why: an MCP call carries no caller identity the engine can verify; the actor is self-declared (OKF §7) | control: the server instructions and CLAUDE.md tell each subagent to pass its own `actor`; G-W7 (not built, CE-14) will cross-check the op log
- residual: the MCP tools are missing at session start, and a session works around them silently | rung: individual | why: whether the server is registered lives in the user's Claude Code config, outside the repo | control: CLAUDE.md's rule (DEC-25): set the server up, use the CLI for the session, ask the owner to restart; manual-mode.md § When the MCP tools are missing
F: the server needs a restart whenever the engine changes, by the owner, after each engine change or install; it goes stale when the engine on disk is newer than the running process
A: every tool is also a CLI subcommand and a manual-mode.md section, so nothing is reachable only through the server
M: the server holds no state but the remembered caller; every operation is the shared ops function
E: one name per operation across library, CLI and MCP (`<group>_<verb>`), registered from one table
