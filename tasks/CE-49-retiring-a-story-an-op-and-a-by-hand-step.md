---
type: Task
id: CE-49
title: 'Retiring a story: an op and a by-hand step'
brief: G-I1 and G-I2 remedies can only say 'file a task' until a story can be retired
pri: NEXT
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
---

From CE-25's review (2026-10-13b, false-red-deploy F6, partly fixed in adfc6db): the G-I1 and G-I2 per-story remedies used to say 'record the story again and retire this one', but no op retires a story and manual-mode has no by-hand step; a hand edit of story_status on a stamped story passes lint, and nothing records who retired it or why. Recommendation: a record op that sets story_status (retired, with a superseded_by link where one exists) carrying the session key and an op-log line, its manual-mode section, then point both remedies at it.
