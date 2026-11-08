---
type: Decision
id: DEC-305
title: "Tier-1 token count: the harness's figure for the agent run, put by the session in its close summary; the session persists the agent's reply on receipt"
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:75d1024dff985274c12cefbadacc848dbb715dbc38defce51ec515d9e00ad411
---

**Decision:** a tier-1 housekeeping run's token count (G-W10, DEC-21: measured, no budget) is the figure the harness reports for the agent's run (Claude Code: the agent's result), and the session puts it in its close summary; the engine does not see it. The agent has no Write tool, so the session persists the agent's reply on receipt; the op log is the durable record of the agent's writes.

**Why:** the engine never calls the model, so it cannot count the tokens; the harness can. Giving the agent Write to persist its own report would break "only hk_" (FRAMEWORK §6.11).

**Rejected:** an engine field or op for the token count (it would carry a number the engine cannot check); giving the agent Write.
