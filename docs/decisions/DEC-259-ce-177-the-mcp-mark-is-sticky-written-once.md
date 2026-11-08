---
type: Decision
id: DEC-259
title: 'CE-177: the MCP mark is sticky: written once, never refreshed; deleting it brings the notice back'
tasks: [CE-177]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:99684d33ff00ddef9110c31b558702d953fde77aa0d5be1bfae6c10914cea147
---

A build-time call for CE-177, the agent's own, PROVISIONAL until the owner reviews it.

The MCP mark is sticky: written once, on the first tool call that reaches an Engine, and never refreshed. A server that later stops connecting is not flagged; deleting the file brings orient's notice back. A dated or refreshed mark would need a new config number with provenance (G-D9) and was not built.
