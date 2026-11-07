---
type: Task
id: CE-200
title: manual-mode § orient omits seven orient parts; AC-110's row is undated
brief: Both runbook copies byte-equal; AC-110 changes through criterion set
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-07d
created: 2026-11-07
moved: 2026-11-07d
updated: 2026-11-07e
---

manual-mode § context-engine orient omits seven parts orient emits; AC-110's row text is undated.

Source: CE-156's builder and verifier (a5b1570), outside CE-156's list.
- manual-mode.md § context-engine orient (both copies) does not describe seven conditional parts working.py::Engine.orient emits: 'Tasks the owner asked for' (CE-112), 'Next work waits on parked items' (CE-116), 'Plans to freeze' (CE-97), 'Unspecified stories' (CE-48), 'Housekeeping owed' (CE-6), 'Foreign commits to reconcile' (CE-101), 'Deprecated config' (CE-185). The CE-156 paragraph's "shown after part 4" is loose against the real order.
- docs/criteria.md AC-110's row still says '33 to 36 under load' with no date; its claiming test now pins the date and version in the kit README (change the row with `criterion set`).

## Traps

- Write "§ Intake, step 4", not "§ Intake step 4": test_every_procedure_step_names_an_existing_operation_and_its_by_hand_section reads the latter as a procedure reference.
- Count CR bytes with Python (b'\r'); Git Bash `grep -c $'\r'` and `od -c | grep` miscount.

## Read first

- working.py::Engine.orient
- docs/runbooks/manual-mode.md § context-engine orient

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): a6fa1d8: CE-200: file CE-156's out-of-scope residuals (orient parts, AC-110 row)
