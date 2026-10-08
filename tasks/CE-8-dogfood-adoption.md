---
type: Task
id: CE-8
title: "The engine adopts this repo's hand-written records"
brief: "Stamp body_sha, make lint green, then switch this repo's rituals from hand edits to the tools"
pri: NOW
state: open
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08d
updated: 2026-10-08d
closed:
---

This repo runs the framework by hand (DEC-7). Once the engine can read and lint its records,
point it here: stamp `body_sha` on stories and decisions, fix what lint finds, move the
routing table from `CLAUDE.md` into `context.toml`, and rewrite the rituals in `CLAUDE.md` to
use the engine's operations.

## Traps

- Stamping freezes a body (G-D10): stamp only stories and decisions whose text is final; a later change is an `amend`.
- `status` and the other board-owned keys change only through their operation; `ce task set` refuses them (DEC-14 item 7).
- `session close` needs `--guards` and `--read`, and `--asked` naming every NOW or NEXT question; set `CE_SESSION` and `CE_ACTOR` once per session.
- The banner is written only with the hash `ce banner show` printed; another session's write in between makes `banner set` refuse.

## Read first

- `ce --help` and `src/context_engine/cli.py::build`
- `context.toml` § [working]; DEC-14
- `CLAUDE.md` § Rituals, the text this task rewrites

## Log

- 2026-10-08c: deps CE-3 -> CE-2. Adopt with the CLI as soon as it exists; the MCP server (CE-3)
  then lands on records that already run through the engine.
