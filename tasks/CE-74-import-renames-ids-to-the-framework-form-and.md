---
type: Task
id: CE-74
title: Import renames ids to the framework form and keeps each old id as a resolvable alias (DEC-37)
brief: 'Blocks CE-7: decision import refuses DEC with a pre-DEC-37 remedy; no aliases field or lookup exists (adhoc dry run F19)'
pri: NEXT
state: closed
deps: []
source: session 2026-10-14a
created: 2026-10-14
moved: 2026-10-14a
updated: 2026-10-14a
review: [record-kind, guard, write-op, shipped]
status: deprecated
closed: 2026-10-14a
---

Import renames ids to the framework form and keeps each old id as a resolvable alias (DEC-37).

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): closed: done in ee2ff09: import renames ids, old ids stay resolvable aliases (DEC-37)

## Design review

affects: every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- eliminated: decision import refuses the framework prefix and tells the adopter to keep the foreign one, against DEC-37
- reduced: an alias resolves to the wrong record or to two records (a live id, a criterion id, a case or zero-padded variant, a look-alike, one carried twice) | rung: reduce | control: every write that sets aliases and lint G-D2 refuse it (guards.py, Store.resolve); tests/test_decisions.py::test_every_write_and_lint_g_d2_refuse_an_alias_that_does_not_name_one_record
- reduced: a re-import duplicates records or mints a number already taken (an adhoc D-45 written before the merge) | rung: reduce | control: decisions.py::plan_import refuses with a remedy; tests/test_decisions.py::test_a_reimport_refuses_an_old_id_already_imported_or_a_number_already_taken
- reduced: an imported decision is silently BUILT with no evidence | rung: reduce | control: the import's reply names how many were set BUILT by default and the decision set command to correct them
- reduced: a chosen --id reuses a number the op log shows was created, or is not canonical | rung: reduce | control: store.py::Store.create_many refuses it
- residual: answered questions from the old log (adhoc Q1..Q8) have no alias that resolves | rung: individual | why: a decision's aliases are fixed and ask answer cannot close on an existing decision | control: kit README § 3 says answered questions stay history
- residual: ids cited in imported bodies and titles stay plain text, so why misses them until linked by hand | rung: individual | why: parsing prose citations into links is not cheap or reliable | control: decision link by hand; manual-mode § decision import
- residual: a rejected row's new number (DEC-45..) can be read by a human as the old D-45 written later | rung: collective | why: rejected rows have no old number to keep | control: procedures § Bootstrap and kit README § 3 say to freeze the old log until the merge; the CE-7 trap re-checks it
- residual: task aliases can be moved or unset, so an old id can come to name a different record | rung: individual | why: boards are rewritten as work moves | control: task set names every alias it drops
- residual: a kind added later whose prefix matches existing aliases turns G-D2 red with no runbook fix | rung: individual | why: aliases on append-only decisions are fixed | control: G-D2 names the clash
- residual: dep, close, promote and comment take only live ids | rung: individual | why: writes resolve aliases only where a lookup is read | control: the refusal points at task show
F: stale when a new record kind or id form is added (the alias rule reads the configured series); the G-D2 alias tests name each refused form
A: aliases is a plain frontmatter list; the by-hand steps are manual-mode § decision import, § task set and § G-D2
M: one resolver, store.py::Store.resolve, behind every lookup; one alias rule, run at write and in lint
E: reuses decision import, task set, record new and G-D2; reviewed by correctness, a skeptic attacking alias resolution and an adhoc-trial user in a clone of adhoc; every finding fixed or filed above
