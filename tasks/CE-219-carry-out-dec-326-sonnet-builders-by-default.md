---
type: Task
id: CE-219
title: 'Carry out DEC-326: sonnet builders by default for pinned-design code tasks (CLAUDE.md, fan-out.md, FRAMEWORK 6.6)'
pri: NOW
state: closed
deps: []
goals: [G-1]
source: session 2026-11-10a
created: 2026-11-10
moved: 2026-11-11a
updated: 2026-11-11a
status: deprecated
closed: 2026-11-11a
---

Carry out DEC-326 (owner's ruling on DEC-45, from CE-198's ADOPT): sonnet builders become the default for code tasks whose plan pins the design, above DEC-173's size floor. An opus planner and an opus verifier stay, and a task escalates to opus after 2 FAIL rounds.

- Rewrite CLAUDE.md's Coordinator line, which still calls it a trial.
- Update docs/runbooks/fan-out.md (kit copy, byte-equal), FRAMEWORK §6.6 and the advice doc DEC-173 names, in place.
- The banner's Lesson line says to "try sonnet builders (CE-198, comment each task's numbers)". Drop the per-task comment duty, and decide whether one cheap metric stays.

## Read first

- DEC-326, DEC-45, DEC-173, CE-198's Log
- docs/evidence/article-takeaways-advice-2026-11-07a.md

## Log

- 2026-11-10c (claude-code/claude-opus-5-5): de35180: CE-219: promote to NOW (owner, 2026-11-10)
- 2026-11-11a (claude-code/claude-haiku-5-5): closed: CE-219 done: DEC-326 carried out. Sonnet builders are the default for pinned-design code tasks above the DEC-173 size floor; opus planner and verifier stay; a task escalates to opus after 2 FAIL rounds. Work commit 5f38ddd; decision and board commits 1d9c7e9 62e60f6 e82a905 b836608 bd92541 8023ad6 ce7ea6e 7bc2b19. Independent verifier PASS.
  residual risk: INV-246, INV-247, INV-248, INV-249, INV-250, INV-251
