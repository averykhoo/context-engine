---
type: Task
id: CE-30
title: 'Coverage guard: lint that every FRAMEWORK component, ritual heading and G-id appears in the coverage map or on the board'
brief: The measure for G7; sabotage by deleting one map row; the map is FROZEN and dated, so the guard reads the newest one
pri: NOW
state: open
deps: [CE-14]
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-12e
updated: 2026-10-12e
review: [guard]
---

Filed by CE-16 (docs/evidence/framework-coverage-2026-10-12.md). The map was checked by a one-off id diff on 2026-10-12; nothing keeps it true when FRAMEWORK.md gains a guard or ritual. A lint guard would grep the §2 component names, the §5.6 and §6.n headings and every G-id out of FRAMEWORK.md and refuse any that is in neither the newest coverage map nor a board item body.

## Design review

affects: every later session, since lint runs in the gate (AC-23); the owner, whose attention a false red costs; every repo the kit deploys to, if the guard ships with `[guards]` defaults
- reduced: a FRAMEWORK.md edit adds a component, ritual or G-id that nothing owns, and no one notices | rung: reduce | control: this guard, sabotaged by deleting one map row and by adding an unowned G-id to a fixture spec
- reduced: the guard fails by passing when a FRAMEWORK heading or id format is reworded, so extraction finds nothing and nothing is checked | rung: reduce | control: the guard reds when an extraction class (components, ritual headings, G-ids) comes back empty or below a floor; a sabotage row empties each class
- reduced: a guard or ritual built by an item that has since closed reads as unowned | rung: reduce | control: every task under `tasks/`, open or closed, counts as the board; pinned by a test with a closed owner
- reduced: the guard reads a stale map when a newer one exists | rung: reduce | control: it picks the newest map by the date in its filename; a test with two dated maps
- reduced: a deployed repo with no FRAMEWORK.md or no coverage map gets a red it cannot fix | rung: reduce | control: the spec and map paths come from `[guards]`; an unset path switches the guard off, and a set path that does not exist is a red (as CE-14's lists do), so a renamed spec cannot pass silently
- residual: a passing mention of an id in a board item body ("G-D4 is not done here") counts as ownership | rung: individual | why: telling ownership from mention needs judgement, and a structured owner field on every item would duplicate the map | control: the map's one-class-per-row rule, redone when FRAMEWORK changes materially
- residual: the map is FROZEN, so making the guard green after a FRAMEWORK change means a new dated map or a new board item, never an edit | rung: collective | why: frozen provenance is never edited (CLAUDE.md) | control: the remedy text names both routes; filing a board item is one `task new`
F: goes stale when FRAMEWORK §2, §5.6, §6 or §8 change their heading or id formats (the empty-extraction red catches this); a new coverage map each time the spec grows materially
A: one function in `src/context_engine/guards.py`, done by hand from manual-mode.md § context-engine lint (grep the ids, diff against the map and `tasks/`); `[guards] off` silences it with no code change
M: reuses the guards frame, `Failure` and `[guards]` path scoping from CE-14; extraction patterns live in one place with the sabotage table pointing at them
E: one guard, one test file section, sabotage rows in the existing table; the remedy names the exact missing id and the two ways to own it
