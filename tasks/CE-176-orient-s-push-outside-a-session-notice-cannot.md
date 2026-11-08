---
type: Task
id: CE-176
title: "Orient's push-outside-a-session notice cannot be cleared: no op records a push"
brief: working.py::upstream_lines only checks session windows; seen in intervals 2026-11-03a; not reproduced first-hand
pri: NOW
state: closed
deps: []
goals: [G-6]
source: session 2026-11-03a
created: 2026-11-03
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

Orient's push-outside-a-session notice cannot be cleared: no op records a push.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: orient's push-outside-a-session flag is cleared by a pushed: close receipt; verifier PASS; work in 2eb3b93 (DEC-237), dba1858 (DEC-238), 11f6039 (DEC-239), b69222d
  residual risk: INV-178, INV-179, INV-180
