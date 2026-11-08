---
type: Task
id: CE-194
title: 'FRAMEWORK principle beside P7: a green gate is the release decision, so a human-only check is a board item to automate (US-20)'
brief: 'US-20: owner words; change FRAMEWORK in place (DEC-19) and the kit contract only via a contract bump'
pri: NOW
state: open
deps: []
goals: [G-7]
source: session 2026-11-06e
created: 2026-11-06
moved: 2026-11-07e
updated: 2026-11-07e
---

A green gate is enough to ship, as a framework principle (US-20, owner 2026-11-06e; audio-workspace feedback item 2, its D-407). Add it to FRAMEWORK.md beside P7: the gate is the whole release decision, so a check that only a human runs (a hand-run smoke driver, a manual playtest) is a board item to automate, not an accepted residual. Then decide what enforces it (a lint or a residual rule) and whether the kit contract text changes (a contract bump, like CE-132).

## Traps

- none yet

## Read first

- docs/stories/US-20-a-green-gate-is-enough-to-ship-a-framework.md
- docs/framework/FRAMEWORK.md (P7)

## Log

- 2026-11-06e (claude-code/claude-opus-5-5): Its criterion is AC-184 (planned, from US-20).
- 2026-11-07e (claude-code/claude-opus-5-5): Built in 28aa329: FRAMEWORK §1 P19 (pointers in P7, §3.3, §7.4; table P1 to P19), RELEASE-NOTES 0.6 bullet, tests/test_principles.py (AC-184 tested, sabotaged). Decisions DEC-307..DEC-310 (PROVISIONAL). Follow-ups: CE-206 (the manual-criterion lint and refusal), CE-207 (contract line at the next contract bump). Kit contract unchanged. Left open for the verifier; close with residual none (the enforcement gap is on the board as CE-206).
