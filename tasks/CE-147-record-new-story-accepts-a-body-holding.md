---
type: Task
id: CE-147
title: 'record new story accepts a body holding ## Amendments; the text below falls outside body_sha'
brief: Refuse it at the write (seen to fail, DEC-11) or name it under Not checked; decisions do this since CE-138 (DEC-88)
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

record new story accepts a body holding ## Amendments

Found by CE-138's builder and its verifier (session 2026-10-30a). Since CE-138 (main 9700437, DEC-88), `record new` of a decision and `ask answer` refuse a text holding a `## Amendments` line through `guards.py::delegation_problems(new=True)`. `record new story` does not: a story body holding that line is created with the text below it outside `body_sha`, where it reads as an amendment.

Options: a general refusal in `store.new` for every append-only kind (DEC-88's option c), or a story-only check; or name it under a Not checked line.

## Traps

- DEC-88's refusal sits behind G-I3's off switch; a story check should not.

## Read first

- DEC-88
- src/context_engine/guards.py::delegation_problems

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 7b5a75e, review fix 917261f (lane wt/2026-10-30a-amend: 9b5f35d, c48112a): record new refuses a ## Amendments line for stories and decisions, and ask answer and ask new --answered refuse one, whatever [guards] off names; AC-140, DEC-125
