---
type: Task
id: CE-198
title: 'Trial: sonnet builders under an opus verifier on the next 6 pinned-design code tasks'
brief: comment each trial task's tokens, FAIL rounds and escalation here; verifier stays opus and never fixes
pri: NEXT
state: open
deps: []
goals: [G-1]
source: session 2026-11-07b
created: 2026-11-07
moved: 2026-11-07b
updated: 2026-11-07b
---

Trial sonnet builders under an opus verifier (DEC-173; shape from docs/evidence/article-takeaways-advice-2026-11-07a.md).

Scope: the next 6 code tasks whose design is pinned (criteria written, no open ASK, no change to FRAMEWORK.md, the contract or the kit). A task that fails the filter keeps an opus builder and does not count.

Shape: builder `sonnet`, verifier `opus` and never the fixer (DEC-44 independence). A second verifier FAIL sends the next fix round to `opus` (escalated).

Measure, per task, as a `task comment` on this item: subagent tokens (builder + verifier + every round), FAIL rounds, escalated yes/no, and whether a trap-class bug (CRLF, kit byte-equality, pycache, Linux divergence) reached the verifier. Baseline: CE-195 (1.15M, opus) and CE-197 (~926k, opus, 3 FAIL rounds).

Decides: adopt if the median tokens per task fall by 30% or more and FAIL rounds rise by at most one; drop it if two tasks escalate. Close this item with the verdict and the numbers, and the owner rules on DEC-45.

## Traps

- Without the per-task numbers the trial is another anecdote: comment each task's figures when it closes.
- Sum a task's edits before applying the size floor; splitting a task into sub-floor edits is gaming it.

## Read first

- docs/evidence/article-takeaways-advice-2026-11-07a.md
- DEC-173

## Log
