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
updated: 2026-11-07d
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

- 2026-11-07c (claude-code/claude-opus-5-5): fc317a7: CE-198: file the sonnet-builder trial; CLAUDE.md points to DEC-173's trial and size floor
- 2026-11-07d (claude-code/claude-opus-5-5): CE-187 (not a trial task: it changed the kit contract): opus builder, 698k subagent tokens over 4 agents (build 306k, verify r1 158k, fix r1 88k, verify r2 146k), 1 FAIL round (FRAMEWORK.md banner left at 0.5; owners_own's actor half unpinned), no escalation, no trap-class bug. A third opus baseline beside CE-195 and CE-197.
- 2026-11-07d (claude-code/claude-opus-5-5): CE-158: NOT eligible (sonnet scout: no criteria, the body names symptoms but not the behaviour, and the fix changes kit manual-mode § ask new), so opus builder; does not count. 543k subagent tokens: scout 81k (sonnet), build 154k, verify r1 101k, fix r1 113k, verify r2 94k; 1 FAIL round (a bold-line option rule regressed one case each way); no trap-class bug. The scout filter worked as designed.
- 2026-11-07d (claude-code/claude-opus-5-5): DEC-177 (owner) amends the trial shape: from CE-191 on, a task above DEC-173's size floor gets an opus planner first (reads the code; writes the behaviour, rejected options and edge cases as test inputs; records design calls as a PROVISIONAL decision), then the sonnet builder and the opus verifier. A task qualifies once the planner pins its design; a FRAMEWORK.md or contract change still keeps an opus builder. Per task, also record planner tokens and the verifier's DRIFT count. CE-161 is the last task run without a planner.
- 2026-11-07d (claude-code/claude-opus-5-5): CE-161: NOT eligible (sonnet scout: a symptom report with a hedged fix, no criteria; Store.heads has many callers), so opus builder; does not count. 604k subagent tokens: scout 67k (sonnet), build 152k, verify r1 113k, fix r1 129k, verify r2 143k; 1 FAIL round (the fix covered broken frontmatter but not a non-UTF-8 body, still a crash under G-W4/G-W12/G-W13); no trap-class bug. Verifier r2 (first to count design calls): 7 SOUND, 1 minor DRIFT. Last task under the scout shape; from CE-191 the DEC-177 planner shape.
