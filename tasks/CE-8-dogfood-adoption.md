---
type: Task
id: CE-8
title: "The engine adopts this repo's hand-written records"
brief: "Stamp body_sha, make lint green, then switch this repo's rituals from hand edits to the tools"
pri: LATER
state: open
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-08c
closed:
---

This repo runs the framework by hand (DEC-7). Once the engine can read and lint its records,
point it here: stamp `body_sha` on stories and decisions, fix what lint finds, move the
routing table from `CLAUDE.md` into `context.toml`, and rewrite the rituals in `CLAUDE.md` to
use the engine's operations.

## Log

- 2026-10-08c: deps CE-3 -> CE-2. Adopt with the CLI as soon as it exists; the MCP server (CE-3)
  then lands on records that already run through the engine.
