---
type: Task
id: CE-10
title: "Run the gate in GitHub Actions on push"
brief: "Its own commit; CI changes stay out of feature work"
pri: LATER
state: open
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-10a
closed:
---

Add a workflow that installs the package with `[dev]` on Python 3.12 and runs pytest. Pushing
it needs the owner's permission, and its first run gets a CI watcher (global `CLAUDE.md`).

## Traps

- **The repo is public** (owner, 2026-10-10, DEC-22), so GitHub Actions minutes are free. The owner's earlier words (2026-10-08: *"its currently private so I don't have unlimited compute so let's not run that too much"*) no longer bind; a cheap workflow (one job, pip cache, `paths:` filter for docs-only pushes) is still the aim.
- Pushes are asked for every time and made only on a green gate (DEC-22); CI does not change that.

## Log
