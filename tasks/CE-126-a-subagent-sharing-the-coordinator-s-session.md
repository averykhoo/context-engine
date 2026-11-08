---
type: Task
id: CE-126
title: A subagent sharing the coordinator's session key defeats CE-125's per-session op-line split
brief: "From CE-125's build (2026-10-22b): subagents run under the parent key, so their lines cannot be told apart"
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-22b
created: 2026-10-22
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

A subagent sharing the coordinator's session key defeats CE-125's per-session op-line split.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-23f (claude-code/claude-opus-5-5): 2026-10-23f: design brief walked through with the owner; options A-D and recommendation B in the new ASK.
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: a subagent's op lines carry its lane (CE_AGENT/--agent/MCP agent = task id), and a commit takes by session and lane; work in d5f6ab1 and 17a814b..0a59a51 (DEC-274..DEC-282, PROVISIONAL, await owner review)
  residual risk: INV-211, INV-212, INV-213, INV-214, INV-215
