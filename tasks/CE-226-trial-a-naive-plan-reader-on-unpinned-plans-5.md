---
type: Task
id: CE-226
title: Trial a naive plan reader on unpinned plans (5 plans)
pri: NEXT
state: open
deps: []
goals: [G-1]
source: session 2026-11-10c
created: 2026-11-10
moved: 2026-11-10c
updated: 2026-11-10c
---

Trial a naive plan reader (DEC-327, idea 3). Elephant-goldfish's comprehension reviewer sees the document alone; a builder is effectively such a reader.

- On plans that do not pin the design, a sonnet agent reads only the plan and lists every unstated assumption, undefined term or step it could not carry out. The planner then revises.
- Trial: 5 plans. Compare what it found with the defects the verifier later found on the same tasks, and record the cost (about $0.2-0.5 per plan, estimated).
- Adopt it only if it catches defects the verifier would have caught at a fix round's cost.
