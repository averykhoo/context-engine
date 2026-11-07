---
type: Task
id: CE-151
title: record new refuses a decision given --set supersedes or --set superseded_by
brief: Only decision supersede writes a supersede link, both sides at once (CE-149 residual, 345a14a)
pri: NEXT
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

record new refuses a decision given --set supersedes or --set superseded_by.

Source: CE-149's close (345a14a), residual. The supersede-links lint catches a one-sided link at rest, and decision set refuses these keys, but record new still writes them; decision supersede is the only route that writes both sides.

## Traps

- none yet

## Read first

- working.py::Engine.record_new

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: record new refuses --set supersedes / superseded_by on a decision (c0711b3); verifier PASS
  residual risk: none
