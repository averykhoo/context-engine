---
type: Decision
id: DEC-4
title: Try a script or MCP before edit subagents
actor: owner
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [housekeeping]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
---

Owner: *"edit subagents were also a considered option, but if a script (or mcp) might work lets
try that out first"*. Housekeeping is built as a no-model script (tier 0) and the engine's `hk_`
MCP operations (tier 1); agents that hand-edit files for the session are deferred (FRAMEWORK
§6.11). Reopen if the trial shows typed operations cannot cover a routine edit.

## Amendments
