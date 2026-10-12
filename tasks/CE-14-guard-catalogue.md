---
type: Task
id: CE-14
title: "The guard catalogue (FRAMEWORK §8.1 to §8.5) as engine lint guards"
brief: "Minimum set first (§11.1); every guard sabotaged red before it is believed; each docstring says what it does not check"
pri: NOW
state: open
deps: [CE-2]
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-12d
updated: 2026-10-12d
closed:
review: [guard]
---

The engine's lint framework (CE-1, CE-2) carries the record-level guards; this item builds the
rest of the catalogue: intent (G-I), trace and existence (G-T), doc (G-D), working-state (G-W)
and verification-state (G-V) guards. Start with the §11.1 minimum set, then the §11.2 triggers
this repo actually hits. Part of G7 (DEC-10).

## Traps

- A guard that fails by passing is the house failure mode: sabotage each one and watch it go
  red before claiming it.
- Existing repos keep their own check numbers; the package maps onto them (§8.0, P3).

## Read first

- `docs/framework/FRAMEWORK.md` §8.0, §8.1 to §8.5, §11.1, §11.2

## Log

- 2026-10-12d (claude-code/claude-opus-5-5): built G-D1, G-D2 (at rest), G-D3, G-D7, G-D8, G-D9, G-T3, G-W7 and [guards] switches in src/context_engine/guards.py; tests/test_guards.py (AC-43..AC-51); tools/sabotage_ce14.py 32 rows all red; split G-D4+G-D5 to CE-33 and G-T5 to CE-34; G-I/G-T1/T2/T6 stay CE-25

## Design review

affects: the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- eliminated: a typo in `[guards]` silently switching a guard off: an unknown key or an `off` id lint does not report is refused at config load, and a listed path that does not exist is a red of that guard
- reduced: a new guard that fails by passing | rung: reduce | control: tools/sabotage_ce14.py, 32 rows, all red on 2026-10-12d (DEC-11)
- reduced: false reds on prose (dated facts, wrapped lines, placeholders such as `file::symbol`) | rung: reduce | control: the exemptions each guard docstring lists, pinned by tests/test_guards.py
- residual: G-D3 and G-T3 grep each dotted part of a symbol as a word, so a renamed symbol whose old name still appears elsewhere in the file passes | rung: reduce | why: resolving definitions needs a parser per language, and the grep works for every file type | control: the citing rule in CLAUDE.md (grep that a symbol exists before citing it)
- residual: a doc missing from a `[guards]` list is not checked at all | rung: collective | why: owner words are append-only and frozen provenance is never edited, so a red there has no remedy and the lists are chosen per repo | control: the kit template's default lists; the coverage guard planned in CE-30
- residual: G-W7 cannot recheck the values of `state`, `pri` and `deps`, only the session keys | rung: reduce | why: the op log records which keys changed, not their values, and logging values would duplicate every record | control: write-time refusal in `task set` (BOARD_OWNED); G-W4 and G-W5 at rest
- residual: G-D9's example check is a word match, so a value copied from a spec example under a note that does not say so passes | rung: individual | why: the spec's examples are prose, with no list to compare against | control: the `wrong if` the note must state; review of the config diff
- residual: G-D8 does not see a session layer written as a sentence inside a banner bullet | rung: reduce | why: dated facts cite session keys mid-sentence and must pass | control: G-D1 line and byte caps on the note's route (the backstop, P6)
F: a moved or new doc means editing a `[guards]` list; a new guard adds its id to LINT_IDS, a test and sabotage rows; it goes stale when FRAMEWORK §8 rewords a guard
A: each guard is one function in `src/context_engine/guards.py`, done by hand from manual-mode.md § context-engine lint; `[guards] off` silences one with no code change
M: the config refuses unknown keys and ids; the kit template is the schema (AC-32) and passes G-D9 itself; the sabotage table stops on a pattern that no longer matches
E: reuses Failure, the `[[routes]]` table, the op log, and one case-exact lookup shared with `decision link`; one module, one runbook section
