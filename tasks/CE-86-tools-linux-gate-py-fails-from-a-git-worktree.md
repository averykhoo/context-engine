---
type: Task
id: CE-86
title: tools/linux_gate.py fails from a git worktree (exit 128); it works only from a plain clone
brief: From CE-77's review, 2026-10-15a; reviewers worked around it with a temp clone
pri: LATER
state: closed
deps: []
source: session 2026-10-15a
created: 2026-10-15
moved: 2026-10-19f
updated: 2026-10-19f
status: deprecated
closed: 2026-10-19f
---

CE-77 review (session 2026-10-15a): tools/linux_gate.py run from a worktree under context-engine-wt/ exits 128 (git cannot follow the worktree's .git file inside the container, presumably); the reviewers ran it from a temp clone instead. Worktrees are how DEC-16 fan-outs run, so the Linux gate should work from one.

## Log

- 2026-10-19f (claude-code/claude-opus-5-5): closed: 331e809: linux_gate mounts the common git dir; ran green from a worktree
