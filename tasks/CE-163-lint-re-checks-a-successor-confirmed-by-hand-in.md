---
type: Task
id: CE-163
title: Lint re-checks a successor confirmed by hand in a predecessor's words
brief: 'CE-102 residual (61735ae): a G-I2 check, or a register entry if not built'
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-06c
updated: 2026-11-06c
status: deprecated
closed: 2026-11-06c
---

Lint re-checks a successor confirmed by hand in a predecessor's words.

Source: CE-102's close (61735ae), residual (builder and verifier, 2026-10-31; left as the coordinator's call). `record confirm` refuses the words that confirmed a story the successor replaces, but only on the write: G-I2 does not re-check it, so manual-mode § context-engine record confirm's by-hand path has no lint backstop. Either a G-I2 check or a register entry.

## Traps

- none yet

## Read first

- working.py::Engine.confirm
- working.py::confirmation_words

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): closed: filed as a register entry instead of a G-I2 check (DEC-162): the task allowed either
  residual risk: INV-98
