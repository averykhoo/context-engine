---
type: Decision
id: DEC-193
title: Pause resume names, never re-applies, the paused session's tasks (CE-152)
actor: agent (claude-sonnet-5-5)
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2729c7a395849423040df08e2eed5cd05889b5a0ca06a3e8439715a622caad55
---

The agent's call on CE-152, made while building it in session 2026-11-07e: what `pause resume` does about the paused session's `tasks:` line.

Options:
(A) apply the paused entry's tasks to the resuming session in `pause resume`;
(B) a `--tasks` flag on `pause resume`;
(C) do nothing, leaving the procedures § Resume step to memory;
(D) name the still-open tasks in the reply and leave applying them to the procedures step.

Chose (D). Session-start housekeeping also resumes a pause whose paths are all committed; that session is not taking up the owner's request, so naming the tasks for it would make its close fail G-W6 for someone else's tasks, and would need the procedures row (a kit file) changed. (B) adds CLI and MCP surface for what `session tasks` already does. (C) leaves the step reliant on memory. Cheap to undo: one reply clause in `working.py::Engine.pause_resume`.
