---
type: Task
id: CE-61
title: prose() reads a leading thematic break as frontmatter and lets ~~~ close a backtick fence
brief: Closes INV-61; one shared reader serves G-D3, G-D5 and G-D7, so a fix moves all three
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-2]
status: deprecated
closed: 2026-10-23a
---

From CE-33's review (2026-10-13c, residual INV-61): guards.py::prose treats a doc opening with --- as frontmatter and toggles a fence on ~~~ inside a backtick fence, hiding lines from G-D3, G-D5 and G-D7. Recommendation: frontmatter only when the block parses as YAML key lines and closes; a fence closes only on its own marker; near-miss fixtures for each.

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in ae02e5e (sweep 2026-10-23a; verified by an independent agent, gate green on main)
