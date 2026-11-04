---
type: Task
id: CE-184
title: An adopter's checkout under core.autocrlf=true drifts to CRLF and stales its content-addressed gate rows
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-04a
created: 2026-11-04
moved: 2026-11-04a
updated: 2026-11-04a
---

An adopter's checkout under core.autocrlf=true drifts to CRLF and stales its content-addressed gate rows.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): Found in CE-167 merge (2026-11-04a): the verified worktree was checked out with core.autocrlf=false, but zanzibar's main checkout runs under the system core.autocrlf=true and held 314 files as CRLF, so its tree id differed from the gated one and the gate rows did not apply. The merger rewrote them to their committed LF bytes (no content change). Any later checkout there writes CRLF again. Fix: the adoption sets core.autocrlf=false in the adopter's local config (or a .gitattributes eol=lf for the tree), and the procedures' bootstrap says so.
