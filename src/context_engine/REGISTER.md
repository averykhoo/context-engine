# Residual-risk register

Residual risks (FRAMEWORK P17, §7.4): each is a risk that was not reasonably practicable to
eliminate, with whom it affects, why it stays, the control that holds it and where it came from.
`task close` appends the residuals of a task's `## Design review`; edit an entry only when the
code changes. Ids are `INV-n`, never reused.

This is the engine's own register. It is package data, so it ships with the engine to every repo
the engine is pointed at: `context-engine register show --engine` reads it there, and `orient`
points at it (the handover, P17 regs. 7 and 11). A target repo keeps its own register for its own
risks (FRAMEWORK §10: `docs/invariants.md`).

## INV-1: a long-lived server keeps running old engine code after the engine changes, and it may outlive `/clear`

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** Claude Code owns the server process, and the engine cannot restart itself inside a session
- **control:** individual: CLAUDE.md asks the owner to restart Claude Code after setting up or changing the server (DEC-25); CE-13 checks what `/clear` does
- **from:** CE-3, session 2026-10-12b

## INV-2: a write is logged under the wrong actor or session, because the server remembers the first `session_start` and a subagent that passes no `actor` inherits the parent's

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** an MCP call carries no caller identity the engine can verify; the actor is self-declared (OKF §7)
- **control:** individual: the server instructions and CLAUDE.md tell each subagent to pass its own `actor`; G-W7 (not built, CE-14) will cross-check the op log
- **from:** CE-3, session 2026-10-12b

## INV-3: the MCP tools are missing at session start, and a session works around them silently

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** whether the server is registered lives in the user's Claude Code config, outside the repo
- **control:** individual: CLAUDE.md's rule (DEC-25): set the server up, use the CLI for the session, ask the owner to restart; manual-mode.md § When the MCP tools are missing
- **from:** CE-3, session 2026-10-12b
