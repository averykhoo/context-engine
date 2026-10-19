---
type: Task
id: CE-52
title: Pin this repo's [guards] off list
brief: A guard switched off with no decision is a silent false green; a test, not a doc warning
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-19f
updated: 2026-10-19f
status: deprecated
closed: 2026-10-19f
---

From CE-26's false-pass review (2026-10-13c, FP#6): nothing stops a commit that adds G-R1, G-D1 or any guard to this repo's [guards] off list, which silences it with lint green. Recommendation: a test pins the off list to its current value and names the decision needed to change it.

## Log

- 2026-10-19f (claude-code/claude-opus-5-5): closed: a9fc2e0: tests/test_repo_records.py pins [guards] off = []
