---
type: Task
id: CE-133
title: commit.py::taken_lines treats a HEAD with no op log like no HEAD and takes every line
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-23a
created: 2026-10-23
moved: 2026-10-23e
updated: 2026-10-23e
status: deprecated
closed: 2026-10-23e
---

commit.py::taken_lines treats a HEAD with no op log like no HEAD and takes every line.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-23e (claude-code/claude-opus-5-5): closed: Fixed in 8291569: commit.py::_head_oplog separates no commit (None) from a HEAD without an op log (""); taken_lines, pending and _commit select whenever a commit exists. Verified by a second agent (.scratch/ce-133/verifier.md): all claims confirmed, sabotage reproduced, CE-55 test rewrite keeps its guard.
