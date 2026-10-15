---
type: Task
id: CE-86
title: tools/linux_gate.py fails from a git worktree (exit 128); it works only from a plain clone
brief: From CE-77's review, 2026-10-15a; reviewers worked around it with a temp clone
pri: LATER
state: open
deps: []
source: session 2026-10-15a
created: 2026-10-15
moved: 2026-10-15a
updated: 2026-10-15a
---

CE-77 review (session 2026-10-15a): tools/linux_gate.py run from a worktree under context-engine-wt/ exits 128 (git cannot follow the worktree's .git file inside the container, presumably); the reviewers ran it from a temp clone instead. Worktrees are how DEC-16 fan-outs run, so the Linux gate should work from one.
