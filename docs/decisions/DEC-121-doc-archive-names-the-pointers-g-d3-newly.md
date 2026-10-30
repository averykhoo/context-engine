---
type: Decision
id: DEC-121
title: doc archive names the pointers G-D3 newly reports after a move and rewrites none of them
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tasks: [CE-96]
code: [src/context_engine/working.py::Engine._pointer_reds, src/context_engine/working.py::_pointer_note]
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:7a9cc9fc51975bf72712e4f7cc9526a9ddce8d45d44d7e698778afed6ec1df3c
---

`doc archive` reports the pointers G-D3 newly reports after the move and rewrites none of them (CE-96).

Options: (a) rewrite the links in other docs to the new path; (b) name each doc and line in the reply and rewrite nothing; (c) say nothing and leave it to lint. Chose (b).

Why: a pointer can sit in a record whose body is hashed (`body_sha`) or append-only, or in a frozen doc, and no write may change any of those. FRAMEWORK §7.3 also never repairs the archive itself. The report is computed from G-D3's own failures before and after the writes, so it matches what lint will say. Cheap to undo: it changes only the reply text.

Known gap (CE-96 verifier): the before/after comparison keys on (path, message), and the message carries a line number, so a red link already below a pruned passage is reported as new when `--lines` shifts it.

Code: working.py::Engine._pointer_reds, working.py::_pointer_note.
