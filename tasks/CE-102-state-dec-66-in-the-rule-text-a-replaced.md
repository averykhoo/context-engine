---
type: Task
id: CE-102
title: 'State DEC-66 in the rule text: a replaced reconstruction is re-confirmed by asking the owner again'
brief: Kit edit (FRAMEWORK §3.2, manual-mode § record confirm); the hold still applies unless the owner lifts it
pri: LATER
state: closed
deps: []
source: session 2026-10-20c
created: 2026-10-20
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-7]
status: deprecated
closed: 2026-10-30a
---

DEC-66 (owner, 2026-10-20c, ASK-16): when retire --by agent replaces a story the owner confirmed, the successor is re-confirmed by asking the owner again, never by quoting the owner's earlier confirmation words. FRAMEWORK §3.2 and manual-mode § context-engine record confirm (both copies) state only the fact today (CE-58, 192f92c). Say the rule there; consider whether record confirm should refuse words identical to the predecessor's confirmation (a cheap guard, sabotage it).

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 16bfb17 (lane 9ba1cf5), cite in 4f2930a: DEC-66 is stated as a rule in FRAMEWORK §3.2 and manual-mode § context-engine record confirm (both copies). working.py::Engine.confirm refuses, before writing anything, words that confirmed a story the record supersedes, directly or down the chain, whitespace aside; the remedy is to ask the owner again, or quote an exact repeat with when and where (DEC-98). AC-112, tests/test_confirm.py, the record_confirm op description and a release-notes line go with it.
