---
type: Task
id: CE-66
title: "Small fixes from CE-55's review: pause open reads git status -z; sabotage_ce45 needs a __main__ guard and fresh patterns"
brief: Each needs a test seen red
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

From CE-55's review (2026-10-13c): (1) pause open matches git status output against the carried set, but git quotes non-ASCII paths, so they are over-listed as uncommitted; read git status -z. (2) tools/sabotage_ce45.py runs on import (no __main__ guard) and its row 2 pattern no longer matches the moved code, so the table cannot be re-run.

## Log

- 2026-10-19f (claude-code/claude-opus-5-5): closed: c6f0dbc: pause open parses status -z; sabotage_ce45 has a __main__ guard and a stale-pattern preflight
