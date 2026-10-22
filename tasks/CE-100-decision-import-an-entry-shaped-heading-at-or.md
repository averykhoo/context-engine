---
type: Task
id: CE-100
title: 'decision import: an entry-shaped heading at #, ## or #### level folds into the entry above'
brief: Any line shaped like an entry heading at a level the importer does not read is refused, or at least named
pri: LATER
state: closed
deps: []
source: session 2026-10-19e
created: 2026-10-19
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-6]
status: deprecated
closed: 2026-10-23a
---

Left over from CE-98 (2026-10-19e). The verifier found that a `#### D-2 -- two *(owner, 2026-07-24)*` heading (four hashes) folds silently into the entry above's stamped body: no refusal, no note, and not in the dry run's layout. The fixer disclosed the `## D-5 -- t *(owner, d)*` case, which is kept as an inner heading and at least listed in the layout. The audio-workspace copy has 0 lines matching either shape (grep 2026-10-19), so the CE-43 migration is not affected.

Fix direction: an entry-shaped heading (an id, then an attribution) at any level other than `### ` is refused, naming its line, the same as the loose `### ` shapes CE-98 already refuses (`decisions.py::IDLIKE_RE`). Every fix gets a sabotaged test (DEC-11).

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 890a44b (sweep 2026-10-23a; verified by an independent agent, gate green on main)
