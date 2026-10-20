---
type: Task
id: CE-65
title: The baseline for reconciling foreign commits can skip a foreign commit made inside another session's life
brief: Any milestone now touches the ledger, so 'the newest ledger commit this session did not make' moves too often
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-20b
updated: 2026-10-20b
status: deprecated
closed: 2026-10-20b
---

From CE-55's review (2026-10-13c): procedures § Reconciling foreign commits starts from the newest ledger commit this session did not make; since milestones commit the ledger, another live session's milestone moves that baseline past foreign commits made earlier. Recommendation: key the baseline on the previous session close's commit (kind: close), or on the session start's own commit, and test it with two interleaved sessions.

## Log

- 2026-10-20b (claude-code/claude-opus-5-5): closed: done in 5775bf5
