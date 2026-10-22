---
type: Task
id: CE-95
title: "Small fixes from CE-27's review: ask answer skips the plan-frozen check, exact-match config warning, liveness_given plan has no remedy"
brief: Three gaps left after 5fa4fcb; reviewer report 2026-10-16a
pri: LATER
state: closed
deps: []
source: session 2026-10-16a
created: 2026-10-16
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-2]
status: deprecated
closed: 2026-10-23a
---

From the CE-27 review and fix pass (session 2026-10-16a): (1) ask answer deprecates a board item without working.py::Engine._plans_frozen, so an ACTIVE-PLAN doc can outlive its last item that way; (2) doc archive's warning about context.toml entries still pointing at the old path matches only an exact quoted path; (3) doc freeze refuses a liveness_given doc, so task close's remedy for an ACTIVE-PLAN doc covered by liveness_given leads nowhere.

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 18a7db6 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
