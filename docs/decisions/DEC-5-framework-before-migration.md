---
type: Decision
id: DEC-5
title: Build the framework and engine before migrating existing repos
actor: owner
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [adoption]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:8801b1d3b74c9785f4aba99db6ad82625ef615c77141f7cc840bef59b50083a8
---

Owner: *"but for now we'll work on the framework not the migration"*. zanzibar's
`tasks/closed/`, audio-workspace's and adhoc's single-file decision logs, and every other
existing record stay where they are. The adhoc trial (CE-7) is the first adoption, done on a
branch in a worktree as one revertible commit.

## Amendments
