---
type: Task
id: CE-209
title: 'ask answer over several questions: one quote, one commit, each decision names what it accepted (audio-workspace items 5, 10)'
brief: CE-113's --ruling is for delegations only; this is the owner's own 'okay to all'
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

`ask answer` over several questions: one quote, one commit, and each decision names what the owner's words accepted (audio-workspace feedback items 5 and 10).

**What happened** (audio-workspace `docs/context-engine-feedback.md`, agent-raised, 2026-11-06): entry 5, the owner answered three questions there with "okay to all" (ASK-98/99/100, its D-404..D-406); the verbatim words say nothing of what was approved, only the agent-written `--title` does, and nothing ties it to the Recommendation the owner saw. Entry 10, four answers in one reply made four commits; a batch of answers is one owner act.

**At HEAD cb362ca:** working.py::Engine.ask_answer takes one id and is a milestone, so one commit per answer (DEC-36). Its `--ruled-by`/`--ruling` (CE-113) cover only a ruling the owner delegated (guards.py::delegation_problems, G-I3), not the owner's own "yes to all".

**The ask:** (1) `ask answer` takes several ids with one `--file` of words and one title per id, refuses every id before writing any if one is closed, already answered or not a question, and commits once. (2) A flag (e.g. `--accepts-recommendation`) copies each question's Recommendation part, verbatim, into its decision, outside the owner's quote, so the decision says what the words approved.

## Traps

- The copied Recommendation is agent text: never inside the owner's quote, never read as `actor: owner` words (the same rule as CE-113's `## Ruling` section).
- Atomic: a refusal on the third id must leave the first two unanswered, with no op line, record or commit written.
- Adjacent, not the same: CE-190 (`ask answer --grant`, closed) and CE-113 (delegated rulings, closed).

## Read first

- src/context_engine/working.py::Engine.ask_answer
- src/context_engine/working.py::Engine._answer_decision
- src/context_engine/guards.py::delegation_problems
- tasks/CE-113-delegated-rulings-are-not-stamped-actor-owner.md
- C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md entries 5 and 10

## Log
