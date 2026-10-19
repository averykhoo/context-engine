---
type: Task
id: CE-99
title: 'Goal-driven rerank: when NOW empties, the coordinator reranks the board against the charter goals and the next milestone'
brief: Design awaits owner answers (milestone record, task goals field, who approves); kit edit under the CE-7 freeze
pri: LATER
state: open
deps: []
source: session 2026-10-19b
created: 2026-10-19
moved: 2026-10-19b
updated: 2026-10-19b
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
