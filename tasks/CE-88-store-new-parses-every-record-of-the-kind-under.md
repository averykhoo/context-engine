---
type: Task
id: CE-88
title: Store.new parses every record of the kind under the lock to find ids in use
brief: 89% of Store.new under cProfile; grows with the record count and lengthens every lock hold
pri: LATER
state: closed
deps: []
source: session 2026-10-15b
created: 2026-10-15
moved: 2026-10-23a
updated: 2026-10-23a
goals: [G-2]
status: deprecated
closed: 2026-10-23a
---

Found by CE-87 (2026-10-15b): store.py::Store.ids_in_use parses the YAML of every record of the kind while the engine lock is held. On this repo, 2026-10-15: 265 ms for tasks (93 files), 223 ms for questions, 109 ms for decisions. It did not cause CE-87's refusal but lengthens every hold. Options: read ids from file names, or a cached id index checked against mtimes.

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): closed: done in 8c08432 (sweep 2026-10-23a; verified by an independent agent, gate green on main)
