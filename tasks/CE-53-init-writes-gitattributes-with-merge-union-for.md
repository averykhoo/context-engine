---
type: Task
id: CE-53
title: init writes .gitattributes with merge=union for the op log
brief: Every adopting repo merges branches that both append op lines; never overwrite an owner's .gitattributes
pri: NOW
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-5, G-6]
status: deprecated
closed: 2026-10-30a
---

From CE-45 (2026-10-13c): this repo's .gitattributes now sets `docs/ledger/ops.jsonl merge=union`, so two branches' op lines merge without conflict, but init does not write it, so adopting repos conflict on every branch merge. Recommendation: init appends the line to an existing .gitattributes (or creates one) only with the same owner yes/no as the settings merge (DEC-32); CE-46's eol=lf lines could be added with it.

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 2ae0621 (lane cf58a1c), cites in 74e4591: init gives the op log git's union merge driver. bootstrap.py::_plan_union creates .gitattributes holding the line, or appends it after a blank line in the file's own line endings when bootstrap.py::_union_merged finds no merge=union for the op log yet, without asking (DEC-95). The path is the op log context.toml names; an edited-after-plan file is refused; a non-UTF-8 file or a path needing quotes gets a warning. A test merges two branches that both appended op lines without a conflict. New AC-116. FRAMEWORK, kit README, manual-mode and procedures updated, kit copies byte-equal. Nine sabotages, all red.
