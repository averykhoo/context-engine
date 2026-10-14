---
type: Decision
id: DEC-42
title: The adhoc trial runs in adhoc's own folder, on main; the worktree is deleted
actor: owner
decision_status: BUILT
decided: 2026-10-14
session: 2026-10-14e
body_sha: sha256:162c925adacc760a4516312acecac2c0855e544527da7142808335244f53ba35
tasks: [CE-7]
---

Owner, 2026-10-14e, verbatim, on learning the trial was set up in a worktree (C:/Users/user/PycharmProjects/adhoc-microphone-array-ce) rather than adhoc's own checkout: "oh wait no it needs to be in the actual folder, not a separate worktree", then "delete the worktree".

So the adhoc trial runs in adhoc's own folder (C:/Users/user/PycharmProjects/adhoc-microphone-array, branch main): the trial branch `context-engine-trial` is fast-forwarded into main, the engine env (DEC-41) is rebuilt at the same pin inside that folder, the MCP server and the SessionStart hook point at it, and the worktree is deleted. This replaces the owner's instruction of 2026-10-13b (CE-7 log: "do the cutover in a worktree branch, touch nothing in adhoc's main checkout"), which was given while another session was live in adhoc; that session has ended. The merge decision CE-7 left to the owner is made by this: the trial is on main.
