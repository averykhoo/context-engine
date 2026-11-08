---
type: Task
id: CE-184
title: An adopter's checkout under core.autocrlf=true drifts to CRLF and stales its content-addressed gate rows
pri: NOW
state: closed
deps: []
goals: [G-6]
source: session 2026-11-04a
created: 2026-11-04
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

An adopter's checkout under core.autocrlf=true drifts to CRLF and stales its content-addressed gate rows.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): Found in CE-167 merge (2026-11-04a): the verified worktree was checked out with core.autocrlf=false, but zanzibar's main checkout runs under the system core.autocrlf=true and held 314 files as CRLF, so its tree id differed from the gated one and the gate rows did not apply. The merger rewrote them to their committed LF bytes (no content change). Any later checkout there writes CRLF again. Fix: the adoption sets core.autocrlf=false in the adopter's local config (or a .gitattributes eol=lf for the tree), and the procedures' bootstrap says so.
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: init warns where the checkout converts line endings, and the kit names the per-clone fix (work: 14c0642 DEC-270, 4ef4ead DEC-271, 1bf8e36 DEC-272, 9382ad0 DEC-273, 57694eb)
  residual risk: INV-208, INV-209, INV-210
