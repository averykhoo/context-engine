---
type: Story
id: US-5
title: Task state is a field with a tool to list and sort; no database
actor: owner
via: Claude Code chat session 2026-10-08a
date: 2026-10-08
story_status: live
goals: [G1, G5]
body_sha: sha256:1b07f2c86f715162689d3c310ff8cacd177f1a1d2b0003ff30b9fd9aaf9f91e7
---

## Owner's words (verbatim)

> okay to not move tasks, it was done that way to make it easy to ls the folder and get all open
> and closed tasks, but having a status in there and a tool to grep for open and closed and list
> and sort is also fine. i guess it could also be sqlite but thats not as friendly to human
> readers/editors or git

## Amendment 1 (2026-10-08, owner, same session)

> tasks in closed/ can migrate as long as the schema is updated and the status is set. one place
> for everything feels cleaner. but for now we'll work on the framework not the migration

## Notes

AGENT: the field is `state: open | closed`, because OKF reserves `status` (FRAMEWORK §9.3.1).
SQLite is DEC-9 (rejected as a source of truth). The migration deferral is DEC-5.
