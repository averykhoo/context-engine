---
type: Task
id: CE-143
title: Drop the leak test's allowance for (CE-n) build marks in FRAMEWORK.md
brief: "Changes AC-33's criterion text: record the decision first (P14), then sabotage with a (CE-1) mark"
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

Drop the leak test's allowance for (CE-n) build marks in FRAMEWORK.md

`tests/test_kit.py::BOARD_MARK` still lets FRAMEWORK.md carry `(CE-n)` build-status marks ("explained in its Summary"), but CE-93 removed every mark and the Summary paragraph explaining them. Found by CE-93's builder and by both verifiers (verify-1 N2, verify-2 N6). Filed in session 2026-10-23f.

Drop the allowance so a build mark cannot come back, mechanically, and sabotage it (put a `(CE-1)` back in FRAMEWORK.md; the leak test must go red).

## Traps

- AC-33's criterion text names the allowance: changing it is a criterion change, so record the decision first (P14).
- The kit's own text and other docs the leak test reads may still rely on the allowance; run the whole test before narrowing it.

## Read first

- `.scratch/ce-93/verify-2.md` (Nonblocking N6) and `.scratch/ce-93/build.md` (Notes found on the way); both gitignored, so the finding is restated above
- `tests/test_kit.py::BOARD_MARK`, `tests/test_kit.py::test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths`; `docs/criteria.md` AC-33; DEC-81

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in e13f852 (lane 78ab6af): dropped tests/test_kit.py::BOARD_MARK and leaks()'s allow_marks, so FRAMEWORK.md is leak-checked like the kit and a (CE-n) build mark cannot come back. AC-33's text no longer names the allowance (DEC-93). tools/sabotage_ce26.py's expected string follows the new leaks() signature. Sabotaged: a (CE-1) put back into FRAMEWORK.md turns the leak test red.
