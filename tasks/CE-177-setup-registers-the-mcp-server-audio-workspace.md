---
type: Task
id: CE-177
title: Setup registers the MCP server (audio-workspace feedback item 1)
pri: NOW
state: closed
deps: []
goals: [G-4, G-6]
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

Setup registers the MCP server (audio-workspace feedback item 1).

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Found in CE-167 (first-hand at pin 309641b): bootstrap.py::next_steps still calls MCP registration optional and init writes no MCP config. Options: (a) next_steps names the claude mcp add step and orient flags a session with no MCP server; (b) init writes a committed .mcp.json at the repo-relative env interpreter (per-OS form); (c) the plugin route as default. Owner to pick the route. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: setup registers the MCP server; orient names it until a tool call marks the clone (verifier PASS; commits 1a00ac3 01ec225 7bd06b0 c95b47e 1edd767 4d7b098 baf3912)
  residual risk: INV-198, INV-199, INV-200, INV-201, INV-202
