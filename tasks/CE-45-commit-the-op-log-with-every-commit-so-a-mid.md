---
type: Task
id: CE-45
title: Commit the op log with every commit, so a mid-session commit passes lint alone
brief: A clean checkout of any commit before the close is red on G-W7; a dead conversation leaves op lines uncommitted
pri: NEXT
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
---

Found 2026-10-13b: per-task commits (2026-10-13a's too) leave docs/ledger/ops.jsonl and the session stub uncommitted until session close, so a clean checkout of any mid-session commit fails lint (G-W7 reads a task's moved against ops.jsonl), and a conversation that dies leaves its op lines dirty in the shared tree for another session's close to sweep up. Options: each engine write commits its own op line by path (FRAMEWORK §5.5 rule 4, today only pause open does); or rituals require the op log in every commit; or G-W7 tolerates an op log behind HEAD. Recommendation: the engine commits its own working-state writes, as §5.5 already intends, with the ritual as the by-hand fallback. 2026-10-13b worked around it by committing ops.jsonl with its commits.
