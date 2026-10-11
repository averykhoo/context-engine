---
type: Task
id: CE-9
title: "Trim FRAMEWORK.md under a cap; move its change history out"
brief: "112 KB on 2026-10-08, breaking its own P6. Move history, never rewrite it; keep section numbers"
pri: LATER
state: closed
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-11c
updated: 2026-10-11c
closed: 2026-10-11c
status: deprecated
---

FRAMEWORK.md grew from 78 KB (v0.4) to 112 KB (v0.5). Move §13's change tables into their own
file (`docs/framework/CHANGES.md`), keep every section number (P3), and consider a cap.

## Log

- 2026-10-11c (claude-code/claude-opus-5-5): closed: FRAMEWORK.md now holds only the framework (DEC-26): v0.5 archived verbatim as FRAMEWORK-v0.5.md; history, prior art, owner answers (§12) and the changelog (§13) left with it; section numbers kept. 141 KB to 106 KB. No cap added: the owner asked for a comprehensive spec, not a short one.
