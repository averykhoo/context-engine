---
type: Task
id: CE-152
title: 'Session task lines: asked drops ids ID_RE cannot read back; pause resume does not re-apply tasks'
brief: CE-112 residuals (358dde6); refuse or keep, never drop an id silently
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

Session task lines: the asked line drops an id ID_RE cannot read back; pause resume does not re-apply a paused entry's tasks.

Source: CE-112's close (358dde6), two residuals.
- The `asked:` line has the ID_RE limitation session tasks now refuses: an ask id of a prefix ID_RE cannot read back drops out silently.
- A resuming session re-names a paused entry's tasks by a procedures step (session tasks), not automatically through pause resume.

## Traps

- none yet

## Read first

- working.py::Engine.session_tasks

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: ask raised refuses an id its asked line would not read back; pause resume names the paused session's open tasks (7c3b613; decisions DEC-193/194/195 in 5559de9, 0be816a, e920b8c)
  residual risk: INV-137, INV-138, INV-139, INV-140
