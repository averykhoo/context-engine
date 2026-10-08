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
updated: 2026-10-08a
closed:
---

Add a workflow that installs the package with `[dev]` on Python 3.12 and runs pytest. Pushing
it needs the owner's permission, and its first run gets a CI watcher (global `CLAUDE.md`).

## Traps

- **CI minutes are limited** (owner, 2026-10-08: *"its currently private so I don't have
  unlimited compute so let's not run that too much"*). Keep the workflow cheap: one job, pip
  cache, skip docs-only pushes (`paths:` filter), and consider running only on PRs or by hand.
- Adding it ends the "push whenever" permission in `CLAUDE.md`; update that line in the same
  commit.

## Log
