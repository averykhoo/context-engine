---
type: Task
id: CE-206
title: 'Lint: a `manual` criterion that no open board item names is red, and `criterion set --status manual` refuses it (FRAMEWORK P19)'
brief: 'P19 (CE-194): a guard id with a §8 entry and a coverage-map owner; refusal at write time and in lint (P7)'
pri: LATER
state: open
deps: []
goals: [G-3, G-7]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Lint: a `manual` criterion that no open board item names is red, and `criterion set --status manual` refuses it (FRAMEWORK P19).

FRAMEWORK §1 P19 (CE-194, US-20): a check only a human runs is a gap in the gate, filed as a board item to automate it. §3.3 says a board item to automate a `manual` criterion's driver stays open while the criterion is `manual`. Nothing enforces that yet. This item builds the guard: a lint in the gate and a write-time refusal (P7), with a guard id, its §8 catalogue entry, a coverage-map owner (G-D12) and its own sabotage.

The residual half of P19 (a hand-run check is never accepted as a residual, §7.4) is not mechanisable: a hand-run check described in a residual's prose is judgement, not a pattern, so the design review (§5.2) keeps it. See the CE-194 decisions.

## Traps

- Today this repo has no `manual` criteria, so the lint's floor needs a fixture repo to be seen red.

## Read first

- docs/framework/FRAMEWORK.md (§1 P19, §3.3)
- tests/test_principles.py

## Log
