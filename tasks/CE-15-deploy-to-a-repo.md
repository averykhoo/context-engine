---
type: Task
id: CE-15
title: "Deploy path: how any repo gets the system, as text Claude Code manages"
brief: "Bootstrap (§6.9) and adoption (§11) after dogfooding here; no server the owner starts (anti-goal, DEC-10)"
pri: NEXT
state: open
deps: [CE-8]
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-08f
updated: 2026-10-09c
closed:
---

The owner: *"lets start with it in here and dogfood it, then we'll figure out how to adopt it in
new repos"* (US-9). After CE-8, design how a repo, new or existing, gets the system: what is
committed (`.mcp.json`, `context.toml`, ritual text in `CLAUDE.md`, skills), how the engine is
found from its own env, how a version upgrade lands (G-D0), and how existing repos map rather
than move (§11.4). Feeds CE-7 and CE-11.

## Traps

- Anti-goal: nothing the owner starts or manages by hand. Any server is started by Claude Code
  as a session ritual (charter G4).
- Never install the engine into a target repo's environment (CLAUDE.md, DEC-1).

## Read first

- `docs/framework/FRAMEWORK.md` §6.9, §8.0.2, §8.0.3, §10, §11
- `docs/decisions/DEC-10-charter-confirmed-whole-framework.md`

## Log

- 2026-10-09b (claude-code/claude-opus-5-5): DEC-16 (FRAMEWORK §6.6, several tasks -> one subagent each, top level only reports) must ship in the deployed contract text, so every framework repo gets it.
- 2026-10-09c (claude-code/claude-opus-5-5): DEC-17 (ultracode has standing approval when used to minimize token/context consumption) is now FRAMEWORK §6.6 'Ultracode'; the deployed contract text must carry it, like DEC-16.
