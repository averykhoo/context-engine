---
type: Task
id: CE-18
title: 'Rollback and close: end a session by undoing its changes, safely in a shared checkout'
brief: "US-13: undo only this session's commits and written paths; never stash or reset; runbook fallback"
pri: NOW
state: closed
deps: []
source: session 2026-10-09e
created: 2026-10-09
moved: 2026-11-07e
updated: 2026-11-07e
goals: [G-7]
status: deprecated
closed: 2026-11-07e
---

Owner story US-13 (2026-10-09). Agent notes for the design are in FRAMEWORK §12.3 (Rollback and close). Owner words recorded this session must survive a rollback.

## Log

- 2026-10-12c (claude-code/claude-opus-5-5): Citation fix: "FRAMEWORK §12.3" in the body means the frozen docs/framework/FRAMEWORK-v0.5.md §12.3 (moved by DEC-26's 2026-10-11c trim); live FRAMEWORK §6.13 says only "not designed".
- 2026-10-30a (claude-code/claude-opus-5-5): rerank: Exit criterion 1 (G-7): section 6.13 says 'not designed', which is none of built, prose-only or deferred. Design it from v0.5 section 12.3, then record build-or-defer as a PROVISIONAL decision.
- 2026-11-06c (claude-code/claude-opus-5-5): Moved NEXT->LATER (DEC-162): the owner's ruling fills NEXT's five slots with CE-156, CE-158, CE-161, CE-47 and the louder close. Agent's call, PROVISIONAL; CE-18 was not named in the ruling.
- 2026-11-07e (claude-code/claude-opus-5-5): Designed: FRAMEWORK 6.13, procedures.md § Rollback and close, plugin skill rollback-and-close, tests/test_rollback_recipe.py; engine op deferred (DEC-322) to CE-215; design calls DEC-323.
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: FRAMEWORK 6.13 Rollback and close designed with its by-hand runbook section, skill and git-recipe test; engine op deferred to CE-215 (DEC-322)
  residual risk: INV-240, INV-241, INV-242, INV-243, INV-244, INV-245
