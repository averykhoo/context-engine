---
type: Task
id: CE-48
title: G-T1 names the board item it counted for an unspecified story
brief: The CE-25 design review promised it; lint has no channel for output that is not a failure
pri: LATER
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-20e
goals: [G-2]
---

From CE-25's review (2026-10-13b, spec-fidelity F4, deferred): the design review's second residual says G-T1's message names the board item it counted for an unspecified story, so a passing mention is visible; lint prints only failures, so a green G-T1 says nothing. Options: a lint --verbose that prints what each guard counted; or orient lists unspecified stories with the item counted. Recommendation: orient, since the session reads it at intake anyway.
