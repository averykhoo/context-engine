---
type: Task
id: CE-148
title: "CE-138 verifier nits: G-I3 off switch also drops the Amendments refusal, unstated; record new remedy lacks 'in any case'"
brief: Docs and remedy wording only, unless the off-switch coupling is changed by a recorded call
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

CE-138 verifier nits (non-blocking), session 2026-10-30a, on main 9700437

1. `[guards] off = ["G-I3"]` also turns off the write-time `## Amendments` refusal (`working.py::Engine.record_new` and `Engine.ask_answer` gate it behind G-I3), a body_sha integrity check. DEC-88 records this cost, but neither FRAMEWORK §8.1 nor manual-mode states it.
2. `record new`'s remedy says `(never owner)` without 'in any case'; `ask answer`'s says it. The test asserts 'in any case' only for ask answer.
3. manual-mode's G-I3 lint entry names only '§ context-engine record new' as where the Amendments case is stopped at the write; `ask answer` step 2 stops it too (keep the kit copy byte-equal).
4. `tests/test_decisions.py`: the record-new refusal test repeats the owner-decision `dec(eng, body=AMENDS)` check in all 5 parametrize rows; redundant but harmless.

## Traps

- manual-mode.md has a kit copy that must stay byte-equal and LF.

## Read first

- DEC-88

## Log
