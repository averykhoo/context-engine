---
type: Task
id: CE-51
title: 'init appends a second ## Gate to a CLAUDE.md that already has one'
brief: Found by CE-26's deploy lens on main; init never overwrites, so merge or name the clash, not replace
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

From CE-26's deploy review (2026-10-13c, finding D#7, already on main before CE-26): running init on a repo whose CLAUDE.md already has a ## Gate section appends the bootloader's stub next to it, leaving two Gate sections. Recommendation: init detects an existing ## Gate and leaves the stub out, saying so in its output, or lint reds a duplicate heading in CLAUDE.md.
