---
type: Decision
id: DEC-113
title: G-D3 reads backticked repo paths only in the docs a new [guards] paths list names
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:def0f79910065b0f18c5bee2047b65fceac241f02561712d1d6f922b1cff8486
---

The agent's call on CE-142, made while building it in session 2026-10-30a.

Options:
(a) check every `links` doc, and use a heuristic to tell a pointer from an example;
(b) a marker convention for examples, with every links doc rewritten to use it, the kit runbooks and open task bodies included;
(c) add the docs to `[guards] existence`, so G-T3 checks them;
(d) a new `[guards] paths` list read by G-D3.

Chose (d). A census on 2026-10-30 found 54 backticked path spans in the links docs that resolve to nothing. Every one is an example, a kit default or another repo's path (`docs/invariants.md`, `bin/python`, `log.md`, tasks quoting other repos), and syntax cannot tell them apart from pointers. (b) would mean hand-editing kit copies and task bodies. (c) would bend G-T3's meaning (normative text). The list follows the existing rule that what a doc guard reads is configured, never guessed. This repo lists CLAUDE.md, README.md, docs/charter.md, docs/engine.md and docs/framework/RELEASE-NOTES.md, with zero false reds. The kit template ships `paths = []` (off). Frozen docs are not listed, so the repo decides whether they are read.

Built in lane commit 057715d, on main as 395088f. Cheap to undo: drop the key and guards.py::path_pointers.
