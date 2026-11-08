---
type: Decision
id: DEC-262
title: 'CE-177: contract and FRAMEWORK 11.1 unchanged, no framework bump; 6.9 and 8.0.2 follow DEC-155'
tasks: [CE-177]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:46af7e6880c6861a5279049d20cbe42a33b2a1f541ea05e0afb7776b9bdc1ccb
---

A build-time call for CE-177, the agent's own, PROVISIONAL until the owner reviews it.

The framework contract (`kit/contract.md`) and FRAMEWORK §11.1 are unchanged: the MCP server stays out of the framework's minimum set until the §8.0.3 trial reports, and there is no framework minor bump. FRAMEWORK §6.9 and §8.0.2 wording follows DEC-155: setup registers the server, and orient names the step until a tool call reaches the engine. Changing the contract to say setup registers the server is a separate owner item, since it needs a framework version bump.
