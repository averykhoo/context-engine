---
type: Task
id: CE-233
title: Fail lint on a record id in a reader-facing doc such as README.md (DEC-338)
brief: 'README orients a stranger: no record ids; kit default untouched'
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-12b
created: 2026-11-12
moved: 2026-11-12b
updated: 2026-11-12b
---

Fail lint on a record id in a reader-facing doc (DEC-338): the README is the page GitHub shows a
stranger, so it orients a reader and carries no record ids and no progress tracking; the board and
the records site hold those.

**What:** a lint guard over a `[guards]` list of reader-facing docs (this repo: `README.md`) that
fails any record id of a configured series (`CE-n`, `DEC-n`, `US-n`, `AC-n`, ... as `context.toml`
defines the kinds' prefixes) in the doc's prose, with a remedy that says to point the reader at the
board or the records site instead. Documented in FRAMEWORK §8.3 and a criterion row; tests marked
with that criterion, each sabotaged (DEC-11).

**Not in scope:** the kit's default `context.toml` (an adopted repo's README may already cite ids;
turning it on there is a follow-up), and judging prose for "progress tracking" that cites no id.

## Traps

## Read first

- DEC-338 (the owner's words)
- `src/context_engine/guards.py::caps` and the G-D3/G-D5 `[guards]` lists in `context.toml`

## Log

- 2026-11-12b (claude-code/claude-opus-5-5): G-D13 is this task's guard id (FRAMEWORK §8.3), off while [guards] reader_docs is empty
