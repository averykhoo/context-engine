---
type: Task
id: CE-152
title: 'Session task lines: asked drops ids ID_RE cannot read back; pause resume does not re-apply tasks'
brief: CE-112 residuals (358dde6); refuse or keep, never drop an id silently
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
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
