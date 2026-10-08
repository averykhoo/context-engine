# Step-0 spike findings (2026-10-08)

Claude Code 2.1.280, headless (`claude -p`, `--model haiku`), Windows 11, Git Bash; MCP Python
SDK 2.3.0 (`mcp.server.mcpserver.MCPServer`: v2 renamed `FastMCP`). Driver: `run_probes.sh`;
server: `probe_server.py`; project config: `project/`; raw outputs: `runs/2026-10-08/`.
Each positive has a control that removes the thing under test and goes the other way.

| # | Claim (FRAMEWORK.md §6.1, §8.0.2) | Run A | Control | Verdict |
|---|---|---|---|---|
| 1 | `.mcp.json` expands `${VAR}` in `command`, `args` and `env` | the server started from `"command": "${CTX_PY}"` and answered | B, `CTX_PY` unset: `TOOL-UNAVAILABLE`, no call logged | **VERIFIED** |
| 2 | Subagents reach the parent's MCP server | main and subagent calls were answered by the **same pid** (3720), per the server's own log `calls.log`, not only per the model's report | none needed: the log is server-side | **VERIFIED: one process per Claude Code session, shared with its subagents** |
| 3 | SessionStart hook stdout is added to the model's context | the model quoted `zebra-4471`, which exists only in the hook's `echo` | C, hook removed: `PROBE-WORD NONE` | **VERIFIED** |
| 4 | The server ends with the session | pid 3720 was gone (`tasklist`) after `claude -p` exited | — | **VERIFIED** for a session exit |
| 5 | `/clear` restarts (or keeps) the server | not testable headless | — | **UNVERIFIED**; the design does not depend on it (sessions begin with an explicit `session.start`) |

Also observed:
- The server's working directory is the project directory Claude Code was started in, so the
  engine can take the repo root from its cwd.
- A project `.mcp.json` server needs approval; `"enabledMcpjsonServers": ["probe"]` in the
  project's `.claude/settings.json` pre-approved it for headless runs.
- **Line endings:** this checkout converts LF to CRLF (`core.autocrlf`). Any body hash the
  engine computes (G-D10) must normalise line endings first, or a Windows checkout of a
  record written on Linux reads as edited.

`run_probes.sh` reproduces the commands that were run by hand for this record; it was written after the runs, from them.

Caveat: all runs are headless. Interactive sessions were not exercised; claims 1–4 are
expected to hold there but that is REASONED, not observed.
