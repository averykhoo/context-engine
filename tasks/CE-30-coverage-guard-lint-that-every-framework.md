---
type: Task
id: CE-30
title: 'Coverage guard: lint that every FRAMEWORK component, ritual heading and G-id appears in the coverage map or on the board'
brief: The measure for G7; sabotage by deleting one map row; the map is FROZEN and dated, so the guard reads the newest one
pri: LATER
state: open
deps: [CE-14]
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-12b
updated: 2026-10-12b
---

Filed by CE-16 (docs/evidence/framework-coverage-2026-10-12.md). The map was checked by a one-off id diff on 2026-10-12; nothing keeps it true when FRAMEWORK.md gains a guard or ritual. A lint guard would grep the §2 component names, the §5.6 and §6.n headings and every G-id out of FRAMEWORK.md and refuse any that is in neither the newest coverage map nor a board item body.
