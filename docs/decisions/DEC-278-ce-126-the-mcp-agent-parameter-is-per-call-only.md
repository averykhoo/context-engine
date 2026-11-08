---
type: Decision
id: DEC-278
title: 'CE-126: the MCP `agent` parameter is per call only: never remembered in the server state, and no CE_AGENT fallback in the shared server process'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a69ad934d28e14d900f70388c9b4d91eef908ee17ffe7d517748d3d1e9b2fff7
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: how the MCP server takes a lane.

The MCP tools take `agent` per call only (`mcp.py::make_tool`). It is never remembered in the server's state, as `session` and `actor` are after `session_start`, and the server never reads `CE_AGENT` from its environment. One server process serves the coordinator and every subagent it spawns (FRAMEWORK §8.0.2), so a remembered or inherited lane would label the coordinator's later writes as a subagent's, and the coordinator's own commits would then leave them out.

Rejected: remembering the last `agent`; a `CE_AGENT` fallback at server start.

Cheap to undo: one keyword popped in one function.
