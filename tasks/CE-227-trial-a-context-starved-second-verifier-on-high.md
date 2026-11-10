---
type: Task
id: CE-227
title: Trial a context-starved second verifier on high-risk tasks (10 tasks)
pri: NEXT
state: open
deps: []
goals: [G-1]
source: session 2026-11-10c
created: 2026-11-10
moved: 2026-11-10c
updated: 2026-11-10c
---

Trial a context-starved second verifier (DEC-327, idea 4): on high-risk tasks, a second verifier gets only the spec (the task body and criteria) and the diff, with no plan and no builder report. It tests whether the plan's framing biases our verifier.

- Trial: 10 tasks. Record per task the defects each verifier found, their overlap, and the extra cost (about +$0.5 per task, since verifiers run cache-cold per US-23).
- Adopt it for a task class only if the starved verifier finds real defects the normal one missed.
- Define "high-risk" before the trial: for example, code touching the engine's write path, or an unpinned design.
