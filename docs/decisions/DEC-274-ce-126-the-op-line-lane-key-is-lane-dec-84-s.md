---
type: Decision
id: DEC-274
title: "CE-126: the op-line lane key is `lane` (DEC-84's word), set from CE_AGENT, the global --agent or the MCP `agent` parameter; it sits right after `session` and is absent when unset"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:e7ab006a4e77e0ac6ae116f6abbf868ba8ed8b5dc9542012d37f4a1c5c21cc93
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: what the lane field on an op line is called, where it comes from, and where it sits.

The op-line key is `lane`, DEC-84's own word for it. It is set from `CE_AGENT` in the environment, the CLI's global `--agent` (which beats the environment), or the MCP tools' per-call `agent` parameter: the input names are the owner's words in DEC-84 too, so both are kept as given. `store.py::Store._log` writes it immediately after `session`, so a line cut short (CE-128) still names its lane, and it is absent when no lane is set, so a coordinator's line is byte-identical to what the engine wrote before CE-126 and no migration is needed.

Rejected: a key named `agent` (DEC-84 calls it a lane field); `lane` at the end of the line (a truncated line would lose it and be filed as the coordinator's).

Cheap to undo: a key name and a position in a dict literal.
