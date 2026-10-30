---
type: Task
id: CE-18
title: 'Rollback and close: end a session by undoing its changes, safely in a shared checkout'
brief: "US-13: undo only this session's commits and written paths; never stash or reset; runbook fallback"
pri: NEXT
state: open
deps: []
source: session 2026-10-09e
created: 2026-10-09
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-7]
---

Owner story US-13 (2026-10-09). Agent notes for the design are in FRAMEWORK §12.3 (Rollback and close). Owner words recorded this session must survive a rollback.

## Log

- 2026-10-12c (claude-code/claude-opus-5-5): Citation fix: "FRAMEWORK §12.3" in the body means the frozen docs/framework/FRAMEWORK-v0.5.md §12.3 (moved by DEC-26's 2026-10-11c trim); live FRAMEWORK §6.13 says only "not designed".
- 2026-10-30a (claude-code/claude-opus-5-5): rerank: Exit criterion 1 (G-7): section 6.13 says 'not designed', which is none of built, prose-only or deferred. Design it from v0.5 section 12.3, then record build-or-defer as a PROVISIONAL decision.
