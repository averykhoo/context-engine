---
type: Task
id: CE-97
title: Orient or housekeeping flags an ACTIVE-PLAN doc whose items were all closed outside the engine
brief: task close refuses an unfrozen plan; nothing catches one left by a by-hand close
pri: LATER
state: open
deps: []
source: session 2026-10-16a
created: 2026-10-16
moved: 2026-10-16a
updated: 2026-10-16a
---

CE-27 made task close refuse to close the last open item an ACTIVE-PLAN doc names. A close done by hand, or the ask answer path, bypasses it; 2026-10-16a found docs/evidence/plugin-design-2026-10-14.md still ACTIVE-PLAN after CE-77 closed. A housekeeping check or an orient line would catch it.
