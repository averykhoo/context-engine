---
type: Task
id: CE-201
title: 'ask_options after CE-158: untested placeholder clause, stale AC-121 row, loose refusal wording'
brief: The placeholder test must be seen red first; AC-121 changes only through criterion set
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-07d
created: 2026-11-07
moved: 2026-11-07d
updated: 2026-11-07e
---

Owner-question options after CE-158: an untested clause, a stale criterion row and loose wording.

Source: CE-158's verifier r2 (e4d2302), residuals that did not block PASS.
- Test gap: the "placeholders aside" clause of guards.py::ask_options (a placeholder-only list item such as `- <option>` does not block bold options) survived a sabotage (`return said if items else bold`): all `-k ask` tests stayed green. Add a case and see it red. Repro: .scratch/ce-158/v2/sab.py, case A (gitignored; copy the case into the test).
- docs/criteria.md AC-121 still says "one list item or ### heading each" and "a heading, a bold label and a plain label all mark a part"; change it with `criterion set` to what DEC-175 (amended) rules.
- guards.py::ask_problems and guards.py::ASK_REMEDY still say "(one list item each)", though bold-led lines count when Options has no list item or `###` heading.
- Two ambiguous shapes, both as at c527d60: a bold option followed by unindented bullets passes as those bullets; bold options followed by an unindented `- note` is refused. Decide whether either is worth a rule (DEC-175's reopen condition).

## Traps

- Every sabotage with a fresh PYTHONPYCACHEPREFIX.

## Read first

- DEC-175
- guards.py::ask_options

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): e5815ba: CE-201: file CE-158's verifier residuals (placeholder test gap, AC-121 row, wording)
