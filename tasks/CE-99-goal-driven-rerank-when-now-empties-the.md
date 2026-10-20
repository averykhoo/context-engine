---
type: Task
id: CE-99
title: 'Goal-driven rerank: when NEXT holds no task, the coordinator reranks the board against the charter goals and the next milestone'
brief: 'Built 2026-10-20e; 2026-10-20f (DEC-64 amendment): orient says rerank due only when NEXT holds no task'
pri: NEXT
state: closed
deps: []
source: session 2026-10-19b
created: 2026-10-19
moved: 2026-10-20f
updated: 2026-10-20f
goals: [G-7]
closed: 2026-10-20f
status: deprecated
---

Owner, 2026-10-19b, verbatim:

"also i want to add a step to prioritize and rerank the tasks based on the stated project goals and whats left thats actually needed for the project to run / hit the next milestone. this will need to run when the now/next are all cleared, and i guess this should be triggered by the coordinator? help me think through this and recommend how to add this in"

## What exists (census 2026-10-19b, .scratch/rerank-census/census.md; §5.2 quotes checked first-hand)

- Goals G-1..G-7 are a table in docs/charter.md (parsed by guards.py::charter_goals); stories carry `goals`, tasks do not.
- No milestone concept anywhere (FRAMEWORK §5.5 "milestone" means an engine commit point).
- FRAMEWORK §5.2: "Do not re-rank at session start; re-rank at clean close." When NOW empties with items open, G-W5 goes red and the reply asks the owner which item to promote ("the engine picks none").
- working.py::Engine.orient prints "no NOW item" and suggests nothing.
- Housekeeping "never forms new intent", so this is its own procedure, not housekeeping. CE-90 (periodic review) is the nearest relative; DEC-48/CE-91 would make a reversible rerank the agent's call.

## Recommendation (pending owner answers)

1. Trigger: NOW empty (G-W5 red) on a task close, plus on owner request; orient prints "rerank due" instead of only "no NOW item".
2. Inputs: add a `goals` list to [kinds.task] (checked against charter goals like G-I1), and a "Next milestone" section in docs/charter.md: one named milestone with its exit criteria.
3. Procedure § Rerank: coordinator sends a ranking agent (opus) that reads the goals, the milestone, and every open item's brief and deps, persists a proposal to a file, and returns: per item keep/promote/demote/drop with a one-line reason tied to a goal or the milestone's exit criteria; items serving no goal flagged for SOMEDAY or retirement.
4. A second agent verifies the proposal (deps respected, caps NOW=1, NEXT<=5, every move cites a G-n or exit criterion).
5. Apply: the coordinator applies with task promote, one task comment per move carrying the reason; owner approves before applying (until DEC-48 lands, then only drops and milestone changes need the owner).
6. By-hand fallback in procedures.md and manual-mode.md (P16); clean-close step 4 stays a light reorder.

## Log

- 2026-10-20b (claude-code/claude-opus-5-5): Design answers recorded: DEC-64 (milestone = framework fully built, G-7; required task goals, backfilled; agent applies moves, owner approves drops and milestone changes) and its 2026-10-20b amendment (full rerank when NOW and NEXT are both cleared, or on owner request; a new owner direction only flags 'rerank due'; clean close keeps the light reorder). Building it still waits on the kit hold (DEC-63 does not cover CE-99).
- 2026-10-20c (claude-code/claude-opus-5-5): DEC-65 (owner, 2026-10-20c, ASK-15): the kit hold is lifted for CE-99; build it next. Promoted to NEXT.
- 2026-10-20e (claude-code/claude-opus-5-5): Builds FRAMEWORK §6.14 Rerank (the sprint) and procedures § Rerank. Before this item closes, G-D12 needs §6.14 owned elsewhere: a row in a new dated coverage map (docs/evidence/framework-coverage-<date>.md), or another open item naming §6.14.
- 2026-10-20e (claude-code/claude-opus-5-5): Verifier (2026-10-20e): the G-D12 concern above is wrong; guards.py::coverage counts closed items too, and lint stays clean after task close CE-99 (checked in a scratch clone). Ship verdict, no fix first; follow-ups filed. Backfilled goals flagged for the first rerank: G-7 likely missing on CE-34, CE-6, CE-12, CE-28, CE-42; CE-88 fits no goal; CE-61 may be G-5; G-1 on CE-17, CE-84 debatable.
- 2026-10-20e (claude-code/claude-opus-5-5): closed: done in 54d437c, 33d3832, a555396; verified 2026-10-20e
- 2026-10-20f (claude-code/claude-opus-5-5): reopened: owner 2026-10-20f (DEC-64 amendment): rerank due only when NEXT is empty
- 2026-10-20f (claude-code/claude-opus-5-5): closed: trigger narrowed in 393e9e4; verified 2026-10-20f
