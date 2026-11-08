---
type: Decision
id: DEC-277
title: 'CE-126: the coordinator-only ops refuse a lane: session start, close, pause and pause open'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2e4a8e9f56f161dec15bff431fb957c7488a040038f68f1d6c54f21e53e11df1
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: which operations refuse a lane.

`session_start`, `session_close`, `session_pause` and `pause_open` are the coordinator's (`ops.py::COORDINATOR_ONLY`): they start, end or pause the session whose key the subagents share. Called with a lane, `ops.py::Op.call` refuses before anything is written, with the remedy to unset `CE_AGENT` (or drop `--agent` / `agent`). A subagent that called one of them would otherwise end the coordinator's session from inside a lane, and its close would take every lane, other subagents' running work included.

Rejected: allowing them and ignoring the lane (silent; the subagent would not learn it did the coordinator's step).

Cheap to undo: one frozenset.
