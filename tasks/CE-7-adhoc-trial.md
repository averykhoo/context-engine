---
type: Task
id: CE-7
title: "Adhoc trial cutover on a worktree branch, scored against the CE-4 rubric"
brief: "One revertible commit; adhoc keeps its paths and ids; stop if adhoc has a live session"
pri: LATER
state: open
deps: [CE-3, CE-4, CE-5]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-08a
closed:
---

In a worktree of adhoc, on a branch: write `context.toml` and `.mcp.json`; import the board,
"still owed" (as batons), the decisions and the session log into records; rewrite the rituals in
adhoc's `CLAUDE.md` and `HANDOFF.md` to use the engine; run real sessions; score them against
the CE-4 baseline. The owner decides whether the branch merges.

## Read first

- `docs/framework/FRAMEWORK.md` §8.0.3, §11.4
- `docs/decisions/DEC-5-framework-before-migration.md`, `DEC-6-adhoc-first.md`

## Log
