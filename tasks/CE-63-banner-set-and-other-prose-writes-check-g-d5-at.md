---
type: Task
id: CE-63
title: banner set and other prose writes check G-D5 at write time
brief: Closes INV-60; a write-time refusal is the twin of the guard on the stored files and calls the same check
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-22b
updated: 2026-10-22b
goals: [G-2]
status: deprecated
closed: 2026-10-22b
---

From CE-33's review (2026-10-13c, residual INV-60): banner set can store a hand-typed count G-D5 fails, and since CE-45 the engine commits it unchecked. Recommendation: when HANDOFF.md (or the written file) is under [guards] numbers, banner set refuses text G-D5 would fail, naming P5's forms as the remedy; G-D8 has the same gap and can share the hook.

## Log

- 2026-10-21b (claude-code/sonnet): Widen (adhoc AAR entry 18, docs/evidence/adhoc-feedback-2026-10-21.md; census F13): banner set accepted a banner lint then rejected and commit does not lint; also check G-D1 line width and G-D8 at write time, and make commit lint first.
- 2026-10-22b (claude-code/claude-opus-5-5): closed: done in 1083e1d
