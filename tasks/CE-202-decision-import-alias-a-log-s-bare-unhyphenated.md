---
type: Task
id: CE-202
title: "decision import: alias a log's bare unhyphenated ids (D17) when its prefix is kept"
brief: Split from CE-171 part 4; design not pinned
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Split from CE-171 part 4 (DEC-213). From the CE-11 intervals cutover (2026-11-02a): with a kind prefix equal to the log's, no imported record gets an alias, so the bare unhyphenated `D17` form (about 287 uses in intervals) cannot be aliased at import, and a citation in that form does not resolve.

Today `decisions.py::plan_import` writes `aliases: [<old id>]` only when an entry's id changed (`if e.old != e.id`). A design has to choose:
- a knob on the CLI and the MCP `decision_import` tool naming the extra alias form (for instance `--alias-form '{prefix}{n}'`);
- how such an alias meets G-D2's alias rule (`store.py` alias problems, checked in `working.py::Working.import_log` before any write);
- the kit runbook wording (`manual-mode.md` § context-engine decision import, both copies) and FRAMEWORK §11.4;
- a path for a log already imported (intervals is), since a second import refuses: an alias added after the import.

## Traps

## Read first
- decisions.py::plan_import
- working.py::Working.import_log
- CE-171, DEC-213

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): Correction: the import entry point is working.py::Engine.import_log (class Engine), not Working.import_log as the brief and CE-171's commit ea3ddb4 say; the G-D2 alias check is called from there.
