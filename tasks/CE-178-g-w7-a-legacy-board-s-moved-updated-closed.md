---
type: Task
id: CE-178
title: "G-W7: a legacy board's moved/updated/closed history has no import path"
pri: NOW
state: open
deps: []
goals: [G-6]
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-07e
updated: 2026-11-07e
---

G-W7: a legacy board's moved/updated/closed history has no import path.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Found in CE-167 (first-hand): any moved/updated/closed value no engine op wrote is red under G-W7 (855 lines on zanzibar's 303-record board). Worked around with taskpy_* keys. Fix: record those values as legacy on the import op line, or exempt values an import declares. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
