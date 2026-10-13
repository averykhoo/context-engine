---
type: Task
id: CE-36
title: task close warns or refuses when it would leave NOW empty with NEXT empty
brief: Closing the only NOW item with NEXT empty turns the gate red on G-W5; say so at close time, with the promote remedy
pri: NEXT
state: open
deps: []
source: session 2026-10-12e
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
---

Seen 2026-10-12e: closing CE-10 (the only NOW item; NEXT empty since 2026-10-12d) left NOW at 0, and the next gate run was red on G-W5 before anything could be committed. The close itself succeeded silently. Options: refuse unless a successor id is named (e.g. `--then CE-n`), or close and print the G-W5 consequence plus the promote remedy. Picking the next NOW item stays the owner's call either way.
