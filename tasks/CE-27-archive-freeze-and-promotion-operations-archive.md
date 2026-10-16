---
type: Task
id: CE-27
title: 'Archive, freeze and promotion operations: archive with a redirect table, ACTIVE-PLAN to FROZEN, the §6.7 table at close'
brief: git mv only, never repair; first line ARCHIVED date; one redirect table per archive dir (FRAMEWORK §7.3)
pri: NOW
state: closed
deps: []
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-16a
updated: 2026-10-16a
status: deprecated
closed: 2026-10-16a
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): components 16 (evidence and plan docs) and 17 (archive), procedure §6.7 (promotion and demotion). FRAMEWORK §7.3 and §6.7: no tool moves material to an archive, writes its ARCHIVED line and redirect table, or freezes an ACTIVE-PLAN doc when its item closes; the §6.7 table is checked by nobody at close. Of the guards that trigger these, caps (G-D1) are built (CE-14) and liveness (G-D4) is CE-33.

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): From CE-33 (2026-10-13c): the freeze and archive operations should write what G-D4 reads (a FROZEN line or ARCHIVED <date> in the first 10 lines), and the close ritual should freeze an ACTIVE-PLAN doc before task close, or G-D4 reds it once its item closes.
- 2026-10-16a (claude-code/claude-opus-5-5): closed: done in c901367
- 2026-10-16a (claude-code/claude-opus-5-5): 5fa4fcb: review fixes (doc archive refusal writes nothing: all checks and reads, the redirect README included, before the first write, inside the lock; tests for non-UTF-8 README, repo-root and record-dir targets, record file; config warning sabotaged; Clean close rows 5a/5b with FRAMEWORK §6.3 5a/5b; plugin-design-2026-10-14.md frozen, which unblocks task close CE-7)
