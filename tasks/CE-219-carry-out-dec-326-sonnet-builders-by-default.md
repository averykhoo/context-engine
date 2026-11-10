---
type: Task
id: CE-219
title: 'Carry out DEC-326: sonnet builders by default for pinned-design code tasks (CLAUDE.md, fan-out.md, FRAMEWORK 6.6)'
pri: NOW
state: open
deps: []
goals: [G-1]
source: session 2026-11-10a
created: 2026-11-10
moved: 2026-11-10b
updated: 2026-11-10c
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
